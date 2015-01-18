#!/usr/bin/python

from gi.repository import Gtk, GLib, GObject
import threading
import time
from datetime import datetime
import subprocess
#import serial
#from scipy.signal import

class Handler:
    link = ""    
    def showOutput(self, op_str):
        global textView
        textView.get_buffer().set_text(op_str)
        #print op_str, l
        
    def getFormats(self):
        ydl = subprocess.Popen(["youtube-dl", self.link, "-F"], stdout=subprocess.PIPE)
        output = ydl.communicate()[0]
        GLib.idle_add(self.showOutput, output)
        #print "This is a thread! :D", self.link
        
    def vidDownloadThread(link, destination):
        ydl = subprocess.Popen(["youtube-dl", self.link, "-F"], stdout=subprocess.PIPE)
        

    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def onFocusOut(self, widget, *args):
        self.link = widget.get_text()
        print self.link
        #self.showOutput("HH")
        getFormatThread = threading.Thread(target=self.getFormats)
        getFormatThread.daemon = True
        getFormatThread.start()

    def onStartDownload(self, fileChooser, *args):
        global textView
        global formatSel
        end_iter = textView.get_buffer().get_end_iter()
        textView.get_buffer().insert(end_iter, "Downloading "+formatSel.get_active_text()+" file to ")
        dest = fileChooser.get_filenames()[0]
        textView.get_buffer().insert(end_iter, dest+"\n")
        

def app_main():
    #Get the gui from the glade file
    builder = Gtk.Builder()
    builder.add_from_file("ytdl-gui.glade")
    builder.connect_signals(Handler())
    global textView
    textView = builder.get_object("textview1")
    global pbar
    pbar = builder.get_object("progressbar1")
    global formatSel
    formatSel = builder.get_object("formatSel")

        
    window = builder.get_object("MainWindow")
    window.show_all()   


if __name__ == "__main__":
    GObject.threads_init()
    app_main()
    Gtk.main()
