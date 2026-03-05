#ATM Modules
import atmEta_IPC
import atmEta_Constants
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
import time
import math
from datetime import datetime, timezone, tzinfo

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

#Local Formatter Functions
def statusToString(vm, status):
    vm_getTP = vm.getTextPack
    if status is None:
        status_str   = "-"
        status_color = 'BLUE_DARK'
    elif status == 'TRADING':
        status_str   = vm_getTP('MARKET:CURRENCYLIST_STATUS_TRADING')
        status_color = 'GREEN_LIGHT'
    elif status == 'SETTLING':
        status_str   = vm_getTP('MARKET:CURRENCYLIST_STATUS_SETTLING')
        status_color = 'RED_LIGHT'
    elif status == 'REMOVED':
        status_str   = vm_getTP('MARKET:CURRENCYLIST_STATUS_REMOVED')
        status_color = 'RED_DARK'
    else:
        status_str   = status
        status_color = 'ORANGE_LIGHT'
    return status_str, status_color

def collectingToString(collecting):
    if collecting:
        collecting_str   = 'TRUE'
        collecting_color = 'GREEN_LIGHT'
    else:
        collecting_str   = 'FALSE'
        collecting_color = 'ORANGE_LIGHT'
    return collecting_str, collecting_color

def firstIntervalToString(firstInterval):
    if firstInterval is None: return "-"
    else:                     return datetime.fromtimestamp(firstInterval, tz=timezone.utc).strftime("%Y/%m/%d %H:%M")

def aRangesToString(availableRanges):
    dt_fts = datetime.fromtimestamp
    tzUTC  = timezone.utc
    if availableRanges is None: 
        return "-"
    else:
        aRanges_str = []
        for aRange in availableRanges:
            begStr = dt_fts(aRange[0], tz=tzUTC).strftime('%Y/%m/%d %H:%M')
            endStr = dt_fts(aRange[1], tz=tzUTC).strftime('%Y/%m/%d %H:%M')
            aRanges_str.append(f"[{begStr} ~ {endStr}]")
        if len(aRanges_str) == 1: return aRanges_str[0]
        else:                     return ", ".join(aRanges_str)

def availabilityToString(availability):
    if availability is None:
        string   = "N/A"
        color = 'DEFAULT'
    else:
        string = f"{availability*100:.3f} %"
        if   availability == 0.000: color = 'GREY'
        elif availability <= 0.333: color = 'ORANGE_LIGHT'
        elif availability <= 0.666: color = 'BLUE_LIGHT'
        elif availability <  1.000: color = 'GREEN_LIGHT'
        else:                       color = 'GREEN'
    return string, color


