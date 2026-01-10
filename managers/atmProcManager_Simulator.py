#ATM Modules
import atmEta_IPC
import atmEta_Analyzers
import atmEta_Auxillaries
import atmEta_NeuralNetworks
import atmEta_Constants
import atmEta_RQPMFunctions

#Python Modules
import time
import math
import numpy
import torch
import matplotlib.pyplot
import json
import os
import pprint

#Constants
_IPC_THREADTYPE_MT         = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT         = atmEta_IPC._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = atmEta_IPC._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = atmEta_IPC._FAR_INVALIDFUNCTIONID

_SIMULATION_PROCESSTIMEOUT_NS                     = 200e6
_SIMULATION_PROCESSING_ANALYSISRESULT_FETCHNEXT   = 0
_SIMULATION_PROCESSING_ANALYSISRESULT_ANALYZENEXT = 1
_SIMULATION_PROCESSING_ANALYSISRESULT_COMPLETE    = 2
_SIMULATION_PROCESSING_ANALYSISRESULT_ERROR       = 3

_SIMULATION_MARKETTRADINGFEE = 0.0005

_SIMULATION_BASEASSETALLOCATABLERATIO = 0.90

_SIMULATION_ASSETPRECISIONS = {'USDT': 8,
                               'USDC': 8}

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

KLINTERVAL   = atmEta_Constants.KLINTERVAL
KLINTERVAL_S = atmEta_Constants.KLINTERVAL_S

from datetime import datetime, timezone, tzinfo

