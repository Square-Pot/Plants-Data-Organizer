import re
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class DB:
    """
    |   In current implementation it's just a csv-file
    """
    SEPARATOR = '|'

    def __init__(self, csv_file_path):
        self.data = {}
        self.csv_file_path = csv_file_path
        self.file_lines = None
        self.__read()
        self.__create_keys_from_titles()
        self.__extract_data()
        

    def __read(self):
        if os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, 'r') as f:
                self.file_lines = f.readlines()
        else:
            logger.info('CSV reference file was not found')
            # TODO: create blank reference file with titles

    def __create_keys_from_titles(self):
        if self.file_lines:
            self.keys = self.file_lines[0].split(DB.SEPARATOR)
        
    def __extract_data(self):
        if self.file_lines:
            for line in self.file_lines[1:]:
                fields = line.split(DB.SEPARATOR)
                if len(fields) > 1:
                    uid = fields[0]
                    if re.match(r'^\d+$', uid):
                        data = {}
                        for i, field in enumerate(fields):
                            if field: 
                                key = self.keys[i]
                                data[key] = field
                        self.data[uid] = data

    def get_data(self):
        return self.data

    def get_item(self, uid):
        return self.data[uid]

    def key_exist(self, uid) -> bool:
        if uid in self.data:
            return True
        else:
            return False

    def get_genus_list(self):
        genus_list = []
        for i in self.data: 
            genus = self.data[i]['genus']
            if genus not in genus_list:
                genus_list.append(genus)
        genus_list.sort()
        return genus_list

    def get_species_list(self, genus):
        """ 
        Returns species for particual genus
        (actially not only species but also ssp, var, field_num, etc.)
        as list of dictionaries:  UID:string_line
        """
        species_list = {}
        fields = ['species', 'subspecies', 'variety', 'cultivar', 'synonym', 'number']
        for i in self.data: 
            if self.data[i]['genus'] == genus:
                species_name_list = []
                for f in fields: 
                    if f in self.data[i]:
                        species_name_list.append(self.data[i][f])
                species_name_str = ' '.join(species_name_list)
                species_list[self.data[i]['UID']] = species_name_str
                
        #species_list.sort()
        return species_list


def main():
    db = DB('../plants_export.txt')


if __name__ == '__main__':
    main()