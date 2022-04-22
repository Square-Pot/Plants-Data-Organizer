import datetime
import re
import copy
from this import d
from turtle import pu
import cv2
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
    if data and \
            field_name in data and        \
            data[field_name] and     \
            data[field_name] != 'None':
        return True
    else:
        return False

def get_fancy_name(data: dict, age=None) -> list:
    
    # name = []
    # if __not_empty(data, 'number'):
    #     name.append({
    #         'content': data['number'] + ' ',
    #         'style': 'regular'
    #     })

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

    if __not_empty(data, 'UID'):
        name += ' [%s]' % data['UID']

    return name

def get_date(data: dict, date_field_name: str):
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

def get_age(db_data, shooting_date) -> str:
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


if __name__ == '__main__':
    image = cv2.imread("/home/demetrius/Projects/DataMatrix-Sorter/app/experiments/train_dm.png")
    info, rect = encode_data_matrix(image)
    print(info)