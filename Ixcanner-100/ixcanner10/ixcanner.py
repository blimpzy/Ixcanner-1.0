import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gio, Gdk, GObject
import subprocess
import threading
import time
import random
import os
from PIL import Image


class IxcannerWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Ixcanner")
        self.connect("destroy", Gtk.main_quit)

        self.canscan = False

        self.searchresults = []

        self._devices = []

        self.isSearchRunning = False

        self.printers = Gtk.Button()
        
        

        self.set_resizable(False)
        self.set_border_width(10)
        self.set_default_size(500,300)
        self.set_position(Gtk.WindowPosition.CENTER)
        outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(outer_box)
        

        hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.headerbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        hbox.pack_start(self.headerbox , False, True, 0)
        self.button1 = Gtk.Button(label="Search")
        self.button1.connect("clicked", self.Search)
        
        self.spinner = Gtk.Spinner()
        self.label1 = Gtk.Label(label="Search for available printers.")

        self.button1box = Gtk.Box()
        self.button1box.pack_start(self.button1,False,False,0)

        self.headerbox.pack_start(self.button1box,False,False,0)
        self.headerbox.pack_end(self.label1,False,False,0)
        self.headerbox.pack_end(self.spinner,False,False,0)
        
        grid2 = Gtk.Grid(column_spacing=10, row_spacing=10)
        

        hbox.pack_start(grid2, False, False, 0)
        self.printerslist = Gtk.ComboBoxText()
        self.signalprinterlist = self.printerslist.connect("changed",self.SetDeviceName)
        grid2.attach(self.printerslist,0,0,49,5)

        self.folderbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.pack_start(self.folderbox , False, False, 0)
        folderlabel = Gtk.Label(label="Select Folder:")
        self.folderbox.pack_start(folderlabel, False,False, 0)
        self.selectfolderbutton = Gtk.FileChooserButton(action=Gtk.FileChooserAction.SELECT_FOLDER)
        self.selectfolderbutton.set_current_folder(os.getcwd())
        self.filepathevent = self.selectfolderbutton.connect("file-set", self.SetFilePath)
        self.folderbox.pack_end(self.selectfolderbutton, False,False, 0)

        self.filenamebox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.pack_start(self.filenamebox , False, False, 0)
        filenamelabel = Gtk.Label()
        filenamelabel.set_markup("Filename:")
        self.filenamebox.pack_start(filenamelabel, False,False, 0)

        #------------IMPORTANT----------------#
        self.name_r = "image"+str(random.randint(0,999999999999))
        self.folderto = ""
        self.extensionto = ""
        self.devicename = ""
        self.ipdevice = ""
        #------------IMPORTANT----------------#

        

        self.filename = Gtk.Entry(text=self.name_r)
        
        self.filename.connect("key_release_event", self.SetFileName)
        self.filenamebox.pack_end(self.filename, False,False, 0)
        

        self.extensionbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.pack_start(self.extensionbox , False, False, 0)
        extensionlabel = Gtk.Label()
        extensionlabel.set_markup("File Extension:")
        self.extensionbox.pack_start(extensionlabel, False,False, 0)
        self.comboextensionlabeltext = Gtk.ComboBoxText()
        self.comboextensionlabeltext.insert(0,"png", "png")
        self.comboextensionlabeltext.insert(1,"jpeg", "jpeg")
        self.comboextensionlabeltext.insert(2,"tif", "tif")
        self.comboextensionlabeltext.insert(3,"pnm", "pnm")
        self.comboextensionlabeltext.insert(4,"pdf", "pdf")
        self.comboextensionlabeltext.set_active(3)
        self.comboextensionlabeltext.connect("changed",self.SetFileExtension)
        self.extensionbox.pack_end(self.comboextensionlabeltext, False,False, 0)


        self.buttonactionbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        
        self.button33 = Gtk.Button(label="Scan")
        self.button33.connect("clicked", self.DoScan)
        self.buttonactionbox.pack_end(self.button33, True,True, 0)
        hbox.pack_start(self.buttonactionbox , True, True, 20)

        self.progressbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox.pack_start(self.progressbox , True, True, 0)

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_show_text(True)
        self.progressbar.set_text(" ")
        self.progressbar.set_fraction(0)
        self.progressbox.pack_start(self.progressbar , True, True, 0)
        


        outer_box.pack_start(hbox, True, True , 0) 

        self.canPulse = False
        self.scanthread = threading.Thread(target=self.PulseBar)
        self.scanthread.daemon = True
        self.scanthread.start()

        self.scanthread = threading.Thread(target=self.ScanProcess)
        self.scanthread.daemon = True
        self.scanthread.start()

        self.thread = threading.Thread(target=self.SearchForPrinters)
        self.thread.daemon = True
        self.signal_handler = None

        self.warbox = None

    def SetDeviceName(self, widget):
        self.devicename = ""
        self.devicename = self.printerslist.get_active_text()
        xx = 0
        ip = ""
        while(xx<len(self._devices)):
            if(self.devicename == self._devices[xx][0]):
                ip = self._devices[xx][1]
            xx += 1
        
        self.ipdevice = ip
        
        

    def DoScan(self, widget):
        filtered = self.filename.get_text().strip()
        if(self._devices == []):
            if(filtered == ""):
                self.WarningBox("<big>You need to name your file!</big>")
            else:
                self.canscan = False
            
        else:
            if (filtered == ""):
                self.WarningBox("<big>You need to name your file!</big>")
            else:
                self.canscan = True
            

    def PulseBar(self):
        while True:
            if (self.canPulse == False):
                None
            else:
                self.progressbar.pulse()
                self.progressbar.set_text("Scanning...")
                time.sleep(0.5)
                

    

    def ScanProcess(self):
        while True:
            if (self.canscan == False):
                    None
            else:
                
                if(self.extensionto == "pdf"):
                    
                    self.canPulse = True
                    rr = os.system('scanimage -d '+self.ipdevice+' --resolution=300dpi -x673.1mm -y928.2mm --mode=Color --format png > '+self.folderto+'/'+self.name_r+'.png')
                    self.canPulse = False
                    self.progressbar.set_fraction(1)
                    image1 = Image.open(r''+self.folderto+'/'+self.name_r+'.png')
                    im1 = image1.convert('RGB')
                    im1.save(r''+self.folderto+'/'+self.name_r+'.pdf')
                    os.system('rm '+self.folderto+'/'+self.name_r+'.png')
                    
                else:
                    
                    #w = 673.1
                    #h = 928.2
                    self.canPulse = True
                    rr = os.system('scanimage -d '+self.ipdevice+' --resolution=300dpi -x673.1mm -y928.2mm --mode=Color --format '+self.extensionto+' > '+self.folderto+'/'+self.name_r+'.'+self.extensionto)
                    self.canPulse = False
                    self.progressbar.set_text("Done!")
                    self.progressbar.set_fraction(1)
                    
                self.canscan = False

    def SetFileExtension(self, widget):
        self.extensionto = self.comboextensionlabeltext.get_active_text()

    def SetFilePath(self, widget):
        self.folderto = Gio.File.get_path(self.selectfolderbutton.get_file())
        

    def SetFileName(self, widget, event):
        
        filtered = self.filename.get_text().strip()
        if filtered == "":
            None
        else: 
            if(filtered.find(".") == -1):
                
                self.name_r = self.filename.get_text()
            else:
                
                self.WarningBox("<big>You can't use '.' !</big>")
                self.filename.set_text(self.name_r)

    def WarningBox(self, warning):
        self.warbox = Gtk.Window(title="Oops!", deletable=False, mnemonics_visible=False)
        self.warbox.deiconify()
        self.warbox.set_decorated(False)
        self.warbox.set_position(Gtk.WindowPosition.CENTER)
        self.warbox.set_resizable(False)
        self.warbox.set_border_width(10)
        self.warbox.set_default_size(500,130)
        wartext = Gtk.Label()
        wartext.set_markup(warning)
        
        hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.warbox.add(hbox)
        hbox.pack_start(wartext, True, False, 0)
        closebutton = Gtk.Button(label="Close")
        closebutton.connect("clicked", self.CloseWarningBox)
        hbox.pack_end(closebutton, True, False, 0)
        
        self.warbox.show_all()

    def CloseWarningBox(self, widget):
        self.warbox.close()

    def AddPrinters(self, widget, __printers, possible, refresh=False):
        if(possible==True):
            if(refresh == True):
                self.printers.disconnect(self.signal_handler)

                temporarylist = []

                r = __printers.rsplit("/*DEVICE*/")
                r[0] = r[0].replace("b'","",1)
                r.remove(r[len(r)-1])

                for x in r: 
                    
                    _total = len(x)
                    rrr = x.find("+/IP/+")
                    i = 0
                    devicename = ""
                    while(i<rrr):
                        devicename += x[i]
                        i += 1
                    
                    ip = ""
                    y=rrr+6
                    while(y<_total):
                        ip += x[y]
                        y += 1
                    temporarylist.append([devicename, ip])
                    
                self.RemoveAllPrinters()
            
                self._devices = []
                z2 = 0
                while(z2<len(temporarylist)):
                    self._devices.append([temporarylist[z2][0],temporarylist[z2][1]])
                    z2+=1
                
                temporarylist = []
                z3 = 0
                while(z3<len(self._devices)):
                    self.NewRow(self._devices[z3][1], self._devices[z3][0])
                    
                    z3+=1
                self.label1.set_text("There are printers available!")
                self.spinner.stop()
                
            else:
                self.printers.disconnect(self.signal_handler)
                self.label1.set_text("There are printers available!")
                self.spinner.stop()
                
                r = __printers.rsplit("/*DEVICE*/")
                r[0] = r[0].replace("b'","",1)
                
                r.remove(r[len(r)-1])

                for x in r: 
                    _total = len(x)
                    rrr = x.find("+/IP/+")
                    i = 0
                    devicename = ""
                    while(i<rrr):
                        devicename += x[i]
                        i += 1
                        
                    ip = ""
                    y=rrr+6
                    while(y<_total):
                        ip += x[y]
                        y += 1
                    self._devices.append([devicename, ip])
                    
                    self.NewRow(ip, devicename)
        else:
            self.printers.disconnect(self.signal_handler)
            
            self.label1.set_text("There are no printers available.")
            self.spinner.stop()

    def NewRow(self, ip, device):

        self.printerslist.append(ip, device)
        self.printerslist.set_active(0)

    def RemoveAllPrinters(self):
        self.printerslist.remove_all()
        self.canscan = False

    def Search(self, widget):
        if(self.isSearchRunning == False):
            
            self.thread.start()
            
            self.spinner.start()
            self.label1.set_text("Searching for printers...")
            
        else:
            
            self.spinner.start()
            self.label1.set_text("Searching for printers...")
            
            _sr = self.searchresults[0]
            _se = self.searchresults[1]
            
            if(_se == "b''" and _sr!=None):
                self.RemoveAllPrinters()
                self.signal_handler = self.printers.connect("clicked", self.AddPrinters, _se, False)
                self.printers.clicked()
            else:
                if(_se != "b''" and _sr!=None):
                    
                    self.signal_handler = self.printers.connect("clicked", self.AddPrinters, _se, True, True)
                    self.printers.clicked()

        

    def SearchForPrinters(self):
        while True:
            _rr = subprocess.run(["scanimage", "-f", "%m+/IP/+%d/*DEVICE*/"], capture_output=True)
            _ss = _rr.stdout
            
            self.searchresults = []
            self.searchresults.append(_rr)
            self.searchresults.append(str(_ss))
            r = GLib.idle_add(self.GetPrinters, _ss, _rr)
            if (r):
                time.sleep(1)
                self.isSearchRunning = True
        
            
            
    
    def GetPrinters(self, s=None, r=None):
        if (self.isSearchRunning == False):
            
            if(s == None and r == None):
                _s = None
            else:
                if(str(s) == "b''" and r!=None):
                    _s="nop"
                    self.signal_handler = self.printers.connect("clicked", self.AddPrinters, _s, False)
                    self.printers.clicked()
                    self.button1.set_label("Refresh")
                        
                if(str(s) != "b''" and r!=None):
                    _s=str(s)
                    self.signal_handler = self.printers.connect("clicked", self.AddPrinters, _s, True)
                    self.printers.clicked()
                    self.button1.set_label("Refresh")
   
        else:
            None

        return None
    
def start():
    win = IxcannerWindow()
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    None
