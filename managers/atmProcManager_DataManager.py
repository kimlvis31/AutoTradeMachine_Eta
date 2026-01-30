#ATM Modules
import atmEta_IPC
import atmEta_Auxillaries

#Python Modules
import time
import os
import termcolor
import sqlite3
import json
import traceback
from datetime import datetime, timedelta, timezone

#Constants
_KLINE_STREAMEDSAVEINTERVAL_NS = 1e9

_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

class procManager_DataManager:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA):
        print(termcolor.colored("   Initializing", 'green'), termcolor.colored("DATAMANAGER", 'light_blue'), termcolor.colored("-----------------------------------------------------------------------------------------------------------------------", 'green'))
        #IPC Assistance
        self.ipcA = ipcA

        #Paths
        self.path_project = path_project
        self.path_dbFolder = os.path.join(self.path_project, 'data', 'db')
        #---Check if the db folder exists and make one if not
        if (os.path.isdir(self.path_dbFolder) == False): os.mkdir(self.path_dbFolder)
        
        #Read DataManager Configuration File
        self.__config_DataManager = {'print_Update':  True,
                                     'print_Warning': True,
                                     'print_Error':   True}
        self.__readDataManagerConfig()

        #Local Data Control
        self.__klines_streamed              = dict()
        self.__klines_streamed_lastSaved_ns = 0
        self.__klines_fetched_requestQueue   = set()
        self.__klines_fetched_activeRequests = dict()

        #sqlite3 Connections & Cursors
        self.__sql_klines_connection         = sqlite3.connect(os.path.join(self.path_dbFolder, 'atmEta_klines.db'));         self.__sql_klines_cursor         = self.__sql_klines_connection.cursor()
        self.__sql_simulations_connection    = sqlite3.connect(os.path.join(self.path_dbFolder, 'atmEta_simulations.db'));    self.__sql_simulations_cursor    = self.__sql_simulations_connection.cursor()
        self.__sql_accounts_connection       = sqlite3.connect(os.path.join(self.path_dbFolder, 'atmEta_accounts.db'));       self.__sql_accounts_cursor       = self.__sql_accounts_connection.cursor()
        self.__sql_neuralNetworks_connection = sqlite3.connect(os.path.join(self.path_dbFolder, 'atmEta_neuralNetworks.db')); self.__sql_neuralNetworks_cursor = self.__sql_neuralNetworks_connection.cursor()
        print(" * SQLite3 Connections Established")

        #Database Contents Read
        if (True): #klines.db
            self.__klineDataInfo           = dict()
            self.__currencySymbolsByID     = dict()
            self.__currencyInfoSubscribers = dict()
            #Table Contents Check
            self.__sql_klines_cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
            tablesInDB = [fetchedElement[0] for fetchedElement in self.__sql_klines_cursor.fetchall()]
            for tableName in ('klines', 'summary'):
                if (tableName not in tablesInDB):
                    if   (tableName == 'klines'):  self.__sql_klines_cursor.execute("CREATE TABLE klines  (id INTEGER PRIMARY KEY, t_open INTEGER, t_close INTEGER, p_open REAL, p_high REAL, p_low REAL, p_close REAL, nTrades INTEGER, v REAL, q REAL, v_tb REAL, q_tb REAL, kType INTEGER)")
                    elif (tableName == 'summary'): self.__sql_klines_cursor.execute("CREATE TABLE summary (id INTEGER PRIMARY KEY, symbol TEXT, precisions TEXT, baseAsset TEXT, quoteAsset TEXT, kline_firstOpenTS INTEGER, kline_availableRanges TEXT)")
            #Currency Data Identification & Read
            self.__sql_klines_cursor.execute("SELECT * FROM summary")
            dbTableData_coinID = self.__sql_klines_cursor.fetchall()
            for summaryRow in dbTableData_coinID:
                currencyID = summaryRow[0]
                symbol     = summaryRow[1]
                precisions = summaryRow[2]
                baseAsset  = summaryRow[3]
                quoteAsset = summaryRow[4]
                mrktRegTS  = summaryRow[5]
                dataRanges = summaryRow[6]
                if (precisions != None): precisions = json.loads(precisions)
                if (dataRanges != None): dataRanges = json.loads(dataRanges)
                self.__klineDataInfo[symbol]           = {'currencyID': currencyID, 'precisions': precisions, 'baseAsset': baseAsset, 'quoteAsset': quoteAsset, 'kline_firstOpenTS': mrktRegTS, 'kline_availableRanges': dataRanges, 'info_server': None}
                self.__currencySymbolsByID[currencyID] = symbol
                self.__currencyInfoSubscribers[symbol] = set(['GUI', 'TRADEMANAGER', 'SIMULATIONMANAGER', 'NEURALNETWORKMANAGER'])
                self.__klines_streamed[symbol]         = {'klines': list(), 'range': None, 'firstOpenTS': None, 'streamConnectionTime': None}
            print(" * {:d} currency data detected!".format(len(self.__klineDataInfo)))
            #Announce the currency info
            for processName in ('GUI', 'TRADEMANAGER', 'SIMULATIONMANAGER', 'NEURALNETWORKMANAGER'): self.ipcA.sendPRDEDIT(targetProcess = processName, prdAddress = 'CURRENCIES', prdContent = self.__klineDataInfo)
        if (True): #accounts.db
            self.__accountDescriptions = dict()
            self.__accountLocalIDsByID = dict()
            #Table Check
            self.__sql_accounts_cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
            tablesInDB = [fetchedElement[0] for fetchedElement in self.__sql_accounts_cursor.fetchall()]
            if ('accountDescriptions' not in tablesInDB): self.__sql_accounts_cursor.execute("""CREATE TABLE accountDescriptions (id                       INTEGER PRIMARY KEY,
                                                                                                                                  localID                  TEXT, 
                                                                                                                                  accountType              TEXT,
                                                                                                                                  buid                     INTEGER, 
                                                                                                                                  assetsTableName          TEXT,
                                                                                                                                  positionsTableName       TEXT,
                                                                                                                                  tradeLogsTableName       TEXT,
                                                                                                                                  periodicReportsTableName TEXT,
                                                                                                                                  hashedPassword           TEXT)""")
        if (True): #simulations.db
            self.__simulationDescriptions = dict()
            self.__simulationCodesByID    = dict()
            #Table Check
            self.__sql_simulations_cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
            tablesInDB = [fetchedElement[0] for fetchedElement in self.__sql_simulations_cursor.fetchall()]
            if ('simulationDescriptions' not in tablesInDB): self.__sql_simulations_cursor.execute("""CREATE TABLE simulationDescriptions (id INTEGER PRIMARY KEY, 
                                                                                                                                           simulationCode                          TEXT, 
                                                                                                                                           simulationRange                         TEXT,
                                                                                                                                           analysisExport                          TEXT,
                                                                                                                                           creationTime                            REAL,
                                                                                                                                           simulationSummary                       TEXT,
                                                                                                                                           currencyAnalysisConfigurationsTableName TEXT,
                                                                                                                                           tradeConfigurationsTableName            TEXT,
                                                                                                                                           assetsTableName                         TEXT,
                                                                                                                                           positionsTableName                      TEXT,
                                                                                                                                           tradeLogsTableName                      TEXT,
                                                                                                                                           periodicReportsTableName                TEXT
                                                                                                                                           )""")
            #Currency Data Identification & Read
            self.__sql_simulations_cursor.execute("SELECT * FROM simulationDescriptions")
            dbTableData_simulationDescriptions = self.__sql_simulations_cursor.fetchall()
            for summaryRow in dbTableData_simulationDescriptions:
                #Read SimulationDescription Line
                dbID                                    = summaryRow[0]
                simulationCode                          = summaryRow[1]
                simulationRange                         = json.loads(summaryRow[2])
                analysisExport                          = json.loads(summaryRow[3])
                creationTime                            = summaryRow[4]
                simulationSummary                       = json.loads(summaryRow[5])
                currencyAnalysisConfigurationsTableName = summaryRow[6]
                tradeConfigurationsTableName            = summaryRow[7]
                assetsTableName                         = summaryRow[8]
                positionsTableName                      = summaryRow[9]
                tradeLogsTableName                      = summaryRow[10]
                periodicReportsTableName                = summaryRow[11]
                if (currencyAnalysisConfigurationsTableName not in tablesInDB): currencyAnalysisConfigurationsTableName = None
                if (tradeConfigurationsTableName            not in tablesInDB): tradeConfigurationsTableName            = None
                if (assetsTableName                         not in tablesInDB): assetsTableName                         = None
                if (positionsTableName                      not in tablesInDB): positionsTableName                      = None
                if (tradeLogsTableName                      not in tablesInDB): tradeLogsTableName                      = None
                if (periodicReportsTableName                not in tablesInDB): periodicReportsTableName                = None
                #Read CurrencyAnalysisConfigurations
                _currencyAnalysisConfigurations = dict()
                if (currencyAnalysisConfigurationsTableName != None):
                    self.__sql_simulations_cursor.execute("SELECT * FROM {:s}".format(currencyAnalysisConfigurationsTableName))
                    _fetchedDBData = self.__sql_simulations_cursor.fetchall()
                    for _cactRow in _fetchedDBData:
                        _configurationCode = _cactRow[1]
                        _configuration     = json.loads(_cactRow[2])
                        _currencyAnalysisConfigurations[_configurationCode] = _configuration
                #Read TradeConfigurations
                _tradeConfigurations = dict()
                if (tradeConfigurationsTableName != None):
                    self.__sql_simulations_cursor.execute("SELECT * FROM {:s}".format(tradeConfigurationsTableName))
                    _fetchedDBData = self.__sql_simulations_cursor.fetchall()
                    for _tctRow in _fetchedDBData:
                        _configurationCode = _tctRow[1]
                        _configuration     = json.loads(_tctRow[2])
                        _tradeConfigurations[_configurationCode] = _configuration
                #Read Assets
                _assets = dict()
                if (assetsTableName != None):
                    self.__sql_simulations_cursor.execute("SELECT * FROM {:s}".format(assetsTableName))
                    _fetchedDBData = self.__sql_simulations_cursor.fetchall()
                    for _atRow in _fetchedDBData:
                        _assetName                      = _atRow[1]
                        _initialWalletBalance           = _atRow[2]
                        _allocatableBalance             = _atRow[3]
                        _allocatedBalance               = _atRow[4]
                        _allocationRatio                = _atRow[5]
                        _assumedRatio                   = _atRow[6]
                        _weightedAssumedRatio           = _atRow[7]
                        _maxAllocatedBalance            = json.loads(_atRow[8])
                        _positionSymbols                = set(json.loads(_atRow[9]))
                        _positionSymbols_prioritySorted = json.loads(_atRow[10])
                        _assets[_assetName] = {'initialWalletBalance':            _initialWalletBalance,
                                               'allocatableBalance':              _allocatableBalance,
                                               'allocatedBalance':                _allocatedBalance,
                                               'allocationRatio':                 _allocationRatio,
                                               'assumedRatio':                    _assumedRatio,
                                               'weightedAssumedRatio':            _weightedAssumedRatio,
                                               'maxAllocatedBalance':             _maxAllocatedBalance,
                                               '_positionSymbols':                _positionSymbols,
                                               '_positionSymbols_prioritySorted': _positionSymbols_prioritySorted}
                #Read Positions
                _positions = dict()
                if (positionsTableName != None):
                    self.__sql_simulations_cursor.execute("SELECT * FROM {:s}".format(positionsTableName))
                    _fetchedDBData = self.__sql_simulations_cursor.fetchall()
                    for _ptRow in _fetchedDBData:
                        _positionSymbol                    = _ptRow[1]
                        _quoteAsset                        = json.loads(_ptRow[2])
                        _precisions                        = json.loads(_ptRow[3])
                        _dataRange                         = json.loads(_ptRow[4])
                        _currencyAnalysisConfigurationCode = _ptRow[5]
                        _tradeConfigurationCode            = _ptRow[6]
                        _isolated                          = (_ptRow[7] == 1)
                        _leverage                          = _ptRow[8]
                        _priority                          = _ptRow[9]
                        _assumedRatio                      = _ptRow[10]
                        _weightedAssumedRatio              = _ptRow[11]
                        _allocatedBalance                  = _ptRow[12]
                        _maxAllocatedBalance               = json.loads(_ptRow[13])
                        _firstKline                        = _ptRow[14]
                        _positions[_positionSymbol] = {'quoteAsset':                        _quoteAsset, 
                                                       'precisions':                        _precisions, 
                                                       'dataRange':                         _dataRange, 
                                                       'currencyAnalysisConfigurationCode': _currencyAnalysisConfigurationCode, 
                                                       'tradeConfigurationCode':            _tradeConfigurationCode, 
                                                       'isolated':                          _isolated, 
                                                       'leverage':                          _leverage, 
                                                       'priority':                          _priority, 
                                                       'assumedRatio':                      _assumedRatio, 
                                                       'weightedAssumedRatio':              _weightedAssumedRatio, 
                                                       'allocatedBalance':                  _allocatedBalance, 
                                                       'maxAllocatedBalance':               _maxAllocatedBalance, 
                                                       'firstKline':                        _firstKline, 
                                                       'tradable':                          True}
                self.__simulationDescriptions[simulationCode] = {'simulationRange':                simulationRange,
                                                                 'currencyAnalysisConfigurations': _currencyAnalysisConfigurations,
                                                                 'tradeConfigurations':            _tradeConfigurations,
                                                                 'analysisExport':                 analysisExport,
                                                                 'assets':                         _assets,
                                                                 'positions':                      _positions,
                                                                 'creationTime':                   creationTime,
                                                                 'simulationSummary':              simulationSummary,
                                                                 'currencyAnalysisConfigurationsTableName': currencyAnalysisConfigurationsTableName,
                                                                 'tradeConfigurationsTableName':            tradeConfigurationsTableName,
                                                                 'assetsTableName':                         assetsTableName,
                                                                 'positionsTableName':                      positionsTableName,
                                                                 'tradeLogsTableName':                      tradeLogsTableName,
                                                                 'periodicReportsTableName':                periodicReportsTableName}
                self.__simulationCodesByID[dbID] = simulationCode
            #Announce the currency info
            self.ipcA.sendPRDEDIT(targetProcess = 'SIMULATIONMANAGER', prdAddress = 'SIMULATIONS', prdContent = self.__simulationDescriptions)
        if (True): #neuralNetworks.db
            self.__neuralNetworkDescriptions = dict()
            self.__neuralNetworCodesByID     = dict()
            #Table Check
            self.__sql_neuralNetworks_cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
            tablesInDB = [fetchedElement[0] for fetchedElement in self.__sql_neuralNetworks_cursor.fetchall()]
            if ('neuralNetworkDescriptions' not in tablesInDB): self.__sql_neuralNetworks_cursor.execute("""CREATE TABLE neuralNetworkDescriptions (id                             INTEGER PRIMARY KEY,
                                                                                                                                                    neuralNetworkCode              TEXT,
                                                                                                                                                    neuralNetworkType              TEXT,
                                                                                                                                                    nKlines                        INT,
                                                                                                                                                    hiddenLayers                   TEXT,
                                                                                                                                                    outputLayer                    TEXT,
                                                                                                                                                    generationTime                 INTEGER,
                                                                                                                                                    hashedControlKey               TEXT,
                                                                                                                                                    networkConnectionDataTableName TEXT,
                                                                                                                                                    trainingLogsTableName          TEXT,
                                                                                                                                                    performanceTestLogsTableName   TEXT)""")

        #Request Control
        self.__klineFetchRequestQueues                = list()
        self.__accountDataEditRequestQueues           = list()
        self.__accountTradeLogAppendRequestQueues     = list()
        self.__accountPeriodicReportUpdateRequestQueues = list()
        self.__neuralNetworkConnectionDataUpdateRequestQueues     = list()
        self.__neuralNetworkTrainingLogAppendRequestQueues        = list()
        self.__neuralNetworkPerformanceTestLogAppendRequestQueues = list()

        #Initial Data Share
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CONFIGURATION', prdContent = self.__config_DataManager.copy())

        #FAR Registration
        #---BINANCEAPI
        self.ipcA.addFARHandler('registerCurrency',      self.__far_registerCurrency,      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onCurrencyInfoUpdate',  self.__far_onCurrencyInfoUpdate,  executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onKlineStreamReceival', self.__far_onKlineStreamReceival, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---SIMULATOR
        self.ipcA.addFARHandler('saveSimulationData', self.__far_saveSimulationData, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---SIMULATIONMANAGER&SIMULATOR
        self.ipcA.addFARHandler('removeSimulationData', self.__far_removeSimulationData, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---TRADEMANAGER
        self.ipcA.addFARHandler('loadAccountDescriptions',     self.__far_loadAccountDescriptions,     executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('addAccountDescription',       self.__far_addAccountDescription,       executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('removeAccountDescription',    self.__far_removeAccountDescription,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('editAccountData',             self.__far_editAccountData,             executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('addAccountTradeLog',          self.__far_addAccountTradeLog,          executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('updateAccountPeriodicReport', self.__far_updateAccountPeriodicReport, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---NEURALNETWORKMANAGER
        self.ipcA.addFARHandler('loadNeuralNetworkDescriptions',      self.__far_loadNeuralNetworkDescriptions,      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('addNeuralNetworkDescription',        self.__far_addNeuralNetworkDescription,        executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('removeNeuralNetworkDescription',     self.__far_removeNeuralNetworkDescription,     executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('updateNeuralNetworkConnectionData',  self.__far_updateNeuralNetworkConnectionData,  executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('addNeuralNetworkTrainingLog',        self.__far_addNeuralNetworkTrainigLog,         executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('addNeuralNetworkPerformanceTestLog', self.__far_addNeuralNetworkPerformanceTestLog, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---GUI
        self.ipcA.addFARHandler('updateConfiguration',            self.__far_updateConfiguration,            executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('fetchSimulationTradeLogs',       self.__far_fetchSimulationTradeLogs,       executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('fetchSimulationPeriodicReports', self.__far_fetchSimulationPeriodicReports, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('fetchAccountTradeLog',           self.__far_fetchAccountTradeLog,           executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('fetchAccountPeriodicReports',    self.__far_fetchAccountPeriodicReports,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---#COMMON#
        self.ipcA.addFARHandler('fetchKlines',                        self.__far_fetchKlines,                        executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        self.ipcA.addFARHandler('registerCurrecnyInfoSubscription',   self.__far_registerCurrecnyInfoSubscription,   executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        self.ipcA.addFARHandler('unregisterCurrecnyInfoSubscription', self.__far_unregisterCurrecnyInfoSubscription, executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)

        #Process Control
        self.__processLoopContinue = True

        print(termcolor.colored("   DATAMANAGER", 'light_blue'), termcolor.colored("Initialization Complete! -----------------------------------------------------------------------------------------------------------", 'green'))
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    
    
    #Manager Process Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        while (self.__processLoopContinue == True):
            #Process any exsiting FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()

            #Save any exsiting streamed klines
            self.__saveStreamedKlines()
            #Send any needed kline fetch requests
            self.__sendKlineFetchRequests()
            #Process a kline fetch request queue
            self.__processKlineFetchRequestQueue()
            #Process any account data edit request queues
            self.__processAccountDataEditRequestQueues()
            #Process any neural network data update request queues
            self.__processNeuralNetworkDataEditRequestQueues()

            #Loop Sleep
            time.sleep(0.001)
    def terminate(self, requester):
        self.__processLoopContinue = False
    #Manager Process Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Internal Functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #---Process Configuration
    def __readDataManagerConfig(self):
        #[1]: Configuration File Read
        try:
            config_dir = os.path.join(self.path_project, 'configs', 'dmConfig.config')
            with open(config_dir, 'r') as f:
                config_loaded = json.load(f)
        except: 
            config_loaded = dict()

        #[2]: Contents Verification
        #---[2-1]: Print_Update
        print_update = config_loaded.get('print_Update', True)
        if not isinstance(print_update, bool): print_update = True
        #---[2-2]: Print_Warning
        print_warning = config_loaded.get('print_Warning', True)
        if not isinstance(print_warning, bool): print_warning = True
        #---[2-3]: Print_Error
        print_error = config_loaded.get('print_Error', True)
        if not isinstance(print_error, bool): print_error = True

        #[3]: Update and save the configuration
        self.__config_DataManager = {'print_Update':  print_update,
                                     'print_Warning': print_warning,
                                     'print_Error':   print_error}
        self.__saveDataManagerConfig()
    def __saveDataManagerConfig(self):
        #[1]: Reformat config for save
        config = self.__config_DataManager
        config_toSave = {'print_Update':  config['print_Update'],
                         'print_Warning': config['print_Warning'],
                         'print_Error':   config['print_Error']}

        #[2]: Save the reformatted configuration file
        config_dir = os.path.join(self.path_project, 'configs', 'dmConfig.config')
        try:
            with open(config_dir, 'w') as f:
                json.dump(config_toSave, f, indent=4)
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Save Data Manager Configuration. User Attention Strongly Advised"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')
    
    #---Klines
    def __saveStreamedKlines(self):
        t_current_ns = time.perf_counter_ns()
        if (_KLINE_STREAMEDSAVEINTERVAL_NS < t_current_ns-self.__klines_streamed_lastSaved_ns):
            klinesCollection = list()
            collectedSymbols = list()
            for symbol in self.__klines_streamed:
                if (self.__klines_streamed[symbol]['range'] != None):
                    #Check data ranges overlap
                    if (self.__klineDataInfo[symbol]['kline_availableRanges'] == None): noOverlap = True
                    else:
                        noOverlap = True
                        for availableDataRange in self.__klineDataInfo[symbol]['kline_availableRanges']:
                            drClassification = self.__dataRange_getClassification(availableDataRange, self.__klines_streamed[symbol]['range'])
                            if not((drClassification == 0b0000) or (drClassification == 0b1111)): noOverlap = False; break
                    #If the data range test has passed, re-format the klines for collective saving and update the available data ranges and the control variables
                    if (noOverlap == True):
                        #Klines Collection
                        klinesCollection += [(self.__klineDataInfo[symbol]['currencyID']*1e10+streamedKline[0],)+streamedKline for streamedKline in self.__klines_streamed[symbol]['klines']]
                        collectedSymbols.append(symbol)
                        #Data Ranges Edit
                        if (self.__klineDataInfo[symbol]['kline_availableRanges'] == None): self.__klineDataInfo[symbol]['kline_availableRanges'] = [self.__klines_streamed[symbol]['range'],]
                        else:
                            availableRanges_newCombined = self.__klineDataInfo[symbol]['kline_availableRanges'].copy()
                            availableRanges_newCombined.append(self.__klines_streamed[symbol]['range'])
                            availableRanges_newCombined.sort(key = lambda x: x[0])
                            availableRanges_merged = list()
                            for dataRange in availableRanges_newCombined:
                                if (len(availableRanges_merged) == 0): availableRanges_merged.append(dataRange)
                                else:
                                    if (availableRanges_merged[-1][1]+1 == dataRange[0]): availableRanges_merged[-1] = (availableRanges_merged[-1][0], dataRange[1])
                                    else:                                                 availableRanges_merged.append(dataRange)
                            self.__klineDataInfo[symbol]['kline_availableRanges'] = availableRanges_merged
                        #Control variable reset
                        self.__klines_streamed[symbol]['klines'].clear()
                        self.__klines_streamed[symbol]['range'] = None
                        #Currency info update on PRD-GUI via PRD and notification by FAR
                        for processName in self.__currencyInfoSubscribers[symbol]:
                            self.ipcA.sendPRDEDIT(targetProcess = processName, prdAddress = ('CURRENCIES', symbol, 'kline_availableRanges'), prdContent = self.__klineDataInfo[symbol]['kline_availableRanges'])
                            self.ipcA.sendFAR(targetProcess = processName, functionID = 'onCurrenciesUpdate', functionParams = {'updatedContents': [{'symbol': symbol, 'id': ('kline_availableRanges',)}]}, farrHandler = None)
                    #If the data range test has not passed, dispose the corresponding streamed klines buffer and perform data re-evaluation
                    else: self.__logger(message = f"An overlap detected between the available data ranges and the streamed klines for {symbol}. The corresponding klines will be disposed", logType = 'Warning', color = 'light_red')
            #If there exists any collected kline, update the .db files
            nKlinesCollection = len(klinesCollection)
            if (0 < nKlinesCollection):
                summaryUpdates = [(json.dumps(self.__klineDataInfo[symbol]['kline_availableRanges']), self.__klineDataInfo[symbol]['currencyID']) for symbol in collectedSymbols]
                #Save new data to the .db file
                self.__sql_klines_cursor.executemany("INSERT INTO klines (id, t_open, t_close, p_open, p_high, p_low, p_close, nTrades, v, q, v_tb, q_tb, kType) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", klinesCollection)
                self.__sql_klines_cursor.executemany("UPDATE summary SET kline_availableRanges = ? WHERE id = ?", summaryUpdates)
                self.__sql_klines_connection.commit()
                #Print comment
                self.__logger(message = f"Successfully saved {nKlinesCollection} streamed klines for {len(collectedSymbols)} symbols", logType = 'Update', color = 'light_green')
            #Update the last save time
            self.__klines_streamed_lastSaved_ns = t_current_ns
    def __sendKlineFetchRequests(self):
        for symbol in self.__klines_fetched_requestQueue:
            #Calculate fetch target ranges
            availableDataRanges = self.__klineDataInfo[symbol]['kline_availableRanges']
            if (availableDataRanges is None): 
                if (self.__klineDataInfo[symbol]['kline_firstOpenTS'] < self.__klines_streamed[symbol]['firstOpenTS']): fetchTargetRanges = [[self.__klineDataInfo[symbol]['kline_firstOpenTS'], self.__klines_streamed[symbol]['firstOpenTS']-1]]
                else:                                                                                                   fetchTargetRanges = list()
            else:
                fetchTargetRanges = list()
                if (self.__klineDataInfo[symbol]['kline_firstOpenTS'] < availableDataRanges[0][0]): fetchTargetRanges.append([self.__klineDataInfo[symbol]['kline_firstOpenTS'], availableDataRanges[0][0]-1])
                for dataRangeIndex in range (len(availableDataRanges)-1):
                    dataRange_this = availableDataRanges[dataRangeIndex]
                    dataRange_next = availableDataRanges[dataRangeIndex+1]
                    fetchTargetRanges.append([dataRange_this[1]+1, dataRange_next[0]-1])
                if (availableDataRanges[-1][1]+1 < self.__klines_streamed[symbol]['firstOpenTS']): fetchTargetRanges.append([availableDataRanges[-1][1]+1, self.__klines_streamed[symbol]['firstOpenTS']-1])
            #If there exists any fetch target ranges, send fetch request to BINANCEAPI
            if (0 < len(fetchTargetRanges)):
                dispatchResult = self.ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                                                   functionID     = 'fetchKlines', 
                                                   functionParams = {'symbol':                      symbol, 
                                                                     'marketRegistrationTimestamp': self.__klineDataInfo[symbol]['kline_firstOpenTS'], 
                                                                     'streamConnectionTime':        self.__klines_streamed[symbol]['streamConnectionTime'], 
                                                                     'fetchTargetRanges':           fetchTargetRanges}, 
                                                   farrHandler = self.__farr_getKlineFetchRequestResult)
                if (dispatchResult != None):
                    dispatchRID = dispatchResult
                    self.__klines_fetched_activeRequests[dispatchRID] = {'symbol': symbol, 'fetchTargetRanges': fetchTargetRanges}
        #Clear the queue
        self.__klines_fetched_requestQueue.clear()
    def __processKlineFetchRequestQueue(self):
        if (0 < len(self.__klineFetchRequestQueues)):
            queue = self.__klineFetchRequestQueues.pop(0)
            queue_requester      = queue['requester']
            queue_requestID      = queue['requestID']
            queue_currencySymbol = queue['currencySymbol']
            queue_fetchRange     = queue['fetchRange']
            #Currency symbol check
            if (queue_currencySymbol not in self.__klineDataInfo): self.ipcA.sendFARR(targetProcess = queue_requester, functionResult = {'result': 'SNF', 'klines': None}, requestID = queue_requestID, complete = True); return #SNF: Symbol Not Found
            #Data Availability Check
            dataAvailable = False
            for dataRange in self.__klineDataInfo[queue_currencySymbol]['kline_availableRanges']:
                classification = 0
                classification += 0b1000*(0 <= dataRange[0]-queue_fetchRange[0])
                classification += 0b0100*(0 <= dataRange[0]-queue_fetchRange[1])
                classification += 0b0010*(0 <  dataRange[1]-queue_fetchRange[0])
                classification += 0b0001*(0 <  dataRange[1]-queue_fetchRange[1])
                if ((classification == 0b0010) or (classification == 0b1010) or (classification == 0b1011) or (classification == 0b0011)): dataAvailable = True; break
            if (dataAvailable == False): self.ipcA.sendFARR(targetProcess = queue_requester, functionResult = {'result': 'DNA', 'klines': None}, requestID = queue_requestID, complete = True); return #DNA: Data Not Available
            #Kline Fetch from .db
            try:
                klines = None
                currencyID = self.__klineDataInfo[queue_currencySymbol]['currencyID']
                self.__sql_klines_cursor.execute('SELECT * FROM klines WHERE ? <= id AND id <= ?', (currencyID*1e10+queue_fetchRange[0], currencyID*1e10+queue_fetchRange[1]))
                klines = [kline_db[1:] for kline_db in self.__sql_klines_cursor.fetchall()]
                self.ipcA.sendFARR(targetProcess = queue_requester, functionResult = {'result': 'SKF', 'klines': klines, 'fetchRange': queue['fetchRange']}, requestID = queue_requestID, complete = True) #SKF: Successful Klines Fetch
            except Exception as e:
                self.__logger(message = f"An unexpected error occurred while attempting to fetch klines from .db for {queue_currencySymbol}@{str(queue_fetchRange)} upon the request of {queue_requester}\n * {str(e)}", logType = 'Error', color = 'red')
                self.ipcA.sendFARR(targetProcess = queue_requester, functionResult = {'result': 'UEO', 'klines': None}, requestID = queue_requestID, complete = True) #UEO: Unexpected Error Occurred
                return
    #---Account Data
    def __createAccountDataTable(self, localID, tableType):
        #[1]: Account Assets Table
        if tableType == 'ASSETS':
            tableName = f"aat_{localID}"
            self.__sql_accounts_cursor.execute(f"""CREATE TABLE {tableName} (id                 INTEGER PRIMARY KEY,
                                                                             asset              TEXT,
                                                                             crossWalletBalance REAL,
                                                                             allocationRatio    REAL
                                                                             )""")
        #[2]: Acocunt Positions Table
        elif tableType == 'POSITIONS':
            tableName = f"apt_{localID}"
            self.__sql_accounts_cursor.execute(f"""CREATE TABLE {tableName} (id                     INTEGER PRIMARY KEY,
                                                                             symbol                 TEXT, 
                                                                             quoteAsset             TEXT, 
                                                                             precisions             TEXT, 
                                                                             tradeStatus            INTEGER, 
                                                                             reduceOnly             INTEGER, 
                                                                             currencyAnalysisCode   TEXT,
                                                                             tradeConfigurationCode TEXT,
                                                                             tradeControlTracker    TEXT,
                                                                             isolatedWalletBalance  REAL,
                                                                             quantity               REAL,
                                                                             entryPrice             REAL,
                                                                             leverage               INTEGER,
                                                                             isolated               INTEGER,
                                                                             assumedRatio           REAL,
                                                                             priority               INTEGER,
                                                                             maxAllocatedBalance    REAL,
                                                                             abruptClearingRecords  TEXT
                                                                             )""")
        #[3]: Account Trade Logs Table
        elif tableType == 'TRADELOGS':
            tableName  = f"atlt_{localID}" #Account Trade Logs Table
            self.__sql_accounts_cursor.execute(f"""CREATE TABLE {tableName} (id       INTEGER PRIMARY KEY,
                                                                             tradeLog TEXT
                                                                             )""")
        #[4]: Account Periodic Reports Table
        elif tableType == 'PERIODICREPORTS':
            tableName  = f"aprt_{localID}" #Account Periodic Reports Table
            self.__sql_accounts_cursor.execute(f"""CREATE TABLE {tableName} (timestamp      INTEGER,
                                                                             periodicReport TEXT
                                                                             )""")
        #[5]: Table Name Return
        return tableName
    def __processAccountDataEditRequestQueues(self):
        #[1]: Instances
        sqlCursor     = self.__sql_accounts_cursor
        sqlConnection = self.__sql_accounts_connection
        ads           = self.__accountDescriptions
        queues_ader   = self.__accountDataEditRequestQueues
        queues_tlar   = self.__accountTradeLogAppendRequestQueues
        queues_prur   = self.__accountPeriodicReportUpdateRequestQueues

        #[2]: Commit Flag
        needCommit = False

        #[3]: Account Data Edit Requests
        if queues_ader:
            while queues_ader:
                #[3-1]: Queue Pop
                address, newValue = queues_ader.pop(0)
                localID = address[0]

                #[3-2]: Account Check
                if localID not in ads: continue
                ad = ads[localID]

                #[3-3]: Asset Edit
                if address[1] == 'assets': 
                    sqlCursor.execute(f"UPDATE {ad['assetsTableName']} SET {address[3]} = ? WHERE id = ?", 
                                      (newValue, ad['assets_dbID'][address[2]]))

                #[3-4]: Position Edit
                elif address[1] == 'positions':
                    #[3-4-1]: New Position
                    if address[3] == '#NEW#':
                        #[3-4-1-1]: Position dbID issuance
                        positions_dbIDs = set(position_dbID for position_dbID in ad['positions_dbID'].values())
                        position_dbID   = 0
                        while position_dbID in positions_dbIDs: position_dbID += 1

                        #[3-4-1-2]: Position Data Formatting
                        if   newValue['isolated'] == True:  isolated = 1
                        elif newValue['isolated'] == False: isolated = 0
                        elif newValue['isolated'] == None:  isolated = None
                        positionData_formatted = (position_dbID,
                                                  address[2],
                                                  newValue['quoteAsset'],
                                                  json.dumps(newValue['precisions']),
                                                  int(newValue['tradeStatus']),
                                                  int(newValue['reduceOnly']),
                                                  newValue['currencyAnalysisCode'],
                                                  newValue['tradeConfigurationCode'],
                                                  json.dumps(newValue['tradeControlTracker']),
                                                  newValue['isolatedWalletBalance'],
                                                  newValue['quantity'],
                                                  newValue['entryPrice'],
                                                  newValue['leverage'],
                                                  isolated,
                                                  newValue['assumedRatio'],
                                                  newValue['priority'],
                                                  newValue['maxAllocatedBalance'],
                                                  json.dumps(newValue['abruptClearingRecords']))
                        
                        #[3-4-1-3]: Position Data Insertion
                        sqlCursor.execute(f"""INSERT INTO {ad['positionsTableName']} (id,
                                                                                      symbol, 
                                                                                      quoteAsset, 
                                                                                      precisions, 
                                                                                      tradeStatus, 
                                                                                      reduceOnly,
                                                                                      currencyAnalysisCode,
                                                                                      tradeConfigurationCode,
                                                                                      tradeControlTracker,
                                                                                      isolatedWalletBalance,
                                                                                      quantity,
                                                                                      entryPrice,
                                                                                      leverage,
                                                                                      isolated,
                                                                                      assumedRatio,
                                                                                      priority,
                                                                                      maxAllocatedBalance,
                                                                                      abruptClearingRecords)
                                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                                          positionData_formatted)
                        #[3-4-1-4]: Positions dbID tracker update
                        ad['positions_dbID'][address[2]] = _position_dbID

                    #[3-4-2]: Trade Control Tracker Update
                    elif address[3] == 'tradeControlTracker':   
                        sqlCursor.execute(f"UPDATE {ad['positionsTableName']} SET {address[3]} = ? WHERE id = ?", 
                                          (json.dumps(newValue), ad['positions_dbID'][address[2]]))

                    #[3-4-3]: Abrupt Clearing Records Update
                    elif address[3] == 'abruptClearingRecords': 
                        sqlCursor.execute(f"UPDATE {ad['positionsTableName']} SET {address[3]} = ? WHERE id = ?", 
                                          (json.dumps(newValue), ad['positions_dbID'][address[2]]))

                    #[3-4-4]: General
                    else:
                        sqlCursor.execute(f"UPDATE {ad['positionsTableName']} SET {address[3]} = ? WHERE id = ?", 
                                          (newValue, ad['positions_dbID'][address[2]]))
                    
                #[3-5]: Account Edit
                else: 
                    sqlCursor.execute(f"UPDATE accountDescriptions SET {address[1]} = ? WHERE id = ?", 
                                      (newValue, ad['dbID']))
            
            #[3-6]: Commit Flag Raise
            needCommit = True

        #[4]: Account Trade Log Append Requests
        if queues_tlar:
            while queues_tlar:
                #[4-1]: Queue Pop
                localID, tradeLog = queues_tlar.pop(0)

                #[4-2]: Account Check
                if localID not in ads: continue
                ad = ads[localID]

                #[4-3]: DB Update
                sqlCursor.execute(f"INSERT INTO {ad['tradeLogsTableName']} (id, tradeLog) VALUES (?, ?)", 
                                  (ad['nTradeLog'], json.dumps(tradeLog)))

                #[4-4]: Trade Logs Counter Update
                ad['nTradeLog'] += 1

            #[4-5]: Commit Flag Raise
            needCommit = True

        #[5]: Account Periodic Report Update Requests
        if queues_prur:
            while queues_prur:
                #[5-1]: Queue Pop
                localID, timestamp, periodicReport = queues_prur.pop(0)

                #[5-2]: Account Check
                if localID not in ads: continue
                ad = ads[localID]

                #[5-3]: Report Verification & DB Update
                lastReportTS = ad['lastReportTS']
                #---[5-3-1]: Timestamp Future
                if (lastReportTS is None) or (lastReportTS < timestamp): 
                    sqlCursor.execute(f"INSERT INTO {ad['periodicReportsTableName']} (timestamp, periodicReport) VALUES (?, ?)", 
                                      (timestamp, json.dumps(periodicReport)))
                #---[5-3-2]: Timestamp Equal
                elif lastReportTS == timestamp:                             
                    sqlCursor.execute(f"UPDATE {ad['periodicReportsTableName']} SET periodicReport = ? WHERE timestamp = ?",     
                                      (json.dumps(periodicReport), timestamp))
                #---[5-3-3]: Timestamp Earlier
                else:
                    self.__logger(message = "Periodic report update requested on an hour timestamp earlier than that of the last. The request will be disposed. User attention advised.\n"\
                                          +f"* Request Queue:  {(localID, timestamp, periodicReport)}\n"\
                                          +f"* Last Report TS: {lastReportTS}", 
                                  logType = 'Warning', 
                                  color = 'light_red')
                    continue

                #[5-4]: Last Report Timestamp Update & Commit Flag Raise
                ad['lastReportTS'] = timestamp
                needCommit = True

        #[6]: Commit If Needed
        if needCommit: sqlConnection.commit()
    #---Neural Network
    def __createNeuralNetworkDataTable(self, neuralNetworkCode, tableType):
        if (tableType == 'NETWORKCONNECTIONDATA'):
            tableName = "ncdt_{:s}".format(neuralNetworkCode)  #Network Connection Data Table
            self.__sql_neuralNetworks_cursor.execute("""CREATE TABLE {:s} (id            INTEGER PRIMARY KEY,
                                                                           type          TEXT,
                                                                           layerAddress  TEXT,
                                                                           tensorAddress TEXT,
                                                                           value         TEXT
                                                                           )""".format(tableName))
        elif (tableType == 'TRAININGLOGS'):
            tableName = "tlt_{:s}".format(neuralNetworkCode)  #Account Positions Table
            self.__sql_neuralNetworks_cursor.execute("""CREATE TABLE {:s} (id          INTEGER PRIMARY KEY,
                                                                           trainingLog TEXT
                                                                           )""".format(tableName))
        elif (tableType == 'PERFORMANCETESTLOGS'):
            tableName  = "ptlt_{:s}".format(neuralNetworkCode) #Account Trade Logs Table
            self.__sql_neuralNetworks_cursor.execute("""CREATE TABLE {:s} (id                 INTEGER PRIMARY KEY,
                                                                           performanceTestLog TEXT
                                                                           )""".format(tableName))
        return tableName
    def __processNeuralNetworkDataEditRequestQueues(self):
        _commit = False
        #[1]: Connection Data Update Requests
        if (0 < len(self.__neuralNetworkConnectionDataUpdateRequestQueues)):
            while (0 < len(self.__neuralNetworkConnectionDataUpdateRequestQueues)):
                queue = self.__neuralNetworkConnectionDataUpdateRequestQueues.pop(0)
                _neuralNetworkCode              = queue[0]
                _newNeuralNetworkConnectionData = queue[1]
                if (_neuralNetworkCode in self.__neuralNetworkDescriptions):
                    _networkConnectionDataTableName = self.__neuralNetworkDescriptions[_neuralNetworkCode]['networkConnectionDataTableName']
                    self.__sql_neuralNetworks_cursor.execute("DELETE FROM {:s}".format(_networkConnectionDataTableName))
                    _newNeuralNetworkConnectionData_formatted = list()
                    for _index, _cData in enumerate(_newNeuralNetworkConnectionData): _newNeuralNetworkConnectionData_formatted.append((_index, _cData[0], _cData[1], json.dumps(_cData[2]), _cData[3]))
                    self.__sql_neuralNetworks_cursor.executemany("INSERT INTO {:s} (id, type, layerAddress, tensorAddress, value) VALUES (?,?,?,?,?)".format(_networkConnectionDataTableName), _newNeuralNetworkConnectionData_formatted)
            _commit = True
        #[2]: Training Log Append Requests
        if (0 < len(self.__neuralNetworkTrainingLogAppendRequestQueues)):
            while (0 < len(self.__neuralNetworkTrainingLogAppendRequestQueues)):
                queue = self.__neuralNetworkTrainingLogAppendRequestQueues.pop(0)
                _neuralNetworkCode = queue[0]
                _trainingLog       = queue[1]
                if (_neuralNetworkCode in self.__neuralNetworkDescriptions):
                    _nnd = self.__neuralNetworkDescriptions[_neuralNetworkCode]
                    self.__sql_neuralNetworks_cursor.execute("INSERT INTO {:s} (id, trainingLog) VALUES (?, ?)".format(_nnd['trainingLogsTableName']), (len(_nnd['trainingLogs']), json.dumps(_trainingLog)))
                    _nnd['trainingLogs'].append(_trainingLog)
            _commit = True
        #[3]: Performance Test Log Append Requests
        if (0 < len(self.__neuralNetworkPerformanceTestLogAppendRequestQueues)):
            while (0 < len(self.__neuralNetworkPerformanceTestLogAppendRequestQueues)):
                queue = self.__neuralNetworkPerformanceTestLogAppendRequestQueues.pop(0)
                _neuralNetworkCode  = queue[0]
                _performanceTestLog = queue[1]
                if (_neuralNetworkCode in self.__neuralNetworkDescriptions):
                    _nnd = self.__neuralNetworkDescriptions[_neuralNetworkCode]
                    self.__sql_neuralNetworks_cursor.execute("INSERT INTO {:s} (id, performanceTestLog) VALUES (?, ?)".format(_nnd['performanceTestLogsTableName']), (len(_nnd['performanceTestLogs']), json.dumps(_performanceTestLog)))
                    _nnd['performanceTestLogs'].append(_performanceTestLog)
            _commit = True
        #Finally
        if (_commit == True): self.__sql_neuralNetworks_connection.commit()
    #---System
    def __logger(self, message, logType, color):
        if (self.__config_DataManager[f'print_{logType}'] == True): 
            _time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
            print(termcolor.colored(f"[DATAMANAGER-{_time_str}] {message}", color))
    #Manager Internal Functions END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #FAR & FARR Handlers ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<BINANCEAPI>
    def __far_registerCurrency(self, requester, symbol, info):
        if (requester == 'BINANCEAPI'):
            #Symbol already exists within the database
            if (symbol in self.__klineDataInfo):
                self.__klineDataInfo[symbol]['info_server'] = info
                updatedCurrencyInfo_db = 0b0
                #Precisions - 0b1
                if (self.__klineDataInfo[symbol]['precisions'] != None):
                    if ((self.__klineDataInfo[symbol]['precisions']['price']    != info['pricePrecision'])    or
                        (self.__klineDataInfo[symbol]['precisions']['quantity'] != info['quantityPrecision']) or
                        (self.__klineDataInfo[symbol]['precisions']['quote']    != info['quotePrecision'])):
                        updatedCurrencyInfo_db += 0b1
                else: updatedCurrencyInfo_db += 0b1
                if (0 < updatedCurrencyInfo_db&0b1):
                    self.__klineDataInfo[symbol]['precisions'] = {'price': info['pricePrecision'], 'quantity': info['quantityPrecision'], 'quote': info['quotePrecision']}
                    self.__sql_klines_cursor.execute("UPDATE summary SET precisions = ? WHERE id = ?", (json.dumps(self.__klineDataInfo[symbol]['precisions']), self.__klineDataInfo[symbol]['currencyID']))
                if (0 < updatedCurrencyInfo_db): self.__sql_klines_connection.commit()
                #Announce the updated info
                for processName in self.__currencyInfoSubscribers[symbol]:
                    self.ipcA.sendPRDEDIT(targetProcess = processName, prdAddress = ('CURRENCIES', symbol, 'info_server'), prdContent = self.__klineDataInfo[symbol]['info_server'])
                    self.ipcA.sendFAR(targetProcess = processName, functionID = 'onCurrenciesUpdate', functionParams = {'updatedContents': [{'symbol': symbol, 'id': ('info_server',)}]}, farrHandler = None)
            #Symbol does not exist within the database (This is a new symbol)
            else:
                #Find the lowest available currencyID
                currencyID = 0
                while (currencyID in self.__currencySymbolsByID): currencyID += 1
                #Update local data tracker instances and the .db file
                self.__klineDataInfo[symbol] = {'currencyID':            currencyID, 
                                                'precisions':            {'price':    info['pricePrecision'], 
                                                                          'quantity': info['quantityPrecision'], 
                                                                          'quote':    info['quotePrecision']},
                                                'baseAsset':             info['baseAsset'],
                                                'quoteAsset':            info['quoteAsset'],
                                                'kline_firstOpenTS':     None, 
                                                'kline_availableRanges': None, 
                                                'info_server':           info}
                self.__currencySymbolsByID[currencyID] = symbol
                if (symbol in self.__currencyInfoSubscribers): self.__currencyInfoSubscribers[symbol].add('GUI'); self.__currencyInfoSubscribers[symbol].add('TRADEMANAGER'); self.__currencyInfoSubscribers[symbol].add('NEURALNETWORKMANAGER')
                else:                                          self.__currencyInfoSubscribers[symbol] = set(['GUI', 'TRADEMANAGER', 'NEURALNETWORKMANAGER'])
                self.__klines_streamed[symbol] = {'klines': list(), 'range': None, 'firstOpenTS': None, 'streamConnectionTime': None}
                self.__sql_klines_cursor.execute("INSERT INTO summary (id, symbol, precisions, baseAsset, quoteAsset, kline_firstOpenTS, kline_availableRanges) VALUES (?,?,?,?,?,?,?)", 
                                                 (currencyID, symbol, json.dumps(self.__klineDataInfo[symbol]['precisions']), self.__klineDataInfo[symbol]['baseAsset'], self.__klineDataInfo[symbol]['quoteAsset'], None, None))
                self.__sql_klines_connection.commit()
                #Announce the updated info
                for processName in self.__currencyInfoSubscribers[symbol]:
                    self.ipcA.sendPRDEDIT(targetProcess = processName, prdAddress = ('CURRENCIES', symbol), prdContent = self.__klineDataInfo[symbol])
                    self.ipcA.sendFAR(targetProcess = processName, functionID = 'onCurrenciesUpdate', functionParams = {'updatedContents': [{'symbol': symbol, 'id': '_ADDED'},]}, farrHandler = None)
            #If the currency's first openTS is not found, send a search request
            if (self.__klineDataInfo[symbol]['kline_firstOpenTS'] == None):
                self.ipcA.sendFAR(targetProcess = 'BINANCEAPI', functionID = 'getFirstKlineOpenTS', functionParams = {'symbol': symbol}, farrHandler = self.__farr_getFirstKlineOpenTS)
    def __far_onCurrencyInfoUpdate(self, requester, symbol, infoUpdates):
        if (requester == 'BINANCEAPI'):
            for infoUpdate in infoUpdates:
                updateSuccessful = True
                updateID    = infoUpdate['id']
                updateValue = infoUpdate['value']
                lenID = len(updateID)
                if   (lenID ==  1): self.__klineDataInfo[symbol][updateID[0]]                                                                                                                      = updateValue
                elif (lenID ==  2): self.__klineDataInfo[symbol][updateID[0]][updateID[1]]                                                                                                         = updateValue
                elif (lenID ==  3): self.__klineDataInfo[symbol][updateID[0]][updateID[1]][updateID[2]]                                                                                            = updateValue
                elif (lenID ==  4): self.__klineDataInfo[symbol][updateID[0]][updateID[1]][updateID[2]][updateID[3]]                                                                               = updateValue
                elif (lenID ==  5): self.__klineDataInfo[symbol][updateID[0]][updateID[1]][updateID[2]][updateID[3]][updateID[4]]                                                                  = updateValue
                elif (lenID ==  6): self.__klineDataInfo[symbol][updateID[0]][updateID[1]][updateID[2]][updateID[3]][updateID[4]][updateID[5]]                                                     = updateValue
                elif (lenID ==  7): self.__klineDataInfo[symbol][updateID[0]][updateID[1]][updateID[2]][updateID[3]][updateID[4]][updateID[5]][updateID[6]]                                        = updateValue
                elif (lenID ==  8): self.__klineDataInfo[symbol][updateID[0]][updateID[1]][updateID[2]][updateID[3]][updateID[4]][updateID[5]][updateID[6]][updateID[7]]                           = updateValue
                elif (lenID ==  9): self.__klineDataInfo[symbol][updateID[0]][updateID[1]][updateID[2]][updateID[3]][updateID[4]][updateID[5]][updateID[6]][updateID[7]][updateID[8]]              = updateValue
                elif (lenID == 10): self.__klineDataInfo[symbol][updateID[0]][updateID[1]][updateID[2]][updateID[3]][updateID[4]][updateID[5]][updateID[6]][updateID[7]][updateID[8]][updateID[9]] = updateValue
                else:
                    self.__logger(message = f"Currency information update failed, key tuple length too long. Developer attention advised\n * symbol: {symbol}\n * updateID: {updateID}\n * updateValue: {updateValue}", logType = 'Error', color = 'red')
                    updateSuccessful = False
                if (updateSuccessful == True):
                    #Announce the updated info
                    for processName in self.__currencyInfoSubscribers[symbol]:
                        self.ipcA.sendPRDEDIT(targetProcess = processName, prdAddress = ('CURRENCIES', symbol)+updateID, prdContent = updateValue)
                        self.ipcA.sendFAR(targetProcess = processName, functionID = 'onCurrenciesUpdate', functionParams = {'updatedContents': [{'symbol': symbol, 'id': updateID},]}, farrHandler = None)
    def __farr_getFirstKlineOpenTS(self, responder, requestID, functionResult):
        #Read the function result
        symbol           = functionResult['symbol']
        firstKlineOpenTS = functionResult['firstKlineOpenTS']
        #Save the found firstKlineOpenTS
        self.__klineDataInfo[symbol]['kline_firstOpenTS'] = firstKlineOpenTS
        self.__sql_klines_cursor.execute("UPDATE summary SET kline_firstOpenTS = ? WHERE id = ?", (firstKlineOpenTS, self.__klineDataInfo[symbol]['currencyID']))
        self.__sql_klines_connection.commit()
        #Currency info update on PRD-GUI via PRD and notification by FAR
        for processName in self.__currencyInfoSubscribers[symbol]:
            self.ipcA.sendPRDEDIT(targetProcess = processName, prdAddress = ('CURRENCIES', symbol, 'kline_firstOpenTS'), prdContent = self.__klineDataInfo[symbol]['kline_firstOpenTS'])
            self.ipcA.sendFAR(targetProcess = processName, functionID = 'onCurrenciesUpdate', functionParams = {'updatedContents': [{'symbol': symbol, 'id': ('kline_firstOpenTS',)}]}, farrHandler = None)
        #Send kline fetch request if possible
        if (self.__klines_streamed[symbol]['firstOpenTS'] is not None): self.__klines_fetched_requestQueue.add(symbol)
    def __far_onKlineStreamReceival(self, requester, symbol, streamConnectionTime, kline, closed):
        if (requester == 'BINANCEAPI'):
            """
            kline = ([0]: openTS, [1]: closeTS, [2]: openPrice, [3]: highPrice, [4]: lowPrice, [5]: closePrice, [6]: nTrades, [7]: baseAssetVolume, [8]: quoteAssetVolume, [9]: baseAssetVolume_takerBuy, [10]: quoteAssetVolume_takerBuy, [11]: klineType)
            """ #Expand to check a data example
            streamedRange = [kline[0], kline[1]]
            #From new connection
            if (streamConnectionTime != self.__klines_streamed[symbol]['streamConnectionTime']):
                self.__klines_streamed[symbol]['streamConnectionTime'] = streamConnectionTime
                self.__klines_streamed[symbol]['firstOpenTS']          = kline[0]
                if (closed == True):
                    self.__klines_streamed[symbol]['klines'] = [kline,]
                    self.__klines_streamed[symbol]['range']  = streamedRange
                else:                
                    self.__klines_streamed[symbol]['klines'] = list()
                    self.__klines_streamed[symbol]['range']  = None
                if (self.__klineDataInfo[symbol]['kline_firstOpenTS'] != None): self.__klines_fetched_requestQueue.add(symbol)
            #From the same connection
            else:
                if (closed == True): 
                    #[1]: Check streamed data range
                    if (self.__klines_streamed[symbol]['range'] == None): dataRangeCheckPass = True
                    else:
                        drClassification = self.__dataRange_getClassification(self.__klines_streamed[symbol]['range'], streamedRange)
                        if ((drClassification == 0b0000) and (self.__klines_streamed[symbol]['range'][1]+1 == streamedRange[0])): dataRangeCheckPass = True
                        else:                                                                                                     dataRangeCheckPass = False
                    #If the data range check has passed, save the kline and and update the range
                    if (dataRangeCheckPass == True):
                        self.__klines_streamed[symbol]['klines'].append(kline)
                        if (self.__klines_streamed[symbol]['range'] == None): self.__klines_streamed[symbol]['range']    = streamedRange
                        else:                                                 self.__klines_streamed[symbol]['range'][1] = streamedRange[1]
                    #If the data range check has not passed, dispose the streamed kline and update the kline fetch request
                    else:
                        _koTS_expected = self.__klines_streamed[symbol]['range'][1]+1
                        self.__logger(message = f"An unexpected streamed kline detected {symbol}@{kline[0]} when expected is a kline with openTS = {_koTS_expected}.", logType = 'Warning', color = 'light_yellow')
                        if (self.__klineDataInfo[symbol]['kline_firstOpenTS'] != None): self.__klines_fetched_requestQueue.add(symbol)
    def __farr_getKlineFetchRequestResult(self, responder, requestID, functionResult):
        if (responder == 'BINANCEAPI'):
            if (requestID in self.__klines_fetched_activeRequests):
                #Function Result
                fetchedKlines = functionResult['klines']
                requestStatus = functionResult['status']
                #If possible, save the klines
                if ((requestStatus == 'fetching') or (requestStatus == 'complete')):
                    #Local tracker
                    request = self.__klines_fetched_activeRequests[requestID]
                    symbol = request['symbol']
                    #Check data ranges overlap
                    fetchedRange = (fetchedKlines[0][0], fetchedKlines[-1][1])
                    if (self.__klineDataInfo[symbol]['kline_availableRanges'] == None): noOverlap = True
                    else:
                        noOverlap = True
                        for availableDataRange in self.__klineDataInfo[symbol]['kline_availableRanges']:
                            drClassification = self.__dataRange_getClassification(availableDataRange, fetchedRange)
                            if not((drClassification == 0b0000) or (drClassification == 0b1111)): noOverlap = False; break
                    #If the data range test has passed, re-format the klines for saving and update the available data ranges and the control variables
                    if (noOverlap == True):
                        #New data range computation
                        if (self.__klineDataInfo[symbol]['kline_availableRanges'] == None): newDataRanges = [fetchedRange,]
                        else:
                            newDataRanges = self.__klineDataInfo[symbol]['kline_availableRanges'].copy()
                            newDataRanges.append(fetchedRange)
                            newDataRanges.sort(key = lambda x: x[0])
                            newDataRanges_merged = list()
                            for dataRange in newDataRanges:
                                if (len(newDataRanges_merged) == 0): newDataRanges_merged.append(dataRange)
                                else:
                                    if (newDataRanges_merged[-1][1]+1 == dataRange[0]): newDataRanges_merged[-1] = (newDataRanges_merged[-1][0], dataRange[1])
                                    else:                                               newDataRanges_merged.append(dataRange)
                            newDataRanges = newDataRanges_merged
                        #Klines formatting
                        klines_formatted = [(self.__klineDataInfo[symbol]['currencyID']*1e10+fetchedKline[0],)+fetchedKline for fetchedKline in fetchedKlines]
                        #Try to update .db files
                        try:
                            self.__sql_klines_cursor.executemany("INSERT INTO klines (id, t_open, t_close, p_open, p_high, p_low, p_close, nTrades, v, q, v_tb, q_tb, kType) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", klines_formatted)
                            self.__sql_klines_cursor.execute("UPDATE summary SET kline_availableRanges = ? WHERE id = ?", (json.dumps(newDataRanges), self.__klineDataInfo[symbol]['currencyID']))
                            self.__sql_klines_connection.commit()
                            dbUpdateSuccess = True
                        except Exception as e:
                            self.__logger(message = f"An unexpected error occurred while attempting to save fetched klines for {symbol}\n * {str(e)}", logType = 'Error', color = 'light_red')
                            dbUpdateSuccess = False
                        #If the database update has succeeded, update the local variables
                        if (dbUpdateSuccess == True): self.__klineDataInfo[symbol]['kline_availableRanges'] = newDataRanges
                        #Announce the updated info
                        for processName in self.__currencyInfoSubscribers[symbol]:
                            self.ipcA.sendPRDEDIT(targetProcess = processName, prdAddress = ('CURRENCIES', symbol, 'kline_availableRanges'), prdContent = self.__klineDataInfo[symbol]['kline_availableRanges'])
                            self.ipcA.sendFAR(targetProcess = processName, functionID = 'onCurrenciesUpdate', functionParams = {'updatedContents': [{'symbol': symbol, 'id': ('kline_availableRanges',)}]}, farrHandler = None)
                    #If data range overlap has been found, dispose the fetched klines and re-send the fetch request
                    else:
                        self.__logger(message = f"A data ranges overlap detected while attempting to save fetched klines for {symbol}. The fetch request will be updated\n Available Ranges: {str(self.__klineDataInfo[symbol]['kline_availableRanges'])}\n Fetched Range: {str(fetchedRange)}", logType = 'Warning', color = 'light_red')
                        self.__klines_fetched_requestQueue.add(symbol)
                #If this request is completed or terminated, remove the tracker variable
                if ((requestStatus == 'complete') or (requestStatus == 'terminate')): del self.__klines_fetched_activeRequests[requestID]
            else: self.__logger(message = f"An unexpected kline fetch request result received with rID: {requestID}, which is not registered within the request tracker. User attention advised!", logType = 'Warning', color = 'light_red')

    #<SIMULATOR>
    def __far_saveSimulationData(self, requester, requestID, simulationCode, simulationRange, currencyAnalysisConfigurations, tradeConfigurations, analysisExport, assets, positions, creationTime, tradeLogs, periodicReports, simulationSummary):
        if (requester[:9] == 'SIMULATOR'):
            try:
                _simulationDescription_dbID = 0
                while (_simulationDescription_dbID in self.__simulationCodesByID): _simulationDescription_dbID += 1
                _currencyAnalysisConfigurationsTableName = "cact_{:s}".format(simulationCode)
                _tradeConfigurationsTableName            = "tct_{:s}".format(simulationCode)
                _assetsTableName                         = "at_{:s}".format(simulationCode)
                _positionsTableName                      = "pt_{:s}".format(simulationCode)
                _tradeLogsTableName                      = "tlt_{:s}".format(simulationCode)
                _periodicReportsTableName                = "drt_{:s}".format(simulationCode)
                _simulationDescription = {'simulationRange':                simulationRange,
                                          'currencyAnalysisConfigurations': currencyAnalysisConfigurations,
                                          'tradeConfigurations':            tradeConfigurations,
                                          'analysisExport':                 analysisExport,
                                          'assets':                         assets,
                                          'positions':                      positions,
                                          'creationTime':                   creationTime,
                                          'simulationSummary':              simulationSummary,
                                          'currencyAnalysisConfigurationsTableName': _currencyAnalysisConfigurationsTableName,
                                          'tradeConfigurationsTableName':            _tradeConfigurationsTableName,
                                          'assetsTableName':                         _assetsTableName,
                                          'positionsTableName':                      _positionsTableName,
                                          'tradeLogsTableName':                      _tradeLogsTableName,
                                          'periodicReportsTableName':                _periodicReportsTableName}
                #Create simulation tables
                self.__sql_simulations_cursor.execute("CREATE TABLE {:s} (id INTEGER PRIMARY KEY, configurationCode TEXT, configuration TEXT)".format(_currencyAnalysisConfigurationsTableName))
                self.__sql_simulations_cursor.execute("CREATE TABLE {:s} (id INTEGER PRIMARY KEY, configurationCode TEXT, configuration TEXT)".format(_tradeConfigurationsTableName))
                self.__sql_simulations_cursor.execute("""CREATE TABLE {:s} (id                             INTEGER PRIMARY KEY, 
                                                                            asset                          TEXT, 
                                                                            initialWalletBalance           REAL, 
                                                                            allocatableBalance             REAL, 
                                                                            allocatedBalance               REAL, 
                                                                            allocationRatio                REAL, 
                                                                            assumedRatio                   REAL, 
                                                                            weightedAssumedRatio           REAL, 
                                                                            maxAllocatedBalance            TEXT, 
                                                                            positionSymbols                TEXT, 
                                                                            positionSymbols_prioritySorted TEXT
                                                                            )""".format(_assetsTableName))
                self.__sql_simulations_cursor.execute("""CREATE TABLE {:s} (id                                INTEGER PRIMARY KEY, 
                                                                            positionSymbol                    TEXT, 
                                                                            quoteAsset                        TEXT, 
                                                                            precisions                        TEXT, 
                                                                            dataRange                         TEXT, 
                                                                            currencyAnalysisConfigurationCode TEXT,
                                                                            tradeConfigurationCode            TEXT,
                                                                            isolated                          INTEGER,
                                                                            leverage                          INTEGER,
                                                                            priority                          INTEGER,
                                                                            assumedRatio                      REAL,
                                                                            weightedAssumedRatio              REAL,
                                                                            allocatedBalance                  REAL,
                                                                            maxAllocatedBalance               TEXT,
                                                                            firstKline                        INTEGER
                                                                            )""".format(_positionsTableName))
                self.__sql_simulations_cursor.execute("CREATE TABLE {:s} (id INTEGER PRIMARY KEY, tradeLog TEXT)".format(_tradeLogsTableName))
                self.__sql_simulations_cursor.execute("CREATE TABLE {:s} (id INTEGER PRIMARY KEY, dayTimeStamp INTERGER, periodicReport TEXT)".format(_periodicReportsTableName))
                #Format and save data
                currencyAnalysisConfigurations_formatted = [(_index, _cacCode, json.dumps(currencyAnalysisConfigurations[_cacCode])) for _index, _cacCode in enumerate(currencyAnalysisConfigurations)]
                tradeConfigurations_formatted            = [(_index, _tcCode,  json.dumps(tradeConfigurations[_tcCode]))             for _index, _tcCode  in enumerate(tradeConfigurations)]
                assets_formatted = list()
                for _index, _assetName in enumerate(assets):
                    _asset = assets[_assetName]
                    assets_formatted.append((_index,
                                             _assetName,
                                             _asset['initialWalletBalance'],
                                             _asset['allocatableBalance'],
                                             _asset['allocatedBalance'],
                                             _asset['allocationRatio'],
                                             _asset['assumedRatio'],
                                             _asset['weightedAssumedRatio'],
                                             json.dumps(_asset['maxAllocatedBalance']),
                                             json.dumps(list(_asset['_positionSymbols'])),
                                             json.dumps(_asset['_positionSymbols_prioritySorted'])
                                             ))
                positions_formatted = list()
                for _index, _pSymbol in enumerate(positions):
                    _position = positions[_pSymbol]
                    positions_formatted.append((_index,
                                                _pSymbol,
                                                json.dumps(_position['quoteAsset']),
                                                json.dumps(_position['precisions']),
                                                json.dumps(_position['dataRange']),
                                                _position['currencyAnalysisConfigurationCode'],
                                                _position['tradeConfigurationCode'],
                                                int(_position['isolated']),
                                                _position['leverage'],
                                                _position['priority'],
                                                _position['assumedRatio'],
                                                _position['weightedAssumedRatio'],
                                                _position['allocatedBalance'],
                                                json.dumps(_position['maxAllocatedBalance']),
                                                _position['firstKline'],
                                                ))
                tradeLogs_formatted       = [(_index, json.dumps(_tradeLog))                                     for _index, _tradeLog     in enumerate(tradeLogs)]
                periodicReports_formatted = [(_index, _dayTimeStamp, json.dumps(periodicReports[_dayTimeStamp])) for _index, _dayTimeStamp in enumerate(periodicReports)]
                self.__sql_simulations_cursor.executemany("INSERT INTO {:s} (id, configurationCode, configuration) VALUES (?,?,?)".format(_currencyAnalysisConfigurationsTableName), currencyAnalysisConfigurations_formatted)
                self.__sql_simulations_cursor.executemany("INSERT INTO {:s} (id, configurationCode, configuration) VALUES (?,?,?)".format(_tradeConfigurationsTableName),            tradeConfigurations_formatted)
                self.__sql_simulations_cursor.executemany("""INSERT INTO {:s} (id, 
                                                                               asset, 
                                                                               initialWalletBalance, 
                                                                               allocatableBalance,
                                                                               allocatedBalance,
                                                                               allocationRatio,
                                                                               assumedRatio,
                                                                               weightedAssumedRatio,
                                                                               maxAllocatedBalance,
                                                                               positionSymbols,
                                                                               positionSymbols_prioritySorted
                                                                               ) 
                                                                               VALUES (?,?,?,?,?,?,?,?,?,?,?)""".format(_assetsTableName), assets_formatted)
                self.__sql_simulations_cursor.executemany("""INSERT INTO {:s} (id, 
                                                                               positionSymbol, 
                                                                               quoteAsset, 
                                                                               precisions, 
                                                                               dataRange,
                                                                               currencyAnalysisConfigurationCode,
                                                                               tradeConfigurationCode,
                                                                               isolated,
                                                                               leverage,
                                                                               priority,
                                                                               assumedRatio,
                                                                               weightedAssumedRatio,
                                                                               allocatedBalance,
                                                                               maxAllocatedBalance,
                                                                               firstKline
                                                                               ) 
                                                                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""".format(_positionsTableName), positions_formatted)
                self.__sql_simulations_cursor.executemany("INSERT INTO {:s} (id, tradeLog)                     VALUES (?,?)".format(_tradeLogsTableName),         tradeLogs_formatted)
                self.__sql_simulations_cursor.executemany("INSERT INTO {:s} (id, dayTimeStamp, periodicReport) VALUES (?,?,?)".format(_periodicReportsTableName), periodicReports_formatted)
                #Save simulation description to the db file
                self.__sql_simulations_cursor.execute("""INSERT INTO simulationDescriptions (id, 
                                                                                             simulationCode, 
                                                                                             simulationRange,
                                                                                             analysisExport,
                                                                                             creationTime,
                                                                                             simulationSummary,
                                                                                             currencyAnalysisConfigurationsTableName, 
                                                                                             tradeConfigurationsTableName, 
                                                                                             assetsTableName, 
                                                                                             positionsTableName, 
                                                                                             tradeLogsTableName,
                                                                                             periodicReportsTableName
                                                                                             ) 
                                                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                                                         (_simulationDescription_dbID, 
                                                          simulationCode,
                                                          json.dumps(simulationRange),
                                                          json.dumps(analysisExport),
                                                          creationTime,
                                                          json.dumps(simulationSummary),
                                                          _currencyAnalysisConfigurationsTableName,
                                                          _tradeConfigurationsTableName,
                                                          _assetsTableName,
                                                          _positionsTableName,
                                                          _tradeLogsTableName,
                                                          _periodicReportsTableName))
                #Commit the db file
                self.__sql_simulations_connection.commit()
                #Save the temporarily created simulation instance
                self.__simulationDescriptions[simulationCode]           = _simulationDescription
                self.__simulationCodesByID[_simulationDescription_dbID] = simulationCode
                #Return succesful save result
                return {'simulationCode': simulationCode, 'saveResult': True, 'errorMsg': None}
            except Exception as e:
                try:    self.__sql_simulations_cursor.execute("DROP TABLE {:s}".format(_currencyAnalysisConfigurationsTableName))
                except: pass
                try:    self.__sql_simulations_cursor.execute("DROP TABLE {:s}".format(_tradeConfigurationsTableName))
                except: pass
                try:    self.__sql_simulations_cursor.execute("DROP TABLE {:s}".format(_assetsTableName))
                except: pass
                try:    self.__sql_simulations_cursor.execute("DROP TABLE {:s}".format(_positionsTableName))
                except: pass
                try:    self.__sql_simulations_cursor.execute("DROP TABLE {:s}".format(_tradeLogsTableName))
                except: pass
                try:    self.__sql_simulations_cursor.execute("DROP TABLE {:s}".format(_periodicReportsTableName))
                except: pass
                try:    self.__sql_simulations_cursor.execute("DELETE from simulationDescriptions where id = ?", (_simulationDescription_dbID,))
                except: pass
                self.__sql_simulations_connection.commit()
                if (_simulationDescription_dbID in self.__simulationCodesByID): del self.__simulationCodesByID[_simulationDescription_dbID]
                if (simulationCode in self.__simulationDescriptions): del self.__simulationDescriptions[simulationCode]
                self.__logger(message = f"An unexpected error occurred while attempting to save simulation result for {str(simulationCode)}\n * {str(e)}", logType = 'Error', color = 'light_red')
                return {'simulationCode': simulationCode, 'saveResult': False, 'errorMsg': str(e)}

    #<SIMULATIONMANAGER&SIMULATOR>
    def __far_removeSimulationData(self, requester, simulationCode):
        if ((requester == 'SIMULATIONMANAGER') or (requester[:9] == 'SIMULATOR')):
            if (simulationCode in self.__simulationDescriptions):
                for _sim_dbID in self.__simulationCodesByID:
                    if (self.__simulationCodesByID[_sim_dbID] == simulationCode): sim_dbID = _sim_dbID; break
                _simulationDescription = self.__simulationDescriptions[simulationCode]
                if (_simulationDescription['currencyAnalysisConfigurationsTableName'] != None): self.__sql_simulations_cursor.execute("DROP TABLE {:s}".format(_simulationDescription['currencyAnalysisConfigurationsTableName']))
                if (_simulationDescription['tradeConfigurationsTableName']            != None): self.__sql_simulations_cursor.execute("DROP TABLE {:s}".format(_simulationDescription['tradeConfigurationsTableName']))
                if (_simulationDescription['assetsTableName']                         != None): self.__sql_simulations_cursor.execute("DROP TABLE {:s}".format(_simulationDescription['assetsTableName']))
                if (_simulationDescription['positionsTableName']                      != None): self.__sql_simulations_cursor.execute("DROP TABLE {:s}".format(_simulationDescription['positionsTableName']))
                if (_simulationDescription['tradeLogsTableName']                      != None): self.__sql_simulations_cursor.execute("DROP TABLE {:s}".format(_simulationDescription['tradeLogsTableName']))
                if (_simulationDescription['periodicReportsTableName']                != None): self.__sql_simulations_cursor.execute("DROP TABLE {:s}".format(_simulationDescription['periodicReportsTableName']))
                self.__sql_simulations_cursor.execute("DELETE from simulationDescriptions where id = ?", (sim_dbID,))
                self.__sql_simulations_connection.commit()
                del self.__simulationCodesByID[sim_dbID]
                del self.__simulationDescriptions[simulationCode]

    #<TRADEMANAGER>
    def __far_loadAccountDescriptions(self, requester, requestID):
        #[1]: Requester Check
        if requester != 'TRADEMANAGER': return None

        #[2]: Account Description Load
        sqlCursor = self.__sql_accounts_cursor
        ads       = dict()
        sqlCursor.execute("SELECT * FROM accountDescriptions")
        ad_DB = sqlCursor.fetchall()
        for ad_DB_row in ad_DB:
            #[2-1]: Account Summary
            dbID                     = ad_DB_row[0]
            localID                  = ad_DB_row[1]
            accountType              = ad_DB_row[2]
            buid                     = ad_DB_row[3]
            assetsTableName          = ad_DB_row[4]
            positionsTableName       = ad_DB_row[5]
            tradeLogsTableName       = ad_DB_row[6]
            periodicReportsTableName = ad_DB_row[7]
            hashedPassword           = ad_DB_row[8]
            self.__accountDescriptions[localID] = {'dbID':                     dbID,
                                                   'assetsTableName':          assetsTableName,
                                                   'positionsTableName':       positionsTableName,
                                                   'tradeLogsTableName':       tradeLogsTableName,
                                                   'periodicReportsTableName': periodicReportsTableName,
                                                   'assets_dbID':              dict(),
                                                   'positions_dbID':           dict(),
                                                   'nTradeLog':                0,
                                                   'lastReportTS':             None}
            self.__accountLocalIDsByID[dbID] = localID
            ads[localID] = {'accountType':        accountType,
                            'buid':               buid,
                            'hashedPassword':     hashedPassword,
                            'assets':             dict(),
                            'positions':          dict(),
                            'lastPeriodicReport': None}
            ad = ads[localID]
            
            #[2-2]: Assets
            if assetsTableName is not None:
                sqlCursor.execute(f'SELECT * FROM {assetsTableName}')
                assets_DB = sqlCursor.fetchall()
                for assetDesc in assets_DB:
                    asset = assetDesc[1]
                    ad['assets'][asset] = {'crossWalletBalance': assetDesc[2],
                                           'allocationRatio':    assetDesc[3]}
                    self.__accountDescriptions[localID]['assets_dbID'][asset] = assetDesc[0]

            #[2-3]: Positions
            if positionsTableName is not None:
                sqlCursor.execute(f'SELECT * FROM {positionsTableName}')
                positions_DB = sqlCursor.fetchall()
                for positionDesc in positions_DB:
                    symbol = positionDesc[1]
                    ad['positions'][symbol] = {'quoteAsset':             positionDesc[2],
                                               'precisions':             json.loads(positionDesc[3]),
                                               'tradeStatus':            (positionDesc[4] == 1),
                                               'reduceOnly':             (positionDesc[5] == 1),
                                               'currencyAnalysisCode':   positionDesc[6],
                                               'tradeConfigurationCode': positionDesc[7],
                                               'tradeControlTracker':    json.loads(positionDesc[8]),
                                               'isolatedWalletBalance':  positionDesc[9],
                                               'quantity':               positionDesc[10],
                                               'entryPrice':             positionDesc[11],
                                               'leverage':               positionDesc[12],
                                               'isolated':               (positionDesc[13] == 1),
                                               'assumedRatio':           positionDesc[14],
                                               'priority':               positionDesc[15],
                                               'maxAllocatedBalance':    positionDesc[16],
                                               'abruptClearingRecords':  json.loads(positionDesc[17])}
                    self.__accountDescriptions[localID]['positions_dbID'][symbol] = positionDesc[0]

            #[2-4]: Read Trade Log Data
            if tradeLogsTableName is not None:
                sqlCursor.execute(f'SELECT COUNT(*) FROM {tradeLogsTableName}')
                tradeLogs_count = sqlCursor.fetchone()[0]
                self.__accountDescriptions[localID]['nTradeLog'] = tradeLogs_count

            #[2-5]: Read Periodic Reports Data
            if periodicReportsTableName is not None:
                sqlCursor.execute(f'SELECT * FROM {periodicReportsTableName} ORDER BY timestamp DESC LIMIT 1')
                last_report_row = sqlCursor.fetchone()
                if last_report_row:
                    timestamp      = last_report_row[0]
                    periodicReport = json.loads(last_report_row[1])
                    ad['lastPeriodicReport'] = {'timestamp': timestamp, 
                                                'report':    periodicReport}
                    self.__accountDescriptions[localID]['lastPeriodicReport'] = timestamp

        #[3]: Return Account Descriptions
        return ads
    def __far_addAccountDescription(self, requester, localID, accountDescription):
        #[1]: Requester Check
        if requester != 'TRADEMANAGER': return

        #[2]: Account Adding
        sqlCursor     = self.__sql_accounts_cursor
        sqlConnection = self.__sql_accounts_connection
        try:
            #[2-1]: Account Description DB ID
            ad_dbID = 0
            while (ad_dbID in self.__accountLocalIDsByID): ad_dbID += 1

            #[2-2]: Tables Initialization
            tName_assets          = self.__createAccountDataTable(localID = localID, tableType = 'ASSETS')
            tName_positions       = self.__createAccountDataTable(localID = localID, tableType = 'POSITIONS')
            tName_tradeLogs       = self.__createAccountDataTable(localID = localID, tableType = 'TRADELOGS')
            tName_periodicReports = self.__createAccountDataTable(localID = localID, tableType = 'PERIODICREPORTS')

            #[2-3]: Account Description
            ad_local = {'dbID':                     ad_dbID,
                        'assetsTableName':          tName_assets,
                        'positionsTableName':       tName_positions,
                        'tradeLogsTableName':       tName_tradeLogs,
                        'periodicReportsTableName': tName_periodicReports,
                        'assets_dbID':              dict(),
                        'positions_dbID':           dict(),
                        'nTradeLog':                0,
                        'lastReportTS':             None}
            
            #[2-4]: Assets  Data
            assetsData_formatted = list()
            for index, assetName in enumerate(accountDescription['assets']):
                assetData = accountDescription['assets'][assetName]
                assetData_formatted = [index,
                                       assetName,
                                       assetData['crossWalletBalance'],
                                       assetData['allocationRatio']]
                assetsData_formatted.append(assetData_formatted)
                ad_local['assets_dbID'][assetName] = index

            #[2-5]: Positions Data
            positionsData_formatted = list()
            for index, symbol in enumerate(accountDescription['positions']):
                positionData = accountDescription['positions'][symbol]
                if   positionData['isolated'] == True:  isolated = 1
                elif positionData['isolated'] == False: isolated = 0
                elif positionData['isolated'] == None:  isolated = None
                positionsData_formatted.append([index,
                                                symbol,
                                                positionData['quoteAsset'],
                                                json.dumps(positionData['precisions']),
                                                int(positionData['tradeStatus']),
                                                int(positionData['reduceOnly']),
                                                positionData['currencyAnalysisCode'],
                                                positionData['tradeConfigurationCode'],
                                                json.dumps(positionData['tradeControlTracker']),
                                                positionData['isolatedWalletBalance'],
                                                positionData['quantity'],
                                                positionData['entryPrice'],
                                                positionData['leverage'],
                                                isolated,
                                                positionData['assumedRatio'],
                                                positionData['priority'],
                                                positionData['maxAllocatedBalance'],
                                                json.dumps(positionData['abruptClearingRecords'])])
                ad_local['positions_dbID'][symbol] = index
            sqlCursor.executemany(f"INSERT INTO {tName_assets} (id, asset, crossWalletBalance, allocationRatio) VALUES (?,?,?,?)", assetsData_formatted)
            sqlCursor.executemany(f"""INSERT INTO {tName_positions} (id, 
                                                                     symbol, 
                                                                     quoteAsset, 
                                                                     precisions, 
                                                                     tradeStatus, 
                                                                     reduceOnly,
                                                                     currencyAnalysisCode,
                                                                     tradeConfigurationCode,
                                                                     tradeControlTracker,
                                                                     isolatedWalletBalance,
                                                                     quantity,
                                                                     entryPrice,
                                                                     leverage,
                                                                     isolated,
                                                                     assumedRatio,
                                                                     priority,
                                                                     maxAllocatedBalance,
                                                                     abruptClearingRecords)
                                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                                  positionsData_formatted)
            
            #[2-6]: DB Update
            sqlCursor.execute("""INSERT INTO accountDescriptions (id,
                                                                  localID, 
                                                                  accountType,
                                                                  buid,
                                                                  assetsTableName,
                                                                  positionsTableName, 
                                                                  tradeLogsTableName,
                                                                  periodicReportsTableName,
                                                                  hashedPassword) 
                              VALUES (?,?,?,?,?,?,?,?,?)""",
                              (ad_dbID,
                               localID,
                               accountDescription['accountType'],
                               accountDescription['buid'],
                               tName_assets,
                               tName_positions,
                               tName_tradeLogs,
                               tName_periodicReports,
                               accountDescription['hashedPassword']))
            sqlConnection.commit()

            #[2-7]: Account Generation Finalization
            self.__accountDescriptions[localID] = ad_local
            self.__accountLocalIDsByID[ad_dbID] = localID

        except Exception as e:
            try:    sqlCursor.execute(f"DROP TABLE {tName_assets}")
            except: pass
            try:    sqlCursor.execute(f"DROP TABLE {tName_positions}")
            except: pass
            try:    sqlCursor.execute(f"DROP TABLE {tName_tradeLogs}")
            except: pass
            try:    sqlCursor.execute(f"DROP TABLE {tName_periodicReports}")
            except: pass
            try:    sqlCursor.execute("DELETE from simulationDescriptions where localID = ?", (localID,))
            except: pass
            sqlConnection.commit()
            if ad_dbID in self.__accountLocalIDsByID: del self.__accountLocalIDsByID[ad_dbID]
            if localID in self.__accountDescriptions: del self.__accountDescriptions[localID]
            self.__logger(message = f"An unexpected error occurred while attempting to save an account description for {str(localID)}\n * {str(e)}", logType = 'Error', color = 'light_red')
    def __far_removeAccountDescription(self, requester, localID):
        #[1]: Requester Check
        if requester != 'TRADEMANAGER': return

        #[2]: Acocunt Check
        if localID not in self.__accountDescriptions: return

        #[3]: Account DB ID Search
        account_dbID = None
        for _account_dbID, _localID in self.__accountLocalIDsByID.items():
            if _localID != localID: continue
            account_dbID = _account_dbID
            break
        if account_dbID is None:
            self.__logger(message = f"Account DB ID Could Not Be Found While Attempting To Remove Account {localID}.", logType = 'Error', color = 'light_red')
            return

        #[4]: Account Removal
        ad = self.__accountDescriptions[localID]
        self.__sql_accounts_cursor.execute(f"DROP TABLE {ad['assetsTableName']}")
        self.__sql_accounts_cursor.execute(f"DROP TABLE {ad['positionsTableName']}")
        self.__sql_accounts_cursor.execute(f"DROP TABLE {ad['tradeLogsTableName']}")
        self.__sql_accounts_cursor.execute(f"DROP TABLE {ad['periodicReportsTableName']}")
        self.__sql_accounts_cursor.execute("DELETE from accountDescriptions where localID = ?", (localID,))
        self.__sql_accounts_connection.commit()
        del self.__accountLocalIDsByID[account_dbID]
        del self.__accountDescriptions[localID]
    def __far_editAccountData(self, requester, updates):
        if (requester == 'TRADEMANAGER'): self.__accountDataEditRequestQueues += updates
    def __far_addAccountTradeLog(self, requester, localID, tradeLog):
        if (requester == 'TRADEMANAGER'): self.__accountTradeLogAppendRequestQueues.append((localID, tradeLog))
    def __far_updateAccountPeriodicReport(self, requester, localID, timestamp, periodicReport):
        #[1]: Requester Check
        if requester != 'TRADEMANAGER': return

        #[2]: Report Update Queue Appending
        prUpdateRequest = (localID, timestamp, periodicReport)
        self.__accountPeriodicReportUpdateRequestQueues.append(prUpdateRequest)

    #<NEURALNETWORKMANAGER>
    def __far_loadNeuralNetworkDescriptions(self, requester, requestID):
        if (requester == 'NEURALNETWORKMANAGER'):
            neuralNetworkDescriptions = dict()
            self.__sql_neuralNetworks_cursor.execute("SELECT * FROM neuralNetworkDescriptions")
            dbTableData_neuralNetworkDescriptions = self.__sql_neuralNetworks_cursor.fetchall()
            for summaryRow in dbTableData_neuralNetworkDescriptions:
                #[1]: Neural Network Description
                dbID                           = summaryRow[0]
                neuralNetworkCode              = summaryRow[1]
                neuralNetworkType              = summaryRow[2]
                nKlines                        = summaryRow[3]
                hiddenLayers                   = json.loads(summaryRow[4])
                outputLayer                    = json.loads(summaryRow[5])
                generationTime                 = summaryRow[6]
                hashedControlKey               = summaryRow[7]
                networkConnectionDataTableName = summaryRow[8]
                trainingLogsTableName          = summaryRow[9]
                performanceTestLogsTableName   = summaryRow[10]
                #[2]: Network Connection Data
                networkConnectionData = list()
                if (networkConnectionDataTableName != None): 
                    self.__sql_neuralNetworks_cursor.execute('SELECT * FROM {:s}'.format(networkConnectionDataTableName))
                    dbTableData_networkConnectionData = self.__sql_neuralNetworks_cursor.fetchall()
                    for networkConnectionDataRow in dbTableData_networkConnectionData: networkConnectionData.append((networkConnectionDataRow[1], networkConnectionDataRow[2], json.loads(networkConnectionDataRow[3]), networkConnectionDataRow[4]))
                #[3]: Training Logs
                trainingLogs = list()
                if (trainingLogsTableName != None):
                    self.__sql_neuralNetworks_cursor.execute('SELECT * FROM {:s}'.format(trainingLogsTableName))
                    dbTableData_trainingLogs = self.__sql_neuralNetworks_cursor.fetchall()
                    for traingLogRow in dbTableData_trainingLogs: trainingLogs.append(json.loads(traingLogRow[1]))
                #[4]: Performance Test Logs
                performanceTestLogs = list()
                if (performanceTestLogsTableName != None):
                    self.__sql_neuralNetworks_cursor.execute('SELECT * FROM {:s}'.format(performanceTestLogsTableName))
                    dbTableData_performanceTestLogs = self.__sql_neuralNetworks_cursor.fetchall()
                    for performanceTestLogRow in dbTableData_performanceTestLogs: performanceTestLogs.append(json.loads(performanceTestLogRow[1]))
                #Finally
                self.__neuralNetworkDescriptions[neuralNetworkCode] = {'dbID':                           dbID,
                                                                       'neuralNetworkType':              neuralNetworkType,
                                                                       'nKlines':                        nKlines,
                                                                       'hiddenLayers':                   hiddenLayers,
                                                                       'outputLayer':                    outputLayer,
                                                                       'generationTime':                 generationTime,
                                                                       'hashedControlKey':               hashedControlKey, 
                                                                       'neuralNetworkConnectionData':    networkConnectionData,
                                                                       'trainingLogs':                   trainingLogs,
                                                                       'performanceTestLogs':            performanceTestLogs,
                                                                       'networkConnectionDataTableName': networkConnectionDataTableName,
                                                                       'trainingLogsTableName':          trainingLogsTableName,
                                                                       'performanceTestLogsTableName':   performanceTestLogsTableName}
                self.__neuralNetworCodesByID[dbID] = neuralNetworkCode
                neuralNetworkDescriptions[neuralNetworkCode] = {'neuralNetworkType':           neuralNetworkType,
                                                                'nKlines':                     nKlines,
                                                                'hiddenLayers':                hiddenLayers,
                                                                'outputLayer':                 outputLayer,
                                                                'generationTime':              generationTime,
                                                                'hashedControlKey':            hashedControlKey, 
                                                                'neuralNetworkConnectionData': networkConnectionData,
                                                                'trainingLogs':                trainingLogs,
                                                                'performanceTestLogs':         performanceTestLogs}
            return neuralNetworkDescriptions
        else: return None
    def __far_addNeuralNetworkDescription(self, requester, neuralNetworkCode, neuralNetworkDescription):
        if (requester == 'NEURALNETWORKMANAGER'):
            try:
                _neuralNetworkDescription_dbID = 0
                while (_neuralNetworkDescription_dbID in self.__neuralNetworCodesByID): _neuralNetworkDescription_dbID += 1
                _networkConnectionDataTableName = self.__createNeuralNetworkDataTable(neuralNetworkCode = neuralNetworkCode, tableType = 'NETWORKCONNECTIONDATA')
                _trainingLogsTableName          = self.__createNeuralNetworkDataTable(neuralNetworkCode = neuralNetworkCode, tableType = 'TRAININGLOGS')
                _performanceTestLogsTableName   = self.__createNeuralNetworkDataTable(neuralNetworkCode = neuralNetworkCode, tableType = 'PERFORMANCETESTLOGS')
                _neuralNetworkDescription = {'dbID':                           _neuralNetworkDescription_dbID,
                                             'neuralNetworkType':              neuralNetworkDescription['type'],
                                             'nKlines':                        neuralNetworkDescription['nKlines'],
                                             'hiddenLayers':                   neuralNetworkDescription['hiddenLayers'],
                                             'outputLayer':                    neuralNetworkDescription['outputLayer'],
                                             'generationTime':                 neuralNetworkDescription['generationTime'],
                                             'hashedControlKey':               neuralNetworkDescription['hashedControlKey'], 
                                             'neuralNetworkConnectionData':    neuralNetworkDescription['connections'],
                                             'trainingLogs':                   list(),
                                             'performanceTestLogs':            list(),
                                             'networkConnectionDataTableName': _networkConnectionDataTableName,
                                             'trainingLogsTableName':          _trainingLogsTableName,
                                             'performanceTestLogsTableName':   _performanceTestLogsTableName}
                #Save Network Connection Data
                _neuralNetworkConnectionData_formatted = list()
                for _index, _cData in enumerate(neuralNetworkDescription['connections']): _neuralNetworkConnectionData_formatted.append((_index, _cData[0], _cData[1], json.dumps(_cData[2]), _cData[3]))
                self.__sql_neuralNetworks_cursor.executemany("INSERT INTO {:s} (id, type, layerAddress, tensorAddress, value) VALUES (?,?,?,?,?)".format(_networkConnectionDataTableName), _neuralNetworkConnectionData_formatted)
                #Save account description to the db file
                self.__sql_neuralNetworks_cursor.execute("""INSERT INTO neuralNetworkDescriptions (id,
                                                                                                   neuralNetworkCode, 
                                                                                                   neuralNetworkType,
                                                                                                   nKlines,
                                                                                                   hiddenLayers,
                                                                                                   outputLayer,
                                                                                                   generationTime,
                                                                                                   hashedControlKey, 
                                                                                                   networkConnectionDataTableName,
                                                                                                   trainingLogsTableName,
                                                                                                   performanceTestLogsTableName) 
                                                                                                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                                                                                                   (_neuralNetworkDescription_dbID,
                                                                                                    neuralNetworkCode,
                                                                                                    neuralNetworkDescription['type'],
                                                                                                    neuralNetworkDescription['nKlines'],
                                                                                                    json.dumps(neuralNetworkDescription['hiddenLayers']),
                                                                                                    json.dumps(neuralNetworkDescription['outputLayer']),
                                                                                                    neuralNetworkDescription['generationTime'],
                                                                                                    neuralNetworkDescription['hashedControlKey'],
                                                                                                    _networkConnectionDataTableName,
                                                                                                    _trainingLogsTableName,
                                                                                                    _performanceTestLogsTableName))
                #Commit the db file
                self.__sql_neuralNetworks_connection.commit()
                #Save the temporarily created neural network instance
                self.__neuralNetworkDescriptions[neuralNetworkCode]          = _neuralNetworkDescription
                self.__neuralNetworCodesByID[_neuralNetworkDescription_dbID] = neuralNetworkCode
            except Exception as e:
                try:    self.__sql_neuralNetworks_cursor.execute(f"DROP TABLE {_networkConnectionDataTableName}")
                except: pass
                try:    self.__sql_neuralNetworks_cursor.execute(f"DROP TABLE {_trainingLogsTableName}")
                except: pass
                try:    self.__sql_neuralNetworks_cursor.execute(f"DROP TABLE {_performanceTestLogsTableName}")
                except: pass
                try:    self.__sql_neuralNetworks_cursor.execute("DELETE from neuralNetworkDescriptions where neuralNetworkCode = ?", (neuralNetworkCode,))
                except: pass
                self.__sql_neuralNetworks_connection.commit()
                if (_neuralNetworkDescription_dbID in self.__neuralNetworCodesByID): del self.__neuralNetworCodesByID[_neuralNetworkDescription_dbID]
                if (neuralNetworkCode in self.__neuralNetworkDescriptions):          del self.__neuralNetworkDescriptions[neuralNetworkCode]
                self.__logger(message = f"An unexpected error occurred while attempting to save a Neural Network description for {str(neuralNetworkCode)}\n * {str(e)}", logType = 'Error', color = 'light_red')
    def __far_removeNeuralNetworkDescription(self, requester, neuralNetworkCode):
        if (requester == 'NEURALNETWORKMANAGER'):
            if (neuralNetworkCode in self.__neuralNetworkDescriptions):
                for _neuralNetworkDescription_dbID in self.__neuralNetworCodesByID:
                    if (self.__neuralNetworCodesByID[_neuralNetworkDescription_dbID] == neuralNetworkCode): neuralNetworkDescription_dbID = _neuralNetworkDescription_dbID; break
                self.__sql_neuralNetworks_cursor.execute("DROP TABLE {:s}".format(self.__neuralNetworkDescriptions[neuralNetworkCode]['networkConnectionDataTableName']))
                self.__sql_neuralNetworks_cursor.execute("DROP TABLE {:s}".format(self.__neuralNetworkDescriptions[neuralNetworkCode]['trainingLogsTableName']))
                self.__sql_neuralNetworks_cursor.execute("DROP TABLE {:s}".format(self.__neuralNetworkDescriptions[neuralNetworkCode]['performanceTestLogsTableName']))
                self.__sql_neuralNetworks_cursor.execute("DELETE from neuralNetworkDescriptions where neuralNetworkCode = ?", (neuralNetworkCode,))
                self.__sql_neuralNetworks_connection.commit()
                del self.__neuralNetworCodesByID[neuralNetworkDescription_dbID]
                del self.__neuralNetworkDescriptions[neuralNetworkCode]
    def __far_updateNeuralNetworkConnectionData(self, requester, neuralNetworkCode, newNeuralNetworkConnectionData):
        if (requester == 'NEURALNETWORKMANAGER'): self.__neuralNetworkConnectionDataUpdateRequestQueues.append((neuralNetworkCode, newNeuralNetworkConnectionData))
    def __far_addNeuralNetworkTrainigLog(self, requester, neuralNetworkCode, trainingLog):
        if (requester == 'NEURALNETWORKMANAGER'): self.__neuralNetworkTrainingLogAppendRequestQueues.append((neuralNetworkCode, trainingLog))
    def __far_addNeuralNetworkPerformanceTestLog(self, requester, neuralNetworkCode, performanceTestLog):
        if (requester == 'NEURALNETWORKMANAGER'): self.__neuralNetworkPerformanceTestLogAppendRequestQueues.append((neuralNetworkCode, performanceTestLog))

    #<GUI>
    def __far_updateConfiguration(self, requester, requestID, newConfiguration):
        if (requester == 'GUI'):
            #Print Update
            self.__config_DataManager['print_Update'] = newConfiguration['print_Update']
            #Print Warning
            self.__config_DataManager['print_Warning'] = newConfiguration['print_Warning']
            #Print Error
            self.__config_DataManager['print_Error'] = newConfiguration['print_Error']
            #Save Config # Update Announcement
            self.__saveDataManagerConfig()
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CONFIGURATION', prdContent = self.__config_DataManager)
            return {'result': True, 'message': "Configuration Successfully Updated!", 'configuration': self.__config_DataManager}
    def __far_fetchSimulationTradeLogs(self, requester, requestID, simulationCode):
        if (requester == 'GUI'):
            if (simulationCode in self.__simulationDescriptions):
                _tradeLogsTableName = self.__simulationDescriptions[simulationCode]['tradeLogsTableName']
                if (_tradeLogsTableName != None):
                    try:
                        self.__sql_simulations_cursor.execute('SELECT * FROM {:s}'.format(_tradeLogsTableName))
                        _tradeLogs_db = self.__sql_simulations_cursor.fetchall()
                        tradeLogs = list()
                        for _tradeLog_db in _tradeLogs_db:
                            _log_formatted = json.loads(_tradeLog_db[1])
                            _log_formatted['logIndex'] = _tradeLog_db[0]
                            tradeLogs.append(_log_formatted)
                        return                    {'result': True,  'simulationCode': simulationCode, 'tradeLogs': tradeLogs, 'failureType': None}
                    except Exception as e: return {'result': False, 'simulationCode': simulationCode, 'tradeLogs': None,      'failureType': str(e)}
                return                            {'result': False, 'simulationCode': simulationCode, 'tradeLogs': None,      'failureType': 'TRADELOGSTABLENOTFOUND'}
            else: return                          {'result': False, 'simulationCode': simulationCode, 'tradeLogs': None,      'failureType': 'SIMULATIONCODE'}
        else: return                              {'result': False, 'simulationCode': simulationCode, 'tradeLogs': None,      'failureType': 'REQUESTERERROR'}
    def __far_fetchSimulationPeriodicReports(self, requester, requestID, simulationCode):
        if (requester == 'GUI'):
            if (simulationCode in self.__simulationDescriptions):
                _periodicReportsTableName = self.__simulationDescriptions[simulationCode]['periodicReportsTableName']
                if (_periodicReportsTableName != None):
                    try:
                        self.__sql_simulations_cursor.execute('SELECT * FROM {:s}'.format(_periodicReportsTableName))
                        _periodicReports_db = self.__sql_simulations_cursor.fetchall()
                        periodicReports = dict()
                        for _pReport_db in _periodicReports_db:
                            _pTS  = _pReport_db[1]
                            _report = json.loads(_pReport_db[2])
                            periodicReports[_pTS] = _report
                        return                    {'result': True,  'simulationCode': simulationCode, 'periodicReports': periodicReports, 'failureType': None}
                    except Exception as e: return {'result': False, 'simulationCode': simulationCode, 'periodicReports': None,            'failureType': str(e)}
                return                            {'result': False, 'simulationCode': simulationCode, 'periodicReports': None,            'failureType': 'PERIODICREPORTSTABLENOTFOUND'}
            else: return                          {'result': False, 'simulationCode': simulationCode, 'periodicReports': None,            'failureType': 'SIMULATIONCODE'}
        else: return                              {'result': False, 'simulationCode': simulationCode, 'periodicReports': None,            'failureType': 'REQUESTERERROR'}
    def __far_fetchAccountTradeLog(self, requester, requestID, localID):
        if (requester == 'GUI'):
            if (localID in self.__accountDescriptions):
                try:
                    accountTradeLogsTableName = self.__accountDescriptions[localID]['tradeLogsTableName']
                    self.__sql_accounts_cursor.execute('SELECT * FROM {:s}'.format(accountTradeLogsTableName))
                    dbTableData_tradeLogs = self.__sql_accounts_cursor.fetchall()
                    tradeLogs = list()
                    for _tradeLog_db in dbTableData_tradeLogs:
                        _log_formatted = json.loads(_tradeLog_db[1])
                        _log_formatted['logIndex'] = _tradeLog_db[0]
                        tradeLogs.append(_log_formatted)
                    return                    {'result': True,  'localID': localID, 'tradeLogs': tradeLogs, 'failureType': None}
                except Exception as e: return {'result': False, 'localID': localID, 'tradeLogs': None,      'failureType': str(e)}
            else: return                      {'result': False, 'localID': localID, 'tradeLogs': None,      'failureType': 'ACCOUNTLOCALID'}
        else: return                          {'result': False, 'localID': localID, 'tradeLogs': None,      'failureType': 'REQUESTERERROR'}
    def __far_fetchAccountPeriodicReports(self, requester, requestID, localID):
        #[1]: Requester Check
        if requester != 'GUI': return {'result': False, 'localID': localID, 'periodicReports': None, 'failureType': 'REQUESTERERROR'}

        #[2]: Account Check
        if localID not in self.__accountDescriptions: return {'result': False, 'localID': localID, 'periodicReports': None, 'failureType': 'LOCALID'}

        #[3]: DB Table Check
        pReports_tableName = self.__accountDescriptions[localID]['periodicReportsTableName']
        if pReports_tableName is None: return {'result': False, 'localID': localID, 'periodicReports': None, 'failureType': 'PERIODICREPORTSTABLENOTFOUND'}

        #[4]: Fetch Attempt
        try:
            self.__sql_accounts_cursor.execute(f'SELECT * FROM {pReports_tableName}')
            pReports_DB = self.__sql_accounts_cursor.fetchall()
            pReports    = dict()
            for pReport_DB in pReports_DB:
                timestamp = pReport_DB[0]
                report    = json.loads(pReport_DB[1])
                pReports[timestamp] = report
            return {'result': True,  'localID': localID, 'periodicReports': pReports, 'failureType': None}
        except Exception as e:
            return {'result': False, 'localID': localID, 'periodicReports': None, 'failureType': str(e)}

    #<#COMMON#>
    def __far_fetchKlines(self, requester, requestID, symbol, fetchRange):
        queue = {'requester': requester, 'requestID': requestID, 'currencySymbol': symbol, 'fetchRange': fetchRange}
        self.__klineFetchRequestQueues.append(queue)
    def __far_registerCurrecnyInfoSubscription(self, requester, symbol):
        if (symbol not in self.__currencyInfoSubscribers): self.__currencyInfoSubscribers[symbol] = set()
        self.__currencyInfoSubscribers[symbol].add(requester)
        self.ipcA.sendPRDEDIT(targetProcess = requester, prdAddress = ('CURRENCIES', symbol), prdContent = self.__klineDataInfo[symbol])
        self.ipcA.sendFAR(targetProcess = requester, functionID = 'onCurrenciesUpdate', functionParams = {'updatedContents': [{'symbol': symbol, 'id': '_ONFIRSTSUBSCRIPTION'},]}, farrHandler = None)
    def __far_unregisterCurrecnyInfoSubscription(self, requester, symbol):
        if ((symbol in self.__currencyInfoSubscribers) and (requester in self.__currencyInfoSubscribers[symbol])): self.__currencyInfoSubscribers[symbol].remove(requester)
        self.ipcA.sendPRDREMOVE(targetProcess = requester, prdAddress = ('CURRENCIES', symbol))
    #FAR & FARR Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Auxillary Functions --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __dataRange_getClassification(self, dataRange1, dataRange2):
        """
        classification == 0b1111: DR2 completely outside on the left of DR1
        classification == 0b1011: the right of DR2 and the left of DR1 overlapped
        classification == 0b0011: DR2 completely inside of DR1
        classification == 0b0010: the left of DR2 and the right of DR1 overlapped
        classification == 0b0000: DR2 completely outside on the right of DR1
        classification == 0b1010: DR1 completely inside of DR2
        """
        classification = 0b0000
        classification += 0b1000*(0 < dataRange1[0]-dataRange2[0])
        classification += 0b0100*(0 < dataRange1[0]-dataRange2[1])
        classification += 0b0010*(0 <= dataRange1[1]-dataRange2[0])
        classification += 0b0001*(0 <= dataRange1[1]-dataRange2[1])
        return classification
    #Manager Auxillary Functions END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------