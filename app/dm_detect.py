import cv2
import numpy

from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg

# for visualizing
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog


class DataMatrixDetector:
    """
    |   Class for detection data matrices on the photo
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

    def set_score_threshold(self, value):
        self.score_threshold = float(value)

    def detect(self, image: numpy.ndarray):
        self.image = image
        self.outputs = self.predictor(image)

    def get_bboxes(self):
        # Instances(
        #     num_instances=2, 
        #     image_height=500, 
        #     image_width=500, 
        #     fields=[
        #         pred_boxes: Boxes(
        #             tensor([
        #                 [139.2361,   7.9742, 250.8367,  92.3241],
        #                 [ 94.9334, 310.9177, 162.9716, 363.9027]
        #             ])
        #         ), 
        #         scores: tensor([0.9987, 0.2421]), 
        #         pred_classes: tensor([1, 1])
        #     ]
        # )


        # print(self.outputs["instances"])
        # print(self.outputs["instances"].scores)


        good_indexes = []
        for i, score in enumerate(self.outputs["instances"].scores):
            if score > self.score_threshold:
                good_indexes.append(i)
        
        good_bboxes = []
        for i in good_indexes:
            good_bboxes.append(self.outputs["instances"].pred_boxes[i].tensor)

        return good_bboxes

    def visualize(self):
        v = Visualizer(self.image[:, :, ::-1], MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]), scale=1.2)
        out = v.draw_instance_predictions(self.outputs["instances"].to("cpu"))
        cv2.imshow('Data Matrices Detected', out.get_image()[:, :, ::-1])
        cv2.waitKey()


def main():
    dmd = DataMatrixDetector('model_final.pth')
    image = cv2.imread("/home/demetrius/Projects/DataMatrix-Sorter/photo_examples/l1.jpg")
    dmd.detect(image)
    bboxes = dmd.get_bboxes()
    print(bboxes)
    dmd.visualize()


if __name__ == '__main__':
    main()