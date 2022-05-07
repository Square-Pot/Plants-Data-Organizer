[EN](README.md) | RU

# Сортировщик и маркирователь фотографий по матричному коду


[![GitHub stars](https://img.shields.io/github/stars/spalk/DataMatrix-Sorter.svg?style=flat-square&label=github%20stars)](https://github.com/spalk/DataMatrix-Sorter)
[![GitHub Contributors](https://img.shields.io/github/contributors/spalk/DataMatrix-Sorter.svg?style=flat-square)](https://github.com/spalk/DataMatrix-Sorter/graphs/contributors)

Automatic **recognition** the plants on the photos by the label with a 2D-code (Data Matrix), photos of plants **organizing** and **marking** it wiht plant information: genus, species, age, etc. Useful tool for botanists and plants collectors.

Автоматическое **распознавание** растений на фотографии по двухмерному коду (Дата Матрице), **организация** фотографий растений, а также **маркирование**  фотографий информацией о данном растении: род, вид, возраст и т.д.  Удобный инструмент для ботаников и коллекционеров растений. 


- [Введение](#введение) 
- [Описание](#описание)
- [Логика приложения](#логика-приложения)
- [Источники данных](#источники-данных) 
  - [Photo sources](#photo-sources)
  - [Reference information source](#reference-information-source)
    - [CSV-file](#csv-file)
    - [XLSX-file](#xlsx-file)
- [Detection and recognition](#detection-and-recognition)
- [Photo files organizing](#photo-files-organizing)
- [Reusult examples](#result-examples)
- [Creating labels](#creating-labels)
- [FAQ](#creating-phisical-labels)

## Введение

*Это некоммерческий проект с открытым исходным кодом. Автор этого проекта является любителем в выращивании суккулентов и мечтает об автоматизации рутинных процессов учета и систематизации информации о растениях, чтобы облегчить жизнь, а также популяризировать **мирное** хобби по выращиванию растений, в особенности мезембов (Аизовых)*


## Описание

Если вы изучаете или коллекционируете расстения или просто являетесь любителем-энтузиастом, то почти наверняка ваш телефон и жесткий диск компьютера содержат тысячи фотографий растений. Это понятно, потому что вы фотографируете растения не только в особые моменты его жизни, например в период цветения, но и просто так, на регулярной освное, чтобы отслеживать развитие данного растения. И все попытки организовать эту кучу фотографий обычно заканчиваются неудачно. 

Другой трудемкой задачей является хранении информации о растении. Пластиковая табличка с минимальной информацей и excel-файл (или амбарная книга) - традиционно используемые инструменты. Поддержка такой системы учета требует много сил, при этом большие риски, связанными с человеческим фактором. 

Автоматически распознаваемые таблички могут помочь решить обе эти проблемы. [Дата Матрица](https://en.wikipedia.org/wiki/Data_Matrix) - это как QR-код, только меньше по размеру, который содрежит только уникальный номер растения. Табличку с Дата Матрицей очень просто сделать самостоятельно: распечтать, вырезать и заламинировать, один раз для всех ваших растений. Преимущества таких табличек:

- автоматическое распознавание растения или нескольких растений на фотографии;
- автоматическая маркировка фотографий информацией об изображенном растении (имя, возраст, источник семян и т.д.);
- автоматическая организация фотографий в индивидуальные папки растений;
- благодаря однотипности и одинаковому размеру бирок - аккуратный и организованный внешний вид вашей коллекции;
- точность идентификации: бирка может также содержать в себе информацию в человеко-понятном виде;
- автомтизация изготовления бирок.

![Data Matrix labeling](img/labels_comparing.png)

![Plantation](img/data-matrix_plantation.jpg)

## Логика приложения

Предлагаются следующие шаги: 

1. Пользователь (любитель растени) делает столько фотографий, сколько он хочет.
2. Приложение анализирует все эти фотографии, пытаясь найти на них Дата Матрицу и распознать расетние. 
3. Имя растения, возраст и др. информация наносится на изображенрие фотографии. 
4. Обновленный файл фотографии сохраняется в индивидуальную папку данного растения. 
  
![4 steps](img/4_steps_ru.png)

По прошествию какого-то количества времени накопятся новые фотографии и цикл повторится. В результате пользователь получит все свои фотографии, маркированные и организованные в отдельные папки полностью автоматически. 

Более детальны алгоритм работе представлен на  [логической схеме](img/logic_scheme.png).


## Источники данных

Приложение использует два вида входных данных: 
- файлы фотографий растений;
- справочная информация о растениях: род, вид, дата посева и т.д.

===============================================================================



### Photo sources

In current version you can provide photos of your plants in three ways: 
1. Put photos to `INPUT` folder in root dir. The app will process them and depending on the result move files to `Successful` or `Unsuccessful` subfolder. 
2. Add path (or multiple paths) of the location where your photos are stored to the `input_paths.txt` file. The app will process all image files in this locations and in subfolders recursively in *read_only* mode. 
3. Photos of plants without or undecoded data-matrix label can be manually put to the particular plant's folder `LABEL_REQURED` subfolder. Such photos will be also processed according and marked with label according to the plant folder. 

### Reference information source

- In current version reference information can be extracted from csv-file. It can be easy created from the list of plants in Excel which you probably have.
- There are plans to make an possibillity to read info from cloud-stored spreadsheet, like Google Spreadsheet. 

#### CSV-file

The main csv-file requirements  are: 
- correct column names in first line;
- filled UID column.

There are multiple inconveniences by editing csv-file, for example: during file opening type of UID column should be choosen as 'text', otherwise as 'number' by default the UID values with zero at the first place will loose it, wich means UID will be modified by opening, wich is unacceptable. Considering this csv format is using as temporary.

#### XLSX-file

Local XLSX-file, XMLX-file in the cloud or online spreadsheet (like Goolge Spreadsheet) support will be added as soon as possible.


## Detection and recognition

There are three possible cases with detection and recognition:
1. The photo has Data Matrix wich was detected and plant recignized successfully
2. The photo has Data Matrix but for some reason it was not detected or recognized or was recognized wrong or recogized correctly, but not found in data base. 
3. The photo doesn't have any Data Matrix, so recognition is possible. 

Photos from cases 2 and 3, if you can identify plant on it, can be manually places to the required plant folder `LABEL_REQURED` subfolder.  See [Photo Sources](#photo-sources) section.

## Photo files organizing
The first step after app runnig is to create or update output folder structure. The output folder structure matches the database (reference file) structure exactly and represents inividual folder for each plant. The Name of individula plant folder containts UID and plant name (genus, species, etc.). If you manually delete some plant folder or delete the output folder structure completely, it will be recreated after next app lounch. 

Each plant folder also has a subfolder with name `LABEL_REQURED` for labeling manual recognised plants photos. 

## Result examples

- Resulting photo of manually recognized plant:  

 [![name](https://i.imgur.com/eKc0SbYt.jpg)](https://imgur.com/eKc0SbY)   


- Resulting photo of two autmatically recognized plants:  

 [![name](https://i.imgur.com/lKOVYqLt.jpg)](https://imgur.com/lKOVYqL)   

- Resulting photo of multiple autmatically recognized plants:  

 [![name](https://i.imgur.com/JVWe48Tt.jpg)](https://imgur.com/JVWe48T)   


## Creating labels
A PDF file with labels can be generated according to the reference file. The next steps for creating smart and durable physical labels are: 
- cut out each paper label; 
- laminate it using as thicker laminating film as you can get;
- leave at least 2 mm gap between paper labels (for insulation of paper);
- cut out each laminated label;
- make oblique cut of the side of lable wich will be put into the soil. 

![Lable](img/label.png)

PDF-generator is not implemented in this repo yet, but it's ready and it will be here soon. 


## FAQ

### Q: Is it works on Windows / Mac?
As all code is python, theoretically - yes. But more likely some refactoring is needed for crossplatform support. If you Windows / Mac user, you can contribute as a tester.

### Q: What code encoded in Data Matrix? 
Only UID - a unque identifier - 6 (or more) digits number. All other plant infromation is retrieved from reference file by UID. 

### Q: Where to get a model for a neural network?
Ask me. It's not a secret, it's just too big to store it in GitHub.

