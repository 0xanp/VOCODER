import tkinter as tk
import speech_recognition as sr
import re as re
from fuzzywuzzy import fuzz
from vosk import SetLogLevel
SetLogLevel(-1)
import os
import json
import pyaudio
import compiler as comp

# list of commands, has some extra strings for testing
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
                 "paste text",
                 "create function",
                 "print statement",
                 "print variable",
                 "show set of variables"]

# this set will contain variable names created by createNewVariable()                 
setOfVariableNames = []

# function to get voice input and returns as a string
def getVoiceInput():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        #audioToText = r.recognize_sphinx(audio)
        audioToText = r.recognize_google(audio)
    return audioToText

def phraseMatch(audioToText,tex2,tex3,tex4):
    win = tk.Toplevel()
    win.wm_title("Prompts")
    prompt = tk.Text(win, width=50, height=15)
    prompt.grid(row=0,column=0,padx=5,pady=5,sticky='nsew')
    print("input: " + audioToText + "\n")
    prompt.insert(tk.END, "input: " + audioToText + "\n")
    validCommand = False
    #send info to command manager window on UI
    tex3.insert(tk.END, "matching phrase to command..." + "\n")
    tex3.see(tk.END)
    closestString = getClosestString(audioToText, commandWords,tex3)
    #send matched command to Command(s) Received window on UI
    tex2.insert(tk.END, closestString + "\n")
    tex2.see(tk.END)
    #set stringP to call for matching functions
    if closestString == "create new variable":
        validCommand = True
        stringP = createNewVariable(tex3, prompt)
    elif closestString == "show set of variables":
        validCommand = True
        showSet(tex4)
        stringP = ""
    elif closestString == "assign old variable":
        validCommand = True
        stringP = assignOldVariable(tex3, prompt)
    elif closestString == "return statement":
        validCommand = True
        stringP = returnStatement(tex3, prompt)
    elif closestString == "create for loop":
        validCommand = True
        stringP = createForLoop(tex3, prompt)
    elif closestString == "create while loop":
        validCommand = True
        stringP = createWhileLoop(tex3, prompt)
    elif closestString == "create if statement":
        validCommand = True
        stringP = createIfStatement(tex3, prompt)
    elif closestString == "create else if statement":
        validCommand = True
        stringP = createElseIfStatement(tex3, prompt)
    elif closestString == "create function":
        validCommand = True
        stringP = createDef(tex3, prompt)
    elif closestString == "print variable":
        validCommand = True
        stringP = printVariable(tex3, prompt)
    elif closestString == "print statement":
        validCommand = True
        stringP = printStatement(tex3, prompt)
    else:
        stringP = ""
        #send response to System Output window on UI
        tex4.insert(tk.END, "no matching phrase found: " + audioToText + "\n")
        tex4.see(tk.END)
        win.after(1000, lambda: win.destroy())
    if validCommand:
        #send response to System Output window on UI
        tex4.insert(tk.END, "valid command received..." + "\n")
        tex4.see(tk.END)
        win.after(1000, lambda: win.destroy())
    validCommand = False
    return stringP

def test_compiler(text,root):
    comp.main(text,root)

def getClosestString(inputString, listToMatch,tex3):
    i = 0
    highest = 0
    closestString = ""
    
    # if there is nothing in the listToMatch, return original string
    if not listToMatch:
        return inputString
        
    for i in range(0,len(listToMatch)):
        string = listToMatch[i]
        ratio = fuzz.token_set_ratio(inputString, string)
        print(string + ": " + str(ratio))
        
        if ratio > highest:
            highest = ratio
            closestString = string
    
    # print("\nClosest string to match input was\n")
    # check for threshold of 80 or greater to find matching command
    if highest >= 80:
        # print(closestString + ": " + str(highest))
        # send status to command manager window on UI
        tex3.insert(tk.END, "closest match: " + closestString + "\n")
        tex3.see(tk.END)
    else:
        # print("not found")
        # send status to command manager window on UI
        tex3.insert(tk.END, inputString + " not found.\n")
        tex3.see(tk.END)
        closestString = "invalid"
    return closestString
    
# Operations dictionary for string to symbol
op_dict = {"plus"       :"+", 
           "minus"      :"-", 
           "times"      :"*",
           "divided by" :"/" }
           
