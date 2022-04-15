import cv2

from .utils import image_resize
from .utils import decode_data_matrix

class DataMatrix:
    def __init__(self):
        self.image = None
        self.bbox = None     # preliminary bounding box (after Data Matrix area detection)
        self.rect = None     # final rectangle (after successul Data Matrix decoding)
        self.parent_image_shape = None
        self.decoded_successful: bool = None
        self.decoded_info: str = None
        self.db_data = None

    def decode(self,  db):
        self.db = db
        info, rect = decode_data_matrix(self.image)
        if info: 
            self.decoded_successful = True
            self.decoded_info = info.decode("utf-8") 
            self.rect = rect
            self.__get_db_data()
        else:
            self.decoded_successful = False

    def __get_db_data(self):
        uid = self.decoded_info
        print(type(uid))
        if self.db.key_exist(uid):
            self.db_data = self.db.get_item(uid)


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

    def decode_dm(self, db):
        if self.data_matrices:
            for dm in self.data_matrices:
                dm.decode(db)
                



    
