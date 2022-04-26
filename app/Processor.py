from configparser import ConfigParser
# import logging

from .db import DB
from .folders import FolderStructure
from .sources import Source
from .classes import TargetImage
from .dmtx_detector import DataMatrixDetector

# logging.basicConfig(level=logging.DEBUG)


class Processor:

    def __init__(self, config: ConfigParser) -> None:
        self.config = config
        self.db = DB(self.config['DATABASE']['csv_file'])
        self.folders = FolderStructure(self.config)
        self.folders.sync_with_db(self.db)
        self.dmd = None

    def __init_dmd(self):
        self.dmd = DataMatrixDetector(self.config['DETECTION']['model_file'])
        self.dmd.set_score_threshold(self.config['DETECTION']['score_threshold'])

    def exec(self):
       
        # Image Sources
        image_source = Source(self.config)

        # Process images from 'paths'
        if int(self.config['SOURCES']['paths']):
            print('Watching source PATHS...')
            source_1_paths = image_source.from_paths()
            print(f'{len(source_1_paths)} photos detected')
            if source_1_paths: 
                if not self.dmd:
                    self.__init_dmd()
                for image_path in source_1_paths: 
                    self.__process_image(image_path, detection_method='datamatrix', dispose=False)

        # Process images from 'input' source
        if int(self.config['SOURCES']['input_folder']):
            print('Watching source INPUT folder...')
            source_2_input = image_source.from_input()
            print(f'{len(source_2_input)} photos detected')
            if source_2_input: 
                if not self.dmd:
                    self.__init_dmd()
                for image_path in source_2_input:
                    self.__process_image(image_path, detection_method='datamatrix', dispose=True)

        # Process images from 'output' source
        if int(self.config['SOURCES']['output_folder']):
            print('Watching source OUTPUT folder...')
            source_3_output = image_source.from_output(self.folders)
            print(f'{len(source_3_output)} photos detected')
            if source_3_output: 
                for image_path in source_3_output:
                    self.__process_image(image_path, detection_method='path', dispose=True)

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
            if not dm_detected:
                self.folders.move_to_unsuccessful(image.path_to_original)
                return
            image.decode_dm()

        if detection_method == 'path':
            image.decode_path()
        
        image.add_shooting_date()
        image.extract_db_data(self.db)
        image.generate_labels()
        image.place_labels_on_image()
        # # image.add_logo()
        self.folders.save_image_to_output(image)
        if dispose:
            self.folders.dispose_original(image)


            



            # dm_is_detected = image.detect_dm(self.dmd)
            # if dm_is_detected:
            #     image.decode_dm(self.db)
            #     for dm in image.data_matrices:
            #         if dm.decoded_successful:
            #             print('Decoded:', dm.decoded_info)
            #         else:
            #             print('Decoded: unsuccessful')
            #     image.extract_db_data()
            #     image.add_plant_labels()
            #     if image.output_image is not None:
            #         folder_structure.save_image_to_output(image)
            #         folder_structure.dispose_original(image)
            #     else:
            #         print('Data Matrix was not decoded', image_path)
            #         folder_structure.move_to_unsuccessful(image_path)
            # else:
            #     print('Data Matrix not found:', image_path)
            #     folder_structure.move_to_unsuccessful(image_path)

            # # Images processing: labeling
            # source_photos_manual = photo_source.read_manual(folder_structure)
            # for image_path in source_photos_manual:
            #     image = TargetImage(image_path, self.config, detected_manual=True)
            #     image.set_db_object(self.db)
            #     image.extract_db_data()
            #     if image.output_image is not None:
            #         folder_structure.save_image_to_output(image)
            #         folder_structure.dispose_original(image)


