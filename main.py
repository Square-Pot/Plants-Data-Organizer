from configparser import ConfigParser
from app.Processor import Processor


def main():
    config = ConfigParser()
    config.read('settings.ini')
    processor = Processor(config)
    processor.exec()


if __name__ == '__main__':
    main()