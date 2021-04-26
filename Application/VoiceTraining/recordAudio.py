# Program to read a .transcription file from a specified directory and record the user speaking each line from them.

import os
import shutil
import sounddevice as sd
from scipy.io.wavfile import write
from pydub import AudioSegment
from pydub.playback import play

path = ""
pathExists = False
while not pathExists:
    dirName = input("Input complete name of directory containing the fileids and transcription file.\n")
    isdir = os.path.isdir(path + dirName)
    if isdir == True:
        pathExists = True
        dirPath = path + dirName
    else:
        print("Directory not found. Please try again.")
        
fileExists = False
while not fileExists:
    fileName = input("Input name of fileids and transcription files without extension.\n")
    transName = fileName + ".transcription"
    transPath = dirPath + "/" + transName
    isfile = os.path.isfile(transPath)
    if isfile == False:
        print("Both files not found.\n")
        continue
    fileExists = True

transFile = open(transPath, "r")
fileLines = transFile.read().split("\n")
fileLines.pop()
transFile.close()

duration = 8
freq = 16000
print("You have " + str(duration) + " seconds to say each line up to the \":\" symbol.")

for fileLine in fileLines:
    line = fileLine
    index = line.index("<",4)
    lastIndex = line.index(")", index + 6)
    fileName = line[index + 6 : lastIndex]

    goodRecording = False
    while not goodRecording:
        print()
        print(line[4:index] + ": " + fileName)

    
        recording = sd.rec(int(duration * freq), samplerate = freq, channels = 1, dtype="int16")
        sd.wait()
        write(fileName + ".wav", freq, recording)

        print("Playing recording back...")

        sound = AudioSegment.from_file(fileName + ".wav")
        play(sound)

        userInput = input("Is the recording fine? (Y/N): ")
        if userInput == "Y" or userInput == "y":
            goodRecording = True
            shutil.move(fileName + ".wav ", dirPath + "/" + fileName + ".wav")
        else:
            print("Retaking recording, please resay the line.")
            os.remove(fileName + ".wav")

print("Recording finished.")

