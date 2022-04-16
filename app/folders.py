import os
import re
import cv2


class FolderStructure:

    def __init__(self, config):
        self.config = config
        self.output_dir = self.config['PATHS']['output_folder']
        self.output_folder_is_exist = os.path.exists(self.output_dir)
        self.manual_detected_folder = self.config['PATHS']['manual_detected_folder']
        self.input_folder = self.config['PATHS']['input_folder']
        self.current_structure = {}
        self.unsuccessful_folder = None

    def check(self, db_object):
        self.db = db_object
        if self.output_folder_is_exist:
            self.__update_structure()
        else:
            self.__create_structure()

    def get_current_structure(self):
        self.__get_current_structure()
        return self.current_structure

    def move_to_unsuccessful(self, file_path):
        if not self.unsuccessful_folder:
            self.__create_unsuccessful_dir()
        os.replace(
            file_path, 
            # could not working on windows:
            os.path.join(self.unsuccessful_folder, os.path.basename(file_path))
        )

    @staticmethod
    def __create_photo_filename(uid: str, dt, extension):
        filename_list = [
            uid,
            dt.strftime('%Y-%m-%d')
        ]
        filename_str = '_'.join(filename_list)
        filename_str += extension

        return filename_str

    def __get_output_path_by_uid(self, uid):
        self.__update_structure()
        path = os.path.join(
            self.output_dir,
            self.current_structure[uid],
        )
        return path

    def save_image_to_output(self, image):
        for dm in image.data_matrices:
            if dm.decoded_successful:
                filename, file_extension = os.path.splitext(image.path_to_original)
                file_name = self.__create_photo_filename(
                    dm.decoded_info,
                    image.shooting_date,
                    file_extension
                )
                file_path = os.path.join(
                    self.__get_output_path_by_uid(dm.decoded_info),
                    file_name
                )
                cv2.imwrite(file_path, image.output_image)
                print('Saved image:', file_path)
    
    def __create_unsuccessful_dir(self):
        self.unsuccessful_folder = os.path.join(self.input_folder, 'unsuccessful')
        if not os.path.exists(self.unsuccessful_folder):
            os.mkdir(self.unsuccessful_folder)

    def __create_folder_item_name(self, item):
        name_list = []
        # UID|number|genus|species|subspecies|variety|cultivar|synonym|form|affinity|ex|information|source|seeding_date|purchase_date|pot_width|pot_height|soil|description
        fields = ['UID', 'number', 'genus', 'species', 'subspecies', 'variety', 'cultivar', 'synonym']
        for f in fields: 
            if f in item:
                value = item[f].replace(' ', '-')
                name_list.append(value)
        name_str = '_'.join(name_list)
        return name_str

    def __create_item_folder(self, item):
        if item and 'UID' in item: 
            folder_name = self.__create_folder_item_name(item)
            
            item_folder_path = os.path.join(self.output_dir, folder_name)
            os.makedirs(item_folder_path)
            
            manual_folder_path = os.path.join(item_folder_path, self.manual_detected_folder)
            os.makedirs(manual_folder_path)

    def __create_structure(self):
        # create main output folder
        os.makedirs(self.output_dir)

        # create inner folder structure
        db_data = self.db.get_data()
        for uid in db_data: 
            self.__create_item_folder(db_data[uid])

    def __get_current_structure(self):
        # get current folder structure
        pattern = r"^(\d+)_.+$"
        output_dir_ls = os.listdir(self.output_dir)
        for folder in output_dir_ls:
            folder_path = os.path.join(self.output_dir, folder)
            if os.path.exists(folder_path):
                uid_search = re.search(pattern, folder)
                if uid_search:
                    uid = uid_search.group(1)
                    self.current_structure[uid] = folder
                else:
                    print('Foreign directory in output folder:', folder)
            else:
                print('Foreign object in output folder:', folder)

    def __update_structure(self):
        self.__get_current_structure()

        # check each item from db: if it exist (by UID) and compare full folder names
        db_data = self.db.get_data()
        for uid in db_data:
            if uid in self.current_structure:
                folder_name_current = self.current_structure[uid]
                folder_name_should_be = self.__create_folder_item_name(db_data[uid])
                if  folder_name_current != folder_name_should_be:
                    os.rename(
                        os.path.join(self.output_dir, folder_name_current),
                        os.path.join(self.output_dir, folder_name_should_be)
                    )
                    print(uid, 'Name of folder was changed')
            else:
                if re.match(r'\d+', uid):
                    self.__create_item_folder(db_data[uid])
                    print(uid, 'Folder for UID was not found. Now created')


def main():
    fs = FolderStructure('../OUTPUT')


if __name__ == '__main__':
    main()