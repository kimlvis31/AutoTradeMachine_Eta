#ATM Modules
from .chart_drawer import (chartDrawer,
                           _NMAXLINES,
                           _MITYPES,
                           _SITYPES)
import auxiliaries
import analyzers
import ipc
import neural_networks
import constants

#Python Modules
import time
import termcolor
import torch
import pprint
import gc
from datetime import datetime, timezone, tzinfo
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

FORMATTEDDATATYPE_FETCHED    = 0
FORMATTEDDATATYPE_EMPTY      = 1
FORMATTEDDATATYPE_DUMMY      = 2
FORMATTEDDATATYPE_STREAMED   = 3
FORMATTEDDATATYPE_INCOMPLETE = 4

COMMONDATAINDEXES = {'openTime':  {'kline': KLINDEX_OPENTIME,  'depth': DEPTHINDEX_OPENTIME,  'aggTrade': ATINDEX_OPENTIME},
                     'closeTime': {'kline': KLINDEX_CLOSETIME, 'depth': DEPTHINDEX_CLOSETIME, 'aggTrade': ATINDEX_CLOSETIME},
                     'closed':    {'kline': KLINDEX_CLOSED,    'depth': DEPTHINDEX_CLOSED,    'aggTrade': ATINDEX_CLOSED},
                     'source':    {'kline': KLINDEX_SOURCE,    'depth': DEPTHINDEX_SOURCE,    'aggTrade': ATINDEX_SOURCE}}

_DUMMYFRAMES = {'kline':    (None, None, None, None, None, None, None, None, None,                   True, FORMATTEDDATATYPE_DUMMY),
                'depth':    (None, None, None, None, None, None, None, None, None, None, None, None, True, FORMATTEDDATATYPE_DUMMY),
                'aggTrade': (None, None, None, None, None, None,                                     True, FORMATTEDDATATYPE_DUMMY)}

KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S

_TYPEMODE_PENDING                              = 0
_TYPEMODE_WAITINGSTREAM                        = 1
_TYPEMODE_WAITINGFIRSTOPENTS                   = 2
_TYPEMODE_WAITINGDATAAVAILABLE                 = 3
_TYPEMODE_FETCHINGMARKETDATA                   = 4
_TYPEMODE_AGGREGATING                          = 5
_TYPEMODE_WAITINGNEURALNETWORKSCONNECTIONSDATA = 6
_TYPEMODE_READY                                = 7

_STREAMCONTINUITY_REVERSE = 0
_STREAMCONTINUITY_NORMAL  = 1
_STREAMCONTINUITY_FUTURE  = 2

_DATAFETCHCHUNKSIZE   = 43_200
_AGGREGATIONCHUNKSIZE = 14_400

_TIMELIMIT_DATAPROCESS_NS                   = 100e6
_AUX_NANALYSISQUEUEDISPLAYUPDATEINTERVAL_NS = 100e6

_DRAWQUEUEADDTARGETCODES = {'kline':    ('KLINE', 'VOL'),
                            'depth':    ('DEPTHOVERLAY', 'DEPTH'),
                            'aggTrade': ('AGGTRADE',)}

_ANALYSIS_GENERATIONORDER = analyzers.ANALYSIS_GENERATIONORDER

