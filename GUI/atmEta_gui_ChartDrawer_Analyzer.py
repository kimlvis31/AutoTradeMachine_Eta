#ATM Modules
from .atmEta_gui_ChartDrawer import (chartDrawer,
                                     _NMAXLINES,
                                     _MITYPES,
                                     _SITYPES)
import atmEta_Auxillaries
import atmEta_Analyzers
import atmEta_IPC
import atmEta_NeuralNetworks
import atmEta_Constants

#Python Modules
import time
import termcolor
import torch
import pprint
import gc
from datetime import datetime, timezone, tzinfo
from collections import deque

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = atmEta_IPC._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = atmEta_IPC._FAR_INVALIDFUNCTIONID

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

COMMONDATAINDEXES = {'openTime':  {'kline': KLINDEX_OPENTIME,  'depth': DEPTHINDEX_OPENTIME,  'aggTrade': ATINDEX_OPENTIME},
                     'closeTime': {'kline': KLINDEX_CLOSETIME, 'depth': DEPTHINDEX_CLOSETIME, 'aggTrade': ATINDEX_CLOSETIME},
                     'closed':    {'kline': KLINDEX_CLOSED,    'depth': DEPTHINDEX_CLOSED,    'aggTrade': ATINDEX_CLOSED},
                     'source':    {'kline': KLINDEX_SOURCE,    'depth': DEPTHINDEX_SOURCE,    'aggTrade': ATINDEX_SOURCE}}

KLINTERVAL   = atmEta_Constants.KLINTERVAL
KLINTERVAL_S = atmEta_Constants.KLINTERVAL_S

_TYPEMODE_PENDING               = 0
_TYPEMODE_WAITINGSTREAM         = 1
_TYPEMODE_WAITINGFIRSTOPENTS    = 2
_TYPEMODE_WAITINGDATAAVAILABLE  = 3
_TYPEMODE_FETCHINGMARKETDATA    = 4
_TYPEMODE_AGGREGATING           = 5
_TYPEMODE_READY                 = 6

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

