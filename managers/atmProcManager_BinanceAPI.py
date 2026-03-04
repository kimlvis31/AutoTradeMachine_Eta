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
import requests
import xml.etree.ElementTree as ET
import io
import zipfile
import csv
import hashlib
import re
import pprint
import calendar
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timezone, tzinfo, timedelta
from collections import deque
from concurrent.futures import ThreadPoolExecutor

#Constants
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
KLINDEX_CLOSED           = 11
KLINDEX_SOURCE           = 12

DEPTHINDEX_OPENTIME  = 0
DEPTHINDEX_CLOSETIME = 1
DEPTHINDEX_BIDS5     = 2
DEPTHINDEX_BIDS4     = 3 
DEPTHINDEX_BIDS3     = 4
DEPTHINDEX_BIDS2     = 5 
DEPTHINDEX_BIDS1     = 6 
DEPTHINDEX_BIDS0     = 7 
DEPTHINDEX_ASKS0     = 8 
DEPTHINDEX_ASKS1     = 9 
DEPTHINDEX_ASKS2     = 10 
DEPTHINDEX_ASKS3     = 11
DEPTHINDEX_ASKS4     = 12
DEPTHINDEX_ASKS5     = 13
DEPTHINDEX_CLOSED    = 14
DEPTHINDEX_SOURCE    = 15

ATINDEX_OPENTIME     = 0
ATINDEX_CLOSETIME    = 1
ATINDEX_QUANTITYBUY  = 2
ATINDEX_QUANTITYSELL = 3
ATINDEX_NTRADESBUY   = 4
ATINDEX_NTRADESSELL  = 5
ATINDEX_NOTIONALBUY  = 6
ATINDEX_NOTIONALSELL = 7
ATINDEX_CLOSED       = 8
ATINDEX_SOURCE       = 9

_CONNECTIONSCHECKINTERVAL_NS = 1e9
_CONNECTIONSTATUS_BINANCE_DISCONNECTED = -1
_CONNECTIONSTATUS_BINANCE_CONNECTED    = 0
_CONNECTIONSTATUS_BINANCE_MAINTENANCE  = 1

_BINANCE_EXCHANGEINFOREADMAXATTEMPT        = 120
_BINANCE_EXCHANGEINFOREADATTEMPTINTERVAL_S = 0.5
_BINANCE_EXCHANGEINFOREADINTERVAL_S        = 60

_BINANCE_VISIONDATAUPDATEINTERVAL_NS                  = 3600e9
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
_BINANCE_TWM_STREAMRENEWALPERIOD_S            = 60*1 #Every 1 hour
_BINANCE_TWM_CLOSEDKLINESMAXWAITTIME_S        = 15

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

_FORMATTEDDATATYPE_FETCHED    = 0
_FORMATTEDDATATYPE_DUMMY      = 1
_FORMATTEDDATATYPE_STREAMED   = 2
_FORMATTEDDATATYPE_INCOMPLETE = 3

_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

KLINTERVAL        = atmEta_Constants.KLINTERVAL
KLINTERVAL_CLIENT = atmEta_Constants.KLINTERVAL_CLIENT
KLINTERVAL_STREAM = atmEta_Constants.KLINTERVAL_STREAM
KLINTERVAL_S      = atmEta_Constants.KLINTERVAL_S

ORDERBOOKACCEPTANCERANGE = atmEta_Constants.ORDERBOOKACCEPTANCERANGE