compare_dict = { "less than or equal to"      : "<=",
                 "less than"                  : "<",
                 "greater than or equal to"   : ">=",
                 "greater than"               : ">",
                 "not equal to"               : "!=",
                 "equal to"                   : "==" }

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

# Test function just to see if the set works    
def showSet(tex4):
    #print("Currently in showSet() function.\n" +
    tex4.insert(tk.END, "Set of variable names:")
    for i in setOfVariableNames:
        tex4.insert(tk.END, "          " + i + ",")
        tex4.see(tk.END)
        
# receives input from user saying yes or no and returns true if yes, false if no
def confirm(prompt):
    vInput = getVoiceInput()
    yesRatio = fuzz.ratio(vInput, "yes")
    noRatio = fuzz.ratio(vInput, "no")
    print("yes: " + str(yesRatio) + "\n" +
          "no:  " + str(noRatio)  + "\n")
    # prompt.insert(tk.END, "\nyes: " + str(yesRatio) + "\n" +"no:  " + str(noRatio)  + "\n" )
    prompt.insert(tk.END, "\n")
    if yesRatio > noRatio: return True 
    else: return False


# Very basic version of create new variable command. The terminal will prompt the user for voice input. The program will be able to take any string of characters and uses snake case for variable name. The program will be able to convert word versions of +, -, *, /, and numbers into their symbol versions.

# Example
# Voice input
#     variableName = test variable
#     expression   = one plus two minus three
#     output:        test_variable = 1 + 2 - 3

# ***************************************************************************************
# command "create new variable" returns string = variableName + " = " + expression + "\n"
# use case 1, CNV
# ***************************************************************************************
def createNewVariable(tex3,prompt):
    # Get and format variable name, will use snake case
    correctName = False
    nameTaken = True
    while not correctName or nameTaken:
        correctName = False
        nameTaken = True
        
        print("Say name of new variable.\n")
        prompt.insert(tk.END,"Say name of new variable.\n")
        vInput = getVoiceInput()
        vInput = vInput.replace(" ","_")
        variableName = vInput
        
        print("Variable name: " + variableName + "\n" +
              "Is this correct? (Yes/No)")
        prompt.insert(tk.END,"Variable name: " + variableName + '\n' +
              "Is this correct? (Yes/No)")
        if confirm(prompt): correctName = True
        else: continue
        
        if variableName in setOfVariableNames:
            print("Variable name: " + variableName + ", is already used in the program.\n" +
                  "Do you still want to use it? (Yes/No)")
            prompt.insert(tk.END,"Variable name: " + variableName + ", is already used in the program.\n" +
                  "Do you still want to use it? (Yes/No)")
            if confirm(prompt): nameTaken = False
        else:
            nameTaken = False
             
    
    # Get expression
    correctExpression = False
    while not correctExpression:    
        print("State value for variable.\n")
        prompt.insert(tk.END,"State value for variable.\n")
        vInput = getVoiceInput()
        # replace operation words with symbols
        for word, symbol in op_dict.items():
            vInput = vInput.replace(word, symbol)   
            
        # remove any periods
        vInput = vInput.replace(".", "")
        
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
                
                # check if the term starts with a letter
                # if so, it must be a preexisting variable name and 
                # match it with one from the setOfVariableNames
                if vInputSplit[i][0].isalpha():
                    closestVariable = getClosestString(vInputSplit[i], setOfVariableNames,tex3)
                    
                    print("Got input of: " + str(vInputSplit) + "\n")
                    prompt.insert(tk.END,"Got input of: " + str(vInputSplit) + "\n")
                    print("Closest match was: " + str(closestVariable) + "\n")
                    prompt.insert(tk.END,"Closest match was: " + str(closestVariable) + "\n")
                    vInputSplit[i] = closestVariable
        
        # reformat expression
        expression = ""
        for i in range(0, len(vInputSplit)): 
            if i in opLocations:   
                expression = expression + vInputSplit[i]
            else:
                expression = expression + vInputSplit[i]
                
        # print("Expression: " + expression + '\n' + "Is this correct? (Yes/No)")
        prompt.insert(tk.END, variableName + " = " + expression + "\n" + "Is this correct? (Yes/No)")
        if confirm(prompt): correctExpression = True
        
    
    # used for checking correctness in terminal    
    # print("expression = " + expression)
    
    if variableName not in setOfVariableNames:
        setOfVariableNames.append(variableName)  
    
    string = variableName + " = " + expression + "\n"
    return string

