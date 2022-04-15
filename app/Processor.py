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

        image = cv2.imread("/home/demetrius/Projects/DataMatrix-Sorter/photo_examples/test.jpg")
        image = image_resize(image, height=500)
        dmd.detect(image)
        data_matrices = dmd.get_result()
        print(data_matrices)
        if data_matrices:
            for dm in data_matrices:
                cv2.imshow('dm', dm.image)
                cv2.waitKey()
        #dmd.visualize()



    def __read_exifs(self):
        pass