TWMSTATUS_PREPARING = 0
TWMSTATUS_READY     = 1
TWMSTATUS_EXPIRED   = 2

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
        #---Binance Vision Session
        self.__binance_visionSession  = requests.Session()
        self.__binance_visionExecutor = ThreadPoolExecutor(max_workers=20)
        bvs_retryStrategy = Retry(total            = 5, 
                                  backoff_factor   = 1, 
                                  status_forcelist = [500, 502, 503, 504], 
                                  allowed_methods  = ["GET"])
        bvs_adapter = HTTPAdapter(max_retries      = bvs_retryStrategy,
                                  pool_connections = 20,
                                  pool_maxsize     = 20)
        self.__binance_visionSession.mount("https://", bvs_adapter)
        self.__binance_visionSession.mount("http://",  bvs_adapter)

        #---TWM Connections
        self.__binance_TWM                             = None
        self.__binance_TWM_StreamQueue                 = set()
        self.__binance_TWM_Connections                 = dict()
        self.__binance_TWM_StreamingData               = dict()
        self.__binance_TWM_LastConnectionGeneration_ns = 0
        self.__binance_TWM_LastExpirationCheck_ns      = 0
        self.__binance_TWM_LastRenewal_intervalN       = 0
        self.__binance_TWM_OverFlowDetected            = False
        self.__binance_TWM_StreamHandlers = {_BINANCE_TWM_STREAMDATATYPE_KLINE:       self.__processTWMStreamMessages_Kline,
                                             _BINANCE_TWM_STREAMDATATYPE_DEPTHUPDATE: self.__processTWMStreamMessages_DepthUpdate,
                                             _BINANCE_TWM_STREAMDATATYPE_AGGTRADES:   self.__processTWMStreamMessages_AggTrade}
        #---Fetch Control
        self.__binance_fetchBlock                            = False
        self.__binance_firstOpenTSSearchRequests             = dict()
        self.__binance_firstOpenTSSearchQueue                = dict()
        self.__binance_firstOpenTSSearchQueue_lastUpdated_ns = 0
        self.__binance_fetchRequests                         = dict()
        self.__binance_fetchRequests_ByStream                = set()
        self.__binance_fetchRequests_SymbolsByPriority       = {0: set(), 1: set(), 2: set()}
        self.__binance_fetchRequests_currentTarget           = None
        self.__binance_fetchRequests_dmCausePause            = False
        self.__binance_fetchTaskHandlers = {('REST',   'kline'):    self.__handleFetchTask_REST_kline,
                                            ('REST',   'depth'):    self.__handleFetchTask_REST_depth,
                                            ('REST',   'aggTrade'): self.__handleFetchTask_REST_aggTrade,
                                            ('VISION', 'kline'):    self.__handleFetchTask_VISION_kline,
                                            ('VISION', 'depth'):    self.__handleFetchTask_VISION_depth,
                                            ('VISION', 'aggTrade'): self.__handleFetchTask_VISION_aggTrade,}

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
        self.ipcA.addFARHandler('getFirstOpenTS',          self.__far_addFirstOpenTSSearchRequest, executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        self.ipcA.addFARHandler('fetchData',               self.__far_addFetchRequestQueue,        executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        self.ipcA.addFARHandler('pauseMarketDataFetch',    self.__far_pauseMarketDataFetch,        executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        self.ipcA.addFARHandler('continueMarketDataFetch', self.__far_continueMarketDataFetch,     executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
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
                #Data Fetching Process
                self.__updateFirstOpenTSSearchQueues()
                self.__processFirstOpenTSSearchRequests()
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
        #[1]: Instances
        conns = self.__binance_TWM_Connections

        #[2]: Stream Data Buffer Check
        if any(conn['buffer'] for conn in conns.values()): return False

        #[3]: Return True If No Hustle Is Needed
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
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Save Binance API Manager Configuration. User Attention Strongly Advised\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"),
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
            #[4-2-1-1]: Save symbol information & prepare local tracker
            marketExchangeInfo_thisSymbol = marketExchangeInfo_Symbols[symbol]
            self.__binance_MarketExchangeInfo_Symbols[symbol] = marketExchangeInfo_thisSymbol

            #[4-2-1-2]: If trading, add to the functional trackers
            if marketExchangeInfo_thisSymbol['status'] == 'TRADING':
                #[4-2-1-2-1]: Streaming Queue
                if symbol not in self.__binance_TWM_StreamingData: 
                    self.__binance_TWM_StreamQueue.add(symbol)

            #[4-2-1-3]: Send FAR to the DataManager for the currency registration
            self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                              functionID     = 'registerCurrency', 
                              functionParams = {'symbol': symbol, 
                                                'info':   marketExchangeInfo_thisSymbol}, 
                              farrHandler    = None)

        #------[4-2-2]: Handle Removed Symbols
        for symbol in symbols_removed:
            #[4-2-2-1]: Market Exchange Info Update
            del self.__binance_MarketExchangeInfo_Symbols[symbol]
            self.__binance_MarketExchangeInfo_Symbols_Set.remove(symbol)

            #[4-2-2-2]: Functional Trackers
            #---[4-2-2-2-1]: First Open TS Search Requests
            if symbol in self.__binance_firstOpenTSSearchRequests:
                del self.__binance_firstOpenTSSearchRequests[symbol]
                if symbol in self.__binance_firstOpenTSSearchQueue: 
                    del self.__binance_firstOpenTSSearchQueue[symbol]
            #---[4-2-2-2-2]: Stream Queue
            if symbol in self.__binance_TWM_StreamQueue:                
                self.__binance_TWM_StreamQueue.remove(symbol)
            
            #[4-2-2-3]: Status Update Announcement
            self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                              functionID     = 'onCurrencyInfoUpdate', 
                              functionParams = {'symbol': symbol, 
                                                'infoUpdates': [{'id': ('status',), 'value': 'REMOVED'}]}, 
                              farrHandler    = None)

        #------[4-2-3]: Check for any changes to the currencies information and respond
        for symbol in symbols_still:
            #[4-2-3-1]: Instances
            currencyInfo_prev = self.__binance_MarketExchangeInfo_Symbols[symbol]
            currencyInfo_new  = marketExchangeInfo_Symbols[symbol]

            #[4-2-3-2]: Information Update
            updates = []
            #---[4-2-3-2-1]: Trading Status
            status_prev = currencyInfo_prev['status']
            status_new  = currencyInfo_new['status']
            if status_prev != status_new:
                #[4-2-3-2-1-1]: Not Trading -> Trading
                if (status_prev != 'TRADING') and (status_new == 'TRADING'):
                    #[4-2-3-2-1-1-1]: Stream Queue
                    if symbol not in self.__binance_TWM_StreamingData: 
                        self.__binance_TWM_StreamQueue.add(symbol)

                #[4-2-3-2-1-2]: Trading -> Not Trading
                if (status_prev == 'TRADING') and (status_new != 'TRADING'):
                    #[4-2-3-2-1-2-1]: First Open TS Search Queue
                    if symbol in self.__binance_firstOpenTSSearchQueue: 
                        del self.__binance_firstOpenTSSearchQueue[symbol]
                    #[4-2-3-2-1-2-2]: Stream Queue
                    if symbol in self.__binance_TWM_StreamQueue:        
                        self.__binance_TWM_StreamQueue.remove(symbol)

                #[4-2-3-2-1-3]: Update Record
                update = {'id':    ('status',),
                          'value': status_new}
                updates.append(update)
                currencyInfo_prev['status'] = status_new

            #---[4-2-3-2-1]: Filters <TO BE IMPLEMENTED>
            for marketFilter in currencyInfo_new['filters']:
                pass

            #---[4-2-3-2-1]: Precisions <TO BE IMPLEMENTED>
            pass

            #[4-2-3-2-3]: Updates Announcement
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
    def __initializeStreamingDataForSymbol(self, symbol):
        #[1]: Streaming Data Initialization
        mei_symbol = self.__binance_MarketExchangeInfo_Symbols[symbol]
        sd = {'connectionID_MAIN':    None,
              'connectionID_EXPIRED': None,
              'pricePrecision':       mei_symbol['pricePrecision'],
              'quantityPrecision':    mei_symbol['quantityPrecision'],
              'quotePrecision':       mei_symbol['quotePrecision'],
              'klines':               {'klines':    dict(), 'waitingFetch': False, 'buffer': [], 'lastStream': None, 'lastInterval': None},
              'depths':               {'depths':    dict(), 'waitingFetch': False, 'buffer': [], 'lastStream': None, 'lastInterval': None, 'lastIntervalSnap': 0, 'dMap_bids': dict(), 'dMap_asks': dict(), 'dMap_bids_plMax': None, 'dMap_asks_plMin': None},
              'aggTrades':            {'aggTrades': dict(), 'waitingFetch': False, 'buffer': [], 'lastStream': None, 'lastInterval': None},
              'updatedTypes':         0b000,
              'lastAnnounced_ns':     0,
              'fetchPriority':        2,
              'subscriptions':        []}
        self.__binance_TWM_StreamingData[symbol] = sd

        #[2]: Subscription From DATAMANAGER
        subscription_DATAMANAGER = {'subscriber':     'DATAMANAGER',
                                    'subscriptionID': None,
                                    'fID_kline':      'onKlineStreamReceival',
                                    'fID_depth':      'onDepthStreamReceival',
                                    'fID_aggTrade':   'onAggTradeStreamReceival',
                                    'closedOnly':     True}
        sd['subscriptions'].append(subscription_DATAMANAGER)

    def __processTWMStreamConnections(self):
        #[1]: Instances
        conns  = self.__binance_TWM_Connections
        sQueue = self.__binance_TWM_StreamQueue

        #[2]: Terminate Expired Connections With Empty CheckList
        connIDs_expired = [connID for connID, conn in conns.items() if conn['status'] == TWMSTATUS_EXPIRED and not conn['terminationCheckList']]
        for connID in connIDs_expired:
            self.__terminateTWMStreamConnection(connectionID = connID)

        #[3]: New Connection Generation
        if _BINANCE_TWM_CONNECTIONGENERATIONINTERVAL_NS <= time.perf_counter_ns()-self.__binance_TWM_LastConnectionGeneration_ns: 
            self.__generateTWMStreamConnection()
            self.__binance_TWM_LastConnectionGeneration_ns = time.perf_counter_ns()

        #[4]: Expiration Checks
        #---[4-1]: By OverFlow (If detected, renew all connections)
        if self.__binance_TWM_OverFlowDetected:
            #[4-1-1]: Logging
            self.__logger(message = f"A TWM Queue Overflow Detected, All Connections Will Be Terminated And Regenerated.",
                          logType = 'Error',
                          color   = 'light_cyan')
            #[4-1-2]: Flag Reset
            self.__binance_TWM_OverFlowDetected = False
            #[4-1-3]: Connections Termination
            connIDs = list(conns)
            symbols = []
            for connID in connIDs:
                symbols.extend(conns[connID]['symbols'])
                self.__terminateTWMStreamConnection(connectionID = connID)
            #[4-1-4]: Connection Queue Update
            sQueue.update(symbols)
            
        #---[4-2]: Periodic Expiration Check & Renewal
        if _BINANCE_TWM_EXPIRATIONCHECKINTERVAL_NS <= time.perf_counter_ns()-self.__binance_TWM_LastExpirationCheck_ns:
            t_current_s         = time.time()
            t_current_intervalN = int(t_current_s/60)
            if self.__binance_TWM_LastRenewal_intervalN < t_current_intervalN:
                for connID, conn in conns.items():
                    #[4-2-2-1]: Connection Conditions Check
                    if conn['status'] != TWMSTATUS_READY:                                       continue
                    if t_current_s-conn['connectionTime'] < _BINANCE_TWM_STREAMRENEWALPERIOD_S: continue
                    #[4-2-2-2]: Expire Connection Check
                    self.__expireTWMStreamConnection(connectionID = connID)
                    #[4-2-2-3]: Timer Update & Logging
                    self.__binance_TWM_LastRenewal_intervalN = t_current_intervalN
                    self.__logger(message = (f"WebSocket Connection Expired For Renewal.\n"
                                             f" * Connection ID: {connID}"),
                                  logType = 'Update', 
                                  color   = 'light_cyan')

            #[4-2-2]: Last Expiration Check Record
            self.__binance_TWM_LastExpirationCheck_ns = time.perf_counter_ns()

    def __generateTWMStreamConnection(self):
        #[1]: Queue Check
        sQueue = self.__binance_TWM_StreamQueue
        if not sQueue: return

        #[1]: Symbols Selection
        meis    = self.__binance_MarketExchangeInfo_Symbols
        symbols = []
        while (len(symbols) < _BINANCE_TWM_NSYMBOLSPERCONN) and sQueue: 
            symbol = sQueue.pop()
            if meis[symbol]['status'] != 'TRADING': continue
            symbols.append(symbol)

        #[2]: Stream Strings
        symbols_lower = [symbol.lower() for symbol in symbols]
        streams = []
        streams.extend([f"{symbol_lower}_perpetual@continuousKline_{KLINTERVAL_STREAM}" for symbol_lower in symbols_lower])
        streams.extend([f"{symbol_lower}@depth"                                         for symbol_lower in symbols_lower])
        streams.extend([f"{symbol_lower}@aggTrade"                                      for symbol_lower in symbols_lower])
        
        #[3]: Socket Start Attempt
        #---[3-1]: Connection Instance
        connectionID = time.time_ns()
        connection = {'connectionName':       None,
                      'connectionID':         connectionID,
                      'connectionTime':       time.time(),
                      'buffer':               deque(),
                      'symbols':              set(symbols),
                      'status':               TWMSTATUS_PREPARING,
                      'terminationCheckList': set()}
        nTries         = 0
        connectionName = None

        #---[3-2]: Connection Attempt
        while nTries < _BINANCE_WEBSOCKETSTREAMCONNECTIONTRIES_MAX:
            nTries += 1
            try:
                connectionName = self.__binance_TWM.start_futures_multiplex_socket(callback = self.__TWM_getStreamReceiverFunction(connection = connection),
                                                                                   streams  = streams,
                                                                                   uid      = str(connectionID))
                if connectionName is not None:
                    break
            except Exception as e:
                self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Generate A TWM Stream Connection. [{nTries}/{_BINANCE_WEBSOCKETSTREAMCONNECTIONTRIES_MAX}]\n",
                                         f" * Error:          {e}\n"
                                         f" * Detailed Trace: {traceback.format_exc()}",
                                         ), 
                              logType = 'Error', 
                              color   = 'light_red')
                time.sleep(_BINANCE_WEBSOCEKTSTREAMCONNECTIONINTERVAL_NS/1e9)

        #---[3-3]: Connection Failure Handling
        if connectionName is None:
            sQueue.update(set(symbols))
            return
        
        #[4]: Upon Successful Connection Generation, Create A Tracker Instance
        #---[4-1]: Connection Name Update
        connection['connectionName'] = connectionName
        self.__binance_TWM_Connections[connectionID] = connection

        #---[4-2]: Streaming Symbol Data Formatting
        sds = self.__binance_TWM_StreamingData
        for symbol in symbols:
            #[4-2-1]: Streaming Data Initialization (If Needed)
            if symbol not in sds: 
                self.__initializeStreamingDataForSymbol(symbol = symbol)
            #[4-2-2]: Streaming Data Connection ID Update
            sd = sds[symbol]
            if sd['connectionID_MAIN'] is not None: #This Should Not Happen, But Placed For An Unexpeceted Logic Flaw
                self.__logger(message = (f"A Symbol With Existing Main WebSocket Connection Detected. Developer Attention Advised.\n",
                                         f" * Symbol:                 {symbol}\n",
                                         f" * Existing Connection ID: {sd['connectionID_MAIN']}\n",
                                         f" * New Connection ID:      {connectionID}",
                                         ), 
                              logType = 'Warning',
                              color   = 'light_red')
            sd['connectionID_MAIN'] = connectionID
            
        #---[4-3]: Connection Status Update
        connection['status'] = TWMSTATUS_READY

        #---[4-4]: Message
        self.__logger(message = (f"WebSocket Connection Generated.\n"
                                 f" * Connection ID:     {connectionID}\n"
                                 f" * Number Of Symbols: {len(connection['symbols'])}"
                                 ), 
                      logType = 'Update', 
                      color   = 'light_green')
            
    def __expireTWMStreamConnection(self, connectionID):
        #[1]: Instances
        sds        = self.__binance_TWM_StreamingData
        connection = self.__binance_TWM_Connections[connectionID]

        #[2]: Status Update
        connection['status'] = TWMSTATUS_EXPIRED

        #[3]: Stream Data Connection ID Update
        for symbol in connection['symbols']:
            sd = sds[symbol]
            #[3-1]: MAIN Connection ID Update (Shoud Originally Be This)
            if sd['connectionID_MAIN'] == connectionID: 
                sd['connectionID_MAIN'] = None
            else:
                self.__logger(message = (f"WebSocket Connection Was Not The Main Connection For A Symbol When Expiring. Ideally This Should Not Have Happened. Developer Attention Advised.\n"
                                         f" * Connection ID: {connectionID}\n"
                                         f" * Symbol:        {symbol}"
                                         ), 
                              logType = 'Warning',
                              color   = 'light_red')

            #[3-2]: EXPIRED Connection ID Update (Should Go Here, And EXPIRED Connection May Not Be Empty If Another Expiration Occurs Before The Last Expiration Is Terminated)
            if sd['connectionID_EXPIRED'] is not None:
                conn_prevExpired_termCL = self.__binance_TWM_Connections[sd['connectionID_EXPIRED']]['terminationCheckList']
                identifier_kline     = (symbol, 'kline')
                identifier_depth     = (symbol, 'depth')
                identifier_aggTrades = (symbol, 'aggTrade')
                if identifier_kline     in conn_prevExpired_termCL: conn_prevExpired_termCL.remove(identifier_kline)
                if identifier_depth     in conn_prevExpired_termCL: conn_prevExpired_termCL.remove(identifier_depth)
                if identifier_aggTrades in conn_prevExpired_termCL: conn_prevExpired_termCL.remove(identifier_aggTrades)
            sd['connectionID_EXPIRED'] = connectionID
            
            #[3-3]: Termination CheckList Update
            connection['terminationCheckList'].update({(symbol, 'kline'), 
                                                       (symbol, 'depth'), 
                                                       (symbol, 'aggTrade')})
            
        #[4]: New Stream Connection Queue Add
        self.__binance_TWM_StreamQueue.update(connection['symbols'])

        #[5]: Console Print
        self.__logger(message = (f"WebSocket Connection Succesfully Expired.\n"
                                 f" * Connection ID:     {connectionID}\n"
                                 f" * Number of Symbols: {len(connection['symbols'])}"
                                 ),
                      logType = 'Update', 
                      color   = 'light_green')

    def __terminateTWMStreamConnection(self, connectionID):
        #[1]: Instances
        sds        = self.__binance_TWM_StreamingData
        connection = self.__binance_TWM_Connections[connectionID]

        #[2]: Socket Stop
        self.__binance_TWM.stop_socket(connection['connectionName'])

        #[3]: Stream Data Connection ID Update
        nSymbols = len(connection['symbols'])
        for symbol in connection['symbols']:
            sd = sds[symbol]
            if   sd['connectionID_MAIN']    == connectionID: sd['connectionID_MAIN']    = None
            elif sd['connectionID_EXPIRED'] == connectionID: sd['connectionID_EXPIRED'] = None

        #[4]: Connection Removal
        del self.__binance_TWM_Connections[connectionID]

        #[5]: Console Print
        self.__logger(message = (f"WebSocket Connection Succesfully Terminated.\n"
                                 f" * Connection ID:     {connectionID}\n"
                                 f" * Number of Symbols: {nSymbols}"
                                 ), 
                      logType = 'Update', 
                      color   = 'light_green')
    
    #---Binance Vision
    def __getBinanceVisionFiles(self, symbol, dataType, range_beg, range_end, firstOnly = False):
        #[1]: Addresses
        url_s3API  = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision/"
        #---[1-1]: Klines
        if dataType == 'kline':
            url_prefix  = f"data/futures/um/daily/klines/{symbol}/1m/"
            name_format = "1m"
        #---[1-2]: Depth
        elif dataType == 'depth':
            url_prefix  = f"data/futures/um/daily/bookDepth/{symbol}/"
            name_format = "bookDepth"
        #---[1-3]: AggTrades
        elif dataType == 'aggTrade':
            url_prefix  = f"data/futures/um/daily/aggTrades/{symbol}/"
            name_format = "aggTrades"
        #---[1-4]: Unexpected
        else:
            return []

        #[2]: Namespace For XML Decryption From S3
        ns = {'s3': 'http://s3.amazonaws.com/doc/2006-03-01/'}

        #[3]: Range Setup
        if firstOnly:
            beg_key = ""
            end_key = ""
        else:
            range_beg_dt = datetime.fromtimestamp(range_beg, tz=timezone.utc) - timedelta(days=1)
            range_end_dt = datetime.fromtimestamp(range_end, tz=timezone.utc)
            range_beg = range_beg_dt.strftime("%Y-%m-%d")
            range_end = range_end_dt.strftime("%Y-%m-%d")
            beg_key = f"{url_prefix}{symbol}-{name_format}-{range_beg}.zip"
            end_key = f"{url_prefix}{symbol}-{name_format}-{range_end}.zip.CHECKSUM"

        #[4]: URLs Collection
        allFiles = set()
        marker   = beg_key
        while True:
            #[4-1]: S3 API Request Parameters
            params = {"prefix": url_prefix,
                      "marker": marker}
                      
            #[4-2]: List Request To S3 Server
            try:
                response = self.__binance_visionSession.get(url    = url_s3API, 
                                                            params = params)
            except Exception as e:
                self.__logger(message = (f"An Unexpected Error Occurred While Requesting Files List From S3 Server.\n"
                                         f" * Symbol:         {symbol}\n"
                                         f" * Data Type:      {dataType}\n"
                                         f" * Error:          {e}\n"
                                         f" * Detailed Trace: {traceback.format_exc()}"
                                         ), 
                              logType = 'Error',
                              color   = 'light_red')
                break
            
            #[4-3]: Status Check
            if response.status_code != 200:
                self.__logger(message = (f"Files List Request To S3 Server Failed While Attempting To Update Binance Vision Availability. User Attention Advised\n"
                                         f" * Symbol:      {symbol}\n"
                                         f" * Data Type:   {dataType}\n"
                                         f" * Status Code: {response.status_code}"
                                         ), 
                              logType = 'Warning',
                              color   = 'light_red')
                break
                
            #[4-4]: Convert HTML/XML to Tree Structure
            root = ET.fromstring(response.text)
            
            #[4-5]: Keys Collection
            contents_list = root.findall('s3:Contents', ns)
            if not contents_list: break
            lastFile    = ""
            reached_end = False
            for contents in contents_list:
                lastFile = contents.find('s3:Key', ns).text
                #[4-5-1]: Beg Check
                if beg_key and lastFile <= beg_key:
                    continue
                #[4-5-2]: End Check
                if end_key and end_key < lastFile:
                    reached_end = True
                    break
                #[4-5-3]: File Collection
                allFiles.add(lastFile)
                #[4-5-4]: First Only Check
                if firstOnly and lastFile.endswith('.CHECKSUM') and lastFile.replace('.CHECKSUM', '') in allFiles:
                    reached_end = True
                    break
            if reached_end:
                break
                    
            #[4-6]: Truncation Check & Marker Update
            is_truncated_elem = root.find('s3:IsTruncated', ns)
            is_truncated = False
            if is_truncated_elem is not None:
                is_truncated = is_truncated_elem.text.lower() == 'true'
            if is_truncated and lastFile:
                marker = lastFile
            else:
                break
                
        #[5]: Filter And Find Those Only With .CHECKSUM
        allFiles_mainWithCheckSum = []
        for file in sorted(list(allFiles)):
            #[5-1]: Check If Is The Main
            if not file.endswith('.zip'):
                continue

            #[5-2]: Check CHECKSUM Existence
            file_checkSum = file + ".CHECKSUM"
            if file_checkSum not in allFiles:
                continue

            #[5-3]: Add To The Filtered List
            allFiles_mainWithCheckSum.append(file)

        #[6]: Return The 
        return allFiles_mainWithCheckSum

    def __downloadBinanceVisionFile(self, file):
        #[1]: Instances
        bv     = self.__binance_visionSession
        logger = self.__logger

        #[2]: URLs
        url_base     = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision/"
        url_zip      = url_base + file
        url_checksum = url_zip + ".CHECKSUM"

        #[3]: Files Download
        try:
            #[3-1]: Download .CHECKSUM File
            response_checkSum = bv.get(url = url_checksum, timeout = 10)
            if response_checkSum.status_code != 200:
                logger(message = (f"A CHECKSUM File Download From Binance Vision Failed.\n"
                                  f" * File:        {url_zip}\n"
                                  f" * Status Code: {response_checkSum.status_code}"
                                  ), 
                       logType = 'Warning', 
                       color   = 'light_red')
                return None

            #[3-2]: Download .zip File
            response_zip = bv.get(url=url_zip, timeout=30)
            if response_zip.status_code != 200:
                logger(message = (f"A ZIP File Download From Binance Vision Failed.\n"
                                  f" * File:        {url_zip}\n"
                                  f" * Status Code: {response_zip.status_code}"
                                  ), 
                       logType = 'Warning', 
                       color   = 'light_red')
                return None
            
            #[3-3]: Extract Data
            hash_expected = response_checkSum.text.strip().split()[0]
            file_zipBytes = response_zip.content

        except Exception as e:
            logger(message = (f"An Unexpeceted Error Occurred While Attempting To Download A File From Binance Vision.\n"
                              f" * File:  {file}\n"
                              f" * Error: {e}\n"
                              f" * Trace: {traceback.format_exc()}"), 
                   logType = 'Error', 
                   color   = 'light_red')
            return None
        
        #[4]: Integrity Check
        try:
            #[4-1]: Get Actual Hash
            hasher = hashlib.sha256()
            hasher.update(file_zipBytes)
            hash_actual = hasher.hexdigest()

            #[4-2]: Check The Hashes
            if hash_expected != hash_actual:
                logger(message = (f"A Data Integrity Test Failed For A File Downloaded From Binance Vision.\n"
                                  f" * Target:        {file}\n"
                                  f" * Expected Hash: {hash_expected}\n"
                                  f" * Actual Hash:   {hash_actual}"), 
                       logType = 'Error', 
                       color   = 'light_red')
                return None
            
        except Exception as e:
            logger(message = (f"An Unexpeceted Error Occurred While Attempting To Verify Integrity Of A File Downloaded From Binance Vision.\n"
                              f" * File:  {file}\n"
                              f" * Error: {e}\n"
                              f" * Trace: {traceback.format_exc()}"), 
                   logType = 'Error', 
                   color   = 'light_red')
            return None

        #[5]: Parsing To Python List
        try:
            data_parsed = []
            with zipfile.ZipFile(io.BytesIO(file_zipBytes)) as z:
                csv_filename = z.namelist()[0]
                with z.open(csv_filename) as csv_file:
                    io_text     = io.TextIOWrapper(csv_file, encoding='utf-8') #Convert To Text
                    csv_reader  = csv.reader(io_text)                          #Parse The Text To List
                    data_parsed = list(csv_reader)                             #Convert To List
            return data_parsed
        
        except Exception as e:
            logger(message = (f"An Unexpeceted Error Occurred While Attempting To Parse A File Downloaded From Binance Vision.\n"
                              f" * File:  {file}\n"
                              f" * Error: {e}\n"
                              f" * Trace: {traceback.format_exc()}"), 
                   logType = 'Error', 
                   color   = 'light_red')
            return None

    #---First Open TS Search
    def __updateFirstOpenTSSearchQueues(self):
        #[1]: Timer Check
        t_current_ns = time.time_ns()
        t_current_s  = int(t_current_ns/1e9)
        if t_current_ns-self.__binance_firstOpenTSSearchQueue_lastUpdated_ns < _BINANCE_FIRSTKLINEOPENTSSEARCHQUEUEUPDATEINTERVAL_NS:
            return
        
        #[2]: Instances
        sReqs   = self.__binance_firstOpenTSSearchRequests
        sQueues = self.__binance_firstOpenTSSearchQueue
        meis    = self.__binance_MarketExchangeInfo_Symbols

        #[3]: Queues Update
        for symbol, requests in sReqs.items():
            #[3-1]: Status Check
            if meis[symbol]['status'] != 'TRADING': continue
            #[3-2]: Queue Add
            for target, request in requests.items():
                if request is None:                     continue
                if t_current_s < request['_waitUntil']: continue
                if symbol not in sQueues: sQueues[symbol] = {target,}
                else:                     sQueues[symbol].add(target)

        #[4]: Timer Update
        self.__binance_firstOpenTSSearchQueue_lastUpdated_ns = t_current_ns

    def __processFirstOpenTSSearchRequests(self):
        #[1]: Instances
        sReqs         = self.__binance_firstOpenTSSearchRequests
        sQueues       = self.__binance_firstOpenTSSearchQueue
        vExecutor     = self.__binance_visionExecutor
        func_gbvf     = self.__getBinanceVisionFiles
        func_dbvf     = self.__downloadBinanceVisionFile
        func_gnitt    = atmEta_Auxillaries.getNextIntervalTickTimestamp
        func_sendFARR = self.ipcA.sendFARR

        #[2]: FirstOpenTS Search
        t_current_s       = int(time.time_ns()/1e9)
        symbols_processed = []
        for symbol in sQueues:
            for target in ('kline', 'depth', 'aggTrade'):
                #[2-2]: Queue Check
                if target not in sQueues[symbol]: continue
                request = sReqs[symbol][target]

                #[2-3]: Files Search
                if request['_status'] == 'pending':
                    request['_status'] = 'GBVF_waiting'
                    vFuture = vExecutor.submit(func_gbvf, 
                                               symbol    = symbol,
                                               dataType  = target,
                                               range_beg = None,
                                               range_end = None,
                                               firstOnly = True)
                    request['_GBVFFuture'] = vFuture
                    continue

                #[2-4]: If Waiting GBVF
                elif request['_status'] == 'GBVF_waiting':
                    #[2-4-1]: Result Arrival Check
                    gbvfFuture = request['_GBVFFuture']
                    if not gbvfFuture.done():
                        continue
                    #[2-4-2]: Result Arrived
                    data = gbvfFuture.result()
                    #---[2-4-2-1]: Failure Handling
                    if data is None:
                        request['_GBVFFuture'] = None
                        request['_status']     = 'pending'
                        request['_waitUntil']  = func_gnitt(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, timestamp = t_current_s, nTicks = 1)
                        symbols_processed.append((symbol, target, False))
                        continue
                    #---[2-4-2-2]: Successful Fetch
                    firstFile = data[0]
                    request['_status'] = 'DBVF_waiting'
                    vFuture = vExecutor.submit(func_dbvf,
                                               file = firstFile)
                    request['_DBVFFuture'] = vFuture
                    continue

                #[2-5]: If Waiting DBVF
                elif request['_status'] == 'DBVF_waiting':
                    #[2-5-1]: Still Waiting
                    dbvfFuture = request['_DBVFFuture']
                    if not dbvfFuture.done():
                        continue
                    #[2-5-2]: Result Arrived
                    data = dbvfFuture.result()
                    #---[2-5-2-1]: Failure Handling
                    if data is None:
                        request['_DBVFFuture'] = None
                        request['_status']     = 'GBVF_waiting'
                        request['_waitUntil']  = func_gnitt(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, timestamp = t_current_s, nTicks = 1)
                        symbols_processed.append((symbol, target, False))
                        continue
                    #---[2-5-2-2]: Successful Fetch
                    if target == 'kline':
                        firstTime_data = int(data[0][0])
                        firstMinute_s = func_gnitt(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, timestamp = int(firstTime_data/1000), nTicks = 0)
                    elif target == 'depth':
                        firstTime_data = data[1][0]
                        firstTime_s    = int(datetime.strptime(firstTime_data, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp())
                        firstMinute_s  = func_gnitt(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, timestamp = firstTime_s, nTicks = 0)
                    elif target == 'aggTrade':
                        firstTime_data = int(data[0][5])
                        firstMinute_s = func_gnitt(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1m, timestamp = int(firstTime_data/1000), nTicks = 0)

                #[2-6]: Finally
                symbols_processed.append((symbol, target, True))
                func_sendFARR(targetProcess  = request['requester'], 
                              functionResult = {'symbol':      symbol, 
                                                'target':      target,
                                                'firstOpenTS': firstMinute_s}, 
                              requestID      = request['requestID'])

        #[3]: Processed Symbols Handling
        self.__handleProcessedFirstOpenTSRequestsAndQueues(symbols_processed = symbols_processed)

    def __handleProcessedFirstOpenTSRequestsAndQueues(self, symbols_processed):
        #[1]: Instances
        sReqs   = self.__binance_firstOpenTSSearchRequests
        sQueues = self.__binance_firstOpenTSSearchQueue

        #[2]: Processed Symbols Handling
        for symbol, target, complete in symbols_processed:
            #[2-1]: Queues
            sQueues[symbol].remove(target)
            if not sQueues[symbol]: del sQueues[symbol]
            #[2-2]: Requests
            if not complete: continue
            sReqs[symbol][target] = None
            if all(req is None for req in sReqs[symbol].values()):
                del sReqs[symbol]

    #---Fetch Processing
    def __addFetchRequest(self, symbol, target, cause, requestParams):
        #[1]: Fetch Type Check
        if target not in ('kline', 'depth', 'aggTrade'):
            return

        #[2]: Cause Check
        if cause not in ('stream', 'dm'):
            return

        #[3]: Fetch Request Tracker Setup (If needed)
        frs = self.__binance_fetchRequests
        if symbol not in frs: frs[symbol] = dict()
        frs_symbol = frs[symbol]
        rID        = (target, cause)

        #[4]: Request Generation
        if rID not in frs_symbol: frs_symbol[rID] = deque()
        newReq = {'cause':                cause,
                  'requestID':            requestParams['requestID'],
                  'fetchTargetRangeType': requestParams['fetchTargetRangeType'],
                  'fetchTargetRanges':    requestParams['fetchTargetRanges'].copy(),
                  '_status':              'pending',
                  '_GBVFFuture':          None,
                  '_GBVFResult':          None,
                  '_tasks':               None}
        frs_symbol[rID].append(newReq)

        #[5]: Symbols Caused By Stream
        if cause == 'stream':
            self.__binance_fetchRequests_ByStream.add(symbol)

        #[6]: Update Fetch Handler Priortization
        sds_subs = self.__binance_TWM_StreamingData
        fr_sbp   = self.__binance_fetchRequests_SymbolsByPriority
        fetchPriority = sds_subs[symbol]['fetchPriority'] if symbol in sds_subs else 2
        for fp, symbols in fr_sbp.items():
            if fp == fetchPriority:   continue
            if symbol not in symbols: continue
            symbols.remove(symbol)
        fr_sbp[fetchPriority].add(symbol)
    
    def __clearFetchRequests(self, symbols = None):
        #[1]: Instances
        frs     = self.__binance_fetchRequests
        frs_bs  = self.__binance_fetchRequests_ByStream
        frs_sbp = self.__binance_fetchRequests_SymbolsByPriority

        #[2]: Target Symbols
        if symbols is None: 
            symbols = list(frs)

        #[3]: Clearing
        for symbol in symbols:
            #[3-1]: Fetch Request
            if symbol in frs:
                del frs[symbol]

            #[3-2]: Symbol Caused By Stream
            frs_bs.discard(symbol)

            #[3-3]: Fetch Prioritization Update
            for symbols_sbp in frs_sbp.values():
                if symbol not in symbols_sbp:
                    continue
                symbols_sbp.remove(symbol)
                break
    
    def __processFetchRequests(self):
        #[1]: First Kline Open TS Search Queue Check (If not empty, do not fetch)
        if self.__binance_firstOpenTSSearchQueue: 
            return

        #[2]: Target Selection (From the Priority 0 -> 2, First Detected Symbol)
        frs_sbp     = self.__binance_fetchRequests_SymbolsByPriority
        frs_bs      = self.__binance_fetchRequests_ByStream
        fetchTarget = None
        #---[2-1]: Give Major Priority To Those With Requests Caused By Stream
        if frs_bs:
            for priority in (0, 1, 2):
                symbols = frs_sbp[priority] & frs_bs
                for symbol in symbols:
                    fetchTarget = (symbol, priority)
                    break
                if fetchTarget is not None:
                    break
        #---[2-2]: Normal Target Selection
        if fetchTarget is None:
            for priority in (0, 1, 2):
                symbols = frs_sbp[priority]
                for symbol in symbols:
                    fetchTarget = (symbol, priority)
                    break
                if fetchTarget is not None:
                    break
        #---[2-3]: If No Target Exists, Return 
        if fetchTarget is None:
            return

        #[3]: Target Process
        symbol, priority = fetchTarget
        self.__processSymbolFetchRequests(symbol = symbol)

        #[4]: Cleared Fetch Requests Removal
        frs        = self.__binance_fetchRequests
        frs_symbol = frs[symbol]
        #---[4-1]: If There Still Exists Any Fetch Requests For The Symbol, Check For Any Stream Caused Fetch Requests And Remove From The Set If None Is Found.
        if frs_symbol:
            if not any(cause == 'stream' for target, cause in frs_symbol):
                frs_bs.discard(symbol)
        #---[4-2]: If There Still Exists No Fetch Requests For The Symbol, Completely Remove It.
        else:
            del frs[symbol]
            frs_sbp[priority].remove(symbol)
            frs_bs.discard(symbol)
    
    """ #Kline Structure
    REST API: fetchedKlines[n] = ([0]: t_open, 
                                  [1]: p_open, 
                                  [2]: p_high, 
                                  [3]: p_low, 
                                  [4]: p_close, 
                                  [5]: baseAssetVolume, 
                                  [6]: t_close, 
                                  [7]: quoteAssetVolume, 
                                  [8]: nTrades, 
                                  [9]: baseAssetVolume_takerBuy, 
                                  [10]: quoteAssetVolume_takerBuy, 
                                  [11]: ignore
                                  )
    VISION: fetchedKlines[n] = ([0]: t_open, 
                                [1]: p_open, 
                                [2]: p_high, 
                                [3]: p_low, 
                                [4]: p_close, 
                                [5]: baseAssetVolume, 
                                [6]: t_close, 
                                [7]: quoteAssetVolume, 
                                [8]: nTrades, 
                                [9]: baseAssetVolume_takerBuy, 
                                [10]: quoteAssetVolume_takerBuy, 
                                [11]: ignore
                                )
    STREAM: buffer[n] = ([0]:  openTS,
                         [1]:  closeTS,
                         [2]:  openPrice,
                         [3]:  highPrice,
                         [4]:  lowPrice,
                         [5]:  closePrice,
                         [6]:  nTrades,
                         [7]:  baseAssetVolume,
                         [8]:  quoteAssetVolume,
                         [9]:  baseAssetVolume_takerBuy,
                         [10]: quoteAssetVolume_takerBuy,
                         [11]: closed,
                         [12]: klineType
                         )
    --->
    SYSTEM: fetchedKlines_formatted[n] = ([0]:  openTS, 
                                          [1]:  closeTS, 
                                          [2]:  openPrice, 
                                          [3]:  highPrice, 
                                          [4]:  lowPrice, 
                                          [5]:  closePrice, 
                                          [6]:  nTrades, 
                                          [7]:  baseAssetVolume, 
                                          [8]:  quoteAssetVolume, 
                                          [9]:  baseAssetVolume_takerBuy, 
                                          [10]: quoteAssetVolume_takerBuy, 
                                          [11]: closed, 
                                          [12]: klineType
                                          )
    """
    """ #Depth Structure
    REST API: fetchedDepth[n] = (['lastUpdateID']: Last Updated ID, 
                                 ['E']:            Event Time, 
                                 ['T']:            Transaction Time, 
                                 ['bids']:         [[Price, Quantity],],
                                 ['asks']:         [[Price, Quantity],],
                                 )
    VISION: fetchedDepth[n(1~)] = ([0]: timestamp, 
                                   [1]: percentage, (-5, -4, -3, -2, -1, -0.2, 0.2, 1, 2, 3, 4, 5)
                                   [2]: depth, 
                                   [3]: notional
                                   )
    STREAM: buffer[n] = ([0]: aggTID,
                         [1]: tradePrice,
                         [2]: quantity,
                         [3]: maker,
                         [4]: nTrades,
                         [5]: tradeTime
                        )
    --->
    SYSTEM: fetchedDepth_formatted[n] = ([0]:  openTS, 
                                         [1]:  closeTS,
                                         [2]:  bids5 (-4.0% ~ -5.0%)
                                         [3]:  bids4 (-3.0% ~ -4.0%)
                                         [4]:  bids3 (-2.0% ~ -3.0%)
                                         [5]:  bids2 (-1.0% ~ -2.0%)
                                         [6]:  bids1 (-0.2% ~ -1.0%)
                                         [7]:  bids0 ( 0.0% ~ -0.2%)
                                         [8]:  asks0 ( 0.0% ~  0.2%)
                                         [9]:  asks1 ( 0.2% ~  1.0%)
                                         [10]: asks2 ( 1.0% ~  2.0%)
                                         [11]: asks3 ( 2.0% ~  3.0%)
                                         [12]: asks4 ( 3.0% ~  4.0%)
                                         [13]: asks5 ( 4.0% ~  5.0%)
                                         [14]: closed,
                                         [15]: depthType
                                        )
    """
    """ #AggTrade Structure
    REST API: fetchedAggTrades[n] = {['a']: Aggregate Trade ID, 
                                     ['p']: Price, 
                                     ['q']: Quantity, 
                                     ['f']: First Trade ID, 
                                     ['l']: Last Trade ID, 
                                     ['T']: Timestamp, 
                                     ['m']: Was The Buyer The Maker? ('SELL' if True, 'BUY' otherwise)
                                     }
    VISION: fetchedAggTrades[n] = ([0]: Aggregate Trade ID,
                                   [1]: Price,
                                   [2]: Quantity,
                                   [3]: First Trade ID,
                                   [4]: Last Trade ID,
                                   [5]: Timestamp,
                                   [6]: Was The Buyer The Maker?  ('SELL' if True, 'BUY' otherwise)
                                   )
    STREAM: buffer[n] = ([0]: aggTID,
                         [1]: tradePrice,
                         [2]: quantity,
                         [3]: maker,
                         [4]: nTrades,
                         [5]: tradeTime
                        )
    --->
    SYSTEM: fetchedAggTrades_formatted[n] = ([0]: openTS,
                                             [1]: closeTS, 
                                             [2]: quantity_buy,
                                             [3]: quantity_sell,
                                             [4]: nTrades_buy,
                                             [5]: nTrades_sell,
                                             [6]: notional_buy,
                                             [7]: notional_sell,
                                             [8]: closed,
                                             [9]: aggTradeType
                                             )
    """
    def __processSymbolFetchRequests(self, symbol):
        #[1]: Instances
        frs       = self.__binance_fetchRequests
        vExecutor = self.__binance_visionExecutor
        func_gbvf = self.__getBinanceVisionFiles

        #[2]: Fetch Request Check (Prioritize Stream Cause)
        frs_symbol = frs[symbol]
        fr         = None
        for cause in ('stream', 'dm'):
            for target in ('kline', 'depth', 'aggTrade'):
                rID = (target, cause)
                if rID in frs_symbol:
                    fr = frs_symbol[rID][0]
                    break
            if fr is not None:
                break
        if fr is None:
            return
        
        #[3]: Fetch Target Change Handling
        ct = self.__binance_fetchRequests_currentTarget
        #---[3-1]: Previous Target Thread Pool Tasks Cancelation
        if ct is not None and ct != (symbol, target, cause):
            fr_prev        = frs[ct[0]][(ct[1], ct[2])][0]
            fr_prev_status = fr_prev['_status']
            #[3-1-1]: If Is In 'GBVF_waiting' State, Cancel Thread Pool Task If Possible And Bring Back To Pending State
            if fr_prev_status == 'GBVF_waiting':
                fr_prev['_GBVFFuture'].cancel()
                fr_prev['_GBVFFuture'] = None
                fr_prev['_status']     = 'pending'
            #[3-1-2]: If Is In 'handleTasks' State, Cancel Thread Pool Tasks If Possible And Bring Back To Pending State
            elif fr_prev_status == 'handleTasks':
                for task in fr_prev['_tasks']:
                    if task['source'] != 'VISION':        continue
                    if task['status'] != 'waitingResult': continue
                    task['future'].cancel()
                    task['future'] = None
                    task['status'] = 'pending'
        #---[3-2]: Current Fetch Target Update
        self.__binance_fetchRequests_currentTarget = (symbol, target, cause)

        #[4]: If Pending, Check If There Is A Need To Check Data Availability From Binance Vision, And Submit Check Task If Do
        if fr['_status'] == 'pending':
            #[4-1]: If The Fetch Target Range Type Is Timestamp, Check On Binance Vision
            if fr['fetchTargetRangeType'] == 'timestamp':
                vc_range_beg = float('inf')
                vc_range_end = float('-inf')
                for ftRange_beg, ftRange_end in fr['fetchTargetRanges']:
                    if ftRange_beg < vc_range_beg: vc_range_beg = ftRange_beg
                    if vc_range_end < ftRange_end: vc_range_end = ftRange_end
                vFuture = vExecutor.submit(func_gbvf, 
                                           symbol    = symbol,
                                           dataType  = target,
                                           range_beg = vc_range_beg,
                                           range_end = vc_range_end,
                                           firstOnly = False)
                fr['_GBVFFuture'] = vFuture
                fr['_status']     = 'GBVF_waiting'
                return
            #[4-2]: If Not, Move Directly To Tasks Generation
            else:
                fr['_status'] = 'generateTasks'

        #[5]: Waiting GBVF Result
        elif fr['_status'] == 'GBVF_waiting':
            #[5-1]: Result Arrival Check
            gbvfFuture = fr['_GBVFFuture']
            if not gbvfFuture.done():
                return
            #[5-2]: Result Arrived
            data = gbvfFuture.result()
            #---[5-2-1]: Fetch Failed, Go Back To The Pending State
            if data is None:
                fr['_GBVFFuture'] = None
                fr['_status']     = 'pending'
                return
            #---[5-2-2]: Successful Fetch, Generate Fetch Tasks
            fr['_GBVFFuture'] = None
            fr['_GBVFResult'] = data
            fr['_status']     = 'generateTasks'
        
        #[6]: Task Generation
        if fr['_status'] == 'generateTasks':
            fr['_tasks']      = self.__generateFetchTasks(target               = target,
                                                          visionFiles          = fr['_GBVFResult'],
                                                          fetchTargetRangeType = fr['fetchTargetRangeType'],
                                                          fetchTargetRanges    = fr['fetchTargetRanges'])
            fr['_GBVFResult'] = None
            fr['_status']     = 'handleTasks'
    
        #[7]: Task Handling & Completion Check
        if fr['_status'] == 'handleTasks':
            tasks            = fr['_tasks']
            tasks_incomplete = [task for task in tasks if task['status'] != 'complete']
            #[7-1]: Fetch Task Hadling
            nTasks         = len(tasks)
            nCompleteTasks = nTasks-len(tasks_incomplete)
            nHandlingTasks = sum(1 for task in tasks_incomplete if task['status'] != 'pending')
            for task in tasks_incomplete:
                #[7-1-1]: Handling Limit Check
                task_status_prev = task['status']
                if (task_status_prev == 'pending') and (100 <= nHandlingTasks):
                    continue
                #[7-1-2]: Task Handling
                self.__binance_fetchTaskHandlers[(task['source'], target)](symbol           = symbol,
                                                                           cause            = cause,
                                                                           fetchTask        = task, 
                                                                           isLastCompletion = (nTasks == nCompleteTasks+1),
                                                                           requestID        = fr['requestID'])
                #[7-1-3]: Task Status Update Handling
                task_status = task['status']
                if task_status_prev == 'pending' and task_status != 'pending':
                    nHandlingTasks += 1
                elif task_status_prev != 'pending' and task_status == 'pending':
                    nHandlingTasks -= 1
                if task_status == 'complete':
                    nCompleteTasks += 1
                    nHandlingTasks -= 1

            #[7-2]: Request Completion Check & Handling
            if nTasks == nCompleteTasks:
                #[7-2-1]: Request Clearing
                frs_symbol[rID].popleft()
                #[7-2-2]: Stream Flag Update
                if cause == 'stream':
                    if not frs_symbol[rID]:
                        self.__binance_TWM_StreamingData[symbol][f'{target}s']['waitingFetch'] = False
                #[7-2-3]: Empty RID Clearing
                if not frs_symbol[rID]: del frs_symbol[rID]
                #[7-2-4]: Current Target Update
                self.__binance_fetchRequests_currentTarget = None

    def __generateFetchTasks(self, target, visionFiles, fetchTargetRangeType, fetchTargetRanges):
        #[1]: Vision Files Range Check
        func_gnitt  = atmEta_Auxillaries.getNextIntervalTickTimestamp
        interval_1d = atmEta_Auxillaries.KLINE_INTERVAL_ID_1d
        visionFileRanges = []
        if visionFiles is not None:
            for file in visionFiles:
                #[1-1]: Scan And Extract Date String From The File Name
                match = re.search(r'(\d{4}-\d{2}-\d{2})\.zip$', file)
                if match is None: continue
                #[1-2]: Construct Timestamp Range The File Represents
                date_str = match.group(1)
                date_dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                ts_beg = int(date_dt.timestamp())
                ts_end = func_gnitt(intervalID = interval_1d, timestamp = ts_beg, mrktReg = None, nTicks = 1)-1
                #[1-3]: Collect Range Data
                visionFileRange = (file, (ts_beg, ts_end))
                visionFileRanges.append(visionFileRange)

        #[2]: Case Dependent Tasks Generation
        tasks = []
        #---[2-1]: Kline
        if target == 'kline':
            #[2-1-1]: Timestamp Ranged Fetch (VISION & REST) (Cause: DM + Stream)
            if fetchTargetRangeType == 'timestamp':
                #[2-1-1-1]: Generate DBVF (Download Binance Vision File) Tasks
                dbvfTasks, remainingFTRs = self.__generateDBVFTasks(visionFileRanges = visionFileRanges, fetchTargetRanges = fetchTargetRanges)
                for dbvfTask in dbvfTasks:
                    task = {'source':      'VISION',
                            'status':      'pending',
                            'fetchTarget': dbvfTask,
                            'future':      None,
                            'data':        None}
                    tasks.append(task)
                #[2-1-1-2]: Generate REST Tasks (Cause: DM + Stream)
                for ftr in remainingFTRs:
                    task = {'source':      'REST',
                            'status':      'pending',
                            'fetchTarget': ftr,
                            'data':        None}
                    tasks.append(task)

        #---[2-2]: Depth
        elif target == 'depth':
            #[2-2-1]: Timestamp Ranged Fetch (VISION) (Cause: DM Only)
            if fetchTargetRangeType == 'timestamp':
                #[2-2-1-1]: Generate DBVF (Download Binance Vision File) Tasks
                dbvfTasks, remainingFTRs = self.__generateDBVFTasks(visionFileRanges = visionFileRanges, fetchTargetRanges = fetchTargetRanges)
                for dbvfTask in dbvfTasks:
                    task = {'source':      'VISION',
                            'status':      'pending',
                            'fetchTarget': dbvfTask,
                            'future':      None,
                            'data':        None}
                    tasks.append(task)
                #[2-2-1-2]: Generate Dummy Filling Tasks
                for ftr in remainingFTRs:
                    task = {'source':      'VISION',
                            'status':      'fetched',
                            'fetchTarget': (None, ftr),
                            'data':        []}
                    tasks.append(task)

            #[2-2-1]: Snapshot Fetch (REST) (Cause: Stream Only)
            elif fetchTargetRangeType == 'snapshot':
                task = {'source':      'REST',
                        'status':      'pending',
                        'fetchTarget': None,
                        'data':        None}
                tasks.append(task)

        #---[2-3]: AggTrade
        elif target == 'aggTrade':
            #[2-3-1]: Timestamp Ranged Fetch (VISION & REST) (Cause: DM Only)
            if fetchTargetRangeType == 'timestamp':
                #[2-3-1-1]: Generate DBVF (Download Binance Vision File) Tasks
                dbvfTasks, remainingFTRs = self.__generateDBVFTasks(visionFileRanges = visionFileRanges, fetchTargetRanges = fetchTargetRanges)
                for dbvfTask in dbvfTasks:
                    task = {'source':      'VISION',
                            'status':      'pending',
                            'fetchTarget': dbvfTask,
                            'future':      None,
                            'data':        None}
                    tasks.append(task)
                #[2-3-1-2]: Generate Dummy Filling Tasks
                for ftr in remainingFTRs:
                    task = {'source':      'VISION',
                            'status':      'fetched',
                            'fetchTarget': (None, ftr),
                            'data':        []}
                    tasks.append(task)

            #[2-3-2]: AggTID Ranged Fetch (REST) (Cause: Stream Only)
            elif fetchTargetRangeType == 'timestampBeg_aggTIDEnd':
                task = {'source':      'REST',
                        'status':      'pending',
                        'fetchTarget': ('timestampBeg_aggTIDEnd', list(fetchTargetRanges[0])),
                        'data':        []}
                tasks.append(task)

            #[2-3-3]: AggTID Ranged Fetch (REST) (Cause: Stream Only)
            elif fetchTargetRangeType == 'aggTID':
                task = {'source':      'REST',
                        'status':      'pending',
                        'fetchTarget': ('aggTID', list(fetchTargetRanges[0])),
                        'data':        []}
                tasks.append(task)

        #[3]: Return Result
        return tasks

    def __generateDBVFTasks(self, visionFileRanges, fetchTargetRanges):
        #[1]: Data Preparation
        dbvfTasks         = []
        remainingFTRs_raw = []
        remainingFTRs     = []
        vFiles = {ts_beg: (file, ts_end) for file, (ts_beg, ts_end) in visionFileRanges}

        #[2]: Instances
        func_gnitt  = atmEta_Auxillaries.getNextIntervalTickTimestamp
        interval_1d = atmEta_Auxillaries.KLINE_INTERVAL_ID_1d

        #[3]: Target Range Daily Chunking & Distribution
        for range_beg, range_end in fetchTargetRanges:
            ts_current = range_beg
            while ts_current <= range_end:
                #[3-1]: Get Current Daily Timestamp Range
                ts_daily_beg = func_gnitt(intervalID = interval_1d, timestamp = ts_current, mrktReg = None, nTicks = 0)
                ts_daily_end = func_gnitt(intervalID = interval_1d, timestamp = ts_current, mrktReg = None, nTicks = 1)-1

                #[3-2]: Chunk Range
                chunk_beg = ts_current
                chunk_end = min(range_end, ts_daily_end)

                #[3-3]: Task Generation
                #---[3-3-1]: Corresponding Data Exists On Vision
                if ts_daily_beg in vFiles:
                    file, ts_end = vFiles[ts_daily_beg]
                    dbvfTasks.append((file, [chunk_beg, min(chunk_end, ts_end)]))
                #---[3-3-2]: Corresponding Data Does Not Exists On Vision
                else:
                    remainingFTRs_raw.append([chunk_beg, chunk_end])

                #[3-4]: Move To Next Daily Tick
                ts_current = ts_daily_end + 1

        #[4]: Remaining FTRs (REST) Merging
        for ftr in remainingFTRs_raw:
            if not remainingFTRs:
                remainingFTRs.append(ftr)
                continue
            ftr_prev = remainingFTRs[-1]
            if ftr[0] == ftr_prev[1]+1:
                ftr_prev[1] = ftr[1]
            else:
                remainingFTRs.append(ftr)

        #[5]: Return Result
        return dbvfTasks, remainingFTRs
    
    def __handleFetchTask_REST_kline(self, symbol, cause, fetchTask, isLastCompletion, requestID):
        #[1]: Instances
        func_gnitt = atmEta_Auxillaries.getNextIntervalTickTimestamp

        #[2]: pending -> Fetch Depth Snapshot From REST
        if fetchTask['status'] == 'pending':
            #[2-1]: Fetch Block Check
            if self.__binance_fetchBlock:
                return
            
            #[2-2]: Effective Fetch Target Range
            ftr = fetchTask['fetchTarget']
            ftr_end_max = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, 
                                                                          timestamp  = ftr[0], 
                                                                          mrktReg    = None,
                                                                          nTicks     = 1000)-1
            ftr_eff = (ftr[0], min(ftr[1], ftr_end_max))

            #[2-3]: API Rate Limit Check
            #---[2-3-1]: Expected Number of Klines
            nKlines_expected = (ftr_eff[1]-ftr_eff[0])//KLINTERVAL_S+1
            if   (  1 <= nKlines_expected) and (nKlines_expected <   100): req_weight =  1; fetchLimit = 99
            elif (100 <= nKlines_expected) and (nKlines_expected <   500): req_weight =  2; fetchLimit = 499
            elif (500 <= nKlines_expected) and (nKlines_expected <= 1000): req_weight =  5; fetchLimit = 1000
            else:                                                          req_weight = 10; fetchLimit = 1500
            #---[2-3-2]: API Rate Limit Check
            if not self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, 
                                            weight    = req_weight,
                                            extraOnly = True,
                                            apply     = True):
                self.__binance_fetchBlock = True
                return
        
            #[2-4]: Fetch Attempt & Save Data
            try:
                fetchedKlines = self.__binance_client_default.futures_historical_klines(symbol        = symbol, 
                                                                                        interval      = KLINTERVAL_CLIENT, 
                                                                                        start_str     = ftr_eff[0]*1000, 
                                                                                        end_str       = ftr_eff[1]*1000, 
                                                                                        limit         = fetchLimit, 
                                                                                        verifyFirstTS = False)
                fetchTask['data'] = (ftr_eff, fetchedKlines)
            except Exception as e:
                self.__binance_fetchBlock = True
                self.__logger(message = (f"An Unexpected Error Ocurred While Attempting To Fetch Klines.\n"
                                        f" * Symbol:         {symbol}\n"
                                        f" * Cause:          {cause}\n"
                                        f" * Error:          {e}\n"
                                        f" * Detailed Trace: {traceback.format_exc()}"
                                        ), 
                            logType = 'Warning', 
                            color   = 'light_red')
                return
            
            #[2-5]: Fetch Target Update
            if not (ftr[0] == ftr_eff[0] and ftr[1] == ftr_eff[1]): fetchTask['fetchTarget'] = (ftr_eff[1]+1, ftr[1])
            else:                                                   fetchTask['fetchTarget'] = None
            
            #[2-6]: Status Update
            fetchTask['status'] = 'fetched'

        #[3]: fetched -> Process Fetched Data
        if fetchTask['status'] == 'fetched':
            #[3-1]: Instances
            fetchedRange, fetchedKlines = fetchTask['data']
            func_gnitt = atmEta_Auxillaries.getNextIntervalTickTimestamp

            #[3-2]: Expected Fetched Klines Timestamps
            efkts_expected = atmEta_Auxillaries.getTimestampList_byRange(intervalID        = KLINTERVAL, 
                                                                         mrktReg           = None, 
                                                                         timestamp_beg     = fetchedRange[0], 
                                                                         timestamp_end     = fetchedRange[1], 
                                                                         lastTickInclusive = True)

            #[3-3]: Format Klines 
            fetchedKlines_dict      = {int(kl[0]//1000): kl for kl in fetchedKlines}
            fetchedKlines_formatted = []
            #---[3-3-1]: Expected Klines
            for efkt in efkts_expected:
                kl_raw = fetchedKlines_dict.get(efkt, None)
                #[3-3-1-1]: Expected Not Fetched - Fill With Dummy Klines
                if kl_raw is None:
                    kl_dummy = (efkt, 
                                func_gnitt(intervalID = KLINTERVAL, 
                                           timestamp  = efkt, 
                                           mrktReg    = None, 
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
                                True,
                                _FORMATTEDDATATYPE_DUMMY)
                    fetchedKlines_formatted.append(kl_dummy)
                    self.__logger(message = (f"An Expected Kline Was Not Fetched. The Corresponding Data Will Be Filled With A Dummy Kline, But An User Attention Is Advised.\n"
                                             f" * Symbol:    {symbol}\n"
                                             f" * Cause:     {cause}\n"
                                             f" * Timestamp: {efkt}"
                                            ), 
                                    logType = 'Warning', 
                                    color   = 'light_magenta')
                #[3-3-1-2]: Expected Fetched - Reformat And Save
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
                    kl_formatted = (efkt,
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
                                    True,
                                    _FORMATTEDDATATYPE_FETCHED)
                    fetchedKlines_formatted.append(kl_formatted)
                    del fetchedKlines_dict[efkt]
            #---[3-3-2]: Unexpected Klines
            if fetchedKlines_dict:
                for ts_unexpected, kl_unexpected in fetchedKlines_dict.items():
                    self.__logger(message = (f"Unexpected Kline Detected. It will be Disposed, But An User Attention Is Advised"
                                             f" * Symbol:    {symbol}\n"
                                             f" * Cause:     {cause}\n"
                                             f" * Timestamp: {ts_unexpected}"
                                             f" * Kline:     {kl_unexpected}"
                                            ), 
                                    logType = 'Warning',
                                    color   = 'red')
                    
            #[3-4]: Formatted Data Save
            fetchTask['data']   = fetchedKlines_formatted
            fetchTask['status'] = 'formatted'

        #[4]: formatted -> Dispatch Data
        if fetchTask['status'] == 'formatted':
            #[4-1]: Formatted Data
            fetchedKlines_formatted = fetchTask['data']

            #[4-2]: Stream Cause
            if cause == 'stream':
                #[4-2-1]: Buffer Insertion Position Search
                sd_klines_buffer = self.__binance_TWM_StreamingData[symbol]['klines']['buffer']
                idx_insertion    = len(sd_klines_buffer)
                kl_fs_lastOpenTS = fetchedKlines_formatted[-1][KLINDEX_OPENTIME]
                for kl_b_idx, kl_b in enumerate(sd_klines_buffer):
                    if kl_fs_lastOpenTS < kl_b[0]:
                        idx_insertion = kl_b_idx
                        break
                #[4-2-2]: Buffer Insertion
                sd_klines_buffer[idx_insertion:idx_insertion] = fetchedKlines_formatted

            #[4-3]: DM Cause
            elif cause == 'dm':
                #[4-3-1]: DM Cause Dispatch Block Check
                if self.__binance_fetchRequests_dmCausePause: 
                    return
                #[4-3-2]: Dispatch
                isComplete     = (fetchTask['fetchTarget'] is None and isLastCompletion)
                fResult_status = 'complete' if isComplete else 'fetching'
                self.ipcA.sendFARR(targetProcess  = 'DATAMANAGER', 
                                   functionResult = {'target':       'kline',
                                                     'fetchedRange': [fetchedKlines_formatted[0][0], fetchedKlines_formatted[-1][1]], 
                                                     'status':       fResult_status, 
                                                     'data':         fetchedKlines_formatted}, 
                                   requestID      = requestID, 
                                   complete       = isComplete)

            #[4-4]: Fetch Continuation | Fetch Task Completion Check
            if fetchTask['fetchTarget'] is not None: fetchTask['status'] = 'pending'
            else:                                    fetchTask['status'] = 'complete'

    def __handleFetchTask_REST_depth(self, symbol, cause, fetchTask, isLastCompletion, requestID):
        #[1]: Instances
        task_status = fetchTask['status']
        func_gnitt  = atmEta_Auxillaries.getNextIntervalTickTimestamp

        #[2]: pending -> Fetch Depth Snapshot From REST
        if task_status == 'pending':
            #[2-1]: Fetch Block Check
            if self.__binance_fetchBlock:
                return
            
            #[2-2]: API Rate Limit Check
            if not self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 20, extraOnly = True, apply = True, printUpdated = True):
                return
        
            #[2-3]: Fetch Attempt & Save Data
            try: 
                ob_fetched = self.__binance_client_default.futures_order_book(symbol = symbol, limit = 1000)
                fetchTask['data'] = ob_fetched
            except Exception as e:
                self.__binance_fetchBlock = True
                self.__logger(message = (f"An Unexpected Error Ocurred While Attempting To Fetch Depth Snapshot.\n"
                                        f" * Symbol:         {symbol}\n"
                                        f" * Cause:          {cause}\n"
                                        f" * Error:          {e}\n"
                                        f" * Detailed Trace: {traceback.format_exc()}"
                                        ), 
                            logType = 'Warning', 
                            color   = 'light_red')
                return
            
            #[2-4]: Status Update
            fetchTask['status'] = 'fetched'

        #[3]: fetched -> Process Fetched Data
        if task_status == 'fetched':
            #[3-1]: Instances
            sd_symbol         = self.__binance_TWM_StreamingData[symbol]
            sd_depths         = sd_symbol['depths']
            sd_quotePrecision = sd_symbol['quotePrecision']
            sd_pricePrecision = sd_symbol['pricePrecision']
            sd_depths_depths  = sd_depths['depths']
            sd_depths_buffer  = sd_depths['buffer']
            ob_fetched        = fetchTask['data']

            #[3-2]: Buffer Check
            if not sd_depths_buffer:
                return

            #[3-3]: Buffer Filtering
            ob_fetched_lastUID           = ob_fetched['lastUpdateId']
            sd_depths_buffer_valid       = deque()
            sd_depths_buffer_lastUID     = None
            sd_depths_buffer_abnormality = None
            #---[3-3-1]: Valid Contents Check
            for depth_base in sd_depths_buffer:
                #[3-3-1-1]: Unpack Base Data
                (db_intervalTS, 
                 db_firstUID, 
                 db_finalUID, 
                 db_finalUID_lastStream, 
                 db_bids, 
                 db_asks) = depth_base
                
                #[3-3-1-2]: Discard Any Contents That Are Older Than The Snapshot
                if db_finalUID < ob_fetched_lastUID:
                    continue 

                #[3-3-1-3]: The First Content (Check Skip)
                if sd_depths_buffer_lastUID is None:
                    if ob_fetched_lastUID < db_firstUID:
                        sd_depths_buffer_abnormality = 'Skip'
                        break

                #[3-3-1-4]: The Contents Afterwards Must Satisfy Continuity
                elif db_finalUID_lastStream != sd_depths_buffer_lastUID:
                    sd_depths_buffer_abnormality = 'Discontinuity'
                    break

                #[3-3-1-5]: Valid Buffer & Last Final UID Update
                sd_depths_buffer_valid.append(depth_base)
                sd_depths_buffer_lastUID = db_finalUID

            #---[3-3-2]: Empty Valid Buffer Handling
            if not sd_depths_buffer_valid:
                return

            #---[3-3-3]: Buffer Abnormality Handling
            if sd_depths_buffer_abnormality is not None:
                #[3-3-3-1]: If Discontinuity, Clear The Buffer
                if sd_depths_buffer_abnormality == 'Discontinuity':
                    sd_depths_buffer.clear()
                #[3-3-3-2]: Go Back To 'pending' Status To Fetch Again
                fetchTask['status'] = 'pending'
                fetchTask['data']   = None
                #[3-3-3-3]: Log and Exit
                self.__logger(message = (f"Buffer {sd_depths_buffer_abnormality} Detected While Processing A Depth Snapshot Fetch. It Will Be Re-Tried Once Buffer Is Filled.\n"
                                        f" * Symbol: {symbol}"
                                        ),
                            logType = 'Update',
                            color   = 'light_magenta')
                return
            
            #[3-4]: Handle Previous Interval & Gap Filling
            intervalTS   = sd_depths_buffer_valid[0][0]
            lastInterval = sd_depths['lastInterval']
            if lastInterval is not None:
                li_openTS = lastInterval[DEPTHINDEX_OPENTIME]
                if li_openTS < intervalTS:
                    #[3-4-1]: Record The Last Interval As Closed And Save To The Announcement Buffer
                    lastInterval[DEPTHINDEX_CLOSED] = True
                    lastInterval[DEPTHINDEX_SOURCE] = _FORMATTEDDATATYPE_INCOMPLETE
                    sd_depths_depths[li_openTS] = tuple(lastInterval)

                    #[3-4-2]: Fill In Any Gaps With Dummy Depths Interval Data
                    di_openTS = func_gnitt(intervalID = KLINTERVAL, timestamp = li_openTS, mrktReg = None, nTicks = 1)
                    while di_openTS < intervalTS:
                        di_openTS_next = func_gnitt(intervalID = KLINTERVAL, timestamp = di_openTS, mrktReg = None, nTicks = 1)
                        dummyInterval = (di_openTS,              #[0]:  openTS
                                        di_openTS_next-1,        #[1]:  closeTS
                                        None,                    #[2]:  bids5
                                        None,                    #[3]:  bids4
                                        None,                    #[4]:  bids3
                                        None,                    #[5]:  bids2
                                        None,                    #[6]:  bids1
                                        None,                    #[7]:  bids0
                                        None,                    #[8]:  asks0
                                        None,                    #[9]:  asks1
                                        None,                    #[10]: asks2
                                        None,                    #[11]: asks3
                                        None,                    #[12]: asks4
                                        None,                    #[13]: asks5
                                        True,                    #[14]: closed
                                        _FORMATTEDDATATYPE_DUMMY #[15]: depthType
                                        )
                        sd_depths_depths[di_openTS] = dummyInterval
                        di_openTS = di_openTS_next

            #[3-5]: Depth Map Update
            dMap_bids = sd_depths['dMap_bids']
            dMap_asks = sd_depths['dMap_asks']
            dMap_bids.clear()
            dMap_asks.clear()
            for pl_str, qt_str in ob_fetched['bids']:
                dMap_bids[pl_str] = float(qt_str)
            for pl_str, qt_str in ob_fetched['asks']:
                dMap_asks[pl_str] = float(qt_str)
            dMap_bids_plMax = max(float(pl_str) for pl_str in dMap_bids)
            dMap_asks_plMin = min(float(pl_str) for pl_str in dMap_asks)
            sd_depths['dMap_bids_plMax'] = dMap_bids_plMax
            sd_depths['dMap_asks_plMin'] = dMap_asks_plMin

            #[3-6]: Buffer Update
            sd_depths['buffer'] = sd_depths_buffer_valid

            #[3-7]: Task Status Update
            fetchTask['status'] = 'complete'

    def __handleFetchTask_REST_aggTrade(self, symbol, cause, fetchTask, isLastCompletion, requestID):
        #[1]: Instances
        task_status = fetchTask['status']
        func_gnitt  = atmEta_Auxillaries.getNextIntervalTickTimestamp

        #[2]: pending -> Fetch AggTrades From REST
        if task_status == 'pending':
            #[2-1]: Fetch Block Check
            if self.__binance_fetchBlock:
                return
            
            #[2-2]: API Rate Limit Check
            if not self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_REQUESTWEIGHT, weight = 20, extraOnly = True, apply = True, printUpdated = True):
                return
        
            #[2-3]: Fetch Attempt & Save Data
            try: 
                ft_type, ft_range = fetchTask['fetchTarget']

                #[2-3-1]: Fetching With Timestamp Begin & AggTID End Range
                if ft_type == 'timestampBeg_aggTIDEnd':
                    #[2-3-1-1]: Fetch & Data Save
                    ts_beg_ms = ft_range[0]*1000
                    ts_end_ms = func_gnitt(intervalID = atmEta_Auxillaries.KLINE_INTERVAL_ID_1h, timestamp = ts_beg_ms, mrktReg = None, nTicks = 1)*1000-1
                    ats_fetched = self.__binance_client_default.futures_aggregate_trades(symbol    = symbol,
                                                                                         startTime = ts_beg_ms,
                                                                                         endTime   = ts_end_ms,
                                                                                         limit     = 1000)
                    #[2-3-1-2]: Timestamp Filtering & Data Save
                    aggTID_end = ft_range[1]
                    for at_f_idx, at_f in enumerate(ats_fetched):
                        if at_f['a'] < aggTID_end:
                            continue
                        else:
                            if   at_f['a'] == aggTID_end: ats_fetched = ats_fetched[:at_f_idx+1]
                            elif aggTID_end < at_f['a']:  ats_fetched = ats_fetched[:at_f_idx]
                            break
                    fetchTask['data'].extend(ats_fetched)
                    #[2-3-3-3]: Fetch Continuation Check
                    if 1000 <= len(ats_fetched) and ats_fetched[-1]['a'] < aggTID_end:
                        fetchTask['fetchTarget'] = ('aggTID', [ats_fetched[-1]['a']+1, aggTID_end])
                        return
                    #[2-3-1-4]: Status Update (Fetch Complete)
                    fetchTask['status'] = 'fetched'
                    
                #[2-3-3]: Fetching With AggTID Range
                elif ft_type == 'aggTID':
                    #[2-3-3-1]: Fetch & Data Save
                    nExpected = ft_range[1]-ft_range[0]+1
                    ats_fetched = self.__binance_client_default.futures_aggregate_trades(symbol = symbol, 
                                                                                         fromId = ft_range[0],
                                                                                         limit  = min(nExpected, 1000))
                    fetchTask['data'].extend(ats_fetched[:nExpected])
                    #[2-3-3-2]: Fetch Continuation Check
                    if 1000 < nExpected:
                        ft_range_beg_new_expected = ft_range[0]+1000
                        ft_range_beg_new_actual   = ats_fetched[-1]['a']+1 if ats_fetched else 0
                        ft_range[0] = max(ft_range_beg_new_expected, ft_range_beg_new_actual)
                        if ft_range[0] <= ft_range[1]:
                            return
                    #[2-3-3-3]: Status Update (Fetch Complete)
                    fetchTask['status'] = 'fetched'

            except Exception as e:
                self.__binance_fetchBlock = True
                self.__logger(message = (f"An Unexpected Error Ocurred While Attempting To Fetch AggTrades.\n"
                                        f" * Symbol:         {symbol}\n"
                                        f" * Cause:          {cause}\n"
                                        f" * Error:          {e}\n"
                                        f" * Detailed Trace: {traceback.format_exc()}"
                                        ), 
                            logType = 'Warning', 
                            color   = 'light_red')
                return

        #[3]: fetched -> Process Fetched Data
        if task_status == 'fetched':
            #[3-1]: Instances
            sd_symbol           = self.__binance_TWM_StreamingData[symbol]
            sd_aggTrades        = sd_symbol['aggTrades']
            sd_aggTrades_buffer = sd_aggTrades['buffer']
            aggTrades_fetched   = fetchTask['data']

            #[3-2]: Formatt The Fetched AggTrades For Buffer Insertion
            ats_f_formatted = [(at_f['a'],
                                float(at_f['p']),
                                float(at_f['q']),
                                at_f['m'],
                                at_f['l']-at_f['f']+1,
                                float(at_f['T']/1000)) 
                               for at_f in aggTrades_fetched]

            #[3-3]: Insert The Fetched AggTrades Into The Buffer
            if ats_f_formatted:
                idx_insertion    = len(sd_aggTrades_buffer)
                at_fs_lastAggTID = aggTrades_fetched[-1]['a']
                for at_b_idx, at_b in enumerate(sd_aggTrades_buffer):
                    if at_fs_lastAggTID < at_b[0]:
                        idx_insertion = at_b_idx
                        break
                sd_aggTrades_buffer[idx_insertion:idx_insertion] = ats_f_formatted

            #[3-4]: Task Status Update
            fetchTask['status'] = 'complete'

    def __handleFetchTask_VISION_kline(self, symbol, cause, fetchTask, isLastCompletion, requestID):
        #[1]: Process 'pending' & 'waitingResult' cases. If not in these cases, True will be returned
        isNextStep = self.__handleFetchTask_VISION_DBVF(fetchTask = fetchTask)
        if not isNextStep:
            return
        
        #[2]: fetched -> Process Fetched Data
        if fetchTask['status'] == 'fetched':
            #[2-1]: Instances
            sd_symbol        = self.__binance_TWM_StreamingData[symbol]
            sd_klines        = sd_symbol['klines']
            sd_klines_buffer = sd_klines['buffer']
            fetchedRange     = fetchTask['fetchTarget'][1]
            fetchedKlines    = fetchTask['data']
            func_gnitt       = atmEta_Auxillaries.getNextIntervalTickTimestamp

            #[2-2]: Header Check & Filtering
            if fetchedKlines and not fetchedKlines[0][0].isdigit():
                fetchedKlines.pop(0)
            
            #[2-3]: Expected Fetched Klines Timestamps
            efkts_expected = atmEta_Auxillaries.getTimestampList_byRange(intervalID        = KLINTERVAL, 
                                                                         mrktReg           = None, 
                                                                         timestamp_beg     = fetchedRange[0], 
                                                                         timestamp_end     = fetchedRange[1], 
                                                                         lastTickInclusive = True)

            #[2-4]: Format Klines
            fetchedKlines_dict      = {int(kl[0])//1000: kl for kl in fetchedKlines}
            fetchedKlines_formatted = []
            for efkt in efkts_expected:
                kl_raw = fetchedKlines_dict.get(efkt, None)
                #[2-4-1]: Expected Not Fetched - Fill With Dummy Klines
                if kl_raw is None:
                    kl_dummy = (efkt, 
                                func_gnitt(intervalID = KLINTERVAL, 
                                           timestamp  = efkt, 
                                           mrktReg    = None, 
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
                                True,
                                _FORMATTEDDATATYPE_DUMMY)
                    fetchedKlines_formatted.append(kl_dummy)
                #[2-4-2]: Expected Fetched - Reformat And Save
                else:
                    (tOpen_str, 
                     pOpen_str,
                     pHigh_str,
                     pLow_str,
                     pClose_str,
                     vBase_str,
                     tClose_str,
                     vQuote_str,
                     nTrades_str,
                     vBaseTB_str,
                     vQuoteTB_str,
                     ignore_str
                    ) = kl_raw
                    kl_formatted = (efkt,
                                    int(tClose_str)//1000,
                                    float(pOpen_str),
                                    float(pHigh_str),
                                    float(pLow_str),
                                    float(pClose_str),
                                    int(nTrades_str),
                                    float(vBase_str),
                                    float(vQuote_str),
                                    float(vBaseTB_str),
                                    float(vQuoteTB_str),
                                    True,
                                    _FORMATTEDDATATYPE_FETCHED)
                    fetchedKlines_formatted.append(kl_formatted)
                    del fetchedKlines_dict[efkt]

            #[2-5]: Formatted Data Save
            fetchTask['data']   = fetchedKlines_formatted
            fetchTask['status'] = 'formatted'

        #[3]: formatted -> Dispatch Data
        if fetchTask['status'] == 'formatted':
            #[3-1]: Formatted Data
            fetchedKlines_formatted = fetchTask['data']

            #[3-2]: Stream Cause
            if cause == 'stream':
                #[3-2-1]: Buffer Insertion Position Search
                sd_klines_buffer = self.__binance_TWM_StreamingData[symbol]['klines']['buffer']
                idx_insertion    = len(sd_klines_buffer)
                kl_fs_lastOpenTS = fetchedKlines_formatted[-1][KLINDEX_OPENTIME]
                for kl_b_idx, kl_b in enumerate(sd_klines_buffer):
                    if kl_fs_lastOpenTS < kl_b[0]:
                        idx_insertion = kl_b_idx
                        break
                #[3-2-2]: Buffer Insertion
                sd_klines_buffer[idx_insertion:idx_insertion] = fetchedKlines_formatted

            #[3-3]: DM Cause
            elif cause == 'dm':
                #[3-3-1]: DM Cause Dispatch Block Check
                if self.__binance_fetchRequests_dmCausePause: 
                    return
                #[3-3-2]: Dispatch
                fResult_status = 'complete' if isLastCompletion else 'fetching'
                self.ipcA.sendFARR(targetProcess  = 'DATAMANAGER',
                                   functionResult = {'target':       'kline',
                                                     'fetchedRange': [fetchedKlines_formatted[0][KLINDEX_OPENTIME], fetchedKlines_formatted[-1][KLINDEX_CLOSETIME]], 
                                                     'status':       fResult_status, 
                                                     'data':         fetchedKlines_formatted}, 
                                   requestID      = requestID, 
                                   complete       = isLastCompletion)
    
            #[3-4]: Explicit Memory Release
            fetchTask['data'] = None 
            
            #[3-5]: Update Status
            fetchTask['status'] = 'complete'

    def __handleFetchTask_VISION_depth(self, symbol, cause, fetchTask, isLastCompletion, requestID):
        #[1]: Process 'pending' & 'waitingResult' cases. If not in these cases, True will be returned
        isNextStep = self.__handleFetchTask_VISION_DBVF(fetchTask = fetchTask)
        if not isNextStep:
            return
        
        #[2]: fetched -> Process Fetched Data
        if fetchTask['status'] == 'fetched':
            #[2-1]: Instances
            sd_symbol         = self.__binance_TWM_StreamingData[symbol]
            sd_quotePrecision = sd_symbol['quotePrecision']
            fetchedRange      = fetchTask['fetchTarget'][1]
            fetchedDepths     = fetchTask['data']
            func_gnitt        = atmEta_Auxillaries.getNextIntervalTickTimestamp

            #[2-2]: Header Check & Filtering
            if fetchedDepths and not fetchedDepths[0][0].isdigit():
                fetchedDepths.pop(0)

            #[2-3]: Expected Fetched Depths Timestamps
            efdts_expected = atmEta_Auxillaries.getTimestampList_byRange(intervalID        = KLINTERVAL, 
                                                                         mrktReg           = None, 
                                                                         timestamp_beg     = fetchedRange[0], 
                                                                         timestamp_end     = fetchedRange[1], 
                                                                         lastTickInclusive = True)

        
            #[2-4]: Preprocess Depths
            fetchedDepths_dict = dict()
            for fd_date_str, fd_perc_str, fd_depth_str, fd_notional_str in fetchedDepths:
                fd_ts       = calendar.timegm(time.strptime(fd_date_str, "%Y-%m-%d %H:%M:%S"))
                fd_perc     = float(fd_perc_str)
                fd_notional = float(fd_notional_str)
                intervalTS  = func_gnitt(intervalID = KLINTERVAL, timestamp = fd_ts, mrktReg = None, nTicks = 0)
                if intervalTS not in fetchedDepths_dict: 
                    fetchedDepths_dict[intervalTS] = dict()
                fetchedDepths_dict[intervalTS][fd_perc] = fd_notional

            #[2-5]: Format Depth Data
            binFormats = (0.2, 1.0, 2.0, 3.0, 4.0, 5.0)
            fetchedDepths_formatted = []
            for efdt in efdts_expected:
                depth_raw = fetchedDepths_dict.get(efdt, None)
                #[2-5-1]: Expected Not Fetched - Fill With Dummy Depth
                if depth_raw is None:
                    depth_dummy = (efdt, 
                                   func_gnitt(intervalID = KLINTERVAL,
                                              timestamp  = efdt,
                                              mrktReg    = None,
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
                                   None,
                                   None,
                                   None,
                                   True,
                                   _FORMATTEDDATATYPE_DUMMY)
                    fetchedDepths_formatted.append(depth_dummy)
                #[2-5-2]: Expected Fetched - Reformat And Save
                else:
                    #[2-5-2-1]: Raw Bins
                    percs_sorted = {'bids': sorted((perc for perc in depth_raw if perc < 0), reverse = True),
                                    'asks': sorted((perc for perc in depth_raw if 0 < perc), reverse = False)}
                    bins_raw = {'bids': [], 'asks': []}
                    for dir in ('bids', 'asks'):
                        percs_sorted_dir = percs_sorted[dir]
                        bins_raw_dir     = bins_raw[dir]
                        for i, perc in enumerate(percs_sorted_dir):
                            if i == 0:
                                binRange_beg = 0
                                binRange_end = perc
                                binValue     = depth_raw[perc]
                            else:
                                binRange_beg = percs_sorted_dir[i-1]
                                binRange_end = perc
                                binValue     = depth_raw[perc]-depth_raw[binRange_beg]
                            bins_raw_dir.append((binRange_beg, binRange_end, binValue))
                            
                    #[2-5-2-2]: Bins Re-Distribution
                    bins_redistributed = {'bids': [], 'asks': []}
                    for dir in ('bids', 'asks'):
                        bins_raw_dir = bins_raw[dir]
                        bins_rd_dir  = bins_redistributed[dir]
                        bBeg_rd = 0.0
                        for bEnd_rd in binFormats:
                            bEnd_rd_abs = abs(bEnd_rd)
                            notionalSum = 0.0
                            for bBeg_raw, bEnd_raw, bValue_raw in bins_raw_dir:
                                #[4-5-2-2-1]: Overshoot & Overlap Check
                                bBeg_raw_abs = abs(bBeg_raw)
                                bEnd_raw_abs = abs(bEnd_raw)
                                if bEnd_rd_abs < bBeg_raw_abs: break
                                r_min, r_max = min(bBeg_raw_abs, bEnd_raw_abs), max(bBeg_raw_abs, bEnd_raw_abs)
                                overlap_width = min(bEnd_rd, r_max)-max(bBeg_rd, r_min)
                                if overlap_width <= 0: continue
                                #[4-5-2-2-2]: Notional Sum Update With Density-Based Redistribution
                                raw_width = r_max-r_min
                                if raw_width <= 0: continue
                                density = bValue_raw/raw_width
                                notionalSum += overlap_width*density
                            #[4-5-2-2-3]: Notional Sum Rounding & Appending
                            notionalSum = round(notionalSum, sd_quotePrecision)
                            bins_rd_dir.append(notionalSum)
                            #[4-5-2-2-4]: Target Bin Range Update
                            bBeg_rd = bEnd_rd

                    #[2-5-2-3]: Depth Formatting & Save
                    bins_rd_bids = bins_redistributed['bids']
                    bins_rd_asks = bins_redistributed['asks']
                    depth_formatted = (efdt, 
                                       func_gnitt(intervalID = KLINTERVAL,
                                                  timestamp  = efdt,
                                                  mrktReg    = None,
                                                  nTicks     = 1)-1,
                                       bins_rd_bids[5],
                                       bins_rd_bids[4],
                                       bins_rd_bids[3],
                                       bins_rd_bids[2],
                                       bins_rd_bids[1],
                                       bins_rd_bids[0],
                                       bins_rd_asks[0],
                                       bins_rd_asks[1],
                                       bins_rd_asks[2],
                                       bins_rd_asks[3],
                                       bins_rd_asks[4],
                                       bins_rd_asks[5],
                                       True,
                                       _FORMATTEDDATATYPE_FETCHED)
                    fetchedDepths_formatted.append(depth_formatted)
                    del fetchedDepths_dict[efdt]

            #[2-6]: Formatted Data Save
            fetchTask['data']   = fetchedDepths_formatted
            fetchTask['status'] = 'formatted'
                
        #[3]: formatted -> Dispatch Data (VISION Fetch Is Only Used For DM Request, So Only DM Cause Is Considered)
        if fetchTask['status'] == 'formatted':
            #[3-1]: Formatted Data
            fetchedDepths_formatted = fetchTask['data']

            #[3-2]: DM Cause Dispatch Block Check
            if self.__binance_fetchRequests_dmCausePause: 
                return
            
            #[3-3]: Dispatch
            fResult_status = 'complete' if isLastCompletion else 'fetching'
            self.ipcA.sendFARR(targetProcess  = 'DATAMANAGER',
                            functionResult = {'target':       'depth',
                                                'fetchedRange': [fetchedDepths_formatted[0][DEPTHINDEX_OPENTIME], fetchedDepths_formatted[-1][DEPTHINDEX_CLOSETIME]], 
                                                'status':       fResult_status, 
                                                'data':         fetchedDepths_formatted}, 
                            requestID      = requestID,
                            complete       = isLastCompletion)

            #[3-4]: Explicit Memory Release
            fetchTask['data'] = None
            
            #[3-5]: Update Status
            fetchTask['status'] = 'complete'

    def __handleFetchTask_VISION_aggTrade(self, symbol, cause, fetchTask, isLastCompletion, requestID):
        #[1]: Process 'pending' & 'waitingResult' cases. If not in these cases, True will be returned
        isNextStep = self.__handleFetchTask_VISION_DBVF(fetchTask = fetchTask)
        if not isNextStep:
            return
        
        #[2]: fetched -> Process Fetched Data
        if fetchTask['status'] == 'fetched':
            #[2-1]: Instances
            sd_symbol            = self.__binance_TWM_StreamingData[symbol]
            sd_quantityPrecision = sd_symbol['quantityPrecision']
            sd_quotePrecision    = sd_symbol['quotePrecision']
            fetchedRange         = fetchTask['fetchTarget'][1]
            fetchedAggTrades     = fetchTask['data']
            func_gnitt           = atmEta_Auxillaries.getNextIntervalTickTimestamp

            #[2-2]: Header Check & Filtering
            if fetchedAggTrades and not fetchedAggTrades[0][0].isdigit():
                fetchedAggTrades.pop(0)

            #[2-3]: Expected Fetched AggTrades Timestamps
            efatts = atmEta_Auxillaries.getTimestampList_byRange(intervalID        = KLINTERVAL, 
                                                                mrktReg           = None, 
                                                                timestamp_beg     = fetchedRange[0], 
                                                                timestamp_end     = fetchedRange[1], 
                                                                lastTickInclusive = True)

            #[2-4]: Preprocess AggTrades
            aggTrades_dict = dict()
            for fat_aggTID_str, fat_tradePrice_str, fat_quantity_str, fat_firstTID_str, fat_lastTID_str, fat_timestamp, fat_buyer_str in fetchedAggTrades:
                fat_tradePrice = float(fat_tradePrice_str)
                fat_quantity   = float(fat_quantity_str)
                fat_nTrades    = int(fat_lastTID_str)-int(fat_firstTID_str)+1
                fat_ts         = int(fat_timestamp)//1000
                fat_buyer      = str(fat_buyer_str).strip().lower() in ['true', '1', 't']
                intervalTS     = func_gnitt(intervalID = KLINTERVAL, timestamp = fat_ts, mrktReg = None, nTicks = 0)
                if intervalTS not in aggTrades_dict:
                    #[quantity_buy, quantity_sell, nTrades_buy, nTrades_sell, notional_buy, notional_sell]
                    aggTrades_dict[intervalTS] = [0, 0, 0, 0, 0, 0]
                at_dict_t = aggTrades_dict[intervalTS]
                if fat_buyer:
                    at_dict_t[1] += fat_quantity
                    at_dict_t[3] += fat_nTrades
                    at_dict_t[5] += fat_quantity*fat_tradePrice
                else:
                    at_dict_t[0] += fat_quantity
                    at_dict_t[2] += fat_nTrades
                    at_dict_t[4] += fat_quantity*fat_tradePrice

            #[2-5]: Format AggTrades Data
            aggTrades_formatted = []
            for efatt in efatts:
                at_pp = aggTrades_dict.get(efatt, None)
                #[2-5-1]: Expected Not Fetched - Fill With Dummy AggTrade
                if at_pp is None:
                    at_dummy = (efatt,
                                func_gnitt(intervalID = KLINTERVAL,
                                        timestamp  = efatt,
                                        mrktReg    = None,
                                        nTicks     = 1)-1,
                                None,
                                None,
                                None,
                                None,
                                None,
                                None,
                                True,
                                _FORMATTEDDATATYPE_DUMMY
                            )
                    aggTrades_formatted.append(at_dummy)
                #[2-5-2]: Expected Fetched - Tuplize And Save
                else:
                    at_f = (efatt,
                            func_gnitt(intervalID = KLINTERVAL,
                                    timestamp  = efatt,
                                    mrktReg    = None,
                                    nTicks     = 1)-1,
                            round(at_pp[0], sd_quantityPrecision),
                            round(at_pp[1], sd_quantityPrecision),
                            at_pp[2],
                            at_pp[3],
                            round(at_pp[4], sd_quotePrecision),
                            round(at_pp[5], sd_quotePrecision),
                            True,
                            _FORMATTEDDATATYPE_FETCHED)
                    aggTrades_formatted.append(at_f)
                    del aggTrades_dict[efatt]

            #[2-6]: Formatted Data Save
            fetchTask['data']   = aggTrades_formatted
            fetchTask['status'] = 'formatted'

        #[3]: formatted -> Dispatch Data (VISION Fetch Is Only Used For DM Request, So Only DM Cause Is Considered)
        if fetchTask['status'] == 'formatted':
            #[3-1]: Formatted Data
            aggTrades_formatted = fetchTask['data']

            #[3-2]: DM Cause Dispatch Block Check
            if self.__binance_fetchRequests_dmCausePause: 
                return

            #[3-3]: Dispatch
            fResult_status = 'complete' if isLastCompletion else 'fetching'
            self.ipcA.sendFARR(targetProcess  = 'DATAMANAGER',
                               functionResult = {'target':       'aggTrade',
                                                 'fetchedRange': [aggTrades_formatted[0][ATINDEX_OPENTIME], aggTrades_formatted[-1][ATINDEX_CLOSETIME]], 
                                                 'status':       fResult_status, 
                                                 'data':         aggTrades_formatted}, 
                               requestID      = requestID, 
                               complete       = isLastCompletion)
            
            #[3-4]: Explicit Memory Release
            fetchTask['data'] = None
            
            #[3-5]: Update Status
            fetchTask['status'] = 'complete'

    def __handleFetchTask_VISION_DBVF(self, fetchTask):
        #[1]: Instances
        task_status      = fetchTask['status']
        task_fetchTarget = fetchTask['fetchTarget']
        vExecutor        = self.__binance_visionExecutor
        func_dbvf        = self.__downloadBinanceVisionFile

        #[2]: pending -> Fetch Depth Snapshot From REST
        if task_status == 'pending':
            vFuture = vExecutor.submit(func_dbvf,
                                       file = task_fetchTarget[0])
            fetchTask['future'] = vFuture
            fetchTask['status'] = 'waitingResult'
            return False

        #[3]: waitingResult -> Check Result From The Vision Executor
        elif task_status == 'waitingResult':
            #[3-1]: Result Arrival Check
            dbvfFuture = fetchTask['future']
            if not dbvfFuture.done():
                return False
            #[3-2]: Result Arrived
            data = dbvfFuture.result()
            #---[3-2-1]: Fetch Failed, Retry 
            if data is None:
                fetchTask['future'] = None
                fetchTask['status'] = 'pending'
                return False
            #---[3-2-2]: Fetch Succeeded, Save Data and Update Status
            fetchTask['future'] = None
            fetchTask['data']   = data
            fetchTask['status'] = 'fetched'
            return True
        
        #[4]: Return True To Indicate The Current Step Is Beyond This Function's Scope 
        return True

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
        buffer_append = connection['buffer'].append
        def receiver(streamContents):
            buffer_append(streamContents)
        return receiver
    
    def __processTWMStreamMessages(self):
        #[1]: Instances
        conns        = self.__binance_TWM_Connections
        func_im      = self.__processTWMStreamMessages_InterpretMessage
        sds          = self.__binance_TWM_StreamingData
        ipca_sendFAR = self.ipcA.sendFAR

        #[1]: Messages Interpretation
        count_limit = 1000
        for conn in conns.values():
            count           = 0
            conn_buffer     = conn['buffer']
            conn_buffer_pop = conn_buffer.popleft
            while count < count_limit and conn_buffer:
                streamMessage = conn_buffer_pop()
                func_im(connection = conn, streamMessage = streamMessage)
                count += 1

        #[2]: Announcements
        t_current_ns = time.perf_counter_ns()
        for symbol in sds:
            sd = sds[symbol]
            #[2-1]: Updates & Last Announced Check
            if not (sd['updatedTypes'] and 100e6 <= t_current_ns-sd['lastAnnounced_ns']): 
                continue

            #[2-2]: Instances
            uTypes = sd['updatedTypes']

            #[2-3]: Kline Response
            if uTypes & _BINANCE_TWM_STREAMDATATYPE_FLAGS[_BINANCE_TWM_STREAMDATATYPE_KLINE]:
                sd_klines_klines = sd['klines']['klines']
                for ts in sorted(sd_klines_klines):
                    kl          = sd_klines_klines[ts]
                    far_fParams = {'symbol': symbol, 
                                   'kline':  kl}
                    for sub in sd['subscriptions']:
                        fID_kline = sub['fID_kline']
                        if sub['closedOnly'] and not kl[KLINDEX_CLOSED]: continue
                        ipca_sendFAR(targetProcess  = sub['subscriber'], 
                                     functionID     = fID_kline, 
                                     functionParams = far_fParams, 
                                     farrHandler    = None)
                sd_klines_klines.clear()

            #[2-4]: Depth Update Response
            if uTypes & _BINANCE_TWM_STREAMDATATYPE_FLAGS[_BINANCE_TWM_STREAMDATATYPE_DEPTHUPDATE]:
                sd_depths_depths = sd['depths']['depths']
                for ts in sorted(sd_depths_depths):
                    depth       = sd_depths_depths[ts]
                    far_fParams = {'symbol': symbol, 
                                   'depth':  depth}
                    for sub in sd['subscriptions']:
                        fID_depth = sub['fID_depth']
                        if sub['closedOnly'] and not depth[DEPTHINDEX_CLOSED]: continue
                        ipca_sendFAR(targetProcess  = sub['subscriber'], 
                                     functionID     = fID_depth, 
                                     functionParams = far_fParams, 
                                     farrHandler    = None)
                sd_depths_depths.clear()
                            
            #[2-5]: AggTrades Response
            if uTypes & _BINANCE_TWM_STREAMDATATYPE_FLAGS[_BINANCE_TWM_STREAMDATATYPE_AGGTRADES]:
                sd_aggTrades_aggTrades = sd['aggTrades']['aggTrades']
                for ts in sorted(sd_aggTrades_aggTrades):
                    aggTrade    = sd_aggTrades_aggTrades[ts]
                    far_fParams = {'symbol':   symbol, 
                                   'aggTrade': aggTrade}
                    for sub in sd['subscriptions']:
                        fID_aggTrade = sub['fID_aggTrade']
                        if sub['closedOnly'] and not aggTrade[ATINDEX_CLOSED]: continue
                        ipca_sendFAR(targetProcess  = sub['subscriber'], 
                                     functionID     = fID_aggTrade, 
                                     functionParams = far_fParams, 
                                     farrHandler    = None)
                sd_aggTrades_aggTrades.clear()

            #[2-6]: Announcement Control
            sd['updatedTypes']     = 0b000
            sd['lastAnnounced_ns'] = t_current_ns
    
    def __processTWMStreamMessages_InterpretMessage(self, connection, streamMessage):
        #[1]: Message Contents
        sm_data = streamMessage.get('data', None)
        sm_e    = streamMessage.get('e',    None)

        #[2]: Expected stream content
        if sm_data is not None:
            sm_data_event = sm_data.get('e', None)
            #[2-1]: Expected Data Type Received
            if sm_data_event in self.__binance_TWM_StreamHandlers:
                #[2-1-1]: Process Attempt
                symbol, dType, raiseUFlag = self.__binance_TWM_StreamHandlers[sm_data_event](streamData = sm_data)
                if symbol is None: return
                sd = self.__binance_TWM_StreamingData[symbol]
                #[2-1-2]: Update Flag Raise
                if raiseUFlag:
                    sd['updatedTypes'] |= _BINANCE_TWM_STREAMDATATYPE_FLAGS[sm_data_event]
                #[2-1-3]: Expired Connection CheckList Update
                if sd['connectionID_EXPIRED'] is not None and sd['connectionID_MAIN'] == connection['connectionID']:
                    tcl        = self.__binance_TWM_Connections[sd['connectionID_EXPIRED']]['terminationCheckList']
                    identifier = (symbol, dType)
                    if identifier in tcl: tcl.remove(identifier)
                #[2-1-4]: Exit Function
                return

            #[2-2]: Unexpected Data Type Received
            #---[2-2-1]: Logger
            self.__logger(message = f"Unexpected Stream Message Detected from Stream '{streamMessage['stream']}'\n * Stream Contents: {streamMessage}", 
                          logType = 'Warning', 
                          color   = 'light_red')
            #---[2-2-2]: Exit Function
            return

        #[3]: Unexpected stream content. Stream may return 'Queue overflow. Message not filled' error, not anymore sending any stream data. In this case, restart all of the existing connections
        if sm_e == 'error':
            #[3-1]: Overflow Occurred
            if streamMessage['m'] == f'Message queue size {self.__binance_TWM._max_queue_size} exceeded maximum {self.__binance_TWM._max_queue_size}':
                self.__binance_TWM_OverFlowDetected = True
            #[3-2]: Other Unexpected
            else: 
                self.__logger(message = f"An unexpected error received from the TWM, the connection symbols will be regenerated.\n * '{streamMessage['m']}'", 
                              logType = 'Warning', 
                              color   = 'light_red')
            #[3-3]: Exit Function
            return
            
        #[4]: Unexpected stream content, unregistered case
        self.__logger(message = f"Unexpected content received from WebSocket streams, user attention advised!\n * Stream Contents: {streamMessage}", 
                      logType = 'Warning', 
                      color   = 'light_red')
    
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
    def __processTWMStreamMessages_Kline(self, streamData):
        #[1]: Process Attempt
        try:
            #[1-1]: Data Read
            sData_symbol    = streamData['ps']
            sData_eventTime = streamData['E']
            sData_kline     = streamData['k']
            kl_openTS     = int(sData_kline['t']/1000) #Kline OpenTS
            kl_closeTS    = int(sData_kline['T']/1000) #Kline CloseTS
            kl_openPrice  = float(sData_kline['o'])    #Open  Price
            kl_highPrice  = float(sData_kline['h'])    #High  Price
            kl_lowPrice   = float(sData_kline['l'])    #Low   Price
            kl_closePrice = float(sData_kline['c'])    #Close Price
            kl_nTrades    = int(sData_kline['n'])      #nTrades
            kl_volBase    = float(sData_kline['v'])    #Base  Asset Volume
            kl_volQuote   = float(sData_kline['q'])    #Quote Asset Volume
            kl_volBaseTB  = float(sData_kline['V'])    #Base  Asset Volume - Taker Buy
            kl_volQuoteTB = float(sData_kline['Q'])    #Quote Asset Volume - Taker Buy
            kl_closed     = sData_kline['x']

            #[1-2]: Continuity Check
            sd_symbol  = self.__binance_TWM_StreamingData[sData_symbol]
            sd_klines  = sd_symbol['klines']
            sd_ls      = sd_klines['lastStream']
            ftr        = None
            func_gnitt = atmEta_Auxillaries.getNextIntervalTickTimestamp
            if sd_ls is not None:
                eventTime_prev, kl_openTS_prev, kl_closed_prev = sd_ls

                #[1-2-1]: Event Time Check
                if sData_eventTime <= eventTime_prev: 
                    return (sData_symbol, 'kline', False)
                
                #[1-2-2]: Kline Open TS Check
                #---[1-2-2-1]: OpenTS_new < OpenTS_prev -> Ignore
                if kl_openTS < kl_openTS_prev: 
                    return (sData_symbol, 'kline', False)
                
                #---[1-2-2-2]: OpenTS_prev == OpenTS_new -> Check Closed
                elif kl_openTS_prev == kl_openTS:
                    #[1-2-2-2-1]: Same Timestamp, But Already Closed -> Ignore
                    if kl_closed_prev:
                        return (sData_symbol, 'kline', False)

                #---[1-2-2-3]: OpenTS_prev < OpenTS_new -> Check Closed & Next Expected Interval
                elif kl_openTS_prev < kl_openTS:
                    #[1-2-2-3-1]: Future Timestamp, And Previous Closed. Check Next Expected
                    if kl_closed_prev:
                        kl_openTS_expected = func_gnitt(intervalID = KLINTERVAL, 
                                                        timestamp  = kl_openTS_prev,
                                                        mrktReg    = None, 
                                                        nTicks     = 1)
                        #[1-2-2-3-1]: Next Timestamp Is Not The Expected -> Request Fetch
                        if kl_openTS_expected != kl_openTS:
                            ftr = (kl_openTS_expected, kl_openTS-1)
                    #---[1-2-2-3-2]: Future Timestamp, And Previous Still Open -> Request Fetch
                    else:
                        ftr = (kl_openTS_prev, kl_openTS-1)

            #[1-3]: If Need Fetch, Request It
            if ftr is not None:
                reqParams = {'requestID':            None,
                             'fetchTargetRangeType': 'timestamp',
                             'fetchTargetRanges':    [ftr,]}
                self.__addFetchRequest(symbol        = sData_symbol, 
                                       target        = 'kline', 
                                       cause         = 'stream', 
                                       requestParams = reqParams)
                sd_klines['waitingFetch'] = True

            #[1-4]: Base Data Formatting
            kl_base = (kl_openTS,
                       kl_closeTS,
                       kl_openPrice,
                       kl_highPrice,
                       kl_lowPrice,
                       kl_closePrice,
                       kl_nTrades,
                       kl_volBase,
                       kl_volQuote,
                       kl_volBaseTB,
                       kl_volQuoteTB,
                       kl_closed,
                       _FORMATTEDDATATYPE_STREAMED)
            
            #[1-5]: Data Formatting & Data Update
            #---[1-5-1]: If Waiting Fetch, Add Base Data To Buffer
            if sd_klines['waitingFetch']:
                sd_klines['buffer'].append(kl_base)

            #---[1-5-2]: Continuous Case, Update Klines
            else:
                #[1-5-2-1]: Collect Base Data
                kls_base = list(sd_klines['buffer'])+[kl_base,]

                #[1-5-2-2]: Process Base Data
                sd_klines_klines = sd_klines['klines']
                lastInterval     = sd_klines['lastInterval']
                for kl_base in kls_base:
                    #[1-5-2-2-1]: Unpack Base Data
                    (kl_openTS,
                     kl_closeTS,
                     kl_openPrice,
                     kl_highPrice,
                     kl_lowPrice,
                     kl_closePrice,
                     kl_nTrades,
                     kl_volBase,
                     kl_volQuote,
                     kl_volBaseTB,
                     kl_volQuoteTB,
                     kl_closed,
                     kl_source) = kl_base
                    db_intervalTS = kl_openTS
                    
                    #[1-5-2-2-2]: Interval Conditions Check
                    #---[1-5-2-2-3-1]: Interval Reversal Check (This Should Not Happen, But Placed Here For Possible Debugging In Case Of A System Logic Flow Failure)
                    if (lastInterval is not None) and (db_intervalTS < lastInterval[KLINDEX_OPENTIME]):
                        self.__logger(message = (f"A Future Interval Timestamp Detected During Kline Stream Handling. This Means A System Logic Failure. Developer Attention Advised.\n"
                                                 f" * Stream Data:                 {streamData}\n"
                                                 f" * Current  Interval Timestamp: {db_intervalTS}\n"
                                                 f" * Previous Interval Timestamp: {lastInterval[KLINDEX_OPENTIME]}"
                                                ),
                                      logType = 'Warning', 
                                      color   = 'light_red')
                        return (sData_symbol, 'kline', False)
                    #---[1-5-2-2-3-2]: Expected Cases
                    ic_newInterval = (lastInterval is None) or (lastInterval[KLINDEX_OPENTIME] < db_intervalTS)
                    
                    #[1-5-2-2-4]: On New Interval
                    if ic_newInterval:
                        #[1-5-2-2-4-1]: Expired Previous Interval Closing & Gap Filling
                        if lastInterval is not None:
                            li_openTS = lastInterval[KLINDEX_OPENTIME]

                            #[1-5-2-2-4-1-1]: Record The Last Interval As Closed And Save To The Announcement Buffer (If It Is Not Yet Closed)
                            if not lastInterval[KLINDEX_CLOSED]:
                                lastInterval[KLINDEX_CLOSED] = True
                                sd_klines_klines[li_openTS] = tuple(lastInterval)

                            #[1-5-2-2-4-1-2]: Fill In Any Gaps With Dummy Klines Data
                            di_openTS = func_gnitt(intervalID = KLINTERVAL, timestamp = li_openTS, mrktReg = None, nTicks = 1)
                            while di_openTS < db_intervalTS:
                                di_openTS_next = func_gnitt(intervalID = KLINTERVAL, timestamp = di_openTS, mrktReg = None, nTicks = 1)
                                dummyInterval = (di_openTS,                #[0]:  openTS
                                                 di_openTS_next-1,         #[1]:  closeTS
                                                 None,                     #[2]:  openPrice
                                                 None,                     #[3]:  highPrice
                                                 None,                     #[4]:  lowPrice
                                                 None,                     #[5]:  closePrice
                                                 None,                     #[6]:  nTrades
                                                 None,                     #[7]:  volBase
                                                 None,                     #[8]:  volQuote
                                                 None,                     #[9]:  volBase  - Taker Buy
                                                 None,                     #[10]: volQuote - Taker Buy
                                                 True,                     #[11]: closed
                                                 _FORMATTEDDATATYPE_DUMMY) #[12]: klineType
                                sd_klines_klines[di_openTS] = dummyInterval
                                di_openTS = di_openTS_next

                    #[1-5-2-2-5]: New Interval
                    lastInterval = [kl_openTS,     #[0]:  openTS
                                    kl_closeTS,    #[1]:  closeTS
                                    kl_openPrice,  #[2]:  openPrice
                                    kl_highPrice,  #[3]:  highPrice
                                    kl_lowPrice,   #[4]:  lowPrice
                                    kl_closePrice, #[5]:  closePrice
                                    kl_nTrades,    #[6]:  nTrades
                                    kl_volBase,    #[7]:  volBase
                                    kl_volQuote,   #[8]:  volQuote
                                    kl_volBaseTB,  #[9]:  volBase  - Taker Buy
                                    kl_volQuoteTB, #[10]: volQuote - Taker Buy
                                    kl_closed,     #[11]: closed
                                    kl_source]     #[12]: klineType
                    sd_klines['lastInterval'] = lastInterval

                    #[1-5-2-2-6]: Interval Tuplization & Announcement Buffer Update
                    sd_klines_klines[kl_openTS] = tuple(lastInterval)
                    
                #[1-5-2-3]: Clear Buffer
                sd_klines['buffer'].clear()

            #[1-6]: Save The Last Stream
            sd_klines['lastStream'] = (sData_eventTime, kl_openTS, kl_closed)

            #[1-7]: Identifier Return
            if sd_klines['waitingFetch']: return (sData_symbol, 'kline', False)
            else:                         return (sData_symbol, 'kline', True)

        #[2]: Exception Handling
        except Exception as e:
            self.__logger(message = (f"Unexpected Error Occurred While Attempting To Process Kline Stream Data\n"
                                     f" * Stream Data:    {streamData}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"),
                          logType = 'Error', 
                          color   = 'light_red')
            return (None, None, False)
    
    """
    streamContents = {'stream': 'dogeusdt@depth', 
                      'data': {"e": "depthUpdate",              // Event type
                               "E": 1771948238192,              // Event time
                               "T": 1771948238186,              // Transaction time 
                               "s": "BTCUSDT",                  // Symbol
                               "U": 157,                        // First update ID in event
                               "u": 160,                        // Final update ID in event
                               "pu": 149,                       // Final update ID in last stream(ie `u` in last stream)
                               "b": [["0.0024", "10"],  [...]], // Bids to be updated (List of (<Price Level to be updated>, <Quantity>))
                               "a": [["0.0026", "100"], [...]]} // Asks to be updated (List of (<Price Level to be updated>, <Quantity>))
                              }

    SYSTEM: fetchedDepth_formatted[n] = ([0]:  openTS,
                                         [1]:  closeTS,
                                         [2]:  bids5 (-4.0% ~ -5.0%)
                                         [3]:  bids4 (-3.0% ~ -4.0%)
                                         [4]:  bids3 (-2.0% ~ -3.0%)
                                         [5]:  bids2 (-1.0% ~ -2.0%)
                                         [6]:  bids1 (-0.2% ~ -1.0%)
                                         [7]:  bids0 ( 0.0% ~ -0.2%)
                                         [8]:  asks0 ( 0.0% ~  0.2%)
                                         [9]:  asks1 ( 0.2% ~  1.0%)
                                         [10]: asks2 ( 1.0% ~  2.0%)
                                         [11]: asks3 ( 2.0% ~  3.0%)
                                         [12]: asks4 ( 3.0% ~  4.0%)
                                         [13]: asks5 ( 4.0% ~  5.0%)
                                         [14]: closed,
                                         [15]: depthType
                                        )

    """ #Expand to check an orderbook stream data example
    def __processTWMStreamMessages_DepthUpdate(self, streamData):
        #[1]: Process Attempt
        try:
            #[1-1]: Data Read
            sData_transactionTime     = float(streamData['T']/1000) #Transaction Time
            sData_transactionTime_int = int(sData_transactionTime)
            sData_symbol              = streamData['s']             #Symbol
            sData_firstUID            = streamData['U']             #First update ID in event
            sData_finalUID            = streamData['u']             #Final update ID in event
            sData_finalUID_lastStream = streamData['pu']            #Final update ID in last stream(ie `u` in last stream)
            sData_bids                = streamData['b']             #Bids to be updated (List of (<Price Level to be updated>, <Quantity>))
            sData_asks                = streamData['a']             #Asks to be updated (List of (<Price Level to be updated>, <Quantity>))

            #[1-2]: Continuity Check
            sd_symbol         = self.__binance_TWM_StreamingData[sData_symbol]
            sd_quotePrecision = sd_symbol['quotePrecision']
            sd_pricePrecision = sd_symbol['pricePrecision']
            sd_depths         = sd_symbol['depths']
            sd_ls             = sd_depths['lastStream']
            needFetch         = None
            func_gnitt        = atmEta_Auxillaries.getNextIntervalTickTimestamp
            #---[1-2-1]: This Is The Very First Stream
            if sd_ls is None:
                needFetch = True
            else:
                sData_finalUID_prev = sd_ls
                #[1-2-2-1]: The Final Expeceted UID Of The Previous Stream Is Before The Final UID Of The Last Stream. Ignore.
                if sData_finalUID_lastStream < sData_finalUID_prev:
                    return (sData_symbol, 'depth', False)
                
                #[1-2-2-2]: The Final Expeceted UID Of The Previous Stream Is After The Final UID Of The Last Stream. Fetch.
                elif sData_finalUID_prev < sData_finalUID_lastStream:
                    needFetch = True

            #[1-3]: If Need Fetch, Request It
            if needFetch and not sd_depths['waitingFetch']:
                reqParams = {'requestID':            None,
                             'fetchTargetRangeType': 'snapshot',
                             'fetchTargetRanges':    []}
                self.__addFetchRequest(symbol        = sData_symbol, 
                                       target        = 'depth',
                                       cause         = 'stream',
                                       requestParams = reqParams)
                sd_depths['waitingFetch'] = True
                
            #[1-4]: Base Data Formatting
            intervalTS_this = func_gnitt(intervalID = KLINTERVAL, timestamp = sData_transactionTime_int, mrktReg = None, nTicks = 0)
            depth_base = (intervalTS_this,
                          sData_firstUID,
                          sData_finalUID,
                          sData_finalUID_lastStream,
                          sData_bids,
                          sData_asks)
            
            #---[1-4-1]: If Waiting Fetch, Add Base Data To Buffer
            if sd_depths['waitingFetch']:
                sd_depths['buffer'].append(depth_base)

            #---[1-4-2]: Continuous Case, Update Intervalized Depths
            else:
                #[1-4-2-1]: Collect Base Data
                depths_base = list(sd_depths['buffer'])+[depth_base,]

                #[1-4-2-2]: Process Base Data
                sd_depths_depths = sd_depths['depths']
                lastInterval     = sd_depths['lastInterval']
                dMap_bids        = sd_depths['dMap_bids']
                dMap_asks        = sd_depths['dMap_asks']
                for depth_base in depths_base:
                    #[1-4-2-2-1]: Unpack Base Data
                    (db_intervalTS, 
                     db_firstUID, 
                     db_finalUID, 
                     db_finalUID_lastStream,
                     db_bids,
                     db_asks) = depth_base

                    #[1-4-2-2-2]: Depth Map Update
                    dMap_bids_plMax = sd_depths['dMap_bids_plMax']
                    dMap_asks_plMin = sd_depths['dMap_asks_plMin']
                    dMap_bids_plMax_recompute = False
                    dMap_asks_plMin_recompute = False
                    for pl_str, qt_str in db_bids:
                        pl, qt = float(pl_str), float(qt_str)
                        if qt == 0.0:
                            if pl_str in dMap_bids:
                                del dMap_bids[pl_str]
                                dMap_bids_plMax_recompute = dMap_bids_plMax_recompute or (pl == dMap_bids_plMax)
                        else:
                            dMap_bids[pl_str] = qt
                            if dMap_bids_plMax < pl:
                                dMap_bids_plMax           = pl
                                dMap_bids_plMax_recompute = False
                    for pl_str, qt_str in db_asks:
                        pl, qt = float(pl_str), float(qt_str)
                        if qt == 0.0: 
                            if pl_str in dMap_asks:
                                del dMap_asks[pl_str]
                                dMap_asks_plMin_recompute = dMap_asks_plMin_recompute or (pl == dMap_asks_plMin)
                        else:
                            dMap_asks[pl_str] = qt
                            if pl < dMap_asks_plMin:
                                dMap_asks_plMin           = pl
                                dMap_asks_plMin_recompute = False
                    if dMap_bids_plMax_recompute:
                        if dMap_bids: dMap_bids_plMax = max(float(pl_str) for pl_str in dMap_bids)
                        else:         dMap_bids_plMax = None
                    if dMap_asks_plMin_recompute:
                        if dMap_asks: dMap_asks_plMin = min(float(pl_str) for pl_str in dMap_asks)
                        else:         dMap_asks_plMin = None
                    sd_depths['dMap_bids_plMax'] = dMap_bids_plMax
                    sd_depths['dMap_asks_plMin'] = dMap_asks_plMin

                    #[1-4-2-2-3]: Interval Conditions Check
                    #---[1-4-2-2-3-1]: Interval Reversal Check (This Should Not Happen, But Placed Here For Possible Debugging In Case Of A System Logic Flow Failure)
                    if (lastInterval is not None) and (db_intervalTS < lastInterval[DEPTHINDEX_OPENTIME]):
                        self.__logger(message = (f"A Future Interval Timestamp Detected During Depth Stream Intervalization. This Means A System Logic Failure. Developer Attention Advised.\n"
                                                 f" * Stream Data:                 {streamData}\n"
                                                 f" * Current  Interval Timestamp: {db_intervalTS}\n"
                                                 f" * Previous Interval Timestamp: {lastInterval[DEPTHINDEX_OPENTIME]}"
                                                ),
                                      logType = 'Warning', 
                                      color   = 'light_red')
                        return (sData_symbol, 'depth', False)
                    #---[1-4-2-2-3-2]: Expected Cases
                    t_current_ns   = time.perf_counter_ns()
                    ic_newInterval = (lastInterval is None) or (lastInterval[DEPTHINDEX_OPENTIME] < db_intervalTS)
                    ic_newSnapShot = 1e9 < t_current_ns-sd_depths['lastIntervalSnap']
                    
                    #[1-4-2-2-4]: Interval Snapshotting
                    if ic_newInterval or ic_newSnapShot:
                        #[1-4-2-2-4-1]: Expired Previous Interval Closing & Gap Filling
                        if ic_newInterval and lastInterval is not None:
                            li_openTS = lastInterval[DEPTHINDEX_OPENTIME]

                            #[1-4-2-2-4-1-1]: Record The Last Interval As Closed And Save To The Announcement Buffer (If It Is Not Yet Closed)
                            if not lastInterval[DEPTHINDEX_CLOSED]:
                                lastInterval[DEPTHINDEX_CLOSED] = True
                                sd_depths_depths[li_openTS] = tuple(lastInterval)

                            #[1-4-2-2-4-1-2]: Fill In Any Gaps With Dummy Depths Interval Data
                            di_openTS = func_gnitt(intervalID = KLINTERVAL, timestamp = li_openTS, mrktReg = None, nTicks = 1)
                            while di_openTS < db_intervalTS:
                                di_openTS_next = func_gnitt(intervalID = KLINTERVAL, timestamp = di_openTS, mrktReg = None, nTicks = 1)
                                dummyInterval = (di_openTS,               #[0]:  openTS
                                                 di_openTS_next-1,        #[1]:  closeTS
                                                 None,                    #[2]:  bids5
                                                 None,                    #[3]:  bids4
                                                 None,                    #[4]:  bids3
                                                 None,                    #[5]:  bids2
                                                 None,                    #[6]:  bids1
                                                 None,                    #[7]:  bids0
                                                 None,                    #[8]:  asks0
                                                 None,                    #[9]:  asks1
                                                 None,                    #[10]: asks2
                                                 None,                    #[11]: asks3
                                                 None,                    #[12]: asks4
                                                 None,                    #[13]: asks5
                                                 True,                    #[14]: closed
                                                 _FORMATTEDDATATYPE_DUMMY #[15]: depthType
                                                )
                                sd_depths_depths[di_openTS] = dummyInterval
                                di_openTS = di_openTS_next

                        #[1-4-2-2-4-2]: Interval Setup
                        if ic_newInterval:
                            db_intervalTS_next = func_gnitt(intervalID = KLINTERVAL, timestamp = db_intervalTS, mrktReg = None, nTicks = 1)
                            lastInterval = [db_intervalTS,              #[0]:  openTS
                                            db_intervalTS_next-1,       #[1]:  closeTS
                                            0,                          #[2]:  bids5
                                            0,                          #[3]:  bids4
                                            0,                          #[4]:  bids3
                                            0,                          #[5]:  bids2
                                            0,                          #[6]:  bids1
                                            0,                          #[7]:  bids0
                                            0,                          #[8]:  asks0
                                            0,                          #[9]:  asks1
                                            0,                          #[10]: asks2
                                            0,                          #[11]: asks3
                                            0,                          #[12]: asks4
                                            0,                          #[13]: asks5
                                            False,                      #[14]: closed
                                            _FORMATTEDDATATYPE_STREAMED #[15]: depthType
                                           ]
                            sd_depths['lastInterval'] = lastInterval
                        else:
                            lastInterval[DEPTHINDEX_BIDS0] = 0
                            lastInterval[DEPTHINDEX_BIDS1] = 0
                            lastInterval[DEPTHINDEX_BIDS2] = 0
                            lastInterval[DEPTHINDEX_BIDS3] = 0
                            lastInterval[DEPTHINDEX_BIDS4] = 0
                            lastInterval[DEPTHINDEX_BIDS5] = 0
                            lastInterval[DEPTHINDEX_ASKS0] = 0
                            lastInterval[DEPTHINDEX_ASKS1] = 0
                            lastInterval[DEPTHINDEX_ASKS2] = 0
                            lastInterval[DEPTHINDEX_ASKS3] = 0
                            lastInterval[DEPTHINDEX_ASKS4] = 0
                            lastInterval[DEPTHINDEX_ASKS5] = 0
                        
                        #[1-4-2-2-4-3]: Center Price
                        if dMap_bids_plMax is not None and dMap_asks_plMin is not None: centerPrice = round((dMap_asks_plMin+dMap_bids_plMax)/2, sd_pricePrecision)
                        else:
                            if   dMap_bids_plMax is not None: centerPrice = dMap_bids_plMax
                            elif dMap_asks_plMin is not None: centerPrice = dMap_asks_plMin
                            else:                             centerPrice = None
                            
                        #[1-4-2-2-4-4]: Interval Snapshot Update
                        if centerPrice is not None:
                            for pl_str, qt in dMap_bids.items():
                                pl       = float(pl_str)
                                pdp      = (centerPrice-pl)/centerPrice
                                notional = round(qt*pl, sd_quotePrecision)
                                if   pdp <  0.000: continue
                                elif pdp <= 0.002: lastInterval[DEPTHINDEX_BIDS0] = round(lastInterval[DEPTHINDEX_BIDS0] + notional, sd_quotePrecision)
                                elif pdp <= 0.010: lastInterval[DEPTHINDEX_BIDS1] = round(lastInterval[DEPTHINDEX_BIDS1] + notional, sd_quotePrecision)
                                elif pdp <= 0.020: lastInterval[DEPTHINDEX_BIDS2] = round(lastInterval[DEPTHINDEX_BIDS2] + notional, sd_quotePrecision)
                                elif pdp <= 0.030: lastInterval[DEPTHINDEX_BIDS3] = round(lastInterval[DEPTHINDEX_BIDS3] + notional, sd_quotePrecision)
                                elif pdp <= 0.040: lastInterval[DEPTHINDEX_BIDS4] = round(lastInterval[DEPTHINDEX_BIDS4] + notional, sd_quotePrecision)
                                elif pdp <= 0.050: lastInterval[DEPTHINDEX_BIDS5] = round(lastInterval[DEPTHINDEX_BIDS5] + notional, sd_quotePrecision)
                                
                            for pl_str, qt in dMap_asks.items():
                                pl       = float(pl_str)
                                pdp      = (pl-centerPrice)/centerPrice
                                notional = round(qt*pl, sd_quotePrecision)
                                if   pdp <  0.000: continue
                                elif pdp <= 0.002: lastInterval[DEPTHINDEX_ASKS0] = round(lastInterval[DEPTHINDEX_ASKS0] + notional, sd_quotePrecision)
                                elif pdp <= 0.010: lastInterval[DEPTHINDEX_ASKS1] = round(lastInterval[DEPTHINDEX_ASKS1] + notional, sd_quotePrecision)
                                elif pdp <= 0.020: lastInterval[DEPTHINDEX_ASKS2] = round(lastInterval[DEPTHINDEX_ASKS2] + notional, sd_quotePrecision)
                                elif pdp <= 0.030: lastInterval[DEPTHINDEX_ASKS3] = round(lastInterval[DEPTHINDEX_ASKS3] + notional, sd_quotePrecision)
                                elif pdp <= 0.040: lastInterval[DEPTHINDEX_ASKS4] = round(lastInterval[DEPTHINDEX_ASKS4] + notional, sd_quotePrecision)
                                elif pdp <= 0.050: lastInterval[DEPTHINDEX_ASKS5] = round(lastInterval[DEPTHINDEX_ASKS5] + notional, sd_quotePrecision)
                        sd_depths_depths[db_intervalTS] = tuple(lastInterval)

                        #[1-4-2-2-4-5]: Snapshot Timer Update
                        sd_depths['lastIntervalSnap'] = t_current_ns
                    
                #[1-4-2-3]: Clear Buffer
                sd_depths['buffer'].clear()

            #[1-5]: Save The Last Stream
            sd_depths['lastStream'] = sData_finalUID

            #[1-6]: Identifier Return
            if sd_depths['waitingFetch']: return (sData_symbol, 'depth', False)
            else:                         return (sData_symbol, 'depth', True)

        #[2]: Exception Handling
        except Exception as e:
            self.__logger(message = (f"Unexpected Error Occurred While Attempting To Process Depth Stream Data\n"
                                     f" * Stream Data:    {streamData}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"),
                          logType = 'Error', 
                          color   = 'light_red')
            return (None, 'depth', False)
    
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
    def __processTWMStreamMessages_AggTrade(self, streamData):
        #[1]: Process Attempt
        try:
            #[1-1]: Data Read
            sData_aggTID        = streamData['a']             #Aggregate Trade ID
            sData_symbol        = streamData['s']             #Symbol
            sData_tradePrice    = float(streamData['p'])      #Trade Price
            sData_quantity      = float(streamData['q'])      #Quantity
            sData_maker         = streamData['m']             #Is the buyer the market maker?
            sData_firstTID      = streamData['f']             #First Trade ID
            sData_lastTID       = streamData['l']             #Last Trade ID
            sData_tradeTime     = float(streamData['T']/1000) #Trade Time (Originally in ms)
            sData_tradeTime_int = int(sData_tradeTime)

            #[1-2]: Continuity Check
            sd_symbol            = self.__binance_TWM_StreamingData[sData_symbol]
            sd_aggTrades         = sd_symbol['aggTrades']
            sd_quantityPrecision = sd_symbol['quantityPrecision']
            sd_quotePrecision    = sd_symbol['quotePrecision']
            sd_ls                = sd_aggTrades['lastStream']
            fetchRequest         = None
            func_gnitt           = atmEta_Auxillaries.getNextIntervalTickTimestamp
            #---[1-2-1]: This Is The Very First Stream
            if sd_ls is None:
                fetchRequest = ('timestampBeg_aggTIDEnd',
                                (func_gnitt(intervalID = KLINTERVAL, timestamp = sData_tradeTime_int, mrktReg = None, nTicks = 0),
                                 sData_aggTID-1))
            #---[1-2-2]: Previous Stream Exists
            else:
                sData_aggTID_prev = sd_ls
                #[1-2-2-1]: The Aggregate TID Of This Stream Is Before The Expeceted. Ignore.
                if sData_aggTID < sData_aggTID_prev+1:
                    return (sData_symbol, 'aggTrade', False)
                
                #[1-2-2-2]: The Aggregate TID Of This Stream Is After The Expeceted. Fetch.
                elif sData_aggTID_prev+1 < sData_aggTID:
                    fetchRequest = ('aggTID', 
                                    (sData_aggTID_prev+1, 
                                     sData_aggTID-1))

            #[1-3]: If Need Fetch, Request It
            if fetchRequest is not None:
                reqParams = {'requestID':            None,
                             'fetchTargetRangeType': fetchRequest[0],
                             'fetchTargetRanges':    [fetchRequest[1],]}
                self.__addFetchRequest(symbol        = sData_symbol, 
                                       target        = 'aggTrade', 
                                       cause         = 'stream', 
                                       requestParams = reqParams)
                sd_aggTrades['waitingFetch'] = True

            #[1-4]: Base Data Formatting
            at_base = (sData_aggTID,
                       sData_tradePrice,
                       sData_quantity,
                       sData_maker,
                       sData_lastTID-sData_firstTID+1,
                       sData_tradeTime
                      )

            #[1-5]: Data Formatting & Data Update
            #---[1-5-1]: If Waiting Fetch, Add Base Data To Buffer
            if sd_aggTrades['waitingFetch']:
                sd_aggTrades['buffer'].append(at_base)

            #---[1-5-2]: Continuous Case, Update Intervalized AggTrades
            else:
                #[1-5-2-1]: Collect Base Data
                aggTrades_base = list(sd_aggTrades['buffer'])+[at_base,]

                #[1-5-2-2]: Process Base Data
                sd_aggTrades_aggTrades = sd_aggTrades['aggTrades']
                lastInterval           = sd_aggTrades['lastInterval']
                for at_base in aggTrades_base:
                    #[1-5-2-2-1]: Unpack Base Data
                    (db_aggTID, 
                     db_tradePrice, 
                     db_quantity, 
                     db_maker,
                     db_nTrades,
                     db_tradeTime) = at_base
                    db_intervalTS = func_gnitt(intervalID = KLINTERVAL, timestamp = db_tradeTime, mrktReg = None, nTicks = 0)
                    
                    #[1-5-2-2-2]: Interval Conditions Check
                    #---[1-5-2-2-3-1]: Interval Reversal Check (This Should Not Happen, But Placed Here For Possible Debugging In Case Of A System Logic Flow Failure)
                    if (lastInterval is not None) and (db_intervalTS < lastInterval[ATINDEX_OPENTIME]):
                        self.__logger(message = (f"A Future Interval Timestamp Detected During AggTrade Stream Intervalization. This Means A System Logic Failure. Developer Attention Advised.\n"
                                                 f" * Stream Data:                 {streamData}\n"
                                                 f" * Current  Interval Timestamp: {db_intervalTS}\n"
                                                 f" * Previous Interval Timestamp: {lastInterval[ATINDEX_OPENTIME]}"
                                                ),
                                      logType = 'Warning', 
                                      color   = 'light_red')
                        return (sData_symbol, 'aggTrade', False)
                    #---[1-5-2-2-3-2]: Expected Cases
                    ic_newInterval = (lastInterval is None) or (lastInterval[ATINDEX_OPENTIME] < db_intervalTS)
                    
                    #[1-5-2-2-4]: On New Interval
                    if ic_newInterval:
                        #[1-5-2-2-4-1]: Expired Previous Interval Closing & Gap Filling
                        if lastInterval is not None:
                            li_openTS = lastInterval[ATINDEX_OPENTIME]

                            #[1-5-2-2-4-1-1]: Record The Last Interval As Closed And Save To The Announcement Buffer (If It Is Not Yet Closed)
                            if not lastInterval[ATINDEX_CLOSED]:
                                lastInterval[ATINDEX_CLOSED] = True
                                sd_aggTrades_aggTrades[li_openTS] = tuple(lastInterval)

                            #[1-5-2-2-4-1-2]: Fill In Any Gaps With Dummy AggTrades Interval Data
                            di_openTS = func_gnitt(intervalID = KLINTERVAL, timestamp = li_openTS, mrktReg = None, nTicks = 1)
                            while di_openTS < db_intervalTS:
                                di_openTS_next = func_gnitt(intervalID = KLINTERVAL, timestamp = di_openTS, mrktReg = None, nTicks = 1)
                                dummyInterval = (di_openTS,               #[0]: openTS
                                                 di_openTS_next-1,        #[1]: closeTS
                                                 None,                    #[2]: quantity_buy
                                                 None,                    #[3]: quantity_sell
                                                 None,                    #[4]: nTrades_buy
                                                 None,                    #[5]: nTrades_sell
                                                 None,                    #[6]: notional_buy
                                                 None,                    #[7]: notional_sell
                                                 True,                    #[8]: closed
                                                 _FORMATTEDDATATYPE_DUMMY #[9]: aggTradeType
                                                )
                                sd_aggTrades_aggTrades[di_openTS] = dummyInterval
                                di_openTS = di_openTS_next

                        #[1-5-2-2-4-2]: New Interval Setup
                        db_intervalTS_next = func_gnitt(intervalID = KLINTERVAL, timestamp = db_intervalTS, mrktReg = None, nTicks = 1)
                        lastInterval = [db_intervalTS,              #[0]: openTS
                                        db_intervalTS_next-1,       #[1]: closeTS
                                        0,                          #[2]: quantity_buy
                                        0,                          #[3]: quantity_sell
                                        0,                          #[4]: nTrades_buy
                                        0,                          #[5]: nTrades_sell
                                        0,                          #[6]: notional_buy
                                        0,                          #[7]: notional_sell
                                        False,                      #[8]: closed
                                        _FORMATTEDDATATYPE_STREAMED #[9]: aggTradeType
                                        ]
                        sd_aggTrades['lastInterval'] = lastInterval
                            
                    #[1-5-2-2-5]: Interval Update
                    if db_maker:
                        lastInterval[ATINDEX_QUANTITYSELL] = round(lastInterval[ATINDEX_QUANTITYSELL]+db_quantity, sd_quantityPrecision)
                        lastInterval[ATINDEX_NTRADESSELL]  += db_nTrades
                        lastInterval[ATINDEX_NOTIONALSELL] = round(lastInterval[ATINDEX_NOTIONALSELL]+db_quantity*db_tradePrice, sd_quotePrecision)
                    else:
                        lastInterval[ATINDEX_QUANTITYBUY] = round(lastInterval[ATINDEX_QUANTITYBUY]+db_quantity, sd_quantityPrecision)
                        lastInterval[ATINDEX_NTRADESBUY]  += db_nTrades
                        lastInterval[ATINDEX_NOTIONALBUY] = round(lastInterval[ATINDEX_NOTIONALBUY]+db_quantity*db_tradePrice, sd_quotePrecision)

                    #[1-5-2-2-6]: Interval Tuplization & Announcement Buffer Update
                    sd_aggTrades_aggTrades[db_intervalTS] = tuple(lastInterval)
                    
                #[1-5-2-3]: Clear Buffer
                sd_aggTrades['buffer'].clear()

            #[1-6]: Save The Last Stream
            sd_aggTrades['lastStream'] = sData_aggTID

            #[1-7]: Identifier Return
            if sd_aggTrades['waitingFetch']: return (sData_symbol, 'aggTrade', False)
            else:                            return (sData_symbol, 'aggTrade', True)
        
        #[2]: Exception Handling
        except Exception as e:
            self.__logger(message = (f"Unexpected Error Occurred While Attempting To Process AggTrade Stream Data\n"
                                     f" * Stream Data:    {streamData}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"),
                          logType = 'Error', 
                          color   = 'light_red')
            return (None, 'aggTrade', False)
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
    def __far_addFirstOpenTSSearchRequest(self, requester, requestID, symbol, target):
        #[1]: Symbol Existence Check
        if symbol not in self.__binance_MarketExchangeInfo_Symbols:
            return
        
        #[2]: Target Check
        if target not in ('kline', 'depth', 'aggTrade'):
            return
        
        #[3]: Symbol Request Queue
        foTSsr = self.__binance_firstOpenTSSearchRequests
        if symbol not in foTSsr:
            foTSsr[symbol] = {'kline':    None,
                              'depth':    None,
                              'aggTrade': None}
        
        #[4]: Request Update
        request = {'symbol':      symbol,
                   'requester':   requester,
                   'requestID':   requestID,
                   '_status':     'pending',
                   '_GBVFFuture': None,
                   '_DBVFFuture': None,
                   '_waitUntil':  0}
        foTSsr[symbol][target] = request
    
    def __far_addFetchRequestQueue(self, requester, requestID, symbol, target, fetchTargetRanges):
        #[1]: Source Check
        if requester != 'DATAMANAGER':
            return

        #[2]: Symbol Check
        if symbol not in self.__binance_TWM_StreamingData:
            self.ipcA.sendFARR(targetProcess  = requester, 
                               functionResult = {'status':       'terminate', 
                                                 'data':         None, 
                                                 'fetchedRange': None}, 
                               requestID      = requestID, 
                               complete       = True)
            return

        #[3]: Request Generation
        requestParams = {'requestID':            requestID,
                         'fetchTargetRangeType': 'timestamp',
                         'fetchTargetRanges':    fetchTargetRanges}
        self.__addFetchRequest(symbol = symbol, target = target, cause = 'dm', requestParams = requestParams)

    def __far_pauseMarketDataFetch(self, requester):
        #[1]: Source Check
        if requester != 'DATAMANAGER':
            return
        
        #[2]: Market Data Fetch Pause Flag Update
        self.__binance_fetchRequests_dmCausePause = True

    def __far_continueMarketDataFetch(self, requester):
        #[1]: Source Check
        if requester != 'DATAMANAGER':
            return
        
        #[2]: Market Data Fetch Pause Flag Update
        self.__binance_fetchRequests_dmCausePause = False

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
            return

        #[2]: Server Availability Check
        if not self.__connection_serverAvailable:
            self.ipcA.sendFARR(targetProcess  = 'TRADEMANAGER', 
                               functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'SERVERUNAVAILABLE', 'errorMessage': None},      
                               requestID      = requestID, 
                               complete       = True)
            return

        #[3]: Account Check
        if localID not in self.__binance_client_users:
            self.ipcA.sendFARR(targetProcess  = 'TRADEMANAGER',
                               functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'LOCALIDNOTFOUND', 'errorMessage': None},      
                               requestID      = requestID,
                               complete       = True)
            return

        #[4]: Account Activation Check
        if localID not in self.__binance_activatedAccounts_LocalIDs:
            self.ipcA.sendFARR(targetProcess  = 'TRADEMANAGER', 
                               functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'ACCOUNTNOTACTIVATED', 'errorMessage': None},      
                               requestID      = requestID, 
                               complete       = True)
            return
            
        #[5]: API Rate Limit Check
        if not self.__checkAPIRateLimit(limitType = _BINANCE_RATELIMITTYPE_ORDERS, weight = 1, apply = True):
            self.ipcA.sendFARR(targetProcess  = 'TRADEMANAGER', 
                               functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'CREATEORDER', 'result': False, 'orderResult': None, 'failType': 'APIRATELIMITREACHED', 'errorMessage': None},      
                               requestID      = requestID, 
                               complete       = True)
            return
            
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
    def __far_registerKlineStreamSubscription(self, requester, subscriptionID, currencySymbol):
        #[1]: Data Formatting
        if currencySymbol not in self.__binance_TWM_StreamingData:
            self.__initializeStreamingDataForSymbol(symbol = currencySymbol)
        sd = self.__binance_TWM_StreamingData[currencySymbol]

        #[2}: Subscription
        if subscriptionID is None:
            fID_kline    = 'onKlineStreamReceival'
            fID_depth    = 'onDepthStreamReceival'
            fID_aggTrade = 'onAggTradeStreamReceival'
        else:
            fID_kline    = f'onKlineStreamReceival_{subscriptionID}'
            fID_depth    = f'onDepthStreamReceival_{subscriptionID}'
            fID_aggTrade = f'onAggTradeStreamReceival_{subscriptionID}'
        subscription = {'subscriber':     requester,
                        'subscriptionID': subscriptionID,
                        'fID_kline':      fID_kline,
                        'fID_depth':      fID_depth,
                        'fID_aggTrade':   fID_aggTrade,
                        'closedOnly':     False}
        
        #[3]: Fetch Priority
        subscribers = set(_subscription['subscriber'] for _subscription in sd['subscriptions']) | {requester,}
        subscribers_hasAnalyzer = False
        subscribers_hasGUI      = False
        for subscriber in subscribers:
            if   subscriber.startswith('ANALYZER'): subscribers_hasAnalyzer = True
            elif subscriber == 'GUI':               subscribers_hasGUI      = True
        if   subscribers_hasAnalyzer: newFetchPriority = 0
        elif subscribers_hasGUI:      newFetchPriority = 1
        else:                         newFetchPriority = 2
        if currencySymbol in self.__binance_fetchRequests_SymbolsByPriority[sd['fetchPriority']]: self.__binance_fetchRequests_SymbolsByPriority[sd['fetchPriority']].remove(currencySymbol)
        if currencySymbol in self.__binance_fetchRequests:                                        self.__binance_fetchRequests_SymbolsByPriority[newFetchPriority].add(currencySymbol)

        #[4]: Finally
        sd['subscriptions'].append(subscription)
        sd['fetchPriority'] = newFetchPriority
    
    def __far_unregisterKlineStreamSubscription(self, requester, subscriptionID, currencySymbol):
        #[1]: Subscription Check
        if currencySymbol not in self.__binance_TWM_StreamingData:
            return

        #[2]: Instance
        sd = self.__binance_TWM_StreamingData[currencySymbol]

        #[3]: Subscription Search & Removal
        subscriptionIndex = None
        for sIndex, subscription in enumerate(sd['subscriptions']):
            if (subscription['subscriber'] == requester) and (subscription['subscriptionID'] == subscriptionID): 
                subscriptionIndex = sIndex
                break

        #[4]: Fetch Priority Re-evalution (If needed)
        subscribers = set(_subscription['subscriber'] for sIndex, _subscription in enumerate(sd['subscriptions']) if sIndex != subscriptionIndex)
        subscribers_hasAnalyzer = False
        subscribers_hasGUI      = False
        for subscriber in subscribers:
            if   subscriber.startswith('ANALYZER'): subscribers_hasAnalyzer = True
            elif subscriber == 'GUI':               subscribers_hasGUI      = True
        if   subscribers_hasAnalyzer: newFetchPriority = 0
        elif subscribers_hasGUI:      newFetchPriority = 1
        else:                         newFetchPriority = 2
        if currencySymbol in self.__binance_fetchRequests_SymbolsByPriority[sd['fetchPriority']]: self.__binance_fetchRequests_SymbolsByPriority[sd['fetchPriority']].remove(currencySymbol)
        if currencySymbol in self.__binance_fetchRequests:                                        self.__binance_fetchRequests_SymbolsByPriority[newFetchPriority].add(currencySymbol)

        #[5]: Finally
        if subscriptionIndex is not None: sd['subscriptions'].pop(subscriptionIndex)
        sd['fetchPriority'] = newFetchPriority
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------