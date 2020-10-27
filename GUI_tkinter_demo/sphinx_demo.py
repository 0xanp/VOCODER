import tkinter as tk
import speech_recognition as sr
import threading
import re as re
from fuzzywuzzy import fuzz

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
                 "show set of variables"]

# this set will contain variable names created by createNewVariable()                 
setOfVariableNames = []

# function to get voice input and returns as a string
def getVoiceInput():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        audioToText = r.recognize_sphinx(audio)
    return audioToText
    
def phraseMatch(audioToText):
    print("input: " + audioToText + "\n")

    closestString = getClosestString(audioToText, commandWords)            

    if closestString == "create new variable":
        string = createNewVariable()
    elif closestString == "show set of variables":
        showSet()
        string = "used showSet()\n"
    elif closestString == "assign old variable":
        string = assignOldVariable()
    elif closestString == "return statement":
        string = returnStatement()
    elif closestString == "create for loop":
        string = createForLoop()
    elif closestString == "create if statement":
        string = createIfStatement()
    else:
        string = "no matching phrase found: " + audioToText + "\n"
    return string

def getClosestString(inputString, listToMatch):
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
    
    print("\nClosest string to match input was\n")
    print(closestString + ": " + str(highest))    
            
    return closestString
    
# Operations dictionary for string to symbol
op_dict = { "plus":"+", 
           "minus":"-", 
           "times":"*",
           "divided by":"/" }
           
compare_dict = { "less than"                : "<",
                 "less than or equal to"    : "<=",
                 "greater than"             : ">",
                 "greater than or equal to" : ">=",
                 "equal to"                 : "==",
                 "not equal to"             : "!=" }

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
def showSet():
    print("Currently in showSet() function.\n" +
          "Set of variable names:")
    for i in setOfVariableNames:
        print("          " + i + ",")
        
# receives input from user saying yes or no and returns true if yes, false if no
def confirm():
    vInput = getVoiceInput()
    yesRatio = fuzz.ratio(vInput, "yes")
    noRatio = fuzz.ratio(vInput, "no")
    print("yes: " + str(yesRatio) + "\n" +
          "no:  " + str(noRatio)  + "\n")
    if yesRatio > noRatio: return True 
    else: return False


# Very basic version of create new variable command. The terminal will prompt the user for voice input. The program will be able to take any string of characters and uses snake case for variable name. The program will be able to convert word versions of +, -, *, /, and numbers into their symbol versions.

# Example
# Voice input
#     variableName = test variable
#     expression   = one plus two minus three
#     output:        test_variable = 1 + 2 - 3

def createNewVariable():
    # Get and format variable name, will use snake case
    correctName = False
    nameTaken = True
    while not correctName or nameTaken:
        correctName = False
        nameTaken = True
        
        print("Say name of new variable.\n")
        vInput = getVoiceInput()
        vInput = vInput.replace(" ","_")
        variableName = vInput
        
        print("Variable name: " + variableName + "\n" +
              "Is this correct? (Yes/No)")
        if confirm(): correctName = True
        else: continue
        
        if variableName in setOfVariableNames:
            print("Variable name: " + variableName + ", is already used in the program.\n" +
                  "Do you still want to use it? (Yes/No)")
            if confirm(): nameTaken = False
        else:
            nameTaken = False
             
    
    # Get expression
    correctExpression = False
    while not correctExpression:    
        print("Say full expression.\n")
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
                    closestVariable = getClosestString(vInputSplit[i], setOfVariableNames)
                    
                    print("Got input of: " + str(vInputSplit) + "\n")
                    print("Closest match was: " + str(closestVariable) + "\n")
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
        if confirm(): correctExpression = True
        
    
    # used for checking correctness in terminal    
    # print("expression = " + expression)
    
    if variableName not in setOfVariableNames:
        setOfVariableNames.append(variableName)  
    
    string = variableName + " = " + expression + "\n"
    return string

def assignOldVariable():
    # check if there are any old variables
    if not setOfVariableNames:
        print("No variable names already initialized.\n")
        return ""
        
    # get input for the variable name to be modified
    correctName = False
    while not correctName:
        print("Say the name of the variable you want to modify.\n")
        vInput = getVoiceInput()
        variableName = getClosestString(vInput, setOfVariableNames)
        print("Variable name: " + variableName + "\n" +
              "Is this correct? (Yes/No)")
        if confirm(): correctName = True
        else: continue
        
    # get expression
    correctExpression = False
    while not correctExpression:    
        print("Say full expression.\n")
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
                    closestVariable = getClosestString(vInputSplit[i], setOfVariableNames)
                    
                    print("Got input of: " + str(vInputSplit) + "\n")
                    print("Closest match was: " + str(closestVariable) + "\n")
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
        if confirm(): correctExpression = True
        
    string = variableName + " = " + expression + "\n"
    return string
    
def returnStatement():
    # get voice input
    correctExpression = False
    while not correctExpression:    
        print("Say what you want to return.\n")
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
                    closestVariable = getClosestString(vInputSplit[i], setOfVariableNames)
                    
                    print("Got input of: " + str(vInputSplit) + "\n")
                    print("Closest match was: " + str(closestVariable) + "\n")
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
        if confirm(): correctExpression = True
    
    expression = "return " + expression + "\n"
    return expression

# for now, can only create a for loop with range function
def createForLoop():
    correctVariable = False
    while not correctVariable:
        print("Say the name of looping variable.\n")
        vInput = getVoiceInput()
        
        vInput = vInput.replace(".","")
        vInput = vInput.replace(" ","_")
        print("Looping variable: " + vInput + "\n" +
              "Is this correct? (Yes/No)")
        if confirm(): correctVariable = True
        
    loopingVariable = vInput
        
    correctRange = False
    while not correctRange:
        print("How many times do you want to repeat this loop?\n")
        vInput = getVoiceInput()
        
        vInput = str(text2int(vInput))
        
        print("Amount of loops: " + vInput + "\n" + 
              "Is this correct? (Yes/No)")
        if confirm(): correctRange = True
        
    rangeInt = vInput
    
    string = "for " + loopingVariable + " in range(" + rangeInt + "):\n"
    return string

    
def createIfStatement():
    correctCondition = False
    while not correctCondition:
        print("Say the condition you want for the if statement.\n")
        vInput = getVoiceInput()
        
        vInput = vInput.replace(".","")
        
        # replace strings of comparison operators with symbols
        for x, y in compare_dict.items():
            vInput = vInput.replace(x, y)
        
        
        # split string into array, while keeping the operator symbols
        vInputSplit = re.split("([<]|[<=]|[>]|[>=][==][!=])", vInput)
        
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
                    closestVariable = getClosestString(vInputSplit[i], setOfVariableNames)
                    
                    print("Got input of: " + str(vInputSplit) + "\n")
                    print("Closest match was: " + str(closestVariable) + "\n")
                    vInputSplit[i] = closestVariable
        
        # reformat expression
        expression = ""
        for i in range(0, len(vInputSplit)): 
            if i in opLocations:   
                expression = expression + vInputSplit[i]
            else:
                expression = expression + vInputSplit[i]
           
        print("Condition: " + expression + "\n" +
              "Is this correct? (Yes/No)")
        if confirm(): correctCondition = True
    
    condition = expression
    string = "if " + condition + ":\n"
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
