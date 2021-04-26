import os
import shutil
import glob
import sys

'''
path = os.getcwd() + "sphinxtrain-master\bin\Debug\Win32"
#os.environ["PATH"] += os.pathsep + path
sys.path += [path]
path = os.getcwd() + "sphinxbase\bin\Debug\Win32"
#os.environ["PATH"] += os.pathsep + path
sys.path += [path]
print(os.environ["PATH"])
'''
'''
os.system("sphinx_fe -argfile AcousticModels/en-us/feat.params -samprate 16000 -c TrainingModel/test/test.fileids -di TrainingModel/test/ -do TrainingModel/test/ -ei wav -eo mfc -mswav yes")

os.chdir("TrainingModel/test")

os.system("bw -hmmdir ../../AcousticModels/en-us/ -moddeffn ../../AcousticModels/en-us/mdef.txt -ts2cbfn .ptm. -feat 1s_c_d_dd -svspec 0-12/13-25/26-38 -cmn current -agc none -dictfn ../../cmudict-en-us.dict -ctlfn test.fileids -lsnfn test.transcription -accumdir .")

os.chdir("..\..")

isdir = os.path.isdir("AcousticModels/test215")
if isdir == False:
    os.mkdir("AcousticModels/test215")

else:
    print("Directory already found, overwriting content in there.")


for file in glob.glob(r"AcousticModels/en-us/*"):
    print(file)
    shutil.copy(file, "AcousticModels/test215/")

os.system("map_adapt -moddeffn AcousticModels/en-us/mdef.txt -ts2cbfn .ptm. -meanfn AcousticModels/en-us/means -varfn AcousticModels/en-us/variances -mixwfn AcousticModels/en-us/mixture_weights -tmatfn AcousticModels/en-us/transition_matrices -accumdir TrainingModel/test/ -mapmeanfn AcousticModels/test215/means -mapvarfn AcousticModels/test215/variances -mapmixwfn AcousticModels/test215/mixture_weights -maptmatfn AcousticModels/test215/transition_matrices")
'''
#for file in glob.glob(r"VoiceTraining/TrainingModel/*"):
#    print(file)
#print(os.listdir("VoiceTraining/TrainingModel/test/*.fileids"))

'''for file in glob.glob(r"VoiceTraining/TrainingModel/arctic20/*.fileids"):
    testString = file.split("\\")
    testString = testString[1]
    testString = testString.split(".")
    testString = testString[0]
    print(testString)'''


print("Removing these files from VoiceTraining/Profiles/en-US/acoustic-model/")
for file in glob.glob("VoiceTraining/Profiles/en-US/acoustic-model/*"):
    print(file)
    os.remove(file)
print("Removed files from that directory")

print("Copying files from VoiceTraining/AcousticModels/steven/ over to VoiceTraining/Profiles/en-US/acoustic-model/")
for file in glob.glob("VoiceTraining/AcousticModels/steven/*"):
    print(file)
    shutil.copy(file, "VoiceTraining/Profiles/en-US/acoustic-model/")
print("Finished copying over files")

for file in glob.glob("VoiceTraining/Profiles/en-US/acoustic-model/*"):
    print(file)

print("Finished test program")
