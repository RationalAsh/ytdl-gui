#!/usr/bin/python

from gi.repository import Gtk, GLib, GObject
import threading
import time
from datetime import datetime
import subprocess
import re
import pexpect
#import serial
#from scipy.signal import

class Handler:
    link = ""
    #Function to show terminal output
    def showOutput(self, op_str):
        global textView
        global statusBar
        #global window
        textView.get_buffer().set_text(op_str)
        cont = statusBar.get_context_id("Talk about data")
        statusBar.pop(cont)
        #print op_str, l
    
    #Helper function to extract formats
    def extractFormats(self, terminal_output):
        lines = terminal_output.split('\n')
        idx = 0
        final_idx = 0
        fmts = []
        for l in lines:
            if 'format code' in l:
                idx = lines.index(l)
                final_idx = idx
        for l in lines[idx:]:
            if 'DASH' in l:
                final_idx += 1
        temp = lines[final_idx+1:]
        for lin in temp:
            fmts.append([s.strip() for s in lin.split(' ') if s.strip()])
        return fmts

    def updateFormats(self, formats):
        global formatSel
        for i in xrange(len(formats) - 1):
            print formats[i][0] + " " +formats[i][1] + " " + formats[i][2], i
            formatSel.append_text(formats[i][0] + " " +formats[i][1] + " " + formats[i][2])
        

    #Function that populates the dropdown menu with available formats
    def getFormats(self):
        global formatList
        #GLib.idle_add()
        ydl = subprocess.Popen(["youtube-dl", self.link, "-F"], stdout=subprocess.PIPE)
        output = ydl.communicate()[0]
        lines = output.split('\n')
        #fmtBest = re.findall(r'\d+', lines[len(lines)-2])[0]
        fmts = self.extractFormats(output)
        formatList = fmts
        GLib.idle_add(self.showOutput, output)
        GLib.idle_add(self.updateFormats, fmts)
        #print "This is a thread! :D", self.link

    def updateDownloadProgress(self, i):
        global pbar
        pbar.set_fraction(i)
        
    # def vidDownloadThread(link, destination):
    #     ydl = subprocess.Popen(["youtube-dl", link, "-F"], stdout=subprocess.PIPE)
    #     i = 0
    #     while True:
    #         inline = ydl.stdout.readline()
    #         if not inline:
    #             break
    #         print inline, destination
    #         i += 1
    #         fract = (i%100)/100.0
    #         Glib.idle_add(self.updateDownloadProgress, fract)
    #         time.sleep(0.5)
        

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
        textView.get_buffer().insert(end_iter, "Downloading "+formatSel.get_active_text().split(" ")[0]+" file to ")
        try:
            dest = fileChooser.get_filenames()[0]
        except IndexError:
            pass
        textView.get_buffer().insert(end_iter, dest+"\n")
        download_t = threading.Thread(target=self.vidDownloadThread, args=(dest, formatSel.get_active_text().split(" ")))
        download_t.daemon = True
        download_t.start()

    def vidDownloadThread(self, dest, fmt):
        global textView
        global formatSel
        global formatList
        global linkEntry
        global fileName

        link = linkEntry.get_text()
        video_name = fileName.get_text()
        video_name += "."+fmt[1]
        fmt_code = fmt[0]

        print "Saving "+video_name+"to"+dest, fmt, link, 

        #ydl = subprocess.Popen(["youtube-dl", link, "-F"], stdout=subprocess.PIPE)
        #download = pexpect.spawn('youtube-dl ' + '-f '+ str(fmt_code) + '-o ' + dest + video_name)
        command_str = 'youtube-dl ' + link + ' -f '+ str(fmt_code) + ' -o ' + dest + "/" + video_name
        download = pexpect.spawn(command_str)
        percent = 0.0
        cont = statusBar.get_context_id("Talk about data")
        statusBar.push(cont, "Downloading...")

        while True:
            string = download.read_nonblocking(1000, 10)
            print string
            idx = string.find("%")
            if(idx >= 4):
                try:
                    percent = float(string[idx-4:idx])
                except:
                    GLib.idle_add(self.updateDownloadProgress, 1.00)
                    print 'Download thread done'
                    break
                if(percent == 100.0):
                    print 'Download thread done'
                    GLib.idle_add(self.updateDownloadProgress, 1.00)
                    break
                GLib.idle_add(self.updateDownloadProgress, percent/100)
        
        statusBar.push(cont, "Done! :D")
            
            

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
    global linkEntry
    linkEntry = builder.get_object('entry1')
    global fileName
    fileName = builder.get_object('entry2')

    global window    
    window = builder.get_object("MainWindow")
    window.show_all()   


if __name__ == "__main__":
    GObject.threads_init()
    app_main()
    Gtk.main()
