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
            if simulation['analysisExport']:
                ae = position['AE']
                #[3-7-1]: Index Identifiers
                if ae['indexIdentifier'] is None: 
                    ae_ii = {'KLINE_OPENTIME':        0,
                             'KLINE_OPENPRICE':       1,
                             'KLINE_HIGHPRICE':       2,
                             'KLINE_LOWPRICE':        3,
                             'KLINE_CLOSEPRICE':      4,
                             'KLINE_VOLBASE':         5,
                             'KLINE_VOLBASETAKERBUY': 6}
                    ae_keys = sorted(aLinearized)
                    laIndex = max(ae_ii.values())+1
                    for laKey in ae_keys:
                        ae_ii[laKey] = laIndex
                        laIndex += 1
                    ae['indexIdentifier']        = ae_ii
                    ae['linearizedAnalysisKeys'] = ae_keys
                #[3-7-2]: Tuplization & Appending
                aLinearized_tuple = (kline[KLINDEX_OPENTIME],
                                     kline[KLINDEX_OPENPRICE],
                                     kline[KLINDEX_HIGHPRICE],
                                     kline[KLINDEX_LOWPRICE],
                                     kline[KLINDEX_CLOSEPRICE],
                                     kline[KLINDEX_VOLBASE],
                                     kline[KLINDEX_VOLBASETAKERBUY]) + tuple(aLinearized[laKey] for laKey in ae['linearizedAnalysisKeys'])
                position['AE']['data'].append(aLinearized_tuple)
                
        #[4]: Wallet Balance Trend Analysis Update
        for assetName in assets_def:
            #[4-1]: Instances
            asset         = assets[assetName]
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
        for assetName in assets_def:
            #[5-1]: Instances & Daily Report Formatting (If needed)
            asset      = assets[assetName]
            pReport_TS = self.__formatPeriodicReport(simulationCode = simulationCode, timestamp = atTS)
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

        #[6]: Post-process handling, update the next analysis target and return how the update occurred
        if atTS == simulation['_lastAnalysisTarget']: 
            return _SIMULATION_PROCESSING_ANALYSISRESULT_COMPLETE
        else:
            simulation['_nextAnalysisTarget'] += KLINTERVAL_S
            if simulation['_currentFocusDay']+86400 <= simulation['_nextAnalysisTarget']: return _SIMULATION_PROCESSING_ANALYSISRESULT_FETCHNEXT
            else:                                                                         return _SIMULATION_PROCESSING_ANALYSISRESULT_ANALYZENEXT
    def __handleKline(self, simulationCode, pSymbol, timestamp, kline):
        #Instances Call
        simulation   = self.__simulations[simulationCode]
        position_def = simulation['positions'][pSymbol]
        position     = simulation['_positions'][pSymbol]
        asset        = simulation['_assets'][position_def['quoteAsset']]
        tcConfig     = simulation['tradeConfigurations'][simulation['positions'][pSymbol]['tradeConfigurationCode']]
        tcTracker    = position['tradeControlTracker']
        precisions   = position_def['precisions']

        #Force Exit Check
        tradeHandler_checkList = {'FSLIMMED':    None,
                                  'FSLCLOSE':    None,
                                  'LIQUIDATION': None}
        if (position['quantity'] != 0):
            #FSL IMMED
            if (tcConfig['fullStopLossImmediate'] is not None):
                #<SHORT>
                if (position['quantity'] < 0):
                    _price_FSL = round(position['entryPrice']*(1+tcConfig['fullStopLossImmediate']), precisions['price'])
                    if (_price_FSL <= kline[KLINDEX_HIGHPRICE]): tradeHandler_checkList['FSLIMMED'] = ('BUY', _price_FSL, _price_FSL-kline[KLINDEX_OPENPRICE])
                #<LONG>
                elif (0 < position['quantity']):
                    _price_FSL = round(position['entryPrice']*(1-tcConfig['fullStopLossImmediate']), precisions['price'])
                    if (kline[KLINDEX_LOWPRICE] <= _price_FSL): tradeHandler_checkList['FSLIMMED'] = ('SELL', _price_FSL, kline[KLINDEX_OPENPRICE]-_price_FSL)
            #FSL CLOSE
            if (tcConfig['fullStopLossClose'] is not None):
                #<SHORT>
                if (position['quantity'] < 0):
                    _price_FSL = round(position['entryPrice']*(1+tcConfig['fullStopLossClose']), precisions['price'])
                    if (_price_FSL <= kline[KLINDEX_HIGHPRICE]): tradeHandler_checkList['FSLCLOSE'] = ('BUY', kline[KLINDEX_CLOSEPRICE])
                #<LONG>
                elif (0 < position['quantity']):
                    _price_FSL = round(position['entryPrice']*(1-tcConfig['fullStopLossClose']), precisions['price'])
                    if (kline[KLINDEX_LOWPRICE] <= _price_FSL): tradeHandler_checkList['FSLCLOSE'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
            #LIQUIDATION
            if (position['liquidationPrice'] is not None):
                #<SHORT>
                if (position['quantity'] < 0):
                    if (position['liquidationPrice'] <= kline[KLINDEX_HIGHPRICE]): tradeHandler_checkList['LIQUIDATION'] = ('LIQUIDATION', position['liquidationPrice'], position['liquidationPrice']-kline[KLINDEX_OPENPRICE])
                #<LONG>
                elif (0 < position['quantity']):
                    if (kline[KLINDEX_LOWPRICE] <= position['liquidationPrice']): tradeHandler_checkList['LIQUIDATION'] = ('LIQUIDATION', position['liquidationPrice'], kline[KLINDEX_OPENPRICE]-position['liquidationPrice'])

        #Trade Handler Determination
        if ((tradeHandler_checkList['LIQUIDATION'] is not None) and (tradeHandler_checkList['FSLIMMED'] is not None)):
            if (tradeHandler_checkList['LIQUIDATION'][2] <= tradeHandler_checkList['FSLIMMED'][2]): tradeHandler = 'LIQUIDATION'
            else:                                                                                   tradeHandler = 'FSLIMMED'
        elif (tradeHandler_checkList['LIQUIDATION'] is not None): tradeHandler = 'LIQUIDATION'
        elif (tradeHandler_checkList['FSLIMMED']    is not None): tradeHandler = 'FSLIMMED'
        elif (tradeHandler_checkList['FSLCLOSE']    is not None): tradeHandler = 'FSLCLOSE'
        else:                                                     tradeHandler = None

        #Trade Handlers Execution
        if (tradeHandler is None): return
        thParams      = tradeHandler_checkList[tradeHandler]
        quantity_prev = position['quantity']
        #---[1]: FSLIMMED
        if (tradeHandler == 'FSLIMMED'):
            self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'FSLIMMED', side = thParams[0], quantity = abs(position['quantity']), timestamp = timestamp, tradePrice = thParams[1])
            if   (quantity_prev < 0): tcTracker['slExited'] = 'SHORT'
            elif (0 < quantity_prev): tcTracker['slExited'] = 'LONG'
        #---[2]: FSLCLOSE
        elif (tradeHandler == 'FSLCLOSE'):
            self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'FSLCLOSE', side = thParams[0], quantity = abs(position['quantity']), timestamp = timestamp, tradePrice = thParams[1])
            if   (quantity_prev < 0): tcTracker['slExited'] = 'SHORT'
            elif (0 < quantity_prev): tcTracker['slExited'] = 'LONG'
        #---[3]: LIQUIDATION
        elif (tradeHandler == 'LIQUIDATION'): 
            self.__processSimulatedTrade(simulationCode = simulationCode, positionSymbol = pSymbol, logicSource = 'LIQUIDATION', side = None, quantity = abs(position['quantity']), timestamp = timestamp, tradePrice = thParams[1]) 
    def __handleAnalysisResult(self, simulationCode, pSymbol, linearizedAnalysis, timestamp, kline):
        #[1]: Instances
        simulation   = self.__simulations[simulationCode]
        position_def = simulation['positions'][pSymbol]
        position     = simulation['_positions'][pSymbol]
        asset        = simulation['_assets'][position_def['quoteAsset']]
        tcConfig     = simulation['tradeConfigurations'][simulation['positions'][pSymbol]['tradeConfigurationCode']]
        tcTracker    = position['tradeControlTracker']
        precisions   = position_def['precisions']

        #[2]: RQP Value
        try:
            rqps = atmEta_RQPMFunctions.RQPMFUNCTIONS_GET_RQPVAL[tcConfig['rqpm_functionType']](params             = tcConfig['rqpm_functionParams'], 
                                                                                                kline              = kline, 
                                                                                                linearizedAnalysis = linearizedAnalysis, 
                                                                                                tcTracker_model    = tcTracker['rqpm_model'])
            rqpDirection, rqpValue = rqps
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

        #[3]: SL Exit Flag
        if tcTracker['slExited'] != rqpDirection: tcTracker['slExited'] = None

        #[4]: Trade Handlers Determination
        tradeHandler_checkList = {'ENTRY': None,
                                  'CLEAR': None,
                                  'EXIT':  None}
        #---[4-1]: CheckList 1: CLEAR
        if   (position['quantity'] < 0) and (rqpDirection != 'SHORT'): tradeHandler_checkList['CLEAR'] = ('BUY',  kline[KLINDEX_CLOSEPRICE])
        elif (0 < position['quantity']) and (rqpDirection != 'LONG'):  tradeHandler_checkList['CLEAR'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
        #---[4-2]: CheckList 2: ENTRY & EXIT
        pslCheck = tcConfig['postStopLossReentry'] or (tcTracker['slExited'] is None)
        if rqpDirection == 'SHORT':  
            if pslCheck and tcConfig['direction'] in ('BOTH', 'SHORT'): 
                tradeHandler_checkList['ENTRY'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
            tradeHandler_checkList['EXIT'] = ('BUY', kline[KLINDEX_CLOSEPRICE])
        elif rqpDirection == 'LONG':
            if pslCheck and tcConfig['direction'] in ('BOTH', 'LONG'): 
                tradeHandler_checkList['ENTRY'] = ('BUY',  kline[KLINDEX_CLOSEPRICE])
            tradeHandler_checkList['EXIT'] = ('SELL', kline[KLINDEX_CLOSEPRICE])
        elif rqpDirection is None:
            if   position['quantity'] < 0: tradeHandler_checkList['EXIT'] = ('BUY',  kline[KLINDEX_CLOSEPRICE])
            elif 0 < position['quantity']: tradeHandler_checkList['EXIT'] = ('SELL', kline[KLINDEX_CLOSEPRICE])

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
                self.__processSimulatedTrade(simulationCode = simulationCode, 
                                             positionSymbol = pSymbol, 
                                             logicSource    = 'CLEAR', 
                                             side           = th_side, 
                                             quantity       = abs(position['quantity']), 
                                             timestamp      = timestamp, 
                                             tradePrice     = th_price)
            #[6-2]: ENTRY & EXIT
            else:
                balance_allocated = position['allocatedBalance']                                          if (position['allocatedBalance'] is not None) else 0
                balance_committed = abs(position['quantity'])*position['entryPrice']/tcConfig['leverage'] if (position['entryPrice']       is not None) else 0
                balance_toCommit  = balance_allocated*abs(rqpValue)
                balance_toEnter   = balance_toCommit-balance_committed
                if balance_toEnter == 0: continue
                #[6-2-1]: ENTRY
                if tradeHandler == 'ENTRY':
                    if not (0 < balance_toEnter): continue
                    quantity_minUnit  = pow(10, -precisions['quantity'])
                    quantity_toEnter  = round(int((balance_toEnter/th_price*tcConfig['leverage'])/quantity_minUnit)*quantity_minUnit, precisions['quantity'])
                    if not (0 < quantity_toEnter): continue
                    self.__processSimulatedTrade(simulationCode = simulationCode, 
                                                 positionSymbol = pSymbol, 
                                                 logicSource    = 'ENTRY', 
                                                 side           = th_side, 
                                                 quantity       = quantity_toEnter, 
                                                 timestamp      = timestamp, 
                                                 tradePrice     = th_price)
                #[6-2-1]: EXIT
                elif tradeHandler == 'EXIT':
                    if not (balance_toEnter < 0): continue
                    quantity_minUnit = pow(10, -precisions['quantity'])
                    quantity_toExit  = round(int((-balance_toEnter/position['entryPrice']*tcConfig['leverage'])/quantity_minUnit)*quantity_minUnit, precisions['quantity'])
                    if not (0 < quantity_toExit): continue
                    self.__processSimulatedTrade(simulationCode = simulationCode, 
                                                 positionSymbol = pSymbol, 
                                                 logicSource    = 'EXIT', 
                                                 side           = th_side, 
                                                 quantity       = quantity_toExit, 
                                                 timestamp      = timestamp, 
                                                 tradePrice     = th_price)
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
        #[1]: Instances
        simulation    = self.__simulations[simulationCode]
        positions_def = simulation['positions']
        assets        = simulation['_assets']
        tradeLogs     = simulation['_tradeLogs']

        #[2]: Entire Summary
        nTrades_total = len(tradeLogs)
        if (0 < nTrades_total):
            dailyTS_firstLog = int(tradeLogs[0]['timestamp']/86400)*86400
            nTradeDays = int((simulation['simulationRange'][1]-dailyTS_firstLog)/86400)+1
        else: nTradeDays = 0
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
                nTradeDays = int((simulation['simulationRange'][1]-dailyTS_firstLog)/86400)+1
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
                gains_total      = round(gains_total,      _SIMULATION_ASSETPRECISIONS[assetName])
                losses_total     = round(losses_total,     _SIMULATION_ASSETPRECISIONS[assetName])
                tradingFee_total = round(tradingFee_total, _SIMULATION_ASSETPRECISIONS[assetName])
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
                                            'nTrades_total': nTrades_total, 
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
    def __exportAnalysis(self, simulationCode):
        simulation = self.__simulations[simulationCode]
        if simulation['analysisExport']:
            #[1]: Analysis Exports Main Folder
            path_Main = os.path.join(self.path_project, 'data', 'analysisExports')
            if not os.path.exists(path_Main): os.makedirs(path_Main)

            #[2]: Analysis Exports Simulation Folder
            index_Sim = None
            path_Sim  = os.path.join(path_Main, f"{simulationCode}_ae")
            if os.path.exists(path_Sim): 
                index_Sim = 0
                while True:
                    path_Sim = os.path.join(path_Main, f"{simulationCode}_ae_{index_Sim}")
                    if not os.path.exists(path_Sim):
                        os.makedirs(path_Sim)
                        break
                    index_Sim += 1
            else:
                os.makedirs(path_Sim)

            #[3]: Numpy Conversion & Save
            positions = simulation['_positions']
            for pSymbol in positions:
                position = positions[pSymbol]
                ae       = position['AE']
                #[3-1]: File Name
                if index_Sim is None: baseName = f"{simulationCode}_{pSymbol}"
                else:                 baseName = f"{simulationCode}_{index_Sim}_{pSymbol}"
                path_descriptor = os.path.join(path_Sim, f"{baseName}_descriptor.json")
                path_data       = os.path.join(path_Sim, f"{baseName}_data.npy")

                #[3-3]: Numpy Conversion
                data_numpy = numpy.array(object = ae['data'], dtype = numpy.float64)

                #[3-2]: Descriptor & Numpy Conversion
                descriptor = {'genTime_ns':      time.time_ns(),
                              'simulationCode':  simulationCode,
                              'positionSymbol':  pSymbol,
                              'indexIdentifier': ae['indexIdentifier']}

                #[3-4]: Data Save
                numpy.save(file = path_data, arr = data_numpy)
                with open(path_descriptor, 'w') as f: f.write(json.dumps(descriptor, indent = 4))
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
                                            'AE': {'indexIdentifier':        None,
                                                   'linearizedAnalysisKeys': None,
                                                   'data':                   list()}
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