#ATM Modules
import ipc
import analyzers
import auxiliaries
import auxiliaries_trade
import neural_networks
import constants
import teffunctions
from managers.workers.trade_manager.account import Account

#Python Modules
import time
import termcolor
import math
import json
import os
import traceback
import numpy
from collections import deque



#External Constants
_IPC_THREADTYPE_MT         = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT         = ipc._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = ipc._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = ipc._FAR_INVALIDFUNCTIONID

FORMATTEDDATATYPE_FETCHED    = constants.FORMATTEDDATATYPE_FETCHED
FORMATTEDDATATYPE_EMPTY      = constants.FORMATTEDDATATYPE_EMPTY
FORMATTEDDATATYPE_DUMMY      = constants.FORMATTEDDATATYPE_DUMMY
FORMATTEDDATATYPE_STREAMED   = constants.FORMATTEDDATATYPE_STREAMED
FORMATTEDDATATYPE_INCOMPLETE = constants.FORMATTEDDATATYPE_INCOMPLETE
KLINDEX_OPENTIME              = constants.KLINDEX_OPENTIME
KLINDEX_CLOSETIME             = constants.KLINDEX_CLOSETIME
KLINDEX_OPENPRICE             = constants.KLINDEX_OPENPRICE
KLINDEX_HIGHPRICE             = constants.KLINDEX_HIGHPRICE
KLINDEX_LOWPRICE              = constants.KLINDEX_LOWPRICE
KLINDEX_CLOSEPRICE            = constants.KLINDEX_CLOSEPRICE
KLINDEX_NTRADES               = constants.KLINDEX_NTRADES
KLINDEX_VOLBASE               = constants.KLINDEX_VOLBASE
KLINDEX_VOLQUOTE              = constants.KLINDEX_VOLQUOTE
KLINDEX_VOLBASETAKERBUY       = constants.KLINDEX_VOLBASETAKERBUY
KLINDEX_VOLQUOTETAKERBUY      = constants.KLINDEX_VOLQUOTETAKERBUY
KLINDEX_CLOSED                = constants.KLINDEX_CLOSED
KLINDEX_SOURCE                = constants.KLINDEX_SOURCE
DEPTHINDEX_OPENTIME           = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_CLOSETIME          = constants.DEPTHINDEX_CLOSETIME
DEPTHINDEX_BIDS5              = constants.DEPTHINDEX_BIDS5
DEPTHINDEX_BIDS4              = constants.DEPTHINDEX_BIDS4
DEPTHINDEX_BIDS3              = constants.DEPTHINDEX_BIDS3
DEPTHINDEX_BIDS2              = constants.DEPTHINDEX_BIDS2
DEPTHINDEX_BIDS1              = constants.DEPTHINDEX_BIDS1
DEPTHINDEX_BIDS0              = constants.DEPTHINDEX_BIDS0
DEPTHINDEX_ASKS0              = constants.DEPTHINDEX_ASKS0
DEPTHINDEX_ASKS1              = constants.DEPTHINDEX_ASKS1
DEPTHINDEX_ASKS2              = constants.DEPTHINDEX_ASKS2
DEPTHINDEX_ASKS3              = constants.DEPTHINDEX_ASKS3
DEPTHINDEX_ASKS4              = constants.DEPTHINDEX_ASKS4
DEPTHINDEX_ASKS5              = constants.DEPTHINDEX_ASKS5
DEPTHINDEX_CLOSED             = constants.DEPTHINDEX_CLOSED
DEPTHINDEX_SOURCE             = constants.DEPTHINDEX_SOURCE
ATINDEX_OPENTIME              = constants.ATINDEX_OPENTIME
ATINDEX_CLOSETIME             = constants.ATINDEX_CLOSETIME
ATINDEX_QUANTITYBUY           = constants.ATINDEX_QUANTITYBUY
ATINDEX_QUANTITYSELL          = constants.ATINDEX_QUANTITYSELL
ATINDEX_NTRADESBUY            = constants.ATINDEX_NTRADESBUY
ATINDEX_NTRADESSELL           = constants.ATINDEX_NTRADESSELL
ATINDEX_NOTIONALBUY           = constants.ATINDEX_NOTIONALBUY
ATINDEX_NOTIONALSELL          = constants.ATINDEX_NOTIONALSELL
ATINDEX_CLOSED                = constants.ATINDEX_CLOSED
ATINDEX_SOURCE                = constants.ATINDEX_SOURCE
METRICINDEX_OPENTIME          = constants.METRICINDEX_OPENTIME
METRICINDEX_CLOSETIME         = constants.METRICINDEX_CLOSETIME
METRICINDEX_OPENINTEREST      = constants.METRICINDEX_OPENINTEREST
METRICINDEX_OPENINTERESTVALUE = constants.METRICINDEX_OPENINTERESTVALUE
METRICINDEX_LONGSHORTRATIO    = constants.METRICINDEX_LONGSHORTRATIO
METRICINDEX_CLOSED            = constants.METRICINDEX_CLOSED
METRICINDEX_SOURCE            = constants.METRICINDEX_SOURCE
DEPTHBINS = constants.DEPTHBINS
COMMONDATAINDEXES = constants.COMMONDATAINDEXES

KLINE_INTERVAL_ID_1m  = constants.KLINE_INTERVAL_ID_1m
KLINE_INTERVAL_ID_3m  = constants.KLINE_INTERVAL_ID_3m
KLINE_INTERVAL_ID_5m  = constants.KLINE_INTERVAL_ID_5m
KLINE_INTERVAL_ID_15m = constants.KLINE_INTERVAL_ID_15m
KLINE_INTERVAL_ID_30m = constants.KLINE_INTERVAL_ID_30m
KLINE_INTERVAL_ID_1h  = constants.KLINE_INTERVAL_ID_1h
KLINE_INTERVAL_ID_2h  = constants.KLINE_INTERVAL_ID_2h
KLINE_INTERVAL_ID_4h  = constants.KLINE_INTERVAL_ID_4h
KLINE_INTERVAL_ID_6h  = constants.KLINE_INTERVAL_ID_6h
KLINE_INTERVAL_ID_8h  = constants.KLINE_INTERVAL_ID_8h
KLINE_INTERVAL_ID_12h = constants.KLINE_INTERVAL_ID_12h
KLINE_INTERVAL_ID_1d  = constants.KLINE_INTERVAL_ID_1d
KLINE_INTERVAL_ID_3d  = constants.KLINE_INTERVAL_ID_3d
KLINE_INTERVAL_ID_1W  = constants.KLINE_INTERVAL_ID_1W
KLINE_INTERVAL_ID_1M  = constants.KLINE_INTERVAL_ID_1M
KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S

DUMMYFRAMES = constants.DUMMYFRAMES



