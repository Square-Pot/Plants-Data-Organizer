from configparser import ConfigParser

config = ConfigParser()
config.read('settings.ini')


print(config['MAIN']['input_folder'])
print(config.sections())



def main():
    pass




if __name__ == '__main__':
    main()