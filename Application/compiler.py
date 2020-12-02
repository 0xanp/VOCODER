"""
- read output from a subprocess in a background thread
- show the output in the GUI
"""
import sys
from itertools import islice
from subprocess import Popen, PIPE
from textwrap import dedent
from threading import Thread

import tkinter as tk # Python 3
from queue import Queue, Empty # Python 3

def iter_except(function, exception):
    """Works like builtin 2-argument `iter()`, but stops on `exception`."""
    try:
        while True:
            yield function()
    except exception:
        return

class DisplaySubprocessOutputDemo:
    def __init__(self, root, script):
        self.root = root
        self.script = script
        # start dummy subprocess to generate some output
        self.process = Popen([sys.executable, "-u", "-c", self.script], stdout=PIPE)
        # launch thread to read the subprocess output
        #   (put the subprocess output into the queue in a background thread,
        #    get output from the queue in the GUI thread.
        #    Output chain: process.readline -> queue -> label)
        q = Queue(maxsize=1024)  # limit output buffering (may stall subprocess)
        t = Thread(target=self.reader_thread, args=[q])
        t.daemon = True # close pipe if GUI process exits
        t.start()

        # show subprocess' stdout in GUI
        self.listbox = tk.Listbox(self.root)
        self.listbox.grid(row=0,column=0,padx=5,pady=5,sticky='nsew')
        #self.label = tk.Label(root, text = "")
        #self.label.pack(ipadx=4, padx=4, ipady=4, pady=4, fill='both')
        self.update(q) # start update loop

    def reader_thread(self, q):
        """Read subprocess output and put it into the queue."""
        try:
            with self.process.stdout as pipe:
                for line in iter(pipe.readline, b''):
                    q.put(line)
        finally:
            q.put(None)

    def update(self, q):
        """Update GUI with items from the queue."""
        for line in iter_except(q.get_nowait, Empty): # display all content
            if line is None:
                return
            else:
                self.listbox.insert(tk.END,line) # update GUI
                break # display no more than one line per 40 milliseconds
        self.root.after(40, self.update, q) # schedule next update

    def quit(self):
        self.process.kill() # exit subprocess if GUI is closed (zombie!)
        self.root.destroy()


def main(text,root):
    app = DisplaySubprocessOutputDemo(root,text)
'''
text = dedent("""
                import itertools, time

                for i in itertools.count():
                    print("%d.%d" % divmod(i, 10))
                    time.sleep(0.1)
                """)
main(text)
'''