#Internal Constants
_FETCHCHUNKSIZE    = 1440
_PROCESSTIMEOUT_NS = 100e6
_TRADINGFEE                = auxiliaries_trade.TRADINGFEE
_MARKETOPENLOSSRATE        = 0.0015
_BASEASSETALLOCATABLERATIO = 0.95
_ASSETPRECISIONS = {'USDT': 8,
                    'USDC': 8}
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
        self.__orders    = dict()

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
                                      'aggTrade': analyzers.aggregator_aggTrade,
                                      'metric':   analyzers.aggregator_metric}
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
            dRaw[symbol] = {target: dict() for target in ('kline', 'depth', 'aggTrade', 'metric')}
            dAgg[symbol] = dict()
            dTSs[symbol] = {'raw': {target: deque() for target in ('kline', 'depth', 'aggTrade', 'metric')}}
            lcas[symbol] = dict()
            lTSs[symbol] = dict()
            dAgg_symbol = dAgg[symbol]
            dTSs_symbol = dTSs[symbol]
            lcas_symbol = lcas[symbol]
            lTSs_symbol = lTSs[symbol]
            for iID, aParams_iID in simAnalyzers[cacCode]['analysisParams'].items():
                dAgg_symbol[iID] = {target: dict()  for target in ('kline', 'depth', 'aggTrade', 'metric')}
                dTSs_symbol[iID] = {target: deque() for target in ('kline', 'depth', 'aggTrade', 'metric')}
                lcas_symbol[iID] = {target: dict()  for target in ('kline', 'depth', 'aggTrade', 'metric')}
                lTSs_symbol[iID] = {target: deque() for target in ('kline', 'depth', 'aggTrade', 'metric')}
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
                                       'metrics':        dAgg_symbol_iID['metric'],
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
        func_gitct   = auxiliaries_trade.getInitializedTradeControlTracker
        func_gnitt   = auxiliaries.getNextIntervalTickTimestamp
        for symbol, position_def in self.__positions_def.items():
            #[5-1]: Generation Range Determination
            drs_min = None
            drs_max = None
            for t in ('kline', 'depth', 'aggTrade', 'metric'):
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
            #[5-2]: Position Data
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
                           #Variation Tracking
                           '_quantity_new':      0,
                           '_entryPrice_new':    None,
                           '_liquidationReport': None,
                           #Trade Control
                           'tradeControlTracker':   func_gitct(),
                           '_tradeHandlers':        deque(),
                           '_orderCreationRequest': None,
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
                lIdx   = 0
                laCode = f'NNA_{lIdx}_LineActive'
                while laCode in cac_iID:
                    if cac_iID[laCode]:
                        nnCode = cac_iID[f'NNA_{lIdx}_NeuralNetworkCode']
                        nns[nnCode] = None
                    lIdx += 1
                    laCode = f'NNA_{lIdx}_LineActive'
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
            for target in ('kline', 'depth', 'aggTrade', 'metric'):
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
    #---L1: Simulation Process Main
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
        positions = self.__positions
        func_hkls   = self.__handleKlines
        func_pths   = self.__processTradeHandlers
        func_pts    = self.__processTrades
        func_uAcc   = self.__updateAccount
        func_rOrder = self.__removeOrder
        func_ga     = self.__generateAnalysis
        func_hars   = self.__handleAnalysisResults
        func_uwbta  = self.__updateWalletBalanceTrendAnalysis
        func_upr    = self.__updatePeriodicReport
        func_gnitt  = auxiliaries.getNextIntervalTickTimestamp
        t_begin_ns   = time.perf_counter_ns()
        t_elapsed_ns = 0
        while naTarget <= lp and t_elapsed_ns < _PROCESSTIMEOUT_NS:
            #[3-1]: Perform Simulation
            #---[3-1-1]: Klines Handling & Trade Handlers Processing (OCR Generation)
            func_hkls(timestamp = naTarget)
            #---[3-1-2]: Trade Processing & Account Update
            updateAccount = True
            for symbol, position in positions.items():
                #[3-1-2-1]: Generation Range Check
                gr_symbol = position['GR']
                if gr_symbol is None or not (gr_symbol[0] <= naTarget <= gr_symbol[1]):
                    continue
                #[3-1-2-2]: Process Loop
                while True:
                    #[3-1-2-2-1]: Trade Handlers Processing (OCR & Order Generation)
                    func_pths(symbol = symbol, timestamp = naTarget)
                    #[3-1-2-2-2]: Trades Processing (OCR & Orders Processing) & Account Update
                    if not func_pts(symbol = symbol, timestamp = naTarget):
                        break
                    func_uAcc(timestamp = naTarget)
                    updateAccount = False
            if updateAccount:
                func_uAcc(timestamp = naTarget)
            #---[3-1-4]: OCR & Trade Handlers Clearing
            for symbol, position in positions.items():
                ocr = position['_orderCreationRequest']
                if ocr is not None and ocr['result'] is None:
                    func_rOrder(orderCode = ocr['orderCode'])
                    position['_orderCreationRequest'] = None
                    self.__allocateBalance
                position['_tradeHandlers'].clear()
            
            #---[3-1-5]: Analysis Generation & Handling
            func_hars(timestamp = naTarget, linearizedAnalyses = func_ga(timestamp = naTarget))
            #---[3-1-6]: Wallet Balance Trend Analysis & Periodic Report Update
            func_uwbta(timestamp = naTarget)
            func_upr(timestamp   = naTarget)

            #[3-2]: Timer Update
            t_elapsed_ns = time.perf_counter_ns()-t_begin_ns

            #[3-3]: Fetch Requests Dispatch
            if naTarget == nfPoint:
                self.__sendMarketDataFetchRequests()
                nfPoint = self.__data_nextFetchPoint

            #[3-4]: Next Analysis Target & Completion Update
            naTarget = func_gnitt(intervalID = KLINTERVAL, timestamp = naTarget, nTicks = 1)

            #[3-5]: Completion Check
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
        self.__updateCompletion(completion = completion_new)

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
            for target in ('kline', 'depth', 'aggTrade', 'metric'):
                dRaw_symbol_target     = dRaw_symbol[target]
                dTSs_symbol_raw_target = dTSs_symbol_raw[target]
                for ts in tTSs_raw:
                    if ts in dRaw_symbol_target:
                        continue
                    if not (gr_symbol[0] <= ts <= gr_symbol[1]):
                        continue
                    ts_close = func_gnitt(intervalID = KLINTERVAL, timestamp = ts, nTicks = 1)-1
                    dRaw_symbol_target[ts] = (ts, ts_close)+DUMMYFRAMES[target]
                    dTSs_symbol_raw_target.append(ts)
                dTSs_symbol_raw[target] = deque(sorted(dTSs_symbol_raw_target))

        #[3]: Last Prepared Update
        self.__data_lastPrepared = range_end

    def __handleKlines(self, timestamp):
        #[1]: Instances
        positions = self.__positions
        dRaw      = self.__data_raw

        #[2]: Generate Analysis and Handle Generated Analysis Results
        for symbol, position in positions.items():
            #[2-1]: Instances
            position_def = self.__positions_def[symbol]
            position     = self.__positions[symbol]
            tc           = self.__tradeConfigurations[position_def['tradeConfigurationCode']]
            precisions   = position_def['precisions']
            kline     = dRaw[symbol]['kline'][timestamp]

            #[2-2]: Force Exit Check
            tradeHandler_checkList = {'FSLIMMED': None,
                                      'FSLCLOSE': None}
            if position['quantity'] != 0 and not (kline[KLINDEX_OPENPRICE] is None or kline[KLINDEX_LOWPRICE] is None or kline[KLINDEX_HIGHPRICE] is None or kline[KLINDEX_CLOSEPRICE] is None):
                #FSL IMMED
                if tc['fullStopLossImmediate'] is not None:
                    #<SHORT>
                    if position['quantity'] < 0:
                        price_FSL = round(position['entryPrice']*(1+tc['fullStopLossImmediate']), precisions['price'])
                        if price_FSL <= kline[KLINDEX_HIGHPRICE]: 
                            tradeHandler_checkList['FSLIMMED'] = ('BUY', price_FSL)
                    #<LONG>
                    elif 0 < position['quantity']:
                        price_FSL = round(position['entryPrice']*(1-tc['fullStopLossImmediate']), precisions['price'])
                        if kline[KLINDEX_LOWPRICE] <= price_FSL: 
                            tradeHandler_checkList['FSLIMMED'] = ('SELL', price_FSL)
                #FSL CLOSE
                if tc['fullStopLossClose'] is not None:
                    #<SHORT>
                    if position['quantity'] < 0:
                        price_FSL = round(position['entryPrice']*(1+tc['fullStopLossClose']), precisions['price'])
                        if price_FSL <= kline[KLINDEX_CLOSEPRICE]: 
                            tradeHandler_checkList['FSLCLOSE'] = ('BUY', kline[KLINDEX_CLOSEPRICE])
                    #<LONG>
                    elif 0 < position['quantity']:
                        price_FSL = round(position['entryPrice']*(1-tc['fullStopLossClose']), precisions['price'])
                        if kline[KLINDEX_CLOSEPRICE] <= price_FSL: 
                            tradeHandler_checkList['FSLCLOSE'] = ('SELL', kline[KLINDEX_CLOSEPRICE])

            #[2-3]: Trade Handlers Execution
            tradeHandlers = []
            if   tradeHandler_checkList['FSLIMMED'] is not None: tradeHandlers = ['FSLIMMED',]
            elif tradeHandler_checkList['FSLCLOSE'] is not None: tradeHandlers = ['FSLCLOSE',]
    
            #[2-4]: Finally
            position_ths = position['_tradeHandlers']
            for thType in tradeHandlers:
                side, price = tradeHandler_checkList[thType]
                th = {'type':      thType,
                      'orderType': 'MARKET',
                      'side':      side,
                      'tefVal':    None,
                      'timestamp': kline[KLINDEX_OPENTIME],
                      'price':     price}
                position_ths.append(th)

    def __processTradeHandlers(self, symbol, timestamp):
        #[1]: Instances
        position     = self.__positions[symbol]
        position_def = self.__positions_def[symbol]
        asset        = self.__assets[position_def['quoteAsset']]
        tc           = self.__tradeConfigurations[position_def['tradeConfigurationCode']]
        tradeHandlers = position['_tradeHandlers']
        precisions    = position_def['precisions']

        #[2]: OCR Check
        if position['_orderCreationRequest'] is not None: 
            return
        
        #[3]: Trade Handlers Processing
        while tradeHandlers:
            #[3-1]: Trade Handler
            th = tradeHandlers.popleft()
            th_type      = th['type']
            th_orderType = th['orderType']
            th_side      = th['side']
            th_tefVal    = th['tefVal']
            th_timestamp = th['timestamp']
            th_price     = th['price']

            #[3-2]: Handling
            #---[3-2-1]: ENTRY
            if th_type == 'ENTRY':
                #[3-2-1-1]: Balance Commitment Check
                balance_allocated = position['allocatedBalance'] or self.__allocateBalance(symbol = symbol, apply = False)
                balance_committed = abs(position['quantity'])*position['entryPrice']/tc['leverage'] if position['entryPrice'] is not None else 0
                balance_toCommit  = balance_allocated*abs(th_tefVal)
                balance_toEnter   = balance_toCommit-balance_committed
                if not (0 < balance_toEnter): 
                    continue
                
                balance_toEnter_eff = min(balance_toEnter, asset['availableBalance'])
                if not (0 < balance_toEnter_eff): 
                    continue

                #[3-2-1-2]: Quantity Determination
                quantity_minUnit = pow(10, -precisions['quantity'])
                quantity         = round(int((balance_toEnter_eff/position['currentPrice']*tc['leverage'])/quantity_minUnit)*quantity_minUnit, precisions['quantity'])
                if quantity <= 0: 
                    continue

                #[3-2-1-3]: Side Confirm
                if not ((position['quantity'] <= 0 and th_side == 'SELL') or \
                        (0 <= position['quantity'] and th_side == 'BUY')): 
                    continue

                #[3-2-1-4]: Finally
                self.__allocateBalance(symbol = symbol, apply = True)
                self.__orderCreationRequest_generate(symbol          = symbol,
                                                     logicSource     = 'ENTRY',
                                                     orderType       = th_orderType,
                                                     side            = th_side,
                                                     quantity        = quantity,
                                                     price           = th_price,
                                                     tcTrackerUpdate = None)
                return
                
            #---[3-2-2]: CLEAR
            elif th_type == 'CLEAR':
                #[3-2-2-1]: Quantity Determination
                quantity = round(abs(position['quantity']), precisions['quantity'])
                if not 0 < quantity: 
                    continue

                #[3-2-2-2]: Side Confirm
                if not ((position['quantity'] < 0 and th_side == 'BUY') or \
                        (0 < position['quantity'] and th_side == 'SELL')): 
                    continue

                #[3-2-2-3]: Finally
                self.__orderCreationRequest_generate(symbol          = symbol,
                                                     logicSource     = 'CLEAR',
                                                     orderType       = th_orderType,
                                                     side            = th_side,
                                                     quantity        = quantity,
                                                     price           = th_price,
                                                     tcTrackerUpdate = None)
                return
                
            #---[3-2-3]: EXIT
            elif th_type == 'EXIT':
                #[3-2-3-1]: Balance Commitment Check
                balance_allocated = position['allocatedBalance'] or self.__allocateBalance(symbol = symbol, apply = False)
                balance_committed = abs(position['quantity'])*position['entryPrice']/tc['leverage'] if position['entryPrice'] is not None else 0
                balance_toCommit  = balance_allocated*abs(th_tefVal)
                balance_toEnter   = balance_toCommit-balance_committed
                if not (balance_toEnter < 0): 
                    continue

                #[3-2-3-2]: Quantity Determination
                if th_tefVal == 0.0:
                    quantity = abs(position['quantity'])
                else:
                    quantity_minUnit = pow(10, -precisions['quantity'])
                    quantity         = round(int((-balance_toEnter/position['entryPrice']*tc['leverage'])/quantity_minUnit)*quantity_minUnit, precisions['quantity'])
                if quantity < 0: 
                    continue
                if quantity == 0: 
                    continue

                #[3-2-3-3]: Side Confirm
                if not ((position['quantity'] < 0 and th_side == 'BUY') or \
                        (0 < position['quantity'] and th_side == 'SELL')): 
                    continue

                #[3-2-3-4]: Finally
                self.__orderCreationRequest_generate(symbol          = symbol,
                                                     logicSource     = 'EXIT',
                                                     orderType       = th_orderType,
                                                     side            = th_side,
                                                     quantity        = quantity,
                                                     price           = th_price,
                                                     tcTrackerUpdate = None)
                return

            #---[3-2-4]: FSLIMMED & FSLCLOSE
            elif th_type == 'FSLIMMED' or th_type == 'FSLCLOSE':
                #[3-2-4-1]: Quantity Determination
                quantity = round(abs(position['quantity']), precisions['quantity'])
                if not (0 < quantity): 
                    continue

                #[3-2-4-2]: Side Confirm
                if not ((position['quantity'] < 0 and th_side == 'BUY') or \
                        (0 < position['quantity'] and th_side == 'SELL')): 
                    continue

                #[3-2-4-3]: Finally
                if   position['quantity'] < 0: slTriggeredSide = 'SHORT'
                elif 0 < position['quantity']: slTriggeredSide = 'LONG'
                self.__orderCreationRequest_generate(symbol          = symbol,
                                                     logicSource     = th_type,
                                                     orderType       = th_orderType,
                                                     side            = th_side,
                                                     quantity        = quantity,
                                                     price           = th_price,
                                                     tcTrackerUpdate = {'slExited': {'onComplete': (slTriggeredSide, th_timestamp), 
                                                                                     'onPartial':  (slTriggeredSide, th_timestamp), 
                                                                                     'onFail':     (slTriggeredSide, th_timestamp)}})
                return
            
    def __processTrades(self, symbol, timestamp):
        #[1]: Instances
        position       = self.__positions[symbol]
        position_def   = self.__positions_def[symbol]
        orders         = self.__orders
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = timestamp, nTicks = -1)
        ocr            = position['_orderCreationRequest']
        price_liq      = position['liquidationPrice']
        precisions     = position_def['precisions']
        dRaw_symbol    = self.__data_raw[symbol]
        kline          = dRaw_symbol['kline'][timestamp]
        depth_prev     = dRaw_symbol['depth'].get(timestamp_prev, None)
        processTarget  = None

        #[2]: Kline Check
        if (kline[KLINDEX_OPENPRICE] is None or kline[KLINDEX_LOWPRICE] is None or kline[KLINDEX_HIGHPRICE] is None or kline[KLINDEX_CLOSEPRICE] is None):
            return
            
        #[3]: Liquidation Check
        liquidation = None
        if price_liq is not None:
            if   position['quantity'] < 0 and (price_liq <= kline[KLINDEX_HIGHPRICE]): liquidation = (price_liq - kline[KLINDEX_OPENPRICE])
            elif 0 < position['quantity'] and (kline[KLINDEX_LOWPRICE] <= price_liq):  liquidation = (kline[KLINDEX_OPENPRICE] - price_liq)

        #[4]: Order Check
        order                    = None if ocr is None else orders.get(ocr['orderCode'], None) 
        order_execution_distance = None
        if order is not None:
            o_side      = order['side']
            o_orderType = order['orderType']
            o_quantity  = order['quantity']
            o_price     = order['price']
            o_recompare = order['recompare']
            if o_orderType == 'LIMIT':
                if   o_side == 'BUY'  and (kline[KLINDEX_LOWPRICE] < o_price):  order_execution_distance = max(0, kline[KLINDEX_OPENPRICE] - o_price)
                elif o_side == 'SELL' and (o_price < kline[KLINDEX_HIGHPRICE]): order_execution_distance = max(0, o_price - kline[KLINDEX_OPENPRICE])
            elif o_orderType == 'MARKET':
                if o_recompare: 
                    if   o_side == 'BUY':  order_execution_distance = max(0, kline[KLINDEX_OPENPRICE] - o_price)
                    elif o_side == 'SELL': order_execution_distance = max(0, o_price - kline[KLINDEX_OPENPRICE])
                else: 
                    order_execution_distance = 0

        #[5]: Process Target Determination
        if liquidation is None:
            if order_execution_distance is not None: processTarget = 'ORDER'
        else:
            if order_execution_distance is None: processTarget = 'LIQUIDATION'
            else:                                processTarget = 'ORDER' if order_execution_distance < liquidation else 'LIQUIDATION'

        #[6]: Target Processing
        #---[6-1]: Liquidation
        if processTarget == 'LIQUIDATION': 
            self.__liquidatePosition(timestamp = timestamp, symbol = symbol)
            return True

        #---[6-2]: Order
        elif processTarget == 'ORDER':
            #[6-2-1]: Trade Parameters Determination
            if   o_orderType == 'LIMIT':  t_price = o_price
            elif o_orderType == 'MARKET': t_price = auxiliaries_trade.getSlippedPrice(side            = o_side,
                                                                                      quantity        = o_quantity,
                                                                                      reference_price = o_price,
                                                                                      depth           = depth_prev,
                                                                                      precision_price = precisions['price'])

            #[6-2-2]: Simulated Trade Processing
            self.__processTrade(timestamp = timestamp,
                                symbol    = symbol,
                                side      = o_side,
                                orderType = o_orderType,
                                quantity  = o_quantity,
                                price     = t_price)

            #[6-2-3]: Clear Order
            del orders[ocr['orderCode']]
            return True

        #[7]: If No Trades Are Processed, Return False
        return False
            
    def __updateAccount(self, timestamp):
        #[1]: Instances
        assets_def    = self.__assets_def
        assets        = self.__assets
        positions_def = self.__positions_def
        positions     = self.__positions
        dRaw          = self.__data_raw
        func_rlr         = self.__readLiquidationReport
        func_ct          = self.__checkTrade
        func_rab         = self.__releaseAllocatedBalance
        get_mmraa        = auxiliaries_trade.getMaintenanceMarginRateAndAmount
        compute_liqPrice = auxiliaries_trade.computeLiquidationPrice

        #[2]: Update Positions
        for symbol, position in positions.items():
            #[2-1]: Instances
            position_def = positions_def[symbol]
            kl           = dRaw[symbol]['kline'].get(timestamp, None)
            kl_cp        = None if kl is None else kl[KLINDEX_CLOSEPRICE]
            cp           = position['currentPrice'] if kl_cp is None else kl_cp

            #[2-2]: Liquidation & OCR Check
            if not func_rlr(symbol = symbol):
                func_ct(symbol         = symbol, 
                        quantity_new   = position['_quantity_new'], 
                        entryPrice_new = position['_entryPrice_new'])
            position['quantity']   = position['_quantity_new']
            position['entryPrice'] = position['_entryPrice_new']
            if position['quantity'] == 0 and 0 < position['allocatedBalance']:
                func_rab(symbol = symbol)

            #[2-3]: Computed Values
            if cp is None:
                position['positionInitialMargin'] = None
                position['maintenanceMargin']     = None
                position['unrealizedPNL']         = None
            else:
                position['currentPrice'] = cp
                position['positionInitialMargin'] = round(cp*abs(position['quantity'])/position_def['leverage'], position_def['precisions']['quote'])
                if position['quantity'] == 0:
                    position['maintenanceMargin'] = 0
                else:
                    notional_cur = abs(position['quantity']) * cp
                    mmr, mma = get_mmraa(positionSymbol=symbol, notional=notional_cur)
                    position['maintenanceMargin'] = round(notional_cur*mmr - mma, position_def['precisions']['quote'])
                if   position['quantity'] < 0:  position['unrealizedPNL'] = round((position['entryPrice']-cp)*abs(position['quantity']), position_def['precisions']['quote'])
                elif position['quantity'] == 0: position['unrealizedPNL'] = None
                elif 0 < position['quantity']:  position['unrealizedPNL'] = round((cp-position['entryPrice'])*abs(position['quantity']), position_def['precisions']['quote'])

        #[3]: Update Assets
        for assetName, asset in assets.items():
            asset_def = assets_def[assetName]
            asset['isolatedPositionInitialMargin'] = sum(pim  for symbol in asset_def['_positionSymbols_isolated'] if (pim  := positions[symbol]['positionInitialMargin']) is not None)
            asset['crossPositionInitialMargin']    = sum(pim  for symbol in asset_def['_positionSymbols_crossed']  if (pim  := positions[symbol]['positionInitialMargin']) is not None)
            asset['crossMaintenanceMargin']        = sum(mm   for symbol in asset_def['_positionSymbols_crossed']  if (mm   := positions[symbol]['maintenanceMargin'])     is not None)
            asset['isolatedUnrealizedPNL']         = sum(uPNL for symbol in asset_def['_positionSymbols_isolated'] if (uPNL := positions[symbol]['unrealizedPNL'])         is not None)
            asset['crossUnrealizedPNL']            = sum(uPNL for symbol in asset_def['_positionSymbols_crossed']  if (uPNL := positions[symbol]['unrealizedPNL'])         is not None)
            asset['walletBalance']      = asset['crossWalletBalance']+asset['isolatedWalletBalance']
            asset['unrealizedPNL']      = asset['isolatedUnrealizedPNL']+asset['crossUnrealizedPNL']
            asset['marginBalance']      = asset['walletBalance']+asset['unrealizedPNL']
            asset['availableBalance']   = asset['crossWalletBalance']-asset['crossPositionInitialMargin']+asset['crossUnrealizedPNL']
            asset['allocatableBalance'] = round((asset['walletBalance'])*_BASEASSETALLOCATABLERATIO*asset_def['allocationRatio'], _ASSETPRECISIONS[assetName])
            if asset['allocatableBalance'] < 0: asset['allocatableBalance'] = 0

        #[4]: Update Secondary Position Data
        for symbol, position in positions.items():
            #[4-1]: Instances
            position_def = positions_def[symbol]
            asset        = assets[position_def['quoteAsset']]

            #[4-2]: None Quantity
            if position['quantity'] is None:
                position['commitmentRate']   = None
                position['liquidationPrice'] = None
                position['riskLevel']        = None

            #[4-3]: Valid Quantity
            else:
                #[4-3-1]: Absolute Quantity
                quantity     = position['quantity']
                quantity_abs = abs(quantity)

                #[4-3-2]: Commitment Rate
                if quantity_abs != 0 and position_def['leverage'] is not None and position['allocatedBalance'] != 0: 
                    position['commitmentRate'] = round((quantity_abs*position['entryPrice']/position_def['leverage'])/position['allocatedBalance'], 5)
                else: 
                    position['commitmentRate'] = None
                
                #[4-3-3]: Liquidation Price
                if position_def['isolated']: wb = position['isolatedWalletBalance']
                else:                        wb = asset['crossWalletBalance']
                liqPrice = compute_liqPrice(positionSymbol    = symbol,
                                            walletBalance     = wb,
                                            quantity          = position['quantity'],
                                            entryPrice        = position['entryPrice'],
                                            currentPrice      = position['currentPrice'],
                                            maintenanceMargin = position['maintenanceMargin'],
                                            upnl              = position['unrealizedPNL'],
                                            isolated          = position_def['isolated'],
                                            mm_crossTotal     = asset['crossMaintenanceMargin'],
                                            upnl_crossTotal   = asset['crossUnrealizedPNL'])
                position['liquidationPrice'] = None if liqPrice is None else round(liqPrice, position_def['precisions']['price'])
                
                #[4-3-4]: Risk Level
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

        #[5]: Update Secondary Asset Data
        for assetName, asset in assets.items():
            asset_def = assets_def[assetName]

            #[5-1]: Allocated Balance
            allocatedBalanceSum = sum(positions[symbol]['allocatedBalance'] for symbol in asset_def['_positionSymbols'])
            if asset['allocatableBalance'] < allocatedBalanceSum:
                reduction_ratio = asset['allocatableBalance'] / allocatedBalanceSum
                allocatedBalanceSum_new = 0
                for symbol in asset_def['_positionSymbols']:
                    position = positions[symbol]
                    if 0 < position['allocatedBalance']:
                        qPrecision = positions_def[symbol]['precisions']['quote']
                        position['allocatedBalance'] = round(position['allocatedBalance'] * reduction_ratio, qPrecision)
                        allocatedBalanceSum_new += position['allocatedBalance']
                allocatedBalanceSum = allocatedBalanceSum_new
            asset['allocatedBalance'] = allocatedBalanceSum

            #[5-2]: Commitment Rate
            commitmentRate_pSymbols = [symbol for symbol in asset_def['_positionSymbols'] if positions[symbol]['commitmentRate'] is not None]
            if commitmentRate_pSymbols:
                commitmentRate_sum     = sum(positions[symbol]['commitmentRate'] for symbol in commitmentRate_pSymbols)
                commitmentRate_average = round(commitmentRate_sum/len(commitmentRate_pSymbols), 5)
            else: 
                commitmentRate_average = None
            asset['commitmentRate'] = commitmentRate_average

            #[5-3]: Risk Level
            riskLevel_pSymbols = [symbol for symbol in asset_def['_positionSymbols'] if (positions[symbol]['riskLevel'] != None)]
            if riskLevel_pSymbols:
                riskLevel_sum     = sum(positions[symbol]['riskLevel'] for symbol in riskLevel_pSymbols)
                riskLevel_average = round(riskLevel_sum/len(riskLevel_pSymbols), 5)
            else: 
                riskLevel_average = None
            asset['riskLevel'] = riskLevel_average

    def __generateAnalysis(self, timestamp):
        #[1]: Instances
        aExport       = self.__analysisExport
        positions_def = self.__positions_def
        positions     = self.__positions
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
        las = dict()

        #[2]: Generate Analysis and Handle Generated Analysis Results
        for symbol, position in positions.items():
            #[2-1]: Instances
            gr_symbol = position['GR']
            if gr_symbol is None or not (gr_symbol[0] <= timestamp <= gr_symbol[1]):
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

            #[2-3]: Analysis Generation
            bdRawTS_remove_min = None
            for iID in dAgg_symbol:
                #[2-3-1]: Instances
                aggTS = func_gnitt(intervalID = iID, timestamp = timestamp, nTicks = 0)
                dAgg_symbol_iID    = dAgg_symbol[iID]
                dTSs_symbol_iID    = dTSs_symbol[iID]
                lcas_symbol_iID    = lcas_symbol[iID]
                lTSs_symbol_iID    = lTSs_symbol[iID]
                aParams_iID        = aParams[iID]
                atp_sorted_iID     = atp_sorted[iID]
                aKwargs_symbol_iID = aKwargs_symbol[iID]

                #[2-3-2]: Aggregation
                for target in ('kline', 'depth', 'aggTrade', 'metric'):
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
                                rawOpenTS      = timestamp,
                                aggOpenTS      = aggTS,
                                aggIntervalID  = iID,
                                precisions     = precisions)
                    if aggTS in lcas_symbol_iID_target:
                        if not lTSs_symbol_iID_target or lTSs_symbol_iID_target[-1] != aggTS:
                            lTSs_symbol_iID_target.append(aggTS)

                #[2-3-3]: Analysis Generation
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

                #[2-3-4]: Memory Optimization (Analysis & Aggregated Base Data)
                #---[2-3-4-1]: Analysis
                for aCode, nAr_keep in nAR_keeps.items():
                    arTS_remove_min = func_gnitt(intervalID = iID, timestamp = aggTS, nTicks = -(nAr_keep-1))-1
                    dAgg_symbol_iID_aCode = dAgg_symbol_iID[aCode]
                    dTSs_symbol_iID_aCode = dTSs_symbol_iID[aCode]
                    while dTSs_symbol_iID_aCode and dTSs_symbol_iID_aCode[0] <= arTS_remove_min:
                        ts_remove = dTSs_symbol_iID_aCode.popleft()
                        del dAgg_symbol_iID_aCode[ts_remove]
                #---[2-3-4-2]: Base Data
                bdTS_remove_min = func_gnitt(intervalID = iID, timestamp = aggTS, nTicks = -(nBD_keep_max-1))-1
                for target in ('kline', 'depth', 'aggTrade', 'metric'):
                    dAgg_symbol_iID_target = dAgg_symbol_iID[target]
                    dTSs_symbol_iID_target = dTSs_symbol_iID[target]
                    lcas_symbol_iID_target = lcas_symbol_iID[target]
                    lTSs_symbol_iID_target = lTSs_symbol_iID[target]
                    #[2-3-4-2-1]: Last Aggregated Data
                    while dTSs_symbol_iID_target and dTSs_symbol_iID_target[0] <= bdTS_remove_min:
                        ts_remove = dTSs_symbol_iID_target.popleft()
                        del dAgg_symbol_iID_target[ts_remove]
                    #[2-3-4-2-2]: Last Closed Aggregation
                    while lTSs_symbol_iID_target and lTSs_symbol_iID_target[0] <= bdTS_remove_min:
                        ts_remove = lTSs_symbol_iID_target.popleft()
                        del lcas_symbol_iID_target[ts_remove]
                if bdRawTS_remove_min is None or bdTS_remove_min < bdRawTS_remove_min: bdRawTS_remove_min = bdTS_remove_min

            #[2-4]: Memory Optimization (Raw Base Data)
            for target in ('kline', 'depth', 'aggTrade', 'metric'):
                dRaw_target     = dRaw_symbol[target]
                dTSs_raw_target = dTSs_symbol_raw[target]
                while dTSs_raw_target and dTSs_raw_target[0] <= bdRawTS_remove_min:
                    ts_remove = dTSs_raw_target.popleft()
                    del dRaw_target[ts_remove]

            #[2-5]: Analysis Result Linearization
            la = func_lAnalysis(dataRaw        = dRaw_symbol,
                                dataAggregated = dAgg_symbol, 
                                analysisPairs  = atp_sorted, 
                                timestamp      = timestamp)
            
            #[2-6]: Linearized Analysis Export
            las[symbol] = la
            if aExport:
                ae = position['AE']
                #[4-9-1]: Index Identifiers
                if ae['indexIdentifier'] is None: 
                    ae_keys = sorted(la)
                    ae_ii   = {k: i for i, k in enumerate(ae_keys)}
                    ae['indexIdentifier']        = ae_ii
                    ae['linearizedAnalysisKeys'] = ae_keys
                #[4-9-2]: Tuplization & Appending
                aLinearized_tuple = tuple(la[laKey] for laKey in ae['linearizedAnalysisKeys'])
                position['AE']['data'].append(aLinearized_tuple)

        #[3]: Linearized Analyses Return
        return las
    
    def __handleAnalysisResults(self, timestamp, linearizedAnalyses):
        #[1]: Instances
        positions     = self.__positions
        positions_def = self.__positions_def

        #[2]: Generate Analysis and Handle Generated Analysis Results
        for symbol, position in positions.items():
            #[2-1]: Instances
            gr_symbol = position['GR']
            if gr_symbol is None or not (gr_symbol[0] <= timestamp <= gr_symbol[1]):
                continue
            position_def = positions_def[symbol]
            precisions   = position_def['precisions']
            tcTracker    = position['tradeControlTracker']
            cp           = position['currentPrice']
            tc           = self.__tradeConfigurations[position_def['tradeConfigurationCode']]
    
            #[2-2]: Target Exposure Factor
            try:
                tef_dir, tef_val = teffunctions.TEFFUNCTIONS_GET_TEF[tc['teff_functionType']](params             = tc['teff_functionParams'],
                                                                                              linearizedAnalysis = linearizedAnalyses[symbol],
                                                                                              tcTracker_model    = tcTracker['teff_model'])
            except Exception as e:
                print(termcolor.colored(f"[SIMULATOR{self.simulatorIndex}] An Unexpected Error Occurred While Attempting To Compute Target Exposure Factor In Simulation.\n"
                                        f" * Simulation Code:   {self.__simulationCode}\n"
                                        f" * TEF Function Type: {tc['teff_functionType']}\n"
                                        f" * Position Symbol:   {symbol}\n"
                                        f" * Timestamp:         {timestamp}\n"
                                        f" * Error:             {e}\n"
                                        f" * Detailed Trace:    {traceback.format_exc()}", 
                                        'light_red'))
                continue
            if (tef_dir not in (None, 'SHORT', 'LONG') or 
                not isinstance(tef_val, (int, float))  or 
                not (-1 <= tef_val <= 1)):
                print(termcolor.colored(f"[SIMULATOR{self.simulatorIndex}] An Unexpected TEF Result Detected. Direction Must Be None, 'SHORT' Or 'LONG', And The Value Must Be An Integer Or Float In Range [-1.0, 1.0].\n"
                                        f" * Simulation Code:   {self.__simulationCode}\n"
                                        f" * TEF Function Type: {tc['teff_functionType']}\n"
                                        f" * TEF Direction:     {tef_dir}\n"
                                        f" * TEF Value:         {tef_val}\n"
                                        f" * Position Symbol:   {symbol}\n"
                                        f" * Timestamp:         {timestamp}", 
                                        'light_red'))
                continue
    
            #[2-3]: SL Exit Flag
            if tcTracker['slExited'] != tef_dir: 
                tcTracker['slExited'] = None
    
            #[2-4]: Trade Handlers Determination
            tradeHandler_checkList = {'ENTRY': None,
                                      'CLEAR': None,
                                      'EXIT':  None}
            #---[2-4-1]: CheckList 1: CLEAR
            if   position['quantity'] < 0 and tef_dir != 'SHORT': tradeHandler_checkList['CLEAR'] = 'BUY'
            elif 0 < position['quantity'] and tef_dir != 'LONG':  tradeHandler_checkList['CLEAR'] = 'SELL'
            #---[2-4-2]: CheckList 2: ENTRY & EXIT
            pslCheck = tc['postStopLossReentry'] or (tcTracker['slExited'] is None)
            if tef_dir == 'SHORT':  
                if pslCheck and tc['direction'] in ('BOTH', 'SHORT'): 
                    tradeHandler_checkList['ENTRY'] = 'SELL'
                tradeHandler_checkList['EXIT'] = 'BUY'
            elif tef_dir == 'LONG':
                if pslCheck and tc['direction'] in ('BOTH', 'LONG'): 
                    tradeHandler_checkList['ENTRY'] = 'BUY'
                tradeHandler_checkList['EXIT'] = 'SELL'
            elif tef_dir is None:
                if   position['quantity'] < 0: tradeHandler_checkList['EXIT'] = 'BUY'
                elif 0 < position['quantity']: tradeHandler_checkList['EXIT'] = 'SELL'
    
            #[2-5]: Trade Handlers Determination
            tradeHandlers = []
            if tradeHandler_checkList['CLEAR'] is not None: tradeHandlers.append('CLEAR')
            if tradeHandler_checkList['EXIT']  is not None: tradeHandlers.append('EXIT')
            if tradeHandler_checkList['ENTRY'] is not None: tradeHandlers.append('ENTRY')
    
            #[2-6]: Update Trade Handlers
            position_ths = position['_tradeHandlers']
            tc_orderType   = tc['orderType']
            tc_orderOffset = tc['orderOffset']
            for thType in tradeHandlers:
                side = tradeHandler_checkList[thType]
                if tc_orderType == 'LIMIT':
                    if   side == 'BUY':  price = round(cp*(1-tc_orderOffset), precisions['price'])
                    elif side == 'SELL': price = round(cp*(1+tc_orderOffset), precisions['price'])
                elif tc_orderType == 'MARKET': 
                    price = cp
                th = {'type':      thType, 
                      'orderType': tc_orderType,
                      'side':      side,
                      'tefVal':    tef_val,
                      'timestamp': timestamp,
                      'price':     price}
                position_ths.append(th)

    def __updateWalletBalanceTrendAnalysis(self, timestamp):
        assets = self.__assets
        for asset in assets.values():
            #[5-1]: Instances
            wbta          = asset['WBTA']
            walletBalance = asset['walletBalance']
            #[5-2]: First Balance Update Check
            if wbta['firstUpdatedTS'] is None:
                if walletBalance != wbta['initialWalletBalance']:
                    wbta['firstUpdatedTS'] = timestamp
            #[5-3]: Counter & Sums Update
            if wbta['firstUpdatedTS'] is None: continue
            x = (timestamp - wbta['firstUpdatedTS'])/KLINTERVAL_S
            y = math.log(walletBalance) if 0 < walletBalance else 0.0
            wbta['count']  += 1
            wbta['sum_x']  += x
            wbta['sum_xx'] += x**2
            wbta['sum_y']  += y
            wbta['sum_yy'] += y**2
            wbta['sum_xy'] += x*y
            #[5-4]: Balance History
            wbta['minimumWalletBalance'] = min(wbta['minimumWalletBalance'], walletBalance)
            wbta['maximumWalletBalance'] = max(wbta['maximumWalletBalance'], walletBalance)
            wbta['finalWalletBalance']   = walletBalance

    def __updatePeriodicReport(self, timestamp):
        assets        = self.__assets
        pReports      = self.__periodicReports
        for assetName, asset in assets.items():
            #[6-1]: Instances & Daily Report Formatting (If needed)
            pReport_TS = self.__formatPeriodicReport(timestamp = timestamp)
            pReport    = pReports[pReport_TS][assetName]
            #[6-2]: Wallet Balance
            walletBalance = asset['walletBalance']
            pReport['walletBalance_min'] = min(pReport['walletBalance_min'], walletBalance)
            pReport['walletBalance_max'] = max(pReport['walletBalance_max'], walletBalance)
            pReport['walletBalance_close'] = walletBalance
            #[6-3]: Margin Balance
            marginBalance = asset['marginBalance']
            pReport['marginBalance_min'] = min(pReport['marginBalance_min'], marginBalance)
            pReport['marginBalance_max'] = max(pReport['marginBalance_max'], marginBalance)
            pReport['marginBalance_close'] = marginBalance
            #[6-4]: Commitment Rate
            if asset['commitmentRate'] is None: commitmentRate = 0
            else:                               commitmentRate = asset['commitmentRate']
            pReport['commitmentRate_min'] = min(pReport['commitmentRate_min'], commitmentRate)
            pReport['commitmentRate_max'] = max(pReport['commitmentRate_max'], commitmentRate)
            pReport['commitmentRate_close'] = commitmentRate
            #[6-5]: Risk Level
            if asset['riskLevel'] is None: riskLevel = 0
            else:                          riskLevel = asset['riskLevel']
            pReport['riskLevel_min'] = min(pReport['riskLevel_min'], riskLevel)
            pReport['riskLevel_max'] = max(pReport['riskLevel_max'], riskLevel)
            pReport['riskLevel_close'] = riskLevel

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



    #---L2: Sub-Functions
    def __orderCreationRequest_generate(self, symbol, logicSource, orderType, side, quantity, price, tcTrackerUpdate = None):
        #[1]: Instances
        position     = self.__positions[symbol]
        position_def = self.__positions_def[symbol]
        precisions   = position_def['precisions']
        
        #[2]: OCR Generation
        if   side == 'BUY':  targetQuantity = round(position['quantity']+quantity, precisions['quantity'])
        elif side == 'SELL': targetQuantity = round(position['quantity']-quantity, precisions['quantity'])
        ocr = {'logicSource':      logicSource,
               'originalQuantity': position['quantity'],
               'targetQuantity':   targetQuantity,
               'orderParams':      {'symbol':     symbol,
                                    'side':       side,
                                    'type':       orderType,
                                    'recompare':  (logicSource == 'FSLIMMED'),
                                    'quantity':   quantity,
                                    'price':      price},
               'tcTrackerUpdate':  tcTrackerUpdate,
               'orderCode':        None,
               'result':           None}
        position['_orderCreationRequest'] = ocr

        #[3]: Request Dispatch
        ocr['orderCode'] = self.__submitOrder(orderParams = ocr['orderParams'].copy())
        
        #[4]: Finally
        return True

    def __orderCreationRequest_terminate(self, symbol):
        #[1]: Instances
        position = self.__positions[symbol]
        ocr      = position['_orderCreationRequest']

        #[2]: Trade Control Tracker Update
        if ocr['tcTrackerUpdate'] is not None:
            auxiliaries_trade.updateTradeControlTracker(position                  = position,
                                                        tradeControlTrackerUpdate = ocr['tcTrackerUpdate'], 
                                                        updateMode                = 'onComplete')
            
        #[3]: OCR Initialization
        position['_orderCreationRequest'] = None
        
    def __submitOrder(self, orderParams):
        #[1]: Instances
        orders = self.__orders

        #[2]: Order Generation
        symbol = orderParams['symbol']
        oCode = (symbol, time.perf_counter_ns())
        order = {'symbol':    symbol,
                 'side':      orderParams['side'],
                 'orderType': orderParams['type'],
                 'quantity':  orderParams['quantity'],
                 'price':     orderParams['price'],
                 'recompare': orderParams['recompare']}
        orders[oCode] = order

        #[3]: Return Order Number
        return oCode
    
    def __removeOrder(self, orderCode):
        #[1]: Instances
        orders = self.__orders

        #[2]: Existence Check
        if orderCode not in orders:
            return False

        #[3]: Order Cancellation
        del orders[orderCode]

        #[4]: Result Return 
        return True

    def __processTrade(self, timestamp, symbol, side, orderType, quantity, price):
        #[1]: Instances
        position_def = self.__positions_def[symbol]
        position     = self.__positions[symbol]
        precisions   = position_def['precisions']
        asset        = self.__assets[position_def['quoteAsset']]
        ocr          = position['_orderCreationRequest']

        #[2]: Compute New Values
        #---[2-1]: Quantity
        if   side == 'BUY':  quantity_new = round(position['quantity']+quantity, precisions['quantity'])
        elif side == 'SELL': quantity_new = round(position['quantity']-quantity, precisions['quantity'])
        quantity_dirDelta = round(abs(quantity_new)-abs(position['quantity']), precisions['quantity'])
        #---[2-2]: Cost, Profit & Entry Price
        if 0 < quantity_dirDelta:
            if position['quantity'] == 0: notional_prev = 0
            else:                         notional_prev = abs(position['quantity'])*position['entryPrice']
            notional_new = notional_prev+quantity_dirDelta*price
            entryPrice_new = round(notional_new/abs(quantity_new), precisions['price'])
            profit = 0
        elif quantity_dirDelta < 0:
            if quantity_new == 0: entryPrice_new = None
            else:                 entryPrice_new = position['entryPrice']
            if   side == 'BUY':  profit = round(quantity*(position['entryPrice']-price), precisions['quote'])
            elif side == 'SELL': profit = round(quantity*(price-position['entryPrice']), precisions['quote'])
        #---[2-3]: Trading Fee
        tradingFee = round(quantity*price*_TRADINGFEE[position_def['contractType']][orderType][position_def['quoteAsset']], precisions['quote'])
        
        #[3]: Apply New Values
        #---[3-1]: Realized PnL & Trading Fee → Cross Wallet
        asset['crossWalletBalance'] = round(asset['crossWalletBalance']+profit-tradingFee, precisions['quote'])
        #---[3-2]: Isolated Mode: Cross ↔ Isolated Wallet Transfer
        if position_def['isolated']:
            if 0 < quantity_dirDelta:   # Entry: cross → isolated
                wb_transfer = round(quantity*price*((1/position_def['leverage'])+_MARKETOPENLOSSRATE), precisions['quote'])
            elif quantity_dirDelta < 0: # Exit: isolated → cross
                if quantity_new == 0: wb_transfer = -position['isolatedWalletBalance']
                else:                 wb_transfer = -round(quantity*position['entryPrice']/position_def['leverage'], precisions['quote'])
            position['isolatedWalletBalance'] = round(position['isolatedWalletBalance']+wb_transfer, precisions['quote'])
            asset['crossWalletBalance']       = round(asset['crossWalletBalance']      -wb_transfer, precisions['quote'])
            asset['isolatedWalletBalance']    = round(asset['isolatedWalletBalance']   +wb_transfer, precisions['quote'])
        #---[3-3]: Position Status
        position['_quantity_new']   = quantity_new
        position['_entryPrice_new'] = entryPrice_new

        #[3]: Order Result Update
        ocr['result'] = {'timestamp':     timestamp,
                         'side':          side,
                         'orderType':     orderType,
                         'price':         price,
                         'quantity':      quantity,
                         'profit':        profit,
                         'tradingFee':    tradingFee,
                         'walletBalance': asset['crossWalletBalance']+asset['isolatedWalletBalance']}

    def __liquidatePosition(self, timestamp, symbol):
        #[1]: Instances
        position_def = self.__positions_def[symbol]
        position     = self.__positions[symbol]
        precisions   = position_def['precisions']
        asset        = self.__assets[position_def['quoteAsset']]
        price_liq    = position['liquidationPrice']

        #[2]: Quantity & Side Determination
        quantity_prev = position['quantity']
        quantity_abs  = abs(quantity_prev)
        if   0 < quantity_prev: side = 'SELL'
        elif quantity_prev < 0: side = 'BUY'
        
        #[3]: Profit, Trading Fee, and Clearance Fee
        if   side == 'SELL': profit = round(quantity_abs*(price_liq-position['entryPrice'])-position['maintenanceMargin'], precisions['quote'])
        elif side == 'BUY':  profit = round(quantity_abs*(position['entryPrice']-price_liq)-position['maintenanceMargin'], precisions['quote'])
        tradingFee = round(quantity_abs*price_liq*_TRADINGFEE[position_def['contractType']]['MARKET']['DEFAULT'], precisions['quote'])
        netProfit = profit - tradingFee
        
        #[4]: Apply State Changes
        if position_def['isolated']:
            new_iwb = max(position['isolatedWalletBalance'] + netProfit, 0)
            asset['isolatedWalletBalance']         = round(asset['isolatedWalletBalance']-position['isolatedWalletBalance']+new_iwb, precisions['quote'])
            asset['crossWalletBalance']            = round(asset['crossWalletBalance']+new_iwb, precisions['quote'])
            position['isolatedWalletBalance']      = 0
        else:
            new_cwb = max(asset['crossWalletBalance'] + netProfit, 0)
            asset['crossWalletBalance'] = round(new_cwb, precisions['quote'])
        
        #[5]: Reset Position State
        position['_quantity_new']   = 0
        position['_entryPrice_new'] = None
        position['_liquidationReport'] = {'timestamp':     timestamp,
                                          'side':          side,
                                          'price':         price_liq,
                                          'quantity':      quantity_abs,
                                          'profit':        profit,
                                          'tradingFee':    tradingFee,
                                          'walletBalance': asset['crossWalletBalance']+asset['isolatedWalletBalance']}

    def __checkTrade(self, symbol, quantity_new, entryPrice_new):
        #[1]: Instances
        position     = self.__positions[symbol]
        position_def = self.__positions_def[symbol]
        ocr          = position['_orderCreationRequest']

        #[2]: OCR Handling
        if ocr is not None:
            #[2-1]: OCR Values
            ocr_result = ocr['result']
            if not ocr_result:
                return

            #[2-2]: Save Trade Log
            self.__saveTradeLog(timestamp           = ocr_result['timestamp'],
                                symbol              = symbol,
                                logicSource         = ocr['logicSource'],
                                side                = ocr_result['side'],
                                quantity            = ocr_result['quantity'],
                                price               = ocr_result['price'],
                                profit              = ocr_result['profit'],
                                tradingFee          = ocr_result['tradingFee'],
                                quantity_new        = quantity_new,
                                entryPrice_new      = entryPrice_new,
                                walletBalance       = ocr_result['walletBalance'],
                                tradeControlTracker = auxiliaries_trade.copyTradeControlTracker(tradeControlTracker = position['tradeControlTracker']))
            
            #[2-3]: Update Periodic Report
            self.__updatePeriodicReport_onTrade(timestamp     = ocr_result['timestamp'],
                                                quoteAsset    = position_def['quoteAsset'],
                                                side          = ocr_result['side'],
                                                logicSource   = ocr['logicSource'],
                                                profit        = ocr_result['profit'],
                                                walletBalance = ocr_result['walletBalance'])

            #[2-4]: OCR Termination
            self.__orderCreationRequest_terminate(symbol = symbol)

    def __readLiquidationReport(self, symbol):
        #[1]: Instances
        position     = self.__positions[symbol]
        position_def = self.__positions_def[symbol]
        liqReport    = position['_liquidationReport']

        #[2]: Report Check
        if liqReport is None:
            return False
        
        #[3]: Save Trade Log
        self.__saveTradeLog(timestamp           = liqReport['timestamp'],
                            symbol              = symbol,
                            logicSource         = 'LIQUIDATION',
                            side                = liqReport['side'],
                            quantity            = liqReport['quantity'],
                            price               = liqReport['price'],
                            profit              = liqReport['profit'],
                            tradingFee          = liqReport['tradingFee'],
                            quantity_new        = 0,
                            entryPrice_new      = None,
                            walletBalance       = liqReport['walletBalance'],
                            tradeControlTracker = auxiliaries_trade.copyTradeControlTracker(tradeControlTracker = position['tradeControlTracker']))

        #[4]: Update Periodic Report
        self.__updatePeriodicReport_onTrade(timestamp     = liqReport['timestamp'],
                                            quoteAsset    = position_def['quoteAsset'],
                                            side          = liqReport['side'],
                                            logicSource   = 'LIQUIDATION',
                                            profit        = liqReport['profit'],
                                            walletBalance = liqReport['walletBalance'])

        #[5]: Order Canceling
        ocr = position['_orderCreationRequest']
        if ocr is not None and ocr['result'] is None:
            self.__removeOrder(orderCode = ocr['orderCode'])
            position['_orderCreationRequest'] = None

        #[6]: Trade Hanlders & Trade Control Tracker Clearing
        position['_tradeHandlers'].clear()
        position['tradeControlTracker'] = auxiliaries_trade.getInitializedTradeControlTracker()

        #[7]: Report Clearing
        position['_liquidationReport'] = None

        #[8]: Return True To Indicate Liquidation Report Read
        return True



    #---LX: General Functions
    def __allocateBalance(self, symbol, apply):
        #[1]: Instances
        position     = self.__positions[symbol]
        position_def = self.__positions_def[symbol]
        asset        = self.__assets[position_def['quoteAsset']]
        qPrecision   = position_def['precisions']['quote']

        #[2]: Position Check
        if 0 < position['allocatedBalance']:
            return position['allocatedBalance']

        #[3]: Balance Allocation
        allocatable_balance_remaining = asset['allocatableBalance']-asset['allocatedBalance']
        allocated_balance_expected    = asset['allocatableBalance']*position_def['assumedRatio']
        allocated_balance_maximum     = position_def['maxAllocatedBalance']
        allocated_balance = round(max(0.0, min(allocatable_balance_remaining, allocated_balance_expected, allocated_balance_maximum)), qPrecision)
        
        #[4]: Apply
        if apply:
            asset['allocatedBalance']    = round(asset['allocatedBalance'] + allocated_balance, qPrecision)
            position['allocatedBalance'] = allocated_balance

        #[5]: Return Allocated Balance
        return allocated_balance

    def __releaseAllocatedBalance(self, symbol):
        #[1]: Instances
        position     = self.__positions[symbol]
        position_def = self.__positions_def[symbol]
        asset        = self.__assets[position_def['quoteAsset']]
        qPrecision   = position_def['precisions']['quote']

        #[2]: Allocated Balance Release
        asset['allocatedBalance']    = round(asset['allocatedBalance'] - position['allocatedBalance'], qPrecision)
        position['allocatedBalance'] = 0
        
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

    def __saveTradeLog(self, timestamp, symbol, logicSource, side, quantity, price, profit, tradingFee, quantity_new, entryPrice_new, walletBalance, tradeControlTracker):
        tradeLog = {'timestamp':           timestamp, 
                    'positionSymbol':      symbol,
                    'logicSource':         logicSource,
                    'side':                side,
                    'quantity':            quantity,
                    'price':               price,
                    'profit':              profit,
                    'tradingFee':          tradingFee,
                    'totalQuantity':       quantity_new,
                    'entryPrice':          entryPrice_new,
                    'walletBalance':       walletBalance,
                    'tradeControlTracker': tradeControlTracker}
        self.__tradeLogs.append(tradeLog)

    def __updatePeriodicReport_onTrade(self, timestamp, quoteAsset, side, logicSource, profit, walletBalance):
        pReport_TS = self.__formatPeriodicReport(timestamp = timestamp)
        pReport    = self.__periodicReports[pReport_TS][quoteAsset]
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
        wb = walletBalance
        pReport['walletBalance_min']   = min(pReport['walletBalance_min'], wb)
        pReport['walletBalance_max']   = max(pReport['walletBalance_max'], wb)
        pReport['walletBalance_close'] = wb
#Simulation Process END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
