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
        self.GUIOs["TITLETEXT_DASHBOARD"] = textBox_typeA(**inst, groupOrder=1, xPos=7000, yPos=8550, width=2000, height=400, style=None, text=self.visualManager.getTextPack('SETTINGS:TITLE'), fontSize = 220, textInteractable = False)
        
        self.GUIOs["BUTTON_MOVETO_DASHBOARD"] = button_typeB(**inst,  groupOrder=2, xPos=  50, yPos=8650, width= 300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['PAGEMOVE_DASHBOARD'], image = 'dashboardIcon_512x512.png', imageSize = (225, 225), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))

        #[1]: Graphics Menu
        self.GUIOs["GRAPHICSCONTROL_WRAPPER"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=8350, width=9800, height=200, style="styleA", text=self.visualManager.getTextPack('SETTINGS:GRAPHICSWRAPPERTITLE'), fontSize = 80)
        #---Audio Play Switch
        self.GUIOs["GRAPHICSCONTROL_TEXT_FULLSCREEN"]   = textBox_typeA(**inst, groupOrder=2, xPos= 100, yPos=8000, width=2000, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:FULLSCREEN'), fontSize=80)
        self.GUIOs["GRAPHICSCONTROL_SWITCH_FULLSCREEN"] = switch_typeB(**inst,  groupOrder=2, xPos=2200, yPos=8000, width= 500, height= 250, style="styleA", align='horizontal', switchStatus=self.sysFunctions["ISFULLSCREEN"](), releaseFunction=self.pageObjectFunctions['TOGGLEFULLSCREEN'])
        #---GUI Theme Selection
        self.GUIOs["GRAPHICSCONTROL_TEXT_GUITHEME"] = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=7650, width=1250, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:GUITHEME'), fontSize=80)
        guiThemeSelectionList = {'LIGHT': {'text': self.visualManager.getTextPack('SETTINGS:LIGHTMODE')}, 'DARK': {'text': self.visualManager.getTextPack('SETTINGS:DARKMODE')}}
        self.GUIOs["GRAPHICSCONTROL_SELECTIONBOX_GUITHEME"] = selectionBox_typeB(**inst, groupOrder=3, xPos=1450, yPos=7650, width=1250, height= 250, style="styleA", fontSize=80, nDisplay = len(guiThemeSelectionList), selectionUpdateFunction = self.pageObjectFunctions['ONGUITHEMESELECTIONUPDATE'])
        self.GUIOs["GRAPHICSCONTROL_SELECTIONBOX_GUITHEME"].setSelectionList(selectionList = guiThemeSelectionList, displayTargets = 'all')
        self.GUIOs["GRAPHICSCONTROL_SELECTIONBOX_GUITHEME"].setSelected(itemKey = self.visualManager.getGUITheme(), callSelectionUpdateFunction = False)
        #---Language Selection
        self.GUIOs["GRAPHICSCONTROL_TEXT_LANGUAGE"] = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=7300, width=1250, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:LANGUAGE'), fontSize=80)
        languageSelectionList = dict()
        for language in self.visualManager.getAvailableLanguages(): languageSelectionList[language] = {'text': self.visualManager.getTextPack('SETTINGS:'+language)}
        self.GUIOs["GRAPHICSCONTROL_SELECTIONBOX_LANGUAGE"] = selectionBox_typeB(**inst, groupOrder=2, xPos=1450, yPos=7300, width=1250, height= 250, style="styleA", fontSize=80, nDisplay = len(languageSelectionList), selectionUpdateFunction = self.pageObjectFunctions['ONLANGUAGESELECTIONUPDATE'])
        self.GUIOs["GRAPHICSCONTROL_SELECTIONBOX_LANGUAGE"].setSelectionList(selectionList = languageSelectionList, displayTargets = 'all')
        self.GUIOs["GRAPHICSCONTROL_SELECTIONBOX_LANGUAGE"].setSelected(itemKey = self.visualManager.getLanguage(), callSelectionUpdateFunction = False)

        #[2]: Audio Menu
        self.GUIOs["AUDIOCONTROL_WRAPPER"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=4000, width=9800, height=200, style="styleA", text=self.visualManager.getTextPack('SETTINGS:AUDIOWRAPPERTITLE'), fontSize = 80)
        #---Audio Play Switch
        self.GUIOs["AUDIOCONTROL_TEXT_AUDIOPALY"]   = textBox_typeA(**inst, groupOrder=2, xPos= 100, yPos=3650, width=1500, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:PLAYSOUND'), fontSize=80)
        self.GUIOs["AUDIOCONTROL_SWITCH_AUDIOPALY"] = switch_typeB(**inst,  groupOrder=2, xPos=1700, yPos=3650, width= 500, height= 250, style="styleA", align='horizontal', switchStatus=not(self.audioManager.ctrl_Mute), releaseFunction=self.pageObjectFunctions['TOGGLEPROGRAMAUDIO'])
        #---Volume Control Slider
        self.GUIOs["AUDIOCONTROL_TEXT_AUDIOVOLUME"]   = textBox_typeA(**inst, groupOrder=2, xPos=2300, yPos=3650, width=1500, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:MAINVOLUME'), fontSize=80)
        self.GUIOs["AUDIOCONTROL_SLIDER_AUDIOVOLUME"] = slider_typeA(**inst,  groupOrder=2, xPos=3900, yPos=3700, width=4850, height= 150, align = 'horizontal', style="styleA", valueUpdateFunction = self.pageObjectFunctions['ADJUSTPROGRAMAUDIOVOLUME'], sliderValue=self.audioManager.getVolume())
        if (self.audioManager.ctrl_Mute == True): self.GUIOs["AUDIOCONTROL_SLIDER_AUDIOVOLUME"].deactivate()
        self.GUIOs["AUDIOCONTROL_TEXT_AUDIOVOLUMEVALUE"] = textBox_typeA(**inst, groupOrder=2, xPos=8900, yPos=3650, width=1000, height= 250, style="styleA", text="{:.1f}".format(self.audioManager.getVolume()), fontSize=80)

        #[3]: System Menu --- BINANCE API
        self.GUIOs["SYSTEM_BINANCEAPI_WRAPPER"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=10000, yPos=8350, width=5900, height=200, style="styleA", text=self.visualManager.getTextPack('SETTINGS:SYSTEM_BINANCEAPI_WRAPPERTITLE'), fontSize = 80)
        #---Rate Limit IP Sharing Number
        self.GUIOs["SYSTEM_BINANCEAPI_RATELIMITIPSHARINGNUMBER_TITLETEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=10000, yPos=8000, width=4500, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:SYSTEM_BINANCEAPI_RATELIMITIPSHARINGNUMBER'), fontSize=80)
        _numberSelections = dict()
        for _i in range (5): _numberSelections[_i+1] = {'text': _i+1}
        self.GUIOs["SYSTEM_BINANCEAPI_RATELIMITIPSHARINGNUMBER_SELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=3, xPos=14600, yPos=8000, width=1300, height= 250, style="styleA", fontSize=80, nDisplay = len(_numberSelections), selectionUpdateFunction = self.pageObjectFunctions['UPDATEBINANCEAPICONFIGURATION'])
        self.GUIOs["SYSTEM_BINANCEAPI_RATELIMITIPSHARINGNUMBER_SELECTIONBOX"].setSelectionList(selectionList = _numberSelections, displayTargets = 'all')
        self.GUIOs["SYSTEM_BINANCEAPI_RATELIMITIPSHARINGNUMBER_SELECTIONBOX"].setSelected(itemKey = 1, callSelectionUpdateFunction = False)
        #---Log Prints
        self.GUIOs["SYSTEM_BINANCEAPI_PRINTUPDATE_TITLETEXT"]  = textBox_typeA(**inst, groupOrder=1, xPos=10000, yPos=7650, width=1300, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:SYSTEM_PRINTUPDATE'),  fontSize=80)
        self.GUIOs["SYSTEM_BINANCEAPI_PRINTUPDATE_SWITCH"]     = switch_typeB(**inst,  groupOrder=1, xPos=11400, yPos=7650, width= 500, height= 250, style="styleA", align='horizontal', switchStatus=False, releaseFunction=self.pageObjectFunctions['UPDATEBINANCEAPICONFIGURATION'])
        self.GUIOs["SYSTEM_BINANCEAPI_PRINTWARNING_TITLETEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=12000, yPos=7650, width=1300, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:SYSTEM_PRINTWARNING'), fontSize=80)
        self.GUIOs["SYSTEM_BINANCEAPI_PRINTWARNING_SWITCH"]    = switch_typeB(**inst,  groupOrder=1, xPos=13400, yPos=7650, width= 500, height= 250, style="styleA", align='horizontal', switchStatus=False, releaseFunction=self.pageObjectFunctions['UPDATEBINANCEAPICONFIGURATION'])
        self.GUIOs["SYSTEM_BINANCEAPI_PRINTERROR_TITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos=14000, yPos=7650, width=1300, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:SYSTEM_PRINTERROR'),   fontSize=80)
        self.GUIOs["SYSTEM_BINANCEAPI_PRINTERROR_SWITCH"]      = switch_typeB(**inst,  groupOrder=1, xPos=15400, yPos=7650, width= 500, height= 250, style="styleA", align='horizontal', switchStatus=False, releaseFunction=self.pageObjectFunctions['UPDATEBINANCEAPICONFIGURATION'])

        #[4]: System Menu --- Data Manager
        self.GUIOs["SYSTEM_DATAMANAGER_WRAPPER"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=10000, yPos=7350, width=5900, height=200, style="styleA", text=self.visualManager.getTextPack('SETTINGS:SYSTEM_DATAMANAGER_WRAPPERTITLE'), fontSize = 80)
        #---Log Prints
        self.GUIOs["SYSTEM_DATAMANAGER_PRINTUPDATE_TITLETEXT"]  = textBox_typeA(**inst, groupOrder=1, xPos=10000, yPos=7000, width=1300, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:SYSTEM_PRINTUPDATE'),  fontSize=80)
        self.GUIOs["SYSTEM_DATAMANAGER_PRINTUPDATE_SWITCH"]     = switch_typeB(**inst,  groupOrder=1, xPos=11400, yPos=7000, width= 500, height= 250, style="styleA", align='horizontal', switchStatus=False, releaseFunction=self.pageObjectFunctions['UPDATEDATAMANAGERCONFIGURATION'])
        self.GUIOs["SYSTEM_DATAMANAGER_PRINTWARNING_TITLETEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=12000, yPos=7000, width=1300, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:SYSTEM_PRINTWARNING'), fontSize=80)
        self.GUIOs["SYSTEM_DATAMANAGER_PRINTWARNING_SWITCH"]    = switch_typeB(**inst,  groupOrder=1, xPos=13400, yPos=7000, width= 500, height= 250, style="styleA", align='horizontal', switchStatus=False, releaseFunction=self.pageObjectFunctions['UPDATEDATAMANAGERCONFIGURATION'])
        self.GUIOs["SYSTEM_DATAMANAGER_PRINTERROR_TITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos=14000, yPos=7000, width=1300, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:SYSTEM_PRINTERROR'),   fontSize=80)
        self.GUIOs["SYSTEM_DATAMANAGER_PRINTERROR_SWITCH"]      = switch_typeB(**inst,  groupOrder=1, xPos=15400, yPos=7000, width= 500, height= 250, style="styleA", align='horizontal', switchStatus=False, releaseFunction=self.pageObjectFunctions['UPDATEDATAMANAGERCONFIGURATION'])

        #[5]: System Menu --- Trade Manager
        self.GUIOs["SYSTEM_TRADEMANAGER_WRAPPER"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=10000, yPos=6700, width=5900, height=200, style="styleA", text=self.visualManager.getTextPack('SETTINGS:SYSTEM_TRADEMANAGER_WRAPPERTITLE'), fontSize = 80)
        #---Log Prints
        self.GUIOs["SYSTEM_TRADEMANAGER_PRINTUPDATE_TITLETEXT"]  = textBox_typeA(**inst, groupOrder=1, xPos=10000, yPos=6350, width=1300, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:SYSTEM_PRINTUPDATE'),  fontSize=80)
        self.GUIOs["SYSTEM_TRADEMANAGER_PRINTUPDATE_SWITCH"]     = switch_typeB(**inst,  groupOrder=1, xPos=11400, yPos=6350, width= 500, height= 250, style="styleA", align='horizontal', switchStatus=False, releaseFunction=self.pageObjectFunctions['UPDATETRADEMANAGERCONFIGURATION'])
        self.GUIOs["SYSTEM_TRADEMANAGER_PRINTWARNING_TITLETEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=12000, yPos=6350, width=1300, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:SYSTEM_PRINTWARNING'), fontSize=80)
        self.GUIOs["SYSTEM_TRADEMANAGER_PRINTWARNING_SWITCH"]    = switch_typeB(**inst,  groupOrder=1, xPos=13400, yPos=6350, width= 500, height= 250, style="styleA", align='horizontal', switchStatus=False, releaseFunction=self.pageObjectFunctions['UPDATETRADEMANAGERCONFIGURATION'])
        self.GUIOs["SYSTEM_TRADEMANAGER_PRINTERROR_TITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos=14000, yPos=6350, width=1300, height= 250, style="styleA", text=self.visualManager.getTextPack('SETTINGS:SYSTEM_PRINTERROR'),   fontSize=80)
        self.GUIOs["SYSTEM_TRADEMANAGER_PRINTERROR_SWITCH"]      = switch_typeB(**inst,  groupOrder=1, xPos=15400, yPos=6350, width= 500, height= 250, style="styleA", align='horizontal', switchStatus=False, releaseFunction=self.pageObjectFunctions['UPDATETRADEMANAGERCONFIGURATION'])

        #[6]: Configuration & Message
        self.GUIOs["CONFIGURATIONANDMESSAGE_WRAPPER"]    = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=800, width=15800, height=200, style="styleA", text=self.visualManager.getTextPack('SETTINGS:CONFIGURATIONANDMESSAGEWRAPPERTITLE'), fontSize = 80)
        self.GUIOs["CONFIGURATIONANDMESSAGE_MESSAGE"]    = textBox_typeA(**inst, groupOrder=1, xPos=100, yPos=450, width=15800, height=250, style="styleA", text="-", fontSize=80)
        self.GUIOs["CONFIGURATIONANDMESSAGE_SAVEBUTTON"] = button_typeA(**inst,  groupOrder=2, xPos=100, yPos=100, width=15800, height=250, style="styleA", releaseFunction=self.pageObjectFunctions['SAVEGUICONFIG'], text=self.visualManager.getTextPack('SETTINGS:SAVECHANGES'), fontSize = 80)
        self.GUIOs["CONFIGURATIONANDMESSAGE_SAVEBUTTON"].deactivate()

    elif (self.displaySpaceDefiner['ratio'] == '21:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 21000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
    elif (self.displaySpaceDefiner['ratio'] == '32:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 32000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
#SETUP PAGE <MAIN> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <LOAD> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageLoadFunction(self):
    #[1]: Binance API Configuration
    _binanceAPI_configuration = self.ipcA.getPRD(processName = 'BINANCEAPI', prdAddress = 'CONFIGURATION')
    self.GUIOs["SYSTEM_BINANCEAPI_RATELIMITIPSHARINGNUMBER_SELECTIONBOX"].setSelected(itemKey = _binanceAPI_configuration['rateLimitIPSharingNumber'], callSelectionUpdateFunction = False)
    self.GUIOs["SYSTEM_BINANCEAPI_PRINTUPDATE_SWITCH"].setStatus(status  = _binanceAPI_configuration['print_Update'],  callStatusUpdateFunction = False)
    self.GUIOs["SYSTEM_BINANCEAPI_PRINTWARNING_SWITCH"].setStatus(status = _binanceAPI_configuration['print_Warning'], callStatusUpdateFunction = False)
    self.GUIOs["SYSTEM_BINANCEAPI_PRINTERROR_SWITCH"].setStatus(status   = _binanceAPI_configuration['print_Error'],   callStatusUpdateFunction = False)
    #[2]: Data Manager Configuration
    _dataManager_configuration = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = 'CONFIGURATION')
    self.GUIOs["SYSTEM_DATAMANAGER_PRINTUPDATE_SWITCH"].setStatus(status  = _dataManager_configuration['print_Update'],  callStatusUpdateFunction = False)
    self.GUIOs["SYSTEM_DATAMANAGER_PRINTWARNING_SWITCH"].setStatus(status = _dataManager_configuration['print_Warning'], callStatusUpdateFunction = False)
    self.GUIOs["SYSTEM_DATAMANAGER_PRINTERROR_SWITCH"].setStatus(status   = _dataManager_configuration['print_Error'],   callStatusUpdateFunction = False)
    #[3]: Trade Manager Configuration
    _tradeManager_configuration = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = 'CONFIGURATION')
    self.GUIOs["SYSTEM_TRADEMANAGER_PRINTUPDATE_SWITCH"].setStatus(status  = _tradeManager_configuration['print_Update'],  callStatusUpdateFunction = False)
    self.GUIOs["SYSTEM_TRADEMANAGER_PRINTWARNING_SWITCH"].setStatus(status = _tradeManager_configuration['print_Warning'], callStatusUpdateFunction = False)
    self.GUIOs["SYSTEM_TRADEMANAGER_PRINTERROR_SWITCH"].setStatus(status   = _tradeManager_configuration['print_Error'],   callStatusUpdateFunction = False)
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
    def __pageMove_DASHBOARD(objInstance, **kwargs): 
        self.sysFunctions['LOADPAGE']('DASHBOARD')
    objFunctions['PAGEMOVE_DASHBOARD'] = __pageMove_DASHBOARD

    #<Audio>
    def __toggleProgramAudio(objInstance, **kwargs):
        if (self.GUIOs['AUDIOCONTROL_SWITCH_AUDIOPALY'].getStatus() == True):
            self.audioManager.setMute(False)
            self.GUIOs["AUDIOCONTROL_SLIDER_AUDIOVOLUME"].activate()
        else:
            self.audioManager.setMute(True)
            self.GUIOs["AUDIOCONTROL_SLIDER_AUDIOVOLUME"].deactivate()
        self.GUIOs["CONFIGURATIONANDMESSAGE_SAVEBUTTON"].activate()
    def __adjustProgramAudioVolume(objInstance, **kwargs):
        self.audioManager.setVolume(self.GUIOs["AUDIOCONTROL_SLIDER_AUDIOVOLUME"].getSliderValue())
        self.GUIOs["AUDIOCONTROL_TEXT_AUDIOVOLUMEVALUE"].updateText("{:.1f}".format(self.audioManager.getVolume()))
        self.GUIOs["CONFIGURATIONANDMESSAGE_SAVEBUTTON"].activate()
    objFunctions['TOGGLEPROGRAMAUDIO']       = __toggleProgramAudio
    objFunctions['ADJUSTPROGRAMAUDIOVOLUME'] = __adjustProgramAudioVolume

    #<Graphics>
    def __toggleFullScreen(objInstance, **kwargs):
        self.sysFunctions["TOGGLE_FULLSCREEN"]()
        self.GUIOs["CONFIGURATIONANDMESSAGE_SAVEBUTTON"].activate()
    def __onGUIThemeSelectionUpdate(objInstance, **kwargs):
        selectedTheme = self.GUIOs["GRAPHICSCONTROL_SELECTIONBOX_GUITHEME"].getSelected()
        self.sysFunctions['CHANGEGUITHEME'](selectedTheme)
        self.GUIOs["CONFIGURATIONANDMESSAGE_SAVEBUTTON"].activate()
    def __onLanguageSelectionUpdate(objInstance, **kwargs):
        selectedLanguage = self.GUIOs["GRAPHICSCONTROL_SELECTIONBOX_LANGUAGE"].getSelected()
        self.sysFunctions['CHANGELANGUAGE'](selectedLanguage)
        self.GUIOs["CONFIGURATIONANDMESSAGE_SAVEBUTTON"].activate()
    objFunctions['TOGGLEFULLSCREEN']          = __toggleFullScreen
    objFunctions['ONGUITHEMESELECTIONUPDATE'] = __onGUIThemeSelectionUpdate
    objFunctions['ONLANGUAGESELECTIONUPDATE'] = __onLanguageSelectionUpdate

    #<Systems>
    def __updateBinanceAPIConfiguration(objInstance, **kwargs):
        _newConfiguration = {'rateLimitIPSharingNumber': self.GUIOs["SYSTEM_BINANCEAPI_RATELIMITIPSHARINGNUMBER_SELECTIONBOX"].getSelected(),
                             'print_Update':             self.GUIOs["SYSTEM_BINANCEAPI_PRINTUPDATE_SWITCH"].getStatus(),
                             'print_Warning':            self.GUIOs["SYSTEM_BINANCEAPI_PRINTWARNING_SWITCH"].getStatus(),
                             'print_Error':              self.GUIOs["SYSTEM_BINANCEAPI_PRINTERROR_SWITCH"].getStatus()}
        self.ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                          functionID     = 'updateConfiguration',
                          functionParams = {'newConfiguration': _newConfiguration,}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONBINANCEAPICONFIGURATIONUPDATEREQUESTRESPONSE'])
    def __updateDataManagerConfiguration(objInstance, **kwargs):
        _newConfiguration = {'print_Update':             self.GUIOs["SYSTEM_DATAMANAGER_PRINTUPDATE_SWITCH"].getStatus(),
                             'print_Warning':            self.GUIOs["SYSTEM_DATAMANAGER_PRINTWARNING_SWITCH"].getStatus(),
                             'print_Error':              self.GUIOs["SYSTEM_DATAMANAGER_PRINTERROR_SWITCH"].getStatus()}
        self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                          functionID     = 'updateConfiguration',
                          functionParams = {'newConfiguration': _newConfiguration,}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONDATAMANAGERCONFIGURATIONUPDATEREQUESTRESPONSE'])
    def __updateTradeManagerConfiguration(objInstance, **kwargs):
        _newConfiguration = {'print_Update':             self.GUIOs["SYSTEM_TRADEMANAGER_PRINTUPDATE_SWITCH"].getStatus(),
                             'print_Warning':            self.GUIOs["SYSTEM_TRADEMANAGER_PRINTWARNING_SWITCH"].getStatus(),
                             'print_Error':              self.GUIOs["SYSTEM_TRADEMANAGER_PRINTERROR_SWITCH"].getStatus()}
        self.ipcA.sendFAR(targetProcess  = 'TRADEMANAGER', 
                          functionID     = 'updateConfiguration',
                          functionParams = {'newConfiguration': _newConfiguration,}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONTRADEMANAGERCONFIGURATIONUPDATEREQUESTRESPONSE'])
    objFunctions['UPDATEBINANCEAPICONFIGURATION']   = __updateBinanceAPIConfiguration
    objFunctions['UPDATEDATAMANAGERCONFIGURATION']  = __updateDataManagerConfiguration
    objFunctions['UPDATETRADEMANAGERCONFIGURATION'] = __updateTradeManagerConfiguration

    #<Etc>
    def __SaveGUIConfig(objInstance, **kwargs):
        self.sysFunctions['SAVEGUICONFIG']()
        self.GUIOs["CONFIGURATIONANDMESSAGE_SAVEBUTTON"].deactivate()
        self.GUIOs["CONFIGURATIONANDMESSAGE_MESSAGE"].updateText(text = "[{:s}] GUI Configuration Successfully Saved!".format(datetime.fromtimestamp(timestamp = time.time()).strftime("%Y/%m/%d %H:%M:%S")), textStyle = "GREEN_LIGHT")
    objFunctions['SAVEGUICONFIG'] = __SaveGUIConfig

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()

    #<Systems>
    def __farr_onBinanceAPIConfigurationUpdateRequestResponse(responder, requestID, functionResult):
        requestResult = functionResult['result']
        message       = functionResult['message']
        configuration = functionResult['configuration']
        self.GUIOs["SYSTEM_BINANCEAPI_RATELIMITIPSHARINGNUMBER_SELECTIONBOX"].setSelected(itemKey = configuration['rateLimitIPSharingNumber'], callSelectionUpdateFunction = False)
        self.GUIOs["SYSTEM_BINANCEAPI_PRINTUPDATE_SWITCH"].setStatus(status  = configuration['print_Update'],  callStatusUpdateFunction = False)
        self.GUIOs["SYSTEM_BINANCEAPI_PRINTWARNING_SWITCH"].setStatus(status = configuration['print_Warning'], callStatusUpdateFunction = False)
        self.GUIOs["SYSTEM_BINANCEAPI_PRINTERROR_SWITCH"].setStatus(status   = configuration['print_Error'],   callStatusUpdateFunction = False)
        _time_str = datetime.fromtimestamp(timestamp = time.time()).strftime("%Y/%m/%d %H:%M:%S")
        if (requestResult == True): self.GUIOs["CONFIGURATIONANDMESSAGE_MESSAGE"].updateText(text = f"[{_time_str}] <BINANCEAPI> - {message}", textStyle = "GREEN_LIGHT")
        else:                       self.GUIOs["CONFIGURATIONANDMESSAGE_MESSAGE"].updateText(text = f"[{_time_str}] <BINANCEAPI> - {message}", textStyle = "RED_LIGHT")
    def __farr_onDataManagerConfigurationUpdateRequestResponse(responder, requestID, functionResult):
        requestResult = functionResult['result']
        message       = functionResult['message']
        configuration = functionResult['configuration']
        self.GUIOs["SYSTEM_DATAMANAGER_PRINTUPDATE_SWITCH"].setStatus(status  = configuration['print_Update'],  callStatusUpdateFunction = False)
        self.GUIOs["SYSTEM_DATAMANAGER_PRINTWARNING_SWITCH"].setStatus(status = configuration['print_Warning'], callStatusUpdateFunction = False)
        self.GUIOs["SYSTEM_DATAMANAGER_PRINTERROR_SWITCH"].setStatus(status   = configuration['print_Error'],   callStatusUpdateFunction = False)
        _time_str = datetime.fromtimestamp(timestamp = time.time()).strftime("%Y/%m/%d %H:%M:%S")
        if (requestResult == True): self.GUIOs["CONFIGURATIONANDMESSAGE_MESSAGE"].updateText(text = f"[{_time_str}] <DATAMANAGER> - {message}", textStyle = "GREEN_LIGHT")
        else:                       self.GUIOs["CONFIGURATIONANDMESSAGE_MESSAGE"].updateText(text = f"[{_time_str}] <DATAMANAGER> - {message}", textStyle = "RED_LIGHT")
    def __farr_onTradeManagerConfigurationUpdateRequestResponse(responder, requestID, functionResult):
        requestResult = functionResult['result']
        message       = functionResult['message']
        configuration = functionResult['configuration']
        self.GUIOs["SYSTEM_TRADEMANAGER_PRINTUPDATE_SWITCH"].setStatus(status  = configuration['print_Update'],  callStatusUpdateFunction = False)
        self.GUIOs["SYSTEM_TRADEMANAGER_PRINTWARNING_SWITCH"].setStatus(status = configuration['print_Warning'], callStatusUpdateFunction = False)
        self.GUIOs["SYSTEM_TRADEMANAGER_PRINTERROR_SWITCH"].setStatus(status   = configuration['print_Error'],   callStatusUpdateFunction = False)
        _time_str = datetime.fromtimestamp(timestamp = time.time()).strftime("%Y/%m/%d %H:%M:%S")
        if (requestResult == True): self.GUIOs["CONFIGURATIONANDMESSAGE_MESSAGE"].updateText(text = f"[{_time_str}] <TRADEMANAGER> - {message}", textStyle = "GREEN_LIGHT")
        else:                       self.GUIOs["CONFIGURATIONANDMESSAGE_MESSAGE"].updateText(text = f"[{_time_str}] <TRADEMANAGER> - {message}", textStyle = "RED_LIGHT")
    auxFunctions['_FARR_ONBINANCEAPICONFIGURATIONUPDATEREQUESTRESPONSE']   = __farr_onBinanceAPIConfigurationUpdateRequestResponse
    auxFunctions['_FARR_ONDATAMANAGERCONFIGURATIONUPDATEREQUESTRESPONSE']  = __farr_onDataManagerConfigurationUpdateRequestResponse
    auxFunctions['_FARR_ONTRADEMANAGERCONFIGURATIONUPDATEREQUESTRESPONSE'] = __farr_onTradeManagerConfigurationUpdateRequestResponse

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------