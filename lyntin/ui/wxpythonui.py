# -*- coding: cp1252 -*-
#######################################################################
# This file is part of Lyntin.
# copyright (c) Free Software Foundation 1999 - 2002
#
# Lyntin is distributed under the GNU General Public License license.  See the
# file LICENSE for distribution details.
#######################################################################
"""
This is a wxPython oriented user interface for lyntin.

Initial port from the tkui.py file by Bryan Muir

KNOWN BUGS
1. Thread error on closeing, intermittent.


New:
9-25-03:  Added Action Manager
          Added save functionality
          Added Load file
          
9-23-03:  Added Alias Manager

"""

from wxPython import wx
from wxPython import stc
import os, types, Queue, re
from lyntin import ansi, event, engine, exported, utils, constants, config, argparser
from lyntin.ui import base, message
from lyntin.modules import alias

from lyntin.ui.wxpui_forms import CommandPanel

##################################################################

USER_CONFIG = "user_config.ini"

import codecs

############################################################################

UNICODE_ENCODING = "latin-1"
ALIAS = 1
ACTION = 2


HELP_TEXT = """The wxpythonui uses wxPython and provides a graphical interface 
to Lyntin.  It also has the following additional functionality:

 - numpad bindings (VK_NUMPAD0 through VK_NUMPAD9)
 - function key bindings (VK_F2 through VK_F12)
 - pgup and pgdown scroll back (escape to get rid of the split 
   screen)
 - up and down command line history
 - ctrl-u removal of text
 - ctrl-c copy from the text buffer and ctrl-v paste into the command
   buffer (in Windows)
 - ctrl-t autotyper
 - NamedWindow handling

To bind function key and numpad bindings, create an alias for the
symbol.  For example:

   #alias {VK_NUMPAD2} {south}


"""

# the complete list of foreground color codes and what color they
# map to in RGB.
fg_color_codes = {"30": "#000000",
                  "31": "#aa0000",
                  "32": "#00dd00",
                  "33": "#daa520",
                  "34": "#0000aa",
                  "35": "#bb00bb",
                  "36": "#00cccc",
                  "37": "#aaaaaa",
                  "b30": "#666666",
                  "b31": "#ff3333",
                  "b32": "#00ff3f",
                  "b33": "#ffff00",
                  "b34": "#2222ff",
                  "b35": "#ff33ff",
                  "b36": "#70eeee",
                  "b37": "#ffffff" }

# the complete list of background color codes and what color they
# map to in RGB.
bg_color_codes = {"40": "#000000",
                  "41": "#ff0000",
                  "42": "#00ff00",
                  "43": "#daa520",
                  "44": "#0000aa",
                  "45": "#ff00ff",
                  "46": "#00cccc",
                  "47": "#bbbbbb",
                  "b40": "#777777",
                  "b41": "#fa6072",
                  "b42": "#00ff7f",
                  "b43": "#ffff00",
                  "b44": "#2222ff",
                  "b45": "#ee82ee",
                  "b46": "#70eeee",
                  "b47": "#ffffff" }


#a dictionary of virtual keycodes and their string based name.  Makes it easier to look
#up the string that something is bound to.
keyMap = {
    wx.WXK_BACK : "WXK_BACK",
    wx.WXK_TAB : "WXK_TAB",
    wx.WXK_RETURN : "WXK_RETURN",
    wx.WXK_ESCAPE : "WXK_ESCAPE",
    wx.WXK_SPACE : "WXK_SPACE",
    wx.WXK_DELETE : "WXK_DELETE",
    wx.WXK_START : "WXK_START",
    wx.WXK_LBUTTON : "WXK_LBUTTON",
    wx.WXK_RBUTTON : "WXK_RBUTTON",
    wx.WXK_CANCEL : "WXK_CANCEL",
    wx.WXK_MBUTTON : "WXK_MBUTTON",
    wx.WXK_CLEAR : "WXK_CLEAR",
    wx.WXK_SHIFT : "WXK_SHIFT",
    wx.WXK_ALT : "WXK_ALT",
    wx.WXK_CONTROL : "WXK_CONTROL",
    wx.WXK_MENU : "WXK_MENU",
    wx.WXK_PAUSE : "WXK_PAUSE",
    wx.WXK_CAPITAL : "WXK_CAPITAL",
    wx.WXK_PRIOR : "WXK_PRIOR",
    wx.WXK_NEXT : "WXK_NEXT",
    wx.WXK_END : "WXK_END",
    wx.WXK_HOME : "WXK_HOME",
    wx.WXK_LEFT : "WXK_LEFT",
    wx.WXK_UP : "WXK_UP",
    wx.WXK_RIGHT : "WXK_RIGHT",
    wx.WXK_DOWN : "WXK_DOWN",
    wx.WXK_SELECT : "WXK_SELECT",
    wx.WXK_PRINT : "WXK_PRINT",
    wx.WXK_EXECUTE : "WXK_EXECUTE",
    wx.WXK_SNAPSHOT : "WXK_SNAPSHOT",
    wx.WXK_INSERT : "WXK_INSERT",
    wx.WXK_HELP : "WXK_HELP",
    wx.WXK_NUMPAD0 : "WXK_NUMPAD0",
    wx.WXK_NUMPAD1 : "WXK_NUMPAD1",
    wx.WXK_NUMPAD2 : "WXK_NUMPAD2",
    wx.WXK_NUMPAD3 : "WXK_NUMPAD3",
    wx.WXK_NUMPAD4 : "WXK_NUMPAD4",
    wx.WXK_NUMPAD5 : "WXK_NUMPAD5",
    wx.WXK_NUMPAD6 : "WXK_NUMPAD6",
    wx.WXK_NUMPAD7 : "WXK_NUMPAD7",
    wx.WXK_NUMPAD8 : "WXK_NUMPAD8",
    wx.WXK_NUMPAD9 : "WXK_NUMPAD9",
    wx.WXK_MULTIPLY : "WXK_MULTIPLY",
    wx.WXK_ADD : "WXK_ADD",
    wx.WXK_SEPARATOR : "WXK_SEPARATOR",
    wx.WXK_SUBTRACT : "WXK_SUBTRACT",
    wx.WXK_DECIMAL : "WXK_DECIMAL",
    wx.WXK_DIVIDE : "WXK_DIVIDE",
    wx.WXK_F1 : "WXK_F1",
    wx.WXK_F2 : "WXK_F2",
    wx.WXK_F3 : "WXK_F3",
    wx.WXK_F4 : "WXK_F4",
    wx.WXK_F5 : "WXK_F5",
    wx.WXK_F6 : "WXK_F6",
    wx.WXK_F7 : "WXK_F7",
    wx.WXK_F8 : "WXK_F8",
    wx.WXK_F9 : "WXK_F9",
    wx.WXK_F10 : "WXK_F10",
    wx.WXK_F11 : "WXK_F11",
    wx.WXK_F12 : "WXK_F12",
    wx.WXK_F13 : "WXK_F13",
    wx.WXK_F14 : "WXK_F14",
    wx.WXK_F15 : "WXK_F15",
    wx.WXK_F16 : "WXK_F16",
    wx.WXK_F17 : "WXK_F17",
    wx.WXK_F18 : "WXK_F18",
    wx.WXK_F19 : "WXK_F19",
    wx.WXK_F20 : "WXK_F20",
    wx.WXK_F21 : "WXK_F21",
    wx.WXK_F22 : "WXK_F22",
    wx.WXK_F23 : "WXK_F23",
    wx.WXK_F24 : "WXK_F24",
    wx.WXK_NUMLOCK : "WXK_NUMLOCK",
    wx.WXK_SCROLL : "WXK_SCROLL",
    wx.WXK_PAGEUP : "WXK_PAGEUP",
    wx.WXK_PAGEDOWN : "WXK_PAGEDOWN",
    wx.WXK_NUMPAD_SPACE : "WXK_NUMPAD_SPACE",
    wx.WXK_NUMPAD_TAB : "WXK_NUMPAD_TAB",
    wx.WXK_NUMPAD_ENTER : "WXK_NUMPAD_ENTER",
    wx.WXK_NUMPAD_F1 : "WXK_NUMPAD_F1",
    wx.WXK_NUMPAD_F2 : "WXK_NUMPAD_F2",
    wx.WXK_NUMPAD_F3 : "WXK_NUMPAD_F3",
    wx.WXK_NUMPAD_F4 : "WXK_NUMPAD_F4",
    wx.WXK_NUMPAD_HOME : "WXK_NUMPAD_HOME",
    wx.WXK_NUMPAD_LEFT : "WXK_NUMPAD_LEFT",
    wx.WXK_NUMPAD_UP : "WXK_NUMPAD_UP",
    wx.WXK_NUMPAD_RIGHT : "WXK_NUMPAD_RIGHT",
    wx.WXK_NUMPAD_DOWN : "WXK_NUMPAD_DOWN",
    wx.WXK_NUMPAD_PRIOR : "WXK_NUMPAD_PRIOR",
    wx.WXK_NUMPAD_PAGEUP : "WXK_NUMPAD_PAGEUP",
    wx.WXK_NUMPAD_NEXT : "WXK_NUMPAD_NEXT",
    wx.WXK_NUMPAD_PAGEDOWN : "WXK_NUMPAD_PAGEDOWN",
    wx.WXK_NUMPAD_END : "WXK_NUMPAD_END",
    wx.WXK_NUMPAD_BEGIN : "WXK_NUMPAD_BEGIN",
    wx.WXK_NUMPAD_INSERT : "WXK_NUMPAD_INSERT",
    wx.WXK_NUMPAD_DELETE : "WXK_NUMPAD_DELETE",
    wx.WXK_NUMPAD_EQUAL : "WXK_NUMPAD_EQUAL",
    wx.WXK_NUMPAD_MULTIPLY : "WXK_NUMPAD_MULTIPLY",
    wx.WXK_NUMPAD_ADD : "WXK_NUMPAD_ADD",
    wx.WXK_NUMPAD_SEPARATOR : "WXK_NUMPAD_SEPARATOR",
    wx.WXK_NUMPAD_SUBTRACT : "WXK_NUMPAD_SUBTRACT",
    wx.WXK_NUMPAD_DECIMAL : "WXK_NUMPAD_DECIMAL",
    wx.WXK_NUMPAD_DIVIDE : "WXK_NUMPAD_DIVIDE",
}

