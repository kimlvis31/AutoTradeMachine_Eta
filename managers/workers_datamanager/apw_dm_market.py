#ATM Modules
import atmEta_IPC
import atmEta_Auxillaries
import atmEta_Constants

#Python Modules
import time
import os
import termcolor
import pprint
import json
import traceback
import shutil
import threading
import queue
import psycopg2
import re
from collections        import deque
from datetime           import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from psycopg2.pool      import ThreadedConnectionPool
from psycopg2.extras    import execute_values, execute_batch

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

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

FORMATTEDDATATYPE_FETCHED    = 0
FORMATTEDDATATYPE_EMPTY      = 1
FORMATTEDDATATYPE_DUMMY      = 2
FORMATTEDDATATYPE_STREAMED   = 3
FORMATTEDDATATYPE_INCOMPLETE = 4

COMMONDATAINDEXES = {'openTime':  {'kline': KLINDEX_OPENTIME,  'depth': DEPTHINDEX_OPENTIME,  'aggTrade': ATINDEX_OPENTIME},
                     'closeTime': {'kline': KLINDEX_CLOSETIME, 'depth': DEPTHINDEX_CLOSETIME, 'aggTrade': ATINDEX_CLOSETIME},
                     'closed':    {'kline': KLINDEX_CLOSED,    'depth': DEPTHINDEX_CLOSED,    'aggTrade': ATINDEX_CLOSED},
                     'source':    {'kline': KLINDEX_SOURCE,    'depth': DEPTHINDEX_SOURCE,    'aggTrade': ATINDEX_SOURCE}}

KLINTERVAL   = atmEta_Constants.KLINTERVAL
KLINTERVAL_S = atmEta_Constants.KLINTERVAL_S

_PERIODICPROCESSINTERVAL_NS = 100e6
_STREAMDATASAVEINTERVAL_S   = 5
_FETCHPAUSETHRESHOLD        = 14400
_FETCHSAVECHUNKSIZE         = 10000
_FETCHSPEEDNSAMPLES         = 100

_MARKETDATA_ANNOUNCEMENT_KEYS = {'precisions', 
                                 'baseAsset', 
                                 'quoteAsset', 
                                 'kline_firstOpenTS', 
                                 'depth_firstOpenTS', 
                                 'aggTrade_firstOpenTS', 
                                 'klines_availableRanges', 
                                 'depths_availableRanges', 
                                 'aggTrades_availableRanges', 
                                 'klines_dummyRanges', 
                                 'depths_dummyRanges', 
                                 'aggTrades_dummyRanges', 
                                 'collecting',
                                 'info_server'}

PGQUERY_READFROMDB = {'kline':    """SELECT t_open, t_close, p_open, p_high, p_low, p_close, ntrades, v, q, v_tb, q_tb, ktype
                                     FROM klines
                                     WHERE symbol = %s AND to_timestamp(%s) <= time AND time <= to_timestamp(%s)
                                     ORDER BY time ASC;
                                  """,
                      'depth':    """SELECT t_open, t_close, bids5, bids4, bids3, bids2, bids1, bids0, asks0, asks1, asks2, asks3, asks4, asks5, dtype
                                     FROM depths
                                     WHERE symbol = %s AND to_timestamp(%s) <= time AND time <= to_timestamp(%s)
                                     ORDER BY time ASC;
                                  """,
                      'aggTrade': """SELECT t_open, t_close, quantity_buy, quantity_sell, ntrades_buy, ntrades_sell, notional_buy, notional_sell, attype
                                     FROM aggtrades
                                     WHERE symbol = %s AND to_timestamp(%s) <= time AND time <= to_timestamp(%s)
                                     ORDER BY time ASC;
                                  """}

PGQUERY_FETCHSAVE_DATA = {'kline':    """INSERT INTO klines (time, symbol, t_open, t_close, p_open, p_high, p_low, p_close, ntrades, v, q, v_tb, q_tb, ktype)
                                         VALUES %s
                                      """,
                          'depth':    """INSERT INTO depths (time, symbol, t_open, t_close, bids5, bids4, bids3, bids2, bids1, bids0, asks0, asks1, asks2, asks3, asks4, asks5, dtype)
                                         VALUES %s
                                      """,
                          'aggTrade': """INSERT INTO aggTrades (time, symbol, t_open, t_close, quantity_buy, quantity_sell, ntrades_buy, ntrades_sell, notional_buy, notional_sell, attype)
                                         VALUES %s
                                      """}
