import datetime
import re
import cv2
import numpy as np
from pylibdmtx import pylibdmtx
from PIL import Image


def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized


def decode_data_matrix(image) -> str:
    """
    | 
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    result: list = pylibdmtx.decode(thresh)
    if result: 
        return result[0].data, result[0].rect
    else:
        return None, None

def __not_empty(data, field_name):
    if data and                         \
            field_name in data and      \
            data[field_name] and        \
            data[field_name] != 'None':
        return True
    else:
        return False


def create_label_text(data: dict, age: str = None, source: bool = False) -> str:
    """
    Returns label text as string. 
    Age and source can be also added as parameters.
    """
    name = ''

    if __not_empty(data, 'number'):
        name += data['number'] + ' '

    if __not_empty(data, 'genus'):
        name += data['genus'] + ' '

    if __not_empty(data, 'species'):
        name += data['species'] + ' '

    if __not_empty(data, 'subspecies'):
        name += 'ssp. ' + data['subspecies'] + ' '

    if __not_empty(data, 'variety'):
        name += 'var. ' + data['variety'] + ' '

    if __not_empty(data, 'cultivar'):
        name += 'cv ' + data['cultivar'] + ' '

    if age:
        name += '| Age: %s' % age

    if source:
        if __not_empty(data, 'cultivar'):
            source_text  += data['source']
            name += '| Seed source: %s' % source_text

    if __not_empty(data, 'UID'):
        name += ' [%s]' % data['UID']

    return name

def get_date(data: dict, date_field_name: str) -> datetime.datetime.date:
    """
    Returns date field as datetime.datetime from db_data dictionary
    """
    if __not_empty(data, date_field_name):
        date_string = data[date_field_name].strip()
        if re.match(r'\d{2}\.\d{2}\.\d{4}', date_string):
            return datetime.datetime.strptime(date_string, '%d.%m.%Y')
        elif re.match(r'\d{4}-\d{2}-\d{2}', date_string):
            return datetime.datetime.strptime(date_string, '%Y-%m-%d')
        else:
            return None
    else:
        return None

def get_seeding_date(data: dict) -> datetime.datetime:
    """
    Returns 'seeding_date' as datetime.datetime
    """
    return get_date(data, 'seeding_date')


def get_purchase_date(data: dict) -> datetime.datetime:
    """
    Returns 'purchase_date' as datetime.datetime
    """
    return get_date(data, 'purchase_date')

def get_age(db_data, shooting_date):
    """
    Returns age as string. If seeding date is not available, it's trying 
    to calculate age since purchase date (and message about it is added)
    """
    seeding_date = first_date = get_seeding_date(db_data)
    if not seeding_date:
        purchase_date = first_date = get_purchase_date(db_data)
        if not purchase_date:
            return None
    
    age_dt = shooting_date - first_date
    age_days = age_dt.days
    years = age_days // 365
    months = (age_days % 365) // 30
    days = (age_days % 365) % 30

    age_str = ''
    if years:
        age_str += '%sy ' % years
    if months:
        age_str += '%sm ' % months
    if days:
        age_str += '%sd ' % days

    if not seeding_date:
        age_str += 'since purchase '
    return age_str


def get_shooting_date(image):
    """Get date when a photo was taken from EXIF"""
    i = Image.open(image)
    exif = i._getexif()
    if exif and 36867 in exif:
        dt_str = exif[36867]
        try:
            dt = datetime.datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S')
            #print('EXIF shooting date:', dt)
            return dt
        except Exception as e:
            print('Parcing EXIF shooting date unsuccessful:', dt_str, e)
            return None
    else:
        print('No shooting date in EXIF')
        return None

def get_text_origin_size(config, image, label_lines: list) -> tuple:
    """ 
    Returns: 
    * text origin as tuple (x, y)  - bottom left corner of text 
    * text size as tupe (width, heigh)
    """
    font = int(config['LABELS']['font'])
    font_scale = int(config['LABELS']['font_scale'])
    font_thickness = int(config['LABELS']['font_thickness'])
    interline_factor = float(config['LABELS']['interline_factor'])
    text_origin_x_value = int(config['LABELS']['text_origin_x'])

    h, w = image.shape[:2]

    # calculate text bounding box size
    text_line_heigh  = 0
    label_w = 0 
    for text_line in label_lines: 
        label_size = cv2.getTextSize(text_line, font, font_scale, font_thickness)

         # adjust font scale if label is not fit in image
        if label_size[0][0] > w:
            font_scale = w/label_size[0][0]
            label_size = cv2.getTextSize(text_line, font, font_scale, font_thickness)

        text_line_heigh = label_size[0][1]
        if label_size[0][0] > label_w:
            label_w = label_size[0][0]
    label_h = text_line_heigh * len(label_lines) * interline_factor

    # calculate text origin
    text_origin_x = text_origin_x_value
    text_origin_y = h - text_line_heigh

    return (text_origin_x, text_origin_y), (label_w, label_h), text_line_heigh

def draw_label_bgnd(config, image, origin, size):
    """
    Drawing background with opacity with size it relation with text
    """
    padding = int(config['LABELS']['background_padding'])
    marker_space = int(config['LABELS']['marker_space'])

    # calculate rectangle point coordinates
    bgnd_x1 = int(origin[0] - marker_space)
    bgnd_y1 = int(origin[1] - size[1] - padding)
    bgnd_x2 = int(size[0] + bgnd_x1 + marker_space + padding)
    bgnd_y2 = int(origin[1] - size[1] + bgnd_y1 + 2 * padding)

    # crop the background rect 
    sub_img = image[bgnd_y1:bgnd_y2, bgnd_x1:bgnd_x2]
    black_rect = np.ones(sub_img.shape, dtype=np.uint8) * 0
    res = cv2.addWeighted(sub_img, 0.5, black_rect, 0.5, 1.0)

    # putting the image back to its position
    image[bgnd_y1:bgnd_y2, bgnd_x1:bgnd_x2] = res
    
    return image

def get_valid_colors() -> list:
    """ Returns list of valid colors (BGR) for markers and frames """
    colors = [
        (0, 0, 200),
        (0, 200, 0),
        (200, 0, 0),
        (200, 130, 0),
        (200, 0, 200),
        (0, 200, 200),
    ]
    return colors

def put_text_on_image(config, image, text, origin, font_color=None):

    font = int(config['LABELS']['font'])
    font_scale = int(config['LABELS']['font_scale'])
    font_thickness = int(config['LABELS']['font_thickness'])
    if not font_color:
        font_color = tuple(int(i) for i in config['LABELS']['font_color'].split(','))

    cv2.putText(
        img=image, 
        text=text, 
        org=(int(origin[0]), int(origin[1])), 
        fontFace=font, 
        fontScale=font_scale, 
        color=font_color,
        thickness=font_thickness
    )

    return image



if __name__ == '__main__':
    image = cv2.imread("/home/demetrius/Projects/DataMatrix-Sorter/app/experiments/train_dm.png")
    info, rect = encode_data_matrix(image)
    print(info)