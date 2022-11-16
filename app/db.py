import re
import os
import logging
import datetime
from random import randint

from .classes import GenusColumnNotFoundError

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
        self.keys = None
        self.no_uid_lines_indexes = []
        self.genus_key_index = None
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
            self.genus_key_index = self.__get_genus_key_index()
                

    def __get_genus_key_index(self):
        for index, key in enumerate(self.keys):
            if 'genus' in key: 
                return index
        raise GenusColumnNotFoundError

    def __extract_data(self):
        if self.file_lines:
            for index, line in enumerate(self.file_lines[1:]):
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
                    else: 
                        if len(fields[self.genus_key_index]) > 2:
                            print('>2')
                            self.no_uid_lines_indexes.append(index+1)

    def __make_backup(self):
        timestampt = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')
        with open(self.csv_file_path) as original:
            lines = original.readlines()
            with open(f"{ self.csv_file_path }_[{ timestampt }].backup", "w") as backup:
                backup.writelines(lines)

    def __get_new_uid(self, additionals_uids):
        while True:
            new_uid = str(self.random_with_N_digits(6))
            if new_uid not in self.data and new_uid not in additionals_uids:
                return new_uid

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

    def get_number_with_no_uid(self):
        return len(self.no_uid_lines_indexes)

    def fill_empty_uids(self):
        #TODO log changes
        self.__make_backup()
        with open(self.csv_file_path) as f: 
            lines = f.readlines()

        delimiter = '|'
        new_uids = []
        for i in self.no_uid_lines_indexes:
            line = lines[i]
            line_list = line.split(delimiter)

            line_list[0] = self.__get_new_uid(new_uids)
            lines[i] = delimiter.join(line_list)

        with open(self.csv_file_path, 'w') as f:
            f.writelines(lines)

    def reinit(self):
        self.__init__(self.csv_file_path)

    @staticmethod        
    def random_with_N_digits(n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return randint(range_start, range_end)





def main():
    db = DB('../plants_export.txt')


if __name__ == '__main__':
    main()