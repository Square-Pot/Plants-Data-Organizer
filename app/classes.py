#import os
import cv2
import random
import re

from .utils import get_valid_colors, image_resize
from .utils import decode_data_matrix
from .utils import create_label_text
#from .utils import get_seeding_date
from .utils import get_shooting_date
from .utils import get_age
from .utils import get_text_origin_size
from .utils import draw_label_bgnd
from .utils import get_valid_colors
from .utils import put_text_on_image


class DataMatrix:
    def __init__(self):
        self.image = None
        self.bbox = None     # preliminary bounding box (after Data Matrix area detection)
        self.rect = None     # ??? final rectangle (after successul Data Matrix decoding)
        self.parent_image_shape = None
        self.decoded_successful: bool = None
        self.decoded_info: str = None
        self.db_data = None
        self.age: str = None
        self.label_text: str = None

    def decode(self):
        """ Decode Data Matrix to get UID """
        info, rect = decode_data_matrix(self.image)
        if info: 
            self.decoded_successful = True
            self.decoded_info = info.decode("utf-8") 
            self.rect = rect
        else:
            self.decoded_successful = False

    def extract_db_data(self, shooting_date):
        """ Extract data from DB by decoded uid  """
        uid = self.decoded_info
        if self.db.key_exist(uid):
            self.db_data = self.db.get_item(uid)

    def generate_labels(self, shooting_date):
        """ Create label text wich contains 'label_text' value """
        self.age = get_age(self.db_data, shooting_date)
        self.label_text = create_label_text(self.db_data, self.age_str, source=True)



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
        self.decoded_uids = []  # ?
        self.db_data = None
        self.shooting_date = None
        self.label_text = None
        self.output_image = None

    def detect_dm(self, data_matrix_detector) -> None:
        """
        Detects data matrices on the photo.
        Save result as list of DataMatrix objects.
        """
        data_matrix_detector.detect(self.image)
        data_matrices = data_matrix_detector.get_result()
        if data_matrices:
            self.data_matrices = data_matrices

    def decode_dm(self, db) -> None:
        """
        Decoding of detected data matrices.
        Result is storing in DataMatrix objects.
        """
        bad_dmtxs = []
        if self.data_matrices:
            for dm in self.data_matrices:
                dm.decode(db)
                if dm.decoded_successful:
                    self.decoded_uids.append(dm.decoded_info)
                else:
                    bad_dmtxs.append(dm)
        # remove unsuccessful detected DataMatrix objects from list 
        for dm in bad_dmtxs:
            self.data_matrices.pop(dm)

    def decode_path(self) -> None:
        """ Extracting UID from file path """
        uid = re.search(r'^.+\/(\d+)_.+$', self.path_to_original).group(1)
        if uid:
            self.decoded_uids.append(uid)
        else:
            print("Can't extract UID from file path %s" % self.path_to_original)

    def add_shooting_date(self):
        """  Add shooting date to Image object from EXIF """
        self.shooting_date = get_shooting_date(self.path_to_original)

    def extract_db_data(self, db):
        """
        Extract data from DB by uid as dictionary.
        For Images with data matrices - the data will be stores in DataMatrix object.
        For Images with UID extracted from path will be stored in self.db_data value
        """
        if self.data_matrices:
            for dm in self.data_matrices:
                dm.extract_db_data(db, self.shooting_date)
        elif self.decoded_uids:
            if self.db.key_exist(self.decoded_uids[0]):
                self.db_data = self.db.get_item(self.decoded_uids[0])

    def generate_labels(self):
        """
        Create label text wich contains:
        * in 'self.label_text'  value if detection was by path
        * in 'DataMatrix.label_text' value if detection was by Data Matrix
        """
        if self.data_matrices:
            for dm in self.data_matrices:
                dm.generate_labels(self.shooting_date)
        else:
            self.age = get_age(self.db_data, self.shooting_date)
            self.label_text = create_label_text(self.db_data, self.age, True)

    def get_image_resized(self, width):
        """ Returns image with resized by widht saving proportions """
        return image_resize(self.image, width=width)

    def place_labels_on_image(self):
        """
        Placing label on the image, color markers and bounding boxes around 
        data matrices, if they were detected.
        """

        text_origin, text_boundig_size, text_line_heigh = get_text_origin_size(self.config, self.output_image, self.label_text)
        output_image = draw_label_bgnd(self.config, self.image.copy(), text_origin, text_boundig_size)

        interline_factor = float(self.config['LABELS']['interline_factor'])
        markers_colors = get_valid_colors()
        color_indexes = list(range(len(markers_colors)))

        if self.data_matrices:
            for dmtx in self.data_matrices:
                # put label text on image
                output_image = put_text_on_image(self.config, output_image, dmtx.label_text, text_origin)

                # get marker color
                if not color_indexes:
                    color_indexes = list(range(len(markers_colors)))
                color_index = random.choice(color_indexes)
                color_indexes.remove(color_index)
                marker_color = markers_colors[color_index]

                # put marker on image
                marker_origin = (text_origin[0]-40, text_origin[1]) 
                output_image = put_text_on_image(self.config, output_image, '#', marker_origin, marker_color)

                # shift 'cursor' one line upper
                text_origin[1] -= text_line_heigh * interline_factor

                # calculate scale factor for bounding frames
                dm_parent_img_width = dmtx.parent_image_shape[0]
                output_image_width = output_image.shape[0]
                scale_factor = output_image_width / dm_parent_img_width

                # draw bounding boxex around detected data matrices
                padding = self.config['LABELS']['bounding_box_padding']
                bbox_thickness = self.config['LABELS']['bounding_box_thickness']
                cv2.rectangle(
                    output_image,
                    (int(dmtx.bbox[0][0] * scale_factor) + padding, int(dmtx.bbox[0][1] * scale_factor) + padding),
                    (int(dmtx.bbox[0][2] * scale_factor) - padding, int(dmtx.bbox[0][3] * scale_factor) - padding), 
                    markers_colors[color_index], 
                    bbox_thickness
                )
            self.output_image = output_image

        elif self.label_text:
            # put label text on image
            output_image = put_text_on_image(self.config, output_image, self.label_text, text_origin)
            self.output_image = output_image