#ID's used to identify menu entries
ID_ABOUT=wx.wxNewId()
ID_EXIT=wx.wxNewId()
ID_TEST = wx.wxNewId()
ID_LOGIN = wx.wxNewId()
ID_ALIAS = wx.wxNewId()
ID_TRIGGER = wx.wxNewId()
ID_SAVE = wx.wxNewId()
ID_LOAD = wx.wxNewId()

#widget ID's
ID_TEXT = wx.wxNewId()
ID_TEXT_BUFFER = wx.wxNewId()
ID_ENTRY = wx.wxNewId()

#misc ID's
ID_QUEUE_TIMER = wx.wxNewId()


# this is the default color--it's what we use when the mud hasn't
# specified a color yet.  this might get a little fishy.
# when using DEFAULT make sure you clone it first.

# The elements of the default color list are as follows...
# [bold, underline, blink, reverse, foreground, background]
DEFAULT_COLOR = list(ansi.DEFAULT_COLOR)

#this sets the fg color to 37, which from ansi.py stylemap is white
#also sets bg color to black
DEFAULT_COLOR[ansi.PLACE_FG] = 37
DEFAULT_COLOR[ansi.PLACE_BG] = 40

myui = None

def get_ui_instance():
    global myui
    if myui == None:
        myui = wxui()
    return myui
  
class _Event:
    def __init__(self):
        pass

    def execute(self, wxui):
        pass

class _OutputEvent(_Event):
    def __init__(self, text):
        self._text = text

    def execute(self, wxui):
        wxui.write_internal(self._text)

class _ColorCheckEvent(_Event):
    def execute(self, wxui):
      wxui.colorCheck() 

class _TitleEvent(_Event):
    def __init__(self, wxFrame, title):
        self._wxFrame = wxFrame
        self._title = title

    def execute(self, wxui):
        wxui._wxFrame.SetTitle(self._title)

class _WriteWindowEvent(_Event):
    def __init__(self, windowname, message):
        self._windowname = windowname
        self._message = message

    def execute(self, wxui):
        wxui.writeWindow_internal(self._windowname, self._message)
    
    
class MudFrame(wx.wxFrame):
    def __init__(self,parent,id,title, pos, size):
        global myui
        wx.wxFrame.__init__(self,parent,-4, title, pos,size,
                            style=wx.wxDEFAULT_FRAME_STYLE|wx.wxNO_FULL_REPAINT_ON_RESIZE)
                            
