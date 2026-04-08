#ATM Modules
from analyzers import KLINDEX_OPENTIME, KLINDEX_CLOSETIME, KLINDEX_OPENPRICE, KLINDEX_CLOSEPRICE, KLINDEX_HIGHPRICE, KLINDEX_LOWPRICE
import ipc
import auxiliaries
import constants
import rqpfunctions
from managers.workers.trade_manager.trade_configurations             import TradeConfigurations
from managers.workers.trade_manager.currency_analysis_configurations import CurrencyAnalysisConfigurations
from managers.workers.trade_manager.currency_analyses                import CurrencyAnalyses
from managers.workers.trade_manager.account                          import Account
from managers.workers.trade_manager.virtual_server                   import VirtualServer
import managers.workers.currency_analysis.currency_analysis as caWorker

#Python Modules
import time
import termcolor
import json
import os
import pprint
import bcrypt
import math
import random
import base64
import hashlib
import traceback
from datetime            import datetime
from collections         import deque
from cryptography.fernet import Fernet

#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT

KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S

_CURRENCYANALYSIS_STATUSINTERPRETATIONS = {caWorker.STATUS_WAITINGNEURALNETWORK: 'WAITINGNEURALNETWORK',
                                           caWorker.STATUS_WAITINGSTREAM:        'WAITINGSTREAM',
                                           caWorker.STATUS_WAITINGDATAAVAILABLE: 'WAITINGDATAAVAILABLE',
                                           caWorker.STATUS_QUEUED:               'QUEUED',
                                           caWorker.STATUS_FETCHING:             'FETCHING',
                                           caWorker.STATUS_INITIALANALYZING:     'INITIALANALYZING',
                                           caWorker.STATUS_ANALYZING:            'ANALYZING',
                                           caWorker.STATUS_ERROR:                'ERROR'}

_ACCOUNT_ACCOUNTTYPE_VIRTUAL    = 'VIRTUAL'
_ACCOUNT_ACCOUNTTYPE_ACTUAL     = 'ACTUAL'
_ACCOUNT_ACCOUNTSTATUS_INACTIVE = 'INACTIVE'
_ACCOUNT_ACCOUNTSTATUS_ACTIVE   = 'ACTIVE'
_ACCOUNT_UPDATEINTERVAL_NS                      = 200e6
_ACCOUNT_PERIODICREPORT_ANNOUNCEMENTINTERVAL_NS = 60*1e9
_ACCOUNT_PERIODICREPORT_INTERVALID              = auxiliaries.KLINE_INTERVAL_ID_5m
_ACCOUNT_READABLEASSETS = ('USDT', 'USDC')
_ACCOUNT_ASSETPRECISIONS = {'USDT': 8,
                            'USDC': 8}
_ACCOUNT_BASEASSETALLOCATABLERATIO = 0.95
_GUIANNOUCEMENT_ASSETDATANAMES = {'marginBalance',
                                  'walletBalance',
                                  'isolatedWalletBalance',
                                  'isolatedPositionInitialMargin',
                                  'crossWalletBalance',
                                  'openOrderInitialMargin',
                                  'crossPositionInitialMargin',
                                  'crossMaintenanceMargin',
                                  'unrealizedPNL',
                                  'isolatedUnrealizedPNL',
                                  'crossUnrealizedPNL',
                                  'availableBalance',
                                  'assumedRatio',
                                  'allocatableBalance',
                                  'allocationRatio',
                                  'allocatedBalance',
                                  'weightedAssumedRatio',
                                  'commitmentRate',
                                  'riskLevel'}
_GUIANNOUCEMENT_POSITIONDATANAMES = {'tradeStatus',
                                     'tradable',
                                     'currencyAnalysisCode',
                                     'tradeConfigurationCode',
                                     'tradeControlTracker',
                                     'quantity',
                                     'entryPrice',
                                     'leverage',
                                     'isolated',
                                     'isolatedWalletBalance',
                                     'positionInitialMargin',
                                     'openOrderInitialMargin',
                                     'maintenanceMargin',
                                     'currentPrice',
                                     'unrealizedPNL',
                                     'liquidationPrice',
                                     'assumedRatio',
                                     'priority',
                                     'allocatedBalance',
                                     'maxAllocatedBalance',
                                     'weightedAssumedRatio',
                                     'commitmentRate',
                                     'riskLevel'}
_VIRTUALACCOUNTDBANNOUNCEMENT_ASSETDATANAMES = {'crossWalletBalance',}
_VIRTUALACCOUNTDBANNOUNCEMENT_POSITIONDATANAMES = {'quantity',
                                                   'entryPrice',
                                                   'leverage',
                                                   'isolated',
                                                   'isolatedWalletBalance'}
_VIRTUALTRADE_MARKETTRADINGFEE = 0.0005
_VIRTUALTRADE_LIQUIDATIONFEE   = 0.0100
_ACTUALTRADE_MARKETTRADINGFEE  = 0.0005

_TRADE_ANALYSISHANDLINGFILTER_KLINECLOSEPRICE = 0.005
_TRADE_MAXIMUMOCRGENERATIONATTEMPTS           = 5

_TRADE_TRADEHANDLER_LIFETIME_NS = int(KLINTERVAL_S*1e9/5)

