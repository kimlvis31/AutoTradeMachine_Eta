#ATM Modules
import atmEta_IPC
import atmEta_Analyzers
import atmEta_Auxillaries
import atmEta_NeuralNetworks
import atmEta_Constants

#Python Modules
import time
import termcolor
import pprint
from collections import deque

#Constants
_IPC_THREADTYPE_MT         = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT         = atmEta_IPC._THREADTYPE_AT
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

KLINE_INTERVAL_ID_1m  = 0
KLINE_INTERVAL_ID_3m  = 1
KLINE_INTERVAL_ID_5m  = 2
KLINE_INTERVAL_ID_15m = 3
KLINE_INTERVAL_ID_30m = 4
KLINE_INTERVAL_ID_1h  = 5
KLINE_INTERVAL_ID_2h  = 6
KLINE_INTERVAL_ID_4h  = 7
KLINE_INTERVAL_ID_6h  = 8
KLINE_INTERVAL_ID_8h  = 9
KLINE_INTERVAL_ID_12h = 10
KLINE_INTERVAL_ID_1d  = 11
KLINE_INTERVAL_ID_3d  = 12
KLINE_INTERVAL_ID_1W  = 13
KLINE_INTERVAL_ID_1M  = 14

KLINTERVAL   = atmEta_Constants.KLINTERVAL
KLINTERVAL_S = atmEta_Constants.KLINTERVAL_S

STATUS_WAITINGNEURALNETWORK = 0
STATUS_WAITINGSTREAM        = 1
STATUS_WAITINGDATAAVAILABLE = 2
STATUS_QUEUED               = 3
STATUS_FETCHING             = 4
STATUS_INITIALANALYZING     = 5
STATUS_ANALYZING            = 6
STATUS_ERROR                = 7

_STREAMCONTINUITY_REVERSE = 0
_STREAMCONTINUITY_NORMAL  = 1
_STREAMCONTINUITY_FUTURE  = 2
_DATAFETCHCHUNKSIZE       = 43_200
_AGGREGATIONCHUNKSIZE     = 14_400
_ANALYSISCHUNKSIZE        = 1_440

_MINANALYSISINTERVAL_NS           = 1e9
_DATAAVAILABILITYCHECKINTERVAL_NS = 1e9

KLINTERVAL   = atmEta_Constants.KLINTERVAL
KLINTERVAL_S = atmEta_Constants.KLINTERVAL_S

