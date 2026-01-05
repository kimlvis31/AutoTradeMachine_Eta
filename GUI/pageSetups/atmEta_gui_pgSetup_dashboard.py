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
from GUI.atmEta_gui_ChartDrawer         import chartDrawer
from GUI.atmEta_gui_DailyReportViewer   import dailyReportViewer
from GUI.atmEta_gui_HourlyReportViewer  import hourlyReportViewer
from GUI.atmEta_gui_NeuralNetworkViewer import neuralNetworkViewer

#Python Modules
import pyglet
import pprint
import termcolor
import time
import random
from datetime import datetime, timezone, tzinfo

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
    pass

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
        
        self.GUIOs["TITLETEXT_DASHBOARD"] = textBox_typeA(**inst, groupOrder=1, xPos= 7000, yPos=8550, width=2000, height=400, style=None, text=self.visualManager.getTextPack('DASHBOARD:TITLE'), fontSize = 220, textInteractable = False)

        self.GUIOs["BUTTON_MOVETO_SETTINGS"]  = button_typeB(**inst, groupOrder=2, xPos=   50, yPos=8650, width=300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['PAGEMOVE_SETTINGS'], image = 'settingsIcon_512x512.png',         imageSize = (250, 250), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        self.GUIOs["BUTTON_TERMINATEPROGRAM"] = button_typeB(**inst, groupOrder=2, xPos=15650, yPos=8650, width=300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['TERMINATEPROGRAM'],  image = 'programTerminateIcon_512x512.png', imageSize = (250, 250), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        
        self.GUIOs["TEXT_MOVETO_ACCOUNTS"]   = textBox_typeA(**inst, groupOrder=1, xPos=4200, yPos=4550, width=1600, height= 250, style=None, text=self.visualManager.getTextPack('ACCOUNTS:TITLE'), fontSize = 100, textInteractable = False); self.GUIOs["TEXT_MOVETO_ACCOUNTS"].hide()
        self.GUIOs["BUTTON_MOVETO_ACCOUNTS"] = button_typeB(**inst,  groupOrder=2, xPos=4200, yPos=4800, width=1600, height=1600, style="styleB",
                                                            releaseFunction=self.pageObjectFunctions['PAGEMOVE_ACCOUNTS'], hoverFunction = self.pageObjectFunctions['SHOWNAVTEXT_ACCOUNTS'], hoverEscapeFunction = self.pageObjectFunctions['HIDENAVTEXT_ACCOUNTS'],
                                                            image = 'accountsIcon_512x512.png', imageSize = (1300, 1300), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        self.GUIOs["TEXT_MOVETO_AUTOTRADE"]   = textBox_typeA(**inst, groupOrder=1, xPos=6200, yPos=4550, width=1600, height= 250, style=None, text=self.visualManager.getTextPack('AUTOTRADE:TITLE'), fontSize = 100, textInteractable = False); self.GUIOs["TEXT_MOVETO_AUTOTRADE"].hide()
        self.GUIOs["BUTTON_MOVETO_AUTOTRADE"] = button_typeB(**inst,  groupOrder=2, xPos=6200, yPos=4800, width=1600, height=1600, style="styleB",
                                                             releaseFunction=self.pageObjectFunctions['PAGEMOVE_AUTOTRADE'], hoverFunction = self.pageObjectFunctions['SHOWNAVTEXT_AUTOTRADE'], hoverEscapeFunction = self.pageObjectFunctions['HIDENAVTEXT_AUTOTRADE'],
                                                             image = 'autotradeIcon_512x512.png', imageSize = (1400, 1400), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        self.GUIOs["TEXT_MOVETO_CURRENCYANALYSIS"]   = textBox_typeA(**inst, groupOrder=1, xPos=8200, yPos=4550, width=1600, height= 250, style=None, text=self.visualManager.getTextPack('CURRENCYANALYSIS:TITLE'), fontSize = 100, textInteractable = False); self.GUIOs["TEXT_MOVETO_CURRENCYANALYSIS"].hide()
        self.GUIOs["BUTTON_MOVETO_CURRENCYANALYSIS"] = button_typeB(**inst,  groupOrder=2, xPos=8200, yPos=4800, width=1600, height=1600, style="styleB",
                                                                    releaseFunction=self.pageObjectFunctions['PAGEMOVE_CURRENCYANALYSIS'], hoverFunction = self.pageObjectFunctions['SHOWNAVTEXT_CURRENCYANALYSIS'], hoverEscapeFunction = self.pageObjectFunctions['HIDENAVTEXT_CURRENCYANALYSIS'],
                                                                    image = 'currencyAnalysisIcon_512x512.png', imageSize = (1400, 1400), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        self.GUIOs["TEXT_MOVETO_ACCOUNTHISTORY"]   = textBox_typeA(**inst, groupOrder=1, xPos=10200, yPos=4550, width=1600, height= 250, style=None, text=self.visualManager.getTextPack('ACCOUNTHISTORY:TITLE'), fontSize = 100, textInteractable = False); self.GUIOs["TEXT_MOVETO_ACCOUNTHISTORY"].hide()
        self.GUIOs["BUTTON_MOVETO_ACCOUNTHISTORY"] = button_typeB(**inst,  groupOrder=2, xPos=10200, yPos=4800, width=1600, height=1600, style="styleB",
                                                                  releaseFunction=self.pageObjectFunctions['PAGEMOVE_ACCOUNTHISTORY'], hoverFunction = self.pageObjectFunctions['SHOWNAVTEXT_ACCOUNTHISTORY'], hoverEscapeFunction = self.pageObjectFunctions['HIDENAVTEXT_ACCOUNTHISTORY'],
                                                                  image = 'accountHistoryIcon_512x512.png', imageSize = (1400, 1400), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        self.GUIOs["TEXT_MOVETO_MARKET"]   = textBox_typeA(**inst, groupOrder=1, xPos=4200, yPos=2550, width=1600, height= 250, style=None, text=self.visualManager.getTextPack('MARKET:TITLE'), fontSize = 100, textInteractable = False); self.GUIOs["TEXT_MOVETO_MARKET"].hide()
        self.GUIOs["BUTTON_MOVETO_MARKET"] = button_typeB(**inst,  groupOrder=2, xPos=4200, yPos=2800, width=1600, height=1600, style="styleB",
                                                          releaseFunction=self.pageObjectFunctions['PAGEMOVE_MARKET'], hoverFunction = self.pageObjectFunctions['SHOWNAVTEXT_MARKET'], hoverEscapeFunction = self.pageObjectFunctions['HIDENAVTEXT_MARKET'],
                                                          image = 'marketIcon_512x512.png', imageSize = (1300, 1300), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        self.GUIOs["TEXT_MOVETO_SIMULATION"]   = textBox_typeA(**inst, groupOrder=1, xPos=6200, yPos=2550, width=1600, height= 250, style=None, text=self.visualManager.getTextPack('SIMULATION:TITLE'), fontSize = 100, textInteractable = False); self.GUIOs["TEXT_MOVETO_SIMULATION"].hide()
        self.GUIOs["BUTTON_MOVETO_SIMULATION"] = button_typeB(**inst,  groupOrder=2, xPos=6200, yPos=2800, width=1600, height=1600, style="styleB",
                                                              releaseFunction=self.pageObjectFunctions['PAGEMOVE_SIMULATION'], hoverFunction = self.pageObjectFunctions['SHOWNAVTEXT_SIMULATION'], hoverEscapeFunction = self.pageObjectFunctions['HIDENAVTEXT_SIMULATION'],
                                                              image = 'simulationIcon_512x512.png', imageSize = (1400, 1400), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        self.GUIOs["TEXT_MOVETO_SIMULATIONRESULT"]   = textBox_typeA(**inst, groupOrder=1, xPos=8200, yPos=2550, width=1600, height= 250, style=None, text=self.visualManager.getTextPack('SIMULATIONRESULT:TITLE'), fontSize = 100, textInteractable = False); self.GUIOs["TEXT_MOVETO_SIMULATIONRESULT"].hide()
        self.GUIOs["BUTTON_MOVETO_SIMULATIONRESULT"] = button_typeB(**inst,  groupOrder=2, xPos=8200, yPos=2800, width=1600, height=1600, style="styleB",
                                                                    releaseFunction=self.pageObjectFunctions['PAGEMOVE_SIMULATIONRESULT'], hoverFunction = self.pageObjectFunctions['SHOWNAVTEXT_SIMULATIONRESULT'], hoverEscapeFunction = self.pageObjectFunctions['HIDENAVTEXT_SIMULATIONRESULT'],
                                                                    image = 'simulationResultIcon_512x512.png', imageSize = (1400, 1400), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        self.GUIOs["TEXT_MOVETO_NEURALNETWORK"]   = textBox_typeA(**inst, groupOrder=1, xPos=10200, yPos=2550, width=1600, height= 250, style=None, text=self.visualManager.getTextPack('NEURALNETWORK:TITLE'), fontSize = 100, textInteractable = False); self.GUIOs["TEXT_MOVETO_NEURALNETWORK"].hide()
        self.GUIOs["BUTTON_MOVETO_NEURALNETWORK"] = button_typeB(**inst,  groupOrder=2, xPos=10200, yPos=2800, width=1600, height=1600, style="styleB",
                                                                 releaseFunction=self.pageObjectFunctions['PAGEMOVE_NEURALNETWORK'], hoverFunction = self.pageObjectFunctions['SHOWNAVTEXT_NEURALNETWORK'], hoverEscapeFunction = self.pageObjectFunctions['HIDENAVTEXT_NEURALNETWORK'],
                                                                 image = 'neuralNetworkIcon_512x512.png', imageSize = (1350, 1350), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))

    elif (self.displaySpaceDefiner['ratio'] == '21:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 21000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
    elif (self.displaySpaceDefiner['ratio'] == '32:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 32000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
#SETUP PAGE <MAIN> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <LOAD> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageLoadFunction(self):
    pass
#SETUP PAGE <LOAD> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <ESCAPE> --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageEscapeFunction(self):
    pass
#SETUP PAGE <ESCAPE> END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <PROCESS> -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageProcessFunction(self, t_elapsed_ns, onLoad = False):
    pass
#SETUP PAGE <PROCESS> END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#OBJECT FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateObjectFunctions(self):
    objFunctions = dict()

    #<Page Navigation>
    def __pageMove_SETTINGS(objInstance, **kwargs):         
        self.sysFunctions['LOADPAGE']('SETTINGS')
    def __pageMove_ACCOUNTS(objInstance, **kwargs):         
        self.sysFunctions['LOADPAGE']('ACCOUNTS')
    def __pageMove_MARKET(objInstance, **kwargs):           
        self.sysFunctions['LOADPAGE']('MARKET')
    def __pageMove_AUTOTRADE(objInstance, **kwargs):        
        self.sysFunctions['LOADPAGE']('AUTOTRADE')
    def __pageMove_CURRENCYANALYSIS(objInstance, **kwargs): 
        self.sysFunctions['LOADPAGE']('CURRENCYANALYSIS')
    def __pageMove_SIMULATION(objInstance, **kwargs):       
        self.sysFunctions['LOADPAGE']('SIMULATION')
    def __pageMove_SIMULATIONRESULT(objInstance, **kwargs): 
        self.sysFunctions['LOADPAGE']('SIMULATIONRESULT')
    def __pageMove_ACCOUNTHISTORY(objInstance, **kwargs):   
        self.sysFunctions['LOADPAGE']('ACCOUNTHISTORY')
    def __pageMove_NEURALNETWORK(objInstance, **kwargs):        
        self.sysFunctions['LOADPAGE']('NEURALNETWORK')
    def __show_NavText_ACCOUNTS(objInstance, **kwargs):         
        self.GUIOs["TEXT_MOVETO_ACCOUNTS"].show()
    def __hide_NavText_ACCOUNTS(objInstance, **kwargs):         
        self.GUIOs["TEXT_MOVETO_ACCOUNTS"].hide()
    def __show_NavText_MARKET(objInstance, **kwargs):           
        self.GUIOs["TEXT_MOVETO_MARKET"].show()
    def __hide_NavText_MARKET(objInstance, **kwargs):           
        self.GUIOs["TEXT_MOVETO_MARKET"].hide()
    def __show_NavText_AUTOTRADE(objInstance, **kwargs):        
        self.GUIOs["TEXT_MOVETO_AUTOTRADE"].show()
    def __hide_NavText_AUTOTRADE(objInstance, **kwargs):        
        self.GUIOs["TEXT_MOVETO_AUTOTRADE"].hide()
    def __show_NavText_CURRENCYANALYSIS(objInstance, **kwargs): 
        self.GUIOs["TEXT_MOVETO_CURRENCYANALYSIS"].show()
    def __hide_NavText_CURRENCYANALYSIS(objInstance, **kwargs): 
        self.GUIOs["TEXT_MOVETO_CURRENCYANALYSIS"].hide()
    def __show_NavText_SIMULATION(objInstance, **kwargs):       
        self.GUIOs["TEXT_MOVETO_SIMULATION"].show()
    def __hide_NavText_SIMULATION(objInstance, **kwargs):       
        self.GUIOs["TEXT_MOVETO_SIMULATION"].hide()
    def __show_NavText_SIMULATIONRESULT(objInstance, **kwargs): 
        self.GUIOs["TEXT_MOVETO_SIMULATIONRESULT"].show()
    def __hide_NavText_SIMULATIONRESULT(objInstance, **kwargs): 
        self.GUIOs["TEXT_MOVETO_SIMULATIONRESULT"].hide()
    def __show_NavText_ACCOUNTHISTORY(objInstance, **kwargs):   
        self.GUIOs["TEXT_MOVETO_ACCOUNTHISTORY"].show()
    def __hide_NavText_ACCOUNTHISTORY(objInstance, **kwargs):   
        self.GUIOs["TEXT_MOVETO_ACCOUNTHISTORY"].hide()
    def __show_NavText_NEURALNETWORK(objInstance, **kwargs):    
        self.GUIOs["TEXT_MOVETO_NEURALNETWORK"].show()
    def __hide_NavText_NEURALNETWORK(objInstance, **kwargs):    
        self.GUIOs["TEXT_MOVETO_NEURALNETWORK"].hide()
    objFunctions['PAGEMOVE_SETTINGS']         = __pageMove_SETTINGS
    objFunctions['PAGEMOVE_ACCOUNTS']         = __pageMove_ACCOUNTS
    objFunctions['PAGEMOVE_MARKET']           = __pageMove_MARKET
    objFunctions['PAGEMOVE_AUTOTRADE']        = __pageMove_AUTOTRADE
    objFunctions['PAGEMOVE_CURRENCYANALYSIS'] = __pageMove_CURRENCYANALYSIS
    objFunctions['PAGEMOVE_SIMULATION']       = __pageMove_SIMULATION
    objFunctions['PAGEMOVE_SIMULATIONRESULT'] = __pageMove_SIMULATIONRESULT
    objFunctions['PAGEMOVE_ACCOUNTHISTORY']   = __pageMove_ACCOUNTHISTORY
    objFunctions['PAGEMOVE_NEURALNETWORK']    = __pageMove_NEURALNETWORK
    objFunctions['SHOWNAVTEXT_ACCOUNTS']         = __show_NavText_ACCOUNTS
    objFunctions['HIDENAVTEXT_ACCOUNTS']         = __hide_NavText_ACCOUNTS
    objFunctions['SHOWNAVTEXT_MARKET']           = __show_NavText_MARKET
    objFunctions['HIDENAVTEXT_MARKET']           = __hide_NavText_MARKET
    objFunctions['SHOWNAVTEXT_AUTOTRADE']        = __show_NavText_AUTOTRADE
    objFunctions['HIDENAVTEXT_AUTOTRADE']        = __hide_NavText_AUTOTRADE
    objFunctions['SHOWNAVTEXT_CURRENCYANALYSIS'] = __show_NavText_CURRENCYANALYSIS
    objFunctions['HIDENAVTEXT_CURRENCYANALYSIS'] = __hide_NavText_CURRENCYANALYSIS
    objFunctions['SHOWNAVTEXT_SIMULATION']       = __show_NavText_SIMULATION
    objFunctions['HIDENAVTEXT_SIMULATION']       = __hide_NavText_SIMULATION
    objFunctions['SHOWNAVTEXT_SIMULATIONRESULT'] = __show_NavText_SIMULATIONRESULT
    objFunctions['HIDENAVTEXT_SIMULATIONRESULT'] = __hide_NavText_SIMULATIONRESULT
    objFunctions['SHOWNAVTEXT_ACCOUNTHISTORY']   = __show_NavText_ACCOUNTHISTORY
    objFunctions['HIDENAVTEXT_ACCOUNTHISTORY']   = __hide_NavText_ACCOUNTHISTORY
    objFunctions['SHOWNAVTEXT_NEURALNETWORK']    = __show_NavText_NEURALNETWORK
    objFunctions['HIDENAVTEXT_NEURALNETWORK']    = __hide_NavText_NEURALNETWORK

    #<Program Control>
    def __terminateProgram(objInstance, **kwargs): 
        self.sysFunctions['TERMINATEPROGRAM']()
    objFunctions['TERMINATEPROGRAM'] = __terminateProgram

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------