# *********************************************************************************
# command "assign old variable" returns string = variableName + " = " + expression + "\n"
# use case 2, AOV
# *********************************************************************************
def assignOldVariable(tex3, prompt):
    # check if there are any old variables
    if not setOfVariableNames:
        print("No variable names already initialized.\n")
        prompt.insert(tk.END, "No variable names already initialized.\n")
        return ""
        
    # get input for the variable name to be modified
    correctName = False
    while not correctName:
        # print("Say the name of the variable you want to modify.\n")
        # ask user for variable to modify in the GUI popup
        prompt.insert(tk.END, "Say the name of the variable you want to modify.\n")
        vInput = getVoiceInput()
        variableName = getClosestString(vInput, setOfVariableNames,tex3)
        if variableName == "invalid":
            variableName = vInput
            prompt.insert(tk.END, "New variable detected.\n")
            tex3.insert(tk.END, variableName + " not found, creating new variable.\n")
            tex3.see(tk.END)
        # print("Variable name: " + variableName + "\n" + "Is this correct? (Yes/No)")
        # ask user for confirmation in GUI popup
        prompt.insert(tk.END, "Variable name: " + variableName + "\n" + "Is this correct? (Yes/No)")
        if confirm(prompt): correctName = True
        else: continue
        
    # get expression
    correctExpression = False
    while not correctExpression:    
        # print("State what the variable equals.\n")
        prompt.insert(tk.END, "State value for variable.\n")
        vInput = getVoiceInput()
        
        # replace operation words with symbols
        for word, symbol in op_dict.items():
            vInput = vInput.replace(word, symbol)   
            
        # remove any periods
        vInput = vInput.replace(".", "")
        
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
                
                # check if the term starts with a letter
                # if so, it must be a preexisting variable name and 
                # match it with one from the setOfVariableNames
                if vInputSplit[i][0].isalpha():
                    closestVariable = getClosestString(vInputSplit[i], setOfVariableNames,tex3)
                    if closestVariable=="invalid":
                        # print("Got input of: " + str(vInputSplit) + "\n")
                        prompt.insert(tk.END, vInputSplit[i] + " is not defined\n")
                        # vInputSplit[i] = closestVariable
                    else:
                        vInputSplit[i] = closestVariable
        
        # reformat expression
        expression = ""
        for i in range(0, len(vInputSplit)): 
            if i in opLocations:   
                expression = expression + vInputSplit[i]
            else:
                expression = expression + vInputSplit[i]
                
        # print("Expression: " + expression + "\n" + "Is this correct? (Yes/No)")
        # confirm output from user in GUI popup
        prompt.insert(tk.END, variableName + " = " + expression + "\n" + "Is this correct? (Yes/No)")
        if confirm(prompt): correctExpression = True
        
    string = variableName + " = " + expression + "\n"
    return string

# *********************************************************************************
# command "return statement" returns expression = "return " + expression + "\n"
# use case 3, RS
# *********************************************************************************  
def returnStatement(tex3, prompt):
    # get voice input
    correctExpression = False
    while not correctExpression:    
        print("Say what you want to return.\n")
        prompt.insert(tk.END, "Say what you want to return.\n")
        vInput = getVoiceInput()
        
        if vInput == "none":
            return "return\n"
        
        # replace operation words with symbols
        for word, symbol in op_dict.items():
            vInput = vInput.replace(word, symbol)   
            
        # remove any periods
        vInput = vInput.replace(".", "")
        
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
                
                # check if the term starts with a letter
                # if so, it must be a preexisting variable name and 
                # match it with one from the setOfVariableNames
                if vInputSplit[i][0].isalpha():
                    closestVariable = getClosestString(vInputSplit[i], setOfVariableNames,tex3)
                    
                    print("Got input of: " + str(vInputSplit) + "\n")
                    # prompt.insert(tk.END, "Got input of: " + str(vInputSplit) + "\n")
                    print("Closest match was: " + str(closestVariable) + "\n")
                    # prompt.insert(tk.END, "Closest match was: " + str(closestVariable) + "\n")
                    vInputSplit[i] = closestVariable
        
        # reformat expression
        expression = ""
        for i in range(0, len(vInputSplit)): 
            if i in opLocations:   
                expression = expression + vInputSplit[i]
            else:
                expression = expression + vInputSplit[i]
                
        print("Expression: " + expression + "\n" +
              "Is this correct? (Yes/No)")
        prompt.insert(tk.END, "return " + expression + "\n" +
              "Is this correct? (Yes/No)")
        if confirm(prompt): correctExpression = True
    
    expression = "return " + expression + "\n"
    return expression

