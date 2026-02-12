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
from datetime import datetime, timezone, tzinfo

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
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
        self.GUIOs["TITLETEXT_MARKET"] = textBox_typeA(**inst, groupOrder=1, xPos= 7000, yPos=8550, width=2000, height=400, style=None, text=self.visualManager.getTextPack('MARKET:TITLE'), fontSize = 220, textInteractable = False)

        self.GUIOs["BUTTON_MOVETO_DASHBOARD"] = button_typeB(**inst,  groupOrder=2, xPos=  50, yPos=8650, width= 300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['PAGEMOVE_DASHBOARD'], image = 'dashboardIcon_512x512.png', imageSize = (225, 225), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))

        #Currency List
        self.GUIOs["BLOCKSUBTITLE_FILTER"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=8350, width=4100, height=200, style="styleA", text=self.visualManager.getTextPack('MARKET:BLOCKTITLE_CURRENCYLIST'), fontSize = 80)
        #---Filter
        self.GUIOs["CURRENCYLIST_SEARCHTITLETEXT"]                            = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=8000, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_SEARCH'),            fontSize=80, textInteractable=False)
        self.GUIOs["CURRENCYLIST_SEARCHTITLETEXTINPUTBOX"]                    = textInputBox_typeA(**inst, groupOrder=1, xPos= 900, yPos=8000, width=3300, height=250, style="styleA", text="",                                                                      fontSize=80, textUpdateFunction  =self.pageObjectFunctions['ONTEXTUPDATE_CURRENCYLIST_SEARCHTEXT'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"]                   = switch_typeC(**inst,       groupOrder=1, xPos= 100, yPos=7650, width= 900, height=250, style="styleB", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_TRADINGTRUE'),       fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGTRUE'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"]                  = switch_typeC(**inst,       groupOrder=1, xPos=1100, yPos=7650, width= 900, height=250, style="styleB", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_TRADINGFALSE'),      fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGFALSE'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_MINNUMBEROFKLINES"]             = switch_typeC(**inst,       groupOrder=1, xPos=2100, yPos=7650, width=1300, height=250, style="styleB", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_MINNUMBEROFKLINES'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_MINNUMBEROFKLINES'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_MINNUMBEROFKLINESTEXTINPUTBOX"] = textInputBox_typeA(**inst, groupOrder=1, xPos=3500, yPos=7650, width= 700, height=250, style="styleA", text="",                                                                      fontSize=80, textUpdateFunction  =self.pageObjectFunctions['ONTEXTUPDATE_CURRENCYLIST_MINNUMBEROFKLINES'])
        self.GUIOs["CURRENCYLIST_SORTBYTITLETEXT"]                            = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=7300, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_SORTBY'),            fontSize=80, textInteractable    =False)
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYID"]                      = switch_typeC(**inst,       groupOrder=1, xPos= 900, yPos=7300, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_ID'),                fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBYID'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYSYMBOL"]                  = switch_typeC(**inst,       groupOrder=1, xPos=2000, yPos=7300, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_SYMBOL'),            fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBYSYMBOL'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYFIRSTKLINE"]              = switch_typeC(**inst,       groupOrder=1, xPos=3100, yPos=7300, width=1100, height=250, style="styleB", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_FIRSTKLINE'),        fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBYFIRSTKLINE'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYID"].setStatus(status = True, callStatusUpdateFunction = False)
        #---List
        self.GUIOs["CURRENCYLIST_SELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=1, xPos=100, yPos=800, width=4100, height=6400, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_CURRENCYLIST_CURRENCYSELECTION'], elementWidths = (700, 1150, 950, 1050))
        self.GUIOs["CURRENCYLIST_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('MARKET:CURRENCYLIST_INDEX')},
                                                                                 {'text': self.visualManager.getTextPack('MARKET:CURRENCYLIST_SYMBOL')},
                                                                                 {'text': self.visualManager.getTextPack('MARKET:CURRENCYLIST_STATUS')},
                                                                                 {'text': self.visualManager.getTextPack('MARKET:CURRENCYLIST_FIRSTKLINE')}])
        #---Information
        self.GUIOs["CURRENCYLIST_CURRENCYIDTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=450, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_CURRENCYID'), fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_CURRENCYIDDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=1200, yPos=450, width=3000, height=250, style="styleA", text="-",                                                              fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_DATARANGETITLETEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=100, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_DATARANGE'),  fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_DATARANGEDISPLAYTEXT"]  = textBox_typeA(**inst, groupOrder=1, xPos=1200, yPos=100, width=3000, height=250, style="styleA", text="-",                                                              fontSize=80, textInteractable=True)

        #Chart
        self.GUIOs["BLOCKSUBTITLE_CHART"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=4300, yPos=8350, width=11600, height=200, style="styleA", text=self.visualManager.getTextPack('MARKET:BLOCKTITLE_CHART'), fontSize = 80)
        self.GUIOs["CHART_CHARTDRAWER"] = chartDrawer(**inst, groupOrder=1, xPos=4300, yPos=100, width=11600, height=8150, style="styleA", name = 'MARKET_CHARTDRAWER', chartDrawerType = 'ANALYZER')

    elif (self.displaySpaceDefiner['ratio'] == '21:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 21000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
    elif (self.displaySpaceDefiner['ratio'] == '32:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 32000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
#SETUP PAGE <MAIN> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <LOAD> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageLoadFunction(self):#FAR Registration
    #---DATAMANAGER
    self.ipcA.addFARHandler('onCurrenciesUpdate', self.pageAuxillaryFunctions['_FAR_ONCURRENCIESUPDATE'], executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

    #Get data via PRD
    currencies_prd = self.ipcA.getPRD(processName = 'DATAMANAGER',  prdAddress = 'CURRENCIES')
    if currencies_prd is not None: self.puVar['currencies'] = currencies_prd.copy()

    #GUIO Update
    #---Currencies List Update
    self.pageAuxillaryFunctions['SETLIST']()
    #---Currencies Selected Currency Info Update
    self.pageAuxillaryFunctions['UPDATEINFORMATION']()
#SETUP PAGE <LOAD> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <ESCAPE> --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageEscapeFunction(self):
    for fID in ('onCurrenciesUpdate',):
        self.ipcA.removeFARHandler(functionID   = fID)
        self.ipcA.addDummyFARHandler(functionID = fID)
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

    #<Currency List>
    #---Filter
    def __onTextUpdate_CurrencyList_SearchText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_TradingTrue(objInstance, **kwargs):
        if (self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"].getStatus() == True): self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_TradingFalse(objInstance, **kwargs):
        if (self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"].getStatus() == True): self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_MinNumberOfKlines(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onTextUpdate_CurrencyList_MinNumberOfKlines(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_SortByID(objInstance, **kwargs):
        if (self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYSYMBOL"].getStatus()     == True): self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status     = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus() == True): self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYFIRSTKLINE"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYID"].getStatus() == False):        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYID"].setStatus(status         = True,  callStatusUpdateFunction = False)
        else:                                                                        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_SortBySymbol(objInstance, **kwargs):
        if (self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYID"].getStatus()         == True): self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYID"].setStatus(status         = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus() == True): self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYFIRSTKLINE"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYSYMBOL"].getStatus() == False):    self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status     = True,  callStatusUpdateFunction = False)
        else:                                                                         self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_SortByFirstKline(objInstance, **kwargs):
        if (self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYSYMBOL"].getStatus() == True):      self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status     = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYID"].getStatus()     == True):      self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYID"].setStatus(status         = False, callStatusUpdateFunction = False)
        if (self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus() == False): self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYFIRSTKLINE"].setStatus(status = True,  callStatusUpdateFunction = False)
        else:                                                                         self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    objFunctions['ONTEXTUPDATE_CURRENCYLIST_SEARCHTEXT']                = __onTextUpdate_CurrencyList_SearchText
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGTRUE']       = __onSwitchStatusUpdate_CurrencyList_TradingTrue
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGFALSE']      = __onSwitchStatusUpdate_CurrencyList_TradingFalse
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_MINNUMBEROFKLINES'] = __onSwitchStatusUpdate_CurrencyList_MinNumberOfKlines
    objFunctions['ONTEXTUPDATE_CURRENCYLIST_MINNUMBEROFKLINES']         = __onTextUpdate_CurrencyList_MinNumberOfKlines
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBYID']          = __onSwitchStatusUpdate_CurrencyList_SortByID
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBYSYMBOL']      = __onSwitchStatusUpdate_CurrencyList_SortBySymbol
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBYFIRSTKLINE']  = __onSwitchStatusUpdate_CurrencyList_SortByFirstKline
    #---List
    def __onSelectionUpdate_CurrencyList_CurrencySelection(objInstance, **kwargs):
        try:    selectedCurrency_symbol = objInstance.getSelected()[0]
        except: selectedCurrency_symbol = None
        self.puVar['currency_selected'] = selectedCurrency_symbol
        self.pageAuxillaryFunctions['UPDATEINFORMATION']()
        self.GUIOs["CHART_CHARTDRAWER"].setTarget(target = self.puVar['currency_selected'], intervalID = 0)
        if (selectedCurrency_symbol is not None): pprint.pprint(self.puVar['currencies'][selectedCurrency_symbol])
    objFunctions['ONSELECTIONUPDATE_CURRENCYLIST_CURRENCYSELECTION'] = __onSelectionUpdate_CurrencyList_CurrencySelection

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()
    
    #<_PAGELOAD>
    def __far_onCurrenciesUpdate(requester, updatedContents):
        if (requester == 'DATAMANAGER'):
            _resetList         = False
            _reapplyListFilter = False
            for updatedContent in updatedContents:
                symbol    = updatedContent['symbol']
                contentID = updatedContent['id']
                #A new currency is added
                if (contentID == '_ADDED'):
                    self.puVar['currencies'][symbol] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol))
                    _resetList = True
                else:
                    #Selected currency info update if needed & check if the currency list item needs an update
                    _updated_status     = False
                    _updated_firstKline = False
                    _updated_dataRanges = False
                    #---[1]: Currency Server Information Updated
                    if (contentID[0] == 'info_server'): 
                        try:    contentID_1 = contentID[1]
                        except: contentID_1 = None
                        #---[1-1]: Entire Server Information Updated
                        if (contentID_1 == None): self.puVar['currencies'][symbol]['info_server'] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server')); _updated_status = True
                        #---[1-2]: Currency Status Updated
                        else:
                            if (contentID_1 == 'status'): self.puVar['currencies'][symbol]['info_server']['status'] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server', 'status')); _updated_status = True
                    #---[2]: KlineFirstOpenTS Updated
                    elif (contentID[0] == 'kline_firstOpenTS'):
                        firstOpenTS_new = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'kline_firstOpenTS'))
                        self.puVar['currencies'][symbol]['kline_firstOpenTS'] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'kline_firstOpenTS'))
                        _updated_firstKline = True
                    #---[3]: KlineAvailableRanges Updated
                    elif (contentID[0] == 'kline_availableRanges'):
                        dataRanges = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'kline_availableRanges'))
                        self.puVar['currencies'][symbol]['kline_availableRanges'] = dataRanges
                        _updated_dataRanges = True
                    #Update Handlers
                    #---Status
                    if (_updated_status == True):
                        if (self.puVar['currencies'][symbol]['info_server'] == None): _status_str = "-"; _status_str_color = 'BLUE_DARK'
                        else:
                            currencyStatus = self.puVar['currencies'][symbol]['info_server']['status']
                            if   (currencyStatus == 'TRADING'):  _status_str = self.visualManager.getTextPack('MARKET:CURRENCYLIST_STATUS_TRADING');  _status_str_color = 'GREEN_LIGHT'
                            elif (currencyStatus == 'SETTLING'): _status_str = self.visualManager.getTextPack('MARKET:CURRENCYLIST_STATUS_SETTLING'); _status_str_color = 'RED_LIGHT'
                            elif (currencyStatus == 'REMOVED'):  _status_str = self.visualManager.getTextPack('MARKET:CURRENCYLIST_STATUS_REMOVED');  _status_str_color = 'RED_DARK'
                            else:                                _status_str = currencyStatus;                                                        _status_str_color = 'ORANGE_LIGHT'
                        _newSelectionBoxItem = {'text': _status_str, 'textStyles': [('all', _status_str_color),], 'textAnchor': 'CENTER'}
                        self.GUIOs["CURRENCYLIST_SELECTIONBOX"].editSelectionListItem(itemKey = symbol, item = _newSelectionBoxItem, columnIndex = 2)
                        _reapplyListFilter = True
                    #---First Kline
                    if (_updated_firstKline == True):
                        if (firstOpenTS_new == None): _firstKline_str = "-"
                        else:                         _firstKline_str = datetime.fromtimestamp(firstOpenTS_new, tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
                        _newSelectionBoxItem = {'text': _firstKline_str, 'textStyles': [('all', 'DEFAULT'),], 'textAnchor': 'CENTER'}
                        self.GUIOs["CURRENCYLIST_SELECTIONBOX"].editSelectionListItem(itemKey = symbol, item = _newSelectionBoxItem, columnIndex = 3)
                        _reapplyListFilter = True
                    #---Data Ranges
                    if (_updated_dataRanges == True):
                        if (symbol == self.puVar['currency_selected']): 
                            if (dataRanges == None): dataRanges_str = "-"
                            else:
                                nDataRanges = len(dataRanges)
                                if (nDataRanges == 1): dataRanges_str = "{:s} ~ {:s}".format(datetime.fromtimestamp(dataRanges[0][0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(dataRanges[0][1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
                                else:
                                    dataRanges_str = ""
                                    for dataRange in dataRanges: dataRanges_str += "({:s} ~ {:s})".format(datetime.fromtimestamp(dataRange[0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(dataRange[1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
                            self.GUIOs["CURRENCYLIST_DATARANGEDISPLAYTEXT"].updateText(text = dataRanges_str)
            #If need to reapply filter
            if   (_resetList         == True): self.pageAuxillaryFunctions['SETLIST']()
            elif (_reapplyListFilter == True): self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    auxFunctions['_FAR_ONCURRENCIESUPDATE'] = __far_onCurrenciesUpdate

    #<Filter>
    def __onFilterUpdate():
        #Localize filter settings
        filter_symbol = self.GUIOs["CURRENCYLIST_SEARCHTITLETEXTINPUTBOX"].getText()
        filter_trading = None
        if   (self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"].getStatus()  == True): filter_trading = True
        elif (self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"].getStatus() == True): filter_trading = False
        filter_nKlinesMin = None
        if (self.GUIOs["CURRENCYLIST_FILTERSWITCH_MINNUMBEROFKLINES"].getStatus() == True):
            try: filter_nKlinesMin = int(self.GUIOs["CURRENCYLIST_FILTERSWITCH_MINNUMBEROFKLINESTEXTINPUTBOX"].getText())
            except: pass
        filter_sort = None
        if   (self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYID"].getStatus()         == True): filter_sort = 'id'
        elif (self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYSYMBOL"].getStatus()     == True): filter_sort = 'symbol'
        elif (self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus() == True): filter_sort = 'firstKline'
        #Filter symbols
        symbols = list(self.puVar['currencies'].keys())
        symbols_filtered = list()
        minuteNumber_current = int(time.time()/60)
        for symbol in symbols:
            testFailed = False
            #Symbol Filter
            if not(filter_symbol in symbol): testFailed = True
            #Status Filter
            if (filter_trading == True):
                if not((self.puVar['currencies'][symbol]['info_server'] != None) and (self.puVar['currencies'][symbol]['info_server']['status'] == 'TRADING')): testFailed = True
            elif (filter_trading == False):
                if ((self.puVar['currencies'][symbol]['info_server'] != None) and (self.puVar['currencies'][symbol]['info_server']['status'] == 'TRADING')): testFailed = True
            #nKlines_min Filter
            if (filter_nKlinesMin != None):
                firstClosedOpenTS_minuteNumber = int(self.puVar['currencies'][symbol]['kline_firstOpenTS']/60)
                nKlines = minuteNumber_current-firstClosedOpenTS_minuteNumber+1
                if (nKlines < filter_nKlinesMin): testFailed = True
            #If all tests passed
            if (testFailed == False): symbols_filtered.append(symbol)
        #Symbols Sorting
        symbols_forSort = list()
        for symbol in symbols_filtered:
            currencyID       = self.puVar['currencies'][symbol]['currencyID']
            firstKlineOpenTS = self.puVar['currencies'][symbol]['kline_firstOpenTS']
            if (firstKlineOpenTS == None): symbol_forSort = (currencyID, symbol, float('inf'))
            else:                          symbol_forSort = (currencyID, symbol, firstKlineOpenTS)
            symbols_forSort.append(symbol_forSort)
        if   (filter_sort == 'id'):         symbols_forSort.sort(key = lambda x: x[0])
        elif (filter_sort == 'symbol'):     symbols_forSort.sort(key = lambda x: x[1])
        elif (filter_sort == 'firstKline'): symbols_forSort.sort(key = lambda x: x[2])
        #Finally
        symbols_filteredAndSorted = [symbol_forSort[1] for symbol_forSort in symbols_forSort]
        self.GUIOs["CURRENCYLIST_SELECTIONBOX"].setDisplayTargets(displayTargets = symbols_filteredAndSorted, resetViewPosition = False)
    auxFunctions['ONFILTERUPDATE'] = __onFilterUpdate

    #<List>
    def __setList():
        #Format and update the selectionBox object
        currencies_selectionList = dict()
        _nCurrencies = len(self.puVar['currencies'])
        for _cIndex, _symbol in enumerate(self.puVar['currencies']):
            if (self.puVar['currencies'][_symbol]['info_server'] == None): _status_str = "-"; _status_str_color = 'BLUE_DARK'
            else:
                currencyStatus = self.puVar['currencies'][_symbol]['info_server']['status']
                if   (currencyStatus == 'TRADING'):  _status_str = self.visualManager.getTextPack('MARKET:CURRENCYLIST_STATUS_TRADING');  _status_str_color = 'GREEN_LIGHT'
                elif (currencyStatus == 'SETTLING'): _status_str = self.visualManager.getTextPack('MARKET:CURRENCYLIST_STATUS_SETTLING'); _status_str_color = 'RED_LIGHT'
                elif (currencyStatus == 'REMOVED'):  _status_str = self.visualManager.getTextPack('MARKET:CURRENCYLIST_STATUS_REMOVED');  _status_str_color = 'RED_DARK'
                else:                                _status_str = currencyStatus;                                                        _status_str_color = 'ORANGE_LIGHT'
            firstOpenTS = self.puVar['currencies'][_symbol]['kline_firstOpenTS']
            if (firstOpenTS == None): firstOpenTS_str = "-"
            else:                     firstOpenTS_str = datetime.fromtimestamp(self.puVar['currencies'][_symbol]['kline_firstOpenTS'], tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
            currencies_selectionList[_symbol] = [{'text': "{:d} / {:d}".format(_cIndex+1, _nCurrencies), 'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                                 {'text': _symbol,                                       'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                                 {'text': _status_str,                                   'textStyles': [('all', _status_str_color),], 'textAnchor': 'CENTER'},
                                                 {'text': firstOpenTS_str,                               'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'}]
        self.GUIOs["CURRENCYLIST_SELECTIONBOX"].setSelectionList(selectionList = currencies_selectionList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)

        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    auxFunctions['SETLIST'] = __setList

    #<Information>
    def __updateInformation():
        selectedCurrency_symbol = self.puVar['currency_selected']
        if ((selectedCurrency_symbol != None) and (selectedCurrency_symbol in self.puVar['currencies'])):
            selectedCurrency_info = self.puVar['currencies'][selectedCurrency_symbol]
            selectedCurrency_dataRanges = selectedCurrency_info['kline_availableRanges']
            selectedCurrency_currencyID = self.puVar['currencies'][selectedCurrency_symbol]['currencyID']
            self.GUIOs["CURRENCYLIST_CURRENCYIDDISPLAYTEXT"].updateText(text = str(selectedCurrency_currencyID))
            if (selectedCurrency_dataRanges == None): selectedCurrency_dataRanges_str = "-"
            else:
                nDataRanges = len(selectedCurrency_dataRanges)
                if (nDataRanges == 1): selectedCurrency_dataRanges_str = "{:s} ~ {:s}".format(datetime.fromtimestamp(selectedCurrency_dataRanges[0][0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(selectedCurrency_dataRanges[0][1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
                else:
                    selectedCurrency_dataRanges_str = ""
                    for dataRange in selectedCurrency_dataRanges: selectedCurrency_dataRanges_str += "({:s} ~ {:s})".format(datetime.fromtimestamp(dataRange[0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(dataRange[1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
            self.GUIOs["CURRENCYLIST_DATARANGEDISPLAYTEXT"].updateText(text = selectedCurrency_dataRanges_str)
        else:
            self.GUIOs["CURRENCYLIST_CURRENCYIDDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["CURRENCYLIST_DATARANGEDISPLAYTEXT"].updateText(text  = "-")
    auxFunctions['UPDATEINFORMATION'] = __updateInformation

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------