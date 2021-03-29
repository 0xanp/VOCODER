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
    useGoogle = False    
    
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
        self.menu_voice.add_command(label="Record voice lines", command=self.recordVoiceLines)
        self.menu_voice.add_command(label="Train language model", command=self.trainLanguageModel)
        self.menu_voice.add_command(label="Choose language model", command=self.chooseLanguageModel)
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
                                        "\t18=Undo Command \t19 Print Statement \t20 Print Variable \t21Create Function \t22Indent Cursor")
        self.help_field.grid_propagate(False)
        self.help_field.config(state=DISABLED)
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
        tk.messagebox.showinfo("VOCODER", "Binh An Pham\nM Rachel Van Pelt\nSteven Tran")
    
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
            file.write(self.txt_editor_field.get(1.0,tk.END)) 
            file.close() 
  
    def cut(self): 
        self.txt_editor_field.event_generate("<<Cut>>") 
  
    def copy(self): 
        self.txt_editor_field.event_generate("<<Copy>>") 
  
    def paste(self): 
        self.txt_editor_field.event_generate("<<Paste>>") 

    def checkNameButton(self, inputString = None):
        """Checks to see if there is a directory with the name of inputString in the path of VoiceTraining/AcousticModels/"""

        profileName = inputString

        # If no text was passed into this function, display messagebox and exit function
        if inputString == None:
            tk.messagebox.showinfo("No name was inputted.")
            return

        # Check if inputString is a preexisting directory in VoiceTraining/AcousticModels/ and display the relevant messagebox    
        isdir = os.path.isdir("VoiceTraining/AcousticModels/" + profileName)
        if isdir == False:
            proceed = tk.messagebox.askyesno("Voice Training", inputString + " was not found. Do you want to create a new one?")
        else:
            proceed = tk.messagebox.askyesno("Voice Training", inputString + " was found as an already existing directory. Do you want to overwrite it?")

    def trainModelButton(self, profileName = None, directoryName = None):
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
        nameButton = tk.Button(modelNameLabelFrame, text="Check Availability", command=lambda: self.checkNameButton(inputString=nameTextField.get()))
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
        trainButton = tk.Button(win, text="Train the language model!", command=lambda: self.trainModelButton(profileName=nameTextField.get(), directoryName=dirNameChoice.get()))
        trainButton.grid(row=2,column=0, padx=225, pady=10, sticky="nsew")

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
        fileLines.pop()
        transFile.close()

        # set up needed variables
        duration = 8
        freq = 16000
        string = "You have " + str(duration) + " seconds to say each line up to the \":\" symbol."
        print(string)

        # set up label in window frame
        instructionLabel = tk.LabelFrame(window, text=string, width = 200, height = 100, borderwidth=2)
        instructionLabel.grid(row=0, column=0, padx=5, pady=5)
        textLabel = tk.Label(instructionLabel, text="testing", width=60)
        textLabel.grid()

        for fileLine in fileLines:
            # get index positions and name to save voice file as
            line = fileLine
            index = line.index("<",4)
            lastIndex = line.index(")", index + 6)
            fileName = line[index + 6: lastIndex]
            string = line[4:index] + ": " + fileName

            # display the text line    
            print(string)
            textLabel.config(text=string)
            textLabel.update()

            goodRecording = False 
            while not goodRecording:         
                window.lift()

                # record the user's input for seconds equal to duration
                recording = sd.rec(int(duration * freq), samplerate = freq, channels = 1, dtype="int16")
                sd.wait()
                write(fileName + ".wav", freq, recording)

                # update text to textLabel
                textLabel.config(text=string + "\n\nPlaying back recording.")
                textLabel.update()

                # playback the just recorded .wav file
                sound = AudioSegment.from_file(fileName + ".wav")
                play(sound)

                goodRecording = tk.messagebox.askyesno(message="Use this recording?")

            # move the .wav file to the training model directory
            shutil.move(fileName + ".wav", dirPath + "/" + fileName + ".wav")

        # After recording voice lines, destroy the window.
        window.destroy()

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

    def featureNotImplemented(self):
        """Function to use to show that a feature has not been implemented yet."""
        tk.messagebox.showinfo(message="This feature has not been implemented yet.")

    def changeLanguageModel(self, modelName="None"):
        """Displays a list of available language models and allows the user to choose one of them to use to parse incoming voice input"""

        print("Inside change language model function")

        # If Google was chosen, change flag to true
        if modelName == "Google":
            print("Going to use Google Voice")
            self.useGoogle = True

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
            tk.messagebox.showinfo(message="Finished changing the language model.")
        

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
        tk.Radiobutton(instructionLabelFrame, text="Google", variable=modelNameChoice, value="Google", command=lambda: self.changeLanguageModel(modelName=modelNameChoice.get()), indicatoron=0, width=20, padx=20).pack()

        # pack the list of available language models
        for modelName in listOfModels:
            tk.Radiobutton(instructionLabelFrame, text=modelName, variable=modelNameChoice, value=modelName, command=lambda: self.changeLanguageModel(modelName=modelNameChoice.get()), indicatoron=0, width=20, padx=20).pack()

    def text_queue(self, thread_queue=None):
        result = vr.listen(self.txt_editor_field,self.cmd_receiver_txt,self.cmd_man_txt,self.sys_out_txt,self.useGoogle)
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
