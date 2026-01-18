#ATM Modules
import torch.random
import atmEta_IPC
import atmEta_Auxillaries
import atmEta_NeuralNetworks
import atmEta_Analyzers
import atmEta_Constants

#Python Modules
import time
import termcolor
import pprint
import bcrypt
import math
import torch
import numpy
import os
import json
import random
import pandas

#Constants
_IPC_THREADTYPE_MT         = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT         = atmEta_IPC._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = atmEta_IPC._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = atmEta_IPC._FAR_INVALIDFUNCTIONID

_NEURALNETWORKTYPES  = {'MLP'}

_INITIALIZATIONTYPES = {'UNIFORM':   {'a': 0, 'b': 1},
                        'NORMAL':    {'mean': 0, 'std': 1},
                        'X_UNIFORM': {'gain': 1.0},
                        'X_NORMAL':  {'gain': 1.0},
                        'Y_UNIFORM': {'a': 0, 'mode': 'fan_in', 'nonlinearity': 'leaky_relu'},
                        'Y_NORMAL':  {'a': 0, 'mode': 'fan_in', 'nonlinearity': 'leaky_relu'}}
_OPTIMIZERTYPES = {'SGD':     {'momentum': 0, 'dampening': 0, 'weight_decay': 0, 'nesterov': False},
                   'Adam':    {'betas': (0.9, 0.999), 'eps': 1e-08, 'weight_decay': 0, 'amsgrad': False},
                   'RMSprop': {'momentum': 0, 'alpha': 0.99, 'eps': 1e-8, 'centered': False, 'weight_decay': 0, 'momentum_decay': 0},
                   'Adagrad': {'lr_decay': 0, 'weight_decay': 0, 'initial_accumulator_value': 0, 'eps': 1e-10},
                   'AdamW':   {'betas': (0.9, 0.999), 'eps': 1e-08, 'weight_decay': 0, 'amsgrad': False}}
_LOSSFUNCTIONTYPES = {'MSE': {'reduction': 'mean'},
                      'MAE': {'reduction': 'mean'},
                      'BCE': {'reduction': 'mean'}}

_PROCESS_TIMEOUT_NS = 100e6
_PROCESS_TYPE_TRAINING                         = 0
_PROCESS_TYPE_PERFORMANCETEST                  = 1
_PROCESS_STATUS_WAITIGKLINES                   = 0
_PROCESS_STATUS_KLINESRECEIVED                 = 1
_PROCESS_STATUS_PREPROCESSING                  = 2
_PROCESS_STATUS_GENERATING                     = 3
_PROCESS_PREPROCESSINGTYPE_LABELSEARCH         = 0
_PROCESS_PREPROCESSINGTYPE_LABELING            = 1
_PROCESS_PREPROCESSINGTYPE_NORMALIZATION       = 2
_PROCESS_ACTIONTYPE_TRAINING                   = 0
_PROCESS_ACTIONTYPE_PERFORMANCETEST            = 1
_PROCESS_PREPROCESSING_SWINGTYPE_LOW  = 0
_PROCESS_PREPROCESSING_SWINGTYPE_HIGH = 1
_PROCESS_ETCCOMPUTE_NSAMPLES = 10000
_PROCESS_ETCCOMPUTE_KVALUE   = 2/(_PROCESS_ETCCOMPUTE_NSAMPLES+1)

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

_NUMPYDTYPE = atmEta_NeuralNetworks._NUMPYDTYPE
_TORCHDTYPE = atmEta_NeuralNetworks._TORCHDTYPE

KLINTERVAL = atmEta_Constants.KLINTERVAL

