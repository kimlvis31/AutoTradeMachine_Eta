#ATM Modules
import atmEta_IPC
import atmEta_Auxillaries
import atmEta_Constants

#Python Modules
import time
import socket
import binance
import termcolor
import os
import json
import traceback
from datetime import datetime, timezone, tzinfo
from collections import deque

#Constants
_CONNECTIONSCHECKINTERVAL_NS = 1e9
_CONNECTIONSTATUS_BINANCE_DISCONNECTED = -1
_CONNECTIONSTATUS_BINANCE_CONNECTED    = 0
_CONNECTIONSTATUS_BINANCE_MAINTENANCE  = 1

_BINANCE_EXCHANGEINFOREADMAXATTEMPT        = 120
_BINANCE_EXCHANGEINFOREADATTEMPTINTERVAL_S = 0.5
_BINANCE_EXCHANGEINFOREADINTERVAL_S        = 60

_BINANCE_FIRSTKLINEOPENTSSEARCHQUEUEUPDATEINTERVAL_NS = 1e9

_BINANCE_WEBSOCKETSTREAMCONNECTIONTRIES_MAX   = 3
_BINANCE_WEBSOCEKTSTREAMCONNECTIONINTERVAL_NS = 1e9

_BINANCE_ACCOUNTDATAREADINTERVAL_MIN_NS           = 1e9
_BINANCE_ACCOUNTDATAREADINTERVAL_MAX_NS           = 10e9
_BINANCE_ACCOUNTDATAREADTOLERATEDCONSECUTIVEFAILS = 3
_BINANCE_CREATEDORDERCHECKINTERVAL_NS      = 1e9
_BINANCE_CREATEDORDERCANCELLATIONTHRESHOLD = 600

_BINANCE_TWM_MAXQUEUESIZE                     = 50000
_BINANCE_TWM_CONNECTIONGENERATIONTIMEWINDOW_S = (15, 45)
_BINANCE_TWM_CONNECTIONGENERATIONINTERVAL_NS  = 1000e6
_BINANCE_TWM_EXPIRATIONCHECKINTERVAL_NS       = 100e6
_BINANCE_TWM_NSYMBOLSPERCONN                  = 50    #Recommended maximum number of streams per connection according to Binance WebSocket API is 200, in this program, it only utilizes 75% of that maximum recommended number (50 streams per conn, 3 streams per symbol -> 150 symbols per conn)
_BINANCE_TWM_STREAMRENEWALPERIOD_S            = 60*60 #Every 1 hour
_BINANCE_TWM_CLOSEDKLINESMAXWAITTIME_S        = 10

_BINANCE_TWM_STREAMDATATYPE_KLINE       = 'continuous_kline'
_BINANCE_TWM_STREAMDATATYPE_DEPTHUPDATE = 'depthUpdate'
_BINANCE_TWM_STREAMDATATYPE_AGGTRADES   = 'aggTrade'
_BINANCE_TWM_STREAMDATATYPE_FLAGS = {_BINANCE_TWM_STREAMDATATYPE_KLINE:       0b001,
                                     _BINANCE_TWM_STREAMDATATYPE_DEPTHUPDATE: 0b010,
                                     _BINANCE_TWM_STREAMDATATYPE_AGGTRADES:   0b100}

_BINANCE_CONTRACTTYPE_PERPETUAL = 'PERPETUAL'
_BINANCE_RATELIMITTYPE_ORDERS        = 'ORDERS'
_BINANCE_RATELIMITTYPE_REQUESTWEIGHT = 'REQUEST_WEIGHT'

_BINANCE_ORDERSTATUS = {'NEW':              {'result': None,  'complete': False},
                        'PARTIALLY_FILLED': {'result': True,  'complete': False},
                        'FILLED':           {'result': True,  'complete': True},
                        'CANCELED':         {'result': False, 'complete': True},
                        'PENDING_CANCEL':   {'result': False, 'complete': True},
                        'REJECTED':         {'result': False, 'complete': True},
                        'EXPIRED':          {'result': True,  'complete': True},
                        'EXPIRED_IN_MATCH': {'result': True,  'complete': True}}

_BINANCE_FUTURESSTART_YEAR  = 2019
_BINANCE_FUTURESSTART_MONTH = 8
_BINANCE_FUTURESSTART_YEAR_TIMESTAMP  = 1546300800
_BINANCE_FUTURESSTART_MONTH_TIMESTAMP = 1564617600

_FORMATTEDKLINETYPE_FETCHED  = 0
_FORMATTEDKLINETYPE_DUMMY    = 1
_FORMATTEDKLINETYPE_STREAMED = 2

_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

KLINTERVAL        = atmEta_Constants.KLINTERVAL
KLINTERVAL_CLIENT = atmEta_Constants.KLINTERVAL_CLIENT
KLINTERVAL_STREAM = atmEta_Constants.KLINTERVAL_STREAM
KLINTERVAL_S      = atmEta_Constants.KLINTERVAL_S

ORDERBOOKACCEPTANCERANGE = atmEta_Constants.ORDERBOOKACCEPTANCERANGE

SUBSCRIPTIONMODE_BIDSANDASKS = 0b01
SUBSCRIPTIONMODE_AGGTRADES   = 0b10

