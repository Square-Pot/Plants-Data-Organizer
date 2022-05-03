import logging
import logging.config
from configparser import ConfigParser
from app.Processor import Processor


def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG) 
    logger.addHandler(logging.StreamHandler())


    logger.info(f"{'='*30} STARTED {'='*30}")
    
    config = ConfigParser()
    config.read('settings.ini')
    processor = Processor(config)
    processor.exec()

    logger.info(f"{'='*30} FINISHED {'='*30}")

if __name__ == '__main__':
    main()