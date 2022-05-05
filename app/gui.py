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
        
        button_input_output = tk.Button(input_frame, text="Proceed", command=self.handle_click_input_proceed)
        button_input_output.pack()

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
        if self.checkbox_input_var:
            print('Input proceed')
        if self.checkbox_paths_var:
            print('Paths proceed')
        if self.checkbox_output_var:
            print('Output proceed')



if __name__ == '__main__':
    main()