#        self.Parent = parent
        self.savefile = ''

        #attr to hold a reference to our command_editor once
        #it is created.  Also used so we dont create it more
        #times than is necessary
        self.command_editor = None
        
        # A Statusbar in the bottom of the window
        self.CreateStatusBar()
        
        # Setting up the File menu.
        filemenu= wx.wxMenu()
        filemenu.Append(ID_LOAD, "&Restaurer configuration", "Restaurer votre configuration depuis le fichier %s" % USER_CONFIG)
        filemenu.Append(ID_SAVE, "&Sauvegarder configuration", "Sauvegarder votre configuration dans le fichier %s" % USER_CONFIG)
        filemenu.AppendSeparator()
        filemenu.Append(ID_EXIT,"&Quitter"," Quitter le programme")

        # Setting up the Tools Menu
        toolmenu = wx.wxMenu()
        toolmenu.Append(ID_ALIAS, "Editeur d'&Alias", "")
        toolmenu.Append(ID_TRIGGER, 'Editeur de T&riggers', '')

        # Setting up test menu
        testmenu = wx.wxMenu()
        testmenu.Append(ID_LOGIN, "&MultiMUD","Se reconnecter à MultiMUD")

        helpmenu = wx.wxMenu()
        helpmenu.Append(ID_ABOUT, "&A propos de..."," Information about this program")
        
        # Creating the menubar.
        menuBar = wx.wxMenuBar()
        menuBar.Append(filemenu, "&Fichier")
        menuBar.Append(toolmenu, "&Outils")
        menuBar.Append(testmenu, "&Connexion")
        menuBar.Append(helpmenu, "&Aide")
        self.SetMenuBar(menuBar)  

        #event table
        wx.EVT_MENU(self, ID_ABOUT, self.OnAbout)                                                   
        wx.EVT_MENU(self, ID_EXIT, self.OnExit)
        wx.EVT_MENU(self, ID_LOGIN, self.testLogin)
        wx.EVT_MENU(self, ID_ALIAS, self.onCommand)
        wx.EVT_MENU(self, ID_TRIGGER, self.onCommand)
        wx.EVT_MENU(self, ID_SAVE, self.onSave)
        wx.EVT_MENU(self, ID_LOAD, self.onLoad)
        wx.EVT_WINDOW_DESTROY(self, self.OnExit)

        #create main container        
        self.panel = wx.wxPanel(self, -1)
        #create widgets
        self._text = wx.wxTextCtrl( self.panel,
                                    ID_TEXT,
                                    "",
                                    wx.wxDefaultPosition,
                                    wx.wxSize(80,40),
                                    style=wx.wxTE_MULTILINE )
        wx.EVT_CHAR(self._text, self._ignoreThis)
        
        self._txtbuffer = wx.wxTextCtrl( self.panel,
                                         ID_TEXT_BUFFER,
                                         "",
                                         wx.wxDefaultPosition,
                                         wx.wxSize(80,40),
                                         style=wx.wxTE_MULTILINE )
        wx.EVT_CHAR(self._txtbuffer, self._ignoreThis)

        self._txtbuffer.Show(0)

        self._entry = CommandEntry(self.panel, ID_ENTRY, '', myui)

        #create vertical sizer to hold the widgets
        self.vsizer=wx.wxBoxSizer(wx.wxVERTICAL)
        self.vsizer.Add(self._text, 1, wx.wxGROW|wx.wxALIGN_CENTER_VERTICAL|wx.wxALL, 5)
        self.vsizer.Add(self._entry,  0, wx.wxGROW|wx.wxALIGN_CENTER_VERTICAL|wx.wxALL, 5)

        #attach sizer to panel
        self.panel.SetSizer(self.vsizer)
        self.panel.SetAutoLayout(1)
        self.vsizer.Fit(self.panel)
        self.Show(1)

    def _ignoreThis(self, event):
        #following line is useful for debugging keycodes
        #print event.GetKeyCode()
        
        if event.GetKeyCode() == 3:
            event.Skip()
        else:
            widget = event.GetEventObject()
            widget.SetValue(widget.GetValue()[:-1])

            self._entry.SetFocus()
            self._entry.SetValue(self._entry.GetValue() + chr(event.GetKeyCode()))
            self._entry.SetInsertionPoint(self._entry.GetInsertionPoint() + 1)

    def testLogin(self, event):
        exported.lyntin_command('#session multimud multimud.homeip.net 6022')
        
    def OnAbout(self,e):
        d= wx.wxMessageDialog( self, " A Lyntin ui (accessible edition) \n"
                            " in wxPython","About wxPython ui", wx.wxOK)
        d.ShowModal() 
        d.Destroy() 
        
    def OnExit(self,e):
        #when we exit, there are two parts that need cleaned up..
        #first close the gui
        self.Close()
        #then we tell lyntin it can shutdown
        exported.lyntin_command('#end')

    def onCommand(self,event):
        id = event.GetId()
        #print 'id_alias:',ID_ALIAS
        #print 'id_trigger:',ID_TRIGGER
        #print 'event.GetId:', event.GetId()
        
        if id == ID_ALIAS:
            mode = ALIAS
            title = 'Alias Editor'
        elif id == ID_TRIGGER:
            mode = ACTION
            title = 'Trigger Editor'

        #print mode
        if not self.command_editor:
            self.command_editor = CommandEditor(self, -1, title, mode = mode)
        else:
            self.command_editor.mode = mode

        self.command_editor.resetWidgetsForMode(mode)
        self.command_editor.CentreOnParent()
        self.command_editor.Show(1)
        
    def onSave(self, event = None):
        self.savefile = USER_CONFIG
        if self.savefile:
            msg = '#write %s' % self.savefile
            exported.lyntin_command(msg)
        else:
            self.onSaveAs()
            
    def onSaveAs(self, event = None):
        """ Save as """
        dlg = wx.wxFileDialog(self, "Choose a file", '.',self.savefile,"*.*", wx.wxSAVE)
        if dlg.ShowModal() == wx.wxID_OK:
            self.savefile = os.path.join(dlg.GetDirectory(), dlg.GetFilename())
            self.onSave()
        dlg.Destroy()
        
    def onLoad(self, event):
        file = USER_CONFIG
##        dlg = wx.wxFileDialog(self, "Choose a file", '.', "", "*.*", wx.wxOPEN)
##        if dlg.ShowModal() == wx.wxID_OK:
##            filename=dlg.GetFilename()
##            dirname=dlg.GetDirectory()
##
##        old_dir = os.getcwd()
##        os.chdir(dirname)
##        file = os.path.join(dirname, filename)
        cmnd = '#read %s' % file
        exported.lyntin_command(cmnd)
    
class MudApp(wx.wxApp):
        
    def OnInit(self):
        self._topFrame = MudFrame(wx.NULL,
                                  -1,
                                  'Lyntin',
                                  wx.wxDefaultPosition,
                                  wx.wxSize(800, 600))
        #not sure why we have to set this in the wxApp instance.  I assumed that it
        #would be set in the wxFRame instance, but when I do that, it is
        # *convientently* ignored
        self._topFrame._text.SetBackgroundColour("BLACK")
        self._topFrame._text.SetForegroundColour("WHITE")
        self._topFrame.Show(1)

        self.SetTopWindow(self._topFrame)
        return 1

