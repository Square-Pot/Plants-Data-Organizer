import os
import sys
import subprocess
from configparser import ConfigParser
import logging
import tkinter as tk
from turtle import width
from PIL import Image, ImageTk

from .folders import FolderStructure
from .sources import Source
from .processor import Processor
from .db import DB

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

        frame_top_left = tk.Frame(self.root, width=left_col_width, height=top_row_height, pady=padding, padx=padding)
        frame_top_center = tk.Frame(self.root, width=center_col_width, height=top_row_height, pady=padding, padx=padding)
        frame_top_right = tk.Frame(self.root, width=rigth_col_width, height=top_row_height, pady=padding, padx=padding)
        frame_bottom_left = tk.Frame(self.root, width=left_col_width, height=bottom_row_hight, pady=padding, padx=padding)
        frame_bottom_center = tk.Frame(self.root, width=center_col_width, height=bottom_row_hight, pady=padding, padx=padding)
        frame_bottom_right = tk.Frame(self.root, width=rigth_col_width, height=bottom_row_hight, pady=padding, padx=padding)

        frame_top_left.grid(row=0, column=0, sticky='nesw')
        frame_top_center.grid(row=0, column=1, sticky='nesw')
        frame_top_right.grid(row=0, column=2,  sticky='nesw')
        frame_bottom_left.grid(row=1, column=0, sticky='ns')
        frame_bottom_center.grid(row=1, column=1, sticky='ns')
        frame_bottom_right.grid(row=1, column=2, sticky='nesw')

        self.__fill_frame_input(frame_top_left)
        self.__fill_frame_db(frame_top_center)
        self.__fill_frame_scroll_one(frame_bottom_left)
        self.__fill_frame_scroll_two(frame_bottom_center)
        self.frame_bottom_center = frame_bottom_center
        self.frame_bottom_right = frame_bottom_right

        self.uid_species_reference = None

    def mainloop(self):
        self.root.mainloop() 

    def __fill_frame_input(self, frame):
        input_frame = tk.LabelFrame(frame, text='Input photos')
            
        checkbox_input = tk.Checkbutton(input_frame, text=f'Input folder [{ self.source.count_input() }]', variable=self.checkbox_input_var)
        if int(self.config['SOURCES']['input_folder']):
            checkbox_input.select()
        checkbox_input.pack(anchor=tk.W, padx=5)

        checkbox_paths = tk.Checkbutton(input_frame, text=f'Paths [{ self.source.count_input() }]', variable=self.checkbox_paths_var)
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

        label_reference = tk.Label(input_frame, text='245 lines, UID for 12 is needed')
        label_reference.pack(padx=5, pady=10)

        button_generate_labels = tk.Button(input_frame, text="Generate Labels")
        button_generate_labels.pack(fill=tk.BOTH,  padx=5)

        button_generate_uids = tk.Button(input_frame, text="Generate UIDs")
        button_generate_uids.pack(fill=tk.BOTH,  padx=5)

        input_frame.pack(side=tk.LEFT, fill=tk.Y)

    def __fill_frame_scroll_one(self, frame):
        genus_scrollbar = tk.Scrollbar(frame) 
        genus_listbox = tk.Listbox(frame, yscrollcommand = genus_scrollbar.set, width=25)  
        genus_list = self.db.get_genus_list()
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
        thumb_min = int(self.config['GUI']['thumbnail_size'])

        max_photos_in_row = frame_width // thumb_min

        num_photos_in_row = 0
        cur_row = 1
        cur_col = 0
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
            label = tk.Label(frame, image = photo)
            label.image = photo

            num_photos_in_row += 1
            cur_col += 1

            if num_photos_in_row > max_photos_in_row:
                cur_row += 1
                cur_col = 1

            label.grid(row=cur_row, column=cur_col)

            label.bind("<Button-1>",lambda e,path=path:self.__open_img_in_default_viewer(path))
            i += 1

        self.cur_plant_path = os.path.dirname(os.path.abspath(path))
        button_open_folder = tk.Button(frame, text="Open containing folder", command=self.__open_folder)
        button_open_folder.grid(column=1, row=cur_row + 1, pady=10)


    @staticmethod
    def __clear_frame(frame):
        for widgets in frame.winfo_children():
            widgets.destroy()

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
            genus = event.widget.get(index)
            self.__clear_frame(self.frame_bottom_center)
            self.__fill_frame_scroll_two(self.frame_bottom_center, genus)

    def handle_select_plant(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            uid = self.uid_species_reference[index]
            img_paths = self.folders.get_img_paths(uid)

            self.__clear_frame(self.frame_bottom_right)
            self.__show_images(self.frame_bottom_right, img_paths)

    @staticmethod
    def __open_img_in_default_viewer(path):
        """ Opens image in external image viewer """
        imageViewerFromCommandLine = {'linux':'xdg-open',
                                    'win32':'explorer',
                                    'darwin':'open'}[sys.platform]
        subprocess.run([imageViewerFromCommandLine, path])


    def __open_folder(self):
        os.system('xdg-open "%s"' % self.cur_plant_path)

