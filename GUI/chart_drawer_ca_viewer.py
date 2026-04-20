#ATM Modules
from .chart_drawer import (chartDrawer,
                           _NMAXLINES,
                           _MITYPES,
                           _SITYPES)
import auxiliaries
import ipc

#Python Modules
import time

#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = ipc._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = ipc._FAR_INVALIDFUNCTIONID

KLINDEX_OPENTIME         =  0
KLINDEX_CLOSETIME        =  1
KLINDEX_OPENPRICE        =  2
KLINDEX_HIGHPRICE        =  3
KLINDEX_LOWPRICE         =  4
KLINDEX_CLOSEPRICE       =  5
KLINDEX_NTRADES          =  6
KLINDEX_VOLBASE          =  7
KLINDEX_VOLQUOTE         =  8
KLINDEX_VOLBASETAKERBUY  =  9
KLINDEX_VOLQUOTETAKERBUY = 10
KLINDEX_CLOSED           = 11
KLINDEX_SOURCE           = 12

DEPTHINDEX_OPENTIME  = 0
DEPTHINDEX_CLOSETIME = 1
DEPTHINDEX_BIDS5     = 2
DEPTHINDEX_BIDS4     = 3 
DEPTHINDEX_BIDS3     = 4
DEPTHINDEX_BIDS2     = 5 
DEPTHINDEX_BIDS1     = 6 
DEPTHINDEX_BIDS0     = 7 
DEPTHINDEX_ASKS0     = 8 
DEPTHINDEX_ASKS1     = 9 
DEPTHINDEX_ASKS2     = 10 
DEPTHINDEX_ASKS3     = 11
DEPTHINDEX_ASKS4     = 12
DEPTHINDEX_ASKS5     = 13
DEPTHINDEX_CLOSED    = 14
DEPTHINDEX_SOURCE    = 15

ATINDEX_OPENTIME     = 0
ATINDEX_CLOSETIME    = 1
ATINDEX_QUANTITYBUY  = 2
ATINDEX_QUANTITYSELL = 3
ATINDEX_NTRADESBUY   = 4
ATINDEX_NTRADESSELL  = 5
ATINDEX_NOTIONALBUY  = 6
ATINDEX_NOTIONALSELL = 7
ATINDEX_CLOSED       = 8
ATINDEX_SOURCE       = 9

_TYPEMODE_PENDING                     = 0
_TYPEMODE_WAITINGALLOCATION           = 1
_TYPEMODE_WAITINGSUBSCRIPTIONRESPONSE = 2
_TYPEMODE_WAITINGANALYZING            = 3
_TYPEMODE_RECEIVING                   = 4

