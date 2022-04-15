import cv2
from pylibdmtx import pylibdmtx


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
    if field_name in data and        \
            data[field_name] and     \
            data[field_name] != 'None':
        return True
    else:
        return False


def get_fancy_name(data: dict) -> list:
    
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
        name += 'subsp.' + data['subspecies'] + ' '

    if __not_empty(data, 'variety'):
        name += 'var.' + data['variety'] + ' '

    if __not_empty(data, 'cultivar'):
        name += 'cv' + data['cultivar'] + ' '

    name += '[%s]' % data['UID']

    return name


if __name__ == '__main__':
    image = cv2.imread("/home/demetrius/Projects/DataMatrix-Sorter/app/experiments/train_dm.png")
    info, rect = encode_data_matrix(image)
    print(info)