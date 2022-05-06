import os
import tkinter as tk
from configparser import ConfigParser

from numpy import source

from .folders import FolderStructure
from .sources import Source
from .processor import Processor


class Gui:

    def __init__(self, config: ConfigParser, folders: FolderStructure, processor: Processor) -> None:
        self.config = config
        self.folders = folders
        self.processor = processor
        self.source = Source(self.config)
        self.root = tk.Tk() 
        self.root.title("Data Matrix Sorter and Labeler")
        self.root.geometry("1000x600") 

        self.checkbox_input_var = tk.IntVar()
        self.checkbox_paths_var = tk.IntVar()
        self.checkbox_output_var = tk.IntVar()
        
    # mylabel = Label(root, text ='Input Data', font = "30")  
    # mylabel.pack() 


    def get_block_input_img(self):
        input_frame = tk.LabelFrame(self.root, text='Input photos:')
        input_frame.pack(anchor=tk.W)
        
        checkbox_input = tk.Checkbutton(input_frame, text=f'Input folder [{ self.source.count_input() }]', variable=self.checkbox_input_var)
        if int(self.config['SOURCES']['input_folder']):
            checkbox_input.select()
        checkbox_input.pack(anchor=tk.W)

        checkbox_paths = tk.Checkbutton(input_frame, text=f'Paths [{ self.source.count_input() }]', variable=self.checkbox_paths_var)
        if int(self.config['SOURCES']['paths']):
            checkbox_paths.select()
        checkbox_paths.pack(anchor=tk.W)

        checkbox_output = tk.Checkbutton(input_frame, text=f'Output folder [{ self.source.count_output(self.folders) }]', variable=self.checkbox_output_var)
        if int(self.config['SOURCES']['output_folder']):
            checkbox_output.select()
        checkbox_output.pack(anchor=tk.W)

        button_edit_paths = tk.Button(input_frame, text="Edit Paths", command=self.handle_click_edit_paths)
        button_edit_paths.pack()

        button_input_output = tk.Button(input_frame, text="Proceed", command=self.handle_click_input_proceed)
        button_input_output.pack()

    def get_block_input_reference(self):
        input_frame = tk.LabelFrame(self.root, text='Input reference file:')
        input_frame.pack()

        label_reference = tk.Label(input_frame, text='245 lines, UID for 12 is needed')
        label_reference.pack()

        button_generate_labels = tk.Button(input_frame, text="Generate Labels")
        button_generate_labels.pack()

        button_generate_uids = tk.Button(input_frame, text="Generate UIDs")
        button_generate_uids.pack()


    def get_bloc_scroll_one(self):
        myscroll = tk.Scrollbar(self.root) 
        myscroll.pack(side = tk.RIGHT, fill = tk.Y) 
        
        mylist = tk.Listbox(self.root, yscrollcommand = myscroll.set )  
        for line in range(1, 100): 
            mylist.insert(tk.END, "Number " + str(line)) 
        mylist.pack(side = tk.LEFT, fill = tk.BOTH )    
        
        myscroll.config(command = mylist.yview) 
    
    def mainloop(self):
        self.root.mainloop() 

    def handle_click_input_proceed(self):
        if self.checkbox_input_var.get():
            print('Input proceed', self.checkbox_input_var.get())
        if self.checkbox_paths_var.get():
            print('Paths proceed', self.checkbox_paths_var.get())
        if self.checkbox_output_var.get():
            print('Output proceed', self.checkbox_output_var.get())

    def handle_click_edit_paths(self):
        paths_file_path = os.path.join(
            os.getcwd(), 
            self.config['PATHS']['paths_file']
        )
        print(paths_file_path)
        # TODO next line is definitely not cross platform
        os.system('gedit %s' % paths_file_path)



if __name__ == '__main__':
    main()