#Chart Drawer CA Viewer Subclass
class chartDrawer_caViewer(chartDrawer):
    def __init__(self, **kwargs):
        self.chartDrawerType = "CAVIEWER"
        super().__init__(**kwargs)
        self.__typeInit()
        self.setTarget(target = None)

    def __typeInit(self):
        #[1]: GUIOs Deactivation
        ssps = self.settingsSubPages
        guios_MAIN    = ssps['MAIN'].GUIOs
        guios_SMA     = ssps['SMA'].GUIOs
        guios_WMA     = ssps['WMA'].GUIOs
        guios_EMA     = ssps['EMA'].GUIOs
        guios_PSAR    = ssps['PSAR'].GUIOs
        guios_BOL     = ssps['BOL'].GUIOs
        guios_IVP     = ssps['IVP'].GUIOs
        guios_SWING   = ssps['SWING'].GUIOs
        guios_VOL     = ssps['VOL'].GUIOs
        guios_NNA     = ssps['NNA'].GUIOs
        guios_MMACD   = ssps['MMACD'].GUIOs
        guios_DMIxADX = ssps['DMIxADX'].GUIOs
        guios_MFI     = ssps['MFI'].GUIOs
        guios_TPD     = ssps['TPD'].GUIOs
        guios_WOI     = ssps['WOI'].GUIOs
        guios_NES     = ssps['NES'].GUIOs

        #MAIN
        guios_MAIN["ANALYZER_ANALYSISRANGEBEG_RANGEINPUT"].deactivate()
        guios_MAIN["ANALYZER_ANALYSISRANGEEND_RANGEINPUT"].deactivate()
        guios_MAIN["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()
        
        #SMA
        for lineIndex in range (_NMAXLINES['SMA']):
            guios_SMA[f"INDICATOR_SMA{lineIndex}"].deactivate()
            guios_SMA[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].deactivate()

        #WMA
        for lineIndex in range (_NMAXLINES['WMA']):
            guios_WMA[f"INDICATOR_WMA{lineIndex}"].deactivate()
            guios_WMA[f"INDICATOR_WMA{lineIndex}_INTERVALINPUT"].deactivate()

        #EMA
        for lineIndex in range (_NMAXLINES['EMA']):
            guios_EMA[f"INDICATOR_EMA{lineIndex}"].deactivate()
            guios_EMA[f"INDICATOR_EMA{lineIndex}_INTERVALINPUT"].deactivate()

        #PSAR
        for lineIndex in range (_NMAXLINES['PSAR']):
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}"].deactivate()
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF0INPUT"].deactivate()
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF+INPUT"].deactivate()
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT"].deactivate()

        #BOL
        guios_BOL["INDICATOR_MATYPESELECTION"].deactivate()
        for lineIndex in range (_NMAXLINES['BOL']):
            guios_BOL[f"INDICATOR_BOL{lineIndex}"].deactivate()
            guios_BOL[f"INDICATOR_BOL{lineIndex}_INTERVALINPUT"].deactivate()
            guios_BOL[f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT"].deactivate()

        #IVP
        guios_IVP["INDICATOR_INTERVAL_INPUTTEXT"].deactivate()
        guios_IVP["INDICATOR_GAMMAFACTOR_SLIDER"].deactivate()
        guios_IVP["INDICATOR_DELTAFACTOR_SLIDER"].deactivate()

        #SWING
        for lineIndex in range (_NMAXLINES['SWING']):
            guios_SWING[f"INDICATOR_SWING{lineIndex}"].deactivate()
            guios_SWING[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].deactivate()

        #VOL
        guios_VOL["INDICATOR_MATYPESELECTION"].deactivate()
        for lineIndex in range (_NMAXLINES['VOL']):
            guios_VOL[f"INDICATOR_VOL{lineIndex}"].deactivate()
            guios_VOL[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].deactivate()

        #NNA
        for lineIndex in range (_NMAXLINES['NNA']):
            guios_NNA[f"INDICATOR_NNA{lineIndex}"].deactivate()
            guios_NNA[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].deactivate()
            guios_NNA[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].deactivate()
            guios_NNA[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].deactivate()

        #MMACD
        guios_MMACD["INDICATOR_SIGNALINTERVALTEXTINPUT"].deactivate()
        for lineIndex in range (_NMAXLINES['MMACD']):
            guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}"].deactivate()
            guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].deactivate()

        #DMIxADX
        for lineIndex in range (_NMAXLINES['DMIxADX']):
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}"].deactivate()
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].deactivate()

        #MFI
        for lineIndex in range (_NMAXLINES['MFI']):
            guios_MFI[f"INDICATOR_MFI{lineIndex}"].deactivate()
            guios_MFI[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].deactivate()

        #TPD
        for lineIndex in range (_NMAXLINES['TPD']):
            guios_TPD[f"INDICATOR_TPD{lineIndex}"].deactivate()
            guios_TPD[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].deactivate()
            guios_TPD[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].deactivate()
            guios_TPD[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].deactivate()

        #WOI
        for lineIndex in range (_NMAXLINES['WOI']):
            guios_WOI[f"INDICATOR_WOI{lineIndex}"].deactivate()
            guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].deactivate()

        #NES
        for lineIndex in range (_NMAXLINES['NES']):
            guios_NES[f"INDICATOR_NES{lineIndex}"].deactivate()
            guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].deactivate()

        #TRADELOG
        guios_MAIN["TRADELOGCOLOR_TARGETSELECTION"].deactivate()
        guios_MAIN["TRADELOGCOLOR_APPLYCOLOR"].deactivate()
        guios_MAIN["TRADELOGCOLOR_R_SLIDER"].deactivate()
        guios_MAIN["TRADELOGCOLOR_G_SLIDER"].deactivate()
        guios_MAIN["TRADELOGCOLOR_B_SLIDER"].deactivate()
        guios_MAIN["TRADELOGCOLOR_A_SLIDER"].deactivate()
        guios_MAIN["TRADELOGDISPLAY_SWITCH"].deactivate()
        guios_MAIN["TRADELOG_APPLYNEWSETTINGS"].deactivate()

        #[2]: Type Unique Variables
        self.__mode                 = None
        self.__currencyAnalysisCode = None
        self.__currencyAnalysis     = None

    def setTarget(self, target):
        #[1]: Target Read & Previous Subscription Unregistration
        if self.__currencyAnalysisCode is not None: 
            caDataRecv    = f"caDataReceiver_{self.name}"
            allocAnalyzer = self.__currencyAnalysis['allocatedAnalyzer']
            self.ipcA.removeFARHandler(functionID   = caDataRecv)
            self.ipcA.addDummyFARHandler(functionID = caDataRecv)
            self.ipcA.sendFAR(targetProcess  = f'ANALYZER{allocAnalyzer}',
                              functionID     = 'unregisterCurrencyAnalysisSubscription',
                              functionParams = {'currencyAnalysisCode': self.__currencyAnalysisCode,
                                                'dataReceiver':         caDataRecv},
                              farrHandler    = None)
        self.__currencyAnalysisCode = target
        self.__currencyAnalysis     = None if self.__currencyAnalysisCode is None else self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', target))
        self.currencySymbol         = None if self.__currencyAnalysis     is None else self.__currencyAnalysis['currencySymbol']
        self.currencyInfo           = None if self.currencySymbol         is None else self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol))
        if self.__currencyAnalysisCode is None: self._updateTargetText(text = "-")
        else:                                   self._updateTargetText(text = f"{self.__currencyAnalysisCode} [{self.currencySymbol}]")
            
        #[2]: Type Mode
        if self.__currencyAnalysisCode is None: self.__mode = _TYPEMODE_PENDING
        else:
            allocAnalyzer = self.__currencyAnalysis['allocatedAnalyzer']
            if allocAnalyzer is None: self.__mode = _TYPEMODE_WAITINGALLOCATION
            else:                     self.__mode = _TYPEMODE_WAITINGSUBSCRIPTIONRESPONSE

        #[3]: Loading Cover
        if   self.__mode == _TYPEMODE_PENDING:                     self._setLoadingCover(show = False, text = None,                                                                             gaugeValue = None)
        elif self.__mode == _TYPEMODE_WAITINGALLOCATION:           self._setLoadingCover(show = True,  text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGANALYZERALLOCATION'),     gaugeValue = None)
        elif self.__mode == _TYPEMODE_WAITINGSUBSCRIPTIONRESPONSE: self._setLoadingCover(show = True,  text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGCASUBSCRIPTIONRESPONSE'), gaugeValue = None)

        #[4]: Data
        aux = auxiliaries
        self.intervalID = aux.KLINE_INTERVAL_ID_1m
        self._clearData()
        self._clearDrawers()

        #[5]: Initialize Highlighters and Descriptors
        if self.__currencyAnalysisCode is not None:
            self._clearHighlightsAndDescriptors()

        #[6]: View Control
        #---[6-1]: Horizontal View Range Parameters Setup
        self._setHVRParams()
        #---[6-2]: RCLCGs Reset
        self._initializeRCLCGs('KLINESPRICE')
        for sivCode in self.displayBox_graphics_visibleSIViewers: self._initializeSIViewer(sivCode)
        #---[6-3] Horizontal View Range Update
        self.horizontalViewRange_magnification = 80
        hvr_new_end = round(time.time()+self.expectedKlineTemporalWidth*5)
        hvr_new_beg = round(hvr_new_end-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
        hvr_new = [hvr_new_beg, hvr_new_end]
        tz_rev  = -self.timezoneDelta
        if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]
        self.horizontalViewRange = hvr_new
        self._onHViewRangeUpdate(1)
        #---[6-4]: Vertical View Range Reset
        self._editVVR_toExtremaCenter('KLINESPRICE')
        for sivCode in self.displayBox_graphics_visibleSIViewers: self._editVVR_toExtremaCenter(sivCode)

        #[7]: Aggregation Interval Buttons
        abp_GUIOs = self.auxBarPage.GUIOs
        for iID in (aux.KLINE_INTERVAL_ID_1m,
                    aux.KLINE_INTERVAL_ID_3m,
                    aux.KLINE_INTERVAL_ID_5m,
                    aux.KLINE_INTERVAL_ID_15m,
                    aux.KLINE_INTERVAL_ID_30m,
                    aux.KLINE_INTERVAL_ID_1h,
                    aux.KLINE_INTERVAL_ID_2h,
                    aux.KLINE_INTERVAL_ID_4h,
                    aux.KLINE_INTERVAL_ID_6h,
                    aux.KLINE_INTERVAL_ID_8h,
                    aux.KLINE_INTERVAL_ID_12h,
                    aux.KLINE_INTERVAL_ID_1d,
                    aux.KLINE_INTERVAL_ID_3d,
                    aux.KLINE_INTERVAL_ID_1W,
                    aux.KLINE_INTERVAL_ID_1M,):
            aiSwitch = abp_GUIOs[f'AGGINTERVAL_{iID}']
            if iID == aux.KLINE_INTERVAL_ID_1m:
                aiSwitch.activate()
                aiSwitch.setStatus(status = True, callStatusUpdateFunction = False)
            else:
                aiSwitch.deactivate()
                aiSwitch.setStatus(status = False, callStatusUpdateFunction = False)
        self.intervalID = aux.KLINE_INTERVAL_ID_1m

        #[8]: Analysis Params Initialization
        self.analysisParams = {self.intervalID: dict()}

        #[9]: SI Type Analysis Codes Update
        self._updateSITypeAnalysisCodes()

        #[10]: Stream Subscription Registration
        if self.__mode == _TYPEMODE_WAITINGSUBSCRIPTIONRESPONSE: 
            caDataRecv    = f"caDataReceiver_{self.name}"
            allocAnalyzer = self.__currencyAnalysis['allocatedAnalyzer']
            self.ipcA.addFARHandler(functionID        = caDataRecv, 
                                    handlerFunction   = self.__onCADataReceival_FAR, 
                                    executionThread   = _IPC_THREADTYPE_MT, 
                                    immediateResponse = True)
            self.ipcA.sendFAR(targetProcess  = f'ANALYZER{allocAnalyzer}',
                              functionID     = 'registerCurrencyAnalysisSubscription',
                              functionParams = {'currencyAnalysisCode': self.__currencyAnalysisCode,
                                                'dataReceiver':         caDataRecv},
                              farrHandler    = self.__onSubscriptionRequestResponse_FARR)

        #[11]: Empty Currency Analysis Configuration Read
        cac = None if self.__currencyAnalysisCode is None else self.__currencyAnalysis['currencyAnalysisConfiguration'][self.intervalID]
        self._readCurrencyAnalysisConfiguration(currencyAnalysisConfiguration = cac)
        
    def _process_typeUnique(self, mei_beg):
        return False
    
    def onCurrencyAnalysisUpdate(self, updateType, currencyAnalysisCode):
        #[1]: Currency Analysis Code Check
        if currencyAnalysisCode != self.__currencyAnalysisCode: 
            return
        
        #[2]: Instances
        caCode = currencyAnalysisCode
        ca     = self.__currencyAnalysis
        mode   = self.__mode
        func_getPRD = self.ipcA.getPRD

        #[3]: Update Handling
        #---[3-1]: Status Update
        if updateType == 'UPDATE_STATUS':
            status = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode, 'status'))
            if mode == _TYPEMODE_WAITINGANALYZING:
                if status == 'ANALYZING':
                    self.__mode = _TYPEMODE_RECEIVING
                    self._setLoadingCover(show = False, text = None, gaugeValue = None)
            if status == 'ERROR':
                self.__mode = _TYPEMODE_PENDING
                self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:CAERROROCCURRED'), gaugeValue = None)

        #---[3-2]: Analyzer Update
        elif updateType == 'UPDATE_ANALYZER':
            if mode == _TYPEMODE_WAITINGALLOCATION:
                caDataRecv    = f"caDataReceiver_{self.name}"
                allocAnalyzer = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode, 'allocatedAnalyzer'))
                ca['allocatedAnalyzer'] = allocAnalyzer
                self.__mode = _TYPEMODE_WAITINGSUBSCRIPTIONRESPONSE
                self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGCASUBSCRIPTIONRESPONSE'), gaugeValue = None)
                self.ipcA.addFARHandler(functionID        = caDataRecv, 
                                        handlerFunction   = self.__onCADataReceival_FAR, 
                                        executionThread   = _IPC_THREADTYPE_MT, 
                                        immediateResponse = True)
                self.ipcA.sendFAR(targetProcess  = f'ANALYZER{allocAnalyzer}',
                                  functionID     = 'registerCurrencyAnalysisSubscription',
                                  functionParams = {'currencyAnalysisCode': caCode,
                                                    'dataReceiver':         caDataRecv},
                                  farrHandler    = self.__onSubscriptionRequestResponse_FARR)
                
        #---[3-3]: Currency Analysis Configuration Update
        elif updateType == 'UPDATE_CURRENCYANALYSISCONFIGURATION':
            cac = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode, 'currencyAnalysisConfiguration'))

        #---[3-4]: Removal
        elif updateType == 'REMOVED': 
            self.setTarget(currencyAnalysisCode = None)

    def __onSubscriptionRequestResponse_FARR(self, responder, requestID, functionResult):
        #[1]: Source Check
        ca = self.__currencyAnalysis
        if not responder.startswith("ANALYZER"):
            return
        if ca is None or ca['allocatedAnalyzer'] != int(responder[8:]):
            return
        
        #[2]: Currency Analysis Code Check
        caCode = functionResult['currencyAnalysisCode']
        if caCode != self.__currencyAnalysisCode:
            return
        
        #[3]: Analysis Parameters Read
        #---[3-1]: Data Formatting
        aParams_ca = functionResult['analysisParams']
        dAgg       = self._data_agg
        dTSs       = self._data_timestamps
        for iID, aParams_iID in aParams_ca.items():
            dAgg[iID] = {target: dict() for target in ('kline', 'depth', 'aggTrade')}
            dTSs[iID] = {target: list() for target in ('kline', 'depth', 'aggTrade')}
            dAgg_iID = dAgg[iID]
            dTSs_iID = dTSs[iID]
            for aCode in aParams_iID:
                dAgg_iID[aCode] = dict()
                dTSs_iID[aCode] = list()
        self.analysisParams = aParams_ca
        #---[3-2]: Aggregation Interval ID
        aParams   = self.analysisParams
        abp_GUIOs = self.auxBarPage.GUIOs
        aux       = auxiliaries
        intervalID = None
        for iID in (aux.KLINE_INTERVAL_ID_1m,
                    aux.KLINE_INTERVAL_ID_3m,
                    aux.KLINE_INTERVAL_ID_5m,
                    aux.KLINE_INTERVAL_ID_15m,
                    aux.KLINE_INTERVAL_ID_30m,
                    aux.KLINE_INTERVAL_ID_1h,
                    aux.KLINE_INTERVAL_ID_2h,
                    aux.KLINE_INTERVAL_ID_4h,
                    aux.KLINE_INTERVAL_ID_6h,
                    aux.KLINE_INTERVAL_ID_8h,
                    aux.KLINE_INTERVAL_ID_12h,
                    aux.KLINE_INTERVAL_ID_1d,
                    aux.KLINE_INTERVAL_ID_3d,
                    aux.KLINE_INTERVAL_ID_1W,
                    aux.KLINE_INTERVAL_ID_1M,):
            aiSwitch = abp_GUIOs[f'AGGINTERVAL_{iID}']
            if iID in aParams: aiSwitch.activate()
            else:              aiSwitch.deactivate()
            aiSwitch.setStatus(status = False, callStatusUpdateFunction = False)
            if intervalID is None and iID in aParams: intervalID = iID
        if intervalID is None: intervalID = aux.KLINE_INTERVAL_ID_1m
        self.intervalID = intervalID
        abp_GUIOs[f'AGGINTERVAL_{intervalID}'].setStatus(status = True, callStatusUpdateFunction = True)
        #---[3-3]: SI Type Analysis Codes
        self._updateSITypeAnalysisCodes()

        #[4]: Mode & Loading Cover Update
        ca_status = ca['status']
        if ca_status == 'ANALYZING':
            self.__mode = _TYPEMODE_RECEIVING
            self._setLoadingCover(show = False, text = None, gaugeValue = None)
        else:
            self.__mode = _TYPEMODE_WAITINGANALYZING
            self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGANALYZING'), gaugeValue = None)

    def __onCADataReceival_FAR(self, requester, currencyAnalysisCode, data_agg = None):
        #[1]: Source Check
        ca = self.__currencyAnalysis
        if not requester.startswith("ANALYZER"):
            return
        if ca is None or ca['allocatedAnalyzer'] != int(requester[8:]):
            return
        
        #[2]: Currency Analysis Code Check
        caCode = currencyAnalysisCode
        if caCode != self.__currencyAnalysisCode:
            return
        
        #[3]: Received Data
        dAgg_ca = data_agg
        if dAgg_ca is None: #data_agg is None when the currency analysis is restarted
            self.setTarget(target = self.__currencyAnalysisCode)
            return
        
        #[4]: Data Record & Draw Queue Update
        dAgg    = self._data_agg
        dTSs    = self._data_timestamps
        intervalID     = self.intervalID
        func_addDQueue = self._addDrawQueue
        func_removeED  = self._drawer_RemoveExpiredDrawings
        func_gnitt     = auxiliaries.getNextIntervalTickTimestamp
        firstReceival  = not any(dAgg[intervalID][target]
                                 for target in dAgg[intervalID])
        for iID in dAgg:
            dAgg_ca_iID = dAgg_ca[iID]
            dAgg_iID    = dAgg[iID]
            dTSs_iID    = dTSs[iID]
            dispLength  = ca['currencyAnalysisConfiguration'][iID]['NI_NAnalysisToDisplay']
            for target in dAgg_iID:
                dAgg_ca_iID_target = dAgg_ca_iID[target]
                dAgg_iID_target    = dAgg_iID[target]
                dTSs_iID_target    = dTSs_iID[target]
                for dTS in sorted(dAgg_ca_iID_target):
                    #[3-1]: Data Record
                    if dTS not in dAgg_iID_target:
                        dTSs_iID_target.append(dTS)
                    dAgg_iID_target[dTS] = dAgg_ca_iID_target[dTS]
                    #[3-2]: Draw Queue
                    if iID == intervalID:
                        if   target == 'kline':    tCodes = ['KLINE',]
                        elif target == 'depth':    tCodes = ['DEPTHOVERLAY', 'DEPTH']
                        elif target == 'aggTrade': tCodes = ['AGGTRADE',]
                        else:                      tCodes = [target,]
                        func_addDQueue(targetCodes = tCodes, 
                                       timestamp   = dTS)
                    #[3-3]: Expired Removal
                    dTS_expired = func_gnitt(intervalID = iID, timestamp = dTS, nTicks = -(dispLength-1))-1
                    dTS_remove  = dTSs_iID_target[0]
                    while dTS_remove <= dTS_expired:
                        dTSs_iID_target.pop(0)
                        del dAgg_iID_target[dTS_remove]
                        func_removeED(timestamp = dTS_remove)
                        dTS_remove = dTSs_iID_target[0]
                        
        #[5]: First Receival View Range Reset
        if firstReceival:
            self._onHViewRangeUpdate(1)
            self._editVVR_toExtremaCenter('KLINESPRICE')
            for sivCode in self.displayBox_graphics_visibleSIViewers: self._editVVR_toExtremaCenter(sivCode)
                
    def _onAggregationIntervalUpdate(self, previousIntervalID):
        #[1]: Instances
        ca  = self.__currencyAnalysis
        iID = self.intervalID

        #[2]: Currency Analysis Configuration
        if ca is None:
            self._data_agg[iID]        = {target: dict() for target in ('kline', 'depth', 'aggTrade')}
            self._data_timestamps[iID] = {target: list() for target in ('kline', 'depth', 'aggTrade')}
        else:
            self._readCurrencyAnalysisConfiguration(currencyAnalysisConfiguration = ca['currencyAnalysisConfiguration'][iID])

    