import cv2
from configparser import ConfigParser

from .classes import TargetImage
from .dmtx_detector import DataMatrixDetector
from .db import DB
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

        # Setting up data matrix detector
        dmd = DataMatrixDetector(self.config['DETECTION']['model_file'])
        dmd.set_score_threshold(self.config['DETECTION']['score_threshold'])

        # Setting up database
        db = DB(self.config['DATABASE']['csv_file'])

        # Image processing
        image_path = '/home/demetrius/Projects/DataMatrix-Sorter/photo_examples/test.jpg'
        image = TargetImage(image_path)
        image.detect_dm(dmd)
        image.decode_dm(db)

        print(image.data_matrices, '\n\n')

        for dm in image.data_matrices:
            if dm.decoded_successful:
                print(dm.db_data)
            else:
                print('Unsuccessful')       
        

        #dmd.visualize()



    def __read_exifs(self):
        pass


