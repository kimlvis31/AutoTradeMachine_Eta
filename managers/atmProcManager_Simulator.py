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
import scipy
import numpy
import torch
import matplotlib.pyplot
import json
import os

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

_SIMULATION_MARKETTRADINGFEE             = 0.0005
_SIMULATION_ASSUMEDMAINTENANCEMARGINRATE = 0.01

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
                            _simulation['_detailedReport']    = self.__generateSimulationDetailedReport(simulationCode = _simulationCode)
                            self.__saveSimulationCycleData(simulationCode = _simulationCode)
                            #Send simulation data save request to DATAMANAGER
                            self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'saveSimulationData', functionParams = {'simulationCode':                 _simulationCode, 
                                                                                                                                  'simulationRange':                _simulation['simulationRange'],
                                                                                                                                  'currencyAnalysisConfigurations': _simulation['currencyAnalysisConfigurations'],
                                                                                                                                  'tradeConfigurations':            _simulation['tradeConfigurations'],
                                                                                                                                  'assets':                         _simulation['assets'],
                                                                                                                                  'positions':                      _simulation['positions'],
                                                                                                                                  'creationTime':                   _simulation['creationTime'],
                                                                                                                                  'tradeLogs':                      _simulation['_tradeLogs'],
                                                                                                                                  'dailyReports':                   _simulation['_dailyReports'],
                                                                                                                                  'simulationSummary':              _simulation['_simulationSummary'],
                                                                                                                                  'detailedReport':                 _simulation['_detailedReport']},
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
        #[2]: Generate Analysis and Handle Any Generated PIPs
        for _pSymbol in _simulation['_positions']:
            #Instantiate
            _position_def = _simulation['positions'][_pSymbol]
            _position     = _simulation['_positions'][_pSymbol]
            _asset        = _simulation['_assets'][_position_def['quoteAsset']]
            _tc           = _simulation['tradeConfigurations'][_simulation['positions'][_pSymbol]['tradeConfigurationCode']]
            _precisions   = _position_def['precisions']
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
                _openPrice  = _kline[KLINDEX_OPENPRICE]
                _highPrice  = _kline[KLINDEX_HIGHPRICE]
                _lowPrice   = _kline[KLINDEX_LOWPRICE]
                _closePrice = _kline[KLINDEX_CLOSEPRICE]
                #[1]: Maximum Profit Price Update
                if (_position['quantity'] != 0):
                    if (0 < _position['quantity']):
                        if (_position['maximumProfitPrice'] < _highPrice): _position['maximumProfitPrice'] = _highPrice
                    elif (_position['quantity'] < 0):
                        if (_lowPrice < _position['maximumProfitPrice']): _position['maximumProfitPrice'] = _lowPrice
                #[2]: Analysis Generation
                if (True):
                    nKlinesToKeep_max = 0
                    for _analysisPair in _analyzer['analysisToProcess_sorted']:
                        _analysisType = _analysisPair[0]; _analysisCode = _analysisPair[1]
                        #---Analysis Generation
                        nAnalysisToKeep, nKlinesToKeep = atmEta_Analyzers.analysisGenerator(analysisType  = _analysisType, 
                                                                                            klineAccess   = _klines, 
                                                                                            intervalID    = KLINTERVAL,
                                                                                            mrktRegTS     = None,
                                                                                            precisions    = _simulation['positions'][_pSymbol]['precisions'], 
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
                #[3]: Trade Processing
                if (('PIP' in _klines) and (_kline[5] != 0)):
                    _pipResult = _klines['PIP'][_analysisTargetTS]
                    _tc_tcm  = _tc['tcMode']
                    _pip_asm = _pipResult['ACTIONSIGNALMODE']
                    if   ((_tc_tcm == 'TS')   and (_pip_asm == 'IMPULSIVE')): self.__handlePIPResult_TS(simulationCode   = _simulationCode, pSymbol = _pSymbol, pipResult = _pipResult, timestamp = _analysisTargetTS, kline = _kline) #[1]: Trade Control Mode - Trade Scenario
                    elif ((_tc_tcm == 'RQPM') and (_pip_asm == 'CYCLIC')):    self.__handlePIPResult_RQPM(simulationCode = _simulationCode, pSymbol = _pSymbol, pipResult = _pipResult, timestamp = _analysisTargetTS, kline = _kline) #[2]: Trade Control Mode - Remaining Quantity Percentage Map
                    #Cycle Records
                    if (_simulation['_cycleData'][0] == True):
                        _cycleData = _position['CycleData']
                        #[1]: On Cycle Update
                        if ((_pipResult['CLASSICALSIGNAL_CYCLEUPDATED'] == True) and (0 < len(_pipResult['SWINGS']))):
                            if   (_pipResult['CLASSICALSIGNAL_CYCLE'] == 'LOW'):  _type = 'SHORT'
                            elif (_pipResult['CLASSICALSIGNAL_CYCLE'] == 'HIGH'): _type = 'LONG'
                            _newCycleTracker = {'type':        _type,
                                                'beginPrice':  _closePrice,
                                                'beginTS':     _analysisTargetTS,
                                                'history':     list(),
                                                'progression': 0}
                            _cycleData['TrackingCycles'].append(_newCycleTracker)
                        #[2]: Cycle Tracker Update
                        for _cTracker in _cycleData['TrackingCycles']:
                            _pDPerc           = round((_closePrice-_cTracker['beginPrice'])    /_cTracker['beginPrice'], 4)
                            _pDPerc_lastSwing = round((_closePrice-_pipResult['SWINGS'][-1][1])/_cTracker['beginPrice'], 4)
                            if   (_cTracker['type'] == 'SHORT'): _pDPerc_reverseMax = round((_highPrice-_cTracker['beginPrice'])/_cTracker['beginPrice'], 4) #SHORT
                            elif (_cTracker['type'] == 'LONG'):  _pDPerc_reverseMax = round((_lowPrice -_cTracker['beginPrice'])/_cTracker['beginPrice'], 4) #LONG
                            _signalStrength   = round(_pipResult['CLASSICALSIGNAL_FILTERED'], 8)
                            _cTracker['history'].append((_pDPerc, _pDPerc_lastSwing, _pDPerc_reverseMax, _signalStrength))
                            _cTracker['progression'] += 1
                        #[3]: Expired Cycles
                        while (0 < len(_cycleData['TrackingCycles'])):
                            _cTracker = _cycleData['TrackingCycles'][0]
                            #Termination Mode
                            if (_simulation['_cycleData'][1] == None): _terminate = (_pipResult['CLASSICALSIGNAL_CYCLEUPDATED'] == True) and (_cTracker['beginTS'] < _analysisTargetTS) and \
                                                                                    (((_cTracker['type'] == 'SHORT') and (_pipResult['CLASSICALSIGNAL_CYCLE'] == 'HIGH')) or \
                                                                                     ((_cTracker['type'] == 'LONG')  and (_pipResult['CLASSICALSIGNAL_CYCLE'] == 'LOW')))
                            else: _terminate = (_cTracker['progression'] == _simulation['_cycleData'][1])
                            if (_terminate == True):
                                _cycleData['CycleRecords'].append({'type': _cTracker['type'], 'beginTS': _cTracker['beginTS'], 'history': _cTracker['history']})
                                _cycleData['TrackingCycles'].pop(0)
                            else: break

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
    def __handlePIPResult_TS(self, simulationCode, pSymbol, pipResult, timestamp, kline):
        #Instances Call
        _simulation = self.__simulations[simulationCode]
        _position_def = _simulation['positions'][pSymbol]
        _position     = _simulation['_positions'][pSymbol]
        _asset        = _simulation['_assets'][_position_def['quoteAsset']]
        _tc           = _simulation['tradeConfigurations'][_simulation['positions'][pSymbol]['tradeConfigurationCode']]
        _precisions   = _position_def['precisions']
        #PIP Action Signal
        if (pipResult['ACTIONSIGNAL'] == None):
            _pas_side         = None
            _pas_allowEntry   = None
        else:
            _pas_side         = pipResult['ACTIONSIGNAL']['side']
            _pas_allowEntry   = pipResult['ACTIONSIGNAL']['allowEntry']
        #PIP Action Signal Interpretation
        _tradeHandler_checkList = {'PIP_ENTRY':   None,
                                   'PIP_EXIT':    None,
                                   'PIP_PSL':     None,
                                   'LIQUIDATION': None,
                                   'RQP_EXIT':    None}
        _tradeHandler_checkList_priceBased = list()
        #---CheckList 1: PIP ENTRY
        if (True):
            if (_position['quantity'] == 0):
                if (pipResult['ACTIONSIGNAL'] != None):
                    if (_pas_allowEntry == True):
                        if (_pas_side == 'BUY'):
                            if ((_tc['direction'] == 'LONG') or (_tc['direction'] == 'BOTH')): _tradeHandler = ('PIP_ENTRY', 'BUY')
                        elif (_pas_side == 'SELL'):
                            if ((_tc['direction'] == 'SHORT') or (_tc['direction'] == 'BOTH')): _tradeHandler = ('PIP_ENTRY', 'SELL')
        #---CheckList 2: FSL Immediate
        if (True):
            if (_position['quantity'] != 0):
                if (_tc['rqpm_fullStopLoss'] != None):
                    if (_position['quantity'] < 0):
                        _price_FSL = round(_position['entryPrice']*(1+_tc['rqpm_fullStopLoss']), _precisions['price'])
                        if (_price_FSL <= kline[KLINDEX_HIGHPRICE]): _tradeHandler_checkList['FSL'] = ('BUY', -_position['quantity'], _price_FSL)
                    elif (0 < _position['quantity']):
                        _price_FSL = round(_position['entryPrice']*(1-_tc['rqpm_fullStopLoss']), _precisions['price'])
                        if (kline[KLINDEX_LOWPRICE] <= _price_FSL): _tradeHandler_checkList['FSL'] = ('SELL', _position['quantity'], _price_FSL)
        #---CheckList 3: FSL Close
        if (True):
            if (_position['quantity'] != 0):
                if (_tc['rqpm_fullStopLoss'] != None):
                    if (_position['quantity'] < 0):
                        _price_FSL = round(_position['entryPrice']*(1+_tc['rqpm_fullStopLoss']), _precisions['price'])
                        if (_price_FSL <= kline[KLINDEX_HIGHPRICE]): _tradeHandler_checkList['FSL'] = ('BUY', -_position['quantity'], kline[KLINDEX_CLOSEPRICE])
                    elif (0 < _position['quantity']):
                        _price_FSL = round(_position['entryPrice']*(1-_tc['rqpm_fullStopLoss']), _precisions['price'])
                        if (kline[KLINDEX_LOWPRICE] <= _price_FSL): _tradeHandler_checkList['FSL'] = ('SELL', _position['quantity'], kline[KLINDEX_CLOSEPRICE])
        #---CheckList 4: LIQUIDATION
        if (True):
            if (_position['quantity'] != 0):
                if (_position['liquidationPrice'] != None):
                    if (_position['quantity'] < 0):
                        if (_position['liquidationPrice'] <= kline[KLINDEX_HIGHPRICE]): _tradeHandler_checkList['LIQUIDATION'] = ('LIQUIDATION', -_position['quantity'], _position['liquidationPrice'])
                    elif (0 < _position['quantity']):
                        if (kline[KLINDEX_LOWPRICE] <= _position['liquidationPrice']): _tradeHandler_checkList['LIQUIDATION'] = ('LIQUIDATION', _position['quantity'], _position['liquidationPrice'])
        #---CheckList 5: WR (Weight Reduce)
        if (True):
            if ((_tradeHandler == None) and (_tc['weightReduce'] != None)):
                #WR Price Test
                _wrPriceTestPassed = False
                if (0 < _position['quantity']):
                    _price_WR = round(_position['entryPrice']*(1+_tc['weightReduce'][0]), _precisions['price'])
                    if (_price_WR <= kline[KLINDEX_HIGHPRICE]): _wrPriceTestPassed = True
                elif (_position['quantity'] < 0):
                    _price_WR = round(_position['entryPrice']*(1-_tc['weightReduce'][0]), _precisions['price'])
                    if (kline[KLINDEX_LOWPRICE] <= _price_WR): _wrPriceTestPassed = True
                #Quantity Test
                if (_wrPriceTestPassed == True):
                    _quantity_minUnit = pow(10, -_precisions['quantity'])
                    _quantity_postWR  = round(int((_position['allocatedBalance']*_tc['weightReduce'][1]/_price_WR*_tc['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                    _quantity_WR      = round(abs(_position['quantity'])-_quantity_postWR, _precisions['quantity'])
                    if (0 < _quantity_WR): _tradeHandler = ('WR', _price_WR, _quantity_WR)
        #---CheckList 6: RAF (Reach And Fall)
        if (True):
            if ((_tradeHandler == None) and (_tc['reachAndFall'] != None) and (_position['maximumProfitPrice'] != None)):
                if (0 < _position['quantity']):
                    _activationPoint1 = round(_position['entryPrice']*(1+_tc['reachAndFall'][0]), _precisions['price'])
                    _activationPoint2 = round(_position['entryPrice']*(1+_tc['reachAndFall'][1]), _precisions['price'])
                    if ((_activationPoint1 <= _position['maximumProfitPrice']) and (kline[KLINDEX_LOWPRICE] <= _activationPoint2)): _tradeHandler = ('RAF', _activationPoint2)
                elif (_position['quantity'] < 0):
                    _activationPoint1 = round(_position['entryPrice']*(1-_tc['reachAndFall'][0]), _precisions['price'])
                    _activationPoint2 = round(_position['entryPrice']*(1-_tc['reachAndFall'][1]), _precisions['price'])
                    if ((_position['maximumProfitPrice'] <= _activationPoint1) and (_activationPoint2 <= kline[KLINDEX_HIGHPRICE])): _tradeHandler = ('RAF', _activationPoint2)
        #---CheckList 7: PIP EXIT & PSL
        if (_tradeHandler == None):
            if (pipResult['ACTIONSIGNAL'] != None):
                #Holding LONG
                if (0 < _position['quantity']):
                    if (_pas_side == 'BUY'):
                        if ((_pas_allowEntry == True) and ((_tc['direction'] == 'LONG') or (_tc['direction'] == 'BOTH'))): _tradeHandler = ('PIP_ENTRY', 'BUY')
                    elif (_pas_side == 'SELL'):
                        if   (_position['entryPrice'] <= kline[KLINDEX_CLOSEPRICE]): _tradeHandler = ('PIP_EXIT', 'SELL')
                        else:                                                        _tradeHandler = ('PIP_PSL',  'SELL')
                #Holding SHORT
                elif (_position['quantity'] < 0):
                    if (_pas_side == 'SELL'): 
                        if ((_pas_allowEntry == True) and ((_tc['direction'] == 'SHORT') or (_tc['direction'] == 'BOTH'))): _tradeHandler = ('PIP_ENTRY', 'SELL')
                    elif (_pas_side == 'BUY'):
                        if   (kline[KLINDEX_CLOSEPRICE] <= _position['entryPrice']): _tradeHandler = ('PIP_EXIT', 'BUY')
                        else:                                                        _tradeHandler = ('PIP_PSL',  'BUY')
        #---Trade Handlers Determination
        _tradeHandlers = list()
        if (True):
            _tradeHandler_checkList_priceBased.sort(key = lambda x: x[1])
            if (len(_tradeHandler_checkList_priceBased) == 0): _tradeHandler_priceBasedClearing_firstTriggerred = None
            else:                                              _tradeHandler_priceBasedClearing_firstTriggerred = _tradeHandler_checkList_priceBased[0][0]
            if (_tradeHandler_checkList['RQP_ENTRY'] != None):
                if   (_tradeHandler_priceBasedClearing_firstTriggerred is not None): _tradeHandlers = [_tradeHandler_priceBasedClearing_firstTriggerred, 'RQP_ENTRY']
                elif (_tradeHandler_checkList['FSLCLOSE']              is not None): _tradeHandlers = ['FSLCLOSE',                                       'RQP_ENTRY']

                if   (_tradeHandler_checkList['FSL']         != None): _tradeHandlers = ['FSL',         'RQP_ENTRY']
                elif (_tradeHandler_checkList['LIQUIDATION'] != None): _tradeHandlers = ['LIQUIDATION', 'RQP_ENTRY']
                elif (_tradeHandler_checkList['RQP_CLEAR']   != None): _tradeHandlers = ['RQP_CLEAR',   'RQP_ENTRY']
                else:                                                  _tradeHandlers = ['RQP_ENTRY',]
            else:
                if   (_tradeHandler_checkList['FSL']         != None): _tradeHandlers = ['FSL',]
                elif (_tradeHandler_checkList['LIQUIDATION'] != None): _tradeHandlers = ['LIQUIDATION',]
                elif (_tradeHandler_checkList['RQP_CLEAR']   != None): _tradeHandlers = ['RQP_CLEAR',]
                elif (_tradeHandler_checkList['RQP_EXIT']    != None): _tradeHandlers = ['RQP_EXIT',]
        #Trade Handlers Execution
        for _tradeHandler in _tradeHandlers:
            _thParams = _tradeHandler_checkList[_tradeHandler]

            if (_tradeHandler == 'PIP_ENTRY'):
                pass
            elif (_tradeHandler == 'PIP_EXIT'):
                pass
            elif (_tradeHandler == 'PIP_PSL'):
                pass
            elif (_tradeHandler == 'ESCAPE'):
                pass
            elif (_tradeHandler == 'FSL'):
                pass
            elif (_tradeHandler == 'RAF'):
                pass
            elif (_tradeHandler == 'WR'):
                pass
            elif (_tradeHandler == 'LIQUIDATION'):
                pass

            #---[1]: PIP ENTRY
            if (_tradeHandler[0] == 'PIP_ENTRY'):
                #[1]: Allocated / Committed Balance / Initial Entry Price
                if (_position['allocatedBalance'] == None): _allocatedBalance = 0
                else:                                       _allocatedBalance = _position['allocatedBalance']
                if (_position['entryPrice'] == None): _committedBalance = 0
                else:                                 _committedBalance = abs(_position['quantity'])*_position['entryPrice']/_tc['leverage']
                if ((_position['quantity'] != 0) and (_position['initialEntryPrice'] == None)): _position['initialEntryPrice'] = _position['entryPrice']
                #[2]: Quantity Determination
                _quantity_minUnit = pow(10, -_precisions['quantity'])
                _quantity         = None
                #---Initial Entry
                if (_position['initialEntryPrice'] == None):
                    if (0 < len(_tc['method_entry'])): 
                        _sd = _tc['method_entry'][0]
                        _targetCommittedBalance = round(_allocatedBalance*_sd[1], _precisions['quote'])
                        _quantity = round(int((_targetCommittedBalance/kline[KLINDEX_CLOSEPRICE]*_tc['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                #---Additional Entry
                else:
                    #From all the satisfied trade scenarios, find the maximum targeting quantity
                    _targetMaxQuantity_perc = None
                    for _sd in _tc['method_entry']:
                        if (((0 < _position['quantity']) and (_sd[0] <= -(kline[KLINDEX_CLOSEPRICE]/_position['initialEntryPrice']-1))) or ((_position['quantity'] < 0) and (_sd[0] <= (kline[KLINDEX_CLOSEPRICE]/_position['initialEntryPrice']-1)))):
                            if ((_targetMaxQuantity_perc == None) or (_targetMaxQuantity_perc < _sd[1])): _targetMaxQuantity_perc = _sd[1]
                    #Determine the quantity to enter additionally
                    if (_targetMaxQuantity_perc != None):
                        _targetCommittedBalance      = round(_allocatedBalance*_targetMaxQuantity_perc, _precisions['quote'])
                        _additionallyRequiredBalance = _targetCommittedBalance-_committedBalance
                        if (0 < _additionallyRequiredBalance): _quantity = round(int((_additionallyRequiredBalance/kline[KLINDEX_CLOSEPRICE]*_tc['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                #[3]: If the quantity check passed, send an order creation request
                if ((_quantity != None) and (0 < _quantity)):
                    self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = _pSymbol, logicSource = 'PIP_ENTRY', side = 'BUY',  quantity = _quantity, timestamp = _analysisTargetTS, tradePrice = _closePrice)
                    #if   (_pipActionSignal[0] == 'BUY'):  self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'PIP_ENTRY', side = 'BUY',  quantity = _quantity, timestamp = _analysisTargetTS, tradePrice = _closePrice)
                    #elif (_pipActionSignal[0] == 'SELL'): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'PIP_ENTRY', side = 'SELL', quantity = _quantity, timestamp = _analysisTargetTS, tradePrice = _closePrice)
                    _position['tm_entryTimestamp']            = timestamp
                    _position['tm_initialQuantity']           = _quantity

                    _position['tm_maximumProfitPrice']        = kline[KLINDEX_CLOSEPRICE]
                    _position['tm_takeProfitPrice']           = _pr_tpPrice
                    _position['tm_stopLossPrice']             = _pr_slPrice
                    _position['tm_partialTakeProfitExecuted'] = False

                    _position['tradeControl'] = {'initialEntryPrice':         None,
                                                 'initialQuantity':           _quantity,
                                                 'takeProfitPrice':           _pr_tpPrice,
                                                 'stopLossPrice':             _pr_slPrice,
                                                 'maximumProfitPrice':        _closePrice,
                                                 'partialTakeProfitExecuted': False,
                                                 'entryTimestamp':            _analysisTargetTS}
            #---[2]: PIP EXIT
            elif (_tradeHandler[0] == 'PIP_EXIT'):
                #[1]: Allocated / Committed Balance
                if (_position['allocatedBalance'] == None): _allocatedBalance = 0
                else:                                       _allocatedBalance = _position['allocatedBalance']
                if (_position['entryPrice'] == None): _committedBalance = 0
                else:                                 _committedBalance = abs(_position['quantity'])*_position['entryPrice']/_tc['leverage']
                #[2]: Quantity Determination
                _quantity_minUnit = pow(10, -_precisions['quantity'])
                _quantity         = None
                #---From all the satisfied trade scenarios, find the minimum targeting quantity
                _targetMinQuantity_perc = None
                for _sd in _tc['method_exit']:
                    if (((0 < _position['quantity']) and (_sd[0] <= (_closePrice/_position['entryPrice']-1))) or ((_position['quantity'] < 0) and (_sd[0] <= -(_closePrice/_position['entryPrice']-1)))):
                        if ((_targetMinQuantity_perc == None) or (_sd[1] < _targetMinQuantity_perc)): _targetMinQuantity_perc = _sd[1]
                #---Determine the quantity to exit
                if (_targetMinQuantity_perc != None):
                    _targetCommittedBalance = round(_allocatedBalance*_targetMinQuantity_perc, _precisions['quote'])
                    _exitRequiredBalance    = _committedBalance-_targetCommittedBalance
                    if (0 < _exitRequiredBalance): _quantity = round(math.ceil((_exitRequiredBalance/_position['entryPrice']*_tc['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                #[3]: Quantity Check & Order Creation Request
                if ((_quantity != None) and (0 < _quantity)):
                    #---Small quantity handling
                    _quantity_remaining = abs(_position['quantity'])
                    if ((_quantity < pow(10, -_precisions['quantity'])) or (_quantity_remaining <= _quantity)): _quantity = _quantity_remaining
                    #---Order creation request
                    if   (0 < _position['quantity']): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'PIP_EXIT', side = 'SELL', quantity = _quantity, timestamp = _analysisTargetTS, tradePrice = _closePrice)
                    elif (_position['quantity'] < 0): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'PIP_EXIT', side = 'BUY',  quantity = _quantity, timestamp = _analysisTargetTS, tradePrice = _closePrice)
            #---[3]: PIP PSL
            elif (_tradeHandler[0] == 'PIP_PSL'):
                #[1]: Allocated / Committed Balance
                if (_position['allocatedBalance'] == None): _allocatedBalance = 0
                else:                                       _allocatedBalance = _position['allocatedBalance']
                if (_position['entryPrice'] == None): _committedBalance = 0
                else:                                 _committedBalance = abs(_position['quantity'])*_position['entryPrice']/_tc['leverage']
                #[2]: Quantity Determination
                _quantity_minUnit = pow(10, -_precisions['quantity'])
                _quantity         = None
                #---From all the satisfied trade scenarios, find the minimum targeting quantity
                _targetMinQuantity_perc = None
                for _sd in _tc['method_psl']:
                    if (((0 < _position['quantity']) and (_sd[0] <= -(_closePrice/_position['entryPrice']-1))) or ((_position['quantity'] < 0) and (_sd[0] <=  (_closePrice/_position['entryPrice']-1)))):
                        if ((_targetMinQuantity_perc == None) or (_sd[1] < _targetMinQuantity_perc)): _targetMinQuantity_perc = _sd[1]
                #---Determine the quantity to exit
                if (_targetMinQuantity_perc != None):
                    _targetCommittedBalance = round(_allocatedBalance*_targetMinQuantity_perc, _precisions['quote'])
                    _exitRequiredBalance    = _committedBalance-_targetCommittedBalance
                    if (0 < _exitRequiredBalance): _quantity = round(math.ceil((_exitRequiredBalance/_position['entryPrice']*_tc['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                #[3]: Quantity Check & Order Creation Request
                if ((_quantity != None) and (0 < _quantity)):
                    #---Small quantity handling
                    _quantity_remaining = abs(_position['quantity'])
                    if ((_quantity < pow(10, -_precisions['quantity'])) or (_quantity_remaining <= _quantity)): _quantity = _quantity_remaining
                    #---Order creation request
                    if   (0 < _position['quantity']): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'PIP_PSL', side = 'SELL', quantity = _quantity, timestamp = _analysisTargetTS, tradePrice = _closePrice)
                    elif (_position['quantity'] < 0): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'PIP_PSL', side = 'BUY',  quantity = _quantity, timestamp = _analysisTargetTS, tradePrice = _closePrice)
            #---[4]: PIP TP
            elif (_tradeHandler[0] == 'TP'):
                _quantity_abs = abs(round(_position['quantity']*_position['takeProfitPrice'][1], _precisions['quantity']))
                if   (0 < _position['quantity']): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'TP', side = 'SELL', quantity = _quantity_abs, timestamp = _analysisTargetTS, tradePrice = _position['takeProfitPrice'][0])
                elif (_position['quantity'] < 0): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'TP', side = 'BUY',  quantity = _quantity_abs, timestamp = _analysisTargetTS, tradePrice = _position['takeProfitPrice'][0])
                _position['tm_partialTakeProfitExecuted'] = True
            #---[5]: PIP SL
            elif (_tradeHandler[0] == 'SL'):
                if   (0 < _position['quantity']): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'SL', side = 'SELL', quantity =  _position['quantity'], timestamp = _analysisTargetTS, tradePrice = _position['stopLossPrice'])
                elif (_position['quantity'] < 0): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'SL', side = 'BUY',  quantity = -_position['quantity'], timestamp = _analysisTargetTS, tradePrice = _position['stopLossPrice'])
            #---[6]: ESCAPE
            elif (_tradeHandler[0] == 'ESCAPE'):
                if   (0 < _position['quantity']): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'ESCAPE', side = 'SELL', quantity =  _position['quantity'], timestamp = _analysisTargetTS, tradePrice = _closePrice)
                elif (_position['quantity'] < 0): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'ESCAPE', side = 'BUY',  quantity = -_position['quantity'], timestamp = _analysisTargetTS, tradePrice = _closePrice)
            #---[7]: FSL (Full-Stop_Loss)
            elif (_tradeHandler[0] == 'FSL'):
                if   (0 < _position['quantity']): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'FSL', side = 'SELL', quantity =  _position['quantity'], timestamp = _analysisTargetTS, tradePrice = _price_FSL)
                elif (_position['quantity'] < 0): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'FSL', side = 'BUY',  quantity = -_position['quantity'], timestamp = _analysisTargetTS, tradePrice = _price_FSL)
            #---[8]: RAF (Reach-And-Fall)
            elif (_tradeHandler[0] == 'RAF'):
                if   (0 < _position['quantity']): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'RAF', side = 'SELL', quantity =  _position['quantity'], timestamp = _analysisTargetTS, tradePrice = _price_RAF)
                elif (_position['quantity'] < 0): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'RAF', side = 'BUY',  quantity = -_position['quantity'], timestamp = _analysisTargetTS, tradePrice = _price_RAF)
            #---[9]: WR (Weight Reduce)
            elif (_tradeHandler[0] == 'WR'):
                if   (0 < _position['quantity']): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'WR', side = 'SELL', quantity = _quantity_WR, timestamp = _analysisTargetTS, tradePrice = _price_WR)
                elif (_position['quantity'] < 0): self.__processSimulatedTrade(simulationCode = _simulationCode, positionSymbol = _pSymbol, logicSource = 'WR', side = 'BUY',  quantity = _quantity_WR, timestamp = _analysisTargetTS, tradePrice = _price_WR)
            #---[10]: Liquidation
            elif (_tradeHandler[0] == 'LIQUIDATION'):
                self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'LIQUIDATION', side = _thParams[0], quantity = _thParams[1], timestamp = timestamp, tradePrice = _thParams[2])
    def __handlePIPResult_RQPM(self, simulationCode, pSymbol, pipResult, timestamp, kline):
        #Instances Call
        _simulation = self.__simulations[simulationCode]
        _position_def = _simulation['positions'][pSymbol]
        _position     = _simulation['_positions'][pSymbol]
        _asset        = _simulation['_assets'][_position_def['quoteAsset']]
        _tc           = _simulation['tradeConfigurations'][_simulation['positions'][pSymbol]['tradeConfigurationCode']]
        _precisions   = _position_def['precisions']
        #PIP Action Signal
        if (pipResult['ACTIONSIGNAL'] is None):
            _pas_allowEntry = None
            _pas_side       = None
        else:
            _pas_allowEntry = pipResult['ACTIONSIGNAL']['allowEntry']
            _pas_side       = pipResult['ACTIONSIGNAL']['side']
        #PIP Action Signal Interpretation & Trade Handlers Determination
        _tradeHandler_checkList = {'RQP_ENTRY':    None,
                                   'RQP_CLEAR':    None,
                                   'RQP_FSLIMMED': None,
                                   'RQP_FSLCLOSE': None,
                                   'LIQUIDATION':  None,
                                   'RQP_EXIT':     None}
        _tradeHandler_checkList_priceBased = list()
        #---CheckList 1: RQP ENTRY & RQP CLEAR
        if ((pipResult['ACTIONSIGNAL'] is not None) and (_pas_allowEntry == True)):
            if (_pas_side == 'BUY'):
                if (_position['quantity'] <= 0):
                    if ((_tc['direction'] == 'LONG') or (_tc['direction'] == 'BOTH')): _tradeHandler_checkList['RQP_ENTRY'] = ('BUY', kline[KLINDEX_CLOSEPRICE])
                    if (_position['quantity'] < 0):                                    _tradeHandler_checkList['RQP_CLEAR'] = ('BUY', kline[KLINDEX_CLOSEPRICE])
            elif (_pas_side == 'SELL'):
                if (0 <= _position['quantity']):
                    if ((_tc['direction'] == 'SHORT') or (_tc['direction'] == 'BOTH')): _tradeHandler_checkList['RQP_ENTRY'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
                    if (0 < _position['quantity']):                                     _tradeHandler_checkList['RQP_CLEAR'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
        #---CheckList 2: FSL Immediate
        if (True):
            if (_position['quantity'] != 0):
                if (_tc['rqpm_fullStopLossImmediate'] is not None):
                    if (_position['quantity'] < 0):
                        _price_FSL = round(_position['entryPrice']*(1+_tc['rqpm_fullStopLossImmediate']), _precisions['price'])
                        if (_price_FSL <= kline[KLINDEX_HIGHPRICE]): 
                            _tradeHandler_checkList['RQP_FSLIMMED'] = ('BUY', _price_FSL)
                            _tradeHandler_checkList_priceBased.append(('RQP_FSLIMMED', _price_FSL-kline[KLINDEX_OPENPRICE]))
                    elif (0 < _position['quantity']):
                        _price_FSL = round(_position['entryPrice']*(1-_tc['rqpm_fullStopLossImmediate']), _precisions['price'])
                        if (kline[KLINDEX_LOWPRICE] <= _price_FSL): 
                            _tradeHandler_checkList['RQP_FSLIMMED'] = ('SELL', _price_FSL)
                            _tradeHandler_checkList_priceBased.append(('RQP_FSLIMMED', kline[KLINDEX_OPENPRICE]-_price_FSL))
        #---CheckList 3: FSL Close
        if (True):
            if (_position['quantity'] != 0):
                if (_tc['rqpm_fullStopLossClose'] is not None):
                    if (_position['quantity'] < 0):
                        _price_FSL = round(_position['entryPrice']*(1+_tc['rqpm_fullStopLossClose']), _precisions['price'])
                        if (_price_FSL <= kline[KLINDEX_HIGHPRICE]): _tradeHandler_checkList['RQP_FSLCLOSE'] = ('BUY', kline[KLINDEX_CLOSEPRICE])
                    elif (0 < _position['quantity']):
                        _price_FSL = round(_position['entryPrice']*(1-_tc['rqpm_fullStopLossClose']), _precisions['price'])
                        if (kline[KLINDEX_LOWPRICE] <= _price_FSL): _tradeHandler_checkList['RQP_FSLCLOSE'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
        #---CheckList 4: LIQUIDATION
        if (True):
            if (_position['quantity'] != 0):
                if (_position['liquidationPrice'] is not None):
                    if (_position['quantity'] < 0):
                        if (_position['liquidationPrice'] <= kline[KLINDEX_HIGHPRICE]): 
                            _tradeHandler_checkList['LIQUIDATION'] = ('LIQUIDATION', _position['liquidationPrice'])
                            _tradeHandler_checkList_priceBased.append(('LIQUIDATION', _position['liquidationPrice']-kline[KLINDEX_OPENPRICE]))
                    elif (0 < _position['quantity']):
                        if (kline[KLINDEX_LOWPRICE] <= _position['liquidationPrice']): 
                            _tradeHandler_checkList['LIQUIDATION'] = ('LIQUIDATION', _position['liquidationPrice'])
                            _tradeHandler_checkList_priceBased.append(('LIQUIDATION', kline[KLINDEX_OPENPRICE]-_position['liquidationPrice']))
        #---CheckList 5: RQP_EXIT
        if ((pipResult['ACTIONSIGNAL'] is not None) and (_pas_allowEntry == False)):
            if (_position['quantity'] != 0):
                #Exit Conditions Check
                #---Impulse
                if (_tc['rqpm_exitOnImpulse'] is None): _rqpExitTest_impulse = True
                else:
                    if   (_pas_side == 'BUY'):  _rqpExitTest_impulse = (pipResult['CLASSICALSIGNAL_CYCLEIMPULSE'] <= -_tc['rqpm_exitOnImpulse'])
                    elif (_pas_side == 'SELL'): _rqpExitTest_impulse = (_tc['rqpm_exitOnImpulse'] <= pipResult['CLASSICALSIGNAL_CYCLEIMPULSE'])
                #---Aligned
                if (_tc['rqpm_exitOnAligned'] is None): _rqpExitTest_aligned = True
                else:
                    _pdp_this = kline[KLINDEX_CLOSEPRICE]/kline[KLINDEX_OPENPRICE]-1
                    if   (_pas_side == 'BUY'):  _rqpExitTest_aligned = (_pdp_this <= -_tc['rqpm_exitOnAligned'])
                    elif (_pas_side == 'SELL'): _rqpExitTest_aligned = (_tc['rqpm_exitOnAligned'] <= _pdp_this)
                #---Profitable
                if (_tc['rqpm_exitOnProfitable'] is None): _rqpExitTest_profitable = True
                else:
                    _pdp = kline[KLINDEX_CLOSEPRICE]/_position['entryPrice']-1
                    if   (_pas_side == 'BUY'):  _rqpExitTest_profitable = (_pdp <= -_tc['rqpm_exitOnProfitable'])
                    elif (_pas_side == 'SELL'): _rqpExitTest_profitable = (_tc['rqpm_exitOnProfitable'] <= _pdp)
                #Finally
                if ((_rqpExitTest_impulse == True) and (_rqpExitTest_aligned == True) and (_rqpExitTest_profitable == True)):
                    if   (_pas_side == 'BUY'):  _tradeHandler_checkList['RQP_EXIT'] = ('BUY',  kline[KLINDEX_CLOSEPRICE])
                    elif (_pas_side == 'SELL'): _tradeHandler_checkList['RQP_EXIT'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
        #---Trade Handlers Determination
        _tradeHandlers = list()
        if (True):
            _tradeHandler_checkList_priceBased.sort(key = lambda x: x[1])
            if (len(_tradeHandler_checkList_priceBased) == 0): _tradeHandler_priceBasedClearing_firstTriggerred = None
            else:                                              _tradeHandler_priceBasedClearing_firstTriggerred = _tradeHandler_checkList_priceBased[0][0]
            if (_tradeHandler_checkList['RQP_ENTRY'] is not None):
                if   (_tradeHandler_priceBasedClearing_firstTriggerred is not None): _tradeHandlers = [_tradeHandler_priceBasedClearing_firstTriggerred, 'RQP_ENTRY']
                elif (_tradeHandler_checkList['RQP_FSLCLOSE']          is not None): _tradeHandlers = ['RQP_FSLCLOSE',                                   'RQP_ENTRY']
                elif (_tradeHandler_checkList['RQP_CLEAR']             is not None): _tradeHandlers = ['RQP_CLEAR',                                      'RQP_ENTRY']
                else:                                                                _tradeHandlers = ['RQP_ENTRY',]
            else:
                if   (_tradeHandler_priceBasedClearing_firstTriggerred is not None): _tradeHandlers = [_tradeHandler_priceBasedClearing_firstTriggerred,]
                elif (_tradeHandler_checkList['RQP_FSLCLOSE']          is not None): _tradeHandlers = ['RQP_FSLCLOSE',]
                elif (_tradeHandler_checkList['RQP_CLEAR']             is not None): _tradeHandlers = ['RQP_CLEAR',]
                elif (_tradeHandler_checkList['RQP_EXIT']              is not None): _tradeHandlers = ['RQP_EXIT',]
        #Trade Handlers Execution
        for _tradeHandler in _tradeHandlers:
            _thParams = _tradeHandler_checkList[_tradeHandler]
            if   (_tradeHandler == 'RQP_ENTRY'):
                #Allocated / Committed Balance
                if (_position['allocatedBalance'] is None): _allocatedBalance = 0
                else:                                       _allocatedBalance = _position['allocatedBalance']
                if (_position['entryPrice'] is None): _committedBalance = 0
                else:                                 _committedBalance = abs(_position['quantity'])*_position['entryPrice']/_tc['leverage']
                #Quantity Determination
                _quantity_minUnit = pow(10, -_precisions['quantity'])
                _quantity = round(int(((_allocatedBalance-_committedBalance)/_thParams[1]*_tc['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                #Side Confirmation
                _side_confirmed = False
                if   ((_position['quantity'] <= 0) and (_thParams[0] == 'SELL')): _side_confirmed = True
                elif ((0 <= _position['quantity']) and (_thParams[0] == 'BUY')):  _side_confirmed = True
                if ((0 < _quantity) and (_side_confirmed == True)):
                    self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'RQP_ENTRY', side = _thParams[0], quantity = _quantity, timestamp = timestamp, tradePrice = _thParams[1])
                    _position['tradeControl']['rqpm_entryTimestamp']  = timestamp
                    _position['tradeControl']['rqpm_initialQuantity'] = _quantity
            elif (_tradeHandler == 'RQP_CLEAR'):
                #Quantity Determination
                if   (_position['quantity'] < 0):  _quantity = -_position['quantity']
                elif (0 < _position['quantity']):  _quantity =  _position['quantity']
                elif (_position['quantity'] == 0): _quantity = 0
                #Side Confirm
                _side_confirmed = False
                if   ((_position['quantity'] < 0) and (_thParams[0] == 'BUY')):  _side_confirmed = True
                elif ((0 < _position['quantity']) and (_thParams[0] == 'SELL')): _side_confirmed = True
                #Finally
                if ((0 < _quantity) and (_side_confirmed == True)): self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'RQP_CLEAR', side = _thParams[0], quantity = _quantity, timestamp = timestamp, tradePrice = _thParams[1])
            elif (_tradeHandler == 'RQP_FSLIMMED'):
                #Quantity Determination
                if   (_position['quantity'] < 0):  _quantity = -_position['quantity']
                elif (0 < _position['quantity']):  _quantity =  _position['quantity']
                elif (_position['quantity'] == 0): _quantity = 0
                #Side Confirm
                _side_confirmed = False
                if   ((_position['quantity'] < 0) and (_thParams[0] == 'BUY')):  _side_confirmed = True
                elif ((0 < _position['quantity']) and (_thParams[0] == 'SELL')): _side_confirmed = True
                #Finally
                if ((0 < _quantity) and (_side_confirmed == True)): self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'FSLIMMED', side = _thParams[0], quantity = _quantity, timestamp = timestamp, tradePrice = _thParams[1])
            elif (_tradeHandler == 'RQP_FSLCLOSE'):
                #Quantity Determination
                if   (_position['quantity'] < 0):  _quantity = -_position['quantity']
                elif (0 < _position['quantity']):  _quantity =  _position['quantity']
                elif (_position['quantity'] == 0): _quantity = 0
                #Side Confirm
                _side_confirmed = False
                if   ((_position['quantity'] < 0) and (_thParams[0] == 'BUY')):  _side_confirmed = True
                elif ((0 < _position['quantity']) and (_thParams[0] == 'SELL')): _side_confirmed = True
                #Finally
                if ((0 < _quantity) and (_side_confirmed == True)): self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'FSLCLOSE', side = _thParams[0], quantity = _quantity, timestamp = timestamp, tradePrice = _thParams[1])
            elif (_tradeHandler == 'LIQUIDATION'):
                #Quantity Determination
                if   (_position['quantity'] < 0):  _quantity = -_position['quantity']
                elif (0 < _position['quantity']):  _quantity =  _position['quantity']
                elif (_position['quantity'] == 0): _quantity = 0
                #Side Confirm
                _side_confirmed = False
                if   ((_position['quantity'] < 0) and (_thParams[0] == 'BUY')):  _side_confirmed = True
                elif ((0 < _position['quantity']) and (_thParams[0] == 'SELL')): _side_confirmed = True
                #Finally
                if ((0 < _quantity) and (_side_confirmed == True)): self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'LIQUIDATION', side = _thParams[0], quantity = _quantity, timestamp = timestamp, tradePrice = _thParams[1])
            elif (_tradeHandler == 'RQP_EXIT'):
                #RQP Value & Quantity Determination
                #---RQP Value
                if (_position['tradeControl']['rqpm_entryTimestamp'] is not None):
                    _rqpfp_contIndex = int((timestamp-_position['tradeControl']['rqpm_entryTimestamp'])/KLINTERVAL_S)
                    _rqpfp_pdp       = round(kline[KLINDEX_CLOSEPRICE]/_position['entryPrice']-1, 4)
                    _rqpfp_pdPerc_LS = round((kline[KLINDEX_CLOSEPRICE]-pipResult['SWINGS'][-1][1])/_ca_beginPrice, 4)

                    
                    if   (_position['quantity'] < 0):  _rqpmValue = atmEta_RQPMFunctions.RQPMFUNCTIONS[_tc['rqpm_functionType']](params      = _tc['rqpm_functionParams_SHORT'], 
                                                                                                                                 contIndex   = _rqpfp_contIndex, 
                                                                                                                                 pDPerc      = _rqpfp_pdp,
                                                                                                                                 pDPerc_LS   = None,
                                                                                                                                 sigStrength = None)
                    elif (0 < _position['quantity']):  _rqpmValue = atmEta_RQPMFunctions.RQPMFUNCTIONS[_tc['rqpm_functionType']](params = _tc['rqpm_functionParams_LONG'], 
                                                                                                                                 contIndex   = _rqpfp_contIndex, 
                                                                                                                                 pDPerc      = _rqpfp_pdp,
                                                                                                                                 pDPerc_LS   = None,
                                                                                                                                 sigStrength = None)
                    elif (_position['quantity'] == 0): _rqpmValue = 0
                else: _rqpmValue = 0
                #---Quantity
                if (_position['tradeControl']['rqpm_initialQuantity'] is not None):
                    _quantity_minUnit = pow(10, -_precisions['quantity'])
                    _quantity_target  = round(_position['tradeControl']['rqpm_initialQuantity']*_rqpmValue, _precisions['quantity'])
                    _quantity = round(abs(_position['quantity'])-_quantity_target, _precisions['quantity'])
                    if (0 < _quantity):
                        if (_quantity < _quantity_minUnit):          _quantity = round(_quantity_minUnit, _precisions['quantity'])
                        if (abs(_position['quantity']) < _quantity): _quantity = abs(_position['quantity'])
                    else: _quantity = 0
                else: _quantity = 0
                #Side Confirm
                _side_confirmed = False
                if   ((_position['quantity'] < 0) and (_thParams[0] == 'BUY')):  _side_confirmed = True
                elif ((0 < _position['quantity']) and (_thParams[0] == 'SELL')): _side_confirmed = True
                if ((0 < _quantity) and (_side_confirmed == True)): self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'RQP_EXIT', side = _thParams[0], quantity = _quantity, timestamp = timestamp, tradePrice = _thParams[1])

        """
        #PIP Cyclic Analysis
        _ca_cycle      = pipResult['CLASSICALSIGNAL_CYCLE']
        _ca_contIndex  = pipResult['CLASSICALSIGNAL_CYCLECONTINDEX']
        _ca_beginPrice = pipResult['CLASSICALSIGNAL_CYCLEBEGINPRICE']
        #RQP Value
        if ((_ca_cycle is not None) and (0 < len(pipResult['SWINGS']))):
            _rqpfp_pdPerc    = round((kline[KLINDEX_CLOSEPRICE]-_ca_beginPrice)            /_ca_beginPrice, 4)
            _rqpfp_pdPerc_LS = round((kline[KLINDEX_CLOSEPRICE]-pipResult['SWINGS'][-1][1])/_ca_beginPrice, 4)
            _rqpfp_sigStr    = pipResult['CLASSICALSIGNAL_FILTERED']
            if   (_ca_cycle == 'LOW'):  _rqpfp = _tc['rqpm_functionParams_SHORT']
            elif (_ca_cycle == 'HIGH'): _rqpfp = _tc['rqpm_functionParams_LONG']
            _rqpmValue = atmEta_RQPMFunctions.RQPMFUNCTIONS[_tc['rqpm_functionType']](params = _tc['rqpm_functionParams'], contIndex = _ca_contIndex, pDPerc = _rqpfp_pdPerc, pDPerc_LS = _rqpfp_pdPerc_LS, sigStrength = _rqpfp_sigStr)
        else: _rqpmValue = None
        """
            
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
                                        'nTrades_exit':        0,
                                        'nTrades_psl':         0,
                                        'nTrades_fsl':         0,
                                        'nTrades_raf':         0,
                                        'nTrades_wr':          0,
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
            _tradingFee     = round(quantity*tradePrice*_SIMULATION_MARKETTRADINGFEE, _precisions['quote'])
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
            #Update Trade Control
            _position['tradeControl'] = {#Trade Scenario
                                         'ts_maximumProfitPrice':        None,
                                         'ts_takeProfitPrice':           None,
                                         'ts_stopLossPrice':             None,
                                         'ts_partialTakeProfitExecuted': False,
                                         'ts_initialQuantity':           None,
                                         #RQPM
                                         'rqpm_entryTimestamp':  None,
                                         'rqpm_initialQuantity': None}
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
            #[3]: Update Trade Control
            if (_quantity_new == 0):
                _position['tradeControl'] = {#Trade Scenario
                                             'ts_maximumProfitPrice':        None,
                                             'ts_takeProfitPrice':           None,
                                             'ts_stopLossPrice':             None,
                                             'ts_partialTakeProfitExecuted': False,
                                             'ts_initialQuantity':           None,
                                             #RQPM
                                             'rqpm_entryTimestamp':  None,
                                             'rqpm_initialQuantity': None}
            elif (0 < _quantity_dirDelta): _position['maximumProfitPrice'] = _entryPrice_new
        #Update Account
        self.__updateAccount(simulationCode = simulationCode, timestamp = timestamp)
        #Save Trade Log
        if (True):
            _tradeLog = {'timestamp':      timestamp, 
                         'positionSymbol': positionSymbol,
                         'logicSource':    logicSource,
                         'side':           side,
                         'quantity':       quantity,
                         'price':          tradePrice,
                         'profit':         _profit,
                         'tradingFee':     _tradingFee,
                         'totalQuantity':  _quantity_new,
                         'entryPrice':     _entryPrice_new,
                         'walletBalance':  _asset['walletBalance'],
                         'tradeControl':   _position['tradeControl']}
            _simulation['_tradeLogs'].append(_tradeLog)
        #Update Daily Report
        if (True):
            _dailyReport = _simulation['_dailyReports'][_simulation['_currentFocusDay']][_position_def['quoteAsset']]
            _dailyReport['nTrades'] += 1
            if   (side == 'BUY'):                _dailyReport['nTrades_buy']         += 1
            elif (side == 'SELL'):               _dailyReport['nTrades_sell']        += 1
            if   (logicSource == 'PIP_ENTRY'):   _dailyReport['nTrades_entry']       += 1
            elif (logicSource == 'PIP_EXIT'):    _dailyReport['nTrades_exit']        += 1
            elif (logicSource == 'PIP_PSL'):     _dailyReport['nTrades_psl']         += 1
            elif (logicSource == 'FSL'):         _dailyReport['nTrades_fsl']         += 1
            elif (logicSource == 'RAF'):         _dailyReport['nTrades_raf']         += 1
            elif (logicSource == 'WR'):          _dailyReport['nTrades_wr']          += 1
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
        _nTrades_exit        = 0
        _nTrades_psl         = 0
        _nTrades_fsl         = 0
        _nTrades_raf         = 0
        _nTrades_wr          = 0
        _nTrades_liquidation = 0
        for _log in _tradeLog:
            _side        = _log['side']
            _logicSource = _log['logicSource']
            if   (_side == 'PIP_BUY'):  _nTrades_buy  += 1
            elif (_side == 'PIP_SELL'): _nTrades_sell += 1
            if   (_logicSource == 'PIP_ENTRY'):   _nTrades_entry       += 1
            elif (_logicSource == 'PIP_EXIT'):    _nTrades_exit        += 1
            elif (_logicSource == 'PIP_PSL'):     _nTrades_psl         += 1
            elif (_logicSource == 'FSL'):         _nTrades_fsl         += 1
            elif (_logicSource == 'RAF'):         _nTrades_raf         += 1
            elif (_logicSource == 'WR'):          _nTrades_wr          += 1
            elif (_logicSource == 'LIQUIDATION'): _nTrades_liquidation += 1
        simulationSummary = {'total': {'nTradeDays':          _nTradeDays,
                                       'nTrades_total':       _nTrades_total, 
                                       'nTrades_buy':         _nTrades_buy, 
                                       'nTrades_sell':        _nTrades_sell, 
                                       'nTrades_entry':       _nTrades_entry,
                                       'nTrades_exit':        _nTrades_exit,
                                       'nTrades_psl':         _nTrades_psl,
                                       'nTrades_fsl':         _nTrades_fsl,
                                       'nTrades_raf':         _nTrades_raf,
                                       'nTrades_wr':          _nTrades_wr,
                                       'nTrades_liquidation': _nTrades_liquidation}}
        #Asset Summary
        _tradeLog_byAssets = dict()
        for _assetName in _simulation['assets']: _tradeLog_byAssets[_assetName] = list()
        for _log in _tradeLog: _tradeLog_byAssets[_positions_def[_log['positionSymbol']]['quoteAsset']].append(_log)
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
            _nTrades_psl         = 0
            _nTrades_liquidation = 0
            _gains_total      = 0
            _losses_total     = 0
            _tradingFee_total = 0
            _initialWalletBalance = _simulation['assets'][_assetName]['initialWalletBalance']
            _walletBalance_min    = _initialWalletBalance
            _walletBalance_max    = _initialWalletBalance
            _walletBalance_final  = _initialWalletBalance
            for _log in _tradeLog_thisAsset:
                _logicSource = _log['logicSource']
                if   (_logicSource == 'PIP_BUY'):     _nTrades_buy         += 1
                elif (_logicSource == 'PIP_SELL'):    _nTrades_sell        += 1
                elif (_logicSource == 'PIP_PSL'):     _nTrades_psl         += 1
                elif (_logicSource == 'LIQUIDATION'): _nTrades_liquidation += 1
                _profit = _log['profit']
                if   (_profit < 0): _losses_total += abs(_profit)
                elif (0 < _profit): _gains_total  += _profit
                _tradingFee_total += _log['tradingFee']
                _gains_total      = round(_gains_total, _SIMULATION_ASSETPRECISIONS[_assetName])
                _losses_total     = round(_losses_total, _SIMULATION_ASSETPRECISIONS[_assetName])
                _tradingFee_total = round(_tradingFee_total, _SIMULATION_ASSETPRECISIONS[_assetName])
                _walletBalance = _log['walletBalance']
                if (_walletBalance < _walletBalance_min): _walletBalance_min = _walletBalance
                if (_walletBalance_max < _walletBalance): _walletBalance_max = _walletBalance
            if (0 < _nTrades_total): _walletBalance_final = _tradeLog_thisAsset[-1]['walletBalance']
            #---Wallet Balance Trend Analysis
            if (0 < _nTrades_total):
                _firstTradeLogTS = _tradeLog_thisAsset[0]['timestamp']
                _bfl_x_raw = [_log['timestamp']-_firstTradeLogTS for _log in _tradeLog_thisAsset]
                _bfl_y_raw = [_log['walletBalance']              for _log in _tradeLog_thisAsset]
                try:
                    _bfl_linear_a, _bfl_linear_b = numpy.polyfit(x = _bfl_x_raw, y = numpy.log(_bfl_y_raw), deg = 1, w = numpy.sqrt(_bfl_y_raw))
                    _a_exp = numpy.exp(_bfl_linear_b)
                    _b_exp = _bfl_linear_a
                    _bfl_x = numpy.array(_bfl_x_raw)
                    _bfl_y = _a_exp*numpy.exp(_b_exp*_bfl_x)
                    _bfl_gr = (numpy.exp(_b_exp)-1)*86400
                    _bfl_channelDeltas = numpy.abs(_bfl_y_raw-_bfl_y)/_bfl_y
                    _bfl_ctAverage = numpy.average(_bfl_channelDeltas)
                    _bfl_ctMaximum = numpy.max(_bfl_channelDeltas)
                except:
                    _a_exp = None
                    _b_exp = None
                    _bfl_gr        = None
                    _bfl_ctAverage = None
                    _bfl_ctMaximum = None
            else:
                _a_exp = None
                _b_exp = None
                _bfl_gr        = None
                _bfl_ctAverage = None
                _bfl_ctMaximum = None
            simulationSummary[_assetName] = {'nTradeDays': _nTradeDays, 'nTrades_total': _nTrades_total, 'nTrades_buy': _nTrades_buy, 'nTrades_sell': _nTrades_sell, 'nTrades_psl': _nTrades_psl, 'nTrades_liquidation': _nTrades_liquidation,
                                             'gains': _gains_total, 'losses': _losses_total, 'tradingFee': _tradingFee_total,
                                             'walletBalance_initial': _simulation['assets'][_assetName]['initialWalletBalance'], 'walletBalance_min': _walletBalance_min, 'walletBalance_max': _walletBalance_max, 'walletBalance_final': _walletBalance_final, 
                                             'walletBalance_bfl_a': _a_exp, 'walletBalance_bfl_b': _b_exp, 'walletBalance_bfl_gr': _bfl_gr, 'walletBalance_bfl_ctAverage': _bfl_ctAverage, 'walletBalance_bfl_ctMaximum': _bfl_ctMaximum}
        return simulationSummary
    def __generateSimulationDetailedReport(self, simulationCode):
        _simulation = self.__simulations[simulationCode]

        detailedReport = dict()
        return detailedReport
    def __saveSimulationCycleData(self, simulationCode):
        _simulation = self.__simulations[simulationCode]
        if (_simulation['_cycleData'][0] == True):
            #[1]: Cycle Data Main Folder
            _path_cycleDataMain = os.path.join(self.path_project, 'data', 'cycleData')
            if (os.path.exists(_path_cycleDataMain) == False): os.makedirs(_path_cycleDataMain)
            #[2]: Cycle Data Simulation Folder
            _index_cycleDataSimulation = None
            _path_cycleDataSimulation  = os.path.join(_path_cycleDataMain, "{:s}_cd".format(simulationCode))
            if (os.path.exists(_path_cycleDataSimulation) == False): os.makedirs(_path_cycleDataSimulation)
            else:
                _index_cycleDataSimulation = 0
                while (True):
                    _path_cycleDataSimulation = os.path.join(self.path_project, 'data', 'cycleData', "{:s}_cd_{:d}".format(simulationCode, _index_cycleDataSimulation))
                    if (os.path.exists(_path_cycleDataSimulation) == False): os.makedirs(_path_cycleDataSimulation); break
                    else:                                                    _index_cycleDataSimulation += 1
            #[3]: Position-wise Cycle Data Save
            _positions = _simulation['_positions']
            for _pSymbol in _positions:
                #File Name
                if (_index_cycleDataSimulation == None): _baseName = "{:s}_{:s}".format(simulationCode, _pSymbol)
                else:                                    _baseName = "{:s}_{:d}_{:s}".format(simulationCode, _index_cycleDataSimulation, _pSymbol)
                _path_cycleDataPosition_cd   = os.path.join(_path_cycleDataSimulation, "{:s}_cd.json".format(_baseName))
                _path_cycleDataPosition_plot = os.path.join(_path_cycleDataSimulation, "{:s}_plot.png".format(_baseName))
                #Data Save
                _cRecs = _positions[_pSymbol]['CycleData']['CycleRecords']
                _file = open(_path_cycleDataPosition_cd, 'w')
                _file.write(json.dumps(_cRecs))
                _file.close()

                #Plot Image
                _maxCycleLen = max([len(_cRec['history']) for _cRec in _cRecs])
                _fig, _axs = matplotlib.pyplot.subplots(3, constrained_layout=True)
                _axs[0].set_title("SHORT", fontsize=8)
                _axs[1].set_title("LONG",  fontsize=8)
                _axs[2].set_title("ALL",        fontsize=8)
                for _ax in _axs:
                    _ax.grid(True)
                    _ax.set_xlim(-int(_maxCycleLen)*0.05, int(_maxCycleLen)*1.05)
                    _ax.set_xlabel("N Candles",       fontsize=6)
                    _ax.set_ylabel("Price Delta [%]", fontsize=6)
                    _ax.tick_params(axis='both', labelsize=6)
                matplotlib.pyplot.suptitle("Cycle Data - '{:s}'".format(_baseName), fontsize=10)
                for _cRec in _cRecs:
                    _cRec_type    = _cRec['type']
                    _cRec_history = _cRec['history']
                    _pPercs = [_data[0] for _data in _cRec_history]
                    _x = list(range(0, len(_cRec_history)))
                    _y = numpy.array(_pPercs)*100
                    if   (_cRec_type == 'SHORT'): _axs[0].plot(_x, _y, color=(1.0, 0.0, 0.0, 0.2), linestyle='-', linewidth=1); _axs[2].plot(_x, _y, color=(1.0, 0.0, 0.0, 0.2), linestyle='-', linewidth=1)
                    elif (_cRec_type == 'LONG'):  _axs[1].plot(_x, _y, color=(0.0, 1.0, 0.0, 0.2), linestyle='-', linewidth=1); _axs[2].plot(_x, _y, color=(0.0, 1.0, 0.0, 0.2), linestyle='-', linewidth=1)
                matplotlib.pyplot.savefig(_path_cycleDataPosition_plot, dpi=150, bbox_inches='tight')
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
    def __far_addSimulation(self, requester, simulationCode, simulationRange, cycleData, assets, positions, currencyAnalysisConfigurations, tradeConfigurations, creationTime):
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
                                                 'tradeControl': {#Trade Scenario
                                                                  'ts_maximumProfitPrice':        None,
                                                                  'ts_takeProfitPrice':           None,
                                                                  'ts_stopLossPrice':             None,
                                                                  'ts_partialTakeProfitExecuted': False,
                                                                  'ts_initialQuantity':           None,
                                                                  #RQPM
                                                                  'rqpm_entryTimestamp':  None,
                                                                  'rqpm_initialQuantity': None},
                                                 #External Analysis
                                                 'CycleData': {'TrackingCycles': list(),
                                                               'CycleRecords':   list()}
                                                 }

            #[4]: Create a simulation instance
            _simulation = {'simulationRange':                simulationRange,
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
                           '_simulationSummary':  None,
                           '_cycleData':          cycleData}
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
                    self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'onSimulationCompletion', functionParams = {'simulationCode': fr_simulationCode, 'simulationSummary': _simulation['_simulationSummary'], 'detailedReport': _simulation['_detailedReport']}, farrHandler = None)
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