#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
    self.puVar['currencies']                             = dict()
    self.puVar['currencies_availabilities']              = dict()
    self.puVar['currencies_availabilities_lastComputed'] = 0
    self.puVar['currencies_selected']                    = set()
    self.puVar['currencies_lastSortBy']                  = None

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
        self.GUIOs["TITLETEXT_DATABASE"] = textBox_typeA(**inst, groupOrder=1, xPos= 6000, yPos=8550, width=4000, height=400, style=None, text=self.visualManager.getTextPack('DATABASE:TITLE'), fontSize = 220, textInteractable = False)
        self.GUIOs["BUTTON_MOVETO_DASHBOARD"] = button_typeB(**inst,  groupOrder=2, xPos=  50, yPos=8650, width= 300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['PAGEMOVE_DASHBOARD'], image = 'dashboardIcon_512x512.png', imageSize = (225, 225), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        


        #<DB Main>
        self.GUIOs["BLOCKSUBTITLE_DBMAIN"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=8350, width=5700, height=200, style="styleA", text=self.visualManager.getTextPack('DATABASE:BLOCKTITLE_DBMAIN'), fontSize = 80)



        #<Currency List>
        self.GUIOs["BLOCKSUBTITLE_CURRENCYLIST"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=5900, yPos=8350, width=10000, height=200, style="styleA", text=self.visualManager.getTextPack('DATABASE:BLOCKTITLE_CURRENCYLIST'), fontSize = 80)
        #---Filter
        self.GUIOs["CURRENCYLIST_SEARCHTITLETEXT"]              = textBox_typeA(**inst,      groupOrder=1, xPos= 5900, yPos=8000, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_SEARCH'), fontSize=80, textInteractable=False)
        self.GUIOs["CURRENCYLIST_SEARCHTITLETEXTINPUTBOX"]      = textInputBox_typeA(**inst, groupOrder=1, xPos= 7000, yPos=8000, width=1700, height=250, style="styleA", text="",                                                             fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_CURRENCYLIST_SEARCHTEXT'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"]     = switch_typeC(**inst, groupOrder=1, xPos= 8800, yPos=8000, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_TRADINGTRUE'),     fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGTRUE'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"]    = switch_typeC(**inst, groupOrder=1, xPos= 9900, yPos=8000, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_TRADINGFALSE'),    fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGFALSE'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_COLLECTINGTRUE"]  = switch_typeC(**inst, groupOrder=1, xPos=11000, yPos=8000, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_COLLECTINGTRUE'),  fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_COLLECTINGTRUE'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_COLLECTINGFALSE"] = switch_typeC(**inst, groupOrder=1, xPos=12100, yPos=8000, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_COLLECTINGFALSE'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_COLLECTINGFALSE'])
        self.GUIOs["CURRENCYLIST_AUXBUTTON_SELECTALL"]  = button_typeA(**inst, groupOrder=1, xPos=13200, yPos=8000, width=1300, height= 250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_SELECTALL'),  fontSize=80, releaseFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SELECTALL'])
        self.GUIOs["CURRENCYLIST_AUXBUTTON_RELEASEALL"] = button_typeA(**inst, groupOrder=1, xPos=14600, yPos=8000, width=1300, height= 250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_RELEASEALL'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_RELEASEALL'])
        self.GUIOs["CURRENCYLIST_SORTBYTITLETEXT"]                       = textBox_typeA(**inst, groupOrder=1, xPos= 5900, yPos=7650, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_SORTBY'),             fontSize=80, textInteractable=False)
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYINDEX"]              = switch_typeC(**inst,  groupOrder=1, xPos= 7000, yPos=7650, width=1400, height=250, style="styleB", name="INDEX",              text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_INDEX'),              fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYSYMBOL"]             = switch_typeC(**inst,  groupOrder=1, xPos= 8500, yPos=7650, width=1400, height=250, style="styleB", name="SYMBOL",             text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_SYMBOL'),             fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYFIRSTINTERVAL"]      = switch_typeC(**inst,  groupOrder=1, xPos=10000, yPos=7650, width=1400, height=250, style="styleB", name="FIRSTINTERVAL",      text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL'),      fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYAVAILABILITY_KL"]    = switch_typeC(**inst,  groupOrder=1, xPos=11500, yPos=7650, width=1400, height=250, style="styleB", name="AVAILABILITY_KL",    text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABILITY_KL'),    fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYAVAILABILITY_DEPTH"] = switch_typeC(**inst,  groupOrder=1, xPos=13000, yPos=7650, width=1400, height=250, style="styleB", name="AVAILABILITY_DEPTH", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABILITY_DEPTH'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYAVAILABILITY_AT"]    = switch_typeC(**inst,  groupOrder=1, xPos=14500, yPos=7650, width=1400, height=250, style="styleB", name="AVAILABILITY_AT",    text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABILITY_AT'),    fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYINDEX"].setStatus(status = True, callStatusUpdateFunction = False)
        self.puVar['currencies_lastSortBy'] = 'INDEX'
        
        #---List
        self.GUIOs["CURRENCYLIST_SELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=1, xPos=5900, yPos=2200, width=10000, height=5350, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = True, singularSelect_allowRelease = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_CURRENCYLIST_CURRENCYSELECTION'], 
                                                                     elementWidths = (800, 1450, 700, 1200, 1200, 1200, 800, 800, 800, 800))
        self.GUIOs["CURRENCYLIST_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_INDEX')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_SYMBOL')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_STATUS')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL_KL')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL_DEPTH')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL_AT')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABILITY_KL')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABILITY_DEPTH')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABILITY_AT')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_COLLECTING')},
                                                                                 ])
        
        #---Information
        self.GUIOs["CURRENCYLIST_SYMBOLTITLETEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos= 5900, yPos=1850, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_SYMBOL'),     fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_SYMBOLDISPLAYTEXT"]     = textBox_typeA(**inst, groupOrder=1, xPos= 7000, yPos=1850, width=1700, height=250, style="styleA", text="-",                                                                fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_STATUSTITLETEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos= 8800, yPos=1850, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_STATUS'),     fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_STATUSDISPLAYTEXT"]     = textBox_typeA(**inst, groupOrder=1, xPos= 9900, yPos=1850, width=1700, height=250, style="styleA", text="-",                                                                fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_COLLECTINGTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos=11700, yPos=1850, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_COLLECTING'), fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_COLLECTINGDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=12800, yPos=1850, width=1000, height=250, style="styleA", text="-",                                                                fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_COLLECTINGSWITCH"]      = switch_typeB(**inst,  groupOrder=2, xPos=13900, yPos=1850, width= 500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSTATUSUPDATE_CURRENCYLIST_COLLECTINGSWITCH'])
        self.GUIOs["CURRENCYLIST_COLLECTINGSWITCH"].deactivate()
        self.GUIOs["CURRENCYLIST_RESETBUTTON"] = button_typeA(**inst, groupOrder=1, xPos=14500, yPos=1850, width=800, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_RESET'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_CURRENCYLIST_RESETBUTTON'])
        self.GUIOs["CURRENCYLIST_RESETSWITCH"] = switch_typeB(**inst, groupOrder=2, xPos=15400, yPos=1850, width=500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSTATUSUPDATE_CURRENCYLIST_RESETSWITCH']) 
        self.GUIOs["CURRENCYLIST_RESETBUTTON"].deactivate()
        self.GUIOs["CURRENCYLIST_RESETSWITCH"].deactivate()
        self.GUIOs["CURRENCYLIST_FIRSTINTERVALKLTITLETEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos= 5900, yPos=1500, width=1650, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL_KL_FULL'),    fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_FIRSTINTERVALKLDISPLAYTEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos= 7650, yPos=1500, width=1500, height=250, style="styleA", text="-",                                                                              fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_FIRSTINTERVALDEPTHTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 9250, yPos=1500, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL_DEPTH_FULL'), fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_FIRSTINTERVALDEPTHDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=11050, yPos=1500, width=1500, height=250, style="styleA", text="-",                                                                              fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_FIRSTINTERVALATTITLETEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos=12650, yPos=1500, width=1650, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL_AT_FULL'),    fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_FIRSTINTERVALATDISPLAYTEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos=14400, yPos=1500, width=1500, height=250, style="styleA", text="-",                                                                              fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABLERANGESKLTITLETEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos= 5900, yPos=1150, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABLERANGES_KL'),    fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABLERANGESKLDISPLAYTEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos= 8000, yPos=1150, width=6800, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABILITYKLDISPLAYTEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos=14900, yPos=1150, width=1000, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABLERANGESDEPTHTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 5900, yPos= 800, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABLERANGES_DEPTH'), fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABLERANGESDEPTHDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos= 8000, yPos= 800, width=6800, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABILITYDEPTHDISPLAYTEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos=14900, yPos= 800, width=1000, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABLERANGESATTITLETEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos= 5900, yPos= 450, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABLERANGES_AT'),    fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABLERANGESATDISPLAYTEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos= 8000, yPos= 450, width=6800, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABILITYATDISPLAYTEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos=14900, yPos= 450, width=1000, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)

        #<Message>
        self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=  100, yPos=100, width=15800, height=250, style="styleA", text="-", fontSize=80, textInteractable=False)

    elif (self.displaySpaceDefiner['ratio'] == '21:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 21000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
    elif (self.displaySpaceDefiner['ratio'] == '32:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 32000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
#SETUP PAGE <MAIN> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <LOAD> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageLoadFunction(self):
    #[1]: FAR Handlers Setup
    #---[1-1]: DATAMANAGER
    self.ipcA.addFARHandler('onCurrenciesUpdate', self.pageAuxillaryFunctions['_FAR_ONCURRENCIESUPDATE'], executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

    #[2]: PRD Read
    #---[2-1]: Currencies
    currencies_prd = self.ipcA.getPRD(processName = 'DATAMANAGER',  prdAddress = 'CURRENCIES')
    if currencies_prd is not None: self.puVar['currencies'] = currencies_prd.copy()

    #[3]: Currencies Availability Computation
    self.pageAuxillaryFunctions['COMPUTECURRENCIESAVAILABILITY']()

    #[4]: GUIO Update
    #---[4-1]: Currencies List Update
    self.pageAuxillaryFunctions['SETLIST']()
    #---[4-2]: Currencies Selected Currency Info Update
    self.pageAuxillaryFunctions['UPDATEINFORMATION']()
    #---[4-3]: Select & Release Buttons
    nSymbols  = len(self.puVar['currencies'])
    nSelected = len(self.puVar['currencies_selected'])
    if nSelected == nSymbols: self.GUIOs["CURRENCYLIST_AUXBUTTON_SELECTALL"].deactivate()
    else:                     self.GUIOs["CURRENCYLIST_AUXBUTTON_SELECTALL"].activate()
    if nSelected == 0: self.GUIOs["CURRENCYLIST_AUXBUTTON_RELEASEALL"].deactivate()
    else:              self.GUIOs["CURRENCYLIST_AUXBUTTON_RELEASEALL"].activate()
#SETUP PAGE <LOAD> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <ESCAPE> --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageEscapeFunction(self):
    for fID in ('onCurrenciesUpdate',):
        self.ipcA.removeFARHandler(functionID   = fID)
        self.ipcA.addDummyFARHandler(functionID = fID)
#SETUP PAGE <ESCAPE> END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <PROCESS> -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageProcessFunction(self, t_elapsed_ns, onLoad = False):
    #[1]: Currencies Availability Computation
    cac_lastComputed = self.puVar['currencies_availabilities_lastComputed']
    cac_this = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Constants.KLINTERVAL, 
                                                               timestamp  = int(time.time()), 
                                                               nTicks     = 0)
    if cac_lastComputed != cac_this:
        self.pageAuxillaryFunctions['COMPUTECURRENCIESAVAILABILITY'](updateSelectionBox = True)
        self.puVar['currencies_availabilities_lastComputed'] = cac_this
#SETUP PAGE <PROCESS> END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#OBJECT FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateObjectFunctions(self):
    objFunctions = dict()

    #<Page Navigation>
    def __pageMove_DASHBOARD(objInstance, **kwargs): 
        self.sysFunctions['LOADPAGE']('DASHBOARD')
    objFunctions['PAGEMOVE_DASHBOARD'] = __pageMove_DASHBOARD

    #<DB Main>

    #<Currency List>
    #---Filter
    def __onTextUpdate_CurrencyList_SearchText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_TradingTrue(objInstance, **kwargs):
        if self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"].getStatus(): self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_TradingFalse(objInstance, **kwargs):
        if self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"].getStatus(): self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onButtonRelease_CurrencyList_SelectAll(objInstance, **kwargs):
        selectionBox = self.GUIOs["CURRENCYLIST_SELECTIONBOX"]
        currencies   = self.puVar['currencies']
        nSymbols     = len(currencies)
        for idx, symbol in enumerate(currencies):
            if idx == nSymbols-1: callSelectionUpdateFunction = True
            else:                 callSelectionUpdateFunction = False
            selectionBox.addSelected(itemKey = symbol, callSelectionUpdateFunction = callSelectionUpdateFunction)
        objInstance.deactivate()
    def __onButtonRelease_CurrencyList_ReleaseAll(objInstance, **kwargs):
        self.GUIOs["CURRENCYLIST_SELECTIONBOX"].clearSelected()
        objInstance.deactivate()
    def __onSwitchStatusUpdate_CurrencyList_CollectingTrue(objInstance, **kwargs):
        if self.GUIOs["CURRENCYLIST_FILTERSWITCH_COLLECTINGFALSE"].getStatus(): self.GUIOs["CURRENCYLIST_FILTERSWITCH_COLLECTINGFALSE"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_CollectingFalse(objInstance, **kwargs):
        if self.GUIOs["CURRENCYLIST_FILTERSWITCH_COLLECTINGTRUE"].getStatus(): self.GUIOs["CURRENCYLIST_FILTERSWITCH_COLLECTINGTRUE"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_SortBy(objInstance, **kwargs):
        #[1]: Instances
        sType_prev = self.puVar['currencies_lastSortBy']
        sType_this = objInstance.getName()

        #[2]: Update Handling
        #---[2-1]: Same Switch (Turning Off Itself - Go Back To Index Sort)
        if sType_prev == sType_this:
            self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYINDEX"].setStatus(status = True, callStatusUpdateFunction = False)
            self.puVar['currencies_lastSortBy'] = 'INDEX'
        #---[2-2]: Different Switch (Turning On A Different Switch)
        else:
            self.GUIOs[f"CURRENCYLIST_FILTERSWITCH_SORTBY{sType_prev}"].setStatus(status = False, callStatusUpdateFunction = False)
            self.puVar['currencies_lastSortBy'] = sType_this

        #[3]: Filter Update
        if sType_prev != self.puVar['currencies_lastSortBy']:
            self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    objFunctions['ONTEXTUPDATE_CURRENCYLIST_SEARCHTEXT']              = __onTextUpdate_CurrencyList_SearchText
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGTRUE']     = __onSwitchStatusUpdate_CurrencyList_TradingTrue
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGFALSE']    = __onSwitchStatusUpdate_CurrencyList_TradingFalse
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SELECTALL']       = __onButtonRelease_CurrencyList_SelectAll
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_RELEASEALL']      = __onButtonRelease_CurrencyList_ReleaseAll
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_COLLECTINGTRUE']  = __onSwitchStatusUpdate_CurrencyList_CollectingTrue
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_COLLECTINGFALSE'] = __onSwitchStatusUpdate_CurrencyList_CollectingFalse
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY']          = __onSwitchStatusUpdate_CurrencyList_SortBy

    #---List
    def __onSelectionUpdate_CurrencyList_CurrencySelection(objInstance, **kwargs):
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs

        #[2]: Selected Currencies & Information Update
        puVar['currencies_selected'] = set(objInstance.getSelected())
        self.pageAuxillaryFunctions['UPDATEINFORMATION']()

        #[3]: Select & Release Buttons
        nSymbols  = len(puVar['currencies'])
        nSelected = len(puVar['currencies_selected'])
        if nSelected == nSymbols: guios["CURRENCYLIST_AUXBUTTON_SELECTALL"].deactivate()
        else:                     guios["CURRENCYLIST_AUXBUTTON_SELECTALL"].activate()
        if nSelected == 0: guios["CURRENCYLIST_AUXBUTTON_RELEASEALL"].deactivate()
        else:              guios["CURRENCYLIST_AUXBUTTON_RELEASEALL"].activate()

        #[4]: Reset Buttons
        guios["CURRENCYLIST_RESETBUTTON"].deactivate()
        guios["CURRENCYLIST_RESETSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
        if 0 < nSelected: guios["CURRENCYLIST_RESETSWITCH"].activate()
        else:             guios["CURRENCYLIST_RESETSWITCH"].deactivate()
    objFunctions['ONSELECTIONUPDATE_CURRENCYLIST_CURRENCYSELECTION'] = __onSelectionUpdate_CurrencyList_CurrencySelection

    #---Information
    def __onStatusUpdate_CurrencyList_CollectingSwitch(objInstance, **kwargs):
        symbols = list(self.puVar['currencies_selected'])
        print("SHUT DOWN BOI")
    def __onButtonRelease_CurrencyList_ResetButton(objInstance, **kwargs):
        symbols = list(self.puVar['currencies_selected'])
        print("RESET BOI")
    def __onStatusUpdate_CurrencyList_ResetSwitch(objInstance, **kwargs):
        status      = objInstance.getStatus()
        resetButton = self.GUIOs["CURRENCYLIST_RESETBUTTON"]
        if status: resetButton.activate()
        else:      resetButton.deactivate()
    objFunctions['ONSTATUSUPDATE_CURRENCYLIST_COLLECTINGSWITCH'] = __onStatusUpdate_CurrencyList_CollectingSwitch
    objFunctions['ONBUTTONRELEASE_CURRENCYLIST_RESETBUTTON']     = __onButtonRelease_CurrencyList_ResetButton
    objFunctions['ONSTATUSUPDATE_CURRENCYLIST_RESETSWITCH']      = __onStatusUpdate_CurrencyList_ResetSwitch

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()

    #<_PAGELOAD>
    def __far_onCurrenciesUpdate(requester, updatedContents):
        #[1]: Source Check
        if requester != 'DATAMANAGER':
            return
        
        #[2]: Instances
        vm     = self.visualManager
        puVar  = self.puVar
        guios  = self.GUIOs
        getPRD = self.ipcA.getPRD
        currencies                = puVar['currencies']
        currencies_availabilities = puVar['currencies_availabilities']
        selectionBox = self.GUIOs["CURRENCYLIST_SELECTIONBOX"]
        func_cca = self.pageAuxillaryFunctions['COMPUTECURRENCIESAVAILABILITY']
        
        #[3]: Reset Flags
        resetList         = False
        reapplyListFilter = False

        #[4]: Updates Read
        checkList_singular = {'kline_firstOpenTS', 'depth_firstOpenTS', 'aggTrade_firstOpenTS', 'klines_availableRanges', 'depths_availableRanges', 'aggTrades_availableRanges'}
        for updatedContent in updatedContents:
            #[4-1]: Instances
            symbol    = updatedContent['symbol']
            contentID = updatedContent['id']

            #[4-2]: New Currency
            if contentID == '_ADDED':
                currencies[symbol] = getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol))
                resetList = True

            #[4-3]: Existing Currency Update
            else:
                #[4-3-1]: Instances & Updated Contents
                currencies_symbol = currencies[symbol]
                cID_0             = contentID[0]
                updated           = set()

                #[4-3-2]: Updates Check
                #---[4-3-2-1]: Currency Server Information Updated (Status)
                if contentID[0] == 'info_server': 
                    try:    cID_1 = contentID[1]
                    except: cID_1 = None
                    #[4-3-2-1-1]: Entire Server Information Updated
                    if cID_1 is None:
                        currencies_symbol['info_server'] = getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server'))
                        updated.add('status')
                    #[4-3-2-1-2]: Currency Status Updated
                    else:
                        if cID_1 == 'status': 
                            currencies_symbol['info_server']['status'] = getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server', 'status'))
                            updated.add('status')
                #---[4-3-2-2]: Singular Address Expected Updated
                elif cID_0 in checkList_singular:
                    currencies_symbol[cID_0] = getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, cID_0))
                    updated.add(cID_0)

                #[4-3-3]: Updates Response
                updateInformation = (symbol in puVar['currencies_selected'] and len(puVar['currencies_selected']) == 1)
                for u in updated:
                    #[4-3-3-1]: Status
                    if u == 'status':
                        info_server = currencies_symbol['info_server']
                        status = None if info_server is None else info_server['status']
                        status_str, status_color = statusToString(vm = vm, status = status)
                        nsbi = {'text':       status_str, 
                                'textStyles': [('all', status_color),], 
                                'textAnchor': 'CENTER'}
                        selectionBox.editSelectionListItem(itemKey = symbol, item = nsbi, columnIndex = 2)
                        reapplyListFilter = True
                        if updateInformation:
                            guios["CURRENCYLIST_STATUSDISPLAYTEXT"].updateText(text = status_str, textStyle = status_color)

                    #[4-3-3-2]: Kline First Interval
                    elif u == 'kline_firstOpenTS':
                        fi_str = firstIntervalToString(firstInterval = currencies_symbol['kline_firstOpenTS'])
                        nsbi = {'text': fi_str, 
                                'textStyles': [('all', 'DEFAULT'),], 
                                'textAnchor': 'CENTER'}
                        selectionBox.editSelectionListItem(itemKey = symbol, item = nsbi, columnIndex = 3)
                        reapplyListFilter = True
                        if updateInformation:
                            guios["CURRENCYLIST_FIRSTINTERVALKLDISPLAYTEXT"].updateText(text = fi_str)

                    #[4-3-3-3]: Depth First Interval
                    elif u == 'depth_firstOpenTS':
                        fi_str = firstIntervalToString(firstInterval = currencies_symbol['depth_firstOpenTS'])
                        nsbi = {'text': fi_str, 
                                'textStyles': [('all', 'DEFAULT'),], 
                                'textAnchor': 'CENTER'}
                        selectionBox.editSelectionListItem(itemKey = symbol, item = nsbi, columnIndex = 4)
                        reapplyListFilter = True
                        if updateInformation:
                            guios["CURRENCYLIST_FIRSTINTERVALDEPTHDISPLAYTEXT"].updateText(text = fi_str)

                    #[4-3-3-4]: AggTrade First Interval
                    elif u == 'aggTrade_firstOpenTS':
                        fi_str = firstIntervalToString(firstInterval = currencies_symbol['aggTrade_firstOpenTS'])
                        nsbi = {'text': fi_str, 
                                'textStyles': [('all', 'DEFAULT'),], 
                                'textAnchor': 'CENTER'}
                        selectionBox.editSelectionListItem(itemKey = symbol, item = nsbi, columnIndex = 5)
                        reapplyListFilter = True
                        if updateInformation:
                            guios["CURRENCYLIST_FIRSTINTERVALATDISPLAYTEXT"].updateText(text = fi_str)

                    #[4-3-3-5]: Klines Available Ranges
                    elif u == 'klines_availableRanges':
                        func_cca(symbols = [symbol,], targets = ['kline',], updateSelectionBox = True)
                        if updateInformation:
                            guios["CURRENCYLIST_AVAILABLERANGESKLDISPLAYTEXT"].updateText(text = aRangesToString(availableRanges = currencies_symbol['klines_availableRanges']))
                            avail_str, avail_color = availabilityToString(availability = currencies_availabilities[symbol]['kline'])
                            guios["CURRENCYLIST_AVAILABILITYKLDISPLAYTEXT"].updateText(text = avail_str, textStyle = avail_color)

                    #[4-3-3-6]: Depths Available Ranges
                    elif u == 'depths_availableRanges':
                        func_cca(symbols = [symbol,], targets = ['depth',], updateSelectionBox = True)
                        if updateInformation:
                            guios["CURRENCYLIST_AVAILABLERANGESDEPTHDISPLAYTEXT"].updateText(text = aRangesToString(availableRanges = currencies_symbol['depths_availableRanges']))
                            avail_str, avail_color = availabilityToString(availability = currencies_availabilities[symbol]['depth'])
                            guios["CURRENCYLIST_AVAILABILITYDEPTHDISPLAYTEXT"].updateText(text = avail_str, textStyle = avail_color)

                    #[4-3-3-7]: AggTrades Available Ranges
                    elif u == 'aggTrades_availableRanges':
                        func_cca(symbols = [symbol,], targets = ['aggTrade',], updateSelectionBox = True)
                        if updateInformation:
                            guios["CURRENCYLIST_AVAILABLERANGESATDISPLAYTEXT"].updateText(text = aRangesToString(availableRanges = currencies_symbol['aggTrades_availableRanges']))
                            avail_str, avail_color = availabilityToString(availability = currencies_availabilities[symbol]['aggTrade'])
                            guios["CURRENCYLIST_AVAILABILITYATDISPLAYTEXT"].updateText(text = avail_str, textStyle = avail_color)

        #[5]: Reset
        if resetList:
            self.pageAuxillaryFunctions['COMPUTECURRENCIESAVAILABILITY'](updateSelectionBox = False)
            self.pageAuxillaryFunctions['SETLIST']()
        elif reapplyListFilter: 
            self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    auxFunctions['_FAR_ONCURRENCIESUPDATE'] = __far_onCurrenciesUpdate

    #<Currency List>
    #---Filter
    def __onFilterUpdate():
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        currencies                = puVar['currencies']
        currencies_availabilities = puVar['currencies_availabilities']

        #[2]: Read Filters
        filter_symbol = guios["CURRENCYLIST_SEARCHTITLETEXTINPUTBOX"].getText()
        filter_trading = None
        if   guios["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"].getStatus():  filter_trading = True
        elif guios["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"].getStatus(): filter_trading = False
        filter_collecting = None
        if   guios["CURRENCYLIST_FILTERSWITCH_COLLECTINGTRUE"].getStatus():  filter_collecting = True
        elif guios["CURRENCYLIST_FILTERSWITCH_COLLECTINGFALSE"].getStatus(): filter_collecting = False
        filter_sort = puVar['currencies_lastSortBy']

        #[3]: Filter symbols
        symbols          = list(currencies)
        symbols_filtered = list()
        for symbol in symbols:
            currencies_symbol = currencies[symbol]
            #[3-1]: Symbol Filter
            if filter_symbol not in symbol: 
                continue
            #[3-2]: Status Filter
            if filter_trading is not None:
                symbol_info_server = currencies_symbol['info_server']
                if filter_trading:
                    if symbol_info_server is None or symbol_info_server['status'] != 'TRADING':
                        continue
                else:
                    if symbol_info_server is not None and symbol_info_server['status'] == 'TRADING': 
                        continue
            #[3-3]: Collecting Filter
            if filter_collecting is not None:
                collecting = currencies_symbol['collecting']
                if filter_collecting:
                    if not collecting:
                        continue
                else:
                    if collecting:
                        continue
            #[3-4]: Finally
            symbols_filtered.append(symbol)

        #[4]: Sort Symbols
        #---[4-1]: Index Sort
        if filter_sort == 'INDEX':              
            symbols_forSort = symbols_filtered

        #---[4-2]: Symbol Sort
        elif filter_sort == 'SYMBOL':             
            symbols_forSort = symbols_filtered

        #---[4-3]: First Interval Sort
        elif filter_sort == 'FIRSTINTERVAL':
            symbols_forSort = []
            for symbol in symbols_filtered:
                currencies_symbol = currencies[symbol]
                fdot_kl    = currencies_symbol['kline_firstOpenTS']
                fdot_depth = currencies_symbol['depth_firstOpenTS']
                fdot_at    = currencies_symbol['aggTrade_firstOpenTS']
                if fdot_kl    is None: fdot_kl    = float('inf')
                if fdot_depth is None: fdot_depth = float('inf')
                if fdot_at    is None: fdot_at    = float('inf')
                fdot = min(fdot_kl, fdot_depth, fdot_at)
                symbols_forSort.append((symbol, fdot))
                
        #---[4-4]: Kline Availability Sort
        elif filter_sort == 'AVAILABILITY_KL':
            symbols_forSort = []
            for symbol in symbols_filtered:
                avail = currencies_availabilities[symbol]['kline']
                if avail is None: avail = float('-inf')
                symbols_forSort.append((symbol, avail))

        #---[4-5]: Kline Availability Sort
        elif filter_sort == 'AVAILABILITY_DEPTH':
            symbols_forSort = []
            for symbol in symbols_filtered:
                avail = currencies_availabilities[symbol]['depth']
                if avail is None: avail = float('-inf')
                symbols_forSort.append((symbol, avail))

        #---[4-6]: Kline Availability Sort
        elif filter_sort == 'AVAILABILITY_AT':
            symbols_forSort = []
            for symbol in symbols_filtered:
                avail = currencies_availabilities[symbol]['aggTrade']
                if avail is None: avail = float('-inf')
                symbols_forSort.append((symbol, avail))

        #---[4-2]: Sort
        if   filter_sort == 'INDEX':              symbols_filteredAndSorted = symbols_forSort
        elif filter_sort == 'SYMBOL':             symbols_filteredAndSorted = sorted(symbols_forSort)
        elif filter_sort == 'FIRSTINTERVAL':      symbols_filteredAndSorted = [sp[0] for sp in sorted(symbols_forSort, key = lambda x: x[1])]
        elif filter_sort == 'AVAILABILITY_KL':    symbols_filteredAndSorted = [sp[0] for sp in sorted(symbols_forSort, key = lambda x: x[1], reverse = True)]
        elif filter_sort == 'AVAILABILITY_DEPTH': symbols_filteredAndSorted = [sp[0] for sp in sorted(symbols_forSort, key = lambda x: x[1], reverse = True)]
        elif filter_sort == 'AVAILABILITY_AT':    symbols_filteredAndSorted = [sp[0] for sp in sorted(symbols_forSort, key = lambda x: x[1], reverse = True)]

        #[5]: Selection Box Update
        guios["CURRENCYLIST_SELECTIONBOX"].setDisplayTargets(displayTargets = symbols_filteredAndSorted, resetViewPosition = False)
    auxFunctions['ONFILTERUPDATE'] = __onFilterUpdate

    #---List
    def __setList():
        #[1]: Instances
        vm    = self.visualManager
        puVar = self.puVar
        guios = self.GUIOs
        currencies                = puVar['currencies']
        currencies_availabilities = puVar['currencies_availabilities']

        #[2]: Selection List Formatting
        sl           = dict()
        nCurrencies  = len(currencies)
        for cIndex, symbol in enumerate(currencies):
            #[2-1]: Instances
            currencies_symbol                = currencies[symbol]
            currencies_availabilities_symbol = currencies_availabilities[symbol]

            #[2-2]: Index
            idx_str   = f"{cIndex+1} / {nCurrencies}"
            idx_color = 'DEFAULT'

            #[2-3]: Symbol
            symbol_str   = symbol
            symbol_color = 'DEFAULT'

            #[2-4]: Status
            info_server = currencies_symbol['info_server']
            status = None if info_server is None else info_server['status']
            status_str, status_color = statusToString(vm = vm, status = status)

            #[2-5]: First Interval - Kline
            fi_kl = currencies_symbol['kline_firstOpenTS']
            fi_kl_str   = firstIntervalToString(firstInterval = fi_kl)
            fi_kl_color = 'DEFAULT'

            #[2-6]: First Interval - Depth
            fi_depth = currencies_symbol['depth_firstOpenTS']
            fi_depth_str   = firstIntervalToString(firstInterval = fi_depth)
            fi_depth_color = 'DEFAULT'

            #[2-7]: First Interval - AggTrade
            fi_at = currencies_symbol['aggTrade_firstOpenTS']
            fi_at_str   = firstIntervalToString(firstInterval = fi_at)
            fi_at_color = 'DEFAULT'

            #[2-8]: Availability - Kline
            avail_kl = currencies_availabilities_symbol['kline']
            avail_kl_str, avail_kl_color = availabilityToString(availability = avail_kl)

            #[2-9]: Availability - Depth
            avail_depth = currencies_availabilities_symbol['depth']
            avail_depth_str, avail_depth_color = availabilityToString(availability = avail_depth)

            #[2-10]: Availability - AggTrade
            avail_at = currencies_availabilities_symbol['aggTrade']
            avail_at_str, avail_at_color = availabilityToString(availability = avail_at)
            
            #[2-11]: Collecting
            collecting = currencies_symbol['collecting']
            collecting_str, collecting_color = collectingToString(collecting = collecting)

            #[2-12]: Finally
            sl[symbol] = [{'text': idx_str,         'textStyles': [('all', idx_color),],         'textAnchor': 'CENTER'},
                          {'text': symbol_str,      'textStyles': [('all', symbol_color),],      'textAnchor': 'CENTER'},
                          {'text': status_str,      'textStyles': [('all', status_color),],      'textAnchor': 'CENTER'},
                          {'text': fi_kl_str,       'textStyles': [('all', fi_kl_color),],       'textAnchor': 'CENTER'},
                          {'text': fi_depth_str,    'textStyles': [('all', fi_depth_color),],    'textAnchor': 'CENTER'},
                          {'text': fi_at_str,       'textStyles': [('all', fi_at_color),],       'textAnchor': 'CENTER'},
                          {'text': avail_kl_str,    'textStyles': [('all', avail_kl_color),],    'textAnchor': 'CENTER'}, #Availabilities Are Updated Separately
                          {'text': avail_depth_str, 'textStyles': [('all', avail_depth_color),], 'textAnchor': 'CENTER'}, #Availabilities Are Updated Separately
                          {'text': avail_at_str,    'textStyles': [('all', avail_at_color),],    'textAnchor': 'CENTER'}, #Availabilities Are Updated Separately
                          {'text': collecting_str,  'textStyles': [('all', collecting_color),],  'textAnchor': 'CENTER'},
                          ]
            
        #[3]: Update Selection Box & Apply Filter
        guios["CURRENCYLIST_SELECTIONBOX"].setSelectionList(selectionList = sl, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __computeCurrenciesAvailability(symbols = None, targets = None, updateSelectionBox = False):
        #[1]: Instances
        puVar   = self.puVar
        sb_esli = self.GUIOs["CURRENCYLIST_SELECTIONBOX"].editSelectionListItem
        currencies                = puVar['currencies']
        currencies_availabilities = puVar['currencies_availabilities']

        #[2]: Update Targets
        if symbols is None: symbols = currencies.keys()
        if targets is None: targets = ['kline', 'depth', 'aggTrade']

        #[3]: Availabilities Update
        #---[3-1]: Current Interval End
        t_current = int(time.time())
        tEnd_current = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Constants.KLINTERVAL, 
                                                                       timestamp  = t_current, 
                                                                       nTicks     = 0)-1
        
        #---[3-2]: Selection Box Item Index
        sbiIdx = {'kline': 6, 'depth': 7, 'aggTrade': 8}

        #---[3-2]: Availabilities Computation & SelectionBox Update (If Needed)
        for symbol in symbols:
            #[3-2-1]: Instances
            if symbol not in currencies_availabilities: currencies_availabilities[symbol] = {'kline': None, 'depth': None, 'aggTrade': None}
            currencies_symbol                = currencies[symbol]
            currencies_availabilities_symbol = currencies_availabilities[symbol]

            #[3-2-2]: Availabilities Computation
            for target in targets:
                #[3-2-2-1]: Previous Availability
                availability_prev = currencies_availabilities_symbol[target]

                #[3-2-2-2]: New Availability
                fi      = currencies_symbol[f'{target}_firstOpenTS']
                aRanges = currencies_symbol[f'{target}s_availableRanges']
                if fi is None or aRanges is None:
                    availability = None
                else:
                    tWidth = tEnd_current-fi+1
                    aWidth = sum(aRange[1]-aRange[0]+1 for aRange in aRanges)
                    if tWidth == aWidth: availability = 1.0
                    else:                availability = math.floor(aWidth/tWidth*1e5)/1e5
                currencies_availabilities_symbol[target] = availability

                #[3-2-2-3]: SelectionBox Update
                if updateSelectionBox and availability_prev != availability:
                    if availability is None:
                        avail_str   = "N/A"
                        avail_color = 'DEFAULT'
                    else:
                        avail_str = f"{availability*100:.3f} %"
                        if   availability == 0.000: avail_color = 'GREY'
                        elif availability <= 0.333: avail_color = 'ORANGE_LIGHT'
                        elif availability <= 0.666: avail_color = 'BLUE_LIGHT'
                        elif availability <  1.000: avail_color = 'GREEN_LIGHT'
                        else:                       avail_color = 'GREEN'
                    sbi_new = {'text':       avail_str, 
                               'textStyles': [('all', avail_color),], 
                               'textAnchor': 'CENTER'}
                    sb_esli(itemKey = symbol, item = sbi_new, columnIndex = sbiIdx[target])
    auxFunctions['COMPUTECURRENCIESAVAILABILITY'] = __computeCurrenciesAvailability
    auxFunctions['SETLIST']                       = __setList

    #---Information
    def __farr_onAnalysisAddRequestResponse(responder, requestID, functionResult):
        pass
    def __updateInformation():
        #[1]: Instances
        vm    = self.visualManager
        guios = self.GUIOs
        puVar = self.puVar
        currencies                = puVar['currencies']
        currencies_availabilities = puVar['currencies_availabilities']
        symbols    = list(puVar['currencies_selected'])
        nSymbols   = len(symbols)

        #[2]: GUIOs Update
        #---[2-1]: No Symbol Selected
        if nSymbols == 0:
            guios["CURRENCYLIST_SYMBOLDISPLAYTEXT"].updateText(text     = "-")
            guios["CURRENCYLIST_STATUSDISPLAYTEXT"].updateText(text     = "-")
            guios["CURRENCYLIST_COLLECTINGDISPLAYTEXT"].updateText(text = "-")
            guios["CURRENCYLIST_COLLECTINGSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
            guios["CURRENCYLIST_COLLECTINGSWITCH"].deactivate()
            guios["CURRENCYLIST_FIRSTINTERVALKLDISPLAYTEXT"].updateText(text      = "-")
            guios["CURRENCYLIST_FIRSTINTERVALDEPTHDISPLAYTEXT"].updateText(text   = "-")
            guios["CURRENCYLIST_FIRSTINTERVALATDISPLAYTEXT"].updateText(text      = "-")
            guios["CURRENCYLIST_AVAILABLERANGESKLDISPLAYTEXT"].updateText(text    = "-")
            guios["CURRENCYLIST_AVAILABILITYKLDISPLAYTEXT"].updateText(text       = "-")
            guios["CURRENCYLIST_AVAILABLERANGESDEPTHDISPLAYTEXT"].updateText(text = "-")
            guios["CURRENCYLIST_AVAILABILITYDEPTHDISPLAYTEXT"].updateText(text    = "-")
            guios["CURRENCYLIST_AVAILABLERANGESATDISPLAYTEXT"].updateText(text    = "-")
            guios["CURRENCYLIST_AVAILABILITYATDISPLAYTEXT"].updateText(text       = "-")

        #---[2-2]: One Symbol Selected
        elif nSymbols == 1:
            symbol = symbols[0]
            currencies_symbol                = currencies[symbol]
            currencies_availabilities_symbol = currencies_availabilities[symbol]
            #[2-2-1]: Symbol
            guios["CURRENCYLIST_SYMBOLDISPLAYTEXT"].updateText(text = symbol)

            #[2-2-2]: Status
            info_server = currencies_symbol['info_server']
            status = None if info_server is None else info_server['status']
            status_str, status_color = statusToString(vm = vm, status = status)
            guios["CURRENCYLIST_STATUSDISPLAYTEXT"].updateText(text = status_str, textStyle = status_color)

            #[2-2-3]: Collecting
            collecting = currencies_symbol['collecting']
            collecting_str, collecting_color = collectingToString(collecting = collecting)
            guios["CURRENCYLIST_COLLECTINGDISPLAYTEXT"].updateText(text = collecting_str, textStyle = collecting_color)
            guios["CURRENCYLIST_COLLECTINGSWITCH"].setStatus(status = collecting, callStatusUpdateFunction = False)
            guios["CURRENCYLIST_COLLECTINGSWITCH"].activate()

            #[2-2-4]: First Intervals
            fi_kl    = currencies_symbol['kline_firstOpenTS']
            fi_depth = currencies_symbol['depth_firstOpenTS']
            fi_at    = currencies_symbol['aggTrade_firstOpenTS']
            fi_kl_str    = firstIntervalToString(firstInterval = fi_kl)
            fi_depth_str = firstIntervalToString(firstInterval = fi_depth)
            fi_at_str    = firstIntervalToString(firstInterval = fi_at)
            guios["CURRENCYLIST_FIRSTINTERVALKLDISPLAYTEXT"].updateText(text    = fi_kl_str)
            guios["CURRENCYLIST_FIRSTINTERVALDEPTHDISPLAYTEXT"].updateText(text = fi_depth_str)
            guios["CURRENCYLIST_FIRSTINTERVALATDISPLAYTEXT"].updateText(text    = fi_at_str)

            #[2-2-5]: Available Ranges
            aRanges_kl    = currencies_symbol['klines_availableRanges']
            aRanges_depth = currencies_symbol['depths_availableRanges']
            aRanges_at    = currencies_symbol['aggTrades_availableRanges']
            guios["CURRENCYLIST_AVAILABLERANGESKLDISPLAYTEXT"].updateText(text    = aRangesToString(availableRanges = aRanges_kl))
            guios["CURRENCYLIST_AVAILABLERANGESDEPTHDISPLAYTEXT"].updateText(text = aRangesToString(availableRanges = aRanges_depth))
            guios["CURRENCYLIST_AVAILABLERANGESATDISPLAYTEXT"].updateText(text    = aRangesToString(availableRanges = aRanges_at))

            #[2-2-6]: Availabilities
            avail_kl    = currencies_availabilities_symbol['kline']
            avail_depth = currencies_availabilities_symbol['depth']
            avail_at    = currencies_availabilities_symbol['aggTrade']
            avail_kl_str,    avail_kl_color    = availabilityToString(availability = avail_kl)
            avail_depth_str, avail_depth_color = availabilityToString(availability = avail_depth)
            avail_at_str,    avail_at_color    = availabilityToString(availability = avail_at)
            guios["CURRENCYLIST_AVAILABILITYKLDISPLAYTEXT"].updateText(text    = avail_kl_str,    textStyle = avail_kl_color)
            guios["CURRENCYLIST_AVAILABILITYDEPTHDISPLAYTEXT"].updateText(text = avail_depth_str, textStyle = avail_depth_color)
            guios["CURRENCYLIST_AVAILABILITYATDISPLAYTEXT"].updateText(text    = avail_at_str,    textStyle = avail_at_color)

        #---[2-3]: More Than One Symbols Selected
        else:
            guios["CURRENCYLIST_SYMBOLDISPLAYTEXT"].updateText(text = f"{symbols[0]} and {nSymbols-1} Others")
            collecting = all(currencies[symbol]['collecting'] for symbol in symbols)
            collecting_str, collecting_color = collectingToString(collecting = collecting)
            guios["CURRENCYLIST_COLLECTINGDISPLAYTEXT"].updateText(text = collecting_str, textStyle = collecting_color)
            guios["CURRENCYLIST_COLLECTINGSWITCH"].setStatus(status = collecting, callStatusUpdateFunction = False)
            guios["CURRENCYLIST_COLLECTINGSWITCH"].activate()
            guios["CURRENCYLIST_STATUSDISPLAYTEXT"].updateText(text               = "-")
            guios["CURRENCYLIST_FIRSTINTERVALKLDISPLAYTEXT"].updateText(text      = "-")
            guios["CURRENCYLIST_FIRSTINTERVALDEPTHDISPLAYTEXT"].updateText(text   = "-")
            guios["CURRENCYLIST_FIRSTINTERVALATDISPLAYTEXT"].updateText(text      = "-")
            guios["CURRENCYLIST_AVAILABLERANGESKLDISPLAYTEXT"].updateText(text    = "-")
            guios["CURRENCYLIST_AVAILABILITYKLDISPLAYTEXT"].updateText(text       = "-")
            guios["CURRENCYLIST_AVAILABLERANGESDEPTHDISPLAYTEXT"].updateText(text = "-")
            guios["CURRENCYLIST_AVAILABILITYDEPTHDISPLAYTEXT"].updateText(text    = "-")
            guios["CURRENCYLIST_AVAILABLERANGESATDISPLAYTEXT"].updateText(text    = "-")
            guios["CURRENCYLIST_AVAILABILITYATDISPLAYTEXT"].updateText(text       = "-")
    auxFunctions['_FARR_ONANALYSISADDREQUESTRESPONSE'] = __farr_onAnalysisAddRequestResponse
    auxFunctions['UPDATEINFORMATION'] = __updateInformation

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------