class wxui(base.BaseUI):
    """
    This is a ui class which handles the wxPython user interface
    """
    def __init__(self):
        base.BaseUI.__init__(self)

        #internal ui queue
        self._event_queue = Queue.Queue() # map of session -> (bold, foreground, background)

        # map of session -> (bold, foreground, background)
        self._currcolors = {}

        # ses -> string
        self._unfinishedcolor = {}

        self._viewhistory = 0
        self._do_i_echo = 0 # JLP
        
        # holds a map of window names -> window references
        self._windows = {}


        self._wx = MudApp(0)

        self._wx._topFrame._entry.SetFocus()
        
        #since the entry control is created before the wxui is finished being created,
        #we set it afterward.  A bit of an ugly hack, but not sure how to get around it.
        self._wx._topFrame._entry._wxui = self
        
        self.queue_timer = wx.wxTimer(self._wx, ID_QUEUE_TIMER)
        wx.EVT_TIMER(self._wx, ID_QUEUE_TIMER, self.dequeue)
        self.dequeue()

        exported.hook_register("mudecho_hook", self.echo)
        exported.hook_register("to_user_hook", self.write)
  
    def runui(self):
        global HELP_TEXT
        exported.add_help("wxui", HELP_TEXT)
        exported.write_message("For wx help type \"#help wxui\".")
        exported.add_command("colorcheck", colorcheck_cmd)


        #start the wxPython mainloop here
        self._wx.MainLoop()

    def wantMainThread(self):
        # wxPython needs the main thread of execution so we return
        # a 1 here.
        return 1


    def dequeue(self, event = None):
        qsize = self._event_queue.qsize()
        if qsize > 10:
            qsize = 10

        for i in range(qsize):
            ev = self._event_queue.get_nowait()
            ev.execute(self)
        self.queue_timer.Start(25, 1)

        
    def settitle(self, title=""):
        """
        Sets the title bar to the Lyntin title plus the given string.

        @param title: the title to set
        @type  title: string
        """
        if title:
            title = constants.LYNTINTITLE + title
        else:
            title = constants.LYNTINTITLE
        self._event_queue.put(_TitleEvent(self._wx, title))
        
    def removeWindow(self, windowname):
        """
        This removes a NamedWindow from our list of NamedWindows.

        @param windowname: the name of the window to write to
        @type  windowname: string
        """
        if self._windows.has_key(windowname):
            del self._windows[windowname]
    
    def writeWindow_internal(self, windowname, message):
        if not self._windows.has_key(windowname):
            self._windows[windowname] = NamedWindow(windowname, self, self._wx)
        self._windows[windowname].write(message)
        
        
    def writeWindow(self, windowname, message):
        """
        This writes to the window named "windowname".  If the window
        does not exist, we spin one off.  It handles ansi text and
        messages just like writing to the main window.
    
        @param windowname: the name of the window to write to
        @type  windowname: string
    
        @param message: the message to write to the window
        @type  message: string or Message instance
        """
        self._event_queue.put(_WriteWindowEvent(windowname, message))
        
    def pageUp(self, event):
        self._page(event, -1)

    def pageDown(self, event):
        self._page(event, 1)

    def _page(self, event, inc):
        tf = self._wx._topFrame
        e = tf._entry
        t = tf._text
        if inc == 1:
            start = 0
            end = t.GetNumberOfLines() - 1
        else:
            start = t.GetNumberOfLines() - 1
            end = 0
        if self._viewhistory == 0:
            self._history_line = start - inc
            self._viewhistory = 1
            e._edit_mode = True
        if event.ControlDown():
            nb = 22
        else:
            nb = 1
        for i in xrange(nb):
            if self._history_line == end:
                break
            self._history_line += inc
            while not t.GetLineText(self._history_line) or \
                  t.GetLineText(self._history_line).strip() == ">":
                if self._history_line == end:
                    break
                self._history_line += inc
        e.SetValue(t.GetLineText(self._history_line))
        e.SetSelection(-1, -1)
##        return
##        """ Handles prior (Page-Up) events."""
##        if self._viewhistory == 0:
##            self._wx._topFrame.vsizer.Insert(0,
##                                             self._wx._topFrame._txtbuffer,
##                                             1,
##                                             wx.wxGROW|wx.wxALIGN_CENTER_VERTICAL|wx.wxALL, 5)
##            self._wx._topFrame._txtbuffer.Show(1)
##            #tell the vertical sizer to recalc its layout so that the
##            #txtbuffer gets resized.
##            self._wx._topFrame.vsizer.Layout()
##            self._viewhistory = 1
##            self._wx._topFrame._txtbuffer.Clear()
##            lotofstuff = self._wx._topFrame._text.GetValue()
##            self._wx._topFrame._txtbuffer.AppendText(lotofstuff)
            
##    def pageDown(self):
##        tf = self._wx._topFrame
##        e = tf._entry
##        t = tf._text
##        if self._viewhistory == 1:
##            self._history_line += 1
##            if self._history_line > t.GetNumberOfLines() - 1:
##                self._history_line = t.GetNumberOfLines() - 1
##        e.SetValue(t.GetLineText(self._history_line))
####        return
####        """ Handles next (Page-Down) events."""
####        if self._viewhistory == 1:
####            # yscroll down stuff
####            self._wx.topFrame._txtbuffer.ScrollToLine(self._wx._txtbuffer.GetCurrentLine())
    
    def escape(self, event):
        tf = self._wx._topFrame
        e = tf._entry
        t = tf._text
        if self._viewhistory == 1:
            self._viewhistory = 0
            if e._content:
                e.SetValue(e._content)
        else:
            e.Clear()
##        return
##        """ Handles escape (Escape) events."""
##        if self._viewhistory == 1:
##            self._wx._topFrame.vsizer.Remove(self._wx._topFrame._txtbuffer)
##            self._wx._topFrame._txtbuffer.Show(0)
##            self._wx._topFrame.vsizer.Layout()
##            self._viewhistory = 0
##        else:
##            self._wx._topFrame._entry.Clear()
            
    def echo(self, args):
        """ This turns echo on and off on the CommandEntry widget."""
        yesno = args["yesno"]
        if yesno==1:
            # echo on
            self._do_i_echo = 1
        else:
            # echo off
            self._do_i_echo = 0
            
    def write(self, args):
        """
        This writes text to the text buffer for viewing by the user.
        This is overridden from the 'base.BaseUI'.
        """
        self._event_queue.put(_OutputEvent(args))


    def write_internal(self, args):
        mess = args["message"]
        if type(mess) == types.StringType:
            mess = message.Message(mess, message.LTDATA)

        line = mess.data
        ses = mess.session

        if line == '' or self.showTextForSession(ses) == 0:
            return

     
        color, leftover = buffer_write(mess, self._wx._topFrame._text, self._currcolors, 
                                   self._unfinishedcolor)

        if mess.type == message.MUDDATA:
            self._unfinishedcolor[ses] = leftover
            self._currcolors[ses] = color
            
    def colorCheck(self):
        """
        Goes through and displays all the combinations of fg and bg
        with the text string involved.  Purely for debugging
        purposes.
        """
        fgkeys = ['30','31','32','33','34','35','36','37']
        bgkeys = ['40','41','42','43','44','45','46','47']

        #used for convienence, as I was being lazy and didnt wanna type it
        #out all the time
        txt_widget = self._wx._topFrame._text

        txt_widget.AppendText('color check:\n')
        for bg in bgkeys:
            for fg in fgkeys:
              txt_widget.GetDefaultStyle().SetTextColour(fg_color_codes[fg]) 
              txt_widget.GetDefaultStyle().SetBackgroundColour(bg_color_codes[bg])
              txt_widget.AppendText(fg)
              txt_widget.GetDefaultStyle().SetTextColour(fg_color_codes["b" +fg])
              txt_widget.AppendText("b" + fg)
            txt_widget.AppendText('\n')
            for fg in fgkeys:
              txt_widget.GetDefaultStyle().SetTextColour(fg_color_codes[fg]) 
              txt_widget.GetDefaultStyle().SetBackgroundColour(bg_color_codes["b" + bg])
              txt_widget.AppendText(fg)
              txt_widget.GetDefaultStyle().SetTextColour(fg_color_codes["b" +fg])
              txt_widget.GetDefaultStyle().SetBackgroundColour(bg_color_codes["b" + bg])
              txt_widget.AppendText("b" + fg)
            txt_widget.AppendText('\n')
        txt_widget.AppendText('\n')
        txt_widget.AppendText('\n')

