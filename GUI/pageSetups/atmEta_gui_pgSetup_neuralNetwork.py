#ATM Modules
import atmEta_IPC
import atmEta_Auxillaries
from GUI import atmEta_gui_AdvancedPygletGroups
from GUI.atmEta_gui_TextControl import textObject_SL, textObject_SL_I, textObject_SL_IE
from GUI.atmEta_gui_Generals import passiveGraphics_typeA,\
                                    passiveGraphics_wrapperTypeA,\
                                    passiveGraphics_wrapperTypeB,\
                                    passiveGraphics_wrapperTypeC,\
                                    textBox_typeA,\
                                    imageBox_typeA,\
                                    button_typeA,\
                                    button_typeB,\
                                    switch_typeA,\
                                    switch_typeB,\
                                    switch_typeC,\
                                    slider_typeA,\
                                    scrollBar_typeA,\
                                    textInputBox_typeA,\
                                    LED_typeA,\
                                    gaugeBar_typeA,\
                                    selectionBox_typeA,\
                                    selectionBox_typeB,\
                                    selectionBox_typeC,\
                                    subPageBox_typeA
from GUI.atmEta_gui_ChartDrawer          import chartDrawer
from GUI.atmEta_gui_PeriodicReportViewer import periodicReportViewer
from GUI.atmEta_gui_NeuralNetworkViewer  import neuralNetworkViewer

#Python Modules
import pyglet
import pprint
import termcolor
import time
import random
import json
from datetime import datetime, timezone, tzinfo

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

_NEURALNETWORKLISTUPDATEINTERVAL_NS = 1000e6

_NKLINES_DEFAULT      = 10
_OUTPUTLAYER_DEFAULT  = json.dumps({'type': 'SIGMOID', 'params': None})
_HIDDENLAYERS_DEFAULT = json.dumps([{'type': 'SIGMOID', 'size': 10, 'params': None}])

