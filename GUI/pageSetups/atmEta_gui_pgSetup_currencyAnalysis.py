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
_IPC_PRD_INVALIDADDRESS    = atmEta_IPC._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = atmEta_IPC._FAR_INVALIDFUNCTIONID

#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
    self.puVar['currencyAnalysis']          = dict()
    self.puVar['currencyAnalysis_selected'] = None
    self.puVar['currencyAnalysis_toLoad']   = None

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
        self.GUIOs["TITLETEXT_CURRENCYANALYSIS"] = textBox_typeA(**inst, groupOrder=1, xPos= 5000, yPos=8550, width=6000, height=400, style=None, text=self.visualManager.getTextPack('CURRENCYANALYSIS:TITLE'), fontSize = 220, textInteractable = False)

        self.GUIOs["BUTTON_MOVETO_DASHBOARD"] = button_typeB(**inst,  groupOrder=2, xPos=  50, yPos=8650, width= 300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['PAGEMOVE_DASHBOARD'], image = 'dashboardIcon_512x512.png', imageSize = (225, 225), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        
        #Currency Analysis List
        self.GUIOs["BLOCKSUBTITLE_CURRENCYANALYSISLIST"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=8350, width=4100, height=200, style="styleA", text=self.visualManager.getTextPack('CURRENCYANALYSIS:BLOCKTITLE_CURRENCYANALYSISLIST'), fontSize = 80)
        #---Filter
        self.GUIOs["CURRENCYANALYSISLIST_SEARCHTITLETEXT"]                  = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=8000, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_SEARCH'),        fontSize=80, textInteractable    =False)
        self.GUIOs["CURRENCYANALYSISLIST_SEARCHTITLETEXTINPUTBOX"]          = textInputBox_typeA(**inst, groupOrder=1, xPos=1200, yPos=8000, width=3000, height=250, style="styleA", text="",                                                                      fontSize=80, textUpdateFunction  =self.pageObjectFunctions['ONTEXTUPDATE_CURRENCYANALYSISLIST_SEARCHTEXT'])
        self.GUIOs["CURRENCYANALYSISLIST_SORTBYTITLETEXT"]                  = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=7650, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_SORTBY'),   fontSize=80, textInteractable    =False)
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"]            = switch_typeC(**inst,       groupOrder=1, xPos=1200, yPos=7650, width= 900, height=250, style="styleB", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_ID'),       fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTBYID'])
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"]      = switch_typeC(**inst,       groupOrder=1, xPos=2200, yPos=7650, width= 900, height=250, style="styleB", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_ANALYZER'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTBYANALYZER'])
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"]  = switch_typeC(**inst,       groupOrder=1, xPos=3200, yPos=7650, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_CACODE'),   fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTBYANALYSISCODE'])
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"]        = switch_typeC(**inst,       groupOrder=1, xPos= 100, yPos=7300, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_SYMBOL'),   fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTBYSYMBOL'])
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"] = switch_typeC(**inst,       groupOrder=1, xPos=1200, yPos=7300, width=1900, height=250, style="styleB", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_CACCODE'),  fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTBYCONFIGURATION'])
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"]        = switch_typeC(**inst,       groupOrder=1, xPos=3200, yPos=7300, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS'),   fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTBYSTATUS'])
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].setStatus(status = True, callStatusUpdateFunction = False)
        #---List
        self.GUIOs["CURRENCYANALYSISLIST_SELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=1, xPos=100, yPos=800, width=4100, height=6400, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_CURRENCYANALYSISLIST_ANALYSISSELECTION'], elementWidths = (600, 900, 1150, 1200))
        self.GUIOs["CURRENCYANALYSISLIST_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_INDEX')},
                                                                                         {'text': self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_CURRENCYANALYSISCODE')},
                                                                                         {'text': self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_SYMBOL')},
                                                                                         {'text': self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS')}])
        #---Information
        self.GUIOs["CURRENCYANALYSISLIST_CONFIGURATIONCODETITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=450, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_CONFIGURATIONCODE'), fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYANALYSISLIST_CONFIGURATIONCODEDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=1700, yPos=450, width=2500, height=250, style="styleA", text="-",                                                                                       fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYANALYSISLIST_ALLOCATEDANALYZERTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=100, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_ALLOCATEDANALYZER'), fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYANALYSISLIST_ALLOCATEDANALYZERDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=1700, yPos=100, width=2500, height=250, style="styleA", text="-",                                                                                       fontSize=80, textInteractable=True)

        #Currency Analysis Chart
        self.GUIOs["BLOCKSUBTITLE_CHART"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=4300, yPos=8350, width=11600, height=200, style="styleA", text=self.visualManager.getTextPack('CURRENCYANALYSIS:BLOCKTITLE_CHART'), fontSize = 80)
        self.GUIOs["CHART_CHARTDRAWER"] = chartDrawer(**inst, groupOrder=1, xPos=4300, yPos=100, width=11600, height=8150, style="styleA", name = 'CURRENCYANALYSIS_CHARTDRAWER', chartDrawerType = 'CAVIEWER')

    elif (self.displaySpaceDefiner['ratio'] == '21:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 21000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
    elif (self.displaySpaceDefiner['ratio'] == '32:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 32000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
#SETUP PAGE <MAIN> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <LOAD> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageLoadFunction(self):
    #FAR Registration
    #---TRADEMANAGER
    self.ipcA.addFARHandler('onCurrencyAnalysisUpdate', self.pageAuxillaryFunctions['_FAR_ONCURRENCYANALYSISUPDATE'], executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

    #Get data via PRD
    self.puVar['currencyAnalysis'] = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = 'CURRENCYANALYSIS')
    
    #GUIO Update
    #---List
    self.pageAuxillaryFunctions['SETLIST']()
    #---Information
    if ((self.puVar['currencyAnalysis_selected'] != None) and (self.puVar['currencyAnalysis_selected'] not in self.puVar['currencyAnalysis'])): 
        self.puVar['currencyAnalysis_selected'] = None
        self.GUIOs["CHART_CHARTDRAWER"].setTarget(target = None)
    self.pageAuxillaryFunctions['UPDATEINFORMATION']()

    #Currency Analysis Load
    if (self.puVar['currencyAnalysis_toLoad'] != None):
        self.GUIOs["CURRENCYANALYSISLIST_SELECTIONBOX"].clearSelected()
        self.GUIOs["CURRENCYANALYSISLIST_SELECTIONBOX"].addSelected(itemKey = self.puVar['currencyAnalysis_toLoad'], callSelectionUpdateFunction = True)
        self.puVar['currencyAnalysis_toLoad'] = None
#SETUP PAGE <LOAD> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <ESCAPE> --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageEscapeFunction(self):
    self.ipcA.removeFARHandler('onCurrencyAnalysisUpdate')
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

    #<Currency Analysis List>
    #---Filter
    def __onTextUpdate_CurrencyAnalysisList_SearchText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyAnalysisList_SortByID(objInstance, **kwargs):
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"].getStatus()      == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"].setStatus(status      = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus()  == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"].setStatus(status  = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"].getStatus()        == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].getStatus()        == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].getStatus() == False):           self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].setStatus(status            = True,  callStatusUpdateFunction = False)
        else:                                                                                         self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyAnalysisList_SortByAnalyzer(objInstance, **kwargs):
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].getStatus()            == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].setStatus(status            = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus()  == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"].setStatus(status  = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"].getStatus()        == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].getStatus()        == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"].getStatus() == False):     self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"].setStatus(status      = True,  callStatusUpdateFunction = False)
        else:                                                                                         self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyAnalysisList_SortByAnalysisCode(objInstance, **kwargs):
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].getStatus()            == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].setStatus(status            = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"].getStatus()      == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"].setStatus(status      = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"].getStatus()        == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].getStatus()        == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus() == False): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"].setStatus(status  = True,  callStatusUpdateFunction = False)
        else:                                                                                         self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyAnalysisList_SortBySymbol(objInstance, **kwargs):
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].getStatus()            == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].setStatus(status            = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"].getStatus()      == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"].setStatus(status      = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus()  == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"].setStatus(status  = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].getStatus()        == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"].getStatus() == False):       self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status        = True,  callStatusUpdateFunction = False)
        else:                                                                                         self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyAnalysisList_SortByConfiguration(objInstance, **kwargs):
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].getStatus()           == True):  self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].setStatus(status            = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"].getStatus()     == True):  self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"].setStatus(status      = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus() == True):  self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"].setStatus(status  = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"].getStatus()       == True):  self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].getStatus()       == True):  self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == False): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"].setStatus(status = True,  callStatusUpdateFunction = False)
        else:                                                                                          self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyAnalysisList_SortByStatus(objInstance, **kwargs):
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].getStatus()            == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].setStatus(status            = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"].getStatus()      == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"].setStatus(status      = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus()  == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"].setStatus(status  = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"].getStatus()        == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == True): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].getStatus() == False): self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].setStatus(status              = True,  callStatusUpdateFunction = False)
        else:                                                                                   self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    objFunctions['ONTEXTUPDATE_CURRENCYANALYSISLIST_SEARCHTEXT']                  = __onTextUpdate_CurrencyAnalysisList_SearchText
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTBYID']            = __onSwitchStatusUpdate_CurrencyAnalysisList_SortByID
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTBYANALYZER']      = __onSwitchStatusUpdate_CurrencyAnalysisList_SortByAnalyzer
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTBYANALYSISCODE']  = __onSwitchStatusUpdate_CurrencyAnalysisList_SortByAnalysisCode
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTBYSYMBOL']        = __onSwitchStatusUpdate_CurrencyAnalysisList_SortBySymbol
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTBYCONFIGURATION'] = __onSwitchStatusUpdate_CurrencyAnalysisList_SortByConfiguration
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTBYSTATUS']        = __onSwitchStatusUpdate_CurrencyAnalysisList_SortByStatus
    #---List
    def __onSelectionUpdate_CurrencyAnalysisList_AnalysisSelection(objInstance, **kwargs):
        try:    currencyAnalysis_selected = objInstance.getSelected()[0]
        except: currencyAnalysis_selected = None
        self.puVar['currencyAnalysis_selected'] = currencyAnalysis_selected
        self.pageAuxillaryFunctions['UPDATEINFORMATION']()
        self.GUIOs["CHART_CHARTDRAWER"].setTarget(target = self.puVar['currencyAnalysis_selected'])
    objFunctions['ONSELECTIONUPDATE_CURRENCYANALYSISLIST_ANALYSISSELECTION'] = __onSelectionUpdate_CurrencyAnalysisList_AnalysisSelection

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()
    
    #<_PAGELOAD>
    def __far_onCurrencyAnalysisUpdate(requester, updateType, currencyAnalysisCode):
        if (requester == 'TRADEMANAGER'):
            if (updateType == 'UPDATE_STATUS'):
                newStatus = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'status'))
                self.puVar['currencyAnalysis'][currencyAnalysisCode]['status'] = newStatus
                #List item update
                if   (newStatus == 'CURRENCYNOTFOUND'):     _status_color = "RED"
                elif (newStatus == 'CONFIGNOTFOUND'):       _status_color = "RED_LIGHT"
                elif (newStatus == 'WAITINGTRADING'):       _status_color = "ORANGE_LIGHT"
                elif (newStatus == 'WAITINGNNCDATA'):       _status_color = "BLUE_DARK"
                elif (newStatus == 'WAITINGSTREAM'):        _status_color = "BLUE_DARK"
                elif (newStatus == 'WAITINGDATAAVAILABLE'): _status_color = "BLUE_LIGHT"
                elif (newStatus == 'PREP_QUEUED'):          _status_color = "BLUE_LIGHT"
                elif (newStatus == 'PREP_ANALYZINGKLINES'): _status_color = "BLUE_LIGHT"
                elif (newStatus == 'ANALYZINGREALTIME'):    _status_color = "GREEN_LIGHT"
                elif (newStatus == 'ERROR'):                _status_color = "RED_DARK"
                _newSelectionBoxItem = {'text': self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_{:s}'.format(newStatus)), 'textStyles': [('all', _status_color),], 'textAnchor': 'CENTER'}
                self.GUIOs["CURRENCYANALYSISLIST_SELECTIONBOX"].editSelectionListItem(itemKey = currencyAnalysisCode, item = _newSelectionBoxItem, columnIndex = 3)
                #Re-apply filter (if needed)
                if (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].getStatus() == True): self.pageAuxillaryFunctions['ONFILTERUPDATE']()
            elif (updateType == 'UPDATE_ANALYZER'):
                allocatedAnalyzer = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'allocatedAnalyzer'))
                self.puVar['currencyAnalysis'][currencyAnalysisCode]['allocatedAnalyzer'] = allocatedAnalyzer
                if (currencyAnalysisCode == self.puVar['currencyAnalysis_selected']):
                    if (allocatedAnalyzer == None): self.GUIOs["CURRENCYANALYSISLIST_ALLOCATEDANALYZERDISPLAYTEXT"].updateText(text = "-")
                    else:                           self.GUIOs["CURRENCYANALYSISLIST_ALLOCATEDANALYZERDISPLAYTEXT"].updateText(text = "ANALYZER {:d}".format(allocatedAnalyzer))
            elif (updateType == 'ADDED'):
                self.puVar['currencyAnalysis'][currencyAnalysisCode] = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode))
                self.pageAuxillaryFunctions['SETLIST']()
            elif (updateType == 'REMOVED'):
                self.pageAuxillaryFunctions['SETLIST']()
                if (currencyAnalysisCode == self.puVar['currencyAnalysis_selected']):
                    self.puVar['currencyAnalysis_selected'] = None
                    self.pageAuxillaryFunctions['UPDATEINFORMATION']()
            #Send the update to the chart drawer if this is for the selected currency analysis
            if (currencyAnalysisCode == self.puVar['currencyAnalysis_selected']): self.GUIOs["CHART_CHARTDRAWER"].CAViewer_onCurrencyAnalysisUpdate(updateType = updateType, currencyAnalysisCode = currencyAnalysisCode)
    auxFunctions['_FAR_ONCURRENCYANALYSISUPDATE'] = __far_onCurrencyAnalysisUpdate

    #<Filter>
    def __onFilterUpdate():
        filter_analysisCode = self.GUIOs["CURRENCYANALYSISLIST_SEARCHTITLETEXTINPUTBOX"].getText()
        analysisCodes_filtered = [analysisCode for analysisCode in self.puVar['currencyAnalysis'] if (filter_analysisCode in analysisCode)]
        if   (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].getStatus()       == True): listForSort = 'id'
        elif (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"].getStatus() == True):
            listForSort = list()
            for analysisCode in self.puVar['currencyAnalysis']:
                allocatedAnalyzer = self.puVar['currencyAnalysis'][analysisCode]['allocatedAnalyzer']
                if (allocatedAnalyzer == None): listForSort.append((analysisCode, float('inf')))
                else:                           listForSort.append((analysisCode, allocatedAnalyzer))
        elif (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus()  == True): listForSort = 'analysisCode'
        elif (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"].getStatus()        == True): listForSort = [(analysisCode, self.puVar['currencyAnalysis'][analysisCode]['currencySymbol'])                    for analysisCode in analysisCodes_filtered]
        elif (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == True): listForSort = [(analysisCode, self.puVar['currencyAnalysis'][analysisCode]['currencyAnalysisConfigurationCode']) for analysisCode in analysisCodes_filtered]
        elif (self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].getStatus()        == True): 
            listForSort = list()
            for analysisCode in self.puVar['currencyAnalysis']:
                ca_status = self.puVar['currencyAnalysis'][analysisCode]['status']
                if   (ca_status == 'ANALYZINGREALTIME'):    priority = 0
                elif (ca_status == 'PREP_ANALYZINGKLINES'): priority = 1
                elif (ca_status == 'PREP_FETCHINGKLINES'):  priority = 2
                elif (ca_status == 'PREP_QUEUED'):          priority = 3
                elif (ca_status == 'WAITINGDATAAVAILABLE'): priority = 4
                elif (ca_status == 'WAITINGSTREAM'):        priority = 5
                elif (ca_status == 'WAITINGTRADING'):       priority = 6
                elif (ca_status == 'CURRENCYNOTFOUND'):     priority = 7
                elif (ca_status == 'CONFIGNOTFOUND'):       priority = 8
                elif (ca_status == 'ERROR'):                priority = 9
                listForSort.append((analysisCode, priority))
        if   (listForSort == 'id'):           analysisCodes_sorted = analysisCodes_filtered
        elif (listForSort == 'analysisCode'): analysisCodes_sorted = analysisCodes_filtered; analysisCodes_sorted.sort()
        else:                                 listForSort.sort(key = lambda x: x[1]); analysisCodes_sorted = [sortPair[0] for sortPair in listForSort]
        self.GUIOs["CURRENCYANALYSISLIST_SELECTIONBOX"].setDisplayTargets(displayTargets = analysisCodes_sorted)
    auxFunctions['ONFILTERUPDATE'] = __onFilterUpdate

    #<List>
    def __setList():
        #Format and update the selectionBox object
        currencyAnalysis_selectionList = dict()
        nCAs = len(self.puVar['currencyAnalysis'])
        for _index, _caCode in enumerate(self.puVar['currencyAnalysis']):
            _ca = self.puVar['currencyAnalysis'][_caCode]
            _currencySymbol = _ca['currencySymbol']
            _status         = _ca['status']
            if   (_status == 'CURRENCYNOTFOUND'):     _status_color = "RED"
            elif (_status == 'CONFIGNOTFOUND'):       _status_color = "RED_LIGHT"
            elif (_status == 'WAITINGTRADING'):       _status_color = "ORANGE_LIGHT"
            elif (_status == 'WAITINGSTREAM'):        _status_color = "BLUE_DARK"
            elif (_status == 'WAITINGDATAAVAILABLE'): _status_color = "BLUE_LIGHT"
            elif (_status == 'PREP_QUEUED'):          _status_color = "BLUE_LIGHT"
            elif (_status == 'PREP_FETCHINGKLINES'):  _status_color = "BLUE_LIGHT"
            elif (_status == 'PREP_ANALYZINGKLINES'): _status_color = "BLUE_LIGHT"
            elif (_status == 'ANALYZINGREALTIME'):    _status_color = "GREEN_LIGHT"
            elif (_status == 'ERROR'):                _status_color = "RED_DARK"
            currencyAnalysis_selectionList[_caCode] = [{'text': "{:d} / {:d}".format(_index+1, nCAs),                                                                'textStyles': [('all', 'DEFAULT'),],     'textAnchor': 'CENTER'},
                                                       {'text': _caCode,                                                                                             'textStyles': [('all', 'DEFAULT'),],     'textAnchor': 'CENTER'},
                                                       {'text': _currencySymbol,                                                                                     'textStyles': [('all', 'DEFAULT'),],     'textAnchor': 'CENTER'},
                                                       {'text': self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_{:s}'.format(_status)), 'textStyles': [('all', _status_color),], 'textAnchor': 'CENTER'}]
        self.GUIOs["CURRENCYANALYSISLIST_SELECTIONBOX"].setSelectionList(selectionList = currencyAnalysis_selectionList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    auxFunctions['SETLIST'] = __setList

    #<Information>
    def __updateInformation():
        selectedCurrencyAnalysis_analysisCode = self.puVar['currencyAnalysis_selected']
        if (selectedCurrencyAnalysis_analysisCode == None):
            self.GUIOs["CURRENCYANALYSISLIST_CONFIGURATIONCODEDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["CURRENCYANALYSISLIST_ALLOCATEDANALYZERDISPLAYTEXT"].updateText(text = "-")
        else:
            selectedCurrencyAnalysis_info = self.puVar['currencyAnalysis'][selectedCurrencyAnalysis_analysisCode]
            selectedCurrencyAnalysis_configurationCode = selectedCurrencyAnalysis_info['currencyAnalysisConfigurationCode']
            selectedCurrencyAnalysis_allocatedAnalyzer = selectedCurrencyAnalysis_info['allocatedAnalyzer']
            self.GUIOs["CURRENCYANALYSISLIST_CONFIGURATIONCODEDISPLAYTEXT"].updateText(text = selectedCurrencyAnalysis_configurationCode)
            if (selectedCurrencyAnalysis_allocatedAnalyzer == None): self.GUIOs["CURRENCYANALYSISLIST_ALLOCATEDANALYZERDISPLAYTEXT"].updateText(text = "-")
            else:                                                    self.GUIOs["CURRENCYANALYSISLIST_ALLOCATEDANALYZERDISPLAYTEXT"].updateText(text = "ANALYZER {:d}".format(selectedCurrencyAnalysis_allocatedAnalyzer))
    auxFunctions['UPDATEINFORMATION'] = __updateInformation

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------