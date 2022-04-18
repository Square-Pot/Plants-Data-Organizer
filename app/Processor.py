import os
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

        # Proceed soure photos with auto detection
        source_photos_auto = photo_source.read_auto()
        print(len(source_photos_auto), 'photos found in INPUT')

        # Setting up data matrix detector
        dmd = DataMatrixDetector(self.config['DETECTION']['model_file'])
        dmd.set_score_threshold(self.config['DETECTION']['score_threshold'])
      
        # Image processing
        for image_path in source_photos_auto:
            #image_path = '/home/demetrius/Projects/DataMatrix-Sorter/photo_examples/test_exif2.jpg'
            resize_width = int(self.config['MAIN']['output_width'])
            image = TargetImage(image_path, self.config)
            dm_is_detected = image.detect_dm(dmd)
            if dm_is_detected:
                image.decode_dm(self.db)
                for dm in image.data_matrices:
                    if dm.decoded_successful:
                        print('Decoded:', dm.decoded_info)
                    else:
                        print('Decoded: unsuccessful')
                image.extract_db_data()
                image.add_plant_labels()
                if image.output_image is not None:
                    folder_structure.save_image_to_output(image)
                    folder_structure.dispose_original(image)
                else:
                    print('Data Matrix was not decoded', image_path)
                    folder_structure.move_to_unsuccessful(image_path)
            else:
                print('Data Matrix not found:', image_path)
                folder_structure.move_to_unsuccessful(image_path)
                

        # cv2.imshow('with name', img_with_name)
        # cv2.waitKey()



        # Proceed photos manyally detected

    def __read_exifs(self):
        pass


