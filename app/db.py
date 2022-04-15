

class DB:
    """
    |   In current implementation it's just a csv-file
    """
    SEPARATOR = '|'

    def __init__(self, csv_file_path):
        self.data = {}
        self.csv_file_path = csv_file_path
        self.__read()
        self.__create_keys_from_titles()
        self.__extract_data()

    def __read(self):
        with open(self.csv_file_path, 'r') as f:
            self.file_lines = f.readlines()    

    def __create_keys_from_titles(self):
        self.keys = self.file_lines[0].split(DB.SEPARATOR)
        
    def __extract_data(self):
        for line in self.file_lines[1:]:
            fields = line.split(DB.SEPARATOR)
            if len(fields) > 1:
                uid = fields[0]
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