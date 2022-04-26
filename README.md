

# Data Matrix File Sorter and Image Labeler

[![GitHub stars](https://img.shields.io/github/stars/spalk/DataMatrix-Sorter.svg?style=flat-square&label=github%20stars)](https://github.com/yzhang-gh/vscode-markdown)
[![GitHub Contributors](https://img.shields.io/github/contributors/spalk/DataMatrix-Sorter.svg?style=flat-square)](https://github.com/yzhang-gh/vscode-markdown/graphs/contributors)

Automatic recognition plants on the photos by label with code (Data Matrix), organizing and labeling photos by plant. Useful tool for botanists and collectors.


- [Intro](#intro) 
- [Data Sources](#data-sources) 
  - [Photo sources](#photo-sources)
  - [Refernce information source](#refernce-information-source)
    - [CSV-file](#csv-file)
    - [XLSX-file](#xlsx-file)
- [Detection Methods](#detection-methods) •
- [Photo files organizing](#saving-disposing) •
- [Creating labels](#creating-phisical-labels) • 
- [FAQ](#creating-phisical-labels)



## Intro

If you are botanist,plants collerctor or grower enthusiast, your mobile phone and computer are almost certainly full of thousands of photos of plants. This is understandable, because you take photos not only in special moments in plants life like flowering, but also just regulary, to track the development of the plant. And all attempts to organize this bunch of photos are usual unsuccessful. 

The other laborious task is to keep information about plants. Plastic labels with basic information and excel-file (or barn notebook) are traditional tools. Maintaining of such accounting system requires a lot of work and has high risks of human factor mistakes.

Automatically recognizible labels can help to solve both of this tasks. [Data Matrix](https://en.wikipedia.org/wiki/Data_Matrix) is like QR-Code, but smaller and containts just a unique number of plant. Label with Data Matrix is easy to **DIY** - print, cut and laminate for all plants at once. The benefits of such labels: 
- recognition automation of plant or multiple plants on the photo;
- automatically marking of the photos with plant information (name, age, seed source, etc.);
- automatically plants photos organizing between particular plant folder;
- neat and organized look because of same label size;
- identification reliability: it can also contain *human-readable* information as a backup;
- labels making automation. 



## Data sources

There are two types of input data: 
- photos of plants;
- reference information like genus, species, seeding date, etc.

### Photo sources

In current version you can provide photos of your plants in three ways: 
1. Put photos to `INPUT` folder in root dir. The app will process them and depending on the result move files to `Successful` or `Unsuccessful` subfolder. 
2. Add path (or multiple paths) of the location where your photos are stored to the `input_paths.txt` file. The app will process all image files in this locations and in subfolders recursively in *read_only* mode. 
3. Photos of plants without or undecoded data-matrix label can be manually put to the particular plant's folder `LABEL_REQURED` subfolder. Such photos will be also processed according and marked with label according to the plant folder. 

### Refernce information source

- In current version reference information can be extracted from csv-file. It can be easy created from the list of plants in Excel which you probably have.
- There are plans to make an possibillity to read info from cloud-stored spreadsheet, like Google Spreadsheet. 

#### CSV-file

The main csv-file requirements  are: 
- correct column names in first line;
- filled UID column.

There are multiple inconveniences by editing csv-file, for example: during file opening type of UID column should be choosen as 'text', otherwise as 'number' by default the UID values with zero at the first place will loose it, wich means UID will be modified by opening, wich is unacceptable. Considering this csv format is using as temporary.

#### XLSX-file

Local XLSX-file, XMLX-file in the cloud or online spreadsheet (like Goolge Spreadsheet) support will be added as soon as possible.


