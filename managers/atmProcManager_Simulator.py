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
import termcolor
import gc
import traceback
import random

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

_SIMULATION_BASEASSETALLOCATABLERATIO = 0.95

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

PERIODICREPORT_INTERVALID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1h

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
        #[1]: Activation Check
        if not self.__activation: return

        #[2]: Currently Handling Simulation Check
        if self.__simulations_currentlyHandling is None:
            if self.__simulations_handlingQueue: self.__startSimulation(self.__simulations_handlingQueue.pop(0))

        #[3]: Simulation Handling
        if self.__simulations_currentlyHandling is None: return
        #---[3-1]: Simulation
        simCode = self.__simulations_currentlyHandling
        sim     = self.__simulations[simCode]
        #---[3-2]: Status Check
        if sim['_status'] != 'PROCESSING': return
        #---[3-3]: Process Status
        #------[3-3-1]: Fetching Status
        if sim['_procStatus'] == 'FETCHING':
            if sim['_klines_fetchRequestIDs']: return
            sim['_procStatus']         = 'PROCESSING'
            sim['_nextAnalysisTarget'] = sim['_currentFocusDay']
        #------[3-3-2]: Processing Status
        elif (sim['_procStatus'] == 'PROCESSING'):
            t_begin_ns     = time.perf_counter_ns()
            t_elapsed_ns   = 0
            analysisResult = _SIMULATION_PROCESSING_ANALYSISRESULT_ANALYZENEXT
            while (analysisResult == _SIMULATION_PROCESSING_ANALYSISRESULT_ANALYZENEXT) and (t_elapsed_ns < _SIMULATION_PROCESSTIMEOUT_NS):
                analysisResult = self.__performSimulationOnTarget()
                t_elapsed_ns   = time.perf_counter_ns()-t_begin_ns
            #[3-3-2-1]: There exists more targets to process within the current focus day
            if analysisResult == _SIMULATION_PROCESSING_ANALYSISRESULT_ANALYZENEXT:
                #[3-3-2-1-1]: Compute simulation completion and announce
                sim['_completion'] = round(((sim['_nextAnalysisTarget']-1)-sim['simulationRange'][0]+1)/(sim['simulationRange'][1]-sim['simulationRange'][0]+1), 5)
                self.ipcA.sendFAR(targetProcess  = 'SIMULATIONMANAGER', 
                                  functionID     = 'onSimulationUpdate', 
                                  functionParams = {'simulationCode': simCode, 
                                                    'updateType':     'COMPLETION', 
                                                    'updatedValue':   sim['_completion']}, 
                                  farrHandler    = None)
            #[3-3-2-2]: Next focus day needs to be fetched
            elif analysisResult == _SIMULATION_PROCESSING_ANALYSISRESULT_FETCHNEXT:
                #[3-3-2-2-1]: Compute simulation completion and announce
                sim['_completion'] = round(((sim['_nextAnalysisTarget']-1)-sim['simulationRange'][0]+1)/(sim['simulationRange'][1]-sim['simulationRange'][0]+1), 5)
                self.ipcA.sendFAR(targetProcess  = 'SIMULATIONMANAGER', 
                                  functionID     = 'onSimulationUpdate', 
                                  functionParams = {'simulationCode': simCode, 
                                                    'updateType':     'COMPLETION', 
                                                    'updatedValue':   sim['_completion']}, 
                                  farrHandler    = None)
                #[3-3-2-2-2]: Update the procStatus and current focus day and request fetch
                sim['_procStatus']         = 'FETCHING'
                sim['_currentFocusDay']    += 86400
                sim['_nextAnalysisTarget'] = None
                self.__sendKlineFetchRequestForTheCurrentFocusDay(simulationCode = simCode)
            #[3-3-2-3]: Simulation has completed
            elif analysisResult == _SIMULATION_PROCESSING_ANALYSISRESULT_COMPLETE:
                #[3-3-2-3-1]: Update process status and save simulation summary & export analysis (if needed)
                sim['_procStatus'] = 'SAVING'
                sim['_simulationSummary'] = self.__generateSimulationSummary(simulationCode = simCode)
                self.__exportAnalysis(simulationCode = simCode)
                #[3-3-2-3-2]: Send simulation data save request to DATAMANAGER
                self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', 
                                  functionID = 'saveSimulationData',
                                  functionParams = {'simulationCode':                 simCode, 
                                                    'simulationRange':                sim['simulationRange'],
                                                    'currencyAnalysisConfigurations': sim['currencyAnalysisConfigurations'],
                                                    'tradeConfigurations':            sim['tradeConfigurations'],
                                                    'analysisExport':                 sim['analysisExport'],
                                                    'assets':                         sim['assets'],
                                                    'positions':                      sim['positions'],
                                                    'creationTime':                   sim['creationTime'],
                                                    'tradeLogs':                      sim['_tradeLogs'],
                                                    'periodicReports':                sim['_periodicReports'],
                                                    'simulationSummary':              sim['_simulationSummary']},
                                  farrHandler = self.__farr_onSimulationDataSaveRequestResponse)
            #[3-3-2-4]: An error has occurred
            elif analysisResult == _SIMULATION_PROCESSING_ANALYSISRESULT_ERROR: 
                self.__raiseSimulationError(simulationCode = simCode, errorCause = 'INPROCESSERROR')
    def __startSimulation(self, simulationCode):
        #[1]: Simulation
        self.__simulations_currentlyHandling = simulationCode
        simulation = self.__simulations[simulationCode]

        #[2]: Simulation status update
        simulation['_status']     = 'PROCESSING'
        simulation['_completion'] = 0
        self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'onSimulationUpdate', functionParams = {'simulationCode': simulationCode, 'updateType': 'STATUS',     'updatedValue': simulation['_status']},     farrHandler = None)
        self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'onSimulationUpdate', functionParams = {'simulationCode': simulationCode, 'updateType': 'COMPLETION', 'updatedValue': simulation['_completion']}, farrHandler = None)
        
        #[3]: Neural Networks Connections Data Request
        nn_codes = set()
        for cacCode in simulation['currencyAnalysisConfigurations']: 
            cac = simulation['currencyAnalysisConfigurations'][cacCode]
            if not cac['NNA_Master']: continue
            for lineIndex in range (atmEta_Constants.NLINES_NNA):
                nn_lineActive = cac[f'NNA_{lineIndex}_LineActive']
                nn_code       = cac[f'NNA_{lineIndex}_NeuralNetworkCode']
                if not nn_lineActive: continue
                if nn_code is None:   continue
                nn_codes.add(nn_code)
        if nn_codes:
            simulation['_procStatus'] = 'WAITINGNNCONNECTIONSDATA'
            for nn_code in nn_codes:
                rID = self.ipcA.sendFAR(targetProcess  = "NEURALNETWORKMANAGER",
                                        functionID     = 'getNeuralNetworkConnections',
                                        functionParams = {'neuralNetworkCode': nn_code},
                                        farrHandler    = self.__farr_onNeuralNetworkConnectionsDataRequestResponse)
                simulation['_neuralNetworks_connectionsDataRequestIDs'].add(rID)
            return

        #[4]: Kline Fetch Request
        simulation['_procStatus'] = 'FETCHING'
        self.__sendKlineFetchRequestForTheCurrentFocusDay(simulationCode = simulationCode)
    def __sendKlineFetchRequestForTheCurrentFocusDay(self, simulationCode):
        _simulation = self.__simulations[simulationCode]
        _focusDayTimeRange = (_simulation['_currentFocusDay'], _simulation['_currentFocusDay']+86400-1)
        for _pSymbol in _simulation['_positions']:
            _dispatchID = self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'fetchKlines', functionParams = {'symbol': _pSymbol, 'fetchRange': _focusDayTimeRange}, farrHandler = self.__farr_onKlineFetchResponse)
            _simulation['_klines_fetchRequestIDs'][_dispatchID] = _pSymbol
    def __performSimulationOnTarget(self):
        #[1]: Instances
        simulationCode = self.__simulations_currentlyHandling
        simulation     = self.__simulations[simulationCode]
        positions_def  = simulation['positions']
        positions      = simulation['_positions']
        assets_def     = simulation['assets']
        assets         = simulation['_assets']
        pReports       = simulation['_periodicReports']
        analyzers      = simulation['_analyzers']
        atTS = simulation['_nextAnalysisTarget']
        func_gnitt   = atmEta_Auxillaries.getNextIntervalTickTimestamp
        func_gtsl_br = atmEta_Auxillaries.getTimestampList_byRange

        #[2]: Update Account
        self.__updateAccount(simulationCode = simulationCode, timestamp = atTS)

        #[3]: Generate Analysis and Handle Generated Analysis Results
        for pSymbol in simulation['_positions']:
            #[3-1]: Instances
            position_def = positions_def[pSymbol]
            position     = positions[pSymbol]
            asset        = assets[position_def['quoteAsset']]
            cacCode      = position_def['currencyAnalysisConfigurationCode']
            analyzer     = analyzers[cacCode]
            klines                   = simulation['_klines'][pSymbol]
            klines_dataRange         = simulation['_klines_dataRange'][pSymbol]
            klines_lastRemovedOpenTS = simulation['_klines_lastRemovedOpenTS'][pSymbol]

            #[3-2]: Kline Check
            if atTS not in klines['raw']: continue
            kline = klines['raw'][atTS] #Kline ([0]: openTS, [1]: closeTS, [2]: openPrice, [3]: highPrice, [4]: lowPrice, [5]: closePrice, [6]: nTrades, [7]: baseAssetVolume, [8]: quoteAssetVolume, [9]: baseAssetVolume_takerBuy, [10]: quoteAssetVolume_takerBuy)
            
            #[3-3]: Analysis Generation
            nKlinesToKeep_max = 0
            for aType, aCode in analyzer['analysisToProcess_sorted']:
                #[3-3-1]: Analysis Generation
                nAnalysisToKeep, nKlinesToKeep = atmEta_Analyzers.analysisGenerator(analysisType   = aType, 
                                                                                    klineAccess    = klines, 
                                                                                    intervalID     = KLINTERVAL,
                                                                                    mrktRegTS      = None,
                                                                                    precisions     = position_def['precisions'], 
                                                                                    timestamp      = atTS,
                                                                                    neuralNetworks = simulation['_neuralNetworks'],
                                                                                    bidsAndAsks    = None, 
                                                                                    aggTrades      = None,
                                                                                    **analyzer['analysisParams'][aCode])
                nKlinesToKeep_max = max(nKlinesToKeep_max, nKlinesToKeep)
                #[3-3-2]: Memory Optimization (Analysis)
                ts_expired = func_gnitt(intervalID = KLINTERVAL, mrktReg = None, timestamp = atTS, nTicks = -(nAnalysisToKeep+1))
                if klines_dataRange[0] <= ts_expired:
                    if klines_lastRemovedOpenTS[aCode] is None: tsToRemove_beg = max(klines_dataRange[0], simulation['simulationRange'][0])
                    else:                                       tsToRemove_beg = func_gnitt(intervalID = KLINTERVAL, mrktReg = None, timestamp = klines_lastRemovedOpenTS[aCode], nTicks = 1)
                    tsToRemove = func_gtsl_br(intervalID = KLINTERVAL, timestamp_beg = tsToRemove_beg, timestamp_end = ts_expired, mrktReg = None, lastTickInclusive = True)
                    if tsToRemove:
                        for ts in tsToRemove: 
                            del klines[aCode][ts]
                        klines_lastRemovedOpenTS[aCode] = ts_expired
            #---[3-3-3]: Memory Optimization (Kline Raw, Kline Raw_Status)
            ts_expired = func_gnitt(intervalID = KLINTERVAL, mrktReg = None, timestamp = atTS, nTicks = -(nKlinesToKeep_max+1))
            if klines_dataRange[0] <= ts_expired:
                if klines_lastRemovedOpenTS['raw'] is None: tsToRemove_beg = max(klines_dataRange[0], simulation['simulationRange'][0])
                else:                                       tsToRemove_beg = func_gnitt(intervalID = KLINTERVAL, mrktReg = None, timestamp = klines_lastRemovedOpenTS['raw'], nTicks = 1)
                tsToRemove = func_gtsl_br(intervalID = KLINTERVAL, timestamp_beg = tsToRemove_beg, timestamp_end = ts_expired, mrktReg = None, lastTickInclusive = True)
                if tsToRemove:
                    for ts in tsToRemove: 
                        del klines['raw'][ts]
                    klines_lastRemovedOpenTS['raw'] = ts_expired

            #[3-4]: New Kline Handling
            self.__handleKline(simulationCode = simulationCode, pSymbol = pSymbol, timestamp = atTS, kline = kline)

            #[3-5]: Analysis Linearization
            aLinearized = atmEta_Analyzers.linearizeAnalysis(klineAccess = klines, analysisPairs = analyzer['analysisToProcess_sorted'], timestamp = atTS)

            #[3-6]: Analysis Handling
            self.__handleAnalysisResult(simulationCode = simulationCode, pSymbol = pSymbol, linearizedAnalysis = aLinearized, timestamp = atTS, kline = kline)

            #[3-7]: Analysis Export
            if simulation['analysisExport'][0]: position['AE']['data'].append(aLinearized)
                
        #[4]: Periodic Report Update
        for assetName in assets_def:
            #[4-1]: Instances & Daily Report Formatting (If needed)
            asset      = assets[assetName]
            pReport_TS = self.__formatPeriodicReport(simulationCode = simulationCode, timestamp = atTS)
            pReport    = pReports[pReport_TS][assetName]
            #[4-2]: Margin Balance
            marginBalance = asset['marginBalance']
            pReport['marginBalance_min'] = min(pReport['marginBalance_min'], marginBalance)
            pReport['marginBalance_max'] = max(pReport['marginBalance_max'], marginBalance)
            pReport['marginBalance_close'] = marginBalance
            #[4-3]: Commitment Rate
            if asset['commitmentRate'] is None: commitmentRate = 0
            else:                               commitmentRate = asset['commitmentRate']
            pReport['commitmentRate_min'] = min(pReport['commitmentRate_min'], commitmentRate)
            pReport['commitmentRate_max'] = max(pReport['commitmentRate_max'], commitmentRate)
            pReport['commitmentRate_close'] = commitmentRate
            #[4-4]: Risk Level
            if asset['riskLevel'] is None: riskLevel = 0
            else:                          riskLevel = asset['riskLevel']
            pReport['riskLevel_min'] = min(pReport['riskLevel_min'], riskLevel)
            pReport['riskLevel_max'] = max(pReport['riskLevel_max'], riskLevel)
            pReport['riskLevel_close'] = riskLevel

        #[5]: Post-process handling, update the next analysis target and return how the update occurred
        if atTS == simulation['_lastAnalysisTarget']: return _SIMULATION_PROCESSING_ANALYSISRESULT_COMPLETE
        else:
            simulation['_nextAnalysisTarget'] += KLINTERVAL_S
            if simulation['_currentFocusDay']+86400 <= simulation['_nextAnalysisTarget']: return _SIMULATION_PROCESSING_ANALYSISRESULT_FETCHNEXT
            else:                                                                         return _SIMULATION_PROCESSING_ANALYSISRESULT_ANALYZENEXT
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
        _thParams      = _tradeHandler_checkList[_tradeHandler]
        _quantity_prev = _position['quantity']
        #---[1]: FSLIMMED
        if (_tradeHandler == 'FSLIMMED'):
            self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'FSLIMMED', side = _thParams[0], quantity = abs(_position['quantity']), timestamp = timestamp, tradePrice = _thParams[1])
            if   (_quantity_prev < 0): _tcTracker['slExited'] = 'SHORT'
            elif (0 < _quantity_prev): _tcTracker['slExited'] = 'LONG'
        #---[2]: FSLCLOSE
        elif (_tradeHandler == 'FSLCLOSE'):
            self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'FSLCLOSE', side = _thParams[0], quantity = abs(_position['quantity']), timestamp = timestamp, tradePrice = _thParams[1])
            if   (_quantity_prev < 0): _tcTracker['slExited'] = 'SHORT'
            elif (0 < _quantity_prev): _tcTracker['slExited'] = 'LONG'
        #---[3]: LIQUIDATION
        elif (_tradeHandler == 'LIQUIDATION'): 
            self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'LIQUIDATION', side = None, quantity = abs(_position['quantity']), timestamp = timestamp, tradePrice = _thParams[1]) 
    def __handleAnalysisResult(self, simulationCode, pSymbol, linearizedAnalysis, timestamp, kline):
        #Instances Call
        simulation = self.__simulations[simulationCode]
        position_def = simulation['positions'][pSymbol]
        position     = simulation['_positions'][pSymbol]
        asset        = simulation['_assets'][position_def['quoteAsset']]
        tcConfig     = simulation['tradeConfigurations'][simulation['positions'][pSymbol]['tradeConfigurationCode']]
        tcTracker    = position['tradeControlTracker']
        precisions   = position_def['precisions']

        #RQP Value
        try:
            """
            rqpValue = atmEta_RQPMFunctions.RQPMFUNCTIONS_GET_RQPVAL[tcConfig['rqpm_functionType']](params             = tcConfig['rqpm_functionParams'], 
                                                                                                    kline              = kline, 
                                                                                                    linearizedAnalysis = linearizedAnalysis, 
                                                                                                    tcTracker_model    = tcTracker['rqpm_model'])
            """
            rqpValue = random.randint(-100, 100)/100
            if rqpValue is None: return
        except Exception as e:
            print(termcolor.colored(f"[SIMULATOR{self.simulatorIndex}] An unexpected error occurred while attempting to compute RQP value in simulation '{simulationCode}'.\n"
                                    f" * RQP Function Type: {tcConfig['rqpm_functionType']}\n"
                                    f" * Position Symbol:   {pSymbol}\n"
                                    f" * Timestamp:         {timestamp}\n"
                                    f" * Error:             {e}\n"
                                    f" * Detailed Trace:    {traceback.format_exc()}", 
                                    'light_red'))
            return
        if (type(rqpValue) not in (float, int)) or not (-1 <= rqpValue <= 1):
            print(termcolor.colored(f"[SIMULATOR{self.simulatorIndex}] An unexpected RQP value detected in simulation '{simulationCode}'. RQP value must be an integer or float in range [-1.0, 1.0].\n"
                                    f" * RQP Function Type: {tcConfig['rqpm_functionType']}\n"
                                    f" * RQP Value:         {rqpValue}\n"
                                    f" * Position Symbol:   {pSymbol}\n"
                                    f" * Timestamp:         {timestamp}", 
                                    'light_red'))
            return

        #SL Exit Flag
        tct_sle = tcTracker['slExited']
        if tcTracker['slExited'] is not None:
            if (tct_sle == 'SHORT' and 0 < rqpValue) or (tct_sle == 'LONG' and rqpValue < 0): tcTracker['slExited'] = None

        #Trade Handlers Determination
        tradeHandler_checkList = {'ENTRY': None,
                                  'CLEAR': None,
                                  'EXIT':  None}
        #---CheckList 1: CLEAR
        if   ((position['quantity'] < 0) and (0 < rqpValue)): tradeHandler_checkList['CLEAR'] = ('BUY',  kline[KLINDEX_CLOSEPRICE])
        elif ((0 < position['quantity']) and (rqpValue < 0)): tradeHandler_checkList['CLEAR'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
        #---CheckList 2: ENTRY & EXIT
        pslCheck = (tcConfig['postStopLossReentry'] == True) or (tcTracker['slExited'] is None)
        if (rqpValue < 0):  
            if ((pslCheck == True) and ((tcConfig['direction'] == 'BOTH') or (tcConfig['direction'] == 'SHORT'))): tradeHandler_checkList['ENTRY'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
            tradeHandler_checkList['EXIT']  = ('BUY',  kline[KLINDEX_CLOSEPRICE])
        elif (0 < rqpValue):
            if ((pslCheck == True) and ((tcConfig['direction'] == 'BOTH') or (tcConfig['direction'] == 'LONG'))): tradeHandler_checkList['ENTRY'] = ('BUY',  kline[KLINDEX_CLOSEPRICE])
            tradeHandler_checkList['EXIT']  = ('SELL', kline[KLINDEX_CLOSEPRICE])
        elif (rqpValue == 0):
            if   (position['quantity'] < 0): tradeHandler_checkList['EXIT'] = ('BUY',  kline[KLINDEX_CLOSEPRICE])
            elif (0 < position['quantity']): tradeHandler_checkList['EXIT'] = ('SELL', kline[KLINDEX_CLOSEPRICE])

        #Trade Handlers Determination
        tradeHandlers = list()
        if (tradeHandler_checkList['CLEAR'] is not None): tradeHandlers.append('CLEAR')
        if (tradeHandler_checkList['EXIT']  is not None): tradeHandlers.append('EXIT')
        if (tradeHandler_checkList['ENTRY'] is not None): tradeHandlers.append('ENTRY')

        #Trade Handlers Execution
        for tradeHandler in tradeHandlers:
            thParams = tradeHandler_checkList[tradeHandler]
            if (tradeHandler == 'CLEAR'): self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'CLEAR', side = thParams[0], quantity = abs(position['quantity']), timestamp = timestamp, tradePrice = thParams[1])
            else:
                _balance_allocated = position['allocatedBalance']                                          if (position['allocatedBalance'] is not None) else 0
                _balance_committed = abs(position['quantity'])*position['entryPrice']/tcConfig['leverage'] if (position['entryPrice']       is not None) else 0
                _balance_toCommit  = _balance_allocated*abs(rqpValue)
                _balance_toEnter   = _balance_toCommit-_balance_committed

                if (_balance_toEnter == 0): continue

                if (tradeHandler == 'ENTRY'):
                    if (0 < _balance_toEnter): 
                        _quantity_minUnit  = pow(10, -precisions['quantity'])
                        _quantity_toEnter  = round(int((_balance_toEnter/thParams[1]*tcConfig['leverage'])/_quantity_minUnit)*_quantity_minUnit, precisions['quantity'])
                        if (0 < _quantity_toEnter): self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'ENTRY', side = thParams[0], quantity = _quantity_toEnter, timestamp = timestamp, tradePrice = thParams[1])
                elif (tradeHandler == 'EXIT'):
                    if (_balance_toEnter < 0): 
                        _quantity_minUnit = pow(10, -precisions['quantity'])
                        _quantity_toExit  = round(int((-_balance_toEnter/position['entryPrice']*tcConfig['leverage'])/_quantity_minUnit)*_quantity_minUnit, precisions['quantity'])
                        if (0 < _quantity_toExit): self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'EXIT', side = thParams[0], quantity = _quantity_toExit, timestamp = timestamp, tradePrice = thParams[1])
    def __formatPeriodicReport(self, simulationCode, timestamp):
        #[1]: Instances
        simulation = self.__simulations[simulationCode]
        pReports   = simulation['_periodicReports']

        #[2]: Report Timestamp Check
        prTS = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = PERIODICREPORT_INTERVALID, timestamp = timestamp, mrktReg = None, nTicks = 0)
        if prTS in pReports: return prTS

        #[3]: Previous Report
        prTS_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = PERIODICREPORT_INTERVALID, timestamp = timestamp, mrktReg = None, nTicks = -1)
        prs_prev  = simulation['_periodicReports'].get(prTS_prev, None)

        #[4]: New Report Formatting
        assets  = simulation['_assets']
        pReport = dict()
        for assetName in simulation['assets']:
            asset = assets[assetName]
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
        simulation['_periodicReports'][prTS] = pReport

        #[5]: Return Periodic Report Timestamp
        return prTS
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
        simulation    = self.__simulations[simulationCode]
        assets_def    = simulation['assets']
        assets        = simulation['_assets']
        positions_def = simulation['positions']
        positions     = simulation['_positions']
        for assetName in simulation['assets']:
            asset_def = assets_def[assetName]
            asset     = assets[assetName]
            allocatedAssumedRatio = 0
            #[1]: Zero Quantity Allocation Zero
            for pSymbol in asset_def['_positionSymbols']: 
                position_def = positions_def[pSymbol]
                position     = positions[pSymbol]
                #[1-1]: Zero quantity
                if (position['quantity'] == 0): 
                    assumedRatio_effective       = 0
                    position['allocatedBalance'] = 0
                #[1-2]: Non-Zero Quantity
                else:
                    assumedRatio_effective = round(position['allocatedBalance']/asset['allocatableBalance'], 4)
                allocatedAssumedRatio += assumedRatio_effective
            #[2]: Zero Quantity Re-Allocation
            for pSymbol in asset_def['_positionSymbols_prioritySorted']:
                position_def = positions_def[pSymbol]
                position     = positions[pSymbol]
                #[2-1]: Condition Check (Zero Quantity )
                if not((position['quantity'] == 0) or ((position_def['assumedRatio'] != 0) and (position['allocatedBalance'] == 0))): continue
                #[2-2]: Allocated Balance & Effective Assumed Ratio Update
                allocatedBalance = min(round(asset['allocatableBalance']*position_def['assumedRatio'], position_def['precisions']['quote']), 
                                       position_def['maxAllocatedBalance'])
                assumedRatio_effective = round(allocatedBalance/asset['allocatableBalance'], 4)
                #[2-3]: Allocatability Check
                if (allocatedAssumedRatio+assumedRatio_effective <= 1):
                    allocatedAssumedRatio += assumedRatio_effective
                    position['allocatedBalance'] = allocatedBalance
                else: break
    def __processSimulatedTrade(self, simulationCode, positionSymbol, logicSource, side, quantity, timestamp, tradePrice):
        #Instantiation
        simulation   = self.__simulations[simulationCode]
        position_def = simulation['positions'][positionSymbol]
        position     = simulation['_positions'][positionSymbol]
        precisions   = position_def['precisions']
        asset        = simulation['_assets'][position_def['quoteAsset']]
        #Trade Processing
        if (logicSource == 'LIQUIDATION'):
            quantity_new = 0
            if   (0 < position['quantity']): profit = round(abs(position['quantity'])*(tradePrice-position['entryPrice']), precisions['quote'])
            elif (position['quantity'] < 0): profit = round(abs(position['quantity'])*(position['entryPrice']-tradePrice), precisions['quote'])
            entryPrice_new = None
            tradingFee     = round(position['quantity']*tradePrice*_SIMULATION_MARKETTRADINGFEE, precisions['quote'])
            if (position_def['isolated'] == True):
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
        else:
            #[1]: Compute Values
            #---Quantity
            if   (side == 'BUY'):  quantity_new = round(position['quantity']+quantity, precisions['quantity'])
            elif (side == 'SELL'): quantity_new = round(position['quantity']-quantity, precisions['quantity'])
            quantity_dirDelta = round(abs(quantity_new)-abs(position['quantity']), precisions['quantity'])
            #---Cost, Profit & Entry Price
            if (0 < quantity_dirDelta):
                #Entry Price
                if (position['quantity'] == 0): notional_prev = 0
                else:                           notional_prev = abs(position['quantity'])*position['entryPrice']
                notional_new = notional_prev+quantity_dirDelta*tradePrice
                entryPrice_new = round(notional_new/abs(quantity_new), precisions['price'])
                #Profit
                profit = 0
            elif (quantity_dirDelta < 0):
                #Entry Price
                if (quantity_new == 0): entryPrice_new = None
                else:                    entryPrice_new = position['entryPrice']
                #Profit
                if   (side == 'BUY'):  profit = round(quantity*(position['entryPrice']-tradePrice), precisions['quote'])
                elif (side == 'SELL'): profit = round(quantity*(tradePrice-position['entryPrice']), precisions['quote'])
            tradingFee = round(quantity*tradePrice*_SIMULATION_MARKETTRADINGFEE, precisions['quote'])
            currentNotional = tradePrice*abs(position['quantity'])
            maintenanceMarginRate, maintenanceAmount = atmEta_Constants.getMaintenanceMarginRateAndAmount(positionSymbol = positionSymbol, notional = currentNotional)
            maintenanceMargin_new = round(currentNotional*maintenanceMarginRate-maintenanceAmount, precisions['quote'])
            #[2]: Apply Values
            position['entryPrice']        = entryPrice_new
            position['quantity']          = quantity_new
            position['maintenanceMargin'] = maintenanceMargin_new
            asset['crossWalletBalance']   = round(asset['crossWalletBalance']+profit-tradingFee, precisions['quote'])
            position_positionInitialMargin_prev = position['positionInitialMargin']
            position['positionInitialMargin'] = round(tradePrice*abs(position['quantity'])/position_def['leverage'], precisions['price'])
            if (position_def['isolated'] == True):
                # _walletBalanceToTransfer = Balance from 'CrossWalletBalance' -> 'IsolatedWalletBalance' (Assuming all the other additional parameters (Insurance Fund, Open-Loss, etc) to be 1% of the notional value)
                #---Entry
                if (0 < quantity_dirDelta): walletBalanceToTransfer = round(quantity*tradePrice*((1/position_def['leverage'])+0.01), precisions['quote'])
                #---Exit
                elif (quantity_dirDelta < 0):
                    if (quantity_new == 0): walletBalanceToTransfer = -position['isolatedWalletBalance']
                    else:                   walletBalanceToTransfer = -round(quantity*position['entryPrice']/position_def['leverage'], precisions['quote'])
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
        #Update Account
        self.__updateAccount(simulationCode = simulationCode, timestamp = timestamp)
        #Save Trade Log
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
        simulation['_tradeLogs'].append(tradeLog)
        #Update Daily Report
        pReport_TS = self.__formatPeriodicReport(simulationCode = simulationCode, timestamp = timestamp)
        pReport    = simulation['_periodicReports'][pReport_TS][position_def['quoteAsset']]
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
        _nTrades_gain        = 0
        _nTrades_loss        = 0
        for _log in _tradeLog:
            _side        = _log['side']
            _logicSource = _log['logicSource']
            _profit      = _log['profit']
            if   (_side == 'BUY'):  _nTrades_buy  += 1
            elif (_side == 'SELL'): _nTrades_sell += 1
            if   (_logicSource == 'ENTRY'):       _nTrades_entry       += 1
            elif (_logicSource == 'CLEAR'):       _nTrades_clear       += 1
            elif (_logicSource == 'EXIT'):        _nTrades_exit        += 1
            elif (_logicSource == 'FSLIMMED'):    _nTrades_fslImmed    += 1
            elif (_logicSource == 'FSLCLOSE'):    _nTrades_fslClose    += 1
            elif (_logicSource == 'LIQUIDATION'): _nTrades_liquidation += 1
            if   (0 < _profit): _nTrades_gain += 1
            elif (_profit < 0): _nTrades_loss += 1
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
                                       'nTrades_gain':        _nTrades_gain,
                                       'nTrades_loss':        _nTrades_loss}}
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
            _nTrades_gain        = 0
            _nTrades_loss        = 0
            _gains_total         = 0
            _losses_total        = 0
            _tradingFee_total    = 0
            _initialWalletBalance = _simulation['assets'][_assetName]['initialWalletBalance']
            _walletBalance_min    = _initialWalletBalance
            _walletBalance_max    = _initialWalletBalance
            _walletBalance_final  = _initialWalletBalance
            for _log in _tradeLog_thisAsset:
                _side        = _log['side']
                _logicSource = _log['logicSource']
                _profit      = _log['profit']
                if   (_side == 'BUY'):  _nTrades_buy  += 1
                elif (_side == 'SELL'): _nTrades_sell += 1
                if   (_logicSource == 'ENTRY'):       _nTrades_entry       += 1
                elif (_logicSource == 'CLEAR'):       _nTrades_clear       += 1
                elif (_logicSource == 'EXIT'):        _nTrades_exit        += 1
                elif (_logicSource == 'FSLIMMED'):    _nTrades_fslImmed    += 1
                elif (_logicSource == 'FSLCLOSE'):    _nTrades_fslClose    += 1
                elif (_logicSource == 'LIQUIDATION'): _nTrades_liquidation += 1
                if   (0 < _profit): _nTrades_gain += 1
                elif (_profit < 0): _nTrades_loss += 1
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
                                             'nTrades_gain':        _nTrades_gain, 
                                             'nTrades_loss':        _nTrades_loss,
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
    def __exportAnalysis(self, simulationCode):
        _simulation = self.__simulations[simulationCode]
        if (_simulation['analysisExport'][0] == True):
            #[1]: Analysis Exports Main Folder
            _path_Main = os.path.join(self.path_project, 'data', 'analysisExports')
            if (os.path.exists(_path_Main) == False): os.makedirs(_path_Main)

            #[2]: Analysis Exports Simulation Folder
            _index_Sim = None
            _path_Sim  = os.path.join(_path_Main, f"{simulationCode}_ae")
            if (os.path.exists(_path_Sim) == False): os.makedirs(_path_Sim)
            else:
                _index_Sim = 0
                while (True):
                    _path_Sim = os.path.join(self.path_project, 'data', 'analysisExports', f"{simulationCode}_ae_{_index_Sim}")
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
                _data_numpy = numpy.array(object = _position['AE']['data'], dtype = numpy.float32)

                #Data Save
                numpy.save(file = _path_files['data'], arr = _data_numpy)
                with open(_path_files['descriptor'], 'w') as _f: _f.write(json.dumps(_descriptor))

                #Plot Image
                if (_simulation['analysisExport'][1] == True):
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
                        matplotlib.pyplot.suptitle(f"'{_baseName}' ANALYSIS EXPORT - KLINE", fontsize=10)
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
                        for _ae_data_row in _position['AE']['data']:
                            _closePrice = _ae_data_row[4]
                            _pip_cs     = _ae_data_row[10]
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
                        matplotlib.pyplot.suptitle(f"'{_baseName}' ANALYSIS EXPORT - SIGNAL PRICE DEVIATION CYCLIC", fontsize=10)
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
                        for _ae_data_row in _position['AE']['data']:
                            _closePrice  = _ae_data_row[4]
                            _pip_lsType  = _ae_data_row[7]
                            _pip_lsPrice = _ae_data_row[8]
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
                        matplotlib.pyplot.suptitle(f"'{_baseName}' ANALYSIS EXPORT - SWING PRICE DEVIATION CYCLIC", fontsize=10)
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
        simulation = self.__simulations[simulationCode]
        simulation['_status']   = 'ERROR'
        simulation['_errorMsg'] = errorCause
        self.ipcA.sendFAR(targetProcess = 'SIMULATIONMANAGER', functionID = 'onSimulationUpdate', functionParams = {'simulationCode': simulationCode, 'updateType': 'STATUS', 'updatedValue': simulation['_status']}, farrHandler = None)
        self.__simulations_removalQueue.append(simulationCode)
        if self.__simulations_currentlyHandling == simulationCode: self.__simulations_currentlyHandling = None
    def __processSimulationRemovalQueue(self):
        while self.__simulations_removalQueue:
            simulationCode    = self.__simulations_removalQueue.pop(0)
            hadNeuralNetworks = (0 < len(self.__simulations[simulationCode]['_neuralNetworks']))
            del self.__simulations[simulationCode]
            if hadNeuralNetworks:
                gc.collect()
                torch.cuda.empty_cache()
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
    def __far_addSimulation(self, requester, simulationCode, simulationRange, analysisExport, assets, positions, currencyAnalysisConfigurations, tradeConfigurations, creationTime):
        #[1]: Requester Check
        if requester != 'SIMULATIONMANAGER': return
        
        #[2]: Construct Analysis Params
        analyzers = dict()
        for cacCode in currencyAnalysisConfigurations:
            analysisParams, invalidLines = atmEta_Analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(currencyAnalysisConfigurations[cacCode])
            if invalidLines:
                invalidLines_str = atmEta_Auxillaries.formatInvalidLinesReportToString(invalidLines = invalidLines)
                print(termcolor.colored((f"[SIMULATOR-{self.name}] Invalid lines detected while attempting to start currency analysis."+invalidLines_str), 'light_red'))
        
            analysisToProcess_sorted = list()
            for analysisType in atmEta_Analyzers.ANALYSIS_GENERATIONORDER: analysisToProcess_sorted.extend([(analysisType, analysisCode) for analysisCode in analysisParams if analysisCode.startswith(analysisType)])
            analyzers[cacCode] = {'analysisParams':           analysisParams,
                                  'analysisToProcess_sorted': analysisToProcess_sorted}
            
        #[3]: Format Assets
        assets_formatted = dict()
        for assetName in assets:
            iwb = assets[assetName]['initialWalletBalance']
            assets_formatted[assetName] = {'marginBalance':                 iwb,
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
                                           'riskLevel':      None}
            
        #[4]: Format Positions
        positions_formatted = dict()
        for pSymbol in positions:
            positions_formatted[pSymbol] = {#Base
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
                                                                    'rqpm_model': dict()},
                                            #Analysis Export
                                            'AE': {'index': None,
                                                   'data':  list()}
                                            }

        #[5]: Create a simulation instance
        simulation = {'simulationRange':                simulationRange,
                      'analysisExport':                 analysisExport,
                      'assets':                         assets,
                      'positions':                      positions,
                      'currencyAnalysisConfigurations': currencyAnalysisConfigurations,
                      'tradeConfigurations':            tradeConfigurations,
                      'creationTime':                   creationTime,
                      '_neuralNetworks':                           dict(),
                      '_neuralNetworks_connectionsDataRequestIDs': set(),
                      '_assets':                   assets_formatted,
                      '_positions':                positions_formatted,
                      '_analyzers':                analyzers,
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
                      '_periodicReports':    dict(),
                      '_simulationSummary':  None}
        
        #[6]: Position-dependent variables
        for pSymbol in simulation['_positions']: 
            simulation['_klines'][pSymbol]                   = {'raw': dict(), 'raw_status': dict()}
            simulation['_klines_dataRange'][pSymbol]         = positions[pSymbol]['dataRange']
            simulation['_klines_lastRemovedOpenTS'][pSymbol] = {'raw': None}
            _analysisParams = simulation['_analyzers'][simulation['positions'][pSymbol]['currencyAnalysisConfigurationCode']]['analysisParams']
            for analysisCode in _analysisParams: 
                simulation['_klines'][pSymbol][analysisCode]                   = dict()
                simulation['_klines_lastRemovedOpenTS'][pSymbol][analysisCode] = None

        #[7]: Add the created simulation instance and append to the handling queue
        self.__simulations[simulationCode] = simulation
        self.__simulations_handlingQueue.append(simulationCode)
    def __far_removeSimulation(self, requester, simulationCode):
        #[1]: Requester Check
        if requester != 'SIMULATIONMANAGER': return

        #[2]: Simulation Removal
        if simulationCode in self.__simulations:
            simulation = self.__simulations[simulationCode]
            if simulation['_status'] == 'QUEUED':
                self.__simulations_handlingQueue.remove(simulationCode)
                self.__simulations_removalQueue.append(simulationCode)
            elif simulation['_status'] == 'PROCESSING':
                self.__simulations_removalQueue.append(simulationCode)
            if self.__simulations_currentlyHandling == simulationCode: self.__simulations_currentlyHandling = None

        #[3]: Response 
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
        #[1]: Responder Check
        if responder != 'NEURALNETWORKMANAGER': return

        #[2]: Request ID Check
        simulationCode = self.__simulations_currentlyHandling
        simulation     = self.__simulations[simulationCode]
        cdRIDs = simulation['_neuralNetworks_connectionsDataRequestIDs']
        if requestID not in cdRIDs: return

        #[3]: Result Interpretation
        cdRIDs.remove(requestID)
        #---[3-1]: Request Failure Handling
        if functionResult is None:
            self.__raiseSimulationError(simulationCode = simulationCode, errorCause = 'NONEURALNETWORKFOUND')
            return
        #---[3-2]: Request Success Handling
        #------Results
        neuralNetworkCode  = functionResult['neuralNetworkCode']
        nKlines            = functionResult['nKlines']
        hiddenLayers       = functionResult['hiddenLayers']
        outputLayer        = functionResult['outputLayer']
        connections        = functionResult['connections']
        #------Neural Network Instance
        nn = atmEta_NeuralNetworks.neuralNetwork_MLP(nKlines      = nKlines,
                                                     hiddenLayers = hiddenLayers, 
                                                     outputLayer  = outputLayer, 
                                                     device       = 'cpu')
        nn.importConnectionsData(connections = connections)
        nn.setEvaluationMode()
        simulation['_neuralNetworks'][neuralNetworkCode] = nn
        #------Last Request Result Receival
        if not cdRIDs:
            simulation['_procStatus'] = 'FETCHING'
            self.__sendKlineFetchRequestForTheCurrentFocusDay(simulationCode = simulationCode)
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------