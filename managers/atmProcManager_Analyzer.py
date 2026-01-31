#ATM Modules
from atmEta_Analyzers import KLINDEX_OPENTIME, KLINDEX_OPENPRICE, KLINDEX_CLOSEPRICE, KLINDEX_HIGHPRICE, KLINDEX_LOWPRICE
import atmEta_IPC
import atmEta_Analyzers
import atmEta_Auxillaries
import atmEta_NeuralNetworks
import atmEta_Constants

#Python Modules
import time
import termcolor
import gc
import pprint
import torch
import random
import math

#Constants
_IPC_THREADTYPE_MT         = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT         = atmEta_IPC._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = atmEta_IPC._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = atmEta_IPC._FAR_INVALIDFUNCTIONID

KLINDEX_CLOSED = 11

_CURRENCYANALYSIS_STATUS_WAITINGNEURALNETWORKCONNECTIONSDATA = 0
_CURRENCYANALYSIS_STATUS_WAITINGSTREAM                       = 1
_CURRENCYANALYSIS_STATUS_WAITINGDATAAVAILABLE                = 2
_CURRENCYANALYSIS_STATUS_PREPARING_QUEUED                    = 3
_CURRENCYANALYSIS_STATUS_PREPARING_ANALYZINGKLINES           = 4
_CURRENCYANALYSIS_STATUS_ANALYZINGREALTIME                   = 5
_CURRENCYANALYSIS_STATUS_ERROR                               = 6

_CURRENCYANALYSIS_MAXFETCHLENGTH                   = 4320
_CURRENCYANALYSIS_MINANALYSISINTERVAL_NS           = 1e9
_CURRENCYANALYSIS_DATAAVAILABILITYCHECKINTERVAL_NS = 1e9

_ANALYSISGENERATIONTIMETRACKER_LIFETIME_NS = 5e9


KLINTERVAL   = atmEta_Constants.KLINTERVAL
KLINTERVAL_S = atmEta_Constants.KLINTERVAL_S