_VIRTUALTRADE_SERVER_PROBABILITY_SUCCESS             = 1.00
_VIRTUALTRADE_SERVER_PROBABILITY_INCOMPLETEEXECUTION = 0.00

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
        """
        self.__tradeConfigurations        = dict()
        self.__tradeConfigurations_loaded = dict()
        """

        #[4]: Currency Analysis Configurations
        self.__currencyAnalysisConfigurations = CurrencyAnalysisConfigurations(path_project = path_project, 
                                                                               ipcA         = ipcA, 
                                                                               tmConfig     = self.__config_TradeManager)
        """
        self.__currencyAnalysisConfigurations = dict()
        """

        #[5]: Currency Analyses
        self.__currencyAnalyses = CurrencyAnalyses(path_project                   = path_project, 
                                                   ipcA                           = ipcA, 
                                                   tmConfig                       = self.__config_TradeManager, 
                                                   analyzerProcessNames           = analyzerProcessNames,
                                                   currencies                     = self.__currencies,
                                                   currencyAnalysisConfigurations = self.__currencyAnalysisConfigurations)
        """
        self.__currencyAnalysis                 = dict()
        self.__currencyAnalysis_bySymbol        = dict()
        self.__currencyAnalysis_analysisResults = dict()
        """

        #[6]: Accounts & Virtual Server
        self.__virtualServer = VirtualServer(path_project = path_project, ipcA = ipcA, tmConfig = self.__config_TradeManager)
        self.__accounts      = dict()
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'ACCOUNTS', prdContent = self.__accounts)
        """
        self.__accounts_virtualServer = dict()
        self.__accountInstanceGenerationRequests = dict()
        """

        #[7]: FAR Registration
        self.ipcA.addFARHandler('onCurrenciesUpdate',         self.__far_onCurrenciesUpdate,         executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #DATAMANAGER
        self.ipcA.addFARHandler('updateConfiguration',        self.__far_updateConfiguration,        executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        self.ipcA.addFARHandler('addAccount',                 self.__far_addAccount,                 executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        self.ipcA.addFARHandler('removeAccount',              self.__far_removeAccount,              executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        self.ipcA.addFARHandler('activateAccount',            self.__far_activateAccount,            executionThread = _IPC_THREADTYPE_MT, immediateResponse = False) #GUI
        self.ipcA.addFARHandler('deactivateAccount',          self.__far_deactivateAccount,          executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        self.ipcA.addFARHandler('setAccountTradeStatus',      self.__far_setAccountTradeStatus,      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        self.ipcA.addFARHandler('transferBalance',            self.__far_transferBalance,            executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        self.ipcA.addFARHandler('updateAllocationRatio',      self.__far_updateAllocationRatio,      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        self.ipcA.addFARHandler('forceClearPosition',         self.__far_forceClearPosition,         executionThread = _IPC_THREADTYPE_MT, immediateResponse = False) #GUI
        self.ipcA.addFARHandler('updatePositionTradeStatus',  self.__far_updatePositionTradeStatus,  executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        self.ipcA.addFARHandler('updatePositionReduceOnly',   self.__far_updatePositionReduceOnly,   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        self.ipcA.addFARHandler('updatePositionTraderParams', self.__far_updatePositionTraderParams, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        self.ipcA.addFARHandler('resetTradeControlTracker',   self.__far_resetTradeControlTracker,   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        self.ipcA.addFARHandler('verifyPassword',             self.__far_verifyPassword,             executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        self.ipcA.addFARHandler('onKlineStreamReceival',      self.__far_onKlineStreamReceival,      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #BINANCEAPI
        self.ipcA.addDummyFARHandler(functionID = 'onDepthStreamReceival')                                                                                            #BINANCEAPI
        self.ipcA.addDummyFARHandler(functionID = 'onAggTradeStreamReceival')                                                                                         #BINANCEAPI
        self.ipcA.addFARHandler('onAccountDataReceival',      self.__far_onAccountDataReceival,      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #BINANCEAPI

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
        
        #[3]: Get Account Data from DATAMANAGER
        self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                          functionID     = 'loadAccountDescriptions',
                          functionParams = None, 
                          farrHandler    = self.__farr_onAccountDescriptionLoadRequestResponse)
        
        #[4]: Start Process Loop
        while self.__processLoopContinue:
            #[4-1]: Process any existing FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()

            """
            #Process Any Virtual Order Requests
            self.__virtualServer.process()
            #Update Accounts
            self.__updateAccounts()
            """

            #[4-2]: Updates Processing
            self.process_TradeConfigurationUpdates()
            self.process_CurrencyAnalysisConfigurationUpdates()
            self.process_CurrencyAnalysisUpdates()

            #[4-3]: Loop Sleep
            time.sleep(0.001)

    def process_TradeConfigurationUpdates(self):
        for update in self.__tradeConfigurations.getUpdates():
            uType  = update['type']
            tcCode = update['code']

            if uType == 'NEW':
                pass

    def process_CurrencyAnalysisConfigurationUpdates(self):
        cas = self.__currencyAnalyses
        for update in self.__currencyAnalysisConfigurations.getUpdates():
            uType   = update['type']
            cacCode = update['code']

            if uType == 'NEW':
                cas.onNewCurrencyAnalysisConfiguration(cacCode = cacCode)

    def process_CurrencyAnalysisUpdates(self):
        for update in self.__currencyAnalyses.getUpdates():
            uType  = update['type']
            caCode = update['code']

            if uType == 'NEW':
                pass

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

    #---Accounts
    def __addAccount(self, localID, buid, accountType, password, newAccount = True, assets = None, positions = None, lastPeriodicReport = None, silentTerminal = False, sendIPCM = True):
        #[1]: Account Name Validity Test
        if ((localID != None) and (localID not in self.__accounts)): validityTest_accountName = True
        else:                                                        validityTest_accountName = False
        #[2]: Account Generation
        if (validityTest_accountName == True):
            try:
                #Initial Format
                _account = {'accountType':    accountType,
                            'buid':           None,
                            'hashedPassword': None,
                            'assets':         dict(),
                            'positions':      dict(),
                            'status':         None,
                            'tradeStatus':    False,
                            '_lastUpdated':   0,
                            '_periodicReport':                  None,
                            '_periodicReport_timestamp':        None,
                            '_periodicReport_lastAnnounced_ns': 0}
                self.__accounts[localID] = _account
                if (accountType == _ACCOUNT_ACCOUNTTYPE_VIRTUAL):
                    _account_virtualServer = {'assets':    dict(),
                                              'positions': dict(),
                                              '_marginTypeControlRequests': list(),
                                              '_leverageControlRequests':   list(),
                                              '_orderCreationRequests':     dict(),
                                              '_nonZeroQuantityPositions_isolated': list(),
                                              '_nonZeroQuantityPositions_cross':    list(),
                                              '_lastUpdated':               0}
                    self.__accounts_virtualServer[localID] = _account_virtualServer
                #BUID (Binance User ID)
                if   (accountType == _ACCOUNT_ACCOUNTTYPE_VIRTUAL): _account['buid'] = None
                elif (accountType == _ACCOUNT_ACCOUNTTYPE_ACTUAL):  _account['buid'] = int(buid)
                #Password
                if (newAccount == True): _account['hashedPassword'] = bcrypt.hashpw(password=password.encode(encoding = "utf-8"), salt=bcrypt.gensalt())
                else:                    _account['hashedPassword'] = password
                #Status
                if   (accountType == _ACCOUNT_ACCOUNTTYPE_VIRTUAL): _account['status'] = _ACCOUNT_ACCOUNTSTATUS_ACTIVE
                elif (accountType == _ACCOUNT_ACCOUNTTYPE_ACTUAL):  _account['status'] = _ACCOUNT_ACCOUNTSTATUS_INACTIVE
                #Assets & Positions Formatting
                for _assetName in _ACCOUNT_READABLEASSETS: self.__formatNewAccountAsset(localID = localID, assetName = _assetName)
                for _currencySymbol in self.__currencies:
                    if (self.__currencies[_currencySymbol]['quoteAsset'] in _ACCOUNT_READABLEASSETS): self.__formatNewAccountPosition(localID = localID, currencySymbol = _currencySymbol)
                for _assetName in _ACCOUNT_READABLEASSETS: self.__sortPositionSymbolsByPriority(localID = localID, assetName = _assetName)
                #If is not a new account, import assets & positions, and last periodic report if needed
                if (newAccount == False): 
                    self.__updateAccount(localID               = localID, importedData = {'source': 'DB', 'positions': positions, 'assets': assets})
                    self.__updateAccountPeriodicReport(localID = localID, importedData = lastPeriodicReport)
                #If new account, send account data save request to DATAMANAGER
                if (newAccount == True): self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'addAccountDescription', functionParams = {'localID': localID, 'accountDescription': _account}, farrHandler = None)
                #If this needs to be sent via PRD and FAR separately, send it
                if (sendIPCM == True):
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID), prdContent = self.__accounts[localID])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'ADDED', 'updatedContent': localID}, farrHandler = None)
                _addResult = 1
            except Exception as e: _addResult = -1; _addResult_exception = e
        else:                      _addResult = -2
        #[3]: Result Announcing
        if (silentTerminal == False):
            if   (_addResult ==  1): self.__logger(message = f"Account '{localID}' Successfully Added!",                                                   logType = 'Update',  color = 'light_green')
            elif (_addResult == -1): self.__logger(message = f"Account '{localID}' Add Failed Due To An Unexpected Error\n * {str(_addResult_exception)}", logType = 'Error',   color = 'light_red')
            elif (_addResult == -2): self.__logger(message = f"Account '{localID}' Add Failed. 'Check Account Name'",                                      logType = 'Warning', color = 'light_red')
        if (sendIPCM == True):
            if   (_addResult ==  1): return {'result': True,  'message': "Account '{:s}' Successfully Added!".format(localID)}
            elif (_addResult == -1): return {'result': False, 'message': "Account '{:s}' Add Failed Due To An Unexpected Error. '{:s}'".format(localID, str(_addResult_exception))}
            elif (_addResult == -2): return {'result': False, 'message': "Account '{:s}' Add Failed. 'Check Account Name'".format(localID)}
    
    def __updateAccounts(self):
        for localID in self.__accounts_virtualServer:
            #[1]: Instances
            account               = self.__accounts[localID]
            account_virtualServer = self.__accounts_virtualServer[localID]

            #[2]: Account Data Update
            if not (_ACCOUNT_UPDATEINTERVAL_NS < time.perf_counter_ns()-account['_lastUpdated']): 
                continue

            #[3]: Account Data Update
            self.__updateAccount(localID      = localID, 
                                 importedData = {'source':    'VIRTUALSERVER', 
                                                 'positions': account_virtualServer['positions'], 
                                                 'assets':    account_virtualServer['assets']})
            self.__updateAccountPeriodicReport(localID      = localID, 
                                               importedData = None)
    
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
        currencies       = self.__currencies
        accounts         = self.__accounts
        cas              = self.__currencyAnalyses
        func_getPRD      = self.ipcA.getPRD
        func_sendPRDEDIT = self.ipcA.sendPRDEDIT
        func_sendFAR     = self.ipcA.sendFAR

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
                if currencies[symbol]['quoteAsset'] in _ACCOUNT_READABLEASSETS:
                    for localID in accounts:
                        self.__formatNewAccountPosition(localID = localID, currencySymbol = symbol)
                        func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', symbol), prdContent = accounts[localID]['positions'][symbol])
                        func_sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION_ADDED', 'updatedContent': (localID, symbol)}, farrHandler = None)
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

    def __farr_onAccountDescriptionLoadRequestResponse(self, responder, requestID, functionResult):
        """
        if (responder == 'DATAMANAGER'):
            accountDescriptions = functionResult
            for _localID in accountDescriptions:
                _ad = accountDescriptions[_localID]
                self.__addAccount(localID            = _localID, 
                                  buid               = _ad['buid'],
                                  accountType        = _ad['accountType'],
                                  password           = _ad['hashedPassword'],
                                  newAccount         = False,
                                  assets             = _ad['assets'],
                                  positions          = _ad['positions'],
                                  lastPeriodicReport = _ad['lastPeriodicReport'],
                                  sendIPCM           = False)
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', _localID), prdContent = self.__accounts[_localID])
            #Format new positions for any non-registered currencies (that are in Market but not in DB)
            #---Local formatting
            _newPositions = list()
            for currencySymbol in self.__currencies:
                if (self.__currencies[currencySymbol]['quoteAsset'] in _ACCOUNT_READABLEASSETS):
                    for _localID in self.__accounts:
                        _account = self.__accounts[_localID]
                        if (currencySymbol not in _account['positions']): self.__formatNewAccountPosition(localID = _localID, currencySymbol = currencySymbol); _newPositions.append((_localID, currencySymbol))
            #---Update Requests
            if (0 < len(_newPositions)):
                _dbUpdateRequests = list()
                for _localID, _pSymbol in _newPositions:
                    _account  = self.__accounts[_localID]
                    _position = _account['positions'][_pSymbol]
                    _asset    = _account['assets'][_position['quoteAsset']]
                    _dbUpdateRequests.append(((_localID, 'positions', _pSymbol, '#NEW#'), _position))
                if (0 < len(_dbUpdateRequests)): self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': _dbUpdateRequests}, farrHandler = None)
        """
    


    #<GUI>
    #---Manager Configuration
    def __far_updateConfiguration(self, requester, requestID, newConfiguration):
        if (requester == 'GUI'):
            #Print Update
            self.__config_TradeManager['print_Update'] = newConfiguration['print_Update']
            #Print Warning
            self.__config_TradeManager['print_Warning'] = newConfiguration['print_Warning']
            #Print Error
            self.__config_TradeManager['print_Error'] = newConfiguration['print_Error']
            #Save Config # Update Announcement
            self.__saveTradeManagerConfig()
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CONFIGURATION', prdContent = self.__config_TradeManager)
            return {'result': True, 'message': "Configuration Successfully Updated!", 'configuration': self.__config_TradeManager}
    
    def __far_addAccount(self, requester, requestID, localID, buid, accountType, password):
        if (requester == 'GUI'):
            _result = self.__addAccount(localID = localID, buid = buid, accountType = accountType, password = password, newAccount = True, silentTerminal = False, lastPeriodicReport = None, sendIPCM = True)
            return {'localID': localID, 'responseOn': 'ADDACCOUNT', 'result': _result['result'], 'message': _result['message']}
    
    def __far_removeAccount(self, requester, requestID, localID, password):
        if (requester == 'GUI'): 
            _result = self.__removeAccount(localID = localID, password = password)
            return {'localID': localID, 'responseOn': 'REMOVEACCOUNT', 'result': _result['result'], 'message': _result['message']}
    
    def __far_activateAccount(self, requester, requestID, localID, password, apiKey, secretKey, encrypted):
        if (requester != 'GUI'): return
        activationResult = self.__activateAccount(localID   = localID, 
                                                  password  = password, 
                                                  apiKey    = apiKey, 
                                                  secretKey = secretKey, 
                                                  encrypted = encrypted, 
                                                  requestID = requestID)
        if (activationResult is not None): 
            self.ipcA.sendFARR(targetProcess = 'GUI', 
                               functionResult = {'localID':    localID, 
                                                 'responseOn': 'ACTIVATEACCOUNT', 
                                                 'result':     False, 
                                                 'message':    activationResult['message']}, 
                               requestID = requestID, 
                               complete = True)
    
    def __far_deactivateAccount(self, requester, requestID, localID, password):
        if (requester != 'GUI'): return
        deactivationResult = self.__deactivateAccount(localID  = localID, 
                                                      password = password)
        return {'localID':    localID, 
                'responseOn': 'DEACTIVATEACCOUNT', 
                'result':     deactivationResult['result'], 
                'message':    deactivationResult['message']}
    
    def __far_setAccountTradeStatus(self, requester, requestID, localID, password, newStatus):
        if (requester == 'GUI'):
            if (localID in self.__accounts):
                _account = self.__accounts[localID]
                #Check Password
                passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
                if (passwordTest == True):
                    self.__accounts[localID]['tradeStatus'] = newStatus
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'tradeStatus'), prdContent = self.__accounts[localID]['tradeStatus'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_TRADESTATUS', 'updatedContent': localID}, farrHandler = None)
                    return   {'localID': localID, 'responseOn': 'SETACCOUNTTRADESTATUS', 'result': True,  'message': "Account '{:s}' Trade Status Update Sucessful!".format(localID)}
                else: return {'localID': localID, 'responseOn': 'SETACCOUNTTRADESTATUS', 'result': False, 'message': "Account '{:s}' Trade Status Update Failed. 'Incorrect Password'".format(localID)}
            else:     return {'localID': localID, 'responseOn': 'SETACCOUNTTRADESTATUS', 'result': False, 'message': "Account '{:s}' Trade Status Update Failed. 'The Account Does Not Exist'".format(localID)}
    
    def __far_transferBalance(self, requester, requestID, localID, password, asset, amount):
        if (requester == 'GUI'):
            if (localID in self.__accounts):
                _account = self.__accounts[localID]
                #Check Password
                passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
                if (passwordTest == True):
                    if (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL):
                        _account_virtualServer = self.__accounts_virtualServer[localID]
                        _asset_virtualServer   = _account_virtualServer['assets'][asset]
                        #If this is a withdrawl and the amount is more than the available, set the amount equal to the available
                        if ((amount < 0) and (_asset_virtualServer['availableBalance'] < -amount)): amount = -_asset_virtualServer['availableBalance']
                        #Update the crossWallet balance
                        _asset_virtualServer['crossWalletBalance'] += amount
                        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'assets', asset, 'crossWalletBalance'), _asset_virtualServer['crossWalletBalance'])]}, farrHandler = None)
                        return   {'localID': localID, 'responseOn': 'BALANCETRANSFER', 'result': True,  'message': "Account '{:s}' Asset '{:s}' Balance Transfer Successful!".format(localID, asset)}
                    else: return {'localID': localID, 'responseOn': 'BALANCETRANSFER', 'result': False, 'message': "Account '{:s}' Asset '{:s}' Balance Transfer Failed. 'Internal Balance Transfer Is Only Available For 'VIRTUAL' Type Account'".format(localID, asset)}
                else: return     {'localID': localID, 'responseOn': 'BALANCETRANSFER', 'result': False, 'message': "Account '{:s}' Asset '{:s}' Balance Transfer Failed. 'Incorrect Password'".format(localID, asset)}
            else: return         {'localID': localID, 'responseOn': 'BALANCETRANSFER', 'result': False, 'message': "Account '{:s}' Asset '{:s}' Balance Transfer Failed. 'The Account Does Not Exist'".format(localID, asset)}
    
    def __far_updateAllocationRatio(self, requester, requestID, localID, password, asset, newAllocationRatio):
        if (requester == 'GUI'):
            if (localID in self.__accounts):
                _account = self.__accounts[localID]
                #Check Password
                passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
                if (passwordTest == True):
                    _asset = _account['assets'][asset]
                    if (newAllocationRatio < 0): newAllocationRatio = 0
                    if (1 < newAllocationRatio): newAllocationRatio = 1
                    _asset['allocationRatio'] = newAllocationRatio
                    #Annoucement
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'assets', asset, 'allocationRatio'), prdContent = _asset['allocationRatio'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_ASSET', 'updatedContent': (localID, asset, 'allocationRatio')}, farrHandler = None)
                    self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'assets', asset, 'allocationRatio'), _asset['allocationRatio']),]}, farrHandler = None)
                    #Return update result
                    return   {'localID': localID, 'asset': asset, 'responseOn': 'ALLOCATIONRATIOUPDATE', 'result': True,  'message': "Account '{:s}' Asset {:s} Allocation Ratio Update Successful!".format(localID, asset)}
                else: return {'localID': localID, 'asset': asset, 'responseOn': 'ALLOCATIONRATIOUPDATE', 'result': False, 'message': "Account '{:s}' Asset {:s} Allocation Ratio UpdateFailed. 'Incorrect Password'".format(localID, asset)}
            else: return     {'localID': localID, 'asset': asset, 'responseOn': 'ALLOCATIONRATIOUPDATE', 'result': False, 'message': "Account '{:s}' Asset {:s} Allocation Ratio UpdateFailed. 'The Account Does Not Exist'".format(localID, asset)}
    
    def __far_forceClearPosition(self, requester, requestID, localID, password, positionSymbol):
        #[1]: Requester Check
        if (requester != 'GUI'): return

        #[2]: Acocunt Check
        if (localID not in self.__accounts):
            self.ipcA.sendFARR(targetProcess = 'GUI', 
                               functionResult = {'localID': localID, 
                                                 'positionSymbol': positionSymbol, 
                                                 'responseOn': 'FORCECLEARPOSITION', 
                                                 'result': False, 
                                                 'message': f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Failed. 'Account Not Found'"},         
                               requestID = requestID, 
                               complete = True)
            return
        account = self.__accounts[localID]

        #[3]: Password Check
        if not(bcrypt.checkpw(password.encode(encoding = "utf-8"), account['hashedPassword'])):
            self.ipcA.sendFARR(targetProcess = 'GUI', 
                               functionResult = {'localID': localID, 
                                                 'positionSymbol': positionSymbol, 
                                                 'responseOn': 'FORCECLEARPOSITION', 
                                                 'result': False, 
                                                 'message': f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Failed. 'Incorrect Password'"},         
                               requestID = requestID, 
                               complete  = True)
            return
        
        #[4]: OCR Check
        position = account['positions'][positionSymbol]
        ocr      = position['_orderCreationRequest']
        if (ocr is not None):
            self.ipcA.sendFARR(targetProcess = 'GUI', 
                               functionResult = {'localID': localID, 
                                                 'positionSymbol': positionSymbol, 
                                                 'responseOn': 'FORCECLEARPOSITION', 
                                                 'result': False, 
                                                 'message': f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Failed. 'OCR Not Empty'"},              
                               requestID = requestID, 
                               complete = True)
            return
        
        #[5]: Quantity Check
        if ((position['quantity'] is None) or (position['quantity'] == 0)):
            self.ipcA.sendFARR(targetProcess = 'GUI', 
                               functionResult = {'localID': localID, 
                                                 'positionSymbol': positionSymbol, 
                                                 'responseOn': 'FORCECLEARPOSITION', 
                                                 'result': False, 
                                                 'message': f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Failed. 'Check The Quantity'"},         
                               requestID = requestID, 
                               complete = True)
            return
        
        #[6]: Force Clearing
        #---[6-1]: Side & Quantity Determination
        if   (position['quantity'] < 0): _side = 'BUY';  _quantity = -position['quantity']
        elif (0 < position['quantity']): _side = 'SELL'; _quantity =  position['quantity']
        #---[6-2]: Trade Control Update
        if   (position['quantity'] < 0): tcTracker_slExited = 'SHORT'
        elif (0 < position['quantity']): tcTracker_slExited = 'LONG'
        tcTracker = position['tradeControlTracker']
        kline_TS  = self.__currencies_lastKline[positionSymbol][KLINDEX_OPENTIME]
        tcTrackerUpdate = {'slExited': {'onComplete': (tcTracker_slExited, kline_TS), 
                                        'onPartial':  (tcTracker_slExited, kline_TS),  
                                        'onFail':     tcTracker['slExited']}}
        #---[6-3]: OCR Generation
        ocrGenResult = self.__orderCreationRequest_generate(localID         = localID, 
                                                            positionSymbol  = positionSymbol, 
                                                            logicSource     = 'FORCECLEAR', 
                                                            side            = _side,
                                                            quantity        = _quantity,
                                                            tcTrackerUpdate = tcTrackerUpdate,
                                                            ipcRID          = requestID)
        if (ocrGenResult == False):
            self.ipcA.sendFARR(targetProcess = 'GUI', 
                               functionResult = {'localID': localID, 
                                                 'positionSymbol': positionSymbol, 
                                                 'responseOn': 'FORCECLEARPOSITION', 
                                                 'result': False, 
                                                 'message': f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Failed. 'OCR Generation Rejected'"},         
                               requestID = requestID, 
                               complete = True)
    
    def __far_updatePositionTradeStatus(self, requester, requestID, localID, password, positionSymbol, newTradeStatus):
        if (requester == 'GUI'):
            if (localID in self.__accounts):
                _account = self.__accounts[localID]
                if (positionSymbol in _account['positions']):
                    _position = _account['positions'][positionSymbol]
                    #Check Password
                    passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
                    if (passwordTest == True):
                        if (_position['tradable'] == True):
                            _position['tradeStatus'] = newTradeStatus
                            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol, 'tradeStatus'), prdContent = newTradeStatus)
                            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, positionSymbol, 'tradeStatus')}, farrHandler = None)
                            self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'positions', positionSymbol, 'tradeStatus'), _position['tradeStatus'])]}, farrHandler = None)
                            if (newTradeStatus == True):
                                _position['abruptClearingRecords'].clear()
                                self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'positions', positionSymbol, 'abruptClearingRecords'), _position['abruptClearingRecords'].copy())]}, farrHandler = None)
                            return   {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADESTATUS', 'result': True,  'message': "Account '{:s}' Position '{:s}' Trade Status Update Successful!".format(localID, positionSymbol)}
                        else: return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADESTATUS', 'result': False, 'message': "Account '{:s}' Position '{:s}' Trade Status Update Failed. 'The Position Is Not Tradable'".format(localID, positionSymbol)}
                    else: return     {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADESTATUS', 'result': False, 'message': "Account '{:s}' Position '{:s}' Trade Status Update Failed. 'Incorrect Password'".format(localID, positionSymbol)}
                else: return         {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADESTATUS', 'result': False, 'message': "Account '{:s}' Position '{:s}' Trade Status Update Failed. 'The Position Does Not Exist'".format(localID, positionSymbol)}
            else: return             {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADESTATUS', 'result': False, 'message': "Account '{:s}' Position '{:s}' Trade Status Update Failed. 'The Account Does Not Exist'".format(localID, positionSymbol)}
    
    def __far_updatePositionReduceOnly(self, requester, requestID, localID, password, positionSymbol, newReduceOnly):
        if (requester == 'GUI'):
            if (localID in self.__accounts):
                _account = self.__accounts[localID]
                if (positionSymbol in _account['positions']):
                    _position = _account['positions'][positionSymbol]
                    #Check Password
                    passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
                    if (passwordTest == True):
                        _position['reduceOnly'] = newReduceOnly
                        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol, 'reduceOnly'), prdContent = newReduceOnly)
                        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, positionSymbol, 'reduceOnly')}, farrHandler = None)
                        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'positions', positionSymbol, 'reduceOnly'), _position['reduceOnly'])]}, farrHandler = None)
                        return   {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONREDUCEONLY', 'result': True,  'message': "Account '{:s}' Position '{:s}' Reduce-Only Update Successful!".format(localID, positionSymbol)}
                    else: return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONREDUCEONLY', 'result': False, 'message': "Account '{:s}' Position '{:s}' Reduce-Only Update Failed. 'Incorrect Password'".format(localID, positionSymbol)}
                else: return     {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONREDUCEONLY', 'result': False, 'message': "Account '{:s}' Position '{:s}' Reduce-Only Update Failed. 'The Position Does Not Exist'".format(localID, positionSymbol)}
            else: return         {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONREDUCEONLY', 'result': False, 'message': "Account '{:s}' Position '{:s}' Reduce-Only Update Failed. 'The Account Does Not Exist'".format(localID, positionSymbol)}
    
    def __far_updatePositionTraderParams(self, requester, requestID, localID, password, positionSymbol, newCurrencyAnalysisCode, newTradeConfigurationCode, newPriority, newAssumedRatio, newMaxAllocatedBalance):
        #[1]: Requester Check
        if (requester != 'GUI'): return

        #[2]: Account Check
        if (localID not in self.__accounts):
            return {'localID':        localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn':     'UPDATEPOSITIONTRADERPARAMS', 
                    'result':         False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'The Account Does Not Exist'"}
        account = self.__accounts[localID]
        
        #[3]: Position Check
        if (positionSymbol not in account['positions']):
            return {'localID':        localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn':     'UPDATEPOSITIONTRADERPARAMS', 
                    'result':         False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'The Position Does Not Exist'"}
        
        #[4]: Password Check
        if not(bcrypt.checkpw(password.encode(encoding = "utf-8"), account['hashedPassword'])):
            return {'localID':        localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn':     'UPDATEPOSITIONTRADERPARAMS', 
                    'result':         False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'Incorrect Password'"}
        
        #[5]: Quantity Check
        position = account['positions'][positionSymbol]
        if (position['quantity'] != 0):
            return {'localID': localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn': 'UPDATEPOSITIONTRADERPARAMS', 
                    'result': False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'Non-Zero Quantity'"}
        
        #[6]: Update
        position_prev = position.copy()
        assetName     = position['quoteAsset']
        asset         = account['assets'][assetName]
        asset_prev    = asset.copy()
        _toRequestDBUpdate = list()
        #---[6-1]: Currency Analysis Code
        if ((position['currencyAnalysisCode'] != newCurrencyAnalysisCode)):
            #New Parameter Validity Test
            if   (newCurrencyAnalysisCode == None):                    _testPassed = True
            elif (newCurrencyAnalysisCode in self.__currencyAnalysis): _testPassed = True
            else:                                                      _testPassed = False
            #Finally
            if (_testPassed == True):
                self.__registerPositionToCurrencyAnalysis(localID = localID, positionSymbol = positionSymbol, currencyAnalysisCode = newCurrencyAnalysisCode)
                _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'currencyAnalysisCode'), position['currencyAnalysisCode']))
        #---[6-2]: Trade Configuration Code
        if (position['tradeConfigurationCode'] != newTradeConfigurationCode):
            #New Parameter Validity Test
            if   (newTradeConfigurationCode == None):                       _testPassed = True
            elif (newTradeConfigurationCode in self.__tradeConfigurations): _testPassed = True
            else:                                                           _testPassed = False
            #Finally
            if (_testPassed == True):
                #Apply Change & Announce
                self.__registerPositionTradeConfiguration(localID = localID, positionSymbol = positionSymbol, tradeConfigurationCode = newTradeConfigurationCode)
                position['tradeControlTracker'] = self.__getInitializedTradeControlTracker()
                _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'tradeConfigurationCode'), position['tradeConfigurationCode']))
                _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'tradeControlTracker'),    self.__copyTradeControlTracker(position['tradeControlTracker'])))
        #---[6-3]: Priority
        if (position['priority'] != newPriority):
            #New Parameter Validity Test
            try:
                if ((1 <= newPriority) and (newPriority <= len(account['positions']))): _testPassed = True
                else:                                                                   _testPassed = False
            except:                                                                     _testPassed = False
            #Finally
            if (_testPassed == True):
                #Effected Positions
                priorityUpdatedPositions = list()
                if (position['priority'] < newPriority): 
                    _target = (position['priority']+1, newPriority)
                    for _pSymbol in account['positions']:
                        __position = account['positions'][_pSymbol]
                        if ((_target[0] <= __position['priority']) and (__position['priority'] <= _target[1])): __position['priority'] -= 1; priorityUpdatedPositions.append(_pSymbol)
                elif (newPriority < position['priority']): 
                    _target = (newPriority, position['priority']-1)
                    for _pSymbol in account['positions']:
                        __position = account['positions'][_pSymbol]
                        if ((_target[0] <= __position['priority']) and (__position['priority'] <= _target[1])): __position['priority'] += 1; priorityUpdatedPositions.append(_pSymbol)
                for _pSymbol in priorityUpdatedPositions:
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', _pSymbol, 'priority'), prdContent = account['positions'][_pSymbol]['priority'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, _pSymbol, 'priority')}, farrHandler = None)
                #Target Position
                position['priority'] = newPriority
                _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'priority'), position['priority']))
        #---[6-4]: Assumed Ratio
        if (position['assumedRatio'] != newAssumedRatio):
            #New Parameter Validity Test
            try:
                if (0 <= newAssumedRatio): _testPassed = True
                else:                      _testPassed = False
            except: _testPassed = False
            #Finally
            if (_testPassed == True): 
                position['assumedRatio'] = newAssumedRatio
                _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'assumedRatio'), position['assumedRatio']))
        #---[6-5]: Max Allocated Balance
        if (position['maxAllocatedBalance'] != newMaxAllocatedBalance):
            #New Parameter Validity Test
            try:
                if (0 <= newMaxAllocatedBalance): _testPassed = True
                else:                             _testPassed = False
            except: _testPassed = False
            #Finally
            if (_testPassed == True): 
                position['maxAllocatedBalance'] = newMaxAllocatedBalance
                _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'maxAllocatedBalance'), position['maxAllocatedBalance']))

        #[7]: Tradability Check & MarginType and Leverage Update
        self.__checkPositionTradability(localID = localID, positionSymbol = positionSymbol)
        self.__requestMarginTypeAndLeverageUpdate(localID = localID, positionSymbol = positionSymbol) #If this needs to be done will be determined internally
        if (position['tradeConfigurationCode'] in self.__tradeConfigurations_loaded): position['weightedAssumedRatio'] = position['assumedRatio']*self.__tradeConfigurations_loaded[position['tradeConfigurationCode']]['config']['leverage']
        else:                                                                         position['weightedAssumedRatio'] = None
        
        #[8]: DB & GUI Annoucement
        if (0 < len(_toRequestDBUpdate)): self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': _toRequestDBUpdate}, farrHandler = None)
        for _dataName in position:
            if ((_dataName in _GUIANNOUCEMENT_POSITIONDATANAMES) and (position[_dataName] != position_prev[_dataName])): 
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol, _dataName), prdContent = position[_dataName])
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, positionSymbol, _dataName)}, farrHandler = None)
        for _dataName in asset:
            if ((_dataName in _GUIANNOUCEMENT_ASSETDATANAMES) and (asset[_dataName] != asset_prev[_dataName])): 
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'assets', assetName, _dataName), prdContent = asset[_dataName])
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_ASSET', 'updatedContent': (localID, assetName, _dataName)}, farrHandler = None)
        
        #[9]: Result Return
        return {'localID':        localID, 
                'positionSymbol': positionSymbol, 
                'responseOn':     'UPDATEPOSITIONTRADERPARAMS', 
                'result':         True,  
                'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Successful!"}
    
    def __far_resetTradeControlTracker(self, requester, requestID, localID, password, positionSymbol):
        #[1]: Requester Check
        if (requester != 'GUI'): return

        #[2]: Account Check
        if (localID not in self.__accounts):
            return {'localID':        localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn':     'RESETTRADECONTROLTRACKER', 
                    'result':         False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'The Account Does Not Exist'"}
        account = self.__accounts[localID]
        
        #[3]: Position Check
        if (positionSymbol not in account['positions']):
            return {'localID':        localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn':     'RESETTRADECONTROLTRACKER', 
                    'result':         False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'The Position Does Not Exist'"}
        
        #[4]: Password Check
        if not(bcrypt.checkpw(password.encode(encoding = "utf-8"), account['hashedPassword'])):
            return {'localID':        localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn':     'RESETTRADECONTROLTRACKER', 
                    'result':         False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'Incorrect Password'"}
        
        #[5]: Trade Control Reset (Run-time specific parameters are not reset)
        position = account['positions'][positionSymbol]
        tcTracker_prev = self.__copyTradeControlTracker(tradeControlTracker = position['tradeControlTracker'])
        tcTracker_new  = self.__getInitializedTradeControlTracker()
        tcTracker_new['rqpm_model']    = tcTracker_prev['rqpm_model'].copy()
        position['tradeControlTracker'] = tcTracker_new

        #[6]: Announcement
        tcTracker_copied = self.__copyTradeControlTracker(tradeControlTracker = position['tradeControlTracker'])
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                              prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol, 'tradeControlTracker'), 
                              prdContent = tcTracker_copied)
        self.ipcA.sendFAR(targetProcess  = 'GUI', 
                          functionID     = 'onAccountUpdate', 
                          functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, positionSymbol, 'tradeControlTracker')}, 
                          farrHandler    = None)
        self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER',
                          functionID     = 'editAccountData',
                          functionParams = {'updates': [((localID, 'positions', positionSymbol, 'tradeControlTracker'), tcTracker_copied),]}, 
                          farrHandler    = None)
            
        #[7]: Result Return
        return {'localID':        localID, 
                'positionSymbol': positionSymbol, 
                'responseOn':     'RESETTRADECONTROLTRACKER', 
                'result':         True,
                'message': f"Account '{localID}' Position '{positionSymbol}' Trade Control Tracker Initialization Successful!"}
    
    def __far_verifyPassword(self, requester, requestID, localID, password):
        #[1]: Requester Check
        if (requester != 'GUI'): return

        #[2]: Account Check
        if (localID not in self.__accounts):
            return {'localID':         localID, 
                    'responseOn':      'VERIFYPASSWORD', 
                    'result':          False, 
                    'result_detailed': None,
                    'message': f"Account '{localID}' Password Verification Failed. 'The Account Does Not Exist'"}
        account = self.__accounts[localID]
        
        #[3]: Password Check
        ispasswordCorrect = bcrypt.checkpw(password.encode(encoding = "utf-8"), account['hashedPassword'])
        return {'localID':         localID,
                'responseOn':      'VERIFYPASSWORD', 
                'result':          True, 
                'result_detailed': {'isPasswordCorrect': ispasswordCorrect},
                'message': None}

    #<BINANCEAPI>
    def __far_onKlineStreamReceival(self, requester, symbol, kline):
        #[1]: Source Check
        if requester != 'BINANCEAPI':
            return
        
        #[2]: Record the last close price
        self.__currencies_lastKline[symbol] = kline

        return

        #[3]: Position Responses
        for lID, account in self.__accounts.items():
            if symbol not in account['positions']:
                continue
            position = account['positions'][symbol]
            if position['quantity'] is not None and position['quantity'] != 0: 
                self.__trade_checkConditionalExits(localID        = lID, 
                                                   positionSymbol = symbol, 
                                                   kline          = kline)

    def __farr_onAccountInstanceGenerationRequestResponse(self, responder, requestID, functionResult):
        if (responder == 'BINANCEAPI'):
            if (requestID in self.__accountInstanceGenerationRequests):
                localID         = self.__accountInstanceGenerationRequests[requestID][0]
                requestID_toGUI = self.__accountInstanceGenerationRequests[requestID][1]
                if (functionResult['result'] == True):
                    _account = self.__accounts[localID]
                    #Update the account status and signal it
                    _account['status'] = _ACCOUNT_ACCOUNTSTATUS_ACTIVE
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'status'), prdContent = _account['status'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_STATUS', 'updatedContent': localID}, farrHandler = None)
                    #Send FARR signaling account activaion success
                    self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'responseOn': 'ACTIVATEACCOUNT', 'result': True, 'message': "Account '{:s}' Activation Successful!".format(localID)}, requestID = requestID_toGUI, complete = True)
                else:
                    failType = functionResult['failType']
                    if   (failType == 'FUTURESDISABLED'):   self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'responseOn': 'ACTIVATEACCOUNT', 'result': False, 'message': "Account '{:s}' Activation Failed. 'Futures Disabled, Check API Permissions'".format(localID)},                              requestID = requestID_toGUI, complete = True)
                    elif (failType == 'UIDMISMATCH'):       self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'responseOn': 'ACTIVATEACCOUNT', 'result': False, 'message': "Account '{:s}' Activation Failed. 'BUID Mismatch'".format(localID)},                                                        requestID = requestID_toGUI, complete = True)
                    elif (failType == 'UNEXPECTEDERROR'):   self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'responseOn': 'ACTIVATEACCOUNT', 'result': False, 'message': "Account '{:s}' Activation Failed Due To An Unexpected Error. '{:s}'".format(localID, str(functionResult['errorMessage']))}, requestID = requestID_toGUI, complete = True)
                    elif (failType == 'SERVERUNAVAILABLE'): self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'responseOn': 'ACTIVATEACCOUNT', 'result': False, 'message': "Account '{:s}' Activation Failed. 'Server Unavailable'".format(localID)},                                                   requestID = requestID_toGUI, complete = True)
                del self.__accountInstanceGenerationRequests[requestID]
    
    def __far_onAccountDataReceival(self, requester, localID, accountData):
        if (requester == 'BINANCEAPI'):
            if (localID in self.__accounts):
                #Format assets and positions data for internal interpretation
                _assetsData    = dict()
                _positionsData = dict()
                for _asset in accountData['assets']:
                    if (_asset['asset'] in _ACCOUNT_READABLEASSETS): 
                        _assetsData[_asset['asset']] = {'marginBalance':      float(_asset['marginBalance']),
                                                        'walletBalance':      float(_asset['walletBalance']),
                                                        'crossWalletBalance': float(_asset['crossWalletBalance']),
                                                        'availableBalance':   float(_asset['availableBalance'])}
                for _position in accountData['positions']:
                    if (_position['symbol'] in self.__currencies):
                        if (self.__currencies[_position['symbol']]['quoteAsset'] in _ACCOUNT_READABLEASSETS):
                            _entryPrice = float(_position['entryPrice'])
                            if (_entryPrice == 0): _entryPrice = None
                            _positionsData[_position['symbol']] = {'quantity':               float(_position['positionAmt']),
                                                                   'entryPrice':             _entryPrice,
                                                                   'leverage':               int(_position['leverage']),
                                                                   'isolated':               bool(_position['isolated']),
                                                                   'isolatedWalletBalance':  float(_position['isolatedWallet']),
                                                                   'openOrderInitialMargin': float(_position['openOrderInitialMargin']),
                                                                   'positionInitialMargin':  float(_position['positionInitialMargin']),
                                                                   'maintenanceMargin':      float(_position['maintMargin']),
                                                                   'unrealizedPNL':          float(_position['unrealizedProfit'])}
                #Update the account using the imported data
                self.__updateAccount(localID = localID, importedData = {'source': 'BINANCE', 'positions': _positionsData, 'assets': _assetsData})
                self.__updateAccountPeriodicReport(localID = localID, importedData = None)
    
    def __far_onPositionControlResponse(self, responder, requestID, functionResult):
        localID        = functionResult['localID']
        positionSymbol = functionResult['positionSymbol']
        responseOn     = functionResult['responseOn']
        result         = functionResult['result']
        if (localID in self.__accounts):
            if (positionSymbol in self.__accounts[localID]['positions']):
                _position = self.__accounts[localID]['positions'][positionSymbol]
                #MarginType Update Request Response
                if (responseOn == 'MARGINTYPEUPDATE'):
                    if (result == True): pass
                    else:
                        failType = functionResult['failType']
                        if (failType == 'SERVERUNAVAILABLE'):     pass
                        elif (failType == 'LOCALIDNOTFOUND'):     pass
                        elif (failType == 'ACCOUNTNOTACTIVATED'): pass
                        elif (failType == 'MARGINTYPEERROR'):     pass
                        elif (failType == 'APIERROR'):            pass
                    _position['_marginTypeControlRequested'] = False
                #Leverage Update Request Response
                elif (responseOn == 'LEVERAGEUPDATE'):
                    if (result == True): pass
                    else:
                        failType = functionResult['failType']
                        if (failType == 'SERVERUNAVAILABLE'):     pass
                        elif (failType == 'LOCALIDNOTFOUND'):     pass
                        elif (failType == 'ACCOUNTNOTACTIVATED'): pass
                        elif (failType == 'APIERROR'):            pass
                    _position['_leverageControlRequested'] = False
                #Order Creation Request Response
                elif (responseOn == 'CREATEORDER'):
                    _ocr = _position['_orderCreationRequest']
                    if (_ocr is not None):
                        if (_ocr['dispatchID'] == requestID):
                            _requestResult = {'resultReceivalTime': time.time(), 
                                              'result':             result,
                                              'failType':           functionResult['failType'],
                                              'orderResult':        functionResult['orderResult'],
                                              'errorMessage':       functionResult['errorMessage']}
                            _ocr['results'].append(_requestResult)
                            _ocr['lastRequestReceived'] = True
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    
#<ON CURRENCY ANALYSIS ADD> -> ACCOUNT 
"""
accounts     = self.__accounts
#[11]: Account Update
for lID, account in accounts.items():
    #[11-1]: Position
    position = account['positions'][cSymbol]
    if position['currencyAnalysisCode'] != caCode:
        continue
    pos_prevs = {'tradable':    position['tradable'],
                    'tradeStatus': position['tradeStatus']}
    
    #[11-2]: Register currency analysis
    self.__registerPositionToCurrencyAnalysis(localID = lID, positionSymbol = cSymbol, currencyAnalysisCode = caCode)

    #[11-3]: Update tradability & trade status and announce
    self.__checkPositionTradability(localID = lID, positionSymbol = cSymbol)
    for dType in ('tradable', 'tradeStatus'):
        if position[dType] == pos_prevs[dType]:
            continue
        func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', lID, 'positions', cSymbol, dType), prdContent = position[dType])
        func_sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (lID, cSymbol, dType)}, farrHandler = None)
"""