class CommandEntry(wx.wxTextCtrl):
    """ This class handles the user input area."""

    def __init__(self, master, id, text, wxui):
        """ Initializes and sets the key-bindings."""
        self._wxui = wxui
        self._inputstack = []
        self._autotyper = None
        self._autotyper_ses = None

        wx.wxTextCtrl.__init__(self,master, id, text, style = wx.wxTE_PROCESS_ENTER) #|wx.wxTE_PASSWORD)
        
        #since wxPython doesnt bind events the same way as TKinter,
        #this is used as a map between the keycode, and the func to call
        self._key_func_map ={
                   wx.WXK_RETURN: self.createInputEvent,
                   wx.WXK_TAB: self.insertTab,
                   wx.WXK_PRIOR: self.callPrior,
                   wx.WXK_UP: self.insertPrevCommand,
                   wx.WXK_DOWN: self.insertNextCommand,
                   wx.WXK_NEXT: self.callNext,
                   'Ctrl-T':self.startAutotyper,
                   'Ctrl-U':self.callKillLine,
                   'Ctrl-Up': self.callPushInputStack,
                   'Ctrl-Down':self.callPopInputStack,
                   'Ctrl-M': self.createInputEvent,
                   wx.WXK_ESCAPE: self.callEsc,
                   wx.WXK_F1: self.callBinding,
                   wx.WXK_F2: self.callBinding,
                   wx.WXK_F3: self.callBinding,
                   wx.WXK_F4: self.callBinding,
                   wx.WXK_F5: self.callBinding,
                   wx.WXK_F6: self.callBinding,
                   wx.WXK_F7: self.callBinding,
                   wx.WXK_F8: self.callBinding,
                   wx.WXK_F9: self.callBinding,
                   wx.WXK_F10: self.callBinding,
                   wx.WXK_F11: self.callBinding,
                   wx.WXK_F12: self.editMode,
                   wx.WXK_NUMPAD_UP: self.callKP8,
                   wx.WXK_NUMPAD_RIGHT: self.callKP6,
                   wx.WXK_NUMPAD_LEFT: self.callKP4,
                   wx.WXK_NUMPAD_DOWN: self.callKP2,
                   wx.WXK_NUMPAD_PRIOR: self.callKP9,
                   wx.WXK_NUMPAD_HOME: self.callKP7,
                   wx.WXK_NUMPAD_BEGIN: self.callKP5,
                   wx.WXK_NUMPAD_NEXT: self.callKP3,
                   wx.WXK_NUMPAD_END: self.callKP1}

        wx.EVT_CHAR(self, self.onChar)
        
        self.hist_index = -1
        self._wxui = wxui
        self.saveinputhighlight = 0
        self._edit_mode = False
        self._content = ""

    def editMode(self, event=None):
        self._edit_mode = not self._edit_mode
        if self._edit_mode:
            self.SetValue(self._content)
            self.SetInsertionPointEnd()
        else:
            self._content = self.GetValue()
            self.SetValue("")

    def editModeOn(self):
        if not self._edit_mode:
            self.editMode()

    def onChar(self, event):
        keycode = event.GetKeyCode()
        keyname = keyMap.get(keycode, None)
        if keycode == 0:
            keyname = None
        elif keycode < 27:
            keyname = "Ctrl-%s" % chr(ord('A') + keycode-1)

        if keycode in [wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_BACK]:
            self.editModeOn()

        #check out key-func mapping and see if the keyname is there
        if self._key_func_map.has_key(keyname):
            self._key_func_map[keyname](event)
        #if the name wasnt there.. check for the keycode
        elif self._key_func_map.has_key(keycode):
            self._key_func_map[keycode](event)
        #if we aint found a thing.. skip the event
        else:
            if self._edit_mode:
                event.Skip()
            else:
