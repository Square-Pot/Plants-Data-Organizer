from tkinter import *
   
root = Tk() 
root.geometry("200x250") 
    
mylabel = Label(root, text ='Scrollbars', font = "30")  
mylabel.pack() 
 
myscroll = Scrollbar(root) 
myscroll.pack(side = RIGHT, fill = Y) 
 
mylist = Listbox(root, yscrollcommand = myscroll.set )  
for line in range(1, 100): 
    mylist.insert(END, "Number " + str(line)) 
mylist.pack(side = LEFT, fill = BOTH )    
 
myscroll.config(command = mylist.yview) 
    
root.mainloop() 