AGGTRADESAMPLINGINTERVAL_S    = atmEta_Analyzers.AGGTRADESAMPLINGINTERVAL_S
BIDSANDASKSSAMPLINGINTERVAL_S = atmEta_Analyzers.BIDSANDASKSSAMPLINGINTERVAL_S
NMAXAGGTRADESSAMPLES          = atmEta_Analyzers.NMAXAGGTRADESSAMPLES
NMAXBIDSANDASKSSAMPLES        = atmEta_Analyzers.NMAXBIDSANDASKSSAMPLES
class procManager_Analyzer:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA, analyzerIndex):
        #IPC Assistance
        self.ipcA = ipcA

        #Analyzer ID
        self.analyzerIndex = analyzerIndex

        #Project Path
        self.path_project = path_project

        #Currency Analysis
        self.__currencyAnalysis = dict()
        self.__currencyAnalysisPrep_currentlyPreparing = None
        self.__currencyAnalysisPrep_preparationQueue   = list()
        self.__currencyAnalysisPrep_klineFetchRequests = dict()

        #Neural Networks
        self.__neuralNetworks                                = dict()
        self.__neuralNetworks_Referrers                      = dict()
        self.__neuralNetworks_ConnectionDataRequests_RIDs    = dict()
        self.__neuralNetworks_ConnectionDataRequests_NNCodes = dict()

        #Analyzer Status Trackers
        self.__analyzerSummary = {'averageAnalysisGenerationTime_ns':   None,
                                  'currentlyPreparingCurrencyAnalysis': self.__currencyAnalysisPrep_currentlyPreparing}
        self.__analysisGenerationTimes_ns = list()
        self.__analysisGenerationTimes_Updated = False #onAnalyzerSummaryUpdate

        #Subscription Request Control
        self.__klineInfoSubscribedSymbols   = dict()
        self.__klineStreamSubscribedSymbols = dict()

        #FAR Registration
        #---TRADEMANAGER
        self.ipcA.addFARHandler('addCurrencyAnalysis',     self.__far_addCurrencyAnalysis,     executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        self.ipcA.addFARHandler('removeCurrencyAnalysis',  self.__far_removeCurrencyAnalysis,  executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        self.ipcA.addFARHandler('restartCurrencyAnalysis', self.__far_restartCurrencyAnalysis, executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        #---BINANCEAPI
        self.ipcA.addFARHandler('onKlineStreamReceival',    self.__far_onKlineStreamReceival,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onOrderbookUpdate',        self.__far_onOrderbookUpdate,        executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onAggTradeStreamReceival', self.__far_onAggTradeStreamReceival, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---DATAMANAGER
        self.ipcA.addFARHandler('onCurrenciesUpdate', self.__far_onCurrenciesUpdate, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---GUI
        self.ipcA.addFARHandler('registerCurrencyAnalysisDataSubscription',   self.__far_registerCurrencyAnalysisDataSubscription,   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('unregisterCurrencyAnalysisDataSubscription', self.__far_unregisterCurrencyAnalysisDataSubscription, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

        #IPCA PRD Formatting
        self.ipcA.formatPRD('DATAMANAGER', 'CURRENCIES', dict())

        #Process Control
        self.__processLoopContinue = True
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Process Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        self.__currencies = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = 'CURRENCIES')
        self.ipcA.sendPRDEDIT(targetProcess = 'TRADEMANAGER', prdAddress = 'ANALYZERSUMMARY', prdContent = self.__analyzerSummary)
        while self.__processLoopContinue:
            #Process any existing FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()
            #Process Currency Analysis
            self.__ca_process()
            #Analysis Generation Time Tracker
            self.__analysisGenerationTimeTracker_process()
            #Process Loop Control
            self.__loopSleeper()

    def __loopSleeper(self):
        for ca in self.__currencyAnalysis.values():
            if 0 < len(ca['kline_analysisTargets']): return
        time.sleep(0.001)

    def terminate(self, requester):
        self.__processLoopContinue = False
    #Manager Process Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Internal Functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __ca_process(self):
        #Currency Analysis Processing
        for caCode in self.__currencyAnalysis:
            ca        = self.__currencyAnalysis[caCode]
            ca_status = ca['status']
            ca_klines = ca['klines']
            #[1]: Analyzing Real-Time or Analyzing For Prep
            if ((ca_status == _CURRENCYANALYSIS_STATUS_ANALYZINGREALTIME) or (ca_status == _CURRENCYANALYSIS_STATUS_PREPARING_ANALYZINGKLINES)):
                #[1-1]: Analysis Generation
                targetTSs_sorted = sorted(list(ca['kline_analysisTargets']))
                for ts in targetTSs_sorted:
                    self.__ca_performAnalysisOnKline(currencyAnalysisCode = caCode, klineOpenTS = ts)
                    if (ca_status == _CURRENCYANALYSIS_STATUS_ANALYZINGREALTIME): self.__analysisGenerationTimeTracker_append(time.perf_counter_ns()-ca['kline_lastStreamedProcTime'])
                ca['kline_analysisTargets'].clear()
                        
                #[1-2]: In Case Of Preparing, Send Next Fetch Request Or Start Real-Time Analysis
                if (ca_status == _CURRENCYANALYSIS_STATUS_PREPARING_ANALYZINGKLINES):
                    if (ca['kline_preparing_waitingFetch']): continue
                    if (ca['kline_preparing_targetFetchRange'] is None): self.__ca_startRealTimeAnalysis(currencyAnalysisCode = caCode)
                    else:                                                self.__ca_sendKlinesFetchRequest(currencyAnalysisCode = caCode)
            
            #[2]: Waiting Data Available
            elif (ca_status == _CURRENCYANALYSIS_STATUS_WAITINGDATAAVAILABLE):
                #[2-1]: Check Data Availability
                if (time.perf_counter_ns()-ca['kline_lastDataAvailableCheck_ns'] < _CURRENCYANALYSIS_DATAAVAILABILITYCHECKINTERVAL_NS):
                    continue
                data_available = self.__ca_isCurrencyDataAvailable(currencyAnalysisCode = caCode)

                #[2-2]: Add to prep queue if data is available
                if not(data_available):
                    continue
                self.__ca_addToPreparationQueue(currencyAnalysisCode = caCode)

    def __ca_performAnalysisOnKline(self, currencyAnalysisCode, klineOpenTS):
        _ca = self.__currencyAnalysis[currencyAnalysisCode]
        if (_ca['kline_firstAnalyzedOpenTS'] is None): _ca['kline_firstAnalyzedOpenTS'] = klineOpenTS
        #Perform analysis
        nKlinesToKeep_max = 0
        expiredAnalysisOpenTS_nToDisplay = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = klineOpenTS, nTicks = -_ca['nKlines_toDisplay'])
        for analysisPair in _ca['analysisToProcess_sorted']:
            analysisType = analysisPair[0]; analysisCode = analysisPair[1]
            #---Analysis Generation
            nAnalysisToKeep, nKlinesToKeep = atmEta_Analyzers.analysisGenerator(analysisType   = analysisType,
                                                                                klineAccess    = _ca['klines'],
                                                                                intervalID     = KLINTERVAL,
                                                                                mrktRegTS      = _ca['marketRegistrationTS'],
                                                                                precisions     = _ca['precisions'],
                                                                                timestamp      = klineOpenTS,
                                                                                neuralNetworks = self.__neuralNetworks,
                                                                                bidsAndAsks    = _ca['bidsAndAsks'],
                                                                                aggTrades      = _ca['aggTrades'],
                                                                                **_ca['analysisParams'][analysisCode])
            #---Analysis Result Dispatch to TRADEMANAGER
            kline = _ca['klines']['raw'][klineOpenTS]
            if kline[11]:
                aLinearized = atmEta_Analyzers.linearizeAnalysis(klineAccess   = _ca['klines'], 
                                                                 analysisPairs = _ca['analysisToProcess_sorted'], 
                                                                 timestamp     = klineOpenTS)
                self.ipcA.sendFAR(targetProcess  = 'TRADEMANAGER', 
                                  functionID     = 'onAnalysisGeneration', 
                                  functionParams = {'currencyAnalysisCode': currencyAnalysisCode,
                                                    'kline':                kline,
                                                    'linearizedAnalysis':   aLinearized}, 
                                  farrHandler    = None)
            #---Update Optimization Variables
            nKlinesToKeep_max = max(nKlinesToKeep_max, nKlinesToKeep, _ca['neuralNetworkMaxKlinesRefLen'])
            #---Memory Optimization (Analysis)
            if (True):
                expiredAnalysisOpenTS_nAnalysisToKeep = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = klineOpenTS, nTicks = -(nAnalysisToKeep+1))
                if (expiredAnalysisOpenTS_nAnalysisToKeep < expiredAnalysisOpenTS_nToDisplay): expiredKlineOpenTS_effective = expiredAnalysisOpenTS_nAnalysisToKeep
                else:                                                                          expiredKlineOpenTS_effective = expiredAnalysisOpenTS_nToDisplay
                if (_ca['kline_firstAnalyzedOpenTS'] <= expiredKlineOpenTS_effective):
                    if (_ca['klines_lastRemovedOpenTS'][analysisCode] == None): tsRemovalRange_beg = _ca['kline_firstAnalyzedOpenTS']
                    else:                                                       tsRemovalRange_beg = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = _ca['klines_lastRemovedOpenTS'][analysisCode], nTicks = 1)
                    for _ts in atmEta_Auxillaries.getTimestampList_byRange(intervalID = KLINTERVAL, timestamp_beg = tsRemovalRange_beg, timestamp_end = expiredKlineOpenTS_effective, mrktReg = _ca['marketRegistrationTS'], lastTickInclusive = True): del _ca['klines'][analysisCode][_ts]
                    _ca['klines_lastRemovedOpenTS'][analysisCode] = expiredKlineOpenTS_effective
        #---Memory Optimization (Kline Raw, Kline Raw_Status)
        if (True):
            expiredAnalysisOpenTS_nKlinesToKeep = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = klineOpenTS, nTicks = -(nKlinesToKeep_max+1))
            expiredKlineOpenTS_effective = min(expiredAnalysisOpenTS_nKlinesToKeep, expiredAnalysisOpenTS_nToDisplay)
            if (_ca['kline_firstAnalyzedOpenTS'] <= expiredKlineOpenTS_effective):
                if (_ca['klines_lastRemovedOpenTS']['raw'] == None): tsRemovalRange_beg = _ca['kline_firstAnalyzedOpenTS']
                else:                                                tsRemovalRange_beg = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = _ca['klines_lastRemovedOpenTS']['raw'], nTicks = 1)
                for _ts in atmEta_Auxillaries.getTimestampList_byRange(intervalID = KLINTERVAL, timestamp_beg = tsRemovalRange_beg, timestamp_end = expiredKlineOpenTS_effective, mrktReg = _ca['marketRegistrationTS'], lastTickInclusive = True):
                    del _ca['klines']['raw'][_ts]
                    del _ca['klines']['raw_status'][_ts]
                _ca['klines_lastRemovedOpenTS']['raw'] = expiredKlineOpenTS_effective
        #Record the last analyzed kline openTS
        _ca['kline_lastAnalyzedKline']    = (klineOpenTS, _ca['klines']['raw'][klineOpenTS][KLINDEX_CLOSED])
        _ca['kline_lastAnalyzedProcTime'] = time.perf_counter_ns()
        #If there exists any data subscription for this currency analysis, send data
        if ((_ca['status'] == _CURRENCYANALYSIS_STATUS_ANALYZINGREALTIME) and (0 < len(_ca['dataSubscribers']))):
            for caDataReceiver in _ca['dataSubscribers']:
                dispatchedRange = _ca['dataSubscribers'][caDataReceiver]['KLINES']
                analyzedKlines = dict()
                for klineDataType in _ca['klines']: analyzedKlines[klineDataType] = {klineOpenTS: _ca['klines'][klineDataType][klineOpenTS]}
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = caDataReceiver, functionParams = {'currencyAnalysisCode': currencyAnalysisCode, 'dataType': 'KLINES', 'caData': analyzedKlines}, farrHandler = None)
                _ca['dataSubscribers'][caDataReceiver]['KLINES'] = [dispatchedRange[0], atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = klineOpenTS, nTicks = 1)-1]

    def __ca_addCurrencyAnalysisToKlineStreamSubscription(self, currencySymbol, currencyAnalysisCode):
        if (currencySymbol in self.__klineStreamSubscribedSymbols): self.__klineStreamSubscribedSymbols[currencySymbol].add(currencyAnalysisCode)
        else:
            self.__klineStreamSubscribedSymbols[currencySymbol] = set()
            self.__klineStreamSubscribedSymbols[currencySymbol].add(currencyAnalysisCode)
            self.ipcA.sendFAR(targetProcess = 'BINANCEAPI', 
                              functionID = 'registerKlineStreamSubscription', 
                              functionParams = {'subscriptionID': None, 
                                                'currencySymbol': currencySymbol, 
                                                'subscribeBidsAndAsks': True, 
                                                'subscribeAggTrades': True}, 
                              farrHandler = None)

    def __ca_addCurrencyAnalysisToKlineInfoSubscription(self, currencySymbol, currencyAnalysisCode):
        if (currencySymbol in self.__klineInfoSubscribedSymbols): self.__klineInfoSubscribedSymbols[currencySymbol].add(currencyAnalysisCode)
        else:
            self.__klineInfoSubscribedSymbols[currencySymbol] = set()
            self.__klineInfoSubscribedSymbols[currencySymbol].add(currencyAnalysisCode)
            self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'registerCurrecnyInfoSubscription', functionParams = {'symbol': currencySymbol}, farrHandler = None)

    def __ca_onStreamReceival_Kline(self, currencyAnalysisCode, streamConnectionTime, kline, closed):
        """
        kline[0]:  ts_open
        kline[1]:  ts_close
        kline[2]:  p_open
        kline[3]:  p_high
        kline[4]:  p_low
        kline[5]:  p_close
        kline[6]:  nTrades
        kline[7]:  base asset volume
        kline[8]:  quote asset volume
        kline[9]:  base asset volume - taker buy
        kline[10]: quote asset volume - taker buy
        kline[11]: kline local type (== 2, indicating a 'Streamed Kline'. Ignore in this case)
        """ #Expand to see the description of the original kline format
        #Instances
        _ca                = self.__currencyAnalysis[currencyAnalysisCode]
        _klines_raw        = _ca['klines']['raw']
        _klines_raw_status = _ca['klines']['raw_status']
        _kline  = kline[:11]+(closed,)
        _t_open = _kline[0]
        #Stream Connection Check
        if ((_ca['streamConnection'] is None) or (_ca['streamConnection']['connectionTime'] <= streamConnectionTime)):
            if ((_t_open not in _klines_raw) or (_klines_raw[_t_open][11] == False)):
                #[1]: Kline Update
                _klines_raw[_t_open] = _kline
                _klines_raw_status[_t_open] = {'p_max': kline[KLINDEX_HIGHPRICE]}
                _ts_open_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = _t_open, nTicks = -1)
                if (_ts_open_prev in _klines_raw_status) and (_klines_raw_status[_t_open]['p_max'] < _klines_raw_status[_ts_open_prev]['p_max']): _klines_raw_status[_t_open]['p_max'] = _klines_raw_status[_ts_open_prev]['p_max']
                #[2]: Stream Tracker Update
                _ca['kline_lastStreamedProcTime'] = time.perf_counter_ns()
                #[3-1]: If this is a new stream connection
                if ((_ca['streamConnection'] is None) or (streamConnectionTime != _ca['streamConnection']['connectionTime'])):
                    #If this currency analysis was preparing, update preparation target
                    if   (currencyAnalysisCode == self.__currencyAnalysisPrep_currentlyPreparing): self.__ca_startNextPreparation()
                    elif (currencyAnalysisCode in self.__currencyAnalysisPrep_preparationQueue):   self.__currencyAnalysisPrep_preparationQueue.remove(currencyAnalysisCode)
                    #Update the connection control variables
                    _ca['streamConnection'] = {'connectionTime':     streamConnectionTime,
                                               'firstReceivedKline': _kline}
                    _ca['kline_preparing_targetFetchRange'] = None
                    _ca['kline_preparing_waitingFetch']     = False
                    _ca['kline_analysisTargets'].clear()
                    self.__ca_determineTargetFetchRange(currencyAnalysisCode = currencyAnalysisCode)
                    #Update Status & Announce
                    _ca['status'] = _CURRENCYANALYSIS_STATUS_WAITINGDATAAVAILABLE
                    self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'onCurrencyAnalysisStatusUpdate', functionParams = {'currencyAnalysisCode': currencyAnalysisCode, 'newStatus': _ca['status']}, farrHandler = None)
                    #Currency Data Availability Check
                    if   (_ca['kline_preparing_targetFetchRange'] is None):                                        self.__ca_startRealTimeAnalysis(currencyAnalysisCode = currencyAnalysisCode)
                    elif (self.__ca_isCurrencyDataAvailable(currencyAnalysisCode = currencyAnalysisCode) == True): self.__ca_addToPreparationQueue(currencyAnalysisCode = currencyAnalysisCode)
                #[3-2]: If this stream is from the same stream connection
                else:
                    #[3-1-1]: Analyzing Real Time
                    if (_ca['status'] == _CURRENCYANALYSIS_STATUS_ANALYZINGREALTIME):
                        if ((closed == True) or (_CURRENCYANALYSIS_MINANALYSISINTERVAL_NS < time.perf_counter_ns()-_ca['kline_lastAnalyzedProcTime'])): _ca['kline_analysisTargets'].add(_t_open)

    def __ca_onStreamReceival_OrderBook(self, currencyAnalysisCode, streamConnectionTime, bids, asks):
        _ca          = self.__currencyAnalysis[currencyAnalysisCode]
        _cac         = _ca['currencyAnalysisConfiguration']
        _bidsAndAsks = _ca['bidsAndAsks']
        if ((_ca['streamConnection'] is not None) and (streamConnectionTime == _ca['streamConnection']['connectionTime'])):
            #Data Read & Analysis Generation
            _newOldestComputed, _newLatestComputed, _updatedItems = atmEta_Analyzers.updateBidsAndAsks(bidsAndAsks    = _bidsAndAsks,
                                                                                                       newBidsAndAsks = (bids, asks),
                                                                                                       oldestComputed = _ca['bidsAndAsks_WOI_oldestComputedS'],
                                                                                                       latestComputed = _ca['bidsAndAsks_WOI_latestComputedS'],
                                                                                                       analysisLines  = [(f'WOI_{lIdx}', _cac[f'WOI_{lIdx}_NSamples'], _cac[f'WOI_{lIdx}_Sigma']) 
                                                                                                                          for lIdx in range (atmEta_Constants.NLINES_WOI) if _cac[f'WOI_{lIdx}_LineActive']])
            #Variables Update
            _ca['bidsAndAsks_WOI_oldestComputedS'] = _newOldestComputed
            _ca['bidsAndAsks_WOI_latestComputedS'] = _newLatestComputed
            #If there exists any data subscription for this currency analysis, send data
            if ((_ca['status'] == _CURRENCYANALYSIS_STATUS_ANALYZINGREALTIME) and (0 < len(_ca['dataSubscribers']))):
                for caDataReceiver in _ca['dataSubscribers']:
                    _t_intervalOpen      = _ca['bidsAndAsks_WOI_latestComputedS']
                    _baa_depth           = _bidsAndAsks['depth']
                    _dispatchedRange_baa = _ca['dataSubscribers'][caDataReceiver]['BIDSANDASKS']
                    #Data Collection
                    _baa_copy = {'depth': dict()}
                    for _pl in _baa_depth: _baa_copy['depth'][_pl] = _baa_depth[_pl]
                    if   (_dispatchedRange_baa is None):                 _dispatchRange_beg = _ca['bidsAndAsks_WOI_oldestComputedS']
                    elif (_dispatchedRange_baa[1]+1 <= _t_intervalOpen): _dispatchRange_beg = _dispatchedRange_baa[1]+1
                    else:                                                _dispatchRange_beg = _t_intervalOpen
                    if (_dispatchRange_beg <= _t_intervalOpen):
                        for _baaDataType in _bidsAndAsks:
                            if (_baaDataType != 'depth'):
                                _baa_thisDataType      = _bidsAndAsks[_baaDataType]
                                _baa_thisDataType_copy = dict()
                                for _tt in range (_dispatchRange_beg, _t_intervalOpen+1, BIDSANDASKSSAMPLINGINTERVAL_S): _baa_thisDataType_copy[_tt] = _baa_thisDataType[_tt]
                                _baa_copy[_baaDataType] = _baa_thisDataType_copy
                        #Dispatched Range Update
                        if (_dispatchedRange_baa is None): _ca['dataSubscribers'][caDataReceiver]['BIDSANDASKS'] = [_dispatchRange_beg,      _t_intervalOpen+BIDSANDASKSSAMPLINGINTERVAL_S-1]
                        else:                              _ca['dataSubscribers'][caDataReceiver]['BIDSANDASKS'] = [_dispatchedRange_baa[0], _t_intervalOpen+BIDSANDASKSSAMPLINGINTERVAL_S-1]
                        #Data Dispatch
                        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = caDataReceiver, functionParams = {'currencyAnalysisCode': currencyAnalysisCode, 'dataType': 'BIDSANDASKS', 'caData': _baa_copy}, farrHandler = None)

    def __ca_onStreamReceival_AggTrade(self, currencyAnalysisCode, streamConnectionTime, aggTrade):
        _ca        = self.__currencyAnalysis[currencyAnalysisCode]
        _cac       = _ca['currencyAnalysisConfiguration']
        _aggTrades = _ca['aggTrades']
        if ((_ca['streamConnection'] is not None) and (streamConnectionTime == _ca['streamConnection']['connectionTime'])):
            #Data Read & Analysis Generation
            _newOldestComputed, _newLatestComputed, _updatedItems = atmEta_Analyzers.updateAggTrades(aggTrades      = _aggTrades,
                                                                                                     newAggTrade    = aggTrade,
                                                                                                     oldestComputed = _ca['aggTrades_NES_oldestComputedS'],
                                                                                                     latestComputed = _ca['aggTrades_NES_latestComputedS'],
                                                                                                     analysisLines  = [(f'NES_{lIdx}', _cac[f'NES_{lIdx}_NSamples'], _cac[f'NES_{lIdx}_Sigma']) 
                                                                                                                        for lIdx in range (atmEta_Constants.NLINES_NES) if _cac[f'NES_{lIdx}_LineActive']])
            #Variables Update
            _ca['aggTrades_NES_oldestComputedS'] = _newOldestComputed
            _ca['aggTrades_NES_latestComputedS'] = _newLatestComputed
            #If there exists any data subscription for this currency analysis, send data
            if ((_ca['status'] == _CURRENCYANALYSIS_STATUS_ANALYZINGREALTIME) and (0 < len(_ca['dataSubscribers']))):
                if (0 < len(_ca['dataSubscribers'])):
                    for caDataReceiver in _ca['dataSubscribers']:
                        _t_intervalOpen     = _ca['aggTrades_NES_latestComputedS']
                        _dispatchedRange_at = _ca['dataSubscribers'][caDataReceiver]['AGGTRADES']
                        #Data Collection
                        _aggTrades_copy = dict()
                        if   (_dispatchedRange_at is None):                 _dispatchRange_beg = _ca['aggTrades_NES_oldestComputedS']
                        elif (_dispatchedRange_at[1]+1 <= _t_intervalOpen): _dispatchRange_beg = _dispatchedRange_at[1]+1
                        else:                                               _dispatchRange_beg = _t_intervalOpen
                        if (_dispatchRange_beg <= _t_intervalOpen):
                            for _atDataType in _aggTrades:
                                if (_atDataType != 'volumes'):
                                    _at_thisDataType      = _aggTrades[_atDataType]
                                    _at_thisDataType_copy = dict()
                                    for _tt in range (_dispatchRange_beg, _t_intervalOpen+1, AGGTRADESAMPLINGINTERVAL_S): _at_thisDataType_copy[_tt] = _at_thisDataType[_tt]
                                    _aggTrades_copy[_atDataType] = _at_thisDataType_copy
                            #Dispatched Range Update
                            if (_dispatchedRange_at is None): _ca['dataSubscribers'][caDataReceiver]['AGGTRADES'] = [_dispatchRange_beg,     _t_intervalOpen+AGGTRADESAMPLINGINTERVAL_S-1]
                            else:                             _ca['dataSubscribers'][caDataReceiver]['AGGTRADES'] = [_dispatchedRange_at[0], _t_intervalOpen+AGGTRADESAMPLINGINTERVAL_S-1]
                            #Data Dispatch
                            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = caDataReceiver, functionParams = {'currencyAnalysisCode': currencyAnalysisCode, 'dataType': 'AGGTRADES', 'caData': _aggTrades_copy}, farrHandler = None)

    def __ca_determineTargetFetchRange(self, currencyAnalysisCode):
        _ca = self.__currencyAnalysis[currencyAnalysisCode]
        _ca_streamConnection_firstReceivedKline = _ca['streamConnection']['firstReceivedKline']
        #[1]: Fetch Target Begin Point
        #---[1-1]: If there exists no analyzed kline, let the beginning fetch range be that of the necessary for the first analysis
        if (_ca['kline_lastAnalyzedKline'] is None):
            _tfr_beg = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], 
                                                                       timestamp = _ca_streamConnection_firstReceivedKline[KLINDEX_OPENTIME],
                                                                       nTicks    = -((_ca['nKlines_nSamplesMax']-1)+(_ca['nKlines_minCompleteAnalysis']-1)))
        #---[1-2]: If there exists any analyzed klines, let the beginning fetch range be the last analyzed kline or the one after (If was on a closed kline)
        else:
           if (_ca['kline_lastAnalyzedKline'][1] == True): _tfr_beg = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = _ca['kline_lastAnalyzedKline'][0], nTicks = 1)
           else:                                           _tfr_beg = _ca['kline_lastAnalyzedKline'][0]
        #[2]: Fetch Target End Point 
        _tfr_end = _ca_streamConnection_firstReceivedKline[KLINDEX_OPENTIME]-1
        #[3]: Fetch Target Update (If needed)
        if (_tfr_beg < _tfr_end): _ca['kline_preparing_targetFetchRange'] = [_tfr_beg, _tfr_end]
        else:                     _ca['kline_preparing_targetFetchRange'] = None

    def __ca_isCurrencyDataAvailable(self, currencyAnalysisCode):
        _ca = self.__currencyAnalysis[currencyAnalysisCode]
        #Check data availability
        _dataAvailable = False
        _dataRanges    = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', _ca['currencySymbol'], 'kline_availableRanges'))
        if (_dataRanges is not None):
            for _dr in _dataRanges:
                if (_dr[0] <= _ca['kline_preparing_targetFetchRange'][0]) and (_ca['kline_preparing_targetFetchRange'][1] <= _dr[1]): _dataAvailable = True; break
        #Last Check Counter Update
        _ca['kline_lastDataAvailableCheck_ns'] = time.perf_counter_ns()
        #Return Result
        return _dataAvailable

    def __ca_addToPreparationQueue(self, currencyAnalysisCode):
        _ca = self.__currencyAnalysis[currencyAnalysisCode]
        #[1]: Preparation Queue Update
        self.__currencyAnalysisPrep_preparationQueue.append(currencyAnalysisCode)
        #[2]: Status Update
        _ca['status'] = _CURRENCYANALYSIS_STATUS_PREPARING_QUEUED
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'onCurrencyAnalysisStatusUpdate', functionParams = {'currencyAnalysisCode': currencyAnalysisCode, 'newStatus': _ca['status']}, farrHandler = None)
        #[3]: If There Exists No Currently Preparing Currency Analysis, Start Preparation
        if (self.__currencyAnalysisPrep_currentlyPreparing == None): self.__ca_startNextPreparation()

    def __ca_startNextPreparation(self):
        #[1]: Start next currency analysis prepration
        if (0 < len(self.__currencyAnalysisPrep_preparationQueue)): 
            _caCode = self.__currencyAnalysisPrep_preparationQueue.pop(0)
            _ca     = self.__currencyAnalysis[_caCode]
            #Preparation Target Update
            self.__currencyAnalysisPrep_currentlyPreparing = _caCode
            #Currency Analysis Status Update
            _ca['status'] = _CURRENCYANALYSIS_STATUS_PREPARING_ANALYZINGKLINES
            self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'onCurrencyAnalysisStatusUpdate', functionParams = {'currencyAnalysisCode': _caCode, 'newStatus': _CURRENCYANALYSIS_STATUS_PREPARING_ANALYZINGKLINES}, farrHandler = None)
        else: self.__currencyAnalysisPrep_currentlyPreparing = None
        #[2]: Currently preparing currency analysis report
        self.__analyzerSummary['currentlyPreparingCurrencyAnalysis'] = self.__currencyAnalysisPrep_currentlyPreparing
        self.ipcA.sendPRDEDIT(targetProcess = 'TRADEMANAGER', prdAddress = ('ANALYZERSUMMARY', 'currentlyPreparingCurrencyAnalysis'), prdContent = self.__analyzerSummary['currentlyPreparingCurrencyAnalysis'])
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'onAnalyzerSummaryUpdate', functionParams = {'updatedSummary': 'currentlyPreparingCurrencyAnalysis'}, farrHandler = None)

    def __ca_sendKlinesFetchRequest(self, currencyAnalysisCode):
        _ca               = self.__currencyAnalysis[currencyAnalysisCode]
        _targetFetchRange = _ca['kline_preparing_targetFetchRange']
        if (_targetFetchRange is not None):
            #[2-1]: Determine the effective target fetch range
            _targetFetchRange_end_max = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = _targetFetchRange[0], mrktReg = _ca['marketRegistrationTS'], nTicks = _CURRENCYANALYSIS_MAXFETCHLENGTH)-1
            if (_targetFetchRange_end_max < _targetFetchRange[1]): _targetFetchRange_effective = (_targetFetchRange[0], _targetFetchRange_end_max)
            else:                                                  _targetFetchRange_effective = (_targetFetchRange[0], _targetFetchRange[1])
            #[2-2]: Request for kline fetch
            _dispatchID = self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'fetchKlines', functionParams = {'symbol': _ca['currencySymbol'], 'fetchRange': _targetFetchRange_effective}, farrHandler = self.__farr_onKlineFetchResponse)
            if (_dispatchID is not None):
                self.__currencyAnalysisPrep_klineFetchRequests[_dispatchID] = {'currencyAnalysisCode': currencyAnalysisCode, 'streamConnectionTimeOnDispatch': _ca['streamConnection']['connectionTime']}
                _ca['kline_preparing_waitingFetch'] = True

    def __ca_startRealTimeAnalysis(self, currencyAnalysisCode):
        _ca = self.__currencyAnalysis[currencyAnalysisCode]
        #[1]: Update the status
        _ca['status'] = _CURRENCYANALYSIS_STATUS_ANALYZINGREALTIME
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'onCurrencyAnalysisStatusUpdate', functionParams = {'currencyAnalysisCode': currencyAnalysisCode, 'newStatus': _ca['status']}, farrHandler = None)
        #[2]: Update analysis targets
        _at                 = _ca['streamConnection']['firstReceivedKline'][KLINDEX_OPENTIME]
        _ca_klines_raw      = _ca['klines']['raw']
        _ca_analysisTargets = _ca['kline_analysisTargets']
        while (_at in _ca_klines_raw):
            _ca_analysisTargets.add(_at)
            _at = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = _at, nTicks = 1)
        #[2]: If there exist any data subscription for this currency analysis, send data
        if (0 < len(_ca['dataSubscribers'])):
            for caDataReceiver in _ca['dataSubscribers']:
                #Klines
                _analyzedKlines = dict()
                _dispatchedRange_klines = _ca['dataSubscribers'][caDataReceiver]['KLINES']
                #---New
                if (_dispatchedRange_klines is None): 
                    _dispatchRange_klines = [atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = _ca['kline_lastAnalyzedKline'][0], nTicks = -(_ca['nKlines_toDisplay']-1)),
                                             atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = _ca['kline_lastAnalyzedKline'][0], nTicks = 1)-1]
                    for _klDataType in _ca['klines']:
                        _analyzedKlines[_klDataType] = dict()
                        for _ts in atmEta_Auxillaries.getTimestampList_byRange(intervalID = KLINTERVAL, timestamp_beg = _dispatchRange_klines[0], timestamp_end = _dispatchRange_klines[1], mrktReg = _ca['marketRegistrationTS'], lastTickInclusive = True):
                            if (_ts in _ca['klines'][_klDataType]): _analyzedKlines[_klDataType][_ts] = _ca['klines'][_klDataType][_ts]
                    _ca['dataSubscribers'][caDataReceiver]['KLINES'] = [_dispatchRange_klines[0], _dispatchRange_klines[1]]
                #---Continued
                else: 
                    _dispatchRange_klines = [atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = _dispatchedRange_klines[1],        nTicks = -1)+1, 
                                             atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = _ca['kline_lastAnalyzedKline'][0], nTicks =  1)-1]
                    for _klDataType in _ca['klines']:
                        _analyzedKlines[_klDataType] = dict()
                        for _ts in atmEta_Auxillaries.getTimestampList_byRange(intervalID = KLINTERVAL, timestamp_beg = _dispatchRange_klines[0], timestamp_end = _dispatchRange_klines[1], mrktReg = _ca['marketRegistrationTS'], lastTickInclusive = True):
                            _analyzedKlines[_klDataType][_ts] = _ca['klines'][_klDataType][_ts]
                    _ca['dataSubscribers'][caDataReceiver]['KLINES'] = [_dispatchedRange_klines[0], _dispatchRange_klines[1]]
                #---Finally
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = caDataReceiver, functionParams = {'currencyAnalysisCode': currencyAnalysisCode, 'dataType': 'KLINES', 'caData': _analyzedKlines}, farrHandler = None)
        #[3]: Start next currency analysis preparation
        self.__ca_startNextPreparation()

    def __analysisGenerationTimeTracker_process(self):
        #Remove any expired element
        t_current_ns = time.time_ns()
        self.__analysisGenerationTimes_Updated = (self.__analysisGenerationTimes_ns and (_ANALYSISGENERATIONTIMETRACKER_LIFETIME_NS < t_current_ns-self.__analysisGenerationTimes_ns[0][1]))
        while self.__analysisGenerationTimes_ns and (_ANALYSISGENERATIONTIMETRACKER_LIFETIME_NS < t_current_ns-self.__analysisGenerationTimes_ns[0][1]): 
            self.__analysisGenerationTimes_ns.pop(0)
        #If there was any change in the tracker buffer, recompute the average
        if self.__analysisGenerationTimes_Updated:
            nRecs = len(self.__analysisGenerationTimes_ns)
            if not self.__analysisGenerationTimes_ns: self.__analyzerSummary['averageAnalysisGenerationTime_ns'] = None
            else:            self.__analyzerSummary['averageAnalysisGenerationTime_ns'] = round(sum(aGenTR[0] for aGenTR in self.__analysisGenerationTimes_ns)/nRecs)
            self.ipcA.sendPRDEDIT(targetProcess = 'TRADEMANAGER', prdAddress = ('ANALYZERSUMMARY', 'averageAnalysisGenerationTime_ns'), prdContent = self.__analyzerSummary['averageAnalysisGenerationTime_ns'])
            self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'onAnalyzerSummaryUpdate', functionParams = {'updatedSummary': 'averageAnalysisGenerationTime_ns'}, farrHandler = None)
        #Update flag reset
        self.__analysisGenerationTimes_Updated = False

    def __analysisGenerationTimeTracker_append(self, newAnalysisGenerationTime_ns):
        self.__analysisGenerationTimes_ns.append((newAnalysisGenerationTime_ns, time.time_ns()))
        self.__analysisGenerationTimes_Updated = True
    #Manager Internal Functions END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #FAR Handlers -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<TRADEMANAGER>
    def __far_addCurrencyAnalysis(self, requester, currencyAnalysisCode, currencySymbol, currencyAnalysisConfigurationCode, currencyAnalysisConfiguration):
        #[1]: Requester Check
        if requester != 'TRADEMANAGER': return

        #[2]: Construct analysis params from the currency analysis configuration
        cac = currencyAnalysisConfiguration
        analysisParams, invalidLines = atmEta_Analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(cac)
        if invalidLines:
            invalidLines_str = atmEta_Auxillaries.formatInvalidLinesReportToString(invalidLines = invalidLines)
            print(termcolor.colored((f"[ANALYZER{self.analyzerIndex}] Invalid lines detected while attempting to start currency analysis."+invalidLines_str), 'light_red'))

        #[3]: Prepare the analysis codes to process in order
        analysisToProcess_sorted = list()
        for analysisType in atmEta_Analyzers.ANALYSIS_GENERATIONORDER: analysisToProcess_sorted += [(analysisType, analysisCode) for analysisCode in analysisParams if analysisCode[:len(analysisType)] == analysisType]

        #[4]: Find the minimum number of klines to be able to start analysis
        if (True):
            nKlines_nSamplesMax = 0
            #---SMA
            if cac['SMA_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_SMA):
                    lineActive = cac.get(f'SMA_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac[f'SMA_{lineIndex}_NSamples']
                    nKlines_nSamplesMax = max(nKlines_nSamplesMax, nSamples)
            #---WMA
            if cac['WMA_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_WMA):
                    lineActive = cac.get(f'WMA_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac[f'WMA_{lineIndex}_NSamples']
                    nKlines_nSamplesMax = max(nKlines_nSamplesMax, nSamples)
            #---EMA
            if cac['EMA_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_EMA):
                    lineActive = cac.get(f'EMA_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac[f'EMA_{lineIndex}_NSamples']
                    nKlines_nSamplesMax = max(nKlines_nSamplesMax, nSamples)
            #---BOL
            if cac['BOL_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_BOL):
                    lineActive = cac.get(f'BOL_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac[f'BOL_{lineIndex}_NSamples']
                    nKlines_nSamplesMax = max(nKlines_nSamplesMax, nSamples)
            #---IVP
            if cac['IVP_Master']:
                nSamples = cac['IVP_NSamples']
                nKlines_nSamplesMax = max(nKlines_nSamplesMax, nSamples)
            #---VOL
            if cac['VOL_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_VOL):
                    lineActive = cac.get(f'VOL_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac[f'VOL_{lineIndex}_NSamples']
                    nKlines_nSamplesMax = max(nKlines_nSamplesMax, nSamples)
            #---MMACDSHORT
            if cac['MMACDSHORT_Master']:
                multiplier = cac['MMACDSHORT_Multiplier']
                for lineIndex in range (atmEta_Constants.NLINES_MMACDSHORT):
                    lineActive = cac.get(f'MMACDSHORT_MA{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac[f'MMACDSHORT_MA{lineIndex}_NSamples']
                    nKlines_nSamplesMax = max(nKlines_nSamplesMax, nSamples*multiplier)
            #---MMACDLONG
            if cac['MMACDLONG_Master']:
                multiplier = cac['MMACDLONG_Multiplier']
                for lineIndex in range (atmEta_Constants.NLINES_MMACDLONG):
                    lineActive = cac.get(f'MMACDLONG_MA{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac[f'MMACDLONG_MA{lineIndex}_NSamples']
                    nKlines_nSamplesMax = max(nKlines_nSamplesMax, nSamples*multiplier)
            #---DMIxADX
            if cac['DMIxADX_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_DMIxADX):
                    lineActive = cac.get(f'DMIxADX_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac[f'DMIxADX_{lineIndex}_NSamples']
                    nKlines_nSamplesMax = max(nKlines_nSamplesMax, nSamples)
            #---MFI
            if cac['MFI_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_MFI):
                    lineActive = cac.get(f'MFI_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac[f'MFI_{lineIndex}_NSamples']
                    nKlines_nSamplesMax = max(nKlines_nSamplesMax, nSamples)
        
        #[5]: Number of completely analyzed klines & to display
        nKlines_minCompleteAnalysis = max(cac['NI_MinCompleteAnalysis'], 1)
        nKlines_toDisplay           = max(cac['NI_NAnalysisToDisplay'],  2)

        #[6]: Generate a currency analysis tracker
        #---Currency Analysis Description & Base Elements
        currencyData = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', currencySymbol))
        if currencyData == _IPC_PRD_INVALIDADDRESS: 
            precisions = None
            mrktRegTS  = None
        else:
            precisions = currencyData['precisions'].copy()
            mrktRegTS  = currencyData['kline_firstOpenTS']
        currencyAnalysis = {'currencySymbol':                    currencySymbol,
                            'currencyAnalysisConfigurationCode': currencyAnalysisConfigurationCode,
                            'currencyAnalysisConfiguration':     cac,
                            'status':                            None,
                            'precisions':                        precisions,
                            'marketRegistrationTS':              mrktRegTS,
        #---Currency Analysis Processing Params
                            'analysisParams':                   analysisParams,
                            'analysisToProcess_sorted':         analysisToProcess_sorted,
                            'nKlines_nSamplesMax':              nKlines_nSamplesMax,
                            'nKlines_minCompleteAnalysis':      nKlines_minCompleteAnalysis,
                            'nKlines_toDisplay':                nKlines_toDisplay,
                            'neuralNetworkCodes':               list(),
                            'neuralNetworkMaxKlinesRefLen':     0,
                            'streamConnection':                 None,
                            'kline_lastDataAvailableCheck_ns':  0,
                            'kline_preparing_targetFetchRange': None,
                            'kline_preparing_waitingFetch':     False,
                            'kline_analysisTargets':            set(),
                            'kline_lastStreamedProcTime':       None,
                            'kline_lastAnalyzedKline':          None,
                            'kline_lastAnalyzedProcTime':       None,
                            'kline_firstAnalyzedOpenTS':        None,
                            'klines':                           {'raw': dict(), 'raw_status': dict()},
                            'klines_lastRemovedOpenTS':         {'raw': None},
                            'bidsAndAsks':                      {'depth': dict(), 'WOI': dict()},
                            'bidsAndAsks_WOI_oldestComputedS':  None,
                            'bidsAndAsks_WOI_latestComputedS':  None,
                            'aggTrades':                        {'volumes': {'samples': list(), 'buy': 0, 'sell': 0}, 'NES': dict()},
                            'aggTrades_NES_oldestComputedS':    None,
                            'aggTrades_NES_latestComputedS':    None,
                            'dataSubscribers': dict()}
        #---Klines & WOI & NES Data Containers
        for aCode in analysisParams: 
            currencyAnalysis['klines'][aCode] = dict()
            currencyAnalysis['klines_lastRemovedOpenTS'][aCode] = None
        if cac['WOI_Master']:
            for lineIndex in range (atmEta_Constants.NLINES_WOI):
                lineActive = cac.get(f'WOI_{lineIndex}_LineActive', False)
                if not lineActive: continue
                currencyAnalysis['bidsAndAsks'][f'WOI_{lineIndex}'] = dict()
        if cac['NES_Master']:
            for lineIndex in range (atmEta_Constants.NLINES_NES):
                lineActive = cac.get(f'NES_{lineIndex}_LineActive', False)
                if not lineActive: continue
                currencyAnalysis['aggTrades'][f'NES_{lineIndex}'] = dict()
        #---Finally
        self.__currencyAnalysis[currencyAnalysisCode] = currencyAnalysis

        #[7]: Error Upon Generation
        if invalidLines:
            currencyAnalysis['status'] = _CURRENCYANALYSIS_STATUS_ERROR
            self.ipcA.sendFAR(targetProcess  = 'TRADEMANAGER', 
                              functionID     = 'onCurrencyAnalysisStatusUpdate', 
                              functionParams = {'currencyAnalysisCode': currencyAnalysisCode, 
                                                'newStatus':            currencyAnalysis['status']}, 
                              farrHandler = None)
            return

        #[8]: Neural Network Connections Data Request (If needed)
        if cac['NNA_Master']:
            #[8-1]: Neural Network Codes for Active Lines
            for lineIndex in range (atmEta_Constants.NLINES_NNA):
                lineActive = cac.get(f'NNA_{lineIndex}_LineActive', False)
                if not lineActive: continue
                nnCode = cac[f'NNA_{lineIndex}_NeuralNetworkCode']
                currencyAnalysis['neuralNetworkCodes'].append(nnCode)

            #[8-2]: If there exist NN connecions data to request
            for nnCode in currencyAnalysis['neuralNetworkCodes']:
                if nnCode in self.__neuralNetworks: 
                    self.__neuralNetworks_Referrers[nnCode].add(currencyAnalysisCode)
                    continue
                if nnCode in self.__neuralNetworks_ConnectionDataRequests_NNCodes:
                    self.__neuralNetworks_ConnectionDataRequests_NNCodes[nnCode].add(currencyAnalysisCode)
                    continue
                else:
                    rID = self.ipcA.sendFAR(targetProcess  = "NEURALNETWORKMANAGER",
                                            functionID     = 'getNeuralNetworkConnections',
                                            functionParams = {'neuralNetworkCode': nnCode},
                                            farrHandler    = self.__farr_onNeuralNetworkConnectionsDataRequestResponse)
                    self.__neuralNetworks_ConnectionDataRequests_RIDs[rID]       = nnCode
                    self.__neuralNetworks_ConnectionDataRequests_NNCodes[nnCode] = {currencyAnalysisCode,}

            #[8-3]: Check if is waiting for any NN connections data
            if any(nnCode not in self.__neuralNetworks for nnCode in currencyAnalysis['neuralNetworkCodes']):
                #Initial status set
                currencyAnalysis['status'] = _CURRENCYANALYSIS_STATUS_WAITINGNEURALNETWORKCONNECTIONSDATA
                #Exit Function
                return
            
        #[9]: Initial Status & Base Data Subscription Requests
        currencyAnalysis['status'] = _CURRENCYANALYSIS_STATUS_WAITINGSTREAM
        self.__ca_addCurrencyAnalysisToKlineInfoSubscription(currencySymbol   = currencySymbol, currencyAnalysisCode = currencyAnalysisCode)
        self.__ca_addCurrencyAnalysisToKlineStreamSubscription(currencySymbol = currencySymbol, currencyAnalysisCode = currencyAnalysisCode)

    def __far_removeCurrencyAnalysis(self, requester, currencyAnalysisCode):
        #[1]: Requester Check
        if requester != 'TRADEMANAGER': return

        #[2]: Currency Analysis Existence Check
        if currencyAnalysisCode not in self.__currencyAnalysis: return

        #[3]: Currency Analysis
        ca      = self.__currencyAnalysis[currencyAnalysisCode]
        cSymbol = ca['currencySymbol']

        #[4]: Kline Stream Subscription
        if cSymbol in self.__klineStreamSubscribedSymbols:
            if currencyAnalysisCode in self.__klineStreamSubscribedSymbols[cSymbol]: self.__klineStreamSubscribedSymbols[cSymbol].remove(currencyAnalysisCode)
            if not self.__klineStreamSubscribedSymbols[cSymbol]: 
                del self.__klineStreamSubscribedSymbols[cSymbol]
                self.ipcA.sendFAR(targetProcess = 'BINANCEAPI', functionID = 'unregisterKlineStreamSubscription', functionParams = {'subscriptionID': None, 'currencySymbol': cSymbol}, farrHandler = None)
        
        #[5]: Currency Info Subscription Tracker
        if cSymbol in self.__klineInfoSubscribedSymbols:
            if currencyAnalysisCode in self.__klineInfoSubscribedSymbols[cSymbol]: self.__klineInfoSubscribedSymbols[cSymbol].remove(currencyAnalysisCode)
            if not self.__klineInfoSubscribedSymbols[cSymbol]: 
                del self.__klineInfoSubscribedSymbols[cSymbol]
                self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'unregisterCurrecnyInfoSubscription', functionParams = {'symbol': cSymbol}, farrHandler = None)
        
        #[6]: Neural Network
        for nnCode in ca['neuralNetworkCodes']:
            #[6-1]: Connection Data Request Tracker Update
            if nnCode in self.__neuralNetworks_ConnectionDataRequests_NNCodes:
                self.__neuralNetworks_ConnectionDataRequests_NNCodes[nnCode].remove(currencyAnalysisCode)
            #[6-2]: Neural Network Referrer Update & Clearing
            if nnCode in self.__neuralNetworks:
                self.__neuralNetworks_Referrers[nnCode].remove(currencyAnalysisCode)
                if not self.__neuralNetworks_Referrers[nnCode]:
                    del self.__neuralNetworks[nnCode]
                    del self.__neuralNetworks_Referrers[nnCode]
        gc.collect()
        torch.cuda.empty_cache()

        #[7]: Currency Analysis
        del self.__currencyAnalysis[currencyAnalysisCode]

    def __far_restartCurrencyAnalysis(self, requester, currencyAnalysisCode):
        if (requester == 'TRADEMANAGER'):
            if (currencyAnalysisCode in self.__currencyAnalysis):
                pass

    #<BINANCEAPI>
    def __far_onKlineStreamReceival(self, requester, symbol, streamConnectionTime, kline, closed):
        if (requester == 'BINANCEAPI'):
            if (symbol in self.__klineStreamSubscribedSymbols):
                for currencyAnalysisCode in self.__klineStreamSubscribedSymbols[symbol]: 
                    if (self.__currencyAnalysis[currencyAnalysisCode]['precisions'] != None): self.__ca_onStreamReceival_Kline(currencyAnalysisCode, streamConnectionTime, kline, closed)
    def __far_onOrderbookUpdate(self, requester, symbol, streamConnectionTime, bids, asks):
        if (requester == 'BINANCEAPI'):
            if (symbol in self.__klineStreamSubscribedSymbols):
                for currencyAnalysisCode in self.__klineStreamSubscribedSymbols[symbol]: self.__ca_onStreamReceival_OrderBook(currencyAnalysisCode, streamConnectionTime, bids, asks)
    def __far_onAggTradeStreamReceival(self, requester, symbol, streamConnectionTime, aggTrade):
        if (requester == 'BINANCEAPI'):
            if (symbol in self.__klineStreamSubscribedSymbols):
                for currencyAnalysisCode in self.__klineStreamSubscribedSymbols[symbol]: self.__ca_onStreamReceival_AggTrade(currencyAnalysisCode, streamConnectionTime, aggTrade)

    #<DATAMANAGER>
    def __far_onCurrenciesUpdate(self, requester, updatedContents):
        if (requester == 'DATAMANAGER'):
            for updatedContent in updatedContents:
                symbol    = updatedContent['symbol']
                contentID = updatedContent['id']
                contentID_type = type(contentID)
                if (contentID_type == str):
                    if (contentID == '_ONFIRSTSUBSCRIPTION'):
                        _currencyInfo = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol))
                        for _caCode in self.__klineInfoSubscribedSymbols[symbol]:
                            self.__currencyAnalysis[_caCode]['precisions']           = _currencyInfo['precisions'].copy()
                            self.__currencyAnalysis[_caCode]['marketRegistrationTS'] = _currencyInfo['kline_firstOpenTS']
                elif (contentID_type == tuple): pass
    def __farr_onKlineFetchResponse(self, responder, requestID, functionResult):
        if (responder == 'DATAMANAGER'):
            _localRequestTracker = self.__currencyAnalysisPrep_klineFetchRequests[requestID]
            _caCode                         = _localRequestTracker['currencyAnalysisCode']
            _streamConnectionTimeOnDispatch = _localRequestTracker['streamConnectionTimeOnDispatch']
            _ca                             = self.__currencyAnalysis[_caCode]
            if ((_ca['streamConnection'] is not None) and (_ca['streamConnection']['connectionTime'] == _streamConnectionTimeOnDispatch)):
                _requestResult_result = functionResult['result']
                _requestResult_klines = functionResult['klines']
                #[1-1]: On Successful Kline Fetch
                if (_requestResult_result == 'SKF'):
                    #Update the target fetch range
                    _targetFetchRange   = _ca['kline_preparing_targetFetchRange']
                    _fetchedKlinesRange = (_requestResult_klines[0][0], _requestResult_klines[-1][1])
                    if ((_targetFetchRange[0] == _fetchedKlinesRange[0]) and (_targetFetchRange[1] == _fetchedKlinesRange[1])): _ca['kline_preparing_targetFetchRange'] = None
                    else:                                                                                                       _ca['kline_preparing_targetFetchRange'] = [_fetchedKlinesRange[1]+1, _targetFetchRange[1]]
                    #Store the received klines and add to the analysis queue
                    _ca_klines_raw        = _ca['klines']['raw']
                    _ca_klines_raw_status = _ca['klines']['raw_status']
                    _ca_analysisTargets   = _ca['kline_analysisTargets']
                    for _kline in _requestResult_klines:
                        _t_open = _kline[KLINDEX_OPENTIME]
                        #Kline Raw
                        _ca_klines_raw[_t_open] = _kline[:11]+(True,)
                        #Kline Raw Status
                        _ca_klines_raw_status[_t_open] = {'p_max': _kline[KLINDEX_HIGHPRICE]}
                        if (_t_open-KLINTERVAL_S in _ca_klines_raw_status) and (_ca_klines_raw_status[_t_open]['p_max'] < _ca_klines_raw_status[_t_open-KLINTERVAL_S]['p_max']): _ca_klines_raw_status[_t_open]['p_max'] = _ca_klines_raw_status[_t_open-KLINTERVAL_S]['p_max']
                        #Analysis Queue Add
                        _ca_analysisTargets.add(_t_open)
                #[1-2]: On Unexpected Error Occurrance during kline fetch
                elif (_requestResult_result == 'UEO'): pass
                #Update The Fetch Waiting Flag
                _ca['kline_preparing_waitingFetch'] = False
            del self.__currencyAnalysisPrep_klineFetchRequests[requestID]

    #<GUI>
    def __far_registerCurrencyAnalysisDataSubscription(self, requester, requestID, currencyAnalysisCode, dataReceiver):
        if (requester == 'GUI'):
            if (currencyAnalysisCode in self.__currencyAnalysis):
                _ca = self.__currencyAnalysis[currencyAnalysisCode]
                if (_ca['status'] == _CURRENCYANALYSIS_STATUS_ANALYZINGREALTIME):
                    #Klines
                    _dispatchRange_klines = [atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = _ca['kline_lastAnalyzedKline'][0], nTicks = -(_ca['nKlines_toDisplay']-1)),
                                             _ca['kline_lastAnalyzedKline'][0]+(KLINTERVAL_S-1)]
                    _analyzedKlines = dict()
                    for _klDataType in _ca['klines']:
                        _analyzedKlines[_klDataType] = dict()
                        for _ts in range (_dispatchRange_klines[0], _dispatchRange_klines[1], KLINTERVAL_S):
                            if (_ts in _ca['klines'][_klDataType]): _analyzedKlines[_klDataType][_ts] = _ca['klines'][_klDataType][_ts]
                    #BidsAndAsks
                    if (_ca['bidsAndAsks_WOI_oldestComputedS'] is None): _dispatchRange_bidsAndAsks = None
                    else:                                                _dispatchRange_bidsAndAsks = [_ca['bidsAndAsks_WOI_oldestComputedS'], _ca['bidsAndAsks_WOI_latestComputedS']+BIDSANDASKSSAMPLINGINTERVAL_S-1]
                    _bidsAndAsks_copy = {'depth': dict()}
                    _baa_depth_copy = _bidsAndAsks_copy['depth'] 
                    _baa_depth      = _ca['bidsAndAsks']['depth']
                    for _pl in _baa_depth: _baa_depth_copy[_pl] = _baa_depth[_pl]
                    for _baaDataType in _ca['bidsAndAsks']:
                        if (_baaDataType != 'depth'):
                            _baa_data_copy = dict()
                            _baa_data      = _ca['bidsAndAsks'][_baaDataType]
                            if (_dispatchRange_bidsAndAsks is not None):
                                for _tt in range(_dispatchRange_bidsAndAsks[0], _dispatchRange_bidsAndAsks[1]+1, BIDSANDASKSSAMPLINGINTERVAL_S): _baa_data_copy[_tt] = _baa_data[_tt]
                            _bidsAndAsks_copy[_baaDataType] = _baa_data_copy
                    #AggTrades
                    if (_ca['aggTrades_NES_oldestComputedS'] is None): _dispatchRange_aggTrades = None
                    else:                                              _dispatchRange_aggTrades = [_ca['aggTrades_NES_oldestComputedS'], _ca['aggTrades_NES_oldestComputedS']+AGGTRADESAMPLINGINTERVAL_S-1]
                    _aggTrades_copy = dict()
                    for _atDataType in _ca['aggTrades']:
                        if (_atDataType != 'volumes'):
                            _at_data_copy = dict()
                            _at_data      = _ca['aggTrades'][_atDataType]
                            if (_dispatchRange_aggTrades is not None):
                                for _tt in range (_dispatchRange_aggTrades[0], _dispatchRange_aggTrades[1]+1, AGGTRADESAMPLINGINTERVAL_S): _at_data_copy[_tt] = _at_data[_tt]
                            _aggTrades_copy[_atDataType] = _at_data_copy
                    #Dispatch Range Record
                    _ca['dataSubscribers'][dataReceiver] = {'KLINES':      _dispatchRange_klines,
                                                            'BIDSANDASKS': _dispatchRange_bidsAndAsks,
                                                            'AGGTRADES':   _dispatchRange_aggTrades}
                    return {'analysisParams': _ca['analysisParams'], 'klines': _analyzedKlines, 'bidsAndAsks': _bidsAndAsks_copy, 'aggTrades': _aggTrades_copy}
                else: 
                    _ca['dataSubscribers'][dataReceiver] = {'KLINES':      None,
                                                            'BIDSANDASKS': None,
                                                            'AGGTRADES':   None}
                    return {'analysisParams': _ca['analysisParams'], 'klines': None, 'bidsAndAsks': None, 'aggTrades': None}
    def __far_unregisterCurrencyAnalysisDataSubscription(self, requester, currencyAnalysisCode, dataReceiver):
        if (requester == 'GUI'):
            if (currencyAnalysisCode in self.__currencyAnalysis): 
                if (dataReceiver in self.__currencyAnalysis[currencyAnalysisCode]['dataSubscribers']): del self.__currencyAnalysis[currencyAnalysisCode]['dataSubscribers'][dataReceiver]

    #<NEURALNETWORK>
    def __farr_onNeuralNetworkConnectionsDataRequestResponse(self, responder, requestID, functionResult):
        #[1]: Responder Check
        if responder != 'NEURALNETWORKMANAGER': return

        #[2]: Request ID Check
        if requestID not in self.__neuralNetworks_ConnectionDataRequests_RIDs: return

        #[3]: Result Interpretation
        nnCode_rq = self.__neuralNetworks_ConnectionDataRequests_RIDs.pop(requestID)
        caCodes   = self.__neuralNetworks_ConnectionDataRequests_NNCodes.pop(nnCode_rq)
        if functionResult is not None:
            #[3-1]: Results
            neuralNetworkCode = functionResult['neuralNetworkCode']
            nKlines           = functionResult['nKlines']
            hiddenLayers      = functionResult['hiddenLayers']
            outputLayer       = functionResult['outputLayer']
            connections       = functionResult['connections']

            #[3-2]: Neural Network Code Check
            if neuralNetworkCode == nnCode_rq:
                #[3-3]: Generate a local Neural Network Instance
                nn = atmEta_NeuralNetworks.neuralNetwork_MLP(nKlines = nKlines, hiddenLayers = hiddenLayers, outputLayer = outputLayer, device = 'cpu')
                nn.importConnectionsData(connections = connections)
                nn.setEvaluationMode()
                self.__neuralNetworks[neuralNetworkCode]           = nn
                self.__neuralNetworks_Referrers[neuralNetworkCode] = set()

                #[3-4]: Currency Analysis Handling
                for caCode in caCodes:
                    ca = self.__currencyAnalysis[caCode]
                    #[3-4-1]: Add Referrer
                    self.__neuralNetworks_Referrers[neuralNetworkCode].add(caCode)

                    #[3-4-2]: Check If All Neural Networks Are Loaded For This CA
                    if all(nnCode in self.__neuralNetworks for nnCode in ca['neuralNetworkCodes']):
                        #Currency Analysis Status update
                        ca['status'] = _CURRENCYANALYSIS_STATUS_WAITINGSTREAM
                        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'onCurrencyAnalysisStatusUpdate', functionParams = {'currencyAnalysisCode': caCode, 'newStatus': ca['status']}, farrHandler = None)

                        #Neural Network Maximum Klines Reference Length
                        ca['neuralNetworkMaxKlinesRefLen'] = max(self.__neuralNetworks[nnCode].getNKlines() for nnCode in ca['neuralNetworkCodes'])

                        #Precisions Read (If possible)
                        precisions = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', ca['currencySymbol'], 'precisions'))
                        if precisions != _IPC_PRD_INVALIDADDRESS: ca['precisions'] = precisions

                        #Klines data setup
                        self.__ca_addCurrencyAnalysisToKlineInfoSubscription(currencySymbol   = ca['currencySymbol'], currencyAnalysisCode = caCode)
                        self.__ca_addCurrencyAnalysisToKlineStreamSubscription(currencySymbol = ca['currencySymbol'], currencyAnalysisCode = caCode)

                #[3-4]: Exit Function
                return

        #[4]: If reached here, it means an exception has occurred
        for caCode in caCodes:
            ca = self.__currencyAnalysis[caCode]
            ca['status'] = _CURRENCYANALYSIS_STATUS_ERROR
            self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'onCurrencyAnalysisStatusUpdate', functionParams = {'currencyAnalysisCode': caCode, 'newStatus': ca['status']}, farrHandler = None)
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------