##                if keycode == wx.WXK_BACK:
##                    self._content = self._content[:-1]
##                else:
                    if event.MetaDown() or event.AltDown() or event.CmdDown() or event.ControlDown():
                        event.Skip()
                    else:
                        self.SetValue(codecs.latin_1_decode(chr(keycode))[0])
                        self.SetInsertionPointEnd()
                        self._content += codecs.latin_1_decode(chr(keycode))[0]
    
    def createInputEvent(self, event):
        """ Handles the <KeyPress-Return> event."""
        if self._edit_mode:
            val = fix_unicode(self.GetValue())
            self._edit_mode = False
            self._content = ""
        else:
            val = fix_unicode(self._content)
            self._content = ""
        self._wxui.handleinput(val)

        if self.saveinputhighlight == 1:
            self.SetSelection(-1, -1)
        else:
            self.Clear()
        self.hist_index = -1
        self._wxui._viewhistory = 0

    def _executeBinding(self, binding):
        """ Returns the alias for this keybinding."""
        ses = exported.get_current_session()
        action = exported.get_manager("alias").getAlias(ses, binding)
        if action:
            self._wxui.handleinput(action)
            return 1
        else:
            exported.write_error("%s is currently not bound to anything." % binding)
            return 0

    def callBinding(self, event):
        """ Handles arbitrary bindings of function call keypresses."""

        # handle all the function keys except F1
        if event.GetKeyCode() == wx.WXK_F1:
            self._wxui.handleinput(exported.get_config("commandchar") + "help")
            return "break"
      
        if self._executeBinding(keyMap[event.GetKeyCode()]) == 1:
            return "break"

        # these two lines help in debugging stuff we bound
        # print repr(event)
        # print repr(event.__dict__)

    def callKP9(self, event):
        if self._executeBinding("WXK_NUMPAD9") == 1:
            return "break"

    def callKP8(self, event):
        if self._executeBinding("WXK_NUMPAD8") == 1:
            return "break"

    def callKP7(self, event):
        if self._executeBinding("WXK_NUMPAD7") == 1:
            return "break"

    def callKP6(self, event):
        if self._executeBinding("WXK_NUMPAD6") == 1:
            return "break"

    def callKP5(self, event):
        if self._executeBinding("WXK_NUMPAD5") == 1:
            return "break"

    def callKP4(self, event):
        if self._executeBinding("WXK_NUMPAD4") == 1:
            return "break"

    def callKP3(self, event):
        if self._executeBinding("WXK_NUMPAD3") == 1:
            return "break"

    def callKP2(self, event):
        if self._executeBinding("WXK_NUMPAD2") == 1:
            return "break"

    def callKP1(self, event):
        if self._executeBinding("WXK_NUMPAD1") == 1:
            return "break"

    def startAutotyper(self, event):
        """
       This will start the autotyper. It will be called if you type <Ctrl>+<t>.
       There can be only one autotyper at a time. The autotyper cannot be started
       for the common session.
       """
        if self._autotyper != None:
            self._autotyper.Show(1)
            #exported.write_error("cannot start autotyper: already started.")
            return
    
        session = exported.get_current_session()
    
        if session.getName() == "common":
            exported.write_error("autotyper cannot be applied to common session.")
            return
    
        self._autotyper = Autotyper(self._wxui._wx._topFrame, self.autotyperDone)
        self._autotyper_ses = session
    
        exported.write_message("autotyper: started.")

    def autotyperDone(self, data):
        """
       This is a callback for the autotyper. It will be called when the autotyper
       is finished.
      
        @param data: the autotyper data--None if the user clicked on "Cancel"
            or closed the autotyper window
        @type  data: string or None  
        """
        if data != None:
            self._autotyper_ses.writeSocket(data)
            
        exported.write_message("autotyper: done.")

    def clearInput(self):
        """ Clears the text widget."""
        self.Clear()
        
    def insertTab(self, event):
        """ Handles the <KeyPress-Tab> event."""
        pass
        
    def callPrior(self, event):
        """ Handles the <KeyPress-Prior> event."""
        self._wxui.pageUp(event)
        
    def callNext(self, event):
        """ Handles the <KeyPress-Next> event."""
        self._wxui.pageDown(event)
        
    def callEsc(self, event):
        """ Handles the <KeyPress-Escape> event."""
        self._wxui.escape(event)
    
    def callKillLine(self, event): 
        """ Handles the <Control-KeyPress-u> event."""
        self.Clear()

    def callPushInputStack(self, event):
        """ Handles the <Control-KeyPress-Up> event."""
        self._inputstack.append((self.index('insert'),self.GetValue()))
        self.Clear()

    def callPopInputStack(self,event):
        """ Handles the <Control-KeyPress-Down> event."""
        if len(self._inputstack) < 1:
            return
        poppage = self._inputstack.pop()
        self.Clear()
        self.SetValue(poppage[1])
        
    def insertPrevCommand(self, event):
        self._edit_mode = True
        """ Handles the <KeyPress-Up> event."""
        hist = exported.get_history()
        if self.hist_index == -1:
            self.current_input = self.GetValue()
        if self.hist_index < len(hist) - 1:
            self.hist_index = self.hist_index + 1
            self.Clear()
            self.SetValue(hist[self.hist_index])
        self.SetInsertionPointEnd()

    def insertNextCommand(self, event):
        self._edit_mode = True
        """ Handles the <KeyPress-Down> event."""
        hist = exported.get_history()
        if self.hist_index == -1:
            return
        self.hist_index = self.hist_index - 1
        if self.hist_index == -1:
            self.Clear()
            self.SetValue(self.current_input)
            
        else:
            self.Clear()
            self.SetValue(hist[self.hist_index])        
        self.SetInsertionPointEnd()


class NamedWindow:
    """
    This creates a window for the wxpythonui which you can then write to 
    programmatically.  This allows modules to spin off new named windows
    and write to them.
    """
    def __init__(self, windowname, master, wxui):
      """
      Initializes the window

      @param windowname: the name of the new window
      @type  windowname: string

      @param master: the main wxpythonui window
      @type  master: wxFrame
      """
      self._parent = master
      self._frame = wx.wxFrame(master, -1, 'Lyntin -- ' + windowname)
      self._windowname = windowname
    
      # map of session -> (bold, foreground, background)
      self._currcolors = {}

      # ses -> string
      self._unfinishedcolor = {}

      self._do_i_echo = 1

      self._txt = wx.wxTextCtrl( self._frame, -1, "",
                                 wx.wxDefaultPosition,
                                 wx.wxSize(80,40), wx.wxTE_MULTILINE )
       
    def close(self):
      """
      Closes and destroys references to this window.
      """
      self._parent.removeWindow(self._windowname)
      self._frame.Close()

    def write(self, msg):
      """
      This writes text to the text buffer for viewing by the user.
  
      This is overridden from the 'base.BaseUI'.
      """
      if type(msg) == types.TupleType:
        msg = msg[0]

      if type(msg) == types.StringType:
          msg = message.Message(message, message.LTDATA)

      line = msg.data
      ses = msg.session

      if line == '':
          return

      color, leftover = buffer_write(msg, self._txt, self._currcolors, 
                                   self._unfinishedcolor)

      if msg.type == message.MUDDATA:
          self._unfinishedcolor[ses] = leftover
          self._currcolors[ses] = color

class Autotyper(wx.wxFrame):
    """
    Autotyper class, it generates the autotyper window, waits for entering text
    and then calls a function to work with the text.
    """
    def __init__(self, master, sendfunc):
        """
        Initializes the autotyper.

        @param master: the parent window
        @type  master: wxWindow

        @param sendfunc: the callback function
        @type  sendfunc: function
        """
        self._sendfunc = sendfunc

        send_btn = wx.wxNewId()
        cancel_btn = wx.wxNewId()

        wx.wxFrame.__init__(self, master, -1, "Lyntin -- Autotyper")
        self._panel = wx.wxPanel(self, -1)
        self._vsizer = wx.wxBoxSizer(wx.wxVERTICAL)
        self._txt = wx.wxTextCtrl( self._panel, -1, '',wx.wxDefaultPosition,
                                   wx.wxSize(80,40), wx.wxTE_MULTILINE )
        self._vsizer.Add(self._txt, 1,
                         wx.wxGROW|wx.wxALIGN_CENTER_VERTICAL|wx.wxALL, 5)

        self._hsizer = wx.wxBoxSizer(wx.wxHORIZONTAL)
        self._sendbtn = wx.wxButton( self._panel, send_btn, "Send",
                                     wx.wxDefaultPosition, wx.wxDefaultSize, 0 )
        self._hsizer.AddWindow( self._sendbtn, 0, wx.wxALIGN_CENTRE|wx.wxALL, 5 )

        self.cancel_btn = wx.wxButton( self._panel, cancel_btn, "Cancel",
                                       wx.wxDefaultPosition, wx.wxDefaultSize, 0 )
        self._hsizer.AddWindow( self.cancel_btn, 0, wx.wxALIGN_CENTRE|wx.wxALL, 5 )

        self._vsizer.AddSizer( self._hsizer, 0,
                               wx.wxALIGN_RIGHT|wx.wxALIGN_CENTER_VERTICAL|wx.wxALL, 5 )
        wx.EVT_BUTTON(self, send_btn, self.send)
        wx.EVT_BUTTON(self, cancel_btn, self.cancel)
        self._panel.SetSizer(self._vsizer)
        self._panel.SetAutoLayout(1)
        self._vsizer.Fit(self._panel)

        self.CentreOnParent()
        self.Show(1)
        self._txt.SetFocus()
        self._txt.SetInsertionPoint(0)

    def send(self, event):
        """
        Will be called when the user clicks on the 'Send' button.
        """
        text = fix_unicode(self._txt.GetValue())
        self._sendfunc(text)
        self._txt.Clear()
        self.Show(0)

    def cancel(self, event):
        """
        Will be called when the user clicks on the 'Cancel' button.
        """
        self._sendfunc(None)
        self.Show(0)