#<ON CURRENCY ANALYSIS REMOVE> -> ACCOUNT
"""
#[3]: Reference Check (If Any Exists, Cannot Remove)
#---[3-1]: Trading Accounts Check
usingAccounts = []
for lID, account in accounts.items():
    position = account['positions'][cSymbol]
    if position['currencyAnalysisCode'] == caCode and position['tradeStatus']:
        usingAccounts.append(f"'{lID}'")

#---[3-2]: If Any Found, Return False
if usingAccounts:
    return {'result':               False,
            'responseOn':           "REMOVECURRENCYANALYSIS",
            'currencyAnalysisCode': currencyAnalysisCode,
            'message':              f"Currency Analysis '{caCode}' Removal Failed. Currency Analysis Being Used For Trading By Accounts [{', '.join(usingAccounts)}]"}

#---[3-3]: If No Account Is Trading With The Currency Analysis, Unregister
for lID, account in accounts.items():
    #[3-3-1]: Position
    position = account['positions'][cSymbol]
    if position['currencyAnalysisCode'] != caCode:
        continue
    tradable_prev = position['tradable']
    #[3-3-2]: Unregister currency analysis
    self.__unregisterPositionFromCurrencyAnalysis(localID        = lID, 
                                                    positionSymbol = cSymbol)
    #[3-3-3]: Update tradability & trade status and announce
    self.__checkPositionTradability(localID = lID, positionSymbol = cSymbol)
    if position['tradable'] == tradable_prev:
        continue
    func_sendPRDEDIT(targetProcess = 'GUI', 
                        prdAddress    = ('ACCOUNTS', lID, 'positions', cSymbol, 'tradable'), 
                        prdContent    = position['tradable'])
    func_sendFAR(targetProcess  = 'GUI',
                    functionID     = 'onAccountUpdate',
                    functionParams = {'updateType': 'UPDATED_POSITION', 
                                    'updatedContent': (lID, cSymbol, 'tradable')}, 
                    farrHandler    = None)
"""

#<ON TRADE CONFIGURATION ADD> -> ACCOUNT
"""
#If there exist any account positions that refer to this trade configuration, register
for _localID in self.__accounts:
    for _positionSymbol in self.__accounts[_localID]['positions']:
        _position = self.__accounts[_localID]['positions'][_positionSymbol]
        if (_position['tradeConfigurationCode'] == tradeConfigurationCode):
            _tradable_prev    = _position['tradable']
            _tradeStatus_prev = _position['tradeStatus']
            self.__registerPositionTradeConfiguration(localID = _localID, positionSymbol = _positionSymbol, tradeConfigurationCode = tradeConfigurationCode)
            self.__checkPositionTradability(localID = _localID, positionSymbol = _positionSymbol)
            if (sendIPCM == True): 
                if (_position['tradable'] != _tradable_prev):
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', _localID, 'positions', _positionSymbol, 'tradable'), prdContent = _position['tradable'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (_localID, _positionSymbol, 'tradable')}, farrHandler = None)
                if (_position['tradeStatus'] != _tradeStatus_prev):
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', _localID, 'positions', _positionSymbol, 'tradeStatus'), prdContent = _position['tradeStatus'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (_localID, _positionSymbol, 'tradeStatus')}, farrHandler = None)
"""