_ANALYSIS_GENERATIONORDER = atmEta_Analyzers.ANALYSIS_GENERATIONORDER

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
        self.__stream = {target: {'firstStreamOpenTS': None,
                                  'lastStream':        None}
                         for target in ('kline', 'depth', 'aggTrade')}
        self.__availabilityChecks = {target: [] for target in ('kline', 'depth', 'aggTrade')}
        self.__fetchRequests      = dict()
        self.__aggregators            = {'kline':    atmEta_Analyzers.aggregator_kline,
                                         'depth':    atmEta_Analyzers.aggregator_depth,
                                         'aggTrade': atmEta_Analyzers.aggregator_aggTrade}
        self.__lastAggregated         = {self.intervalID: {target: None   for target in ('kline', 'depth', 'aggTrade')}}
        self.__lastClosedAggregations = {self.intervalID: {target: dict() for target in ('kline', 'depth', 'aggTrade')}}
        self.__firstAggregation       = True

    def __initializeAnalysisControl(self):
        self.__neuralNetworkInstances                = dict()
        self.__neuralNetworkConnectionDataRequestIDs = dict()
        self.__analyzingStream          = False
        self.__analysisToProcess_Sorted = list()
        self.__analysisKwargs           = dict()
        self.__analysisQueue            = deque()
        self.__lastNumberOfAnalysisQueueDisplayUpdated_ns = 0
        torch.cuda.empty_cache()

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
        self._clearDrawers()

        #[5]: Initialize Highlighters and Descriptors
        if self.currencySymbol is not None:
            self._clearHighlightsAndDescriptors()

        #[6]: View Control
        self._setHVRParams()
        if self.currencySymbol is None: 
            self.__onDataFetchComplete()
        else:
            self._initializeRCLCGs('KLINESPRICE')
            for sivCode in self.displayBox_graphics_visibleSIViewers: self._initializeSIViewer(sivCode)

        #[7]: Stream Subscription Registration
        if self.currencySymbol is not None: 
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
            aggCompletes = [self.__aggregateData(target = target, onStream = False) for target in ('kline', 'depth', 'aggTrade')]

            #[1-2]: Post-Aggregation Handling
            if all(aggCompletes):
                self.__onAggregationComplete()
                return False
            else:
                currentIntervalCloseTS = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = time.time(), nTicks = 0)-1
                lastAggs               = self.__lastAggregated[self.intervalID]
                tWidthSum = 0
                pWidthSum = 0
                for target in ('kline', 'depth', 'aggTrade'):
                    firstOpenTS = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol, f'{target}_firstOpenTS'))
                    tWidthSum += (currentIntervalCloseTS-firstOpenTS+1)
                    pWidthSum += (lastAggs[target][0]   -firstOpenTS+1)
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
                self.__mode = _TYPEMODE_WAITINGFIRSTOPENTS
                self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:WAITINGDATAAVAILABLE'), gaugeValue = None)

        #[3]: Waiting First Open TS
        if self.__mode == _TYPEMODE_WAITINGFIRSTOPENTS:
            firstOpenTSs = dict()
            for t in ('kline', 'depth', 'aggTrade'):
                firstOpenTS = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol, f'{t}_firstOpenTS'))
                if firstOpenTS == _IPC_PRD_INVALIDADDRESS: firstOpenTS = None
                firstOpenTSs[t] = firstOpenTS
            if all(fot is not None for fot in firstOpenTSs.values()):
                for t, fot in firstOpenTSs.items():
                    self.__availabilityChecks[t].append((fot, sControl[t]['firstStreamOpenTS']-1))
                self.__mode = _TYPEMODE_WAITINGDATAAVAILABLE

        #[4]: Stream Continuity Check
        discontinuity = _STREAMCONTINUITY_NORMAL
        if sControl_dt['lastStream'] is not None:
            ls_openTS, ls_closed = sControl_dt['lastStream']
            nextOpenTS = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = ls_openTS, nTicks = 1)
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

        #[5]: If Waiting Data Available (If All Targets Are Available, Dispatch Fetch Requests)
        if self.__mode == _TYPEMODE_WAITINGDATAAVAILABLE:
            if self.__checkDataAvailable():
                for t in ('kline', 'depth', 'aggTrade'):
                    for aCheck_beg, aCheck_end in self.__availabilityChecks[t]:
                        chunkBeg = aCheck_beg
                        while chunkBeg <= aCheck_end:
                            chunkEnd_max = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = chunkBeg, nTicks = _DATAFETCHCHUNKSIZE)-1
                            chunkEnd_eff = min(chunkEnd_max, aCheck_end)
                            rID = self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER',
                                                    functionID     = 'fetchMarketData',
                                                    functionParams = {'symbol':     self.currencySymbol,
                                                                      'target':     t,
                                                                      'fetchRange': (chunkBeg, chunkEnd_eff)},
                                                    farrHandler    = self.__onFetchRequestResponse_FARR)
                            self.__fetchRequests[rID] = {'target':            t,
                                                         'fetchRequestRange': (chunkBeg, chunkEnd_eff),
                                                         'fetchedRange':      None,
                                                         'complete':          False}
                            chunkBeg = chunkEnd_eff+1
                    self.__availabilityChecks[t].clear()
                self.__mode = _TYPEMODE_FETCHINGMARKETDATA
                self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:FETCHINGMARKETDATA'), gaugeValue = self.__computeFetchCompletion())
                        
        #[6]: Data Record
        if discontinuity != _STREAMCONTINUITY_REVERSE:
            #[6-1]: Last Stream Record
            sControl_dt['lastStream'] = (stream_openTime, stream_closed)
            #[6-2]: Raw Data Record
            self._data_raw[target][stream_openTime] = stream
            #[6-3]: Aggregation Queue
            if self.__mode == _TYPEMODE_READY and discontinuity == _STREAMCONTINUITY_NORMAL:
                self.__aggregateData(target = target, onStream = True)

    def __checkDataAvailable(self):
        #[1]: Currency Data
        cInfo = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol))
        if cInfo == _IPC_PRD_INVALIDADDRESS or not cInfo: return

        #[2]: Availability Check
        for target in ('kline', 'depth', 'aggTrade'):
            firstOpenTS = cInfo[f'{target}_firstOpenTS']
            aRanges     = cInfo[f'{target}s_availableRanges']
            if not firstOpenTS or not aRanges:
                return False
            for aCheck_beg, aCheck_end in self.__availabilityChecks[target]:
                if not any(((aRange[0] <= aCheck_beg) and (aCheck_end <= aRange[1])) for aRange in aRanges):
                    return False
                
        #[3]: If Reached Here, All Are Available. Return True.
        return True
    
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

        #[5]: Completion Check & Fetch Continuation
        fReq['complete']     = True
        fReq['fetchedRange'] = [fr_fetchRange[0], fr_fetchRange[1]]

        #[6]: Status Control
        self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:FETCHINGMARKETDATA'), gaugeValue = self.__computeFetchCompletion())
        if all(_fReq['complete'] for _fReq in self.__fetchRequests.values()): 
            self.__onDataFetchComplete()

    def __onDataFetchComplete(self):
        #[1]: Clear Fetch Requests
        self.__fetchRequests.clear()

        #[2]: Loading Cover
        self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:AGGREGATINGMARKETDATA'), gaugeValue = 0)

        #[3]: Mode Update
        self.__mode = _TYPEMODE_AGGREGATING

    def _onAggregationIntervalUpdate(self, previousIntervalID):
        #[1]: Analysis Control
        dType_base = {'kline', 'depth', 'aggTrade'}
        for dType in list(self._data_agg[previousIntervalID]):
            if dType in dType_base: continue
            self._drawer_RemoveDrawings(analysisCode = dType, gRemovalSignal = None)
            del self._data_agg[previousIntervalID][dType]
        self.__initializeAnalysisControl()

        #[2]: Loading Cover Open
        self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:AGGREGATINGMARKETDATA'), gaugeValue = 0)

        #[3]: Aggregation
        if self.intervalID not in self._data_agg:
            self._data_agg[self.intervalID]                = {target: dict() for target in ('kline', 'depth', 'aggTrade')}
            self._data_timestamps[self.intervalID]         = {target: list() for target in ('kline', 'depth', 'aggTrade')}
            self.__lastAggregated[self.intervalID]         = {target: None   for target in ('kline', 'depth', 'aggTrade')}
            self.__lastClosedAggregations[self.intervalID] = {target: dict() for target in ('kline', 'depth', 'aggTrade')}
        self.__mode = _TYPEMODE_AGGREGATING

        #[4]: Loading Cover
        self._setLoadingCover(show = False, text = "-", gaugeValue = None)

    def __aggregateData(self, target, onStream):
        #[1]: Instances
        cInfo         = self.currencyInfo
        dRaw_target   = self._data_raw[target]
        dAgg_target   = self._data_agg[self.intervalID][target]
        dTSs          = self._data_timestamps[self.intervalID]
        dTSs_target   = dTSs[target]
        lcAggs_target = self.__lastClosedAggregations[self.intervalID][target]
        aggregator    = self.__aggregators[target]
        aQueue        = self.__analysisQueue
        func_gnitt    = atmEta_Auxillaries.getNextIntervalTickTimestamp

        #[1]: Aggregation Begin Timestamp
        la = self.__lastAggregated[self.intervalID][target]
        if la is None:
            aggBeg = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol, f'{target}_firstOpenTS'))
        else:
            la_openTS, la_closed = la
            if la_closed: aggBeg = func_gnitt(intervalID = KLINTERVAL, timestamp = la_openTS, nTicks = 1)
            else:         aggBeg = la_openTS

        #[2]: Aggregation
        dIdx_closed = COMMONDATAINDEXES['closed'][target]
        rawOpenTS   = aggBeg
        aggComplete = True
        count       = 0
        while rawOpenTS in dRaw_target:
            #[2-1]: Instances
            dl_raw    = dRaw_target[rawOpenTS]
            aggOpenTS = func_gnitt(intervalID = self.intervalID, timestamp = rawOpenTS, nTicks = 0)

            #[2-2]: Aggregation
            if aggOpenTS not in dAgg_target: dTSs_target.append(aggOpenTS)
            aggregator(dataRaw        = dRaw_target,
                       dataAgg        = dAgg_target,
                       lastClosedAggs = lcAggs_target,
                       rawOpenTS      = rawOpenTS,
                       aggOpenTS      = aggOpenTS,
                       aggIntervalID  = self.intervalID,
                       precisions     = cInfo['precisions'])
            
            #[2-3]: Analysis Queue
            if self.__analyzingStream:
                atTS_min = min(dTSs[target][-1] for target in ('kline', 'depth', 'aggTrade'))
                if aggOpenTS == atTS_min and (not aQueue or aQueue[-1] != atTS_min):
                    aQueue.append(atTS_min)

            #[2-4]: Draw Queue
            if onStream:
                self._addDrawQueue(targetCodes = _DRAWQUEUEADDTARGETCODES[target], timestamp = aggOpenTS)

            #[2-5]: Tracker
            la        = (rawOpenTS, dl_raw[dIdx_closed])
            rawOpenTS = func_gnitt(intervalID = KLINTERVAL, timestamp = rawOpenTS, nTicks = 1)

            #[2-6]: Limit Check
            count += 1
            if count == _AGGREGATIONCHUNKSIZE: 
                if rawOpenTS in dRaw_target:
                    aggComplete = False
                break
        self.__lastAggregated[self.intervalID][target] = la

        #[3]: Return Aggregation Completion
        return aggComplete

    def __onAggregationComplete(self):
        #[1]: Reset View Flag
        resetView = self.__firstAggregation
        self.__firstAggregation = False

        #[2]: Loading Cover
        self._setLoadingCover(show = False, text = "-", gaugeValue = None)

        #[3]: Horizontal ViewRange Reset
        if resetView:
            self.horizontalViewRange_magnification = 80
            hvr_new_end = round(time.time()+self.expectedKlineTemporalWidth*5)
            hvr_new_beg = round(hvr_new_end-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
            hvr_new = [hvr_new_beg, hvr_new_end]
            tz_rev  = -self.timezoneDelta
            if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]
            self.horizontalViewRange = hvr_new
        self._onHViewRangeUpdate(1)
        self._editVVR_toExtremaCenter('KLINESPRICE')
        for siViewerCode in self.displayBox_graphics_visibleSIViewers: self._editVVR_toExtremaCenter(siViewerCode)

        #[4]: Analysis Availability Check
        self.__checkIfCanStartAnalysis()

        #[5]: Mode Update
        self.__mode = _TYPEMODE_READY
    
    def _onAnalysisRangeUpdate(self):
        self.__checkIfCanStartAnalysis()

    def _onAnalysisConfigurationUpdate(self):
        self.__checkIfCanStartAnalysis()

    def __checkIfCanStartAnalysis(self):
        #[1]: Instances
        ssps = self.settingsSubPages
        oc   = self.objectConfig
        dTSs = self._data_timestamps[self.intervalID]

        #[2]: Target Check
        result = self.currencySymbol is not None

        #[3]: Analysis Range Check
        if result:
            aRange_beg = oc['AnalysisRangeBeg']
            aRange_end = oc['AnalysisRangeEnd']
            if ((aRange_beg is None) or
                (aRange_end is not None and not aRange_beg <= aRange_end)): 
                result = False
            else:
                faTSs, laTSs = [], []
                for target in ('kline', 'depth', 'aggTrade'):
                    dTSs_target = dTSs[target]
                    if dTSs_target:
                        faTSs.append(dTSs_target[0])
                        laTSs.append(dTSs_target[-1])
                    else:
                        faTSs.append(None)
                        laTSs.append(None)
                if any(faTS is None for faTS in faTSs):
                    result = False
                else:
                    faTS_min = min(faTSs)
                    laTS_min = min(laTSs)
                    if ((aRange_beg < faTS_min) or 
                        (aRange_end is not None and laTS_min < aRange_end)):
                        result = False

        #[4]: Analysis Configurations Check
        if result:
            analysisParams, invalidLines = atmEta_Analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(oc)
            if not analysisParams or invalidLines:
                result = False

        #[5]: Result Interpretation
        saButton = ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"]
        if result: saButton.activate()
        else:      saButton.deactivate()

    def _onStartAnalysis(self):
        #[1]: Instances
        ssps         = self.settingsSubPages
        oc           = self.objectConfig
        nncd_rIDs    = self.__neuralNetworkConnectionDataRequestIDs
        nns          = self.__neuralNetworkInstances
        func_sendFAR = self.ipcA.sendFAR

        #[2]: Start Analysis Button Deactivation
        ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()

        #[3]: Neural Networks Data Clearing
        nns.clear()
        nncd_rIDs.clear()
        gc.collect()
        torch.cuda.empty_cache()

        #[4]: Neural Networks Connections Data Request
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

        #[5]: Analysis Start
        if not nns:
            self.__startAnalysis()
    
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
            nn = atmEta_NeuralNetworks.neuralNetwork_MLP(nKlines      = nKlines, 
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
            self.__startAnalysis()
            return
        #---[5-2]: A Neural Network Load Failed
        eMsg = f"[GUI-{self.name}] A Failure Returned From NEURALNETWORKMANAGER While Attempting To Load Neural Network Connections Data For The Following Models."
        for nnCode, nn in nns.items(): 
            if nn is not None: continue
            eMsg += f"\n * '{nnCode}'"
        print(termcolor.colored(eMsg, 'light_red'))
        ssps['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].activate()

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
        analysisParams, invalidLines = atmEta_Analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(oc)
        self.analysisParams = analysisParams
        aParams = self.analysisParams
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
        atTSs = atmEta_Auxillaries.getTimestampList_byRange(intervalID        = iID,
                                                            timestamp_beg     = atTS_beg, 
                                                            timestamp_end     = atTS_end,
                                                            lastTickInclusive = True)
        aQueue.extend(atTSs)

        #[6]: Analysis Start Button
        self.settingsSubPages['MAIN'].GUIOs["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()

    def __analyzeData(self):
        #[1]: Instances
        dAgg       = self._data_agg[self.intervalID]
        aParams    = self.analysisParams
        atp_sorted = self.__analysisToProcess_Sorted
        aKwargs    = self.__analysisKwargs
        aQueue     = self.__analysisQueue
        func_aGen      = atmEta_Analyzers.analysisGenerator
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