# *********************************************************************************
# command "create for loop" returns string = "for " + loopingVariable + " in range
#                                             (" + rangeInt + "):\n    "
# for now, can only create a for loop with range function
# use case 4, CFL
# *********************************************************************************
def createForLoop(tex3, prompt):
    correctVariable = False
    while not correctVariable:
        # print("Say the name of looping variable.\n")
        # system asks user for variable in the popup window of GUI
        prompt.insert(tk.END, "Say the name of the looping variable.\n")
        vInput = getVoiceInput()
        
        vInput = vInput.replace(".","")
        vInput = vInput.replace(" ","_")
        # print("Looping variable: " + vInput + "\n" + "Is this correct? (Yes/No)")
        # confirmation sent to user in popup window of GUI
        prompt.insert(tk.END, "Looping variable: " + vInput + "\n" + "Is this correct? (Yes/No)")
        if confirm(prompt): correctVariable = True
        
    loopingVariable = vInput
        
    correctRange = False
    while not correctRange:
        # print("How many times do you want to repeat this loop?\n")
        # question sent to user in popup window of GUI
        prompt.insert(tk.END, "How many times do you want to repeat this loop?\n")
        vInput = getVoiceInput()
        vInput = str(text2int(vInput))
        
        # print("Amount of loops: " + vInput + "\n" + "Is this correct? (Yes/No)")
        # confirmation sent to user in popup window of GUI
        prompt.insert(tk.END, "Amount of loops: " + vInput + "\n" + "Is this correct? (Yes/No)")
        if confirm(prompt): correctRange = True
        
    rangeInt = vInput
    # string created for insertion in text editor window of GUI
    string = "for " + loopingVariable + " in range(" + rangeInt + "):\n    "
    return string

# *********************************************************************************
# command "create while loop" returns string = "while " + condition + ":\n"
# use case 5, CWL
# *********************************************************************************
def createWhileLoop(tex3, prompt):
    correctCondition = False
    while not correctCondition:
        print("Say the condition you want for the while loop.\n")
        prompt.insert(tk.END, "Say the condition you want for the while loop.\n")
        vInput = getVoiceInput()
        
        vInput = vInput.replace(".","")
        
        # replace strings of comparison operators with symbols
        for x, y in compare_dict.items():
            vInput = vInput.replace(x, y)
        
        
        # split string into array, while keeping the operator symbols
        vInputSplit = re.split("([<=][>=][!=][==]|[>]|[<])", vInput)
        
        # find location of operators    
        opLocations = []
        for i in range(0, len(vInputSplit)):
            if vInputSplit[i] in compare_dict.values():
                opLocations.append(i)    
        
        # go through the split string and replace with symbols/literals            
        for i in range(0, len(vInputSplit)):
            if i not in opLocations:   
                vInputSplit[i] = str(text2int(vInputSplit[i]))
                
                # check if the term starts with a letter
                # if so, it must be a preexisting variable name and 
                # match it with one from the setOfVariableNames
                if vInputSplit[i][0].isalpha():
                    closestVariable = getClosestString(vInputSplit[i], setOfVariableNames,tex3)
                    
                    print("Got input of: " + str(vInputSplit) + "\n")
                    # prompt.insert(tk.END, "Got input of: " + str(vInputSplit) + "\n")
                    print("Closest match was: " + str(closestVariable) + "\n")
                    # prompt.insert(tk.END, "Closest match was: " + str(closestVariable) + "\n")
                    vInputSplit[i] = closestVariable
        
        # reformat expression
        expression = ""
        for i in range(0, len(vInputSplit)): 
            if i in opLocations:   
                expression = expression + vInputSplit[i]
            else:
                expression = expression + vInputSplit[i]
        print("Condition: " + expression + "\n" + "Is this correct? (Yes/No)")
        prompt.insert(tk.END, "while " + expression + "\n" + "Is this correct? (Yes/No)")
        if confirm(prompt): correctCondition = True
    
    condition = expression
    string = "while " + condition + ":\n    "
    return string

