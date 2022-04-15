import cv2

from .utils import image_resize
from .utils import decode_data_matrix

class DataMatrix:
    def __init__(self):
        image = None
        bbox = None     # preliminary bounding box (after Data Matrix area detection)
        rect = None     # final rectangle (after successul Data Matrix decoding)
        parent_image_shape = None
        decoded_successful: bool = None
        decoded_info: str = None


class TargetImage:
    def __init__(self, path_to_original: str):
        self.path_to_original = path_to_original
        self.image = cv2.imread(self.path_to_original)
        self.data_matrices = None

    def get_image_resized(self, height):
        return image_resize(self.image, height=height)

    def detect_dm(self, data_matrix_detector):
        data_matrix_detector.detect(self.get_image_resized(500)) # TODO: size of detecting image
        data_matrices = data_matrix_detector.get_result()
        if data_matrices:
            self.data_matrices = data_matrices

    def decode_dm(self):
        if self.data_matrices:
            for dm in self.data_matrices:
                info, rect = decode_data_matrix(dm.image)
                if info: 
                    dm.decoded_successful = True
                    dm.decoded_info = info
                    dm.rect = rect
                else:
                    dm.decoded_successful = False
        else:
            print('Looks like there is no Data Matrix on image')



    
