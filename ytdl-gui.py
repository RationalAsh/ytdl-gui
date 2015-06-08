#!/usr/bin/python

from gi.repository import Gtk, GLib, GObject
import threading
import time
from datetime import datetime
import subprocess
import re
#import serial
#from scipy.signal import

class Handler:
    link = ""    
    def showOutput(self, op_str):
        global textView
        global statusBar
        #global window
        textView.get_buffer().set_text(op_str)
        cont = statusBar.get_context_id("Talk about data")
        statusBar.pop(cont)
        #print op_str, l
        
    def getFormats(self):
        #GLib.idle_add()
        ydl = subprocess.Popen(["youtube-dl", self.link, "-F"], stdout=subprocess.PIPE)
        output = ydl.communicate()[0]
        lines = output.split('\n')
        fmtBest = re.findall(r'\d+', lines[len(lines)-2])[0]
        GLib.idle_add(self.showOutput, output)
        #print "This is a thread! :D", self.link

    def updateDownloadProgress(self, i):
        global pbar
        pbar.set_fraction(i)
        
    def vidDownloadThread(link, destination):
        ydl = subprocess.Popen(["youtube-dl", link, "-F"], stdout=subprocess.PIPE)
        i = 0
        while True:
            inline = ydl.stdout.readline()
            if not inline:
                break
            print inline, destination
            i += 1
            fract = (i%100)/100.0
            Glib.idle_add(self.updateDownloadProgress, fract)
            time.sleep(0.5)
        

    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def onFocusOut(self, widget, *args):
        global window
        global statusBar
        self.link = widget.get_text()
        print self.link
        cont = statusBar.get_context_id("Talk about data")
        statusBar.push(cont, "Getting video info. Please Wait...")
        #self.showOutput("HH")
        getFormatThread = threading.Thread(target=self.getFormats)
        getFormatThread.daemon = True
        getFormatThread.start()
        #window.set_sensitive(False)
        #time.sleep(5)
        #window.set_sensitive(True)

    def onStartDownload(self, fileChooser, *args):
        global textView
        global formatSel
        end_iter = textView.get_buffer().get_end_iter()
        textView.get_buffer().insert(end_iter, "Downloading "+formatSel.get_active_text()+" file to ")
        dest = fileChooser.get_filenames()[0]
        textView.get_buffer().insert(end_iter, dest+"\n")
        download_t = threading.Thread(target=self.vidDownloadThread, args=(dest,))
        download_t.daemon = True
        download_t.start()
        

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
    formatSel.set_active(0)
    global statusBar
    statusBar = builder.get_object("statusbar1")
    cont = statusBar.get_context_id("Talk about data")
    statusBar.push(cont, "Ready")

    global window    
    window = builder.get_object("MainWindow")
    window.show_all()   


if __name__ == "__main__":
    GObject.threads_init()
    app_main()
    Gtk.main()
