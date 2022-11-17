#!/usr/bin/env python

import logging
import logging.config
from configparser import ConfigParser
#from app.Processor import Processor
from app.folders import FolderStructure
from app.processor import Processor
from app.db import DB
from app.gui import Gui


def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG) 
    logger.addHandler(logging.StreamHandler())

    logger.info(f"{'='*30} STARTED {'='*30}")
    
    config = ConfigParser()
    config.read('settings.ini')
    folders = FolderStructure(config)
    processor = Processor(config)
    db = DB(config['DATABASE']['csv_file'])

    #TODO: db-object create multiple times

    gui = Gui(config, db, folders, processor)
    gui.mainloop()

    logger.info(f"{'='*30} FINISHED {'='*30}")


if __name__ == '__main__':
    main()