class CommandEditor(wx.wxFrame):
    ID_COMMAND_LOAD = wx.wxNewId()

    def __init__(self, parent, id, text, mode = 0, savefile = ''):
        wx.wxFrame.__init__(self,parent, id, text)
        self.parent = parent
        self.mode = mode
        self.mainpanel = CommandPanel(self, -1)
        self.mainpanel.Fit()
        self.mainpanel.command_list.InsertColumn(0, 'alias')
        self.mainpanel.command_list.InsertColumn(1, "replacement")
        self.mainpanel.txt_command_name.SetFocus()
        self.alias_dict = {}
        self.action_dict = {}
        self.savefile = savefile
        
        filemenu = wx.wxMenu()
        filemenu.Append(self.ID_COMMAND_LOAD, "&Load","Load from a file...")
        
        # Creating the menubar.
        menuBar = wx.wxMenuBar()
        menuBar.Append(filemenu,"&File")
        self.SetMenuBar(menuBar)  

        wx.EVT_MENU(self,self.ID_COMMAND_LOAD, self.onLoadCommand)  
        wx.EVT_BUTTON(self,self.mainpanel.btn_close.GetId(),self.OnExit)
        wx.EVT_BUTTON(self,self.mainpanel.btn_add.GetId(),self.addCommand)
        wx.EVT_BUTTON(self,self.mainpanel.btn_delete.GetId(),self.removeCommand)
        wx.EVT_WINDOW_DESTROY(self, self.OnExit)
        wx.EVT_LIST_ITEM_SELECTED(self, self.mainpanel.command_list.GetId(), self.onCommandSelected)
        self.getCommandsFromMud(self.mode)

        if self.mode == ALIAS:
            if self.alias_dict:
                self.fillCommandWidget(self.alias_dict)
        elif self.mode == ACTION:
            if self.action_dict:
                self.fillCommandWidget(self.trigger_dict)
            

        #self.mainpanel.btn_save.Enable(0)
        
    def getColumnText(self, index, col):
        item = self.mainpanel.command_list.GetItem(index, col)
        return item.GetText()

    def resetWidgetsForMode(self, mode):
        self.getCommandsFromMud(mode)
        if mode == ALIAS:
            title = ['alias', 'replacement']
            dict = self.alias_dict
        elif mode == ACTION:
            title = ['trigger', 'command']
            dict = self.action_dict

        self.mainpanel.command_list.DeleteColumn(0)
        self.mainpanel.command_list.InsertColumn(0, title[0])
        self.SetTitle(title[0].capitalize() + ' Editor')
        self.mainpanel.label_command_name.SetLabel(title[0])
        self.mainpanel.label_replacement.SetLabel(title[1])
        self.fillCommandWidget(dict)
    
    def _getSelectedIndices( self):
        state =  wx.wxLIST_STATE_SELECTED
        indices = []
        found = 1
        lastFound = -1
        while found:
                index = self.mainpanel.command_list.GetNextItem(
                        lastFound,
                        wx.wxLIST_NEXT_ALL,
                        state,
                )
                if index == -1:
                        break
                else:
                        lastFound = index
                        indices.append( index )
        return indices



    def onCommandSelected(self, event):
        currentItem = event.m_itemIndex
        self.mainpanel.txt_command_name.SetValue(self.mainpanel.command_list.GetItemText(currentItem))
        self.mainpanel.txt_command_replacement.SetValue( self.getColumnText(currentItem, 1))


    def onLoadCommand(self, event):
        dlg = wx.wxFileDialog(self, "Choose a file", '.', "", "*.*", wx.wxOPEN)
        if dlg.ShowModal() == wx.wxID_OK:
            filename=dlg.GetFilename()
            dirname=dlg.GetDirectory()

        old_dir = os.getcwd()
        os.chdir(dirname)
        file = os.path.join(dirname, filename)
        cmnd = '#read %s' % file
        exported.lyntin_command(cmnd)
        self.getCommandsFromMud(mode = self.mode)
        if self.mode == ALIAS:
            if self.alias_dict:
                self.fillCommandWidget(self.alias_dict)
        elif self.mode == ACTION:
            if self.trigger_dict:
                self.fillCommandWidget(self.trigger_dict)
            
        dlg.Destroy()
        os.chdir(old_dir)
                        
    def getCommandsFromMud(self, mode):
        ses = exported.get_current_session()
        if mode == ALIAS:
            am = exported.get_manager("alias")
        elif mode == ACTION:
            am = exported.get_manager("action")
            
        cm = exported.get_manager("command")
        defined_commands = am.getInfo(ses)

        for mem in defined_commands:
            command, args = mem.split(" ", 1)

            argumentparser = cm.getArgParser(command)
            if argparser == None:
                args = args.split(" ")

            else:
                fixedmem = mem
                if len(fixedmem) > 0 and fixedmem.startswith("^"):
                    fixedmem = fixedmem[1:]

                try:
                    args = argumentparser.parse(args)
                    args["command"] = command
                except ValueError, e:
                    print "ack--valueerror!"

                except argparser.ParserException, e:
                    print "ack--parserexception"
            
            if mode == ALIAS:
                self.alias_dict[args['alias']] = args['expansion']
            elif mode == ACTION:
                #print args
                #print self.action_dict
                self.action_dict[args['trigger']] = args['action']

    def addToCommandWidget(self, name, expansion):
        row_ndx = self.mainpanel.command_list.GetItemCount()
        self.mainpanel.command_list.InsertStringItem(row_ndx,name)
        self.mainpanel.command_list.SetStringItem(row_ndx,1,expansion)
        self.mainpanel.txt_command_name.Clear()
        self.mainpanel.txt_command_replacement.Clear()
        self.mainpanel.txt_command_name.SetFocus()
        self.mainpanel.command_list.SetColumnWidth(0, wx.wxLIST_AUTOSIZE)
        self.mainpanel.command_list.SetColumnWidth(1, wx.wxLIST_AUTOSIZE)
        
    def updateCommandWidget(self, name, expansion, mode):
        if mode == ALIAS:
            command_list = self.alias_dict.keys()
        elif mode == ACTION:
            command_list = self.trigger_dict.keys()
            
        command_list.sort()
        row_ndx = command_list.index(name)
        self.mainpanel.command_list.SetStringItem(row_ndx,1,expansion)
        self.mainpanel.command_list.SetColumnWidth(0, wx.wxLIST_AUTOSIZE)
        self.mainpanel.command_list.SetColumnWidth(1, wx.wxLIST_AUTOSIZE)
        
    def fillCommandWidget(self, dict):
        self.mainpanel.command_list.DeleteAllItems()
        dict_list = dict.keys()
        dict_list.sort()
        for entry in dict_list:
            self.addToCommandWidget(entry, dict[entry])

    def addCommand(self, event):
        name = self.mainpanel.txt_command_name.GetValue()
        expansion = self.mainpanel.txt_command_replacement.GetValue()
        #print self.mode
        found = None
        if self.mode == ALIAS:
            msg = '#alias {%s} {%s}' % (name, expansion)
            found = self.alias_dict.has_key(name)
        elif self.mode == ACTION:
            msg = '#action {%s} {%s}' % (name, expansion)
            found = self.action_dict.has_key(name)
            
        exported.lyntin_command(msg)
            
        if found:
            self.updateCommandWidget(name, expansion)
        else:
            self.addToCommandWidget(name, expansion)

    def removeCommand(self, event):
        ndx = self._getSelectedIndices()
        item = self.mainpanel.alias_list.GetItem(ndx[0], 0)
        name = item.GetText()
        if self.mode == ALIAS:
            msg = '#unalias %s' % name
        elif self.mode == ACTION:
            msg = '#unaction %s' % name
            
        exported.lyntin_command(msg)
        self.mainpanel.command_list.DeleteItem(ndx[0])
        
    def OnExit(self,e):
        self.Show(0)



        
