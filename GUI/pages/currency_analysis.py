#ATM Modules
import ipc
from GUI.generals import passiveGraphics_wrapperTypeC,\
                                    textBox_typeA,\
                                    button_typeB,\
                                    switch_typeC,\
                                    textInputBox_typeA,\
                                    selectionBox_typeC
from GUI.chart_drawer_ca_viewer import chartDrawer_caViewer

#Python Modules
import pyglet
import time
from datetime import datetime, timezone

#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = ipc._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = ipc._FAR_INVALIDFUNCTIONID

_CLOCK_UPDATE_INTERVAL_NS = 100e6

#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
    self.puVar['currencyAnalysis']          = dict()
    self.puVar['currencyAnalysis_selected'] = None
    self.puVar['currencyAnalysis_toLoad']   = None
    self.puVar['currencyAnalysis_sortMode'] = None
    self.puVar['clock_lastUpdated_ns']      = 0

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
        self.GUIOs["CURRENCYANALYSISLIST_SEARCHTITLETEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=8000, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_SEARCH'),        fontSize=80, textInteractable    =False)
        self.GUIOs["CURRENCYANALYSISLIST_SEARCHTITLETEXTINPUTBOX"]     = textInputBox_typeA(**inst, groupOrder=1, xPos=1200, yPos=8000, width=3000, height=250, style="styleA", text="",                                                                      fontSize=80, textUpdateFunction  =self.pageObjectFunctions['ONTEXTUPDATE_CURRENCYANALYSISLIST_SEARCHTEXT'])
        self.GUIOs["CURRENCYANALYSISLIST_SORTBYTITLETEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=7650, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_SORTBY'),   fontSize=80, textInteractable    =False)
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"]       = switch_typeC(**inst,       groupOrder=1, xPos=1200, yPos=7650, width= 900, height=250, style="styleB", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_ID'),       fontSize=80, name = 'ID',       statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTSWITCH'])
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYANALYZER"] = switch_typeC(**inst,       groupOrder=1, xPos=2200, yPos=7650, width= 900, height=250, style="styleB", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_ANALYZER'), fontSize=80, name = 'ANALYZER', statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTSWITCH'])
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCACODE"]   = switch_typeC(**inst,       groupOrder=1, xPos=3200, yPos=7650, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_CACODE'),   fontSize=80, name = 'CACODE',   statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTSWITCH'])
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSYMBOL"]   = switch_typeC(**inst,       groupOrder=1, xPos= 100, yPos=7300, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_SYMBOL'),   fontSize=80, name = 'SYMBOL',   statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTSWITCH'])
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYCACCODE"]  = switch_typeC(**inst,       groupOrder=1, xPos=1200, yPos=7300, width=1900, height=250, style="styleB", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_CACCODE'),  fontSize=80, name = 'CACCODE',  statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTSWITCH'])
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"]   = switch_typeC(**inst,       groupOrder=1, xPos=3200, yPos=7300, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS'),   fontSize=80, name = 'STATUS',   statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTSWITCH'])
        self.GUIOs["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].setStatus(status = True, callStatusUpdateFunction = False)
        self.puVar['currencyAnalysis_sortMode'] = 'ID'
        #---List
        self.GUIOs["CURRENCYANALYSISLIST_SELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=1, xPos=100, yPos=800, width=4100, height=6400, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_CURRENCYANALYSISLIST_ANALYSISSELECTION'], elementWidths = (600, 900, 1150, 1200))
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
        self.GUIOs["CHART_CHARTDRAWER"] = chartDrawer_caViewer(**inst, groupOrder=1, xPos=4300, yPos=100, width=11600, height=8150, style="styleA", name = 'CURRENCYANALYSIS_CHARTDRAWER')
        
        #Clock
        self.GUIOs["CLOCK_LOCAL"] = textBox_typeA(**inst, groupOrder=1, xPos= 14000, yPos=8800, width=1950, height=150, style=None, text="", anchor = 'E', fontSize = 80, textInteractable = False)
        self.GUIOs["CLOCK_UTC"]   = textBox_typeA(**inst, groupOrder=1, xPos= 14000, yPos=8650, width=1950, height=150, style=None, text="", anchor = 'E', fontSize = 80, textInteractable = False)

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
    for fID in ('onCurrencyAnalysisUpdate',):
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
        self.sysFunctions['LOADPAGE']('DASHBOARD')
    objFunctions['PAGEMOVE_DASHBOARD'] = __pageMove_DASHBOARD

    #<Currency Analysis List>
    #---Filter
    def __onTextUpdate_CurrencyAnalysisList_SearchText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()

    def __onSwitchStatusUpdate_CurrencyAnalysisList_SortSwitch(objInstance, **kwargs):
        #[1]: Instances
        puVar      = self.puVar
        guios      = self.GUIOs
        pafs       = self.pageAuxillaryFunctions
        sName      = objInstance.name
        sMode_prev = puVar['currencyAnalysis_sortMode']

        #[2]: Switch Update
        if objInstance.getStatus():
            guios[f"CURRENCYANALYSISLIST_FILTERSWITCH_SORTBY{sMode_prev}"].setStatus(status = False, callStatusUpdateFunction = False)
            sMode_new = sName
        else:
            guios[f"CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYID"].setStatus(status = True, callStatusUpdateFunction = False)
            sMode_new = 'ID'

        #[3]: Filter Update
        if sMode_prev != sMode_new:
            puVar['currencyAnalysis_sortMode'] = sMode_new
            pafs['ONFILTERUPDATE']()
    objFunctions['ONTEXTUPDATE_CURRENCYANALYSISLIST_SEARCHTEXT']         = __onTextUpdate_CurrencyAnalysisList_SearchText
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYANALYSISLIST_SORTSWITCH'] = __onSwitchStatusUpdate_CurrencyAnalysisList_SortSwitch



    #---List
    def __onSelectionUpdate_CurrencyAnalysisList_AnalysisSelection(objInstance, **kwargs):
        sels       = objInstance.getSelected()
        caCode_sel = sels[0] if sels else None
        self.puVar['currencyAnalysis_selected'] = caCode_sel
        self.pageAuxillaryFunctions['UPDATEINFORMATION']()
        self.GUIOs["CHART_CHARTDRAWER"].setTarget(target = caCode_sel)
    objFunctions['ONSELECTIONUPDATE_CURRENCYANALYSISLIST_ANALYSISSELECTION'] = __onSelectionUpdate_CurrencyAnalysisList_AnalysisSelection

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()
    
    #<_PAGELOAD>
    def __far_onCurrencyAnalysisUpdate(requester, updateType, currencyAnalysisCode):
        #[1]: Source Check
        if requester != 'TRADEMANAGER':
            return
        
        #[2]: Instances
        puVar  = self.puVar
        guios  = self.GUIOs
        vm_gtp = self.visualManager.getTextPack
        pafs   = self.pageAuxillaryFunctions
        caCode = currencyAnalysisCode
        func_getPRD = self.ipcA.getPRD

        #[3]: Update Response
        #---[3-1]: Status Updated
        if updateType == 'UPDATE_STATUS':
            status = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode, 'status'))
            puVar['currencyAnalysis'][caCode]['status'] = status
            status_str = vm_gtp(f'CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_{status}')
            if   status == 'CURRENCYNOTFOUND':     status_col = 'RED'
            elif status == 'CONFIGNOTFOUND':       status_col = 'RED_LIGHT'
            elif status == 'WAITINGTRADING':       status_col = 'ORANGE'
            elif status == 'WAITINGNEURALNETWORK': status_col = 'ORANGE_LIGHT'
            elif status == 'WAITINGSTREAM':        status_col = 'BLUE_LIGHT'
            elif status == 'WAITINGDATAAVAILABLE': status_col = 'CYAN_LIGHT'
            elif status == 'QUEUED':               status_col = 'VIOLET_LIGHT'
            elif status == 'FETCHING':             status_col = 'BLUE_LIGHT'
            elif status == 'INITIALANALYZING':     status_col = 'GREEN_DARK'
            elif status == 'ANALYZING':            status_col = 'GREEN_LIGHT'
            elif status == 'ERROR':                status_col = 'RED_DARK'
            nsbi = {'text': status_str, 'textStyles': [('all', status_col),], 'textAnchor': 'CENTER'}
            guios["CURRENCYANALYSISLIST_SELECTIONBOX"].editSelectionListItem(itemKey = caCode, item = nsbi, columnIndex = 3)
            if guios["CURRENCYANALYSISLIST_FILTERSWITCH_SORTBYSTATUS"].getStatus(): 
                pafs['ONFILTERUPDATE']()

        #---[3-2]: Analyzer Updated
        elif updateType == 'UPDATE_ANALYZER':
            allocatedAnalyzer = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode, 'allocatedAnalyzer'))
            puVar['currencyAnalysis'][caCode]['allocatedAnalyzer'] = allocatedAnalyzer
            if caCode == puVar['currencyAnalysis_selected']:
                if allocatedAnalyzer is None: guios["CURRENCYANALYSISLIST_ALLOCATEDANALYZERDISPLAYTEXT"].updateText(text = "-")
                else:                         guios["CURRENCYANALYSISLIST_ALLOCATEDANALYZERDISPLAYTEXT"].updateText(text = f"ANALYZER {allocatedAnalyzer}")

        #---[3-3]: Added
        elif updateType == 'ADDED':
            puVar['currencyAnalysis'][caCode] = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode))
            pafs['SETLIST']()

        #---[3-4]: Removed
        elif updateType == 'REMOVED':
            pafs['SETLIST']()
            if caCode == puVar['currencyAnalysis_selected']:
                puVar['currencyAnalysis_selected'] = None
                pafs['UPDATEINFORMATION']()

        #Send the update to the chart drawer if this is for the selected currency analysis
        if caCode == puVar['currencyAnalysis_selected']: 
            guios["CHART_CHARTDRAWER"].onCurrencyAnalysisUpdate(updateType = updateType, currencyAnalysisCode = caCode)
    auxFunctions['_FAR_ONCURRENCYANALYSISUPDATE'] = __far_onCurrencyAnalysisUpdate

    #<Filter>
    def __onFilterUpdate():
        #[1]: Instances
        puVar  = self.puVar
        guios  = self.GUIOs
        cas    = puVar['currencyAnalysis']
        sMode  = puVar['currencyAnalysis_sortMode']

        #[2]: Analysis Code Filtering
        filter_aCode    = guios["CURRENCYANALYSISLIST_SEARCHTITLETEXTINPUTBOX"].getText()
        aCodes_filtered = [aCode for aCode in cas if (filter_aCode in aCode)]

        #[3]: Sorting
        if sMode == 'ID': 
            listForSort = 'id'
        elif sMode == 'ANALYZER':
            listForSort = []
            for aCode in aCodes_filtered:
                allocatedAnalyzer = cas[aCode]['allocatedAnalyzer']
                if allocatedAnalyzer is None: listForSort.append((aCode, float('inf')))
                else:                         listForSort.append((aCode, allocatedAnalyzer))
        elif sMode == 'CACODE': 
            listForSort = 'analysisCode'
        elif sMode == 'SYMBOL': 
            listForSort = [(aCode, cas[aCode]['currencySymbol'])                    for aCode in aCodes_filtered]
        elif sMode == 'CACCODE': 
            listForSort = [(aCode, cas[aCode]['currencyAnalysisConfigurationCode']) for aCode in aCodes_filtered]
        elif sMode == 'STATUS': 
            listForSort = []
            for aCode in aCodes_filtered:
                status = cas[aCode]['status']
                if   status == 'CURRENCYNOTFOUND':     priority = 9
                elif status == 'CONFIGNOTFOUND':       priority = 8
                elif status == 'WAITINGTRADING':       priority = 7
                elif status == 'WAITINGNEURALNETWORK': priority = 6
                elif status == 'WAITINGSTREAM':        priority = 5
                elif status == 'WAITINGDATAAVAILABLE': priority = 4
                elif status == 'QUEUED':               priority = 3
                elif status == 'FETCHING':             priority = 2
                elif status == 'INITIALANALYZING':     priority = 1
                elif status == 'ANALYZING':            priority = 0
                elif status == 'ERROR':                priority = 10
                listForSort.append((aCode, priority))
        if   listForSort == 'id':           aCodes_sorted = aCodes_filtered
        elif listForSort == 'analysisCode': aCodes_sorted = sorted(aCodes_filtered)
        else:                               aCodes_sorted = [sp[0] for sp in sorted(listForSort, key = lambda x: x[1])]

        #[4]: Selection Box Update
        guios["CURRENCYANALYSISLIST_SELECTIONBOX"].setDisplayTargets(displayTargets = aCodes_sorted, resetViewPosition = False)
    auxFunctions['ONFILTERUPDATE'] = __onFilterUpdate

    #<List>
    def __setList():
        #[1]: Instances
        guios  = self.GUIOs
        vm_gtp = self.visualManager.getTextPack
        pafs   = self.pageAuxillaryFunctions
        cas    = self.puVar['currencyAnalysis']
        nCAs   = len(cas)

        #[2]: Selection Box Update
        caSelList = dict()
        for caIdx, caCode in enumerate(cas):
            ca = cas[caCode]
            status = ca['status']
            symbol = ca['currencySymbol']
            status_str = vm_gtp(f'CURRENCYANALYSIS:CURRENCYANALYSISLIST_STATUS_{status}')
            if   status == 'CURRENCYNOTFOUND':     status_col = 'RED'
            elif status == 'CONFIGNOTFOUND':       status_col = 'RED_LIGHT'
            elif status == 'WAITINGTRADING':       status_col = 'ORANGE'
            elif status == 'WAITINGNEURALNETWORK': status_col = 'ORANGE_LIGHT'
            elif status == 'WAITINGSTREAM':        status_col = 'BLUE_LIGHT'
            elif status == 'WAITINGDATAAVAILABLE': status_col = 'CYAN_LIGHT'
            elif status == 'QUEUED':               status_col = 'VIOLET_LIGHT'
            elif status == 'FETCHING':             status_col = 'BLUE_LIGHT'
            elif status == 'INITIALANALYZING':     status_col = 'GREEN_DARK'
            elif status == 'ANALYZING':            status_col = 'GREEN_LIGHT'
            elif status == 'ERROR':                status_col = 'RED_DARK'
            caSelList[caCode] = [{'text': f"{caIdx+1} / {nCAs}", 'textStyles': [('all', 'DEFAULT'),],  'textAnchor': 'CENTER'},
                                 {'text': caCode,                'textStyles': [('all', 'DEFAULT'),],  'textAnchor': 'CENTER'},
                                 {'text': symbol,                'textStyles': [('all', 'DEFAULT'),],  'textAnchor': 'CENTER'},
                                 {'text': status_str,            'textStyles': [('all', status_col),], 'textAnchor': 'CENTER'}]
        guios["CURRENCYANALYSISLIST_SELECTIONBOX"].setSelectionList(selectionList = caSelList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
        
        #[3]: Filter Update
        pafs['ONFILTERUPDATE']()
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