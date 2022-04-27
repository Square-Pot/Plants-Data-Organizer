import logging
import os
import re
import cv2


class FolderStructure:

    def __init__(self, config):
        self.config = config
        self.output_dir = self.config['PATHS']['output_folder']
        self.output_folder_is_exist = os.path.exists(self.output_dir)
        self.label_required_folder = self.config['PATHS']['label_required_folder_name']
        self.input_folder = self.config['PATHS']['input_folder']
        self.current_structure = {}
        self.unsuccessful_folder = None

    def sync_with_db(self, db_object):
        """
        |   Create or update folder structure in 'output_folder'
        |   according to DB structure.
        |   Remember: DB is MASTER, folder structure is SLAVE
        """
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

    def dispose_original(self, image):
        if int(self.config['MAIN']['delete_processed_files']):
            os.remove(image.path_to_original)
        else: 
            self.__create_successful_dir()
            os.replace(
                image.path_to_original, 
                os.path.join(
                    self.successful_folder,
                    os.path.basename(image.path_to_original)
                )
            )
            

    @staticmethod
    def __create_photo_filename(uid: str, dt, extension):
        filename_list = [
            uid,
            dt.strftime('%Y-%m-%d_%H-%M-%S')
        ]
        filename_str = '_'.join(filename_list)
        filename_str += extension

        return filename_str

    def __get_output_path_by_uid(self, uid):
        #  self.__update_structure()   # what for? 
        path = os.path.join(
            self.output_dir,
            self.current_structure[uid],
        )
        return path

    def save_image_to_output(self, image):
        if image.decoded_uids:
            for uid in image.decoded_uids:
                if uid in self.current_structure:
                    filename, file_extension = os.path.splitext(image.path_to_original)
                    file_name = self.__create_photo_filename(
                        uid,
                        image.shooting_date,
                        file_extension
                    )
                    file_path = os.path.join(
                        self.__get_output_path_by_uid(uid),
                        file_name
                    )
                    cv2.imwrite(file_path, image.output_image)
                    logging.info('Saved image: %s', file_path)
                else: 
                    logging.warning("Can't save file, unknown UID:", uid)

    def __create_successful_dir(self):
        self.successful_folder = os.path.join(self.input_folder, 'successful')
        if not os.path.exists(self.successful_folder):
            os.mkdir(self.successful_folder)

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
            
            manual_folder_path = os.path.join(item_folder_path, self.label_required_folder)
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
                    logging.warning('Foreign directory in output folder: %s', folder)
            else:
                logging.warning('Foreign object in output folder: %s', folder)

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
                    logging.info('Name of folder was changed for UID: %s', uid)
            else:
                if re.match(r'\d+', uid):
                    self.__create_item_folder(db_data[uid])
                    logging.info('Folder for UID: %s was not found. Now created', uid)


def main():
    fs = FolderStructure('../OUTPUT')


if __name__ == '__main__':
    main()
