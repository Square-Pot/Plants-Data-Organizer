import cv2
import numpy
import logging

from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg

# for visualizing
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog

from .classes import DataMatrix

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class DataMatrixDetector:
    """
    |   Class for detection data matrices on the photo
    |   One instance can be used multiple times
    """
    def __init__(self, path_to_model):
        self.pth = path_to_model
        self.score_threshold = 0.8  # 80% - default value
        self.__config()

    def __config(self):
        self.cfg = get_cfg()
        self.cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))
        self.cfg.DATASETS.TRAIN = ("my_dataset_train",)
        self.cfg.DATASETS.TEST = ("my_dataset_val",)
        self.cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 64
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = 4 #your number of classes + 1
        self.cfg.MODEL.DEVICE = 'cpu'
        self.cfg.MODEL.WEIGHTS = self.pth
        self.predictor = DefaultPredictor(self.cfg)

    def __get_bboxes(self):
        """
        |   Returns boundign boxes for detected data matrices
        |   with score more than theshold
        """
        good_indexes = []
        for i, score in enumerate(self.outputs["instances"].scores):
            if score > self.score_threshold:
                good_indexes.append(i)
        good_bboxes = []
        for i in good_indexes:
            good_bboxes.append(self.outputs["instances"].pred_boxes[i].tensor)
        return good_bboxes

    def __get_cropped_img(self, tens):
        """
        |   Returns cropped image with data matrix only according to boundig box
        """
        y1 = int(tens[0][1])
        y2 = int(tens[0][3])
        x1 = int(tens[0][0])
        x2 = int(tens[0][2])
        return self.image[y1:y2, x1:x2]

    def set_score_threshold(self, value):
        """
        |   Set theshold for detected data matrices to filter 
        |   zones with low match level.
        |   Float or float as string. 
        |   Example: 0.7 (is meaning 70%)
        """
        self.score_threshold = float(value)

    def detect(self, image: numpy.ndarray):
        self.image = image
        self.outputs = self.predictor(image)
        bboxes = self.__get_bboxes()
        logger.debug('%s data matrices was detected', len(bboxes))
        if bboxes:
            self.result = []
            for bbox in bboxes:
                dm = DataMatrix()
                dm.bbox = bbox
                dm.image = self.__get_cropped_img(bbox)
                dm.parent_image_shape = self.image.shape
                self.result.append(dm)
            return True
        else:
            return False


    def get_result(self) -> list:
        """
        | Returns list of DataMatrix objects
        | Should be call after 'detect' method
        """
        return self.result

    def visualize(self):
        """
        |   Show *all* detected regions
        """
        v = Visualizer(self.image[:, :, ::-1], MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]), scale=1.2)
        out = v.draw_instance_predictions(self.outputs["instances"].to("cpu"))
        cv2.imshow('Data Matrices Detected', out.get_image()[:, :, ::-1])
        cv2.waitKey()
  

def main():
    dmd = DataMatrixDetector('../model_final.pth')
    image = cv2.imread("/home/demetrius/Projects/DataMatrix-Sorter/photo_examples/l1.jpg")
    dmd.detect(image)
    result = dmd.get_result()
    print(result)
    dmd.visualize()


if __name__ == '__main__':
    main()