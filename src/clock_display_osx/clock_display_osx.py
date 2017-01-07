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

    def displayPrefWindow_(self, sender):
        self.clock.DisplayPreferencesWindow()
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


class ClockDisplay():

    def DisplayPreferencesWindow(self):
        print "DEBUG: Called ClockDisplay::PreferencesWindow"
        frame = ((100.0, 650.0), (self.WindowWidth, self.WindowHeight))
        self.prefwin.initWithContentRect_styleMask_backing_defer_ (frame, 15, 2, 0)
        print "DEBUG: ClockDisplay::PreferencesWindow init done"
        self.prefwin.setTitle_ ('Preferences')
        self.prefwin.display()
        print "DEBUG: ClockDisplay::PreferencesWindow display done"
        self.prefwin.makeKeyAndOrderFront_(self.app)
        print "DEBUG: Exited ClockDisplay::PreferencesWindow"

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
        self.testmenu.removeAllItems()
        self.testmenu.addItemsWithTitles_( self.ScanSerialPorts() )
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

        #setup notification center
        self.not_cent = Foundation.NSNotificationCenter.defaultCenter()

        frame = ((100.0, 650.0), (self.WindowWidth, self.WindowHeight))
        self.win.initWithContentRect_styleMask_backing_defer_ (frame, 15, 2, 0)
        self.win.autorelease()
        self.win.setTitle_ ('Archery Clock')
        self.win.setFrame_display_animate_
        self.wincontroller = NSWindowController.alloc()
        self.wincontroller.initWithWindow_(self.win)
        self.wincontroller.autorelease()


        bye = NSButton.alloc().initWithFrame_ (((120.0, 10.0), (100.0, 25.0)))
        self.win.contentView().addSubview_( bye )
        bye.setBezelStyle_( 4 )
        bye.setTarget_ ( self.app )
        bye.setAction_ ( 'stop:' )
        bye.setEnabled_ ( 1 )
        bye.setTitle_( 'ShutDown' )

        rescan = NSButton.alloc().initWithFrame_ (((10.0, 10.0), (100.0, 25.0)))
        self.win.contentView().addSubview_ (rescan)
        rescan.setBezelStyle_( 4 )
        rescan.setTitle_( 'Rescan' )
        rescan.setTarget_( self.app.delegate() )
        rescan.setAction_( "buildSerialPortsMenu:" )

        prefbut = NSButton.alloc().initWithFrame_ (((230.0, 10.0), (100.0, 25.0)))
        self.win.contentView().addSubview_ (prefbut)
        prefbut.setBezelStyle_( 4 )
        prefbut.setTitle_( 'Pref.' )
        prefbut.setTarget_( self.app.delegate() )
        prefbut.setAction_( "displayPrefWindow:" )

        self.testmenu = NSPopUpButton.alloc().initWithFrame_(((10.0, 100.0), (self.win.frame().size.width-20.0, 20.0)))
        self.testmenu.setTitle_("serialmenu")
        self.win.contentView().addSubview_( self.testmenu )

        self.not_cent.addObserver_selector_name_object_(self.app.delegate(), 'buildSerialPortsMenu:', 'NSPopUpButtonWillPopUpNotification', self.testmenu)

        self.win.display()
        self.win.orderFrontRegardless()          ## but this one does
        self.win.makeMainWindow()

        AppHelper.runEventLoop()

    def __init__(self):
        self.WindowWidth  = 500.0
        self.WindowHeight = 200.0
        self.prefwin = NSWindow.alloc()
        self.win     = NSWindow.alloc()