#Chart Drawer Analyzer Subclass
class chartDrawer_analyzer(chartDrawer):
    def __init__(self, **kwargs):
        self.chartDrawerType = "ANALYZER"
        super().__init__(**kwargs)
        self.__typeInit()
        self.setTarget(target = None)

    def __typeInit(self):
        #[1]: Trade Log Graphics Control GUIOs Deactivation
        guios_MAIN = self.settingsSubPages['MAIN'].GUIOs
        guios_MAIN["TRADELOGCOLOR_TARGETSELECTION"].deactivate()
        guios_MAIN["TRADELOGCOLOR_APPLYCOLOR"].deactivate()
        guios_MAIN["TRADELOGCOLOR_R_SLIDER"].deactivate()
        guios_MAIN["TRADELOGCOLOR_G_SLIDER"].deactivate()
        guios_MAIN["TRADELOGCOLOR_B_SLIDER"].deactivate()
        guios_MAIN["TRADELOGCOLOR_A_SLIDER"].deactivate()
        guios_MAIN["TRADELOGDISPLAY_SWITCH"].deactivate()
        guios_MAIN["TRADELOG_APPLYNEWSETTINGS"].deactivate()

        #[2]: Type Unique Variables
        #---[2-1]: Mode
        self.__mode = _TYPEMODE_PENDING
        #---[2-2]: Fetch & Aggregation Control
        self.__initializeDataControl()
        #---[2-3]: Analysis
        self.__initializeAnalysisControl()

    def __initializeDataControl(self):
        #[1]: Identity & Stream Control
        self.__firstOpenTSs = {target: None for target in ('kline', 'depth', 'aggTrade')}
        self.__stream       = {target: {'firstStreamOpenTS': None,
                                        'lastStream':        None}
                               for target in ('kline', 'depth', 'aggTrade')}
        
        #[2]: Fetch Control
        self.__availabilityChecks = {target: [] for target in ('kline', 'depth', 'aggTrade')}
        self.__fetchRequests      = dict()
        self.__fetchedLeftBound   = {target: None for target in ('kline', 'depth', 'aggTrade')}

        #[3]: Aggregation Control
        self.__aggregators            = {'kline':    analyzers.aggregator_kline,
                                         'depth':    analyzers.aggregator_depth,
                                         'aggTrade': analyzers.aggregator_aggTrade}
        self.__aggregatedRanges       = {self.intervalID: {target: deque() for target in ('kline', 'depth', 'aggTrade')}}
        self.__lastClosedAggregations = {self.intervalID: {target: dict()  for target in ('kline', 'depth', 'aggTrade')}}
        self.__firstAggregation       = True
        self.__analysisAggregation    = False

    def __initializeAnalysisControl(self):
        #[1]: Control Data Reset
        try:    emptyCuda = (0 < len(self.__neuralNetworkInstances))
        except: emptyCuda = False
        self.__neuralNetworkInstances                = dict()
        self.__neuralNetworkConnectionDataRequestIDs = dict()
        self.__analyzingStream          = False
        self.__analysisToProcess_Sorted = list()
        self.__analysisKwargs           = dict()
        self.__analysisQueue            = deque()

        #[3]: Cuda Memory Clearing (If Needed)
        if emptyCuda:
            gc.collect()
            torch.cuda.empty_cache()

        #[4]: Status Display Update
        self.__lastNumberOfAnalysisQueueDisplayUpdated_ns = 0
        self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT3'].hide()

    def setTarget(self, target):
        #[1]: Target Read & Previous Subscription Unregistration
        if self.currencySymbol is not None: 
            self.ipcA.removeFARHandler(functionID = f'onKlineStreamReceival_{self.name}')
            self.ipcA.removeFARHandler(functionID = f'onDepthStreamReceival_{self.name}')
            self.ipcA.removeFARHandler(functionID = f'onAggTradeStreamReceival_{self.name}')
            self.ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                              functionID     = 'unregisterStreamSubscription', 
                              functionParams = {'subscriptionID': self.name, 
                                                'currencySymbol': self.currencySymbol}, 
                              farrHandler    = None)
        self.currencySymbol = target
        self.currencyInfo   = None if self.currencySymbol is None else self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol))
        if self.currencySymbol is None: self._updateTargetText(text = "-")
        else:                           self._updateTargetText(text = f"{self.currencySymbol}")

        #[2]: Type Mode
        if self.currencySymbol is None: self.__mode = _TYPEMODE_PENDING
        else:                           self.__mode = _TYPEMODE_WAITINGSTREAM

        #[3]: Loading Cover
        if self.currencySymbol is None: self._setLoadingCover(show = False, text = None,                                                                  gaugeValue = None)
        else:                           self._setLoadingCover(show = True,  text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGFIRSTSTREAM'), gaugeValue = None)
            
        #[4]: Data
        self._clearData()
        self.__initializeDataControl()
        self.__initializeAnalysisControl()
        self.analysisParams   = {self.intervalID: dict()}
        self.__analysisKwargs = dict()
        self._updateSITypeAnalysisCodes()

        #[5]: Initialize Highlighters and Descriptors
        if self.currencySymbol is not None:
            self._clearHighlightsAndDescriptors()

        #[6]: View Control Initialization
        self._setHVRParams()
        self._initializeRCLCGs('KLINESPRICE')
        for sivCode in self.displayBox_graphics_visibleSIViewers: 
            self._initializeSIViewer(sivCode)
        self._clearDrawers()

        #[7]: View Range Reset
        self.horizontalViewRange_magnification = 80
        hvr_new_end = round(time.time()+self.expectedKlineTemporalWidth*5)
        hvr_new_beg = round(hvr_new_end-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
        hvr_new = [hvr_new_beg, hvr_new_end]
        tz_rev  = -self.timezoneDelta
        if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]
        self.horizontalViewRange = hvr_new
        self._onHViewRangeUpdate(updateType = 1, onNewTarget = True)
        self._editVVR_toExtremaCenter('KLINESPRICE')
        for sivCode in self.displayBox_graphics_visibleSIViewers: 
            self._editVVR_toExtremaCenter(sivCode)

        #[8]: Stream Subscription Registration
        if self.currencySymbol is None:
            self.__onDataFetchComplete()
        else: 
            self.ipcA.addFARHandler(f'onKlineStreamReceival_{self.name}',    self.__onKlineStreamReceival,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
            self.ipcA.addFARHandler(f'onDepthStreamReceival_{self.name}',    self.__onDepthStreamReceival,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
            self.ipcA.addFARHandler(f'onAggTradeStreamReceival_{self.name}', self.__onAggTradeStreamReceival, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
            self.ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                              functionID     = 'registerStreamSubscription', 
                              functionParams = {'subscriptionID': self.name, 
                                                'currencySymbol': self.currencySymbol},
                              farrHandler    = None)
    
    def _process_typeUnique(self, mei_beg):
        #[1]: Aggregation
        if self.__mode == _TYPEMODE_AGGREGATING:
            #[1-1]: Aggregation & Completion Checks
            aggCompletes = [self.__aggregateData(target = target) for target in ('kline', 'depth', 'aggTrade')]

            #[1-2]: Post-Aggregation Handling
            if all(aggCompletes):
                self.__onAggregationComplete()
                return False
            else:
                cicTS       = auxiliaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = time.time(), nTicks = 0)-1
                flb         = self.__fetchedLeftBound
                aggedRanges = self.__aggregatedRanges[self.intervalID]
                tWidthSum = 0
                pWidthSum = 0
                flbs_min  = min(flb[target] for target in ('kline', 'depth', 'aggTrade'))
                for target in ('kline', 'depth', 'aggTrade'):
                    aggedRanges_target = aggedRanges[target]
                    if self.__analysisAggregation:
                        baseTS = flbs_min
                    else:
                        chunkBeg = self.__getLoadChunkBeginPoint()
                        baseTS   = max(flbs_min, chunkBeg)
                    tWidthSum += (cicTS - baseTS + 1)
                    for aggedRange in aggedRanges_target:
                        overlap_beg = max(aggedRange['beg'], baseTS)
                        overlap_end = min(aggedRange['end'], cicTS)
                        if overlap_beg <= overlap_end:
                            pWidthSum += (overlap_end - overlap_beg + 1)
                self._setLoadingCover(show       = True, 
                                      text       = self.visualManager.getTextPack('GUIO_CHARTDRAWER:AGGREGATINGMARKETDATA'), 
                                      gaugeValue = pWidthSum/tWidthSum*100)
                return True

        #[2]: Analysis
        elif self.__mode == _TYPEMODE_READY:
            #[2-1]: Instances
            aQueue           = self.__analysisQueue
            func_analyzeData = self.__analyzeData

            #[2-2]: Analysis
            analyzed = False
            while aQueue and (time.perf_counter_ns()-mei_beg <= _TIMELIMIT_DATAPROCESS_NS): 
                func_analyzeData()
                analyzed = True

            #[2-3]: Description Text Update
            aQueue_len = len(aQueue)
            if analyzed and (not aQueue_len or _AUX_NANALYSISQUEUEDISPLAYUPDATEINTERVAL_NS <= time.perf_counter_ns()-self.__lastNumberOfAnalysisQueueDisplayUpdated_ns):
                dText = self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT3']
                if aQueue_len: 
                    dText.show()
                    dText.setText(f"Analysis Queue: {aQueue_len}")
                else:
                    dText.hide()
                self.__lastNumberOfAnalysisQueueDisplayUpdated_ns = time.perf_counter_ns()

            #[2-4]: Return If More Queue Exists
            return 0 < aQueue_len
        
        #[3]: Pending, Return False
        return False

    def __onDepthStreamReceival(self, requester, symbol, depth):
        #[1]: Requester & Symbol Check
        if requester != 'BINANCEAPI':     return
        if symbol != self.currencySymbol: return

        #[2]: General Handler
        self.__onDataStreamReceival(target = 'depth', stream = depth)

    def __onAggTradeStreamReceival(self, requester, symbol, aggTrade):
        #[1]: Requester & Symbol Check
        if requester != 'BINANCEAPI':     return
        if symbol != self.currencySymbol: return

        #[2]: General Handler
        self.__onDataStreamReceival(target = 'aggTrade', stream = aggTrade)

    def __onKlineStreamReceival(self, requester, symbol, kline):
        #[1]: Requester & Symbol Check
        if requester != 'BINANCEAPI':     return
        if symbol != self.currencySymbol: return

        #[2]: General Handler
        self.__onDataStreamReceival(target = 'kline', stream = kline)

    def __onDataStreamReceival(self, target, stream):
        #[1]: Instances
        sControl    = self.__stream
        sControl_dt = sControl[target]
        stream_openTime = stream[COMMONDATAINDEXES['openTime'][target]]
        stream_closed   = stream[COMMONDATAINDEXES['closed'][target]]

        #[2]: Waiting Stream
        if self.__mode == _TYPEMODE_WAITINGSTREAM:
            #[2-1]: If This Is The First Stream, Record
            if sControl_dt['firstStreamOpenTS'] is None:
                sControl_dt['firstStreamOpenTS'] = stream_openTime

            #[2-2]: Check If All Targets Received Their First Stream
            if not any(sControl[t]['firstStreamOpenTS'] is None for t in ('kline', 'depth', 'aggTrade')):
                #[2-2-1]: Latest First Stream Open TS
                fsoTS_max = max(sControl[t]['firstStreamOpenTS'] for t in ('kline', 'depth', 'aggTrade'))

                #[2-2-2]: View Range Reset
                self.horizontalViewRange_magnification = 80
                hvr_new_end = round(fsoTS_max+self.expectedKlineTemporalWidth*5)
                hvr_new_beg = round(hvr_new_end-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
                hvr_new = [hvr_new_beg, hvr_new_end]
                tz_rev  = -self.timezoneDelta
                if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]
                self.horizontalViewRange = hvr_new
                self._onHViewRangeUpdate(updateType = 1, onNewTarget = True)
                self._editVVR_toExtremaCenter('KLINESPRICE')
                for sivCode in self.displayBox_graphics_visibleSIViewers: 
                    self._editVVR_toExtremaCenter(sivCode)

                #[2-2-3]: Mode & Loading Cover Update
                self.__mode = _TYPEMODE_WAITINGFIRSTOPENTS
                self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGDATAAVAILABLE'), gaugeValue = None)

        #[3]: Waiting First Open TS
        if self.__mode == _TYPEMODE_WAITINGFIRSTOPENTS:
            #[3-1]: Instances
            symbol      = self.currencySymbol
            foTSs       = self.__firstOpenTSs
            func_getPRD = self.ipcA.getPRD

            #[3-2]: First Open TS Update
            for t, foTS in foTSs.items():
                if foTS is not None:
                    continue
                foTS_prd = func_getPRD(processName = 'DATAMANAGER', 
                                       prdAddress  = ('CURRENCIES', 
                                                      symbol, 
                                                      f'{t}_firstOpenTS'))
                if foTS_prd == _IPC_PRD_INVALIDADDRESS or foTS_prd is None:
                    continue
                foTSs[t] = foTS_prd

            #[3-3]: If All Are Identified, Update Availability Check
            if all(v is not None for v in foTSs.values()):
                self.__updateAvailabilityChecks()
                self.__mode = _TYPEMODE_WAITINGDATAAVAILABLE
                self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGDATAAVAILABLE'), gaugeValue = None)

        #[4]: Stream Continuity Check
        discontinuity = _STREAMCONTINUITY_NORMAL
        if sControl_dt['lastStream'] is not None:
            ls_openTS, ls_closed = sControl_dt['lastStream']
            nextOpenTS = auxiliaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = ls_openTS, nTicks = 1)
            if ls_closed:
                if   stream_openTime <= ls_openTS: discontinuity = _STREAMCONTINUITY_REVERSE
                elif nextOpenTS < stream_openTime: discontinuity = _STREAMCONTINUITY_FUTURE
            else:
                if   stream_openTime <  ls_openTS: discontinuity = _STREAMCONTINUITY_REVERSE
                elif ls_openTS < stream_openTime:  discontinuity = _STREAMCONTINUITY_FUTURE
            if discontinuity == _STREAMCONTINUITY_FUTURE:
                if ls_closed: aCheck = (nextOpenTS, stream_openTime-1)
                else:         aCheck = (ls_openTS,  stream_openTime-1)
                self.__availabilityChecks[target].append(aCheck)
                if self.__mode not in (_TYPEMODE_WAITINGSTREAM, _TYPEMODE_WAITINGFIRSTOPENTS):
                    self.__mode = _TYPEMODE_WAITINGDATAAVAILABLE
                    self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGDATAAVAILABLE'), gaugeValue = None)

        #[5]: If Waiting Data Available (If All Targets Are Available, Dispatch Fetch Requests)
        if self.__mode == _TYPEMODE_WAITINGDATAAVAILABLE:
            if self.__checkDataAvailable():
                if self.__dispatchDataRequests():
                    self.__mode = _TYPEMODE_FETCHINGMARKETDATA
                    self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:FETCHINGMARKETDATA'), gaugeValue = self.__computeFetchCompletion())
                else:
                    self.__mode = _TYPEMODE_AGGREGATING
                    self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:AGGREGATINGMARKETDATA'), gaugeValue = 0)

        #[6]: Data Record
        if discontinuity != _STREAMCONTINUITY_REVERSE:
            #[6-1]: Last Stream Record
            sControl_dt['lastStream'] = (stream_openTime, stream_closed)
            #[6-2]: Raw Data Record
            self._data_raw[target][stream_openTime] = stream
            #[6-3]: Aggregation Queue
            if self.__mode == _TYPEMODE_READY and discontinuity == _STREAMCONTINUITY_NORMAL:
                self.__aggregateData(target = target)

    def __updateAvailabilityChecks(self, analysisBegin = None):
        #[1]: Instances
        foTSs    = self.__firstOpenTSs
        sControl = self.__stream
        aChecks  = self.__availabilityChecks
        flb      = self.__fetchedLeftBound
        
        #[2]: Availability Checks Update
        aCheck_beg = None
        #---[2-1]: View Range Mode
        if analysisBegin is None:
            aCheck_beg = self.__getLoadChunkBeginPoint()

        #---[2-2]: Analysis Range Mode
        else:
            aCheck_beg = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, 
                                                                  timestamp  = analysisBegin, 
                                                                  nTicks     = 0)

        #---[2-3]: Check List Update
        if aCheck_beg is not None:
            for t, foTS in foTSs.items():
                flb_t = flb[t]
                if flb_t is None: aCheck = (max(foTS, aCheck_beg), sControl[t]['firstStreamOpenTS']-1)
                else:             aCheck = (max(foTS, aCheck_beg), flb_t                           -1)
                if aCheck[1] < aCheck[0]:
                    continue
                aChecks[t].append(aCheck)

        #[3]: Mode Update
        return any(aChecks_t for aChecks_t in aChecks.values())

    def __checkDataAvailable(self):
        #[1]: Currency Data
        cInfo = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol))
        if cInfo == _IPC_PRD_INVALIDADDRESS or not cInfo: 
            return False

        #[2]: Availability Check
        for target in ('kline', 'depth', 'aggTrade'):
            aRanges = cInfo[f'{target}s_availableRanges']
            if not aRanges:
                return False
            for aCheck_beg, aCheck_end in self.__availabilityChecks[target]:
                if not any(((aRange[0] <= aCheck_beg) and (aCheck_end <= aRange[1])) for aRange in aRanges):
                    return False
                
        #[3]: If Reached Here, All Are Available. Return True.
        return True
    
    def __dispatchDataRequests(self):
        #[1]: Instances
        symbol  = self.currencySymbol
        aChecks = self.__availabilityChecks
        frs     = self.__fetchRequests
        func_gnitt    = auxiliaries.getNextIntervalTickTimestamp
        func_sendFAR  = self.ipcA.sendFAR
        func_frr_farr = self.__onFetchRequestResponse_FARR

        #[2]: Requests Dispatch
        for t in ('kline', 'depth', 'aggTrade'):
            for aCheck_beg, aCheck_end in aChecks[t]:
                chunkBeg = aCheck_beg
                while chunkBeg <= aCheck_end:
                    chunkEnd_max = func_gnitt(intervalID = KLINTERVAL, timestamp = chunkBeg, nTicks = _DATAFETCHCHUNKSIZE)-1
                    chunkEnd_eff = min(chunkEnd_max, aCheck_end)
                    rID = func_sendFAR(targetProcess  = 'DATAMANAGER',
                                       functionID     = 'fetchMarketData',
                                       functionParams = {'symbol':     symbol,
                                                         'target':     t,
                                                         'fetchRange': (chunkBeg, chunkEnd_eff)},
                                       farrHandler    = func_frr_farr)
                    frs[rID] = {'target':            t,
                                'fetchRequestRange': (chunkBeg, chunkEnd_eff),
                                'fetchedRange':      None,
                                'complete':          False}
                    chunkBeg = chunkEnd_eff+1
            aChecks[t].clear()

        #[3]: Mode & Loading Cover Update
        return (0 < len(frs)) 

    def __computeFetchCompletion(self):
        if not self.__fetchRequests:
            return 100.0
        frrWidth_sum = 0
        frWidth_sum  = 0
        for fReq in self.__fetchRequests.values():
            frr = fReq['fetchRequestRange']
            fr  = fReq['fetchedRange']
            frrWidth_sum += (frr[1]-frr[0]+1)
            if fr is not None: frWidth_sum += (fr[1]-fr[0]+1)
        return frWidth_sum/frrWidth_sum*100

    def __onFetchRequestResponse_FARR(self, responder, requestID, functionResult):
        #[1]: Instances
        fr_result     = functionResult['result']
        fr_data       = functionResult['data']
        fr_fetchRange = functionResult.get('fetchRange', None)

        #[2]: Request ID Check
        fReq = self.__fetchRequests.get(requestID, None)
        if fReq is None:
            return
        target = fReq['target']

        #[3]: Result Check <TO BE IMPLEMENTED>
        if fr_result != 'SDF':
            if fr_result == 'SNF':
                return
            elif fr_result == 'UDT':
                return
            elif fr_result == 'DNA':
                return
            elif fr_result == 'UEO':
                return
            else:
                return

        #[4]: Data Record
        dRaw_target   = self._data_raw[target]
        dIdx_openTime = COMMONDATAINDEXES['openTime'][target]
        for dl in fr_data:
            dRaw_target[dl[dIdx_openTime]] = dl

        #[5]: Fetched Range Tracker
        if fr_data:
            flb         = self.__fetchedLeftBound
            flb[target] = fr_data[0][dIdx_openTime] if flb[target] is None else min(flb[target], fr_data[0][dIdx_openTime])

        #[6]: Completion Check & Fetch Continuation
        fReq['complete']     = True
        fReq['fetchedRange'] = [fr_fetchRange[0], fr_fetchRange[1]]

        #[7]: Status Control
        self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:FETCHINGMARKETDATA'), gaugeValue = self.__computeFetchCompletion())
        if all(_fReq['complete'] for _fReq in self.__fetchRequests.values()): 
            self.__onDataFetchComplete()

    def __onDataFetchComplete(self):
        #[1]: Clear Fetch Requests
        self.__fetchRequests.clear()

        #[2]: Dummy Filling
        dRaw     = self._data_raw
        sControl = self.__stream
        flb      = self.__fetchedLeftBound
        flbs     = [flb_t for target in ('kline', 'depth', 'aggTrade') if (flb_t := flb[target]) is not None]
        if flbs:
            func_gnitt = auxiliaries.getNextIntervalTickTimestamp
            tTSs_raw   = auxiliaries.getTimestampList_byRange(intervalID        = KLINTERVAL, 
                                                              timestamp_beg     = min(flbs), 
                                                              timestamp_end     = max(sControl[t]['firstStreamOpenTS'] for t in ('kline', 'depth', 'aggTrade')) - 1,
                                                              lastTickInclusive = True)
            for target in ('kline', 'depth', 'aggTrade'):
                dRaw_target = dRaw[target]
                for ts in tTSs_raw:
                    if ts in dRaw_target:
                        continue
                    ts_close = func_gnitt(intervalID = KLINTERVAL, timestamp = ts, nTicks = 1)-1
                    dRaw_target[ts] = (ts, ts_close)+_DUMMYFRAMES[target]

        #[3]: Mode & Loading Cover Update
        self.__mode = _TYPEMODE_AGGREGATING
        self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:AGGREGATINGMARKETDATA'), gaugeValue = 0)

    def _onAggregationIntervalUpdate(self, previousIntervalID):
        #[1]: Previous Aggregation
        dAgg_prevIID = self._data_agg[previousIntervalID]
        dType_base   = {'kline', 'depth', 'aggTrade'}
        for dType in list(dAgg_prevIID):
            if dType in dType_base: continue
            self._drawer_RemoveDrawings(analysisCode = dType, gRemovalSignal = None)
            del dAgg_prevIID[dType]
        del self.analysisParams[previousIntervalID]

        #[2]: Analysis Control Initializaiton
        self.__initializeAnalysisControl()

        #[3]: Loading Cover Open
        self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:AGGREGATINGMARKETDATA'), gaugeValue = 0)

        #[4]: Aggregation
        if self.intervalID not in self._data_agg:
            self._data_agg[self.intervalID]                = {target: dict()  for target in ('kline', 'depth', 'aggTrade')}
            self._data_timestamps[self.intervalID]         = {target: list()  for target in ('kline', 'depth', 'aggTrade')}
            self.__aggregatedRanges[self.intervalID]       = {target: deque() for target in ('kline', 'depth', 'aggTrade')}
            self.__lastClosedAggregations[self.intervalID] = {target: dict()  for target in ('kline', 'depth', 'aggTrade')}
        self.__firstAggregation    = True
        self.__analysisAggregation = False

        #[5]: Analysis Parameters & Control Reset
        self.analysisParams[self.intervalID] = dict()

        #[6]: Mode Update
        self.__mode = _TYPEMODE_AGGREGATING

        #[7]: Loading Cover
        self._setLoadingCover(show = False, text = "-", gaugeValue = None)

    def __aggregateData(self, target):
        #[1]: Instances
        cInfo         = self.currencyInfo
        hVR0, hVR1    = self.horizontalViewRange
        dRaw_target   = self._data_raw[target]
        dAgg_target   = self._data_agg[self.intervalID][target]
        dTSs          = self._data_timestamps[self.intervalID]
        dTSs_target   = dTSs[target]
        lcAggs_target = self.__lastClosedAggregations[self.intervalID][target]
        aggregator    = self.__aggregators[target]
        aQueue        = self.__analysisQueue
        func_gnitt    = auxiliaries.getNextIntervalTickTimestamp

        #[2]: Aggregation Begin Timestamp
        #---[2-1]: Fetched Left Bound Check
        flb          = self.__fetchedLeftBound
        flbs         = [flb_t for target in ('kline', 'depth', 'aggTrade') if (flb_t := flb[target]) is not None]
        if not flbs:
            return True
        #---[2-2]: Aggregation Start Point Determination
        flbs_min    = min(flbs)
        aggedRanges = self.__aggregatedRanges[self.intervalID][target]
        if self.__analysisAggregation:
            effBeg = flbs_min
        else:
            chunkBeg       = self.__getLoadChunkBeginPoint()
            effBeg         = max(flbs_min, chunkBeg)
        if not aggedRanges or effBeg < aggedRanges[0]['beg']:
            aggBeg = effBeg
        else:
            aggedRange0 = aggedRanges[0]
            if aggedRange0['end_closed']: aggBeg = func_gnitt(intervalID = KLINTERVAL, timestamp = aggedRange0['end'], nTicks = 1)
            else:                         aggBeg = func_gnitt(intervalID = KLINTERVAL, timestamp = aggedRange0['end'], nTicks = 0)

        #[3]: Aggregation
        dIdx_closed = COMMONDATAINDEXES['closed'][target]
        rawOpenTS   = aggBeg
        aggComplete = True
        count       = 0
        while rawOpenTS in dRaw_target:
            #[3-1]: Instances
            dl_raw    = dRaw_target[rawOpenTS]
            aggOpenTS  = func_gnitt(intervalID = self.intervalID, timestamp = rawOpenTS, nTicks = 0)
            aggCloseTS = func_gnitt(intervalID = self.intervalID, timestamp = rawOpenTS, nTicks = 1)-1

            #[3-2]: Aggregation
            if aggOpenTS not in dAgg_target: dTSs_target.append(aggOpenTS)
            aggregator(dataRaw        = dRaw_target,
                       dataAgg        = dAgg_target,
                       lastClosedAggs = lcAggs_target,
                       rawOpenTS      = rawOpenTS,
                       aggOpenTS      = aggOpenTS,
                       aggIntervalID  = self.intervalID,
                       precisions     = cInfo['precisions'])
            
            #[3-3]: Analysis Queue
            if self.__analyzingStream:
                atTS_min = min(dTSs[target][-1] for target in ('kline', 'depth', 'aggTrade'))
                if aggOpenTS == atTS_min and (not aQueue or aQueue[-1] != atTS_min):
                    aQueue.append(atTS_min)

            #[3-4]: Draw Queue
            if hVR0 <= aggCloseTS and aggOpenTS <= hVR1:
                self._addDrawQueue(targetCodes = _DRAWQUEUEADDTARGETCODES[target], timestamp = aggOpenTS)

            #[3-5]: Tracker Update
            if not aggedRanges or rawOpenTS < aggedRanges[0]['beg']:
                aggedRange = {'beg':        rawOpenTS,
                              'end':        func_gnitt(intervalID = KLINTERVAL, timestamp = rawOpenTS, nTicks = 1)-1,
                              'end_closed': dl_raw[dIdx_closed]}
                aggedRanges.appendleft(aggedRange)
            else:
                aggedRange0 = aggedRanges[0]
                aggedRange0['end']        = func_gnitt(intervalID = KLINTERVAL, timestamp = rawOpenTS, nTicks = 1)-1
                aggedRange0['end_closed'] = dl_raw[dIdx_closed]
            if 2 <= len(aggedRanges) and aggedRanges[0]['end']+1 == aggedRanges[1]['beg']:
                aggedRanges[1]['beg'] = aggedRanges[0]['beg']
                aggedRanges.popleft()
            
            #[3-6]: Target Update & Aggregated Range Skip Jump
            aggedRange0 = aggedRanges[0]
            rawOpenTS   = func_gnitt(intervalID = KLINTERVAL, timestamp = rawOpenTS, nTicks = 1)
            if aggedRange0['beg'] <= rawOpenTS <= aggedRange0['end']:
                if aggedRange0['end_closed']: rawOpenTS = func_gnitt(intervalID = KLINTERVAL, timestamp = aggedRange0['end'], nTicks = 1)
                else:                         rawOpenTS = aggedRange0['end']+1

            #[3-7]: Limit Check
            count += 1
            if count == _AGGREGATIONCHUNKSIZE: 
                if rawOpenTS in dRaw_target:
                    aggComplete = False
                break

        #[4]: Return Aggregation Completion
        return aggComplete

    def __onAggregationComplete(self):
        #[1]: Sort Timestamps
        dTSs_iID = self._data_timestamps[self.intervalID]
        for target in ('kline', 'depth', 'aggTrade'):
            dTSs_iID[target].sort()

        #[2]: First Aggregation Check
        if self.__firstAggregation:
            self._onHViewRangeUpdate(updateType = 1, onNewTarget = True)
            self._editVVR_toExtremaCenter('KLINESPRICE')
            for sivCode in self.displayBox_graphics_visibleSIViewers: 
                self._editVVR_toExtremaCenter(sivCode)
            self.__firstAggregation = False

        #[3]: Analysis Aggregation Check
        if self.__analysisAggregation:
            if self.__dispatchNeuralNetworksConnectionsData():
                self.__mode                = _TYPEMODE_WAITINGNEURALNETWORKSCONNECTIONSDATA
                self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:LOADINGNEURALNETWORKCONNECTIONSDATA'), gaugeValue = None)
                return
            else:
                self.__startAnalysis()
            self.__analysisAggregation = False

        #[4]: Analysis Availability Check
        self.__checkIfCanStartAnalysis()

        #[5]: Mode & Loading Cover Update
        self.__mode = _TYPEMODE_READY
        self._setLoadingCover(show = False, text = "-", gaugeValue = None)

    def _onAnalysisRangeUpdate(self):
        self.__checkIfCanStartAnalysis()

    def _onAnalysisConfigurationUpdate(self):
        self.__checkIfCanStartAnalysis()

    def __checkIfCanStartAnalysis(self):
        #[1]: Instances
        ssps        = self.settingsSubPages
        oc          = self.objectConfig
        foTSs       = self.__firstOpenTSs
        aggedRanges = self.__aggregatedRanges[self.intervalID]

        #[2]: Target Check
        result = self.currencySymbol is not None

        #[3]: Analysis Range Check
        if result:
            aRange_beg = oc['AnalysisRangeBeg']
            aRange_end = oc['AnalysisRangeEnd']
            if ((aRange_beg is None) or
                (aRange_end is not None and not aRange_beg <= aRange_end)): 
                result = False
            elif any (foTSs[target] is None or not aggedRanges[target] 
                      for target in ('kline', 'depth', 'aggTrade')):
                result = False
            else:
                foTS_min = min(foTSs[target]                  for target in ('kline', 'depth', 'aggTrade'))
                laTS_min = min(aggedRanges[target][-1]['end'] for target in ('kline', 'depth', 'aggTrade'))
                if aRange_beg < foTS_min:
                    result = False
                if aRange_end is not None and laTS_min < aRange_end:
                    result = False

        #[4]: Analysis Configurations Check
        if result:
            analysisParams, invalidLines = analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(oc)
            if not analysisParams or invalidLines:
                result = False

        #[5]: Result Interpretation
        saButton = ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"]
        if result: saButton.activate()
        else:      saButton.deactivate()

    def _onStartAnalysis(self):
        #[1]: Instances
        ssps = self.settingsSubPages
        oc   = self.objectConfig

        #[2]: Start Analysis Button Deactivation
        ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()

        #[3]: Neural Networks Data Clearing
        self.__initializeAnalysisControl()

        #[4]: Analysis Aggregation Flag Raise
        self.__analysisAggregation = True

        #[5]: Data Availability Check Update
        if self.__updateAvailabilityChecks(analysisBegin = oc['AnalysisRangeBeg']):
            if self.__checkDataAvailable():
                if self.__dispatchDataRequests():
                    self.__mode = _TYPEMODE_FETCHINGMARKETDATA
                    self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:FETCHINGMARKETDATA'), gaugeValue = self.__computeFetchCompletion())
                    return
            else:
                self.__mode = _TYPEMODE_WAITINGDATAAVAILABLE
                self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGDATAAVAILABLE'), gaugeValue = None)
                return
            
        #[6]: Neural Network Connections Data Requests
        if self.__dispatchNeuralNetworksConnectionsData():
            self.__mode = _TYPEMODE_WAITINGNEURALNETWORKSCONNECTIONSDATA
            self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:LOADINGNEURALNETWORKCONNECTIONSDATA'), gaugeValue = None)
        else:
            self.__mode = _TYPEMODE_AGGREGATING
            self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:AGGREGATINGMARKETDATA'), gaugeValue = 0)

    def __dispatchNeuralNetworksConnectionsData(self):
        #[1]: Instances
        nncd_rIDs    = self.__neuralNetworkConnectionDataRequestIDs
        nns          = self.__neuralNetworkInstances
        oc           = self.objectConfig
        func_sendFAR = self.ipcA.sendFAR

        #[2]: Neural Networks Check & Request Dispatch
        if oc['NNA_Master']:
            nns_prd = self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'NEURALNETWORKS')
            for lineIndex in range (_NMAXLINES['NNA']):
                nnLineActive = oc[f'NNA_{lineIndex}_LineActive']
                nnCode       = oc[f'NNA_{lineIndex}_NeuralNetworkCode']
                if not nnLineActive:      continue
                if nnCode is None:        continue
                if nnCode not in nns_prd: continue
                if nnCode in nns:         continue
                nncd_rID = func_sendFAR(targetProcess  = "NEURALNETWORKMANAGER",
                                        functionID     = 'getNeuralNetworkConnections',
                                        functionParams = {'neuralNetworkCode': nnCode},
                                        farrHandler    = self.__onNeuralNetworkConnectionsDataRequestResponse_FARR)
                nns[nnCode]         = None
                nncd_rIDs[nncd_rID] = nnCode

        return (0 < len(nns))
    
    def __onNeuralNetworkConnectionsDataRequestResponse_FARR(self, responder, requestID, functionResult):
        #[1]: Instances
        ssps      = self.settingsSubPages
        nns       = self.__neuralNetworkInstances
        nncd_rIDs = self.__neuralNetworkConnectionDataRequestIDs

        #[2]: Source Check
        if responder != 'NEURALNETWORKMANAGER': return
        if requestID not in nncd_rIDs:          return

        #[3]: RID Removal
        nnCode = nncd_rIDs.pop(requestID)

        #[4]: Result Handling
        if functionResult is not None:
            nKlines      = functionResult['nKlines']
            hiddenLayers = functionResult['hiddenLayers']
            outputLayer  = functionResult['outputLayer']
            connections  = functionResult['connections']
            nn = neural_networks.neuralNetwork_MLP(nKlines      = nKlines, 
                                                   hiddenLayers = hiddenLayers, 
                                                   outputLayer  = outputLayer, 
                                                   device       = 'cpu')
            nn.importConnectionsData(connections = connections)
            nn.setEvaluationMode()
            nns[nnCode] = nn

        #[5]: Final Request Handling
        if nncd_rIDs:
            return
        #---[5-1]: All Neural Networks Are Loaded
        if all(nns[nnCode] is not None for nnCode in nns):
            self.__mode = _TYPEMODE_AGGREGATING
            self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:AGGREGATINGMARKETDATA'), gaugeValue = 0)
        #---[5-2]: A Neural Network Load Failed
        else:
            eMsg = f"[GUI-{self.name}] A Failure Returned From NEURALNETWORKMANAGER While Attempting To Load Neural Network Connections Data For The Following Models."
            for nnCode, nn in nns.items(): 
                if nn is not None: continue
                eMsg += f"\n * '{nnCode}'"
            print(termcolor.colored(eMsg, 'light_red'))
            ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()

        #[6]: Loading Cover Update
        self._setLoadingCover(show = False, text = "-", gaugeValue = None)
        self.__mode = _TYPEMODE_READY

    def __startAnalysis(self):
        #[1]: Instances
        iID        = self.intervalID
        cInfo      = self.currencyInfo
        oc         = self.objectConfig
        dAgg       = self._data_agg[iID]
        dTSs       = self._data_timestamps[self.intervalID]
        sit_aCodes = self.siTypes_analysisCodes
        atp_sorted = self.__analysisToProcess_Sorted
        aQueue     = self.__analysisQueue
        
        #[2]: Reset Previous Analysis Data, Drawings, And Queue
        dType_base = {'kline', 'depth', 'aggTrade'}
        for dType in list(dAgg):
            if dType in dType_base: continue
            self._drawer_RemoveDrawings(analysisCode = dType, gRemovalSignal = None)
            del dAgg[dType]
        aQueue.clear()

        #[3]: Construct a new analysis params
        aParams, invalidLines = analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(oc)
        self.analysisParams[self.intervalID] = aParams
        for aCode in aParams: 
            dAgg[aCode] = dict()
        for siType in _SITYPES:
            sit_aCodes[siType] = [aCode for aCode in aParams if aCode[:len(siType)] == siType]
        atp_sorted.clear()
        for aType in _ANALYSIS_GENERATIONORDER: 
            atp_sorted.extend([(aType, aCode) for aCode in aParams if aCode[:len(aType)] == aType])
        self.__analysisKwargs = {'intervalID':     iID,
                                 'precisions':     cInfo['precisions'],
                                 'klines':         dAgg['kline'],
                                 'depths':         dAgg['depth'],
                                 'aggTrades':      dAgg['aggTrade'],
                                 'neuralNetworks': self.__neuralNetworkInstances}

        #[4]: Stream Mode
        self.__analyzingStream = (oc['AnalysisRangeEnd'] is None)

        #[5]: Add Analysis Queue
        atTS_beg = oc['AnalysisRangeBeg']
        atTS_end = min(dTSs[target][-1] for target in ('kline', 'depth', 'aggTrade')) if self.__analyzingStream else oc['AnalysisRangeEnd']
        atTSs = auxiliaries.getTimestampList_byRange(intervalID        = iID,
                                                     timestamp_beg     = atTS_beg, 
                                                     timestamp_end     = atTS_end,
                                                     lastTickInclusive = True)
        aQueue.extend(atTSs)

    def __analyzeData(self):
        #[1]: Instances
        dAgg       = self._data_agg[self.intervalID]
        aParams    = self.analysisParams[self.intervalID]
        atp_sorted = self.__analysisToProcess_Sorted
        aKwargs    = self.__analysisKwargs
        aQueue     = self.__analysisQueue
        func_aGen      = analyzers.analysisGenerator
        func_addDQueue = self._addDrawQueue

        #[2]: Analysis
        aTargetTS = aQueue.popleft()
        for aType, aCode in atp_sorted:
            func_aGen(analysisType    = aType,
                      timestamp       = aTargetTS,
                      analysisResults = dAgg[aCode],
                      **aKwargs,
                      **aParams[aCode])
        func_addDQueue(targetCodes = [aCode for aType, aCode in atp_sorted], 
                       timestamp   = aTargetTS)
        
    def __getLoadChunkBeginPoint(self):
        eTSWidth       = self.expectedKlineTemporalWidth
        loadChunkWidth = eTSWidth * 5000
        loadChunkBeg   = (self.horizontalViewRange[0] // loadChunkWidth - 1) * loadChunkWidth
        chunkBeg       = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = loadChunkBeg, nTicks = 0)
        return chunkBeg

    def _onHViewRangeUpdate(self, updateType, onNewTarget = False):
        #[1]: Parent Class Response
        super()._onHViewRangeUpdate(updateType = updateType)

        #[2]: Target Check
        if self.currencySymbol is None:
            return

        #[3]: Availability Checks
        if not onNewTarget:
            if self.__updateAvailabilityChecks():
                if self.__checkDataAvailable():
                    if self.__dispatchDataRequests():
                        self.__mode = _TYPEMODE_FETCHINGMARKETDATA
                        self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:FETCHINGMARKETDATA'), gaugeValue = self.__computeFetchCompletion())
                else:
                    self.__mode = _TYPEMODE_WAITINGDATAAVAILABLE
                    self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGDATAAVAILABLE'), gaugeValue = None)