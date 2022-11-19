from configparser import ConfigParser
# import logging

from .db import DB
from .folders import FolderStructure
from .sources import Source
from .classes import TargetImage
from .dmtx_detector import DataMatrixDetector
from .hash import Hash

# logging.basicConfig(level=logging.DEBUG)


#TODO: collect hash for processed photos

class Processor:

    def __init__(self, config: ConfigParser, db: DB, folders: FolderStructure ) -> None:
        self.config = config
        self.db = db
        self.folders = folders
        self.folders.sync_with_db(self.db)
        self.hash = Hash(self.config)
        self.dmd = None
        # Image Sources
        self.image_source = Source(self.config)
        self.__init_dmd()

    def __init_dmd(self):
        self.dmd = DataMatrixDetector(self.config['DETECTION']['model_file'])
        self.dmd.set_score_threshold(self.config['DETECTION']['score_threshold'])

    def exec_from_paths(self):
        """ Process images from 'paths' """
        # if int(self.config['SOURCES']['paths']):
        print('Watching source PATHS...')
        source_1_paths = self.image_source.from_paths()
        print(f'{len(source_1_paths)} photos detected')
        if source_1_paths: 
            # if not self.dmd:
            #     self.__init_dmd()
            for image_path in source_1_paths: 
                if self.hash.check(image_path):
                    self.__process_image(image_path, detection_method='datamatrix', dispose=False)
                else:
                    print(f'Hash was found for photo [{ image_path }]. Procedure was cancelled.')

    def exec_from_input(self):
        """ Process images from 'input' source """
        # if int(self.config['SOURCES']['input_folder']):
        print('Watching source INPUT folder...')
        source_2_input = self.image_source.from_input()
        print(f'{len(source_2_input)} photos detected')
        if source_2_input: 
            # if not self.dmd:
            #     self.__init_dmd()
            for image_path in source_2_input:
                if self.hash.check(image_path):
                    self.__process_image(image_path, detection_method='datamatrix', dispose=True)
                else:
                    print(f'Hash was found for photo [{ image_path }]. Procedure was cancelled.')
                    self.folders.move_to_successful(image_path)
  
    def exec_from_output(self):
        """ Process images from 'output' source """
        # if int(self.config['SOURCES']['output_folder']):
        print('Watching source OUTPUT folder...')
        source_3_output = self.image_source.from_output(self.folders)
        print(f'{len(source_3_output)} photos detected')
        if source_3_output: 
            for image_path in source_3_output:
                if self.hash.check(image_path):
                    self.__process_image(image_path, detection_method='path', dispose=True)
                else:
                    print(f'Hash was found for photo [{ image_path }]. Procedure was cancelled.')

    # def exec(self):
    #     self.exec_from_paths()
    #     self.exec_from_input()
    #     self.exec_from_output()
 
    def __process_image(self, image_path: str, detection_method: str, dispose: bool):
        """
        * Detection method: 
        There are two ways to get UID: from data matrix (detection_method = 'datamatrix') 
        and form file path (datection_method = 'path').

        * Disposing: 
        Original files can be disposed or untouched. Disposing method is specified
        in 'settings.ini' file.
        """
        valid_detection_methods = {'datamatrix', 'path'}
        if detection_method not in valid_detection_methods:
            raise ValueError("results: status must be one of %r." % valid_detection_methods)

        image = TargetImage(image_path, self.config)

        if detection_method == 'datamatrix':
            dm_detected = image.detect_dm(self.dmd)
            if dm_detected:
                image.decode_dm()
            else: 
                print('No Data Matices was detected')

        elif detection_method == 'path':
            image.decode_path()
        
        if image.decoded_uids: 
            image.add_shooting_date()
            image.extract_db_data(self.db)
            image.generate_labels()
            image.place_labels_on_image()
            # # image.add_logo()
            self.folders.save_image_to_output(image)
            self.hash.add_hash_to_collection(image_path)
            if dispose:
                self.folders.dispose_original(image)
            del image
        else: 
            self.folders.move_to_unsuccessful(image.path_to_original)
        


