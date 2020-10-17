import tkinter as tk
from PIL import Image, ImageTk

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        ## Header
        self.header = tk.Frame(self,borderwidth=2, relief="ridge")
        load = Image.open("assets/vocoder_icon.png")
        render = ImageTk.PhotoImage(load)
        img = tk.Label(self.header,image=render)
        img.image = render
        img.pack()
        self.header.grid(row=0)
        ## App_Layout
        self.app_layout = tk.Frame(self)
        ## Voice recoder Frame
        self.voice_recog = tk.LabelFrame(self.app_layout, text = "Voice Recorder",borderwidth=2, relief="ridge")
        self.start_button = tk.Button(self.voice_recog,text="START")
        self.end_button = tk.Button(self.voice_recog,text="END")
        self.noti_label = tk.Label(self.voice_recog, text="Place holder status")
        self.cmd_receiver = tk.LabelFrame(self.voice_recog, text="command(s) received")
        self.cmd_receiver_txt = tk.Listbox(self.cmd_receiver)
        self.add_scrollbar(self.cmd_receiver_txt)
        ## System Output
        self.sys_out = tk.LabelFrame(self.app_layout,text="System Output",borderwidth=2, relief="ridge")
        self.sys_out_txt = tk.Listbox(self.sys_out)
        self.add_scrollbar(self.sys_out_txt)
        ## Command Manager 
        self.cmd_man = tk.LabelFrame(self.app_layout,text="Command Manager",borderwidth=2, relief="ridge")
        self.cmd_man_txt = tk.Listbox(self.cmd_man)
        self.add_scrollbar(self.cmd_man_txt)
        ## Text Editor
        self.txt_editor = tk.LabelFrame(self.app_layout,text="Text Editor",borderwidth=2, relief="ridge")
        self.txt_editor_field = tk.Text(self.txt_editor)
        #self.add_scrollbar(self.txt_editor_field)
        ## Terminal
        self.terminal = tk.LabelFrame(self.app_layout,text="Terminal",borderwidth=2, relief="ridge")
        self.terminal_txt = tk.Listbox(self.terminal)
        self.add_scrollbar(self.terminal_txt)
        ## Help Field
        self.help_field = tk.LabelFrame(self.app_layout,text="Help",borderwidth=2, relief="ridge")
        self.help_field_txt = tk.Listbox(self.help_field)
        ## Packing all the widgets in Voice Recorder
        self.start_button.grid(column=0,row=0)
        self.end_button.grid(column=0,row=1)
        self.noti_label.grid(column=0,row=2)
        self.cmd_receiver_txt.grid(column=0,row=0)
        self.cmd_receiver.grid(column=1,row=0,rowspan=3)
        ## Packing all the widgets in System Output
        self.voice_recog.grid(column=0,row=0)
        self.sys_out.grid(column=0,row=1)
        self.app_layout.grid(row=1)
        self.sys_out_txt.pack()
        self.sys_out.grid(column=0,row=1)
        ## Packing all the widgets in Command Manager
        self.cmd_man_txt.pack()
        self.cmd_man.grid(column=0,row=2)
        ## Packing all the widgets in Text Editor
        self.txt_editor_field.pack()
        self.txt_editor.grid(column=1,row=0,rowspan=2)
        ## Packing all the widgets in Terminal
        self.terminal_txt.pack()
        self.terminal.grid(column=1,row=2)
        ## Packing all the widgets in Help
        self.help_field_txt.pack()
        self.help_field.grid(row=3,column=0,columnspan=2)


    ## Adding scrollbar to Listbox widgets
    def add_scrollbar(self, widget_name):
        widget_name.yScroll = tk.Scrollbar(widget_name, orient=tk.VERTICAL)
        widget_name.yScroll.grid(row=0, column=1, sticky=tk.N+tk.S)
        widget_name.listbox = tk.Listbox(widget_name,
            yscrollcommand=widget_name.yScroll.set)
        widget_name.listbox.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        widget_name.yScroll['command'] = widget_name.listbox.yview
def main():
    root = tk.Tk()
    app = Application(master=root)
    app.master.title("VOCODER")
    app.mainloop()

if __name__ == "__main__":
    main()