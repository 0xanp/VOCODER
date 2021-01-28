import os

os.system('clear')
os.system('echo "Creating adapted language model"')

path = ""
profileExists = True
while profileExists:
    profileName = input("What's the name you want to use for the language model?\n")
    isdir = os.path.isdir(path + "AcousticModels/en-us-" + profileName)
    if isdir == False:
        profileExists = False
    else:
        reply = input("Model name already exists. Would you like to overwrite it? (Y/N)\n")
        if reply == "y" or reply == "Y":
            profileExists = False
        else:
            print("Please enter another name for language model.")

pathExists = False
while not pathExists:
    dirName = input("Input complete path and name of directory containing wav files to use for training.\n" +
    "(Don't include '/' at the end)\n")
    isdir = os.path.isdir(path + dirName)
    if isdir == True:
        pathExists = True
    else:
        print("Directory not found. Please try again.")
        
fileExists = False
while not fileExists:
    fileName = input("Input name of fileids and transcription file without extension.\n")
    idsName = fileName + ".fileids"
    transName = fileName + ".transcription"
    isfile = os.path.isfile(path + dirName + "/" + idsName)
    if isfile == False:
        print(fileName + ".fileids not found.\n")
        continue
    isfile = os.path.isfile(path + dirName + "/" + transName)
    if isfile == False:
        print(fileName + ".transcription not found.\n")
        continue
    fileExists = True
    
       
# train a new adapted language model
os.system("sphinx_fe " +
            "-argfile AcousticModels/en-us/feat.params " +
            "-samprate 16000 " +
            "-c " + dirName + "/" + idsName + " "
            "-di " + dirName + "/ " +
            "-do " + dirName + "/ " +
            "-ei wav " + 
            "-eo mfc " + 
            "-mswav yes")

         
os.chdir(dirName)
os.system("../.././bw " +
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
os.chdir("../..")

os.system("cp -af AcousticModels/en-us AcousticModels/" + profileName)

os.system("./map_adapt " +
            "-moddeffn AcousticModels/en-us/mdef.txt " +
            "-ts2cbfn .ptm. " +
            "-meanfn AcousticModels/en-us/means " +
            "-varfn AcousticModels/en-us/variances " +
            "-mixwfn AcousticModels/en-us/mixture_weights " +
            "-tmatfn AcousticModels/en-us/transition_matrices " +
            "-accumdir " + dirName + " " +
            "-mapmeanfn AcousticModels/" + profileName + "/means " +
            "-mapvarfn AcousticModels/" + profileName + "/variances " +
            "-mapmixwfn AcousticModels/" + profileName + "/mixture_weights " +
            "-maptmatfn AcousticModels/" + profileName + "/transition_matrices")
