#ATM Modules
from .chart_drawer import chartDrawer
import auxiliaries
import ipc
import analyzers

#Python Modules
import time
from collections import deque

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
_TYPEMODE_WAITINGANALYZING            = 2
_TYPEMODE_WAITINGSUBSCRIPTIONRESPONSE = 3
_TYPEMODE_WAITINGANALYSISRESULT       = 4
_TYPEMODE_RECEIVING                   = 5

#Chart Drawer CA Viewer Subclass
class chartDrawer_caViewer(chartDrawer):
    def __init__(self, **kwargs):
        self.chartDrawerType = "CAVIEWER"
        super().__init__(**kwargs)
        self.__typeInit()
        self.setTarget(target = None)

    def __typeInit(self):
        #[1]: Instances
        ssps       = self.settingsSubPages
        guios_MAIN = ssps['MAIN'].GUIOs

        #[2]: MAIN
        guios_MAIN["ANALYZER_ANALYSISRANGEBEG_RANGEINPUT"].deactivate()
        guios_MAIN["ANALYZER_ANALYSISRANGEEND_RANGEINPUT"].deactivate()
        guios_MAIN["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()

        #[3]: INDICATORS
        for amType, am in analyzers.ANALYSES.items():
            am['FN_TYPEINIT'](subPage = ssps[amType])

        #[4]: TRADELOG
        guios_MAIN["TRADELOGCOLOR_TARGETSELECTION"].deactivate()
        guios_MAIN["TRADELOGCOLOR_APPLYCOLOR"].deactivate()
        guios_MAIN["TRADELOGCOLOR_R_SLIDER"].deactivate()
        guios_MAIN["TRADELOGCOLOR_G_SLIDER"].deactivate()
        guios_MAIN["TRADELOGCOLOR_B_SLIDER"].deactivate()
        guios_MAIN["TRADELOGCOLOR_A_SLIDER"].deactivate()
        guios_MAIN["TRADELOGDISPLAY_SWITCH"].deactivate()
        guios_MAIN["TRADELOG_APPLYNEWSETTINGS"].deactivate()

        #[5]: Type Unique Variables
        self.__mode                    = None
        self.__currencyAnalysisCode    = None
        self.__currencyAnalysis        = None
        self.__currencyAnalysis_rID    = None
        self.__currencyAnalysis_buffer = deque()
        self.__firstAnalysisResult     = True

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
                                                'dataReceiver':         caDataRecv,
                                                'subRequestID':         self.__currencyAnalysis_rID},
                              farrHandler    = None)
        self.__currencyAnalysisCode = target
        self.__currencyAnalysis     = None if self.__currencyAnalysisCode is None else self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', target))
        self.currencySymbol         = None if self.__currencyAnalysis     is None else self.__currencyAnalysis['currencySymbol']
        self.currencyInfo           = None if self.currencySymbol         is None else self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol))
        if self.__currencyAnalysisCode is None: self._updateTargetText(text = "-")
        else:                                   self._updateTargetText(text = f"{self.__currencyAnalysisCode} [{self.currencySymbol}]")
        self.__currencyAnalysis_rID    = None
        self.__currencyAnalysis_buffer = deque()
        self.__firstAnalysisResult     = True
            
        #[2]: Type Mode
        if self.__currencyAnalysisCode is None: self.__mode = _TYPEMODE_PENDING
        else:
            allocAnalyzer = self.__currencyAnalysis['allocatedAnalyzer']
            if allocAnalyzer is None: self.__mode = _TYPEMODE_WAITINGALLOCATION
            else:                     self.__mode = _TYPEMODE_WAITINGANALYZING

        #[3]: Loading Cover
        if   self.__mode == _TYPEMODE_PENDING:           self._setLoadingCover(show = False, text = None,                                                                         gaugeValue = None)
        elif self.__mode == _TYPEMODE_WAITINGALLOCATION: self._setLoadingCover(show = True,  text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGANALYZERALLOCATION'), gaugeValue = None)
        elif self.__mode == _TYPEMODE_WAITINGANALYZING:  self._setLoadingCover(show = True,  text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGANALYZING'),          gaugeValue = None)

        #[4]: Data
        aux = auxiliaries
        self.intervalID = aux.KLINE_INTERVAL_ID_1m
        self._clearData()
        self._clearDrawers()

        #[5]: Initialize Highlighters and Descriptors
        if self.__currencyAnalysisCode is not None:
            self._clearHighlightsAndDescriptors()

        #[6]: Aggregation Interval Buttons
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

        #[7]: Analysis Params Initialization
        self.analysisParams = {self.intervalID: dict()}

        #[8]: View Control
        #---[8-1]: Horizontal View Range Parameters Setup
        self._setHVRParams()
        #---[8-2]: RCLCGs Reset
        self._initializeRCLCGs('KLINESPRICE')
        for sivCode in self.displayBox_graphics_visibleSIViewers: self._initializeSIViewer(sivCode)
        #---[8-3] Horizontal View Range Update
        self.horizontalViewRange_magnification = 80
        hvr_new_end = round(time.time()+self.expectedKlineTemporalWidth*5)
        hvr_new_beg = round(hvr_new_end-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
        hvr_new = [hvr_new_beg, hvr_new_end]
        tz_rev  = -self.timezoneDelta
        if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]
        self.horizontalViewRange = hvr_new
        self._onHViewRangeUpdate(1)
        #---[8-4]: Vertical View Range Reset
        self._editVVR_toExtremaCenter('KLINESPRICE')
        for sivCode in self.displayBox_graphics_visibleSIViewers: self._editVVR_toExtremaCenter(sivCode)

        #[9]: SI Type Analysis Codes Update
        self._updateSITypeAnalysisCodes()

        #[10]: Empty Currency Analysis Configuration Read
        cac = None if self.__currencyAnalysisCode is None else self.__currencyAnalysis['currencyAnalysisConfiguration'][self.intervalID]
        self._readCurrencyAnalysisConfiguration(currencyAnalysisConfiguration = cac)

        #[11]: Stream Subscription Registration
        if self.__mode == _TYPEMODE_WAITINGANALYZING and self.__currencyAnalysis['status'] == 'ANALYZING':
            self.__registerStreamSubscription()
            self.__mode = _TYPEMODE_WAITINGSUBSCRIPTIONRESPONSE
            self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGCASUBSCRIPTIONRESPONSE'), gaugeValue = None)

    def _process_typeUnique(self, mei_beg):
        #[1]: Waiting Analyzing
        if self.__mode == _TYPEMODE_WAITINGANALYZING:
            self.__currencyAnalysis = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', self.__currencyAnalysisCode))
            ca_status = self.__currencyAnalysis['status']
            if ca_status == 'ANALYZING':
                self.__registerStreamSubscription()
                self.__mode = _TYPEMODE_WAITINGSUBSCRIPTIONRESPONSE
                self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGCASUBSCRIPTIONRESPONSE'), gaugeValue = None)

        #[2]: Currency Analysis Data Buffer Processing
        if self.__mode in (_TYPEMODE_WAITINGANALYSISRESULT,
                           _TYPEMODE_RECEIVING):
            self.__processCurrencyAnalysisBuffer()

        #[3]: Return False To Inidicate Not Busy
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
                    self.__registerStreamSubscription()
                    self.__mode = _TYPEMODE_WAITINGSUBSCRIPTIONRESPONSE
                    self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGCASUBSCRIPTIONRESPONSE'), gaugeValue = None)
            if status == 'ERROR':
                self.__mode = _TYPEMODE_PENDING
                self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:CAERROROCCURRED'), gaugeValue = None)

        #---[3-2]: Analyzer Update
        elif updateType == 'UPDATE_ANALYZER':
            if mode == _TYPEMODE_WAITINGALLOCATION:
                allocAnalyzer           = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode, 'allocatedAnalyzer'))
                ca['allocatedAnalyzer'] = allocAnalyzer
                if ca['status'] == 'ANALYZING':
                    self.__registerStreamSubscription()
                    self.__mode = _TYPEMODE_WAITINGSUBSCRIPTIONRESPONSE
                    self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGCASUBSCRIPTIONRESPONSE'), gaugeValue = None)
                else:
                    self.__mode = _TYPEMODE_WAITINGANALYZING
                    self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGANALYZING'), gaugeValue = None)
                
        #---[3-3]: Currency Analysis Configuration Update
        elif updateType == 'UPDATE_CURRENCYANALYSISCONFIGURATION':
            cac = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode, 'currencyAnalysisConfiguration'))

        #---[3-4]: Removal
        elif updateType == 'REMOVED': 
            self.setTarget(setTarget = None)

    def __registerStreamSubscription(self):
        caDataRecv    = f"caDataReceiver_{self.name}"
        allocAnalyzer = self.__currencyAnalysis['allocatedAnalyzer']
        self.ipcA.addFARHandler(functionID        = caDataRecv,
                                handlerFunction   = self.__onCADataReceival_FAR,
                                executionThread   = _IPC_THREADTYPE_MT,
                                immediateResponse = True)
        self.__currencyAnalysis_rID = self.ipcA.sendFAR(targetProcess  = f'ANALYZER{allocAnalyzer}',
                                                        functionID     = 'registerCurrencyAnalysisSubscription',
                                                        functionParams = {'currencyAnalysisCode': self.__currencyAnalysisCode,
                                                                          'dataReceiver':         caDataRecv},
                                                        farrHandler    = self.__onSubscriptionRequestResponse_FARR)

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
        
        #[3]: Subscription Request ID Check
        if requestID != self.__currencyAnalysis_rID:
            return
        
        #[4]: Analysis Parameters Read
        #---[4-1]: Data Formatting
        aParams_ca = functionResult['analysisParams']
        dAgg       = self._data_agg
        dTSs       = self._data_timestamps
        dAgg.clear()
        dTSs.clear()
        for iID, aParams_iID in aParams_ca.items():
            dAgg[iID] = {target: dict() for target in ('kline', 'depth', 'aggTrade')}
            dTSs[iID] = {target: list() for target in ('kline', 'depth', 'aggTrade')}
            dAgg_iID = dAgg[iID]
            dTSs_iID = dTSs[iID]
            for aCode in aParams_iID:
                dAgg_iID[aCode] = dict()
                dTSs_iID[aCode] = list()
        self.analysisParams = aParams_ca
        #---[4-2]: Aggregation Interval ID
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

        #[5]: View Control
        #---[5-1]: Horizontal View Range Parameters Setup
        self._setHVRParams()
        #---[5-2]: RCLCGs Reset
        self._initializeRCLCGs('KLINESPRICE')
        for sivCode in self.displayBox_graphics_visibleSIViewers: self._initializeSIViewer(sivCode)
        #---[5-3] Horizontal View Range Update
        self.horizontalViewRange_magnification = 80
        hvr_new_end = round(time.time()+self.expectedKlineTemporalWidth*5)
        hvr_new_beg = round(hvr_new_end-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
        hvr_new = [hvr_new_beg, hvr_new_end]
        tz_rev  = -self.timezoneDelta
        if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]
        self.horizontalViewRange = hvr_new
        self._onHViewRangeUpdate(1)
        #---[5-4]: Vertical View Range Reset
        self._editVVR_toExtremaCenter('KLINESPRICE')
        for sivCode in self.displayBox_graphics_visibleSIViewers: self._editVVR_toExtremaCenter(sivCode)

        #[6]: SI Type Analysis Codes
        self._updateSITypeAnalysisCodes()

        #[7]: Mode & Loading Cover Update
        self.__mode = _TYPEMODE_WAITINGANALYSISRESULT
        self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGANALYSISRESULT'), gaugeValue = None)

    def __onCADataReceival_FAR(self, requester, currencyAnalysisCode, subRequestID, data_agg = None):
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
        
        #[3]: Subscription Request ID Check
        if subRequestID != self.__currencyAnalysis_rID:
            return
        
        #[4]: Received Data
        dAgg_ca = data_agg
        if dAgg_ca is None: #data_agg is None when the currency analysis is restarted
            self.setTarget(target = self.__currencyAnalysisCode)
            return
        
        #[5]: Buffer Update
        self.__currencyAnalysis_buffer.append(data_agg)
        
    def __processCurrencyAnalysisBuffer(self):
        #[1]: Instances
        intervalID = self.intervalID
        dAgg       = self._data_agg
        dTSs       = self._data_timestamps
        ca         = self.__currencyAnalysis
        caBuffer   = self.__currencyAnalysis_buffer
        func_addDQueue = self._addDrawQueue
        func_removeED  = self._drawer_RemoveExpiredDrawings
        func_gnitt     = auxiliaries.getNextIntervalTickTimestamp

        #[2]: Buffer Processing
        while caBuffer:
            #[2-1]: Buffer Item
            dAgg_ca = caBuffer.popleft()

            #[2-2]: Data Save
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
                        #[2-2-1]: Data Record
                        if dTS not in dAgg_iID_target:
                            dTSs_iID_target.append(dTS)
                        dAgg_iID_target[dTS] = dAgg_ca_iID_target[dTS]
                        #[2-2-2]: Draw Queue
                        if iID == intervalID:
                            if   target == 'kline':    tCodes = ['KLINE',]
                            elif target == 'depth':    tCodes = ['DEPTHOVERLAY', 'DEPTH']
                            elif target == 'aggTrade': tCodes = ['AGGTRADE',]
                            else:                      tCodes = [target,]
                            func_addDQueue(targetCodes = tCodes, 
                                        timestamp   = dTS)
                        #[2-2-3]: Expired Removal
                        dTS_expired = func_gnitt(intervalID = iID, timestamp = dTS, nTicks = -(dispLength-1))-1
                        dTS_remove  = dTSs_iID_target[0]
                        while dTS_remove <= dTS_expired:
                            dTSs_iID_target.pop(0)
                            del dAgg_iID_target[dTS_remove]
                            func_removeED(timestamp = dTS_remove)
                            dTS_remove = dTSs_iID_target[0]
                            
            #[2-3]: First Receival View Range Reset
            if self.__firstAnalysisResult:
                #[2-3-1]: Mode & Loading Cover Update
                self.__mode = _TYPEMODE_RECEIVING
                self._setLoadingCover(show = False, text = None, gaugeValue = None)
                #[2-3-2]: View Range Reset
                self._onHViewRangeUpdate(1)
                self._editVVR_toExtremaCenter('KLINESPRICE')
                for sivCode in self.displayBox_graphics_visibleSIViewers: 
                    self._editVVR_toExtremaCenter(sivCode)
                #[2-3-3]: First Analysis Result Flag Lowering
                self.__firstAnalysisResult = False
                
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

    