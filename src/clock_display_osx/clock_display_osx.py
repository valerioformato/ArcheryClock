import sys
import glob
import serial

import objc
from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper


class AppDelegate (NSObject):
    def setClock_(self, clock):
        self.clock = clock
        pass

    def buildSerialPortsMenu_(self, sender):
        self.clock.BuildSerialPortsMenu()
        pass

    def debugNotifications_(self, aNotification):
        print "Not:", aNotification.name()
        print "From:", aNotification.object()
        print aNotification.userInfo()
        pass

    def applicationDidFinishLaunching_(self, aNotification):
        pass

class ClockWindowController(NSWindowController):
    def setClock_(self, clock):
        self.clock = clock
        pass

    @objc.IBAction
    def displayPrefWindow_(self, sender):
        self.clock.DisplayPreferencesWindow()
        pass


class ClockDisplay():

    def DisplayPreferencesWindow(self):
        frame = ((100.0, 650.0), (400.0, 300.0))
        prefwin = NSWindow.alloc()
        prefwin.initWithContentRect_styleMask_backing_defer_ (frame, 15, 2, 0)
        prefwin.setTitle_ ('Preferences')
        self.prefwincontroller = NSWindowController.alloc().initWithWindow_(prefwin)
        self.prefwincontroller.showWindow_(self.app)
        prefwin.makeKeyAndOrderFront_(self.app)

    def DisplayMainWindow(self):
        frame = ((400.0, 650.0), (self.WindowWidth, self.WindowHeight))
        self.win = NSWindow.alloc()
        self.win.initWithContentRect_styleMask_backing_defer_ (frame, 15, 2, 0)
        self.win.setTitle_ ('Archery Clock')
        self.win.setFrame_display_animate_

        rescan = NSButton.alloc().initWithFrame_ (((10.0, 10.0), (100.0, 25.0)))
        self.win.contentView().addSubview_ (rescan)
        rescan.setBezelStyle_( 4 )
        rescan.setTitle_( 'Rescan' )
        rescan.setTarget_( self.app.delegate() )
        rescan.setAction_( "buildSerialPortsMenu:" )

        prefbut = NSButton.alloc().initWithFrame_ (((120.0, 10.0), (100.0, 25.0)))
        self.win.contentView().addSubview_ (prefbut)
        prefbut.setBezelStyle_( 4 )
        prefbut.setTitle_( 'Pref.' )
        prefbut.setTarget_( self.menuViewController )
        prefbut.setAction_( "displayPrefWindow:" )

        self.serialmenu = NSPopUpButton.alloc().initWithFrame_(((10.0, 100.0), (self.win.frame().size.width-20.0, 20.0)))
        self.serialmenu.setTitle_("serialmenu")
        self.win.contentView().addSubview_( self.serialmenu )

        self.win.center()
        self.wincontroller = NSWindowController.alloc().initWithWindow_(self.win)
        self.wincontroller.showWindow_(self.app)
        pass

    def SetupNotificationCenter(self):

        #close app if click on red button
        self.not_cent.addObserver_selector_name_object_(self.app, 'stop:', 'NSWindowDidCloseNotification', self.win)
        #refresh serial port list on menu click
        self.not_cent.addObserver_selector_name_object_(self.app.delegate(), 'buildSerialPortsMenu:', 'NSPopUpButtonWillPopUpNotification', self.serialmenu)
        pass

    def SetupMenus(self, app, delegate):
        prefmenu = self.app.mainMenu.itemAtIndex_(0).submenu
        print prefmenu.isEnabled
        pass


    def ScanSerialPorts(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                if "bluetooth" in port.lower():
                    port = "[Bluetooth] " + port
                elif "usb" in port.lower():
                    port = "[USB] " + port

                result.append(port)
            except (OSError, serial.SerialException):
                pass

        print "DEBUG:", result
        return result

    def BuildSerialPortsMenu(self):
        self.serialmenu.removeAllItems()
        self.serialmenu.addItemsWithTitles_( self.ScanSerialPorts() )
        self.win.update()
        pass

    def StartApp(self):
        self.app = NSApplication.sharedApplication()

        # we must keep a reference to the delegate object ourselves,
        # NSApp.setDelegate_() doesn't retain it. A local variable is
        # enough here.
        self.delegate = AppDelegate.alloc().init()
        self.delegate.setClock_(self)
        NSApp().setDelegate_(self.delegate)

        #get notification center
        self.not_cent = Foundation.NSNotificationCenter.defaultCenter()

        #set up main menu
        self.menuViewController = ClockWindowController.alloc().initWithWindowNibName_("MainMenu")
        self.menuViewController.setClock_(self)
        self.menuViewController.showWindow_(self.menuViewController)
        # self.SetupMenus(self.app, self.app.delegate())

        #show main window
        self.DisplayMainWindow()

        #setup notiication center
        self.SetupNotificationCenter()

        AppHelper.runEventLoop()

    def __init__(self):
        self.WindowWidth  = 500.0
        self.WindowHeight = 200.0
