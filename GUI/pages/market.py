#ATM Modules
import ipc
from GUI.generals import passiveGraphics_wrapperTypeC,\
                         textBox_typeA,\
                         button_typeB,\
                         switch_typeC,\
                         textInputBox_typeA,\
                         selectionBox_typeC
from GUI.chart_drawer_analyzer import chartDrawer_analyzer

#Python Modules
import pyglet
import time
from datetime import datetime, timezone

#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT

_CLOCK_UPDATE_INTERVAL_NS = 100e6

#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
    self.puVar['currencies']           = dict()
    self.puVar['currency_selected']    = None
    self.puVar['clock_lastUpdated_ns'] = 0

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
        self.GUIOs["CURRENCYLIST_SEARCHTITLETEXT"]               = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=8000, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_SEARCH'),       fontSize=80, textInteractable=False)
        self.GUIOs["CURRENCYLIST_SEARCHTITLETEXTINPUTBOX"]       = textInputBox_typeA(**inst, groupOrder=1, xPos= 900, yPos=8000, width=3300, height=250, style="styleA", text="",                                                                 fontSize=80, textUpdateFunction  =self.pageObjectFunctions['ONTEXTUPDATE_CURRENCYLIST_SEARCHTEXT'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"]      = switch_typeC(**inst,       groupOrder=1, xPos= 100, yPos=7650, width=2000, height=250, style="styleB", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_TRADINGTRUE'),  fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGTRUE'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"]     = switch_typeC(**inst,       groupOrder=1, xPos=2200, yPos=7650, width=2000, height=250, style="styleB", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_TRADINGFALSE'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGFALSE'])
        self.GUIOs["CURRENCYLIST_SORTBYTITLETEXT"]               = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=7300, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_SORTBY'),       fontSize=80, textInteractable    =False)
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYID"]         = switch_typeC(**inst,       groupOrder=1, xPos= 900, yPos=7300, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_ID'),           fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBYID'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYSYMBOL"]     = switch_typeC(**inst,       groupOrder=1, xPos=2000, yPos=7300, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_SYMBOL'),       fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBYSYMBOL'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYFIRSTKLINE"] = switch_typeC(**inst,       groupOrder=1, xPos=3100, yPos=7300, width=1100, height=250, style="styleB", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_FIRSTKLINE'),   fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBYFIRSTKLINE'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYID"].setStatus(status = True, callStatusUpdateFunction = False)
        #---List
        self.GUIOs["CURRENCYLIST_SELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=1, xPos=100, yPos=1150, width=4100, height=6050, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_CURRENCYLIST_CURRENCYSELECTION'], elementWidths = (700, 1150, 950, 1050))
        self.GUIOs["CURRENCYLIST_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('MARKET:CURRENCYLIST_INDEX')},
                                                                                 {'text': self.visualManager.getTextPack('MARKET:CURRENCYLIST_SYMBOL')},
                                                                                 {'text': self.visualManager.getTextPack('MARKET:CURRENCYLIST_STATUS')},
                                                                                 {'text': self.visualManager.getTextPack('MARKET:CURRENCYLIST_FIRSTKLINE')}])
        #---Information
        self.GUIOs["CURRENCYLIST_KLINEDATARANGETITLETEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=800, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_KLINE'),    fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_KLINEDATARANGEDISPLAYTEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos=1200, yPos=800, width=3000, height=250, style="styleA", text="-",                                                            fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_DEPTHDATARANGETITLETEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=450, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_DEPTH'),    fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_DEPTHDATARANGEDISPLAYTEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos=1200, yPos=450, width=3000, height=250, style="styleA", text="-",                                                            fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AGGTRADEDATARANGETITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=100, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('MARKET:CURRENCYLIST_AGGTRADE'), fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AGGTRADEDATARANGEDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=1200, yPos=100, width=3000, height=250, style="styleA", text="-",                                                            fontSize=80, textInteractable=True)

        #Chart
        self.GUIOs["BLOCKSUBTITLE_CHART"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=4300, yPos=8350, width=11600, height=200, style="styleA", text=self.visualManager.getTextPack('MARKET:BLOCKTITLE_CHART'), fontSize = 80)
        self.GUIOs["CHART_CHARTDRAWER"] = chartDrawer_analyzer(**inst, groupOrder=1, xPos=4300, yPos=100, width=11600, height=8150, style="styleA", name = 'MARKET_CHARTDRAWER')
        
        #Clock
        self.GUIOs["CLOCK_LOCAL"] = textBox_typeA(**inst, groupOrder=1, xPos= 14000, yPos=8800, width=1950, height=150, style=None, text="", anchor = 'E', fontSize = 80, textInteractable = False)
        self.GUIOs["CLOCK_UTC"]   = textBox_typeA(**inst, groupOrder=1, xPos= 14000, yPos=8650, width=1950, height=150, style=None, text="", anchor = 'E', fontSize = 80, textInteractable = False)

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
    #[1]: Instances
    puVar = self.puVar
    guios = self.GUIOs
    t_current_ns = time.perf_counter_ns()

    #[2]: Clock Update
    if _CLOCK_UPDATE_INTERVAL_NS <= t_current_ns-puVar['clock_lastUpdated_ns']:
        t_current_s = time.time()
        guios["CLOCK_LOCAL"].updateText(text = datetime.fromtimestamp(timestamp = t_current_s).strftime("[LOCAL] %Y/%m/%d %H:%M:%S.%f")[:-5])
        guios["CLOCK_UTC"].updateText(text   = datetime.fromtimestamp(timestamp = t_current_s, tz=timezone.utc).strftime("[UTC] %Y/%m/%d %H:%M:%S.%f")[:-5])
        puVar['clock_lastUpdated_ns'] = t_current_ns
#SETUP PAGE <PROCESS> END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#OBJECT FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateObjectFunctions(self):
    objFunctions = dict()

    #<Page Navigation>
    def __pageMove_DASHBOARD(objInstance, **kwargs): 
        self.sysFunctions['LOADPAGE']['function']('DASHBOARD')
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
    objFunctions['ONTEXTUPDATE_CURRENCYLIST_SEARCHTEXT']               = __onTextUpdate_CurrencyList_SearchText
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGTRUE']      = __onSwitchStatusUpdate_CurrencyList_TradingTrue
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGFALSE']     = __onSwitchStatusUpdate_CurrencyList_TradingFalse
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBYID']         = __onSwitchStatusUpdate_CurrencyList_SortByID
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBYSYMBOL']     = __onSwitchStatusUpdate_CurrencyList_SortBySymbol
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBYFIRSTKLINE'] = __onSwitchStatusUpdate_CurrencyList_SortByFirstKline
    #---List
    def __onSelectionUpdate_CurrencyList_CurrencySelection(objInstance, **kwargs):
        try:    selectedCurrency_symbol = objInstance.getSelected()[0]
        except: selectedCurrency_symbol = None
        self.puVar['currency_selected'] = selectedCurrency_symbol
        self.pageAuxillaryFunctions['UPDATEINFORMATION']()
        self.GUIOs["CHART_CHARTDRAWER"].setTarget(target = self.puVar['currency_selected'])
    objFunctions['ONSELECTIONUPDATE_CURRENCYLIST_CURRENCYSELECTION'] = __onSelectionUpdate_CurrencyList_CurrencySelection

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
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions
        currencies = puVar['currencies']
        dt_fts      = datetime.fromtimestamp
        vm_gtp      = self.visualManager.getTextPack
        func_getPRD = self.ipcA.getPRD

        #[3]: Updates Read
        resetList         = False
        reapplyListFilter = False
        for uContent in updatedContents:
            #[3-1]: Instances
            symbol    = uContent['symbol']
            contentID = uContent['id']

            #[3-2]: New Currency
            if contentID == '_ADDED':
                currencies[symbol] = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol))
                resetList = True

            #[3-3]: Existing Currency Updated
            else:
                #[3-3-1]: Instances
                currency = currencies[symbol]

                #[3-3-2]: Updated Contents Check
                updated = set()
                #---[3-3-2-1]: Currency Server Information Updated
                if contentID[0] == 'info_server': 
                    try:    contentID_1 = contentID[1]
                    except: contentID_1 = None
                    if contentID_1 is None: 
                        currency['info_server'] = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server'))
                        updated.add('status')
                    else:
                        if contentID_1 == 'status': 
                            currency['info_server']['status'] = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server', 'status'))
                            updated.add('status')

                #---[3-3-2-2]: KlineFirstOpenTS Updated
                elif contentID[0] == 'kline_firstOpenTS':
                    currency['kline_firstOpenTS'] = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'kline_firstOpenTS'))
                    updated.add('kline_firstOpenTS')

                #---[3-3-2-3]: Kline Available Ranges Updated
                elif contentID[0] == 'klines_availableRanges':
                    currency['klines_availableRanges'] = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'klines_availableRanges'))
                    updated.add('klines_availableRanges')

                #---[3-3-2-3]: Depth AvailableRanges Updated
                elif contentID[0] == 'depths_availableRanges':
                    currency['depths_availableRanges'] = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'depths_availableRanges'))
                    updated.add('depths_availableRanges')

                #---[3-3-2-3]: AggTrade Available Ranges Updated
                elif contentID[0] == 'aggTrades_availableRanges':
                    currency['aggTrades_availableRanges'] = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'aggTrades_availableRanges'))
                    updated.add('aggTrades_availableRanges')

                #[3-3-3]: Update Handlers
                #---[3-3-3-1]: Status
                if 'status' in updated:
                    if currency['info_server'] is None: 
                        status_str       = "-"
                        status_str_color = 'BLUE_DARK'
                    else:
                        status = currency['info_server']['status']
                        if   status == 'TRADING':  status_str = vm_gtp('MARKET:CURRENCYLIST_STATUS_TRADING');  status_str_color = 'GREEN_LIGHT'
                        elif status == 'SETTLING': status_str = vm_gtp('MARKET:CURRENCYLIST_STATUS_SETTLING'); status_str_color = 'RED_LIGHT'
                        elif status == 'REMOVED':  status_str = vm_gtp('MARKET:CURRENCYLIST_STATUS_REMOVED');  status_str_color = 'RED_DARK'
                        else:                      status_str = status;                                        status_str_color = 'ORANGE_LIGHT'
                    nsbi = {'text': status_str, 'textStyles': [('all', status_str_color),], 'textAnchor': 'CENTER'}
                    guios["CURRENCYLIST_SELECTIONBOX"].editSelectionListItem(itemKey = symbol, item = nsbi, columnIndex = 2)
                    reapplyListFilter = True

                #---[3-3-3-2]: First Kline
                if 'kline_firstOpenTS' in updated:
                    firstOpenTS = currency['kline_firstOpenTS']
                    if firstOpenTS is None: firstKline_str = "-"
                    else:                   firstKline_str = dt_fts(firstOpenTS, tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
                    nsbi = {'text': firstKline_str, 'textStyles': [('all', 'DEFAULT'),], 'textAnchor': 'CENTER'}
                    guios["CURRENCYLIST_SELECTIONBOX"].editSelectionListItem(itemKey = symbol, item = nsbi, columnIndex = 3)
                    reapplyListFilter = True

                #---[3-3-3-3]: Data Ranges
                if symbol == puVar['currency_selected']:
                    for key1, key2 in (('klines',    'KLINE'), 
                                       ('depths',    'DEPTH'), 
                                       ('aggTrades', 'AGGTRADE')):
                        key = f'{key1}_availableRanges'
                        if key not in updated:
                            continue
                        drs = currency[key]
                        if drs: 
                            nDRs = len(drs)
                            if nDRs == 1: 
                                dr = drs[0]
                                dr_beg_str = dt_fts(dr[0], tz=timezone.utc).strftime('%Y/%m/%d %H:%M')
                                dr_end_str = dt_fts(dr[1], tz=timezone.utc).strftime('%Y/%m/%d %H:%M')
                                drs_str = f"{dr_beg_str} ~ {dr_end_str}"
                            else:
                                drs_str = ""
                                for dr in drs: 
                                    dr_beg_str = dt_fts(dr[0], tz=timezone.utc).strftime('%Y/%m/%d %H:%M')
                                    dr_end_str = dt_fts(dr[1], tz=timezone.utc).strftime('%Y/%m/%d %H:%M')
                                    drs_str += f"({dr_beg_str} ~ {dr_end_str})"
                        else:
                            drs_str = "-"
                        guios[f"CURRENCYLIST_{key2}DATARANGEDISPLAYTEXT"].updateText(text = drs_str)
        
        #[4]: List Update & Filter Apply
        if   resetList :        pafs['SETLIST']()
        elif reapplyListFilter: pafs['ONFILTERUPDATE']()
    auxFunctions['_FAR_ONCURRENCIESUPDATE'] = __far_onCurrenciesUpdate

    #<Filter>
    def __onFilterUpdate():
        #Localize filter settings
        filter_symbol = self.GUIOs["CURRENCYLIST_SEARCHTITLETEXTINPUTBOX"].getText()
        filter_trading = None
        if   (self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"].getStatus()  == True): filter_trading = True
        elif (self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"].getStatus() == True): filter_trading = False
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
            #If all tests passed
            if (testFailed == False): symbols_filtered.append(symbol)
        #Symbols Sorting
        symbols_forSort = list()
        for symbol in symbols_filtered:
            firstKlineOpenTS = self.puVar['currencies'][symbol]['kline_firstOpenTS']
            if (firstKlineOpenTS == None): symbol_forSort = (symbol, float('inf'))
            else:                          symbol_forSort = (symbol, firstKlineOpenTS)
            symbols_forSort.append(symbol_forSort)
        if   (filter_sort == 'symbol'):     symbols_forSort.sort(key = lambda x: x[0])
        elif (filter_sort == 'firstKline'): symbols_forSort.sort(key = lambda x: x[1])
        #Finally
        symbols_filteredAndSorted = [symbol_forSort[0] for symbol_forSort in symbols_forSort]
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
        #[1]: Instances
        puVar  = self.puVar
        guios  = self.GUIOs
        symbol = self.puVar['currency_selected']
        currency = puVar['currencies'].get(symbol, None)
        dt_fts = datetime.fromtimestamp

        #[2]: GUIOs Update
        if currency is None:
            guios["CURRENCYLIST_KLINEDATARANGEDISPLAYTEXT"].updateText(text    = "-")
            guios["CURRENCYLIST_DEPTHDATARANGEDISPLAYTEXT"].updateText(text    = "-")
            guios["CURRENCYLIST_AGGTRADEDATARANGEDISPLAYTEXT"].updateText(text = "-")
        else:
            for key1, key2 in (('klines',    'KLINE'), 
                               ('depths',    'DEPTH'), 
                               ('aggTrades', 'AGGTRADE')):
                drs = currency[f'{key1}_availableRanges']
                if drs:
                    nDRs = len(drs)
                    if nDRs == 1: 
                        dr = drs[0]
                        dr_beg_str = dt_fts(dr[0], tz=timezone.utc).strftime('%Y/%m/%d %H:%M')
                        dr_end_str = dt_fts(dr[1], tz=timezone.utc).strftime('%Y/%m/%d %H:%M')
                        drs_str = f"{dr_beg_str} ~ {dr_end_str}"
                    else:
                        drs_str = ""
                        for dr in drs: 
                            dr_beg_str = dt_fts(dr[0], tz=timezone.utc).strftime('%Y/%m/%d %H:%M')
                            dr_end_str = dt_fts(dr[1], tz=timezone.utc).strftime('%Y/%m/%d %H:%M')
                            drs_str += f"({dr_beg_str} ~ {dr_end_str})"
                else:
                    drs_str = "-"
                guios[f"CURRENCYLIST_{key2}DATARANGEDISPLAYTEXT"].updateText(text = drs_str)
    auxFunctions['UPDATEINFORMATION'] = __updateInformation

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------