def buffer_write(msg, txtbuffer, currentcolor, unfinishedcolor):
    """
    Handles writing messages to a text widget taking into accound
    ANSI colors, message types, session scoping, and a variety of
    other things.

    @param message: the Message to write to the buffer
    @type  message: Message

    @param txtbuffer: the text buffer to write to
    @type  txtbuffer: Text

    @param currentcolor: the current color that we should start with
    @type  currentcolor: color (list of ints)

    @param unfinishedcolor: the string of unfinished ANSI color stuff
        that we'll prepend to the string we're printing
    @type  unfinishedcolor: string

    @returns: the new color and unfinished color
    @rtype: list of ints, string
    """
    line = msg.data
    ses = msg.session

    if msg.type == message.ERROR:
        if line.endswith("\n"):
            line = "%s%s%s\n" % (ansi.get_color("b blue"), 
                          line[:-1], 
                          ansi.get_color("default"))
        else:
            line = "%s%s%s" % (ansi.get_color("b blue"), 
                        line[:-1], 
                        ansi.get_color("default"))

    elif msg.type == message.USERDATA:
        if myui._do_i_echo == 1:
            if line.endswith("\n"):
                line = "%s%s%s\n" % (ansi.get_color("b blue"), 
                            line[:-1], 
                            ansi.get_color("default"))
            else:
                line = "%s%s%s" % (ansi.get_color("b blue"), 
                          line[:-1], 
                          ansi.get_color("default"))
        else:
            # if echo is not on--we don't print this
            return currentcolor, unfinishedcolor

    elif msg.type == message.LTDATA:
        if line.endswith("\n"):
            line = "# %s\n" % line[:-1].replace("\n", "\n# ")
        else:
            line = "# %s" % line.replace("\n", "\n# ")


    # now we go through and handle writing all the data
    index = 0
    start = 0

    # we prepend the session name to the text if this is not the 
    # current session sending text and if the Message is session
    # scoped.
    if (ses != None and ses != exported.get_current_session()):
        pretext = "[%s]" % ses.getName()
 
        if line.endswith("\n"):
            line = (pretext + line[:-1].replace("\n", "\n" + pretext) + "\n")
        else:
            line = pretext + line.replace("\n", "\n" + pretext)


    # we remove all \\r stuff because it's icky
    line = line.replace("\r", "")

    tokens = ansi.split_ansi_from_text(line)

    # each session has a saved current color for MUDDATA.  we grab
    # that current color--or use our default if we don't have one
    # for the session yet.  additionally, some sessions have an
    # unfinished color as well--in case we got a part of an ansi 
    # color code in a mud message, and the other part is in another 
    # message.
    if msg.type == message.MUDDATA:
        color = currentcolor.get(ses, list(DEFAULT_COLOR))
        leftover = unfinishedcolor.get(ses, "")

    else:
        color = list(DEFAULT_COLOR)
        leftover = ""


    for mem in tokens:
        if ansi.is_color_token(mem):
            color, leftover = ansi.figure_color([mem], color, leftover)

        else:
            format = []
            fg = ""
            bg = ""

            # handle reverse
            if color[ansi.PLACE_REVERSE] == 0:
                if color[ansi.PLACE_FG] == -1:
                    fg = "37"
                else:
                    fg = str(color[ansi.PLACE_FG])

                if color[ansi.PLACE_BG] != -1:
                    bg = str(color[ansi.PLACE_BG])
                elif color[ansi.PLACE_BG] == -1:
                    bg = "40"
                    

            else:
                if color[ansi.PLACE_BG] == -1:
                    fg = "30"

                else:
                    fg = str(color[ansi.PLACE_BG] - 10)

                if color[ansi.PLACE_FG] == -1:
                    bg = "47"
                else:
                    bg = str(color[ansi.PLACE_FG] + 10)

            # handle bold
            if color[ansi.PLACE_BOLD] == 1:
                fg = "b" + fg

            # handle underline
            if color[ansi.PLACE_UNDERLINE] == 1:
                format.append("u")

            txtbuffer.GetDefaultStyle().SetTextColour(fg_color_codes[fg])
            if bg:
                txtbuffer.GetDefaultStyle().SetBackgroundColour(bg_color_codes[bg])

#            mem = my_filters(mem)

            #following line used for wxTextCtrl
            txtbuffer.AppendText(mem)

    return color, leftover

    
def fix_unicode(text):
    """
    Unicode to standard string translation--fixes unicode bug.
    """
    if type(text) == unicode:
        return text.encode(UNICODE_ENCODING)
    else:
        return text

def colorcheck_cmd(ses, args, input):
    """
    Prints out all the colors so you can verify that things are working
    properly.
    """
    myengine = exported.get_engine()
    myengine._ui._event_queue.put(_ColorCheckEvent())

def colorcheck_cmd(ses, args, input):
    """
    Prints out all the colors so you can verify that things are working
    properly.
    """
    myengine = exported.get_engine()
    myengine._ui._event_queue.put(_ColorCheckEvent())
