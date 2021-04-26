'''
import pyaudio
import wave

chunk = 1024

f = wave.open(r"VoiceTraining/line2.wav","rb")

p = pyaudio.PyAudio()

stream = p.open(format = p.get_format_from_width(f.getsampwidth()), channels = f.getnchannels(), rate = f.getframerate(), output = True)

data = f.readframes(chunk)

while data:
    stream.write(data)
    data = f.readframes(chunk)

    stream.stop_stream()
    stream.close()

    p.terminate()
'''
print("Start of testplay.py")

#from playsound import playsound
#playsound('VoiceTraining/line2.wav')

from pydub import AudioSegment
from pydub.playback import play

sound = AudioSegment.from_file("line1.wav")
print("Playing wav file...")
play(sound)

print("End of program")