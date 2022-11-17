import os
import hashlib


class Hash:
    def __init__(self, config) -> None:
        self.existing_hashes = []
        self.config = config
        self.hash_collection_file = self.config['PATHS']['hash_collection']
        self.__check_hash_collection_file()
        self.__read_existing_hashes()

    @staticmethod
    def get_hash(path_to_file):
    
        # A arbitrary (but fixed) buffer
        # size (change accordingly)
        # 65536 = 65536 bytes = 64 kilobytes
        BUF_SIZE = 65536
    
        # Initializing the sha256() method
        sha256 = hashlib.sha256()
    
        # Opening the file provided as
        # the first commandline argument
        with open(path_to_file, 'rb') as f:
            
            while True:
                
                # reading data = BUF_SIZE from
                # the file and saving it in a
                # variable
                data = f.read(BUF_SIZE)
    
                # True if eof = 1
                if not data:
                    break
        
                # Passing that data to that sh256 hash
                # function (updating the function with
                # that data)
                sha256.update(data)
    
        
        # sha256.hexdigest() hashes all the input
        # data passed to the sha256() via sha256.update()
        # Acts as a finalize method, after which
        # all the input data gets hashed hexdigest()
        # hashes the data, and returns the output
        # in hexadecimal format
        return sha256.hexdigest()
    
    def __read_existing_hashes(self):
        with open(self.hash_collection_file, 'r') as f: 
            lines = f.readlines()

        for l in lines:
            l = l.strip()
            if l:
                self.existing_hashes.append(l)

    def add_hash_to_collection(self, path_to_file):
        hash = self.get_hash(path_to_file)
        with open(self.hash_collection_file, 'a+') as f:
            f.write('\n')
            f.write(hash)
    
    def check(self, path_to_file):
        """
        Returns True if hash was NOT found in hash collection
        """
        hash = self.get_hash(path_to_file)
        return hash not in self.existing_hashes

    def __check_hash_collection_file(self):
        """
        Create file for hash collection if it does not exist
        """
        if not os.path.isfile(self.hash_collection_file):
            with open(self.hash_collection_file, 'w') as f:
                pass