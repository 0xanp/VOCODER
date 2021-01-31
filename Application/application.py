import tkinter as tk
from PIL import Image, ImageTk
import voice_recognition as vr
import multiprocessing as mp
import threading
import queue

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        # Making the App window resizeable
        top=self.winfo_toplevel()                
        top.rowconfigure(0, weight=1)            
        top.columnconfigure(0, weight=1)         
        self.rowconfigure(0, weight=1)           
        self.columnconfigure(0, weight=1)

        ## Header
        self.header = tk.Frame(self, borderwidth=2, relief="ridge")
        load = Image.open("assets/vocoder_icon_title.png")
        render = ImageTk.PhotoImage(load)
        img = tk.Label(self.header,image=render)
        img.image = render
        img.pack()
        self.header.grid(row=0,padx=5,pady=5,sticky='nsew')
        
        ## App_Layout
        self.app_layout = tk.Frame(self,width = 1727, height=700, borderwidth=2, relief="ridge")
        self.app_layout.grid_propagate(False)
        
        ## Voice recorder Frame
        self.voice_recog = tk.LabelFrame(self.app_layout, text = "Voice Recorder",width=600, height=200, borderwidth=2, relief="ridge")
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
        self.txt_editor = tk.LabelFrame(self.app_layout,text="Text Editor",width=1112, height=400,borderwidth=2, relief="ridge")
        self.txt_editor.grid_propagate(False)
        self.txt_editor_field = tk.Text(self.txt_editor)

        ## Terminal
        self.terminal = tk.LabelFrame(self.app_layout,text="Terminal",width=1112, height=200,borderwidth=2, relief="ridge")
        self.terminal.grid_propagate(False)
        self.terminal_txt = tk.Listbox(self.terminal)

        ## Help Field
        self.help_field = tk.Text(self.app_layout, height=2, width=30)
        self.help_field.insert(tk.END, "1=Create Array \t2=Create Else Statement \t3=Create Else-If Statement \t4=Create If Statement \t5=Create While Loop "+\
                                        "\t6=Create For Loop \t7=Return Statement \t8=Assign Old Variable \t9=Create New Variable\n10=Copy Text \t11=Select Block "+\
                                        "\t12=Select Line \t13=Select Word \t14=Move to Word \t15=Move Cursor \t16=Paste Text \t17=Redo Command "+\
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
    
    def text_queue(self, thread_queue=None):
        result = vr.listen(self.txt_editor_field,self.cmd_receiver_txt,self.cmd_man_txt,self.sys_out_txt)
        thread_queue.put(result)

    def update_text(self):
        self.loadred = Image.open("assets/redCircle.jpg")
        self.renderred = ImageTk.PhotoImage(self.loadred)
        self.imggray.configure(image=self.renderred)
        self.thread_queue = queue.Queue()
        self.new_thread = threading.Thread(
            target=self.text_queue,
            kwargs={'thread_queue':self.thread_queue})
        self.new_thread.start()
        self.after(100, self.listen_for_result)

    def listen_for_result(self):
        try:
            self.txt_editor_field.insert(tk.END, self.thread_queue.get(0))
        except queue.Empty:
            self.after(100, self.listen_for_result)
    
    ## Handling end/compile buttons
    def change_indicator(self):
        vr.test_compiler(self.txt_editor_field.get(1.0,tk.END), self.terminal)
        self.imggray.configure(image=self.rendergray) 
            
def main():
    root = tk.Tk()
    app = Application(master=root)
    app.master.title("VOCODER")
    app.mainloop()
    
if __name__ == "__main__":
    main()