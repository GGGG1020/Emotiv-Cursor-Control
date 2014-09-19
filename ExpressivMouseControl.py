import ctypes
import sys
import platform
import time
import os
from ctypes import c_int, Structure, pointer
from ctypes import util
class POINT(Structure):
    _fields_ = [("x", c_int),
               ("y", c_int)]
class EmotivError(Exception):
    """An exception for general emotiv-related errors"""
    pass
class User32Error(Exception):
    """For User32 errors"""
if not sys.platform=="win32":
    raise OSError("This is only available for Windows 32 bit")
#Import our dlls!!
User32Lib=ctypes.windll.LoadLibrary(ctypes.util.find_library("User32"))
os.chdir("")#Insert Emotiv DLL path here!
EmotivLib=ctypes.cdll.LoadLibrary("edk.dll")
class Mouse:
    def __init__(self):
        self.MOUSEEVENTF_ABSOLUTE=0x8000
        self.MOUSEEVENTF_LEFTDOWN=0x0002
        self.MOUSEEVENTF_LEFTUP=0x0004
        self.MOUSEEVENTF_MIDDLEDOWN=0x0020
        self.MOUSEEVENTF_MIDDLEUP=0x0040
        self.MOUSEEVENTF_MOVE=0x0001
        self.MOUSEEVENTF_RIGHTDOWN=0x0008
        self.MOUSEEVENTF_RIGHTUP=0x0010
        self.MOUSEEVENTF_WHEEL=0x0800
        self.MOUSEEVENTF_XDOWN=0x0080
        self.MOUSEEVENTF_XUP=0x0100
        self.MOUSEEVENTF_HWHEEL=0x01000
        self.mouse_current=int()
    def right_click(self):
        """Presses down and releases right mouse button"""
        self.right_down()
        self.right_up()
    def right_down(self):
        """Holds down right mouse button"""
        User32Lib.mouse_event(self.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    def right_up(self):
        """Releases the right mouse button"""
        User32Lib.mouse_event(self.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    def left_click(self):
        self.left_down()
        self.left_up()
    def left_down(self):
        User32Lib.mouse_event(self.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    def left_up(self):
        User32Lib.mouse_event(self.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    def move_mouse(self, x, y):
        User32Lib.SetCursorPos(x, y)
    def get_mouse_pos(self):
        self.point=POINT()
        User32Lib.GetCursorPos(ctypes.pointer(self.point))
        return tuple((self.point.x, self.point.y))
class EmotivMouseControl:
    def __init__(self, development=True):
        self.mouse=Mouse() #Handle to the mouse/cursor
        self.connect_status=int()
        self.user=c_int(0)
        self.userId=pointer(self.user)
        self.eventType=int()
        #Initialize our Emotiv stuff
        if development: #For EmoComposer
            self.connect_status=EmotivLib.EE_EngineRemoteConnect(b'127.0.0.1', c_int(1726)) 
            if not self.connect_status==0:
                raise EmotivError("The call to EE_EngineRemoteConnect resulted in an error, returning with a code of {0}".format(self.connect_status)) #Required for try/except mechanisms 
        else: #For EmoEngine
            self.connect_status=EmotivLib.EE_EngineConnect(b'Emotiv Systems-5')
            if not self.connect_status==0:
                raise EmotivError("The call to EE_EngineRemoteConnect resulted in an error, returning with a code of {0}".format(self.connect_status)) #Required for try/except mechanisms
        self.eEvent=EmotivLib.EE_EmoEngineEventCreate()
        self.eState=EmotivLib.EE_EmoStateCreate()
        while not self.eventType==16:
            EmotivLib.EE_EngineGetNextEvent(self.eEvent)
            self.eventType = EmotivLib.EE_EmoEngineEventGetType(self.eEvent)
        retcode=EmotivLib.EE_EmoEngineEventGetUserId(self.eEvent, self.userId)
        print(self.userId.contents)
    def train(self):
        self.eventType=int()
        EmotivLib.EE_ExpressivSetTrainingAction(self.userId.contents, 1)
        EmotivLib.EE_ExpressivSetTrainingControl(self.userId.contents, 1)
        while not self.eventType==1:
                self.state_current=EmotivLib.EE_EngineGetNextEvent(self.eEvent)
                self.eventType = EmotivLib.EE_ExpressivEventGetType(self.eEvent)   
        print("Begin Training  for nuetral NOW!")
        while not self.eventType==2:
                self.state_current=EmotivLib.EE_EngineGetNextEvent(self.eEvent)
                self.eventType = EmotivLib.EE_ExpressivEventGetType(self.eEvent)   
        print("succeded")
        EmotivLib.EE_ExpressivSetTrainingControl(c_int(0), 2)
        while not self.eventType==4:
                self.state_current=EmotivLib.EE_EngineGetNextEvent(self.eEvent)
                self.eventType = EmotivLib.EE_ExpressivEventGetType(self.eEvent)
        print("DONE!")
        #Furrow
        EmotivLib.EE_ExpressivSetTrainingAction(self.userId.contents,0x0040 )
        EmotivLib.EE_ExpressivSetTrainingControl(self.userId.contents, 1)
        while not self.eventType==1:
            self.state_current=EmotivLib.EE_EngineGetNextEvent(self.eEvent)
            self.eventType = EmotivLib.EE_ExpressivEventGetType(self.eEvent)
        print("Begin Training  for furrow NOW!")
        while not self.eventType==2:
            self.state_current=EmotivLib.EE_EngineGetNextEvent(self.eEvent)
            self.eventType = EmotivLib.EE_ExpressivEventGetType(self.eEvent)
        print("success")
        EmotivLib.EE_ExpressivSetTrainingControl(self.userId.contents, 2)
        while not self.eventType==4:
            self.state_current=EmotivLib.EE_EngineGetNextEvent(self.eEvent)
            self.eventType = EmotivLib.EE_ExpressivEventGetType(self.eEvent)
        print("done")
        #Raise
        EmotivLib.EE_ExpressivSetTrainingAction(self.userId.contents, 0x0020)
        EmotivLib.EE_ExpressivSetTrainingControl(self.userId.contents, 1)
        while not self.eventType==1:
            self.state_current=EmotivLib.EE_EngineGetNextEvent(self.eEvent)
            self.eventType = EmotivLib.EE_ExpressivEventGetType(self.eEvent)
        print("Begin Training  for raise NOW!")
        while not self.eventType==2:
            self.state_current=EmotivLib.EE_EngineGetNextEvent(self.eEvent)
            self.eventType = EmotivLib.EE_ExpressivEventGetType(self.eEvent)
        print("Success!")
        EmotivLib.EE_ExpressivSetTrainingControl(self.userId.contents, 2)
        while not self.eventType==4:
            self.state_current=EmotivLib.EE_EngineGetNextEvent(self.eEvent)
            self.eventType = EmotivLib.EE_ExpressivEventGetType(self.eEvent)
        print("done!")
    def _handle(self, UserID):
        self.mousex, self.mousey=self.mouse.get_mouse_pos()
        if EmotivLib.ES_ExpressivGetUpperFaceAction (self.eState)==0x0020 and not self.mousey==0:
            self.mousey-=10
        if EmotivLib.ES_ExpressivGetUpperFaceAction(self.eState)==0x0040 and not self.mousey==767:
            self.mousey+=10
        if EmotivLib.ES_ExpressivIsLookingLeft(self.eState)==1 and not self.mousey==0:
            self.mousex-=10
        if EmotivLib.ES_ExpressivIsLookingRight(self.eState)==1 and not self.mousey==1365:
            self.mousex+=10
        if EmotivLib.ES_ExpressivIsLeftWink(self.eState)==1:
            self.mouse.left_click()
        self.mouse.move_mouse(self.mousex, self.mousey)        
    def shutdown(self):
        """Bring it DOWN"""
        EmotivLib.EE_EngineDisconnect()
        EmotivLib.EE_EmoStateFree(self.eState)
        EmotivLib.EE_EmoEngineEventFree(self.eEvent)
        print("Cleaup")
        raise 
    def mainloop(self):
        try:
            self.train()
            while True:
                self.state_current=EmotivLib.EE_EngineGetNextEvent(self.eEvent)
                if self.state_current==0:
                    self.eventType = EmotivLib.EE_EmoEngineEventGetType(self.eEvent)
                    EmotivLib.EE_EmoEngineEventGetUserId(self.eEvent, self.user)
                    if self.eventType==64: #New Event!!
                        EmotivLib.EE_EmoEngineEventGetEmoState(self.eEvent,self.eState)
                        self._handle(c_int(0))
        except:self.shutdown()
if __name__=='__main__':
    control=EmotivMouseControl(True)
    control.mainloop()
                
        
            
            
            
            
    
             
        
        
    
        

    

    
