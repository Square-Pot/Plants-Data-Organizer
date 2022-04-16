import cv2
from configparser import ConfigParser

from .db import DB
from .folders import FolderStructure
from .source import Source
from .classes import TargetImage
from .dmtx_detector import DataMatrixDetector
from .utils import image_resize 



class Processor:

    def __init__(self, config: ConfigParser) -> None:
        self.config = config
        self.db = DB(self.config['DATABASE']['csv_file'])

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

        
        # Create/update output folder structure
        folder_structure = FolderStructure(self.config)
        folder_structure.check(self.db)

        # Read input forlder
        photo_source = Source(self.config)
        source_photos_auto = photo_source.read_auto()
        source_photos_manual = photo_source.read_manual(folder_structure)



        # # Setting up data matrix detector
        # dmd = DataMatrixDetector(self.config['DETECTION']['model_file'])
        # dmd.set_score_threshold(self.config['DETECTION']['score_threshold'])
      
        # # Image processing
        # image_path = '/home/demetrius/Projects/DataMatrix-Sorter/photo_examples/test_exif2.jpg'
        # image = TargetImage(image_path)
        # image.detect_dm(dmd)
        # image.decode_dm(self.db)
        # image.extract_db_data()
        # img_with_name = image.add_plant_name()

        # cv2.imshow('with name', img_with_name)
        # cv2.waitKey()


    def __read_exifs(self):
        pass