class procManager_BinanceAPI:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA):
        print(termcolor.colored("   Initializing", 'green'), termcolor.colored("BINANCEAPI Manager", 'light_blue'), termcolor.colored("----------------------------------------------------------------------------------------------------------------", 'green'))
        #IPC Assistance
        self.ipcA = ipcA
        #Project Path
        self.path_project = path_project
        #Process Configuration
        self.config_BinanceAPI = {'rateLimitIPSharingNumber': 1,
                                  'assetRegFilter':           None,
                                  'print_Update':             True,
                                  'print_Warning':            True,
                                  'print_Error':              True}
        self.__readBinanceAPIConfig()
        #Network & Binance Connection
        self.__connection_network_first   = True
        self.__connection_network         = False
        self.__connection_binance         = -1 #[-1]: Disconnected, [0]: Available, [1]: Maintenance
        self.__connection_serverAvailable = False
        self.__connection_lastConnectionsCheck_ns = 0
        #Binance
        self.__binance_client_default = None
        self.__binance_client_users   = dict()
        self.__binance_MarketExchangeInfo_Symbols     = dict()
        self.__binance_MarketExchangeInfo_Symbols_Set = set()
        self.__binance_MarketExchangeInfo_RateLimits  = None
        self.__binance_MarketExchangeInfo_LastRead_intervalN = -1
        #---TWM Connections
        self.__binance_TWM                             = None
        self.__binance_TWM_StreamQueue                 = set()
        self.__binance_TWM_Connections                 = dict()
        self.__binance_TWM_StreamingData               = dict()
        self.__binance_TWM_StreamingData_Subscriptions = dict()
        self.__binance_TWM_LastConnectionGeneration_ns = 0
        self.__binance_TWM_LastExpirationCheck_ns      = 0
        self.__binance_TWM_LastRenewal_intervalN       = 0
        self.__binance_TWM_OverFlowDetected            = False
        self.__binance_TWM_StreamHandlers = {_BINANCE_TWM_STREAMDATATYPE_KLINE:       self.__processTWMStreamMessages_Kline,
                                             _BINANCE_TWM_STREAMDATATYPE_DEPTHUPDATE: self.__processTWMStreamMessages_DepthUpdate,
                                             _BINANCE_TWM_STREAMDATATYPE_AGGTRADES:   self.__processTWMStreamMessages_AggTrade}
        #---Fetch Control
        self.__binance_fetchBlock                                 = False
        self.__binance_firstKlineOpenTSSearchRequests             = dict()
        self.__binance_firstKlineOpenTSSearchQueue_lastUpdated_ns = 0
        self.__binance_firstKlineOpenTSSearchQueue                = set()
        self.__binance_fetchRequests                              = dict()
        self.__binance_fetchRequests_SymbolsByPriority            = {0: set(), 1: set(), 2: set()}
        #---Account Data
        self.__binance_activatedAccounts_LocalIDs        = set()
        self.__binance_activatedAccounts_maxActivation   = 0
        self.__binance_activatedAccounts_readInterval_ns = _BINANCE_ACCOUNTDATAREADINTERVAL_MIN_NS
        self.__binance_activatedAccounts_lastDataRead_ns = 0
        self.__binance_activatedAccounts_dataReadRequest = False
        self.__binance_createdOrders                     = dict()

        #Initial Data Share
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CONFIGURATION', prdContent = self.config_BinanceAPI.copy())

        #FAR Registration
        #---GUI
        self.ipcA.addFARHandler('updateConfiguration', self.__far_updateConfiguration, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---DATAMANAGER
        self.ipcA.addFARHandler('getFirstKlineOpenTS', self.__far_addFirstKlineOpenTSSearchRequest, executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        self.ipcA.addFARHandler('fetchKlines',         self.__far_addKlineFetchRequestQueue,        executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        #---TRADEMANAGER
        self.ipcA.addFARHandler('generateAccountInstance', self.__far_generateAccountInstance, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('removeAccountInstance',   self.__far_removeAccountInstance,   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('setPositionMarginType',   self.__far_setPositionMarginType,   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('setPositionLeverage',     self.__far_setPositionLeverage,     executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('createOrder',             self.__far_createOrder,             executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        #---#COMMON#
        self.ipcA.addFARHandler('registerKlineStreamSubscription',   self.__far_registerKlineStreamSubscription,   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('unregisterKlineStreamSubscription', self.__far_unregisterKlineStreamSubscription, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

        #Process Control
        self.__processLoopContinue = True

        print(termcolor.colored("   BINANCAPI Manager", 'light_blue'), termcolor.colored("Initialization Complete! -----------------------------------------------------------------------------------------------------", 'green'))
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    
    
    #Manager Process Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        while self.__processLoopContinue:
            t_current_ns = time.perf_counter_ns()

            #Check network and server connection every certain interval
            if _CONNECTIONSCHECKINTERVAL_NS <= t_current_ns-self.__connection_lastConnectionsCheck_ns:
                self.__checkConnections()
                self.__connection_lastConnectionsCheck_ns = t_current_ns

            #If both network and binance connections are True
            if (self.__connection_network) and (self.__connection_binance == 0):
                #Check and update the API rate limit control variables
                self.__updateAPIRateLimiter()
                #Check market exchange info every certain interval
                self.__getMarketExchangeInfo()
                #Process WebSocket
                self.__processTWMStreamConnections()
                self.__processTWMStreamMessages()
                #Process any exsiting FirstKlineOpenTSSearchQueues and FetchRequests
                self.__processFirstKlineOpenTSSearchRequests()
                self.__processFetchRequests()
                #Get data of any existing activated accounts
                self.__readActivatedAccountsData()
                #Check the completion of any created orders
                self.__checkCreatedOrdersCompletion()

            #Process any exsiting FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()

            #Loop Sleep
            if self.__loopSleepDeterminer(): time.sleep(0.001)

        #Terminate TWM if it is alive
        try: 
            if self.__binance_TWM.is_alive(): self.__binance_TWM.stop()
            self.__binance_TWM.join()
        except: pass

    def __loopSleepDeterminer(self):
        return True

    def terminate(self, requester):
        self.__processLoopContinue = False
    #Manager Process Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Internal Functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #---Manager Configuration
    def __readBinanceAPIConfig(self):
        #[1]: Configuration File Read
        try:
            config_dir = os.path.join(self.path_project, 'configs', 'binanceAPIConfig.config')
            with open(config_dir, 'r') as f:
                config_loaded = json.load(f)
        except: 
            config_loaded = dict()

        #[2]: Contents Verification
        #---[2-1]: Rate Limit IP Sharing Number
        rateLimitIPSharingNumber = config_loaded.get('rateLimitIPSharingNumber', 1)
        if not isinstance(rateLimitIPSharingNumber, int): rateLimitIPSharingNumber = 1
        if not 1 <= rateLimitIPSharingNumber <= 5:        rateLimitIPSharingNumber = 1
        #---[2-2]: Asset Registration Filter
        assetRegFilter = config_loaded.get('assetRegFilter', None)
        if (assetRegFilter is not None) and not(isinstance(assetRegFilter, list)): assetRegFilter = None
        assetRegFilter = set(assetRegFilter) if assetRegFilter is not None else None
        #---[2-3]: Print_Update
        print_update = config_loaded.get('print_Update', True)
        if not isinstance(print_update, bool): print_update = True
        #---[2-4]: Print_Warning
        print_warning = config_loaded.get('print_Warning', True)
        if not isinstance(print_warning, bool): print_warning = True
        #---[2-5]: Print_Error
        print_error = config_loaded.get('print_Error', True)
        if not isinstance(print_error, bool): print_error = True

        #[3]: Update and save the configuration
        self.config_BinanceAPI = {'rateLimitIPSharingNumber': int(rateLimitIPSharingNumber),
                                  'assetRegFilter':           assetRegFilter,
                                  'print_Update':             print_update,
                                  'print_Warning':            print_warning,
                                  'print_Error':              print_error}
        self.__saveBinanceAPIConfig()
    def __saveBinanceAPIConfig(self):
        #[1]: Reformat config for save
        config = self.config_BinanceAPI
        config_toSave = {'rateLimitIPSharingNumber': config['rateLimitIPSharingNumber'],
                         'assetRegFilter':           None,
                         'print_Update':             config['print_Update'],
                         'print_Warning':            config['print_Warning'],
                         'print_Error':              config['print_Error']}
        if config['assetRegFilter'] is not None: config_toSave['assetRegFilter'] = list(config['assetRegFilter'])

        #[2]: Save the reformatted configuration file
        config_dir = os.path.join(self.path_project, 'configs', 'binanceAPIConfig.config')
        try:
            with open(config_dir, 'w') as f:
                json.dump(config_toSave, f, indent=4)
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Save Binance API Manager Configuration. User Attention Strongly Advised"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')
    
    #---Market Connection & Management
    def __checkConnections(self):
        #[1]: Get new connection status
        self.__connection_network = self.__checkNetworkConnection()
        if self.__connection_network and self.__connection_network_first: 
            self.__connection_network_first = False
            time.sleep(5)
        if self.__connection_network: self.__connection_binance = self.__checkBinanceConnection()
        else:                         self.__connection_binance = _CONNECTIONSTATUS_BINANCE_DISCONNECTED
        serverAvailable = self.__connection_network and self.__connection_binance == _CONNECTIONSTATUS_BINANCE_CONNECTED

        #[2]: Connection status update handling
        if   self.__connection_serverAvailable and not serverAvailable: self.__onServerUnavailable() #[1]: Available   -> Unavailable
        elif not self.__connection_serverAvailable and serverAvailable: self.__onServerAvailable()   #[2]: Unavailable -> Available
        self.__connection_serverAvailable = serverAvailable
    def __checkNetworkConnection(self):
        testSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        testSocket.settimeout(1)
        try:
            testSocket.connect(("www.google.com", 80))
            testSocket.close()
            return True
        except: return False
    def __checkBinanceConnection(self):
        try:
            if self.__binance_client_default is None:
                client = binance.Client()
                status = client.get_system_status()['status']
                self.__binance_client_default = client
                return status
            else: 
                return self.__binance_client_default.get_system_status()['status']
        except: 
            return _CONNECTIONSTATUS_BINANCE_DISCONNECTED
    def __onServerAvailable(self):
        self.__logger(message = "BINANCE SERVER NOW AVAILABLE!", logType = 'Update', color = 'light_green')
        #Market Exchange Info Read
        if self.__getMarketExchangeInfo(): self.__logger(message = "Binance Futures Exchange Information Read Successful", logType = 'Update', color = 'light_green')
        else:                              self.__logger(message = "Binance Futures Exchange Information Read Failed",     logType = 'Update', color = 'light_red')
        #Threaded WebSocket Manager
        if self.__binance_TWM is None:
            self.__binance_TWM = binance.ThreadedWebsocketManager(max_queue_size = _BINANCE_TWM_MAXQUEUESIZE)
            self.__binance_TWM.start()
            self.__logger(message = "Binance Threaded WebSocket Manager Generated and Started", logType = 'Update', color = 'light_green')
    def __onServerUnavailable(self):
        self.__logger(message = "BINANCE SERVER NOW UNAVAILABLE!", logType = 'Update', color = 'light_red')
        #[1]: Reset the default binance client and market info
        #---[1-1]: Clear the binance default client
        self.__binance_client_default = None
        #---[1-2]: Clear the read market exchange info
        self.__binance_MarketExchangeInfo_Symbols.clear()
        self.__binance_MarketExchangeInfo_Symbols_Set.clear()
        self.__binance_MarketExchangeInfo_RateLimits         = None
        self.__binance_MarketExchangeInfo_LastRead_intervalN = -1
        #[2]: WebSocket
        self.__clearFetchRequests(symbols = None)
        if self.__binance_TWM.is_alive():
            for connectionID in self.__binance_TWM_Connections:
                connection     = self.__binance_TWM_Connections[connectionID]
                connectionName = connection['connectionName']
                self.__binance_TWM.stop_socket(connectionName)
        self.__binance_TWM_StreamQueue.clear()
        self.__binance_TWM_Connections.clear()
        self.__binance_TWM_StreamingData.clear()
        self.__binance_TWM_OverFlowDetected = False
    def __updateAPIRateLimiter(self):
        for limitType in self.__binance_MarketExchangeInfo_RateLimits:
            for rateLimit in self.__binance_MarketExchangeInfo_RateLimits[limitType]:
                t_current_intervalN = int(time.time()/rateLimit['interval_sec'])
                if not (rateLimit['tracker_intervalN'] < t_current_intervalN): continue
                if (rateLimit['tracker_intervalN'] != -1):
                    rateLimit['tracker_usedLimit'] = 0
                    self.__binance_fetchBlock = False
                rateLimit['tracker_intervalN'] = t_current_intervalN
    def __getMarketExchangeInfo(self):
        #[1]: Processing Interval Check
        t_current_intervalN = int(time.time()/_BINANCE_EXCHANGEINFOREADINTERVAL_S)
        if not (self.__binance_MarketExchangeInfo_LastRead_intervalN < t_current_intervalN): 
            return False

        #[2]: Market Exchange Info Read Attempt
        exchangeInfo_futures = None
        nAttempts = 0
        while (nAttempts < _BINANCE_EXCHANGEINFOREADMAXATTEMPT):
            self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 1, apply = True)
            try:    
                exchangeInfo_futures = self.__binance_client_default.futures_exchange_info()
                break
            except: 
                nAttempts += 1
                time.sleep(_BINANCE_EXCHANGEINFOREADATTEMPTINTERVAL_S)
        if exchangeInfo_futures is None: 
            return False

        #[3]: If rateLimits is not read, read it
        if self.__binance_MarketExchangeInfo_RateLimits is None:
            """
            <Example>
            exchangeInfo_futures['rateLimits'] = [{'rateLimitType': 'REQUEST_WEIGHT', 'interval': 'MINUTE', 'intervalNum': 1, 'limit': 2400}, 
                                                  {'rateLimitType': 'ORDERS', 'interval': 'MINUTE', 'intervalNum': 1, 'limit': 1200}, 
                                                  {'rateLimitType': 'ORDERS', 'interval': 'SECOND', 'intervalNum': 10, 'limit': 300}]
            """
            self.__binance_MarketExchangeInfo_RateLimits = dict()
            for rateLimit in exchangeInfo_futures['rateLimits']: 
                limitType = rateLimit['rateLimitType']
                if limitType not in self.__binance_MarketExchangeInfo_RateLimits: 
                    self.__binance_MarketExchangeInfo_RateLimits[limitType] = []
                if   rateLimit['interval'] == 'SECOND': interval_sec =    1*rateLimit['intervalNum']
                elif rateLimit['interval'] == 'MINUTE': interval_sec =   60*rateLimit['intervalNum']
                elif rateLimit['interval'] == 'HOUR':   interval_sec = 3600*rateLimit['intervalNum']
                else: 
                    interval_sec = None
                    self.__logger(message = f"An unexpected interval detected while attempting to read market exchange info - rateLimits. User attention advised!\n * {str(rateLimit)}", 
                                  logType = 'Warning', 
                                  color   = 'light_red')
                if interval_sec is not None: 
                    rl_this = {'interval_sec':      interval_sec, 
                               'limit':             rateLimit['limit'], 
                               'tracker_intervalN': int(time.time()/interval_sec), 
                               'tracker_usedLimit': rateLimit['limit']}
                    self.__binance_MarketExchangeInfo_RateLimits[limitType].append(rl_this)
            #Activated Accounts Data Read Limit Update
            self.__computeMaximumNumberOfAccountsActivation()
            self.__computeActivatedAccountsDataReadInterval()

        #[4]: Read Symbols Info
        #---[4-1]: Re-organize the currency information in terms of the symbols
        marketExchangeInfo_Symbols = dict()
        """
        <Example>
        exchangeInfo_futures['symbols'][0] = {'symbol': 'BTCUSDT', 
                                              'pair': 'BTCUSDT', 
                                              'contractType': 'PERPETUAL', 
                                              'deliveryDate': 4133404800000, 
                                              'onboardDate': 1569398400000, 
                                              'status': 'TRADING', 
                                              'maintMarginPercent': '2.5000', 
                                              'requiredMarginPercent': '5.0000', 
                                              'baseAsset': 'BTC', 
                                              'quoteAsset': 'USDT', 
                                              'marginAsset': 'USDT', 
                                              'pricePrecision': 2, 
                                              'quantityPrecision': 3, 
                                              'baseAssetPrecision': 8, 
                                              'quotePrecision': 8, 
                                              'underlyingType': 'COIN', 
                                              'underlyingSubType': ['PoW'], 
                                              'settlePlan': 0, 
                                              'triggerProtect': '0.0500', 
                                              'liquidationFee': '0.012500', 
                                              'marketTakeBound': '0.05', 
                                              'maxMoveOrderLimit': 10000, 
                                              'filters': [{'minPrice': '556.80', 'tickSize': '0.10', 'maxPrice': '4529764', 'filterType': 'PRICE_FILTER'}, 
                                                          {'minQty': '0.001', 'stepSize': '0.001', 'maxQty': '1000', 'filterType': 'LOT_SIZE'}, 
                                                          {'minQty': '0.001', 'maxQty': '120', 'filterType': 'MARKET_LOT_SIZE', 'stepSize': '0.001'}, 
                                                          {'limit': 200, 'filterType': 'MAX_NUM_ORDERS'}, 
                                                          {'limit': 10, 'filterType': 'MAX_NUM_ALGO_ORDERS'}, 
                                                          {'notional': '100', 'filterType': 'MIN_NOTIONAL'}, 
                                                          {'multiplierDecimal': '4', 'multiplierUp': '1.0500', 'multiplierDown': '0.9500', 'filterType': 'PERCENT_PRICE'}], 
                                              'orderTypes': ['LIMIT', 'MARKET', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET', 'TRAILING_STOP_MARKET'], 
                                              'timeInForce': ['GTC', 'IOC', 'FOK', 'GTX', 'GTD']}
        """ #Expand to check a data example
        for currencyInfo in exchangeInfo_futures['symbols']:
            arf = self.config_BinanceAPI['assetRegFilter']
            if (arf is None or currencyInfo['symbol'] in arf) and (currencyInfo['contractType'] == _BINANCE_CONTRACTTYPE_PERPETUAL): 
                marketExchangeInfo_Symbols[currencyInfo['symbol']] = currencyInfo

        #---[4-2]: Identify added and removed assets
        symbols_new  = set(marketExchangeInfo_Symbols)
        symbols_prev = self.__binance_MarketExchangeInfo_Symbols_Set
        symbols_added   = symbols_new-symbols_prev
        symbols_removed = symbols_prev-symbols_new
        symbols_still   = symbols_prev-symbols_added-symbols_removed

        #------[4-2-1]: Handle Added Symbols
        for symbol in symbols_added:
            #Save symbol information & prepare local tracker
            marketExchangeInfo_thisSymbol = marketExchangeInfo_Symbols[symbol]
            self.__binance_MarketExchangeInfo_Symbols[symbol] = marketExchangeInfo_thisSymbol
            #Check for stream need and add to the queue if needed
            if (marketExchangeInfo_thisSymbol['status'] == 'TRADING') and (symbol not in self.__binance_TWM_StreamingData): 
                self.__binance_TWM_StreamQueue.add(symbol)
            #Send FAR to the DataManager for the currency registration
            self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'registerCurrency', functionParams = {'symbol': symbol, 'info': marketExchangeInfo_thisSymbol}, farrHandler = None)

        #------[4-2-2]: Handle Removed Symbols
        for symbol in symbols_removed:
            #Market Exchange Info Update
            del self.__binance_MarketExchangeInfo_Symbols[symbol]
            self.__binance_MarketExchangeInfo_Symbols_Set.remove(symbol)
            #Queue Control
            if symbol in self.__binance_firstKlineOpenTSSearchRequests:
                del self.__binance_firstKlineOpenTSSearchRequests[symbol]
                if symbol in self.__binance_firstKlineOpenTSSearchQueue: 
                    self.__binance_firstKlineOpenTSSearchQueue.remove(symbol)
            if symbol in self.__binance_TWM_StreamQueue:                
                self.__binance_TWM_StreamQueue.remove(symbol)
            #Status Update Announcement
            self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'onCurrencyInfoUpdate', functionParams = {'symbol': symbol, 'infoUpdates': [{'id': ('status',), 'value': 'REMOVED'}]}, farrHandler = None)

        #------[4-2-3]: Check for any changes to the currencies information and respond
        for symbol in symbols_still:
            currencyInfo_prev = self.__binance_MarketExchangeInfo_Symbols[symbol]
            currencyInfo_new  = marketExchangeInfo_Symbols[symbol]
            #Internal currency information response
            updates = []
            #---Trading Status
            status_prev = currencyInfo_prev['status']
            status_new  = currencyInfo_new['status']
            if status_prev != status_new:
                if (status_prev != 'TRADING') and (status_new == 'TRADING'): #Not Trading -> Trading
                    if symbol in self.__binance_firstKlineOpenTSSearchRequests: self.__binance_firstKlineOpenTSSearchQueue.add(symbol) #Add to the first kline open TS search queue
                    if symbol not in self.__binance_TWM_StreamingData:          self.__binance_TWM_StreamQueue.add(symbol)             #Add to the stream queue
                if (status_prev == 'TRADING') and (status_new != 'TRADING'): #Trading -> Not Trading
                    if symbol in self.__binance_firstKlineOpenTSSearchQueue: self.__binance_firstKlineOpenTSSearchQueue.remove(symbol) #Remove from the first kline open TS search queue
                    if symbol in self.__binance_TWM_StreamQueue:             self.__binance_TWM_StreamQueue.remove(symbol)             #Remove from the stream queue
                update = {'id':    ('status',),
                          'value': status_new}
                updates.append(update)
                currencyInfo_prev['status'] = status_new
            #---Filters <TO BE IMPLEMENTED>
            for marketFilter in currencyInfo_new['filters']:
                pass
            #---Precisions <TO BE IMPLEMENTED>
            pass
            #---Updates Announcement
            if updates:
                self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                  functionID     = 'onCurrencyInfoUpdate', 
                                  functionParams = {'symbol': symbol, 
                                                    'infoUpdates': updates}, 
                                  farrHandler    = None)

        #[5]: Update symbols set
        self.__binance_MarketExchangeInfo_Symbols_Set = symbols_new

        #[6]: Record the last market exhange info read minute
        self.__binance_MarketExchangeInfo_LastRead_intervalN = t_current_intervalN

        #[7]: Return 'True' to indicate successful market exchange info read
        return True
    def __checkAPIRateLimit(self, limitType, weight, extraOnly = False, apply = True, printUpdated = True):
        #[1]: Rate Limits Check
        if self.__binance_MarketExchangeInfo_RateLimits is None:
            return None

        #[2]: Test
        testPass = True
        for rateLimit in self.__binance_MarketExchangeInfo_RateLimits[limitType]:
            limit_maxEffective = int(rateLimit['limit']/self.config_BinanceAPI['rateLimitIPSharingNumber'])
            if extraOnly:
                limit_maxEffective -= rateLimit['interval_sec']
                limit_maxEffective -= len(self.__binance_activatedAccounts_LocalIDs)*5*int(rateLimit['interval_sec']*1e9/_BINANCE_ACCOUNTDATAREADINTERVAL_MIN_NS)
                limit_maxEffective -= len(self.__binance_createdOrders)             *1*int(rateLimit['interval_sec']*1e9/_BINANCE_CREATEDORDERCHECKINTERVAL_NS)
            if (limit_maxEffective <= rateLimit['tracker_usedLimit']+weight):
                testPass = False
                break

        #[3]: Result Handling
        if testPass and apply:
            comment = ""
            for rateLimit in self.__binance_MarketExchangeInfo_RateLimits[limitType]:
                rateLimit['tracker_usedLimit'] += weight
                limit_maxEffective_withExtra = int(rateLimit['limit']/self.config_BinanceAPI['rateLimitIPSharingNumber'])
                comment += f"\n * [{limitType}-{rateLimit['interval_sec']}]: {rateLimit['tracker_usedLimit']}/{limit_maxEffective_withExtra}"
            if printUpdated: self.__logger(message = f"API Used RateLimit Updated{comment}", logType = 'Update', color = 'light_yellow')

        #[4]: Result Return
        return testPass

    #---WebSocket
    def __processTWMStreamConnections(self):
        #[1]: Expiration Handling
        _connectionIDs_removed = list()
        for _connectionID in self.__binance_TWM_Connections:
            _connection = self.__binance_TWM_Connections[_connectionID]
            if (_connection['expired'] == True):
                _connectionIDs_removed.append(_connectionID)
                for _symbol in _connection['symbols']:
                    self.__binance_TWM_StreamingData[_symbol]['connectionID'] = None
                    if (self.__binance_MarketExchangeInfo_Symbols[_symbol]['status'] == 'TRADING'): self.__binance_TWM_StreamQueue.add(_symbol)
        for _connectionID in _connectionIDs_removed: del self.__binance_TWM_Connections[_connectionID]
        #[2]: Stream Queue Check & New Connection Generation
        if ((0 < len(self.__binance_TWM_StreamQueue)) and (_BINANCE_TWM_CONNECTIONGENERATIONINTERVAL_NS <= time.perf_counter_ns()-self.__binance_TWM_LastConnectionGeneration_ns)): self.__generateTWMStreamConnection()
        #[3]: Expiration Checks
        #---[3-1]: By OverFlow
        if (self.__binance_TWM_OverFlowDetected == True):
            for _connectionID in self.__binance_TWM_Connections:
                _connection = self.__binance_TWM_Connections[_connectionID]
                if (_connection['expired'] == False): self.__expireTWMStreamConnection(connectionID = _connectionID)
            self.__binance_TWM_OverFlowDetected = False
            self.__logger(message = f"A TWM Queue Overflow detected, all connections will be regenerated.", logType = 'Error', color = 'light_cyan')
        else:
            if (_BINANCE_TWM_EXPIRATIONCHECKINTERVAL_NS <= time.perf_counter_ns()-self.__binance_TWM_LastExpirationCheck_ns):
                #[3-2]: By Last Closed Kline Receival Time
                for _connectionID in self.__binance_TWM_Connections:
                    _connection = self.__binance_TWM_Connections[_connectionID]
                    if (_connection['expired'] == False):
                        for _symbol in _connection['symbols']:
                            _streamingData = self.__binance_TWM_StreamingData[_symbol]
                            if (_streamingData['firstReceivedKlineOpenTS'] is not None):
                                _t_current_s = time.time()
                                _expectedCurrentKlineOpenTS            = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = _t_current_s, mrktReg = _streamingData['firstReceivedKlineOpenTS'], nTicks =  0)
                                _expectedLastReceivedClosedKlineOpenTS = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = _t_current_s, mrktReg = _streamingData['firstReceivedKlineOpenTS'], nTicks = -1)
                                if ((_BINANCE_TWM_CLOSEDKLINESMAXWAITTIME_S <= _t_current_s-_expectedCurrentKlineOpenTS)        and                                                             #More Than Maximum Closed Kline Wait Time Has Passed Since the Current Expected Kline OpenTS
                                    (_streamingData['firstReceivedKlineOpenTS']      <= _expectedLastReceivedClosedKlineOpenTS) and                                                             #ExpectedLastReceivedClosedKlineOpenTS is at or after the FirstReceivedKlineOpenTS
                                    ((_streamingData['lastReceivedClosedKlineOpenTS'] is None) or (_streamingData['lastReceivedClosedKlineOpenTS'] < _expectedLastReceivedClosedKlineOpenTS))): #ExpectedLastReceivedClosedKlineOpenTS has not been received yet
                                    self.__expireTWMStreamConnection(connectionID = _connectionID)
                                    self.__logger(message = f"WebSocket Connection {_connectionID} Expired. 'Closed Kline Not Received For More Than {_BINANCE_TWM_CLOSEDKLINESMAXWAITTIME_S} Seconds'", logType = 'Update', color = 'light_cyan')
                                    break
                #[3-3]: Connection Renewal
                _nOrderBookFetchRequests   = sum(1 for _symbol in self.__binance_fetchRequests if (self.__binance_fetchRequests[_symbol]['orderBookFetchRequest'] == True))
                _nExpiredConnectionSymbols = sum(len(_connection['symbols']) for _connection in self.__binance_TWM_Connections.values() if (_connection['expired'] == True))
                _t_current_s         = time.time()
                _t_current_intervalN = int(_t_current_s/60)
                _t_current_s_minRel  = _t_current_s%60
                _test_renewalIntervalN         = (self.__binance_TWM_LastRenewal_intervalN < _t_current_intervalN)
                _test_generationTimeWindow     = ((_BINANCE_TWM_CONNECTIONGENERATIONTIMEWINDOW_S[0] <= _t_current_s_minRel) and (_t_current_s_minRel <= _BINANCE_TWM_CONNECTIONGENERATIONTIMEWINDOW_S[1]))
                _test_lastConnectionGeneration = (_BINANCE_TWM_CONNECTIONGENERATIONINTERVAL_NS <= time.perf_counter_ns()-self.__binance_TWM_LastConnectionGeneration_ns)
                if ((_test_renewalIntervalN == True) and (_test_generationTimeWindow == True) and (_test_lastConnectionGeneration == True)):
                    _renewalExpired = False
                    for _connectionID in self.__binance_TWM_Connections:
                        _connection = self.__binance_TWM_Connections[_connectionID]
                        if (_connection['expired'] == False):
                            _nSymbols = len(_connection['symbols'])
                            _test_needRenewal             = (_BINANCE_TWM_STREAMRENEWALPERIOD_S <= _t_current_s-_connection['connectionTime'])
                            _test_streamQueue             = (_nExpiredConnectionSymbols+_nSymbols <= _BINANCE_TWM_NSYMBOLSPERCONN)
                            _test_nOrderBookFetchRequests = (_nOrderBookFetchRequests  +_nSymbols <= _BINANCE_TWM_NSYMBOLSPERCONN)
                            if ((_test_needRenewal == True) and (_test_streamQueue == True) and (_test_nOrderBookFetchRequests == True)): 
                                self.__expireTWMStreamConnection(connectionID = _connectionID)
                                _nOrderBookFetchRequests   += _nSymbols
                                _nExpiredConnectionSymbols += _nSymbols
                                _renewalExpired = True
                                self.__logger(message = f"WebSocket Connection {_connectionID} Expired. 'Renewal Period'", logType = 'Update', color = 'light_cyan')
                    if (_renewalExpired == True): self.__binance_TWM_LastRenewal_intervalN = _t_current_intervalN
                #Last Expiration Check Record
                self.__binance_TWM_LastExpirationCheck_ns = time.perf_counter_ns()
    def __expireTWMStreamConnection(self, connectionID):
        connection = self.__binance_TWM_Connections[connectionID]
        #[1]: Socket Stop
        self.__binance_TWM.stop_socket(connection['connectionName'])
        #[2]: Expired Flag Raise & Buffer Update Wait
        connection['expired'] = True
        while connection['buffer_writing']: time.sleep(0.001)
        #[3]: Announcement Tracker Update
        for symbol in connection['symbols']: self.__binance_TWM_StreamingData[symbol]['lastAnnounced_ns'] = 0
        #[4]: Fetch Requests Clearing
        self.__clearFetchRequests(symbols = connection['symbols'])
    def __generateTWMStreamConnection(self):
        #[1]: Symbols Selection
        _symbols = list()
        while ((len(_symbols) < _BINANCE_TWM_NSYMBOLSPERCONN) and (0 < len(self.__binance_TWM_StreamQueue))): _symbols.append(self.__binance_TWM_StreamQueue.pop())
        #[2]: Stream Strings
        _symbols_lower = [_symbol.lower() for _symbol in _symbols]
        _streams = [f"{_symbol_lower}_perpetual@continuousKline_{KLINTERVAL_STREAM}" for _symbol_lower in _symbols_lower]\
                  +[f"{_symbol_lower}@depth"                                         for _symbol_lower in _symbols_lower]\
                  +[f"{_symbol_lower}@aggTrade"                                      for _symbol_lower in _symbols_lower]
        #[3]: Socket Start Attempt
        _connection = {'connectionName': None,
                       'connectionID':   None,
                       'connectionTime': time.time(),
                       'buffer':         list(),
                       'buffer_writing': False,
                       'symbols':        set(_symbols),
                       'expired':        False}
        _nTries         = 0
        _connectionName = None
        while (_nTries < _BINANCE_WEBSOCKETSTREAMCONNECTIONTRIES_MAX):
            _nTries += 1
            try:
                _connectionName = self.__binance_TWM.start_futures_multiplex_socket(callback=self.__TWM_getStreamReceiverFunction(connection = _connection), streams=_streams)
                if (_connectionName is not None): break
            except Exception as e:
                self.__logger(message = f"An unexpected error occurred while attempting to generate a TWM stream connection [{_nTries}/{_BINANCE_WEBSOCKETSTREAMCONNECTIONTRIES_MAX}]\n * {str(e)}", logType = 'Error', color = 'light_red')
                time.sleep(_BINANCE_WEBSOCEKTSTREAMCONNECTIONINTERVAL_NS/1e9)
        #[4]: Upon Successful Connection Generation, Create A Tracker Instance. If connection generation failed, add back the symbols to the queue
        if (_connectionName is None): self.__binance_TWM_StreamQueue = self.__binance_TWM_StreamQueue.union(set(_symbols))
        else:
            #[3-1]: Connection Data Update
            _connection['connectionID']   = time.time_ns()
            _connection['connectionName'] = _connectionName
            self.__binance_TWM_Connections[_connection['connectionID']] = _connection
            #[3-2]: Streaming Symbol Data Formatting
            for _symbol in _symbols:
                self.__initializeStreamingDataForSymbol(symbol = _symbol, connectionID = _connection['connectionID'])
                if (_symbol not in self.__binance_TWM_StreamingData_Subscriptions): self.__initializeStreamDataSubscriptionsForSymbol(symbol = _symbol)
            self.__logger(message = f"WebSocket Connection Generation Successful! <ConnectionID: {_connection['connectionID']}, nSymbols: {len(_symbols)}>", logType = 'Update', color = 'light_green')
        #[5]: Last Connection Generation Time Record
        self.__binance_TWM_LastConnectionGeneration_ns = time.perf_counter_ns()
    def __initializeStreamingDataForSymbol(self, symbol, connectionID):
        if symbol in self.__binance_TWM_StreamingData: 
            sd_this = self.__binance_TWM_StreamingData[symbol]
            sd_this['connectionID'] = connectionID
            sd_this['firstReceivedKlineOpenTS']      = None
            sd_this['lastReceivedClosedKlineOpenTS'] = None
            sd_this['depth']['fetchRequested'] = False
            sd_this['depth']['lastUID']        = None
            sd_this['depth']['lastUID_Fetch']  = None
        else:
            self.__binance_TWM_StreamingData[symbol] = {'connectionID':                  connectionID,
                                                        'firstReceivedKlineOpenTS':      None,
                                                        'lastReceivedClosedKlineOpenTS': None,
                                                        'klines':                        dict(),
                                                        'depth':                         {'buffer': list(), 'fetchRequested': False, 'bids': dict(), 'asks': dict(), 'lastUID': None, 'lastUID_Fetch': None},
                                                        'aggTrades':                     {'buffer': list(), 'lastTradePrice': None},
                                                        'updatedTypes':                  0b000,
                                                        'lastAnnounced_ns':              0}
    def __initializeStreamDataSubscriptionsForSymbol(self, symbol):
        _subscription_DATAMANAGER = {'subscriber':     'DATAMANAGER',
                                     'subscriptionID': None,
                                     'fID_kline':     'onKlineStreamReceival',
                                     'fID_depth':     None,
                                     'fID_aggTrades': None}
        self.__binance_TWM_StreamingData_Subscriptions[symbol] = {'fetchPriority': 2, 'subscriptions': [_subscription_DATAMANAGER,]}
    
    #---First Kline Open TS Search
    def __processFirstKlineOpenTSSearchRequests(self):
        #[1]: Instances
        sReqs   = self.__binance_firstKlineOpenTSSearchRequests
        sQueues = self.__binance_firstKlineOpenTSSearchQueue
        meis    = self.__binance_MarketExchangeInfo_Symbols

        #[2]: Queue Update
        t_current_ns = time.time_ns()
        t_current_s  = int(t_current_ns/1e9)
        if _BINANCE_FIRSTKLINEOPENTSSEARCHQUEUEUPDATEINTERVAL_NS <= t_current_ns-self.__binance_firstKlineOpenTSSearchQueue_lastUpdated_ns:
            for symbol, request in sReqs.items():
                if (request['waitUntil'] < t_current_s  and 
                    meis[symbol]['status'] == 'TRADING' and
                    symbol not in sQueues):
                    sQueues.add(symbol)
            self.__binance_firstKlineOpenTSSearchQueue_lastUpdated_ns = t_current_ns

        #[3]: FirstKlineOpenTS Search
        symbols_processed = []
        for symbol in sQueues:
            #[3-1]: Fetch Block Check
            if self.__binance_fetchBlock: break

            #[3-2]: Search Process Setup
            request = sReqs[symbol]
            ts_firstMonth  = None
            ts_firstDay    = None
            ts_firstHour   = None
            ts_firstMinute = None
            ts_target_beg = _BINANCE_FUTURESSTART_YEAR_TIMESTAMP
            ts_target_end = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1M, 
                                                                            timestamp  = ts_target_beg, 
                                                                            nTicks     = 96)-1
            
            #[3-3]: Find the first month (Check every 8 years (= 96 months, largest year multiple under 100), for the first monthly kline since the BINANCE FUTURES market open year)
            skipThisSymbol = False
            breakQueueLoop = False
            while ts_firstMonth is None:
                #[3-3-1]: Check API Rate Limit
                if not self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 1, extraOnly = True, apply = True):
                    breakQueueLoop = True
                    break
                #[3-3-2]: Try Klines Fetch
                try: fetchedKlines = self.__binance_client_default.futures_historical_klines(symbol        = symbol, 
                                                                                             interval      = binance.Client.KLINE_INTERVAL_1MONTH, 
                                                                                             start_str     = ts_target_beg*1000, 
                                                                                             end_str       = ts_target_end*1000, 
                                                                                             limit         = 99, 
                                                                                             verifyFirstTS = False)
                except Exception as e:
                    fetchedKlines = None
                    self.__logger(message = f"An unexpected error ocurred while attempting to fetch klines for a firstKlineOpenTSSearch for {symbol}\n Exception: {str(e)}", logType = 'Error', color = 'light_red')
                    breakQueueLoop            = True
                    self.__binance_fetchBlock = True
                    break
                #[3-3-3]: Check Fetch Result
                if fetchedKlines is None:
                    request['waitUntil'] = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, timestamp = t_current_s, nTicks = 1)
                    symbols_processed.append((symbol, False))
                    skipThisSymbol = True
                    break
                if fetchedKlines:
                    ts_firstMonth = int(fetchedKlines[0][0]/1000)
                    break
                else:
                    ts_target_beg = ts_target_end+1
                    ts_target_end = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1M, 
                                                                                    timestamp  = ts_target_beg, 
                                                                                    nTicks     = 96)-1
                    if t_current_s < ts_target_beg:
                        request['waitUntil'] = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, timestamp = t_current_s, nTicks = 1)
                        symbols_processed.append((symbol, False))
                        skipThisSymbol = True
                        break
            if breakQueueLoop:
                break
            if skipThisSymbol:
                continue

            #[3-4]: Find the first day within the first month
            #---[3-4-1]: Check API Rate Limit
            if not self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 1, extraOnly = True, apply = True):
                break
            #---[3-4-2]: Try Klines Fetch
            ts_target_beg = ts_firstMonth
            ts_target_end = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1M, 
                                                                            timestamp  = ts_target_beg, 
                                                                            nTicks     = 1)-1
            try: fetchedKlines = self.__binance_client_default.futures_historical_klines(symbol    = symbol, 
                                                                                         interval  = binance.Client.KLINE_INTERVAL_1DAY, 
                                                                                         start_str = ts_target_beg*1000, 
                                                                                         end_str   = ts_target_end*1000, 
                                                                                         limit     = 99, 
                                                                                         verifyFirstTS = False)
            except Exception as e:
                fetchedKlines = None
                self.__logger(message = f"An unexpected error ocurred while attempting to fetch klines for a firstKlineOpenTSSearch for {symbol}\n Exception: {str(e)}", logType = 'Error', color = 'light_red')
                self.__binance_fetchBlock = True
                break
            #---[3-4-3]: Check Fetch Result
            if fetchedKlines is None:
                request['waitUntil'] = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, timestamp = t_current_s, nTicks = 1)
                symbols_processed.append((symbol, False))
                continue
            if fetchedKlines:
                ts_firstDay = int(fetchedKlines[0][0]/1000)
            else:
                request['waitUntil'] = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, timestamp = t_current_s, nTicks = 1)
                symbols_processed.append((symbol, False))
                continue

            #[3-5]: Find the first hour within the first day
            #---[3-5-1]: Check API Rate Limit
            if not self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 1, extraOnly = True, apply = True):
                break
            #---[3-5-2]: Try Klines Fetch
            ts_target_beg = ts_firstDay
            ts_target_end = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1h, 
                                                                            timestamp  = ts_target_beg, 
                                                                            nTicks     = 24)-1
            try: fetchedKlines = self.__binance_client_default.futures_historical_klines(symbol    = symbol, 
                                                                                         interval  = binance.Client.KLINE_INTERVAL_1HOUR, 
                                                                                         start_str = ts_target_beg*1000, 
                                                                                         end_str   = ts_target_end*1000, 
                                                                                         limit     = 99, 
                                                                                         verifyFirstTS = False)
            except Exception as e:
                fetchedKlines = None
                self.__binance_fetchBlock = True
                self.__logger(message = f"An unexpected error ocurred while attempting to fetch klines for a firstKlineOpenTSSearch for {symbol}\n Exception: {str(e)}", logType = 'Error', color = 'light_red')
                break
            #---[3-5-3]: Check Fetch Result
            if fetchedKlines is None:
                request['waitUntil'] = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, timestamp = t_current_s, nTicks = 1)
                symbols_processed.append((symbol, False))
                continue
            if fetchedKlines:
                ts_firstHour = int(fetchedKlines[0][0]/1000)
            else:
                request['waitUntil'] = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, timestamp = t_current_s, nTicks = 1)
                symbols_processed.append((symbol, False))
                continue

            #[3-6]: Find the first minute within the first hour
            #---[3-6-1]: Check API Rate Limit
            if not self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 1, extraOnly = True, apply = True):
                break
            #---[3-6-2]: Try Klines Fetch
            ts_target_beg = ts_firstHour
            ts_target_end = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, 
                                                                            timestamp  = ts_target_beg, 
                                                                            nTicks     = 60)-1
            try: fetchedKlines = self.__binance_client_default.futures_historical_klines(symbol    = symbol, 
                                                                                         interval  = binance.Client.KLINE_INTERVAL_1MINUTE, 
                                                                                         start_str = ts_target_beg*1000, 
                                                                                         end_str   = ts_target_end*1000, 
                                                                                         limit     = 99, 
                                                                                         verifyFirstTS = False)
            except Exception as e:
                fetchedKlines = None
                self.__binance_fetchBlock = True
                self.__logger(message = f"An unexpected error ocurred while attempting to fetch klines for a firstKlineOpenTSSearch for {symbol}\n Exception: {str(e)}", logType = 'Error', color = 'light_red')
                break
            #---[3-6-3]: Check Fetch Result
            if fetchedKlines is None:
                request['waitUntil'] = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, timestamp = t_current_s, nTicks = 1)
                symbols_processed.append((symbol, False))
                continue
            if fetchedKlines:
                ts_firstMinute = int(fetchedKlines[0][0]/1000)
            else:
                request['waitUntil'] = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, timestamp = t_current_s, nTicks = 1)
                symbols_processed.append((symbol, False))
                continue

            #[3-7]: Finally
            symbols_processed.append((symbol, True))
            self.ipcA.sendFARR(request['requester'], {'symbol': symbol, 'firstKlineOpenTS': ts_firstMinute}, request['requestID'])
            self.__logger(message = f"The first kline openTS found for {symbol}: {ts_firstMinute}! ({len(self.__binance_firstKlineOpenTSSearchQueue)-len(symbols_processed)} remaining)", logType = 'Update', color = 'light_green')

        #[4]: Processed Symbols Handling
        for symbol, complete in symbols_processed:
            self.__binance_firstKlineOpenTSSearchQueue.remove(symbol)
            if complete: 
                del self.__binance_firstKlineOpenTSSearchRequests[symbol]

    #---Fetch Processing
    def __addFetchRequest(self, symbol, fetchType, requestParams = None):
        #[1]: Fetch Request Tracker Setup (If needed)
        if symbol not in self.__binance_fetchRequests:
            self.__binance_fetchRequests[symbol] = {'klineFetchRequest': None, 'orderBookFetchRequest': None}
        fetchRequest = self.__binance_fetchRequests[symbol]

        #[2]: Previous Fetch Control (If needed)
        if fetchType == 'KLINE' and fetchRequest['klineFetchRequest'] is not None:
            fr_prev = fetchRequest['klineFetchRequest']
            self.ipcA.sendFARR(targetProcess  = fr_prev['requester'], 
                               functionResult = {'status': 'terminate', 'klines': None}, 
                               requestID      = fr_prev['requestID'], 
                               complete       = True)

        #[3]: Request Generation
        #---[3-1]: KLINE
        if fetchType == 'KLINE':
            fetchRequest['klineFetchRequest'] = {'requester':                 requestParams['requester'],
                                                 'requestID':                 requestParams['requestID'],
                                                 'marketRegistrationTS':      requestParams['marketRegistrationTS'],
                                                 'fetchTargetRanges_initial': requestParams['fetchTargetRanges'].copy(),
                                                 'fetchTargetRanges':         requestParams['fetchTargetRanges'].copy(),
                                                 'fetchedRanges':             []
                                                 }
        #---[3-2]: DEPTH
        elif fetchType == 'DEPTH':
            fetchRequest['orderBookFetchRequest'] = True

        #[4]: Update Fetch Handler Priortization
        tsd_subs = self.__binance_TWM_StreamingData_Subscriptions
        fr_sbp   = self.__binance_fetchRequests_SymbolsByPriority
        if symbol in tsd_subs: fetchPriority = tsd_subs[symbol]['fetchPriority']
        else:                  fetchPriority = 2
        for fp, symbols in fr_sbp.items():
            if fp != fetchPriority and symbol in symbols: 
                symbols.remove(symbol)
        fr_sbp[fetchPriority].add(symbol)
    def __clearFetchRequests(self, symbols = None):
        #[1]: Target Symbols
        if symbols is None: 
            symbols = list(self.__binance_fetchRequests)

        #[2]: Fetch Requests Clearing
        for symbol in symbols:
            #[2-1]: Symbol Check
            if symbol not in self.__binance_fetchRequests:
                continue
            #[2-2]: Kline Fetch Request Termination Signaling
            kfr = self.__binance_fetchRequests[symbol]['klineFetchRequest']
            if kfr is not None: 
                self.ipcA.sendFARR(targetProcess  = kfr['requester'], 
                                   functionResult = {'status': 'terminate', 'klines': None}, 
                                   requestID      = kfr['requestID'], 
                                   complete       = True)
            #[2-3]: Symbol Fetch Request Removal
            del self.__binance_fetchRequests[symbol]
            #[2-4]: Fetch Prioritization Update
            for symbols_sbp in self.__binance_fetchRequests_SymbolsByPriority.values():
                if symbol not in symbols_sbp: 
                    continue
                symbols_sbp.remove(symbol)
                break
    def __processFetchRequests(self):
        #[1]: First Kline Open TS Search Queue Check (If not empty, do not fetch)
        if self.__binance_firstKlineOpenTSSearchQueue: 
            return

        #[2]: Target Selection
        fetchTarget = None
        for priority, symbols in self.__binance_fetchRequests_SymbolsByPriority.items():
            for symbol in symbols: 
                fetchTarget = (symbol, priority)
                break
            if fetchTarget is not None:
                break
        if fetchTarget is None:
            return

        #[3]: Target Process
        symbol, priority = fetchTarget
        if not self.__binance_fetchBlock: self.__processFetchRequests_Kline(symbol     = symbol)
        if not self.__binance_fetchBlock: self.__processFetchRequests_OrderBook(symbol = symbol)
        if (self.__binance_fetchRequests[symbol]['klineFetchRequest'] is None) and (self.__binance_fetchRequests[symbol]['orderBookFetchRequest'] is None): 
            del self.__binance_fetchRequests[symbol]
            self.__binance_fetchRequests_SymbolsByPriority[priority].remove(symbol)
    def __processFetchRequests_Kline(self, symbol):
        """
        fetchedKlines[n]           = ([0]: t_open, [1]: p_open, [2]: p_high, [3]: p_low, [4]: p_close, [5]: baseAssetVolume, [6]: t_close, [7]: quoteAssetVolume, [8]: nTrades, [9]: baseAssetVolume_takerBuy, [10]: quoteAssetVolume_takerBuy, [11]: ignore)
        fetchedKlines_formatted[n] = ([0]: openTS, [1]: closeTS, [2]: openPrice, [3]: highPrice, [4]: lowPrice, [5]: closePrice, [6]: nTrades, [7]: baseAssetVolume, [8]: quoteAssetVolume, [9]: baseAssetVolume_takerBuy, [10]: quoteAssetVolume_takerBuy, [11]: klineType)
        """
        #[1]: Fetch Request Check
        frs  = self.__binance_fetchRequests
        klfr = frs[symbol]['klineFetchRequest']
        if klfr is None: return

        #[2]: Effective Fetch Target Range
        ftr = klfr['fetchTargetRanges'][0]
        ftr_end_max = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, 
                                                                      timestamp  = ftr[0], 
                                                                      mrktReg    = klfr['marketRegistrationTS'], 
                                                                      nTicks     = 1000)-1
        ftr_eff = (ftr[0], min(ftr[1], ftr_end_max))

        #[3]: Check API Rate Limit and Fetch Klines If Possible
        #---[3-1]: Expected Number of Klines
        kots_expected = atmEta_Auxillaries.getTimestampList_byRange(intervalID        = KLINTERVAL, 
                                                                    mrktReg           = klfr['marketRegistrationTS'], 
                                                                    timestamp_beg     = ftr_eff[0], 
                                                                    timestamp_end     = ftr_eff[1], 
                                                                    lastTickInclusive = True)
        kots_expected_len = len(kots_expected)
        if   (  1 <= kots_expected_len) and (kots_expected_len <   100): req_weight =  1; fetchLimit = 99
        elif (100 <= kots_expected_len) and (kots_expected_len <   500): req_weight =  2; fetchLimit = 499
        elif (500 <= kots_expected_len) and (kots_expected_len <= 1000): req_weight =  5; fetchLimit = 1000
        else:                                                            req_weight = 10; fetchLimit = kots_expected_len
        #---[3-2]: API Rate Limit Check
        if not self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, 
                                        weight    = req_weight, 
                                        extraOnly = True, 
                                        apply     = True):
            self.__binance_fetchBlock = True
            return
        #---[3-3]: Fetch Attempt
        try: 
            fetchedKlines = self.__binance_client_default.futures_historical_klines(symbol        = symbol, 
                                                                                    interval      = KLINTERVAL_CLIENT, 
                                                                                    start_str     = ftr_eff[0]*1000, 
                                                                                    end_str       = ftr_eff[1]*1000, 
                                                                                    limit         = fetchLimit, 
                                                                                    verifyFirstTS = False)
        except Exception as e:
            self.__binance_fetchBlock = True
            self.__logger(message = f"An unexpected error ocurred while attempting to fetch klines\n Symbol: {symbol}\n queue: {str(klfr)}\n Exception: {str(e)}", 
                          logType = 'Warning', 
                          color   = 'light_red') 
            return

        #[3]: Format Klines 
        fetchedKlines_dict      = {int(kl[0]/1000): kl for kl in fetchedKlines}
        fetchedKlines_formatted = []
        func_gnitt = atmEta_Auxillaries.getNextIntervalTickTimestamp
        #---[3-1]: Expected Klines
        for ts in kots_expected:
            kl_raw = fetchedKlines_dict.get(ts, None)
            #[3-1-1]: Expected Not Fetched - Fill With Dummy Klines
            if kl_raw is None:
                kl_dummy = (ts, 
                            func_gnitt(intervalID = KLINTERVAL, 
                                       timestamp  = ts, 
                                       mrktReg    = klfr['marketRegistrationTS'], 
                                       nTicks     = 1)-1,
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            None,
                            _FORMATTEDKLINETYPE_DUMMY)
                fetchedKlines_formatted.append(kl_dummy)
                self.__logger(message = f"An expected kline was not fetched for {symbol}@{ts}. The corresponding position will be filled with a dummy kline, but an user attention is advised*", logType = 'Warning', color = 'light_magenta')
            #[3-1-2]: Expected Fetched - Reformat And Save
            else:
                (tOpen, 
                 pOpen,
                 pHigh,
                 pLow,
                 pClose,
                 vBase,
                 tClose,
                 vQuote,
                 nTrades,
                 vBaseTB,
                 vQuoteTB,
                 ignore
                 ) = kl_raw
                kl_formatted = (ts,
                                int(tClose/1000),
                                pOpen,
                                pHigh,
                                pLow,
                                pClose,
                                nTrades,
                                vBase,
                                vQuote,
                                vBaseTB,
                                vQuoteTB,
                                _FORMATTEDKLINETYPE_FETCHED)
                fetchedKlines_formatted.append(kl_formatted)
                del fetchedKlines_dict[ts]
        #---[3-2]: Unexpected Klines
        if fetchedKlines_dict:
            for ts_unexpected, kl_unexpected in fetchedKlines_dict.items():
                self.__logger(message = f"Unexpected kline detected: {symbol}@{ts_unexpected}. It will be Disposed. \n * {kl_unexpected}", 
                              logType = 'Warning', 
                              color   = 'red')

        #[4]: Update the Fetch Ranges
        #---[4-1]: Fetch Target Ranges
        if (ftr[0] == ftr_eff[0]) and (ftr[1] == ftr_eff[1]): klfr['fetchTargetRanges'].pop(0)
        else:                                                 klfr['fetchTargetRanges'][0] = (ftr_eff[1]+1, klfr['fetchTargetRanges'][0][1])
        #---[4-2]: Fetched Ranges
        klfr['fetchedRanges'].append(ftr_eff)
        klfr['fetchedRanges'].sort(key = lambda x: x[0])
        frs_merged = [klfr['fetchedRanges'][0],]
        for dr in klfr['fetchedRanges'][1:]:
            if frs_merged[-1][1]+1 == dr[0]: frs_merged[-1] = (frs_merged[-1][0], dr[1])
            else:                            frs_merged.append(dr)
        klfr['fetchedRanges'] = frs_merged

        #[5]: Send fetch result
        if klfr['fetchTargetRanges']:
            self.ipcA.sendFARR(targetProcess  = klfr['requester'], 
                               functionResult = {'status': 'fetching', 'klines': fetchedKlines_formatted}, 
                               requestID      = klfr['requestID'], 
                               complete       = False)
            totalTSLength   = sum((_tfr[1]-_tfr[0]+1) for _tfr in klfr['fetchTargetRanges_initial'])
            fetchedTSLength = sum((_fr[1] -_fr[0] +1) for _fr  in klfr['fetchedRanges'])
            completion      = round(fetchedTSLength/totalTSLength*100, 3)
            nRemainingKLFRs = sum(1 for _fr in frs.values() if _fr['klineFetchRequest'] is not None)
            self.__logger(message = f"Successfully processed a kline fetch request for {symbol} from {klfr['requester']} [{completion:.3f} % Complete] [{nRemainingKLFRs} Symbols Remaining]", 
                          logType = 'Update', 
                          color   = 'light_green')
        else:
            frs[symbol]['klineFetchRequest'] = None
            self.ipcA.sendFARR(targetProcess  = klfr['requester'], 
                               functionResult = {'status': 'complete', 'klines': fetchedKlines_formatted}, 
                               requestID      = klfr['requestID'], 
                               complete       = True)
            nRemainingKLFRs = sum(1 for _fr in frs.values() if _fr['klineFetchRequest'] is not None)
            self.__logger(message = f"Successfully completed a kline fetch request for {symbol} from {klfr['requester']} [{nRemainingKLFRs} Symbols Remaining]", 
                          logType = 'Update', 
                          color   = 'light_green')
    def __processFetchRequests_OrderBook(self, symbol):
        #[1]: Fetch Request Check
        frs  = self.__binance_fetchRequests
        obfr = frs[symbol]['orderBookFetchRequest']
        if obfr is None: return

        #[2]: API Rate Limit Check
        if not self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 20, extraOnly = True, apply = True, printUpdated = True):
            return
        
        #[3]: Fetch Attempt
        try: 
            ob_fetched = self.__binance_client_default.futures_order_book(symbol = symbol, limit = 1000)
        except Exception as e:
            self.__binance_fetchBlock = True
            self.__logger(message = f"An unexpected error ocurred while attempting to fetch order blocks for {symbol}\n Exception: {str(e)}", logType = 'Warning', color = 'light_red')
            return
        
        #[4]: Fetch Result Interpretation
        #---[4-1]: Interpretation Preparation
        sd_depth      = self.__binance_TWM_StreamingData[symbol]['depth']
        complete      = None
        lastUID       = None
        lastUID_fetch = None
        #---[4-2]: Fetched Orderblock Read
        ob_bids = {float(pl): float(val) for pl, val in ob_fetched['bids']}
        ob_asks = {float(pl): float(val) for pl, val in ob_fetched['asks']}
        #---[4-3]: Buffer Read
        if sd_depth['buffer']:
            #[4-3-1]: Buffer Contents Filtering & Continuation Check
            buffer_after = [update for update in sd_depth['buffer'] if (ob_fetched['lastUpdateId'] <= update['u'])]
            buffer_after_uidCheck = True
            if (0 < len(buffer_after)):
                buffer_after_lastFinalUpdateID = buffer_after[0]['u']
                for buffer in buffer_after[1:]:
                    if (buffer['pu'] == buffer_after_lastFinalUpdateID): buffer_after_lastFinalUpdateID = buffer['u']
                    else: buffer_after_uidCheck = False; break
                if (buffer_after_uidCheck == True): buffer_after_uidCheck = (buffer_after[0]['U'] <= ob_fetched['lastUpdateId']) and (ob_fetched['lastUpdateId'] <= buffer_after[0]['u'])
            #[4-3-2]: Buffer Contents Read
            if (len(buffer_after) == 0): 
                complete      = True
                lastUID_fetch = ob_fetched['lastUpdateId']
            elif (buffer_after_uidCheck == True): 
                for _update in buffer_after:
                    for bidUpdate in _update['b']: 
                        pl = float(bidUpdate[0])
                        qt = float(bidUpdate[1])
                        ob_bids[pl] = qt
                        if   (qt == 0):       del ob_bids[pl]
                        elif (pl in ob_asks): del ob_asks[pl]
                    for askUpdate in _update['a']: 
                        pl = float(askUpdate[0])
                        qt = float(askUpdate[1])
                        ob_asks[pl] = qt
                        if   (qt == 0):       del ob_asks[pl]
                        elif (pl in ob_bids): del ob_bids[pl]
                lastUID  = buffer_after[-1]['u']
                complete = True
        else:
            buffer_after  = []
            complete      = True
            lastUID_fetch = ob_fetched['lastUpdateId']

        #[5]: Finally
        sd_depth['buffer'] = buffer_after
        if complete:
            sd_depth['fetchRequested'] = False
            sd_depth['bids']           = ob_bids
            sd_depth['asks']           = ob_asks
            sd_depth['lastUID']        = lastUID
            sd_depth['lastUID_Fetch']  = lastUID_fetch
            #Fetch Result Clearing
            frs[symbol]['orderBookFetchRequest'] = None
            #Console Message
            self.__logger(message = f"Successfully completed the order book profile for {symbol}", logType = 'Update', color = 'light_green')

    #---Accounts
    def __computeMaximumNumberOfAccountsActivation(self):
        maxActivationN_min = float('inf')
        for rateLimit in self.__binance_MarketExchangeInfo_RateLimits['REQUEST_WEIGHT']:
            maxActivationN = int((rateLimit['limit']/self.config_BinanceAPI['rateLimitIPSharingNumber']*0.5*_BINANCE_ACCOUNTDATAREADINTERVAL_MAX_NS/1e9)/(5*rateLimit['interval_sec']))
            maxActivationN_min = min(maxActivationN, maxActivationN_min)
        self.__binance_activatedAccounts_maxActivation = maxActivationN_min
    def __computeActivatedAccountsDataReadInterval(self):
        readInterval_s_max = 0
        for rateLimit in self.__binance_MarketExchangeInfo_RateLimits['REQUEST_WEIGHT']:
            readInterval_sec = (5*len(self.__binance_activatedAccounts_LocalIDs)*rateLimit['interval_sec'])/(rateLimit['limit']*self.config_BinanceAPI['rateLimitIPSharingNumber']*0.5)*1.1
            readInterval_s_max = max(readInterval_s_max, readInterval_sec)
        self.__binance_activatedAccounts_readInterval_ns = max(readInterval_s_max*1e9, _BINANCE_ACCOUNTDATAREADINTERVAL_MIN_NS)
    def __readActivatedAccountsData(self):
        #[1]: Status
        t_current_ns       = time.perf_counter_ns()
        nActivatedAccounts = len(self.__binance_activatedAccounts_LocalIDs)
        if nActivatedAccounts == 0:
            return
        if not ((self.__binance_activatedAccounts_readInterval_ns <= t_current_ns-self.__binance_activatedAccounts_lastDataRead_ns) or (self.__binance_activatedAccounts_dataReadRequest)):
            return
        
        #[2]: API Rate Limit Test
        if not self.__checkAPIRateLimit(limitType    = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, 
                                        weight       = nActivatedAccounts*5, 
                                        extraOnly    = False,
                                        apply        = True, 
                                        printUpdated = False):
            return
        
        #[3]: Account Data Read
        for localID in self.__binance_activatedAccounts_LocalIDs:
            account = self.__binance_client_users[localID]
            try:                   
                accountData = account['accountInstance'].futures_account()
                errorMsg = None
            except Exception as e:
                accountData = None
                errorMsg = str(e)

            if accountData is None:
                account['nConsecutiveDataReadFails'] += 1
                if (_BINANCE_ACCOUNTDATAREADTOLERATEDCONSECUTIVEFAILS < account['nConsecutiveDataReadFails']):
                    self.__logger(message = f"Account Data Read For {localID} Failed More Than {_BINANCE_ACCOUNTDATAREADTOLERATEDCONSECUTIVEFAILS} Times Consecutively.\n * {errorMsg}", logType = 'Warning', color = 'light_red')
            else:
                account['nConsecutiveDataReadFails'] = 0
                self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'onAccountDataReceival', functionParams = {'localID': localID, 'accountData': accountData}, farrHandler = None)

        #[4]: Trackers Update
        self.__binance_activatedAccounts_lastDataRead_ns = t_current_ns
        self.__binance_activatedAccounts_dataReadRequest = False
    def __checkCreatedOrdersCompletion(self):
        #[1]: Check Setup
        completedOrders = []

        #[2]: Check Loop
        for coID, createdOrder in self.__binance_createdOrders.items():
            #[2-1]: Last Check Time
            t_current_ns = time.perf_counter_ns()
            if not (_BINANCE_CREATEDORDERCHECKINTERVAL_NS <= t_current_ns-createdOrder['lastCheckTime']): 
                continue

            #[2-2]: API Rate Limit Update
            if not self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, 
                                            weight    = 1, 
                                            extraOnly = False, 
                                            apply     = True):
                continue

            #[2-3]: Last Check Time Update
            createdOrder['lastCheckTime'] = t_current_ns

            #[2-4]: Order Check
            order_fromServer           = None
            apiError_orderDoesNotExist = False
            #---[2-4-1]: Order Status Read Attempt
            try: 
                order_fromServer = self.__binance_client_users[createdOrder['localID']]['accountInstance'].futures_get_order(symbol            = createdOrder['positionSymbol'], 
                                                                                                                             origclientorderid = coID)
            except Exception as e:
                if (str(e) == 'APIError(code=-2013): Order does not exist.'): 
                    apiError_orderDoesNotExist = True
                else: 
                    self.__logger(message = f"An unexpected error ocrrued while attempting to check created order status for {createdOrder['localID']}-{createdOrder['positionSymbol']}. \n * {str(e)}", 
                                  logType = 'Error', 
                                  color   = 'light_red')
            
            #---[2-4-2]: Read Result Interpretation
            #------[2-4-2-1]: Result Received
            if order_fromServer is not None:
                if not _BINANCE_ORDERSTATUS[order_fromServer['status']]['complete']:
                    continue
                self.ipcA.sendFARR(targetProcess  = 'TRADEMANAGER', 
                                   functionResult = {'localID':        createdOrder['localID'], 
                                                     'positionSymbol': createdOrder['positionSymbol'], 
                                                     'responseOn':     'CREATEORDER', 
                                                     'result':         _BINANCE_ORDERSTATUS[order_fromServer['status']]['result'],
                                                     'orderResult':    {'type':             order_fromServer['type'],
                                                                        'side':             order_fromServer['side'],
                                                                        'averagePrice':     float(order_fromServer['avgPrice']),
                                                                        'originalQuantity': float(order_fromServer['origQty']),
                                                                        'executedQuantity': float(order_fromServer['executedQty'])},
                                                     'failType':       None,
                                                     'errorMessage':   None}, 
                                   requestID = createdOrder['IPCRID'], 
                                   complete  = True)
                completedOrders.append(coID)
            #------[2-4-2-2]: Order Not Found
            elif apiError_orderDoesNotExist:
                createdOrder['nCheckFails'] += 1
                if createdOrder['nCheckFails'] < _BINANCE_CREATEDORDERCANCELLATIONTHRESHOLD:
                    continue
                self.ipcA.sendFARR(targetProcess  = 'TRADEMANAGER', 
                                   functionResult = {'localID':        createdOrder['localID'], 
                                                     'positionSymbol': createdOrder['positionSymbol'], 
                                                     'responseOn':     'CREATEORDER', 
                                                     'result':         False,
                                                     'orderResult':    None,
                                                     'failType':       'CANCELLATIONTHRESHOLDREACHED',
                                                     'errorMessage':   None}, 
                                   requestID = createdOrder['IPCRID'], 
                                   complete  = True)
                self.__logger(message = f"A created order for {createdOrder['localID']}-{createdOrder['positionSymbol']} check loop terminated due to the cancellation threshold reach.", 
                              logType = 'Warning', 
                              color   = 'light_magenta')
                completedOrders.append(coID)
            #------[2-4-2-3]: Unexpectancy
            else:
                self.ipcA.sendFARR(targetProcess  = 'TRADEMANAGER', 
                                   functionResult = {'localID':        createdOrder['localID'], 
                                                     'positionSymbol': createdOrder['positionSymbol'], 
                                                     'responseOn':     'CREATEORDER', 
                                                     'result':         False,
                                                     'orderResult':    None,
                                                     'failType':       'UNEXPECTEDERROR',
                                                     'errorMessage':   None}, 
                                   requestID = createdOrder['IPCRID'], 
                                   complete  = True)
                self.__logger(message = f"A created order for {createdOrder['localID']}-{createdOrder['positionSymbol']} check loop terminated due to an unexpected error.", 
                              logType = 'Warning', 
                              color   = 'light_magenta')
                completedOrders.append(coID)
                
        #[3]: Completed Orders Clearing
        for coID in completedOrders: 
            del self.__binance_createdOrders[coID]

    #---System
    def __logger(self, message, logType, color):
        if not self.config_BinanceAPI[f'print_{logType}']: return
        time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
        print(termcolor.colored(f"[BINANCEAPI-{time_str}] {message}", color))
    #Manager Internal Functions END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Server Response Handlers -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __TWM_getStreamReceiverFunction(self, connection):
        def receiver(streamContents):
            if (connection['expired'] == False):
                connection['buffer_writing'] = True
                connection['buffer'].append(streamContents)
                connection['buffer_writing'] = False
        return receiver
    """
    streamContents = {'stream': 'dogeusdt_perpetual@continuousKline_6h', 
                        'data': {'e': 'continuous_kline', 
                                'E': 1710435281932, 
                                'ps': 'DOGEUSDT', 
                                'ct': 'PERPETUAL', 
                                'k': {'t': 1710417600000,       (= open time)
                                        'T': 1710439199999,       (= close time)
                                        'i': '6h',                (= interval)
                                        'f': 4178342826779,       (= first trade ID)
                                        'L': 4180732271887,       (= last trade ID)
                                        'o': '0.183200',          (= open price)
                                        'c': '0.177400',          (= close price)
                                        'h': '0.189640',          (= high price)
                                        'l': '0.169680',          (= low price)
                                        'v': '6756780082',        (= base asset volume)
                                        'n': 2277398,             (= number of trades)
                                        'x': False,               (= is this kline closed?)
                                        'q': '1211112589.376870', (= quote asset volume)
                                        'V': '3192382498',        (= taker buy base asset volume)
                                        'Q': '572467775.510730',  (= takey buy quote asset volume)
                                        'B': '0'}}}               (= ignore)
    """ #Expand to check a kline stream data example
    """
    streamContents = {'stream': 'dogeusdt@depth', 
                      'data': {"e": "depthUpdate",              // Event type
                               "E": 123456789,                  // Event time
                               "T": 123456788,                  // Transaction time 
                               "s": "BTCUSDT",                  // Symbol
                               "U": 157,                        // First update ID in event
                               "u": 160,                        // Final update ID in event
                               "pu": 149,                       // Final update ID in last stream(ie `u` in last stream)
                               "b": [["0.0024", "10"],  [...]], // Bids to be updated (List of (<Price Level to be updated>, <Quantity>))
                               "a": [["0.0026", "100"], [...]]} // Asks to be updated (List of (<Price Level to be updated>, <Quantity>))
                              }
    """ #Expand to check an orderbook stream data example
    """
    streamContents = {'stream': 'aaveusdt@aggTrade', 
                        'data': {'e': 'aggTrade',    // Event type
                                'E': 1747892844834, // Event time
                                'a': 294734871,     // Aggregate trade ID
                                's': 'AAVEUSDT',    // Symbol
                                'p': '253.430',     // Price
                                'q': '0.1',         // Quantity
                                'f': 659401458,     // First trade ID
                                'l': 659401458,     // Last trade ID
                                'T': 1747892844679, // Trade time
                                'm': False}         // Is the buyer the market maker?
    """ #Expand to check an aggTrade stream data example
    def __processTWMStreamMessages(self):
        #[1]: Messages Interpretation
        _nHandledMessages = 0
        while (_nHandledMessages < 1000):
            _nHandledMessages_onConnLoopBeg = _nHandledMessages
            for _connection in self.__binance_TWM_Connections.values():
                if (_connection['expired'] == True):
                    while (0 < len(_connection['buffer'])): self.__processTWMStreamMessages_InterpretMessage(streamMessage = _connection['buffer'].pop(0)); _nHandledMessages += 1
                elif (_nHandledMessages < 1000):
                    if (0 < len(_connection['buffer'])): self.__processTWMStreamMessages_InterpretMessage(streamMessage = _connection['buffer'].pop(0)); _nHandledMessages += 1
            if (_nHandledMessages == _nHandledMessages_onConnLoopBeg): break
        #[2]: Announcements
        _t_current_ns = time.perf_counter_ns()
        for _symbol in self.__binance_TWM_StreamingData:
            _streamingData = self.__binance_TWM_StreamingData[_symbol]
            if ((0 < _streamingData['updatedTypes']) and (100e6 <= _t_current_ns-_streamingData['lastAnnounced_ns'])):
                _updatedTypes                = _streamingData['updatedTypes']
                _streamingData_subscriptions = self.__binance_TWM_StreamingData_Subscriptions[_symbol]
                _connection                  = self.__binance_TWM_Connections[_streamingData['connectionID']]
                #[2-1]: Kline Response
                if (0 < (_updatedTypes & _BINANCE_TWM_STREAMDATATYPE_FLAGS[_BINANCE_TWM_STREAMDATATYPE_KLINE])):
                    #Subscription Response
                    _openTSs_sorted = list(_streamingData['klines'].keys()); _openTSs_sorted.sort()
                    for _openTS in _openTSs_sorted:
                        _kline        = _streamingData['klines'][_openTS]['kline']
                        _kline_closed = _streamingData['klines'][_openTS]['closed']
                        for _subscription in _streamingData_subscriptions['subscriptions']:
                            _fID_kline = _subscription['fID_kline']
                            if (_fID_kline is not None):
                                self.ipcA.sendFAR(targetProcess  = _subscription['subscriber'], 
                                                  functionID     = _fID_kline, 
                                                  functionParams = {'symbol':               _symbol, 
                                                                    'streamConnectionTime': _connection['connectionTime'],
                                                                    'kline':                _kline, 
                                                                    'closed':               _kline_closed}, 
                                                  farrHandler = None)
                    _streamingData['klines'].clear()
                #[2-2]: Depth Update Response
                if (0 < (_updatedTypes & _BINANCE_TWM_STREAMDATATYPE_FLAGS[_BINANCE_TWM_STREAMDATATYPE_DEPTHUPDATE])):
                    #Subscription Response
                    _streamingData_depth = _streamingData['depth']
                    if (_streamingData_depth['fetchRequested'] == False):
                        for _subscription in _streamingData_subscriptions['subscriptions']:
                            _fID_depth = _subscription['fID_depth']
                            if (_fID_depth is not None):
                                self.ipcA.sendFAR(targetProcess  = _subscription['subscriber'], 
                                                  functionID     = _fID_depth, 
                                                  functionParams = {'symbol':               _symbol,
                                                                    'streamConnectionTime': self.__binance_TWM_Connections[self.__binance_TWM_StreamingData[_symbol]['connectionID']]['connectionTime'],
                                                                    'bids':                 _streamingData_depth['bids'].copy(),
                                                                    'asks':                 _streamingData_depth['asks'].copy()}, 
                                                  farrHandler = None)
                #[2-3]: AggTrades Response
                if (0 < (_updatedTypes & _BINANCE_TWM_STREAMDATATYPE_FLAGS[_BINANCE_TWM_STREAMDATATYPE_AGGTRADES])):
                    #Subscription Response
                    for _aggTrade_formatted in _streamingData['aggTrades']['buffer']:
                        for _subscription in _streamingData_subscriptions['subscriptions']:
                            _fID_aggTrades = _subscription['fID_aggTrades']
                            if (_fID_aggTrades is not None):
                                self.ipcA.sendFAR(targetProcess  = _subscription['subscriber'], 
                                                  functionID     = _fID_aggTrades, 
                                                  functionParams = {'symbol':               _symbol, 
                                                                    'streamConnectionTime': _connection['connectionTime'], 
                                                                    'aggTrade':             _aggTrade_formatted}, 
                                                  farrHandler = None)
                    _streamingData['aggTrades']['buffer'].clear()
                #[2-4]: Announcement Control
                _streamingData['updatedTypes']     = 0b000
                _streamingData['lastAnnounced_ns'] = _t_current_ns
    def __processTWMStreamMessages_InterpretMessage(self, streamMessage):
        #[1-1]: Expected stream content
        if ('data' in streamMessage):
            _streamData     = streamMessage['data']
            _streamDataType = _streamData['e']
            if (_streamDataType in self.__binance_TWM_StreamHandlers):
                _symbol = self.__binance_TWM_StreamHandlers[_streamDataType](streamData = _streamData)
                if (_symbol is not None): self.__binance_TWM_StreamingData[_symbol]['updatedTypes'] |= _BINANCE_TWM_STREAMDATATYPE_FLAGS[_streamDataType]
            else: self.__logger(message = f"Unexpected Stream Message Detected from Stream '{streamMessage['stream']}'\n * {str(streamMessage)}", logType = 'Warning', color = 'light_red')
        #[1-2]: Unexpected stream content. Stream may return 'Queue overflow. Message not filled' error, not anymore sending any stream data. In this case, restart all of the existing connections
        elif (streamMessage['e'] == 'error'):
            if (streamMessage['m'] == f'Message queue size {self.__binance_TWM._max_queue_size} exceeded maximum {self.__binance_TWM._max_queue_size}'):
                if (self.__binance_TWM_OverFlowDetected == False): self.__binance_TWM_OverFlowDetected = True
            else: self.__logger(message = f"An unexpected error received from the TWM, the connection symbols will be regenerated.\n * '{streamMessage['m']}'", logType = 'Warning', color = 'light_red')
        #[1-3]: Unexpected stream content, unregistered case
        else: self.__logger(message = f"Unexpected content received from WebSocket streams, user attention advised!\n * streamContents: {str(streamMessage)}", logType = 'Warning', color = 'light_red')
    def __processTWMStreamMessages_Kline(self, streamData):
        _symbol        = streamData['ps']
        _streamingData = self.__binance_TWM_StreamingData[_symbol]
        #Data Formatting
        _kline = streamData['k']
        _kline_openTS = int(_kline['t']/1000)
        _kline_closed = _kline['x']
        _kline_formatted = (_kline_openTS,         #Kline OpenTS
                            int(_kline['T']/1000), #Kline CloseTS
                            float(_kline['o']),    #Open  Price
                            float(_kline['h']),    #High  Price
                            float(_kline['l']),    #Low   Price
                            float(_kline['c']),    #Close Price
                            int(_kline['n']),      #nTrades
                            float(_kline['v']),    #Base  Asset Volume
                            float(_kline['q']),    #Quote Asset Volume
                            float(_kline['V']),    #Base  Asset Volume - Taker Buy
                            float(_kline['Q']),    #Quote Asset Volume - Taker Buy
                            _FORMATTEDKLINETYPE_STREAMED)
        #Data Save
        if (_streamingData['firstReceivedKlineOpenTS'] is None): _streamingData['firstReceivedKlineOpenTS']      = _kline_openTS
        if (_kline_closed == True):                              _streamingData['lastReceivedClosedKlineOpenTS'] = _kline_openTS
        _streamingData['klines'][_kline_openTS] = {'kline': _kline_formatted, 'closed': _kline_closed}
        #Finally
        return _symbol
    def __processTWMStreamMessages_DepthUpdate(self, streamData):
        _symbol = streamData['s']
        _streamingData       = self.__binance_TWM_StreamingData[_symbol]
        _streamingData_depth = _streamingData['depth']
        if (_streamingData_depth['fetchRequested'] == True): _streamingData_depth['buffer'].append(streamData); return None
        else:
            if (_streamingData_depth['lastUID_Fetch'] is None): 
                _uidCheck = (streamData['pu'] == _streamingData_depth['lastUID'])
                _ignore   = False
            else:                                               
                _uidCheck = (streamData['U'] <= _streamingData_depth['lastUID_Fetch']) and (_streamingData_depth['lastUID_Fetch'] <= streamData['u'])
                _ignore   = (streamData['u'] < _streamingData_depth['lastUID_Fetch'])
            if (_ignore == True): return None
            else:
                if (_uidCheck == True):
                    _streamingData_depth_bids = _streamingData_depth['bids']
                    _streamingData_depth_asks = _streamingData_depth['asks']
                    #Bids and Asks Update
                    for _bidUpdate in streamData['b']:
                        _pl = float(_bidUpdate[0])
                        _qt = float(_bidUpdate[1])
                        _streamingData_depth_bids[_pl] = _qt
                        if   (_qt == 0):                         del _streamingData_depth_bids[_pl]
                        elif (_pl in _streamingData_depth_asks): del _streamingData_depth_asks[_pl]
                    for _askUpdate in streamData['a']:
                        _pl = float(_askUpdate[0])
                        _qt = float(_askUpdate[1])
                        _streamingData_depth_asks[_pl] = _qt
                        if   (_qt == 0):                         del _streamingData_depth_asks[_pl]
                        elif (_pl in _streamingData_depth_bids): del _streamingData_depth_bids[_pl]
                    #Acceptance Range Filtering
                    _lastTradePrice = _streamingData['aggTrades']['lastTradePrice']
                    if (_lastTradePrice is None): _obAcceptanceRange = (0, float('inf'))
                    else:                         _obAcceptanceRange = (_lastTradePrice*(1-ORDERBOOKACCEPTANCERANGE/2), _lastTradePrice*(1+ORDERBOOKACCEPTANCERANGE/2))
                    for _pl in [_pl for _pl in _streamingData_depth_bids if not((_obAcceptanceRange[0] <= _pl) and (_pl <= _obAcceptanceRange[1]))]: del _streamingData_depth_bids[_pl]
                    for _pl in [_pl for _pl in _streamingData_depth_asks if not((_obAcceptanceRange[0] <= _pl) and (_pl <= _obAcceptanceRange[1]))]: del _streamingData_depth_asks[_pl]
                    #Last UID Update
                    _streamingData_depth['lastUID']       = streamData['u']
                    _streamingData_depth['lastUID_Fetch'] = None
                    #Symbol Return
                    return _symbol
                elif (self.__binance_TWM_Connections[self.__binance_TWM_StreamingData[_symbol]['connectionID']]['expired'] == False):
                    _streamingData_depth['buffer'].append(streamData)
                    _streamingData_depth['fetchRequested'] = True
                    self.__addFetchRequest(symbol = _symbol, fetchType = 'DEPTH')
                    return None
    def __processTWMStreamMessages_AggTrade(self, streamData):
        _symbol = streamData['s']
        _streamingData = self.__binance_TWM_StreamingData[_symbol]
        #Data Formatting
        _tradePrice = float(streamData['p'])
        _aggTrade_formatted = (int(streamData['T']/1000), #Trade Time
                               _tradePrice,                #Trade Price
                               float(streamData['q']),     #Quantity
                               streamData['m'])            #Is the buyer the market maker?
        #Data Append To Buffer
        _streamingData['aggTrades']['buffer'].append(_aggTrade_formatted)
        _streamingData['aggTrades']['lastTradePrice'] = _tradePrice
        #Finally
        return _symbol
    #Server Response Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #FAR Handlers -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<GUI>
    def __far_updateConfiguration(self, requester, requestID, newConfiguration):
        #[1]: Source Check
        if requester != 'GUI': return

        #[2]: Configuration Update
        #---[2-1]: Rate Limit IP Sharing Number
        if (type(newConfiguration['rateLimitIPSharingNumber']) == int) and (1 <= newConfiguration['rateLimitIPSharingNumber']) and (newConfiguration['rateLimitIPSharingNumber'] <= 5): 
            self.config_BinanceAPI['rateLimitIPSharingNumber'] = newConfiguration['rateLimitIPSharingNumber']
        #---[2-2]: Print Update
        self.config_BinanceAPI['print_Update'] = newConfiguration['print_Update']
        #---[2-3]: Print Warning
        self.config_BinanceAPI['print_Warning'] = newConfiguration['print_Warning']
        #---[2-4]: Print Error
        self.config_BinanceAPI['print_Error'] = newConfiguration['print_Error']

        #[3]: Save Configuration & Update Announcement
        self.__saveBinanceAPIConfig()
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CONFIGURATION', prdContent = self.config_BinanceAPI)

        #[4]: Return Result
        return {'result': True, 'message': "Configuration Successfully Updated!", 'configuration': self.config_BinanceAPI}
    #<DATAMANAGER>
    def __far_addFirstKlineOpenTSSearchRequest(self, requester, requestID, symbol):
        #[1]: Symbol Existence Check
        if symbol not in self.__binance_MarketExchangeInfo_Symbols:
            return
        #[2]: Request Update
        request = {'symbol':    symbol, 
                   'requester': requester, 
                   'requestID': requestID,
                   'waitUntil': 0}
        self.__binance_firstKlineOpenTSSearchRequests[symbol] = request
    def __far_addKlineFetchRequestQueue(self, requester, requestID, symbol, marketRegistrationTimestamp, streamConnectionTime, fetchTargetRanges):
        #[1]: Symbol Check
        if symbol not in self.__binance_TWM_StreamingData:
            self.ipcA.sendFARR(targetProcess = requester, functionResult = {'status': 'terminate', 'klines': None}, requestID = requestID, complete = True)
            return
        
        #[2]: Connection Check
        sdDesc                       = self.__binance_TWM_StreamingData[symbol]
        connection                   = self.__binance_TWM_Connections.get(sdDesc['connectionID'], None)
        streamConnectionTime_current = None
        if connection is not None and not connection['expired']:
            streamConnectionTime_current = connection['connectionTime']
        if streamConnectionTime_current != streamConnectionTime:
            self.ipcA.sendFARR(targetProcess = requester, functionResult = {'status': 'terminate', 'klines': None}, requestID = requestID, complete = True)
            return

        #[3]: Request Generation
        requestParams = {'requester':            requester,
                         'requestID':            requestID,
                         'marketRegistrationTS': marketRegistrationTimestamp,
                         'fetchTargetRanges':    fetchTargetRanges}
        self.__addFetchRequest(symbol = symbol, fetchType = 'KLINE', requestParams = requestParams)

    #<TRADEMANAGER>
    def __far_generateAccountInstance(self, requester, requestID, localID, uid, apiKey, secretKey):
        #[1]: Source Check
        if requester != 'TRADEMANAGER':
            return {'result': False, 'failType': 'INVALIDREQUESTER'}
        
        #[2]: Server Check
        if not self.__connection_serverAvailable:
            return {'result': False, 'failType': 'SERVERUNAVAILABLE'}
        
        #[3]: Activation Number Check
        if not (len(self.__binance_activatedAccounts_LocalIDs) < self.__binance_activatedAccounts_maxActivation):
            return {'result': False, 'failType': 'MAXACTIVATIONREACHED'}
        
        #[4]: Client Generation
        try:
            newAccount = binance.Client(api_key = apiKey, api_secret = secretKey)
            newAccount_uid            = newAccount.get_account()['uid']
            newAccount_enableFutures = newAccount.get_account_api_permissions()['enableFutures']
        except Exception as e: 
            return {'result': False, 'failType': 'UNEXPECTEDERROR', 'errorMessage': str(e)}
        
        #[5]: UID Check
        if newAccount_uid != uid:
            return {'result': False, 'failType': 'UIDMISMATCH'}
        
        #[6]: Future Enabled Check
        if not newAccount_enableFutures:
            return {'result': False, 'failType': 'FUTURESDISABLED'}
        
        #[7]: Finally
        self.__binance_client_users[localID] = {'accountInstance':           newAccount,
                                                'nConsecutiveDataReadFails': 0}
        #---[7-1]: Local ID, Data Read Request
        self.__binance_activatedAccounts_LocalIDs.add(localID)
        self.__binance_activatedAccounts_dataReadRequest = True
        #---[7-2]: Read Interval
        self.__computeActivatedAccountsDataReadInterval()
        #---[7-3]: Result Return
        return {'result': True}
    def __far_removeAccountInstance(self, requester, localID):
        #[1]: Source Check
        if requester != 'TRADEMANAGER': 
            return

        #[2]: ID Check
        if localID not in self.__binance_client_users:
            return
        
        #[3]: Removal
        #---[3-1]: Account Removal
        del self.__binance_client_users[localID]
        self.__binance_activatedAccounts_LocalIDs.remove(localID)
        #---[3-2]: Account Data Read Interval Update
        self.__computeActivatedAccountsDataReadInterval()
    def __far_setPositionMarginType(self, requester, requestID, localID, positionSymbol, newMarginType):
        #[1]: Source Check
        if requester != 'TRADEMANAGER':
            return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'MARGINTYPEUPDATE', 'result': False, 'failType': 'INVALIDREQUESTER'}

        #[2]: Server Availability Check
        if not self.__connection_serverAvailable:
            return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'MARGINTYPEUPDATE', 'result': False, 'failType': 'SERVERUNAVAILABLE'}

        #[3]: Account Check
        if localID not in self.__binance_client_users:
            return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'MARGINTYPEUPDATE', 'result': False, 'failType': 'LOCALIDNOTFOUND'}

        #[4]: Account Activation Check
        if localID not in self.__binance_activatedAccounts_LocalIDs:
            return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'MARGINTYPEUPDATE', 'result': False, 'failType': 'ACCOUNTNOTACTIVATED'}

        #[5]: Margin Type Check
        if newMarginType not in ('ISOLATED', 'CROSSED'):
            return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'MARGINTYPEUPDATE', 'result': False, 'failType': 'MARGINTYPEERROR'}

        #[6]: Update Attempt
        try:
            apiResult = self.__binance_client_users[localID]['accountInstance'].futures_change_margin_type(symbol = positionSymbol, marginType = newMarginType)
        except Exception as e: 
            return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'MARGINTYPEUPDATE', 'result': False, 'failType': 'APIERROR', 'errorMessage': str(e)}

        #[7]: Result Return
        return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'MARGINTYPEUPDATE', 'result': True,  'apiResult': apiResult}
    def __far_setPositionLeverage(self, requester, requestID, localID, positionSymbol, newLeverage):
        #[1]: Source Check
        if requester != 'TRADEMANAGER':
            return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'LEVERAGEUPDATE', 'result': False, 'failType': 'INVALIDREQUESTER'}

        #[2]: Server Availability Check
        if not self.__connection_serverAvailable:
            return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'LEVERAGEUPDATE', 'result': False, 'failType': 'SERVERUNAVAILABLE'}

        #[3]: Account Check
        if localID not in self.__binance_client_users:
            return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'LEVERAGEUPDATE', 'result': False, 'failType': 'LOCALIDNOTFOUND'}

        #[4]: Account Activation Check
        if localID not in self.__binance_activatedAccounts_LocalIDs:
            return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'LEVERAGEUPDATE', 'result': False, 'failType': 'ACCOUNTNOTACTIVATED'}
        
        #[5]: Update Attempt
        try:
            apiResult = self.__binance_client_users[localID]['accountInstance'].futures_change_leverage(symbol = positionSymbol, leverage = newLeverage)
        except Exception as e: 
            return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'LEVERAGEUPDATE', 'result': False, 'failType': 'APIERROR', 'errorMessage': str(e)}

        #[6]: Result Return
        return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'LEVERAGEUPDATE', 'result': True,  'apiResult': apiResult}
    def __far_createOrder(self, requester, requestID, localID, positionSymbol, orderParams):
        #[1]: Source Check
        if requester != 'TRADEMANAGER':
            self.ipcA.sendFARR(targetProcess  = requester, 
                               functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'INVALIDREQUESTER', 'errorMessage': None},      
                               requestID      = requestID,
                               complete       = True)

        #[2]: Server Availability Check
        if not self.__connection_serverAvailable:
            self.ipcA.sendFARR(targetProcess  = 'TRADEMANAGER', 
                               functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'SERVERUNAVAILABLE', 'errorMessage': None},      
                               requestID      = requestID, 
                               complete       = True)

        #[3]: Account Check
        if localID not in self.__binance_client_users:
            self.ipcA.sendFARR(targetProcess  = 'TRADEMANAGER',
                               functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'LOCALIDNOTFOUND', 'errorMessage': None},      
                               requestID      = requestID,
                               complete       = True)

        #[4]: Account Activation Check
        if localID not in self.__binance_activatedAccounts_LocalIDs:
            self.ipcA.sendFARR(targetProcess  = 'TRADEMANAGER', 
                               functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'ACCOUNTNOTACTIVATED', 'errorMessage': None},      
                               requestID      = requestID, 
                               complete       = True)
            
        #[5]: API Rate Limit Check
        if not self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_ORDERS, weight = 1, apply = True):
            self.ipcA.sendFARR(targetProcess  = 'TRADEMANAGER', 
                               functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'APIRATELIMITREACHED', 'errorMessage': None},      
                               requestID      = requestID, 
                               complete       = True)
            
        #[6]: Order Creation Attempt
        #---[6-1]: Order Params Completion
        orderParams['newClientOrderId'] = "ATMETA"+str(time.time_ns())
        orderParams['newOrderRespType'] = "FULL"
        #---[6-2]: Order Creation Request
        try:                   
            response_createOrder = self.__binance_client_users[localID]['accountInstance'].futures_create_order(**orderParams)
            errorMsg = None
        except Exception as e: 
            response_createOrder = None                                                                                     
            errorMsg = str(e)
        #---[6-3]: Server Response Handling
        if response_createOrder is not None:
            #[6-3-1]: Order has immediately been filled
            if _BINANCE_ORDERSTATUS[response_createOrder['status']]['complete']:
                self.ipcA.sendFARR(targetProcess = 'TRADEMANAGER', 
                                    functionResult = {'localID':        localID, 
                                                      'positionSymbol': positionSymbol, 
                                                      'responseOn':     'CREATEORDER', 
                                                      'result':         _BINANCE_ORDERSTATUS[response_createOrder['status']]['result'],
                                                      'orderResult':    {'type':             response_createOrder['type'],
                                                                         'side':             response_createOrder['side'],
                                                                         'averagePrice':     float(response_createOrder['avgPrice']),
                                                                         'originalQuantity': float(response_createOrder['origQty']),
                                                                         'executedQuantity': float(response_createOrder['executedQty'])},
                                                      'failType':       None,
                                                      'errorMessage':   None},
                                    requestID = requestID, complete = True)
            #[6-3-2]: Order has not immediately been filled
            else:
                self.__binance_createdOrders[response_createOrder['clientOrderId']] = {'IPCRID':                 requestID, 
                                                                                       'localID':                localID, 
                                                                                       'positionSymbol':         positionSymbol, 
                                                                                       'creationCompletionTime': time.perf_counter_ns()+1e9, 
                                                                                       'lastCheckTime':          0, 
                                                                                       'nCheckFails':            0}
        else: 
            self.ipcA.sendFARR(targetProcess  = 'TRADEMANAGER', 
                               functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'APIERROR', 'errorMessage': errorMsg}, 
                               requestID      = requestID, 
                               complete       = True)

    #<#COMMON#>
    def __far_registerKlineStreamSubscription(self, requester, subscriptionID, currencySymbol, subscribeBidsAndAsks = False, subscribeAggTrades = False):
        #[1]: Data Formatting
        if (currencySymbol not in self.__binance_TWM_StreamingData_Subscriptions): 
            self.__initializeStreamDataSubscriptionsForSymbol(symbol = currencySymbol)
        symbolSubscriptions = self.__binance_TWM_StreamingData_Subscriptions[currencySymbol]

        #[2}: Subscription
        if subscriptionID is None:     fID_kline     = 'onKlineStreamReceival'
        else:                          fID_kline     = f'onKlineStreamReceival_{subscriptionID}'
        if   not subscribeBidsAndAsks: fID_depth     = None
        elif subscriptionID is None:   fID_depth     = 'onOrderbookUpdate'
        else:                          fID_depth     = f'onOrderbookUpdate_{subscriptionID}'
        if   not subscribeAggTrades:   fID_aggTrades = None
        elif subscriptionID:           fID_aggTrades = 'onAggTradeStreamReceival'
        else:                          fID_aggTrades = f'onAggTradeStreamReceival_{subscriptionID}'
        subscription = {'subscriber':     requester,
                        'subscriptionID': subscriptionID,
                        'fID_kline':      fID_kline,
                        'fID_depth':      fID_depth,
                        'fID_aggTrades':  fID_aggTrades}
        
        #[3]: Fetch Priority
        subscribers = set(_subscription['subscriber'] for _subscription in symbolSubscriptions['subscriptions']) | {requester,}
        subscribers_hasAnalyzer = False
        subscribers_hasGUI      = False
        for subscriber in subscribers:
            if   subscriber.startswith('ANALYZER'): subscribers_hasAnalyzer = True
            elif subscriber == 'GUI':               subscribers_hasGUI      = True
        if   subscribers_hasAnalyzer: newFetchPriority = 0
        elif subscribers_hasGUI:      newFetchPriority = 1
        else:                         newFetchPriority = 2
        if currencySymbol in self.__binance_fetchRequests_SymbolsByPriority[symbolSubscriptions['fetchPriority']]: self.__binance_fetchRequests_SymbolsByPriority[symbolSubscriptions['fetchPriority']].remove(currencySymbol)
        if currencySymbol in self.__binance_fetchRequests:                                                         self.__binance_fetchRequests_SymbolsByPriority[newFetchPriority].add(currencySymbol)

        #[4]: Finally
        symbolSubscriptions['subscriptions'].append(subscription)
        symbolSubscriptions['fetchPriority'] = newFetchPriority
    def __far_unregisterKlineStreamSubscription(self, requester, subscriptionID, currencySymbol):
        #[1]: Subscription Check
        if currencySymbol not in self.__binance_TWM_StreamingData_Subscriptions:
            return

        #[2]: Instance
        symbolSubscriptions = self.__binance_TWM_StreamingData_Subscriptions[currencySymbol]

        #[3]: Subscription Search & Removal
        subscriptionIndex = None
        for sIndex, subscription in enumerate(symbolSubscriptions['subscriptions']):
            if (subscription['subscriber'] == requester) and (subscription['subscriptionID'] == subscriptionID): 
                subscriptionIndex = sIndex
                break

        #[4]: Fetch Priority Re-evalution (If needed)
        subscribers = set(_subscription['subscriber'] for sIndex, _subscription in enumerate(symbolSubscriptions['subscriptions']) if sIndex != subscriptionIndex)
        subscribers_hasAnalyzer = False
        subscribers_hasGUI      = False
        for subscriber in subscribers:
            if   subscriber.startswith('ANALYZER'): subscribers_hasAnalyzer = True
            elif subscriber == 'GUI':               subscribers_hasGUI      = True
        if   subscribers_hasAnalyzer: newFetchPriority = 0
        elif subscribers_hasGUI:      newFetchPriority = 1
        else:                         newFetchPriority = 2
        if currencySymbol in self.__binance_fetchRequests_SymbolsByPriority[symbolSubscriptions['fetchPriority']]: self.__binance_fetchRequests_SymbolsByPriority[symbolSubscriptions['fetchPriority']].remove(currencySymbol)
        if currencySymbol in self.__binance_fetchRequests:                                                         self.__binance_fetchRequests_SymbolsByPriority[newFetchPriority].add(currencySymbol)

        #[5]: Finally
        if subscriptionIndex is not None: symbolSubscriptions['subscriptions'].pop(subscriptionIndex)
        symbolSubscriptions['fetchPriority'] = newFetchPriority
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------