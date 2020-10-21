import tkinter as tk
import speech_recognition as sr
import threading
import re as re
from fuzzywuzzy import fuzz

commandWords = [ "create new variable", 
                 "assign old variable",
                 "return statement",
                 "create for loop",
                 "create while loop",
                 "create if statement",
                 "create else if statement",
                 "create else statement",
                 "create array",
                 "move cursor",
                 "move to word",
                 "undo command",
                 "redo command",
                 "select word",
                 "select line",
                 "select block",
                 "copy text",
                 "paste text" ]
                 
variableNames = []

# function to get voice input and returns as a string
def getVoiceInput():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        audioToText = r.recognize_sphinx(audio)
    return audioToText
    
def phraseMatch(audioToText):
    print("input: " + audioToText + "\n")

    i = 0
    highest = 0
    closestString = ""
    for i in range(0,len(commandWords)):
        string = commandWords[i]
        ratio = fuzz.token_set_ratio(audioToText, string)
        print(string + ": " + str(ratio))
        
        if ratio > highest:
            highest = ratio
            closestString = string
    
        
    print("\nClosest string to match input was\n")
    print(closestString + ": " + str(highest))

    if audioToText == "apple":
        string = "found matching phrase: apple\n"
    elif audioToText == "create new variable":
        string = createNewVariable()       
        #string = "found matching phrase: createNewVariable\n"
    else:
        string = "no matching phrase found: " + audioToText + "\n"
    return string
    
# Operations dictionary for string to symbol
op_dict = { "plus":"+", 
           "minus":"-", 
           "times":"*",
           "divided by":"/" }

# obtained from https://stackoverflow.com/questions/493174/is-there-a-way-to-convert-number-words-to-integers
# will convert number words to int literals
def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
            # raise Exception("Illegal word: " + word)
            return textnum

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

# Very basic version of create new variable command. The terminal will prompt the user for voice input. The program will be able to take any string of characters and uses snake case for variable name. The program will be able to convert word versions of +, -, *, /, and numbers into their symbol versions.

# Example
# Voice input
#     variableName = test variable
#     expression   = one plus two minus three
#     output:        test_variable = 1 + 2 - 3

def createNewVariable():
    # Get and format variable name, will use snake case
    print("Say name of new variable.\n")
    vInput = getVoiceInput()
    vInput = vInput.replace(" ","_")
    variableName = vInput
    
    # used for checking correctness in terminal
    # print("variableName = " + variableName);
    
    # Get and format expression
    print("Say full expression.\n")
    vInput = getVoiceInput()
    
    # replace operation words with symbols
    for word, symbol in op_dict.items():
        vInput = vInput.replace(word, symbol)   
    
    # split input by operators    
    vInputSplit = re.split("([+]|[-]|[*]|[/])", vInput)
    
    # find indexes of the operations
    opLocations = []
    for i in range(0, len(vInputSplit)):
        if vInputSplit[i] in op_dict.values():
            opLocations.append(i)
    
    # go through the split string and replace with symbols/literals            
    for i in range(0, len(vInputSplit)):
        if i not in opLocations:   
            vInputSplit[i] = str(text2int(vInputSplit[i]))
    
    # reformat expression
    expression = ""
    for i in range(0, len(vInputSplit)): 
        if i in opLocations:   
            expression = expression + " " + vInputSplit[i] + " "
        else:
            expression = expression + vInputSplit[i]
    
    # used for checking correctness in terminal    
    # print("expression = " + expression)
    
    string = variableName + " = " + expression + "\n"
    return string


def cbc(txt):

    return lambda : callback(tex)

def callback(tex):
    button = "Listen" 

    tex.insert(tk.END, button)
    tex.see(tk.END)# Scroll if necessary

def listen(tex):
    def callback(tex):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
            audioToText = r.recognize_sphinx(audio)
            audio_txt = phraseMatch(audioToText)

        tex.insert(tk.END, audio_txt)
        tex.see(tk.END)

    a_thread = threading.Thread(target = callback(tex))
    a_thread.start()

top = tk.Tk()
tex = tk.Text(master=top)
tex.pack(side=tk.RIGHT)
bop = tk.Frame()
bop.pack(side=tk.LEFT)


tk.Button(bop, text='Listen', command=lambda: listen(tex)).pack()
tk.Button(bop, text='Exit', command=top.destroy).pack()

top.mainloop()
