import logging
from configparser import ConfigParser
from app.Processor import Processor


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info(f"{'='*30} STARTED {'='*30}")
    
    config = ConfigParser()
    config.read('settings.ini')
    processor = Processor(config)
    processor.exec()

    logging.info(f"{'='*30} FINISHED {'='*30}")

if __name__ == '__main__':
    main()