class procManager_Simulator:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA, simulatorIndex):
        #IPC Assistance
        self.ipcA = ipcA
        
        #Simulator ID
        self.simulatorIndex = simulatorIndex

        #Simulation Control
        self.__activation  = False
        self.__simulations = dict()
        self.__simulations_currentlyHandling = None
        self.__simulations_handlingQueue     = list()
        self.__simulations_removalQueue      = list()

        #Project Path
        self.path_project = path_project

        #FAR Registration
        #---SIMULATIONMANAGER
        self.ipcA.addFARHandler('setActivation',    self.__far_setActivation,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('addSimulation',    self.__far_addSimulation,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('removeSimulation', self.__far_removeSimulation, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

        #IPCA PRD Formatting

        #Process Control
        self.__processLoopContinue = True
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Process Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        while (self.__processLoopContinue == True):
            #Process any existing FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()
            #Process Simulations
            self.__processSimulation()
            #Remove any completed & terminated simulation data
            self.__processSimulationRemovalQueue()
            #Process Loop Control
            if (self.__loopSleepDeterminer() == True): time.sleep(0.001)
    def __loopSleepDeterminer(self):
        sleepLoop = True
        if (self.__simulations_currentlyHandling != None):
            _simulation = self.__simulations[self.__simulations_currentlyHandling]
            if ((self.__activation == True) and (_simulation['_status'] == 'PROCESSING') and (_simulation['_procStatus'] == 'PROCESSING')): sleepLoop = False
        return sleepLoop
    def terminate(self, requester):
        self.__processLoopContinue = False
    #Manager Process Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Internal Functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __processSimulation(self):
        if (self.__activation == True):
            if (self.__simulations_currentlyHandling == None):
                if (0 < len(self.__simulations_handlingQueue)): self.__startSimulation(self.__simulations_handlingQueue.pop(0))
            if (self.__simulations_currentlyHandling != None):
                _simulationCode = self.__simulations_currentlyHandling
                _simulation     = self.__simulations[_simulationCode]
                if (_simulation['_status'] == 'PROCESSING'):
                    if (_simulation['_procStatus'] == 'FETCHING'):
                        if (len(_simulation['_klines_fetchRequestIDs']) == 0):
                            _simulation['_procStatus']         = 'PROCESSING'
                            _simulation['_nextAnalysisTarget'] = _simulation['_currentFocusDay']
                            self.__formatDailyReport(simulationCode = _simulationCode)
                    elif (_simulation['_procStatus'] == 'PROCESSING'):
                        t_begin_ns   = time.perf_counter_ns()
                        t_elapsed_ns = 0
                        analysisResult = _SIMULATION_PROCESSING_ANALYSISRESULT_ANALYZENEXT
                        while ((analysisResult == _SIMULATION_PROCESSING_ANALYSISRESULT_ANALYZENEXT) and (t_elapsed_ns < _SIMULATION_PROCESSTIMEOUT_NS)):
                            analysisResult = self.__performSimulationOnTarget()
                            t_elapsed_ns   = time.perf_counter_ns()-t_begin_ns
                        #[1]: There exists more targets to process within the current focus day
                        if (analysisResult == _SIMULATION_PROCESSING_ANALYSISRESULT_ANALYZENEXT):
                            #[1]: Compute simulation completion and announce
                            _simulation['_completion'] = round(((_simulation['_nextAnalysisTarget']-1)-_simulation['simulationRange'][0]+1)/(_simulation['simulationRange'][1]-_simulation['simulationRange'][0]+1), 5)
                            self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'onSimulationUpdate', functionParams = {'simulationCode': _simulationCode, 'updateType': 'COMPLETION', 'updatedValue': _simulation['_completion']}, farrHandler = None)
                        #[2]: Next focus day needs to be fetched
                        elif (analysisResult == _SIMULATION_PROCESSING_ANALYSISRESULT_FETCHNEXT):
                            #[1]: Compute simulation completion and announce
                            _simulation['_completion'] = round(((_simulation['_nextAnalysisTarget']-1)-_simulation['simulationRange'][0]+1)/(_simulation['simulationRange'][1]-_simulation['simulationRange'][0]+1), 5)
                            self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'onSimulationUpdate', functionParams = {'simulationCode': _simulationCode, 'updateType': 'COMPLETION', 'updatedValue': _simulation['_completion']}, farrHandler = None)
                            #[2]: Update the procStatus and current focus day and request fetch
                            _simulation['_procStatus']         = 'FETCHING'
                            _simulation['_currentFocusDay']    += 86400
                            _simulation['_nextAnalysisTarget'] = None
                            self.__sendKlineFetchRequestForTheCurrentFocusDay(simulationCode = _simulationCode)
                        #[3]: Simulation has completed
                        elif (analysisResult == _SIMULATION_PROCESSING_ANALYSISRESULT_COMPLETE):
                            _simulation['_procStatus'] = 'SAVING'
                            _simulation['_simulationSummary'] = self.__generateSimulationSummary(simulationCode = _simulationCode)
                            self.__savePPIPS(simulationCode = _simulationCode)
                            #Send simulation data save request to DATAMANAGER
                            self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'saveSimulationData', functionParams = {'simulationCode':                 _simulationCode, 
                                                                                                                                  'simulationRange':                _simulation['simulationRange'],
                                                                                                                                  'currencyAnalysisConfigurations': _simulation['currencyAnalysisConfigurations'],
                                                                                                                                  'tradeConfigurations':            _simulation['tradeConfigurations'],
                                                                                                                                  'ppips':                          _simulation['ppips'],
                                                                                                                                  'assets':                         _simulation['assets'],
                                                                                                                                  'positions':                      _simulation['positions'],
                                                                                                                                  'creationTime':                   _simulation['creationTime'],
                                                                                                                                  'tradeLogs':                      _simulation['_tradeLogs'],
                                                                                                                                  'dailyReports':                   _simulation['_dailyReports'],
                                                                                                                                  'simulationSummary':              _simulation['_simulationSummary']},
                                              farrHandler = self.__farr_onSimulationDataSaveRequestResponse)
                        #[3]: An error has occurred
                        elif (analysisResult == _SIMULATION_PROCESSING_ANALYSISRESULT_ERROR): self.__raiseSimulationError(simulationCode = _simulationCode, errorCause = 'INPROCESSERROR')
    def __startSimulation(self, simulationCode):
        self.__simulations_currentlyHandling = simulationCode
        _simulation = self.__simulations[simulationCode]
        #Simulation status update
        _simulation['_status']     = 'PROCESSING'
        _simulation['_completion'] = 0
        self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'onSimulationUpdate', functionParams = {'simulationCode': simulationCode, 'updateType': 'STATUS',     'updatedValue': _simulation['_status']},     farrHandler = None)
        self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'onSimulationUpdate', functionParams = {'simulationCode': simulationCode, 'updateType': 'COMPLETION', 'updatedValue': _simulation['_completion']}, farrHandler = None)
        #Neural network connections data request need check
        _nnCodes = set()
        for _cacCode in _simulation['currencyAnalysisConfigurations']: 
            _nnCode = _simulation['currencyAnalysisConfigurations'][_cacCode]['PIP_NeuralNetworkCode']
            _simulation['_neuralNetworkCodes_byCACCodes'][_cacCode] = _nnCode
            if (_nnCode != None): _nnCodes.add(_nnCode)
        if (0 < len(_nnCodes)):
            _simulation['_procStatus'] = 'WAITINGNNCONNECTIONSDATA'
            for _nnCode in _nnCodes:
                _dispatchID = self.ipcA.sendFAR(targetProcess  = "NEURALNETWORKMANAGER",
                                                functionID     = 'getNeuralNetworkConnections',
                                                functionParams = {'neuralNetworkCode': _nnCode},
                                                farrHandler    = self.__farr_onNeuralNetworkConnectionsDataRequestResponse)
                _simulation['_neuralNetworks_connectionsDataRequestIDs'].add(_dispatchID)
        else:
            _simulation['_procStatus'] = 'FETCHING'
            self.__sendKlineFetchRequestForTheCurrentFocusDay(simulationCode = simulationCode)
    def __sendKlineFetchRequestForTheCurrentFocusDay(self, simulationCode):
        _simulation = self.__simulations[simulationCode]
        _focusDayTimeRange = (_simulation['_currentFocusDay'], _simulation['_currentFocusDay']+86400-1)
        for _pSymbol in _simulation['_positions']:
            _dispatchID = self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'fetchKlines', functionParams = {'symbol': _pSymbol, 'fetchRange': _focusDayTimeRange}, farrHandler = self.__farr_onKlineFetchResponse)
            _simulation['_klines_fetchRequestIDs'][_dispatchID] = _pSymbol
    def __performSimulationOnTarget(self):
        _simulationCode = self.__simulations_currentlyHandling
        _simulation     = self.__simulations[_simulationCode]
        _analysisTargetTS = _simulation['_nextAnalysisTarget']
        #[1]: Allocate Balances of Any Needed Assets
        self.__updateAccount(simulationCode = _simulationCode, timestamp = _analysisTargetTS)
        #[2]: Generate Analysis and Handle Generated PIPs
        for _pSymbol in _simulation['_positions']:
            #Instantiate
            _position_def = _simulation['positions'][_pSymbol]
            _position     = _simulation['_positions'][_pSymbol]
            _asset        = _simulation['_assets'][_position_def['quoteAsset']]
            _cacCode      = _position_def['currencyAnalysisConfigurationCode']
            _analyzer     = _simulation['_analyzers'][_cacCode]
            if (_simulation['_neuralNetworkCodes_byCACCodes'][_cacCode] == None): _neuralNetwork = None
            else:                                                                 _neuralNetwork = _simulation['_neuralNetworks'][_simulation['_neuralNetworkCodes_byCACCodes'][_cacCode]]
            _klines                   = _simulation['_klines'][_pSymbol]
            _klines_dataRange         = _simulation['_klines_dataRange'][_pSymbol]
            _klines_lastRemovedOpenTS = _simulation['_klines_lastRemovedOpenTS'][_pSymbol]
            #Perform
            if (_analysisTargetTS in _klines['raw']):
                _kline = _klines['raw'][_analysisTargetTS] # ([0]: openTS, [1]: closeTS, [2]: openPrice, [3]: highPrice, [4]: lowPrice, [5]: closePrice, [6]: nTrades, [7]: baseAssetVolume, [8]: quoteAssetVolume, [9]: baseAssetVolume_takerBuy, [10]: quoteAssetVolume_takerBuy)
                _openPrice          = _kline[KLINDEX_OPENPRICE]
                _highPrice          = _kline[KLINDEX_HIGHPRICE]
                _lowPrice           = _kline[KLINDEX_LOWPRICE]
                _closePrice         = _kline[KLINDEX_CLOSEPRICE]
                _baseAssetVolume    = _kline[KLINDEX_VOLBASE]
                _baseAssetVolume_tb = _kline[KLINDEX_VOLBASETAKERBUY]
                #[1]: Analysis Generation
                if (True):
                    nKlinesToKeep_max = 0
                    for _analysisPair in _analyzer['analysisToProcess_sorted']:
                        _analysisType = _analysisPair[0]; _analysisCode = _analysisPair[1]
                        #---Analysis Generation
                        nAnalysisToKeep, nKlinesToKeep = atmEta_Analyzers.analysisGenerator(analysisType  = _analysisType, 
                                                                                            klineAccess   = _klines, 
                                                                                            intervalID    = KLINTERVAL,
                                                                                            mrktRegTS     = None,
                                                                                            precisions    = _position_def['precisions'], 
                                                                                            timestamp     = _analysisTargetTS,
                                                                                            neuralNetwork = _neuralNetwork,
                                                                                            bidsAndAsks   = None, 
                                                                                            aggTrades     = None,
                                                                                            **_analyzer['analysisParams'][_analysisCode])
                        if (_neuralNetwork != None):
                            _nSamples_NN = _neuralNetwork.getNKlines()
                            if (nAnalysisToKeep < _nSamples_NN): nAnalysisToKeep = _nSamples_NN
                        if (nKlinesToKeep_max < nKlinesToKeep): nKlinesToKeep_max = nKlinesToKeep
                        #---Memory Optimization (Analysis)
                        if (True):
                            expiredAnalysisOpenTS_nAnalysisToKeep = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = None, timestamp = _analysisTargetTS, nTicks = -(nAnalysisToKeep+1))
                            if (_klines_dataRange[0] <= expiredAnalysisOpenTS_nAnalysisToKeep):
                                if (_klines_lastRemovedOpenTS[_analysisCode] == None): 
                                    if (_klines_dataRange[0] < _simulation['simulationRange'][0]): tsRemovalRange_beg = _simulation['simulationRange'][0]
                                    else:                                                          tsRemovalRange_beg = _klines_dataRange[0]
                                else:                                                              tsRemovalRange_beg = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = None, timestamp = _klines_lastRemovedOpenTS[_analysisCode], nTicks = 1)
                                _tsToRemoveList = atmEta_Auxillaries.getTimestampList_byRange(intervalID = KLINTERVAL, timestamp_beg = tsRemovalRange_beg, timestamp_end = expiredAnalysisOpenTS_nAnalysisToKeep, mrktReg = None, lastTickInclusive = True)
                                if (0 < len(_tsToRemoveList)):
                                    for _tsToRemove in atmEta_Auxillaries.getTimestampList_byRange(intervalID = KLINTERVAL, timestamp_beg = tsRemovalRange_beg, timestamp_end = expiredAnalysisOpenTS_nAnalysisToKeep, mrktReg = None, lastTickInclusive = True): del _klines[_analysisCode][_tsToRemove]
                                    _klines_lastRemovedOpenTS[_analysisCode] = expiredAnalysisOpenTS_nAnalysisToKeep
                    #---Memory Optimization (Kline Raw, Kline Raw_Status)
                    if (True):
                        expiredAnalysisOpenTS_nKlinesToKeep = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = None, timestamp = _analysisTargetTS, nTicks = -(nKlinesToKeep_max+1))
                        if (_klines_dataRange[0] <= expiredAnalysisOpenTS_nKlinesToKeep):
                            if (_klines_lastRemovedOpenTS['raw'] == None): 
                                if (_klines_dataRange[0] < _simulation['simulationRange'][0]): tsRemovalRange_beg = _simulation['simulationRange'][0]
                                else:                                                          tsRemovalRange_beg = _klines_dataRange[0]
                            else:                                                              tsRemovalRange_beg = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, mrktReg = None, timestamp = _klines_lastRemovedOpenTS['raw'], nTicks = 1)
                            _tsToRemoveList = atmEta_Auxillaries.getTimestampList_byRange(intervalID = KLINTERVAL, timestamp_beg = tsRemovalRange_beg, timestamp_end = expiredAnalysisOpenTS_nKlinesToKeep, mrktReg = None, lastTickInclusive = True)
                            if (0 < len(_tsToRemoveList)):
                                for _tsToRemove in _tsToRemoveList: del _klines['raw'][_tsToRemove]
                                _klines_lastRemovedOpenTS['raw'] = expiredAnalysisOpenTS_nKlinesToKeep
                #[2]: New Kline Handling
                self.__handleKline(simulationCode = _simulationCode, pSymbol = _pSymbol, timestamp = _analysisTargetTS, kline = _kline)
                #[3]: PIP Handling
                if (('PIP' in _klines) and (_kline[5] != 0)):
                    _pipResult = _klines['PIP'][_analysisTargetTS]
                    #[3-1]: Trade Control
                    self.__handlePIPResult(simulationCode = _simulationCode, pSymbol = _pSymbol, pipResult = _pipResult, timestamp = _analysisTargetTS, kline = _kline)
                    #[3-2]: PPIPS
                    if (_simulation['ppips'][0]):
                        #Swing
                        if (_pipResult['SWINGS']):
                            _lastSwing = _pipResult['SWINGS'][-1]
                            if   (_lastSwing[2] == 'LOW'):  _pip_lastSwing_type = -1
                            elif (_lastSwing[2] == 'HIGH'): _pip_lastSwing_type =  1
                            _pip_lastSwing_price = _lastSwing[1]
                        else:
                            _pip_lastSwing_type  = None
                            _pip_lastSwing_price = None
                        #Finally
                        _position['PPIPS']['data'].append((#Kline
                                                           _analysisTargetTS,
                                                           _openPrice,
                                                           _highPrice,
                                                           _lowPrice,
                                                           _closePrice,
                                                           _baseAssetVolume,
                                                           _baseAssetVolume_tb,
                                                           #PIP
                                                           _pip_lastSwing_type,
                                                           _pip_lastSwing_price,
                                                           _pipResult['NNASIGNAL'],
                                                           _pipResult['CLASSICALSIGNAL_FILTERED'],
                                                           *_pipResult['NEARIVPBOUNDARIES'],
                                                           ))
        #[3]: Daily Report Update
        for _assetName in _simulation['assets']:
            _asset = _simulation['_assets'][_assetName]
            _dailyReport = _simulation['_dailyReports'][_simulation['_currentFocusDay']][_assetName]
            #[1]: Margin Balance
            _marginBalance = _asset['marginBalance']
            if (_marginBalance < _dailyReport['marginBalance_min']): _dailyReport['marginBalance_min'] = _marginBalance
            if (_dailyReport['marginBalance_max'] < _marginBalance): _dailyReport['marginBalance_max'] = _marginBalance
            _dailyReport['marginBalance_close'] = _marginBalance
            #[2]: Commitment Rate
            if (_asset['commitmentRate'] == None): _commimtmentRate = 0
            else:                                  _commimtmentRate = _asset['commitmentRate']
            if (_commimtmentRate < _dailyReport['commitmentRate_min']): _dailyReport['commitmentRate_min'] = _commimtmentRate
            if (_dailyReport['commitmentRate_max'] < _commimtmentRate): _dailyReport['commitmentRate_max'] = _commimtmentRate
            _dailyReport['commitmentRate_close'] = _commimtmentRate
            #[3]: Risk Level
            if (_asset['riskLevel'] == None): _riskLevel = 0
            else:                             _riskLevel = _asset['riskLevel']
            if (_riskLevel < _dailyReport['riskLevel_min']): _dailyReport['riskLevel_min'] = _riskLevel
            if (_dailyReport['riskLevel_max'] < _riskLevel): _dailyReport['riskLevel_max'] = _riskLevel
            _dailyReport['riskLevel_close'] = _riskLevel
        #[4]: Post-process handling, update the next analysis target and return how the update occurred
        if (_analysisTargetTS == _simulation['_lastAnalysisTarget']): return _SIMULATION_PROCESSING_ANALYSISRESULT_COMPLETE
        else:
            _simulation['_nextAnalysisTarget'] += KLINTERVAL_S
            if (_simulation['_currentFocusDay']+86400 <= _simulation['_nextAnalysisTarget']): return _SIMULATION_PROCESSING_ANALYSISRESULT_FETCHNEXT
            else:                                                                             return _SIMULATION_PROCESSING_ANALYSISRESULT_ANALYZENEXT
    def __handleKline(self, simulationCode, pSymbol, timestamp, kline):
        #Instances Call
        _simulation   = self.__simulations[simulationCode]
        _position_def = _simulation['positions'][pSymbol]
        _position     = _simulation['_positions'][pSymbol]
        _asset        = _simulation['_assets'][_position_def['quoteAsset']]
        _tcConfig     = _simulation['tradeConfigurations'][_simulation['positions'][pSymbol]['tradeConfigurationCode']]
        _tcTracker    = _position['tradeControlTracker']
        _precisions   = _position_def['precisions']

        #Force Exit Check
        _tradeHandler_checkList = {'FSLIMMED':    None,
                                   'FSLCLOSE':    None,
                                   'LIQUIDATION': None}
        if (_position['quantity'] != 0):
            #FSL IMMED
            if (_tcConfig['fullStopLossImmediate'] is not None):
                #<SHORT>
                if (_position['quantity'] < 0):
                    _price_FSL = round(_position['entryPrice']*(1+_tcConfig['fullStopLossImmediate']), _precisions['price'])
                    if (_price_FSL <= kline[KLINDEX_HIGHPRICE]): _tradeHandler_checkList['FSLIMMED'] = ('BUY', _price_FSL, _price_FSL-kline[KLINDEX_OPENPRICE])
                #<LONG>
                elif (0 < _position['quantity']):
                    _price_FSL = round(_position['entryPrice']*(1-_tcConfig['fullStopLossImmediate']), _precisions['price'])
                    if (kline[KLINDEX_LOWPRICE] <= _price_FSL): _tradeHandler_checkList['FSLIMMED'] = ('SELL', _price_FSL, kline[KLINDEX_OPENPRICE]-_price_FSL)
            #FSL CLOSE
            if (_tcConfig['fullStopLossClose'] is not None):
                #<SHORT>
                if (_position['quantity'] < 0):
                    _price_FSL = round(_position['entryPrice']*(1+_tcConfig['fullStopLossClose']), _precisions['price'])
                    if (_price_FSL <= kline[KLINDEX_HIGHPRICE]): _tradeHandler_checkList['FSLCLOSE'] = ('BUY', kline[KLINDEX_CLOSEPRICE])
                #<LONG>
                elif (0 < _position['quantity']):
                    _price_FSL = round(_position['entryPrice']*(1-_tcConfig['fullStopLossClose']), _precisions['price'])
                    if (kline[KLINDEX_LOWPRICE] <= _price_FSL): _tradeHandler_checkList['FSLCLOSE'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
            #LIQUIDATION
            if (_position['liquidationPrice'] is not None):
                #<SHORT>
                if (_position['quantity'] < 0):
                    if (_position['liquidationPrice'] <= kline[KLINDEX_HIGHPRICE]): _tradeHandler_checkList['LIQUIDATION'] = ('LIQUIDATION', _position['liquidationPrice'], _position['liquidationPrice']-kline[KLINDEX_OPENPRICE])
                #<LONG>
                elif (0 < _position['quantity']):
                    if (kline[KLINDEX_LOWPRICE] <= _position['liquidationPrice']): _tradeHandler_checkList['LIQUIDATION'] = ('LIQUIDATION', _position['liquidationPrice'], kline[KLINDEX_OPENPRICE]-_position['liquidationPrice'])

        #Trade Handler Determination
        if ((_tradeHandler_checkList['LIQUIDATION'] is not None) and (_tradeHandler_checkList['FSLIMMED'] is not None)):
            if (_tradeHandler_checkList['LIQUIDATION'][2] <= _tradeHandler_checkList['FSLIMMED'][2]): _tradeHandler = 'LIQUIDATION'
            else:                                                                                     _tradeHandler = 'FSLIMMED'
        elif (_tradeHandler_checkList['LIQUIDATION'] is not None): _tradeHandler = 'LIQUIDATION'
        elif (_tradeHandler_checkList['FSLIMMED']    is not None): _tradeHandler = 'FSLIMMED'
        elif (_tradeHandler_checkList['FSLCLOSE']    is not None): _tradeHandler = 'FSLCLOSE'
        else:                                                      _tradeHandler = None

        #Trade Handlers Execution
        if (_tradeHandler is None): return
        _thParams = _tradeHandler_checkList[_tradeHandler]
        if   (_tradeHandler == 'FSLIMMED'):    self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'FSLIMMED',    side = _thParams[0], quantity = abs(_position['quantity']), timestamp = timestamp, tradePrice = _thParams[1])
        elif (_tradeHandler == 'FSLCLOSE'):    self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'FSLCLOSE',    side = _thParams[0], quantity = abs(_position['quantity']), timestamp = timestamp, tradePrice = _thParams[1])
        elif (_tradeHandler == 'LIQUIDATION'): self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'LIQUIDATION', side = None,         quantity = abs(_position['quantity']), timestamp = timestamp, tradePrice = _thParams[1])
        _tcTracker['slExited'] = True
    def __handlePIPResult(self, simulationCode, pSymbol, pipResult, timestamp, kline):
        #Instances Call
        _simulation = self.__simulations[simulationCode]
        _position_def = _simulation['positions'][pSymbol]
        _position     = _simulation['_positions'][pSymbol]
        _asset        = _simulation['_assets'][_position_def['quoteAsset']]
        _tcConfig     = _simulation['tradeConfigurations'][_simulation['positions'][pSymbol]['tradeConfigurationCode']]
        _tcTracker    = _position['tradeControlTracker']
        _precisions   = _position_def['precisions']

        #RQP Value
        _rqpmValue = atmEta_RQPMFunctions.RQPMFUNCTIONS_GET_RQPVAL[_tcConfig['rqpm_functionType']](params = _tcConfig['rqpm_functionParams'], kline = kline, pipResult = pipResult, tcTracker_model = _tcTracker['rqpm_model'])
        if (_rqpmValue == None): return

        #SL Exit Flag
        if (_tcTracker['rqpm_val_prev'] is None): _tcTracker['slExited'] = False
        else:
            if   ((_tcTracker['rqpm_val_prev'] < 0) and (0 < _rqpmValue)): _tcTracker['slExited'] = False
            elif ((0 < _tcTracker['rqpm_val_prev']) and (_rqpmValue < 0)): _tcTracker['slExited'] = False

        #PIP Action Signal Interpretation & Trade Handlers Determination
        _tradeHandler_checkList = {'ENTRY': None,
                                   'CLEAR': None,
                                   'EXIT':  None}
        #---CheckList 1: CLEAR
        if   ((_position['quantity'] < 0) and (0 < _rqpmValue)): _tradeHandler_checkList['CLEAR'] = ('BUY',  kline[KLINDEX_CLOSEPRICE])
        elif ((0 < _position['quantity']) and (_rqpmValue < 0)): _tradeHandler_checkList['CLEAR'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
        #---CheckList 2: ENTRY & EXIT
        _pslCheck = (_tcConfig['postStopLossReentry'] == True) or (_tcTracker['slExited'] == False)
        if (_rqpmValue < 0):  
            if ((_pslCheck == True) and ((_tcConfig['direction'] == 'BOTH') or (_tcConfig['direction'] == 'SHORT'))): _tradeHandler_checkList['ENTRY'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
            _tradeHandler_checkList['EXIT']  = ('BUY',  kline[KLINDEX_CLOSEPRICE])
        elif (0 < _rqpmValue):
            if ((_pslCheck == True) and ((_tcConfig['direction'] == 'BOTH') or (_tcConfig['direction'] == 'LONG'))): _tradeHandler_checkList['ENTRY'] = ('BUY',  kline[KLINDEX_CLOSEPRICE])
            _tradeHandler_checkList['EXIT']  = ('SELL', kline[KLINDEX_CLOSEPRICE])
        elif (_rqpmValue == 0):
            if   (_position['quantity'] < 0): _tradeHandler_checkList['EXIT'] = ('BUY',  kline[KLINDEX_CLOSEPRICE])
            elif (0 < _position['quantity']): _tradeHandler_checkList['EXIT'] = ('SELL', kline[KLINDEX_CLOSEPRICE])

        #Trade Handlers Determination
        _tradeHandlers = list()
        if (_tradeHandler_checkList['CLEAR'] is not None): _tradeHandlers.append('CLEAR')
        if (_tradeHandler_checkList['EXIT']  is not None): _tradeHandlers.append('EXIT')
        if (_tradeHandler_checkList['ENTRY'] is not None): _tradeHandlers.append('ENTRY')

        #Trade Handlers Execution
        for _tradeHandler in _tradeHandlers:
            _thParams = _tradeHandler_checkList[_tradeHandler]
            if (_tradeHandler == 'CLEAR'): self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'CLEAR', side = _thParams[0], quantity = abs(_position['quantity']), timestamp = timestamp, tradePrice = _thParams[1])
            else:
                _balance_allocated = _position['allocatedBalance']                                            if (_position['allocatedBalance'] is not None) else 0
                _balance_committed = abs(_position['quantity'])*_position['entryPrice']/_tcConfig['leverage'] if (_position['entryPrice']       is not None) else 0
                _balance_toCommit  = _balance_allocated*abs(_rqpmValue)
                _balance_toEnter   = _balance_toCommit-_balance_committed

                if (_balance_toEnter == 0): continue

                if (_tradeHandler == 'ENTRY'):
                    if (0 < _balance_toEnter): 
                        _quantity_minUnit  = pow(10, -_precisions['quantity'])
                        _quantity_toEnter  = round(int((_balance_toEnter/_thParams[1]*_tcConfig['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                        if (0 < _quantity_toEnter): self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'ENTRY', side = _thParams[0], quantity = _quantity_toEnter, timestamp = timestamp, tradePrice = _thParams[1])
                elif (_tradeHandler == 'EXIT'):
                    if (_balance_toEnter < 0): 
                        _quantity_minUnit = pow(10, -_precisions['quantity'])
                        _quantity_toExit  = round(int((-_balance_toEnter/_position['entryPrice']*_tcConfig['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                        if (0 < _quantity_toExit): self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'EXIT', side = _thParams[0], quantity = _quantity_toExit, timestamp = timestamp, tradePrice = _thParams[1])
            
        #RQPM Value Record
        _tcTracker['rqpm_val_prev'] = _rqpmValue
    def __formatDailyReport(self, simulationCode):
        _simulation = self.__simulations[simulationCode]
        _assets     = _simulation['_assets']
        _dailyReport = dict()
        for _assetName in _simulation['assets']:
            _asset = _assets[_assetName]
            _mb = _asset['marginBalance']
            _wb = _asset['walletBalance']
            if (_asset['commitmentRate'] == None): _commimtmentRate = 0
            else:                                  _commimtmentRate = _asset['commitmentRate']
            if (_asset['riskLevel'] == None): _riskLevel = 0
            else:                             _riskLevel = _asset['riskLevel']
            if (_asset['riskLevel'] == None): _riskLevel = 0
            else:                             _riskLevel = _asset['riskLevel']
            _dailyReport[_assetName] = {'nTrades':             0,
                                        'nTrades_buy':         0,
                                        'nTrades_sell':        0,
                                        'nTrades_entry':       0,
                                        'nTrades_clear':       0,
                                        'nTrades_exit':        0,
                                        'nTrades_fslImmed':    0,
                                        'nTrades_fslClose':    0,
                                        'nTrades_liquidation': 0,
                                        'nTrades_gains':       0,
                                        'nTrades_losses':      0,
                                        'marginBalance_open': _mb, 'marginBalance_min': _mb, 'marginBalance_max': _mb, 'marginBalance_close': _mb,
                                        'walletBalance_open': _wb, 'walletBalance_min': _wb, 'walletBalance_max': _wb, 'walletBalance_close': _wb,
                                        'commitmentRate_open': _commimtmentRate, 'commitmentRate_min': _commimtmentRate, 'commitmentRate_max': _commimtmentRate, 'commitmentRate_close': _commimtmentRate,
                                        'riskLevel_open':      _riskLevel,       'riskLevel_min':      _riskLevel,       'riskLevel_max':      _riskLevel,       'riskLevel_close':      _riskLevel}
        _simulation['_dailyReports'][_simulation['_currentFocusDay']] = _dailyReport
    def __updateAccount(self, simulationCode, timestamp):
        _simulation = self.__simulations[simulationCode]
        _assets_def    = _simulation['assets']
        _assets        = _simulation['_assets']
        _positions_def = _simulation['positions']
        _positions     = _simulation['_positions']
        #[1]: Update Positions
        for _positionSymbol in _positions:
            _position_def = _positions_def[_positionSymbol]
            _position     = _positions[_positionSymbol]
            _klines       = _simulation['_klines'][_positionSymbol]
            if (timestamp in _klines['raw']): _position['currentPrice'] = _klines['raw'][timestamp][5]
            else:                             _position['currentPrice'] = None
            if (_position['currentPrice'] == None):
                _position['positionInitialMargin'] = None
                _position['unrealizedPNL']         = None
            else:
                _position['positionInitialMargin'] = round(_position['currentPrice']*abs(_position['quantity'])/_position_def['leverage'], _position_def['precisions']['quote'])
                if   (_position['quantity'] < 0):  _position['unrealizedPNL'] = round((_position['entryPrice']-_position['currentPrice'])*abs(_position['quantity']), _position_def['precisions']['quote'])
                elif (_position['quantity'] == 0): _position['unrealizedPNL'] = None
                elif (0 < _position['quantity']):  _position['unrealizedPNL'] = round((_position['currentPrice']-_position['entryPrice'])*abs(_position['quantity']), _position_def['precisions']['quote'])
        #[2]: Update Assets
        for _assetName in _assets:
            _asset_def = _assets_def[_assetName]
            _asset     = _assets[_assetName]
            _asset['isolatedPositionInitialMargin'] = sum([_positions[_positionSymbol]['positionInitialMargin']    for _positionSymbol in _asset_def['_positionSymbols_isolated'] if (_positions[_positionSymbol]['positionInitialMargin'] != None)])
            _asset['crossPositionInitialMargin']    = sum([_positions[_positionSymbol]['positionInitialMargin']    for _positionSymbol in _asset_def['_positionSymbols_crossed']  if (_positions[_positionSymbol]['positionInitialMargin'] != None)])
            _asset['crossMaintenanceMargin']        = sum([_positions[_positionSymbol]['maintenanceMargin']        for _positionSymbol in _asset_def['_positionSymbols_crossed']])
            _asset['isolatedUnrealizedPNL']         = sum([_positions[_positionSymbol]['unrealizedPNL']            for _positionSymbol in _asset_def['_positionSymbols_isolated'] if (_positions[_positionSymbol]['unrealizedPNL'] != None)])
            _asset['crossUnrealizedPNL']            = sum([_positions[_positionSymbol]['unrealizedPNL']            for _positionSymbol in _asset_def['_positionSymbols_crossed']  if (_positions[_positionSymbol]['unrealizedPNL'] != None)])
            _asset['assumedRatio']                  = sum([_positions_def[_positionSymbol]['assumedRatio']         for _positionSymbol in _asset_def['_positionSymbols']])
            _asset['weightedAssumedRatio']          = sum([_positions_def[_positionSymbol]['weightedAssumedRatio'] for _positionSymbol in _asset_def['_positionSymbols'] if (_positions_def[_positionSymbol]['weightedAssumedRatio'] != None)])
            _asset['walletBalance']      = _asset['crossWalletBalance']+_asset['isolatedWalletBalance']
            _asset['unrealizedPNL']      = _asset['isolatedUnrealizedPNL']+_asset['crossUnrealizedPNL']
            _asset['marginBalance']      = _asset['walletBalance']+_asset['unrealizedPNL']
            _asset['availableBalance']   = _asset['crossWalletBalance']-_asset['crossPositionInitialMargin']+_asset['crossUnrealizedPNL']
            _asset['allocatableBalance'] = round((_asset['walletBalance'])*_SIMULATION_BASEASSETALLOCATABLERATIO*_asset_def['allocationRatio'], _SIMULATION_ASSETPRECISIONS[_assetName])
            if (_asset['allocatableBalance'] < 0): _asset['allocatableBalance'] = 0
        #[3]: Balance Allocation
        self.__allocateBalance(simulationCode = simulationCode)
        #[4]: Update Secondary Position Data
        for _positionSymbol in _positions:
            _position_def = _positions_def[_positionSymbol]
            _position     = _positions[_positionSymbol]
            _quantity_abs = abs(_position['quantity'])
            #[1]: Commitment Rate
            if ((0 < _quantity_abs) and (_position['allocatedBalance'] != 0)): _position['commitmentRate'] = round((_quantity_abs*_position['entryPrice']/_position_def['leverage'])/_position['allocatedBalance'], 5)
            else:                                                              _position['commitmentRate'] = None
            #[2]: Liquidation Price
            if (_position_def['isolated'] == True): _wb = _position['isolatedWalletBalance']
            else:                                   _wb = _asset['crossWalletBalance']
            _position['liquidationPrice'] = self.__computeLiquidationPrice(positionSymbol    = _positionSymbol,
                                                                           walletBalance     = _wb,
                                                                           quantity          = _position['quantity'],
                                                                           entryPrice        = _position['entryPrice'],
                                                                           currentPrice      = _position['currentPrice'],
                                                                           maintenanceMargin = _position['maintenanceMargin'],
                                                                           upnl              = _position['unrealizedPNL'],
                                                                           isolated          = _position_def['isolated'],
                                                                           mm_crossTotal     = _asset['crossMaintenanceMargin'],
                                                                           upnl_crossTotal   = _asset['crossUnrealizedPNL'])
            #[3]: Risk Level
            if ((_position['entryPrice'] is not None) and (_position['currentPrice'] is not None)):
                if (_position['liquidationPrice'] is None): _position['riskLevel'] = 0
                else:
                    if   (0 < _position['quantity']): _lp = (_position['entryPrice']-_position['currentPrice'])/(_position['entryPrice']-_position['liquidationPrice'])
                    elif (_position['quantity'] < 0): _lp = (_position['currentPrice']-_position['entryPrice'])/(_position['liquidationPrice']-_position['entryPrice'])
                    if (_lp < 0): _lp = 0
                    if (_position['commitmentRate'] is None): _position['riskLevel'] = _lp
                    else:                                     _position['riskLevel'] = _position['commitmentRate']*_lp
            else: _position['riskLevel'] = None
        #[5]: Update Secondary Asset Data
        for _assetName in _assets:
            _asset_def = _assets_def[_assetName]
            _asset     = _assets[_assetName]
            #[1]: Allocated Balance
            allocatedBalanceSum = sum([_positions[_positionSymbol]['allocatedBalance'] for _positionSymbol in _asset_def['_positionSymbols']])
            _asset['allocatedBalance'] = allocatedBalanceSum
            #[2]: Commitment Rate
            _commitmentRate_pSymbols = [_pSymbol for _pSymbol in _asset_def['_positionSymbols'] if (_positions[_pSymbol]['commitmentRate'] != None)]
            _commitmentRate_pSymbols_n = len(_commitmentRate_pSymbols)
            if (0 < _commitmentRate_pSymbols_n):
                _commitmentRate_sum = sum([_positions[_pSymbol]['commitmentRate'] for _pSymbol in _commitmentRate_pSymbols])
                _commitmentRate_average = round(_commitmentRate_sum/_commitmentRate_pSymbols_n, 5)
            else: _commitmentRate_average = None
            _asset['commitmentRate'] = _commitmentRate_average
            #[3]: Risk Level
            _riskLevel_pSymbols = [_pSymbol for _pSymbol in _asset_def['_positionSymbols'] if (_positions[_pSymbol]['riskLevel'] != None)]
            _riskLevel_pSymbols_n = len(_riskLevel_pSymbols)
            if (0 < _riskLevel_pSymbols_n):
                _riskLevel_sum     = sum([_positions[_pSymbol]['riskLevel'] for _pSymbol in _riskLevel_pSymbols])
                _riskLevel_average = round(_riskLevel_sum/_riskLevel_pSymbols_n, 5)
            else: _riskLevel_average = None
            _asset['riskLevel'] = _riskLevel_average
            if (_assetName == 'USDT'):
                pass
                #if (_asset['commitmentRate'] == None): print(datetime.fromtimestamp(timestamp, tz = timezone.utc).strftime("[%Y/%m/%d %H:%M]"), "{:.8f} USDT /".format(_asset['walletBalance']), "{:.8f} USDT".format(_asset['marginBalance']))
                #else:                                  print(datetime.fromtimestamp(timestamp, tz = timezone.utc).strftime("[%Y/%m/%d %H:%M]"), "{:.8f} USDT /".format(_asset['walletBalance']), "{:.8f} USDT".format(_asset['marginBalance']), "{:.3f} %".format(_asset['commitmentRate']*100))
    def __computeLiquidationPrice(self, positionSymbol, walletBalance, quantity, entryPrice, currentPrice, maintenanceMargin, upnl, isolated = True, mm_crossTotal = 0, upnl_crossTotal = 0):
        if ((quantity == 0) or (currentPrice is None) or (maintenanceMargin is None)): return None
        else:
            _quantity_abs = abs(quantity)
            _maintenanceMarginRate, _maintenanceAmount = atmEta_Constants.getMaintenanceMarginRateAndAmount(positionSymbol = positionSymbol, notional = _quantity_abs*currentPrice)
            if (isolated == True): mm_others = 0;                               upnl_others = 0
            else:                  mm_others = mm_crossTotal-maintenanceMargin; upnl_others = upnl_crossTotal-upnl
            if   (quantity < 0):  _side = -1
            elif (0 < quantity):  _side =  1
            _liquidationPrice = (walletBalance-mm_others+upnl_others-maintenanceMargin+_quantity_abs*(currentPrice*_maintenanceMarginRate-entryPrice*_side))/(_quantity_abs*(_maintenanceMarginRate-_side))
            if (_liquidationPrice <= 0): _liquidationPrice = 0
            return _liquidationPrice
    def __allocateBalance(self, simulationCode):
        _simulation    = self.__simulations[simulationCode]
        _positions_def = _simulation['positions']
        _positions     = _simulation['_positions']
        for _assetName in _simulation['assets']:
            _asset_def = _simulation['assets'][_assetName]
            _asset     = _simulation['_assets'][_assetName]
            _allocatedAssumedRatio = 0
            #Zero Quantity Allocation Zero
            for _pSymbol in _asset_def['_positionSymbols']: 
                _position_def = _positions_def[_pSymbol]
                _position     = _positions[_pSymbol]
                if (_position['quantity'] == 0): _assumedRatio_effective = 0; _position['allocatedBalance'] = 0
                else:                            _assumedRatio_effective = round(_position['allocatedBalance']/_asset['allocatableBalance'], 3)
                _allocatedAssumedRatio += _assumedRatio_effective
            #Zero Quantity Re-Allocation
            for _pSymbol in _asset_def['_positionSymbols_prioritySorted']:
                _position_def = _positions_def[_pSymbol]
                _position     = _positions[_pSymbol]
                if ((_position['quantity'] == 0) or ((_position_def['assumedRatio'] != 0) and (_position['allocatedBalance'] == 0))):
                    _allocatedBalance = round(_asset['allocatableBalance']*_position_def['assumedRatio'], _position_def['precisions']['quote'])
                    if (_position_def['maxAllocatedBalance'] < _allocatedBalance): _allocatedBalance = _position_def['maxAllocatedBalance']
                    _assumedRatio_effective = round(_allocatedBalance/_asset['allocatableBalance'], 3)
                    if (_allocatedAssumedRatio+_assumedRatio_effective <= 1):
                        _allocatedAssumedRatio += _assumedRatio_effective
                        _position['allocatedBalance'] = _allocatedBalance
                    else: break
    def __processSimulatedTrade(self, simulationCode, positionSymbol, logicSource, side, quantity, timestamp, tradePrice):
        #Instantiation
        _simulation   = self.__simulations[simulationCode]
        _position_def = _simulation['positions'][positionSymbol]
        _position     = _simulation['_positions'][positionSymbol]
        _precisions   = _position_def['precisions']
        _asset        = _simulation['_assets'][_position_def['quoteAsset']]
        #Trade Processing
        if (logicSource == 'LIQUIDATION'):
            _quantity_new = 0
            if   (0 < _position['quantity']): _profit = round(abs(_position['quantity'])*(tradePrice-_position['entryPrice']), _precisions['quote'])
            elif (_position['quantity'] < 0): _profit = round(abs(_position['quantity'])*(_position['entryPrice']-tradePrice), _precisions['quote'])
            _entryPrice_new = None
            _tradingFee     = round(_position['quantity']*tradePrice*_SIMULATION_MARKETTRADINGFEE, _precisions['quote'])
            if (_position_def['isolated'] == True):
                _asset['isolatedWalletBalance']         = round(_asset['isolatedWalletBalance']-_position['isolatedWalletBalance'],         _precisions['quote'])
                _position['isolatedWalletBalance']      = round(_position['isolatedWalletBalance']+_profit-_tradingFee,                     _precisions['quote'])
                _asset['crossWalletBalance']            = round(_asset['crossWalletBalance']+_position['isolatedWalletBalance'],            _precisions['quote'])
                _asset['isolatedPositionInitialMargin'] = round(_asset['isolatedPositionInitialMargin']-_position['positionInitialMargin'], _precisions['quote'])
            else:
                _asset['crossWalletBalance']         = round(_asset['crossWalletBalance']+_profit-_tradingFee,                        _precisions['quote'])
                _asset['crossPositionInitialMargin'] = round(_asset['crossPositionInitialMargin']-_position['positionInitialMargin'], _precisions['quote'])
                _asset['crossMaintenanceMargin']     = round(_asset['crossMaintenanceMargin']-_position['maintenanceMargin'],         _precisions['quote'])
            _position['entryPrice']            = None
            _position['quantity']              = 0
            _position['maintenanceMargin']     = 0
            _position['positionInitialMargin'] = 0
            #Wallet, Margin and Available Balance
            _asset['walletBalance']    = _asset['crossWalletBalance']+_asset['isolatedWalletBalance']
            _asset['marginBalance']    = _asset['walletBalance']+_asset['unrealizedPNL']
            _asset['availableBalance'] = _asset['crossWalletBalance']-_asset['crossPositionInitialMargin']+_asset['unrealizedPNL']
        else:
            #[1]: Compute Values
            #---Quantity
            if   (side == 'BUY'):  _quantity_new = round(_position['quantity']+quantity, _precisions['quantity'])
            elif (side == 'SELL'): _quantity_new = round(_position['quantity']-quantity, _precisions['quantity'])
            _quantity_dirDelta = round(abs(_quantity_new)-abs(_position['quantity']), _precisions['quantity'])
            #---Cost, Profit & Entry Price
            if (0 < _quantity_dirDelta):
                #Entry Price
                if (_position['quantity'] == 0): _notional_prev = 0
                else:                            _notional_prev = abs(_position['quantity'])*_position['entryPrice']
                _notional_new = _notional_prev+_quantity_dirDelta*tradePrice
                _entryPrice_new = round(_notional_new/abs(_quantity_new), _precisions['price'])
                #Profit
                _profit = 0
            elif (_quantity_dirDelta < 0):
                #Entry Price
                if (_quantity_new == 0): _entryPrice_new = None
                else:                    _entryPrice_new = _position['entryPrice']
                #Profit
                if   (side == 'BUY'):  _profit = round(quantity*(_position['entryPrice']-tradePrice), _precisions['quote'])
                elif (side == 'SELL'): _profit = round(quantity*(tradePrice-_position['entryPrice']), _precisions['quote'])
            _tradingFee = round(quantity*tradePrice*_SIMULATION_MARKETTRADINGFEE, _precisions['quote'])
            _currentNotional = tradePrice*abs(_position['quantity'])
            _maintenanceMarginRate, _maintenanceAmount = atmEta_Constants.getMaintenanceMarginRateAndAmount(positionSymbol = positionSymbol, notional = _currentNotional)
            _maintenanceMargin_new = round(_currentNotional*_maintenanceMarginRate-_maintenanceAmount, _precisions['quote'])
            #[2]: Apply Values
            _position['entryPrice']        = _entryPrice_new
            _position['quantity']          = _quantity_new
            _position['maintenanceMargin'] = _maintenanceMargin_new
            _asset['crossWalletBalance']   = round(_asset['crossWalletBalance']+_profit-_tradingFee, _precisions['quote'])
            _position_positionInitialMargin_prev = _position['positionInitialMargin']
            _position['positionInitialMargin'] = round(tradePrice*abs(_position['quantity'])/_position_def['leverage'], _precisions['price'])
            if (_position_def['isolated'] == True):
                # _walletBalanceToTransfer = Balance from 'CrossWalletBalance' -> 'IsolatedWalletBalance' (Assuming all the other additional parameters (Insurance Fund, Open-Loss, etc) to be 1% of the notional value)
                #---Entry
                if (0 < _quantity_dirDelta): _walletBalanceToTransfer = round(quantity*tradePrice*((1/_position_def['leverage'])+0.01), _precisions['quote'])
                #---Exit
                elif (_quantity_dirDelta < 0):
                    if (_quantity_new == 0): _walletBalanceToTransfer = -_position['isolatedWalletBalance']
                    else:                    _walletBalanceToTransfer = -round(quantity*_position['entryPrice']/_position_def['leverage'], _precisions['quote'])
                _position['isolatedWalletBalance'] = round(_position['isolatedWalletBalance']+_walletBalanceToTransfer, _precisions['quote'])
                _asset['crossWalletBalance']            = round(_asset['crossWalletBalance']-_walletBalanceToTransfer,    _precisions['quote'])
                _asset['isolatedWalletBalance']         = round(_asset['isolatedWalletBalance']+_walletBalanceToTransfer, _precisions['quote'])
                _asset['isolatedPositionInitialMargin'] = round(_asset['isolatedPositionInitialMargin']-_position_positionInitialMargin_prev+_position['positionInitialMargin'], _precisions['quote'])
            else:
                _asset['crossPositionInitialMargin']    = round(_asset['crossPositionInitialMargin']-_position_positionInitialMargin_prev+_position['positionInitialMargin'], _precisions['quote'])
            #---Wallet, Margin and Available Balance
            _asset['walletBalance']    = _asset['crossWalletBalance']+_asset['isolatedWalletBalance']
            _asset['marginBalance']    = _asset['walletBalance']+_asset['unrealizedPNL']
            _asset['availableBalance'] = _asset['crossWalletBalance']-_asset['crossPositionInitialMargin']+_asset['unrealizedPNL']
        #Update Account
        self.__updateAccount(simulationCode = simulationCode, timestamp = timestamp)
        #Save Trade Log
        if (True):
            _tradeLog = {'timestamp':           timestamp, 
                         'positionSymbol':      positionSymbol,
                         'logicSource':         logicSource,
                         'side':                side,
                         'quantity':            quantity,
                         'price':               tradePrice,
                         'profit':              _profit,
                         'tradingFee':          _tradingFee,
                         'totalQuantity':       _quantity_new,
                         'entryPrice':          _entryPrice_new,
                         'walletBalance':       _asset['walletBalance'],
                         'tradeControlTracker': _position['tradeControlTracker']}
            _simulation['_tradeLogs'].append(_tradeLog)
        #Update Daily Report
        if (True):
            _dailyReport = _simulation['_dailyReports'][_simulation['_currentFocusDay']][_position_def['quoteAsset']]
            _dailyReport['nTrades'] += 1
            if   (side == 'BUY'):                _dailyReport['nTrades_buy']         += 1
            elif (side == 'SELL'):               _dailyReport['nTrades_sell']        += 1
            if   (logicSource == 'ENTRY'):       _dailyReport['nTrades_entry']       += 1
            elif (logicSource == 'CLEAR'):       _dailyReport['nTrades_clear']       += 1
            elif (logicSource == 'EXIT'):        _dailyReport['nTrades_exit']        += 1
            elif (logicSource == 'FSLIMMED'):    _dailyReport['nTrades_fslImmed']    += 1
            elif (logicSource == 'FSLCLOSE'):    _dailyReport['nTrades_fslClose']    += 1
            elif (logicSource == 'LIQUIDATION'): _dailyReport['nTrades_liquidation'] += 1
            if   (0 < _profit): _dailyReport['nTrades_gains']  += 1
            elif (_profit < 0): _dailyReport['nTrades_losses'] += 1
            _walletBalance = _asset['walletBalance']
            if (_walletBalance < _dailyReport['walletBalance_min']): _dailyReport['walletBalance_min'] = _walletBalance
            if (_dailyReport['walletBalance_max'] < _walletBalance): _dailyReport['walletBalance_max'] = _walletBalance
            _dailyReport['walletBalance_close'] = _asset['walletBalance']
    def __generateSimulationSummary(self, simulationCode):
        _simulation    = self.__simulations[simulationCode]
        _positions_def = _simulation['positions']
        _tradeLog      = _simulation['_tradeLogs']
        #Total Summary
        _nTrades_total = len(_tradeLog)
        if (0 < _nTrades_total):
            _dailyTS_firstLog = int(_tradeLog[0]['timestamp']/86400)*86400
            _nTradeDays = int((_simulation['simulationRange'][1]-_dailyTS_firstLog)/86400)+1
        else: _nTradeDays = 0
        _nTrades_buy         = 0
        _nTrades_sell        = 0
        _nTrades_entry       = 0
        _nTrades_clear       = 0
        _nTrades_exit        = 0
        _nTrades_fslImmed    = 0
        _nTrades_fslClose    = 0
        _nTrades_liquidation = 0
        _nTrades_gains       = 0
        _nTrades_losses      = 0
        for _log in _tradeLog:
            _side        = _log['side']
            _logicSource = _log['logicSource']
            _profit      = _log['profit']
            if   (_side == 'PIP_BUY'):  _nTrades_buy  += 1
            elif (_side == 'PIP_SELL'): _nTrades_sell += 1
            if   (_logicSource == 'ENTRY'):       _nTrades_entry       += 1
            elif (_logicSource == 'CLEAR'):       _nTrades_clear       += 1
            elif (_logicSource == 'EXIT'):        _nTrades_exit        += 1
            elif (_logicSource == 'FSLIMMED'):    _nTrades_fslImmed    += 1
            elif (_logicSource == 'FSLCLOSE'):    _nTrades_fslClose    += 1
            elif (_logicSource == 'LIQUIDATION'): _nTrades_liquidation += 1
            if   (0 < _profit): _nTrades_gains  += 1
            elif (_profit < 0): _nTrades_losses += 1
        simulationSummary = {'total': {'nTradeDays':          _nTradeDays,
                                       'nTrades_total':       _nTrades_total, 
                                       'nTrades_buy':         _nTrades_buy, 
                                       'nTrades_sell':        _nTrades_sell, 
                                       'nTrades_entry':       _nTrades_entry,
                                       'nTrades_clear':       _nTrades_clear,
                                       'nTrades_exit':        _nTrades_exit,
                                       'nTrades_fslImmed':    _nTrades_fslImmed,
                                       'nTrades_fslClose':    _nTrades_fslClose,
                                       'nTrades_liquidation': _nTrades_liquidation,
                                       'nTrades_gains':       _nTrades_gains,
                                       'nTrades_losses':      _nTrades_losses}}
        #Asset Summary
        _tradeLog_byAssets = dict()
        for _assetName in _simulation['assets']: _tradeLog_byAssets[_assetName] = list()
        for _log       in _tradeLog:             _tradeLog_byAssets[_positions_def[_log['positionSymbol']]['quoteAsset']].append(_log)
        for _assetName in _simulation['assets']:
            _tradeLog_thisAsset = _tradeLog_byAssets[_assetName]
            #---Bases
            _nTrades_total = len(_tradeLog_thisAsset)
            if (0 < _nTrades_total):
                _dailyTS_firstLog = int(_tradeLog_thisAsset[0]['timestamp']/86400)*86400
                _nTradeDays = int((_simulation['simulationRange'][1]-_dailyTS_firstLog)/86400)+1
            else: _nTradeDays = 0
            _nTrades_buy         = 0
            _nTrades_sell        = 0
            _nTrades_entry       = 0
            _nTrades_clear       = 0
            _nTrades_exit        = 0
            _nTrades_fslImmed    = 0
            _nTrades_fslClose    = 0
            _nTrades_liquidation = 0
            _nTrades_gains       = 0
            _nTrades_losses      = 0
            _gains_total      = 0
            _losses_total     = 0
            _tradingFee_total = 0
            _initialWalletBalance = _simulation['assets'][_assetName]['initialWalletBalance']
            _walletBalance_min    = _initialWalletBalance
            _walletBalance_max    = _initialWalletBalance
            _walletBalance_final  = _initialWalletBalance
            for _log in _tradeLog_thisAsset:
                _side        = _log['side']
                _logicSource = _log['logicSource']
                _profit      = _log['profit']
                if   (_side == 'PIP_BUY'):  _nTrades_buy  += 1
                elif (_side == 'PIP_SELL'): _nTrades_sell += 1
                if   (_logicSource == 'ENTRY'):       _nTrades_entry       += 1
                elif (_logicSource == 'CLEAR'):       _nTrades_clear       += 1
                elif (_logicSource == 'EXIT'):        _nTrades_exit        += 1
                elif (_logicSource == 'FSLIMMED'):    _nTrades_fslImmed    += 1
                elif (_logicSource == 'FSLCLOSE'):    _nTrades_fslClose    += 1
                elif (_logicSource == 'LIQUIDATION'): _nTrades_liquidation += 1
                if   (0 < _profit): _nTrades_gains  += 1
                elif (_profit < 0): _nTrades_losses += 1
                _profit = _log['profit']
                if   (_profit < 0): _losses_total += abs(_profit)
                elif (0 < _profit): _gains_total  += _profit
                _tradingFee_total += _log['tradingFee']
                _gains_total      = round(_gains_total,      _SIMULATION_ASSETPRECISIONS[_assetName])
                _losses_total     = round(_losses_total,     _SIMULATION_ASSETPRECISIONS[_assetName])
                _tradingFee_total = round(_tradingFee_total, _SIMULATION_ASSETPRECISIONS[_assetName])
                _walletBalance = _log['walletBalance']
                if (_walletBalance < _walletBalance_min): _walletBalance_min = _walletBalance
                if (_walletBalance_max < _walletBalance): _walletBalance_max = _walletBalance
            if (0 < _nTrades_total): _walletBalance_final = _tradeLog_thisAsset[-1]['walletBalance']
            #---Wallet Balance Trend Analysis
            _wbta_growthRate = None
            _wbta_volatility = None
            if (1 < _nTrades_total):
                _firstTradeLogTS = _tradeLog_thisAsset[0]['timestamp']
                _wbta_n      = len(_tradeLog_thisAsset)
                _wbta_sum_x  = 0.0
                _wbta_sum_xx = 0.0
                _wbta_sum_y  = 0.0
                _wbta_sum_yy = 0.0
                _wbta_sum_xy = 0.0
                for _log in _tradeLog_thisAsset:
                    _x = (_log['timestamp']-_firstTradeLogTS)/86400
                    _y = math.log(_log['walletBalance']) if (0 < _log['walletBalance']) else 0.0
                    _wbta_sum_x  += _x
                    _wbta_sum_xx += _x**2
                    _wbta_sum_y  += _y
                    _wbta_sum_yy += _y**2
                    _wbta_sum_xy += _x*_y
                _numerator   = (_wbta_n*_wbta_sum_xy)-(_wbta_sum_x*_wbta_sum_y)
                _denominator = (_wbta_n*_wbta_sum_xx)-(_wbta_sum_x*_wbta_sum_x)
                if (0 < _denominator):
                    _wbta_growthRate = _numerator/_denominator
                    _mean_x = _wbta_sum_x/_wbta_n
                    _mean_y = _wbta_sum_y/_wbta_n
                    _var_x = (_wbta_sum_xx/_wbta_n) - (_mean_x**2)
                    _var_y = (_wbta_sum_yy/_wbta_n) - (_mean_y**2)
                    _variance_resid  = max(_var_y-(_wbta_growthRate**2 * _var_x), 0.0)
                    _wbta_volatility = math.sqrt(_variance_resid)
            #---Finally
            simulationSummary[_assetName] = {#Counts
                                             'nTradeDays':    _nTradeDays, 
                                             'nTrades_total': _nTrades_total, 
                                             'nTrades_buy':   _nTrades_buy, 
                                             'nTrades_sell':  _nTrades_sell,
                                             'nTrades_entry':       _nTrades_entry, 
                                             'nTrades_clear':       _nTrades_clear, 
                                             'nTrades_exit':        _nTrades_exit, 
                                             'nTrades_fslImmed':    _nTrades_fslImmed, 
                                             'nTrades_fslClose':    _nTrades_fslClose, 
                                             'nTrades_liquidation': _nTrades_liquidation,
                                             'nTrades_gains':       _nTrades_gains, 
                                             'nTrades_losses':      _nTrades_losses,
                                             #Profit
                                             'gains':      _gains_total, 
                                             'losses':     _losses_total, 
                                             'tradingFee': _tradingFee_total,
                                             #Balance Trend
                                             'walletBalance_initial': _simulation['assets'][_assetName]['initialWalletBalance'], 
                                             'walletBalance_min':     _walletBalance_min, 
                                             'walletBalance_max':     _walletBalance_max, 
                                             'walletBalance_final':   _walletBalance_final, 
                                             'wbta_growthRate_daily': _wbta_growthRate, 
                                             'wbta_volatility':       _wbta_volatility}
        return simulationSummary
    def __savePPIPS(self, simulationCode):
        _simulation = self.__simulations[simulationCode]
        if (_simulation['ppips'][0] == True):
            #[1]: PPIPS Main Folder
            _path_Main = os.path.join(self.path_project, 'data', 'ppips')
            if (os.path.exists(_path_Main) == False): os.makedirs(_path_Main)

            #[2]: PPIPS Simulation Folder
            _index_Sim = None
            _path_Sim  = os.path.join(_path_Main, f"{simulationCode}_ppips")
            if (os.path.exists(_path_Sim) == False): os.makedirs(_path_Sim)
            else:
                _index_Sim = 0
                while (True):
                    _path_Sim = os.path.join(self.path_project, 'data', 'ppips', f"{simulationCode}_ppips_{_index_Sim}")
                    if (os.path.exists(_path_Sim) == False): os.makedirs(_path_Sim); break
                    else:                                    _index_Sim += 1

            #[3]: Numpy Conversion & Save
            _positions_def = _simulation['positions']
            _positions     = _simulation['_positions']
            for _pSymbol in _positions:
                _position_def = _positions_def[_pSymbol]
                _position     = _positions[_pSymbol]

                #File Name
                if (_index_Sim is None): _baseName = f"{simulationCode}_{_pSymbol}"
                else:                    _baseName = f"{simulationCode}_{_index_Sim}_{_pSymbol}"
                _path_files = dict()
                for _content, _fe in (('descriptor',          'json'), 
                                      ('data',                'npy'), 
                                      ('plot_kline'   ,       'png'), 
                                      ('plot_signalPDCyclic', 'png'),
                                      ('plot_swingPDCyclic',  'png'),
                                      ):
                    _path_files[_content] = os.path.join(_path_Sim, f"{_baseName}_{_content}.{_fe}")

                #Descriptor & Numpy Conversion
                _descriptor = {'genTime_ns':     time.time_ns(),
                               'simulationCode': simulationCode,
                               'positionSymbol': _pSymbol,
                               }
                _data_numpy = numpy.array(object = _position['PPIPS']['data'], dtype = numpy.float32)

                #Data Save
                numpy.save(file = _path_files['data'], arr = _data_numpy)
                with open(_path_files['descriptor'], 'w') as _f: _f.write(json.dumps(_descriptor))

                #Plot Image
                if (_simulation['ppips'][1] == True):
                    #---[1]: Candlestick
                    if (True):
                        #Plot Figure Settings
                        _dataLen = _data_numpy.shape[0]
                        _fig, _axs = matplotlib.pyplot.subplots(2, constrained_layout=True)
                        _axs[0].set_title("Candlestick Prices", fontsize=8)
                        _axs[1].set_title("Trade Volumes",      fontsize=8)
                        _axs[0].grid(True)
                        _axs[1].grid(True)
                        _axs[0].set_xlim(-int(_dataLen)*0.05, int(_dataLen)*1.05)
                        _axs[1].set_xlim(-int(_dataLen)*0.05, int(_dataLen)*1.05)
                        _axs[0].set_xlabel("Index",                                   fontsize=6)
                        _axs[1].set_xlabel("Index",                                   fontsize=6)
                        _axs[0].set_ylabel(f"Price [{_position_def['quoteAsset']}]",  fontsize=6)
                        _axs[1].set_ylabel(f"Volume [{_position_def['quoteAsset']}]", fontsize=6)
                        _axs[0].tick_params(axis='both', labelsize=6)
                        _axs[1].tick_params(axis='both', labelsize=6)
                        matplotlib.pyplot.suptitle(f"'{_baseName}' PPIPS - KLINE", fontsize=10)
                        #Drawing
                        _x = numpy.arange(_dataLen)
                        _highPrice  = _data_numpy[:,2]
                        _lowPrice   = _data_numpy[:,3]
                        _closePrice = _data_numpy[:,4]
                        _bav        = _data_numpy[:,5]
                        _bav_tb     = _data_numpy[:,6]
                        _axs[0].plot(_x, _closePrice, color=(0.0, 0.5, 1.0, 1.0), linestyle='solid',  linewidth=2, zorder = 2)
                        _axs[0].plot(_x, _highPrice,  color=(0.0, 1.0, 0.0, 0.5), linestyle='dashed', linewidth=1, zorder = 1)
                        _axs[0].plot(_x, _lowPrice,   color=(1.0, 0.0, 0.0, 0.5), linestyle='dashed', linewidth=1, zorder = 1)
                        _axs[1].plot(_x, _bav,        color=(1.0, 0.0, 0.0, 1.0), linestyle='solid',  linewidth=1, zorder = 2)
                        _axs[1].plot(_x, _bav_tb,     color=(1.0, 0.0, 0.0, 1.0), linestyle='dashed', linewidth=1, zorder = 1)
                        #---Plot Saving
                        _fig.savefig(_path_files['plot_kline'], dpi=150, bbox_inches='tight')
                        matplotlib.pyplot.close(_fig)
                    #---[2] Signal Price Deviation Cyclic
                    if (True):
                        #---Data Prep
                        _cycles_low    = list()
                        _cycles_high   = list()
                        _cycle_current = list()
                        _lastCycle_type  = None
                        _lastCycle_price = None
                        for _ppips_data_row in _position['PPIPS']['data']:
                            _closePrice = _ppips_data_row[4]
                            _pip_cs     = _ppips_data_row[10]
                            if (_pip_cs is None): continue
                            if (_lastCycle_type is None):
                                _lastCycle_type = -1 if _pip_cs < 0 else 1
                                _lastCycle_price = _closePrice
                                _cycle_current = [0.0,]
                                continue
                            _pd = (_closePrice-_lastCycle_price)/_lastCycle_price
                            if (_lastCycle_type == -1) and (0 < _pip_cs): 
                                _cycles_low.append(_cycle_current)
                                _lastCycle_type  = 1
                                _lastCycle_price = _closePrice
                                _cycle_current = [0.0,]
                            elif (_lastCycle_type == 1) and (_pip_cs < 0):
                                _cycles_high.append(_cycle_current)
                                _lastCycle_type  = -1
                                _lastCycle_price = _closePrice
                                _cycle_current = [0.0,]
                            else: _cycle_current.append(_pd)
                        if   (_lastCycle_type == -1): _cycles_low.append(_cycle_current)
                        elif (_lastCycle_type ==  1): _cycles_high.append(_cycle_current)
                        #---Plot Settings
                        _dataLen = max(max([len(_cycle) for _cycle in _cycles_low]  or [0]), 
                                    max([len(_cycle) for _cycle in _cycles_high] or [0]))
                        _fig, _axs = matplotlib.pyplot.subplots(3, constrained_layout=True)
                        _axs[0].set_title("LOW",  fontsize=8)
                        _axs[1].set_title("HIGH", fontsize=8)
                        _axs[2].set_title("ALL",  fontsize=8)
                        for _ax in _axs:
                            _ax.grid(True)
                            _ax.set_xlim(-int(_dataLen)*0.05, int(_dataLen)*1.05)
                            _ax.set_xlabel("N Candles",           fontsize=6)
                            _ax.set_ylabel("Price Deviation [%]", fontsize=6)
                            _ax.tick_params(axis='both', labelsize=6)
                        matplotlib.pyplot.suptitle(f"'{_baseName}' PPIPS - SIGNAL PRICE DEVIATION CYCLIC", fontsize=10)
                        #---Plot Drawing
                        for _cycle in _cycles_low:
                            _y = numpy.array(_cycle)*100
                            _x = numpy.arange(len(_y))
                            _axs[0].plot(_x, _y, color=(1.0, 0.0, 0.0, 0.1), linestyle='-', linewidth=1)
                            _axs[2].plot(_x, _y, color=(1.0, 0.0, 0.0, 0.1), linestyle='-', linewidth=1)
                        for _cycle in _cycles_high:
                            _y = numpy.array(_cycle)*100
                            _x = numpy.arange(len(_y))
                            _axs[1].plot(_x, _y, color=(0.0, 1.0, 0.0, 0.1), linestyle='-', linewidth=1)
                            _axs[2].plot(_x, _y, color=(0.0, 1.0, 0.0, 0.1), linestyle='-', linewidth=1)
                        #---Plot Saving
                        matplotlib.pyplot.savefig(_path_files['plot_signalPDCyclic'], dpi=150, bbox_inches='tight')
                        matplotlib.pyplot.close(_fig)
                    #---[3] Swing Price Deviation Cyclic
                    if (True):
                        #---Data Prep
                        _swings_low    = list()
                        _swings_high   = list()
                        _swing_current = list()
                        _lastSwing_type = None
                        for _ppips_data_row in _position['PPIPS']['data']:
                            _closePrice = _ppips_data_row[4]
                            _pip_lsType  = _ppips_data_row[7]
                            _pip_lsPrice = _ppips_data_row[8]
                            if (_pip_lsType is None): continue
                            if (_lastSwing_type is None):
                                _lastSwing_type  = _pip_lsType
                                _swing_current = [0.0,]
                                continue
                            _pd = (_closePrice-_pip_lsPrice)/_pip_lsPrice
                            if (_lastSwing_type == -1) and (_pip_lsType == 1): 
                                _swings_low.append(_swing_current)
                                _lastSwing_type  = 1
                                _swing_current = [0.0,]
                            elif (_lastSwing_type == 1) and (_pip_lsType == -1):
                                _swings_high.append(_swing_current)
                                _lastSwing_type  = -1
                                _swing_current = [0.0,]
                            else: _swing_current.append(_pd)
                        if   (_lastSwing_type == -1): _swings_low.append(_swing_current)
                        elif (_lastSwing_type ==  1): _swings_high.append(_swing_current)
                        #---Plot Settings
                        _dataLen = max(max([len(_cycle) for _cycle in _swings_low]  or [0]), 
                                    max([len(_cycle) for _cycle in _swings_high] or [0]))
                        _fig, _axs = matplotlib.pyplot.subplots(3, constrained_layout=True)
                        _axs[0].set_title("LOW",  fontsize=8)
                        _axs[1].set_title("HIGH", fontsize=8)
                        _axs[2].set_title("ALL",  fontsize=8)
                        for _ax in _axs:
                            _ax.grid(True)
                            _ax.set_xlim(-int(_dataLen)*0.05, int(_dataLen)*1.05)
                            _ax.set_xlabel("N Candles",           fontsize=6)
                            _ax.set_ylabel("Price Deviation [%]", fontsize=6)
                            _ax.tick_params(axis='both', labelsize=6)
                        matplotlib.pyplot.suptitle(f"'{_baseName}' PPIPS - SWING PRICE DEVIATION CYCLIC", fontsize=10)
                        #---Plot Drawing
                        for _cycle in _swings_low:
                            _y = numpy.array(_cycle)*100
                            _x = numpy.arange(len(_y))
                            _axs[0].plot(_x, _y, color=(1.0, 0.0, 0.0, 0.1), linestyle='-', linewidth=1)
                            _axs[2].plot(_x, _y, color=(1.0, 0.0, 0.0, 0.1), linestyle='-', linewidth=1)
                        for _cycle in _swings_high:
                            _y = numpy.array(_cycle)*100
                            _x = numpy.arange(len(_y))
                            _axs[1].plot(_x, _y, color=(0.0, 1.0, 0.0, 0.1), linestyle='-', linewidth=1)
                            _axs[2].plot(_x, _y, color=(0.0, 1.0, 0.0, 0.1), linestyle='-', linewidth=1)
                        #---Plot Saving
                        matplotlib.pyplot.savefig(_path_files['plot_swingPDCyclic'], dpi=150, bbox_inches='tight')
                        matplotlib.pyplot.close(_fig)
    def __raiseSimulationError(self, simulationCode, errorCause):
        _simulation = self.__simulations[simulationCode]
        _simulation['_status']   = 'ERROR'
        _simulation['_errorMsg'] = errorCause
        self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'onSimulationUpdate', functionParams = {'simulationCode': simulationCode, 'updateType': 'STATUS', 'updatedValue': _simulation['_status']}, farrHandler = None)
        self.__simulations_removalQueue.append(simulationCode)
        if (self.__simulations_currentlyHandling == simulationCode): self.__simulations_currentlyHandling = None
    def __processSimulationRemovalQueue(self):
        while (0 < len(self.__simulations_removalQueue)):
            _simulationCode = self.__simulations_removalQueue.pop(0)
            _hadNeuralNetworks = (0 < len(self.__simulations[_simulationCode]['_neuralNetworks']))
            del self.__simulations[_simulationCode]
            if (_hadNeuralNetworks == True): torch.cuda.empty_cache()
    #Manager Internal Functions END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #FAR Handlers -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<SIMULATIONMANAGER>
    def __far_setActivation(self, requester, activation):
        if (requester == 'SIMULATIONMANAGER'):
            self.__activation = activation
            if (self.__simulations_currentlyHandling != None):
                _simulationStatus = self.__simulations[self.__simulations_currentlyHandling]['_status']
                if (activation == True):
                    if (_simulationStatus == 'PAUSED'):
                        self.__simulations[self.__simulations_currentlyHandling]['_status'] = 'PROCESSING'
                        self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'onSimulationUpdate', functionParams = {'simulationCode': self.__simulations_currentlyHandling, 'updateType': 'STATUS', 'updatedValue': self.__simulations[self.__simulations_currentlyHandling]['_status']}, farrHandler = None)
                else:
                    if (_simulationStatus == 'PROCESSING'):
                        self.__simulations[self.__simulations_currentlyHandling]['_status'] = 'PAUSED'
                        self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'onSimulationUpdate', functionParams = {'simulationCode': self.__simulations_currentlyHandling, 'updateType': 'STATUS', 'updatedValue': self.__simulations[self.__simulations_currentlyHandling]['_status']}, farrHandler = None)
    def __far_addSimulation(self, requester, simulationCode, simulationRange, ppips, assets, positions, currencyAnalysisConfigurations, tradeConfigurations, creationTime):
        if (requester == 'SIMULATIONMANAGER'):
            #[1]: Construct Analysis Params
            _analyzers = dict()
            for _cacCode in currencyAnalysisConfigurations:
                _analysisParams = atmEta_Analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(currencyAnalysisConfigurations[_cacCode])
                _analysisToProcess_sorted = list()
                for analysisType in atmEta_Analyzers.ANALYSIS_GENERATIONORDER: _analysisToProcess_sorted += [(analysisType, analysisCode) for analysisCode in _analysisParams if analysisCode[:len(analysisType)] == analysisType]
                _analyzers[_cacCode] = {'analysisParams':           _analysisParams,
                                        'analysisToProcess_sorted': _analysisToProcess_sorted}
            #[2]: Format Assets
            assets_formatted = dict()
            for _assetName in assets:
                _iwb = assets[_assetName]['initialWalletBalance']
                assets_formatted[_assetName] = {'marginBalance':                 _iwb,
                                                'walletBalance':                 _iwb,
                                                'isolatedWalletBalance':         0,
                                                'isolatedPositionInitialMargin': 0,
                                                'crossWalletBalance':            _iwb,
                                                'openOrderInitialMargin':        0,
                                                'crossPositionInitialMargin':    0,
                                                'crossMaintenanceMargin':        0, 
                                                'unrealizedPNL':                 0,
                                                'isolatedUnrealizedPNL':         0,
                                                'crossUnrealizedPNL':            0,
                                                'availableBalance':              _iwb,
                                                #Positional Distribution
                                                'allocatableBalance': 0,
                                                'allocatedBalance':   0,
                                                #Risk Management
                                                'commitmentRate': None,
                                                'riskLevel':      None}
            #[3]: Format Positions
            positions_formatted = dict()
            for _pSymbol in positions:
                positions_formatted[_pSymbol] = {#Base
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
                                                 'tradeControlTracker': {'slExited':      False,
                                                                         'rqpm_val_prev': None,
                                                                         'rqpm_model':    dict()},
                                                 #External Analysis
                                                 'PPIPS': {'index': None,
                                                           'data':  list()}
                                                 }

            #[4]: Create a simulation instance
            _simulation = {'simulationRange':                simulationRange,
                           'ppips':                          ppips,
                           'assets':                         assets,
                           'positions':                      positions,
                           'currencyAnalysisConfigurations': currencyAnalysisConfigurations,
                           'tradeConfigurations':            tradeConfigurations,
                           'creationTime':                   creationTime,
                           '_neuralNetworks':                           dict(),
                           '_neuralNetworks_connectionsDataRequestIDs': set(),
                           '_neuralNetworkCodes_byCACCodes':            dict(),
                           '_assets':                   assets_formatted,
                           '_positions':                positions_formatted,
                           '_analyzers':                _analyzers,
                           '_klines':                   dict(),
                           '_klines_dataRange':         dict(),
                           '_klines_lastRemovedOpenTS': dict(),
                           '_klines_fetchRequestIDs':   dict(),
                           '_status':             'QUEUED',
                           '_procStatus':         None,
                           '_completion':         None,
                           '_currentFocusDay':    int(simulationRange[0]/86400)*86400,
                           '_nextAnalysisTarget': None,
                           '_lastAnalysisTarget': atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = simulationRange[1], mrktReg = None, nTicks = 0),
                           '_errorMsg':           None,
                           '_tradeLogs':          list(),
                           '_dailyReports':       dict(),
                           '_simulationSummary':  None}
            #[5]: Position-dependent variables
            for _pSymbol in _simulation['_positions']: 
                _simulation['_klines'][_pSymbol]                   = {'raw': dict(), 'raw_status': dict()}
                _simulation['_klines_dataRange'][_pSymbol]         = positions[_pSymbol]['dataRange']
                _simulation['_klines_lastRemovedOpenTS'][_pSymbol] = {'raw': None}
                _analysisParams = _simulation['_analyzers'][_simulation['positions'][_pSymbol]['currencyAnalysisConfigurationCode']]['analysisParams']
                for analysisCode in _analysisParams: _simulation['_klines'][_pSymbol][analysisCode] = dict(); _simulation['_klines_lastRemovedOpenTS'][_pSymbol][analysisCode] = None
            #[6]: Add the created simulation instance and append to the handling queue
            self.__simulations[simulationCode] = _simulation
            self.__simulations_handlingQueue.append(simulationCode)
    def __far_removeSimulation(self, requester, simulationCode):
        if (requester == 'SIMULATIONMANAGER'):
            if (simulationCode in self.__simulations):
                _simulation = self.__simulations[simulationCode]
                if (_simulation['_status'] == 'QUEUED'):
                    self.__simulations_handlingQueue.remove(simulationCode)
                    self.__simulations_removalQueue.append(simulationCode)
                elif (_simulation['_status'] == 'PROCESSING'):
                    self.__simulations_removalQueue.append(simulationCode)
                if (self.__simulations_currentlyHandling == simulationCode): self.__simulations_currentlyHandling = None
            self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'removeSimulationData', functionParams = {'simulationCode': simulationCode}, farrHandler = None)

    #<DATAMANAGER>
    def __farr_onKlineFetchResponse(self, responder, requestID, functionResult):
        if (responder == 'DATAMANAGER'):
            if (self.__simulations_currentlyHandling != None):
                _simulationCode = self.__simulations_currentlyHandling
                _simulation     = self.__simulations[_simulationCode]
                if (requestID in _simulation['_klines_fetchRequestIDs']):
                    _pSymbol = _simulation['_klines_fetchRequestIDs'][requestID]
                    requestResult_result = functionResult['result']
                    requestResult_klines = functionResult['klines']
                    #[1-1]: On Successful Kline Fetch
                    if (requestResult_result == 'SKF'):
                        _klines = _simulation['_klines'][_pSymbol]
                        for kline in requestResult_klines: # ([0]: openTS, [1]: closeTS, [2]: openPrice, [3]: highPrice, [4]: lowPrice, [5]: closePrice, [6]: nTrades, [7]: baseAssetVolume, [8]: quoteAssetVolume, [9]: baseAssetVolume_takerBuy, [10]: quoteAssetVolume_takerBuy)
                            t_open = kline[0]
                            #Raw
                            if (((kline[2] == None) or (kline[3] == None) or (kline[4] == None) or (kline[5] == None)) and (t_open-KLINTERVAL_S in _klines['raw'])): 
                                kline_prev = _klines['raw'][t_open-KLINTERVAL_S]
                                kline = (kline[0], kline[0], kline_prev[5], kline_prev[5], kline_prev[5], kline_prev[5], 0, 0, 0, 0)
                            _klines['raw'][t_open] = kline[:11] + (True,)
                            #Raw Status
                            p_high = kline[3]
                            _klines['raw_status'][t_open] = {'p_max': p_high}
                            if (t_open-KLINTERVAL_S in _klines['raw_status']):
                                p_max_prev = _klines['raw_status'][t_open-KLINTERVAL_S]['p_max']
                                if ((p_max_prev != None) and (p_high < p_max_prev)): _klines['raw_status'][t_open]['p_max'] = p_max_prev
                    #[1-2]: On unexpected error occurrence
                    elif (requestResult_result == 'UEO'): pass
                    #[2]: Remove the requestID from the tracker
                    del _simulation['_klines_fetchRequestIDs'][requestID]
    def __farr_onSimulationDataSaveRequestResponse(self, responder, requestID, functionResult):
        if (responder == 'DATAMANAGER'):
            fr_simulationCode = functionResult['simulationCode']
            fr_saveResult     = functionResult['saveResult']
            fr_errorMsg       = functionResult['errorMsg']
            if (fr_simulationCode in self.__simulations): _simulation = self.__simulations[fr_simulationCode]
            else:                                         _simulation = None
            if ((_simulation != None) and (_simulation['_status'] == 'PROCESSING') and (_simulation['_procStatus'] == 'SAVING')):
                if (fr_saveResult == True):
                    _simulation['_status'] = 'COMPLETED'
                    self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'onSimulationCompletion', functionParams = {'simulationCode': fr_simulationCode, 'simulationSummary': _simulation['_simulationSummary']}, farrHandler = None)
                    self.__simulations_removalQueue.append(fr_simulationCode)
                    self.__simulations_currentlyHandling = None
                else: self.__raiseSimulationError(simulationCode = fr_simulationCode, errorCause = fr_errorMsg)

    #<NEURALNETWORKMANAGER>
    def __farr_onNeuralNetworkConnectionsDataRequestResponse(self, responder, requestID, functionResult):
        if (responder == 'NEURALNETWORKMANAGER'):
            _simulationCode = self.__simulations_currentlyHandling
            _simulation     = self.__simulations[_simulationCode]
            if (requestID in _simulation['_neuralNetworks_connectionsDataRequestIDs']):
                _simulation['_neuralNetworks_connectionsDataRequestIDs'].remove(requestID)
                if (functionResult != None):
                    #Get results
                    _neuralNetworkCode  = functionResult['neuralNetworkCode']
                    _nKlines            = functionResult['nKlines']
                    _analysisReferences = functionResult['analysisReferences']
                    _hiddenLayers       = functionResult['hiddenLayers']
                    _outputLayer        = functionResult['outputLayer']
                    _connections        = functionResult['connections']
                    #Generate a neural network instance and prepare it
                    _neuralNetwork = atmEta_NeuralNetworks.neuralNetwork_MLP(nKlines = _nKlines, analysisReferences = _analysisReferences, hiddenLayers = _hiddenLayers, outputLayer = _outputLayer, device = 'cpu')
                    _neuralNetwork.importConnectionsData(connections = _connections)
                    _neuralNetwork.setEvaluationMode()
                    _simulation['_neuralNetworks'][_neuralNetworkCode] = _neuralNetwork
                    #If this is the last neural networks connections data receival, continue the simulation to the next process
                    if (len(_simulation['_neuralNetworks_connectionsDataRequestIDs']) == 0): 
                        _simulation['_procStatus'] = 'FETCHING'
                        self.__sendKlineFetchRequestForTheCurrentFocusDay(simulationCode = _simulationCode)
                else: self.__raiseSimulationError(simulationCode = _simulationCode, errorCause = 'NONEURALNETWORKFOUND')
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------