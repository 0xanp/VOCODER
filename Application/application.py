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
import glob
import shutil
import time
import sounddevice as sd
from scipy.io.wavfile import write
from pydub import AudioSegment
from pydub.playback import play
from screeninfo import get_monitors

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class TextLineNumbers(tk.Canvas):
    """Custom object to handle the drawing of the number line"""
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs, highlightthickness=0)
        self.textwidget = None

    def attach(self, text_widget):
        """Attach new drawn object back to the text editor"""
        self.textwidget = text_widget

    def redraw(self, *args):
        """Redraw line numbers"""
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum, fill="#606366")
            i = self.textwidget.index("%s+1line" % i)



class Application:
    """This is the documentation for Application"""
    root = Tk()
    width = 1600
    height = 900
    menu_bar = tk.Menu(root)
    menu_file = tk.Menu(menu_bar, tearoff=0)
    menu_edit = tk.Menu(menu_bar, tearoff=0)
    menu_voice = tk.Menu(menu_bar, tearoff=0)
    menu_help = tk.Menu(menu_bar, tearoff=0)
    master = tk.Frame(root,bg='#2b2b2b')
    file = None
    useGoogle = False
    lineNumber = 0    
    
    def __init__(self,**kwargs):
        # Set icon 
        try: 
            self.root.wm_iconbitmap("Notepad.ico")  
        except: 
            pass
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
        self.header = tk.Frame(self.master, borderwidth=2, relief="ridge",bg='#2b2b2b')
        self.render = ImageTk.PhotoImage(file=resource_path("assets/vocoder_icon_titledark.png"))
        self.img = tk.Label(self.header,image=self.render)
        self.img.pack()
        self.header.grid(row=0,padx=5,pady=5,sticky='nsew')
        self.header.bind("<Configure>", self.image_resizer)


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
        self.menu_voice.add_command(label="Record voice lines", command=self.recordVoiceLines)
        self.menu_voice.add_command(label="Train language model", command=self.trainLanguageModel)
        self.menu_voice.add_command(label="Choose language model", command=self.chooseLanguageModel)
        self.menu_bar.add_cascade(label="Voice", menu = self.menu_voice)

        # Help option
        self.menu_help.add_command(label="About Notepad", command=self.showAbout)
        self.menu_bar.add_cascade(label="Help", menu=self.menu_help)
        
        self.root.config(menu=self.menu_bar)
        
        ## App_Layout
        self.app_layout = tk.Frame(self.master,width = self.thisWidth, height=int(self.thisHeight*0.8), borderwidth=2, relief="ridge",bg='#2b2b2b')
        self.app_layout.rowconfigure(0,weight=1)
        self.app_layout.columnconfigure(0,weight=1)
        self.app_layout.grid_propagate(False)
        
        ## Voice recorder Frame
        self.voice_recog = tk.LabelFrame(self.app_layout, text = "Voice Recorder", borderwidth=2, relief="ridge",bg='#2b2b2b',foreground="#d1dce8")
        self.voice_recog.grid_propagate(False)
        self.indicator = tk.Frame(self.voice_recog, width = 2, height=2, bg='#2b2b2b')
        self.loadgray = Image.open(resource_path("assets/grayCircle.jpg"))
        self.rendergray = ImageTk.PhotoImage(self.loadgray)
        self.imggray = tk.Label(self.indicator,image=self.rendergray, pady=0, padx=0, borderwidth=0, highlightthickness=0)
        self.imggray.image = self.rendergray
        self.imggray.pack()
        self.start_button = tk.Button(self.voice_recog,text="start",command=lambda: self.update_text(),bg='#2b2b2b',foreground="#d1dce8")
        self.end_button = tk.Button(self.voice_recog,text="end",command=lambda: self.change_indicator(),bg='#2b2b2b',foreground="#d1dce8")
        self.cmd_receiver = tk.LabelFrame(self.voice_recog, text="command(s) received",width=700,height=355,bg='#2b2b2b',foreground="#d1dce8")
        self.cmd_receiver.grid_propagate(False)
        self.cmd_receiver_txt = tk.Listbox(self.cmd_receiver,bg='#2b2b2b',foreground="#d1dce8")
        
        ## System Output
        self.sys_out = tk.LabelFrame(self.app_layout,text="System Output",width=600, height=200,relief="ridge",bg='#2b2b2b',foreground="#d1dce8")
        self.sys_out.grid_propagate(False)
        self.sys_out_txt = tk.Listbox(self.sys_out,bg='#2b2b2b',foreground="#d1dce8")

        ## Command Manager 
        self.cmd_man = tk.LabelFrame(self.app_layout,text="Command Manager",width=600, height=200,borderwidth=2, relief="ridge",bg='#2b2b2b',foreground="#d1dce8")
        self.cmd_man.grid_propagate(False)
        self.cmd_man_txt = tk.Listbox(self.cmd_man,bg='#2b2b2b',foreground="#d1dce8")

        ## Text Editor
        self.txt_editor = tk.LabelFrame(self.app_layout,text='Editor', width=int(self.app_layout.winfo_width()*0.7), height=400,borderwidth=2, relief="ridge",bg='#2b2b2b',foreground="#d1dce8")
        self.txt_editor.grid_propagate(False)
        self.txt_editor_field = tk.Text(self.txt_editor, bg='#2b2b2b', foreground="#d1dce8", 
                        insertbackground='white',
                        selectbackground="blue", undo=True)
        
        self.scrollbar = tk.Scrollbar(self.txt_editor, orient=tk.VERTICAL, command=self.txt_editor_field.yview,bg='#2b2b2b')
        self.txt_editor_field.configure(yscrollcommand=self.scrollbar.set)

        self.numberLines = TextLineNumbers(self.txt_editor, width=35, bg='#313335')
        self.numberLines.attach(self.txt_editor_field)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.numberLines.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
        self.txt_editor_field.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.txt_editor_field.bind("<Key>", self.onPressDelay)
        self.txt_editor_field.bind("<Button-1>", self.numberLines.redraw)
        self.scrollbar.bind("<Button-1>", self.onScrollPress)
        self.txt_editor_field.bind("<MouseWheel>", self.onPressDelay)

        ## Terminal
        self.terminal = tk.LabelFrame(self.app_layout,text="Terminal",width=1112, height=200,borderwidth=2, relief="ridge",bg='#2b2b2b',foreground="#d1dce8")
        self.terminal.grid_propagate(False)
        self.terminal_txt = tk.Listbox(self.terminal,bg='#2b2b2b',foreground="#d1dce8")

        ## Help Field
        self.help_field = tk.Text(self.app_layout, height=2, width=30,bg='#2b2b2b',foreground="#d1dce8")
        self.help_field.insert(tk.END, "1=Create Array \t2=Create Else Stmnt Done\t3=Create Else-If Stmnt \t4=Create If Stmnt \t5=Create While Loop "+\
                                        "\t6=Create For Loop \t7=Return Stmnt \t8=Assign Old Var \t9=Create New Var \t10=Copy Txt \t11=Select Block "+\
                                        "\t12=Select Line \t13=Select Word \n14=Cut Txt \t15=Move Cursor \t16=Paste Txt \t17=Redo Command \t18=Undo Command "+\
                                        "\t19=Print Stmnt \t20=Print Var \t21=Create Func \t22=Indent Cursor \t23=Insert Chars")
        self.help_field.grid_propagate(False)
        self.help_field.config(state=DISABLED)
        self.app_layout.grid(row=1,padx=5,pady=5,sticky='nsew')
        self.voice_recog.grid(column=0,row=0,padx=5,pady=5,sticky='nsew')

        ## Packing all the widgets in Voice Recorder
        self.start_button.grid(column=0,row=0)
        self.end_button.grid(column=0,row=1)
        self.indicator.grid(column=0,row=2)
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
        #self.txt_editor_field.grid(row=0,column=0,padx=5,pady=5,sticky='nsew')

        ## Packing all the widgets in Terminal
        self.terminal.grid(column=1,row=2,padx=5,pady=5,sticky='nsew')
        self.terminal.columnconfigure(0,weight=1)
        self.terminal.rowconfigure(0,weight=1)
        self.terminal_txt.grid(row=0,column=0,padx=5,pady=5,sticky='nsew')

        ## Packing all the widgets in Help
        self.help_field.grid(row=3,columnspan=3,padx=5,pady=5,sticky='nsew')
        
        
    def showAbout(self):
        """Handling about option for the menu""" 
        tk.messagebox.showinfo("VOCODER", "Binh An Pham\nM Rachel Van Pelt\nSteven Tran")
    
    def openFile(self):
        """Handling open file option for the menu""" 
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
        """Handling new file option for the menu""" 
        self.root.title("Untitled - VOCODER") 
        self.file = None
        self.txt_editor_field.delete(1.0,tk.END) 

    def saveFile(self):
        """Handling save file option for the menu""" 
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
            file.write(self.txt_editor_field.get(1.0,tk.END)) 
            file.close() 
  
    def cut(self): 
        """Handling cut event for the text editor"""
        self.txt_editor_field.event_generate("<<Cut>>") 
  
    def copy(self): 
        """Handling copy event for the text editor"""
        self.txt_editor_field.event_generate("<<Copy>>") 
  
    def paste(self): 
        """Handling paste event for the text editor"""
        self.txt_editor_field.event_generate("<<Paste>>") 

    # Connected with the nameButton button in trainLanguageModel()
    #
    # Function to inform the user if a directory with given name already exists in VoiceTraining/AcousticModels/
    def checkNameButton(self, inputString = None, window=None):
        """Checks to see if there is a directory with the name of inputString in the path of VoiceTraining/AcousticModels/"""

        profileName = inputString

        # If no text was passed into this function, display messagebox and exit function
        if inputString == None:
            tk.messagebox.showinfo("No name was inputted.")
            return

        # Check if inputString is a preexisting directory in VoiceTraining/AcousticModels/ and display the relevant messagebox    
        isdir = os.path.isdir("VoiceTraining/AcousticModels/" + profileName)
        if isdir == False:
            proceed = tk.messagebox.showinfo("Voice Training", inputString + " was not found. " + inputString + " will be created as a new language model.")
        else:
            proceed = tk.messagebox.showinfo("Voice Training", inputString + " was found as an already existing directory. " + inputString + " will be overwritten.")
        
        window.lift()

    # Connected with the trainButton button in trainLanguageModel()
    #
    # Function to create/overwrite a directory using a given name and directory inside VoiceTraining/AcousticModels/
    def trainModelButton(self, profileName = None, directoryName = None, window=None):
        """Takes in a profileName and directoryName, adapts the language model with the profileName using the voice lines from directoryName"""

        # If profileName does not already exist, creates a new directory with that name
        isdir = os.path.isdir("VoiceTraining/AcousticModels/" + profileName)
        if isdir == False:
            os.mkdir("VoiceTraining/AcousticModels/" + profileName)
        
        # Gets the needed file name from directoryName
        dirPath = "VoiceTraining/TrainingModel/" + directoryName
        for file in glob.glob(r"VoiceTraining/TrainingModel/" + directoryName + "/*.fileids"):
            fileName = file.split("\\")
            fileName = fileName[1]
            fileName = fileName.split(".")
            fileName = fileName[0]
            print(fileName)

        idsName = fileName + ".fileids"
        transName = fileName + ".transcription"

        # Creates .mfc files from current .wav files
        os.system("sphinx_fe " + 
                    "-argfile VoiceTraining/AcousticModels/en-us/feat.params " +
                    "-samprate 16000 " +
                    "-c " + dirPath + "/" + idsName + " "
                    "-di " + dirPath + "/ " +
                    "-do " + dirPath + "/ " +
                    "-ei wav " + 
                    "-eo mfc " + 
                    "-mswav yes")

        # Create gauden_counts, mixw_counts, and tmat_counts from the .mfc files
        os.chdir(dirPath)
        os.system("bw " +
                    "-hmmdir ../../AcousticModels/en-us " +
                    "-moddeffn ../../AcousticModels/en-us/mdef.txt " +
                    "-ts2cbfn .ptm. " +
                    "-feat 1s_c_d_dd " +
                    "-svspec 0-12/13-25/26-38 " +
                    "-cmn current " +
                    "-agc none " +
                    "-dictfn ../../cmudict-en-us.dict " +
                    "-ctlfn " + idsName + " " +
                    "-lsnfn " + transName + " " +
                    "-accumdir .")
        os.chdir("../../..")

        # Copy files from default language model to new language model
        for file in glob.glob(r"VoiceTraining/AcousticModels/en-us/*"):
            shutil.copy(file, "VoiceTraining/AcousticModels/" + profileName)

        # Adapt the copied files in the new language model
        os.system("map_adapt " +
                    "-moddeffn VoiceTraining/AcousticModels/en-us/mdef.txt " +
                    "-ts2cbfn .ptm. " +
                    "-meanfn VoiceTraining/AcousticModels/en-us/means " +
                    "-varfn VoiceTraining/AcousticModels/en-us/variances " +
                    "-mixwfn VoiceTraining/AcousticModels/en-us/mixture_weights " +
                    "-tmatfn VoiceTraining/AcousticModels/en-us/transition_matrices " +
                    "-accumdir " + dirPath + " " +
                    "-mapmeanfn VoiceTraining/AcousticModels/" + profileName + "/means " +
                    "-mapvarfn VoiceTraining/AcousticModels/" + profileName + "/variances " +
                    "-mapmixwfn VoiceTraining/AcousticModels/" + profileName + "/mixture_weights " +
                    "-maptmatfn VoiceTraining/AcousticModels/" + profileName + "/transition_matrices")

        print("New adapted language model created!")
        tk.messagebox.showinfo(message="New adapted language model created!")

        window.destroy()

    # 2nd Option under Voice Training menu
    # Creates a new window with a field to enter a name, button connected to checkNameButton(), another button connected to trainModelButton(), 
    # and a list of radio buttons representing directory names in VoiceTraining/TrainingModel
    #
    # Allows the user to enter a name into the text field and choose one of the radio buttons
    # After entering a name, if user clicks the check name button, will inform the user if a directory with that name already exists in VoiceTraining/AcousticModels
    # After entering a name and choosing a radio button, if user clicks on the train model button, will create/overwrite a language model with that name using the 
    # chosen training model from the list of radio buttons
    def trainLanguageModel(self):
        """Window frame to train a language model. Includes a text field to enter name of language model, radiobutton options to choose which directory has the voice lines to use to train, a button to check the language model name, and a button to train the model. """

        win = tk.Toplevel()
        win.wm_title("Voice Adaption")

        # LabelFrame for the name of language model to train.
        modelNameLabelFrame = tk.LabelFrame(win, text="Enter the name you want to use for the language model, click the button to check if it's available.", width=600, height=10, borderwidth=2, relief="ridge")
        modelNameLabelFrame.grid(column=0, columnspan=2, padx=10, pady=10, ipadx=35, ipady=10)
        # Label for "Name"
        nameLabel = tk.Label(modelNameLabelFrame, text="Name:")
        nameLabel.grid(row=0, column=0, padx=10, pady=10)
        # Text field to input name of model
        nameTextField = tk.Entry(modelNameLabelFrame)
        nameTextField.grid(row=0, column=1, ipadx=80, ipady=5)
        # Button to check for model name availability
        nameButton = tk.Button(modelNameLabelFrame, text="Check Availability", command=lambda: self.checkNameButton(inputString=nameTextField.get(), window=win))
        nameButton.grid(row=0, column=2, padx=10, sticky="W")
        
        # LabelFrame for target directory and train button
        targetDirLabelFrame = tk.LabelFrame(win, text="Choose the directory containing the recorded voice lines that you want to use to train the language model.", width=600, height=10, borderwidth=2, relief="ridge")
        targetDirLabelFrame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, ipadx=10, ipady=10)
        # Radiobutton for list of directories to choose from
        trainPath = "VoiceTraining/TrainingModel"
        listOfDirs = os.listdir(trainPath)
        dirNameChoice = tk.StringVar()
        dirNameChoice.set("None")

        for dirName in listOfDirs:
            tk.Radiobutton(targetDirLabelFrame, text=dirName, variable=dirNameChoice, value=dirName, indicatoron=0, width=20, padx=20).pack()

        # Button to start training the language model
        trainButton = tk.Button(win, text="Train the language model!", command=lambda: self.trainModelButton(profileName=nameTextField.get(), directoryName=dirNameChoice.get(), window=win))
        trainButton.grid(row=2,column=0, padx=225, pady=10, sticky="nsew")

    # Connected to prevButton button in recordingVoice()
    #
    # Gets the previous line and displays it to the window, if there is no previous line, informs the user of that
    def getPrevLine(self, listOfLines=None, textLabel=None, fileNameLabel=None, window=None):
        index = self.lineNumber
        #print("len(listOfLines) = " + str(len(listOfLines)) + ", index = " + str(index))
        if (index == 0):
            tk.messagebox.showinfo(message="The first line of the file is already being displayed.")
            window.lift()
            return()

        index -= 1

        fileName = listOfLines[index][0]
        fileText = listOfLines[index][1]
        
        #string = listOfLines[index][0] + " : " + listOfLines[index][1]
        textLabel.config(text=fileText)
        textLabel.update()
        fileNameLabel.config(text=fileName)
        fileNameLabel.update()

        self.lineNumber = index

    # Connected to nextButton button in recordingVoice()
    #
    # Gets the next line and displays it to the window, if there is no next line, informs the user of that
    def getNextLine(self, listOfLines=None, textLabel=None, fileNameLabel=None, window=None):
        index = self.lineNumber
        #print("len(listOfLines) = " + str(len(listOfLines)) + ", index = " + str(index))
        if (index == (len(listOfLines) - 1)):
            tk.messagebox.showinfo(message="The last line of the file is already being displayed.")
            window.lift()
            return()

        index += 1

        fileName = listOfLines[index][0]
        fileText = listOfLines[index][1]

        #string = listOfLines[index][0] + " : " + listOfLines[index][1]
        textLabel.config(text=fileText)
        textLabel.update()
        fileNameLabel.config(text=fileName)
        fileNameLabel.update()

        self.lineNumber = index

    # Connected to playButton button in recordingVoice()
    #
    # Gets the wav file of the currently displayed line of text and plays it for the user to hear, if one doesn't exist, inform the user.
    def playWavFile(self, dirPath=None, fileName=None, window=None):
        wavExists = os.path.exists(dirPath + fileName + ".wav")
        if not wavExists:
            tk.messagebox.showinfo(message="No recording found for this line. Record your voice by clicking on the record button.")
            window.lift()
            return

        # playback the just recorded .wav file
        sound = AudioSegment.from_file(dirPath + fileName + ".wav")
        play(sound)

    # Connected to recButton button in recordingVoice()
    #
    # Records the user for the next 8 seconds and saves it with the name related to the currently displayed line of text.
    def recWavFile(self, dirPath=None, fileName=None, window=None):
        duration = 8
        freq = 16000

        # record the user's input for seconds equal to duration
        recording = sd.rec(int(duration * freq), samplerate = freq, channels = 1, dtype="int16")
        sd.wait()
        write(fileName + ".wav", freq, recording)

        # move the .wav file to the training model directory
        shutil.move(fileName + ".wav", dirPath + fileName + ".wav")

        window.lift()
        return

    # Connected to radio buttons in recordingVoiceLines()
    #
    # Takes in the user's choice from radio buttons as an argument and pulls the relevant text file to display in window.
    # Displays one line of text at a time and adds 4 buttons that the user is able to click on:
    #     prevButton, recButton, playButton, nextButton
    def recordingVoice(self, directory=None, window=None):
        """Gets the transcription file from given directory and prompts the user to say the given lines while recording the user saying them."""
        
        # clear the previous tk frame to make room for new widgets
        for widget in window.winfo_children():
            widget.destroy()
        
        # get the name of the fileids/transcription file
        for file in glob.glob(r"VoiceTraining/TrainingModel/" + directory + "/*.fileids"):
            fileName = file.split("\\")
            fileName = fileName[1]
            fileName = fileName.split(".")
            fileName = fileName[0]
            print(fileName)

        dirPath = "VoiceTraining/TrainingModel/" + directory + "/"
        transPath = dirPath + fileName + ".transcription"

        #isFile = os.path.isfile(transPath)
        #if not isFile:
        #    tk.messagebox.showerror(message="Transcription file not found in directory.")

        # open the file and save it into a list
        transFile = open(transPath, "r")
        fileLines = transFile.read().split("\n")
        transFile.close()

        # set up needed variables
        duration = 8
        freq = 16000

        # set up 2d array to hold file names and text
        self.lineNumber = 0
        listOfLines = []
        for fileLine in fileLines:
            # get index positions and name to save voice file as
            line = fileLine
            index = line.index("<",4)
            lastIndex = line.index(")", index)
            fileName = line[index + 6: lastIndex]
            string = line[4:index]
            tempArray = [fileName, string]
            listOfLines.append(tempArray)

        # set up label in window frame
        fileNameLabel = tk.LabelFrame(window, text=listOfLines[0][0], width = 200, height = 100, borderwidth=2)
        fileNameLabel.grid(row=0, column=0, columnspan=4, padx=5, pady=5)
        textLabel = tk.Label(fileNameLabel, text="testing", width=60)
        textLabel.grid()
        prevButton = tk.Button(window, text="Prev", command = lambda: self.getPrevLine(listOfLines=listOfLines, textLabel=textLabel, fileNameLabel=fileNameLabel, window=window))
        recButton = tk.Button(window, text="Rec", command = lambda: self.recWavFile(dirPath=dirPath, fileName=listOfLines[self.lineNumber][0], window=window))
        playButton = tk.Button(window, text="Play", command = lambda: self.playWavFile(dirPath=dirPath, fileName=listOfLines[self.lineNumber][0], window=window))
        nextButton = tk.Button(window, text="Next", command = lambda: self.getNextLine(listOfLines=listOfLines, textLabel=textLabel, fileNameLabel=fileNameLabel, window=window))
        prevButton.grid(row=1, column=0, ipadx=5, ipady=5, padx=10, pady=10, sticky="sw")
        recButton.grid(row=1, column=1, ipadx=5, ipady=5, padx=10, pady=10, sticky="sw")
        playButton.grid(row=1, column=2, ipadx=5, ipady=5, padx=10, pady=10, sticky="sw")
        nextButton.grid(row=1, column=3, ipadx=5, ipady=5, padx=10, pady=10, sticky="sw")

        # display the first text line
        textLabel.config(text=listOfLines[0][1])
        textLabel.update()

    # 1st Option under Voice Training menu
    # Creates a new window with a list of options for the user to choose which training model to choose from to record voice lines
    #
    # Allows the user to click on one of the options, and then sends program counter to recordingVoice()
    def recordVoiceLines(self):
        """Window frame to record user voice lines reading from a .transcription file in specified directory."""
        
        win = tk.Toplevel()
        win.wm_title("Voice Recordings")

        # LabelFrame for choosing which folder to record voice lines from
        recordVoiceLabelFrame = tk.LabelFrame(win, text="Choose the directory with the voice lines you want to record.", width=600, height=10, borderwidth=2, relief="ridge")
        recordVoiceLabelFrame.grid(column=0, columnspan=10, padx=10, pady=10, ipadx=10, ipady=10)
        
        # Get list of available directories to train from
        listOfDirs = os.listdir("VoiceTraining/TrainingModel")
        dirNameChoice = tk.StringVar()

        # Pack all the training model directories into a radiobutton
        for dirName in listOfDirs:
            tk.Radiobutton(recordVoiceLabelFrame, text=dirName, variable=dirNameChoice, value=dirName, command=lambda: self.recordingVoice(directory=dirNameChoice.get(), window=win), indicatoron=0, width=20, padx=20).pack()

    # Temporary function to use for a button with an unimplemented feature.
    def featureNotImplemented(self):
        """Function to use to show that a feature has not been implemented yet."""
        tk.messagebox.showinfo(message="This feature has not been implemented yet.")

    # Connected to radio buttons in chooseLanguageModel()
    #
    # Takes in the user's choice from radio buttons as an argument and changes the used language model to that.
    # If Google was chosen, set the useGoogle boolean flag to true
    # If something else was chosen, copies the chosen language model and pastes it into VoiceTraining/Profiles/en-US/acoustic-model
    def changeLanguageModel(self, modelName="None", win=None):
        """Displays a list of available language models and allows the user to choose one of them to use to parse incoming voice input"""

        print("Inside change language model function")

        # If Google was chosen, change flag to true
        if modelName == "Google":
            print("Going to use Google Voice")
            self.useGoogle = True
            tk.messagebox.showinfo(message="Now using Google Voice for the voice recognition.")
            
        # If modelName = "None" for some reason, quit
        elif modelName == "None":
            tk.messagebox.showerror(message="Unexpected error.\nmodelName = None")
            return

        # For all other options chosen
        else:
            print("Switching to " + modelName)
            self.useGoogle = False

            # Starting process of replacing file in 
            # VoiceTraining/Profiles/en-US/acoustic-model/
            # with files in
            # VoiceTraining/AcousticModels/ + modelName
            
            pathUse    = "VoiceTraining/Profiles/en-US/acoustic-model/"
            pathChosen = "VoiceTraining/AcousticModels/" + modelName + "/"

            # First delete all the files in pathUse
            print("Removing these files from " + pathUse)
            for file in glob.glob(pathUse + "*"):
                print(file)
                os.remove(file)
            print("Removed files from that path")

            # Next copy files from pathChosen to pathUse
            print("Copying files from " + pathChosen + " over to " + pathUse)
            for file in glob.glob(pathChosen + "*"):
                print(file)
                shutil.copy(file, pathUse)
            print("Finished copying over files")

            print("Finished changing language model")
            tk.messagebox.showinfo(message="Now using " + modelName + " as the language model for CMU Sphinx.")

        # Close out window after finished changing language model
        win.destroy()
        
    # 3rd Option under Voice Training menu
    #
    # Creates a new window with a list of radio buttons for the user to choose from. After choosing one, the program counter is sent to changeLanguageModel()
    # List of names is retrieved from directory names in VoiceTraining/AcousticModels
    def chooseLanguageModel(self):
        """Window frame to choose a language model from a list of radiobutton options"""
        #tk.messagebox.showinfo(message="In choose language model function")
        win = tk.Toplevel()
        win.wm_title("Choose Language Model")

        # LabelFrame for choosing which language model to use
        instructionLabelFrame = tk.LabelFrame(win, text="Choose the language model you want to use from the list below.", width=600, height=10, borderwidth=2, relief="ridge")
        instructionLabelFrame.grid(column=0, columnspan=10, padx=10, pady=30, ipadx=10, ipady=10)
        
        # get list of available language models
        listOfModels = os.listdir("VoiceTraining/AcousticModels")
        modelNameChoice = tk.StringVar()

        # pack Google into the list of radiobuttons
        tk.Radiobutton(instructionLabelFrame, text="Google", variable=modelNameChoice, value="Google", command=lambda: self.changeLanguageModel(modelName=modelNameChoice.get(), win=win), indicatoron=0, width=20, padx=20).pack()

        # pack the list of available language models
        for modelName in listOfModels:
            tk.Radiobutton(instructionLabelFrame, text=modelName, variable=modelNameChoice, value=modelName, command=lambda: self.changeLanguageModel(modelName=modelNameChoice.get(),win=win), indicatoron=0, width=20, padx=20).pack()

    def text_queue(self, thread_queue=None):
        """Put result from voice recognition model into a queue"""
        result = vr.listen(self.txt_editor_field,self.cmd_receiver_txt,self.cmd_man_txt,self.sys_out_txt,self.useGoogle)
        thread_queue.put(result)

    def image_resizer(self, e):
        """Dynamically resize the header banner"""
        global img1, resized_img1, re_render
        img1 = Image.open(resource_path("assets/vocoder_icon_titledark.png"))
        resized_img1 = img1.resize((e.width, e.height), Image.ANTIALIAS)
        re_render = ImageTk.PhotoImage(resized_img1)
        self.img.configure(image=re_render)

    def update_text(self):
        """Runner code for the queue-thread systems, calling listen_for_results after every new thread is spawned"""
        self.loadred = Image.open(resource_path("redCircle.jpg"))
        self.renderred = ImageTk.PhotoImage(self.loadred)
        self.imggray.configure(image=self.renderred)
        self.thread_queue = queue.Queue()
        self.new_thread = threading.Thread(
            target=self.text_queue,
            kwargs={'thread_queue':self.thread_queue})
        self.new_thread.start()
        self.root.after(1, self.listen_for_result)
        

    def listen_for_result(self):
        """Check for content in the queue and update the widget appropriately"""
        try:
            text = self.thread_queue.get(0)
            if text == "":
                self.sys_out_txt.insert(tk.END,"No command received. Please say a commands!")
                self.imggray.configure(image=self.rendergray)
            elif text == "*":
                self.txt_editor_field.insert(tk.INSERT, "")
                self.root.after(2, self.numberLines.redraw)
                self.imggray.configure(image=self.rendergray)
            else:
                self.txt_editor_field.insert(tk.INSERT, text)
                self.root.after(2, self.numberLines.redraw)
                self.imggray.configure(image=self.rendergray)
        except queue.Empty:
            self.root.after(1, self.listen_for_result)

    def change_indicator(self):
        """Handling end/compile buttons"""
        vr.test_compiler(self.txt_editor_field.get(1.0,tk.END), self.terminal)
        self.imggray.configure(image=self.rendergray) 
    
    def on_closing(self):
        """Handling Close the app event, delete all the cache built up"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            os.popen('find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf')
            self.root.destroy()

    def onScrollPress(self, *args):
        """Handling Scroll Press event for the text editor"""
        self.scrollbar.bind("<B1-Motion>", self.numberLines.redraw)

    def onScrollRelease(self, *args):
        """Handling Scroll Release event for the text editor"""
        self.scrollbar.unbind("<B1-Motion>", self.numberLines.redraw)

    def onPressDelay(self, *args):
        """"Handling Any Key Press event for the text editor"""
        self.root.after(2, self.numberLines.redraw)

    def get(self, *args, **kwargs):
        """Handling get event for the text editor"""
        return self.txt_editor_field.get(*args, **kwargs)

    def insert(self, *args, **kwargs):
        """Handling insert event for the text editor"""
        return self.txt_editor_field.insert(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Handling delete event for the text editor"""
        return self.txt_editor_field.delete(*args, **kwargs)

    def index(self, *args, **kwargs):
        """Handling index event for the text editor"""
        return self.txt_editor_field.index(*args, **kwargs)

    def redraw(self):
        """Handling the redraw of the number line"""
        self.numberLines.redraw()
    
def main():
    """Main function for the application.py"""
    dimension = []
    for m in get_monitors():
        if m.x == 0 and m.y == 0:
            dimension.append(m.width)
            dimension.append(m.height)
    app = Application(width=dimension[0], height=dimension[1])
    app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.root.mainloop()

if __name__ == "__main__":
    main()