# *********************************************************************************
# command "create if statement" returns string = "if " + condition + ":\n"
# use case 6, CIF
# *********************************************************************************    
def createIfStatement(tex3, prompt):
    correctCondition = False
    while not correctCondition:
        print("Say the condition you want for the if statement.\n")
        prompt.insert(tk.END, "Say the condition you want for the if statement.\n")
        vInput = getVoiceInput()
        
        vInput = vInput.replace(".","")
        
        # replace strings of comparison operators with symbols
        for x, y in compare_dict.items():
            vInput = vInput.replace(x, y)
        
        # split string into array, while keeping the operator symbols
        vInputSplit = re.split("([<=][>=][!=][==]|[>]|[<])", vInput)
        
        # find location of operators    
        opLocations = []
        for i in range(0, len(vInputSplit)):
            if vInputSplit[i] in compare_dict.values():
                opLocations.append(i)    
        
        # go through the split string and replace with symbols/literals            
        for i in range(0, len(vInputSplit)):
            if i not in opLocations:   
                vInputSplit[i] = str(text2int(vInputSplit[i]))
                
                # check if the term starts with a letter
                # if so, it must be a preexisting variable name and 
                # match it with one from the setOfVariableNames
                if vInputSplit[i][0].isalpha():
                    closestVariable = getClosestString(vInputSplit[i], setOfVariableNames,tex3)
                    
                    print("Got input of: " + str(vInputSplit) + "\n")
                    # prompt.insert(tk.END, "Got input of: " + str(vInputSplit) + "\n")
                    print("Closest match was: " + str(closestVariable) + "\n")
                    # prompt.insert(tk.END, "Closest match was: " + str(closestVariable) + "\n")
                    vInputSplit[i] = closestVariable
        
        # reformat expression
        expression = ""
        for i in range(0, len(vInputSplit)):
            if i in opLocations:
                expression = expression + vInputSplit[i]
            else:
                expression = expression + vInputSplit[i]
        print("Condition: " + expression + "\n" + "Is this correct? (Yes/No)")
        prompt.insert(tk.END, "if " + expression + "\n" + "Is this correct? (Yes/No)")
        if confirm(prompt): correctCondition = True
    
    condition = expression
    string = "if " + condition + ":\n    "
    return string

# *********************************************************************************
# command "create else-if statement" returns string = "elif " + condition + ":\n"
# use case 7, CEIF
# *********************************************************************************
def createElseIfStatement(tex3, prompt):
    correctCondition = False
    while not correctCondition:
        print("Say the condition you want for the else if statement.\n")
        prompt.insert(tk.END, "Say the condition you want for the else if statement.\n")
        vInput = getVoiceInput()
        
        vInput = vInput.replace(".","")
        
        # replace strings of comparison operators with symbols
        for x, y in compare_dict.items():
            vInput = vInput.replace(x, y)
        
        
        # split string into array, while keeping the operator symbols
        vInputSplit = re.split("([<=][>=][!=][==]|[>]|[<])", vInput)
        
        # find location of operators    
        opLocations = []
        for i in range(0, len(vInputSplit)):
            if vInputSplit[i] in compare_dict.values():
                opLocations.append(i)    
        
        # go through the split string and replace with symbols/literals            
        for i in range(0, len(vInputSplit)):
            if i not in opLocations:   
                vInputSplit[i] = str(text2int(vInputSplit[i]))
                
                # check if the term starts with a letter
                # if so, it must be a preexisting variable name and 
                # match it with one from the setOfVariableNames
                if vInputSplit[i][0].isalpha():
                    closestVariable = getClosestString(vInputSplit[i], setOfVariableNames,tex3)
                    
                    print("Got input of: " + str(vInputSplit) + "\n")
                    # prompt.insert(tk.END, "Got input of: " + str(vInputSplit) + "\n")
                    print("Closest match was: " + str(closestVariable) + "\n")
                    # prompt.insert(tk.END, "Closest match was: " + str(closestVariable) + "\n")
                    vInputSplit[i] = closestVariable
        
        # reformat expression
        expression = ""
        for i in range(0, len(vInputSplit)): 
            if i in opLocations:   
                expression = expression + vInputSplit[i]
            else:
                expression = expression + vInputSplit[i]
        print("Condition: " + expression + "\n" + "Is this correct? (Yes/No)")
        prompt.insert(tk.END, "elif " + expression + "\n" + "Is this correct? (Yes/No)")
        if confirm(prompt): correctCondition = True
    
    condition = expression
    string = "elif " + condition + ":\n    "
    return string

