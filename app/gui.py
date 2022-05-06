import os
import tkinter as tk
from configparser import ConfigParser
import logging

from .folders import FolderStructure
from .sources import Source
from .processor import Processor

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class Gui:

    def __init__(self, config: ConfigParser, folders: FolderStructure, processor: Processor) -> None:
        self.config = config
        self.folders = folders
        self.processor = processor
        self.source = Source(self.config)
        self.root = tk.Tk() 
        self.root.title("Data Matrix Sorter and Labeler")
        self.root.geometry("1000x600") 
        self.main_frame = tk.Frame(self.root)

        self.checkbox_input_var = tk.IntVar()
        self.checkbox_paths_var = tk.IntVar()
        self.checkbox_output_var = tk.IntVar()


    def get_block_input_img(self, col, row):
        input_frame = tk.LabelFrame(self.main_frame, text='Input photos')
        # input_frame.pack(side=tk.LEFT)
        
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

        input_frame.grid(column=0, row=0)


    def get_block_input_reference(self, col, row):
        input_frame = tk.LabelFrame(self.main_frame, text='Input reference file')
        #input_frame.pack(side=tk.LEFT,  padx=5)

        label_reference = tk.Label(input_frame, text='245 lines, UID for 12 is needed')
        label_reference.pack()

        button_generate_labels = tk.Button(input_frame, text="Generate Labels")
        button_generate_labels.pack()

        button_generate_uids = tk.Button(input_frame, text="Generate UIDs")
        button_generate_uids.pack()

        input_frame.grid(column=1, row=0)


    def get_bloc_scroll_one(self):
        myscroll = tk.Scrollbar(self.root) 
        myscroll.pack(side = tk.RIGHT, fill = tk.Y) 
        
        mylist = tk.Listbox(self.root, yscrollcommand = myscroll.set )  
        for line in range(1, 100): 
            mylist.insert(tk.END, "Number " + str(line)) 
        mylist.pack(side = tk.LEFT, fill = tk.BOTH )    
        
        myscroll.config(command = mylist.yview) 


    def maingrid(self):
        
        self.get_block_input_img(col=0, row=0)
        self.get_block_input_reference(col=1, row=0)

    

    def mainloop(self):
        self.root.mainloop() 


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



if __name__ == '__main__':
    main()
