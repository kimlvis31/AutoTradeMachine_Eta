#ATM Modules
import ipc
import constants
from managers.workers.trade_manager.trade_configurations             import TradeConfigurations
from managers.workers.trade_manager.currency_analysis_configurations import CurrencyAnalysisConfigurations
from managers.workers.trade_manager.currency_analyses                import CurrencyAnalyses
from managers.workers.trade_manager.accounts                         import Accounts
from managers.workers.trade_manager.virtual_server                   import VirtualServer

#Python Modules
import time
import termcolor
import json
import os
import traceback
from datetime import datetime

#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT

class TradeManager:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA, analyzerProcessNames):
        print(termcolor.colored("   Initializing", 'green'), termcolor.colored("TRADEMANAGER Manager", 'light_blue'), termcolor.colored("--------------------------------------------------------------------------------------------------------------", 'green'))
        
        #[1]: System
        self.path_project = path_project
        self.ipcA         = ipcA
        self.__config_TradeManager = {'print_Update':  True,
                                      'print_Warning': True,
                                      'print_Error':   True}
        self.__readTradeManagerConfig()
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CONFIGURATION', prdContent = self.__config_TradeManager.copy())

        #[2]: Market Currencies
        self.__currencies           = dict()
        self.__currencies_lastKline = dict()

        #[3]: Trade Configurations
        self.__tradeConfigurations = TradeConfigurations(path_project = path_project, 
                                                         ipcA         = ipcA, 
                                                         tmConfig     = self.__config_TradeManager)

        #[4]: Currency Analysis Configurations
        self.__currencyAnalysisConfigurations = CurrencyAnalysisConfigurations(path_project = path_project, 
                                                                               ipcA         = ipcA, 
                                                                               tmConfig     = self.__config_TradeManager)

        #[5]: Currency Analyses
        self.__currencyAnalyses = CurrencyAnalyses(path_project                   = path_project, 
                                                   ipcA                           = ipcA, 
                                                   tmConfig                       = self.__config_TradeManager, 
                                                   analyzerProcessNames           = analyzerProcessNames,
                                                   currencies                     = self.__currencies,
                                                   currencyAnalysisConfigurations = self.__currencyAnalysisConfigurations)

        #[6]: Accounts & Virtual Server
        self.__virtualServer = VirtualServer(tmConfig   = self.__config_TradeManager,
                                             currencies = self.__currencies)
        self.__accounts = Accounts(ipcA                 = ipcA, 
                                   tmConfig             = self.__config_TradeManager, 
                                   currencies           = self.__currencies, 
                                   currencies_lastKline = self.__currencies_lastKline, 
                                   virtualServer        = self.__virtualServer,
                                   currencyAnalyses     = self.__currencyAnalyses, 
                                   tradeConfigurations  = self.__tradeConfigurations)

        #[7]: FAR Registration
        self.ipcA.addFARHandler('onCurrenciesUpdate',    self.__far_onCurrenciesUpdate,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #DATAMANAGER
        self.ipcA.addFARHandler('updateConfiguration',   self.__far_updateConfiguration,   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #GUI
        self.ipcA.addFARHandler('onKlineStreamReceival', self.__far_onKlineStreamReceival, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #BINANCEAPI
        self.ipcA.addDummyFARHandler(functionID = 'onDepthStreamReceival')                                                                                 #BINANCEAPI
        self.ipcA.addDummyFARHandler(functionID = 'onAggTradeStreamReceival')                                                                              #BINANCEAPI

        #[8]: Process Control
        self.__processLoopContinue = True

        print(termcolor.colored("   TRADEMANAGER Manager", 'light_blue'), termcolor.colored("Initialization Complete! --------------------------------------------------------------------------------------------------", 'green'))
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    
    
    #Manager Process Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        #[1]: Get currency info from DATAMANGER
        self.__currencies.update(self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = 'CURRENCIES'))

        #[2]: Currency Analyses Update
        cas = self.__currencyAnalyses
        for symbol, currency in self.__currencies.items():
            status = None if currency['info_server'] is None else currency['info_server']['status']
            cas.onCurrencyStatusUpdate(symbol = symbol, status = status)
        
        #[4]: Start Process Loop
        while self.__processLoopContinue:
            #[4-1]: Process any existing FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()

            #[4-2]: Virtual Server Processing
            self.__virtualServer.process()

            #[4-3]: Accounts Processing
            self.__accounts.process()

            #[4-4]: Updates Processing
            self.process_TradeConfigurationUpdates()
            self.process_CurrencyAnalysisConfigurationUpdates()
            self.process_CurrencyAnalysisUpdates()

            #[4-5]: Loop Sleep
            time.sleep(0.001)

    def process_TradeConfigurationUpdates(self):
        accounts = self.__accounts
        for update in self.__tradeConfigurations.getUpdates():
            uType  = update['type']
            tcCode = update['code']
            if uType == 'NEW':
                accounts.onTradeConfigurationAdd(tradeConfigurationCode = tcCode)

    def process_CurrencyAnalysisConfigurationUpdates(self):
        cas = self.__currencyAnalyses
        for update in self.__currencyAnalysisConfigurations.getUpdates():
            uType   = update['type']
            cacCode = update['code']
            if uType == 'NEW':
                cas.onNewCurrencyAnalysisConfiguration(cacCode = cacCode)

    def process_CurrencyAnalysisUpdates(self):
        accounts = self.__accounts
        for update in self.__currencyAnalyses.getUpdates():
            uType  = update['type']
            caCode = update['code']
            if uType == 'NEW':
                accounts.onCurrencyAnalysisAdd(currencyAnalysisCode = caCode)

    def terminate(self, requester):
        self.__processLoopContinue = False
    #Manager Process Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Internal Functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #---Process Configuration
    def __readTradeManagerConfig(self):
        #[1]: Configuration File Read
        try:
            config_dir = os.path.join(self.path_project, 'configs', 'tmConfig.config')
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
        self.__config_TradeManager = {'print_Update':  print_update,
                                      'print_Warning': print_warning,
                                      'print_Error':   print_error}
        self.__saveTradeManagerConfig()
    
    def __saveTradeManagerConfig(self):
        #[1]: Reformat config for save
        config = self.__config_TradeManager
        config_toSave = {'print_Update':  config['print_Update'],
                         'print_Warning': config['print_Warning'],
                         'print_Error':   config['print_Error']}

        #[2]: Save the reformatted configuration file
        config_dir = os.path.join(self.path_project, 'configs', 'tmConfig.config')
        try:
            with open(config_dir, 'w') as f:
                json.dump(config_toSave, f, indent=4)
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Save Trade Manager Configuration. User Attention Strongly Advised"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')

    #---System
    def __logger(self, message, logType, color):
        if (self.__config_TradeManager[f'print_{logType}'] == True): 
            _time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
            print(termcolor.colored(f"[TRADEMANAGER-{_time_str}] {message}", color))
    #Manager Internal Functions END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #FAR Handlers -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<DATAMANAGER>
    def __far_onCurrenciesUpdate(self, requester, updatedContents):
        #[1]: Source Check
        if requester != 'DATAMANAGER':
            return

        #[2]: Instances
        currencies  = self.__currencies
        cas         = self.__currencyAnalyses
        accounts    = self.__accounts
        vs          = self.__virtualServer
        func_getPRD = self.ipcA.getPRD

        #[3]: Updates Read 
        for uContent in updatedContents:
            symbol    = uContent['symbol']
            contentID = uContent['id']
            #[3-1]: Currency Dict Update
            currency = func_getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol))
            currencies[symbol] = currency

            #[3-2]: Status Update Check
            statusUpdated = False
            if contentID == '_ADDED':
                accounts.onNewCurrency(symbol = symbol)
                vs.onNewCurrency(symbol       = symbol)
                statusUpdated = True
            else:
                if contentID[0] == 'info_server':
                    try:    contentID_1 = contentID[1]
                    except: contentID_1 = None
                    if   contentID_1 is None:     statusUpdated = True
                    elif contentID_1 == 'status': statusUpdated = True

            #[3-3]: Status Update Response
            if statusUpdated:
                status = None if currency['info_server'] is None else currency['info_server']['status']
                cas.onCurrencyStatusUpdate(symbol = symbol, status = status)

    #<GUI>
    def __far_updateConfiguration(self, requester, requestID, newConfiguration):
        #[1]: Source Check
        if requester != 'GUI':
            return
        
        #[2]: Configuration Update
        tmConfig = self.__config_TradeManager
        tmConfig['print_Update']  = newConfiguration['print_Update']
        tmConfig['print_Warning'] = newConfiguration['print_Warning']
        tmConfig['print_Error']   = newConfiguration['print_Error']
        self.__saveTradeManagerConfig()

        #[3]: Announcement
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CONFIGURATION', prdContent = self.__config_TradeManager)

        #[4]: Result Return
        return {'result':        True, 
                'message':       "Configuration Successfully Updated!", 
                'configuration': self.__config_TradeManager}
    
    #<BINANCEAPI>
    def __far_onKlineStreamReceival(self, requester, symbol, kline):
        #[1]: Source Check
        if requester != 'BINANCEAPI':
            return
        
        #[2]: Record the last close price
        self.__currencies_lastKline[symbol] = kline

        #[3]: Virtual Server & Accounts Response
        self.__virtualServer.onKlineStreamReceival(symbol = symbol, kline = kline)
        self.__accounts.onKlineStreamReceival(symbol      = symbol, kline = kline)
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