#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
    self.puVar['_FIRSTLOAD'] = True
    
    self.puVar['manager_viewType'] = 'NEURALNETWORKS'
    self.puVar['manager_viewDependentGUIOs'] = {'NEURALNETWORKS': set(),
                                                'PROCESSES':      set()}
    self.puVar['neuralNetworks']             = dict()
    self.puVar['neuralNetwork_selected']     = None
    self.puVar['neuralNetworks_controlKeys'] = dict()
    self.puVar['neuralNetworksListUpdate_ItemsToUpdate']  = dict()
    self.puVar['neuralNetworksListUpdate_LastUpdated_ns'] = 0
    self.puVar['initializationTypes'] = dict()
    self.puVar['optimizerTypes']      = dict()
    self.puVar['lossFunctionTypes']   = dict()

    self.puVar['processes']          = dict()
    self.puVar['process_selected']   = None
    self.puVar['process_controlKey'] = None
    self.puVar['processesListUpdate_ItemsToUpdate']  = dict()
    self.puVar['processesListUpdate_LastUpdated_ns'] = 0

    self.puVar['controlAndDetail_viewType']  = 'NETWORKSTRUCTURE'
    self.puVar['controlAndDetail_viewDependentGUIOs'] = {'NETWORKSTRUCTURE': set(),
                                                         'TAP':              set()}
    self.puVar['currencies']        = dict()
    self.puVar['currency_selected'] = None

    #Setup Functions
    self.pageAuxillaryFunctions = __generateAuxillaryFunctions(self) #Generate auxillary functions
    self.pageLoadFunction       = __pageLoadFunction                 #Set page load function
    self.pageEscapeFunction     = __pageEscapeFunction               #Set page escape function
    self.pageProcessFunction    = __pageProcessFunction              #Set page process function
    self.pageObjectFunctions    = __generateObjectFunctions(self)    #Generate object functions

    #Setup a pyglet group for background
    self.groups['BACKGROUND'] = pyglet.graphics.Group(order = 0)

    #Generate guioInitialization base instances
    inst = {'windowInstance':      self.windowInstance,
            'displaySpaceDefiner': self.displaySpaceDefiner,
            'guioConfig':          self.guioConfig,
            'batch':               self.batch,
            'scaler':              self.displaySpaceDefiner['scaler'],
            'imageManager':        self.imageManager,
            'audioManager':        self.audioManager,
            'visualManager':       self.visualManager,
            'sysFunctions':        self.sysFunctions,
            'ipcA':                self.ipcA}

    #GUIO Initializations
    if (self.displaySpaceDefiner['ratio'] == '16:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 16000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
        self.GUIOs["TITLETEXT_NEURALNETWORK"] = textBox_typeA(**inst, groupOrder=1, xPos= 6000, yPos=8550, width=4000, height=400, style=None, text=self.visualManager.getTextPack('NEURALNETWORK:TITLE'), fontSize = 220, textInteractable = False)

        self.GUIOs["BUTTON_MOVETO_DASHBOARD"] = button_typeB(**inst,  groupOrder=2, xPos=  50, yPos=8650, width= 300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['PAGEMOVE_DASHBOARD'], image = 'dashboardIcon_512x512.png', imageSize = (225, 225), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        
        #<NeuralNetwork Manager>
        self.GUIOs["BLOCKTITLE_NEURALNETWORKMANAGER"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=8350, width=4600, height=200, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:BLOCKTITLE_NEURALNETWORKMANAGER'), fontSize=80)
        #---View Type Selection
        self.GUIOs["NEURALNETWORKMANAGER_VIEWNEURALNETWORKS"] = switch_typeC(**inst, groupOrder=1, xPos= 100, yPos=8000, width=2250, height=250, style="styleB", name = 'NEURALNETWORKS', text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_NEURALNETWORKMANAGER_VIEWSWITCH'])
        self.GUIOs["NEURALNETWORKMANAGER_VIEWPROCESSES"]      = switch_typeC(**inst, groupOrder=1, xPos=2450, yPos=8000, width=2250, height=250, style="styleB", name = 'PROCESSES',      text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES'),      fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_NEURALNETWORKMANAGER_VIEWSWITCH'])
        self.GUIOs["NEURALNETWORKMANAGER_VIEWNEURALNETWORKS"].setStatus(status = True, callStatusUpdateFunction = False)
        #---[1]: NeuralNetworks
        if (True):
            self.GUIOs["BLOCKSUBTITLE_NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=7700, width=4600, height=200, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKS'), fontSize=80)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_SELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=2, xPos= 100, yPos=2900, width=4600, height=4700, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKSELECTION'], 
                                                                           elementWidths = (800, 2350, 1200)) #4350
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_ST_INDEX')},       # 800
                                                                                                            {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_ST_NETWORKCODE')}, #2350
                                                                                                            {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_ST_STATUS')}])     #1200
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMETITLETEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=2550, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAME'), fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMETEXTINPUTBOX"]   = textInputBox_typeA(**inst, groupOrder=1, xPos=1500, yPos=2550, width=3200, height=250, style="styleA", text="",                                                                                                    fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKCODE'])
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMEDISPLAYTEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=1500, yPos=2550, width=3200, height=250, style="styleA", text="",                                                                                                    fontSize=80, textInteractable=True)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMEDISPLAYTEXT"].hide()
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPETITLETEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=2200, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPE'), fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPESELECTIONBOX"]   = selectionBox_typeB(**inst, groupOrder=2, xPos=1500, yPos=2200, width=3200, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = None)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPEDISPLAYTEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=1500, yPos=2200, width=3200, height=250, style="styleA", text="",                                                                                                    fontSize=80, textInteractable=True)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPEDISPLAYTEXT"].hide()
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTITLETEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=1850, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEY'),        fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"]          = textInputBox_typeA(**inst, groupOrder=1, xPos=1500, yPos=1850, width=2100, height=250, style="styleA", text="",                                                                                                    fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEY'])
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASESWITCH"]     = switch_typeC(**inst,       groupOrder=1, xPos=3700, yPos=1850, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_HOLDCONTROLKEY'),    fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASE'])
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASESWITCH"].deactivate()
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATIONTIMETITLETEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=1500, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATIONTIME'),    fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATIONTIMEDISPLAYTEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=1500, yPos=1500, width=3200, height=250, style="styleA", text="-",                                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_STATUSTITLETEXT"]                 = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=1150, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS'),            fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_STATUSDISPLAYTEXT"]               = textBox_typeA(**inst,      groupOrder=1, xPos= 900, yPos=1150, width=1000, height=250, style="styleA", text="-",                                                                                                   fontSize=80, textInteractable=True)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONGAUGEBAR"]              = gaugeBar_typeA(**inst,     groupOrder=1, xPos=2000, yPos=1150, width=2700, height=250, style="styleB", align='horizontal', gaugeColor = (0, 0, 0, 255))
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = 0)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONGAUGEBAR"].updateGaugeColor(rValue = 100, gValue = 200, bValue = 255)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONDISPLAYTEXT"]           = textBox_typeA(**inst,      groupOrder=1, xPos=2000, yPos=1150, width=2700, height=250, style=None, text="-", fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONTITLETEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos= 800, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONSETUP'), fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONSELECTIONBOX"]      = selectionBox_typeB(**inst, groupOrder=3, xPos=1500, yPos= 800, width=1300, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 1, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONTYPE'])
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONTEXTINPUTBOX"]      = textInputBox_typeA(**inst, groupOrder=1, xPos=2900, yPos= 800, width=1800, height=250, style="styleA", text="",                                                                                                      fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONTEXT'])
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATENEURALNETWORKBUTTON"]     = button_typeA(**inst,       groupOrder=1, xPos= 100, yPos= 450, width=1800, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATE'),            fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATENEURALNETWORK'])
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATENEURALNETWORKBUTTON"].deactivate()
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONBUTTON"]            = button_typeA(**inst,       groupOrder=1, xPos=2000, yPos= 450, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZE'),          fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZENEURALNETWORK'])
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONBUTTON"].deactivate()
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_REMOVENEURALNETWORKBUTTON"]        = button_typeA(**inst,      groupOrder=1, xPos=3100, yPos= 450, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_REMOVE'),              fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_NEURALNETWORKMANAGER_NEURALNETWORKS_REMOVENEURALNETWORK'])
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"] = switch_typeB(**inst,      groupOrder=2, xPos=4200, yPos= 450, width= 500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSTATUSUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH'])
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_REMOVENEURALNETWORKBUTTON"].deactivate()
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"].deactivate()
            _guioNamesGroups = self.puVar['manager_viewDependentGUIOs']['NEURALNETWORKS']
            _guioNamesGroups.add("BLOCKSUBTITLE_NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKS")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_SELECTIONBOX")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMETITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMETEXTINPUTBOX")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMEDISPLAYTEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPETITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPESELECTIONBOX")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPEDISPLAYTEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASESWITCH")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATIONTIMETITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATIONTIMEDISPLAYTEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_STATUSTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_STATUSDISPLAYTEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONGAUGEBAR")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONDISPLAYTEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONSELECTIONBOX")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONTEXTINPUTBOX")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATENEURALNETWORKBUTTON")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONBUTTON")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_REMOVENEURALNETWORKBUTTON")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH")
        #---[2]: Processes
        if (True):
            self.GUIOs["BLOCKSUBTITLE_NEURALNETWORKMANAGER_PROCESSES_PROCESSES"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=7700, width=4600, height=200, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKMANAGER_PROCESSES_PROCESSES'), fontSize=80)
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_SELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=2, xPos= 100, yPos=1500, width=4600, height=6100, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_NEURALNETWORKMANAGER_PROCESSES_PROCESSSELECTION'], 
                                                                                           elementWidths = (600, 1050, 700, 700, 600, 700, 1500, 2500, 600, 600, 600, 600)) #4350
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_INDEX')},         # 600
                                                                                                       {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_NETWORKCODE')},   #1050
                                                                                                       {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_TYPE')},          # 700
                                                                                                       {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_STATUS')},        # 700
                                                                                                       {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_COMPLETION')},    # 600
                                                                                                       {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_ETC')},           # 700
                                                                                                       {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_TARGET')},        #1500
                                                                                                       {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_TARGETRANGE')},   #2500
                                                                                                       {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_NEPOCHS')},       # 600
                                                                                                       {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_BATCHSIZE')},     # 600
                                                                                                       {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_LEARNINGRATE')},  # 600
                                                                                                       {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_ST_SWINGRANGE')}])   # 600
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_STATUSTITLETEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=1150, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS'),         fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_STATUSDISPLAYTEXT"]           = textBox_typeA(**inst,      groupOrder=1, xPos= 900, yPos=1150, width=1000, height=250, style="styleA", text="-",                                                                                           fontSize=80, textInteractable=True)
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONGAUGEBAR"]          = gaugeBar_typeA(**inst,     groupOrder=1, xPos=2000, yPos=1150, width=2700, height=250, style="styleB", align='horizontal', gaugeColor = (0, 0, 0, 255))
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = 0)
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONGAUGEBAR"].updateGaugeColor(rValue = 100, gValue = 200, bValue = 255)
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONDISPLAYTEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=2000, yPos=1150, width=2700, height=250, style=None, text="-", fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYTITLETEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos= 800, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_CONTROLKEY'),     fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYTEXTINPUTBOX"]      = textInputBox_typeA(**inst, groupOrder=1, xPos=1700, yPos= 800, width=1900, height=250, style="styleA", text="",                                                                                            fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKMANAGER_PROCESSES_CONTROLKEY'])
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYHOLDRELEASESWITCH"] = switch_typeC(**inst,       groupOrder=1, xPos=3700, yPos= 800, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_HOLDCONTROLKEY'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYHOLDRELEASE'])
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYHOLDRELEASESWITCH"].deactivate()
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTON"]         = button_typeA(**inst,       groupOrder=1, xPos= 100, yPos= 450, width=4000, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_REMOVE'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESS'])
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH"]   = switch_typeB(**inst,       groupOrder=2, xPos=4200, yPos= 450, width= 500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH'])
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTON"].deactivate()
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH"].deactivate()
            _guioNamesGroups = self.puVar['manager_viewDependentGUIOs']['PROCESSES']
            _guioNamesGroups.add("BLOCKSUBTITLE_NEURALNETWORKMANAGER_PROCESSES_PROCESSES")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_PROCESSES_SELECTIONBOX")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_PROCESSES_STATUSTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_PROCESSES_STATUSDISPLAYTEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_PROCESSES_COMPLETIONGAUGEBAR")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_PROCESSES_COMPLETIONDISPLAYTEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYTEXTINPUTBOX")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYHOLDRELEASESWITCH")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTON")
            _guioNamesGroups.add("NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH")
        #---View Targets Initialization
        if (True):
            for _viewTarget in self.puVar['manager_viewDependentGUIOs']:
                if (_viewTarget == self.puVar['manager_viewType']):
                    for _guioName in self.puVar['manager_viewDependentGUIOs'][_viewTarget]: self.GUIOs[_guioName].show()
                    if (_viewTarget == 'NEURALNETWORKS'):
                        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMEDISPLAYTEXT"].hide()
                        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPEDISPLAYTEXT"].hide()
                else:
                    for _guioName in self.puVar['manager_viewDependentGUIOs'][_viewTarget]: self.GUIOs[_guioName].hide()

        #<NeuralNetwork Control & Detail>
        self.GUIOs["BLOCKTITLE_NEURALNETWORKCONTROL&DETAIL"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=4800, yPos=8350, width=11100, height=200, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:BLOCKTITLE_NEURALNETWORKCONTROL&DETAIL'), fontSize=80)
        #---View Type Selection
        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_VIEWNETWORKSTRUCTURE"] = switch_typeC(**inst, groupOrder=1, xPos= 4800, yPos=8000, width=5500, height=250, style="styleB", name = 'NETWORKSTRUCTURE', text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_NEURALNETWORKCONTROL&DETAIL_VIEWSWITCH'])
        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_VIEWTAP"]              = switch_typeC(**inst, groupOrder=1, xPos=10400, yPos=8000, width=5500, height=250, style="styleB", name = 'TAP',              text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP'),              fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_NEURALNETWORKCONTROL&DETAIL_VIEWSWITCH'])
        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_VIEWNETWORKSTRUCTURE"].setStatus(status = True, callStatusUpdateFunction = False)
        #---[1]: Network Structure
        if (True):
            self.GUIOs["BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_STRUCTUREPARAMETERS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=4800, yPos=7700, width=11100, height=200, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_STRUCTUREPARAMETERS'), fontSize=80)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESTITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=4800, yPos=7350, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINES'),      fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESTEXTINPUT"]        = textInputBox_typeA(**inst, groupOrder=1, xPos=5900, yPos=7350, width= 500, height=250, style="styleA", text="{:d}".format(_NKLINES_DEFAULT),                                                                           fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESTEXT'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESDISPLAYTEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=5900, yPos=7350, width= 500, height=250, style="styleA", text="-",                                                                                                       fontSize=80, textInteractable=True)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=6500, yPos=7350, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYER'),  fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERTEXTINPUT"]    = textInputBox_typeA(**inst, groupOrder=1, xPos=7800, yPos=7350, width=8100, height=250, style="styleA", text=_OUTPUTLAYER_DEFAULT,                                                                                      fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERTEXT'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERDISPLAYTEXT"]  = textBox_typeA(**inst,      groupOrder=1, xPos=7800, yPos=7350, width=8100, height=250, style="styleA", text="-",                                                                                                       fontSize=80, textInteractable=True)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSTITLETEXT"]   = textBox_typeA(**inst,      groupOrder=1, xPos=4800, yPos=7000, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERS'), fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSTEXTINPUT"]   = textInputBox_typeA(**inst, groupOrder=1, xPos=6100, yPos=7000, width=9800, height=250, style="styleA", text=_HIDDENLAYERS_DEFAULT,                                                                                     fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSTEXT'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSDISPLAYTEXT"] = textBox_typeA(**inst,      groupOrder=1, xPos=6100, yPos=7000, width=9800, height=250, style="styleA", text="-",                                                                                                       fontSize=80, textInteractable=True)
            self.GUIOs["BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_STRUCTUREDETAIL"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=4800, yPos=6700, width=11100, height=200, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_STRUCTUREDETAIL'), fontSize=80)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NEURALNETWORKVIEWER"] = neuralNetworkViewer(**inst, groupOrder=1, xPos=4800, yPos=450, width=11100, height=6150, style="styleA", name = 'NEURALNETWORK_NEURALNETWORKCONTROLANDDETAIL_NETWORKSTRUCTURE_NEURALNETWORKVIEWER')
            _guioNamesGroups = self.puVar['controlAndDetail_viewDependentGUIOs']['NETWORKSTRUCTURE']
            _guioNamesGroups.add("BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_STRUCTUREPARAMETERS")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESTEXTINPUT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESDISPLAYTEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERTEXTINPUT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERDISPLAYTEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSTEXTINPUT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSDISPLAYTEXT")
            _guioNamesGroups.add("BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_STRUCTUREDETAIL")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NEURALNETWORKVIEWER")
        #---[2]: TAP (Training And Performance)
        if (True):
            self.GUIOs["BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCIES"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=4800, yPos=7700, width=3950, height=200, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCIES'), fontSize=80)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSEARCHTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=4800, yPos=7350, width= 800, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SEARCH'), fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSEARCHTEXTINPUT"]    = textInputBox_typeA(**inst, groupOrder=1, xPos=5700, yPos=7350, width=3050, height=250, style="styleA", text="",                                                                                     fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSEARCHTEXT'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSORTBYTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=4800, yPos=7000, width= 800, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SORTBY'), fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSORTBYSELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=2, xPos=5700, yPos=7000, width=3050, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSORTBYTYPE'])
            _currencySortTypes = {'INDEX':      {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SORTBY_INDEX')},
                                  'SYMBOL':     {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SORTBY_SYMBOL')},
                                  'STATUS':     {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SORTBY_STATUS')},
                                  'FIRSTKLINE': {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SORTBY_FIRSTKLINE')}}
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSORTBYSELECTIONBOX"].setSelectionList(selectionList = _currencySortTypes, displayTargets = 'all')
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSORTBYSELECTIONBOX"].setSelected(itemKey = 'INDEX', callSelectionUpdateFunction = False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=2, xPos=4800, yPos=3250, width=3950, height=3650, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCY'], 
                                                                                                    elementWidths = (700, 1200, 700, 1100)) #3700
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_INDEX')},       # 700
                                                                                                                {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_SYMBOL')},      #1200
                                                                                                                {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_STATUS')},      # 700
                                                                                                                {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_FIRSTKLINE')}]) #1100
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSYMBOLTITLETEXT"]   = textBox_typeA(**inst,      groupOrder=1, xPos=4800, yPos=2900, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SYMBOL'),             fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSYMBOLDISPLAYTEXT"] = textBox_typeA(**inst,      groupOrder=1, xPos=6100, yPos=2900, width=2650, height=250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=True)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_DATARANGESTITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=4800, yPos=2550, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_DATARANGES'),         fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_DATARANGESDISPLAYTEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=6100, yPos=2550, width=2650, height=250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=True)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGETITLETEXT"]  = textBox_typeA(**inst,      groupOrder=1, xPos=4800, yPos=2200, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGE'),    fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGEINPUTTEXT1"] = textInputBox_typeA(**inst, groupOrder=1, xPos=6100, yPos=2200, width=1275, height=250, style="styleA", text="",                                                                                                 fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGE'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGEINPUTTEXT2"] = textInputBox_typeA(**inst, groupOrder=1, xPos=7475, yPos=2200, width=1275, height=250, style="styleA", text="",                                                                                                 fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGE'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERTITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=4800, yPos=1850, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZER'),          fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERSELECTIONBOX"]     = selectionBox_typeB(**inst, groupOrder=2, xPos=6100, yPos=1850, width=1000, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 1, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERTYPE'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERINPUTTEXT"]        = textInputBox_typeA(**inst, groupOrder=1, xPos=7200, yPos=1850, width=1550, height=250, style="styleA", text="",                                                                                                 fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZER'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONTITLETEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=4800, yPos=1500, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTION'),       fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONSELECTIONBOX"]  = selectionBox_typeB(**inst, groupOrder=3, xPos=6100, yPos=1500, width=1000, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 1, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONTYPE'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONINPUTTEXT"]     = textInputBox_typeA(**inst, groupOrder=1, xPos=7200, yPos=1500, width=1550, height=250, style="styleA", text="",                                                                                                 fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTION'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_NEPOCHSTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos=4800, yPos=1150, width= 825, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_NEPOCHS'),            fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_NEPOCHSINPUTTEXT"]          = textInputBox_typeA(**inst, groupOrder=1, xPos=5725, yPos=1150, width=1000, height=250, style="styleA", text="1",                                                                                                fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_NEPOCHS'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_BATCHSIZETITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=6825, yPos=1150, width= 825, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_BATCHSIZE'),          fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_BATCHSIZEINPUTTEXT"]        = textInputBox_typeA(**inst, groupOrder=1, xPos=7750, yPos=1150, width=1000, height=250, style="styleA", text="10",                                                                                               fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_BATCHSIZE'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LEARNINGRATETITLETEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=4800, yPos= 800, width= 825, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_LEARNINGRATE'),       fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LEARNINGRATEINPUTTEXT"]     = textInputBox_typeA(**inst, groupOrder=1, xPos=5725, yPos= 800, width=1000, height=250, style="styleA", text="0.01",                                                                                             fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_LEARNINGRATE'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_SWINGRANGETITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=6825, yPos= 800, width= 825, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_SWINGRANGE'),         fontSize=80, textInteractable=False)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_SWINGRANGEINPUTTEXT"]       = textInputBox_typeA(**inst, groupOrder=1, xPos=7750, yPos= 800, width=1000, height=250, style="styleA", text="0.0100",                                                                                           fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_SWINGRANGE'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_RUNTRAININGBUTTON"]         = button_typeA(**inst,       groupOrder=1, xPos=4800, yPos= 450, width=1925, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_RUNTRAINING'),        fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_NEURALNETWORKCONTROL&DETAIL_TAP_RUNTRAINING'])
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_RUNPERFORMANCETESTBUTTON"]  = button_typeA(**inst,       groupOrder=1, xPos=6825, yPos= 450, width=1925, height=250, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_RUNPERFORMANCETEST'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_NEURALNETWORKCONTROL&DETAIL_TAP_RUNPERFORMANCETEST'])
            self.GUIOs["BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_TAP_TRAININGLOG"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=8850, yPos=7700, width=7050, height=200, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_TAP_TRAININGLOG'), fontSize=80)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TRAININGLOGSELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=2, xPos=8850, yPos=4300, width=7050, height=3300, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCY'], 
                                                                                                       elementWidths = (800, 1000, 1500, 2200, 1300)) #6800
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TRAININGLOGSELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_INDEX')},       # 800
                                                                                                                   {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_TIME')},        #1000
                                                                                                                   {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_TARGET')},      #1500
                                                                                                                   {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_TARGETRANGE')}, #2200
                                                                                                                   {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_LOSSVALUE')}])  #1300
            self.GUIOs["BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_TAP_PERFORMANCETESTLOG"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=8850, yPos=4000, width=7050, height=200, style="styleA", text=self.visualManager.getTextPack('NEURALNETWORK:BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_TAP_PERFORMANCETESTLOG'), fontSize=80)
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_PERFORMANCETESTLOGSELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=2, xPos=8850, yPos=450, width=7050, height=3450, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCY'], 
                                                                                                              elementWidths = (800, 1000, 1500, 2200, 1300)) #6800
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_PERFORMANCETESTLOGSELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_INDEX')},       # 800
                                                                                                                          {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_TIME')},        #1000
                                                                                                                          {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_TARGET')},      #1500
                                                                                                                          {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_TARGETRANGE')}, #2200
                                                                                                                          {'text': self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_ST_LOSSVALUE')}])  #1300
            _guioNamesGroups = self.puVar['controlAndDetail_viewDependentGUIOs']['TAP']
            _guioNamesGroups.add("BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCIES")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSEARCHTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSEARCHTEXTINPUT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSORTBYTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSORTBYSELECTIONBOX")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSELECTIONBOX")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSYMBOLTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSYMBOLDISPLAYTEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_DATARANGESTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_DATARANGESDISPLAYTEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGETITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGEINPUTTEXT1")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGEINPUTTEXT2")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERSELECTIONBOX")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERINPUTTEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONSELECTIONBOX")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONINPUTTEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_NEPOCHSTITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_NEPOCHSINPUTTEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_BATCHSIZETITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_BATCHSIZEINPUTTEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_LEARNINGRATETITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_LEARNINGRATEINPUTTEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_SWINGRANGETITLETEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_SWINGRANGEINPUTTEXT")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_RUNTRAININGBUTTON")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_RUNPERFORMANCETESTBUTTON")
            _guioNamesGroups.add("BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_TAP_TRAININGLOG")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_TRAININGLOGSELECTIONBOX")
            _guioNamesGroups.add("BLOCKSUBTITLE_NEURALNETWORKCONTROL&DETAIL_TAP_PERFORMANCETESTLOG")
            _guioNamesGroups.add("NEURALNETWORKCONTROL&DETAIL_TAP_PERFORMANCETESTLOGSELECTIONBOX")
        #---View Targets Initialization
        if (True):
            for _viewTarget in self.puVar['controlAndDetail_viewDependentGUIOs']:
                if (_viewTarget == self.puVar['controlAndDetail_viewType']):
                    for _guioName in self.puVar['controlAndDetail_viewDependentGUIOs'][_viewTarget]: self.GUIOs[_guioName].show()
                    if (_viewTarget == 'NETWORKSTRUCTURE'):
                        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESDISPLAYTEXT"].hide()
                        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSDISPLAYTEXT"].hide()
                        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERDISPLAYTEXT"].hide()
                else:
                    for _guioName in self.puVar['controlAndDetail_viewDependentGUIOs'][_viewTarget]: self.GUIOs[_guioName].hide()

        #<Message>
        self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=  100, yPos=100, width=15800, height=250, style="styleA", text="-", fontSize=80, textInteractable=False)

    elif (self.displaySpaceDefiner['ratio'] == '21:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 21000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
    elif (self.displaySpaceDefiner['ratio'] == '32:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 32000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
#SETUP PAGE <MAIN> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <LOAD> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageLoadFunction(self):
    #FAR Registration
    #---NEURALNETWORKMANAGER
    self.ipcA.addFARHandler('onNeuralNetworkUpdate', self.pageAuxillaryFunctions['_FAR_ONNEURALNETWORKUPDATE'], executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
    self.ipcA.addFARHandler('onProcessUpdate',     self.pageAuxillaryFunctions['_FAR_ONPROCESSUPDATE'],         executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
    #---DATAMANAGER
    self.ipcA.addFARHandler('onCurrenciesUpdate', self.pageAuxillaryFunctions['_FAR_ONCURRENCIESUPDATE'], executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
    
    #Get data via PRD
    self.puVar['neuralNetworks']         = self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'NEURALNETWORKS')
    self.puVar['processes']              = self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'PROCESSES')
    self.puVar['currencies']             = self.ipcA.getPRD(processName = 'DATAMANAGER',          prdAddress = 'CURRENCIES')
    self.puVar['analysisConfigurations'] = self.ipcA.getPRD(processName = 'TRADEMANAGER',         prdAddress = 'CURRENCYANALYSISCONFIGURATIONS').copy()

    #FirstLoad Handler
    if (self.puVar['_FIRSTLOAD'] == True):
        #[1]: Neural Network Types
        _neuralNetworkTypes = dict()
        _firstNNT = None
        for _neuralNetworkType in self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'NEURALNETWORKTYPES'): 
            _neuralNetworkTypes[_neuralNetworkType] = {'text': _neuralNetworkType}
            if (_firstNNT == None): _firstNNT = _neuralNetworkType
        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPESELECTIONBOX"].setSelectionList(selectionList = _neuralNetworkTypes, displayTargets = 'all')
        if (_firstNNT != None): self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPESELECTIONBOX"].setSelected(itemKey = _firstNNT, callSelectionUpdateFunction = True)
        #[2]: Initialization Types
        #---Data Read
        _initTypes_PRD = self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'INITIALIZATIONTYPES') 
        self.puVar['initializationTypes'] = dict()
        for _initType in _initTypes_PRD: self.puVar['initializationTypes'][_initType] = json.dumps(_initTypes_PRD[_initType])
        #---Selection Box
        _initializationTypesList = dict()
        _firstIT = None
        for _initializationType in self.puVar['initializationTypes']: 
            _initializationTypesList[_initializationType] = {'text': _initializationType}
            if (_firstIT == None): _firstIT = _initializationType
        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONSELECTIONBOX"].setSelectionList(selectionList = _initializationTypesList, displayTargets = 'all')
        if (_firstIT != None): self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONSELECTIONBOX"].setSelected(itemKey = _firstIT, callSelectionUpdateFunction = True)
        #[3]: Optimizer Types
        _optimizerTypes_PRD = self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'OPTIMIZERTYPES') 
        self.puVar['optimizerTypes'] = dict()
        for _optimizerType in _optimizerTypes_PRD: self.puVar['optimizerTypes'][_optimizerType] = json.dumps(_optimizerTypes_PRD[_optimizerType])
        #---Selection Box
        _optimizerTypesList = dict()
        _firstOT = None
        for _optimizerType in self.puVar['optimizerTypes']: 
            _optimizerTypesList[_optimizerType] = {'text': _optimizerType}
            if (_firstOT == None): _firstOT = _optimizerType
        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERSELECTIONBOX"].setSelectionList(selectionList = _optimizerTypesList, displayTargets = 'all')
        if (_firstOT != None): self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERSELECTIONBOX"].setSelected(itemKey = _firstOT, callSelectionUpdateFunction = True)
        #[4]: Loss Function Types
        _lossFunctionTypes_PRD = self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'LOSSFUNCTIONTYPES') 
        self.puVar['lossFunctionTypes'] = dict()
        for _lossFunctionType in _lossFunctionTypes_PRD: self.puVar['lossFunctionTypes'][_lossFunctionType] = json.dumps(_lossFunctionTypes_PRD[_lossFunctionType])
        #---Selection Box
        _lossFunctionTypesList = dict()
        _firstLFT = None
        for _lossFunctionType in self.puVar['lossFunctionTypes']: 
            _lossFunctionTypesList[_lossFunctionType] = {'text': _lossFunctionType}
            if (_firstLFT == None): _firstLFT = _lossFunctionType
        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONSELECTIONBOX"].setSelectionList(selectionList = _lossFunctionTypesList, displayTargets = 'all')
        if (_firstLFT != None): self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONSELECTIONBOX"].setSelected(itemKey = _firstLFT, callSelectionUpdateFunction = True)
        #Finally
        self.puVar['_FIRSTLOAD'] = False

    self.pageAuxillaryFunctions['SETNEURALNETWORKSLIST']() #Set Neural Networks List
    self.pageAuxillaryFunctions['SETPROCESSESLIST']()      #Set Processes List
    self.pageAuxillaryFunctions['SETCURRENCIESLIST']()     #Set Currencies List
#SETUP PAGE <LOAD> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <ESCAPE> --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageEscapeFunction(self):
    pass
#SETUP PAGE <ESCAPE> END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <PROCESS> -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageProcessFunction(self, t_elapsed_ns, onLoad = False):
    t_current_ns = time.perf_counter_ns()
    #Neural Networks List Update
    if (0 < len(self.puVar['neuralNetworksListUpdate_ItemsToUpdate'])) and (_NEURALNETWORKLISTUPDATEINTERVAL_NS <= t_current_ns-self.puVar['neuralNetworksListUpdate_LastUpdated_ns']):
        for _neuralNetworkCode in self.puVar['neuralNetworksListUpdate_ItemsToUpdate']:
            for _dataName in self.puVar['neuralNetworksListUpdate_ItemsToUpdate'][_neuralNetworkCode]:
                if (_neuralNetworkCode in self.puVar['neuralNetworks']):
                    _neuralNetwork = self.puVar['neuralNetworks'][_neuralNetworkCode]
                    if (_dataName == 'status'):
                        _status = _neuralNetwork['status']
                        if   (_status == 'STANDBY'):  _text = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_STANDBY');  _textColor = 'GREEN_LIGHT' 
                        elif (_status == 'QUEUED'):   _text = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_QUEUED');   _textColor = 'BLUE'
                        elif (_status == 'TRAINING'): _text = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_TRAINING'); _textColor = 'BLUE_LIGHT'
                        elif (_status == 'TESTING'):  _text = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_TESTING');  _textColor = 'BLUE_LIGHT'
                        _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),]}
                        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_SELECTIONBOX"].editSelectionListItem(itemKey = _neuralNetworkCode, item = _newSelectionBoxItem, columnIndex = 2)
        self.puVar['neuralNetworksListUpdate_ItemsToUpdate'].clear()
        self.puVar['neuralNetworksListUpdate_LastUpdated_ns'] = t_current_ns
    #Process List Update
    if (0 < len(self.puVar['processesListUpdate_ItemsToUpdate'])) and (_NEURALNETWORKLISTUPDATEINTERVAL_NS <= t_current_ns-self.puVar['processesListUpdate_LastUpdated_ns']):
        for _processCode in self.puVar['processesListUpdate_ItemsToUpdate']:
            for _dataName in self.puVar['processesListUpdate_ItemsToUpdate'][_processCode]:
                if (_processCode in self.puVar['processes']):
                    _process = self.puVar['processes'][_processCode]
                    if (_dataName == 'status'):
                        _status = _process['status']
                        if   (_status == 'QUEUED'):        _text = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_QUEUED');        _textColor = 'BLUE_LIGHT'
                        elif (_status == 'PREPARING'):     _text = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PREPARING');     _textColor = 'ORANGE_LIGHT'
                        elif (_status == 'PREPROCESSING'): _text = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PREPROCESSING'); _textColor = 'CYAN_LIGHT'
                        elif (_status == 'PROCESSING'):    _text = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PROCESSING');    _textColor = 'GREEN_LIGHT'
                        _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),]}
                        self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_SELECTIONBOX"].editSelectionListItem(itemKey = _processCode, item = _newSelectionBoxItem, columnIndex = 3)
                    elif (_dataName == 'completion'):
                        #Completion
                        _completion = _process['completion']
                        if (_completion == None): _text = "-"
                        else:                     _text = "{:.3f} %".format(_completion*100)
                        _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', 'DEFAULT'),]}
                        self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_SELECTIONBOX"].editSelectionListItem(itemKey = _processCode, item = _newSelectionBoxItem, columnIndex = 4)
                        #Completion ETC
                        _completion_ETC_s = _process['completion_ETC_s']
                        if (_completion_ETC_s == None): _text = "-"
                        else:                           _text = atmEta_Auxillaries.timeStringFormatter(time_seconds = int(_completion_ETC_s))
                        _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', 'DEFAULT'),]}
                        self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_SELECTIONBOX"].editSelectionListItem(itemKey = _processCode, item = _newSelectionBoxItem, columnIndex = 5)
        self.puVar['processesListUpdate_ItemsToUpdate'].clear()
        self.puVar['processesListUpdate_LastUpdated_ns'] = t_current_ns
#SETUP PAGE <PROCESS> END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#OBJECT FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateObjectFunctions(self):
    objFunctions = dict()

    #<Page Navigation>
    def __pageMove_DASHBOARD(objInstance, **kwargs): 
        self.sysFunctions['LOADPAGE']('DASHBOARD')
    objFunctions['PAGEMOVE_DASHBOARD'] = __pageMove_DASHBOARD

    #<Neural Network Manager>
    def __onStatusUpdate_NeuralNetworkManager_viewSwitch(objInstance, **kwargs):
        if (self.puVar['manager_viewType'] == objInstance.name): objInstance.setStatus(status = True, callStatusUpdateFunction = False)
        else:
            #General Cases
            for _objName in ("NEURALNETWORKMANAGER_VIEWNEURALNETWORKS",
                             "NEURALNETWORKMANAGER_VIEWPROCESSES"):
                if (self.GUIOs[_objName].name != objInstance.name): self.GUIOs[_objName].setStatus(status = False, callStatusUpdateFunction = False)
            for _guioName in self.puVar['manager_viewDependentGUIOs'][self.puVar['manager_viewType']]: self.GUIOs[_guioName].hide()
            for _guioName in self.puVar['manager_viewDependentGUIOs'][objInstance.name]:               self.GUIOs[_guioName].show()
            #Exceptional Cases
            if (objInstance.name == 'NEURALNETWORKS'):
                if (self.puVar['neuralNetwork_selected'] == None):
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMETEXTINPUTBOX"].show()
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPESELECTIONBOX"].show()
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMEDISPLAYTEXT"].hide()
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPEDISPLAYTEXT"].hide()
                else:
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMETEXTINPUTBOX"].hide()
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPESELECTIONBOX"].hide()
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMEDISPLAYTEXT"].show()
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPEDISPLAYTEXT"].show()
            self.puVar['manager_viewType'] = objInstance.name
    objFunctions['ONSTATUSUPDATE_NEURALNETWORKMANAGER_VIEWSWITCH'] = __onStatusUpdate_NeuralNetworkManager_viewSwitch
    #---Neural Networks
    def __onSelectionUpdate_NeuralNetworkManager_NeuralNetworks_NeuralNetworkSelection(objInstance, **kwargs):
        try:    _neuralNetwork_selected = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_SELECTIONBOX"].getSelected()[0]
        except: _neuralNetwork_selected = None
        self.puVar['neuralNetwork_selected'] = _neuralNetwork_selected
        self.pageAuxillaryFunctions['ONNEURALNETWORKSELECTIONUPDATE']()
        self.pageAuxillaryFunctions['CHECKIFCANRUNTRAINING']()
        self.pageAuxillaryFunctions['CHECKIFCANRUNPERFORMANCETEST']()
    def __onTextUpdate_NeuralNetworkManager_NeuralNetworks_NeuralNetworkCode(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANGENERATENEURALNETWORK']()
    def __onTextUpdate_NeuralNetworkManager_NeuralNetworks_ControlKey(objInstance, **kwargs):
        if (self.puVar['neuralNetwork_selected'] != None):
            _controlKey_entered = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].getText()
            _controlKey_textLen = len(_controlKey_entered)
            if (8 <= _controlKey_textLen): self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASESWITCH"].activate()
            else:                          self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASESWITCH"].deactivate()
            if ((self.puVar['neuralNetwork_selected'] != None) and (8 <= _controlKey_textLen)): self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"].activate()
            else:
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"].setStatus(status = False, callStatusUpdateFunction = True)
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"].deactivate()
        self.pageAuxillaryFunctions['CHECKIFCANGENERATENEURALNETWORK']()
        self.pageAuxillaryFunctions['CHECKIFCANRUNTRAINING']()
    def __onStatusUpdate_NeuralNetworkManager_NeuralNetworks_ControlKeyHoldRelease(objInstance, **kwargs):
        _switchStatus      = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASESWITCH"].getStatus()
        _neuralNetworkCode = self.puVar['neuralNetwork_selected']
        if (_switchStatus == True):
            self.puVar['neuralNetworks_controlKeys'][_neuralNetworkCode] = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].getText()
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].deactivate()
        else:
            del self.puVar['neuralNetworks_controlKeys'][_neuralNetworkCode]
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].activate()
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASESWITCH"].deactivate()
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"].setStatus(status = False, callStatusUpdateFunction = True)
            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"].deactivate()
        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].updateText(text = "")
    def __onSelectionUpdate_NeuralNetworkManager_NeuralNetworks_InitializationType(objInstance, **kwargs):
        _initType_selected = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONSELECTIONBOX"].getSelected()
        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONTEXTINPUTBOX"].updateText(text = self.puVar['initializationTypes'][_initType_selected])
    def __onTextUpdate_NeuralNetworkManager_NeuralNetworks_InitializationText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANINITIALIZENEURALNETWORK']()
    def __onButtonRelease_NeuralNetworkManager_NeuralNetworks_InitializeNeuralNetwork(objInstance, **kwargs):
        _neuralNetworkCode = self.puVar['neuralNetwork_selected']
        if (_neuralNetworkCode in self.puVar['neuralNetworks_controlKeys']): _controlKey = self.puVar['neuralNetworks_controlKeys'][_neuralNetworkCode]
        else:                                                                _controlKey = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].getText()
        _initialization = {'type':   self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONSELECTIONBOX"].getSelected(),
                           'params': json.loads(self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONTEXTINPUTBOX"].getText())}
        self.ipcA.sendFAR(targetProcess = 'NEURALNETWORKMANAGER',
                          functionID = 'initializeNeuralNetwork',
                          functionParams = {'neuralNetworkCode': _neuralNetworkCode,
                                            'initialization':    _initialization,
                                            'controlKey':        _controlKey},
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONNEURALNETWORKCONTROLREQUESTRESPONSE'])
        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONBUTTON"].deactivate()
    def __onButtonRelease_NeuralNetworkManager_NeuralNetworks_GenerateNeuralNetwork(objInstance, **kwargs):
        _neuralNetworkCode = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMETEXTINPUTBOX"].getText()
        _neuralNetworkType = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPESELECTIONBOX"].getSelected()
        _initialization = {'type':   self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONSELECTIONBOX"].getSelected(),
                           'params': json.loads(self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONTEXTINPUTBOX"].getText())}
        _nKlines      = int(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESTEXTINPUT"].getText())
        _hiddenLayers = json.loads(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSTEXTINPUT"].getText())
        _outputLayer  = json.loads(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERTEXTINPUT"].getText())
        _controlKey   = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].getText()
        #Send FAR to the Neural Network Manager
        self.ipcA.sendFAR(targetProcess = 'NEURALNETWORKMANAGER',
                          functionID = 'generateNeuralNetwork',
                          functionParams = {'neuralNetworkCode':  _neuralNetworkCode,
                                            'neuralNetworkType':  _neuralNetworkType,
                                            'initialization':     _initialization,
                                            'nKlines':            _nKlines,
                                            'hiddenLayers':       _hiddenLayers,
                                            'outputLayer':        _outputLayer,
                                            'controlKey':         _controlKey},
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONNEURALNETWORKCONTROLREQUESTRESPONSE'])
        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATENEURALNETWORKBUTTON"].deactivate()
    def __onButtonRelease_NeuralNetworkManager_NeuralNetworks_RemoveNeuralNetwork(objInstance, **kwargs):
        _neuralNetworkCode = self.puVar['neuralNetwork_selected']
        if (_neuralNetworkCode in self.puVar['neuralNetworks_controlKeys']): _controlKey = self.puVar['neuralNetworks_controlKeys'][_neuralNetworkCode]
        else:                                                                _controlKey = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].getText()
        self.ipcA.sendFAR(targetProcess = 'NEURALNETWORKMANAGER',
                          functionID = 'removeNeuralNetwork',
                          functionParams = {'neuralNetworkCode': _neuralNetworkCode,
                                            'controlKey':        _controlKey},
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONNEURALNETWORKCONTROLREQUESTRESPONSE'])
        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_REMOVENEURALNETWORKBUTTON"].deactivate()
    def __onStatusUpdate_NeuralNetworkManager_NeuralNetworks_ControlNeuralNetworkButtonSwitch(objInstance, **kwargs):
        _switchStatus = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"].getStatus()
        if (_switchStatus == True): self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_REMOVENEURALNETWORKBUTTON"].activate()
        else:                       self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_REMOVENEURALNETWORKBUTTON"].deactivate()
        self.pageAuxillaryFunctions['CHECKIFCANINITIALIZENEURALNETWORK']()
    objFunctions['ONSELECTIONUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKSELECTION']       = __onSelectionUpdate_NeuralNetworkManager_NeuralNetworks_NeuralNetworkSelection
    objFunctions['ONTEXTUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKCODE']                 = __onTextUpdate_NeuralNetworkManager_NeuralNetworks_NeuralNetworkCode
    objFunctions['ONTEXTUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEY']                        = __onTextUpdate_NeuralNetworkManager_NeuralNetworks_ControlKey
    objFunctions['ONSTATUSUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASE']           = __onStatusUpdate_NeuralNetworkManager_NeuralNetworks_ControlKeyHoldRelease
    objFunctions['ONSELECTIONUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONTYPE']           = __onSelectionUpdate_NeuralNetworkManager_NeuralNetworks_InitializationType
    objFunctions['ONTEXTUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONTEXT']                = __onTextUpdate_NeuralNetworkManager_NeuralNetworks_InitializationText
    objFunctions['ONBUTTONRELEASE_NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZENEURALNETWORK']        = __onButtonRelease_NeuralNetworkManager_NeuralNetworks_InitializeNeuralNetwork
    objFunctions['ONBUTTONRELEASE_NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATENEURALNETWORK']          = __onButtonRelease_NeuralNetworkManager_NeuralNetworks_GenerateNeuralNetwork
    objFunctions['ONBUTTONRELEASE_NEURALNETWORKMANAGER_NEURALNETWORKS_REMOVENEURALNETWORK']            = __onButtonRelease_NeuralNetworkManager_NeuralNetworks_RemoveNeuralNetwork
    objFunctions['ONSTATUSUPDATE_NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH'] = __onStatusUpdate_NeuralNetworkManager_NeuralNetworks_ControlNeuralNetworkButtonSwitch
    #---Processes
    def __onSelectionUpdate_NeuralNetworkManager_Processes_ProcessSelection(objInstance, **kwargs):
        try:    _process_selected = self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_SELECTIONBOX"].getSelected()[0]
        except: _process_selected = None
        self.puVar['process_selected'] = _process_selected
        self.pageAuxillaryFunctions['ONPROCESSSELECTIONUPDATE']()
    def __onTextUpdate_NeuralNetworkManager_Processes_ControlKey(objInstance, **kwargs):
        if (self.puVar['process_selected'] != None):
            _controlKey_entered = self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYTEXTINPUTBOX"].getText()
            _controlKey_textLen = len(_controlKey_entered)
            if (8 <= _controlKey_textLen): self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYHOLDRELEASESWITCH"].activate()
            else:                          self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYHOLDRELEASESWITCH"].deactivate()
            if ((self.puVar['process_selected'] != None) and (8 <= _controlKey_textLen)): self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH"].activate()
            else:
                self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH"].setStatus(status = False, callStatusUpdateFunction = True)
                self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH"].deactivate()
    def __onStatusUpdate_NeuralNetworkManager_Processes_ControlKeyHoldRelease(objInstance, **kwargs):
        _switchStatus = self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYHOLDRELEASESWITCH"].getStatus()
        if (_switchStatus == True):
            self.puVar['process_controlKey'] = self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYTEXTINPUTBOX"].getText()
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYTEXTINPUTBOX"].deactivate()
        else:
            self.puVar['process_controlKey'] = None
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYTEXTINPUTBOX"].activate()
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYHOLDRELEASESWITCH"].deactivate()
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH"].setStatus(status = False, callStatusUpdateFunction = True)
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH"].deactivate()
        self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYTEXTINPUTBOX"].updateText(text = "")
    def __onButtonRelease_NeuralNetworkManager_Processes_RemoveProcess(objInstance, **kwargs):
        _processCode = self.puVar['process_selected']
        if (self.puVar['process_controlKey'] == None): _controlKey = self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYTEXTINPUTBOX"].getText()
        else:                                          _controlKey = self.puVar['process_controlKey']
        self.ipcA.sendFAR(targetProcess = 'NEURALNETWORKMANAGER',
                          functionID = 'removeProcess',
                          functionParams = {'processCode': _processCode,
                                            'controlKey':  _controlKey},
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONPROCESSCONTROLREQUESTRESPONSE'])
        self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTON"].deactivate()
    def __onStatusUpdate_NeuralNetworkManager_Processes_RemoveProcessButtonSwitch(objInstance, **kwargs):
        _switchStatus = self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH"].getStatus()
        if   (_switchStatus == True): self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTON"].activate()
        else:                         self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTON"].deactivate()
    objFunctions['ONSELECTIONUPDATE_NEURALNETWORKMANAGER_PROCESSES_PROCESSSELECTION']       = __onSelectionUpdate_NeuralNetworkManager_Processes_ProcessSelection
    objFunctions['ONTEXTUPDATE_NEURALNETWORKMANAGER_PROCESSES_CONTROLKEY']                  = __onTextUpdate_NeuralNetworkManager_Processes_ControlKey
    objFunctions['ONSTATUSUPDATE_NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYHOLDRELEASE']     = __onStatusUpdate_NeuralNetworkManager_Processes_ControlKeyHoldRelease
    objFunctions['ONBUTTONRELEASE_NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESS']            = __onButtonRelease_NeuralNetworkManager_Processes_RemoveProcess
    objFunctions['ONSTATUSUPDATE_NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH'] = __onStatusUpdate_NeuralNetworkManager_Processes_RemoveProcessButtonSwitch

    #<Neural Network Control & Detail>
    def __onStatusUpdate_NeuralNetworkControlDetail_viewSwitch(objInstance, **kwargs):
        if (self.puVar['controlAndDetail_viewType'] == objInstance.name): objInstance.setStatus(status = True, callStatusUpdateFunction = False)
        else:
            #General Cases
            for _objName in ("NEURALNETWORKCONTROL&DETAIL_VIEWNETWORKSTRUCTURE",
                             "NEURALNETWORKCONTROL&DETAIL_VIEWTAP"):
                if (self.GUIOs[_objName].name != objInstance.name): self.GUIOs[_objName].setStatus(status = False, callStatusUpdateFunction = False)
            for _guioName in self.puVar['controlAndDetail_viewDependentGUIOs'][self.puVar['controlAndDetail_viewType']]: self.GUIOs[_guioName].hide()
            for _guioName in self.puVar['controlAndDetail_viewDependentGUIOs'][objInstance.name]:                        self.GUIOs[_guioName].show()
            #Exceptional Cases
            if (objInstance.name == 'NETWORKSTRUCTURE'):
                if (self.puVar['neuralNetwork_selected'] == None):
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESTEXTINPUT"].show()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERTEXTINPUT"].show()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSTEXTINPUT"].show()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESDISPLAYTEXT"].hide()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERDISPLAYTEXT"].hide()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSDISPLAYTEXT"].hide()
                else:
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESTEXTINPUT"].hide()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERTEXTINPUT"].hide()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSTEXTINPUT"].hide()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESDISPLAYTEXT"].show()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERDISPLAYTEXT"].show()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSDISPLAYTEXT"].show()
            self.puVar['controlAndDetail_viewType'] = objInstance.name
    objFunctions['ONSTATUSUPDATE_NEURALNETWORKCONTROL&DETAIL_VIEWSWITCH'] = __onStatusUpdate_NeuralNetworkControlDetail_viewSwitch
    #---Network Structure
    def __onTextUpdate_NeuralNetworkControlDetail_NetworkStructure_NKlinesText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANGENERATENEURALNETWORK']()
    def __onTextUpdate_NeuralNetworkControlDetail_NetworkStructure_HiddenLayersText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANGENERATENEURALNETWORK']()
    def __onTextUpdate_NeuralNetworkControlDetail_NetworkStructure_OutputLayerText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANGENERATENEURALNETWORK']()
    objFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESTEXT']      = __onTextUpdate_NeuralNetworkControlDetail_NetworkStructure_NKlinesText
    objFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSTEXT'] = __onTextUpdate_NeuralNetworkControlDetail_NetworkStructure_HiddenLayersText
    objFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERTEXT']  = __onTextUpdate_NeuralNetworkControlDetail_NetworkStructure_OutputLayerText
    #---TAP
    def __onTextUpdate_NeuralNetworkControlDetail_TAP_CurrecnySearchText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONCURRENCIESFILTERUPDATE']()
    def __onSelectionUpdate_NeuralNetworkControlDetail_TAP_CurrencySortByType(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONCURRENCIESFILTERUPDATE']()
    def __onSelectionUpdate_NeuralNetworkControlDetail_TAP_Currency(objInstance, **kwargs):
        try:    self.puVar['currency_selected'] = self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSELECTIONBOX"].getSelected()[0]
        except: self.puVar['currency_selected'] = None
        self.pageAuxillaryFunctions['ONCURRENCYSELECTION']()
    def __onTextUpdate_NeuralNetworkControlDetail_TAP_TargetDataRange(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANRUNTRAINING']()
        self.pageAuxillaryFunctions['CHECKIFCANRUNPERFORMANCETEST']()
    def __onSelectionUpdate_NeuralNetworkControlDetail_TAP_OptimizerType(objInstance, **kwargs):
        _optimizerType_selected = self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERSELECTIONBOX"].getSelected()
        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERINPUTTEXT"].updateText(text = self.puVar['optimizerTypes'][_optimizerType_selected])
    def __onTextUpdate_NeuralNetworkControlDetail_TAP_Optimizer(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANRUNTRAINING']()
    def __onSelectionUpdate_NeuralNetworkControlDetail_TAP_LossFunctionType(objInstance, **kwargs):
        _lossFunctionType_selected = self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONSELECTIONBOX"].getSelected()
        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONINPUTTEXT"].updateText(text = self.puVar['lossFunctionTypes'][_lossFunctionType_selected])
    def __onTextUpdate_NeuralNetworkControlDetail_TAP_LossFunction(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANRUNTRAINING']()
        self.pageAuxillaryFunctions['CHECKIFCANRUNPERFORMANCETEST']()
    def __onTextUpdate_NeuralNetworkControlDetail_TAP_NEpochs(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANRUNTRAINING']()
    def __onTextUpdate_NeuralNetworkControlDetail_TAP_BatchSize(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANRUNTRAINING']()
    def __onTextUpdate_NeuralNetworkControlDetail_TAP_LearningRate(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANRUNTRAINING']()
    def __onTextUpdate_NeuralNetworkControlDetail_TAP_SwingRange(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANRUNTRAINING']()
        self.pageAuxillaryFunctions['CHECKIFCANRUNPERFORMANCETEST']()
    def __onButtonRelease_NeuralNetworkControlDetail_TAP_RunTraining(objInstance, **kwargs):
        _neuralNetworkCode = self.puVar['neuralNetwork_selected']
        if (_neuralNetworkCode in self.puVar['neuralNetworks_controlKeys']): _controlKey = self.puVar['neuralNetworks_controlKeys'][_neuralNetworkCode]
        else:                                                                _controlKey = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].getText()
        _targetCurrencySymbol = self.puVar['currency_selected']
        _targetRange          = (datetime.strptime(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGEINPUTTEXT1"].getText(), "%Y/%m/%d %H:%M").timestamp()-time.timezone,
                                 datetime.strptime(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGEINPUTTEXT2"].getText(), "%Y/%m/%d %H:%M").timestamp()-time.timezone)
        _optimizer = {'type':   self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERSELECTIONBOX"].getSelected(),
                      'params': json.loads(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERINPUTTEXT"].getText())}
        _lossFunction = {'type':   self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONSELECTIONBOX"].getSelected(),
                         'params': json.loads(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONINPUTTEXT"].getText())}
        _nEpochs      = int(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_NEPOCHSINPUTTEXT"].getText())
        _batchSize    = int(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_BATCHSIZEINPUTTEXT"].getText())
        _learningRate = round(float(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LEARNINGRATEINPUTTEXT"].getText()), 6)
        _swingRange   = round(float(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_SWINGRANGEINPUTTEXT"].getText()),   4)
        #Send FAR to the Neural Network Manager
        self.ipcA.sendFAR(targetProcess = 'NEURALNETWORKMANAGER',
                          functionID = 'runTraining',
                          functionParams = {'neuralNetworkCode':    _neuralNetworkCode,
                                            'controlKey':           _controlKey,
                                            'targetCurrencySymbol': _targetCurrencySymbol,
                                            'targetRange':          _targetRange,
                                            'optimizer':            _optimizer,
                                            'lossFunction':         _lossFunction,
                                            'nEpochs':              _nEpochs,
                                            'batchSize':            _batchSize,
                                            'learningRate':         _learningRate,
                                            'swingRange':           _swingRange},
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONNEURALNETWORKCONTROLREQUESTRESPONSE'])
        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_RUNTRAININGBUTTON"].deactivate()
    def __onButtonRelease_NeuralNetworkControlDetail_TAP_RunPerformanceTest(objInstance, **kwargs):
        _neuralNetworkCode = self.puVar['neuralNetwork_selected']
        _targetCurrencySymbol = self.puVar['currency_selected']
        _targetRange = (datetime.strptime(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGEINPUTTEXT1"].getText(), "%Y/%m/%d %H:%M").timestamp()-time.timezone,
                        datetime.strptime(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGEINPUTTEXT2"].getText(), "%Y/%m/%d %H:%M").timestamp()-time.timezone)
        _lossFunction = {'type':   self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONSELECTIONBOX"].getSelected(),
                         'params': json.loads(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONINPUTTEXT"].getText())}
        _swingRange = round(float(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_SWINGRANGEINPUTTEXT"].getText()), 4)
        #Send FAR to the Neural Network Manager
        self.ipcA.sendFAR(targetProcess = 'NEURALNETWORKMANAGER',
                          functionID = 'runPerformanceTest',
                          functionParams = {'neuralNetworkCode':    _neuralNetworkCode,
                                            'targetCurrencySymbol': _targetCurrencySymbol,
                                            'targetRange':          _targetRange,
                                            'lossFunction':         _lossFunction,
                                            'swingRange':           _swingRange},
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONNEURALNETWORKCONTROLREQUESTRESPONSE'])
        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_RUNPERFORMANCETESTBUTTON"].deactivate()
    objFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSEARCHTEXT']      = __onTextUpdate_NeuralNetworkControlDetail_TAP_CurrecnySearchText
    objFunctions['ONSELECTIONUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSORTBYTYPE'] = __onSelectionUpdate_NeuralNetworkControlDetail_TAP_CurrencySortByType
    objFunctions['ONSELECTIONUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCY']           = __onSelectionUpdate_NeuralNetworkControlDetail_TAP_Currency
    objFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGE']         = __onTextUpdate_NeuralNetworkControlDetail_TAP_TargetDataRange
    objFunctions['ONSELECTIONUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERTYPE']      = __onSelectionUpdate_NeuralNetworkControlDetail_TAP_OptimizerType
    objFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZER']               = __onTextUpdate_NeuralNetworkControlDetail_TAP_Optimizer
    objFunctions['ONSELECTIONUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONTYPE']   = __onSelectionUpdate_NeuralNetworkControlDetail_TAP_LossFunctionType
    objFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTION']            = __onTextUpdate_NeuralNetworkControlDetail_TAP_LossFunction
    objFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_NEPOCHS']                 = __onTextUpdate_NeuralNetworkControlDetail_TAP_NEpochs
    objFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_BATCHSIZE']               = __onTextUpdate_NeuralNetworkControlDetail_TAP_BatchSize
    objFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_LEARNINGRATE']            = __onTextUpdate_NeuralNetworkControlDetail_TAP_LearningRate
    objFunctions['ONTEXTUPDATE_NEURALNETWORKCONTROL&DETAIL_TAP_SWINGRANGE']              = __onTextUpdate_NeuralNetworkControlDetail_TAP_SwingRange
    objFunctions['ONBUTTONRELEASE_NEURALNETWORKCONTROL&DETAIL_TAP_RUNTRAINING']          = __onButtonRelease_NeuralNetworkControlDetail_TAP_RunTraining
    objFunctions['ONBUTTONRELEASE_NEURALNETWORKCONTROL&DETAIL_TAP_RUNPERFORMANCETEST']   = __onButtonRelease_NeuralNetworkControlDetail_TAP_RunPerformanceTest

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()
    
    #<_PAGELOAD>
    def __far_onNeuralNetworkUpdate(requester, updateType, updatedContent):
        if (requester == 'NEURALNETWORKMANAGER'):
            if (updateType == 'ADDED'):
                _neuralNetworkCode = updatedContent
                self.puVar['neuralNetworks'][_neuralNetworkCode] = self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = ('NEURALNETWORKS', _neuralNetworkCode))
                self.pageAuxillaryFunctions['SETNEURALNETWORKSLIST']()
            elif (updateType == 'REMOVED'):
                _neuralNetworkCode = updatedContent
                self.pageAuxillaryFunctions['SETNEURALNETWORKSLIST']()
                if (_neuralNetworkCode == self.puVar['neuralNetwork_selected']):
                    #[1]: Account Information & Control
                    self.puVar['neuralNetwork_selected'] = None
                    self.pageAuxillaryFunctions['ONNEURALNETWORKSELECTIONUPDATE']()
                    if (_neuralNetworkCode in self.puVar['neuralNetworks_controlKeys']): del self.puVar['neuralNetworks_controlKeys'][_neuralNetworkCode]
            elif (updateType == 'STATUS'):
                _neuralNetworkCode = updatedContent
                if (_neuralNetworkCode == self.puVar['neuralNetwork_selected']):
                    _status = self.puVar['neuralNetworks'][_neuralNetworkCode]['status']
                    if   (_status == 'STANDBY'):  _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_STANDBY');  _textColor_status = 'GREEN_LIGHT' 
                    elif (_status == 'QUEUED'):   _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_QUEUED');   _textColor_status = 'BLUE'
                    elif (_status == 'TRAINING'): _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_TRAINING'); _textColor_status = 'BLUE_LIGHT'
                    elif (_status == 'TESTING'):  _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_TESTING');  _textColor_status = 'BLUE_LIGHT'
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_STATUSDISPLAYTEXT"].updateText(text = _text_status, textStyle = _textColor_status)
                if (_neuralNetworkCode in self.puVar['neuralNetworksListUpdate_ItemsToUpdate']): self.puVar['neuralNetworksListUpdate_ItemsToUpdate'][_neuralNetworkCode].add('status')
                else:                                                                            self.puVar['neuralNetworksListUpdate_ItemsToUpdate'][_neuralNetworkCode] = {'status',}
            elif (updateType == 'COMPLETION'):
                _neuralNetworkCode = updatedContent
                if (_neuralNetworkCode == self.puVar['neuralNetwork_selected']):
                    _completion       = self.puVar['neuralNetworks'][_neuralNetworkCode]['completion']
                    _completion_ETC_s = self.puVar['neuralNetworks'][_neuralNetworkCode]['completion_ETC_s']
                    if (_completion == None): 
                        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = 0)
                        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONDISPLAYTEXT"].updateText(text = "-")
                    else:                                      
                        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = _completion*100)
                        if (_completion_ETC_s == None): self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONDISPLAYTEXT"].updateText(text = "{:.3f} %".format(_completion*100))
                        else:                           self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONDISPLAYTEXT"].updateText(text = "{:.3f} % [{:s}]".format(_completion*100, atmEta_Auxillaries.timeStringFormatter(time_seconds = int(_completion_ETC_s))))
            elif (updateType == 'TRAININGLOG'):
                _neuralNetworkCode = updatedContent[0]
                _log               = updatedContent[1]
                self.puVar['neuralNetworks'][_neuralNetworkCode]['trainingLogs'].append(_log)
                if (_neuralNetworkCode == self.puVar['neuralNetwork_selected']): self.pageAuxillaryFunctions['SETTRAININGLOGLIST']()
            elif (updateType == 'PERFORMANCETESTLOG'):
                _neuralNetworkCode = updatedContent[0]
                _log               = updatedContent[1]
                self.puVar['neuralNetworks'][_neuralNetworkCode]['performanceTestLogs'].append(_log)
                if (_neuralNetworkCode == self.puVar['neuralNetwork_selected']): self.pageAuxillaryFunctions['SETPERFORMANCETESTLOGLIST']()
    def __far_onProcessUpdate(requester, updateType, updatedContent):
        if (requester == 'NEURALNETWORKMANAGER'):
            if (updateType == 'ADDED'):
                _processCode = updatedContent
                self.puVar['processes'][_processCode] = self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = ('PROCESSES', _processCode))
                self.pageAuxillaryFunctions['SETPROCESSESLIST']()
            elif (updateType == 'REMOVED'): 
                _processCode = updatedContent
                self.pageAuxillaryFunctions['SETPROCESSESLIST']()
                if (_processCode == self.puVar['process_selected']):
                    #[1]: Account Information & Control
                    self.puVar['process_selected'] = None
                    self.pageAuxillaryFunctions['ONPROCESSSELECTIONUPDATE']()
            elif (updateType == 'STATUS'): 
                _processCode = updatedContent
                if (_processCode == self.puVar['process_selected']):
                    _status = self.puVar['processes'][_processCode]['status']
                    if   (_status == 'QUEUED'):        _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_QUEUED');        _textColor_status = 'BLUE_LIGHT';   _gaugeBarColor = (0,   0,   0)
                    elif (_status == 'PREPARING'):     _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PREPARING');     _textColor_status = 'ORANGE_LIGHT'; _gaugeBarColor = (0,   0,   0)
                    elif (_status == 'PREPROCESSING'): _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PREPROCESSING'); _textColor_status = 'CYAN_LIGHT';   _gaugeBarColor = (0, 230, 230)
                    elif (_status == 'PROCESSING'):    _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PROCESSING');    _textColor_status = 'GREEN_LIGHT';  _gaugeBarColor = (0, 200,  30)
                    self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_STATUSDISPLAYTEXT"].updateText(text = _text_status, textStyle = _textColor_status)
                    self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONGAUGEBAR"].updateGaugeColor(rValue = _gaugeBarColor[0], gValue = _gaugeBarColor[1], bValue = _gaugeBarColor[2])
                if (_processCode in self.puVar['processesListUpdate_ItemsToUpdate']): self.puVar['processesListUpdate_ItemsToUpdate'][_processCode].add('status')
                else:                                                                 self.puVar['processesListUpdate_ItemsToUpdate'][_processCode] = {'status',}
            elif (updateType == 'COMPLETION'):
                _processCode = updatedContent
                if (_processCode == self.puVar['process_selected']):
                    if (_processCode in self.puVar['processes']):
                        _completion       = self.puVar['processes'][_processCode]['completion']
                        _completion_ETC_s = self.puVar['processes'][_processCode]['completion_ETC_s']
                        if (_completion == None):
                            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = 0)
                            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONDISPLAYTEXT"].updateText(text = "-")
                        else:                                      
                            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = _completion*100)
                            if (_completion_ETC_s == None): self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONDISPLAYTEXT"].updateText(text = "{:.3f} %".format(_completion*100))
                            else:                           self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONDISPLAYTEXT"].updateText(text = "{:.3f} % [{:s}]".format(_completion*100, atmEta_Auxillaries.timeStringFormatter(time_seconds = int(_completion_ETC_s))))
                    else: 
                        self.puVar['process_selected'] = None
                        self.pageAuxillaryFunctions['ONPROCESSSELECTIONUPDATE']()
                if (_processCode in self.puVar['processesListUpdate_ItemsToUpdate']): self.puVar['processesListUpdate_ItemsToUpdate'][_processCode].add('completion')
                else:                                                                 self.puVar['processesListUpdate_ItemsToUpdate'][_processCode] = {'completion',}
    def __far_onCurrenciesUpdate(requester, updatedContents):
        if (requester == 'DATAMANAGER'):
            for updatedContent in updatedContents:
                symbol    = updatedContent['symbol']
                contentID = updatedContent['id']
                #A new currency is added
                if (contentID == '_ADDED'):
                    self.puVar['currencies'][symbol] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol))
                    self.pageAuxillaryFunctions['SETCURRENCIESLIST']()
                else:
                    #Selected currency info update if needed & check if the currency list item needs an update
                    _updated_status          = False
                    _updated_firstKline      = False
                    _updated_availableRanges = False
                    #---[1]: Currency Server Information Updated
                    if (contentID[0] == 'info_server'): 
                        try:    contentID_1 = contentID[1]
                        except: contentID_1 = None
                        #---[1]: Entire Server Information Updated
                        if (contentID_1 == None):
                            self.puVar['currencies'][symbol]['info_server'] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server'))
                            _updated_status = True
                        #---[2]: Currency Status Updated
                        else:
                            if (contentID_1 == 'status'):
                                self.puVar['currencies'][symbol]['info_server']['status'] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server', 'status'))
                                _updated_status = True
                    #---[2]: KlineFirstOpenTS Updated
                    elif (contentID[0] == 'kline_firstOpenTS'):
                        self.puVar['currencies'][symbol]['kline_firstOpenTS'] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'kline_firstOpenTS'))
                        _updated_firstKline = True
                    #---[3]: KlineAvailableRanges Updated
                    elif (contentID[0] == 'kline_availableRanges'):
                        self.puVar['currencies'][symbol]['kline_availableRanges'] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'kline_availableRanges'))
                        _updated_availableRanges = False
                    #Update the currency list item
                    if (_updated_status == True):
                        if (self.puVar['currencies'][symbol]['info_server'] == None): _currencyStatus = None
                        else:                                                         _currencyStatus = self.puVar['currencies'][symbol]['info_server']['status']
                        if   (_currencyStatus == 'TRADING'):  _text = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_STATUS_TRADING');  _text_color = 'GREEN_LIGHT'
                        elif (_currencyStatus == 'SETTLING'): _text = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_STATUS_SETTLING'); _text_color = 'RED_LIGHT'
                        elif (_currencyStatus == 'REMOVED'):  _text = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_STATUS_REMOVED');  _text_color = 'RED_DARK'
                        elif (_currencyStatus == None):       _text = '-';                                                                                             _text_color = 'BLUE_DARK'
                        else:                                 _text = _currencyStatus;                                                                                 _text_color = 'VIOLET'
                        _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _text_color),]}
                        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSELECTIONBOX"].editSelectionListItem(itemKey = symbol, item = _newSelectionBoxItem, columnIndex = 2)
                        if (self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSORTBYSELECTIONBOX"].getSelected() == 'STATUS'): self.pageAuxillaryFunctions['ONCURRENCIESFILTERUPDATE']()
                    if (_updated_firstKline == True):
                        _firstKline = self.puVar['currencies'][symbol]['kline_firstOpenTS']
                        if (_firstKline == None): _text = "-"
                        else:                     _text = datetime.fromtimestamp(_firstKline, tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
                        _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', 'DEFAULT'),]}
                        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSELECTIONBOX"].editSelectionListItem(itemKey = symbol, item = _newSelectionBoxItem, columnIndex = 3)
                        if (self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSORTBYSELECTIONBOX"].getSelected() == 'FIRSTKLINE'): self.pageAuxillaryFunctions['ONCURRENCIESFILTERUPDATE']()
                    if (_updated_availableRanges == True):
                        if (symbol == self.puVar['currency_selected']): 
                            _dataRanges = self.puVar['currencies'][symbol]['kline_availableRanges']
                            if (_dataRanges == None): _text = "-"
                            else:        
                                _nAvailableRanges = len(_dataRanges)
                                if (_nAvailableRanges == 1): _text = "{:s} ~ {:s}".format(datetime.fromtimestamp(_dataRanges[0][0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(_dataRanges[0][1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
                                else:
                                    _text = ""
                                    for _dataRange in _dataRanges: _text += "({:s} ~ {:s})".format(datetime.fromtimestamp(_dataRange[0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(_dataRange[1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
                            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_DATARANGESDISPLAYTEXT"].updateText(text = _text)
    auxFunctions['_FAR_ONNEURALNETWORKUPDATE'] = __far_onNeuralNetworkUpdate
    auxFunctions['_FAR_ONPROCESSUPDATE']       = __far_onProcessUpdate
    auxFunctions['_FAR_ONCURRENCIESUPDATE']    = __far_onCurrenciesUpdate

    #<Neural Network Manager>
    #---Neural Networks
    def __setNeuralNetworksList():
        neuralNetworks_selectionList = dict()
        for _nnIndex, _nnCode in enumerate(self.puVar['neuralNetworks']):
            _neuralNetwork = self.puVar['neuralNetworks'][_nnCode]
            #Display Table Formatting
            _status = _neuralNetwork['status']
            if   (_status == 'STANDBY'):  _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_STANDBY');  _textColor_status = 'GREEN_LIGHT' 
            elif (_status == 'QUEUED'):   _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_QUEUED');   _textColor_status = 'BLUE'
            elif (_status == 'TRAINING'): _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_TRAINING'); _textColor_status = 'BLUE_LIGHT'
            elif (_status == 'TESTING'):  _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_TESTING');  _textColor_status = 'BLUE_LIGHT'
            neuralNetworks_selectionList[_nnCode] = [{'text': str(_nnIndex), 'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                                     {'text': _nnCode,       'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                                     {'text': _text_status,  'textStyles': [('all', _textColor_status),], 'textAnchor': 'CENTER'}]
        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_SELECTIONBOX"].setSelectionList(selectionList = neuralNetworks_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = False)
    def __onNeuralNetworkSelectionUpdate():
        if (self.puVar['neuralNetwork_selected'] == None):
            #Neural Networks List
            if (True):
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMETEXTINPUTBOX"].show()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMEDISPLAYTEXT"].hide()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPESELECTIONBOX"].show()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPEDISPLAYTEXT"].hide()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].updateText(text = "")
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].activate()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASESWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASESWITCH"].deactivate()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATIONTIMEDISPLAYTEXT"].updateText(text = "-")
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_STATUSDISPLAYTEXT"].updateText(text = "-")
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = 0)
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONDISPLAYTEXT"].updateText(text = "-")
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONBUTTON"].deactivate()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_REMOVENEURALNETWORKBUTTON"].deactivate()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"].deactivate()
                self.pageAuxillaryFunctions['CHECKIFCANGENERATENEURALNETWORK']()
            #Control & Detail
            if (True):
                if (self.puVar['controlAndDetail_viewType'] == 'NETWORKSTRUCTURE'):
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESTEXTINPUT"].show()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERTEXTINPUT"].show()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSTEXTINPUT"].show()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESDISPLAYTEXT"].hide()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERDISPLAYTEXT"].hide()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSDISPLAYTEXT"].hide()
        else:
            _neuralNetwork = self.puVar['neuralNetworks'][self.puVar['neuralNetwork_selected']]
            #Neural Networks List
            if (True):
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMETEXTINPUTBOX"].hide()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMEDISPLAYTEXT"].show()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMEDISPLAYTEXT"].updateText(text = self.puVar['neuralNetwork_selected'])
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPESELECTIONBOX"].hide()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPEDISPLAYTEXT"].show()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKTYPEDISPLAYTEXT"].updateText(text = _neuralNetwork['type'])
                if (self.puVar['neuralNetwork_selected'] in self.puVar['neuralNetworks_controlKeys']):
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].updateText(text = "")
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].deactivate()
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASESWITCH"].activate()
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASESWITCH"].setStatus(status = True, callStatusUpdateFunction = False)
                else:
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].updateText(text = "")
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].activate()
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASESWITCH"].deactivate()
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYHOLDRELEASESWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATIONTIMEDISPLAYTEXT"].updateText(text = datetime.fromtimestamp(_neuralNetwork['generationTime'], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
                _status = _neuralNetwork['status']
                if   (_status == 'STANDBY'):  _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_STANDBY');  _textColor_status = 'GREEN_LIGHT' 
                elif (_status == 'QUEUED'):   _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_QUEUED');   _textColor_status = 'BLUE'
                elif (_status == 'TRAINING'): _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_TRAINING'); _textColor_status = 'BLUE_LIGHT'
                elif (_status == 'TESTING'):  _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_NEURALNETWORKS_STATUS_TESTING');  _textColor_status = 'BLUE_LIGHT'
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_STATUSDISPLAYTEXT"].updateText(text = _text_status, textStyle = _textColor_status)
                if (_neuralNetwork['completion'] == None):
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = 0)
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONDISPLAYTEXT"].updateText(text = "-")
                else:
                    self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = _neuralNetwork['completion']*100)
                    if (_neuralNetwork['completion_ETC_s'] == None): self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONDISPLAYTEXT"].updateText(text = "{:.3f} %".format(_neuralNetwork['completion']*100))
                    else:                                            self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_COMPLETIONDISPLAYTEXT"].updateText(text = "{:.3f} % [{:s}]".format(_neuralNetwork['completion']*100, atmEta_Auxillaries.timeStringFormatter(time_seconds = int(_neuralNetwork['completion_ETC_s']))))
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATENEURALNETWORKBUTTON"].deactivate()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONBUTTON"].deactivate()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_REMOVENEURALNETWORKBUTTON"].deactivate()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                if ((self.puVar['neuralNetwork_selected'] in self.puVar['neuralNetworks_controlKeys']) or (8 <= len(self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].getText()))): self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"].activate()
                else:                                                                                                                                                                                      self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"].deactivate()
            #Control & Detail
            if (True):
                if (self.puVar['controlAndDetail_viewType'] == 'NETWORKSTRUCTURE'):
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESTEXTINPUT"].hide()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERTEXTINPUT"].hide()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSTEXTINPUT"].hide()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESDISPLAYTEXT"].show()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERDISPLAYTEXT"].show()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSDISPLAYTEXT"].show()
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESDISPLAYTEXT"].updateText(text = "{:d}".format(_neuralNetwork['nKlines']))
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERDISPLAYTEXT"].updateText(text  = str(_neuralNetwork['outputLayer']))
                    self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSDISPLAYTEXT"].updateText(text = str(_neuralNetwork['hiddenLayers']))
        self.pageAuxillaryFunctions['SETTRAININGLOGLIST']()
        self.pageAuxillaryFunctions['SETPERFORMANCETESTLOGLIST']()
        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NEURALNETWORKVIEWER"].setTarget(neuralNetworkCode = self.puVar['neuralNetwork_selected'])
    def __checkIfCanInitializeNeuralNetwork():
        _controlSwitchStatus = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLNEURALNETWORKBUTTONSWITCH"].getStatus()
        _textTest = False
        try:
            _initializationText = json.loads(self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONTEXTINPUTBOX"].getText())
            _textTest = True
        except: pass
        if ((_controlSwitchStatus == True) and (_textTest == True)): self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONBUTTON"].activate()
        else:                                                        self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONBUTTON"].deactivate()
    def __checkIfCanGenerateNeuralNetwork():
        #[1]: Neural Network Code Test
        _neuralNetworkCode_entered = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMETEXTINPUTBOX"].getText()
        if ((0 < len(_neuralNetworkCode_entered)) and (_neuralNetworkCode_entered not in self.puVar['neuralNetworks'])): _test_neuralNetworks = True
        else:                                                                                                            _test_neuralNetworks = False
        #[2]: Control key Test
        _controlKey_entered = self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].getText()
        if (8 <= len(_controlKey_entered)): _test_controlKey = True
        else:                               _test_controlKey = False
        #[3]: Initialization
        try:
            _initialization_params = json.loads(self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_INITIALIZATIONTEXTINPUTBOX"].getText())
            _test_initialization = True
        except: _test_initialization = False

        #[3]: nKlines
        _nKlines_str = self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_NKLINESTEXTINPUT"].getText()
        try:
            _nKlines = int(_nKlines_str)
            if (0 < _nKlines): _test_nKlines = True
            else:              _test_nKlines = False
        except: _test_nKlines = False
        #[4]: Hidden Layers
        _hiddenLayers_str = self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_HIDDENLAYERSTEXTINPUT"].getText()
        try:
            _hiddenLayers = json.loads(_hiddenLayers_str)
            if (0 < len(_hiddenLayers)):
                _test_hiddenLayers = True
                for _hiddenLayer in _hiddenLayers:
                    if (type(_hiddenLayer) != dict): _test_hiddenLayers = False; break
            else: _test_hiddenLayers = False
        except: _test_hiddenLayers = False
        #[5]: Output Layer
        _outputLayer_str = self.GUIOs["NEURALNETWORKCONTROL&DETAIL_NETWORKSTRUCTURE_OUTPUTLAYERTEXTINPUT"].getText()
        try:
            _outputLayer = json.loads(_outputLayer_str)
            if (type(_outputLayer) == dict): _test_outputLayer = True
            else:                            _test_outputLayer = False
        except: _test_outputLayer = False
        #Finally
        _testPassed = ((_test_neuralNetworks == True) and (_test_controlKey == True) and (_test_initialization == True) and (_test_nKlines == True) and (_test_hiddenLayers == True) and (_test_outputLayer == True))
        if (_testPassed == True): self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATENEURALNETWORKBUTTON"].activate()
        else:                     self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATENEURALNETWORKBUTTON"].deactivate()
    def __farr_onNeuralNetworkControlRequestResponse(responder, requestID, functionResult):
        neuralNetworkCode           = functionResult['neuralNetworkCode']
        responseOn                  = functionResult['responseOn']
        requestResult               = functionResult['result']
        neuralNetworkManagerMessage = functionResult['message']
        if (responseOn == 'GENERATENEURALNETWORKREQUEST'):
            if (requestResult == True):
                self.puVar['neuralNetwork_selected'] = neuralNetworkCode
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_SELECTIONBOX"].addSelected(itemKey = neuralNetworkCode, callSelectionUpdateFunction = False)
                self.pageAuxillaryFunctions['ONNEURALNETWORKSELECTIONUPDATE']()
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_NEURALNETWORKNAMETEXTINPUTBOX"].updateText(text = "")
                self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = neuralNetworkManagerMessage, textStyle = 'GREEN_LIGHT')
            else:                       
                self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_GENERATENEURALNETWORKBUTTON"].activate()
                self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = neuralNetworkManagerMessage, textStyle = 'RED_LIGHT')
        elif (responseOn == 'REMOVENEURALNETWORKREQUEST'):
            if (requestResult == True): self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = neuralNetworkManagerMessage, textStyle = 'ORANGE_LIGHT')
            else:                       
                if (neuralNetworkCode == self.puVar['neuralNetwork_selected']): self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_REMOVENEURALNETWORKBUTTON"].activate()
                self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = neuralNetworkManagerMessage, textStyle = 'RED_LIGHT')
        elif (responseOn == 'RUNTRAININGREQUEST'):
            if (neuralNetworkCode == self.puVar['neuralNetwork_selected']): self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_RUNTRAININGBUTTON"].activate()
            if (requestResult == True): self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = neuralNetworkManagerMessage, textStyle = 'GREEN_LIGHT')
            else:                       self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = neuralNetworkManagerMessage, textStyle = 'RED_LIGHT')
        elif (responseOn == 'RUNPERFORMANCETESTREQUEST'):
            if (neuralNetworkCode == self.puVar['neuralNetwork_selected']): self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_RUNPERFORMANCETESTBUTTON"].activate()
            if (requestResult == True): self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = neuralNetworkManagerMessage, textStyle = 'GREEN_LIGHT')
            else:                       self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = neuralNetworkManagerMessage, textStyle = 'RED_LIGHT')
        elif (responseOn == 'INITIALIZENEURALNETWORKREQUEST'):
            if (neuralNetworkCode == self.puVar['neuralNetwork_selected']): self.pageAuxillaryFunctions['CHECKIFCANINITIALIZENEURALNETWORK']()
            if (requestResult == True): self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = neuralNetworkManagerMessage, textStyle = 'GREEN_LIGHT')
            else:                       self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = neuralNetworkManagerMessage, textStyle = 'RED_LIGHT')
    auxFunctions['SETNEURALNETWORKSLIST']                       = __setNeuralNetworksList
    auxFunctions['ONNEURALNETWORKSELECTIONUPDATE']              = __onNeuralNetworkSelectionUpdate
    auxFunctions['CHECKIFCANINITIALIZENEURALNETWORK']           = __checkIfCanInitializeNeuralNetwork
    auxFunctions['CHECKIFCANGENERATENEURALNETWORK']             = __checkIfCanGenerateNeuralNetwork
    auxFunctions['_FARR_ONNEURALNETWORKCONTROLREQUESTRESPONSE'] = __farr_onNeuralNetworkControlRequestResponse
    #---Processes
    def __setProcessesList():
        processes_selectionList = dict()
        _nProcesses = len(self.puVar['processes'])
        for _pIndex, _pCode in enumerate(self.puVar['processes']):
            _process = self.puVar['processes'][_pCode]
            #Display Table Formatting
            #[1]: Index
            _text_index = "{:d} / {:d}".format(_pIndex+1, _nProcesses)
            #[2]: Network Code
            _text_networkCode = _process['neuralNetworkCode']
            #[3]: Type
            if   (_process['processType'] == 'TRAINING'):        _text_type = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_TYPE_TRAINING')
            elif (_process['processType'] == 'PERFORMANCETEST'): _text_type = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_TYPE_PERFORMANCETEST')
            #[4]: Status
            if   (_process['status'] == 'QUEUED'):        _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_QUEUED');        _textColor_status = 'BLUE_LIGHT'
            elif (_process['status'] == 'PREPARING'):     _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PREPARING');     _textColor_status = 'ORANGE_LIGHT'
            elif (_process['status'] == 'PREPROCESSING'): _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PREPROCESSING'); _textColor_status = 'CYAN_LIGHT'
            elif (_process['status'] == 'PROCESSING'):    _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PROCESSING');    _textColor_status = 'GREEN_LIGHT'
            #[5]: Completion
            if (_process['completion'] == None): _text_completion = "-"
            else:                                _text_completion = "{:.3f} %".format(_process['completion']*100)
            #[6]: ETC
            if (_process['completion_ETC_s'] == None): _text_ETC = "-"
            else:                                      _text_ETC = atmEta_Auxillaries.timeStringFormatter(time_seconds = int(_process['completion_ETC_s']))
            #[7]: Target
            _text_target = _process['targetCurrencySymbol']
            #[8]: Target Range
            _text_targetRange = "{:s} ~ {:s}".format(datetime.fromtimestamp(_process['targetRange'][0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(_process['targetRange'][1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
            #[9]: Iterations
            if (_process['processType'] == 'TRAINING'): _text_nEpochs = "{:d}".format(_process['nEpochs'])
            else:                                       _text_nEpochs = "-"
            #[10]: Learning Batch
            if (_process['processType'] == 'TRAINING'): _text_batchSize = "{:d}".format(_process['batchSize'])
            else:                                       _text_batchSize = "-"
            #[11]: Learning Rate
            if (_process['processType'] == 'TRAINING'): _text_learningRate = "{:.6f}".format(_process['learningRate'])
            else:                                       _text_learningRate = "-"
            #[12]: Swing Range
            _text_swingRange = "{:.4f}".format(_process['swingRange'])
            processes_selectionList[_pCode] = [{'text': _text_index,         'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                               {'text': _text_networkCode,   'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                               {'text': _text_type,          'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                               {'text': _text_status,        'textStyles': [('all', _textColor_status),], 'textAnchor': 'CENTER'},
                                               {'text': _text_completion,    'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                               {'text': _text_ETC,           'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                               {'text': _text_target,        'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                               {'text': _text_targetRange,   'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                               {'text': _text_nEpochs,       'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                               {'text': _text_batchSize,     'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                               {'text': _text_learningRate,  'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                               {'text': _text_swingRange,    'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'}]
        self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_SELECTIONBOX"].setSelectionList(selectionList = processes_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = False)
    def __onProcessSelectionUpdate():
        if (self.puVar['process_selected'] == None):
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_STATUSDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = 0)
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTON"].deactivate()
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH"].deactivate()
        else:
            _process = self.puVar['processes'][self.puVar['process_selected']]
            if   (_process['status'] == 'QUEUED'):        _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_QUEUED');        _textColor_status = 'BLUE_LIGHT';   _gaugeBarColor = (0,   0,   0)
            elif (_process['status'] == 'PREPARING'):     _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PREPARING');     _textColor_status = 'ORANGE_LIGHT'; _gaugeBarColor = (0,   0,   0)
            elif (_process['status'] == 'PREPROCESSING'): _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PREPROCESSING'); _textColor_status = 'CYAN_LIGHT';   _gaugeBarColor = (0, 230, 230)
            elif (_process['status'] == 'PROCESSING'):    _text_status = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKMANAGER_PROCESSES_STATUS_PROCESSING');    _textColor_status = 'GREEN_LIGHT';  _gaugeBarColor = (0, 200,  30)
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_STATUSDISPLAYTEXT"].updateText(text = _text_status, textStyle = _textColor_status)
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONGAUGEBAR"].updateGaugeColor(rValue = _gaugeBarColor[0], gValue = _gaugeBarColor[1], bValue = _gaugeBarColor[2])
            if (_process['completion'] == None):
                self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = 0)
                self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONDISPLAYTEXT"].updateText(text = "-")
            else:
                self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONGAUGEBAR"].updateGaugeValue(gaugeValue = _process['completion']*100)
                if (_process['completion_ETC_s'] == None): self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONDISPLAYTEXT"].updateText(text = "{:.3f} %".format(_process['completion']*100))
                else:                                      self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_COMPLETIONDISPLAYTEXT"].updateText(text = "{:.3f} % [{:s}]".format(_process['completion']*100, atmEta_Auxillaries.timeStringFormatter(time_seconds = int(_process['completion_ETC_s']))))
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTON"].deactivate()
            self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
            if ((self.puVar['process_controlKey'] != None) or (8 <= len(self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_CONTROLKEYTEXTINPUTBOX"].getText()))): self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH"].activate()
            else:                                                                                                                                         self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTONSWITCH"].deactivate()
    def __farr_onProcessControlRequestResponse(responder, requestID, functionResult):
        processCode                 = functionResult['processCode']
        responseOn                  = functionResult['responseOn']
        requestResult               = functionResult['result']
        neuralNetworkManagerMessage = functionResult['message']
        if (responseOn == 'REMOVEPROCESSREQUEST'):
            if (requestResult == True): self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = neuralNetworkManagerMessage, textStyle = 'ORANGE_LIGHT')
            else:
                if (processCode == self.puVar['process_selected']): self.GUIOs["NEURALNETWORKMANAGER_PROCESSES_REMOVEPROCESSBUTTON"].activate()
                self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = neuralNetworkManagerMessage, textStyle = 'RED_LIGHT')
    auxFunctions['SETPROCESSESLIST']                      = __setProcessesList
    auxFunctions['ONPROCESSSELECTIONUPDATE']              = __onProcessSelectionUpdate
    auxFunctions['_FARR_ONPROCESSCONTROLREQUESTRESPONSE'] = __farr_onProcessControlRequestResponse

    #<Neural Network Control & Detail>
    #---Network Structure
    #---TAP
    def __onCurrenciesFilterUpdate():
        _currencies = self.puVar['currencies']
        #Localize filter settings
        _filter_symbol   = self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSEARCHTEXTINPUT"].getText()
        _filter_sortType = self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSORTBYSELECTIONBOX"].getSelected()
        #Filtering
        if (_filter_symbol == ""): _symbols_filtered = list(_currencies.keys())
        else:                      _symbols_filtered = [_symbol for _symbol in _currencies if _filter_symbol in _symbol]
        #Sorting
        if (_filter_sortType == 'INDEX'):
            _symbols_forSort = [(_symbol, _currencies[_symbol]['currencyID']) for _symbol in _symbols_filtered]
            _symbols_forSort.sort(key = lambda x: x[1], reverse = False)
        elif (_filter_sortType == 'SYMBOL'):
            _symbols_forSort = [(_symbol,) for _symbol in _symbols_filtered]
            _symbols_forSort.sort(reverse = False)
        elif (_filter_sortType == 'STATUS'):
            _symbols_forSort = list()
            for _symbol in _symbols_filtered:
                _currency = _currencies[_symbol]
                if (_currency['info_server'] == None): _status = None
                else:                                  _status = _currency['info_server']['status']
                if   (_status == 'TRADING'):  _symbols_forSort.append((_symbol, 0))
                elif (_status == 'SETTLING'): _symbols_forSort.append((_symbol, 1))
                elif (_status == 'REMOVED'):  _symbols_forSort.append((_symbol, 2))
                elif (_status == None):       _symbols_forSort.append((_symbol, 3))
            _symbols_forSort.sort(key = lambda x: x[1], reverse = False)
        elif (_filter_sortType == 'FIRSTKLINE'):
            _symbols_forSort = list()
            for _symbol in _symbols_filtered:
                _currency = _currencies[_symbol]
                if (_currency['kline_firstOpenTS'] == None): _symbols_forSort.append((_symbol, float('inf')))
                else:                                        _symbols_forSort.append((_symbol, _currency['kline_firstOpenTS']))
            _symbols_forSort.sort(key = lambda x: x[1], reverse = False)
        #Finally
        _symbols_filteredAndSorted = [_sortPair[0] for _sortPair in _symbols_forSort]
        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSELECTIONBOX"].setDisplayTargets(displayTargets = _symbols_filteredAndSorted, resetViewPosition = False)
    def __setCurrenciesList():
        _currencies  = self.puVar['currencies']
        _nCurrencies = len(_currencies)
        _currencies_selectionList = dict()
        for _index, _symbol in enumerate(_currencies):
            _currency = _currencies[_symbol]
            #[0]:  Index
            _index_str = "{:d} / {:d}".format(_index+1, _nCurrencies)
            #[1]:  Symbol
            _symbol_str = _symbol
            #[2]: Market Status
            _serverInfo = _currency['info_server']
            if (_serverInfo == None): _currencyStatus = None
            else:                     _currencyStatus = _serverInfo['status']
            if   (_currencyStatus == 'TRADING'):  _marketStatus_str = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_STATUS_TRADING');  _marketStatus_str_color = 'GREEN_LIGHT'
            elif (_currencyStatus == 'SETTLING'): _marketStatus_str = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_STATUS_SETTLING'); _marketStatus_str_color = 'RED_LIGHT'
            elif (_currencyStatus == 'REMOVED'):  _marketStatus_str = self.visualManager.getTextPack('NEURALNETWORK:NEURALNETWORKCONTROL&DETAIL_TAP_STATUS_REMOVED');  _marketStatus_str_color = 'RED_DARK'
            elif (_currencyStatus == None):       _marketStatus_str = '-';                                                                                                     _marketStatus_str_color = 'BLUE_DARK'
            else:                                 _marketStatus_str = _currencyStatus;                                                                                         _marketStatus_str_color = 'VIOLET'
            #[3]: First Kline
            if (_currency['kline_firstOpenTS'] == None): _firstKline_str = "-"
            else:                                        _firstKline_str = datetime.fromtimestamp(_currency['kline_firstOpenTS'], tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
            #Finally
            _currencies_selectionList[_symbol] = [{'text': _index_str},
                                                  {'text': _symbol_str},
                                                  {'text': _marketStatus_str, 'textStyles': [('all', _marketStatus_str_color),]},
                                                  {'text': _firstKline_str}]
        self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSELECTIONBOX"].setSelectionList(selectionList = _currencies_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = True)
        self.pageAuxillaryFunctions['ONCURRENCIESFILTERUPDATE']()
    def __onCurrencySelection():
        _currencySymbol_selected = self.puVar['currency_selected']
        if (self.puVar['currency_selected'] == None):
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSYMBOLDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_DATARANGESDISPLAYTEXT"].updateText(text     = "-")
        else:
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_CURRENCYSYMBOLDISPLAYTEXT"].updateText(text = _currencySymbol_selected)
            _dataRanges = self.puVar['currencies'][_currencySymbol_selected]['kline_availableRanges']
            if (_dataRanges == None): _dataRanges_str = "-"
            else:        
                _nAvailableRanges = len(_dataRanges)
                if (_nAvailableRanges == 1): _dataRanges_str = "{:s} ~ {:s}".format(datetime.fromtimestamp(_dataRanges[0][0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(_dataRanges[0][1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
                else:
                    _dataRanges_str = ""
                    for _dataRange in _dataRanges: _dataRanges_str += "({:s} ~ {:s})".format(datetime.fromtimestamp(_dataRange[0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(_dataRange[1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_DATARANGESDISPLAYTEXT"].updateText(text = _dataRanges_str)
        self.pageAuxillaryFunctions['CHECKIFCANRUNTRAINING']()
        self.pageAuxillaryFunctions['CHECKIFCANRUNPERFORMANCETEST']()
    def __checkIfCanRunTraining():
        _canRun = False
        if ((self.puVar['neuralNetwork_selected'] != None) and (self.puVar['currency_selected'] != None)):
            #Password Check
            _test_password = (self.puVar['neuralNetwork_selected'] in self.puVar['neuralNetworks_controlKeys']) or (8 <= len(self.GUIOs["NEURALNETWORKMANAGER_NEURALNETWORKS_CONTROLKEYTEXTINPUTBOX"].getText()))
            #Data Ranges Check
            _test_dataRanges = False
            _dataRanges = self.puVar['currencies'][self.puVar['currency_selected']]['kline_availableRanges']
            if (_dataRanges != None):
                try:
                    _targetDataRange = (datetime.strptime(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGEINPUTTEXT1"].getText(), "%Y/%m/%d %H:%M").timestamp()-time.timezone,
                                        datetime.strptime(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGEINPUTTEXT2"].getText(), "%Y/%m/%d %H:%M").timestamp()-time.timezone)
                    if (_targetDataRange[0] < _targetDataRange[1]):
                        for _dataRange in _dataRanges:
                            if ((_dataRange[0] <= _targetDataRange[0]) and (_targetDataRange[1] <= _dataRange[1])): _test_dataRanges = True; break
                except: pass
            #Optimizer Check
            _test_optimizer = False
            try:
                _optimizerParams = json.loads(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_OPTIMIZERINPUTTEXT"].getText())
                _test_optimizer = True
            except: pass
            #Loss Function Check
            _test_lossFunction = False
            try:
                _lossFunctionParams = json.loads(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONINPUTTEXT"].getText())
                _test_lossFunction = True
            except: pass
            #nEpochs Check
            _test_nEpochs = False
            try:
                _nEpochs = int(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_NEPOCHSINPUTTEXT"].getText())
                if (0 < _nEpochs): _test_nEpochs = True
            except: pass
            #Batch Size Check
            _test_batchSize = False
            try:
                _batchSize = int(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_BATCHSIZEINPUTTEXT"].getText())
                if (0 < _batchSize): _test_batchSize = True
            except: pass
            #Learning Rate Check
            _test_learningRate = False
            try:
                _learningRate = float(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LEARNINGRATEINPUTTEXT"].getText())
                if ((1e-6 < _learningRate) and (_learningRate <= 1)): _test_learningRate = True
            except: pass
            #Swing Range 0 Check
            _test_swingRange = False
            try:
                _swingRange = float(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_SWINGRANGEINPUTTEXT"].getText())
                if ((0.0010 <= _swingRange) and (_swingRange <= 0.0500)): _test_swingRange = True
            except: pass
            #Finally
            _canRun = ((_test_password == True) and (_test_dataRanges == True) and (_test_optimizer == True) and (_test_lossFunction == True) and (_test_nEpochs == True) and (_test_batchSize == True) and (_test_learningRate == True) and (_test_swingRange == True))
        if (_canRun == True): self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_RUNTRAININGBUTTON"].activate()
        else:                 self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_RUNTRAININGBUTTON"].deactivate()
    def __checkIfCanRunPerformanceTest():
        _canRun = False
        if ((self.puVar['neuralNetwork_selected'] != None) and (self.puVar['currency_selected'] != None)):
            #Data Ranges Check
            _test_dataRanges = False
            _dataRanges = self.puVar['currencies'][self.puVar['currency_selected']]['kline_availableRanges']
            if (_dataRanges != None):
                try:
                    _targetDataRange = (datetime.strptime(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGEINPUTTEXT1"].getText(), "%Y/%m/%d %H:%M").timestamp()-time.timezone,
                                        datetime.strptime(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TARGETDATARANGEINPUTTEXT2"].getText(), "%Y/%m/%d %H:%M").timestamp()-time.timezone)
                    if (_targetDataRange[0] < _targetDataRange[1]):
                        for _dataRange in _dataRanges:
                            if ((_dataRange[0] <= _targetDataRange[0]) and (_targetDataRange[1] <= _dataRange[1])): _test_dataRanges = True; break
                except: pass
            #Loss Function Check
            _test_lossFunction = False
            try:
                _lossFunctionParams = json.loads(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_LOSSFUNCTIONINPUTTEXT"].getText())
                _test_lossFunction = True
            except: pass
            #Swing Range Check
            _test_swingRange = False
            try:
                _swingRange = float(self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_SWINGRANGEINPUTTEXT"].getText())
                if ((0.0010 <= _swingRange) and (_swingRange <= 0.0500)): _test_swingRange = True
            except: pass
            #Finally
            _canRun = ((_test_dataRanges == True) and (_test_lossFunction == True) and (_test_swingRange == True))
        if (_canRun == True): self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_RUNPERFORMANCETESTBUTTON"].activate()
        else:                 self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_RUNPERFORMANCETESTBUTTON"].deactivate()
    def __setTrainingLogList():
        if (self.puVar['neuralNetwork_selected'] == None): self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TRAININGLOGSELECTIONBOX"].clearSelectionList(callSelectionUpdateFunction = False)
        else:
            _neuralNetwork = self.puVar['neuralNetworks'][self.puVar['neuralNetwork_selected']]
            _trainingLogs_selectionList = dict()
            _nLogs = len(_neuralNetwork['trainingLogs'])
            for _logIndex, _log in enumerate(_neuralNetwork['trainingLogs']):
                _text_log          = "{:d} / {:d}".format(_logIndex+1, _nLogs)
                _text_startTime    = datetime.fromtimestamp(_log['startTime']).strftime("%Y/%m/%d %H:%M:%S")
                _text_targetSymbol = _log['target']
                _text_targetRange  = "{:s} ~ {:s}".format(datetime.fromtimestamp(_log['targetRange'][0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(_log['targetRange'][1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
                _text_loss         = "{:.15f}".format(_log['lossAverage'])
                _trainingLogs_selectionList[_logIndex] = [{'text': _text_log,          'textStyles': [('all', 'DEFAULT'),], 'textAnchor': 'CENTER'},
                                                          {'text': _text_startTime,    'textStyles': [('all', 'DEFAULT'),], 'textAnchor': 'CENTER'},
                                                          {'text': _text_targetSymbol, 'textStyles': [('all', 'DEFAULT'),], 'textAnchor': 'CENTER'},
                                                          {'text': _text_targetRange,  'textStyles': [('all', 'DEFAULT'),], 'textAnchor': 'CENTER'},
                                                          {'text': _text_loss,         'textStyles': [('all', 'DEFAULT'),], 'textAnchor': 'CENTER'}]
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_TRAININGLOGSELECTIONBOX"].setSelectionList(selectionList = _trainingLogs_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = False)
    def __setPerformanceTestLogList():
        if (self.puVar['neuralNetwork_selected'] == None): self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_PERFORMANCETESTLOGSELECTIONBOX"].clearSelectionList(callSelectionUpdateFunction = False)
        else:
            _neuralNetwork = self.puVar['neuralNetworks'][self.puVar['neuralNetwork_selected']]
            _performanceTestLogs_selectionList = dict()
            _nLogs = len(_neuralNetwork['performanceTestLogs'])
            for _logIndex, _log in enumerate(_neuralNetwork['performanceTestLogs']):
                _text_log          = "{:d} / {:d}".format(_logIndex+1, _nLogs)
                _text_startTime    = datetime.fromtimestamp(_log['startTime']).strftime("%Y/%m/%d %H:%M:%S")
                _text_targetSymbol = _log['target']
                _text_targetRange  = "{:s} ~ {:s}".format(datetime.fromtimestamp(_log['targetRange'][0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(_log['targetRange'][1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
                _text_loss         = "{:.15f}".format(_log['lossAverage'])
                _performanceTestLogs_selectionList[_logIndex] = [{'text': _text_log,          'textStyles': [('all', 'DEFAULT'),], 'textAnchor': 'CENTER'},
                                                                 {'text': _text_startTime,    'textStyles': [('all', 'DEFAULT'),], 'textAnchor': 'CENTER'},
                                                                 {'text': _text_targetSymbol, 'textStyles': [('all', 'DEFAULT'),], 'textAnchor': 'CENTER'},
                                                                 {'text': _text_targetRange,  'textStyles': [('all', 'DEFAULT'),], 'textAnchor': 'CENTER'},
                                                                 {'text': _text_loss,         'textStyles': [('all', 'DEFAULT'),], 'textAnchor': 'CENTER'}]
            self.GUIOs["NEURALNETWORKCONTROL&DETAIL_TAP_PERFORMANCETESTLOGSELECTIONBOX"].setSelectionList(selectionList = _performanceTestLogs_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = False)
    auxFunctions['ONCURRENCIESFILTERUPDATE']      = __onCurrenciesFilterUpdate
    auxFunctions['SETCURRENCIESLIST']             = __setCurrenciesList
    auxFunctions['ONCURRENCYSELECTION']           = __onCurrencySelection
    auxFunctions['CHECKIFCANRUNTRAINING']         = __checkIfCanRunTraining
    auxFunctions['CHECKIFCANRUNPERFORMANCETEST']  = __checkIfCanRunPerformanceTest
    auxFunctions['SETTRAININGLOGLIST']            = __setTrainingLogList
    auxFunctions['SETPERFORMANCETESTLOGLIST']     = __setPerformanceTestLogList

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------