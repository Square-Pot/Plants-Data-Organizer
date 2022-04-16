import os


class FolderStructure:

    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.output_folder_is_exist = os.path.exists(output_dir)


    def check(self, db_object):
        self.db = db_object
        if self.output_folder_is_exist:
            self.__update_structure()
        else:
            self.__create_structure()
    
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
            
            manual_folder_path = os.path.join(item_folder_path, 'manual_detected')
            os.makedirs(manual_folder_path)


    def __create_structure(self):
        # create main output folder
        os.makedirs(self.output_dir)

        # create inner folder structure
        db_data = self.db.get_data()
        for uid in db_data: 
            self.__create_item_folder(db_data[uid])




def main():
    fs = FolderStructure('../OUTPUT')
    


if __name__ == '__main__':
    main()
