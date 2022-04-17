import cv2
import numpy as np
import random

from .utils import image_resize
from .utils import decode_data_matrix
from .utils import get_fancy_name
from .utils import get_seeding_date
from .utils import get_shooting_date

class DataMatrix:
    def __init__(self):
        self.image = None
        self.bbox = None     # preliminary bounding box (after Data Matrix area detection)
        self.rect = None     # ??? final rectangle (after successul Data Matrix decoding)
        self.parent_image_shape = None
        self.decoded_successful: bool = None
        self.decoded_info: str = None
        self.db_data = None
        self.fancy_name = None
        self.age_td = None
        self.age_str = None

    def decode(self,  db):
        self.db = db
        info, rect = decode_data_matrix(self.image)
        if info: 
            self.decoded_successful = True
            self.decoded_info = info.decode("utf-8") 
            self.rect = rect
        else:
            self.decoded_successful = False

    def extract_db_data(self, shooting_date):
        self.shooting_date = shooting_date
        self.__get_db_data()
        self.__get_fansy_name()

    def __get_db_data(self):
        uid = self.decoded_info
        if self.db.key_exist(uid):
            self.db_data = self.db.get_item(uid)

    def __get_age(self):
        seeding_date = get_seeding_date(self.db_data)
        if seeding_date and self.shooting_date:
            self.age_td = self.shooting_date - seeding_date
            age_days = self.age_td.days
            
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

            self.age_str = age_str

    def __get_fansy_name(self):
        self.__get_age()
        self.fancy_name = get_fancy_name(self.db_data, self.age_str)



class TargetImage:
    def __init__(self, path_to_original: str, config):
        self.path_to_original = path_to_original
        self.image = cv2.imread(self.path_to_original)
        self.config = config
        resize = int(config['MAIN']['resize_output'])
        if resize:
            size = int(config['MAIN']['output_width'])
            self.image = self.get_image_resized(size)
        self.data_matrices = None
        self.shooting_date = None
        self.__get_shooting_date()
        self.output_image = None

    def __get_shooting_date(self):
        self.shooting_date = get_shooting_date(self.path_to_original)

    def get_image_resized(self, width):
        return image_resize(self.image, width=width)

    def detect_dm(self, data_matrix_detector):
        data_matrix_detector.detect(self.image)
        data_matrices = data_matrix_detector.get_result()
        if data_matrices:
            self.data_matrices = data_matrices
            return True
        else:
            return False

    def decode_dm(self, db):
        if self.data_matrices:
            for dm in self.data_matrices:
                dm.decode(db)

    def extract_db_data(self):
        if self.data_matrices:
            for dm in self.data_matrices:
                if dm.decoded_successful:
                    dm.extract_db_data(self.shooting_date)


    def add_plant_labels(self):
        # generate name or names
        dmtxs = []
        if self.data_matrices:
            for dm in self.data_matrices:
                if dm.decoded_successful:
                    dmtxs.append(dm)

        if dmtxs:
        
            # font style
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = int(self.config['LABELS']['font_scale'])
            color = tuple(int(i) for i in self.config['LABELS']['font_color'].split(','))
            thickness = int(self.config['LABELS']['font_thickness'])

            # number of text lines
            lines_num = len(dmtxs)

            # calculate text bounding box size
            line_h  = 0
            label_h = 0
            label_w = 0 
            for dmtx in dmtxs: 
                label_size = cv2.getTextSize(dmtx.fancy_name, font, font_scale, thickness)
                label_h += label_size[0][1]
                if label_size[0][1] > line_h:
                    line_h = label_size[0][1]
                if label_size[0][0] > label_w:
                    label_w = label_size[0][0]

            # interline factor
            line_h = line_h * 1.6

            # calculate text origin
            output_image = self.image.copy()
            h, w = output_image.shape[:2]
            text_origin_x = 100
            text_origin_y = h - line_h * lines_num

            # adjust font scale if label is not fit in image
            if label_w > w:
                font_scale = w/label_w



            # calculate background origin and size 
            margin = 5
            bgnd_x1 = text_origin_x - 60
            bgnd_y1 = int(text_origin_y - line_h)
            bgnd_x2 = int(label_w) + bgnd_x1 + 60 + margin
            bgnd_y2 = int(line_h * lines_num) + bgnd_y1 + 2 * margin

            # crop the background rect 
            sub_img = output_image[bgnd_y1:bgnd_y2, bgnd_x1:bgnd_x2]
            black_rect = np.ones(sub_img.shape, dtype=np.uint8) * 0
            res = cv2.addWeighted(sub_img, 0.5, black_rect, 0.5, 1.0)

            # putting the image back to its position
            output_image[bgnd_y1:bgnd_y2, bgnd_x1:bgnd_x2] = res

            colors = [
                (0, 0, 200),
                (0, 200, 0),
                (200, 0, 0),
                (200, 200, 0),
                (200, 0, 200),
                (0, 200, 200),
            ]

            color_indexes = list(range(len(colors)))

            for dmtx in dmtxs:
                # put text name
                cv2.putText(
                    img=output_image, 
                    text=dmtx.fancy_name, 
                    org=(int(text_origin_x), int(text_origin_y)), 
                    fontFace=font, 
                    fontScale=font_scale, 
                    color=color,
                    thickness=thickness
                )
                
                # get marker color
                if not color_indexes:
                    color_indexes = list(range(len(colors)))
                color_index = random.choice(color_indexes)
                color_indexes.remove(color_index)

                # put marker
                cv2.putText(
                    img=output_image, 
                    text='#', 
                    org=(int(text_origin_x) - 40, int(text_origin_y)), 
                    fontFace=cv2.FONT_HERSHEY_DUPLEX, 
                    fontScale=font_scale, 
                    color=colors[color_index],
                    thickness=thickness
                )

                # calculate scale factor
                dm_parent_img_width = dm.parent_image_shape[0]
                output_image_width = output_image.shape[0]
                scale_factor = output_image_width / dm_parent_img_width

                # draw bounding boxex
                padding = 5
                cv2.rectangle(
                    output_image,
                    (int(dmtx.bbox[0][0] * scale_factor) + padding, int(dmtx.bbox[0][1] * scale_factor) + padding),
                    (int(dmtx.bbox[0][2] * scale_factor) - padding, int(dmtx.bbox[0][3] * scale_factor) - padding), 
                    colors[color_index], 
                    5
                )

                text_origin_y += line_h
            self.output_image = output_image


                



    
