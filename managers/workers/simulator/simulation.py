#ATM Modules
import ipc
import analyzers
import auxiliaries
import auxiliaries_trade
import neural_networks
import constants
import teffunctions

#Python Modules
import time
import termcolor
import math
import json
import os
import traceback
import numpy
from collections import deque

#Constants
_IPC_THREADTYPE_MT         = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT         = ipc._THREADTYPE_AT
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

KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S

_DUMMYFRAMES = {'kline':    (None, None, None, None, None, None, None, None, None,                   True, FORMATTEDDATATYPE_DUMMY),
                'depth':    (None, None, None, None, None, None, None, None, None, None, None, None, True, FORMATTEDDATATYPE_DUMMY),
                'aggTrade': (None, None, None, None, None, None,                                     True, FORMATTEDDATATYPE_DUMMY)}

_FETCHCHUNKSIZE    = 1440
_PROCESSTIMEOUT_NS = 100e6

_MARKETTRADINGFEE          = 0.0005
_BASEASSETALLOCATABLERATIO = 0.95
_ASSETPRECISIONS = {'USDT': 8,
                    'USDC': 8}

KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S

PERIODICREPORT_INTERVALID = auxiliaries.KLINE_INTERVAL_ID_1h

class Simulation:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, simulatorIndex, ipcA, simulationCode, simulationRange, analysisExport, assets, positions, currencyAnalysisConfigurations, tradeConfigurations, creationTime):
        #[1]: Instances
        self.path_project   = path_project
        self.simulatorIndex = simulatorIndex
        self.ipcA           = ipcA

        #[2]: Simulation Variables
        #---[2-1]: Defining Parameters
        self.__simulationCode                 = simulationCode
        self.__simulationRange                = (auxiliaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = simulationRange[0], nTicks = 0),
                                                 auxiliaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = simulationRange[1], nTicks = 1)-1)
        self.__analysisExport                 = analysisExport
        self.__assets_def                     = assets
        self.__positions_def                  = positions
        self.__currencyAnalysisConfigurations = currencyAnalysisConfigurations
        self.__tradeConfigurations            = tradeConfigurations
        self.__creationTime                   = creationTime

        #---[2-2]: Simulation Control
        self.__assets    = None
        self.__positions = None

        #---[2-3]: Data Control
        self.__data_raw            = dict()
        self.__data_agg            = dict()
        self.__data_timestamps     = dict()
        self.__data_nextFetchPoint = None
        self.__data_fetchRIDs      = dict()
        self.__data_fetchGroups    = dict()
        self.__data_lastPrepared   = None
        self.__aggregators         = {'kline':    analyzers.aggregator_kline,
                                      'depth':    analyzers.aggregator_depth,
                                      'aggTrade': analyzers.aggregator_aggTrade}
        self.__lastClosedAggregations            = dict()
        self.__lastClosedAggregations_timestamps = dict()

        #---[2-4]: Analysis Control
        self.__analyzers           = None
        self.__analysisKwargs      = None
        self.__neuralNetworks      = dict()
        self.__neuralNetworks_rIDs = dict()

        #---[2-5]: Simulation Results
        self.__tradeLogs         = list()
        self.__periodicReports   = dict()
        self.__simulationSummary = None

        #---[2-6]: State Control
        self.__status             = 'QUEUED'
        self.__procStatus         = None
        self.__completion         = None
        self.__nextAnalysisTarget = None
        self.__lastAnalysisTarget = auxiliaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = simulationRange[1], nTicks = 0)
        self.__errorMsg           = None

    def start(self):
        #[1]: Analysis Parameters & Analysis To Process Sorted
        cacs          = self.__currencyAnalysisConfigurations
        func_ccapfcac = analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration
        func_filrts   = auxiliaries.formatInvalidLinesReportToString
        aGenOrder     = analyzers.ANALYSIS_GENERATIONORDER
        simAnalyzers  = dict()
        invalidFound = False
        emptyConfigs = set()
        for cacCode, cac_all in cacs.items():
            aParams_all    = dict()
            atp_sorted_all = dict()
            for iID, cac_iID in cac_all.items():
                aParams_iID, invalidLines = func_ccapfcac(currencyAnalysisConfiguration = cac_iID)
                if invalidLines:
                    invalidFound = True
                    invalidLines_str = func_filrts(invalidLines = invalidLines)
                    print(termcolor.colored((f"[SIMULATOR{self.simulatorIndex}] Invalid Lines Detected In Interval '{iID}' While Attempting To Add Currency Analysis '{cacCode}'."+invalidLines_str), 'light_red'))
                elif aParams_iID:
                    atp_sorted_iID = []
                    for aType in aGenOrder: 
                        atp_sorted_iID.extend([(aType, aCode) for aCode in aParams_iID if aCode.startswith(aType)])
                    aParams_all[iID]    = aParams_iID
                    atp_sorted_all[iID] = atp_sorted_iID
                else:
                    emptyConfigs.add((cacCode, iID))
            if aParams_all:
                simAnalyzers[cacCode] = {'analysisParams':           aParams_all,
                                         'analysisToProcess_sorted': atp_sorted_all}
        if invalidFound:
            self.__raiseSimulationError(errorCause = 'INVALIDCURRENCYANALYSISCONFIGURATION')
            return
        for cacCode_empty, iID_empty in emptyConfigs:
            del cacs[cacCode_empty][iID_empty]
            if not cacs[cacCode_empty]:
                del cacs[cacCode_empty]
        self.__analyzers = simAnalyzers

        #[2]: Data Containers
        dRaw = self.__data_raw
        dAgg = self.__data_agg
        dTSs = self.__data_timestamps
        lcas = self.__lastClosedAggregations
        lTSs = self.__lastClosedAggregations_timestamps
        for symbol, position_def in self.__positions_def.items():
            cacCode = position_def['currencyAnalysisConfigurationCode']
            dRaw[symbol] = {target: dict() for target in ('kline', 'depth', 'aggTrade')}
            dAgg[symbol] = dict()
            dTSs[symbol] = {'raw': {target: deque() for target in ('kline', 'depth', 'aggTrade')}}
            lcas[symbol] = dict()
            lTSs[symbol] = dict()
            dAgg_symbol = dAgg[symbol]
            dTSs_symbol = dTSs[symbol]
            lcas_symbol = lcas[symbol]
            lTSs_symbol = lTSs[symbol]
            for iID, aParams_iID in simAnalyzers[cacCode]['analysisParams'].items():
                dAgg_symbol[iID] = {target: dict()  for target in ('kline', 'depth', 'aggTrade')}
                dTSs_symbol[iID] = {target: deque() for target in ('kline', 'depth', 'aggTrade')}
                lcas_symbol[iID] = {target: dict()  for target in ('kline', 'depth', 'aggTrade')}
                lTSs_symbol[iID] = {target: deque() for target in ('kline', 'depth', 'aggTrade')}
                dAgg_symbol_iID = dAgg_symbol[iID]
                dTSs_symbol_iID = dTSs_symbol[iID]
                for aCode in aParams_iID:
                    dAgg_symbol_iID[aCode] = dict()
                    dTSs_symbol_iID[aCode] = deque()

        #[3]: Analysis Keyword Arguments Construction
        aKwargs = dict()
        for symbol, position_def in self.__positions_def.items():
            precisions     = position_def['precisions']
            aParams        = simAnalyzers[position_def['currencyAnalysisConfigurationCode']]['analysisParams']
            dAgg_symbol    = dAgg[symbol]
            aKwargs_symbol = dict()
            for iID in aParams:
                dAgg_symbol_iID = dAgg_symbol[iID]
                aKwargs_symbol[iID] = {'intervalID':     iID,
                                       'precisions':     precisions,
                                       'klines':         dAgg_symbol_iID['kline'],
                                       'depths':         dAgg_symbol_iID['depth'],
                                       'aggTrades':      dAgg_symbol_iID['aggTrade'],
                                       'neuralNetworks': self.__neuralNetworks}
            aKwargs[symbol] = aKwargs_symbol
        self.__analysisKwargs = aKwargs
        
        #[4]: Format Assets
        sc_assets = dict()
        for assetName, asset in self.__assets_def.items():
            iwb = asset['initialWalletBalance']
            sc_assets[assetName] = {'marginBalance':                 iwb,
                                    'walletBalance':                 iwb,
                                    'isolatedWalletBalance':         0,
                                    'isolatedPositionInitialMargin': 0,
                                    'crossWalletBalance':            iwb,
                                    'openOrderInitialMargin':        0,
                                    'crossPositionInitialMargin':    0,
                                    'crossMaintenanceMargin':        0, 
                                    'unrealizedPNL':                 0,
                                    'isolatedUnrealizedPNL':         0,
                                    'crossUnrealizedPNL':            0,
                                    'availableBalance':              iwb,
                                    #Positional Distribution
                                    'allocatableBalance': 0,
                                    'allocatedBalance':   0,
                                    #Risk Management
                                    'commitmentRate': None,
                                    'riskLevel':      None,
                                    #Result Summary Computation
                                    'WBTA': {'count':                0,
                                             'sum_x':                0,
                                             'sum_xx':               0,
                                             'sum_y':                0,
                                             'sum_yy':               0,
                                             'sum_xy':               0,
                                             'initialWalletBalance': iwb,
                                             'minimumWalletBalance': iwb,
                                             'maximumWalletBalance': iwb,
                                             'finalWalletBalance':   iwb,
                                             'firstUpdatedTS':       None},
                                   }
        self.__assets = sc_assets

        #[5]: Format Positions
        sc_positions = dict()
        sRange       = self.__simulationRange
        func_gnitt   = auxiliaries.getNextIntervalTickTimestamp
        for symbol, position_def in self.__positions_def.items():
            drs_min = None
            drs_max = None
            for t in ('kline', 'depth', 'aggTrade'):
                drs_t       = position_def['dataRanges'][t]
                drs_t_inSim = [dr for dr in drs_t if sRange[0] <= dr[1] and dr[0] <= sRange[1]] if drs_t else []
                if not drs_t_inSim:
                    continue
                drs_t_inSim_min = drs_t_inSim[0][0]
                drs_t_inSim_max = drs_t_inSim[-1][1]
                if drs_min is None or drs_t_inSim_min < drs_min: drs_min = drs_t_inSim_min
                if drs_max is None or drs_max < drs_t_inSim_max: drs_max = drs_t_inSim_max
            if drs_min is None or drs_max is None:
                gr = None
            else:
                gr = (func_gnitt(intervalID = KLINTERVAL, timestamp = max(drs_min, sRange[0]), nTicks = 0),
                      func_gnitt(intervalID = KLINTERVAL, timestamp = min(drs_max, sRange[1]), nTicks = 1)-1)
            sc_position = {#Base
                           'quantity':                0,
                           'entryPrice':              None,
                           'isolatedWalletBalance':   0,
                           'positionInitialMargin':   0,
                           'openOrderInitialMargin':  0,
                           'maintenanceMargin':       0,
                           'currentPrice':            None,
                           'unrealizedPNL':           None,
                           'liquidationPrice':        None,
                           #Positional Distribution
                           'allocatedBalance': 0,
                           #Risk Management
                           'commitmentRate': None,
                           'riskLevel':      None,
                           #Trade Control
                           'tradeControlTracker': {'slExited':   None,
                                                   'teff_model': dict()},
                           #Generation Range
                           'GR': gr,
                           #Analysis Export
                           'AE': {'indexIdentifier':        None,
                                  'linearizedAnalysisKeys': None,
                                  'data':                   list()}
                          }
            sc_positions[symbol] = sc_position
        self.__positions = sc_positions

        #[6]: Status & Completion Update
        self.__updateStatus(status = 'PROCESSING')
        self.__updateCompletion(completion = 0)
        self.__procStatus = 'PROCESSING'
        
        #[7]: Neural Networks Connections Data Request
        nns      = self.__neuralNetworks
        nns_rIDs = self.__neuralNetworks_rIDs
        func_sendFAR = self.ipcA.sendFAR
        func_onncdrr = self.__farr_onNeuralNetworkConnectionsDataRequestResponse
        for cac_all in cacs.values():
            for iID, cac_iID in cac_all.items():
                if not cac_iID['NNA_Master']:
                    continue
                for lIdx in range (constants.NLINES_NNA):
                    lActive = cac_iID.get(f'NNA_{lIdx}_LineActive', False)
                    if not lActive: continue
                    nnCode = cac_iID[f'NNA_{lIdx}_NeuralNetworkCode']
                    nns[nnCode] = None
        if nns:
            for nnCode in nns:
                rID = func_sendFAR(targetProcess  = "NEURALNETWORKMANAGER",
                                   functionID     = 'getNeuralNetworkConnections',
                                   functionParams = {'neuralNetworkCode': nnCode},
                                   farrHandler    = func_onncdrr)
                nns_rIDs[rID] = nnCode
            self.__procStatus = 'WAITINGNNCONNECTIONSDATA'
            return

        #[8]: Fetch Requests Dispatch & Analysis Target Set
        self.__sendMarketDataFetchRequests()
        self.__nextAnalysisTarget = self.__simulationRange[0]

    #State Control --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def getStatus(self):
        return self.__status
    
    def setActivation(self, activation):
        if activation: status_new = 'PROCESSING'
        else:          status_new = 'PAUSED'
        self.__updateStatus(status = status_new)
    
    def isProcessing(self):
        #[1]: Status Check
        if self.__status != 'PROCESSING' or self.__procStatus != 'PROCESSING':
            return False
        
        #[2]: Processing Readiness Check
        lp       = self.__data_lastPrepared
        naTarget = self.__nextAnalysisTarget
        if lp is None or naTarget is None or not naTarget <= lp:
            return False

        #[3]: All Checks Passed, Return True
        return True

    def __raiseSimulationError(self, errorCause):
        self.__updateStatus(status = 'ERROR')
        self.__errorMsg = errorCause
        
    def __updateStatus(self, status):
        #[1]: New Status Check & Update
        if self.__status == status:
            return
        self.__status = status

        #[2]: New Status Announcement
        self.ipcA.sendFAR(targetProcess  = 'SIMULATIONMANAGER', 
                          functionID     = 'onSimulationUpdate', 
                          functionParams = {'simulationCode': self.__simulationCode, 
                                            'updateType':     'STATUS', 
                                            'updatedValue':   status}, 
                          farrHandler    = None)
        if status == 'COMPLETED':
            self.ipcA.sendFAR(targetProcess  = 'SIMULATIONMANAGER', 
                              functionID     = 'onSimulationCompletion', 
                              functionParams = {'simulationCode':    self.__simulationCode, 
                                                'simulationSummary': self.__simulationSummary},
                              farrHandler    = None)

    def __updateCompletion(self, completion):
        self.__completion = completion
        self.ipcA.sendFAR(targetProcess  = 'SIMULATIONMANAGER', 
                          functionID     = 'onSimulationUpdate', 
                          functionParams = {'simulationCode': self.__simulationCode, 
                                            'updateType':     'COMPLETION', 
                                            'updatedValue':   self.__completion}, 
                          farrHandler    = None)
    #State Control END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    



    
    #IPCs -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __farr_onNeuralNetworkConnectionsDataRequestResponse(self, responder, requestID, functionResult):
        #[1]: Responder Check
        if responder != 'NEURALNETWORKMANAGER': return

        #[2]: Instances
        nns      = self.__neuralNetworks
        nns_rIDs = self.__neuralNetworks_rIDs
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
            self.__raiseSimulationError(errorCause = 'NEURALNETWORKCONNECTIONLOADERROR')
            return
        nn = neural_networks.neuralNetwork_MLP(nKlines      = nKlines, 
                                                     hiddenLayers = hiddenLayers, 
                                                     outputLayer  = outputLayer, 
                                                     device       = 'cpu')
        nn.importConnectionsData(connections = connections)
        nn.setEvaluationMode()
        nns[neuralNetworkCode] = nn

        #[5]: Check If All Neural Networks Are Ready
        if any(_nn is None for _nn in nns.values()):
            return

        #[6]: Status Update
        self.__updateStatus(status = 'PROCESSING')
        self.__procStatus = 'PROCESSING'

        #[7]: Fetch Requests Dispatch & Analysis Target Set
        self.__sendMarketDataFetchRequests()
        self.__nextAnalysisTarget = self.__simulationRange[0]

    def __sendMarketDataFetchRequests(self):
        #[1]: Instance
        sRange        = self.__simulationRange
        positions_def = self.__positions_def
        nfp           = self.__data_nextFetchPoint
        dfRIDs        = self.__data_fetchRIDs
        dfGroups      = self.__data_fetchGroups
        func_gnitt   = auxiliaries.getNextIntervalTickTimestamp
        func_sendFAR = self.ipcA.sendFAR
        func_odfr    = self.__farr_onDataFetchResponse

        #[2]: Fetch Range Determination
        if nfp is None:
            range_beg = sRange[0]
            range_end = func_gnitt(intervalID = KLINTERVAL, timestamp = range_beg, nTicks = _FETCHCHUNKSIZE*2)-1
            nfp_new   = func_gnitt(intervalID = KLINTERVAL, timestamp = range_beg, nTicks = _FETCHCHUNKSIZE)
        else:
            range_beg = func_gnitt(intervalID = KLINTERVAL, timestamp = nfp,       nTicks = _FETCHCHUNKSIZE)
            range_end = func_gnitt(intervalID = KLINTERVAL, timestamp = range_beg, nTicks = _FETCHCHUNKSIZE)-1
            nfp_new   = range_beg
        if nfp_new <= sRange[1]:
            self.__data_nextFetchPoint = nfp_new
        else:
            self.__data_nextFetchPoint = None
        range_end = min(range_end, sRange[1])

        #[3]: Fetch Request Dispatch
        dfGroup_rIDs = set()
        for symbol, position_def in positions_def.items():
            for target in ('kline', 'depth', 'aggTrade'):
                #[3-1]: Fetch Ranges Determination
                aRanges = position_def['dataRanges'][target]
                if not aRanges:
                    continue
                fRanges = []
                for aRange_beg, aRange_end in aRanges:
                    overlap_beg = max(range_beg, aRange_beg)
                    overlap_end = min(range_end, aRange_end)
                    if overlap_beg <= overlap_end:
                        fRanges.append((overlap_beg, overlap_end))

                #[3-2]: Fetch Requests Dispatch
                for fRange in fRanges:
                    rID = func_sendFAR(targetProcess  = 'DATAMANAGER', 
                                       functionID     = 'fetchMarketData', 
                                       functionParams = {'symbol':     symbol, 
                                                         'target':     target,
                                                         'fetchRange': fRange}, 
                                       farrHandler    = func_odfr)
                    dfRIDs[rID] = {'symbol':       symbol,
                                   'target':       target,
                                   'fetchGroupID': range_beg}
                    dfGroup_rIDs.add(rID)

        #---[3-3]: Data Fetch Group Update
        dfGroups[range_beg] = {'fetchRange': (range_beg, range_end),
                               'rIDs':       dfGroup_rIDs}

    def __farr_onDataFetchResponse(self, responder, requestID, functionResult):
        #[1]: Source Check
        if responder != 'DATAMANAGER':
            return
        
        #[2]: Instances
        dfRIDs   = self.__data_fetchRIDs
        dfGroups = self.__data_fetchGroups
        fr_result     = functionResult['result']
        fr_data       = functionResult['data']
        fr_fetchRange = functionResult.get('fetchRange', None)

        #[3]: Result Check
        if fr_result != 'SDF':
            self.__raiseSimulationError(errorCause = f'DATAFETCHERROR_{fr_result}')
            return

        #[4]: Request ID Check
        fReq = dfRIDs.get(requestID, None)
        if fReq is None:
            return
        symbol = fReq['symbol']
        target = fReq['target']
        fgID   = fReq['fetchGroupID']

        #[5]: Data Record
        dRaw_symbol_target     = self.__data_raw[symbol][target]
        dTSs_symbol_raw_target = self.__data_timestamps[symbol]['raw'][target]
        dIdx_openTime = COMMONDATAINDEXES['openTime'][target]
        for dl in fr_data:
            dl_openTime = dl[dIdx_openTime]
            if dl_openTime not in dRaw_symbol_target:
                dTSs_symbol_raw_target.append(dl_openTime)
            dRaw_symbol_target[dl_openTime] = dl

        #[6]: Fetch Group Check
        del dfRIDs[requestID]
        dfGroups[fgID]['rIDs'].remove(requestID)

    def __farr_onSimulationDataSaveRequestResponse(self, responder, requestID, functionResult):
        #[1]: Source Check
        if responder != 'DATAMANAGER':
            return

        #[2]: Instances
        simCode    = functionResult['simulationCode']
        saveResult = functionResult['saveResult']
        errorMsg   = functionResult['errorMsg']

        #[3]: Result Handling
        if not saveResult:
            self.__raiseSimulationError(errorCause = errorMsg)
            return
        self.__updateStatus(status = 'COMPLETED')
    #IPCs END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Simulation Process ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def process(self):
        #[1]: Status Check
        status     = self.__status
        procStatus = self.__procStatus
        if not (status == 'PROCESSING' and procStatus == 'PROCESSING'): 
            return

        #[2]: Fetch Check & Aggregation
        dfGroups = self.__data_fetchGroups
        if dfGroups:
            dfgID_min  = min(dfGroups)
            dfg        = dfGroups[dfgID_min]
            dfg_fRange = dfg['fetchRange']
            dfg_rIDs   = dfg['rIDs']
            if not dfg_rIDs:
                self.__prepareData(range_beg = dfg_fRange[0], 
                                   range_end = dfg_fRange[1])
                del dfGroups[dfgID_min]

        #[3]: Simulation Processing
        sRange  = self.__simulationRange
        nfPoint = self.__data_nextFetchPoint
        lp      = self.__data_lastPrepared
        if lp is None:
            return
        naTarget = self.__nextAnalysisTarget
        laTarget = self.__lastAnalysisTarget
        func_gnitt       = auxiliaries.getNextIntervalTickTimestamp
        func_psot        = self.__performSimulationOnTarget
        func_uCompletion = self.__updateCompletion
        t_begin_ns   = time.perf_counter_ns()
        t_elapsed_ns = 0
        while naTarget <= lp and t_elapsed_ns < _PROCESSTIMEOUT_NS:
            #[3-1]: Perform Analysis & Timer Update
            func_psot(atTS = naTarget)
            t_elapsed_ns = time.perf_counter_ns()-t_begin_ns

            #[3-2]: Fetch Requests Dispatch
            if naTarget == nfPoint:
                self.__sendMarketDataFetchRequests()
                nfPoint = self.__data_nextFetchPoint

            #[3-3]: Next Analysis Target & Completion Update
            naTarget = func_gnitt(intervalID = KLINTERVAL, timestamp = naTarget, nTicks = 1)

            #[3-4]: Completion Check
            if naTarget == laTarget:
                self.__procStatus        = 'SAVING'
                self.__simulationSummary = self.__generateSimulationSummary()
                self.__exportAnalysis()
                self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                  functionID     = 'saveSimulationData',
                                  functionParams = {'simulationCode':                 self.__simulationCode, 
                                                    'simulationRange':                self.__simulationRange,
                                                    'currencyAnalysisConfigurations': self.__currencyAnalysisConfigurations,
                                                    'tradeConfigurations':            self.__tradeConfigurations,
                                                    'analysisExport':                 self.__analysisExport,
                                                    'assets':                         self.__assets_def,
                                                    'positions':                      self.__positions_def,
                                                    'creationTime':                   self.__creationTime,
                                                    'tradeLogs':                      self.__tradeLogs,
                                                    'periodicReports':                self.__periodicReports,
                                                    'simulationSummary':              self.__simulationSummary},
                                  farrHandler    = self.__farr_onSimulationDataSaveRequestResponse)
                break
        self.__nextAnalysisTarget = naTarget

        #[4]: Completion Update
        completion_new = round(((naTarget-1)-sRange[0]+1)/(sRange[1]-sRange[0]+1), 5)
        func_uCompletion(completion = completion_new)

    def __prepareData(self, range_beg, range_end):
        #[1]: Instances
        positions     = self.__positions
        positions_def = self.__positions_def
        dRaw          = self.__data_raw
        dTSs          = self.__data_timestamps
        tTSs_raw   = auxiliaries.getTimestampList_byRange(intervalID = KLINTERVAL, timestamp_beg = range_beg, timestamp_end = range_end, lastTickInclusive = True)
        func_gnitt = auxiliaries.getNextIntervalTickTimestamp

        #[2]: Dummy Filling
        for symbol in positions_def:
            #[2-1]: Instances
            dRaw_symbol     = dRaw[symbol]
            dTSs_symbol_raw = dTSs[symbol]['raw']
            gr_symbol       = positions[symbol]['GR']
            if gr_symbol is None:
                continue

            #[2-2]: Dummy Filling
            for target in ('kline', 'depth', 'aggTrade'):
                dRaw_symbol_target     = dRaw_symbol[target]
                dTSs_symbol_raw_target = dTSs_symbol_raw[target]
                for ts in tTSs_raw:
                    if ts in dRaw_symbol_target:
                        continue
                    if not (gr_symbol[0] <= ts <= gr_symbol[1]):
                        continue
                    ts_close = func_gnitt(intervalID = KLINTERVAL, timestamp = ts, nTicks = 1)-1
                    dRaw_symbol_target[ts] = (ts, ts_close)+_DUMMYFRAMES[target]
                    dTSs_symbol_raw_target.append(ts)
                dTSs_symbol_raw[target] = deque(sorted(dTSs_symbol_raw_target))

        #[3]: Last Prepared Update
        self.__data_lastPrepared = range_end

    def __performSimulationOnTarget(self, atTS):
        #[1]: Instances
        aExport       = self.__analysisExport
        positions_def = self.__positions_def
        positions     = self.__positions
        assets        = self.__assets
        pReports      = self.__periodicReports
        simAnalyzers  = self.__analyzers
        aKwargs       = self.__analysisKwargs
        dRaw = self.__data_raw
        dAgg = self.__data_agg
        dTSs = self.__data_timestamps
        lcas = self.__lastClosedAggregations
        lTSs = self.__lastClosedAggregations_timestamps
        aggregators    = self.__aggregators
        func_aGen      = analyzers.analysisGenerator
        func_lAnalysis = analyzers.linearizeAnalysis
        func_gnitt     = auxiliaries.getNextIntervalTickTimestamp
        func_handleKline = self.__handleKline
        func_handleAR    = self.__handleAnalysisResult

        #[2]: Update Account
        self.__updateAccount(timestamp = atTS)

        #[3]: Generate Analysis and Handle Generated Analysis Results
        for symbol, position in positions.items():
            #[3-1]: Instances
            gr_symbol = position['GR']
            if gr_symbol is None or not (gr_symbol[0] <= atTS <= gr_symbol[1]):
                continue
            position_def    = positions_def[symbol]
            precisions      = position_def['precisions']
            dRaw_symbol     = dRaw[symbol]
            dAgg_symbol     = dAgg[symbol]
            dTSs_symbol     = dTSs[symbol]
            dTSs_symbol_raw = dTSs_symbol['raw']
            lcas_symbol     = lcas[symbol]
            lTSs_symbol     = lTSs[symbol]
            analyzer        = simAnalyzers[position_def['currencyAnalysisConfigurationCode']]
            aKwargs_symbol  = aKwargs[symbol]
            aParams         = analyzer['analysisParams']
            atp_sorted      = analyzer['analysisToProcess_sorted']

            #[3-2]: Analysis Generation
            bdRawTS_remove_min = None
            for iID in dAgg_symbol:
                #[3-2-1]: Instances
                aggTS = func_gnitt(intervalID = iID, timestamp = atTS, nTicks = 0)
                dAgg_symbol_iID    = dAgg_symbol[iID]
                dTSs_symbol_iID    = dTSs_symbol[iID]
                lcas_symbol_iID    = lcas_symbol[iID]
                lTSs_symbol_iID    = lTSs_symbol[iID]
                aParams_iID        = aParams[iID]
                atp_sorted_iID     = atp_sorted[iID]
                aKwargs_symbol_iID = aKwargs_symbol[iID]

                #[3-2-2]: Aggregation
                for target in ('kline', 'depth', 'aggTrade'):
                    dRaw_symbol_target     = dRaw_symbol[target]
                    dAgg_symbol_iID_target = dAgg_symbol_iID[target]
                    dTSs_symbol_iID_target = dTSs_symbol_iID[target]
                    lcas_symbol_iID_target = lcas_symbol_iID[target]
                    lTSs_symbol_iID_target = lTSs_symbol_iID[target]
                    aggregator = aggregators[target]
                    if aggTS not in dAgg_symbol_iID_target:
                        dTSs_symbol_iID_target.append(aggTS)
                    aggregator(dataRaw        = dRaw_symbol_target,
                                dataAgg        = dAgg_symbol_iID_target,
                                lastClosedAggs = lcas_symbol_iID_target,
                                rawOpenTS      = atTS,
                                aggOpenTS      = aggTS,
                                aggIntervalID  = iID,
                                precisions     = precisions)
                    if aggTS in lcas_symbol_iID_target:
                        if not lTSs_symbol_iID_target or lTSs_symbol_iID_target[-1] != aggTS:
                            lTSs_symbol_iID_target.append(aggTS)

                #[3-2-3]: Analysis Generation
                nAR_keeps    = dict()
                nBD_keep_max = 1
                for aType, aCode in atp_sorted_iID:
                    dAgg_symbol_iID_aCode = dAgg_symbol_iID[aCode]
                    dTSs_symbol_iID_aCode = dTSs_symbol_iID[aCode]
                    if aggTS not in dAgg_symbol_iID_aCode:
                        dTSs_symbol_iID_aCode.append(aggTS)
                    nAR_keep, nBD_keep = func_aGen(analysisType    = aType,
                                                   timestamp       = aggTS,
                                                   analysisResults = dAgg_symbol_iID_aCode,
                                                   **aKwargs_symbol_iID,
                                                   **aParams_iID[aCode])
                    nAR_keeps[aCode] = nAR_keep+1
                    if nBD_keep_max < nBD_keep: nBD_keep_max = nBD_keep 
                nBD_keep_max += 1

                #[3-2-4]: Memory Optimization (Analysis & Aggregated Base Data)
                #---[3-2-4-1]: Analysis
                for aCode, nAr_keep in nAR_keeps.items():
                    arTS_remove_min = func_gnitt(intervalID = iID, timestamp = aggTS, nTicks = -(nAr_keep-1))-1
                    dAgg_symbol_iID_aCode = dAgg_symbol_iID[aCode]
                    dTSs_symbol_iID_aCode = dTSs_symbol_iID[aCode]
                    while dTSs_symbol_iID_aCode and dTSs_symbol_iID_aCode[0] <= arTS_remove_min:
                        ts_remove = dTSs_symbol_iID_aCode.popleft()
                        del dAgg_symbol_iID_aCode[ts_remove]
                #---[3-2-4-2]: Base Data
                bdTS_remove_min = func_gnitt(intervalID = iID, timestamp = aggTS, nTicks = -(nBD_keep_max-1))-1
                for target in ('kline', 'depth', 'aggTrade'):
                    dAgg_symbol_iID_target = dAgg_symbol_iID[target]
                    dTSs_symbol_iID_target = dTSs_symbol_iID[target]
                    lcas_symbol_iID_target = lcas_symbol_iID[target]
                    lTSs_symbol_iID_target = lTSs_symbol_iID[target]
                    #[3-2-4-2-1]: Last Aggregated Data
                    while dTSs_symbol_iID_target and dTSs_symbol_iID_target[0] <= bdTS_remove_min:
                        ts_remove = dTSs_symbol_iID_target.popleft()
                        del dAgg_symbol_iID_target[ts_remove]
                    #[3-2-4-2-2]: Last Closed Aggregation
                    while lTSs_symbol_iID_target and lTSs_symbol_iID_target[0] <= bdTS_remove_min:
                        ts_remove = lTSs_symbol_iID_target.popleft()
                        del lcas_symbol_iID_target[ts_remove]
                if bdRawTS_remove_min is None or bdTS_remove_min < bdRawTS_remove_min: bdRawTS_remove_min = bdTS_remove_min

            #[3-3]: Memory Optimization (Raw Base Data)
            for target in ('kline', 'depth', 'aggTrade'):
                dRaw_target     = dRaw_symbol[target]
                dTSs_raw_target = dTSs_symbol_raw[target]
                while dTSs_raw_target and dTSs_raw_target[0] <= bdRawTS_remove_min:
                    ts_remove = dTSs_raw_target.popleft()
                    del dRaw_target[ts_remove]

            #[3-4]: New Kline Handling
            func_handleKline(positionSymbol = symbol, 
                             timestamp      = atTS, 
                             kline          = dRaw_symbol['kline'][atTS])

            #[3-5]: Analysis Result Linearization
            aLinearized = func_lAnalysis(dataRaw        = dRaw_symbol,
                                         dataAggregated = dAgg_symbol, 
                                         analysisPairs  = atp_sorted, 
                                         timestamp      = atTS)

            #[3-6]: Analysis Handling
            func_handleAR(positionSymbol     = symbol, 
                          linearizedAnalysis = aLinearized, 
                          timestamp          = atTS)

            #[3-7]: Analysis Export
            if aExport:
                ae = position['AE']
                #[3-7-1]: Index Identifiers
                if ae['indexIdentifier'] is None: 
                    ae_keys = sorted(aLinearized)
                    ae_ii   = {k: i for i, k in enumerate(ae_keys)}
                    ae['indexIdentifier']        = ae_ii
                    ae['linearizedAnalysisKeys'] = ae_keys
                #[3-7-2]: Tuplization & Appending
                aLinearized_tuple = tuple(aLinearized[laKey] for laKey in ae['linearizedAnalysisKeys'])
                position['AE']['data'].append(aLinearized_tuple)
                
        #[4]: Wallet Balance Trend Analysis Update
        for assetName, asset in assets.items():
            #[4-1]: Instances
            wbta          = asset['WBTA']
            walletBalance = asset['walletBalance']
            #[4-2]: First Balance Update Check
            if wbta['firstUpdatedTS'] is None:
                if walletBalance != wbta['initialWalletBalance']:
                    wbta['firstUpdatedTS'] = atTS
            #[4-3]: Counter & Sums Update
            if wbta['firstUpdatedTS'] is None: continue
            x = (atTS - wbta['firstUpdatedTS'])/KLINTERVAL_S
            y = math.log(walletBalance) if 0 < walletBalance else 0.0
            wbta['count']  += 1
            wbta['sum_x']  += x
            wbta['sum_xx'] += x**2
            wbta['sum_y']  += y
            wbta['sum_yy'] += y**2
            wbta['sum_xy'] += x*y
            #[4-4]: Balance History
            wbta['minimumWalletBalance'] = min(wbta['minimumWalletBalance'], walletBalance)
            wbta['maximumWalletBalance'] = max(wbta['maximumWalletBalance'], walletBalance)
            wbta['finalWalletBalance']   = walletBalance

        #[5]: Periodic Report Update
        for assetName, asset in assets.items():
            #[5-1]: Instances & Daily Report Formatting (If needed)
            pReport_TS = self.__formatPeriodicReport(timestamp = atTS)
            pReport    = pReports[pReport_TS][assetName]
            #[5-2]: Wallet Balance
            walletBalance = asset['walletBalance']
            pReport['walletBalance_min'] = min(pReport['walletBalance_min'], walletBalance)
            pReport['walletBalance_max'] = max(pReport['walletBalance_max'], walletBalance)
            pReport['walletBalance_close'] = walletBalance
            #[5-3]: Margin Balance
            marginBalance = asset['marginBalance']
            pReport['marginBalance_min'] = min(pReport['marginBalance_min'], marginBalance)
            pReport['marginBalance_max'] = max(pReport['marginBalance_max'], marginBalance)
            pReport['marginBalance_close'] = marginBalance
            #[5-4]: Commitment Rate
            if asset['commitmentRate'] is None: commitmentRate = 0
            else:                               commitmentRate = asset['commitmentRate']
            pReport['commitmentRate_min'] = min(pReport['commitmentRate_min'], commitmentRate)
            pReport['commitmentRate_max'] = max(pReport['commitmentRate_max'], commitmentRate)
            pReport['commitmentRate_close'] = commitmentRate
            #[5-5]: Risk Level
            if asset['riskLevel'] is None: riskLevel = 0
            else:                          riskLevel = asset['riskLevel']
            pReport['riskLevel_min'] = min(pReport['riskLevel_min'], riskLevel)
            pReport['riskLevel_max'] = max(pReport['riskLevel_max'], riskLevel)
            pReport['riskLevel_close'] = riskLevel
    
    def __updateAccount(self, timestamp):
        #[1]: Instances
        assets_def    = self.__assets_def
        assets        = self.__assets
        positions_def = self.__positions_def
        positions     = self.__positions
        dRaw          = self.__data_raw
        compute_liqPrice = auxiliaries_trade.computeLiquidationPrice

        #[2]: Update Positions
        for symbol, position in positions.items():
            position_def = positions_def[symbol]
            kl           = dRaw[symbol]['kline'].get(timestamp, None)
            kl_cp        = None if kl is None else kl[KLINDEX_CLOSEPRICE]
            cp           = position['currentPrice'] if kl_cp is None else kl_cp
            if cp is None:
                position['positionInitialMargin'] = None
                position['unrealizedPNL']         = None
            else:
                position['currentPrice'] = cp
                position['positionInitialMargin'] = round(cp*abs(position['quantity'])/position_def['leverage'], position_def['precisions']['quote'])
                if   position['quantity'] < 0:  position['unrealizedPNL'] = round((position['entryPrice']-cp)*abs(position['quantity']), position_def['precisions']['quote'])
                elif position['quantity'] == 0: position['unrealizedPNL'] = None
                elif 0 < position['quantity']:  position['unrealizedPNL'] = round((cp-position['entryPrice'])*abs(position['quantity']), position_def['precisions']['quote'])

        #[3]: Update Assets
        for assetName, asset in assets.items():
            asset_def = assets_def[assetName]
            asset['isolatedPositionInitialMargin'] = sum([positions[symbol]['positionInitialMargin']    for symbol in asset_def['_positionSymbols_isolated'] if positions[symbol]['positionInitialMargin'] is not None])
            asset['crossPositionInitialMargin']    = sum([positions[symbol]['positionInitialMargin']    for symbol in asset_def['_positionSymbols_crossed']  if positions[symbol]['positionInitialMargin'] is not None])
            asset['crossMaintenanceMargin']        = sum([positions[symbol]['maintenanceMargin']        for symbol in asset_def['_positionSymbols_crossed']])
            asset['isolatedUnrealizedPNL']         = sum([positions[symbol]['unrealizedPNL']            for symbol in asset_def['_positionSymbols_isolated'] if positions[symbol]['unrealizedPNL'] is not None])
            asset['crossUnrealizedPNL']            = sum([positions[symbol]['unrealizedPNL']            for symbol in asset_def['_positionSymbols_crossed']  if positions[symbol]['unrealizedPNL'] is not None])
            asset['assumedRatio']                  = sum([positions_def[symbol]['assumedRatio']         for symbol in asset_def['_positionSymbols']])
            asset['weightedAssumedRatio']          = sum([positions_def[symbol]['weightedAssumedRatio'] for symbol in asset_def['_positionSymbols'] if (positions_def[symbol]['weightedAssumedRatio'] is not None)])
            asset['walletBalance']      = asset['crossWalletBalance']+asset['isolatedWalletBalance']
            asset['unrealizedPNL']      = asset['isolatedUnrealizedPNL']+asset['crossUnrealizedPNL']
            asset['marginBalance']      = asset['walletBalance']+asset['unrealizedPNL']
            asset['availableBalance']   = asset['crossWalletBalance']-asset['crossPositionInitialMargin']+asset['crossUnrealizedPNL']
            asset['allocatableBalance'] = round((asset['walletBalance'])*_BASEASSETALLOCATABLERATIO*asset_def['allocationRatio'], _ASSETPRECISIONS[assetName])
            if asset['allocatableBalance'] < 0: asset['allocatableBalance'] = 0

        #[4]: Balance Allocation
        self.__allocateBalance()

        #[5]: Update Secondary Position Data
        for symbol, position in positions.items():
            #[5-1]: Instances
            position_def = positions_def[symbol]
            asset        = assets[position_def['quoteAsset']]

            #[5-2]: None Quantity
            if position['quantity'] is None:
                position['commitmentRate']   = None
                position['liquidationPrice'] = None
                position['riskLevel']        = None

            #[5-3]: Valid Quantity
            else:
                #[5-3-1]: Absolute Quantity
                quantity     = position['quantity']
                quantity_abs = abs(quantity)

                #[5-3-2]: Commitment Rate
                if quantity_abs != 0 and position_def['leverage'] is not None and position['allocatedBalance'] != 0: 
                    position['commitmentRate'] = round((quantity_abs*position['entryPrice']/position_def['leverage'])/position['allocatedBalance'], 5)
                else: 
                    position['commitmentRate'] = None
                
                #[5-3-3]: Liquidation Price
                if position_def['isolated']: wb = position['isolatedWalletBalance']
                else:                        wb = asset['crossWalletBalance']
                position['liquidationPrice'] = compute_liqPrice(positionSymbol    = symbol,
                                                                walletBalance     = wb,
                                                                quantity          = position['quantity'],
                                                                entryPrice        = position['entryPrice'],
                                                                currentPrice      = position['currentPrice'],
                                                                maintenanceMargin = position['maintenanceMargin'],
                                                                upnl              = position['unrealizedPNL'],
                                                                isolated          = position_def['isolated'],
                                                                mm_crossTotal     = asset['crossMaintenanceMargin'],
                                                                upnl_crossTotal   = asset['crossUnrealizedPNL'])
                
                #[5-3-4]: Risk Level
                ep = position['entryPrice']
                cp = position['currentPrice']
                lp = position['liquidationPrice']
                cr = position['commitmentRate']
                if ep is not None and cp is not None:
                    if lp is None: lp = 0
                    if   0 < quantity: rl = (ep-cp)/(ep-lp)
                    elif quantity < 0: rl = (cp-ep)/(lp-ep)
                    if rl < 0: rl = 0
                    if cr is None: position['riskLevel'] = rl
                    else:          position['riskLevel'] = position['commitmentRate']*rl
                else: 
                    position['riskLevel'] = None

        #[6]: Update Secondary Asset Data
        for assetName, asset in assets.items():
            asset_def = assets_def[assetName]

            #[6-1]: Allocated Balance
            allocatedBalanceSum = sum(positions[symbol]['allocatedBalance'] for symbol in asset_def['_positionSymbols'])
            asset['allocatedBalance'] = allocatedBalanceSum

            #[6-2]: Commitment Rate
            commitmentRate_pSymbols = [symbol for symbol in asset_def['_positionSymbols'] if positions[symbol]['commitmentRate'] is not None]
            if commitmentRate_pSymbols:
                commitmentRate_sum     = sum([positions[symbol]['commitmentRate'] for symbol in commitmentRate_pSymbols])
                commitmentRate_average = round(commitmentRate_sum/len(commitmentRate_pSymbols), 5)
            else: 
                commitmentRate_average = None
            asset['commitmentRate'] = commitmentRate_average

            #[6-3]: Risk Level
            riskLevel_pSymbols = [symbol for symbol in asset_def['_positionSymbols'] if (positions[symbol]['riskLevel'] != None)]
            if riskLevel_pSymbols:
                riskLevel_sum     = sum([positions[symbol]['riskLevel'] for symbol in riskLevel_pSymbols])
                riskLevel_average = round(riskLevel_sum/len(riskLevel_pSymbols), 5)
            else: 
                riskLevel_average = None
            asset['riskLevel'] = riskLevel_average
    
    def __allocateBalance(self):
        #[1]: Instances
        assets_def    = self.__assets_def
        assets        = self.__assets
        positions_def = self.__positions_def
        positions     = self.__positions

        #[2]: Balance Allocation
        for assetName, asset in assets.items():
            #[2-1]: Instances
            asset_def = assets_def[assetName]
            allocatedAssumedRatio = 0

            #[2-2]: Zero Quantity Allocation Zero
            for symbol in asset_def['_positionSymbols']:
                #[2-2-1]: Instances
                position = positions[symbol]

                #[2-2-2]: Zero quantity
                if position['quantity'] == 0: 
                    assumedRatio_effective       = 0
                    position['allocatedBalance'] = 0

                #[2-2-3]: Non-Zero Quantity
                else:
                    if 0 < asset['allocatableBalance']:
                        assumedRatio_effective = round(position['allocatedBalance']/asset['allocatableBalance'], 4)
                    else:
                        assumedRatio_effective = 0

                #[2-2-4]: Effective Assumed Ratio Update
                allocatedAssumedRatio += assumedRatio_effective

            #[2-3]: Zero Quantity Re-Allocation
            for symbol in asset_def['_positionSymbols_prioritySorted']:
                #[2-3-1]: Instances
                position_def = positions_def[symbol]
                position     = positions[symbol]

                #[2-3-2]: Condition Check (Zero Quantity )
                if not(position['quantity'] == 0 or (position_def['assumedRatio'] != 0 and position['allocatedBalance'] == 0)): 
                    continue

                #[2-3-3]: Allocated Balance & Effective Assumed Ratio Update
                if 0 < asset['allocatableBalance']:
                    allocatedBalance       = min(round(asset['allocatableBalance']*position_def['assumedRatio'], position_def['precisions']['quote']),
                                                 position_def['maxAllocatedBalance'])
                    assumedRatio_effective = round(allocatedBalance/asset['allocatableBalance'], 4)
                else:
                    allocatedBalance       = 0
                    assumedRatio_effective = 0

                #[2-3-4]: Allocatability Check
                if allocatedAssumedRatio+assumedRatio_effective <= 1:
                    allocatedAssumedRatio += assumedRatio_effective
                    position['allocatedBalance'] = allocatedBalance
                else: break
    
    def __formatPeriodicReport(self, timestamp):
        #[1]: Instances
        assets   = self.__assets
        pReports = self.__periodicReports
        func_gnitt = auxiliaries.getNextIntervalTickTimestamp

        #[2]: Report Timestamp Check
        prTS = func_gnitt(intervalID = PERIODICREPORT_INTERVALID, timestamp = timestamp, mrktReg = None, nTicks = 0)
        if prTS in pReports: return prTS

        #[3]: Previous Report
        prTS_prev = func_gnitt(intervalID = PERIODICREPORT_INTERVALID, timestamp = timestamp, mrktReg = None, nTicks = -1)
        prs_prev  = pReports.get(prTS_prev, None)

        #[4]: New Report Formatting
        pReport = dict()
        for assetName, asset in assets.items():
            #[4-1]: Current Values
            mb = asset['marginBalance']
            wb = asset['walletBalance']
            cr = 0 if asset['commitmentRate'] is None else asset['commitmentRate']
            rl = 0 if asset['riskLevel']      is None else asset['riskLevel']
            #[4-2]: Previous Values
            if prs_prev is not None:
                pr_prev = prs_prev[assetName]
                mb_open = pr_prev['marginBalance_close']
                wb_open = pr_prev['walletBalance_close']
                cr_open = pr_prev['commitmentRate_close']
                rl_open = pr_prev['riskLevel_close']
            else:
                mb_open = mb
                wb_open = wb
                cr_open = cr
                rl_open = rl
            #[4-3]: Formatting
            pReport[assetName] = {'nTrades':             0,
                                  'nTrades_buy':         0,
                                  'nTrades_sell':        0,
                                  'nTrades_entry':       0,
                                  'nTrades_clear':       0,
                                  'nTrades_exit':        0,
                                  'nTrades_fslImmed':    0,
                                  'nTrades_fslClose':    0,
                                  'nTrades_liquidation': 0,
                                  'nTrades_forceClear':  0,
                                  'nTrades_unknown':     0,
                                  'nTrades_gain':        0,
                                  'nTrades_loss':        0,
                                  'marginBalance_open':  mb_open, 'marginBalance_min':  mb, 'marginBalance_max':  mb, 'marginBalance_close':  mb,
                                  'walletBalance_open':  wb_open, 'walletBalance_min':  wb, 'walletBalance_max':  wb, 'walletBalance_close':  wb,
                                  'commitmentRate_open': cr_open, 'commitmentRate_min': cr, 'commitmentRate_max': cr, 'commitmentRate_close': cr,
                                  'riskLevel_open':      rl_open, 'riskLevel_min':      rl, 'riskLevel_max':      rl, 'riskLevel_close':      rl,
                                  '_intervalID': PERIODICREPORT_INTERVALID}
        pReports[prTS] = pReport

        #[5]: Return Periodic Report Timestamp
        return prTS
    
    def __handleKline(self, positionSymbol, timestamp, kline):
        #[1]: Instances
        position_def = self.__positions_def[positionSymbol]
        position     = self.__positions[positionSymbol]
        tcConfig     = self.__tradeConfigurations[position_def['tradeConfigurationCode']]
        tcTracker    = position['tradeControlTracker']
        precisions   = position_def['precisions']

        #[2]: Force Exit Check
        tradeHandler_checkList = {'FSLIMMED':    None,
                                  'FSLCLOSE':    None,
                                  'LIQUIDATION': None}
        if position['quantity'] != 0 and not (kline[KLINDEX_OPENPRICE] is None or kline[KLINDEX_LOWPRICE] is None or kline[KLINDEX_HIGHPRICE] is None or kline[KLINDEX_CLOSEPRICE] is None):
            #FSL IMMED
            if tcConfig['fullStopLossImmediate'] is not None:
                #<SHORT>
                if position['quantity'] < 0:
                    price_FSL = round(position['entryPrice']*(1+tcConfig['fullStopLossImmediate']), precisions['price'])
                    if price_FSL <= kline[KLINDEX_HIGHPRICE]: 
                        tradeHandler_checkList['FSLIMMED'] = ('BUY', price_FSL, price_FSL-kline[KLINDEX_OPENPRICE])
                #<LONG>
                elif 0 < position['quantity']:
                    price_FSL = round(position['entryPrice']*(1-tcConfig['fullStopLossImmediate']), precisions['price'])
                    if kline[KLINDEX_LOWPRICE] <= price_FSL: 
                        tradeHandler_checkList['FSLIMMED'] = ('SELL', price_FSL, kline[KLINDEX_OPENPRICE]-price_FSL)
            #FSL CLOSE
            if tcConfig['fullStopLossClose'] is not None:
                #<SHORT>
                if position['quantity'] < 0:
                    price_FSL = round(position['entryPrice']*(1+tcConfig['fullStopLossClose']), precisions['price'])
                    if price_FSL <= kline[KLINDEX_CLOSEPRICE]: 
                        tradeHandler_checkList['FSLCLOSE'] = ('BUY', kline[KLINDEX_CLOSEPRICE])
                #<LONG>
                elif 0 < position['quantity']:
                    price_FSL = round(position['entryPrice']*(1-tcConfig['fullStopLossClose']), precisions['price'])
                    if kline[KLINDEX_CLOSEPRICE] <= price_FSL: 
                        tradeHandler_checkList['FSLCLOSE'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
            #LIQUIDATION
            if position['liquidationPrice'] is not None:
                #<SHORT>
                if position['quantity'] < 0:
                    if position['liquidationPrice'] <= kline[KLINDEX_HIGHPRICE]: 
                        tradeHandler_checkList['LIQUIDATION'] = ('LIQUIDATION', position['liquidationPrice'], position['liquidationPrice']-kline[KLINDEX_OPENPRICE])
                #<LONG>
                elif 0 < position['quantity']:
                    if kline[KLINDEX_LOWPRICE] <= position['liquidationPrice']: 
                        tradeHandler_checkList['LIQUIDATION'] = ('LIQUIDATION', position['liquidationPrice'], kline[KLINDEX_OPENPRICE]-position['liquidationPrice'])

        #[3]: Trade Handler Determination
        if tradeHandler_checkList['LIQUIDATION'] is not None and tradeHandler_checkList['FSLIMMED'] is not None:
            if tradeHandler_checkList['LIQUIDATION'][2] <= tradeHandler_checkList['FSLIMMED'][2]: tradeHandler = 'LIQUIDATION'
            else:                                                                                 tradeHandler = 'FSLIMMED'
        elif tradeHandler_checkList['LIQUIDATION'] is not None: tradeHandler = 'LIQUIDATION'
        elif tradeHandler_checkList['FSLIMMED']    is not None: tradeHandler = 'FSLIMMED'
        elif tradeHandler_checkList['FSLCLOSE']    is not None: tradeHandler = 'FSLCLOSE'
        else:                                                   tradeHandler = None

        #[4]: Trade Handlers Execution
        if tradeHandler is None: 
            return
        thParams      = tradeHandler_checkList[tradeHandler]
        quantity_prev = position['quantity']
        #---[4-1]: FSLIMMED
        if tradeHandler == 'FSLIMMED':
            self.__processSimulatedTrade(positionSymbol = positionSymbol, 
                                         logicSource    = 'FSLIMMED', 
                                         side           = thParams[0], 
                                         quantity       = abs(position['quantity']), 
                                         timestamp      = timestamp, 
                                         tradePrice     = thParams[1])
            if   quantity_prev < 0: tcTracker['slExited'] = 'SHORT'
            elif 0 < quantity_prev: tcTracker['slExited'] = 'LONG'
        #---[4-2]: FSLCLOSE
        elif tradeHandler == 'FSLCLOSE':
            self.__processSimulatedTrade(positionSymbol = positionSymbol, 
                                         logicSource    = 'FSLCLOSE', 
                                         side           = thParams[0], 
                                         quantity       = abs(position['quantity']), 
                                         timestamp      = timestamp, 
                                         tradePrice     = thParams[1])
            if   quantity_prev < 0: tcTracker['slExited'] = 'SHORT'
            elif 0 < quantity_prev: tcTracker['slExited'] = 'LONG'
        #---[4-3]: LIQUIDATION
        elif tradeHandler == 'LIQUIDATION': 
            self.__processSimulatedTrade(positionSymbol = positionSymbol, 
                                         logicSource    = 'LIQUIDATION', 
                                         side           = None, 
                                         quantity       = abs(position['quantity']), 
                                         timestamp      = timestamp, 
                                         tradePrice     = thParams[1]) 
            if   quantity_prev < 0: tcTracker['slExited'] = 'SHORT'
            elif 0 < quantity_prev: tcTracker['slExited'] = 'LONG'

    def __handleAnalysisResult(self, positionSymbol, linearizedAnalysis, timestamp):
        #[1]: Instances
        position_def = self.__positions_def[positionSymbol]
        position     = self.__positions[positionSymbol]
        tcConfig     = self.__tradeConfigurations[position_def['tradeConfigurationCode']]
        tcTracker    = position['tradeControlTracker']
        precisions   = position_def['precisions']

        #[2]: Target Exposure Factor
        try:
            tef_dir, tef_val = teffunctions.TEFFUNCTIONS_GET_TEF[tcConfig['teff_functionType']](params             = tcConfig['teff_functionParams'],
                                                                                                linearizedAnalysis = linearizedAnalysis,
                                                                                                tcTracker_model    = tcTracker['teff_model'])
        except Exception as e:
            print(termcolor.colored(f"[SIMULATOR{self.simulatorIndex}] An Unexpected Error Occurred While Attempting To Compute Target Exposure Factor In Simulation.\n"
                                    f" * Simulation Code:   {self.__simulationCode}\n"
                                    f" * TEF Function Type: {tcConfig['teff_functionType']}\n"
                                    f" * Position Symbol:   {positionSymbol}\n"
                                    f" * Timestamp:         {timestamp}\n"
                                    f" * Error:             {e}\n"
                                    f" * Detailed Trace:    {traceback.format_exc()}", 
                                    'light_red'))
            return
        if (tef_dir not in (None, 'SHORT', 'LONG') or 
            not isinstance(tef_val, (int, float))  or 
            not (-1 <= tef_val <= 1)):
            print(termcolor.colored(f"[SIMULATOR{self.simulatorIndex}] An Unexpected TEF Result Detected. Direction Must Be None, 'SHORT' Or 'LONG', And The Value Must Be An Integer Or Float In Range [-1.0, 1.0].\n"
                                    f" * Simulation Code:   {self.__simulationCode}\n"
                                    f" * TEF Function Type: {tcConfig['teff_functionType']}\n"
                                    f" * TEF Direction:     {tef_dir}\n"
                                    f" * TEF Value:         {tef_val}\n"
                                    f" * Position Symbol:   {positionSymbol}\n"
                                    f" * Timestamp:         {timestamp}", 
                                    'light_red'))
            return

        #[3]: SL Exit Flag
        if tcTracker['slExited'] != tef_dir: 
            tcTracker['slExited'] = None

        #[4]: Trade Handlers Determination
        tradeHandler_checkList = {'ENTRY': None,
                                  'CLEAR': None,
                                  'EXIT':  None}
        #---[4-1]: CheckList 1: CLEAR
        if   position['quantity'] < 0 and tef_dir != 'SHORT': tradeHandler_checkList['CLEAR'] = ('BUY',  position['currentPrice'])
        elif 0 < position['quantity'] and tef_dir != 'LONG':  tradeHandler_checkList['CLEAR'] = ('SELL', position['currentPrice'])
        #---[4-2]: CheckList 2: ENTRY & EXIT
        pslCheck = tcConfig['postStopLossReentry'] or (tcTracker['slExited'] is None)
        if tef_dir == 'SHORT':  
            if pslCheck and tcConfig['direction'] in ('BOTH', 'SHORT'): 
                tradeHandler_checkList['ENTRY'] = ('SELL', position['currentPrice'])
            tradeHandler_checkList['EXIT'] = ('BUY', position['currentPrice'])
        elif tef_dir == 'LONG':
            if pslCheck and tcConfig['direction'] in ('BOTH', 'LONG'): 
                tradeHandler_checkList['ENTRY'] = ('BUY', position['currentPrice'])
            tradeHandler_checkList['EXIT'] = ('SELL', position['currentPrice'])
        elif tef_dir is None:
            if   position['quantity'] < 0: tradeHandler_checkList['EXIT'] = ('BUY',  position['currentPrice'])
            elif 0 < position['quantity']: tradeHandler_checkList['EXIT'] = ('SELL', position['currentPrice'])

        #[5]: Trade Handlers Determination
        tradeHandlers = []
        if tradeHandler_checkList['CLEAR'] is not None: tradeHandlers.append('CLEAR')
        if tradeHandler_checkList['EXIT']  is not None: tradeHandlers.append('EXIT')
        if tradeHandler_checkList['ENTRY'] is not None: tradeHandlers.append('ENTRY')

        #[6]: Trade Handlers Execution
        for tradeHandler in tradeHandlers:
            th_side, th_price = tradeHandler_checkList[tradeHandler]
            #[6-1]: CLEAR
            if tradeHandler == 'CLEAR': 
                self.__processSimulatedTrade(positionSymbol = positionSymbol, 
                                             logicSource    = 'CLEAR', 
                                             side           = th_side, 
                                             quantity       = abs(position['quantity']), 
                                             timestamp      = timestamp, 
                                             tradePrice     = th_price)
            #[6-2]: ENTRY & EXIT
            else:
                balance_allocated = position['allocatedBalance']                                          if position['allocatedBalance'] is not None else 0
                balance_committed = abs(position['quantity'])*position['entryPrice']/tcConfig['leverage'] if position['entryPrice']       is not None else 0
                balance_toCommit  = balance_allocated*abs(tef_val)
                balance_toEnter   = balance_toCommit-balance_committed
                if balance_toEnter == 0: continue
                #[6-2-1]: ENTRY
                if tradeHandler == 'ENTRY':
                    if not 0 < balance_toEnter: continue
                    quantity_minUnit  = pow(10, -precisions['quantity'])
                    quantity_toEnter  = round(int((balance_toEnter/th_price*tcConfig['leverage'])/quantity_minUnit)*quantity_minUnit, precisions['quantity'])
                    if not 0 < quantity_toEnter: continue
                    self.__processSimulatedTrade(positionSymbol = positionSymbol, 
                                                 logicSource    = 'ENTRY', 
                                                 side           = th_side, 
                                                 quantity       = quantity_toEnter, 
                                                 timestamp      = timestamp, 
                                                 tradePrice     = th_price)
                #[6-2-2]: EXIT
                elif tradeHandler == 'EXIT':
                    if not balance_toEnter < 0: continue
                    quantity_minUnit = pow(10, -precisions['quantity'])
                    quantity_toExit  = round(int((-balance_toEnter/position['entryPrice']*tcConfig['leverage'])/quantity_minUnit)*quantity_minUnit, precisions['quantity'])
                    if not 0 < quantity_toExit: continue
                    self.__processSimulatedTrade(positionSymbol = positionSymbol, 
                                                 logicSource    = 'EXIT', 
                                                 side           = th_side, 
                                                 quantity       = quantity_toExit, 
                                                 timestamp      = timestamp, 
                                                 tradePrice     = th_price)
    
    def __processSimulatedTrade(self, positionSymbol, logicSource, side, quantity, timestamp, tradePrice):
        #[1]: Instances
        position_def = self.__positions_def[positionSymbol]
        position     = self.__positions[positionSymbol]
        precisions   = position_def['precisions']
        asset        = self.__assets[position_def['quoteAsset']]

        #[2]: Trade Processing
        #---[2-1]: LIQUIDATION
        if (logicSource == 'LIQUIDATION'):
            quantity_new = 0
            if   0 < position['quantity']: profit = round(abs(position['quantity'])*(tradePrice-position['entryPrice']), precisions['quote'])
            elif position['quantity'] < 0: profit = round(abs(position['quantity'])*(position['entryPrice']-tradePrice), precisions['quote'])
            entryPrice_new = None
            tradingFee     = round(abs(position['quantity'])*tradePrice*_MARKETTRADINGFEE, precisions['quote'])
            if position_def['isolated']:
                asset['isolatedWalletBalance']         = round(asset['isolatedWalletBalance']-position['isolatedWalletBalance'],         precisions['quote'])
                position['isolatedWalletBalance']      = round(position['isolatedWalletBalance']+profit-tradingFee,                      precisions['quote'])
                asset['crossWalletBalance']            = round(asset['crossWalletBalance']+position['isolatedWalletBalance'],            precisions['quote'])
                asset['isolatedPositionInitialMargin'] = round(asset['isolatedPositionInitialMargin']-position['positionInitialMargin'], precisions['quote'])
            else:
                asset['crossWalletBalance']         = round(asset['crossWalletBalance']+profit-tradingFee,                         precisions['quote'])
                asset['crossPositionInitialMargin'] = round(asset['crossPositionInitialMargin']-position['positionInitialMargin'], precisions['quote'])
                asset['crossMaintenanceMargin']     = round(asset['crossMaintenanceMargin']-position['maintenanceMargin'],         precisions['quote'])
            position['entryPrice']            = None
            position['quantity']              = 0
            position['maintenanceMargin']     = 0
            position['positionInitialMargin'] = 0
            #Wallet, Margin and Available Balance
            asset['walletBalance']    = asset['crossWalletBalance']+asset['isolatedWalletBalance']
            asset['marginBalance']    = asset['walletBalance']+asset['unrealizedPNL']
            asset['availableBalance'] = asset['crossWalletBalance']-asset['crossPositionInitialMargin']+asset['unrealizedPNL']

        #---[2-2]: General Trading
        else:
            #[2-2-1]: Compute Values
            #---Quantity
            if   side == 'BUY':  quantity_new = round(position['quantity']+quantity, precisions['quantity'])
            elif side == 'SELL': quantity_new = round(position['quantity']-quantity, precisions['quantity'])
            quantity_dirDelta = round(abs(quantity_new)-abs(position['quantity']), precisions['quantity'])
            #---Cost, Profit & Entry Price
            if 0 < quantity_dirDelta:
                #Entry Price
                if position['quantity'] == 0: notional_prev = 0
                else:                         notional_prev = abs(position['quantity'])*position['entryPrice']
                notional_new = notional_prev+quantity_dirDelta*tradePrice
                entryPrice_new = round(notional_new/abs(quantity_new), precisions['price'])
                #Profit
                profit = 0
            elif quantity_dirDelta < 0:
                #Entry Price
                if quantity_new == 0: entryPrice_new = None
                else:                 entryPrice_new = position['entryPrice']
                #Profit
                if   side == 'BUY':  profit = round(quantity*(position['entryPrice']-tradePrice), precisions['quote'])
                elif side == 'SELL': profit = round(quantity*(tradePrice-position['entryPrice']), precisions['quote'])
            tradingFee = round(quantity*tradePrice*_MARKETTRADINGFEE, precisions['quote'])
            currentNotional = tradePrice*abs(position['quantity'])
            maintenanceMarginRate, maintenanceAmount = auxiliaries_trade.getMaintenanceMarginRateAndAmount(positionSymbol = positionSymbol, notional = currentNotional)
            maintenanceMargin_new = round(currentNotional*maintenanceMarginRate-maintenanceAmount, precisions['quote'])
            
            #[2-2-2]: Apply Values
            position['entryPrice']        = entryPrice_new
            position['quantity']          = quantity_new
            position['maintenanceMargin'] = maintenanceMargin_new
            asset['crossWalletBalance']   = round(asset['crossWalletBalance']+profit-tradingFee, precisions['quote'])
            position_positionInitialMargin_prev = position['positionInitialMargin']
            position['positionInitialMargin'] = round(tradePrice*abs(position['quantity'])/position_def['leverage'], precisions['price'])
            if position_def['isolated']:
                # _walletBalanceToTransfer = Balance from 'CrossWalletBalance' -> 'IsolatedWalletBalance' (Assuming all the other additional parameters (Insurance Fund, Open-Loss, etc) to be 1% of the notional value)
                #---Entry
                if 0 < quantity_dirDelta: 
                    walletBalanceToTransfer = round(quantity*tradePrice*((1/position_def['leverage'])+0.01), precisions['quote'])
                #---Exit
                elif quantity_dirDelta < 0:
                    if quantity_new == 0: walletBalanceToTransfer = -position['isolatedWalletBalance']
                    else:                 walletBalanceToTransfer = -round(quantity*position['entryPrice']/position_def['leverage'], precisions['quote'])
                position['isolatedWalletBalance'] = round(position['isolatedWalletBalance']+walletBalanceToTransfer, precisions['quote'])
                asset['crossWalletBalance']            = round(asset['crossWalletBalance']-walletBalanceToTransfer,    precisions['quote'])
                asset['isolatedWalletBalance']         = round(asset['isolatedWalletBalance']+walletBalanceToTransfer, precisions['quote'])
                asset['isolatedPositionInitialMargin'] = round(asset['isolatedPositionInitialMargin']-position_positionInitialMargin_prev+position['positionInitialMargin'], precisions['quote'])
            else:
                asset['crossPositionInitialMargin']    = round(asset['crossPositionInitialMargin']-position_positionInitialMargin_prev+position['positionInitialMargin'], precisions['quote'])
            #---Wallet, Margin and Available Balance
            asset['walletBalance']    = asset['crossWalletBalance']+asset['isolatedWalletBalance']
            asset['marginBalance']    = asset['walletBalance']+asset['unrealizedPNL']
            asset['availableBalance'] = asset['crossWalletBalance']-asset['crossPositionInitialMargin']+asset['unrealizedPNL']

        #[3]: Update Account
        self.__updateAccount(timestamp = timestamp)

        #[4]: Save Trade Log
        tradeLog = {'timestamp':           timestamp, 
                    'positionSymbol':      positionSymbol,
                    'logicSource':         logicSource,
                    'side':                side,
                    'quantity':            quantity,
                    'price':               tradePrice,
                    'profit':              profit,
                    'tradingFee':          tradingFee,
                    'totalQuantity':       quantity_new,
                    'entryPrice':          entryPrice_new,
                    'walletBalance':       asset['walletBalance'],
                    'tradeControlTracker': position['tradeControlTracker']}
        self.__tradeLogs.append(tradeLog)

        #[5]: Update Daily Report
        pReport_TS = self.__formatPeriodicReport(timestamp = timestamp)
        pReport    = self.__periodicReports[pReport_TS][position_def['quoteAsset']]
        pReport['nTrades'] += 1
        if   side == 'BUY':                pReport['nTrades_buy']         += 1
        elif side == 'SELL':               pReport['nTrades_sell']        += 1
        if   logicSource == 'ENTRY':       pReport['nTrades_entry']       += 1
        elif logicSource == 'CLEAR':       pReport['nTrades_clear']       += 1
        elif logicSource == 'EXIT':        pReport['nTrades_exit']        += 1
        elif logicSource == 'FSLIMMED':    pReport['nTrades_fslImmed']    += 1
        elif logicSource == 'FSLCLOSE':    pReport['nTrades_fslClose']    += 1
        elif logicSource == 'LIQUIDATION': pReport['nTrades_liquidation'] += 1
        if   0 < profit: pReport['nTrades_gain'] += 1
        elif profit < 0: pReport['nTrades_loss'] += 1
        wb = asset['walletBalance']
        pReport['walletBalance_min']   = min(pReport['walletBalance_min'], wb)
        pReport['walletBalance_max']   = max(pReport['walletBalance_max'], wb)
        pReport['walletBalance_close'] = wb
    
    def __generateSimulationSummary(self):
        #[1]: Instances
        positions_def = self.__positions_def
        assets        = self.__assets
        tradeLogs     = self.__tradeLogs

        #[2]: Entire Summary
        nTrades_total = len(tradeLogs)
        if 0 < nTrades_total:
            dailyTS_firstLog = int(tradeLogs[0]['timestamp']/86400)*86400
            nTradeDays = int((self.__simulationRange[1]-dailyTS_firstLog)/86400)+1
        else: 
            nTradeDays = 0
        nTrades_buy         = 0
        nTrades_sell        = 0
        nTrades_entry       = 0
        nTrades_clear       = 0
        nTrades_exit        = 0
        nTrades_fslImmed    = 0
        nTrades_fslClose    = 0
        nTrades_liquidation = 0
        nTrades_gain        = 0
        nTrades_loss        = 0
        for log in tradeLogs:
            side        = log['side']
            logicSource = log['logicSource']
            profit      = log['profit']
            if   side == 'BUY':  nTrades_buy  += 1
            elif side == 'SELL': nTrades_sell += 1
            if   logicSource == 'ENTRY':       nTrades_entry       += 1
            elif logicSource == 'CLEAR':       nTrades_clear       += 1
            elif logicSource == 'EXIT':        nTrades_exit        += 1
            elif logicSource == 'FSLIMMED':    nTrades_fslImmed    += 1
            elif logicSource == 'FSLCLOSE':    nTrades_fslClose    += 1
            elif logicSource == 'LIQUIDATION': nTrades_liquidation += 1
            if   0 < profit: nTrades_gain += 1
            elif profit < 0: nTrades_loss += 1
        simulationSummary = {'total': {'nTradeDays':          nTradeDays,
                                       'nTrades_total':       nTrades_total, 
                                       'nTrades_buy':         nTrades_buy, 
                                       'nTrades_sell':        nTrades_sell, 
                                       'nTrades_entry':       nTrades_entry,
                                       'nTrades_clear':       nTrades_clear,
                                       'nTrades_exit':        nTrades_exit,
                                       'nTrades_fslImmed':    nTrades_fslImmed,
                                       'nTrades_fslClose':    nTrades_fslClose,
                                       'nTrades_liquidation': nTrades_liquidation,
                                       'nTrades_gain':        nTrades_gain,
                                       'nTrades_loss':        nTrades_loss}}
        
        #[3]: Asset Summary
        #---[3-1]: Trade Logs Collection
        tradeLog_byAssets = dict()
        for assetName in assets: tradeLog_byAssets[assetName] = []
        for log in tradeLogs:    tradeLog_byAssets[positions_def[log['positionSymbol']]['quoteAsset']].append(log)
        #---[3-2]: Asset Summary Generation
        for assetName in assets:
            #[3-2-1]: Instances
            asset              = assets[assetName]
            tradeLog_thisAsset = tradeLog_byAssets[assetName]
            #[3-2-2]: Counts
            if len(tradeLog_thisAsset):
                dailyTS_firstLog = int(tradeLog_thisAsset[0]['timestamp']/86400)*86400
                nTradeDays = int((self.__simulationRange[1]-dailyTS_firstLog)/86400)+1
            else: 
                nTradeDays = 0
            nTrades_buy         = 0
            nTrades_sell        = 0
            nTrades_entry       = 0
            nTrades_clear       = 0
            nTrades_exit        = 0
            nTrades_fslImmed    = 0
            nTrades_fslClose    = 0
            nTrades_liquidation = 0
            nTrades_gain        = 0
            nTrades_loss        = 0
            gains_total         = 0
            losses_total        = 0
            tradingFee_total    = 0
            for log in tradeLog_thisAsset:
                side        = log['side']
                logicSource = log['logicSource']
                profit      = log['profit']
                if   side == 'BUY':  nTrades_buy  += 1
                elif side == 'SELL': nTrades_sell += 1
                if   logicSource == 'ENTRY':       nTrades_entry       += 1
                elif logicSource == 'CLEAR':       nTrades_clear       += 1
                elif logicSource == 'EXIT':        nTrades_exit        += 1
                elif logicSource == 'FSLIMMED':    nTrades_fslImmed    += 1
                elif logicSource == 'FSLCLOSE':    nTrades_fslClose    += 1
                elif logicSource == 'LIQUIDATION': nTrades_liquidation += 1
                if   0 < profit: nTrades_gain += 1
                elif profit < 0: nTrades_loss += 1
                profit = log['profit']
                if   profit < 0: losses_total += abs(profit)
                elif 0 < profit: gains_total  += profit
                tradingFee_total += log['tradingFee']
                gains_total      = round(gains_total,      _ASSETPRECISIONS[assetName])
                losses_total     = round(losses_total,     _ASSETPRECISIONS[assetName])
                tradingFee_total = round(tradingFee_total, _ASSETPRECISIONS[assetName])
            #[3-2-3]: Wallet Balance Trend Analysis
            wbta = asset['WBTA']
            walletBalance_initial = wbta['initialWalletBalance']
            walletBalance_min     = wbta['minimumWalletBalance']
            walletBalance_max     = wbta['maximumWalletBalance']
            walletBalance_final   = wbta['finalWalletBalance']
            wbta_growthRate = None
            wbta_volatility = None
            if 1 < wbta['count']:
                numerator   = (wbta['count']*wbta['sum_xy']) - (wbta['sum_x']*wbta['sum_y'])
                denominator = (wbta['count']*wbta['sum_xx']) - (wbta['sum_x']*wbta['sum_x'])
                if 0 < denominator:
                    wbta_growthRate = numerator / denominator
                    mean_x = wbta['sum_x']/wbta['count']
                    mean_y = wbta['sum_y']/wbta['count']
                    var_x = (wbta['sum_xx']/wbta['count']) - (mean_x**2)
                    var_y = (wbta['sum_yy']/wbta['count']) - (mean_y**2)
                    variance_resid = max(var_y - (wbta_growthRate**2 * var_x), 0.0)
                    wbta_volatility = math.sqrt(variance_resid)
            #[3-2-4]: Update Summary
            simulationSummary[assetName] = {#Counts
                                            'nTradeDays':    nTradeDays, 
                                            'nTrades_total': len(tradeLog_thisAsset), 
                                            'nTrades_buy':   nTrades_buy, 
                                            'nTrades_sell':  nTrades_sell,
                                            'nTrades_entry':       nTrades_entry, 
                                            'nTrades_clear':       nTrades_clear, 
                                            'nTrades_exit':        nTrades_exit, 
                                            'nTrades_fslImmed':    nTrades_fslImmed, 
                                            'nTrades_fslClose':    nTrades_fslClose, 
                                            'nTrades_liquidation': nTrades_liquidation,
                                            'nTrades_gain':        nTrades_gain, 
                                            'nTrades_loss':        nTrades_loss,
                                            #Profit
                                            'gains':      gains_total, 
                                            'losses':     losses_total, 
                                            'tradingFee': tradingFee_total,
                                            #Balance Trend
                                            'walletBalance_initial': walletBalance_initial, 
                                            'walletBalance_min':     walletBalance_min, 
                                            'walletBalance_max':     walletBalance_max, 
                                            'walletBalance_final':   walletBalance_final, 
                                            'wbta_growthRate':       wbta_growthRate, 
                                            'wbta_volatility':       wbta_volatility,
                                            'wbta_KLINTERVAL_S':     KLINTERVAL_S}
            
        #[4]: Return The Generated Simulation Summary
        return simulationSummary
    
    def __exportAnalysis(self):
        #[1]: Analysis Export Check
        aExport = self.__analysisExport
        if not aExport:
            return
        
        #[2]: Instances
        simCode       = self.__simulationCode
        positions     = self.__positions
        positions_def = self.__positions_def

        #[3]: Analysis Exports Main Folder
        path_Main = os.path.join(self.path_project, 'data', 'analysisExports')
        if not os.path.exists(path_Main): os.makedirs(path_Main)

        #[4]: Analysis Exports Simulation Folder
        index_Sim = None
        path_Sim  = os.path.join(path_Main, f"{simCode}_ae")
        if os.path.exists(path_Sim): 
            index_Sim = 0
            while True:
                path_Sim = os.path.join(path_Main, f"{simCode}_ae_{index_Sim}")
                if not os.path.exists(path_Sim):
                    os.makedirs(path_Sim)
                    break
                index_Sim += 1
        else:
            os.makedirs(path_Sim)

        #[5]: Numpy Conversion & Save
        for symbol, position in positions.items():
            #[5-1]: Instances
            ae         = position['AE']
            precisions = positions_def[symbol]['precisions']

            #[5-2]: File Name
            if index_Sim is None: baseName = f"{simCode}_{symbol}"
            else:                 baseName = f"{simCode}_{index_Sim}_{symbol}"
            path_descriptor = os.path.join(path_Sim, f"{baseName}_descriptor.json")
            path_data       = os.path.join(path_Sim, f"{baseName}_data.npy")

            #[5-3]: Numpy Conversion
            data_numpy = numpy.array(object = ae['data'], dtype = numpy.float64)

            #[5-4]: Descriptor & Numpy Conversion
            descriptor = {'genTime_ns':        time.time_ns(),
                          'simulationCode':    simCode,
                          'positionSymbol':    symbol,
                          'pricePrecision':    precisions['price'],
                          'quantityPrecision': precisions['quantity'],
                          'quotePrecision':    precisions['quote'],
                          'indexIdentifier':   ae['indexIdentifier']}

            #[5-5]: Data Save
            numpy.save(file = path_data, 
                       arr  = data_numpy)
            with open(path_descriptor, 'w') as f: 
                f.write(json.dumps(descriptor, indent = 4))
    #Simulation Process END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
