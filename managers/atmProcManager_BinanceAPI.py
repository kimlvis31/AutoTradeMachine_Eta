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
from datetime import datetime, timezone, tzinfo

#Constants
_SOCKET_HOSTNAME = socket.gethostname()
_SOCKET_HOST_INTERNAL = '127.0.0.1'
_CONNECTIONSCHECKINTERVAL_NS = 1e9
_CONNECTIONSTATUS_BINANCE_DISCONNECTED = -1
_CONNECTIONSTATUS_BINANCE_CONNECTED    = 0
_CONNECTIONSTATUS_BINANCE_MAINTENANCE  = 1

_BINANCE_EXCHANGEINFOREADMAXATTEMPT        = 120
_BINANCE_EXCHANGEINFOREADATTEMPTINTERVAL_S = 0.5
_BINANCE_EXCHANGEINFOREADINTERVAL_S        = 60

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
_BINANCE_TWM_STREAMRENEWALPERIOD_S            = 60*15 #Every 1 hour
_BINANCE_TWM_CLOSEDKLINESMAXWAITTIME_S        = 30

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
        self.__binance_fetchBlock                         = False
        self.__binance_firstKlineOpenTSSearchRequests     = dict()
        self.__binance_firstKlineOpenTSSearchQueue        = set()
        self.__binance_fetchRequests                      = dict()
        self.__binance_fetchRequests_SymbolsByPriority    = {0: set(), 1: set(), 2: set()}
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
        while (self.__processLoopContinue == True):
            t_current_ns = time.perf_counter_ns()

            #Check network and server connection every certain interval
            if (_CONNECTIONSCHECKINTERVAL_NS <= t_current_ns-self.__connection_lastConnectionsCheck_ns):
                self.__checkConnections()
                self.__connection_lastConnectionsCheck_ns = t_current_ns

            #If both network and binance connections are True
            if ((self.__connection_network == True) and (self.__connection_binance == 0)):
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
            time.sleep(0.001)

        #Terminate TWM if it is alive
        try: 
            if (self.__binance_TWM.is_alive() == True): self.__binance_TWM.stop()
            self.__binance_TWM.join()
        except: pass

    def terminate(self, requester):
        self.__processLoopContinue = False
    #Manager Process Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Internal Functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #---Process Configuration
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
        with open(config_dir, 'w') as f:
            json.dump(config_toSave, f, indent=4)
    
    #---Market Connection & Management
    def __checkConnections(self):
        #Get new connection status
        self.__connection_network = self.__checkNetworkConnection()
        if ((self.__connection_network == True) and (self.__connection_network_first == True)): self.__connection_network_first = False; time.sleep(5)
        if (self.__connection_network == True): self.__connection_binance = self.__checkBinanceConnection()
        else:                                   self.__connection_binance = _CONNECTIONSTATUS_BINANCE_DISCONNECTED
        serverAvailable = ((self.__connection_network == True) and (self.__connection_binance == _CONNECTIONSTATUS_BINANCE_CONNECTED))
        #Connection status update handling
        if   ((self.__connection_serverAvailable == True)  and (serverAvailable == False)): self.__onServerUnavailable() #[1]: Available   -> Unavailable
        elif ((self.__connection_serverAvailable == False) and (serverAvailable == True)):  self.__onServerAvailable()   #[2]: Unavailable -> Available
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
            if (self.__binance_client_default == None):
                client = binance.Client()
                status = client.get_system_status()['status']
                self.__binance_client_default = client
                return status
            else: return self.__binance_client_default.get_system_status()['status']
        except: return _CONNECTIONSTATUS_BINANCE_DISCONNECTED
    def __onServerAvailable(self):
        self.__logger(message = "BINANCE SERVER NOW AVAILABLE!", logType = 'Update', color = 'light_green')
        #Market Exchange Info Read
        if self.__getMarketExchangeInfo(): self.__logger(message = "Binance Futures Exchange Information Read Successful", logType = 'Update', color = 'light_green')
        else:                              self.__logger(message = "Binance Futures Exchange Information Read Failed",     logType = 'Update', color = 'light_red')
        #Threaded WebSocket Manager
        if (self.__binance_TWM is None):
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
        if (self.__binance_TWM.is_alive() == True):
            for _connectionID in self.__binance_TWM_Connections:
                _connection     = self.__binance_TWM_Connections[_connectionID]
                _connectionName = _connection['connectionName']
                self.__binance_TWM.stop_socket(_connectionName)
        self.__binance_TWM_StreamQueue.clear()
        self.__binance_TWM_Connections.clear()
        self.__binance_TWM_StreamingData.clear()
        self.__binance_TWM_OverFlowDetected = False
    def __updateAPIRateLimiter(self):
        for limitType in self.__binance_MarketExchangeInfo_RateLimits:
            for rateLimit in self.__binance_MarketExchangeInfo_RateLimits[limitType]:
                t_current_intervalN = int(time.time()/rateLimit['interval_sec'])
                if (rateLimit['tracker_intervalN'] < t_current_intervalN):
                    if (rateLimit['tracker_intervalN'] != -1):
                        rateLimit['tracker_usedLimit'] = 0
                        self.__binance_fetchBlock = False
                    rateLimit['tracker_intervalN'] = t_current_intervalN
    def __getMarketExchangeInfo(self):
        t_current_intervalN = int(time.time()/_BINANCE_EXCHANGEINFOREADINTERVAL_S)
        if (self.__binance_MarketExchangeInfo_LastRead_intervalN < t_current_intervalN):
            #[1]: Market Exchange Info Read Attempt
            if (True):
                exchangeInfo_futures = None
                nAttempts = 0
                self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 1, apply = True)
                while (nAttempts < _BINANCE_EXCHANGEINFOREADMAXATTEMPT):
                    try:    exchangeInfo_futures = self.__binance_client_default.futures_exchange_info(); break
                    except: nAttempts += 1; time.sleep(_BINANCE_EXCHANGEINFOREADATTEMPTINTERVAL_S)
                if (exchangeInfo_futures == None): return False
            #[2]: If rateLimits is not read, read it
            if (True):
                if (self.__binance_MarketExchangeInfo_RateLimits == None):
                    """
                    <Example>
                    exchangeInfo_futures['rateLimits'] = [{'rateLimitType': 'REQUEST_WEIGHT', 'interval': 'MINUTE', 'intervalNum': 1, 'limit': 2400}, 
                                                          {'rateLimitType': 'ORDERS', 'interval': 'MINUTE', 'intervalNum': 1, 'limit': 1200}, 
                                                          {'rateLimitType': 'ORDERS', 'interval': 'SECOND', 'intervalNum': 10, 'limit': 300}]
                    """ #Expand to check a data example
                    self.__binance_MarketExchangeInfo_RateLimits = dict()
                    for rateLimit in exchangeInfo_futures['rateLimits']: 
                        limitType = rateLimit['rateLimitType']
                        if (limitType not in self.__binance_MarketExchangeInfo_RateLimits): self.__binance_MarketExchangeInfo_RateLimits[limitType] = list()
                        if   (rateLimit['interval'] == 'SECOND'): interval_sec =    1*rateLimit['intervalNum']
                        elif (rateLimit['interval'] == 'MINUTE'): interval_sec =   60*rateLimit['intervalNum']
                        elif (rateLimit['interval'] == 'HOUR'):   interval_sec = 3600*rateLimit['intervalNum']
                        else: interval_sec = None; self.__logger(message = f"An unexpected interval detected while attempting to read market exchange info - rateLimits. User attention advised!\n * {str(rateLimit)}", logType = 'Warning', color = 'light_red')
                        if (interval_sec != None): self.__binance_MarketExchangeInfo_RateLimits[limitType].append({'interval_sec': interval_sec, 'limit': rateLimit['limit'], 'tracker_intervalN': int(time.time()/interval_sec), 'tracker_usedLimit': rateLimit['limit']})
                    #Activated Accounts Data Read Limit Update
                    self.__computeMaximumNumberOfAccountsActivation()
                    self.__computeActivatedAccountsDataReadInterval()
            #[3]: Read Symbols Info
            if (True):
                #[3-1]: Re-organize the currency information in terms of the symbols
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
                    if (arf is None or currencyInfo['symbol'] in arf) and (currencyInfo['contractType'] == _BINANCE_CONTRACTTYPE_PERPETUAL): marketExchangeInfo_Symbols[currencyInfo['symbol']] = currencyInfo

                #[3-2]: Identify added and removed assets
                symbols_new  = set(marketExchangeInfo_Symbols.keys())
                symbols_prev = self.__binance_MarketExchangeInfo_Symbols_Set
                symbols_added   = symbols_new-symbols_prev
                symbols_removed = symbols_prev-symbols_new
                symbols_still   = symbols_prev-symbols_added-symbols_removed

                #---[3-2-1]: Handle Added Symbols
                for symbol in symbols_added:
                    #Save symbol information & prepare local tracker
                    marketExchangeInfo_thisSymbol = marketExchangeInfo_Symbols[symbol]
                    self.__binance_MarketExchangeInfo_Symbols[symbol] = marketExchangeInfo_thisSymbol
                    #Check for stream need and add to the queue if needed
                    if ((marketExchangeInfo_thisSymbol['status'] == 'TRADING') and (symbol not in self.__binance_TWM_StreamingData)): self.__binance_TWM_StreamQueue.add(symbol)
                    #Send FAR to the DataManager for the currency registration
                    self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'registerCurrency', functionParams = {'symbol': symbol, 'info': marketExchangeInfo_thisSymbol}, farrHandler = None)

                #---[3-2-2]: Handle Removed Symbols
                for symbol in symbols_removed:
                    #Market Exchange Info Update
                    del self.__binance_MarketExchangeInfo_Symbols[symbol]
                    self.__binance_MarketExchangeInfo_Symbols_Set.remove(symbol)
                    #Queue Control
                    if (symbol in self.__binance_firstKlineOpenTSSearchRequests):
                        del self.__binance_firstKlineOpenTSSearchRequests[symbol]
                        if (symbol in self.__binance_firstKlineOpenTSSearchQueue): self.__binance_firstKlineOpenTSSearchQueue.remove(symbol)
                    if (symbol in self.__binance_TWM_StreamQueue):                self.__binance_TWM_StreamQueue.remove(symbol)
                    #Status Update Announcement
                    self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'onCurrencyInfoUpdate', functionParams = {'symbol': symbol, 'infoUpdates': [{'id': ('status',), 'value': 'REMOVED'}]}, farrHandler = None)

                #---[3-2-3]: Check for any changes to the currencies information and respond
                for symbol in symbols_still:
                    currencyInfo_prev = self.__binance_MarketExchangeInfo_Symbols[symbol]
                    currencyInfo_new  = marketExchangeInfo_Symbols[symbol]
                    #Internal currency information response
                    #---Trading Status
                    if (currencyInfo_prev['status'] != currencyInfo_new['status']):
                        if ((currencyInfo_prev['status'] != 'TRADING') and (currencyInfo_new['status'] == 'TRADING')): #Not Trading -> Trading
                            if (symbol in self.__binance_firstKlineOpenTSSearchRequests): self.__binance_firstKlineOpenTSSearchQueue.add(symbol) #Add to the first kline open TS search queue
                            if (symbol not in self.__binance_TWM_StreamingData):          self.__binance_TWM_StreamQueue.add(symbol)             #Add to the stream queue
                        if ((currencyInfo_prev['status'] == 'TRADING') and (currencyInfo_new['status'] != 'TRADING')): #Trading -> Not Trading
                            if (symbol in self.__binance_firstKlineOpenTSSearchQueue): self.__binance_firstKlineOpenTSSearchQueue.remove(symbol) #Remove from the first kline open TS search queue
                            if (symbol in self.__binance_TWM_StreamQueue):             self.__binance_TWM_StreamQueue.remove(symbol)             #Remove from the stream queue
                        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'onCurrencyInfoUpdate', functionParams = {'symbol': symbol, 'infoUpdates': [{'id': ('status',), 'value': 'TRADING'}]}, farrHandler = None)
                    #---Filters
                    for marketFilter in currencyInfo_new['filters']:
                        pass
            #[4]: Update symbols set
            self.__binance_MarketExchangeInfo_Symbols_Set = symbols_new
            #[5]: Record the last market exhange info read minute
            self.__binance_MarketExchangeInfo_LastRead_intervalN = t_current_intervalN
            #[6]: Return 'True' to indicate successful market exchange info read
            return True
        else: return False
    def __checkAPIRateLimit(self, limitType, weight, extraOnly = False, apply = True, printUpdated = True):
        if (self.__binance_MarketExchangeInfo_RateLimits != None):
            testPass = True
            for rateLimit in self.__binance_MarketExchangeInfo_RateLimits[limitType]:
                _limit_maxEffective = int(rateLimit['limit']/self.config_BinanceAPI['rateLimitIPSharingNumber'])
                if (extraOnly == True):
                    _limit_maxEffective -= rateLimit['interval_sec']
                    _limit_maxEffective -= len(self.__binance_activatedAccounts_LocalIDs)*5*int(rateLimit['interval_sec']*1e9/_BINANCE_ACCOUNTDATAREADINTERVAL_MIN_NS)
                    _limit_maxEffective -= len(self.__binance_createdOrders)             *1*int(rateLimit['interval_sec']*1e9/_BINANCE_CREATEDORDERCHECKINTERVAL_NS)
                if (_limit_maxEffective <= rateLimit['tracker_usedLimit']+weight): testPass = False; break
            if ((testPass == True) and (apply == True)):
                _comment = ""
                for rateLimit in self.__binance_MarketExchangeInfo_RateLimits[limitType]:
                    rateLimit['tracker_usedLimit'] += weight
                    _limit_maxEffective_withExtra = int(rateLimit['limit']/self.config_BinanceAPI['rateLimitIPSharingNumber'])
                    _comment += f"\n * [{limitType}-{rateLimit['interval_sec']}]: {rateLimit['tracker_usedLimit']}/{_limit_maxEffective_withExtra}"
                if (printUpdated == True): self.__logger(message = f"API Used RateLimit Updated{_comment}", logType = 'Update', color = 'light_yellow')
            return testPass
        return None

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
        _connection = self.__binance_TWM_Connections[connectionID]
        #[1]: Socket Stop
        self.__binance_TWM.stop_socket(_connection['connectionName'])
        #[2]: Expired Flag Raise & Buffer Update Wait
        _connection['expired'] = True
        while (_connection['buffer_writing'] == True): time.sleep(0.001)
        #[3]: Announcement Tracker Update
        for _symbol in _connection['symbols']: self.__binance_TWM_StreamingData[_symbol]['lastAnnounced_ns'] = 0
        #[4]: Fetch Requests Clearing
        self.__clearFetchRequests(symbols = _connection['symbols'])
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
        if (symbol in self.__binance_TWM_StreamingData): 
            _sd_this = self.__binance_TWM_StreamingData[symbol]
            _sd_this['connectionID'] = connectionID
            _sd_this['firstReceivedKlineOpenTS']      = None
            _sd_this['lastReceivedClosedKlineOpenTS'] = None
            _sd_this['depth']['fetchRequested'] = False
            _sd_this['depth']['lastUID']        = None
            _sd_this['depth']['lastUID_Fetch']  = None
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
    def __processFirstKlineOpenTSSearchRequests(self):
        _symbols_processed = set()
        #[1]: FirstKlineOpenTS Search
        for _symbol in self.__binance_firstKlineOpenTSSearchQueue:
            #[1-1]: Fetch Block Check
            if (self.__binance_fetchBlock == True): break
            _request = self.__binance_firstKlineOpenTSSearchRequests[_symbol]
            _firstKlineOpenTS = None
            _ts_firstMonth    = None
            _ts_firstDay      = None
            _ts_firstHour     = None
            _ts_first15Minute = None
            _ts_target_beg = _BINANCE_FUTURESSTART_YEAR_TIMESTAMP
            _ts_target_end = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1M, timestamp = _ts_target_beg, nTicks = 96)-1
            #[1-2]: Find the first month (Check every 8 years (= 96 months, largest year multiple under 100), for the first monthly kline since the BINANCE FUTURES market open year)
            _breakQueueLoop = False
            while (_ts_firstMonth is None):
                if (self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 1, extraOnly = True, apply = True) == True):
                    _fetchedKlines = None
                    try: _fetchedKlines = self.__binance_client_default.futures_historical_klines(symbol = _symbol, interval = binance.Client.KLINE_INTERVAL_1MONTH, start_str = _ts_target_beg*1000, end_str = _ts_target_end*1000, limit = 99, verifyFirstTS = False)
                    except Exception as e:
                        self.__binance_fetchBlock = True
                        self.__logger(message = f"An unexpected error ocurred while attempting to fetch klines for a firstKlineOpenTSSearch for {_symbol}\n Exception: {str(e)}", logType = 'Error', color = 'light_red')
                        break
                    if (_fetchedKlines is not None):
                        if (0 < len(_fetchedKlines)): _ts_firstMonth = int(_fetchedKlines[0][0]/1000); break
                        else:
                            _ts_target_beg = _ts_target_end+1
                            _ts_target_end = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1M, timestamp = _ts_target_beg, nTicks = 96)-1
                else: _breakQueueLoop = True; break
            if (_breakQueueLoop == True): break
            #[1-3]: Find the first day within the first month
            if (_ts_firstMonth is not None):
                if (self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 1, extraOnly = True, apply = True) == True):
                    _fetchedKlines = None
                    _ts_target_beg = _ts_firstMonth
                    _ts_target_end = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1M, timestamp = _ts_target_beg, nTicks = 1)-1
                    try: _fetchedKlines = self.__binance_client_default.futures_historical_klines(symbol = _symbol, interval = binance.Client.KLINE_INTERVAL_1DAY, start_str = _ts_target_beg*1000, end_str = _ts_target_end*1000, limit = 99, verifyFirstTS = False)
                    except Exception as e:
                        self.__binance_fetchBlock = True
                        self.__logger(message = f"An unexpected error ocurred while attempting to fetch klines for a firstKlineOpenTSSearch for {_symbol}\n Exception: {str(e)}", logType = 'Error', color = 'light_red')
                    if ((_fetchedKlines is not None) and (0 < len(_fetchedKlines))): _ts_firstDay = int(_fetchedKlines[0][0]/1000)
                else: break
            #[1-4]: Find the first hour within the first day
            if (_ts_firstDay is not None):
                if (self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 1, extraOnly = True, apply = True) == True):
                    _fetchedKlines = None
                    _ts_target_beg = _ts_firstDay
                    _ts_target_end = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1h, timestamp = _ts_target_beg, nTicks = 24)-1
                    try: _fetchedKlines = self.__binance_client_default.futures_historical_klines(symbol = _symbol, interval = binance.Client.KLINE_INTERVAL_1HOUR, start_str = _ts_target_beg*1000, end_str = _ts_target_end*1000, limit = 99, verifyFirstTS = False)
                    except Exception as e:
                        self.__binance_fetchBlock = True
                        self.__logger(message = f"An unexpected error ocurred while attempting to fetch klines for a firstKlineOpenTSSearch for {_symbol}\n Exception: {str(e)}", logType = 'Error', color = 'light_red')
                    if ((_fetchedKlines is not None) and (0 < len(_fetchedKlines))): _ts_firstHour = int(_fetchedKlines[0][0]/1000)
                else: break
            #[1-5]: Find the first 15 minute within the first hour
            if (_ts_firstHour is not None):
                if (self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 1, extraOnly = True, apply = True) == True):
                    _fetchedKlines = None
                    _ts_target_beg = _ts_firstHour
                    _ts_target_end = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_15m, timestamp = _ts_target_beg, nTicks = 4)-1
                    try: _fetchedKlines = self.__binance_client_default.futures_historical_klines(symbol = _symbol, interval = binance.Client.KLINE_INTERVAL_15MINUTE, start_str = _ts_target_beg*1000, end_str = _ts_target_end*1000, limit = 99, verifyFirstTS = False)
                    except Exception as e:
                        self.__binance_fetchBlock = True
                        self.__logger(message = f"An unexpected error ocurred while attempting to fetch klines for a firstKlineOpenTSSearch for {_symbol}\n Exception: {str(e)}", logType = 'Error', color = 'light_red')
                    if ((_fetchedKlines is not None) and (0 < len(_fetchedKlines))): _ts_first15Minute = int(_fetchedKlines[0][0]/1000)
                else: break
            #[1-6]: Finally
            _firstKlineOpenTS = _ts_first15Minute
            if (_firstKlineOpenTS is not None): 
                _symbols_processed.add(_symbol)
                self.ipcA.sendFARR(_request['requester'], {'symbol': _symbol, 'firstKlineOpenTS': _firstKlineOpenTS}, _request['requestID'])
                self.__logger(message = f"The first kline openTS found for {_symbol}: {_firstKlineOpenTS}! ({len(self.__binance_firstKlineOpenTSSearchQueue)-len(_symbols_processed)} remaining)", logType = 'Update', color = 'light_green')
        #[2]: Processed Symbols Removal
        for _symbol in _symbols_processed:
            self.__binance_firstKlineOpenTSSearchQueue.remove(_symbol)
            del self.__binance_firstKlineOpenTSSearchRequests[_symbol]
    def __addFetchRequest(self, symbol, fetchType, requestParams = None):
        #Fetch Request Tracker Setup (If needed)
        if (symbol not in self.__binance_fetchRequests): self.__binance_fetchRequests[symbol] = {'klineFetchRequest': None, 'orderBookFetchRequest': None}
        _fetchRequests_thisSymbol = self.__binance_fetchRequests[symbol]
        #Previous Fetch Control (If needed)
        if (fetchType == 'KLINE'):
            if (_fetchRequests_thisSymbol['klineFetchRequest'] is not None): 
                _fr_prev = _fetchRequests_thisSymbol['klineFetchRequest']
                self.ipcA.sendFARR(targetProcess = _fr_prev['requester'], functionResult = {'status': 'terminate', 'klines': None}, requestID = _fr_prev['requestID'], complete = True)
        #Request Generation
        if (fetchType == 'KLINE'):
            _fetchRequests_thisSymbol['klineFetchRequest'] = {'requester':                 requestParams['requester'],
                                                              'requestID':                 requestParams['requestID'],
                                                              'marketRegistrationTS':      requestParams['marketRegistrationTS'],
                                                              'fetchTargetRanges_initial': requestParams['fetchTargetRanges'].copy(),
                                                              'fetchTargetRanges':         requestParams['fetchTargetRanges'].copy(), 
                                                              'fetchedRanges':             list()}
        if (fetchType == 'DEPTH'):
            _fetchRequests_thisSymbol['orderBookFetchRequest'] = True
        #Update Fetch Handler Priortization
        if (symbol in self.__binance_TWM_StreamingData_Subscriptions): _fetchPriority = self.__binance_TWM_StreamingData_Subscriptions[symbol]['fetchPriority']
        else:                                                          _fetchPriority = 2
        for _fp in self.__binance_fetchRequests_SymbolsByPriority:
            if ((_fp != _fetchPriority) and (symbol in self.__binance_fetchRequests_SymbolsByPriority[_fp])): self.__binance_fetchRequests_SymbolsByPriority[_fp].remove(symbol)
        self.__binance_fetchRequests_SymbolsByPriority[_fetchPriority].add(symbol)
    def __clearFetchRequests(self, symbols = None):
        if (symbols is None): symbols = list(self.__binance_fetchRequests.keys())
        for _symbol in symbols:
            if (_symbol in self.__binance_fetchRequests): 
                #Kline Fetch Request Termination Signaling
                _kfr = self.__binance_fetchRequests[_symbol]['klineFetchRequest']
                if (_kfr is not None): self.ipcA.sendFARR(targetProcess = _kfr['requester'], functionResult = {'status': 'terminate', 'klines': None}, requestID = _kfr['requestID'], complete = True)
                #Symbol Fetch Request Removal
                del self.__binance_fetchRequests[_symbol]
                #Fetch Prioritization Update
                for _fp in self.__binance_fetchRequests_SymbolsByPriority:
                    if (_symbol in self.__binance_fetchRequests_SymbolsByPriority[_fp]): self.__binance_fetchRequests_SymbolsByPriority[_fp].remove(_symbol)
    def __processFetchRequests(self):
        if (len(self.__binance_firstKlineOpenTSSearchQueue) == 0):
            #Target Selection
            _fetchTarget = None
            for _priority in range (3):
                if (_fetchTarget is None): 
                    for _symbol in self.__binance_fetchRequests_SymbolsByPriority[_priority]: _fetchTarget = (_symbol, _priority); break
                else: break
            #Target Process
            if (_fetchTarget is not None):
                _symbol   = _fetchTarget[0]
                _priority = _fetchTarget[1]
                if (self.__binance_fetchBlock == False): self.__processFetchRequests_Kline(symbol     = _symbol)
                if (self.__binance_fetchBlock == False): self.__processFetchRequests_OrderBook(symbol = _symbol)
                if ((self.__binance_fetchRequests[_symbol]['klineFetchRequest'] is None) and (self.__binance_fetchRequests[_symbol]['orderBookFetchRequest'] is None)): 
                    del self.__binance_fetchRequests[_symbol]
                    self.__binance_fetchRequests_SymbolsByPriority[_priority].remove(_symbol)
    def __processFetchRequests_Kline(self, symbol):
        """
        fetchedKlines[n]           = ([0]: t_open, [1]: p_open, [2]: p_high, [3]: p_low, [4]: p_close, [5]: baseAssetVolume, [6]: t_close, [7]: quoteAssetVolume, [8]: nTrades, [9]: baseAssetVolume_takerBuy, [10]: quoteAssetVolume_takerBuy, [11]: ignore)
        fetchedKlines_formatted[n] = ([0]: openTS, [1]: closeTS, [2]: openPrice, [3]: highPrice, [4]: lowPrice, [5]: closePrice, [6]: nTrades, [7]: baseAssetVolume, [8]: quoteAssetVolume, [9]: baseAssetVolume_takerBuy, [10]: quoteAssetVolume_takerBuy, [11]: klineType)
        """ #Expand to check an example of a fetched kline
        _fr = self.__binance_fetchRequests[symbol]['klineFetchRequest']
        if (_fr is not None):
            #[1]: Determine Effective Fetch Target Range
            _fetchTargetRange           = _fr['fetchTargetRanges'][0]
            _fetchTargetRange_effective = None
            _fetchTargetRange_end_max   = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = _fetchTargetRange[0], mrktReg = _fr['marketRegistrationTS'], nTicks = 1000)-1
            if (_fetchTargetRange[1] <= _fetchTargetRange_end_max): _fetchTargetRange_effective = (_fetchTargetRange[0], _fetchTargetRange[1])
            else:                                                   _fetchTargetRange_effective = (_fetchTargetRange[0], _fetchTargetRange_end_max)
            #[2]: Check API Rate Limit and Fetch Klines If Possible
            _expectedKlineOpenTSs   = atmEta_Auxillaries.getTimestampList_byRange(intervalID = KLINTERVAL, mrktReg = _fr['marketRegistrationTS'], timestamp_beg = _fetchTargetRange_effective[0], timestamp_end = _fetchTargetRange_effective[1], lastTickInclusive = True)
            _expectedNumberOfKlines = len(_expectedKlineOpenTSs)
            if   ((  1 <= _expectedNumberOfKlines) and (_expectedNumberOfKlines <   100)): req_weight =  1; fetchLimit = 99
            elif ((100 <= _expectedNumberOfKlines) and (_expectedNumberOfKlines <   500)): req_weight =  2; fetchLimit = 499
            elif ((500 <= _expectedNumberOfKlines) and (_expectedNumberOfKlines <= 1000)): req_weight =  5; fetchLimit = 1000
            else:                                                                          req_weight = 10; fetchLimit = _expectedNumberOfKlines
            if (self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = req_weight, extraOnly = True, apply = True) == True):
                try: fetchedKlines = self.__binance_client_default.futures_historical_klines(symbol = symbol, interval = KLINTERVAL_CLIENT, start_str = _fetchTargetRange_effective[0]*1000, end_str = _fetchTargetRange_effective[1]*1000, limit = fetchLimit, verifyFirstTS = False)
                except Exception as e:
                    self.__binance_fetchBlock = True
                    self.__logger(message = f"An unexpected error ocurred while attempting to fetch klines\n Symbol: {symbol}\n queue: {str(_fr)}\n Exception: {str(e)}", logType = 'Warning', color = 'light_red') 
                    return
            else: self.__binance_fetchBlock = True; return
            #[3]: Format Klines 
            _fetchedKlines_formatted_dict = dict.fromkeys(_expectedKlineOpenTSs, None)
            #---[3-1]: Reformat and insert the fetched klines
            for _kline in fetchedKlines:
                _t_open = int(_kline[0]/1000)
                if (_t_open in _fetchedKlines_formatted_dict): _fetchedKlines_formatted_dict[_t_open] = (_t_open,
                                                                                                         int(_kline[6]/1000),
                                                                                                         _kline[1],
                                                                                                         _kline[2],
                                                                                                         _kline[3],
                                                                                                         _kline[4],
                                                                                                         _kline[8],
                                                                                                         _kline[5],
                                                                                                         _kline[7],
                                                                                                         _kline[9],
                                                                                                         _kline[10],
                                                                                                         _FORMATTEDKLINETYPE_FETCHED)
                else: self.__logger(message = f"An unexpected fetched kline detected for {symbol}@{_t_open}. The corresponding kline will be disposed, but an user attention is advised\n * Effective Fetch Target Range: {str(_fetchTargetRange_effective)}\n * Kline: {str(_kline)}", logType = 'Warning', color = 'red')
            #---[3-2]: Fill in any empty position with a dummy kline
            for _ts in _fetchedKlines_formatted_dict:
                if (_fetchedKlines_formatted_dict[_ts] == None):
                    _fetchedKlines_formatted_dict[_ts] = (_ts, 
                                                          atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = _ts, mrktReg = _fr['marketRegistrationTS'], nTicks = 1)-1, 
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
                    self.__logger(message = f"An expected kline was not fetched for {symbol}@{_ts}. The corresponding position will be filled with a dummy kline, but an user attention is advised*", logType = 'Warning', color = 'light_magenta')
            #---[3-3]: Finally, re-locate the klines into a list and sort
            _fetchedKlines_formatted_list = [_fetchedKlines_formatted_dict[t_open] for t_open in _fetchedKlines_formatted_dict]
            _fetchedKlines_formatted_list.sort(key = lambda x: x[0])
            #[4]: Update the Fetch Ranges
            #---[4-1]: Fetch Target Ranges
            if ((_fetchTargetRange[0] == _fetchTargetRange_effective[0]) and (_fetchTargetRange[1] == _fetchTargetRange_effective[1])): _fr['fetchTargetRanges'].pop(0)
            else:                                                                                                                       _fr['fetchTargetRanges'][0] = (_fetchTargetRange_effective[1]+1, _fr['fetchTargetRanges'][0][1])
            #---[4-2]: Fetched Ranges
            _fr['fetchedRanges'].append(_fetchTargetRange_effective)
            _fr['fetchedRanges'].sort(key = lambda x: x[0])
            _fetchedRanges_merged = [_fr['fetchedRanges'][0],]
            for _dataRange in _fr['fetchedRanges'][1:]:
                if (_fetchedRanges_merged[-1][1]+1 == _dataRange[0]): _fetchedRanges_merged[-1] = (_fetchedRanges_merged[-1][0], _dataRange[1])
                else:                                                 _fetchedRanges_merged.append(_dataRange)
            _fr['fetchedRanges'] = _fetchedRanges_merged
            #Send fetch result
            if (len(_fr['fetchTargetRanges']) == 0):
                self.ipcA.sendFARR(targetProcess = _fr['requester'], functionResult = {'status': 'complete', 'klines': _fetchedKlines_formatted_list}, requestID = _fr['requestID'], complete = True)
                self.__binance_fetchRequests[symbol]['klineFetchRequest'] = None
                self.__logger(message = f"Successfully completed a kline fetch request for {symbol} from {_fr['requester']}", logType = 'Update', color = 'light_green')
            else: 
                self.ipcA.sendFARR(targetProcess = _fr['requester'], functionResult = {'status': 'fetching', 'klines': _fetchedKlines_formatted_list}, requestID = _fr['requestID'], complete = False)
                totalTSLength   = sum([targetRange[1] -targetRange[0] +1 for targetRange  in _fr['fetchTargetRanges_initial']])
                fetchedTSLength = sum([fetchedRange[1]-fetchedRange[0]+1 for fetchedRange in _fr['fetchedRanges']])
                completion = round(fetchedTSLength/totalTSLength*100, 3)
                self.__logger(message = f"Successfully processed a kline fetch request for {symbol} from {_fr['requester']} ({completion:.3f} % Complete)", logType = 'Update', color = 'light_green')
    def __processFetchRequests_OrderBook(self, symbol):
        _fr = self.__binance_fetchRequests[symbol]['orderBookFetchRequest']
        if (_fr is not None):
            if (self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 20, extraOnly = True, apply = True, printUpdated = True) == True):
                _streamingData_depth = self.__binance_TWM_StreamingData[symbol]['depth']
                _ob_fetched = None
                try: _ob_fetched = self.__binance_client_default.futures_order_book(symbol = symbol, limit = 1000)
                except Exception as e:
                    self.__binance_fetchBlock = True
                    self.__logger(message = f"An unexpected error ocurred while attempting to fetch order blocks for {symbol}\n Exception: {str(e)}", logType = 'Warning', color = 'light_red')
                if (_ob_fetched is not None):
                    _complete      = None
                    _lastUID       = None
                    _lastUID_fetch = None
                    #Orderbooks Init
                    _orderbook_bids = dict()
                    _orderbook_asks = dict()
                    #From the fetched OB
                    for _bid in _ob_fetched['bids']: _orderbook_bids[float(_bid[0])] = float(_bid[1])
                    for _ask in _ob_fetched['asks']: _orderbook_asks[float(_ask[0])] = float(_ask[1])
                    #Buffer Read
                    if (0 < len(_streamingData_depth['buffer'])):
                        #Buffer Contents Filtering & Continuation Check
                        _buffer_after = [_update for _update in _streamingData_depth['buffer'] if (_ob_fetched['lastUpdateId'] <= _update['u'])]
                        _buffer_after_uidCheck = True
                        if (0 < len(_buffer_after)):
                            _buffer_after_lastFinalUpdateID = _buffer_after[0]['u']
                            for _buffer in _buffer_after[1:]:
                                if (_buffer['pu'] == _buffer_after_lastFinalUpdateID): _buffer_after_lastFinalUpdateID = _buffer['u']
                                else: _buffer_after_uidCheck = False; break
                            if (_buffer_after_uidCheck == True): _buffer_after_uidCheck = (_buffer_after[0]['U'] <= _ob_fetched['lastUpdateId']) and (_ob_fetched['lastUpdateId'] <= _buffer_after[0]['u'])
                        #Buffer Contents Read
                        if (len(_buffer_after) == 0): 
                            _complete      = True
                            _lastUID_fetch = _ob_fetched['lastUpdateId']
                        elif (_buffer_after_uidCheck == True): 
                            for _update in _buffer_after:
                                for _bidUpdate in _update['b']: 
                                    _pl = float(_bidUpdate[0])
                                    _qt = float(_bidUpdate[1])
                                    _orderbook_bids[_pl] = _qt
                                    if   (_qt == 0):               del _orderbook_bids[_pl]
                                    elif (_pl in _orderbook_asks): del _orderbook_asks[_pl]
                                for _askUpdate in _update['a']: 
                                    _pl = float(_askUpdate[0])
                                    _qt = float(_askUpdate[1])
                                    _orderbook_asks[_pl] = _qt
                                    if   (_qt == 0):               del _orderbook_asks[_pl]
                                    elif (_pl in _orderbook_bids): del _orderbook_bids[_pl]
                            _lastUID  = _buffer_after[-1]['u']
                            _complete = True
                    else:
                        _buffer_after  = list()
                        _complete      = True
                        _lastUID_fetch = _ob_fetched['lastUpdateId']
                    #Finally
                    _streamingData_depth['buffer'] = _buffer_after
                    if (_complete == True):
                        _streamingData_depth['fetchRequested'] = False
                        _streamingData_depth['bids']           = _orderbook_bids
                        _streamingData_depth['asks']           = _orderbook_asks
                        _streamingData_depth['lastUID']        = _lastUID
                        _streamingData_depth['lastUID_Fetch']  = _lastUID_fetch
                        #Fetch Result Clearing
                        self.__binance_fetchRequests[symbol]['orderBookFetchRequest'] = None
                        #Console Message
                        self.__logger(message = f"Successfully completed the order book profile for {symbol}", logType = 'Update', color = 'light_green')

    #---Accounts
    def __computeMaximumNumberOfAccountsActivation(self):
        _maxActivationN_min = float('inf')
        for rateLimit in self.__binance_MarketExchangeInfo_RateLimits['REQUEST_WEIGHT']:
            _maxActivationN = int((rateLimit['limit']/self.config_BinanceAPI['rateLimitIPSharingNumber']*0.5*_BINANCE_ACCOUNTDATAREADINTERVAL_MAX_NS/1e9)/(5*rateLimit['interval_sec']))
            if (_maxActivationN < _maxActivationN_min): _maxActivationN_min = _maxActivationN
        self.__binance_activatedAccounts_maxActivation = _maxActivationN_min
    def __computeActivatedAccountsDataReadInterval(self):
        _readInterval_s_max = 0
        for rateLimit in self.__binance_MarketExchangeInfo_RateLimits['REQUEST_WEIGHT']:
            _readInterval_sec = (5*len(self.__binance_activatedAccounts_LocalIDs)*rateLimit['interval_sec'])/(rateLimit['limit']*self.config_BinanceAPI['rateLimitIPSharingNumber']*0.5)*1.1
            if (_readInterval_s_max < _readInterval_sec): _readInterval_s_max = _readInterval_sec
        self.__binance_activatedAccounts_readInterval_ns = _readInterval_s_max*1e9
        if (self.__binance_activatedAccounts_readInterval_ns < _BINANCE_ACCOUNTDATAREADINTERVAL_MIN_NS): self.__binance_activatedAccounts_readInterval_ns = _BINANCE_ACCOUNTDATAREADINTERVAL_MIN_NS
    def __readActivatedAccountsData(self):
        _t_current_ns       = time.perf_counter_ns()
        _nActivatedAccounts = len(self.__binance_activatedAccounts_LocalIDs)
        if ((0 < _nActivatedAccounts) and (self.__binance_activatedAccounts_readInterval_ns <= _t_current_ns-self.__binance_activatedAccounts_lastDataRead_ns) or (self.__binance_activatedAccounts_dataReadRequest == True)):
            _apiRateLimitTest = self.__checkAPIRateLimit(limitType    = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, 
                                                         weight       = _nActivatedAccounts*5, 
                                                         extraOnly    = False,
                                                         apply        = True, 
                                                         printUpdated = False)
            if (_apiRateLimitTest == True):
                for _localID in self.__binance_activatedAccounts_LocalIDs:
                    _account = self.__binance_client_users[_localID]
                    try:                   _accountData = _account['accountInstance'].futures_account(); _errorMsg = None
                    except Exception as e: _accountData = None;                                          _errorMsg = str(e)
                    if (_accountData is None):
                        _account['nConsecutiveDataReadFails'] += 1
                        if (_BINANCE_ACCOUNTDATAREADTOLERATEDCONSECUTIVEFAILS < _account['nConsecutiveDataReadFails']):
                            self.__logger(message = f"Account Data Read For {_localID} Failed More Than {_BINANCE_ACCOUNTDATAREADTOLERATEDCONSECUTIVEFAILS} Times Consecutively.\n * {_errorMsg}", logType = 'Warning', color = 'light_red')
                    else:
                        _account['nConsecutiveDataReadFails'] = 0
                        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'onAccountDataReceival', functionParams = {'localID': _localID, 'accountData': _accountData}, farrHandler = None)
                self.__binance_activatedAccounts_lastDataRead_ns = _t_current_ns
                self.__binance_activatedAccounts_dataReadRequest = False
    def __checkCreatedOrdersCompletion(self):
        _completedOrders = list()
        for _coID, _createdOrder in self.__binance_createdOrders.items():
            t_current_ns = time.perf_counter_ns()
            if (_BINANCE_CREATEDORDERCHECKINTERVAL_NS <= t_current_ns-_createdOrder['lastCheckTime']):
                if (self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 1, extraOnly = False, apply = True) == True):
                    _order_fromServer           = None
                    _apiError_orderDoesNotExist = False
                    #Order Status Read Attempt
                    try: _order_fromServer = self.__binance_client_users[_createdOrder['localID']]['accountInstance'].futures_get_order(symbol = _createdOrder['positionSymbol'], origclientorderid = _coID)
                    except Exception as e:
                        if (str(e) == 'APIError(code=-2013): Order does not exist.'): _apiError_orderDoesNotExist = True
                        else: self.__logger(message = f"An unexpected error ocrrued while attempting to check created order status for {_createdOrder['localID']}-{_createdOrder['positionSymbol']}. \n * {str(e)}", logType = 'Error', color = 'light_red')
                    #Order Status Read Attempt Result Handling
                    if (_order_fromServer is not None):
                        if (_BINANCE_ORDERSTATUS[_order_fromServer['status']]['complete'] == True):
                            self.ipcA.sendFARR(targetProcess = 'TRADEMANAGER', 
                                               functionResult = {'localID':        _createdOrder['localID'], 
                                                                 'positionSymbol': _createdOrder['positionSymbol'], 
                                                                 'responseOn':     'CREATEORDER', 
                                                                 'result':         _BINANCE_ORDERSTATUS[_order_fromServer['status']]['result'],
                                                                 'orderResult':    {'type':             _order_fromServer['type'],
                                                                                    'side':             _order_fromServer['side'],
                                                                                    'averagePrice':     float(_order_fromServer['avgPrice']),
                                                                                    'originalQuantity': float(_order_fromServer['origQty']),
                                                                                    'executedQuantity': float(_order_fromServer['executedQty'])},
                                                                 'failType':       None,
                                                                 'errorMessage':   None}, 
                                               requestID = _createdOrder['IPCRID'], complete = True)
                            _completedOrders.append(_coID)
                    elif (_apiError_orderDoesNotExist == True):
                        _createdOrder['nCheckFails'] += 1
                        if (_createdOrder['nCheckFails'] == _BINANCE_CREATEDORDERCANCELLATIONTHRESHOLD):
                            self.ipcA.sendFARR(targetProcess = 'TRADEMANAGER', 
                                               functionResult = {'localID':        _createdOrder['localID'], 
                                                                 'positionSymbol': _createdOrder['positionSymbol'], 
                                                                 'responseOn':     'CREATEORDER', 
                                                                 'result':         False,
                                                                 'orderResult':    None,
                                                                 'failType':       'CANCELLATIONTHRESHOLDREACHED',
                                                                 'errorMessage':   None}, 
                                               requestID = _createdOrder['IPCRID'], complete = True)
                            self.__logger(message = f"A created order for {_createdOrder['localID']}-{_createdOrder['positionSymbol']} check loop terminated due to the cancellation threshold reach.", logType = 'Warning', color = 'light_magenta')
                            _completedOrders.append(_coID)
                    else:
                        self.ipcA.sendFARR(targetProcess = 'TRADEMANAGER', 
                                            functionResult = {'localID':        _createdOrder['localID'], 
                                                              'positionSymbol': _createdOrder['positionSymbol'], 
                                                              'responseOn':     'CREATEORDER', 
                                                              'result':         False,
                                                              'orderResult':    None,
                                                              'failType':       'UNEXPECTEDERROR',
                                                              'errorMessage':   None}, 
                                            requestID = _createdOrder['IPCRID'], complete = True)
                        self.__logger(message = f"A created order for {_createdOrder['localID']}-{_createdOrder['positionSymbol']} check loop terminated due to an unexpected error.", logType = 'Warning', color = 'light_magenta')
                        _completedOrders.append(_coID)
                _createdOrder['lastCheckTime'] = t_current_ns
        for _coID in _completedOrders: del self.__binance_createdOrders[_coID]

    #---System
    def __logger(self, message, logType, color):
        if (self.config_BinanceAPI[f'print_{logType}'] == True): 
            _time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
            print(termcolor.colored(f"[BINANCEAPI-{_time_str}] {message}", color))
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
        if (requester == 'GUI'):
            #Rate Limit IP Sharing Number
            if ((type(newConfiguration['rateLimitIPSharingNumber']) == int) and (1 <= newConfiguration['rateLimitIPSharingNumber']) and (newConfiguration['rateLimitIPSharingNumber'] <= 5)): self.config_BinanceAPI['rateLimitIPSharingNumber'] = newConfiguration['rateLimitIPSharingNumber']
            #Print Update
            self.config_BinanceAPI['print_Update'] = newConfiguration['print_Update']
            #Print Warning
            self.config_BinanceAPI['print_Warning'] = newConfiguration['print_Warning']
            #Print Error
            self.config_BinanceAPI['print_Error'] = newConfiguration['print_Error']
            #Save Config # Update Announcement
            self.__saveBinanceAPIConfig()
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CONFIGURATION', prdContent = self.config_BinanceAPI)
            return {'result': True, 'message': "Configuration Successfully Updated!", 'configuration': self.config_BinanceAPI}
    #<DATAMANAGER>
    def __far_addFirstKlineOpenTSSearchRequest(self, requester, requestID, symbol):
        if (symbol in self.__binance_MarketExchangeInfo_Symbols):
            self.__binance_firstKlineOpenTSSearchRequests[symbol] = {'symbol':    symbol, 
                                                                     'requester': requester, 
                                                                     'requestID': requestID}
            if (self.__binance_MarketExchangeInfo_Symbols[symbol]['status'] == 'TRADING'): self.__binance_firstKlineOpenTSSearchQueue.add(symbol)
    def __far_addKlineFetchRequestQueue(self, requester, requestID, symbol, marketRegistrationTimestamp, streamConnectionTime, fetchTargetRanges):
        #[1]: Current Stream Connection Time
        _streamConnectionTime_current = None
        if (symbol in self.__binance_TWM_StreamingData):
            _connectionID = self.__binance_TWM_StreamingData[symbol]['connectionID']
            if ((_connectionID is not None) and (self.__binance_TWM_Connections[_connectionID]['expired'] == False)): _streamConnectionTime_current = self.__binance_TWM_Connections[_connectionID]['connectionTime']
        #[2]: Request Generation
        if (_streamConnectionTime_current == streamConnectionTime):
            _requestParams = {'requester':            requester,
                              'requestID':            requestID,
                              'marketRegistrationTS': marketRegistrationTimestamp,
                              'fetchTargetRanges':    fetchTargetRanges}
            self.__addFetchRequest(symbol = symbol, fetchType = 'KLINE', requestParams = _requestParams)
        else: self.ipcA.sendFARR(targetProcess = requester, functionResult = {'status': 'terminate', 'klines': None}, requestID = requestID, complete = True)

    #<TRADEMANAGER>
    def __far_generateAccountInstance(self, requester, requestID, localID, uid, apiKey, secretKey):
        if (requester == 'TRADEMANAGER'):
            if (self.__connection_serverAvailable == True):
                try:
                    if (len(self.__binance_activatedAccounts_LocalIDs) < self.__binance_activatedAccounts_maxActivation):
                        newAccount = binance.Client(api_key = apiKey, api_secret = secretKey)
                        newAccount_uid = newAccount.get_account()['uid']
                        if (newAccount_uid == uid):
                            apiPermissions = newAccount.get_account_api_permissions()
                            if (apiPermissions['enableFutures'] == True):
                                self.__binance_client_users[localID] = {'accountInstance':           newAccount,
                                                                        'nConsecutiveDataReadFails': 0}
                                #---Local ID, Data Read Request
                                self.__binance_activatedAccounts_LocalIDs.add(localID)
                                self.__binance_activatedAccounts_dataReadRequest = True
                                #---Read Interval
                                self.__computeActivatedAccountsDataReadInterval()
                                #---Result Return
                                return        {'result': True}
                            else: return      {'result': False, 'failType': 'FUTURESDISABLED'}
                        else: return          {'result': False, 'failType': 'UIDMISMATCH'}
                    else: return              {'result': False, 'failType': 'MAXACTIVATIONREACHED'}
                except Exception as e: return {'result': False, 'failType': 'UNEXPECTEDERROR', 'errorMessage': str(e)}
            else: return                      {'result': False, 'failType': 'SERVERUNAVAILABLE'}
    def __far_removeAccountInstance(self, requester, localID):
        if (requester == 'TRADEMANAGER'):
            if (localID in self.__binance_client_users):
                #---Local ID, Data Read Request
                del self.__binance_client_users[localID]
                self.__binance_activatedAccounts_LocalIDs.remove(localID)
                #---Read Interval
                _readInterval_s_max = 0
                for rateLimit in self.__binance_MarketExchangeInfo_RateLimits['REQUEST_WEIGHT']:
                    _readInterval_sec = (5*len(self.__binance_activatedAccounts_LocalIDs)*rateLimit['interval_sec'])/(rateLimit['limit']*self.config_BinanceAPI['rateLimitIPSharingNumber']*0.5)*1.1
                    if (_readInterval_s_max < _readInterval_sec): _readInterval_s_max = _readInterval_sec
                self.__binance_activatedAccounts_readInterval_ns = _readInterval_s_max*1e9
                if (self.__binance_activatedAccounts_readInterval_ns < _BINANCE_ACCOUNTDATAREADINTERVAL_MIN_NS): self.__binance_activatedAccounts_readInterval_ns = _BINANCE_ACCOUNTDATAREADINTERVAL_MIN_NS
    def __far_setPositionMarginType(self, requester, requestID, localID, positionSymbol, newMarginType):
        if (requester == 'TRADEMANAGER'):
            if (self.__connection_serverAvailable == True):
                if (localID in self.__binance_client_users):
                    if (localID in self.__binance_activatedAccounts_LocalIDs):
                        if ((newMarginType == 'ISOLATED') or (newMarginType == 'CROSSED')):
                            try:
                                if   (newMarginType == 'ISOLATED'): apiResult = self.__binance_client_users[localID]['accountInstance'].futures_change_margin_type(symbol = positionSymbol, marginType = newMarginType)
                                elif (newMarginType == 'CROSSED'):  apiResult = self.__binance_client_users[localID]['accountInstance'].futures_change_margin_type(symbol = positionSymbol, marginType = newMarginType)
                                return                    {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'MARGINTYPEUPDATE', 'result': True,  'apiResult': apiResult}
                            except Exception as e: return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'MARGINTYPEUPDATE', 'result': False, 'failType': 'APIERROR', 'errorMessage': str(e)}
                        else: return                      {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'MARGINTYPEUPDATE', 'result': False, 'failType': 'MARGINTYPEERROR'}
                    else: return                          {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'MARGINTYPEUPDATE', 'result': False, 'failType': 'ACCOUNTNOTACTIVATED'}
                else: return                              {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'MARGINTYPEUPDATE', 'result': False, 'failType': 'LOCALIDNOTFOUND'}
            else: return                                  {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'MARGINTYPEUPDATE', 'result': False, 'failType': 'SERVERUNAVAILABLE'}
    def __far_setPositionLeverage(self, requester, requestID, localID, positionSymbol, newLeverage):
        if (requester == 'TRADEMANAGER'):
            if (self.__connection_serverAvailable == True):
                if (localID in self.__binance_client_users):
                    if (localID in self.__binance_activatedAccounts_LocalIDs):
                        try:
                            apiResult = self.__binance_client_users[localID]['accountInstance'].futures_change_leverage(symbol = positionSymbol, leverage = newLeverage)
                            return                        {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'LEVERAGEUPDATE', 'result': True,  'apiResult': apiResult}
                        except Exception as e: return     {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'LEVERAGEUPDATE', 'result': False, 'failType': 'APIERROR', 'errorMessage': str(e)}
                    else: return                          {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'LEVERAGEUPDATE', 'result': False, 'failType': 'ACCOUNTNOTACTIVATED'}
                else: return                              {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'LEVERAGEUPDATE', 'result': False, 'failType': 'LOCALIDNOTFOUND'}
            else: return                                  {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'LEVERAGEUPDATE', 'result': False, 'failType': 'SERVERUNAVAILABLE'}
    def __far_createOrder(self, requester, requestID, localID, positionSymbol, orderParams):
        if (requester == 'TRADEMANAGER'):
            if (self.__connection_serverAvailable == True):
                if (localID in self.__binance_client_users):
                    if (localID in self.__binance_activatedAccounts_LocalIDs):
                        if (self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_ORDERS, weight = 1, apply = True) == True):
                            _coID = "ATMETA"+str(time.time_ns())
                            orderParams['newClientOrderId'] = _coID
                            orderParams['newOrderRespType'] = "FULL"
                            try:                   _response_createOrder = self.__binance_client_users[localID]['accountInstance'].futures_create_order(**orderParams); _errorMsg = None
                            except Exception as e: _response_createOrder = None;                                                                                        _errorMsg = str(e)
                            if (_response_createOrder is not None):
                                #[1]: Order has immediately been filled
                                if (_BINANCE_ORDERSTATUS[_response_createOrder['status']]['complete'] == True):
                                    self.ipcA.sendFARR(targetProcess = 'TRADEMANAGER', 
                                                       functionResult = {'localID':        localID, 
                                                                         'positionSymbol': positionSymbol, 
                                                                         'responseOn':     'CREATEORDER', 
                                                                         'result':         _BINANCE_ORDERSTATUS[_response_createOrder['status']]['result'],
                                                                         'orderResult':    {'type':             _response_createOrder['type'],
                                                                                            'side':             _response_createOrder['side'],
                                                                                            'averagePrice':     float(_response_createOrder['avgPrice']),
                                                                                            'originalQuantity': float(_response_createOrder['origQty']),
                                                                                            'executedQuantity': float(_response_createOrder['executedQty'])},
                                                                         'failType':       None,
                                                                         'errorMessage':   None},
                                                        requestID = requestID, complete = True)
                                #[2]: Order has not immediately been filled
                                else:
                                    self.__binance_createdOrders[_response_createOrder['clientOrderId']] = {'IPCRID':                 requestID, 
                                                                                                            'localID':                localID, 
                                                                                                            'positionSymbol':         positionSymbol, 
                                                                                                            'creationCompletionTime': time.perf_counter_ns()+1e9, 
                                                                                                            'lastCheckTime':          0, 
                                                                                                            'nCheckFails':            0}
                            else: self.ipcA.sendFARR(targetProcess = 'TRADEMANAGER', functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'APIERROR',            'errorMessage': _errorMsg}, requestID = requestID, complete = True)
                        else:     self.ipcA.sendFARR(targetProcess = 'TRADEMANAGER', functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'APIRATELIMITREACHED', 'errorMessage': None},      requestID = requestID, complete = True)
                    else:         self.ipcA.sendFARR(targetProcess = 'TRADEMANAGER', functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'ACCOUNTNOTACTIVATED', 'errorMessage': None},      requestID = requestID, complete = True)
                else:             self.ipcA.sendFARR(targetProcess = 'TRADEMANAGER', functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'LOCALIDNOTFOUND',     'errorMessage': None},      requestID = requestID, complete = True)
            else:                 self.ipcA.sendFARR(targetProcess = 'TRADEMANAGER', functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'SERVERUNAVAILABLE',   'errorMessage': None},      requestID = requestID, complete = True)

    #<#COMMON#>
    def __far_registerKlineStreamSubscription(self, requester, subscriptionID, currencySymbol, subscribeBidsAndAsks = False, subscribeAggTrades = False):
        #[1]: Data Formatting
        if (currencySymbol not in self.__binance_TWM_StreamingData_Subscriptions): self.__initializeStreamDataSubscriptionsForSymbol(symbol = currencySymbol)
        _symbolSubscriptions = self.__binance_TWM_StreamingData_Subscriptions[currencySymbol]
        #[2}: Subscription
        if (subscriptionID is None):          _fID_kline     = 'onKlineStreamReceival'
        else:                                 _fID_kline     = f'onKlineStreamReceival_{subscriptionID}'
        if   (subscribeBidsAndAsks == False): _fID_depth     = None
        elif (subscriptionID is None):        _fID_depth     = 'onOrderbookUpdate'
        else:                                 _fID_depth     = f'onOrderbookUpdate_{subscriptionID}'
        if   (subscribeAggTrades == False):   _fID_aggTrades = None
        elif (subscriptionID is None):        _fID_aggTrades = 'onAggTradeStreamReceival'
        else:                                 _fID_aggTrades = f'onAggTradeStreamReceival_{subscriptionID}'
        _subscription = {'subscriber':     requester,
                         'subscriptionID': subscriptionID,
                         'fID_kline':     _fID_kline,
                         'fID_depth':     _fID_depth,
                         'fID_aggTrades': _fID_aggTrades}
        #[3]: Fetch Priority
        _subscribers  = set(_subscription['subscriber'] for _subscription in _symbolSubscriptions['subscriptions']) | {requester,}
        _subscribers_hasAnalyzer = False
        _subscribers_hasGUI      = False
        for _subscriber in _subscribers:
            if   (_subscriber[:8] == 'ANALYZER'): _subscribers_hasAnalyzer = True
            elif (_subscriber     == 'GUI'):      _subscribers_hasGUI      = True
        if   (_subscribers_hasAnalyzer == True): _newFetchPriority = 0
        elif (_subscribers_hasGUI      == True): _newFetchPriority = 1
        else:                                    _newFetchPriority = 2
        if (currencySymbol in self.__binance_fetchRequests_SymbolsByPriority[_symbolSubscriptions['fetchPriority']]): self.__binance_fetchRequests_SymbolsByPriority[_symbolSubscriptions['fetchPriority']].remove(currencySymbol)
        if (currencySymbol in self.__binance_fetchRequests):                                                          self.__binance_fetchRequests_SymbolsByPriority[_newFetchPriority].add(currencySymbol)
        #[4]: Finally
        _symbolSubscriptions['subscriptions'].append(_subscription)
        _symbolSubscriptions['fetchPriority'] = _newFetchPriority
    def __far_unregisterKlineStreamSubscription(self, requester, subscriptionID, currencySymbol):
        if (currencySymbol in self.__binance_TWM_StreamingData_Subscriptions):
            _symbolSubscriptions = self.__binance_TWM_StreamingData_Subscriptions[currencySymbol]
            #[1]: Subscription Search & Removal
            _subscriptionIndex = None
            for _sIndex, _subscription in enumerate(_symbolSubscriptions['subscriptions']):
                if ((_subscription['subscriber'] == requester) and (_subscription['subscriptionID'] == subscriptionID)): _subscriptionIndex = _sIndex; break
            #[2]: Fetch Priority Re-evalution (If needed)
            _subscribers  = set(_subscription['subscriber'] for _subscription in _symbolSubscriptions['subscriptions'])
            _subscribers_hasAnalyzer = False
            _subscribers_hasGUI      = False
            for _subscriber in _subscribers:
                if   (_subscriber[:8] == 'ANALYZER'): _subscribers_hasAnalyzer = True
                elif (_subscriber     == 'GUI'):      _subscribers_hasGUI      = True
            if   (_subscribers_hasAnalyzer == True): _newFetchPriority = 0
            elif (_subscribers_hasGUI      == True): _newFetchPriority = 1
            else:                                    _newFetchPriority = 2
            if (currencySymbol in self.__binance_fetchRequests_SymbolsByPriority[_symbolSubscriptions['fetchPriority']]): self.__binance_fetchRequests_SymbolsByPriority[_symbolSubscriptions['fetchPriority']].remove(currencySymbol)
            if (currencySymbol in self.__binance_fetchRequests):                                                          self.__binance_fetchRequests_SymbolsByPriority[_newFetchPriority].add(currencySymbol)
            #[3]: Finally
            if (_subscriptionIndex is not None): _symbolSubscriptions['subscriptions'].pop(_subscriptionIndex)
            _symbolSubscriptions['fetchPriority'] = _newFetchPriority
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------