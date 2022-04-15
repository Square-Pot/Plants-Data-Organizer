import cv2

from .utils import image_resize
from .utils import decode_data_matrix
from .utils import get_fancy_name

class DataMatrix:
    def __init__(self):
        self.image = None
        self.bbox = None     # preliminary bounding box (after Data Matrix area detection)
        self.rect = None     # final rectangle (after successul Data Matrix decoding)
        self.parent_image_shape = None
        self.decoded_successful: bool = None
        self.decoded_info: str = None
        self.db_data = None
        self.fancy_name = None

    def decode(self,  db):
        self.db = db
        info, rect = decode_data_matrix(self.image)
        if info: 
            self.decoded_successful = True
            self.decoded_info = info.decode("utf-8") 
            self.rect = rect
            self.__get_db_data()
            self.__get_fansy_name()
        else:
            self.decoded_successful = False

    def __get_db_data(self):
        uid = self.decoded_info
        if self.db.key_exist(uid):
            self.db_data = self.db.get_item(uid)

    def __get_fansy_name(self):
        if self.decoded_successful:
            self.fancy_name = get_fancy_name(self.db_data)



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

    def add_plant_name(self):
        # generate name or names
        names = []
        if self.data_matrices:
            for dm in self.data_matrices:
                if dm.decoded_successful:
                    names.append(dm.fancy_name)
        
        # font style
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (255, 255, 255)
        thickness = 1

        # number of text lines
        lines_num = len(names)

        # calculate text bounding box size
        line_h  = 0
        label_h = 0
        label_w = 0 
        for line in names: 
            label_size = cv2.getTextSize(line, font, font_scale, thickness)
            label_h += label_size[0][1]
            if label_size[0][1] > line_h:
                line_h = label_size[0][1]
            if label_size[0][0] > label_w:
                label_w = label_size[0][0]

        # interline factor
        line_h = line_h * 1.6

        # calculate text origin
        output_image = image_resize(self.image, 600)
        h, w = output_image.shape[:2]
        text_origin_x = 20
        text_origin_y = h - line_h * lines_num

        for name in names:

            cv2.putText(
                img=output_image, 
                text=name, 
                org=(int(text_origin_x), int(text_origin_y)), 
                fontFace=font, 
                fontScale=font_scale, 
                color=color,
                thickness=thickness
            )
            text_origin_y += line_h
        return output_image


                



    