class CurrencyAnalysis:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, ipcA, neuralNetworks, currencyAnalysisCode, currencySymbol, currencyAnalysisConfigurationCode, currencyAnalysisConfiguration):
        #[1]: Instances
        self.ipcA = ipcA
        #---[1-1]: Identity
        self.__currencyAnalysisCode              = currencyAnalysisCode
        self.__currencySymbol                    = currencySymbol
        self.__currencyAnalysisConfigurationCode = currencyAnalysisConfigurationCode
        self.__currencyAnalysisConfiguration     = currencyAnalysisConfiguration
        self.__status                            = STATUS_WAITINGSTREAM
        #---[1-2]: Market Data Control
        self.__data_raw               = {target: dict() for target in ('kline', 'depth', 'aggTrade')}
        self.__data_agg               = dict() #{intervalID: {target: dict() for target in ('kline', 'depth', 'aggTrade')}}
        self.__data_timestamps        = {'raw': {target: deque() for target in ('kline', 'depth', 'aggTrade')}}
        self.__stream                 = {target: {'firstStreamOpenTS': None,
                                                  'lastStream':        None}
                                         for target in ('kline', 'depth', 'aggTrade')}
        self.__availabilityChecks     = {target: [] for target in ('kline', 'depth', 'aggTrade')}
        self.__fetchRequests          = dict()
        self.__aggregators            = {'kline':    atmEta_Analyzers.aggregator_kline,
                                         'depth':    atmEta_Analyzers.aggregator_depth,
                                         'aggTrade': atmEta_Analyzers.aggregator_aggTrade}
        self.__lastAggregated         = {target: None for target in ('kline', 'depth', 'aggTrade')}
        self.__lastClosedAggregations = dict() #{intervalID: {target: dict() for target in ('kline', 'depth', 'aggTrade')}}
        #---[1-3]: Analysis Control
        self.__neuralNetworks           = neuralNetworks
        self.__neuralNetworkCodes       = None
        self.__analysisParams           = None
        self.__analysisToProcess_sorted = None
        self.__analysisKwargs           = None
        self.__analysisQueue            = deque()
        self.__lastQueuedRawTS          = None
        #---[1-4]: Memory Control
        self.__memCtrl = None
        #---[1-5]: Subscription
        self.__subscribers = dict()

        #[2]: Currency Information Read
        self.__currencyInfo = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', currencySymbol))

        #[3]: Analysis Control Preparation
        self.__initializeAnalysisControl(currencyAnalysisConfiguration = currencyAnalysisConfiguration)

    def __initializeAnalysisControl(self, currencyAnalysisConfiguration):
        cac_all = currencyAnalysisConfiguration
        #[1]: Analysis Parameters
        aParams_all  = dict()
        iIDs_invalid = set()
        invalidFound = False
        for iID, cac_iID in cac_all.items():
            aParams_iID, invalidLines = atmEta_Analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(cac_iID)
            if invalidLines:
                invalidLines_str = atmEta_Auxillaries.formatInvalidLinesReportToString(invalidLines = invalidLines)
                print(termcolor.colored((f"[ANALYZER{self.analyzerIndex}] Invalid Lines Detected While Attempting To Add Currency Analysis."+invalidLines_str), 'light_red'))
                invalidFound = True
            if aParams_iID: 
                aParams_all[iID] = aParams_iID
            if invalidLines or not aParams_iID:
                iIDs_invalid.add(iID)
        self.__analysisParams = aParams_all
        if invalidFound:
            print(termcolor.colored((f"[ANALYZER{self.analyzerIndex}] Invalid Lines Detected While Attempting To Add Currency Analysis."+invalidLines_str), 'light_red'))
            self.__updateStatus(status = STATUS_ERROR)
        for iID_invalid in iIDs_invalid:
            del cac_all[iID_invalid]

        #[2]: Data Containers
        dAgg = self.__data_agg
        dTSs = self.__data_timestamps
        lcas = self.__lastClosedAggregations
        for iID, aParams_iID in aParams_all.items():
            dAgg[iID] = {target: dict()  for target in ('kline', 'depth', 'aggTrade')}
            dTSs[iID] = {target: deque() for target in ('kline', 'depth', 'aggTrade')}
            lcas[iID] = {target: dict()  for target in ('kline', 'depth', 'aggTrade')}
            dAgg_iID = dAgg[iID]
            dTSs_iID = dTSs[iID]
            for aCode in aParams_iID:
                dAgg_iID[aCode] = dict()
                dTSs_iID[aCode] = deque()

        #[3]: Analysis To Process Sorted
        atp_sorted_all = dict()
        for iID, aParams_iID in aParams_all.items():
            atp_sorted_iID = []
            for aType in atmEta_Analyzers.ANALYSIS_GENERATIONORDER:
                atp_sorted_iID += [(aType, aCode) for aCode in aParams_iID if aCode[:len(aType)] == aType]
            atp_sorted_all[iID] = atp_sorted_iID
        self.__analysisToProcess_sorted = atp_sorted_all

        #[4]: Neural Network Codes
        nnCodes = set()
        for cac_iID in cac_all.values():
            if not cac_iID['NNA_Master']:
                continue
            for lIdx in range (atmEta_Constants.NLINES_NNA):
                lActive = cac_iID.get(f'NNA_{lIdx}_LineActive', False)
                if not lActive: continue
                nnCode = cac_iID[f'NNA_{lIdx}_NeuralNetworkCode']
                nnCodes.add(nnCode)
        self.__neuralNetworkCodes = tuple(nnCodes)
        if nnCodes and self.__status != STATUS_ERROR:
            self.__updateStatus(status = STATUS_WAITINGNEURALNETWORK)

        #[5]: Required Minimum Data Length Determination
        mc = dict()
        for iID, cac_iID in cac_all.items():
            mmdrl = 1
            #---SMA
            if cac_iID['SMA_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_SMA):
                    lineActive = cac_iID.get(f'SMA_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac_iID[f'SMA_{lineIndex}_NSamples']
                    mmdrl = max(mmdrl, nSamples)
            #---WMA
            if cac_iID['WMA_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_WMA):
                    lineActive = cac_iID.get(f'WMA_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac_iID[f'WMA_{lineIndex}_NSamples']
                    mmdrl = max(mmdrl, nSamples)
            #---EMA
            if cac_iID['EMA_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_EMA):
                    lineActive = cac_iID.get(f'EMA_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac_iID[f'EMA_{lineIndex}_NSamples']
                    mmdrl = max(mmdrl, nSamples)
            #---BOL
            if cac_iID['BOL_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_BOL):
                    lineActive = cac_iID.get(f'BOL_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac_iID[f'BOL_{lineIndex}_NSamples']
                    mmdrl = max(mmdrl, nSamples)
            #---IVP
            if cac_iID['IVP_Master']:
                nSamples = cac_iID['IVP_NSamples']
                mmdrl = max(mmdrl, nSamples)
            #---VOL
            if cac_iID['VOL_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_VOL):
                    lineActive = cac_iID.get(f'VOL_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac_iID[f'VOL_{lineIndex}_NSamples']
                    mmdrl = max(mmdrl, nSamples)
            #---MMACD
            if cac_iID['MMACD_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_MMACD):
                    lineActive = cac_iID.get(f'MMACD_MA{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac_iID[f'MMACD_MA{lineIndex}_NSamples']
                    mmdrl = max(mmdrl, nSamples)
            #---DMIxADX
            if cac_iID['DMIxADX_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_DMIxADX):
                    lineActive = cac_iID.get(f'DMIxADX_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac_iID[f'DMIxADX_{lineIndex}_NSamples']
                    mmdrl = max(mmdrl, nSamples)
            #---MFI
            if cac_iID['MFI_Master']:
                for lineIndex in range (atmEta_Constants.NLINES_MFI):
                    lineActive = cac_iID.get(f'MFI_{lineIndex}_LineActive', False)
                    if not lineActive: continue
                    nSamples = cac_iID[f'MFI_{lineIndex}_NSamples']
                    mmdrl = max(mmdrl, nSamples)
            #Record
            mc[iID] = {'minCompleteAnalysis':          max(cac_iID['NI_MinCompleteAnalysis'], 1),
                       'analysisDisplayLength':        max(cac_iID['NI_NAnalysisToDisplay'],  2),
                       'maxMarketDataReferenceLength': mmdrl}
        self.__memCtrl = mc
    
    def getNeuralNetworkCodes(self):
        return self.__neuralNetworkCodes

    def getCurrencySymbol(self):
        return self.__currencySymbol

    def onCurrencyUpdate(self, currencyInfo):
        #[1]: Currency Info Update
        self.__currencyInfo = currencyInfo

        #[2]: If Waiting Data Available, Check Data Availability And Move to Queued Status If So.
        if self.__status == STATUS_WAITINGDATAAVAILABLE:
            if self.__checkDataAvailable():
                self.__updateStatus(status = STATUS_QUEUED)

    def onNeuralNetworkConnectionsDataArrival(self, neuralNetworkCode):
        #[1]: Fetch Success Check
        if neuralNetworkCode is None:
            self.__updateStatus(status = STATUS_ERROR)
            return

        #[2]: Instances
        nns     = self.__neuralNetworks
        nnCodes = self.__neuralNetworkCodes

        #[3]: Check If All Neural Networks Are Ready
        if not all(nnCode in nns for nnCode in nnCodes):
            return
        
        #[4]: Update Market Data Reference Length
        for nnCode in nnCodes:
            nn = nns[nnCode]
            nReferenceLength = nn.getNKlines()

        #[5]: Status Update
        self.__updateStatus(status = STATUS_WAITINGSTREAM)

    def addSubscriber(self, subscriber):
        #[1]: Instance
        subs = self.__subscribers

        #[2]: Subscriber Update
        subs[subscriber] = None
        
        #[3]: Analysis Parameters Return
        return {'analysisParams': self.__analysisParams}

    def removeSubscriber(self, subscriber):
        #[1]: Instance
        subs = self.__subscribers

        #[2]: Subscriber Update
        if subscriber in subs:
            del subs[subscriber]

    def isBusy(self):
        return (0 < len(self.__analysisQueue))

    def isRunning(self):
        return (self.__status == STATUS_ANALYZING)

    def process(self, allowPrep):
        #[1]: Instances
        status = self.__status

        #[2]: Status-Dependent Handling
        aGenTime_ns = None

        #---[3-1]: Analyzing
        if status == STATUS_ANALYZING:
            _, aGenTime_ns = self.__analyzeData()

        #---[3-2]: Queued - This Means Waiting For Other Currency Analysis To Complete Their Preparations, So This Can Start Fetching Market Data
        elif status == STATUS_QUEUED:
            if allowPrep:
                acs = self.__availabilityChecks
                frs = self.__fetchRequests
                func_gnitt   = atmEta_Auxillaries.getNextIntervalTickTimestamp
                func_sendFAR = self.ipcA.sendFAR
                for t in ('kline', 'depth', 'aggTrade'):
                    for aCheck_beg, aCheck_end in acs[t]:
                        chunkBeg = aCheck_beg
                        while chunkBeg <= aCheck_end:
                            chunkEnd_max = func_gnitt(intervalID = KLINTERVAL, timestamp = chunkBeg, nTicks = _DATAFETCHCHUNKSIZE)-1
                            chunkEnd_eff = min(chunkEnd_max, aCheck_end)
                            rID = func_sendFAR(targetProcess  = 'DATAMANAGER',
                                               functionID     = 'fetchMarketData',
                                               functionParams = {'symbol':     self.__currencySymbol,
                                                                 'target':     t,
                                                                 'fetchRange': (chunkBeg, chunkEnd_eff)},
                                               farrHandler    = self.__onFetchRequestResponse_FARR)
                            frs[rID] = {'target':            t,
                                        'fetchRequestRange': (chunkBeg, chunkEnd_eff),
                                        'fetchedRange':      None,
                                        'complete':          False}
                            chunkBeg = chunkEnd_eff+1
                    acs[t].clear()
                if frs: self.__updateStatus(status = STATUS_FETCHING)
                else:   self.__updateStatus(status = STATUS_INITIALANALYZING)

        #---[3-3]: Initial Analyzing
        elif status == STATUS_INITIALANALYZING:
            #[3-3-1]: Aggregation
            allAggComplete = True
            for target in ('kline', 'depth', 'aggTrade'):
                allAggComplete = self.__aggregateData(target = target)
                if not allAggComplete: break
            #[3-3-2]: Analysis
            allAnalysisComplete = False
            if allAggComplete: 
                allAnalysisComplete, _ = self.__analyzeData()
            #[3-3-3]: Status Update
            if allAnalysisComplete:
                self.__updateStatus(status = STATUS_ANALYZING)

        #[3]: Return Analysis Generation Time
        return aGenTime_ns

    def restart(self, currencyAnalysisConfiguration):
        self.__initializeAnalysisControl(currencyAnalysisConfiguration = currencyAnalysisConfiguration)

    def onDataStreamReceival(self, target, stream):
        #[1]: Error Raised Check
        if self.__status == STATUS_ERROR:
            return
        
        #[2]: Instances
        sControl    = self.__stream
        sControl_dt = sControl[target]
        stream_openTime = stream[COMMONDATAINDEXES['openTime'][target]]
        stream_closed   = stream[COMMONDATAINDEXES['closed'][target]]
        func_gnitt = atmEta_Auxillaries.getNextIntervalTickTimestamp

        #[3]: Waiting Stream
        if self.__status == STATUS_WAITINGSTREAM:
            #[3-1]: If This Is The First Stream, Record
            if sControl_dt['firstStreamOpenTS'] is None:
                sControl_dt['firstStreamOpenTS'] = stream_openTime
            #[3-2]: Check If All Targets Received Their First Stream
            if not any(sControl[t]['firstStreamOpenTS'] is None for t in ('kline', 'depth', 'aggTrade')):
                acs = self.__availabilityChecks
                mc  = self.__memCtrl
                fsoTS_min      = min(sControl[t]['firstStreamOpenTS'] for t in ('kline', 'depth', 'aggTrade'))
                fetchBegTS_min = None
                for iID, mc_iID in mc.items():
                    mca   = mc_iID['minCompleteAnalysis']
                    mmdrl = mc_iID['maxMarketDataReferenceLength']
                    fsoTS_min_agg = func_gnitt(intervalID = iID, timestamp = fsoTS_min,     nTicks = 0)
                    fetchBegTS    = func_gnitt(intervalID = iID, timestamp = fsoTS_min_agg, nTicks = -(mca+mmdrl-1))
                    if fetchBegTS_min is None or fetchBegTS < fetchBegTS_min: fetchBegTS_min = fetchBegTS
                for t in ('kline', 'depth', 'aggTrade'):
                    fsoTS = sControl[t]['firstStreamOpenTS']
                    acs[t].append((fetchBegTS_min, fsoTS-1))
                if self.__checkDataAvailable(): self.__updateStatus(status = STATUS_QUEUED)
                else:                           self.__updateStatus(status = STATUS_WAITINGDATAAVAILABLE)

        #[4]: Stream Continuity Check
        discontinuity = _STREAMCONTINUITY_NORMAL
        if sControl_dt['lastStream'] is not None:
            ls_openTS, ls_closed = sControl_dt['lastStream']
            nextOpenTS = func_gnitt(intervalID = KLINTERVAL, timestamp = ls_openTS, nTicks = 1)
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
                if self.__status not in (STATUS_WAITINGNEURALNETWORK, STATUS_WAITINGSTREAM):
                    self.__updateStatus(status = STATUS_WAITINGDATAAVAILABLE)
                        
        #[5]: Data Record
        if discontinuity != _STREAMCONTINUITY_REVERSE:
            #[5-1]: Last Stream Record
            sControl_dt['lastStream'] = (stream_openTime, stream_closed)
            #[5-2]: Raw Data Record
            dRaw_target     = self.__data_raw[target]
            dTSs_raw_target = self.__data_timestamps['raw'][target]
            if stream_openTime not in dRaw_target:
                dTSs_raw_target.append(stream_openTime)
            dRaw_target[stream_openTime] = stream
            #[5-3]: Aggregation Queue
            if self.__status == STATUS_ANALYZING and discontinuity == _STREAMCONTINUITY_NORMAL:
                self.__aggregateData(target = target)

    def __checkDataAvailable(self):
        #[1]: Currency Data
        cInfo = self.__currencyInfo
        if cInfo == _IPC_PRD_INVALIDADDRESS or not cInfo: 
            return

        #[2]: Availability Check
        for target in ('kline', 'depth', 'aggTrade'):
            aRanges = cInfo[f'{target}s_availableRanges']
            if not aRanges:
                return False
            for aCheck_beg, aCheck_end in self.__availabilityChecks[target]:
                if not any(((aRange[0] <= aCheck_beg) and (aCheck_end <= aRange[1])) for aRange in aRanges):
                    return False
                
        #[3]: Currency Information Check & Analysis Keyword Arguments Construction
        if not all(cInfo['precisions'][pType] is not None for pType in ('price', 'quantity', 'quote')):
            return False
        aParams_all = self.__analysisParams
        dAgg_all    = self.__data_agg
        aKwargs     = dict()
        for iID in aParams_all:
            dAgg_iID = dAgg_all[iID]
            aKwargs[iID] = {'intervalID':     iID,
                            'precisions':     cInfo['precisions'],
                            'klines':         dAgg_iID['kline'],
                            'depths':         dAgg_iID['depth'],
                            'aggTrades':      dAgg_iID['aggTrade'],
                            'neuralNetworks': self.__neuralNetworks}
        self.__analysisKwargs = aKwargs
                
        #[4]: If Reached Here, All Are Available. Return True.
        return True

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
        dRaw_target = self.__data_raw[target]
        dTSs_raw    = self.__data_timestamps['raw']
        dIdx_openTime = COMMONDATAINDEXES['openTime'][target]
        for dl in fr_data:
            dl_openTime = dl[dIdx_openTime]
            if dl_openTime not in dRaw_target:
                dTSs_raw[target].append(dl_openTime)
            dRaw_target[dl_openTime] = dl

        #[5]: Completion Check & Fetch Continuation
        fReq['complete']     = True
        fReq['fetchedRange'] = [fr_fetchRange[0], fr_fetchRange[1]]

        #[6]: Status Control
        if all(_fReq['complete'] for _fReq in self.__fetchRequests.values()): 
            for t in ('kline', 'depth', 'aggTrade'):
                dTSs_raw[t] = deque(sorted(dTSs_raw[t]))
            self.__fetchRequests.clear()
            self.__updateStatus(status = STATUS_INITIALANALYZING)

    def __aggregateData(self, target):
        #[1]: Instances
        cInfo       = self.__currencyInfo
        dRaw_target = self.__data_raw[target]
        dAgg        = self.__data_agg
        dTSs        = self.__data_timestamps
        dTSs_raw    = dTSs['raw']
        las         = self.__lastAggregated
        lcAggs      = self.__lastClosedAggregations
        aggregator  = self.__aggregators[target]
        aQueue      = self.__analysisQueue
        func_gnitt  = atmEta_Auxillaries.getNextIntervalTickTimestamp

        #[2]: Aggregation Begin Timestamp
        la = las[target]
        if la is None:
            aggBeg = dTSs_raw[target][0]
        else:
            la_openTS, la_closed = la
            if la_closed: aggBeg = func_gnitt(intervalID = KLINTERVAL, timestamp = la_openTS, nTicks = 1)
            else:         aggBeg = la_openTS

        #[3]: Aggregation
        dIdx_closed = COMMONDATAINDEXES['closed'][target]
        rawOpenTS   = aggBeg
        aggComplete = True
        count       = 0
        aggTSs      = []
        while rawOpenTS in dRaw_target:
            for iID in dAgg:
                #[3-1]: Instances
                dAgg_iID_target   = dAgg[iID][target]
                dTSs_iID_target   = dTSs[iID][target]
                lcAggs_iID_target = lcAggs[iID][target]
                dl_raw    = dRaw_target[rawOpenTS]
                aggOpenTS = func_gnitt(intervalID = iID, timestamp = rawOpenTS, nTicks = 0)

                #[3-2]: Aggregation
                if aggOpenTS not in dAgg_iID_target: dTSs_iID_target.append(aggOpenTS)
                aggregator(dataRaw        = dRaw_target,
                           dataAgg        = dAgg_iID_target,
                           lastClosedAggs = lcAggs_iID_target,
                           rawOpenTS      = rawOpenTS,
                           aggOpenTS      = aggOpenTS,
                           aggIntervalID  = iID,
                           precisions     = cInfo['precisions'])

                #[3-3]: Count Update
                count += 1

            #[3-5]: Tracker Update
            aggTSs.append(rawOpenTS)
            la        = (rawOpenTS, dl_raw[dIdx_closed])
            rawOpenTS = func_gnitt(intervalID = KLINTERVAL, timestamp = rawOpenTS, nTicks = 1)

            #[3-6]: Count Check
            if _AGGREGATIONCHUNKSIZE <= count:
                if rawOpenTS in dRaw_target: 
                    aggComplete = False
                break
        las[target] = la

        #[4]: Analysis Queue Update
        lastQueuedRawTS = self.__lastQueuedRawTS
        for aggTS in aggTSs:
            if lastQueuedRawTS is None:
                if all(las[t] is not None for t in ('kline', 'depth', 'aggTrade')):
                    targetTS = max(dTSs_raw[t][0] for t in ('kline', 'depth', 'aggTrade'))
                    while targetTS <= aggTS:
                        aQueue.append(targetTS)
                        lastQueuedRawTS = targetTS
                        targetTS = func_gnitt(intervalID = KLINTERVAL, timestamp = targetTS, nTicks = 1)
            else:
                lastAggTS_min = min(las[t][0] for t in ('kline', 'depth', 'aggTrade'))
                if aggTS <= lastAggTS_min and (not aQueue or aQueue[-1] != aggTS):
                    aQueue.append(aggTS)
                    lastQueuedRawTS = aggTS
                else:
                    break
        self.__lastQueuedRawTS = lastQueuedRawTS

        #[5]: Return Aggregation Completion
        return aggComplete

    def __analyzeData(self):
        #[1]: Instances
        dRaw       = self.__data_raw
        dAgg       = self.__data_agg
        dTSs       = self.__data_timestamps
        dTSs_raw   = dTSs['raw']
        aParams    = self.__analysisParams
        atp_sorted = self.__analysisToProcess_sorted
        aKwargs    = self.__analysisKwargs
        aQueue     = self.__analysisQueue
        caCode     = self.__currencyAnalysisCode
        subs       = self.__subscribers
        func_aGen      = atmEta_Analyzers.analysisGenerator
        func_gnitt     = atmEta_Auxillaries.getNextIntervalTickTimestamp
        func_lAnalysis = atmEta_Analyzers.linearizeAnalysis
        func_sendFAR   = self.ipcA.sendFAR

        #[2]: Analysis
        count        = 0
        aTime_beg_ns = time.perf_counter_ns()
        while aQueue:
            #[2-1]: Queue
            aTargetTS = aQueue.popleft()

            #[2-2]: Analysis Generation
            bdRawTS_remove_min = None
            for iID in dAgg:
                #[2-2-1]: Instances
                aggTS = func_gnitt(intervalID = iID, timestamp = aTargetTS, nTicks = 0)
                dAgg_iID       = dAgg[iID]
                dTSs_iID       = dTSs[iID]
                aParams_iID    = aParams[iID]
                atp_sorted_iID = atp_sorted[iID]
                aKwargs_iID    = aKwargs[iID]

                #[2-2-2]: Analysis Generation
                nAR_keeps    = dict()
                nBD_keep_max = 1
                for aType, aCode in atp_sorted_iID:
                    dAgg_iID_aCode = dAgg_iID[aCode]
                    dTSs_iID_aCode = dTSs_iID[aCode]
                    if aggTS not in dAgg_iID_aCode:
                        dTSs_iID_aCode.append(aggTS)
                    nAR_keep, nBD_keep = func_aGen(analysisType    = aType,
                                                   timestamp       = aggTS,
                                                   analysisResults = dAgg_iID[aCode],
                                                   **aKwargs_iID,
                                                   **aParams_iID[aCode])
                    nAR_keeps[aCode] = nAR_keep+1 #Add 1 For Re-Analysis
                    if nBD_keep_max < nBD_keep: nBD_keep_max = nBD_keep
                nBD_keep_max += 1 #Add 1 For Re-Analysis
                    
                #[2-2-3]: Memory Optimization (Analysis & Aggregated Base Data)
                #---[2-2-3-1]: Analysis
                for aCode, nAr_keep in nAR_keeps.items():
                    arTS_remove_min = func_gnitt(intervalID = iID, timestamp = aggTS, nTicks = -(nAr_keep-1))-1
                    dAgg_iID_aCode  = dAgg_iID[aCode]
                    dTSs_iID_aCode  = dTSs_iID[aCode]
                    ts_remove       = dTSs_iID_aCode[0]
                    while ts_remove <= arTS_remove_min:
                        dTSs_iID_aCode.popleft()
                        del dAgg_iID_aCode[ts_remove]
                        ts_remove = dTSs_iID_aCode[0]
                #---[2-2-3-2]: Base Data
                bdTS_remove_min = func_gnitt(intervalID = iID, timestamp = aggTS, nTicks = -(nBD_keep_max-1))-1
                for target in ('kline', 'depth', 'aggTrade'):
                    dAgg_iID_target = dAgg_iID[target]
                    dTSs_iID_target = dTSs_iID[target]
                    ts_remove       = dTSs_iID_target[0]
                    while ts_remove <= bdTS_remove_min:
                        dTSs_iID_target.popleft()
                        del dAgg_iID_target[ts_remove]
                        ts_remove = dTSs_iID_target[0]
                if bdRawTS_remove_min is None or bdTS_remove_min < bdRawTS_remove_min: bdRawTS_remove_min = bdTS_remove_min
                
            #[2-3]: Memory Optimization (Raw Base Data)
            for target in ('kline', 'depth', 'aggTrade'):
                dRaw_target     = dRaw[target]
                dTSs_raw_target = dTSs_raw[target]
                ts_remove       = dTSs_raw_target[0]
                while ts_remove <= bdRawTS_remove_min:
                    dTSs_raw_target.popleft()
                    del dRaw_target[ts_remove]
                    ts_remove = dTSs_raw_target[0]

            #[2-4]: Analysis Result Linearization & Dispatch
            aLinearized = func_lAnalysis(dataRaw        = dRaw,
                                         dataAggregated = dAgg, 
                                         analysisPairs  = atp_sorted, 
                                         timestamp      = aTargetTS)
            func_sendFAR(targetProcess  = 'TRADEMANAGER', 
                         functionID     = 'onAnalysisGeneration', 
                         functionParams = {'currencyAnalysisCode': caCode,
                                           'linearizedAnalysis':   aLinearized}, 
                         farrHandler    = None)

            #[2-6]: Analysis Dispatch
            for dRecv, lastReceived in subs:
                dAgg_copy = {iID: {target: dict() for target in ('kline', 'depth', 'aggTrade')} for iID in dAgg}
                """
                while lastReceived is None or lastReceived <= aTargetTS:
                    if lastReceived is None:
                        pass
                    for iID, dAgg_iID in dAgg.items():
                        pass

                    lastReceived = func_gnitt(intervalID = iID, timestamp = aggTS, nTicks = -(nBD_keep_max-1))-1

                func_sendFAR(targetProcess  = 'GUI', 
                             functionID     = dRecv, 
                             functionParams = {'currencyAnalysisCode': caCode, 
                                               'data':                 dAgg_copy}, 
                             farrHandler    = None)
                """
                    
            #[2-7] Count Update
            count += 1
            if count == _ANALYSISCHUNKSIZE:
                break
        aTime_end_ns = time.perf_counter_ns()
        if count: aGenTime_ns = (aTime_end_ns-aTime_beg_ns)/count
        else:     aGenTime_ns = None

        #[5]: Return If Analysis Queue Is Empty
        return (not aQueue, aGenTime_ns)

    def __updateStatus(self, status):
        self.__status = status
        self.ipcA.sendFAR(targetProcess  = 'TRADEMANAGER', 
                          functionID     = 'onCurrencyAnalysisStatusUpdate', 
                          functionParams = {'currencyAnalysisCode': self.__currencyAnalysisCode, 
                                            'newStatus':            status}, 
                          farrHandler    = None)
























    def __performAnalysisOnKline(self, currencyAnalysisCode, klineOpenTS):
        _ca = self.__currencyAnalysis[currencyAnalysisCode]
        if (_ca['kline_firstAnalyzedOpenTS'] is None): _ca['kline_firstAnalyzedOpenTS'] = klineOpenTS
        #Perform analysis
        nKlinesToKeep_max = 0
        expiredAnalysisOpenTS_nToDisplay = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = klineOpenTS, nTicks = -_ca['nKlines_toDisplay'])
        for aType, aCode in _ca['analysisToProcess_sorted']:
            #---Analysis Generation
            nAnalysisToKeep, nKlinesToKeep = atmEta_Analyzers.analysisGenerator(analysisType   = aType,
                                                                                klineAccess    = _ca['klines'],
                                                                                intervalID     = KLINTERVAL,
                                                                                mrktRegTS      = _ca['marketRegistrationTS'],
                                                                                precisions     = _ca['precisions'],
                                                                                timestamp      = klineOpenTS,
                                                                                neuralNetworks = self.__neuralNetworks,
                                                                                bidsAndAsks    = _ca['bidsAndAsks'],
                                                                                aggTrades      = _ca['aggTrades'],
                                                                                **_ca['analysisParams'][aCode])
            
            #---Update Optimization Variables
            nKlinesToKeep_max = max(nKlinesToKeep_max, nKlinesToKeep, _ca['neuralNetworkMaxKlinesRefLen'])
            #---Memory Optimization (Analysis)
            expiredAnalysisOpenTS_nAnalysisToKeep = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = klineOpenTS, nTicks = -(nAnalysisToKeep+1))
            if (expiredAnalysisOpenTS_nAnalysisToKeep < expiredAnalysisOpenTS_nToDisplay): expiredKlineOpenTS_effective = expiredAnalysisOpenTS_nAnalysisToKeep
            else:                                                                          expiredKlineOpenTS_effective = expiredAnalysisOpenTS_nToDisplay
            if (_ca['kline_firstAnalyzedOpenTS'] <= expiredKlineOpenTS_effective):
                if (_ca['klines_lastRemovedOpenTS'][aCode] == None): tsRemovalRange_beg = _ca['kline_firstAnalyzedOpenTS']
                else:                                                tsRemovalRange_beg = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = _ca['klines_lastRemovedOpenTS'][analysisCode], nTicks = 1)
                for _ts in atmEta_Auxillaries.getTimestampList_byRange(intervalID = KLINTERVAL, timestamp_beg = tsRemovalRange_beg, timestamp_end = expiredKlineOpenTS_effective, mrktReg = _ca['marketRegistrationTS'], lastTickInclusive = True): del _ca['klines'][analysisCode][_ts]
                _ca['klines_lastRemovedOpenTS'][aCode] = expiredKlineOpenTS_effective
        #---Memory Optimization (Kline Raw, Kline Raw_Status)
        expiredAnalysisOpenTS_nKlinesToKeep = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = klineOpenTS, nTicks = -(nKlinesToKeep_max+1))
        expiredKlineOpenTS_effective = min(expiredAnalysisOpenTS_nKlinesToKeep, expiredAnalysisOpenTS_nToDisplay)
        if (_ca['kline_firstAnalyzedOpenTS'] <= expiredKlineOpenTS_effective):
            if (_ca['klines_lastRemovedOpenTS']['raw'] == None): tsRemovalRange_beg = _ca['kline_firstAnalyzedOpenTS']
            else:                                                tsRemovalRange_beg = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = _ca['marketRegistrationTS'], timestamp = _ca['klines_lastRemovedOpenTS']['raw'], nTicks = 1)
            for _ts in atmEta_Auxillaries.getTimestampList_byRange(intervalID = KLINTERVAL, timestamp_beg = tsRemovalRange_beg, timestamp_end = expiredKlineOpenTS_effective, mrktReg = _ca['marketRegistrationTS'], lastTickInclusive = True):
                del _ca['klines']['raw'][_ts]
                del _ca['klines']['raw_status'][_ts]
            _ca['klines_lastRemovedOpenTS']['raw'] = expiredKlineOpenTS_effective

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

    def onKlineStreamReceival(self, kline):
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

    def onDepthStreamReceival(self, depth):
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

    def onAggTradeStreamReceival(self, aggTrade):
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