PGTEMPLATE_FETCHSAVE_DATA = {'kline':    "(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                             'depth':    "(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                             'aggTrade': "(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"}
PGQUERY_FETCHSAVE_ARANGES = {'kline':    "UPDATE descriptors SET klines_availableranges = %s::jsonb WHERE symbol = %s",
                             'depth':    "UPDATE descriptors SET depths_availableranges = %s::jsonb WHERE symbol = %s",
                             'aggTrade': "UPDATE descriptors SET aggTrades_availableranges = %s::jsonb WHERE symbol = %s"}
PGQUERY_FETCHSAVE_DRANGES = {'kline':    "UPDATE descriptors SET klines_dummyranges = %s::jsonb WHERE symbol = %s",
                             'depth':    "UPDATE descriptors SET depths_dummyranges = %s::jsonb WHERE symbol = %s",
                             'aggTrade': "UPDATE descriptors SET aggTrades_dummyranges = %s::jsonb WHERE symbol = %s"}

def mergeRangeToRanges(ranges, range_new):
    if ranges is None: 
        return [range_new.copy(),]
    ranges_new = [rng.copy() for rng in ranges]
    ranges_new.append(range_new.copy())
    ranges_new.sort(key = lambda x: x[0])
    ranges_merged = []
    for nr in ranges_new:
        if not ranges_merged: 
            ranges_merged.append(nr)
        else:
            if ranges_merged[-1][1]+1 == nr[0]: ranges_merged[-1][1] = nr[1]
            else:                               ranges_merged.append(nr)
    return ranges_merged

def mergeRangesToRanges(ranges1, ranges2):
    ranges1 = ranges1 or []
    ranges2 = ranges2 or []
    ranges_new = sorted((r.copy() for r in ranges1+ranges2), key = lambda x: x[0])
    ranges_merged = []
    for nr in ranges_new:
        if not ranges_merged: 
            ranges_merged.append(nr)
        else:
            if ranges_merged[-1][1]+1 == nr[0]: ranges_merged[-1][1] = nr[1]
            else:                               ranges_merged.append(nr)
    return ranges_merged

def subtractRangeFromRanges(ranges, range_sub):
    if not ranges:
        return []
    ranges_new = []
    range2     = range_sub
    for range1 in ranges:
        classification = getRangesClassification(range1 = range1, range2 = range2)
        #[1]: No Overlap
        if classification in (0b0000, 0b1111):
            ranges_new.append(range1)
        #[2]: Overlap On The Left Of Range 1 And The Right Of Range 2
        elif classification == 0b1011:
            rBeg_new = range2[1]+1
            if rBeg_new <= range1[1]:
                ranges_new.append([rBeg_new, range1[1]])
        #[3]: Overlap On The Right Of Range 1 And The Left Of Range 2
        elif classification == 0b0010:
            rEnd_new = range2[0]-1
            if range1[0] <= rEnd_new:
                ranges_new.append([range1[0], rEnd_new])
        #[4]: Range 2 Is Completely Inside Of DR1
        elif classification == 0b0011:
            rLeft_beg  = range2[0]-1
            rRight_end = range2[1]+1
            if range1[0] <= rLeft_beg:
                ranges_new.append([range1[0], rLeft_beg])
            if rRight_end <= range1[1]:
                ranges_new.append([rRight_end, range1[1]])
    return ranges_new

def subtractRangesFromRanges(ranges1, ranges2):
    if not ranges1:
        return []
    if not ranges2:
        return ranges1
    ranges_new = ranges1
    for range2 in ranges2:
        ranges_new = subtractRangeFromRanges(ranges = ranges_new, range_sub = range2)
        if not ranges_new:
            break
    return ranges_new

"""
classification == 0b1111: DR2 completely outside on the left of DR1
classification == 0b1011: the right of DR2 and the left of DR1 overlapped
classification == 0b0011: DR2 completely inside of DR1
classification == 0b0010: the left of DR2 and the right of DR1 overlapped
classification == 0b0000: DR2 completely outside on the right of DR1
classification == 0b1010: DR1 completely inside of DR2
"""
def getRangesClassification(range1, range2):
    classification = 0b0000
    classification += 0b1000*(0 <  range1[0]-range2[0])
    classification += 0b0100*(0 <  range1[0]-range2[1])
    classification += 0b0010*(0 <= range1[1]-range2[0])
    classification += 0b0001*(0 <= range1[1]-range2[1])
    return classification

def checkNewRangeOverlap(ranges, range_new):
    grc = getRangesClassification
    return any(grc(bRange, range_new) not in (0b0000, 0b1111) for bRange in ranges)

class Worker:
    def __init__(self, path_project, dmConfig, ipcA, portNumber):
        #[1]: Base Parameters & Instances
        path_dbFolder = os.path.join(path_project, 'data', 'db')
        self.__path_project  = path_project
        self.__path_dbFolder = path_dbFolder
        self.__dmConfig      = dmConfig
        self.__ipcA          = ipcA

        #[2]: Task Data
        self.__marketData        = dict()
        self.__collectingSymbols = dict()
        self.__readCollectingSymbolsList()
        self.__fetchRequests = {'pending': {dataType: set()  for dataType in ('kline', 'depth', 'aggTrade')},
                                'active':  {dataType: dict() for dataType in ('kline', 'depth', 'aggTrade')},
                                'pauseRequested':     False,
                                'validBufferLength':  0,
                                'lastProcessTime_ns': None}
        self.__fetchStatus = {'lastFetched':               None,
                              'remainingRanges_kline':     None,
                              'remainingRanges_depth':     None,
                              'remainingRanges_aggTrade':  None,
                              'fetchSpeed_kline':          None,
                              'fetchSpeed_depth':          None,
                              'fetchSpeed_aggTrade':       None,
                              'estimatedTimeOfCompletion': None}
        
        #[3]: Initial PRD Announcement
        for processName in ('GUI', 'TRADEMANAGER', 'SIMULATIONMANAGER', 'NEURALNETWORKMANAGER'):
            ipcA.sendPRDEDIT(targetProcess = processName, prdAddress = 'CURRENCIES', prdContent = dict())
        ipcA.sendPRDEDIT(targetProcess = 'GUI',        prdAddress = 'FETCHSTATUS',      prdContent = self.__fetchStatus.copy())
        ipcA.sendPRDEDIT(targetProcess = 'BINANCEAPI', prdAddress = 'STREAMINGSYMBOLS', prdContent = set(symbol for symbol, coll in self.__collectingSymbols.items() if coll['collectingStream']))

        #[4]: PostgreSQL Configuration
        self.__pg_config = {'dbname':   dmConfig['pg_dbName'],
                            'user':     dmConfig['pg_user'],
                            'password': dmConfig['pg_password'],
                            'port':     portNumber,
                            'host':     'localhost'}
        
        #[5]: FAR Handlers Setup
        ipcA.addFARHandler('registerCurrency',                    self.__far_registerCurrency,                    executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #BINANCEAPI
        ipcA.addFARHandler('onCurrencyInfoUpdate',                self.__far_onCurrencyInfoUpdate,                executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #BINANCEAPI
        ipcA.addFARHandler('onKlineStreamReceival',               self.__far_onKlineStreamReceival,               executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #BINANCEAPI
        ipcA.addFARHandler('onDepthStreamReceival',               self.__far_onDepthStreamReceival,               executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #BINANCEAPI
        ipcA.addFARHandler('onAggTradeStreamReceival',            self.__far_onAggTradeStreamReceival,            executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #BINANCEAPI
        ipcA.addFARHandler('readMarketDBStatus',                  self.__far_readDBStatus,                        executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #GUI
        ipcA.addFARHandler('setMarketDataCollection',             self.__far_setMarketDataCollection,             executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #GUI
        ipcA.addFARHandler('compressMarketDB',                    self.__far_compressMarketDB,                    executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #GUI
        ipcA.addFARHandler('resetMarketData',                     self.__far_resetMarketData,                     executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #GUI
        ipcA.addFARHandler('refetchDummyMarketData',              self.__far_refetchDummyMarketData,              executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #GUI
        ipcA.addFARHandler('loadDummyMarketDataFromLocalNetwork', self.__far_loadDummyMarketDataFromLocalNetwork, executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #GUI
        ipcA.addFARHandler('fetchMarketData',                     self.__far_fetchMarketData,                     executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #COMMON
        ipcA.addFARHandler('registerCurrecnyInfoSubscription',    self.__far_registerCurrecnyInfoSubscription,    executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #COMMON
        ipcA.addFARHandler('unregisterCurrecnyInfoSubscription',  self.__far_unregisterCurrecnyInfoSubscription,  executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #COMMON

        #[6]: Task Handling Setup
        #---[6-1]: Tasks Queue, Worker Thread, Task Pool, and PostgreSQL Pool
        self.__taskQueue = queue.Queue()
        self.__wThread   = threading.Thread(target = self.__processLoop, args = (), daemon = False)
        self.__taskPool  = ThreadPoolExecutor(max_workers=10, thread_name_prefix="apw_dm_market_tpool")
        self.__pgPool    = self.__getPGThreadedConnectionPool(minConn = 1, maxConn = 12)

        #---[6-2]: Write-Designated Connection
        if self.__pgPool is not None:
            self.__pgConn_write = self.__pgPool.getconn()
            self.__pgConn_write.autocommit = False
            self.__pgCursor_write = self.__pgConn_write.cursor()
        else:
            self.__pgConn_write   = None
            self.__pgCursor_write = None

        #---[6-3]: Periodic Processes (Regularly Processed Functions Whenever Queue Empty Timeout Occurs)
        self.__periodicProcesses = {'saveStreamedData':  self.__pp_saveStreamedData,
                                    'saveFetchedData':   self.__pp_saveFetchedData,
                                    'sendFetchRequests': self.__pp_sendFetchRequests}
        self.__periodicProcess_lastRun_ns            = 0
        self.__periodicProcess_lastStreamDataSaved_s = 0
        
        #---[6-4]: Queue-Based Task Handlers
        self.__taskHandlers = {'initialDBRead':                       self.__th_initialDBRead,
                               'setMarketDataCollection':             self.__th_setMarketDataCollection,
                               'registerCurrency':                    self.__th_registerCurrency,
                               'onCurrencyInfoUpdate':                self.__th_onCurrencyInfoUpdate,
                               'saveFirstOpenTS':                     self.__th_saveFirstOpenTS,
                               'saveDataFetchResult':                 self.__th_saveDataFetchResult,
                               'onDataStreamReceival':                self.__th_onDataStreamReceival,
                               'compressDB':                          self.__th_compressDB,
                               'resetMarketData':                     self.__th_resetMarketData,
                               'refetchDummyMarketData':              self.__th_refetchDummyMarketData,
                               'loadDummyMarketDataFromLocalNetwork': self.__th_loadDummyMarketDataFromLocalNetwork,
                               'registerCurrencyInfoSubscription':    self.__th_registerCurrencyInfoSubscription,
                               'unregisterCurrencyInfoSubscription':  self.__th_unregisterCurrencyInfoSubscription}
        
        #[7]: Initial Task Completion Flag
        self.__initialTaskComplete = False

    #Configuration ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __readCollectingSymbolsList(self):
        #[1]: Configuration File Read
        try:
            config_dir = os.path.join(self.__path_project, 'configs', 'dmConfig_cSymbols.config')
            with open(config_dir, 'r') as f:
                config_loaded = json.load(f)
        except: 
            config_loaded = dict()
        #[2]: Contents Verification
        config_valid = dict()
        if isinstance(config_loaded, dict):
            for symbol, val in config_loaded.items():
                if not isinstance(val, dict):
                    continue
                collStrm = val.get('collectingStream',     False)
                collHist = val.get('collectingHistorical', False)
                if not collStrm and collHist:
                    collHist = False
                config_valid[symbol] = {'collectingStream':     collStrm,
                                        'collectingHistorical': collHist}
        #[3]: Update and save the configuration
        self.__collectingSymbols = config_valid
        self.__saveCollectingSymbolsList()

    def __saveCollectingSymbolsList(self):
        #[1]: Formatting
        config = self.__collectingSymbols

        #[2]: Save the reformatted configuration file
        config_dir = os.path.join(self.__path_project, 'configs', 'dmConfig_cSymbols.config')
        try:
            with open(config_dir, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Save Data Manager Market Data Configuration. User Attention Strongly Advised"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')
    #Configuration END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #System -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __getPGThreadedConnectionPool(self, minConn, maxConn):
        nAttempts     = 0
        nAttempts_max = 5
        while nAttempts < nAttempts_max:
            try:
                pgPool = ThreadedConnectionPool(minconn = minConn, maxconn = maxConn, **self.__pg_config)
                return pgPool
            except Exception as e:
                print(termcolor.colored((f"    * PostgreSQL Connection Attempt Failed [Attmpt: {nAttempts+1} / {nAttempts_max}].\n"
                                        f"      * Error:          {e}\n"
                                        f"      * Detailed Trace: {traceback.format_exc()}"
                                        ), 
                                        'light_red'))
                nAttempts += 1
                time.sleep(10)
        return None
    
    def __processLoop(self):
        #[1]: Instances
        tQueue               = self.__taskQueue
        tHandlers            = self.__taskHandlers
        runPeriodicProcesses = self.runPeriodicProcesses
        logger               = self.__logger
        
        #[2]: Task Handling Loop
        while True:
            #[2-1]: Handling Attempt
            task = None
            try:
                #[2-1-1]: Task
                task = tQueue.get(timeout = 0.01)
                #[2-1-2]: Termination Check
                if task is None:
                    tQueue.task_done()
                    break
                #[2-3-3]: Task Handling
                tHandlers[task['type']](task = task)
                tQueue.task_done()
            #[2-2]: Empty Queue & Periodic Processes
            except queue.Empty:
                continue
            #[2-3]: Exception Handling
            except Exception as e: 
                if task is not None: tQueue.task_done()
                logger(message = (f"An Unexpected Error Occurred While Attempting To Handle A Task\n"
                                  f" * Error:          {e}\n"
                                  f" * Detailed Trace: {traceback.format_exc()}"),
                       logType = 'Error', 
                       color   = 'light_red')
            #[2-4]: Periodic Process
            finally:
                runPeriodicProcesses()
        
        #[3]: Final Periodic Processes
        runPeriodicProcesses(ignoreTimer = True)

        #[4]: Thread Pools Close
        self.__taskPool.shutdown(wait=True)
        self.__pgPool.closeall()

    def runPeriodicProcesses(self, ignoreTimer = False):
        t_current_ns = time.perf_counter_ns()
        if not ignoreTimer:
            if t_current_ns-self.__periodicProcess_lastRun_ns < _PERIODICPROCESSINTERVAL_NS:
                return
        try:
            for pProcess in self.__periodicProcesses.values(): 
                pProcess()
            self.__periodicProcess_lastRun_ns = t_current_ns
        except Exception as e: 
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting Perform Periodic Processes\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"),
                          logType = 'Error', 
                          color   = 'light_red')

    def start(self):
        #[1]: Initial DB Read Task
        task = {'type':      'initialDBRead',
                'requester': None,
                'requestID': None,
                'params':    None}
        self.__taskQueue.put(task)

        #[2]: Task Handler Thread Start
        self.__wThread.start()

    def terminate(self):
        self.__taskQueue.put(None)
        if self.__wThread.is_alive():
            self.__wThread.join()

    def __logger(self, message, logType, color):
        if not self.__dmConfig[f'print_{logType}']:
            return
        time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
        msg      = f"[DATAMANAGER-MARKETDATAWORKER-{time_str}] {message}"
        print(termcolor.colored(msg, color))
    
    def initialTaskComplete(self):
        return self.__initialTaskComplete
    #System END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Periodic Processes -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __pp_saveStreamedData(self):
        #[1]: Timer & DB Condition Check
        t_current_s = time.perf_counter()
        if t_current_s-self.__periodicProcess_lastStreamDataSaved_s < _STREAMDATASAVEINTERVAL_S: return
        self.__periodicProcess_lastStreamDataSaved_s = t_current_s
        if self.__checkDBBusy(): return

        #[2]: Instances
        pgConn   = self.__pgConn_write
        pgCursor = self.__pgCursor_write
        md       = self.__marketData
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR

        #[3]: Streamed Data Collection
        sqlParams_data_total    = {'kline': [], 'depth': [], 'aggTrade': []}
        sqlParams_aRanges_total = {'kline': [], 'depth': [], 'aggTrade': []}
        sqlParams_dRanges_total = {'kline': [], 'depth': [], 'aggTrade': []}
        aRanges_new_updated = dict()
        dRanges_new_updated = dict()
        for symbol, md_symbol in md.items():
            for dataType in ('kline', 'depth', 'aggTrade'):
                #[3-1]: Stream Range Check
                sData = md_symbol[f'_stream_{dataType}s']
                sData_data   = sData[f'{dataType}s']
                sData_ranges = sData['ranges']
                if not sData_ranges: continue

                #[3-2]: Stream Dummy Range
                sData_ranges_dummy = None
                dIdx_openTS  = COMMONDATAINDEXES['openTime'][dataType]
                dIdx_closeTS = COMMONDATAINDEXES['closeTime'][dataType]
                dIdx_source  = COMMONDATAINDEXES['source'][dataType]
                for dl in sData_data:
                    dl_source = dl[dIdx_source]
                    if dl_source == FORMATTEDDATATYPE_DUMMY or dl_source == FORMATTEDDATATYPE_INCOMPLETE:
                        dl_openTS  = dl[dIdx_openTS]
                        dl_closeTS = dl[dIdx_closeTS]
                        if sData_ranges_dummy is None: sData_ranges_dummy = [[dl_openTS, dl_closeTS],]
                        else:
                            if sData_ranges_dummy[-1][1]+1 == dl_openTS: sData_ranges_dummy[-1][1] = dl_closeTS
                            else:                                        sData_ranges_dummy.append([dl_openTS, dl_closeTS])

                #[3-3]: Overlap Check
                overlapped = set()
                aRanges = md_symbol[f'{dataType}s_availableRanges']
                dRanges = md_symbol[f'{dataType}s_dummyRanges']
                if aRanges is not None and any(checkNewRangeOverlap(ranges = aRanges, range_new = sr) for sr in sData_ranges):
                    overlapped.add('available')
                if dRanges is not None and sData_ranges_dummy is not None and any(checkNewRangeOverlap(ranges = dRanges, range_new = dr) for dr in sData_ranges_dummy): 
                    overlapped.add('dummy')
                if overlapped:
                    self.__logger(message = (f"An Overlap Detected Between The Data Ranges And The Streamed Data. The Corresponding Data Will Be Disposed"
                                             f" * Symbol:                {symbol}\n"
                                             f" * Data Type:             {dataType}\n"
                                             f" * Overlapped             {overlapped}\n"
                                             f" * Available Ranges:      {aRanges}\n"
                                             f" * Dummy Ranges:          {dRanges}\n"
                                             f" * Streamed Ranges:       {sData_ranges}\n"
                                             f" * Streamed Dummy Ranges: {sData_ranges_dummy}"
                                            ), 
                                  logType = 'Warning', 
                                  color   = 'light_red')
                    sData_data.clear()
                    sData_ranges.clear()
                    continue

                #[3-4]: New Data Ranges
                aRanges_new = mergeRangesToRanges(ranges1 = aRanges, ranges2 = sData_ranges)
                dRanges_new = mergeRangesToRanges(ranges1 = dRanges, ranges2 = sData_ranges_dummy) if sData_ranges_dummy is not None else None

                #[3-5]: SQL Parameters
                #---[3-5-1]: Kline
                if dataType == 'kline':
                    sqlParams_data = [(kl[KLINDEX_OPENTIME],         # openTS (for to_timestamp(%s))
                                       symbol,                       # symbol
                                       kl[KLINDEX_OPENTIME],         # t_open
                                       kl[KLINDEX_CLOSETIME],        # t_close
                                       kl[KLINDEX_OPENPRICE],        # p_open
                                       kl[KLINDEX_HIGHPRICE],        # p_high
                                       kl[KLINDEX_LOWPRICE],         # p_low
                                       kl[KLINDEX_CLOSEPRICE],       # p_close
                                       kl[KLINDEX_NTRADES],          # nTrades
                                       kl[KLINDEX_VOLBASE],          # base asset volume
                                       kl[KLINDEX_VOLQUOTE],         # quote asset volume
                                       kl[KLINDEX_VOLBASETAKERBUY],  # base asset volume (taker-buy)
                                       kl[KLINDEX_VOLQUOTETAKERBUY], # quote asset volume (taker-buy)
                                       kl[KLINDEX_SOURCE]            # kline type
                                      ) for kl in sData_data if kl[KLINDEX_SOURCE] != FORMATTEDDATATYPE_DUMMY]
                    sqlParams_aRanges = (json.dumps(aRanges_new), symbol)
                    sqlParams_dRanges = (json.dumps(dRanges_new), symbol) if dRanges_new is not None else None

                #---[3-5-2]: Depth
                elif dataType == 'depth':
                    sqlParams_data = [(depth[DEPTHINDEX_OPENTIME],  # openTS (for to_timestamp(%s))
                                       symbol,                      # symbol
                                       depth[DEPTHINDEX_OPENTIME],  # t_open
                                       depth[DEPTHINDEX_CLOSETIME], # t_close
                                       depth[DEPTHINDEX_BIDS5],     # bids5 (-4.0% ~ -5.0%)
                                       depth[DEPTHINDEX_BIDS4],     # bids4 (-3.0% ~ -4.0%)
                                       depth[DEPTHINDEX_BIDS3],     # bids3 (-2.0% ~ -3.0%)
                                       depth[DEPTHINDEX_BIDS2],     # bids2 (-1.0% ~ -2.0%)
                                       depth[DEPTHINDEX_BIDS1],     # bids1 (-0.2% ~ -1.0%)
                                       depth[DEPTHINDEX_BIDS0],     # bids0 ( 0.0% ~ -0.2%)
                                       depth[DEPTHINDEX_ASKS0],     # asks0 ( 0.0% ~  0.2%)
                                       depth[DEPTHINDEX_ASKS1],     # asks1 ( 0.2% ~  1.0%)
                                       depth[DEPTHINDEX_ASKS2],     # asks2 ( 1.0% ~  2.0%)
                                       depth[DEPTHINDEX_ASKS3],     # asks3 ( 2.0% ~  3.0%)
                                       depth[DEPTHINDEX_ASKS4],     # asks4 ( 3.0% ~  4.0%)
                                       depth[DEPTHINDEX_ASKS5],     # asks5 ( 4.0% ~  5.0%)
                                       depth[DEPTHINDEX_SOURCE]     # depth type
                                      ) for depth in sData_data if depth[DEPTHINDEX_SOURCE] != FORMATTEDDATATYPE_DUMMY]
                    sqlParams_aRanges = (json.dumps(aRanges_new), symbol)
                    sqlParams_dRanges = (json.dumps(dRanges_new), symbol) if dRanges_new is not None else None

                #---[3-5-3]: AggTrade
                elif dataType == 'aggTrade':
                    sqlParams_data = [(at[ATINDEX_OPENTIME],     # openTS (for to_timestamp(%s))
                                       symbol,                   # symbol
                                       at[ATINDEX_OPENTIME],     # t_open
                                       at[ATINDEX_CLOSETIME],    # t_close
                                       at[ATINDEX_QUANTITYBUY],  # quantity_buy
                                       at[ATINDEX_QUANTITYSELL], # quantity_sell
                                       at[ATINDEX_NTRADESBUY],   # ntrades_buy
                                       at[ATINDEX_NTRADESSELL],  # ntrades_sell
                                       at[ATINDEX_NOTIONALBUY],  # notional_buy
                                       at[ATINDEX_NOTIONALSELL], # notional_sell
                                       at[ATINDEX_SOURCE]        # aggTrade type
                                      ) for at in sData_data if at[ATINDEX_SOURCE] != FORMATTEDDATATYPE_DUMMY]
                    sqlParams_aRanges = (json.dumps(aRanges_new), symbol)
                    sqlParams_dRanges = (json.dumps(dRanges_new), symbol) if dRanges_new is not None else None

                #[3-6]: Collection
                #---[3-6-1]: Data
                sqlParams_data_total[dataType].extend(sqlParams_data)
                #---[3-6-2]: Available Ranges
                sqlParams_aRanges_total[dataType].append(sqlParams_aRanges)
                if symbol not in aRanges_new_updated: aRanges_new_updated[symbol] = dict()
                aRanges_new_updated[symbol][dataType] = aRanges_new
                #---[3-6-3]: Dummy Ranges
                if dRanges_new is not None: 
                    sqlParams_dRanges_total[dataType].append(sqlParams_dRanges)
                    if symbol not in dRanges_new_updated: dRanges_new_updated[symbol] = dict()
                    dRanges_new_updated[symbol][dataType] = dRanges_new

                #[3-7]: Buffer Clearing
                sData_data.clear()
                sData_ranges.clear()

        #[4]: DB Update
        #---[4-1]: Queries
        #------[4-1-1]: Kline
        if sqlParams_data_total['kline']:
            pgQuery_klines_data = """INSERT INTO klines (time, symbol, t_open, t_close, p_open, p_high, p_low, p_close, ntrades, v, q, v_tb, q_tb, ktype)
                                     VALUES %s
                                  """
            pgQuery_klines_aRanges = "UPDATE descriptors SET klines_availableranges = %s WHERE symbol = %s"
            pgQuery_klines_dRanges = "UPDATE descriptors SET klines_dummyranges = %s WHERE symbol = %s" if sqlParams_dRanges_total['kline'] else None
        else:
            pgQuery_klines_data    = None
            pgQuery_klines_aRanges = None
            pgQuery_klines_dRanges = None
        #------[4-1-2]: Depth
        if sqlParams_data_total['depth']:
            pgQuery_depths_data = """INSERT INTO depths (time, symbol, t_open, t_close, bids5, bids4, bids3, bids2, bids1, bids0, asks0, asks1, asks2, asks3, asks4, asks5, dtype)
                                     VALUES %s
                                  """
            pgQuery_depths_aRanges = "UPDATE descriptors SET depths_availableranges = %s WHERE symbol = %s"
            pgQuery_depths_dRanges = "UPDATE descriptors SET depths_dummyranges = %s WHERE symbol = %s" if sqlParams_dRanges_total['depth'] else None
        else:
            pgQuery_depths_data    = None
            pgQuery_depths_aRanges = None
            pgQuery_depths_dRanges = None
        #------[4-1-3]: AggTrade
        if sqlParams_data_total['aggTrade']:
            pgQuery_aggTrades_data = """INSERT INTO aggTrades (time, symbol, t_open, t_close, quantity_buy, quantity_sell, ntrades_buy, ntrades_sell, notional_buy, notional_sell, attype)
                                        VALUES %s
                                     """
            pgQuery_aggTrades_aRanges = "UPDATE descriptors SET aggTrades_availableranges = %s WHERE symbol = %s"
            pgQuery_aggTrades_dRanges = "UPDATE descriptors SET aggTrades_dummyranges = %s WHERE symbol = %s" if sqlParams_dRanges_total['aggTrade'] else None
        else:
            pgQuery_aggTrades_data    = None
            pgQuery_aggTrades_aRanges = None
            pgQuery_aggTrades_dRanges = None
        #---[4-2]: Queries Execution
        dbUpdated = False
        if any(cd for cd in sqlParams_data_total.values()):
            #[4-2-1]: Expeceted Behavior
            try:
                #[4-2-1-1]: Klines
                if pgQuery_klines_data is not None:
                    execute_values(cur       = pgCursor, 
                                   sql       = pgQuery_klines_data, 
                                   argslist  = sqlParams_data_total['kline'],
                                   template  = "(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                   page_size = 1000)
                    pgCursor.executemany(pgQuery_klines_aRanges, sqlParams_aRanges_total['kline'])
                if pgQuery_klines_dRanges is not None:
                    pgCursor.executemany(pgQuery_klines_dRanges, sqlParams_dRanges_total['kline'])
                #[4-2-1-2]: Depths
                if pgQuery_depths_data is not None:
                    execute_values(cur       = pgCursor, 
                                   sql       = pgQuery_depths_data, 
                                   argslist  = sqlParams_data_total['depth'],
                                   template  = "(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                   page_size = 1000)
                    pgCursor.executemany(pgQuery_depths_aRanges, sqlParams_aRanges_total['depth'])
                if pgQuery_depths_dRanges is not None:
                    pgCursor.executemany(pgQuery_depths_dRanges, sqlParams_dRanges_total['depth'])
                #[4-2-1-3]: AggTrades
                if pgQuery_aggTrades_data is not None:
                    execute_values(cur       = pgCursor, 
                                   sql       = pgQuery_aggTrades_data, 
                                   argslist  = sqlParams_data_total['aggTrade'],
                                   template  = "(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                   page_size = 1000)
                    pgCursor.executemany(pgQuery_aggTrades_aRanges, sqlParams_aRanges_total['aggTrade'])
                if pgQuery_aggTrades_dRanges is not None:
                    pgCursor.executemany(pgQuery_aggTrades_dRanges, sqlParams_dRanges_total['aggTrade'])
                #[4-2-1-4]: Commit
                pgConn.commit()
                dbUpdated = True
            #[4-2-2]: Index Corruption Handling (Auto REINDEX)
            except psycopg2.errors.IndexCorrupted as e:
                pgConn.rollback()
                try:
                    self.__logger(message = (f"Index Corruption Detected While Attempting To Update DB With The The Streamed Data. Attempting Auto REINDEX.\n"
                                             f" * Error: {e}"),
                                  logType = 'Warning',
                                  color   = 'light_yellow')
                    match = re.search(r'index "([^"]+)"', str(e))
                    if match:
                        index_name = match.group(1)
                        pgConn.autocommit = True
                        pgCursor.execute(f'REINDEX INDEX "{index_name}";')
                        pgConn.autocommit = False
                        self.__logger(message = f"Successfully Reindexed '{index_name}'. Will Retry On Next Cycle.",
                                      logType = 'Update',
                                      color   = 'light_green')
                    else:
                        self.__logger(message = f"Could Not Extract Index Name From Error. Manual REINDEX Required.",
                                      logType = 'Error',
                                      color   = 'light_red')
                except Exception as reindex_e:
                    pgConn.autocommit = False
                    self.__logger(message = (f"Auto REINDEX Failed. Manual Intervention Required.\n"
                                             f" * Error:          {reindex_e}\n"
                                             f" * Detailed Trace: {traceback.format_exc()}"),
                                  logType = 'Error',
                                  color   = 'light_red')
            #[4-2-3]: General Exception Handling
            except Exception as e:
                self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Update DB With The Streamed Data. User Attention Advised.\n"
                                         f" * Error:          {e}\n"
                                         f" * Detailed Trace: {traceback.format_exc()}"
                                        ), 
                              logType = 'Warning', 
                              color   = 'light_red')
                pgConn.rollback()

        #[5]: Announcement
        if dbUpdated:
            #[5-1]: IPC
            #---[5-1-1]: Dummy Ranges
            for symbol, updates in dRanges_new_updated.items():
                md_symbol = md[symbol]
                #[5-1-1-1]: Local Tracker & PRD
                for dataType, dRanges_new in updates.items():
                    md_symbol[f'{dataType}s_dummyRanges'] = dRanges_new
                    prdEdit_prdAddress = ('CURRENCIES', symbol, f'{dataType}s_dummyRanges')
                    for procName in md_symbol['_subscribers']:
                        func_sendPRDEDIT(targetProcess = procName, 
                                         prdAddress    = prdEdit_prdAddress, 
                                         prdContent    = dRanges_new)
                #[5-1-1-2]: FAR
                far_functionParams = {'updatedContents': [{'symbol': symbol, 'id': (f'{dataType}s_dummyRanges',)} for dataType in updates]}
                for procName in md_symbol['_subscribers']:
                    func_sendFAR(targetProcess  = procName, 
                                 functionID     = 'onCurrenciesUpdate',
                                 functionParams = far_functionParams, 
                                 farrHandler    = None)
            #---[5-1-2]: Available Ranges
            for symbol, updates in aRanges_new_updated.items():
                md_symbol = md[symbol]
                #[5-1-2-1]: Local Tracker & PRD
                for dataType, aRanges_new in updates.items():
                    md_symbol[f'{dataType}s_availableRanges'] = aRanges_new
                    prdEdit_prdAddress = ('CURRENCIES', symbol, f'{dataType}s_availableRanges')
                    for procName in md_symbol['_subscribers']:
                        func_sendPRDEDIT(targetProcess = procName, 
                                         prdAddress    = prdEdit_prdAddress, 
                                         prdContent    = aRanges_new)
                #[5-1-2-2]: FAR
                far_functionParams = {'updatedContents': [{'symbol': symbol, 'id': (f'{dataType}s_availableRanges',)} for dataType in updates]}
                for procName in md_symbol['_subscribers']:
                    func_sendFAR(targetProcess  = procName, 
                                 functionID     = 'onCurrenciesUpdate',
                                 functionParams = far_functionParams, 
                                 farrHandler    = None)
                    
            #[5-2]: Logger
            nSymbols = len(aRanges_new_updated)
            nData    = sum(len(dataList) for dataList in sqlParams_data_total.values())
            self.__logger(message = f"Successfully Saved {nData} Streamed Data For {nSymbols} Symbols", 
                          logType = 'Update', 
                          color   = 'light_green')
    
    def __pp_saveFetchedData(self):
        #[1]: DB Condition Check
        if self.__checkDBBusy(): return

        #[2]: Instances
        md               = self.__marketData
        fReqs            = self.__fetchRequests
        pgConn           = self.__pgConn_write
        pgCursor         = self.__pgCursor_write
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR

        #[3]: Data Collection
        data_collected     = {'kline': [],     'depth': [],     'aggTrade': []}
        data_slice_counts  = {'kline': dict(), 'depth': dict(), 'aggTrade': dict()}
        aRanges_bf_updates = {'kline': dict(), 'depth': dict(), 'aggTrade': dict()}
        dRanges_bf_updates = {'kline': dict(), 'depth': dict(), 'aggTrade': dict()}
        aRanges_db_updates = {'kline': dict(), 'depth': dict(), 'aggTrade': dict()}
        dRanges_db_updates = {'kline': dict(), 'depth': dict(), 'aggTrade': dict()}
        nRemaining = _FETCHSAVECHUNKSIZE
        for symbol, md_symbol in md.items():
            for target in ('kline', 'depth', 'aggTrade'):
                dIdx_openTime  = COMMONDATAINDEXES['openTime'][target]
                dIdx_closeTime = COMMONDATAINDEXES['closeTime'][target]
                dIdx_source    = COMMONDATAINDEXES['source'][target]
                for fType in ('fill', 'refetch', 'import'):
                    #[3-1]: Instances
                    fBuffer = md_symbol[f'_fetch_{target}s_{fType}']
                    fBuffer_data = fBuffer['data']
                    if not fBuffer['data']: continue
                    
                    #[3-2]: Data Selection
                    nSliced     = 0
                    nBufferData = len(fBuffer_data)
                    while nSliced < nBufferData and 0 < nRemaining:
                        nSliced += 1
                        if fBuffer_data[nSliced-1][dIdx_source] != FORMATTEDDATATYPE_DUMMY:
                            nRemaining -= 1
                    data_selected = fBuffer['data'][:nSliced]
                    data_slice_counts[target][(symbol, fType)] = nSliced

                    #[3-3]: Selected Data Range
                    aRanges_selected = []
                    dRanges_selected = []
                    for dl in data_selected:
                        dl_tOpen  = dl[dIdx_openTime]
                        dl_tClose = dl[dIdx_closeTime]
                        dl_source = dl[dIdx_source]
                        if aRanges_selected and aRanges_selected[-1][1]+1 == dl_tOpen:
                            aRanges_selected[-1][1] = dl_tClose
                        else:
                            aRanges_selected.append([dl_tOpen, dl_tClose])
                        if dl_source == FORMATTEDDATATYPE_DUMMY:
                            if dRanges_selected and dRanges_selected[-1][1]+1 == dl_tOpen:
                                dRanges_selected[-1][1] = dl_tClose
                            else:
                                dRanges_selected.append([dl_tOpen, dl_tClose])
                    
                    #[3-4]: Range Updates Record
                    #---[3-4-1]: Buffer
                    aRanges_bf_updates[target][(symbol, fType)] = subtractRangesFromRanges(ranges1=fBuffer['availableRanges'], ranges2=aRanges_selected)
                    if fType == 'fill':
                        dRanges_bf_updates[target][(symbol, fType)] = subtractRangesFromRanges(ranges1=fBuffer['dummyRanges'], ranges2=dRanges_selected)
                    #---[3-4-2] DB
                    aRanges_db_prev = aRanges_db_updates[target].get(symbol, md_symbol[f'{target}s_availableRanges'])
                    dRanges_db_prev = dRanges_db_updates[target].get(symbol, md_symbol[f'{target}s_dummyRanges'])
                    if fType == 'fill':
                        aRanges_db_updates[target][symbol] = mergeRangesToRanges(ranges1=aRanges_db_prev, ranges2=aRanges_selected)
                        dRanges_db_updates[target][symbol] = mergeRangesToRanges(ranges1=dRanges_db_prev, ranges2=dRanges_selected)
                    elif fType in ('refetch', 'import'):
                        aRanges_db_updates[target][symbol] = aRanges_db_prev
                        dRanges_db_updates[target][symbol] = subtractRangesFromRanges(ranges1=dRanges_db_prev, ranges2=aRanges_selected)

                    #[3-5]: Selected Data Formatting
                    if target == 'kline':
                        data_formatted = [(kl[KLINDEX_OPENTIME],         # openTS (for to_timestamp(%s))
                                           symbol,                       # symbol
                                           kl[KLINDEX_OPENTIME],         # t_open
                                           kl[KLINDEX_CLOSETIME],        # t_close
                                           kl[KLINDEX_OPENPRICE],        # p_open
                                           kl[KLINDEX_HIGHPRICE],        # p_high
                                           kl[KLINDEX_LOWPRICE],         # p_low
                                           kl[KLINDEX_CLOSEPRICE],       # p_close
                                           kl[KLINDEX_NTRADES],          # nTrades
                                           kl[KLINDEX_VOLBASE],          # base asset volume
                                           kl[KLINDEX_VOLQUOTE],         # quote asset volume
                                           kl[KLINDEX_VOLBASETAKERBUY],  # base asset volume (taker-buy)
                                           kl[KLINDEX_VOLQUOTETAKERBUY], # quote asset volume (taker-buy)
                                           kl[KLINDEX_SOURCE]            # kline type
                                          ) for kl in data_selected if kl[KLINDEX_SOURCE] != FORMATTEDDATATYPE_DUMMY]
                    elif target == 'depth':
                        data_formatted = [(depth[DEPTHINDEX_OPENTIME],  # openTS (for to_timestamp(%s))
                                           symbol,                      # symbol
                                           depth[DEPTHINDEX_OPENTIME],  # t_open
                                           depth[DEPTHINDEX_CLOSETIME], # t_close
                                           depth[DEPTHINDEX_BIDS5],     # bids5 (-4.0% ~ -5.0%)
                                           depth[DEPTHINDEX_BIDS4],     # bids4 (-3.0% ~ -4.0%)
                                           depth[DEPTHINDEX_BIDS3],     # bids3 (-2.0% ~ -3.0%)
                                           depth[DEPTHINDEX_BIDS2],     # bids2 (-1.0% ~ -2.0%)
                                           depth[DEPTHINDEX_BIDS1],     # bids1 (-0.2% ~ -1.0%)
                                           depth[DEPTHINDEX_BIDS0],     # bids0 ( 0.0% ~ -0.2%)
                                           depth[DEPTHINDEX_ASKS0],     # asks0 ( 0.0% ~  0.2%)
                                           depth[DEPTHINDEX_ASKS1],     # asks1 ( 0.2% ~  1.0%)
                                           depth[DEPTHINDEX_ASKS2],     # asks2 ( 1.0% ~  2.0%)
                                           depth[DEPTHINDEX_ASKS3],     # asks3 ( 2.0% ~  3.0%)
                                           depth[DEPTHINDEX_ASKS4],     # asks4 ( 3.0% ~  4.0%)
                                           depth[DEPTHINDEX_ASKS5],     # asks5 ( 4.0% ~  5.0%)
                                           depth[DEPTHINDEX_SOURCE]     # depth type
                                          ) for depth in data_selected if depth[DEPTHINDEX_SOURCE] != FORMATTEDDATATYPE_DUMMY]
                    elif target == 'aggTrade':
                        data_formatted = [(at[ATINDEX_OPENTIME],     # openTS (for to_timestamp(%s))
                                           symbol,                   # symbol
                                           at[ATINDEX_OPENTIME],     # t_open
                                           at[ATINDEX_CLOSETIME],    # t_close
                                           at[ATINDEX_QUANTITYBUY],  # quantity_buy
                                           at[ATINDEX_QUANTITYSELL], # quantity_sell
                                           at[ATINDEX_NTRADESBUY],   # ntrades_buy
                                           at[ATINDEX_NTRADESSELL],  # ntrades_sell
                                           at[ATINDEX_NOTIONALBUY],  # notional_buy
                                           at[ATINDEX_NOTIONALSELL], # notional_sell
                                           at[ATINDEX_SOURCE]        # aggTrade type
                                          ) for at in data_selected if at[ATINDEX_SOURCE] != FORMATTEDDATATYPE_DUMMY]
                    data_collected[target].extend(data_formatted)
                    if nRemaining <= 0: break
                if nRemaining <= 0: break
            if nRemaining <= 0: break
        if not any(data_slice_counts[target] for target in ('kline', 'depth', 'aggTrade')):
            return
        
        #[4]: SQL Parameters
        pgParams_data = {'kline':    data_collected['kline'],
                         'depth':    data_collected['depth'],
                         'aggTrade': data_collected['aggTrade']}
        pgParams_aRanges = {'kline':    [(json.dumps(aRanges_new), symbol) for symbol, aRanges_new in aRanges_db_updates['kline'].items()],
                            'depth':    [(json.dumps(aRanges_new), symbol) for symbol, aRanges_new in aRanges_db_updates['depth'].items()],
                            'aggTrade': [(json.dumps(aRanges_new), symbol) for symbol, aRanges_new in aRanges_db_updates['aggTrade'].items()]}
        pgParams_dRanges = {'kline':    [(json.dumps(dRanges_new), symbol) for symbol, dRanges_new in dRanges_db_updates['kline'].items()],
                            'depth':    [(json.dumps(dRanges_new), symbol) for symbol, dRanges_new in dRanges_db_updates['depth'].items()],
                            'aggTrade': [(json.dumps(dRanges_new), symbol) for symbol, dRanges_new in dRanges_db_updates['aggTrade'].items()]}

        #[5]: DB Update
        dbUpdated = False
        #---[5-1]: Expected Behavior
        try:
            #[5-1-1]: Decompression (If Needed)
            dcmprs_tables     = []
            dcmprs_timestamps = []
            for target in ('kline', 'depth', 'aggTrade'):
                data_refetch = pgParams_data[target]
                if not data_refetch: continue
                table = f"{target}s"
                for row in data_refetch:
                    dcmprs_tables.append(table)
                    dcmprs_timestamps.append(row[0])
            decompressed_chunks = []
            if dcmprs_tables:
                pgCursor.execute("SET timescaledb.max_tuples_decompressed_per_dml_transaction = 0;")
                batch_decompress_query = """WITH target_chunks AS (SELECT DISTINCT show_chunks(h_name::regclass, 
                                                                                   newer_than => to_timestamp(ts_val - 1), 
                                                                                   older_than => to_timestamp(ts_val + 1))::text AS c_name
                                                                   FROM (SELECT unnest(%s::text[]) AS h_name, unnest(%s::bigint[]) AS ts_val) AS s
                                                                  ), chunks_to_fix AS (SELECT tc.c_name 
                                                                                       FROM target_chunks tc
                                                                                       JOIN timescaledb_information.chunks c ON c.chunk_name::text = tc.c_name
                                                                                       WHERE c.is_compressed = true
                                                                                      )
                                            SELECT decompress_chunk(c_name, if_compressed => true) FROM chunks_to_fix;
                                         """
                pgCursor.execute(batch_decompress_query, (dcmprs_tables, dcmprs_timestamps))
                decompressed_chunks = [row[0] for row in pgCursor.fetchall()]
                if decompressed_chunks:
                    self.__logger(message = f"Decompressed {len(decompressed_chunks)} HyperTable Chunks Prior To Update",
                                  logType = 'Update', 
                                  color   = 'light_cyan')

            #[5-1-2]: Data Insertion & Update
            for target in ('kline', 'depth', 'aggTrade'):
                if pgParams_data[target]:
                    execute_values(cur       = pgCursor,
                                   sql       = PGQUERY_FETCHSAVE_DATA[target],
                                   argslist  = pgParams_data[target],
                                   template  = PGTEMPLATE_FETCHSAVE_DATA[target],
                                   page_size = 1000)
                if pgParams_aRanges[target]:
                    pgCursor.executemany(PGQUERY_FETCHSAVE_ARANGES[target], pgParams_aRanges[target])
                if pgParams_dRanges[target]:
                    pgCursor.executemany(PGQUERY_FETCHSAVE_DRANGES[target], pgParams_dRanges[target])

            #[5-1-3]: Recompression
            if decompressed_chunks:
                recompress_query = """SELECT compress_chunk(c_name, if_not_compressed => true)
                                      FROM unnest(%s::text[]) AS c_name;
                                   """
                try:
                    pgCursor.execute(recompress_query, (decompressed_chunks,))
                    self.__logger(message = f"Successfully Recompressed {len(decompressed_chunks)} HyperTable Chunks",
                                  logType = 'Update', 
                                  color   = 'light_cyan')
                except Exception as e:
                    self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Recompress HyperTable Chunks. The User May Manually Compress Or Wait For A Periodic Compression.\n"
                                             f" * Error:          {e}\n"
                                             f" * Detailed Trace: {traceback.format_exc()}"
                                            ), 
                                  logType = 'Warning', 
                                  color   = 'light_red')

            #[5-1-4]: Commit
            pgConn.commit()
            dbUpdated = True
        #---[5-2]: Index Corruption Handling (Auto REINDEX)
        except psycopg2.errors.IndexCorrupted as e:
            pgConn.rollback()
            try:
                self.__logger(message = (f"Index Corruption Detected While Attempting To Update DB With The Fetched Data. Attempting Auto REINDEX.\n"
                                         f" * Error: {e}"),
                              logType = 'Warning',
                              color   = 'light_yellow')
                match = re.search(r'index "([^"]+)"', str(e))
                if match:
                    index_name = match.group(1)
                    pgConn.autocommit = True
                    pgCursor.execute(f'REINDEX INDEX "{index_name}";')
                    pgConn.autocommit = False
                    self.__logger(message = f"Successfully Reindexed '{index_name}'. Will Retry On Next Cycle.",
                                  logType = 'Update',
                                  color   = 'light_green')
                else:
                    self.__logger(message = f"Could Not Extract Index Name From Error. Manual REINDEX Required.",
                                  logType = 'Error',
                                  color   = 'light_red')
            except Exception as reindex_e:
                pgConn.autocommit = False
                self.__logger(message = (f"Auto REINDEX Failed. Manual Intervention Required.\n"
                                         f" * Error:          {reindex_e}\n"
                                         f" * Detailed Trace: {traceback.format_exc()}"),
                              logType = 'Error',
                              color   = 'light_red')
        #---[5-3]: General Exception Handling
        except Exception as e:
            pgConn.rollback()
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Update DB With The Fetched Data. User Attention Advised.\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"
                                    ), 
                          logType = 'Warning', 
                          color   = 'light_red')
            pgConn.rollback()
        if not dbUpdated: return

        #[6]: Ranges Update & Announcement
        #---[6-1]: Local DB Range Update & Announcement
        for rType, rUpdates in [('available', aRanges_db_updates), ('dummy', dRanges_db_updates)]:
            for target, symbol_dict in rUpdates.items():
                for symbol, ranges_new in symbol_dict.items():
                    md_symbol = md[symbol]
                    #[6-1-1]: Range
                    md_symbol[f'{target}s_{rType}Ranges'] = ranges_new
                    #[6-1-2]: Announcement
                    prdEdit_prdAddress = ('CURRENCIES', symbol, f'{target}s_{rType}Ranges')
                    far_functionParams = {'updatedContents': [{'symbol': symbol, 'id': (f'{target}s_{rType}Ranges',)}]}
                    for procName in md_symbol['_subscribers']:
                        func_sendPRDEDIT(targetProcess = procName, 
                                         prdAddress    = prdEdit_prdAddress, 
                                         prdContent    = ranges_new)
                        func_sendFAR(targetProcess  = procName, 
                                     functionID     = 'onCurrenciesUpdate',
                                     functionParams = far_functionParams, 
                                     farrHandler    = None)

        #---[6-2]: Buffer Update
        for target in ('kline', 'depth', 'aggTrade'):
            for (symbol, fType), slice_len in data_slice_counts[target].items():
                fBuffer = md[symbol][f'_fetch_{target}s_{fType}']
                #[6-2-1]: Buffer Data
                fBuffer['data'] = fBuffer['data'][slice_len:]
                #[6-2-2]: Buffer Range
                if fBuffer['data']:
                    fBuffer['availableRanges'] = aRanges_bf_updates[target].get((symbol, fType))
                    if fType == 'fill':
                        fBuffer['dummyRanges'] = dRanges_bf_updates[target].get((symbol, fType))
                else:
                    fBuffer['availableRanges'] = None
                    if fType == 'fill':
                        fBuffer['dummyRanges'] = None
                    
        #[7]: Fetch Status Update
        t_current_ns = time.perf_counter_ns()
        if fReqs['lastProcessTime_ns'] is not None:
            tElapsed_ns = time.perf_counter_ns()-fReqs['lastProcessTime_ns']
            fSpeeds     = dict()
            for target in ('kline', 'depth', 'aggTrade'):
                dLen   = len(data_collected[target])
                fSpeed = dLen*60/tElapsed_ns*1e9 if 0 < dLen else None
                fSpeeds[target] = fSpeed
            self.__updateFetchStatus(fetchSpeeds = fSpeeds)
        fReqs['lastProcessTime_ns'] = t_current_ns

        #[8]: Buffer Length Counter Update
        fReqs['validBufferLength'] -= (_FETCHSAVECHUNKSIZE - nRemaining)
        if fReqs['validBufferLength'] < _FETCHPAUSETHRESHOLD and fReqs['pauseRequested']:
            func_sendFAR(targetProcess  = 'BINANCEAPI',
                         functionID     = 'continueMarketDataFetch',
                         functionParams = None,
                         farrHandler    = None)
            fReqs['pauseRequested'] = False

        #[9]: Logging
        nSaved_kline_fill    = len(data_collected['kline'])
        nSaved_depth_fill    = len(data_collected['depth'])
        nSaved_aggTrade_fill = len(data_collected['aggTrade'])
        nSaved_total = (nSaved_kline_fill+nSaved_depth_fill+nSaved_aggTrade_fill)
        self.__logger(message = (f"Succesfully Saved Fetched Market Data.\n"
                                 f" * KLINE:    {nSaved_kline_fill}\n"
                                 f" * DEPTH:    {nSaved_depth_fill}\n"
                                 f" * AGGTRADE: {nSaved_aggTrade_fill}\n"
                                 f" * Total:    {nSaved_total}"
                                 ), 
                      logType = 'Update', 
                      color   = 'light_green')

    def __pp_sendFetchRequests(self):
        #[1]: Instances
        md    = self.__marketData
        fReqs = self.__fetchRequests
        func_sendFAR = self.__ipcA.sendFAR

        #[2]: Dispatch Fetch Requests To BINANCEAPI
        fStatus_updated = False
        for target in ('kline', 'depth', 'aggTrade'):
            #[2-1]: Instances
            fReqs_pending = fReqs['pending'][target]
            fReqs_active  = fReqs['active'][target]

            #[2-2]: Dispatch Fetch Requests To BINANCEAPI
            for symbol in fReqs_pending:
                #[2-2-1]: Instances
                md_symbol    = md[symbol]
                aRanges      = md_symbol[f'{target}s_availableRanges']
                firstOpenTS  = md_symbol[f'{target}_firstOpenTS']
                sFirstOpenTS = md_symbol[f'_stream_{target}s']['firstOpenTS']

                #[2-2-2]: Determine Fetch Target Ranges
                ftRanges = None
                if aRanges is None:
                    if firstOpenTS < sFirstOpenTS: 
                        ftRanges = [(firstOpenTS, sFirstOpenTS-1),]
                else:
                    ftRanges = []
                    if firstOpenTS < aRanges[0][0]: ftRanges.append((firstOpenTS, aRanges[0][0]-1))
                    for drIndex in range (len(aRanges)-1):
                        dr_this = aRanges[drIndex]
                        dr_next = aRanges[drIndex+1]
                        ftRanges.append((dr_this[1]+1, dr_next[0]-1))
                    if aRanges[-1][1]+1 < sFirstOpenTS: ftRanges.append((aRanges[-1][1]+1, sFirstOpenTS-1))
                if not ftRanges: continue

                #[2-2-3]: Dispatch Fetch Request
                dispatchRID = func_sendFAR(targetProcess  = 'BINANCEAPI', 
                                           functionID     = 'fetchData', 
                                           functionParams = {'symbol':            symbol,
                                                             'target':            target,
                                                             'fetchTargetRanges': ftRanges}, 
                                           farrHandler = self.__farr_getDataFetchRequestResult)
                fReqs_active[dispatchRID] = {'symbol':            symbol,
                                             'type':              'FILL',
                                             'fetchedRanges':     [],
                                             'fetchTargetRanges': ftRanges}
                fStatus_updated = True

            #[2-3]: Clear Pending Queues
            fReqs_pending.clear()

        #[3]: Fetch Status Update Announcement
        if fStatus_updated:
            self.__updateFetchStatus()
    #Periodic Processes END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------




    
    #Task Handlers ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __th_initialDBRead(self, task):
        #[1]: Instances
        cSymbols = self.__collectingSymbols
        md       = self.__marketData
        pgConn   = self.__pgConn_write
        pgCursor = self.__pgCursor_write
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT

        #[2]: PostgreSQL Conenction
        if pgConn is None:
            return

        #[3]: Check Tables & Create If Needed
        #---[3-1]: Activate TimescaleDB Extension
        pgCursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")

        #---[3-2]: Get Current Tables
        pgCursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'; """)
        tablesInDB = set(fetchedElement[0] for fetchedElement in pgCursor.fetchall())

        #---[3-3]: Tables Check & Creation
        for tableName in ('descriptors', 'klines', 'depths', 'aggtrades'):
            #[3-3-1]: If The Table Exists, Continue
            if tableName in tablesInDB: continue
            
            #[3-3-2]: Descriptor Table 
            if tableName == 'descriptors': 
                pgCursor.execute("""CREATE TABLE descriptors
                                    (
                                    symbol                      TEXT PRIMARY KEY, 
                                    precisions                  JSONB, 
                                    baseasset                   TEXT, 
                                    quoteasset                  TEXT,
                                    kline_firstopents           BIGINT,
                                    depth_firstopents           BIGINT,
                                    aggtrade_firstopents        BIGINT,
                                    klines_availableranges      JSONB,
                                    depths_availableranges      JSONB,
                                    aggtrades_availableranges   JSONB,
                                    klines_dummyranges          JSONB,
                                    depths_dummyranges          JSONB,
                                    aggtrades_dummyranges       JSONB
                                    )
                                    """)
                
            #[3-3-3]: Klines Table (TimescaleDB)
            elif tableName == 'klines':  
                pgCursor.execute("""CREATE TABLE klines 
                                    (
                                    time        TIMESTAMPTZ NOT NULL,
                                    symbol      TEXT NOT NULL,
                                    t_open      BIGINT, 
                                    t_close     BIGINT, 
                                    p_open      DOUBLE PRECISION, 
                                    p_high      DOUBLE PRECISION, 
                                    p_low       DOUBLE PRECISION, 
                                    p_close     DOUBLE PRECISION, 
                                    ntrades     INTEGER, 
                                    v           DOUBLE PRECISION, 
                                    q           DOUBLE PRECISION, 
                                    v_tb        DOUBLE PRECISION, 
                                    q_tb        DOUBLE PRECISION, 
                                    ktype       INTEGER,
                                    PRIMARY KEY (time, symbol)
                                    )
                                    """)
                #TimescaleDB Conversion
                pgCursor.execute("SELECT create_hypertable('klines', 'time');")
                #Add Search Index
                pgCursor.execute("CREATE INDEX idx_klines_symbol_time ON klines (symbol, time DESC);")
                #Activate Compression
                pgCursor.execute("ALTER TABLE klines SET (timescaledb.compress, timescaledb.compress_segmentby = 'symbol', timescaledb.compress_orderby = 'time DESC');")
                pgCursor.execute("SELECT add_compression_policy('klines', INTERVAL '7 days');")
                
            #[3-3-4]: Depths Table (TimescaleDB)
            elif tableName == 'depths':
                pgCursor.execute("""CREATE TABLE depths 
                                    (
                                    time        TIMESTAMPTZ NOT NULL,
                                    symbol      TEXT NOT NULL,
                                    t_open      BIGINT, 
                                    t_close     BIGINT, 
                                    bids5       DOUBLE PRECISION, 
                                    bids4       DOUBLE PRECISION, 
                                    bids3       DOUBLE PRECISION, 
                                    bids2       DOUBLE PRECISION, 
                                    bids1       DOUBLE PRECISION, 
                                    bids0       DOUBLE PRECISION, 
                                    asks0       DOUBLE PRECISION, 
                                    asks1       DOUBLE PRECISION, 
                                    asks2       DOUBLE PRECISION, 
                                    asks3       DOUBLE PRECISION, 
                                    asks4       DOUBLE PRECISION, 
                                    asks5       DOUBLE PRECISION, 
                                    dtype       INTEGER,
                                    PRIMARY KEY (time, symbol)
                                    )
                                    """)
                #TimescaleDB Conversion
                pgCursor.execute("SELECT create_hypertable('depths', 'time');")
                #Add Search Index
                pgCursor.execute("CREATE INDEX idx_depths_symbol_time ON depths (symbol, time DESC);")
                #Activate Compression
                pgCursor.execute("ALTER TABLE depths SET (timescaledb.compress, timescaledb.compress_segmentby = 'symbol', timescaledb.compress_orderby = 'time DESC');")
                pgCursor.execute("SELECT add_compression_policy('depths', INTERVAL '7 days');")
                
            #[3-3-5]: AggTrades Table (TimescaleDB)
            elif tableName == 'aggtrades':  
                pgCursor.execute("""CREATE TABLE aggtrades 
                                    (
                                    time          TIMESTAMPTZ NOT NULL,
                                    symbol        TEXT NOT NULL,
                                    t_open        BIGINT, 
                                    t_close       BIGINT, 
                                    quantity_buy  DOUBLE PRECISION, 
                                    quantity_sell DOUBLE PRECISION, 
                                    ntrades_buy   DOUBLE PRECISION, 
                                    ntrades_sell  DOUBLE PRECISION, 
                                    notional_buy  DOUBLE PRECISION, 
                                    notional_sell DOUBLE PRECISION,
                                    attype        INTEGER,
                                    PRIMARY KEY   (time, symbol)
                                    )
                                    """)
                #TimescaleDB Conversion
                pgCursor.execute("SELECT create_hypertable('aggtrades', 'time');")
                #Add Search Index
                pgCursor.execute("CREATE INDEX idx_aggtrades_symbol_time ON aggtrades (symbol, time DESC);")
                #Activate Compression
                pgCursor.execute("ALTER TABLE aggtrades SET (timescaledb.compress, timescaledb.compress_segmentby = 'symbol', timescaledb.compress_orderby = 'time DESC');")
                pgCursor.execute("SELECT add_compression_policy('aggtrades', INTERVAL '7 days');")

        #---[3-4]: Commit Changes
        pgConn.commit()

        #[4]: Read From DB
        pgCursor.execute("SELECT * FROM descriptors")
        db_descriptors  = pgCursor.fetchall()
        baseSubscribers = {'GUI', 'TRADEMANAGER', 'SIMULATIONMANAGER', 'NEURALNETWORKMANAGER'}
        for summaryRow in db_descriptors:
            symbol                    = summaryRow[0]
            precisions                = summaryRow[1]
            baseAsset                 = summaryRow[2]
            quoteAsset                = summaryRow[3]
            kline_firstOpenTS         = summaryRow[4]
            depth_firstOpenTS         = summaryRow[5]
            aggTrade_firstOpenTS      = summaryRow[6]
            klines_availableRanges    = summaryRow[7]
            depths_availableRanges    = summaryRow[8]
            aggTrades_availableRanges = summaryRow[9]
            klines_dummyRanges        = summaryRow[10]
            depths_dummyRanges        = summaryRow[11]
            aggTrades_dummyRanges     = summaryRow[12]
            coll = cSymbols.get(symbol, None)
            if coll is None:
                collStrm = False
                collHist = False
            else:
                collStrm = coll['collectingStream']
                collHist = coll['collectingHistorical']
            md[symbol] = {'precisions':                precisions,
                          'baseAsset':                 baseAsset,
                          'quoteAsset':                quoteAsset,
                          'kline_firstOpenTS':         kline_firstOpenTS,
                          'depth_firstOpenTS':         depth_firstOpenTS,
                          'aggTrade_firstOpenTS':      aggTrade_firstOpenTS,
                          'klines_availableRanges':    klines_availableRanges,
                          'depths_availableRanges':    depths_availableRanges,
                          'aggTrades_availableRanges': aggTrades_availableRanges,
                          'klines_dummyRanges':        klines_dummyRanges,
                          'depths_dummyRanges':        depths_dummyRanges,
                          'aggTrades_dummyRanges':     aggTrades_dummyRanges,
                          'collecting':                (collStrm, collHist),
                          'info_server':               None,
                          '_stream_klines':            {'klines':    list(), 'ranges': list(), 'firstOpenTS': None, 'lastOpenTS': None},
                          '_stream_depths':            {'depths':    list(), 'ranges': list(), 'firstOpenTS': None, 'lastOpenTS': None},
                          '_stream_aggTrades':         {'aggTrades': list(), 'ranges': list(), 'firstOpenTS': None, 'lastOpenTS': None},
                          '_fetch_klines_fill':        {'data': list(), 'availableRanges': None, 'dummyRanges': None},
                          '_fetch_klines_refetch':     {'data': list(), 'availableRanges': None},
                          '_fetch_klines_import':      {'data': list(), 'availableRanges': None},
                          '_fetch_depths_fill':        {'data': list(), 'availableRanges': None, 'dummyRanges': None},
                          '_fetch_depths_refetch':     {'data': list(), 'availableRanges': None},
                          '_fetch_depths_import':      {'data': list(), 'availableRanges': None},
                          '_fetch_aggTrades_fill':     {'data': list(), 'availableRanges': None, 'dummyRanges': None},
                          '_fetch_aggTrades_refetch':  {'data': list(), 'availableRanges': None},
                          '_fetch_aggTrades_import':   {'data': list(), 'availableRanges': None},
                          '_subscribers':              baseSubscribers.copy()}
        print(f"     * {len(md)} Currencies Data Imported!")

        #[5]: Announce The Market (Currency) Info
        md_announce = {symbol: {k: v for k, v in data.items() if k in _MARKETDATA_ANNOUNCEMENT_KEYS} for symbol, data in md.items()}
        for processName in ('GUI', 'TRADEMANAGER', 'SIMULATIONMANAGER', 'NEURALNETWORKMANAGER'):
            func_sendPRDEDIT(targetProcess = processName,
                             prdAddress    = 'CURRENCIES',
                             prdContent    = md_announce)

        #[6]: Collecting Symbols Save
        self.__saveCollectingSymbolsList()

        #[7]: Initial Task Completion Flag
        self.__initialTaskComplete = True
       
    def __th_setMarketDataCollection(self, task):
        #[1]: Instances
        md               = self.__marketData
        fReqs            = self.__fetchRequests
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR
        func_sendFARR    = self.__ipcA.sendFARR
        tParams = task['params']
        symbols            = tParams['symbols']
        collStrm, collHist = tParams['mode']
        if not collStrm and collHist:
            collHist = False
        mode = (collStrm, collHist)
        
        #[2]: Symbols Check
        symbols_updated = []
        modes_prev      = dict()
        for symbol in symbols:
            #[2-1]: Instance
            md_symbol = md.get(symbol, None)
            if md_symbol is None:               continue
            if md_symbol['collecting'] == mode: continue

            #[2-2]: Update
            modes_prev[symbol] = md_symbol['collecting']
            md_symbol['collecting'] = mode
            symbols_updated.append(symbol)

            #[2-3]: Update Announcement
            prdEdit_prdAddress = ('CURRENCIES', symbol, 'collecting')
            far_functionParams = {'updatedContents': [{'symbol': symbol, 'id': ('collecting',)}]}
            for procName in md_symbol['_subscribers']:
                func_sendPRDEDIT(targetProcess = procName, 
                                 prdAddress    = prdEdit_prdAddress, 
                                 prdContent    = mode)
                func_sendFAR(targetProcess  = procName, 
                             functionID     = 'onCurrenciesUpdate',
                             functionParams = far_functionParams, 
                             farrHandler    = None)

        #[3]: Configuration Update
        if symbols_updated:
            cSymbols = self.__collectingSymbols
            updates_ba = []
            for symbol in symbols_updated:
                cSymbols[symbol] = {'collectingStream':     collStrm,
                                    'collectingHistorical': collHist}
                updates_ba.append((symbol, collStrm, collHist))
            func_sendFAR(targetProcess  = 'BINANCEAPI', 
                         functionID     = 'onSymbolCollectionUpdate',
                         functionParams = {'updates': updates_ba}, 
                         farrHandler    = None)
            self.__saveCollectingSymbolsList()

        #[4]: Stream Variables Reset (If Not Collecting Stream Anymore)
        if not collStrm:
            for symbol in symbols_updated:
                md_symbol = md[symbol]
                md_symbol['_stream_klines']['klines'].clear()
                md_symbol['_stream_klines']['ranges'].clear()
                md_symbol['_stream_klines']['firstOpenTS'] = None
                md_symbol['_stream_klines']['lastOpenTS']  = None
                md_symbol['_stream_depths']['depths'].clear()
                md_symbol['_stream_depths']['ranges'].clear()
                md_symbol['_stream_depths']['firstOpenTS'] = None
                md_symbol['_stream_depths']['lastOpenTS']  = None
                md_symbol['_stream_aggTrades']['aggTrades'].clear()
                md_symbol['_stream_aggTrades']['ranges'].clear()
                md_symbol['_stream_aggTrades']['firstOpenTS'] = None
                md_symbol['_stream_aggTrades']['lastOpenTS']  = None

        #[5]: Requests Update & Dispatch
        for symbol in symbols_updated:
            md_symbol = md[symbol]
            for target in ('kline', 'depth', 'aggTrade'):
                #[5-1]: First Open TS
                if md_symbol[f'{target}_firstOpenTS'] is None:
                    func_sendFAR(targetProcess  = 'BINANCEAPI', 
                                 functionID     = 'getFirstOpenTS', 
                                 functionParams = {'symbol': symbol, 
                                                   'target': target},
                                 farrHandler    = self.__farr_getFirstOpenTS)
                #[5-2]: Historical Fetch Requests
                elif collHist:
                    (collStrm_prev, collHist_prev) = modes_prev[symbol]
                    if collHist_prev:                                          continue
                    if md_symbol[f'_stream_{target}s']['firstOpenTS'] is None: continue
                    fReqs['pending'][target].add(symbol)

        #[6]: Return Result
        nSymbols_updated = len(symbols_updated)
        if   nSymbols_updated == 0: fResult = {'result': False, 'message': f"No Collection Flags Were Updated"}
        elif nSymbols_updated == 1: fResult = {'result': True,  'message': f"Successfully Updated Collection Flag For {symbols_updated[0]}! ({len(symbols)} Requested)"}
        else:                       fResult = {'result': True,  'message': f"Successfully Updated Collection Flags For {nSymbols_updated} Symbols! ({len(symbols)} Requested)"}
        func_sendFARR(targetProcess  = task['requester'], 
                      functionResult = fResult, 
                      requestID      = task['requestID'],
                      complete       = True)

    def __th_registerCurrency(self, task):
        #[1]: Instances
        cSymbols  = self.__collectingSymbols
        pgConn    = self.__pgConn_write
        pgCursor  = self.__pgCursor_write
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR
        tParams = task['params']
        symbol = tParams['symbol']
        info   = tParams['info']

        #[2]: Market Data
        md_symbol = self.__marketData.get(symbol, None)
        
        #[3]: New Symbol
        if md_symbol is None:
            #[3-1]: Symbol Market Data
            coll = cSymbols.get(symbol, None)
            if coll is None:
                collStrm = False
                collHist = False
            else:
                collStrm = coll['collectingStream']
                collHist = coll['collectingHistorical']
            md_symbol = {'precisions':                {'price':    info['pricePrecision'], 
                                                       'quantity': info['quantityPrecision'], 
                                                       'quote':    info['quotePrecision']},
                         'baseAsset':                 info['baseAsset'],
                         'quoteAsset':                info['quoteAsset'],
                         'kline_firstOpenTS':         None,
                         'depth_firstOpenTS':         None,
                         'aggTrade_firstOpenTS':      None,
                         'klines_availableRanges':    None,
                         'depths_availableRanges':    None,
                         'aggTrades_availableRanges': None,
                         'klines_dummyRanges':        None,
                         'depths_dummyRanges':        None,
                         'aggTrades_dummyRanges':     None,
                         'collecting':                (collStrm, collHist),
                         'info_server':               info,
                         '_stream_klines':            {'klines':    list(), 'ranges': list(), 'firstOpenTS': None, 'lastOpenTS': None},
                         '_stream_depths':            {'depths':    list(), 'ranges': list(), 'firstOpenTS': None, 'lastOpenTS': None},
                         '_stream_aggTrades':         {'aggTrades': list(), 'ranges': list(), 'firstOpenTS': None, 'lastOpenTS': None},
                         '_fetch_klines_fill':        {'data': list(), 'availableRanges': None, 'dummyRanges': None},
                         '_fetch_klines_refetch':     {'data': list(), 'availableRanges': None},
                         '_fetch_klines_import':      {'data': list(), 'availableRanges': None},
                         '_fetch_depths_fill':        {'data': list(), 'availableRanges': None, 'dummyRanges': None},
                         '_fetch_depths_refetch':     {'data': list(), 'availableRanges': None},
                         '_fetch_depths_import':      {'data': list(), 'availableRanges': None},
                         '_fetch_aggTrades_fill':     {'data': list(), 'availableRanges': None, 'dummyRanges': None},
                         '_fetch_aggTrades_refetch':  {'data': list(), 'availableRanges': None},
                         '_fetch_aggTrades_import':   {'data': list(), 'availableRanges': None},
                         '_subscribers':              {'GUI', 'TRADEMANAGER', 'SIMULATIONMANAGER', 'NEURALNETWORKMANAGER'}}
            self.__marketData[symbol] = md_symbol

            #[3-2]: DB Update
            pgQuery = """INSERT INTO descriptors 
                         (
                          symbol, 
                          precisions, 
                          baseAsset, 
                          quoteAsset, 
                          kline_firstOpenTS, 
                          depth_firstOpenTS, 
                          aggTrade_firstOpenTS, 
                          klines_availableRanges,
                          depths_availableRanges,
                          aggTrades_availableRanges,
                          klines_dummyRanges,
                          depths_dummyRanges,
                          aggTrades_dummyRanges
                         ) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
            try:
                params = (symbol, 
                          json.dumps(md_symbol['precisions']) if md_symbol['precisions'] is not None else None, 
                          md_symbol['baseAsset'], 
                          md_symbol['quoteAsset'], 
                          md_symbol['kline_firstOpenTS'], 
                          md_symbol['depth_firstOpenTS'], 
                          md_symbol['aggTrade_firstOpenTS'], 
                          json.dumps(md_symbol['klines_availableRanges'])    if md_symbol['klines_availableRanges']    is not None else None,
                          json.dumps(md_symbol['depths_availableRanges'])    if md_symbol['depths_availableRanges']    is not None else None,
                          json.dumps(md_symbol['aggTrades_availableRanges']) if md_symbol['aggTrades_availableRanges'] is not None else None,
                          json.dumps(md_symbol['klines_dummyRanges'])        if md_symbol['klines_dummyRanges']        is not None else None,
                          json.dumps(md_symbol['depths_dummyRanges'])        if md_symbol['depths_dummyRanges']        is not None else None,
                          json.dumps(md_symbol['aggTrades_dummyRanges'])     if md_symbol['aggTrades_dummyRanges']     is not None else None
                          )
                pgCursor.execute(pgQuery, params)
                pgConn.commit()
            except Exception as e:
                pgConn.rollback()
                self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Register A New Currency\n"
                                         f" * Error:          {e}\n"
                                         f" * Detailed Trace: {traceback.format_exc()}"
                                         ), 
                              logType = 'Error', 
                              color   = 'light_red')

                print(f" * Error updating descriptors for {symbol}: {e}")

            #[3-3]: Announce The Symbol Market Data
            md_symbol_announce = {k: md_symbol[k] for k in _MARKETDATA_ANNOUNCEMENT_KEYS}
            prdEdit_prdAddress = ('CURRENCIES', symbol)
            far_functionParams = {'updatedContents': [{'symbol': symbol, 'id': '_ADDED'},]}
            for procName in md_symbol['_subscribers']:
                func_sendPRDEDIT(targetProcess = procName, 
                                 prdAddress    = prdEdit_prdAddress, 
                                 prdContent    = md_symbol_announce)
                func_sendFAR(targetProcess  = procName, 
                             functionID     = 'onCurrenciesUpdate', 
                             functionParams = far_functionParams, 
                             farrHandler    = None)
                
            #[3-4]: Update & Save Collecting Symbols List
            self.__collectingSymbols[symbol] = {'collectingStream':     md_symbol['collecting'][0],
                                                'collectingHistorical': md_symbol['collecting'][1]}
            self.__saveCollectingSymbolsList()

        #[4]: Symbol already exists within the database
        else:
            #[4-1]: Update Server Information
            md_symbol['info_server'] = info

            #[4-2]: Updates Check
            updated = set()
            #---[4-2-1]: Precisions - 0b1
            if md_symbol['precisions'] is None:
                updated.add('precisions')
            else:
                md_symbol_precisions = md_symbol['precisions']
                for pType in ('price', 'quantity', 'quote'):
                    p_prev = md_symbol_precisions[pType]
                    p_new  = info[f'{pType}Precision']
                    if p_prev != p_new:
                        md_symbol_precisions[pType] = p_new
                        updated.add('precisions')

            #[4-3]: DB Update
            try:
                #[4-3-1]: Precisions
                if 'precisions' in updated:
                    pgQuery = "UPDATE descriptors SET precisions = %s WHERE symbol = %s"
                    params  = (json.dumps(md_symbol['precisions']), 
                               symbol)
                    pgCursor.execute(pgQuery, params)
                #[4-3-2]: Finally, Commit
                if updated:
                    pgConn.commit()
            except Exception as e:
                pgConn.rollback()
                self.__logger(message = (f"An Unexpected Error Occurred While Attempting Update DB On Market Currency Data Update\n"
                                         f" * Error:          {e}\n"
                                         f" * Detailed Trace: {traceback.format_exc()}"
                                         ), 
                              logType = 'Error', 
                              color   = 'light_red')

            #[4-4]: Announce the updated info
            updatedIDs         = ('info_server',)+tuple(updated)
            far_functionParams = {'updatedContents': [{'symbol': symbol, 'id': (updatedID,)} for updatedID in updatedIDs]}
            for procName in md_symbol['_subscribers']:
                for updatedID in updatedIDs:
                    func_sendPRDEDIT(targetProcess = procName, 
                                    prdAddress    = ('CURRENCIES', symbol, updatedID), 
                                    prdContent    = md_symbol[updatedID])
                func_sendFAR(targetProcess  = procName, 
                             functionID     = 'onCurrenciesUpdate',
                             functionParams = far_functionParams, 
                             farrHandler    = None)
                
        #[5]: Send First Open Timestamps Search Requests If Collecting Historical
        for target in ('kline', 'depth', 'aggTrade'):
            if md_symbol[f'{target}_firstOpenTS'] is not None: continue
            func_sendFAR(targetProcess  = 'BINANCEAPI', 
                         functionID     = 'getFirstOpenTS', 
                         functionParams = {'symbol': symbol, 
                                           'target': target},
                         farrHandler    = self.__farr_getFirstOpenTS)

    def __th_onCurrencyInfoUpdate(self, task):
        #[1]: Instances
        tParams = task['params']
        symbol      = tParams['symbol']
        infoUpdates = tParams['infoUpdates']
        md_symbol        = self.__marketData[symbol]
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR
        baseAddress_prd = ('CURRENCIES', symbol, 'info_server')
        baseAddress_far = ('info_server',)
        
        #[2]: Market Currency Data Update & Announcement
        for infoUpdate in infoUpdates:
            #[2-1]: Instances
            updateID    = infoUpdate['id']
            updateValue = infoUpdate['value']

            #[2-2]: Target Access
            target = md_symbol['info_server']
            for key in updateID[:-1]:
                target = target[key]

            #[2-3]: Data Update
            target[updateID[-1]] = updateValue

            #[2-4]: Announcement
            prdEdit_prdAddress = baseAddress_prd + updateID
            far_functionParams = {'updatedContents': [{'symbol': symbol, 'id': baseAddress_far+updateID},]}
            for procName in md_symbol['_subscribers']:
                func_sendPRDEDIT(targetProcess = procName, 
                                 prdAddress    = prdEdit_prdAddress, 
                                 prdContent    = updateValue)
                func_sendFAR(targetProcess  = procName, 
                             functionID     = 'onCurrenciesUpdate', 
                             functionParams = far_functionParams, 
                             farrHandler    = None)

    def __th_saveFirstOpenTS(self, task):
        #[1]: Instances
        tParams = task['params']
        symbol      = tParams['symbol']
        target      = tParams['target']
        firstOpenTS = tParams['firstOpenTS']
        md_symbol = self.__marketData[symbol]
        fReqs     = self.__fetchRequests
        pgConn    = self.__pgConn_write
        pgCursor  = self.__pgCursor_write
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR

        #[2]: Save the found firstOpenTS
        md_symbol[f'{target}_firstOpenTS'] = firstOpenTS
        try:
            pgQuery = f"UPDATE descriptors SET {target}_firstOpenTS = %s WHERE symbol = %s"
            params  = (md_symbol[f'{target}_firstOpenTS'], 
                       symbol)
            pgCursor.execute(pgQuery, params)
            pgConn.commit()
        except Exception as e:
            pgConn.rollback()
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Update First Open Timestamp On DB.\n"
                                     f" * Symbol:            {symbol}\n"
                                     f" * Target:            {target}\n"
                                     f" * New First Open TS: {firstOpenTS}\n"
                                     f" * Error:             {e}\n"
                                     f" * Detailed Trace:    {traceback.format_exc()}"
                                    ), 
                          logType = 'Error', 
                          color   = 'light_red')

        #[3]: Currency info update on PRD-GUI via PRD and notification by FAR
        prdEdit_prdAddress = ('CURRENCIES', symbol, f'{target}_firstOpenTS')
        far_functionParams = {'updatedContents': [{'symbol': symbol, 'id': (f'{target}_firstOpenTS',)}]}
        for processName in md_symbol['_subscribers']:
            func_sendPRDEDIT(targetProcess = processName, 
                             prdAddress    = prdEdit_prdAddress, 
                             prdContent    = md_symbol[f'{target}_firstOpenTS'])
            func_sendFAR(targetProcess  = processName, 
                         functionID     = 'onCurrenciesUpdate', 
                         functionParams = far_functionParams, 
                         farrHandler    = None)
        
        #[4]: Send Fetch Request If Possible
        stream_target = md_symbol[f'_stream_{target}s']
        if stream_target['firstOpenTS'] is not None:
            fReqs['pending'][target].add(symbol)

    """
    kline = ([0]:  openTS, 
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
    depth = ([0]: openTS, 
             [1]: closeTS,
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
    aggTrade = ([0]: openTS,
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
    def __th_saveDataFetchResult(self, task):
        #[1]: Instances
        fReqs   = self.__fetchRequests
        tParams = task['params']
        requestID    = tParams['requestID']
        target       = tParams['target']
        fetchedRange = tParams['fetchedRange']
        status       = tParams['status']
        data         = tParams['data']
        request = fReqs['active'][target].get(requestID, None)
        if request is None:
            return
        frType = request['type']
        md           = self.__marketData
        func_sendFAR = self.__ipcA.sendFAR

        #[2]: Result Interpretation
        if status in ('fetching', 'complete'):
            #[2-1]: Instances
            symbol    = request['symbol']
            md_symbol = md[symbol]
            aRanges   = md_symbol[f'{target}s_availableRanges']
            fRange    = fetchedRange
            if   frType == 'FILL':    fBuffer = md_symbol[f'_fetch_{target}s_fill']
            elif frType == 'REFETCH': fBuffer = md_symbol[f'_fetch_{target}s_refetch']
            dIdx_openTS  = COMMONDATAINDEXES['openTime'][target]
            dIdx_closeTS = COMMONDATAINDEXES['closeTime'][target]
            dIdx_source  = COMMONDATAINDEXES['source'][target]

            #[2-2]: Overlap Check
            if frType == 'FILL':
                aRanges_buffer = fBuffer['availableRanges']
                overlaps = []
                if aRanges        is not None and checkNewRangeOverlap(ranges = aRanges,        range_new = fRange): overlaps.append('DB')
                if aRanges_buffer is not None and checkNewRangeOverlap(ranges = aRanges_buffer, range_new = fRange): overlaps.append('BUFFER')
                if overlaps:
                    self.__logger(message = (f"A Data Ranges Overlap Detected While Attempting To Save Fetched Data. The Fetch Request Will Be Updated.\n"
                                            f" * Symbol:                    {symbol}\n"
                                            f" * Target:                    {target}\n"
                                            f" * Available Ranges - DB:     {aRanges}\n"
                                            f" * Available Ranges - BUFFER: {aRanges_buffer}\n"
                                            f" * Fetched Range:             {fRange}\n"
                                            f" * Overlaps:                  {overlaps}"
                                            ),
                                logType = 'Warning',
                                color   = 'light_red')
                    fReqs['pending'][target].add(symbol)
                    del fReqs['active'][target][requestID]
                    self.__updateFetchStatus()
                    return
            
            #[2-3]: Dummy Control & Ranges Update
            #---[2-3-1]: FILL Case, Simply Find Dummy Ranges
            if frType == 'FILL':
                #[2-3-1-1]: Dummy Range
                fRanges_dummy = None
                for dl in data:
                    dl_source = dl[dIdx_source]
                    if dl_source == FORMATTEDDATATYPE_DUMMY:
                        dl_openTS  = dl[dIdx_openTS]
                        dl_closeTS = dl[dIdx_closeTS]
                        if fRanges_dummy is None: fRanges_dummy = [[dl_openTS, dl_closeTS],]
                        else:
                            if fRanges_dummy[-1][1]+1 == dl_openTS: fRanges_dummy[-1][1] = dl_closeTS
                            else:                                   fRanges_dummy.append([dl_openTS, dl_closeTS])
                #[2-3-1-2]: Ranges Update
                fBuffer['availableRanges'] = mergeRangeToRanges(ranges = fBuffer['availableRanges'], range_new = fRange)
                fBuffer['dummyRanges']     = mergeRangesToRanges(ranges1 = fBuffer['dummyRanges'], ranges2 = fRanges_dummy)
            #---[2-3-2]: REFETCH Case, Filter Out Dummy Data
            elif frType == 'REFETCH':
                #[2-3-2-1]: Dummy Filtering
                data = [dl for dl in data if dl[dIdx_source] != FORMATTEDDATATYPE_DUMMY]
                #[2-3-2-2]: Import Buffer Overlap Filtering
                import_aRanges = md_symbol[f'_fetch_{target}s_import']['availableRanges']
                if data and import_aRanges:
                    data = [dl for dl in data
                            if not any(r[0] <= dl[dIdx_openTS] and dl[dIdx_closeTS] <= r[1] for r in import_aRanges)]
                #[2-3-2-3]: Effective Ranges Computation & Update
                if data:
                    fRange_effective = []
                    for dl in data:
                        dl_tOpen  = dl[dIdx_openTS]
                        dl_tClose = dl[dIdx_closeTS]
                        if fRange_effective and fRange_effective[-1][1]+1 == dl_tOpen:
                            fRange_effective[-1][1] = dl_tClose
                        else:
                            fRange_effective.append([dl_tOpen, dl_tClose])
                    fBuffer['availableRanges'] = mergeRangesToRanges(ranges1 = fBuffer['availableRanges'], ranges2 = fRange_effective)

            #[2-5]: Buffer Update & Threshold Check
            if data:
                fBuffer['data'].extend(data)
                fReqs['validBufferLength'] += sum(1 for dl in data if dl[dIdx_source] != FORMATTEDDATATYPE_DUMMY)
                if _FETCHPAUSETHRESHOLD <= fReqs['validBufferLength'] and not fReqs['pauseRequested']:
                    func_sendFAR(targetProcess  = 'BINANCEAPI',
                                 functionID     = 'pauseMarketDataFetch',
                                 functionParams = None,
                                 farrHandler    = None)
                    fReqs['pauseRequested'] = True

            #[2-6]: Ranges Update & Announcement
            request['fetchedRanges'] = mergeRangeToRanges(ranges = request['fetchedRanges'], range_new = fRange)
                        
            #[2-7]: Fetch Status Update
            self.__updateFetchStatus(lastFetched = (symbol, target, time.time()))

        #[3]: Request Update
        if status in ('complete', 'terminate'):
            #[3-1]: Remove 
            del fReqs['active'][target][requestID]
            #[3-2]: On-Termination Fetch Status Update
            if status == 'terminate':
                self.__updateFetchStatus(lastFetched = None)

    def __th_onDataStreamReceival(self, task):
        #[1]: Stream & Closed Check
        tParams = task['params']
        symbol       = tParams['symbol']
        streamType   = tParams['streamType']
        streamedData = tParams['streamedData']
        if not streamedData[COMMONDATAINDEXES['closed'][streamType]]: return

        #[2]: Instances
        md_symbol = self.__marketData.get(symbol, None)
        if md_symbol is None: return
        fReqs        = self.__fetchRequests
        func_sendFAR = self.__ipcA.sendFAR
        sData = md_symbol[f'_stream_{streamType}s']
        sData_data        = sData[f'{streamType}s']
        sData_range       = sData['ranges']
        sData_firstOpenTS = sData['firstOpenTS']
        sData_lastOpenTS  = sData['lastOpenTS']

        #[3]: Collection Check
        if not md_symbol['collecting'][0]: return

        #[4]: Range Check
        sd_openTS  = streamedData[COMMONDATAINDEXES['openTime'][streamType]]
        sd_closeTS = streamedData[COMMONDATAINDEXES['closeTime'][streamType]]
        if sData_lastOpenTS is not None:
            openTS_expected = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL,
                                                                              timestamp  = sData_lastOpenTS,
                                                                              mrktReg    = None,
                                                                              nTicks     = 1)
            #[4-1]: Forward Gap
            if openTS_expected < sd_openTS:
                gap_beg = openTS_expected
                gap_end = sd_openTS-1
                dispatchRID = func_sendFAR(targetProcess  = 'BINANCEAPI',
                                           functionID     = 'fetchData',
                                           functionParams = {'symbol':            symbol,
                                                             'target':            streamType,
                                                             'fetchTargetRanges': [(gap_beg, gap_end)]},
                                           farrHandler    = self.__farr_getDataFetchRequestResult)
                fReqs['active'][streamType][dispatchRID] = {'symbol':            symbol,
                                                            'type':              'FILL',
                                                            'fetchedRanges':     [],
                                                            'fetchTargetRanges': [(gap_beg, gap_end)]}
                self.__logger(message = (f"Gap Detected In Stream Data. Fetch Request Dispatched.\n"
                                         f" * Symbol:      {symbol}\n"
                                         f" * Stream Type: {streamType}\n"
                                         f" * Gap Range:   [{gap_beg}, {gap_end}]"),
                              logType = 'Warning',
                              color   = 'light_yellow')

            #[4-2]: Reverse
            elif sd_openTS < openTS_expected:
                self.__logger(message = (f"An Unexpected Streamed Data Detected And Will Be Disposed.\n"
                                         f" * Symbol:             {symbol}\n"
                                         f" * Streamed Data:      {streamedData}\n"
                                         f" * Received Timestamp: {streamedData[COMMONDATAINDEXES['openTime'][streamType]]}\n"
                                         f" * Expected Timestamp: {openTS_expected}"),
                              logType = 'Warning',
                              color   = 'light_yellow')
                return

        #[5]: First Stream Open TS Update & Fetch Request Pending Queue Append (If Collecting Historical And The First Open TS Is Found)
        if sData_firstOpenTS is None:
            sData['firstOpenTS'] = streamedData[COMMONDATAINDEXES['openTime'][streamType]]
            if md_symbol['collecting'][1] and md_symbol[f'{streamType}_firstOpenTS'] is not None: 
                fReqs['pending'][streamType].add(symbol)

        #[6]: Save The Streamed Data & Update Streamed Range
        sData_data.append(streamedData)
        if sData_range and sData_range[-1][1]+1 == sd_openTS: sData['ranges'][-1][1] = sd_closeTS
        else:                                                 sData['ranges'].append([sd_openTS, sd_closeTS])
        sData['lastOpenTS'] = sd_openTS

    def __th_compressDB(self, task):
        #[1]: Instances
        db_path       = self.__dmConfig['pg_directory']
        pgConn   = self.__pgConn_write
        pgCursor = self.__pgCursor_write
        func_logger   = self.__logger
        func_sendFARR = self.__ipcA.sendFARR

        #[2]: Compression
        compressed        = True
        nCompressed_total = 0
        try:
            pgConn.rollback()
            pgConn.autocommit = True
            for table in ('klines', 'depths', 'aggtrades'):
                func_logger(message = f"Starting Compression For Table '{table}'", 
                            logType = 'Update', 
                            color   = 'light_cyan')
                pgCursor.execute(f"""SELECT compress_chunk(i, if_not_compressed => true) 
                                     FROM show_chunks('{table}', older_than => INTERVAL '7 days') i;
                                  """)
                nCompressed       =  len(pgCursor.fetchall())
                nCompressed_total += nCompressed
                func_logger(message = f"Successfully Compressed {nCompressed} Chunks In Table '{table}'.", 
                            logType = 'Update', 
                            color   = 'light_green')
        except Exception as e:
            compressed = False
            func_logger(message = (f"An Unexpected Error Occurred While Attempting To Compress Market DB.\n"
                                   f" * Error:          {e}\n"
                                   f" * Detailed Trace: {traceback.format_exc()}"), 
                        logType = 'Error', 
                        color   = 'light_red')
        finally:
            pgConn.rollback()
            pgConn.autocommit = False
            func_logger(message = "Market DB Compression Completed!", 
                        logType = 'Update', 
                        color   = 'light_green')

        #[3]: DB Status
        dbStatus = {'location':                db_path,
                    'driveSize_total':         None,
                    'driveSize_used':          None,
                    'driveSize_free':          None,
                    'size_total':              None,
                    'size_beforeCompression':  None,
                    'size_afterCompression':   None}
        try:
            dbStatus.update(self.__getDBStatus(pgCursor = pgCursor))
        except Exception as e:
            func_logger(message = (f"An Unexpected Error Occurred While Attempting To Read PostgreSQL Size After Compression.\n"
                                     f" * DB Path:        {db_path}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"), 
                        logType = 'Error', 
                        color   = 'light_red')
        finally:
            pgConn.rollback()

        #[4]: Result Return
        if compressed: message = f"Successfully Completed Market DB Compression! ({nCompressed_total} Chunks Compressed)"
        else:          message = f"Market DB Compression Failed."
        func_sendFARR(targetProcess  = task['requester'], 
                      functionResult = {'result':   compressed,
                                        'dbStatus': dbStatus,
                                        'message':  message}, 
                      requestID      = task['requestID'],
                      complete       = True)
    
    def __th_resetMarketData(self, task):
        #[1]: Instances
        tParams = task['params']
        symbols = tParams['symbols']
        cSymbols      = self.__collectingSymbols
        md            = self.__marketData
        fReqs         = self.__fetchRequests
        fReqs_pending = fReqs['pending']
        fReqs_active  = fReqs['active']
        pgConn        = self.__pgConn_write
        pgCursor      = self.__pgCursor_write
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR
        func_sendFARR    = self.__ipcA.sendFARR

        #[2]: DB Update
        try:
            pgParams = (symbols,)
            #[2-1]: Descriptor Update
            pgCursor.execute("""UPDATE descriptors 
                                SET kline_firstopents         = NULL,
                                    depth_firstopents         = NULL,
                                    aggTrade_firstopents      = NULL,
                                    klines_availableranges    = NULL,
                                    klines_dummyranges        = NULL,
                                    depths_availableranges    = NULL,    
                                    depths_dummyranges        = NULL,
                                    aggtrades_availableranges = NULL, 
                                    aggtrades_dummyranges     = NULL
                                WHERE symbol = ANY(%s);
                            """, 
                            pgParams)
            #[2-2]: Historical Data Update
            pgCursor.execute("DELETE FROM klines WHERE symbol = ANY(%s);", pgParams)
            pgCursor.execute("DELETE FROM depths WHERE symbol = ANY(%s);", pgParams)
            pgCursor.execute("DELETE FROM aggTrades WHERE symbol = ANY(%s);", pgParams)
            pgConn.commit()
        except Exception as e:
            func_sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':  False, 
                                            'message': f"An Unexpected Error Occurred While Attempting To Clear Market Data ({str(e)})."}, 
                          requestID      = task['requestID'],
                          complete       = True)
            return

        #[3]: Local Instances Update & PRD Edit
        for symbol in symbols:
            #[3-1]: Instances
            md_symbol = md.get(symbol, None)
            if md_symbol is None:
                continue
            far_updatedContents = []
            
            #[3-2]: Descriptor Reset
            md_symbol['kline_firstOpenTS']         = None
            md_symbol['depth_firstOpenTS']         = None
            md_symbol['aggTrade_firstOpenTS']      = None
            md_symbol['klines_availableRanges']    = None
            md_symbol['depths_availableRanges']    = None
            md_symbol['aggTrades_availableRanges'] = None
            md_symbol['klines_dummyRanges']        = None
            md_symbol['depths_dummyRanges']        = None
            md_symbol['aggTrades_dummyRanges']     = None
            md_symbol['collecting']                = (False, False)
            md_symbol['_stream_klines']    = {'klines':    list(), 'ranges': list(), 'firstOpenTS': None, 'lastOpenTS': None}
            md_symbol['_stream_depths']    = {'depths':    list(), 'ranges': list(), 'firstOpenTS': None, 'lastOpenTS': None}
            md_symbol['_stream_aggTrades'] = {'aggTrades': list(), 'ranges': list(), 'firstOpenTS': None, 'lastOpenTS': None}
            for fType in ('fill', 'refetch', 'import'):
                md_symbol[f'_fetch_klines_{fType}']['data'].clear()
                md_symbol[f'_fetch_klines_{fType}']['availableRanges'] = None
                md_symbol[f'_fetch_depths_{fType}']['data'].clear()
                md_symbol[f'_fetch_depths_{fType}']['availableRanges'] = None
                md_symbol[f'_fetch_aggTrades_{fType}']['data'].clear()
                md_symbol[f'_fetch_aggTrades_{fType}']['availableRanges'] = None
                if fType == 'fill':
                    md_symbol[f'_fetch_klines_{fType}']['dummyRanges']    = None
                    md_symbol[f'_fetch_depths_{fType}']['dummyRanges']    = None
                    md_symbol[f'_fetch_aggTrades_{fType}']['dummyRanges'] = None
            
            #[3-3]: PRD Edit & FAR Announcement Params Collection
            for iKey in ('kline_firstOpenTS',
                         'depth_firstOpenTS',
                         'aggTrade_firstOpenTS',
                         'klines_availableRanges',
                         'depths_availableRanges',
                         'aggTrades_availableRanges',
                         'klines_dummyRanges',
                         'depths_dummyRanges',
                         'aggTrades_dummyRanges',
                         'collecting',
                         ):
                prdEdit_prdAddress = ('CURRENCIES', symbol, iKey)
                for procName in md_symbol['_subscribers']:
                    func_sendPRDEDIT(targetProcess = procName, 
                                     prdAddress    = prdEdit_prdAddress, 
                                     prdContent    = md_symbol[iKey])
                far_updatedContents.append({'symbol': symbol, 'id': (iKey,)})

            #[3-4]: FAR Announcement
            far_functionParams = {'updatedContents': far_updatedContents}
            for procName in md_symbol['_subscribers']:
                func_sendFAR(targetProcess  = procName, 
                             functionID     = 'onCurrenciesUpdate',
                             functionParams = far_functionParams, 
                             farrHandler    = None)

        #[4]: Symbol Collection Configuration Update & Announcement
        for symbol in symbols:
            cSymbols[symbol] = {'collectingStream':     False,
                                'collectingHistorical': False}
        self.__saveCollectingSymbolsList()
        updates_ba = [(symbol, False, False) for symbol in symbols]
        func_sendFAR(targetProcess  = 'BINANCEAPI', 
                     functionID     = 'onSymbolCollectionUpdate',
                     functionParams = {'updates': updates_ba}, 
                     farrHandler    = None)

        #[5]: Fetch Requests Clearing & Status Update
        symbols_set = set(symbols)
        for target in ('kline', 'depth', 'aggTrade'):
            for rID in [rID for rID, request in fReqs_active[target].items() if request['symbol'] in symbols_set]:
                del fReqs_active[target][rID]
            fReqs_pending[target] -= symbols_set
        self.__updateFetchStatus()

        #[6]: Result Return
        func_sendFARR(targetProcess  = task['requester'], 
                      functionResult = {'result':  True, 
                                        'message': f"Market Data Successfully Cleared!"}, 
                      requestID      = task['requestID'],
                      complete       = True)

    def __th_refetchDummyMarketData(self, task):
        #[1]: Instances
        md      = self.__marketData
        fReqs   = self.__fetchRequests
        tParams = task['params']
        symbols = tParams['symbols']
        func_sendFAR  = self.__ipcA.sendFAR
        func_sendFARR = self.__ipcA.sendFARR

        #[2]: Dispatch Fetch Requests To BINANCEAPI
        fStatus_updated = False
        for target in ('kline', 'depth', 'aggTrade'):
            #[2-1]: Instances
            fReqs_active  = fReqs['active'][target]

            #[2-2]: Dispatch Fetch Requests To BINANCEAPI
            for symbol in symbols:
                #[2-2-1]: Instances
                md_symbol = md[symbol]
                dRanges   = md_symbol[f'{target}s_dummyRanges']
                if not dRanges: continue

                #[2-2-2]: Determine Fetch Target Ranges
                ftRanges = [dRange.copy() for dRange in dRanges]

                #[2-2-3]: Dispatch Fetch Request
                dispatchRID = func_sendFAR(targetProcess  = 'BINANCEAPI', 
                                           functionID     = 'fetchData', 
                                           functionParams = {'symbol':            symbol,
                                                             'target':            target,
                                                             'fetchTargetRanges': ftRanges}, 
                                           farrHandler = self.__farr_getDataFetchRequestResult)
                fReqs_active[dispatchRID] = {'symbol':            symbol,
                                             'type':              'REFETCH',
                                             'fetchedRanges':     [],
                                             'fetchTargetRanges': ftRanges}
                fStatus_updated = True

        #[3]: Fetch Status Update Announcement
        if fStatus_updated:
            self.__updateFetchStatus()

        #[4]: Result Return
        func_sendFARR(targetProcess  = task['requester'], 
                      functionResult = {'result':  True, 
                                        'message': f"Dummy Ranges Refetch Requests Successfully Requested!"}, 
                      requestID      = task['requestID'],
                      complete       = True)

    def __th_loadDummyMarketDataFromLocalNetwork(self, task):
        #[1]: Instances
        md      = self.__marketData
        tParams = task['params']
        symbols    = tParams['symbols']
        ipAddress  = tParams['ipAddress']
        portNumber = tParams['portNumber']
        dbName     = tParams['dbName']
        user       = tParams['user']
        password   = tParams['password']
        func_sendFAR  = self.__ipcA.sendFAR
        func_sendFARR = self.__ipcA.sendFARR
        func_logger   = self.__logger

        #[2]: Connection Attempt
        conn = None
        try:
            conn = psycopg2.connect(host     = ipAddress,
                                    port     = int(portNumber),
                                    dbname   = dbName,
                                    user     = user,
                                    password = password)
            cursor = conn.cursor()
        except Exception as e:
            func_sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':  False, 
                                            'message': f"Connection Failed: ({str(e)})"}, 
                          requestID      = task['requestID'],
                          complete       = True)
            return
            
        #[3]: Get Descriptor Table Contents
        tSymbols  = set(symbols)
        md_remote = dict()
        try:
            cursor.execute("SELECT * FROM descriptors")
            descriptors = cursor.fetchall()
            for summaryRow in descriptors:
                symbol = summaryRow[0]
                if symbol not in tSymbols: continue
                kline_firstOpenTS         = summaryRow[4]
                depth_firstOpenTS         = summaryRow[5]
                aggTrade_firstOpenTS      = summaryRow[6]
                klines_availableRanges    = summaryRow[7]
                depths_availableRanges    = summaryRow[8]
                aggTrades_availableRanges = summaryRow[9]
                klines_dummyRanges        = summaryRow[10]
                depths_dummyRanges        = summaryRow[11]
                aggTrades_dummyRanges     = summaryRow[12]
                md_remote[symbol] = {'kline_firstOpenTS':         kline_firstOpenTS,
                                     'depth_firstOpenTS':         depth_firstOpenTS,
                                     'aggTrade_firstOpenTS':      aggTrade_firstOpenTS,
                                     'klines_availableRanges':    klines_availableRanges,
                                     'depths_availableRanges':    depths_availableRanges,
                                     'aggTrades_availableRanges': aggTrades_availableRanges,
                                     'klines_dummyRanges':        klines_dummyRanges,
                                     'depths_dummyRanges':        depths_dummyRanges,
                                     'aggTrades_dummyRanges':     aggTrades_dummyRanges}
        except Exception as e:
            conn.rollback()
            func_logger(message = (f"An Unexpected Error Occurred While Attempting To Read The Remote Descriptor Table.\n"
                                   f" * Error:          {e}\n"
                                   f" * Detailed Trace: {traceback.format_exc()}"), 
                        logType = 'Error', 
                        color   = 'light_red')
            func_sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':  False, 
                                            'message': f"Sync Error: {str(e)}"}, 
                          requestID      = task['requestID'],
                          complete       = True)
            return

        #[4]: Fetch Target Determination
        fetchTargets = {'kline':    dict(),
                        'depth':    dict(),
                        'aggTrade': dict()}
        for symbol in symbols:
            #[4-1]: Instances
            md_symbol        = md.get(symbol,        None)
            md_remote_symbol = md_remote.get(symbol, None)
            if md_symbol is None or md_remote_symbol is None:
                continue
            for target in ('kline', 'depth', 'aggTrade'):
                dRanges_local  = md_symbol[f'{target}s_dummyRanges']
                aRanges_remote = md_remote_symbol[f'{target}s_availableRanges']
                dRanges_remote = md_remote_symbol[f'{target}s_dummyRanges']
                if not dRanges_local:  continue
                if not aRanges_remote: continue

                #[4-2]: Intersections Between The Local Dummy Ranges And The Remote Available Ranges
                fRanges_initial = []
                for dRange_local in dRanges_local:
                    for aRange_remote in aRanges_remote:
                        overlap_beg = max(dRange_local[0], aRange_remote[0])
                        overlap_end = min(dRange_local[1], aRange_remote[1])
                        if overlap_beg <= overlap_end:
                            fRanges_initial.append([overlap_beg, overlap_end])
                if not fRanges_initial: continue

                #[4-3]: Remote Dummy Ranges Filtering
                if not dRanges_remote:
                    fRanges_final = fRanges_initial
                else:
                    fRanges_final = []
                    for fRange in fRanges_initial:
                        current_pieces = [fRange,]
                        for dRange_remote in dRanges_remote:
                            next_pieces = []
                            for piece in current_pieces:
                                overlap_beg = max(piece[0], dRange_remote[0])
                                overlap_end = min(piece[1], dRange_remote[1])
                                if overlap_beg <= overlap_end:
                                    if piece[0] < overlap_beg:
                                        next_pieces.append([piece[0], overlap_beg - 1])
                                    if overlap_end < piece[1]:
                                        next_pieces.append([overlap_end + 1, piece[1]])
                                else:
                                    next_pieces.append(piece)
                            current_pieces = next_pieces
                        fRanges_final.extend(current_pieces)
                if not fRanges_final: continue
                
                #[4-4]: Fragmented Ranges Merging
                fRanges_final.sort(key=lambda x: x[0])
                fRanges_merged = []
                for fRange in fRanges_final:
                    if not fRanges_merged or fRanges_merged[-1][1]+1 < fRange[0]:
                        fRanges_merged.append(fRange)
                    else:
                        fRanges_merged[-1][1] = fRange[1]

                #[4-5]: Save
                fetchTargets[target][symbol] = fRanges_merged

        #[5]: Data Fetch & Buffer Save
        nImported = 0
        for target, target_symbols in fetchTargets.items():
            dIdx_openTS  = COMMONDATAINDEXES['openTime'][target]
            dIdx_closeTS = COMMONDATAINDEXES['closeTime'][target]
            for symbol, ftrs in target_symbols.items():
                md_symbol    = md[symbol]
                fBuffer_import  = md_symbol[f'_fetch_{target}s_import']
                fBuffer_refetch = md_symbol[f'_fetch_{target}s_refetch']
                for ftr in ftrs:
                    fr_beg, fr_end = ftr
                    #[5-1]: Refetch Buffer Overlap Check
                    refetch_aRanges = fBuffer_refetch['availableRanges']
                    if refetch_aRanges:
                        ftr_ranges_effective = subtractRangesFromRanges(ranges1 = [[fr_beg, fr_end]],
                                                                        ranges2 = refetch_aRanges)
                    else:
                        ftr_ranges_effective = [[fr_beg, fr_end]]
                    if not ftr_ranges_effective:
                        continue

                    #[5-2]: Remote DB Fetch
                    try:
                        cursor.execute(PGQUERY_READFROMDB[target], (symbol, fr_beg, fr_end))
                        data_DB = cursor.fetchall()
                    except Exception as e:
                        self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Import Data From Local Network.\n"
                                                 f" * Error:          {e}\n"
                                                 f" * Detailed Trace: {traceback.format_exc()}"
                                                ),
                                      logType = 'Warning',
                                      color   = 'light_red')
                        continue
                    if not data_DB:
                        continue
                    if   target == 'kline':    fetchedData = [kl[:11]     +(True, kl[11])      for kl       in data_DB]
                    elif target == 'depth':    fetchedData = [depth[:14]  +(True, depth[14])   for depth    in data_DB]
                    elif target == 'aggTrade': fetchedData = [aggTrade[:8]+(True, aggTrade[8]) for aggTrade in data_DB]

                    #[5-3]: Filter Out Data That Falls Within Refetch Buffer Ranges
                    if refetch_aRanges:
                        fetchedData = [dl for dl in fetchedData
                                        if not any(r[0] <= dl[dIdx_openTS] and dl[dIdx_closeTS] <= r[1] for r in refetch_aRanges)]
                    if not fetchedData:
                        continue

                    #[5-4]: Effective Range Computation
                    fRange_effective = []
                    for dl in fetchedData:
                        dl_tOpen  = dl[dIdx_openTS]
                        dl_tClose = dl[dIdx_closeTS]
                        if fRange_effective and fRange_effective[-1][1]+1 == dl_tOpen:
                            fRange_effective[-1][1] = dl_tClose
                        else:
                            fRange_effective.append([dl_tOpen, dl_tClose])

                    #[5-5]: Buffer Update
                    fBuffer_import['data'].extend(fetchedData)
                    fBuffer_import['availableRanges'] = mergeRangesToRanges(ranges1 = fBuffer_import['availableRanges'],
                                                                                ranges2 = fRange_effective)
                    nImported += len(fetchedData)

        #[6]: Connection Close
        conn.close()

        #[7]: Result Return
        func_sendFARR(targetProcess  = task['requester'], 
                      functionResult = {'result':  True, 
                                        'message': f"Successfully Imported {nImported} Market Data!"}, 
                      requestID      = task['requestID'],
                      complete       = True)

    def __th_registerCurrencyInfoSubscription(self, task):
        #[1]: Instances
        requester = task['requester']
        tParams   = task['params']
        symbol = tParams['symbol']

        #[2]: Symbol Check
        md_symbol = self.__marketData.get(symbol, None)
        if md_symbol is None:
            return
        
        #[3]: Subscription Add
        md_symbol['_subscribers'].add(requester)

        #[4]: Symbol Market Data Announcement
        md_symbol_announce = {k: md_symbol[k] for k in _MARKETDATA_ANNOUNCEMENT_KEYS}
        self.__ipcA.sendPRDEDIT(targetProcess = requester, 
                                prdAddress    = ('CURRENCIES', symbol), 
                                prdContent    = md_symbol_announce)
        self.__ipcA.sendFAR(targetProcess  = requester, 
                            functionID     = 'onCurrenciesUpdate', 
                            functionParams = {'updatedContents': [{'symbol': symbol, 'id': '_ONFIRSTSUBSCRIPTION'},]}, 
                            farrHandler    = None)

    def __th_unregisterCurrencyInfoSubscription(self, task):
        #[1]: Instances
        requester = task['requester']
        tParams   = task['params']
        symbol = tParams['symbol']

        #[2]: Symbol Check
        md_symbol = self.__marketData.get(symbol, None)
        if md_symbol is None:
            return
        
        #[3]: Subscription Removal
        if requester in md_symbol['_subscribers']: 
            md_symbol['_subscribers'].remove(requester)
            self.__ipcA.sendPRDREMOVE(targetProcess = requester, 
                                      prdAddress    = ('CURRENCIES', symbol))
    #Task Handlers END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Thread Execution Handlers ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __teh_readDBStatus(self, requester, requestID):
        #[1]: Instances
        pgPool        = self.__pgPool
        func_sendFARR = self.__ipcA.sendFARR
        db_path       = self.__dmConfig['pg_directory']
        dbStatus = {'location':                db_path,
                    'driveSize_total':         None,
                    'driveSize_used':          None,
                    'driveSize_free':          None,
                    'size_total':              None,
                    'size_beforeCompression':  None,
                    'size_afterCompression':   None}

        #[2]: Data Fetch
        pgConn = None
        #---[2-1]: Fetch Attempt
        try:
            #[2-1-1]: Connection & Cursor
            pgConn   = pgPool.getconn()
            pgCursor = pgConn.cursor()

            #[2-1-2]: DB Status
            dbStatus.update(self.__getDBStatus(pgCursor = pgCursor))

            #[2-1-3]: Close Transaction
            pgConn.rollback()

            #[2-1-4]: Return Return
            func_sendFARR(targetProcess  = requester, 
                          functionResult = {'type':     'market',
                                            'result':   True, 
                                            'dbStatus': dbStatus, 
                                            'message':  "DB Status Succesfully Read!"}, 
                          requestID      = requestID,
                          complete       = True)

        #---[2-2]: Exception Handling
        except Exception as e:
            #[2-2-1]: Return Return
            func_sendFARR(targetProcess  = requester, 
                          functionResult = {'type':     'market',
                                            'result':   False, 
                                            'dbStatus': dbStatus, 
                                            'message':  f"An Unexpected Error Occurred While Attempting To Read PostgreSQL Size. ({str(e)})"}, 
                          requestID      = requestID,
                          complete       = True)
            
            #[2-2-2]: Logging
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Read PostgreSQL Size.\n"
                                     f" * DB Path:        {db_path}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"), 
                          logType = 'Error', 
                          color   = 'light_red')
            
            #[2-2-3]: Rollback
            if pgConn is not None: pgConn.rollback()

        #---[2-3]: Connection Retrieval
        finally:
            if pgConn is not None: pgPool.putconn(pgConn)
        
    def __teh_fetchMarketData(self, requester, requestID, symbol, target, fetchRange):
        #[1]: Instances
        pgPool = self.__pgPool
        md     = self.__marketData
        func_sendFARR = self.__ipcA.sendFARR
        md_symbol = md.get(symbol, None)
        if md_symbol is None:
            func_sendFARR(targetProcess  = requester, 
                          functionResult = {'result': 'SNF', #SNF: Symbol Not Found
                                            'data':   None}, 
                          requestID      = requestID, 
                          complete       = True)
            return
        
        #[2]: Target Check
        if target not in ('kline', 'depth', 'aggTrade'):
            func_sendFARR(targetProcess  = requester, 
                          functionResult = {'result': 'UDT', #UDT: Unexpected Data Type
                                            'data':   None}, 
                          requestID      = requestID, 
                          complete       = True)
            return

        #[3]: Data Availability Check
        dataAvailable = False
        aRanges = md_symbol[f'{target}s_availableRanges']
        if aRanges:
            fRange_beg, fRange_end = fetchRange
            for aRange_beg, aRange_end in md_symbol[f'{target}s_availableRanges']:
                classification = 0
                classification += 0b1000*(0 <= aRange_beg-fRange_beg)
                classification += 0b0100*(0 <= aRange_beg-fRange_end)
                classification += 0b0010*(0 <  aRange_end-fRange_beg)
                classification += 0b0001*(0 <  aRange_end-fRange_end)
                if classification in (0b0010, 0b1010, 0b1011, 0b0011):
                    dataAvailable = True
                    break
        if not dataAvailable:
            func_sendFARR(targetProcess  = requester, 
                          functionResult = {'result': 'DNA', #DNA: Data Not Available
                                            'data':   None}, 
                          requestID      = requestID, 
                          complete       = True)
            return 

        #[4]: Data Fetch
        pgConn = None
        #---[4-1]: Fetch Attempt
        try:
            #[4-1-1]: Instances
            pgConn   = pgPool.getconn()
            pgCursor = pgConn.cursor()
            func_gnitt = atmEta_Auxillaries.getNextIntervalTickTimestamp

            #[4-1-2]: Fetch Data
            fr_beg, fr_end = fetchRange
            pgCursor.execute(PGQUERY_READFROMDB[target], (symbol, fr_beg, fr_end))
            data_DB = pgCursor.fetchall()
            dIdx_openTS = COMMONDATAINDEXES['openTime'][target]
            if target == 'kline':    
                fetchedData  = {fd[dIdx_openTS]: fd[:11]+(True, fd[11]) for fd in data_DB}
                dummyBaseLen = 9
            elif target == 'depth':    
                fetchedData  = {fd[dIdx_openTS]: fd[:14]+(True, fd[14]) for fd in data_DB}
                dummyBaseLen = 12
            elif target == 'aggTrade': 
                fetchedData  = {fd[dIdx_openTS]: fd[: 8]+(True, fd[ 8]) for fd in data_DB}
                dummyBaseLen = 6
            tsList_expeceted = atmEta_Auxillaries.getTimestampList_byRange(intervalID        = KLINTERVAL,
                                                                           mrktReg           = None, 
                                                                           timestamp_beg     = fr_beg, 
                                                                           timestamp_end     = fr_end, 
                                                                           lastTickInclusive = True)
            fetchedData_dummyFilled = []
            for ts_exp in tsList_expeceted:
                if ts_exp in fetchedData:
                    fetchedData_dummyFilled.append(fetchedData[ts_exp])
                else:
                    ts_exp_close = func_gnitt(intervalID = KLINTERVAL, 
                                              timestamp  = ts_exp, 
                                              mrktReg    = None, 
                                              nTicks     = 1)-1
                    dummy = [ts_exp, ts_exp_close] + [None]*dummyBaseLen + [True, FORMATTEDDATATYPE_DUMMY]
                    fetchedData_dummyFilled.append(tuple(dummy))

            #[4-1-3]: Close Transaction
            pgConn.rollback()

            #[4-1-4]: Result Dispatch
            func_sendFARR(targetProcess  = requester, 
                          functionResult = {'result':     'SDF', #SDF: Successful Data Fetch
                                            'data':       fetchedData_dummyFilled, 
                                            'fetchRange': fetchRange}, 
                          requestID      = requestID, 
                          complete       = True)
            
        #---[4-2]: Exception Handling
        except Exception as e:
            #[4-2-1]: Return Return
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Fetch Market Data From The Database.\n"
                                     f" * Requester:      {requester}\n"
                                     f" * RequestID:      {requestID}\n"
                                     f" * Symbol:         {symbol}\n"
                                     f" * Target:         {target}\n"
                                     f" * Fetch Range:    {fetchRange}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"
                                    ), 
                          logType = 'Error', 
                          color   = 'light_red')
            
            #[4-2-2]: Logging
            func_sendFARR(targetProcess  = requester, 
                          functionResult = {'result': 'UEO', #UEO: Unexpected Error Occurred
                                            'data':   None}, 
                          requestID      = requestID, 
                          complete       = True)
            
            #[4-2-3]: Rollback
            if pgConn is not None: pgConn.rollback()
            
        #---[5-3]: Connection Retrieval
        finally:
            if pgConn is not None: pgPool.putconn(pgConn)
    #Thread Execution Handlers END --------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #FAR & FARR Handlers ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __far_registerCurrency(self, requester, symbol, info):
        #[1]: Requester Check
        if requester != 'BINANCEAPI':
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'registerCurrency',
                'requester': requester,
                'requestID': None,
                'params':    {'symbol': symbol, 
                              'info':   info}
               }
        self.__taskQueue.put(task)
                
    def __far_onCurrencyInfoUpdate(self, requester, symbol, infoUpdates):
        #[1]: Requester Check
        if requester != 'BINANCEAPI':
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'onCurrencyInfoUpdate',
                'requester': requester,
                'requestID': None,
                'params':    {'symbol':      symbol, 
                              'infoUpdates': infoUpdates}
               }
        self.__taskQueue.put(task)
    
    def __farr_getFirstOpenTS(self, responder, requestID, functionResult):
        #[1]: Function Result
        symbol      = functionResult['symbol']
        target      = functionResult['target']
        firstOpenTS = functionResult['firstOpenTS']
        if firstOpenTS is None:
            return

        #[2]: Task Generation & Add
        task = {'type':      'saveFirstOpenTS',
                'requester': None,
                'requestID': None,
                'params':    {'symbol':      symbol, 
                              'target':      target,
                              'firstOpenTS': firstOpenTS}
               }
        self.__taskQueue.put(task)

    def __farr_getDataFetchRequestResult(self, responder, requestID, functionResult):
        #[1]: Task Generation & Add
        task = {'type':      'saveDataFetchResult',
                'requester': None,
                'requestID': None,
                'params':    {'requestID':    requestID,
                              'target':       functionResult['target'],
                              'fetchedRange': functionResult['fetchedRange'], 
                              'status':       functionResult['status'],
                              'data':         functionResult['data']}
               }
        self.__taskQueue.put(task)
            
    def __far_onKlineStreamReceival(self, requester, symbol, kline):
        #[1]: Source Check
        if requester != 'BINANCEAPI':
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'onDataStreamReceival',
                'requester': requester,
                'requestID': None,
                'params':    {'symbol':       symbol, 
                              'streamType':   'kline',
                              'streamedData': kline}
               }
        self.__taskQueue.put(task)

    def __far_onDepthStreamReceival(self, requester, symbol, depth):
        #[1]: Source Check
        if requester != 'BINANCEAPI':
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'onDataStreamReceival',
                'requester': requester,
                'requestID': None,
                'params':    {'symbol':       symbol, 
                              'streamType':   'depth',
                              'streamedData': depth}
               }
        self.__taskQueue.put(task)

    def __far_onAggTradeStreamReceival(self, requester, symbol, aggTrade):
        #[1]: Source Check
        if requester != 'BINANCEAPI':
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'onDataStreamReceival',
                'requester': requester,
                'requestID': None,
                'params':    {'symbol':       symbol, 
                              'streamType':   'aggTrade',
                              'streamedData': aggTrade}
               }
        self.__taskQueue.put(task)

    def __far_setMarketDataCollection(self, requester, requestID, symbols, mode):
        #[1]: Requester Check
        if requester != 'GUI':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'result': None, 'message': f"Invalid Requester"}, 
                                 requestID      = requestID,
                                 complete       = True)
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'setMarketDataCollection',
                'requester': requester,
                'requestID': requestID,
                'params':    {'symbols': symbols,
                              'mode':    mode}
               }
        self.__taskQueue.put(task)

    def __far_readDBStatus(self, requester, requestID):
        #[1]: Requester Check
        if requester != 'GUI':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'type':     'market',
                                                   'result':   False, 
                                                   'dbStatus': None, 
                                                   'message':  f"Invalid Requester"}, 
                                 requestID      = requestID,
                                 complete       = True)
            return
        
        #[2]: Task Submit
        self.__taskPool.submit(self.__teh_readDBStatus, requester, requestID)

    def __far_resetMarketData(self, requester, requestID, symbols):
        #[1]: Requester Check
        if requester != 'GUI':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'result':  False,
                                                   'message': f"Invalid Requester"}, 
                                 requestID      = requestID,
                                 complete       = True)
            return
            
        #[2]: Task Generation & Add
        task = {'type':      'resetMarketData',
                'requester': requester,
                'requestID': requestID,
                'params':    {'symbols': symbols}
               }
        self.__taskQueue.put(task)

    def __far_refetchDummyMarketData(self, requester, requestID, symbols):
        #[1]: Requester Check
        if requester != 'GUI':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'result':  False, 
                                                   'message': f"Invalid Requester"}, 
                                 requestID      = requestID,
                                 complete       = True)
            return
            
        #[2]: Task Generation & Add
        task = {'type':      'refetchDummyMarketData',
                'requester': requester,
                'requestID': requestID,
                'params':    {'symbols': symbols}
               }
        self.__taskQueue.put(task)

    def __far_compressMarketDB(self, requester, requestID):
        #[1]: Requester Check
        if requester != 'GUI':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'result':  False, 
                                                   'message': f"Invalid Requester"}, 
                                 requestID      = requestID,
                                 complete       = True)
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'compressDB',
                'requester': requester,
                'requestID': requestID,
                'params':    None
               }
        self.__taskQueue.put(task)

    def __far_loadDummyMarketDataFromLocalNetwork(self, requester, requestID, symbols, ipAddress, portNumber, dbName, user, password):
        #[1]: Requester Check
        if requester != 'GUI':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'result':  False, 
                                                   'message': f"Invalid Requester"}, 
                                 requestID      = requestID,
                                 complete       = True)
            return
            
        #[2]: Task Generation & Add
        task = {'type':      'loadDummyMarketDataFromLocalNetwork',
                'requester': requester,
                'requestID': requestID,
                'params':    {'symbols': symbols,
                              'ipAddress':  ipAddress,
                              'portNumber': portNumber,
                              'dbName':     dbName,
                              'user':       user,
                              'password':   password}
               }
        self.__taskQueue.put(task)

    def __far_fetchMarketData(self, requester, requestID, symbol, target, fetchRange):
        #[1]: Task Submit
        self.__taskPool.submit(self.__teh_fetchMarketData, requester, requestID, symbol, target, fetchRange)
    
    def __far_registerCurrecnyInfoSubscription(self, requester, symbol):
        #[1]: Task Generation & Add
        task = {'type':      'registerCurrencyInfoSubscription',
                'requester': requester,
                'requestID': None,
                'params':    {'symbol': symbol}
               }
        self.__taskQueue.put(task)
    
    def __far_unregisterCurrecnyInfoSubscription(self, requester, symbol):
        #[1]: Task Generation & Add
        task = {'type':      'unregisterCurrencyInfoSubscription',
                'requester': requester,
                'requestID': None,
                'params':    {'symbol': symbol}
               }
        self.__taskQueue.put(task)
    #FAR & FARR Handlers END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------




    
    #Auxilliary Functions -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __getDBStatus(self, pgCursor):
        db_path = self.__dmConfig['pg_directory']
        db_name = self.__pg_config['dbname']
        
        #[1]: DB Drive Size
        drive_usage = shutil.disk_usage(db_path)

        #[2]: Total DB Size
        pgCursor.execute(f"SELECT pg_database_size('{db_name}');")
        db_size_total = pgCursor.fetchone()[0]

        #[3]: Compression Size
        pgCursor.execute("""SELECT 
                            SUM(before_compression_total_bytes) AS before_bytes,
                            SUM(after_compression_total_bytes) AS after_bytes
                            FROM 
                            (
                            SELECT (hypertable_compression_stats(h.hypertable_name::regclass)).*
                            FROM timescaledb_information.hypertables h
                            ) AS stats_subquery;
                        """)
        comp_stats = pgCursor.fetchone()
        db_size_bc = int(comp_stats[0]) if comp_stats[0] is not None else None
        db_size_ac = int(comp_stats[1]) if comp_stats[1] is not None else None

        #[4]: Result Return
        dbStatus = {'location':                db_path,
                    'driveSize_total':         drive_usage.total,
                    'driveSize_used':          drive_usage.used,
                    'driveSize_free':          drive_usage.free,
                    'size_total':              db_size_total,
                    'size_beforeCompression':  db_size_bc,
                    'size_afterCompression':   db_size_ac}
        return dbStatus
    
    def __checkDBBusy(self):
        pgConn   = self.__pgConn_write
        pgCursor = self.__pgCursor_write
        try:
            pgCursor.execute("""SELECT COUNT(*)
                                FROM pg_stat_activity
                                WHERE wait_event_type = 'IO';
                             """)
            io_waiting = pgCursor.fetchone()[0]
            pgConn.rollback()
            return 0 < io_waiting
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Check DB IO Pending Activity. Possible Server Disconnection Or DB Corruption Suspected. User Attention Advised.\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"), 
                          logType = 'Error', 
                          color   = 'light_red')
            pgConn.rollback()
            return True

    def __updateFetchStatus(self, lastFetched = None, fetchSpeeds = None):
        #[1]: Instances
        fReqs   = self.__fetchRequests
        fStatus = self.__fetchStatus
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR

        #[2]: Parameters Update
        #---[2-1]: Last Fetched
        if lastFetched is not None:
            fStatus['lastFetched'] = lastFetched

        #---[2-2]: Remaining Ranges
        for target in ('kline', 'depth', 'aggTrade'):
            rRangeWidth = 0
            for request in fReqs['active'][target].values():
                fetchedRanges_width     = sum(fr[1] -fr[0] +1 for fr  in request['fetchedRanges'])
                fetchTargetRanges_width = sum(ftr[1]-ftr[0]+1 for ftr in request['fetchTargetRanges'])
                rRangeWidth += (fetchTargetRanges_width-fetchedRanges_width)
            fStatus[f'remainingRanges_{target}'] = None if rRangeWidth == 0 else rRangeWidth

        #---[2-3]: Fetch Speed
        if fetchSpeeds is not None:
            for target, fSpeed in fetchSpeeds.items():
                if fSpeed is None:
                    continue
                fSpeed_prev = fStatus[f'fetchSpeed_{target}']
                if fSpeed_prev is None:
                    fSpeed = fSpeed
                else:
                    kValue = 2/(_FETCHSPEEDNSAMPLES+1)
                    fSpeed = (fSpeed*kValue) + (fSpeed_prev*(1-kValue))
                fStatus[f'fetchSpeed_{target}'] = fSpeed

        #---[2-4]: Estimated Completion Time
        fetchSpeed_sum = 0
        nContributors  = 0
        for target in ('kline', 'depth', 'aggTrade'):
            fSpeed = fStatus[f'fetchSpeed_{target}']
            if fSpeed is not None:
                fetchSpeed_sum += fSpeed
                nContributors  += 1
        fetchSpeed_avg = None if nContributors == 0 else fetchSpeed_sum/nContributors
        if fetchSpeed_avg:
            etc_sum = 0
            for target in ('kline', 'depth', 'aggTrade'):
                rRangeWidth = fStatus[f'remainingRanges_{target}']
                fSpeed      = fStatus[f'fetchSpeed_{target}']
                if rRangeWidth is None: continue
                if fSpeed is None:
                    etc_target = rRangeWidth/max(fetchSpeed_avg, 1e-12)
                else:
                    etc_target = rRangeWidth/max(fSpeed, 1e-12)
                etc_sum += etc_target
        else:
            etc_sum = None
        fStatus['estimatedTimeOfCompletion'] = etc_sum

        #[3]: Announcement
        func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'FETCHSTATUS', prdContent = self.__fetchStatus.copy())
        func_sendFAR(targetProcess  = 'GUI', 
                     functionID     = 'onFetchStatusUpdate', 
                     functionParams = None, 
                     farrHandler    = None)
    #Auxilliary Functions END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    