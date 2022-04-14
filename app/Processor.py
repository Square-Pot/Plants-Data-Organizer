import cv2
from configparser import ConfigParser

from app.dm_detect import DataMatrixDetector
from .utils import image_resize


class Processor:

    def __init__(self, config: ConfigParser) -> None:
        self.config = config
        self.exifs = None

    def exec(self):


        # check settings
        # check folders
        # read and check input
        #   file format
        #   read exif 
        #   check if this photo with this exif already exist (md5?)
        # encoding process
        #   resize
        #   detect qr and encode
        #   move original photo to folder 
        #       create folder if needed 
        #       rename file if name is duplicated
        #   remove from input
        #   move undetectable photos to unknown folder

        dmd = DataMatrixDetector('model_final.pth')
        dmd.set_score_threshold(self.config['DETECTION']['score_threshold'])

        image = cv2.imread("/home/demetrius/Projects/DataMatrix-Sorter/photo_examples/l1.jpg")
        image = image_resize(image, height=500)
        dmd.detect(image)
        dmd.visualize()
        bboxes = dmd.get_bboxes()
        for tens in bboxes:
            y1 = int(tens[0][1])
            y2 = int(tens[0][3])
            x1 = int(tens[0][0])
            x2 = int(tens[0][2])
            cropped_image = image[y1:y2, x1:x2]
            cv2.imshow('cropped', cropped_image)
            cv2.waitKey()


    def __read_exifs(self):
        pass