class procManager_NeuralNetworkManager:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA):
        print(termcolor.colored("   Initializing", 'green'), termcolor.colored("NEURALNETWORKMANAGER", 'light_blue'), termcolor.colored("--------------------------------------------------------------------------------------------------------------", 'green'))
        #IPC Assistance
        self.ipcA = ipcA
        
        #Project Path
        self.path_project = path_project
        self.path_manager = os.path.join(self.path_project, 'data', 'nnm')
        
        #Constants Share
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'NEURALNETWORKTYPES',  prdContent = _NEURALNETWORKTYPES)
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'INITIALIZATIONTYPES', prdContent = _INITIALIZATIONTYPES)
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'OPTIMIZERTYPES',      prdContent = _OPTIMIZERTYPES)
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'LOSSFUNCTIONTYPES',   prdContent = _LOSSFUNCTIONTYPES)

        #Currencies Data
        self.__currencies = dict()

        #Neural Networks
        self.__neuralNetworks = dict()
        self.__neuralNetwork_currentProcessCode         = None
        self.__neuralNetwork_currentProcessInternalData = None
        self.__neuralNetwork_processes                  = dict()
        self.__neuralNetwork_processQueues              = list()
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'NEURALNETWORKS', prdContent = self.__neuralNetworks)
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'PROCESSES',      prdContent = self.__neuralNetwork_processes)
        
        #FAR Registration
        #---DATAMANAGER
        self.ipcA.addFARHandler('onCurrenciesUpdate', self.__far_onCurrenciesUpdate, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---GUI
        self.ipcA.addFARHandler('initializeNeuralNetwork', self.__far_initializeNeuralNetwork, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('generateNeuralNetwork',   self.__far_generateNeuralNetwork,   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('removeNeuralNetwork',     self.__far_removeNeuralNetwork,     executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('runTraining',             self.__far_runTraining,             executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('runPerformanceTest',      self.__far_runPerformanceTest,      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('removeProcess',           self.__far_removeProcess,           executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---COMMON
        self.ipcA.addFARHandler('getNeuralNetworkConnections', self.__far_getNeuralNetworkConnections, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

        #Process Control
        self.__processLoopContinue = True
        print(termcolor.colored("   NEURALNETWORKMANAGER", 'light_blue'), termcolor.colored("Initialization Complete! --------------------------------------------------------------------------------------------------", 'green'))
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Process Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        #Get Currencies & Account Data from DATAMANAGER
        self.__currencies = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = 'CURRENCIES')
        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'loadNeuralNetworkDescriptions', functionParams = None, farrHandler = self.__farr_onNeuralNetworkDescriptionLoadRequestResponse)

        while (self.__processLoopContinue == True):
            #Process any existing FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()
            #Process Neural Networks
            self.__processNeuralNetworks()
            #Process Loop Control
            if (self.__loopSleepDeterminer() == True): time.sleep(0.001)

    def __loopSleepDeterminer(self):
        sleepLoop = True
        if (self.__neuralNetwork_currentProcessCode != None):
            _process = self.__neuralNetwork_processes[self.__neuralNetwork_currentProcessCode]
            if (_process['status'] == _PROCESS_STATUS_GENERATING): sleepLoop = False
        return sleepLoop

    def terminate(self, requester):
        self.__processLoopContinue = False
    #Manager Process Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    
    #Manager Internal Functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __processNeuralNetworks(self):
        #Process Target Update (If needed)
        if (self.__neuralNetwork_currentProcessCode is None):
            if (0 < len(self.__neuralNetwork_processQueues)):
                #Process & Neural Network
                self.__neuralNetwork_currentProcessCode = self.__neuralNetwork_processQueues.pop(0)
                _process = self.__neuralNetwork_processes[self.__neuralNetwork_currentProcessCode]
                _neuralNetworkCode = _process['neuralNetworkCode']
                _neuralNetwork     = self.__neuralNetworks[_neuralNetworkCode]
                
                #Internal Data Formatting
                if (_process['processType'] == 'TRAINING'):  
                    self.__neuralNetwork_currentProcessInternalData = {'type':                       _PROCESS_TYPE_TRAINING,
                                                                       'startTime':                  time.time(),
                                                                       'status':                     _PROCESS_STATUS_WAITIGKLINES,
                                                                       'completion_lastComputed_ns': None,
                                                                       'completion_avgRate' :        None,
                                                                       'klineFetchRequestRID':       None,
                                                                       'klines':            {'raw': dict(), 'raw_status': dict()},
                                                                       'klines_timestamps': list(),
                                                                       'klines_length':     0,
                                                                       'preprocessing_type':               None,
                                                                       'preprocessing_swingSearch':        None,
                                                                       'preprocessing_swings':             None,
                                                                       'preprocessing_labelSearchIndex':   None,
                                                                       'preprocessing_labels':             None,
                                                                       'preprocessing_samplingRange':      None,
                                                                       'preprocessing_nextSwingIndex':     None,
                                                                       'preprocessing_labelingIndex':      None,
                                                                       'preprocessing_normalizationIndex': None,
                                                                       'dataSet':                 None,
                                                                       'dataSet_numberOfBatches': None,
                                                                       'dataSet_batchIndex':      None,
                                                                       'training_complete':   False,
                                                                       'training_epochIndex': 0,
                                                                       'result': {'loss_sum': 0, 'loss_n': 0}}
                elif (_process['processType'] == 'PERFORMANCETEST'): 
                    self.__neuralNetwork_currentProcessInternalData = {'type':                       _PROCESS_TYPE_PERFORMANCETEST,
                                                                       'startTime':                  time.time(),
                                                                       'status':                     _PROCESS_STATUS_WAITIGKLINES,
                                                                       'completion_lastComputed_ns': None,
                                                                       'completion_avgRate' :        None,
                                                                       'klineFetchRequestRID':       None,
                                                                       'klines':            {'raw': dict(), 'raw_status': dict()},
                                                                       'klines_timestamps': list(),
                                                                       'klines_length':     0,
                                                                       'preprocessing_type':               None,
                                                                       'preprocessing_swingSearch':        None,
                                                                       'preprocessing_swings':             None,
                                                                       'preprocessing_labelSearchIndex':   None,
                                                                       'preprocessing_labels':             None,
                                                                       'preprocessing_samplingRange':      None,
                                                                       'preprocessing_nextSwingIndex':     None,
                                                                       'preprocessing_labelingIndex':      None,
                                                                       'preprocessing_normalizationIndex': None,
                                                                       'dataSet':                 None,
                                                                       'dataSet_numberOfBatches': None,
                                                                       'dataSet_batchIndex':      None,
                                                                       'result': {'loss_sum': 0, 'loss_n': 0}}
                #Status Update & Announcement
                #---Neural Network
                if   (_process['processType'] == 'TRAINING'):        _neuralNetwork['status'] = 'TRAINING'
                elif (_process['processType'] == 'PERFORMANCETEST'): _neuralNetwork['status'] = 'TESTING'
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', _neuralNetworkCode, 'status'), prdContent = _neuralNetwork['status'])
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'STATUS', 'updatedContent': _neuralNetworkCode}, farrHandler = None)
                #---Process
                _process['status'] = 'PREPARING'
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('PROCESSES', self.__neuralNetwork_currentProcessCode, 'status'), prdContent = _process['status'])
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onProcessUpdate', functionParams = {'updateType': 'STATUS', 'updatedContent': self.__neuralNetwork_currentProcessCode}, farrHandler = None)
                #Klines Request
                self.__neuralNetwork_currentProcessInternalData['klineFetchRequestRID'] = self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER',
                                                                                                            functionID     = 'fetchKlines',
                                                                                                            functionParams = {'symbol':     _process['targetCurrencySymbol'],
                                                                                                                              'fetchRange': _process['targetRange']},
                                                                                                            farrHandler    = self.__farr_onKlineFetchRequestResponse)
        #Processing Traning / Performance Test
        if (self.__neuralNetwork_currentProcessCode is not None):
            _process       = self.__neuralNetwork_processes[self.__neuralNetwork_currentProcessCode]
            _cpi           = self.__neuralNetwork_currentProcessInternalData
            _neuralNetwork = self.__neuralNetworks[_process['neuralNetworkCode']]
            #[1]: Klines Received
            if (_cpi['status'] == _PROCESS_STATUS_KLINESRECEIVED):
                #[1-1]: Identify Klines structure and first processing index
                _klines = _cpi['klines']
                _cpi['klines_timestamps'] = list(_klines['raw'].keys()); _cpi['klines_timestamps'].sort()
                _cpi['klines_length']     = len(_klines['raw'])
                #[1-2]: Set Status
                _cpi['status']     = _PROCESS_STATUS_PREPROCESSING
                _process['status'] = 'PREPROCESSING'
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('PROCESSES', self.__neuralNetwork_currentProcessCode, 'status'), prdContent = _process['status'])
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onProcessUpdate', functionParams = {'updateType': 'STATUS', 'updatedContent': self.__neuralNetwork_currentProcessCode}, farrHandler = None)
                #[1-3]: Prepare for "LABELSEARCH" phase
                _cpi['preprocessing_type']             = _PROCESS_PREPROCESSINGTYPE_LABELSEARCH
                _cpi['preprocessing_labelSearchIndex'] = 0
                _cpi['preprocessing_swingSearch']      = {'lastExtreme': None, 'max': None, 'min': None, 'max_tsIndex': None, 'min_tsIndex': None}
                _cpi['preprocessing_swings']           = list()
                _cpi['completion_avgRate'] = None
            #[2]: Preprocessing
            elif (_cpi['status'] == _PROCESS_STATUS_PREPROCESSING):
                _klines          = _cpi['klines']
                _klineTimestamps = _cpi['klines_timestamps']
                #[2-1]: Preprocessing Label Search
                if (_cpi['preprocessing_type'] == _PROCESS_PREPROCESSINGTYPE_LABELSEARCH):
                    _t_beg_ns = time.perf_counter_ns()
                    while ((time.perf_counter_ns()-_t_beg_ns <= _PROCESS_TIMEOUT_NS) and (_cpi['preprocessing_labelSearchIndex'] < _cpi['klines_length'])):
                        _kline_this = _klines['raw'][_klineTimestamps[_cpi['preprocessing_labelSearchIndex']]]
                        #Swing
                        _swingSearch = _cpi['preprocessing_swingSearch']
                        _swings      = _cpi['preprocessing_swings']
                        _swingRange  = _process['swingRange']
                        if (_swingSearch['lastExtreme'] is None):
                            _swingSearch['lastExtreme'] = True
                            _swingSearch['max']         = _kline_this[KLINDEX_HIGHPRICE]
                            _swingSearch['min']         = _kline_this[KLINDEX_LOWPRICE]
                            _swingSearch['max_tsIndex'] = _cpi['preprocessing_labelSearchIndex']
                            _swingSearch['min_tsIndex'] = _cpi['preprocessing_labelSearchIndex']
                        elif (_swingSearch['lastExtreme'] == True):
                            if (_kline_this[KLINDEX_LOWPRICE] < _swingSearch['min']): 
                                _swingSearch['min']         = _kline_this[KLINDEX_LOWPRICE]
                                _swingSearch['min_tsIndex'] = _cpi['preprocessing_labelSearchIndex']
                            if (_swingSearch['min']*(1+_swingRange) < _kline_this[KLINDEX_CLOSEPRICE]):
                                _swings.append((_swingSearch['min_tsIndex'], _swingSearch['min'], _PROCESS_PREPROCESSING_SWINGTYPE_LOW))
                                _swingSearch['lastExtreme'] = False
                                _swingSearch['max']         = _kline_this[KLINDEX_HIGHPRICE]
                                _swingSearch['max_tsIndex'] = _cpi['preprocessing_labelSearchIndex']
                        elif (_swingSearch['lastExtreme'] == False):
                            if (_swingSearch['max'] < _kline_this[KLINDEX_HIGHPRICE]): 
                                _swingSearch['max']         = _kline_this[KLINDEX_HIGHPRICE]
                                _swingSearch['max_tsIndex'] = _cpi['preprocessing_labelSearchIndex']
                            if (_kline_this[KLINDEX_CLOSEPRICE] < _swingSearch['max']*(1-_swingRange)):
                                _swings.append((_swingSearch['max_tsIndex'], _swingSearch['max'], _PROCESS_PREPROCESSING_SWINGTYPE_HIGH))
                                _swingSearch['lastExtreme'] = True
                                _swingSearch['min']         = _kline_this[KLINDEX_LOWPRICE]
                                _swingSearch['min_tsIndex'] = _cpi['preprocessing_labelSearchIndex']
                        #Index
                        _cpi['preprocessing_labelSearchIndex'] += 1
                #[2-2]: Preprocessing Labeling
                elif (_cpi['preprocessing_type'] == _PROCESS_PREPROCESSINGTYPE_LABELING):
                    _dataSet = _cpi['dataSet']
                    _t_beg_ns = time.perf_counter_ns()
                    while ((time.perf_counter_ns()-_t_beg_ns <= _PROCESS_TIMEOUT_NS) and (_cpi['preprocessing_labelingIndex'] <= _cpi['preprocessing_samplingRange'][1])):
                        #Sample Index
                        _sIndex = _cpi['preprocessing_labelingIndex']-_cpi['preprocessing_samplingRange'][0]
                        #Labeling
                        if (_cpi['preprocessing_nextSwingIndex'] < len(_cpi['preprocessing_swings'])):
                            nsIdx = _cpi['preprocessing_nextSwingIndex']
                            _swing_next = _cpi['preprocessing_swings'][nsIdx]
                            if   (_swing_next[2] == _PROCESS_PREPROCESSING_SWINGTYPE_LOW):  _dataSet[_sIndex][0] = 0
                            elif (_swing_next[2] == _PROCESS_PREPROCESSING_SWINGTYPE_HIGH): _dataSet[_sIndex][0] = 1
                            if (_swing_next[0] == _cpi['preprocessing_labelingIndex']): _cpi['preprocessing_nextSwingIndex'] += 1
                        else: _dataSet[_sIndex][0] = 0.5
                        #---Index
                        _cpi['preprocessing_labelingIndex'] += 1
                #[2-3]: Normalization
                elif (_cpi['preprocessing_type'] == _PROCESS_PREPROCESSINGTYPE_NORMALIZATION):
                    _dataSet = _cpi['dataSet']
                    _t_beg_ns = time.perf_counter_ns()
                    while ((time.perf_counter_ns()-_t_beg_ns <= _PROCESS_TIMEOUT_NS) and (_cpi['preprocessing_normalizationIndex'] <= _cpi['preprocessing_samplingRange'][1])):
                        #Normalization Target Index Range
                        _klineTSIndexes = range(_cpi['preprocessing_normalizationIndex']-(_neuralNetwork['nKlines']-1), _cpi['preprocessing_normalizationIndex']+1)
                        #Kline Raw
                        _klines_raw = _klines['raw']
                        _p_max     = max([_klines_raw[_klineTimestamps[_klTSIndex]][KLINDEX_HIGHPRICE] for _klTSIndex in _klineTSIndexes])
                        _p_min     = min([_klines_raw[_klineTimestamps[_klTSIndex]][KLINDEX_LOWPRICE]  for _klTSIndex in _klineTSIndexes])
                        _p_range   = _p_max-_p_min
                        _vol_max   = max([_klines_raw[_klineTimestamps[_klTSIndex]][KLINDEX_VOLBASE]         for _klTSIndex in _klineTSIndexes])
                        _volTB_max = max([_klines_raw[_klineTimestamps[_klTSIndex]][KLINDEX_VOLBASETAKERBUY] for _klTSIndex in _klineTSIndexes])
                        #Sample Index
                        _sIndex = _cpi['preprocessing_normalizationIndex']-_cpi['preprocessing_samplingRange'][0]
                        for _relKlineIndex in range (0, _neuralNetwork['nKlines']):
                            _tTS = _klineTimestamps[_klineTSIndexes[0]+_relKlineIndex]
                            #Kline
                            _kline = _klines['raw'][_tTS]
                            _ds_sIndex    = _dataSet[_sIndex]
                            _ds_relEIndex = _relKlineIndex*6+1
                            if (_p_range != 0):
                                _ds_sIndex[_ds_relEIndex+0] = (_kline[KLINDEX_OPENPRICE] -_p_min)/_p_range
                                _ds_sIndex[_ds_relEIndex+1] = (_kline[KLINDEX_HIGHPRICE] -_p_min)/_p_range
                                _ds_sIndex[_ds_relEIndex+2] = (_kline[KLINDEX_LOWPRICE]  -_p_min)/_p_range
                                _ds_sIndex[_ds_relEIndex+3] = (_kline[KLINDEX_CLOSEPRICE]-_p_min)/_p_range
                            else:
                                _ds_sIndex[_ds_relEIndex+0] = 0.5
                                _ds_sIndex[_ds_relEIndex+1] = 0.5
                                _ds_sIndex[_ds_relEIndex+2] = 0.5
                                _ds_sIndex[_ds_relEIndex+3] = 0.5
                            if (_vol_max != 0): _ds_sIndex[_ds_relEIndex+4] = (_kline[KLINDEX_VOLBASE])/_vol_max
                            else:               _ds_sIndex[_ds_relEIndex+4] = 0.0
                            if (_volTB_max != 0): _ds_sIndex[_ds_relEIndex+5] = (_kline[KLINDEX_VOLBASETAKERBUY])/_volTB_max
                            else:                 _ds_sIndex[_ds_relEIndex+5] = 0.0
                        #---Index
                        _cpi['preprocessing_normalizationIndex'] += 1
                #[2-4]: Completion update
                if (True):
                    #New Completion
                    if   (_cpi['preprocessing_type'] == _PROCESS_PREPROCESSINGTYPE_LABELSEARCH):   _completion = _cpi['preprocessing_labelSearchIndex']                                           /_cpi['klines_length']                                                            *0.33+0.00
                    elif (_cpi['preprocessing_type'] == _PROCESS_PREPROCESSINGTYPE_LABELING):      _completion = (_cpi['preprocessing_labelingIndex']-_cpi['preprocessing_samplingRange'][0])     /(_cpi['preprocessing_samplingRange'][1]-_cpi['preprocessing_samplingRange'][0]+1)*0.33+0.33
                    elif (_cpi['preprocessing_type'] == _PROCESS_PREPROCESSINGTYPE_NORMALIZATION): _completion = (_cpi['preprocessing_normalizationIndex']-_cpi['preprocessing_samplingRange'][0])/(_cpi['preprocessing_samplingRange'][1]-_cpi['preprocessing_samplingRange'][0]+1)*0.34+0.66
                    #Completion time record & estimated time of completion computation
                    _t_current_ns = time.perf_counter_ns()
                    if (_cpi['completion_lastComputed_ns'] != None):
                        #Find the last completion rate
                        _t_elapsed_ns     = (_t_current_ns-_cpi['completion_lastComputed_ns'])
                        _completion_added = _completion-_neuralNetwork['completion']
                        _completion_rate  = _completion_added/_t_elapsed_ns
                        #Find average completion rate (exponential average)
                        if (_cpi['completion_avgRate'] == None): _cpi['completion_avgRate'] = _completion_rate
                        else:                                    _cpi['completion_avgRate'] = _completion_rate*_PROCESS_ETCCOMPUTE_KVALUE + _cpi['completion_avgRate']*(1-_PROCESS_ETCCOMPUTE_KVALUE)
                        #Find new completion estimated time of completion
                        if   (_cpi['preprocessing_type'] == _PROCESS_PREPROCESSINGTYPE_LABELSEARCH):   _completion_ETC_s = (0.33-_completion)/_cpi['completion_avgRate']/1e9
                        elif (_cpi['preprocessing_type'] == _PROCESS_PREPROCESSINGTYPE_LABELING):      _completion_ETC_s = (0.66-_completion)/_cpi['completion_avgRate']/1e9
                        elif (_cpi['preprocessing_type'] == _PROCESS_PREPROCESSINGTYPE_NORMALIZATION): _completion_ETC_s = (1.00-_completion)/_cpi['completion_avgRate']/1e9
                    else: _completion_ETC_s = None
                    _cpi['completion_lastComputed_ns'] = _t_current_ns
                    #Effective Update & Announcement
                    #---Neural Network
                    _neuralNetwork['completion']       = _completion
                    _neuralNetwork['completion_ETC_s'] = _completion_ETC_s
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', _process['neuralNetworkCode'], 'completion'),       prdContent = _neuralNetwork['completion'])
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', _process['neuralNetworkCode'], 'completion_ETC_s'), prdContent = _neuralNetwork['completion_ETC_s'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'COMPLETION', 'updatedContent': _process['neuralNetworkCode']}, farrHandler = None)
                    #---Process
                    _process['completion']       = _completion
                    _process['completion_ETC_s'] = _completion_ETC_s
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('PROCESSES', self.__neuralNetwork_currentProcessCode, 'completion'),       prdContent = _process['completion'])
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('PROCESSES', self.__neuralNetwork_currentProcessCode, 'completion_ETC_s'), prdContent = _process['completion_ETC_s'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onProcessUpdate', functionParams = {'updateType': 'COMPLETION', 'updatedContent': self.__neuralNetwork_currentProcessCode}, farrHandler = None)
                #[2-5]: If the preprocessing has ended, load the dataset into the network and update status
                if (True):
                    #[2-5-1]: Label Search -> Labeling
                    if (_cpi['preprocessing_type'] == _PROCESS_PREPROCESSINGTYPE_LABELSEARCH):
                        if (_cpi['preprocessing_labelSearchIndex'] == _cpi['klines_length']):
                            #First Swing
                            if (_neuralNetwork['nKlines']-1 < _cpi['preprocessing_swings'][1][0]): _firstLabelableIndex = _cpi['preprocessing_swings'][1][0]
                            else:                                                                  _firstLabelableIndex = _neuralNetwork['nKlines']-1
                            #Sampling Range Determination
                            _cpi['preprocessing_samplingRange']  = (_firstLabelableIndex, _cpi['preprocessing_swings'][-1][0]-1)
                            _cpi['preprocessing_nextSwingIndex'] = 0
                            while (_cpi['preprocessing_swings'][_cpi['preprocessing_nextSwingIndex']][0] < _cpi['preprocessing_samplingRange'][0]): _cpi['preprocessing_nextSwingIndex'] += 1
                            #Finally
                            _cpi['preprocessing_type']           = _PROCESS_PREPROCESSINGTYPE_LABELING
                            _cpi['preprocessing_labelingIndex']  = _cpi['preprocessing_samplingRange'][0]
                            _nSamples   = _cpi['preprocessing_samplingRange'][1]-_cpi['preprocessing_samplingRange'][0]+1
                            _sampleSize = _neuralNetwork['nKlines']*6+1
                            _cpi['dataSet'] = numpy.zeros(shape = (_nSamples, _sampleSize), dtype = _NUMPYDTYPE)
                            _cpi['completion_avgRate'] = None
                    #[2-5-2]: Labeling -> Normalization
                    elif (_cpi['preprocessing_type'] == _PROCESS_PREPROCESSINGTYPE_LABELING):
                        if (_cpi['preprocessing_labelingIndex'] == _cpi['preprocessing_samplingRange'][1]+1):
                            _cpi['preprocessing_type']               = _PROCESS_PREPROCESSINGTYPE_NORMALIZATION
                            _cpi['preprocessing_normalizationIndex'] = _cpi['preprocessing_samplingRange'][0]
                            _cpi['completion_avgRate'] = None

                    #[2-5-3]: Normalization End
                    elif (_cpi['preprocessing_type'] == _PROCESS_PREPROCESSINGTYPE_NORMALIZATION):
                        if (_cpi['preprocessing_normalizationIndex'] == _cpi['preprocessing_samplingRange'][1]+1):
                            #[2-5-3-1]: Dataset loading & network setup
                            _neuralNetwork['instance'].setLossFunction(lossFunctionDescription = _process['lossFunction'])
                            _cpi['dataSet_batchIndex'] = 0
                            if (_cpi['type'] == _PROCESS_TYPE_TRAINING):
                                _neuralNetwork['instance'].setOptimizer(optimizerDescription = _process['optimizer'], learningRate = _process['learningRate'])
                                _cpi['dataSet_numberOfBatches'] = _neuralNetwork['instance'].loadDataSet(dataSet = _dataSet, batch_size = _process['batchSize'], shuffle = True)
                                _neuralNetwork['instance'].setTrainMode()
                            elif (_cpi['type'] == _PROCESS_TYPE_PERFORMANCETEST): 
                                _cpi['dataSet_numberOfBatches'] = _neuralNetwork['instance'].loadDataSet(dataSet = _dataSet, batch_size = _process['batchSize'], shuffle = False)
                                _neuralNetwork['instance'].setEvaluationMode()
                            #[2-5-3-2]: Status Update
                            _cpi['status'] = _PROCESS_STATUS_GENERATING
                            _process['status'] = 'PROCESSING'
                            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('PROCESSES', self.__neuralNetwork_currentProcessCode, 'status'), prdContent = _process['status'])
                            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onProcessUpdate', functionParams = {'updateType': 'STATUS', 'updatedContent': self.__neuralNetwork_currentProcessCode}, farrHandler = None)
                            #[2-5-3-3]: Completion Initialization
                            _cpi['completion_avgRate']         = None
                            _cpi['completion_lastComputed_ns'] = None
                            #---Neural Network
                            _neuralNetwork['completion']       = 0
                            _neuralNetwork['completion_ETC_s'] = None
                            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', _process['neuralNetworkCode'], 'completion'),       prdContent = _neuralNetwork['completion'])
                            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', _process['neuralNetworkCode'], 'completion_ETC_s'), prdContent = _neuralNetwork['completion_ETC_s'])
                            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'COMPLETION', 'updatedContent': _process['neuralNetworkCode']}, farrHandler = None)
                            #---Process
                            _process['completion']       = 0
                            _process['completion_ETC_s'] = None
                            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('PROCESSES', self.__neuralNetwork_currentProcessCode, 'completion'),       prdContent = _process['completion'])
                            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('PROCESSES', self.__neuralNetwork_currentProcessCode, 'completion_ETC_s'), prdContent = _process['completion_ETC_s'])
                            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onProcessUpdate', functionParams = {'updateType': 'COMPLETION', 'updatedContent': self.__neuralNetwork_currentProcessCode}, farrHandler = None)
            #[3]: Generating
            elif (_cpi['status'] == _PROCESS_STATUS_GENERATING):
                #[3-1]: Process Type Determination
                if (_cpi['type'] == _PROCESS_TYPE_TRAINING):
                    if (_cpi['training_complete'] == True):           _actionType = _PROCESS_ACTIONTYPE_PERFORMANCETEST
                    else:                                             _actionType = _PROCESS_ACTIONTYPE_TRAINING
                elif (_cpi['type'] == _PROCESS_TYPE_PERFORMANCETEST): _actionType = _PROCESS_ACTIONTYPE_PERFORMANCETEST
                #[3-2]: Process Loop
                _t_beg_ns = time.perf_counter_ns()
                while ((time.perf_counter_ns()-_t_beg_ns <= _PROCESS_TIMEOUT_NS) and (_cpi['dataSet_batchIndex'] < _cpi['dataSet_numberOfBatches'])):
                    if (_actionType == _PROCESS_ACTIONTYPE_TRAINING):
                        _neuralNetwork['instance'].trainOnBatch()
                    elif (_actionType == _PROCESS_ACTIONTYPE_PERFORMANCETEST): 
                        _loss = _neuralNetwork['instance'].evaluateBatch()
                        _cpi['result']['loss_sum'] += _loss
                        _cpi['result']['loss_n']   += 1
                    _cpi['dataSet_batchIndex'] += 1
                #[3-3]: Completion update
                if (True):
                    #New Completion
                    if   (_cpi['type'] == _PROCESS_TYPE_TRAINING):        _completion = (_cpi['dataSet_batchIndex']/_cpi['dataSet_numberOfBatches']+_cpi['training_epochIndex'])/(_process['nEpochs']+1)
                    elif (_cpi['type'] == _PROCESS_TYPE_PERFORMANCETEST): _completion = _cpi['dataSet_batchIndex']/_cpi['dataSet_numberOfBatches']
                    #Completion time record & estimated time of completion computation
                    _t_current_ns = time.perf_counter_ns()
                    if (_cpi['completion_lastComputed_ns'] != None):
                        #Find the last completion rate
                        _t_elapsed_ns     = (_t_current_ns-_cpi['completion_lastComputed_ns'])
                        _completion_added = _completion-_neuralNetwork['completion']
                        _completion_rate  = _completion_added/_t_elapsed_ns
                        #Find average completion rate (exponential average)
                        if (_cpi['completion_avgRate'] == None): _cpi['completion_avgRate'] = _completion_rate
                        else:                                    _cpi['completion_avgRate'] = _completion_rate*_PROCESS_ETCCOMPUTE_KVALUE + _cpi['completion_avgRate']*(1-_PROCESS_ETCCOMPUTE_KVALUE)
                        #Find new completion estimated time of completion
                        _completion_ETC_s = (1-_completion)/_cpi['completion_avgRate']/1e9
                    else: _completion_ETC_s = None
                    _cpi['completion_lastComputed_ns'] = _t_current_ns
                    #Effective Update & Announcement
                    #---Neural Network
                    _neuralNetwork['completion']       = _completion
                    _neuralNetwork['completion_ETC_s'] = _completion_ETC_s
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', _process['neuralNetworkCode'], 'completion'),       prdContent = _neuralNetwork['completion'])
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', _process['neuralNetworkCode'], 'completion_ETC_s'), prdContent = _neuralNetwork['completion_ETC_s'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'COMPLETION', 'updatedContent': _process['neuralNetworkCode']}, farrHandler = None)
                    #---Process
                    _process['completion']       = _completion
                    _process['completion_ETC_s'] = _completion_ETC_s
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('PROCESSES', self.__neuralNetwork_currentProcessCode, 'completion'),       prdContent = _process['completion'])
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('PROCESSES', self.__neuralNetwork_currentProcessCode, 'completion_ETC_s'), prdContent = _process['completion_ETC_s'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onProcessUpdate', functionParams = {'updateType': 'COMPLETION', 'updatedContent': self.__neuralNetwork_currentProcessCode}, farrHandler = None)
                #[3-4]: Finalization Check
                if (True):
                    _finalize = False
                    if (_cpi['type'] == _PROCESS_TYPE_TRAINING):
                        if (_cpi['dataSet_batchIndex'] == _cpi['dataSet_numberOfBatches']): 
                            if (_cpi['training_complete'] == True): _finalize = True
                            else:
                                _cpi['dataSet_batchIndex'] = 0
                                _neuralNetwork['instance'].resetIterator()
                                _cpi['training_epochIndex'] += 1
                                if (_cpi['training_epochIndex'] == _process['nEpochs']): 
                                    _cpi['training_complete'] = True
                                    _cpi['dataSet_numberOfBatches'] = _neuralNetwork['instance'].updateBatchSize(batch_size = 1, shuffle = False)
                                    _neuralNetwork['instance'].setEvaluationMode()
                                    _cpi['completion_avgRate'] = None
                    elif (_cpi['type'] == _PROCESS_TYPE_PERFORMANCETEST):
                        if (_cpi['dataSet_batchIndex'] == _cpi['dataSet_numberOfBatches']): _finalize = True
                #[3-5]: If processing has completely ended, finalized it by saving the log, setting the neural network status, and initializing the processing target
                if (_finalize == True):
                    #[1]: Unload Input Data Set
                    _neuralNetwork['instance'].unloadDataSet()
                    #[2]: Save log & updated connections data
                    #---[2-1]: Training
                    if (_cpi['type'] == _PROCESS_TYPE_TRAINING):
                        _lossAverage = _cpi['result']['loss_sum']/_cpi['result']['loss_n']
                        _trainingLog = {'startTime':   _cpi['startTime'],
                                        'endTime':     time.time(),
                                        'target':      _process['targetCurrencySymbol'],
                                        'targetRange': _process['targetRange'],
                                        'lossAverage': _lossAverage}
                        _neuralNetwork['trainingLogs'].append(_trainingLog)
                        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'addNeuralNetworkTrainingLog', functionParams = {'neuralNetworkCode': _process['neuralNetworkCode'], 'trainingLog': _trainingLog}, farrHandler = None)
                        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'TRAININGLOG', 'updatedContent': (_process['neuralNetworkCode'], _trainingLog)}, farrHandler = None)
                        #New connections data save request & announcement to subscribers
                        _connections = _neuralNetwork['instance'].getConnections()
                        _neuralNetwork['connections'] = _connections
                        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'updateNeuralNetworkConnectionData', functionParams = {'neuralNetworkCode': _process['neuralNetworkCode'], 'newNeuralNetworkConnectionData': _connections}, farrHandler = None)
                    #---[2-2]: Performance Test
                    elif (_cpi['type'] == _PROCESS_TYPE_PERFORMANCETEST):
                        _lossAverage = _cpi['result']['loss_sum']/_cpi['result']['loss_n']
                        _performanceTestLog = {'startTime':   _cpi['startTime'],
                                               'endTime':     time.time(),
                                               'target':      _process['targetCurrencySymbol'],
                                               'targetRange': _process['targetRange'],
                                               'lossAverage': _lossAverage}
                        _neuralNetwork['performanceTestLogs'].append(_performanceTestLog)
                        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'addNeuralNetworkPerformanceTestLog', functionParams = {'neuralNetworkCode': _process['neuralNetworkCode'], 'performanceTestLog': _performanceTestLog}, farrHandler = None)
                        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'PERFORMANCETESTLOG', 'updatedContent': (_process['neuralNetworkCode'], _performanceTestLog)}, farrHandler = None)
                    #[3]: Update Status
                    #---Neural Network
                    _moreProcesses = False
                    for _pCode in self.__neuralNetwork_processes:
                        if ((_pCode != self.__neuralNetwork_currentProcessCode) and (self.__neuralNetwork_processes[_pCode]['neuralNetworkCode'] == _process['neuralNetworkCode'])): _moreProcesses = True; break
                    if (_moreProcesses == True): _neuralNetwork['status'] = 'QUEUED'
                    else:                        _neuralNetwork['status'] = 'STANDBY'
                    _neuralNetwork['completion']       = None
                    _neuralNetwork['completion_ETC_s'] = None
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', _process['neuralNetworkCode'], 'status'),           prdContent = _neuralNetwork['status'])
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', _process['neuralNetworkCode'], 'completion'),       prdContent = _neuralNetwork['completion'])
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', _process['neuralNetworkCode'], 'completion_etc_s'), prdContent = _neuralNetwork['completion_ETC_s'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'STATUS',     'updatedContent': _process['neuralNetworkCode']}, farrHandler = None)
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'COMPLETION', 'updatedContent': _process['neuralNetworkCode']}, farrHandler = None)
                    #---Process
                    del self.__neuralNetwork_processes[self.__neuralNetwork_currentProcessCode]
                    self.ipcA.sendPRDREMOVE(targetProcess = 'GUI', prdAddress = ('PROCESSES', self.__neuralNetwork_currentProcessCode))
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onProcessUpdate', functionParams = {'updateType': 'REMOVED', 'updatedContent': self.__neuralNetwork_currentProcessCode}, farrHandler = None)
                    #[4]: Reset current process data
                    self.__neuralNetwork_currentProcessCode         = None
                    self.__neuralNetwork_currentProcessInternalData = None
    
    def __initializeNeuralNetwork(self, neuralNetworkCode, initialization, controlKey):
        if (neuralNetworkCode in self.__neuralNetworks):
            _neuralNetwork = self.__neuralNetworks[neuralNetworkCode]
            #Check Control Key
            _controlKeyTest = bcrypt.checkpw(controlKey.encode(encoding = "utf-8"), _neuralNetwork['hashedControlKey'])
            if (_controlKeyTest == True):
                #Initialize neural network params, save, and announce
                _neuralNetwork = self.__neuralNetworks[neuralNetworkCode]
                _initResult = _neuralNetwork['instance'].initializeParameters(initialization = initialization)
                if (_initResult == True):
                    _connections = _neuralNetwork['instance'].getConnections()
                    _neuralNetwork['connections'] = _connections
                    self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'updateNeuralNetworkConnectionData', functionParams = {'neuralNetworkCode': neuralNetworkCode, 'newNeuralNetworkConnectionData': _connections}, farrHandler = None)
                    #If there exists an on-going process for this neural network, remove it
                    _processCodes_thisNN = [_pCode for _pCode in self.__neuralNetwork_processes if (self.__neuralNetwork_processes[_pCode]['neuralNetworkCode'] == neuralNetworkCode)]
                    for _pCode in _processCodes_thisNN:
                        if (_pCode == self.__neuralNetwork_currentProcessCode): 
                            del self.__neuralNetwork_processes[_pCode]
                            self.__neuralNetwork_currentProcessCode         = None
                            self.__neuralNetwork_currentProcessInternalData = None
                            self.ipcA.sendPRDREMOVE(targetProcess = 'GUI', prdAddress = ('PROCESSES', _pCode))
                            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onProcessUpdate', functionParams = {'updateType': 'REMOVED', 'updatedContent': _pCode}, farrHandler = None)
                    return {'result': True, 'message': "Neural Network '{:s}' Initialization Successful!".format(neuralNetworkCode)}
                else: return {'result': False, 'message': "Neural Network '{:s}' Initialization Failed. '{:s}'".format(neuralNetworkCode, _initResult)}
            else: return     {'result': False, 'message': "Neural Network '{:s}' Initialization Failed. 'Incorrect Control Key'".format(neuralNetworkCode)}
        else:  return        {'result': False, 'message': "Neural Network '{:s}' Initialization Failed. 'The Neural Network Code Does Not Exist'".format(neuralNetworkCode)}

    def __generateNeuralNetwork(self, neuralNetworkCode, neuralNetworkType, initialization, nKlines, hiddenLayers, outputLayer, controlKey):
        #[1]: Neural Network Name
        if (neuralNetworkCode in self.__neuralNetworks): return {'result': False, 'message': "Neural Network '{:s}' Generation Failed. 'The Neural Network Code Already Exists'".format(neuralNetworkCode)}
        #[2]: Neural Network Type
        if (neuralNetworkType not in _NEURALNETWORKTYPES): return {'result': False, 'message': "Neural Network '{:s}' Generation Failed. Type '{:s}' Does Not Exist".format(neuralNetworkCode, neuralNetworkType)}
        #[3]: Neural Network Parameters
        if (neuralNetworkType == 'MLP'):
            _paramTest = True
        if (_paramTest == False): return {'result': False, 'message': "Neural Network '{:s}' Generation Failed. Check Neural Network Parameters".format(neuralNetworkCode)}
        #[4]: Control Key
        try: _hashedControlKey = bcrypt.hashpw(password=controlKey.encode(encoding = "utf-8"), salt=bcrypt.gensalt())
        except Exception as e: return {'result': False, 'message': "Neural Network '{:s}' Generation Failed. Could Not Hash The Control Key. '{:s}'".format(neuralNetworkCode, str(e))}
        #[5]: Neural Network Generation
        try:
            if (neuralNetworkType == 'MLP'): _neuralNetworkInstance = atmEta_NeuralNetworks.neuralNetwork_MLP(nKlines = nKlines, hiddenLayers = hiddenLayers, outputLayer = outputLayer, initialization = initialization)
            _generationTime      = int(time.time())
            _trainingLogs        = list()
            _performanceTestLogs = list()
            _status              = 'STANDBY'
            _completion          = None
            _completion_ETC_s    = None
            _connections         = _neuralNetworkInstance.getConnections()
            _neuralNetwork = {'instance':            _neuralNetworkInstance,
                              'type':                neuralNetworkType,
                              'nKlines':             nKlines,
                              'hiddenLayers':        hiddenLayers,
                              'outputLayer':         outputLayer,
                              'hashedControlKey':    _hashedControlKey,
                              'generationTime':      _generationTime,
                              'connections':         _connections,
                              'trainingLogs':        _trainingLogs,
                              'performanceTestLogs': _performanceTestLogs,
                              'status':              _status,
                              'completion':          _completion,
                              'completion_ETC_s':    _completion_ETC_s}
            self.__neuralNetworks[neuralNetworkCode] = _neuralNetwork
            _neuralNetwork_gui = {'type':                neuralNetworkType,
                                  'nKlines':             nKlines,
                                  'hiddenLayers':        hiddenLayers,
                                  'outputLayer':         outputLayer,
                                  'generationTime':      _generationTime,
                                  'trainingLogs':        _trainingLogs,
                                  'performanceTestLogs': _performanceTestLogs,
                                  'status':              _status,
                                  'completion':          _completion,
                                  'completion_ETC_s':    _completion_ETC_s}
            _neuralNetwork_db = {'type':             neuralNetworkType,
                                 'nKlines':          nKlines,
                                 'hiddenLayers':     hiddenLayers,
                                 'outputLayer':      outputLayer,
                                 'generationTime':   _generationTime,
                                 'hashedControlKey': _hashedControlKey,
                                 'connections':      _connections}
            self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'addNeuralNetworkDescription', functionParams = {'neuralNetworkCode': neuralNetworkCode, 'neuralNetworkDescription': _neuralNetwork_db}, farrHandler = None)
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', neuralNetworkCode), prdContent = _neuralNetwork_gui)
            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'ADDED', 'updatedContent': neuralNetworkCode}, farrHandler = None)
            return {'result': True, 'message': "Neural Network '{:s}' Generation Successful!".format(neuralNetworkCode)}
        except Exception as e: return {'result': False, 'message': "Neural Network '{:s}' Generation Failed Due To An Unexpected Error. '{:s}'".format(neuralNetworkCode, str(e))}

    def __importNeuralNetwork(self, neuralNetworkCode, neuralNetworkDescription):
        _neuralNetworkType   = neuralNetworkDescription['neuralNetworkType']
        _nKlines             = neuralNetworkDescription['nKlines']
        _hiddenLayers        = neuralNetworkDescription['hiddenLayers']
        _outputLayer         = neuralNetworkDescription['outputLayer']
        _generationTime      = neuralNetworkDescription['generationTime']
        _hashedControlKey    = neuralNetworkDescription['hashedControlKey']
        _connections         = neuralNetworkDescription['neuralNetworkConnectionData']
        _trainingLogs        = neuralNetworkDescription['trainingLogs']
        _performanceTestLogs = neuralNetworkDescription['performanceTestLogs']
        _status              = 'STANDBY'
        _completion          = None
        _completion_ETC_s    = None
        if (_neuralNetworkType == 'MLP'): _neuralNetworkInstance = atmEta_NeuralNetworks.neuralNetwork_MLP(nKlines = _nKlines, hiddenLayers = _hiddenLayers, outputLayer = _outputLayer)
        _neuralNetworkInstance.importConnectionsData(connections = _connections)
        _neuralNetwork = {'instance':            _neuralNetworkInstance,
                          'type':                _neuralNetworkType,
                          'nKlines':             _nKlines,
                          'hiddenLayers':        _hiddenLayers,
                          'outputLayer':         _outputLayer,
                          'hashedControlKey':    _hashedControlKey,
                          'generationTime':      _generationTime,
                          'connections':         _connections,
                          'trainingLogs':        _trainingLogs,
                          'performanceTestLogs': _performanceTestLogs,
                          'status':              _status,
                          'completion':          _completion,
                          'completion_ETC_s':    _completion_ETC_s}
        self.__neuralNetworks[neuralNetworkCode] = _neuralNetwork
        _neuralNetwork_gui = {'type':                _neuralNetworkType,
                              'nKlines':             _nKlines,
                              'hiddenLayers':        _hiddenLayers,
                              'outputLayer':         _outputLayer,
                              'generationTime':      _generationTime,
                              'trainingLogs':        _trainingLogs,
                              'performanceTestLogs': _performanceTestLogs,
                              'status':              _status,
                              'completion':          _completion,
                              'completion_ETC_s':    _completion_ETC_s}
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', neuralNetworkCode), prdContent = _neuralNetwork_gui)
        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'ADDED', 'updatedContent': neuralNetworkCode}, farrHandler = None)

    def __removeNeuralNetwork(self, neuralNetworkCode, controlKey):
        if (neuralNetworkCode in self.__neuralNetworks):
            _neuralNetwork = self.__neuralNetworks[neuralNetworkCode]
            #Check Control Key
            _controlKeyTest = bcrypt.checkpw(controlKey.encode(encoding = "utf-8"), _neuralNetwork['hashedControlKey'])
            if (_controlKeyTest == True):
                #Remove the local neural network data and related processes
                del self.__neuralNetworks[neuralNetworkCode]
                _processCodes_thisNN = [_pCode for _pCode in self.__neuralNetwork_processes if (self.__neuralNetwork_processes[_pCode]['neuralNetworkCode'] == neuralNetworkCode)]
                for _pCode in _processCodes_thisNN: 
                    del self.__neuralNetwork_processes[_pCode]
                    if (_pCode == self.__neuralNetwork_currentProcessCode): 
                        self.__neuralNetwork_currentProcessCode         = None
                        self.__neuralNetwork_currentProcessInternalData = None
                    else: self.__neuralNetwork_processQueues.remove(_pCode)
                #Send neural network data removal request to DATAMANAGER
                self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'removeNeuralNetworkDescription', functionParams = {'neuralNetworkCode': neuralNetworkCode}, farrHandler = None)
                #Announce the removals
                self.ipcA.sendPRDREMOVE(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', neuralNetworkCode))
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'REMOVED', 'updatedContent': neuralNetworkCode}, farrHandler = None)
                for _pCode in _processCodes_thisNN:
                    self.ipcA.sendPRDREMOVE(targetProcess = 'GUI', prdAddress = ('PROCESSES', _pCode))
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onProcessUpdate', functionParams = {'updateType': 'REMOVED', 'updatedContent': _pCode}, farrHandler = None)
                return {'result': True, 'message': "Neural Network '{:s}' Removal Successful!".format(neuralNetworkCode)}
            else: return {'result': False, 'message': "Neural Network '{:s}' Removal Failed. 'Incorrect Control Key'".format(neuralNetworkCode)}
        else:     return {'result': False, 'message': "Neural Network '{:s}' Removal Failed. 'The Neural Network Code Does Not Exist'".format(neuralNetworkCode)}

    def __runTraining(self, neuralNetworkCode, controlKey, targetCurrencySymbol, targetRange, optimizer, lossFunction, swingRange, nEpochs, batchSize, learningRate):
        if (neuralNetworkCode in self.__neuralNetworks): 
            _neuralNetwork = self.__neuralNetworks[neuralNetworkCode]
            #Check Control Key
            _controlKeyTest = bcrypt.checkpw(controlKey.encode(encoding = "utf-8"), _neuralNetwork['hashedControlKey'])
            if (_controlKeyTest == True):
                if (self.__checkCurrencyDataRange(targetCurrencySymbol = targetCurrencySymbol, targetRange = targetRange)):
                    #Neural Network Status Update
                    if (_neuralNetwork['status'] == 'STANDBY'): 
                        _neuralNetwork['status'] = 'QUEUED'
                        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', neuralNetworkCode, 'status'), prdContent = _neuralNetwork['status'])
                        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'STATUS', 'updatedContent': neuralNetworkCode}, farrHandler = None)
                    #Process Formatting & Queue Appending
                    _processCode = 'NNP_{:d}'.format(time.perf_counter_ns())
                    _process = {'neuralNetworkCode':             neuralNetworkCode,
                                'processType':                   'TRAINING',
                                'targetCurrencySymbol':          targetCurrencySymbol,
                                'targetRange':                   targetRange,
                                'optimizer':                     optimizer,
                                'lossFunction':                  lossFunction,
                                'nEpochs':                       nEpochs,
                                'batchSize':                     batchSize,
                                'learningRate':                  learningRate,
                                'swingRange':                    swingRange,
                                'status':                        'QUEUED',
                                'completion':                    None,
                                'completion_ETC_s':              None}
                    self.__neuralNetwork_processes[_processCode] = _process
                    self.__neuralNetwork_processQueues.append(_processCode)
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('PROCESSES', _processCode), prdContent = self.__neuralNetwork_processes[_processCode])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onProcessUpdate', functionParams = {'updateType': 'ADDED', 'updatedContent': _processCode}, farrHandler = None)
                    return {'result': True, 'message': "Neural Network '{:s}' Training Queue Added!".format(neuralNetworkCode)}
                else: return {'result': False, 'message': "Neural Network '{:s}' Training Queue Add Failed. 'Check Target Symbol and Available Data Ranges. (Given: ('{:s}', {:s}))'".format(neuralNetworkCode, targetCurrencySymbol, str(targetRange))}
            else: return {'result': False, 'message': "Neural Network '{:s}' Training Queue Add Failed. 'Incorrect Control Key'".format(neuralNetworkCode)}
        else:     return {'result': False, 'message': "Neural Network '{:s}' Training Queue Add Failed. 'The Neural Network Code Does Not Exist'".format(neuralNetworkCode)}

    def __addPerformanceTest(self, neuralNetworkCode, targetCurrencySymbol, targetRange, lossFunction, swingRange):
        if (neuralNetworkCode in self.__neuralNetworks):
            _neuralNetwork = self.__neuralNetworks[neuralNetworkCode]
            if (self.__checkCurrencyDataRange(targetCurrencySymbol = targetCurrencySymbol, targetRange = targetRange)):
                if (_neuralNetwork['status'] == 'STANDBY'): 
                    _neuralNetwork['status'] = 'QUEUED'
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', neuralNetworkCode, 'status'), prdContent = _neuralNetwork['status'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'STATUS', 'updatedContent': neuralNetworkCode}, farrHandler = None)
                _processCode = 'NNP_{:d}'.format(time.perf_counter_ns())
                _process = {'neuralNetworkCode':    neuralNetworkCode,
                            'processType':          'PERFORMANCETEST',
                            'targetCurrencySymbol': targetCurrencySymbol,
                            'targetRange':          targetRange,
                            'lossFunction':         lossFunction,
                            'batchSize':            1,
                            'swingRange':           swingRange,
                            'status':               'QUEUED',
                            'completion':           None,
                            'completion_ETC_s':     None}
                self.__neuralNetwork_processes[_processCode] = _process
                self.__neuralNetwork_processQueues.append(_processCode)
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('PROCESSES', _processCode), prdContent = self.__neuralNetwork_processes[_processCode])
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onProcessUpdate', functionParams = {'updateType': 'ADDED', 'updatedContent': _processCode}, farrHandler = None)
                return {'result': True, 'message': "Neural Network '{:s}' Performance Test Added!".format(neuralNetworkCode)}
            else: return {'result': False, 'message': "Neural Network '{:s}' Performance Test Add Failed. 'Check Target Symbol and Available Data Ranges. (Given: '{:s}', {:s})'".format(neuralNetworkCode, targetCurrencySymbol, str(targetRange))}
        else: return {'result': False, 'message': "Neural Network '{:s}' Performance Test Add Failed. 'The Neural Network Code Does Not Exist'".format(neuralNetworkCode)}

    def __checkCurrencyDataRange(self, targetCurrencySymbol, targetRange):
        _testPassed = False
        if (targetCurrencySymbol in self.__currencies):
            _currency            = self.__currencies[targetCurrencySymbol]
            _availableDataRanges = _currency['kline_availableRanges']
            if (targetRange[0] < targetRange[1]):
                for _availableDataRange in _availableDataRanges:
                    if ((_availableDataRange[0] <= targetRange[0]) and (targetRange[1] <= _availableDataRange[1])): _testPassed = True; break
        return _testPassed

    def __removeProcess(self, processCode, controlKey):
        if (processCode in self.__neuralNetwork_processes):
            _process           = self.__neuralNetwork_processes[processCode]
            _neuralNetworkCode = _process['neuralNetworkCode']
            _neuralNetwork     = self.__neuralNetworks[_neuralNetworkCode]
            #Check Control Key
            _controlKeyTest = bcrypt.checkpw(controlKey.encode(encoding = "utf-8"), _neuralNetwork['hashedControlKey'])
            if (_controlKeyTest == True):
                #Remove the process data
                del self.__neuralNetwork_processes[processCode]
                if (processCode == self.__neuralNetwork_currentProcessCode):
                    self.__neuralNetwork_currentProcessCode         = None
                    self.__neuralNetwork_currentProcessInternalData = None
                    _neuralNetwork['instance'].unloadDataSet()
                    _neuralNetwork['instance'].importConnectionsData(connections = _neuralNetwork['connections'])
                else: self.__neuralNetwork_processQueues.remove(processCode)
                #Announce the process removal
                self.ipcA.sendPRDREMOVE(targetProcess = 'GUI', prdAddress = ('PROCESSES', processCode))
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onProcessUpdate', functionParams = {'updateType': 'REMOVED', 'updatedContent': processCode}, farrHandler = None)
                #Check if there are more processes for this neural network and update status and completion accordingly
                _moreProcesses = False
                for _pCode in self.__neuralNetwork_processes:
                    if (self.__neuralNetwork_processes[_pCode]['neuralNetworkCode'] == _neuralNetworkCode): _moreProcesses = True; break
                if (_moreProcesses == True): _neuralNetwork['status'] = 'QUEUED'
                else:                        _neuralNetwork['status'] = 'STANDBY'
                _neuralNetwork['completion']       = None
                _neuralNetwork['completion_ETC_s'] = None
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', _neuralNetworkCode, 'status'),           prdContent = _neuralNetwork['status'])
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', _neuralNetworkCode, 'completion'),       prdContent = _neuralNetwork['completion'])
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('NEURALNETWORKS', _neuralNetworkCode, 'completion_etc_s'), prdContent = _neuralNetwork['completion_ETC_s'])
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'STATUS',     'updatedContent': _neuralNetworkCode}, farrHandler = None)
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onNeuralNetworkUpdate', functionParams = {'updateType': 'COMPLETION', 'updatedContent': _neuralNetworkCode}, farrHandler = None)
                #Return result
                return {'result': True, 'message': "Process '{:s}' Removal Successful!".format(processCode)}
            else: return {'result': False, 'message': "Process '{:s}' Removal Failed. 'Incorrect Control Key'".format(processCode)}
        else:     return {'result': False, 'message': "Process '{:s}' Removal Failed. 'The Process Does Not Exist'".format(processCode)}
    #Manager Internal Functions END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #FAR Handlers -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<DATAMANAGER>
    def __far_onCurrenciesUpdate(self, requester, updatedContents):
        if (requester == 'DATAMANAGER'):
            for updatedContent in updatedContents:
                symbol    = updatedContent['symbol']
                contentID = updatedContent['id']
                self.__currencies[symbol] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol))
    def __farr_onNeuralNetworkDescriptionLoadRequestResponse(self, responder, requestID, functionResult):
        if (responder == 'DATAMANAGER'):
            neuralNetworkDescriptions = functionResult
            for _neuralNetworkCode in neuralNetworkDescriptions: self.__importNeuralNetwork(neuralNetworkCode = _neuralNetworkCode, neuralNetworkDescription = neuralNetworkDescriptions[_neuralNetworkCode])
    def __farr_onKlineFetchRequestResponse(self, responder, requestID, functionResult):
        if (responder == 'DATAMANAGER'):
            if ((self.__neuralNetwork_currentProcessInternalData != None) and (requestID == self.__neuralNetwork_currentProcessInternalData['klineFetchRequestRID'])):
                _rr_result = functionResult['result']
                _rr_klines = functionResult['klines']
                #[1]: Successful Kline Fetch
                if (_rr_result == 'SKF'):
                    #Save the received klines
                    _klines_raw       = self.__neuralNetwork_currentProcessInternalData['klines']['raw']
                    _klines_rawStatus = self.__neuralNetwork_currentProcessInternalData['klines']['raw_status']
                    for _index, _kline in enumerate(_rr_klines): 
                        _t_open = _kline[0]
                        _klines_raw[_t_open]       = _kline[:11]
                        _klines_rawStatus[_t_open] = {'index': _index, 'p_max': _kline[KLINDEX_HIGHPRICE], 'vol_max': _kline[KLINDEX_VOLBASE]}
                        _t_open_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = _t_open, mrktReg = None, nTicks = -1)
                        if (_t_open_prev in _klines_rawStatus): 
                            _p_max_prev   = _klines_rawStatus[_t_open_prev]['p_max']
                            _vol_max_prev = _klines_rawStatus[_t_open_prev]['vol_max']
                            if (_kline[KLINDEX_HIGHPRICE] < _p_max_prev): _klines_rawStatus[_t_open]['p_max']   = _p_max_prev
                            if (_kline[KLINDEX_VOLBASE] < _vol_max_prev): _klines_rawStatus[_t_open]['vol_max'] = _vol_max_prev
                    #Move to the next phase of the processing
                    self.__neuralNetwork_currentProcessInternalData['status'] = _PROCESS_STATUS_KLINESRECEIVED
                #[2]: Unexpected Error Occurrance
                elif (_rr_result == 'UEO'): pass
    #<GUI>
    def __far_initializeNeuralNetwork(self, requester, requestID, neuralNetworkCode, initialization, controlKey):
        if (requester == 'GUI'): 
            _result = self.__initializeNeuralNetwork(neuralNetworkCode = neuralNetworkCode, initialization = initialization, controlKey = controlKey)
            return {'neuralNetworkCode': neuralNetworkCode, 'responseOn': 'INITIALIZENEURALNETWORKREQUEST', 'result': _result['result'], 'message': _result['message']}
    def __far_generateNeuralNetwork(self, requester, requestID, neuralNetworkCode, neuralNetworkType, initialization, nKlines, hiddenLayers, outputLayer, controlKey):
        if (requester == 'GUI'): 
            _result = self.__generateNeuralNetwork(neuralNetworkCode  = neuralNetworkCode, 
                                                   neuralNetworkType  = neuralNetworkType, 
                                                   initialization     = initialization, 
                                                   nKlines            = nKlines,
                                                   hiddenLayers       = hiddenLayers, 
                                                   outputLayer        = outputLayer, 
                                                   controlKey         = controlKey)
            return {'neuralNetworkCode': neuralNetworkCode, 'responseOn': 'GENERATENEURALNETWORKREQUEST', 'result': _result['result'], 'message': _result['message']}
    def __far_removeNeuralNetwork(self, requester, requestID, neuralNetworkCode, controlKey):
        if (requester == 'GUI'): 
            _result = self.__removeNeuralNetwork(neuralNetworkCode = neuralNetworkCode, controlKey = controlKey)
            return {'neuralNetworkCode': neuralNetworkCode, 'responseOn': 'REMOVENEURALNETWORKREQUEST', 'result': _result['result'], 'message': _result['message']}
    def __far_runTraining(self, requester, requestID, neuralNetworkCode, controlKey, targetCurrencySymbol, targetRange, optimizer, lossFunction, swingRange, nEpochs, batchSize, learningRate):
        if (requester == 'GUI'): 
            _result = self.__runTraining(neuralNetworkCode    = neuralNetworkCode, 
                                         controlKey           = controlKey, 
                                         targetCurrencySymbol = targetCurrencySymbol, 
                                         targetRange          = targetRange, 
                                         optimizer            = optimizer, 
                                         lossFunction         = lossFunction,
                                         swingRange           = swingRange,
                                         nEpochs              = nEpochs, 
                                         batchSize            = batchSize, 
                                         learningRate         = learningRate)
            return {'neuralNetworkCode': neuralNetworkCode, 'responseOn': 'RUNTRAININGREQUEST', 'result': _result['result'], 'message': _result['message']}
    def __far_runPerformanceTest(self, requester, requestID, neuralNetworkCode, targetCurrencySymbol, targetRange, lossFunction, swingRange):
        if (requester == 'GUI'): 
            _result = self.__addPerformanceTest(neuralNetworkCode    = neuralNetworkCode, 
                                                targetCurrencySymbol = targetCurrencySymbol, 
                                                targetRange          = targetRange, 
                                                lossFunction         = lossFunction,
                                                swingRange           = swingRange)
            return {'neuralNetworkCode': neuralNetworkCode, 'responseOn': 'RUNPERFORMANCETESTREQUEST', 'result': _result['result'], 'message': _result['message']}
    def __far_removeProcess(self, requester, requestID, processCode, controlKey):
        if (requester == 'GUI'):
            _result = self.__removeProcess(processCode = processCode, controlKey = controlKey)
            return {'processCode': processCode, 'responseOn': 'REMOVEPROCESSREQUEST', 'result': _result['result'], 'message': _result['message']}
    #<COMMON>
    def __far_getNeuralNetworkConnections(self, requester, requestID, neuralNetworkCode):
        if (neuralNetworkCode in self.__neuralNetworks): 
            _neuralNetwork = self.__neuralNetworks[neuralNetworkCode]
            _nKlines      = _neuralNetwork['nKlines']
            _hiddenLayers = [_hiddenLayer.copy() for _hiddenLayer in _neuralNetwork['hiddenLayers']]
            _outputLayer  = _neuralNetwork['outputLayer'].copy()
            _connections  = _neuralNetwork['connections'].copy()
            return {'neuralNetworkCode': neuralNetworkCode,
                    'nKlines':      _nKlines,
                    'hiddenLayers': _hiddenLayers,
                    'outputLayer':  _outputLayer,
                    'connections':  _connections}
        else: return None
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------