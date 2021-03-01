import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import *
from PIL import Image, ImageTk
import voice_recognition as vr
import multiprocessing as mp
import threading
import queue
import os
import sys
from screeninfo import get_monitors

class Application:
    """This is the documentation for Application"""
    root = tk.Tk()
    width = 1600
    height = 900
    menu_bar = tk.Menu(root)
    menu_file = tk.Menu(menu_bar, tearoff=0)
    menu_edit = tk.Menu(menu_bar, tearoff=0)
    menu_voice = tk.Menu(menu_bar, tearoff=0)
    menu_help = tk.Menu(menu_bar, tearoff=0)
    master = tk.Frame(root)
    txt_editor_field = tk.Text(master)
    file = None    
    
    def __init__(self,**kwargs):
        # Set icon 
        try: 
            self.root.wm_iconbitmap("Notepad.ico")  
        except: 
            pass
  
        # Set window size (the default is 300x300) 
  
        try: 
            self.thisWidth = kwargs['width'] 
        except KeyError: 
            pass
  
        try: 
            self.thisHeight = kwargs['height'] 
        except KeyError: 
            pass

        # Set the window text 
        self.root.title("Untitled - VOCODER") 

        # Center the window 
        screenWidth = self.root.winfo_screenwidth() 
        screenHeight = self.root.winfo_screenheight() 
      
        # For left-alling 
        left = (screenWidth / 2) - (self.width / 2)  
          
        # For right-allign 
        top = (screenHeight / 2) - (self.height /2)  
          
        # For top and bottom 
        '''
        self.root.geometry('%dx%d+%d+%d' % (self.width, 
                                              self.height, 
                                              left, top))  
        '''
        self.root.geometry(f"{self.thisWidth}x{self.thisHeight}")
        self.root.grid_rowconfigure(0, weight=1) 
        self.root.grid_columnconfigure(0, weight=1) 

        self.master.grid(sticky=tk.N+tk.S+tk.E+tk.W)

        # Making the App window resizeable
        top=self.master.winfo_toplevel()                
        top.rowconfigure(0, weight=1)            
        top.columnconfigure(0, weight=1)  
        self.master.rowconfigure(0, weight=1)           
        self.master.columnconfigure(0, weight=1)

        ## Header
        self.header = tk.Frame(self.master, borderwidth=2, relief="ridge")
        self.render = ImageTk.PhotoImage(file="assets/vocoder_icon_title.png")
        self.img = tk.Label(self.header,image=self.render)
        self.img.pack()
        self.header.grid(row=0,padx=5,pady=5,sticky='nsew')
        self.header.bind("<Configure>", self.image_resizer)
        ## Menu Bar
        
        ## Add functionalities to Menu options

        # File option
        self.menu_file.add_command(label="New", command=self.newFile)
        self.menu_file.add_command(label="Open", command=self.openFile)
        self.menu_file.add_command(label="Save", command=self.saveFile)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self.on_closing) 
        self.menu_bar.add_cascade(label="File", menu=self.menu_file)
        
        # Edit option
        self.menu_edit.add_command(label="Cut", command=self.cut)
        self.menu_edit.add_command(label="Copy", command=self.copy)
        self.menu_edit.add_command(label="Paste", command=self.paste)
        self.menu_bar.add_cascade(label="Edit", menu=self.menu_edit)
        
        # Voice option
        self.menu_voice.add_command(label="Set up voice", command=self.setUpVoice)
        self.menu_bar.add_cascade(label="Voice", menu = self.menu_voice)

        # Help option
        self.menu_help.add_command(label="About Notepad", command=self.showAbout)
        self.menu_bar.add_cascade(label="Help", menu=self.menu_help)
        
        self.root.config(menu=self.menu_bar)
        
        ## App_Layout
        self.app_layout = tk.Frame(self.master,width = self.thisWidth, height=int(self.thisHeight*0.8), borderwidth=2, relief="ridge")
        self.app_layout.grid_propagate(False)
        
        ## Voice recorder Frame
        self.voice_recog = tk.LabelFrame(self.app_layout, text = "Voice Recorder",width=int(self.app_layout.winfo_width()*0.3), height=200, borderwidth=2, relief="ridge")
        self.voice_recog.grid_propagate(False)
        self.indicator = tk.Frame(self.voice_recog, width = 2, height=2, borderwidth=0, relief="ridge")
        self.loadgray = Image.open("assets/grayCircle.jpg")
        self.rendergray = ImageTk.PhotoImage(self.loadgray)
        self.imggray = tk.Label(self.indicator,image=self.rendergray)
        self.imggray.image = self.rendergray
        self.imggray.pack()
        self.start_button = tk.Button(self.voice_recog,text="start",command=lambda: self.update_text())
        self.end_button = tk.Button(self.voice_recog,text="end",command=lambda: self.change_indicator())

        #####
        self.cmd_receiver = tk.LabelFrame(self.voice_recog, text="command(s) received",width=500,height=180)
        self.cmd_receiver.grid_propagate(False)
        self.cmd_receiver_txt = tk.Listbox(self.cmd_receiver)
        
        ## System Output
        self.sys_out = tk.LabelFrame(self.app_layout,text="System Output",width=600, height=200, borderwidth=2, relief="ridge")
        self.sys_out.grid_propagate(False)
        self.sys_out_txt = tk.Listbox(self.sys_out)

        ## Command Manager 
        self.cmd_man = tk.LabelFrame(self.app_layout,text="Command Manager",width=600, height=200,borderwidth=2, relief="ridge")
        self.cmd_man.grid_propagate(False)
        self.cmd_man_txt = tk.Listbox(self.cmd_man)

        ## Text Editor
        self.txt_editor = tk.LabelFrame(self.app_layout,text="Text Editor",width=int(self.app_layout.winfo_width()*0.7), height=400,borderwidth=2, relief="ridge")
        self.txt_editor.grid_propagate(False)
        self.txt_editor_field = tk.Text(self.txt_editor, undo=True)

        ## Terminal
        self.terminal = tk.LabelFrame(self.app_layout,text="Terminal",width=1112, height=200,borderwidth=2, relief="ridge")
        self.terminal.grid_propagate(False)
        self.terminal_txt = tk.Listbox(self.terminal)

        ## Help Field
        self.help_field = tk.Text(self.app_layout, height=2, width=30)
        self.help_field.insert(tk.END, "1=Create Array \t2=Create Else Statement Done\t3=Create Else-If Statement \t4=Create If Statement \t5=Create While Loop "+\
                                        "\t6=Create For Loop \t7=Return Statement \t8=Assign Old Variable \t9=Create New Variable\n10=Copy Text \t11=Select Block "+\
                                        "\t12=Select Line \t13=Select Word \t14=Cut Text \t15=Move Cursor \t16=Paste Text \t17=Redo Command "+\
                                        "\t18=Undo Command \t19 Print Statement \t20 Print Variable \t21Create Function")
        self.help_field.grid_propagate(False)
        self.app_layout.grid(row=1,padx=5,pady=5,sticky='nsew')
        self.voice_recog.grid(column=0,row=0,padx=5,pady=5,sticky='nsew')

        ## Packing all the widgets in Voice Recorder
        self.start_button.grid(column=0,row=0)
        self.end_button.grid(column=0,row=2)
        self.indicator.grid(column=0,row=1,padx=3,pady=1,sticky='nsew')
        self.cmd_receiver.grid(column=1,row=0,rowspan=3,sticky='nsew')
        self.cmd_receiver.columnconfigure(0,weight=1)
        self.cmd_receiver.rowconfigure(0,weight=1)
        self.cmd_receiver_txt.grid(row=0,column=0,padx=5,pady=5,sticky='nsew')
        
        ## Packing all the widgets in System Output
        self.sys_out.grid(column=0,row=1,padx=5,pady=5,sticky='nsew')
        self.sys_out.columnconfigure(0,weight=1)
        self.sys_out.rowconfigure(0,weight=1)
        self.sys_out_txt.grid(row=0,column=0,padx=5,pady=5,sticky='nsew')

        ## Packing all the widgets in Command Manager
        self.cmd_man.grid(column=0,row=2,padx=5,pady=5,sticky='nsew')
        self.cmd_man.columnconfigure(0,weight=1)
        self.cmd_man.rowconfigure(0,weight=1)
        self.cmd_man_txt.grid(row=0,column=0,padx=5,pady=5,sticky='nsew')

        ## Packing all the widgets in Text Editor
        self.txt_editor.grid(column=1,row=0,rowspan=2,padx=5,pady=5,sticky='nsew')
        self.txt_editor.columnconfigure(0,weight=1)
        self.txt_editor.rowconfigure(0,weight=1)
        self.txt_editor_field.grid(row=0,column=0,padx=5,pady=5,sticky='nsew')

        ## Packing all the widgets in Terminal
        self.terminal.grid(column=1,row=2,padx=5,pady=5,sticky='nsew')
        self.terminal.columnconfigure(0,weight=1)
        self.terminal.rowconfigure(0,weight=1)
        self.terminal_txt.grid(row=0,column=0,padx=5,pady=5,sticky='nsew')

        ## Packing all the widgets in Help
        self.help_field.grid(row=3,columnspan=3,padx=5,pady=5,sticky='nsew')
        
        
    def showAbout(self):
        tk.messagebox.showinfo("VOCODER", "Binh An Pham\nM Rachel Vanpelt\nSteven Tran")
    
    def openFile(self):
        self.file = askopenfilename(defaultextension=".txt", 
                                      filetypes=[("All Files","*.*"), 
                                        ("Text Documents","*.txt")]) 
  
        if self.file == "": 
              
            # no file to open 
            self.file = None
        else: 
              
            # Try to open the file 
            # set the window title 
            self.root.title(os.path.basename(self.file) + " - VOCODER") 
            self.txt_editor_field.delete(1.0,tk.END) 
  
            file = open(self.file,"r") 
  
            self.txt_editor_field.insert(1.0,file.read()) 
  
            file.close() 

    def newFile(self): 
        self.root.title("Untitled - VOCODER") 
        self.file = None
        self.txt_editor_field.delete(1.0,tk.END) 

    def saveFile(self): 
  
        if self.file == None: 
            # Save as new file 
            self.file = asksaveasfilename(initialfile='Untitled.txt', 
                                            defaultextension=".txt", 
                                            filetypes=[("All Files","*.*"), 
                                                ("Text Documents","*.txt")]) 
  
            if self.file == "": 
                self.file = None

            else: 
                # Try to save the file 
                file = open(self.file,"w") 
                file.write(self.txt_editor_field.get(1.0,tk.END)) 
                file.close() 
                # Change the window title 
                self.root.title(os.path.basename(self.file) + " - VOCODER") 
                  
        else: 
            file = open(self.file,"w") 
            file.write(self.thisTextArea.get(1.0,tk.END)) 
            file.close() 
  
    def cut(self): 
        self.txt_editor_field.event_generate("<<Cut>>") 
  
    def copy(self): 
        self.txt_editor_field.event_generate("<<Copy>>") 
  
    def paste(self): 
        self.txt_editor_field.event_generate("<<Paste>>") 

    def setUpVoice(self):
        tk.messagebox.showinfo("Test")

    def text_queue(self, thread_queue=None):
        result = vr.listen(self.txt_editor_field,self.cmd_receiver_txt,self.cmd_man_txt,self.sys_out_txt)
        thread_queue.put(result)

    def image_resizer(self, e):
        global img1, resized_img1, re_render
        img1 = Image.open("assets/vocoder_icon_title.png")
        resized_img1 = img1.resize((e.width, e.height), Image.ANTIALIAS)
        re_render = ImageTk.PhotoImage(resized_img1)
        self.img.configure(image=re_render)

    def update_text(self):
        self.loadred = Image.open("assets/redCircle.jpg")
        self.renderred = ImageTk.PhotoImage(self.loadred)
        self.imggray.configure(image=self.renderred)
        self.thread_queue = queue.Queue()
        self.new_thread = threading.Thread(
            target=self.text_queue,
            kwargs={'thread_queue':self.thread_queue})
        self.new_thread.start()
        self.root.after(1, self.listen_for_result)

    def listen_for_result(self):
        try:
            text = self.thread_queue.get(0)
            if text == "":
                self.sys_out_txt.insert(tk.END,"No command received. Please say a commands!")
                self.imggray.configure(image=self.rendergray)
            elif text == "*":
                self.txt_editor_field.insert(tk.INSERT, "")
                self.imggray.configure(image=self.rendergray)
            else:
                self.txt_editor_field.insert(tk.INSERT, text)
                self.imggray.configure(image=self.rendergray)
        except queue.Empty:
            self.root.after(1, self.listen_for_result)

    ## Handling end/compile buttons
    def change_indicator(self):
        vr.test_compiler(self.txt_editor_field.get(1.0,tk.END), self.terminal)
        self.imggray.configure(image=self.rendergray) 
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            os.popen('find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf')
            self.root.destroy()
    
def main():
    dimension = []
    for m in get_monitors():
        if m.x == 0 and m.y == 0:
            dimension.append(m.width)
            dimension.append(m.height)
    app = Application(width=dimension[0], height=dimension[1])
    #app = Application(width=1600, height=900)
    app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.root.mainloop()

if __name__ == "__main__":
    main()
