import tkinter as tk
import speech_recognition as sr
import threading

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
        audio_txt = ( r.recognize_sphinx(audio)) + "\n"
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