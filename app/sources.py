import os
import re

class Source:
    """
    |   Class for reading input fotos
    """

    def __init__(self, config):
        self.config = config

    def read_auto(self):
        """
        |   Read photos from 'Input' folder  and automatically 
        |   recognize plants by Data Matrix.
        """
        input_folder = self.config['PATHS']['input_folder']

        if not os.path.exists(input_folder):
            print('Input folder does not exist')
            return
        
        input_content = os.listdir(input_folder)
        input_photos = []
        for filename in input_content:
            if self.__is_photo(filename):
                input_photos.append(
                    os.path.join(input_folder, filename)
                )
        return input_photos

    def read_manual(self, folder_structure_object):
        """
        |   Read fotos from 'Manual' folder in each plant folder
        |   placed manually 
        """
        output_folder = self.config['PATHS']['output_folder']
        label_required_folder_name = self.config['PATHS']['label_required_folder_name']
        current_structure = folder_structure_object.get_current_structure()
        
        input_photos = []
        for uid in current_structure:
            item_folder = current_structure[uid]
            item_path = os.path.join(
                output_folder,
                item_folder,
                label_required_folder_name
            )
            item_files = os.listdir(item_path)
            for filename in item_files:
                if self.__is_photo(filename):
                    input_photos.append(
                        os.path.join(item_path, filename)
                    )
        return input_photos

    def __is_photo(self, filename):
        if re.match(r'^.+\.(?:jpg|png)$', filename):
            return True
        else:
            # check if it folder
            input_folder = self.config['PATHS']['input_folder']
            file_path = os.path.join(input_folder, filename)
            if not os.path.isdir(file_path):
                print('Looks like non image file is in input folder:', filename)
            return False