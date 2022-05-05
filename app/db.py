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




def main():
    db = DB('../plants_export.txt')


if __name__ == '__main__':
    main()