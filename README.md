

# Data Matrix File Sorter and Image Labeler

[![GitHub stars](https://img.shields.io/github/stars/spalk/DataMatrix-Sorter.svg?style=flat-square&label=github%20stars)](https://github.com/yzhang-gh/vscode-markdown)
[![GitHub Contributors](https://img.shields.io/github/contributors/spalk/DataMatrix-Sorter.svg?style=flat-square)](https://github.com/yzhang-gh/vscode-markdown/graphs/contributors)

Automatic recognition plants on the photos by label with code (Data Matrix), organizing and labeling photos by plant. Useful tool for botanists and collectors.


[Description](#description) •
[Image Sources](#image-sources) •
[Detection Methods](#detection-methods) •
[Saving and disposing](#saving-disposing) •
[Creating phisical labels](#creating-phisical-labels) • 
[FAQ](#creating-phisical-labels)



## Description

If you are botanist,plants collerctor or grower enthusiast, your mobile phone and computer are almost certainly full of thousands of photos of plants. This is understandable, because you take photos not only in special moments in plants life like flowering, but also just regulary, to track the development of the plant. And all attempts to organize this bunch of photos are usual unsuccessful. 

The other laborious task is to keep information about plants. Plastic labels with basic information and excel-file (or barn notebook) are traditional tools. Maintaining of such accounting system requires a lot of work and has high risks of human factor mistakes.

Automatically recognizible labels can help to solve both of this tasks. [Data Matrix](https://en.wikipedia.org/wiki/Data_Matrix) is like QR-Code, but smaller and containts just a unique number of plant. Label with Data Matrix is easy to DIY - print, cut and laminate for all plants at once. The benefits of such labels: 
- plant on the photo can be automatically recognized;
- automatically put information about the plant (name, age, seed source, etc.) in the bottom of the photo;
- automatically move photo to the folder of particular plant.



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

