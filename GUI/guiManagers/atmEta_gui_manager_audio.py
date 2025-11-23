import os
import pyglet

_AUDIOCODETABLE = {'button_typeA_HOVERED_A':  '03x00x00x00',
                   'button_typeA_PRESSED_A':  '03x00x01x00',
                   'button_typeA_RELEASED_A': '03x00x02x00',

                   'button_typeB_HOVERED_A':  '03x01x00x00',
                   'button_typeB_PRESSED_A':  '03x01x01x00',
                   'button_typeB_RELEASED_A': '03x01x02x00',

                   'switch_typeA_HOVERED_A':  '04x00x00x00',
                   'switch_typeA_PRESSED_A':  '04x00x01x00',
                   'switch_typeA_RELEASED_A': '04x00x02x00',

                   'switch_typeB_HOVERED_A':  '04x01x00x00',
                   'switch_typeB_PRESSED_A':  '04x01x01x00',
                   'switch_typeB_RELEASED_A': '04x01x02x00',

                   'switch_typeC_HOVERED_A':  '04x02x00x00',
                   'switch_typeC_PRESSED_A':  '04x02x01x00',
                   'switch_typeC_RELEASED_A': '04x02x02x00',

                   'slider_typeA_HOVERED_A':  '05x00x00x00',
                   'slider_typeA_PRESSED_A':  '05x00x01x00',
                   'slider_typeA_RELEASED_A': '05x00x02x00',
                               
                   'scrollBar_typeA_HOVERED_A':  '06x00x00x00',
                   'scrollBar_typeA_PRESSED_A':  '06x00x01x00',
                   'scrollBar_typeA_RELEASED_A': '06x00x02x00',

                   'textInputBox_typeA_HOVERED_A':    '07x00x00x00',
                   'textInputBox_typeA_PRESSED_A':    '07x00x01x00',
                   'textInputBox_typeA_RELEASED_A':   '07x00x02x00',
                   'textInputBox_typeA_TEXTEDITED_A': '07x00x03x00',
                   'textInputBox_typeA_POSMOVED_A':   '07x00x04x00',

                   'selectionBox_typeA_HOVERED_A':     '08x00x00x00',
                   'selectionBox_typeA_PRESSED_A':     '08x00x01x00',
                   'selectionBox_typeA_RELEASED_A':    '08x00x02x00',
                   'selectionBox_typeA_NEWSELHOVERED': '08x00x03x00',

                   'selectionBox_typeB_HOVERED_A':     '08x01x00x00',
                   'selectionBox_typeB_PRESSED_A':     '08x01x01x00',
                   'selectionBox_typeB_RELEASED_A':    '08x01x02x00',
                   'selectionBox_typeB_NEWSELHOVERED': '08x01x03x00',

                   'selectionBox_typeC_HOVERED_A':     '08x02x00x00',
                   'selectionBox_typeC_PRESSED_A':     '08x02x01x00',
                   'selectionBox_typeC_RELEASED_A':    '08x02x02x00',
                   'selectionBox_typeC_NEWSELHOVERED': '08x02x03x00'}

#AUDIO MANAGER OBJECT -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class audioManager:
    def __init__(self, path_project, guiConfig):
        print("\nInitializing Audio Manager")
        self.guiConfig = guiConfig
        self.audios = dict()

        self.path_project = path_project

        #Audio Control Variables
        self.ctrl_Mute   = self.guiConfig['AudioMute']
        self.ctrl_Volume = self.guiConfig['AudioVolume']

        #Read Image Data located at 'path_PROJECT/imgs' Folder
        files = os.listdir(os.path.join(self.path_project, 'GUI', 'audios'))
        for fileName in files:
            if os.path.isfile(os.path.join(self.path_project, 'GUI', 'audios', fileName)):
                try: self.audios[fileName] = pyglet.media.load(os.path.join(self.path_project, 'GUI', 'audios', fileName))
                except: print(" Corrupted or unexpected file detected while attempting to load audio files: '{:s}'".format(fileName))
        print(" * {:d} audio files loaded!".format(len(self.audios)))
        print("Audio Manager Initialization Complete!")

    def playAudio(self, audioName):
        if (self.ctrl_Mute == False):
            if (audioName in self.audios.keys()):
                if (self.ctrl_Mute == False): player = self.audios[audioName].play(); player.volume = self.ctrl_Volume / 100
                return True
            return False

    def playAudioByCode(self, audioCode):
        audioName = "{:s}.mp3".format(_AUDIOCODETABLE[audioCode])
        if (audioName in self.audios.keys()):
            if (self.ctrl_Mute == False): player = self.audios[audioName].play(); player.volume = self.ctrl_Volume / 100
            return True
        return False
        
    def setMute(self, mode = 'toggle'):
        if (mode == 'toggle'): self.ctrl_Mute = not(self.ctrl_Mute)
        elif (mode == True):   self.ctrl_Mute = True
        elif (mode == False):  self.ctrl_Mute = False
        self.guiConfig['AudioMute'] = self.ctrl_Mute

    def isMuted(self):
        return self.ctrl_Mute

    def setVolume(self, volume):
        if ((0 <= volume) and (volume <= 100)): self.ctrl_Volume = round(volume, 1)
        self.guiConfig['AudioVolume'] = self.ctrl_Volume

    def getVolume(self):
        return self.ctrl_Volume
#AUDIO MANAGER OBJECT END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------