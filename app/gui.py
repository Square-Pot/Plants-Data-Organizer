from importlib.resources import path
import os
import sys
import re
import subprocess
from configparser import ConfigParser
import logging
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from .folders import FolderStructure
from .sources import Source
from .processor import Processor
from .db import DB
from .classes import get_plant_as_obj
from .label_builder import LabelsBuilder

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class Gui:

    def __init__(self, config: ConfigParser, db:DB, folders: FolderStructure, processor: Processor) -> None:
        self.config = config
        self.folders = folders
        self.processor = processor
        self.source = Source(self.config)
        self.db = db

        self.root = tk.Tk() 
        self.root.title("Data Matrix Sorter and Labeler")
        self.root.geometry("1000x600") 

        # add icon
        photo = tk.PhotoImage(file = 'icon.png')
        self.root.wm_iconphoto(False, photo)

        self.checkbox_input_var = tk.IntVar()
        self.checkbox_paths_var = tk.IntVar()
        self.checkbox_output_var = tk.IntVar()

        top_row_height = 150
        bottom_row_hight = 450
        left_col_width = 300
        center_col_width = 300
        rigth_col_width = 500
        padding = 3

        self.root.grid_rowconfigure(0, minsize=150)
        self.root.grid_rowconfigure(1, weight=1, minsize=150)
        self.root.grid_columnconfigure(0, minsize=200)
        self.root.grid_columnconfigure(1, minsize=200)
        self.root.grid_columnconfigure(2, weight=1, minsize=500)

        self.frame_top_left = tk.Frame(self.root, width=left_col_width, height=top_row_height, pady=padding, padx=padding)
        frame_top_center = tk.Frame(self.root, width=center_col_width, height=top_row_height, pady=padding, padx=padding)
        frame_top_right = tk.Frame(self.root, width=rigth_col_width, height=top_row_height, pady=padding, padx=padding)
        frame_bottom_left = tk.Frame(self.root, width=left_col_width, height=bottom_row_hight, pady=padding, padx=padding)
        frame_bottom_center = tk.Frame(self.root, width=center_col_width, height=bottom_row_hight, pady=padding, padx=padding)
        frame_bottom_right = tk.Frame(self.root, width=rigth_col_width, height=bottom_row_hight, pady=padding, padx=padding)

        self.frame_top_left.grid(row=0, column=0, sticky='nesw')
        frame_top_center.grid(row=0, column=1, sticky='nesw')
        frame_top_right.grid(row=0, column=2,  sticky='nesw')
        frame_bottom_left.grid(row=1, column=0, sticky='ns')
        frame_bottom_center.grid(row=1, column=1, sticky='ns')
        frame_bottom_right.grid(row=1, column=2, sticky='nesw')

        self.btn_generate_uids_text = tk.StringVar()

        self.__fill_frame_input(self.frame_top_left)
        self.__fill_frame_db(frame_top_center)
        self.__fill_frame_scroll_one(frame_bottom_left)
        self.__fill_frame_scroll_two(frame_bottom_center)
        self.frame_bottom_center = frame_bottom_center
        self.frame_bottom_right = frame_bottom_right
        self.frame_top_right = frame_top_right

        self.uid_species_reference = None
        self.cur_uid = None

    def mainloop(self):
        self.root.mainloop() 

    def __fill_frame_input(self, frame):
        input_frame = tk.LabelFrame(frame, text='Input photos')
            
        checkbox_input = tk.Checkbutton(input_frame, text=f'Input folder [{ self.source.count_input() }]', variable=self.checkbox_input_var)
        if int(self.config['SOURCES']['input_folder']):
            checkbox_input.select()
        checkbox_input.pack(anchor=tk.W, padx=5)

        checkbox_paths = tk.Checkbutton(input_frame, text=f'Paths [{ self.source.count_paths() }]', variable=self.checkbox_paths_var)
        if int(self.config['SOURCES']['paths']):
            checkbox_paths.select()
        checkbox_paths.pack(anchor=tk.W, padx=5)

        checkbox_output = tk.Checkbutton(input_frame, text=f'Output folder [{ self.source.count_output(self.folders) }]', variable=self.checkbox_output_var)
        if int(self.config['SOURCES']['output_folder']):
            checkbox_output.select()
        checkbox_output.pack(anchor=tk.W, padx=5)

        button_frame = tk.Frame(
            master=input_frame,
            #relief=tk.RAISED,
            borderwidth=1
        )
        button_frame.pack(fill=tk.Y)

        button_edit_paths = tk.Button(button_frame, text="Edit Paths", command=self.handle_click_edit_paths)
        button_edit_paths.grid(column=0, row=0, padx=5, pady=5)

        button_input_output = tk.Button(button_frame, text="Proceed", command=self.handle_click_input_proceed)
        button_input_output.grid(column=1, row=0, padx=5, pady=5)

        input_frame.pack(side=tk.LEFT, fill=tk.BOTH) 

    def __fill_frame_db(self, frame):
        input_frame = tk.LabelFrame(frame, text='Input reference file')

        no_uid_number = self.db.get_number_with_no_uid()

        label_reference = tk.Label(input_frame, text=f'245 lines, UID for { no_uid_number } is needed')
        label_reference.pack(padx=5, pady=10)

        button_generate_labels = tk.Button(input_frame, text="Generate Labels", command=self.handle_click_show_table)
        button_generate_labels.pack(fill=tk.BOTH,  padx=5)

        self.btn_generate_uids_text.set(f"Generate UIDs [{ no_uid_number }]")
        button_generate_uids = tk.Button(input_frame, textvariable=self.btn_generate_uids_text, command=self.handle_click_generate_uids)
        button_generate_uids.pack(fill=tk.BOTH,  padx=5)

        input_frame.pack(side=tk.LEFT, fill=tk.Y)

    def __fill_frame_scroll_one(self, frame):
        genus_scrollbar = tk.Scrollbar(frame) 
        genus_listbox = tk.Listbox(frame, yscrollcommand = genus_scrollbar.set, width=25)  
        genus_list = self.db.get_genus_list(count_content=True)
        for genus in genus_list: 
            genus_listbox.insert(tk.END, genus) 
        genus_listbox.pack(side = tk.LEFT, fill = tk.Y )   
        genus_listbox.bind("<<ListboxSelect>>", self.handle_select_genus) 
        genus_scrollbar.pack(side = tk.RIGHT, fill = tk.Y) 

    def __fill_frame_scroll_two(self, frame, genus=None):
        species_scrollbar = tk.Scrollbar(frame) 
        species_listbox = tk.Listbox(frame, yscrollcommand = species_scrollbar.set, width=25 )  
        if genus:
            species_list = self.db.get_species_list(genus)
            self.uid_species_reference = []
            for uid in species_list: 
                self.uid_species_reference.append(uid)
                species_listbox.insert(tk.END, species_list[uid]) 
        species_listbox.pack(side = tk.LEFT, fill = tk.Y )    
        species_listbox.bind("<<ListboxSelect>>", self.handle_select_plant) 
        species_scrollbar.pack(side = tk.RIGHT, fill = tk.Y) 

    def __show_images(self, frame, img_file_list):
        frame_width = frame.winfo_width()
        frame_height = frame.winfo_height()
        thumb_min = int(self.config['GUI']['thumbnail_size'])
        max_photos_in_row = frame_width // thumb_min
        rows_num = len(img_file_list) // max_photos_in_row + 1


        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)
        
        num_photos_in_row = 0
        cur_row = 1
        cur_col = 0
        path = None
        img_file_list = sorted(img_file_list)
        for i, path in enumerate(img_file_list):
            image = Image.open(path)
            coeff = image.width / image.height
            if coeff > 1:
                thumb_w = int(thumb_min * coeff)
                thumb_h = thumb_min
            else: 
                thumb_w = thumb_min
                thumb_h = int(thumb_min / coeff)
            image = image.resize((thumb_w, thumb_h))
            crop_l = (image.width - thumb_min) / 2
            crop_r = crop_l + thumb_min
            crop_u = (image.height - thumb_min) / 2
            crop_b = crop_u + thumb_min
            image = image.crop((crop_l, crop_u, crop_r, crop_b))
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(scrollable_frame, image = photo)
            label.image = photo
            cur_col += 1
            if num_photos_in_row >= max_photos_in_row:
                cur_row += 1
                cur_col = 1
                num_photos_in_row = 0
            label.grid(row=cur_row, column=cur_col)
            num_photos_in_row += 1
            label.bind("<Button-1>",lambda e,path=path:self.__open_img_in_default_viewer(path))
            i += 1

        if path:
            self.cur_plant_path = os.path.dirname(os.path.abspath(path))
            button_open_folder = tk.Button(scrollable_frame, text="Open containing folder", command=self.__open_plant_folder)
            button_open_folder.grid(column=1, row=cur_row + 1, pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")  


    def __show_plant_info(self, frame):

        #TODO: refactor according to https://stackoverflow.com/questions/43731784/tkinter-canvas-scrollbar-with-grid

        data_frame = tk.LabelFrame(frame, text='Plant information')

        canvas = tk.Canvas(data_frame, height=100)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        data = self.db.get_item(self.cur_uid)
        title = self.__get_plant_title(data)
        keys = ':\r'.join(data.keys())
        values = '\r'.join(data.values())

        label_title = tk.Label(scrollable_frame, text=title, font=("Helvetica", 12, 'bold'))
        label_keys = tk.Label(scrollable_frame, text=keys, font=("Helvetica", 9, 'bold'), anchor="w", justify=tk.LEFT)
        label_values = tk.Label(scrollable_frame, text=values, font=("Helvetica", 9), anchor="w", justify=tk.LEFT)

        #data_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=1)

        label_title.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        label_keys.grid(row=1, column=0, padx=5, sticky='w')
        label_values.grid(row=1, column=1, padx=5, sticky='w')


        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y") 
        data_frame.pack(side = tk.LEFT, fill=tk.BOTH, expand=1)

    def __open_plant_folder(self):
        os.system('xdg-open "%s"' % self.cur_plant_path)

    def handle_click_input_proceed(self):
        if self.checkbox_input_var.get():
            logger.debug('Processing input folder')
            self.processor.exec_from_input()
            
        if self.checkbox_paths_var.get():
            logger.debug('Processing paths')
            self.processor.exec_from_paths()

        if self.checkbox_output_var.get():
            logger.debug('Processing output folder')
            self.processor.exec_from_output()

    def handle_click_edit_paths(self):
        paths_file_path = os.path.join(
            os.getcwd(), 
            self.config['PATHS']['paths_file']
        )
        # TODO next line is definitely not cross platform
        os.system('gedit %s' % paths_file_path)

    def handle_select_genus(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            genus_selection = event.widget.get(index)
            genus_search = re.search(r'^(\w+) \[\d+\]$', genus_selection)
            if genus_search:
                genus = genus_search.group(1)
            else:
                print('Something wrong with genus name')
                genus = genus_selection

            self.__clear_frame(self.frame_bottom_center)
            self.__fill_frame_scroll_two(self.frame_bottom_center, genus)

    def handle_select_plant(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.cur_uid = self.uid_species_reference[index]
            img_paths = self.folders.get_img_paths(self.cur_uid)

            self.__clear_frame(self.frame_bottom_right)
            self.__clear_frame(self.frame_top_right)
            self.__show_images(self.frame_bottom_right, img_paths)
            self.__show_plant_info(self.frame_top_right)

    def handle_click_generate_uids(self):
        self.db.fill_empty_uids()
        self.db.reinit()
        self.__update_btn_generate_uids()

    def __update_btn_generate_uids(self):
        self.btn_generate_uids_text.set(f"Generate UIDs [{ self.db.get_number_with_no_uid() }]")

    @staticmethod
    def __open_img_in_default_viewer(path):
        """ Opens image in external image viewer """
        imageViewerFromCommandLine = {'linux':'xdg-open',
                                    'win32':'explorer',
                                    'darwin':'open'}[sys.platform]
        subprocess.run([imageViewerFromCommandLine, path])

    @staticmethod
    def __get_plant_title(data:dict) -> str:
        title = ''
        if 'number' in data:
            title += data['number'] + ' '
        if 'genus' in data:
            title += data['genus'] + ' '
        if 'species' in data:
            title += data['species'] + ' '
        if 'subspecies' in data:
            title += 'ssp. '
            title += data['subspecies']  + ' '
        return title
    
    @staticmethod
    def __clear_frame(frame):
        for widgets in frame.winfo_children():
            widgets.destroy()    

    ### SHOW PLANTS WINDOW

    def handle_click_show_table(self):
        self.window_table = tk.Toplevel(self.root)
        self.window_table.title("Plant List")
        self.window_table.geometry("1000x600") 
        self.__fill_table()

    def __fill_table(self):
        table_frame = tk.Frame(self.window_table)
        table_frame.pack(fill=tk.BOTH, expand=True)

        #scrollbar
        scroll_v = tk.Scrollbar(table_frame)
        scroll_v.pack(side=tk.RIGHT, fill=tk.Y)

        scroll_h = tk.Scrollbar(table_frame,orient='horizontal')
        scroll_h.pack(side=tk.BOTTOM,fill=tk.X)

        self.table = ttk.Treeview(table_frame,yscrollcommand=scroll_v.set, xscrollcommand =scroll_h.set)

        self.table.pack(fill=tk.BOTH, expand=True)

        scroll_v.config(command=self.table.yview)
        scroll_h.config(command=self.table.xview)

        #define our column
        columns = self.db.keys
        if columns[-1] == '\n':
            columns.pop()
        self.table['columns'] = tuple(columns)

        # format our column
        self.table.column("#0", width=0,  stretch=tk.NO)
        for col in columns:
            self.table.column(col, width=100)    


        # create Headings 
        for col in columns: 
            self.table.heading(col, text=col, anchor=tk.CENTER)    
           
    
        #add data 
        data = self.db.get_data()
        for id, uid in enumerate(data):
            item = data[uid]
            values = []
            for key in columns:
                if key in item:
                    values.append(item[key])
                else:
                    values.append('')
            self.table.insert(parent='',index='end',iid=id,text='',values=tuple(values))
        self.table.pack()

        button_generate_labels = tk.Button(table_frame, text="Generate Labels", command=self.handle_click_selected_plants)
        button_open_labels_fld = tk.Button(table_frame, text="Open Labels folder ", command=self.__open_labels_folder)
        # button_show_selected.pack(fill=tk.BOTH,  padx=5)
        button_generate_labels.pack(side=tk.RIGHT, padx=1)
        button_open_labels_fld.pack(side=tk.RIGHT, padx=1)

    def __open_labels_folder(self):
        os.system('xdg-open "%s"' % 'LABELS')

    def handle_click_selected_plants(self):
        Plants = []
        selected_row_ids = self.table.selection()
        for iid in selected_row_ids:
            item = self.table.item(iid)
            plant_data_values = item['values']
            plant_as_dict = {}
            for i, val in enumerate(plant_data_values):
                plant_as_dict[self.db.keys[i].lower()] = val
            plant_as_obj = get_plant_as_obj(plant_as_dict)
            Plants.append(plant_as_obj)

        label_bld = LabelsBuilder(self.folders, Plants)
        label_bld.generate_labels()
        path_to_pdf = label_bld.get_pdf()
        print(path_to_pdf)