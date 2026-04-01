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
    def __init__(self, ipcA, currencyAnalysisCode, currencySymbol, currencyAnalysisConfigurationCode, currencyAnalysisConfiguration):
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
        self.__neuralNetworks           = dict()
        self.__neuralNetworks_rIDs      = dict()
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
        func_ccapfcac = atmEta_Analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration
        func_filrts   = atmEta_Auxillaries.formatInvalidLinesReportToString
        aParams_all  = dict()
        invalidFound = False
        iIDs_empty   = set()
        for iID, cac_iID in cac_all.items():
            aParams_iID, invalidLines = func_ccapfcac(cac_iID)
            if invalidLines:
                invalidFound = True
                invalidLines_str = func_filrts(invalidLines = invalidLines)
                print(termcolor.colored((f"[ANALYZER{self.analyzerIndex}] Invalid Lines Detected In Interval '{iID}' While Attempting To Add Currency Analysis."+invalidLines_str), 'light_red'))
            elif aParams_iID:
                aParams_all[iID] = aParams_iID
            else:
                iIDs_empty.add(iID)
        self.__analysisParams = aParams_all
        if invalidFound:
            self.__updateStatus(status = STATUS_ERROR)
        for iID_empty in iIDs_empty:
            del cac_all[iID_empty]

        #[2]: Analysis To Process Sorted
        aGenOrder = atmEta_Analyzers.ANALYSIS_GENERATIONORDER
        atp_sorted_all = dict()
        for iID, aParams_iID in aParams_all.items():
            atp_sorted_iID = []
            for aType in aGenOrder:
                atp_sorted_iID += [(aType, aCode) for aCode in aParams_iID if aCode[:len(aType)] == aType]
            atp_sorted_all[iID] = atp_sorted_iID
        self.__analysisToProcess_sorted = atp_sorted_all

        #[3]: Data Containers
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

        #[4]: Neural Network Codes
        nns      = dict()
        nns_rIDs = dict()
        func_sendFAR = self.ipcA.sendFAR
        func_onncdrr = self.__farr_onNeuralNetworkConnectionsDataRequestResponse
        for cac_iID in cac_all.values():
            if not cac_iID['NNA_Master']:
                continue
            for lIdx in range (atmEta_Constants.NLINES_NNA):
                lActive = cac_iID.get(f'NNA_{lIdx}_LineActive', False)
                if not lActive: continue
                nnCode = cac_iID[f'NNA_{lIdx}_NeuralNetworkCode']
                nns[nnCode] = None
        if nns and self.__status != STATUS_ERROR:
            for nnCode in nns:
                rID = func_sendFAR(targetProcess  = "NEURALNETWORKMANAGER",
                                   functionID     = 'getNeuralNetworkConnections',
                                   functionParams = {'neuralNetworkCode': nnCode},
                                   farrHandler    = func_onncdrr)
                nns_rIDs[rID] = nnCode
            self.__updateStatus(status = STATUS_WAITINGNEURALNETWORK)
        self.__neuralNetworks      = nns
        self.__neuralNetworks_rIDs = nns_rIDs

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

    def getCurrencySymbol(self):
        return self.__currencySymbol

    def onCurrencyUpdate(self, currencyInfo):
        #[1]: Currency Info Update
        self.__currencyInfo = currencyInfo

        #[2]: If Waiting Data Available, Check Data Availability And Move to Queued Status If So.
        if self.__status == STATUS_WAITINGDATAAVAILABLE:
            if self.__checkDataAvailable():
                self.__updateStatus(status = STATUS_QUEUED)

    def __farr_onNeuralNetworkConnectionsDataRequestResponse(self, responder, requestID, functionResult):
        #[1]: Responder Check
        if responder != 'NEURALNETWORKMANAGER': return

        #[2]: Instances
        nns      = self.__neuralNetworks
        nns_rIDs = self.__neuralNetworks_rIDs
        mc       = self.__memCtrl
        neuralNetworkCode = functionResult['neuralNetworkCode']
        nKlines           = functionResult['nKlines']
        hiddenLayers      = functionResult['hiddenLayers']
        outputLayer       = functionResult['outputLayer']
        connections       = functionResult['connections']

        #[3]: Request ID Check
        if nns_rIDs.get(requestID, None) != neuralNetworkCode: 
            return

        #[4]: Fetch Success Check & Instance Generation
        if neuralNetworkCode is None:
            self.__updateStatus(status = STATUS_ERROR)
            return
        nn = atmEta_NeuralNetworks.neuralNetwork_MLP(nKlines      = nKlines, 
                                                     hiddenLayers = hiddenLayers, 
                                                     outputLayer  = outputLayer, 
                                                     device       = 'cpu')
        nn.importConnectionsData(connections = connections)
        nn.setEvaluationMode()
        nns[neuralNetworkCode] = nn

        #[5]: Check If All Neural Networks Are Ready
        if any(_nn is None for _nn in nns.values()):
            return
        
        #[6]: Target Intervals
        iIDs_applied = dict()
        for iID, aParams_iID in self.__analysisParams.items():
            for aCode, aParams_iID_aCode in aParams_iID.items():
                if not aCode.startswith('NNA'): continue
                nnCode = aParams_iID_aCode['nnCode']
                if nnCode not in iIDs_applied: 
                    iIDs_applied[nnCode] = set()
                iIDs_applied[nnCode].add(iID)

        #[7]: Update Maximum Market Data Reference Length
        for nnCode, iIDs in iIDs_applied.items():
            nn_refLen = nns[nnCode].getNKlines()
            for iID in iIDs:
                mc_iID = mc[iID]
                mc_iID['maxMarketDataReferenceLength'] = max(mc_iID['maxMarketDataReferenceLength'], nn_refLen)

        #[8]: Status Update
        self.__updateStatus(status = STATUS_WAITINGSTREAM)

    def addSubscriber(self, subscriber):
        #[1]: Instance
        subs = self.__subscribers

        #[2]: Subscriber Update
        subs[subscriber] = None
        
        #[3]: Analysis Parameters Return
        return {'currencyAnalysisCode': self.__currencyAnalysisCode,
                'analysisParams':       self.__analysisParams}

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
        #[1]: State Reset
        self.__data_raw               = {target: dict()  for target in ('kline', 'depth', 'aggTrade')}
        self.__data_agg               = dict()
        self.__data_timestamps        = {'raw': {target: deque() for target in ('kline', 'depth', 'aggTrade')}}
        self.__stream                 = {target: {'firstStreamOpenTS': None, 'lastStream': None} for target in ('kline', 'depth', 'aggTrade')}
        self.__availabilityChecks     = {target: [] for target in ('kline', 'depth', 'aggTrade')}
        self.__fetchRequests          = dict()
        self.__lastAggregated         = {target: None for target in ('kline', 'depth', 'aggTrade')}
        self.__lastClosedAggregations = dict()
        self.__analysisQueue          = deque()
        self.__lastQueuedRawTS        = None
        self.__subscribers            = {dRecv: None for dRecv in self.__subscribers}
        self.__updateStatus(status = STATUS_WAITINGSTREAM)

        #[2]: Analysis Control Re-initialization
        self.__initializeAnalysisControl(currencyAnalysisConfiguration = currencyAnalysisConfiguration)

        #[3]: Subscriber Notification
        func_sendFAR = self.ipcA.sendFAR
        for dRecv in self.__subscribers:
            func_sendFAR(targetProcess  = 'GUI',
                         functionID     = dRecv,
                         functionParams = {'currencyAnalysisCode': self.__currencyAnalysisCode,
                                           'data_agg':             None},
                         farrHandler    = None)

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
        mc         = self.__memCtrl
        func_aGen      = atmEta_Analyzers.analysisGenerator
        func_gnitt     = atmEta_Auxillaries.getNextIntervalTickTimestamp
        func_lAnalysis = atmEta_Analyzers.linearizeAnalysis
        func_sendFAR   = self.ipcA.sendFAR

        #[2]: Analysis
        count        = 0
        aTargetTS    = None
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
                mc_iID_adl     = mc[iID]['analysisDisplayLength']

                #[2-2-2]: Analysis Generation
                nAR_keeps    = dict()
                nBD_keep_max = mc_iID_adl
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
                    nAR_keeps[aCode] = max(mc_iID_adl, nAR_keep)+1 #Add 1 For Re-Analysis
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
                    
            #[2-5] Count Update
            count += 1
            if count == _ANALYSISCHUNKSIZE:
                break
        aTime_end_ns = time.perf_counter_ns()
        if count: aGenTime_ns = (aTime_end_ns-aTime_beg_ns)/count
        else:     aGenTime_ns = None

        #[3]: Analysis Dispatch
        if aTargetTS is not None:
            for dRecv, lastReceived in subs.items():
                #[3-1]: Dispatch Data Formatting
                dAgg_copy = {iID: {target: dict() for target in ('kline', 'depth', 'aggTrade')} for iID in dAgg}
                for iID in dAgg:
                    dAgg_copy_iID = dAgg_copy[iID]
                    for aCode in aParams[iID]:
                        dAgg_copy_iID[aCode] = dict()

                #[3-2]: Data Collection
                for iID in dAgg:
                    dAgg_iID      = dAgg[iID]
                    dTSs_iID      = dTSs[iID]
                    dAgg_copy_iID = dAgg_copy[iID]
                    mc_iID_adl    = mc[iID]['analysisDisplayLength']
                    adlTS         = func_gnitt(intervalID = iID, timestamp = aTargetTS, nTicks = -(mc_iID_adl-1))
                    for target in ('kline', 'depth', 'aggTrade') + tuple(aParams[iID]):
                        dAgg_iID_target      = dAgg_iID[target]
                        dTSs_iID_target      = dTSs_iID[target]
                        dAgg_copy_iID_target = dAgg_copy_iID[target]
                        if lastReceived is None:
                            for dTS in dTSs_iID_target:
                                data = dAgg_iID_target.get(dTS, None)
                                if dTS < adlTS or data is None:
                                    continue
                                dAgg_copy_iID_target[dTS] = data
                                if aTargetTS < dTS:
                                    break
                        else:
                            dTS = func_gnitt(intervalID = iID, timestamp = lastReceived, nTicks = 0)
                            while dTS <= aTargetTS:
                                data = dAgg_iID_target.get(dTS, None)
                                if adlTS <= dTS and data is not None:
                                    dAgg_copy_iID_target[dTS] = data
                                dTS = func_gnitt(intervalID = iID, timestamp = dTS, nTicks = 1)
                subs[dRecv] = aTargetTS

                #[3-3]: Data Dispatch
                func_sendFAR(targetProcess  = 'GUI', 
                             functionID     = dRecv, 
                             functionParams = {'currencyAnalysisCode': caCode, 
                                               'data_agg':             dAgg_copy}, 
                             farrHandler    = None)

        #[4]: Return If Analysis Queue Is Empty
        return (not aQueue, aGenTime_ns)

    def __updateStatus(self, status):
        self.__status = status
        self.ipcA.sendFAR(targetProcess  = 'TRADEMANAGER', 
                          functionID     = 'onCurrencyAnalysisStatusUpdate', 
                          functionParams = {'currencyAnalysisCode': self.__currencyAnalysisCode, 
                                            'newStatus':            status}, 
                          farrHandler    = None)