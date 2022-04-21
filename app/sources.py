import os
import re

class Source:
    """
    |   Class for reading input fotos
    """

    def __init__(self, config):
        self.config = config

    def from_paths(self):
        """
        Returns list of photos paths found in locations from 'paths_file'.
        Recurcively! 
        """
        paths_file_path = self.config['PATHS']['paths_file']
        with open(paths_file_path, 'r') as f:
            lines = f.readlines()

        source_paths = []
        for line in lines:
            if os.path.isdir(line):
                source_paths.append(line)

        photo_paths = []
        for source_path in source_paths:
            for path, subdirs, files in os.walk(source_path):
                for name in files: 
                    file_path = os.path.join(path, name)
                    if self.__is_photo(file_path):
                        photo_paths.append(file_path)

        return photo_paths

    def from_input(self):
        """
        Returns list of photo paths from 'Input' folder
        """
        input_folder = self.config['PATHS']['input_folder']

        if not os.path.exists(input_folder):
            print('Input folder does not exist')
            os.mkdir(input_folder)
            return
        
        input_content = os.listdir(input_folder)
        input_photos = []
        for filename in input_content:
            if self.__is_photo(filename):
                input_photos.append(
                    os.path.join(input_folder, filename)
                )
        return input_photos

    def from_output(self, folder_structure_object):
        """
        Returns list of  photo paths from 'Output' folder 'LABEL_REQURED' subfolders
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
        """
        Checks if file is photo by extension in file path
        """
        if re.match(r'^.+\.(?:jpg|png)$', filename):
            return True
        else:
            # check if it folder
            input_folder = self.config['PATHS']['input_folder']
            file_path = os.path.join(input_folder, filename)
            if not os.path.isdir(file_path):
                print('Looks like non image file is in input folder:', filename)
            return False


def test():
    s = Source('config')
    s.from_paths()


if __name__ == '__main__':
    test()