# *********************************************************************************
# command "create else statement" returns string = "else:\n"
# use case 8, CEF
# *********************************************************************************

# *********************************************************************************
# command "create array" returns string = "array = [" + var(s) + "]\n"
# use case 9, CA
# *********************************************************************************

# *********************************************************************************
# command "move cursor"
# use case 10, MC
# *********************************************************************************

# *********************************************************************************
# command "move to word"
# use case 11, MTW
# *********************************************************************************

# *********************************************************************************
# command "undo"
# use case 12, UC
# *********************************************************************************

# *********************************************************************************
# command "redo"
# use case 13, RC
# *********************************************************************************

# *********************************************************************************
# command "select word"
# use case 14, SW
# *********************************************************************************

# *********************************************************************************
# command "select line"
# use case 15, SL
# *********************************************************************************

# *********************************************************************************
# command "select block"
# use case 16, SB
# *********************************************************************************

# *********************************************************************************
# command "copy text"
# use case 17, CT
# *********************************************************************************

# *********************************************************************************
# command "paste text"
# use case 18, PT
# *********************************************************************************

# *********************************************************************************
# command "print statement" returns string = "print('" + printLine + "')\n"
# use case 19, PS
# *********************************************************************************
def printStatement(tex3, prompt):
    correctPrint = False
    while not correctPrint:
        print("Say the line for printing.\n")
        prompt.insert(tk.END, "Say the line for printing.\n")
        vInput = getVoiceInput()
        
        # vInput = vInput.replace(".","")
        # vInput = vInput.replace(" ","_")
        print("line: " + vInput + "\n" +
              "Is this correct? (Yes/No)")
        prompt.insert(tk.END, "line: " + vInput + "\n" +
              "Is this correct? (Yes/No)")
        if confirm(prompt): correctPrint = True
        
    printLine = vInput
    
    string = "print('" + printLine + "')\n"
    return string

# *********************************************************************************
# command "print variable" returns string = "print(" + printVar + ")\n"
# use case 20, PV
# *********************************************************************************
def printVariable(tex3, prompt):
    correctPrint = False
    while not correctPrint:
        print("Say the variable for printing.\n")
        prompt.insert(tk.END, "Say the variable for printing.\n")
        vInput = getVoiceInput()
        
        # vInput = vInput.replace(".","")
        vInput = vInput.replace(" ","_")
        print("variable: " + vInput + "\n" +
              "Is this correct? (Yes/No)")
        prompt.insert(tk.END, "variable: " + vInput + "\n" +
              "Is this correct? (Yes/No)")
        if confirm(prompt): correctPrint = True
        
    printVar = vInput
    
    string = "print(" + printVar + ")\n"
    return string

# *********************************************************************************
# command "create function" returns string = "def " + printLine + "():\n    "
# still need to implement functions with arguments
# use case 21, CF
# *********************************************************************************
def createDef(tex3,prompt):
    correctPrint = False
    while not correctPrint:
        print("Say name of function.\n")
        prompt.insert(tk.END, "Say name of the function.\n")
        vInput = getVoiceInput()
        
        # vInput = vInput.replace(".","")
        vInput = vInput.replace(" ","_")
        print("new def(): " + vInput + "\n" +
              "Is this correct? (Yes/No)")
        prompt.insert(tk.END, "def " + vInput + "():\n" +
              "Is this correct? (Yes/No)")
        if confirm(prompt): correctPrint = True
        
    printLine = vInput
    
    string = "def " + printLine + "():\n    "
    return string

# *********************************************************************************
# returns strings to GUI windows: tex,tex2,tex3,tex4
# *********************************************************************************
def listen(tex,tex2,tex3,tex4):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        try:
            #audioToText = r.recognize_sphinx(audio)
            audioToText = r.recognize_google(audio)
            txtEditorTxt = phraseMatch(audioToText,tex2,tex3,tex4)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""
    return txtEditorTxt
