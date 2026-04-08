#ATM Modules
import ipc

#Python Modules
import threading
import termcolor
import time
import traceback
import queue
import json
import os
import sqlite3
from collections import deque
from datetime    import datetime

#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT

class Worker:
    def __init__(self, path_project, dmConfig, ipcA):
        #[1]: Base Parameters & Instances
        path_dbFolder = os.path.join(path_project, 'data', 'db')
        self.__path_dbFolder = path_dbFolder
        self.__dmConfig      = dmConfig
        self.__ipcA          = ipcA

        #[2]: Task Data
        self.__accountDescriptions = dict()
        self.__accountLocalIDsByID = dict()

        #[3]: FAR Handlers Setup
        ipcA.addFARHandler('readAccountDBStatus',         self.__far_readDBStatus,         executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #GUI
        ipcA.addFARHandler('loadAccountDescriptions',     self.__far_loadDescriptions,     executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #TRADEMANAGER
        ipcA.addFARHandler('addAccountDescription',       self.__far_addDescription,       executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #TRADEMANAGER
        ipcA.addFARHandler('removeAccountDescription',    self.__far_removeDescription,    executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #TRADEMANAGER
        ipcA.addFARHandler('editAccountData',             self.__far_editData,             executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #TRADEMANAGER
        ipcA.addFARHandler('addAccountTradeLog',          self.__far_addTradeLog,          executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #TRADEMANAGER
        ipcA.addFARHandler('updateAccountPeriodicReport', self.__far_updatePeriodicReport, executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #TRADEMANAGER
        ipcA.addFARHandler('fetchAccountTradeLog',        self.__far_fetchTradeLog,        executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #GUI
        ipcA.addFARHandler('fetchAccountPeriodicReports', self.__far_fetchPeriodicReports, executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #GUI

        #[4]: Task Handling Thread Setup
        self.__taskQueue = queue.Queue()
        self.__wThread   = threading.Thread(target = self.__processLoop, args = (), daemon = False)
        self.__taskHandlers = {'initialDBRead':        self.__th_initialDBRead,
                               'readDBStatus':         self.__th_readDBStatus,
                               'loadDescriptions':     self.__th_loadDescriptions,
                               'addDescription':       self.__th_addDescription,
                               'removeDescription':    self.__th_removeDescription,
                               'fetchTradeLogs':       self.__th_fetchTradeLogs,
                               'fetchPeriodicReports': self.__th_fetchPeriodicReports}
        self.__periodicProcesses = {'editData':           self.__pp_editData,
                                    'addTradeLogs':       self.__pp_addTradeLogs,
                                    'addPeriodicReports': self.__pp_addPeriodicReports}
        self.__ppQueue_editData          = deque()
        self.__ppQueue_addTradeLog       = deque()
        self.__ppQueue_addPeriodicReport = deque()
        
        #[5]: Initial Task Completion Flag
        self.__initialTaskComplete = False

    #System -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __processLoop(self):
        #[1]: Instances
        tQueue     = self.__taskQueue
        tHandlers  = self.__taskHandlers
        pProcesses = self.__periodicProcesses
        logger     = self.__logger

        #[2]: Sqlite3 Connection & Cursor
        sqlConn   = sqlite3.connect(os.path.join(self.__path_dbFolder, 'atmEta_accounts.db'))
        sqlCursor = sqlConn.cursor()
        
        #[3]: Task Handling Loop
        while True:
            #[3-1]: Handling Attempt
            task = None
            try:
                #[3-1-1]: Task
                task = tQueue.get(timeout = 1)
                #[3-1-2]: Termination Check
                if task is None:
                    tQueue.task_done()
                    break
                #[3-3-3]: Task Handling
                tHandlers[task['type']](sqlConn   = sqlConn,
                                        sqlCursor = sqlCursor,
                                        task      = task)
                tQueue.task_done()
            #[3-2]: Empty Queue & Periodic Mass Insertion Queue Check
            except queue.Empty:
                if any(pProcess(sqlCursor = sqlCursor) for pProcess in pProcesses.values()):
                    sqlConn.commit()
            #[3-3]: Exception Handling
            except Exception as e: 
                if task is not None: tQueue.task_done()
                logger(message = (f"An Unexpected Error Occurred While Attempting To Handle A Task\n"
                                  f" * Error:          {e}\n"
                                  f" * Detailed Trace: {traceback.format_exc()}"),
                       logType = 'Error', 
                       color   = 'light_red')
        
        #[4]: Final Periodic Processes
        if any(pProcess(sqlCursor = sqlCursor) for pProcess in pProcesses.values()):
            sqlConn.commit()

        #[5]: Sqlite3 Connection Close
        sqlConn.close()

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
        msg      = f"[DATAMANAGER-ACCOUNTDATAWORKER-{time_str}] {message}"
        print(termcolor.colored(msg, color))
    
    def initialTaskComplete(self):
        return self.__initialTaskComplete
    #System END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




    
    #Periodic Processes -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __pp_editData(self, sqlCursor):
        #[1]: Instances
        aDescs = self.__accountDescriptions
        ppq_ed = self.__ppQueue_editData
        if not ppq_ed: return False

        #[2]: Update Divisions
        ud_inserts = dict()
        ud_updates = dict()

        #[3]: Updates Collection
        while ppq_ed:
            #[3-1]: Update Content & Instances
            address, newValue = ppq_ed.popleft()
            localID = address[0]
            aDesc = aDescs.get(localID, None)
            if aDesc is None:
                continue

            #[3-2]: Asset
            if address[1] == 'assets':
                table = aDesc['assetsTableName']
                key   = (table, address[3])
                if key not in ud_updates:
                    ud_updates[key] = []
                ud_updates[key].append((newValue, aDesc['assets_dbID'][address[2]]))

            #[3-3]: Position
            elif address[1] == 'positions':
                table = aDesc['positionsTableName']

                #[3-3-1]: New Position
                if address[3] == '#NEW#':
                    if table not in ud_inserts:
                        ud_inserts[table] = []
                    positions_dbIDs = set(position_dbID for position_dbID in aDesc['positions_dbID'].values())
                    position_dbID   = 0
                    while position_dbID in positions_dbIDs: position_dbID += 1
                    if   newValue['isolated'] == True:  isolated = 1
                    elif newValue['isolated'] == False: isolated = 0
                    elif newValue['isolated'] is None:  isolated = None
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
                    aDesc['positions_dbID'][address[2]] = position_dbID
                    ud_inserts[table].append(positionData_formatted)

                #[3-3-2]: Trade Control Tracker & Abrupt Clearing Records
                elif address[3] in ('tradeControlTracker', 'abruptClearingRecords'):
                    key = (table, address[3])
                    if key not in ud_updates:
                        ud_updates[key] = []
                    ud_updates[key].append((json.dumps(newValue), aDesc['positions_dbID'][address[2]]))

                #[3-3-3]: General
                else:
                    key = (table, address[3])
                    if key not in ud_updates:
                        ud_updates[key] = []
                    ud_updates[key].append((newValue, aDesc['positions_dbID'][address[2]]))

        #[4]: Queries Execution
        for table, iParamsList in ud_inserts.items():
            sqlCursor.executemany(f"""INSERT INTO {table} 
                                  (id,
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
                                   abruptClearingRecords
                                  ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                                  iParamsList)
        for (table, col), uParamsList in ud_updates.items():
            sqlCursor.executemany(f"UPDATE {table} SET {col} = ? WHERE id = ?", uParamsList)

        #[5]: Return True To Commit
        return True

    def __pp_addTradeLogs(self, sqlCursor):
        #[1]: Instances
        aDescs  = self.__accountDescriptions
        ppq_atl = self.__ppQueue_addTradeLog
        if not ppq_atl: return False

        #[2]: Updates Collection
        uc = dict()
        while ppq_atl:
            #[2-1]: Update Content & Instances
            localID, tradeLog = ppq_atl.popleft()
            aDesc = aDescs.get(localID, None)
            if aDesc is None:
                continue

            #[2-2]: Collection
            table = aDesc['tradeLogsTableName']
            if table not in uc:
                uc[table] = list()
            uc[table].append((aDesc['nTradeLog'], json.dumps(tradeLog)))
            
            #[2-3]: Local Descriptor Update
            aDesc['nTradeLog'] += 1

        #[3]: Queries Execution
        for table, iParamsList in uc.items():
            sqlCursor.executemany(f"INSERT INTO {table} (id, tradeLog) VALUES (?, ?)", iParamsList)
        
        #[4]: Return True To Commit
        return True

    def __pp_addPeriodicReports(self, sqlCursor):
        #[1]: Instances
        aDescs  = self.__accountDescriptions
        ppq_apr = self.__ppQueue_addPeriodicReport
        if not ppq_apr: return False

        #[2]: Update Divisions
        ud_inserts = dict()
        ud_updates = dict()

        #[3]: Updates Collection
        while ppq_apr:
            #[3-1]: Update Content & Instances
            localID, timestamp, periodicReport = ppq_apr.popleft()
            aDesc = aDescs.get(localID, None)
            if aDesc is None:
                continue
            lastReportTS = aDesc['lastReportTS']
            table        = aDesc['periodicReportsTableName']

            #[3-2]: Timestamp Future
            if (lastReportTS is None) or (lastReportTS < timestamp): 
                if table not in ud_inserts:
                    ud_inserts[table] = []
                ud_inserts[table].append((timestamp, json.dumps(periodicReport)))
                
            #[3-3]: Timestamp Equal
            elif lastReportTS == timestamp:     
                if table not in ud_updates:
                    ud_updates[table] = []
                ud_updates[table].append((json.dumps(periodicReport), timestamp))
                
            #[3-4]: Timestamp Earlier
            else:
                self.__logger(message = (f"Periodic Report Update Requested On The Earlier Timestamp Than That Of The Last. The Request Will Be Disposed. User Attention Advised.\n"
                                         f"* Request Queue:  {(localID, timestamp, periodicReport)}\n"
                                         f"* Last Report TS: {lastReportTS}"
                                        ), 
                              logType = 'Warning', 
                              color   = 'light_red')
                continue
            
            #[3-5]: Local Descriptor Update
            aDesc['lastReportTS'] = timestamp

        #[4]: Queries Execution
        for table, iParamsList in ud_inserts.items():
            sqlCursor.executemany(f"INSERT INTO {table} (timestamp, periodicReport) VALUES (?, ?)", iParamsList)
        for table, uParamsList in ud_updates.items():
            sqlCursor.executemany(f"UPDATE {table} SET periodicReport = ? WHERE timestamp = ?", uParamsList)

        #[5]: Return True To Commit
        return True
    #Periodic Processes END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Task Handlers ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __th_initialDBRead(self, sqlConn, sqlCursor, task):
        #[1]: Table Check & Creation
        sqlCursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
        tables = set(fetchedElement[0] for fetchedElement in sqlCursor.fetchall())
        if 'accountDescriptions' not in tables: 
            sqlCursor.execute("""CREATE TABLE accountDescriptions 
                              (id                       INTEGER PRIMARY KEY,
                               localID                  TEXT, 
                               accountType              TEXT,
                               buid                     INTEGER, 
                               assetsTableName          TEXT,
                               positionsTableName       TEXT,
                               tradeLogsTableName       TEXT,
                               periodicReportsTableName TEXT,
                               hashedPassword           TEXT)""")
        
        #[2]: Initial Task Completion Flag
        self.__initialTaskComplete = True
            
    def __th_readDBStatus(self, sqlConn, sqlCursor, task):
        #[1]: Fetch DB Status
        try:
            sqlCursor.execute("""SELECT
                                 (page_count * page_size) AS total_size,
                                 (freelist_count * page_size) AS free_size
                                 FROM 
                                 pragma_page_count(), 
                                 pragma_page_size(), 
                                 pragma_freelist_count();
                              """)
            total_bytes, free_bytes = sqlCursor.fetchone()
            result   = True
            dbStatus = (total_bytes, free_bytes)
            msg      = f"Account Sqlite3 DB Size Succesfully Read!"
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Read Sqlite3 DB Size.\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"
                                    ), 
                            logType = 'Error', 
                            color   = 'light_red')
            result   = False
            dbStatus = None
            msg      = f"An Unexpected Error Occurred While Attempting To Read Account Sqlite3 DB Size. ({str(e)})"
            
        #[2]: Return Result
        self.__ipcA.sendFARR(targetProcess  = task['requester'],
                             functionResult = {'type':     'account',
                                               'result':   result,
                                               'dbStatus': dbStatus,
                                               'message':  msg}, 
                             requestID      = task['requestID'],
                             complete       = True)

    def __th_loadDescriptions(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        aDescs    = self.__accountDescriptions
        lIDs_byID = self.__accountLocalIDsByID

        #[2]: Descriptions Fetch
        aDescs_announce = dict()
        sqlCursor.execute("SELECT * FROM accountDescriptions")
        aDescs_db = sqlCursor.fetchall()
        for aDesc_db in aDescs_db:
            #[2-1]: Account Summary
            dbID                     = aDesc_db[0]
            localID                  = aDesc_db[1]
            accountType              = aDesc_db[2]
            buid                     = aDesc_db[3]
            assetsTableName          = aDesc_db[4]
            positionsTableName       = aDesc_db[5]
            tradeLogsTableName       = aDesc_db[6]
            periodicReportsTableName = aDesc_db[7]
            hashedPassword           = aDesc_db[8]
            aDesc = {'dbID':                     dbID,
                     'assetsTableName':          assetsTableName,
                     'positionsTableName':       positionsTableName,
                     'tradeLogsTableName':       tradeLogsTableName,
                     'periodicReportsTableName': periodicReportsTableName,
                     'assets_dbID':              dict(),
                     'positions_dbID':           dict(),
                     'nTradeLog':                0,
                     'lastReportTS':             None}
            aDesc_announce = {'accountType':        accountType,
                              'buid':               buid,
                              'hashedPassword':     hashedPassword,
                              'assets':             dict(),
                              'positions':          dict(),
                              'lastPeriodicReport': None}
            aDescs[localID]          = aDesc
            lIDs_byID[dbID]          = localID
            aDescs_announce[localID] = aDesc_announce
            
            #[2-2]: Assets
            if assetsTableName is not None:
                sqlCursor.execute(f'SELECT * FROM {assetsTableName}')
                assets_DB = sqlCursor.fetchall()
                for assetDesc in assets_DB:
                    asset = assetDesc[1]
                    aDesc_announce['assets'][asset] = {'crossWalletBalance': assetDesc[2],
                                                       'allocationRatio':    assetDesc[3]}
                    aDesc['assets_dbID'][asset] = assetDesc[0]

            #[2-3]: Positions
            if positionsTableName is not None:
                sqlCursor.execute(f'SELECT * FROM {positionsTableName}')
                positions_DB = sqlCursor.fetchall()
                for positionDesc in positions_DB:
                    symbol = positionDesc[1]
                    aDesc_announce['positions'][symbol] = {'quoteAsset':             positionDesc[2],
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
                    aDesc['positions_dbID'][symbol] = positionDesc[0]

            #[2-4]: Read Trade Log Data
            if tradeLogsTableName is not None:
                sqlCursor.execute(f'SELECT COUNT(*) FROM {tradeLogsTableName}')
                tradeLogs_count = sqlCursor.fetchone()[0]
                aDesc['nTradeLog'] = tradeLogs_count

            #[2-5]: Read Periodic Reports Data
            if periodicReportsTableName is not None:
                sqlCursor.execute(f'SELECT * FROM {periodicReportsTableName} ORDER BY timestamp DESC LIMIT 1')
                last_report_row = sqlCursor.fetchone()
                if last_report_row:
                    timestamp      = last_report_row[0]
                    periodicReport = json.loads(last_report_row[1])
                    aDesc_announce['lastPeriodicReport'] = {'timestamp': timestamp, 
                                                            'report':    periodicReport}
                    aDesc['lastReportTS'] = timestamp

        #[3]: Return Account Descriptions
        self.__ipcA.sendFARR(targetProcess  = task['requester'], 
                             functionResult = aDescs_announce, 
                             requestID      = task['requestID'],
                             complete       = True)

    def __th_addDescription(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        aDescs    = self.__accountDescriptions
        lIDs_byID = self.__accountLocalIDsByID
        tParams   = task['params']
        localID            = tParams['localID']
        accountDescription = tParams['accountDescription']

        #[2]: Description Setup
        aDBID = 0
        while aDBID in lIDs_byID: 
            aDBID += 1
        tName_assets          = f"aat_{localID}"
        tName_positions       = f"apt_{localID}"
        tName_tradeLogs       = f"atlt_{localID}"
        tName_periodicReports = f"aprt_{localID}"
        aDesc = {'dbID':                     aDBID,
                 'assetsTableName':          tName_assets,
                 'positionsTableName':       tName_positions,
                 'tradeLogsTableName':       tName_tradeLogs,
                 'periodicReportsTableName': tName_periodicReports,
                 'assets_dbID':              dict(),
                 'positions_dbID':           dict(),
                 'nTradeLog':                0,
                 'lastReportTS':             None}
        
        #[3]: Data Save Attempt
        try:
            #[3-1]: Create Data Tables
            sqlCursor.execute(f"""CREATE TABLE {tName_assets} 
                              (id                 INTEGER PRIMARY KEY,
                               asset              TEXT,
                               crossWalletBalance REAL,
                               allocationRatio    REAL)""")
            sqlCursor.execute(f"""CREATE TABLE {tName_positions} 
                              (id                     INTEGER PRIMARY KEY,
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
                               abruptClearingRecords  TEXT)""")
            sqlCursor.execute(f"""CREATE TABLE {tName_tradeLogs} 
                              (id       INTEGER PRIMARY KEY,
                               tradeLog TEXT)""")
            sqlCursor.execute(f"""CREATE TABLE {tName_periodicReports} 
                              (timestamp      INTEGER,
                               periodicReport TEXT)""")
            
            #[3-2]: Save Assets Data
            accountDescription_assets = accountDescription['assets']
            aDesc_assetsDBID          = aDesc['assets_dbID']
            assetsData                = []
            for index, assetName in enumerate(accountDescription_assets):
                asset = accountDescription_assets[assetName]
                assetData = [index,
                             assetName,
                             asset['crossWalletBalance'],
                             asset['allocationRatio']]
                assetsData.append(assetData)
                aDesc_assetsDBID[assetName] = index
            sqlCursor.executemany(f"""INSERT INTO {tName_assets} 
                                  (id, 
                                   asset, 
                                   crossWalletBalance, 
                                   allocationRatio
                                  ) VALUES (?,?,?,?)""", assetsData)

            #[3-3]: Save Positions Data
            accountDescription_positions = accountDescription['positions']
            aDesc_positionsDBID          = aDesc['positions_dbID']
            positionsData                = []
            for index, symbol in enumerate(accountDescription_positions):
                position = accountDescription_positions[symbol]
                if   position['isolated'] == True:  isolated = 1
                elif position['isolated'] == False: isolated = 0
                elif position['isolated'] == None:  isolated = None
                positionData = [index,
                                symbol,
                                position['quoteAsset'],
                                json.dumps(position['precisions']),
                                int(position['tradeStatus']),
                                int(position['reduceOnly']),
                                position['currencyAnalysisCode'],
                                position['tradeConfigurationCode'],
                                json.dumps(position['tradeControlTracker']),
                                position['isolatedWalletBalance'],
                                position['quantity'],
                                position['entryPrice'],
                                position['leverage'],
                                isolated,
                                position['assumedRatio'],
                                position['priority'],
                                position['maxAllocatedBalance'],
                                json.dumps(position['abruptClearingRecords'])]
                positionsData.append(positionData)
                aDesc_positionsDBID[symbol] = index
            sqlCursor.executemany(f"""INSERT INTO {tName_positions} 
                                  (id, 
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
                                   abruptClearingRecords
                                  ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                                  positionsData)
            
            #[3-4]: Save The Description
            sqlCursor.execute("""INSERT INTO accountDescriptions 
                              (id,
                               localID, 
                               accountType,
                               buid,
                               assetsTableName,
                               positionsTableName, 
                               tradeLogsTableName,
                               periodicReportsTableName,
                               hashedPassword
                              ) VALUES (?,?,?,?,?,?,?,?,?)""",
                              (aDBID,
                               localID,
                               accountDescription['accountType'],
                               accountDescription['buid'],
                               tName_assets,
                               tName_positions,
                               tName_tradeLogs,
                               tName_periodicReports,
                               accountDescription['hashedPassword']))
            
            #[3-5]: Commit
            sqlConn.commit()

            #[3-6]: Local Descriptions Update
            aDescs[localID] = aDesc
            lIDs_byID[aDBID] = localID

        #[4]: Exception Handling
        except Exception as e:
            #[4-1]: Tables Clearing
            try:    sqlCursor.execute(f"DROP TABLE {tName_assets}")
            except: pass
            try:    sqlCursor.execute(f"DROP TABLE {tName_positions}")
            except: pass
            try:    sqlCursor.execute(f"DROP TABLE {tName_tradeLogs}")
            except: pass
            try:    sqlCursor.execute(f"DROP TABLE {tName_periodicReports}")
            except: pass
            try:    sqlCursor.execute("DELETE from accountDescriptions where localID = ?", (localID,))
            except: pass
            sqlConn.commit()

            #[4-2]: Description Clearing
            lIDs_byID.pop(aDBID, None)
            aDescs.pop(localID, None)
            
            #[4-3]: Logging
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Save An Account Description.\n"
                                     f" * Local ID:       {localID}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"),
                          logType = 'Error', 
                          color   = 'light_red')
    
    def __th_removeDescription(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        aDescs    = self.__accountDescriptions
        lIDs_byID = self.__accountLocalIDsByID
        tParams   = task['params']
        localID   = tParams['localID']

        #[2]: Simulation Check
        aDesc = aDescs.get(localID, None)
        if aDesc is None:
            return

        #[3]: Data Removal
        aDBID = None
        for _aDBID, _localID in lIDs_byID.items():
            if _localID == localID:
                aDBID = _aDBID
                break
        if aDBID is None:
            self.__logger(message = (f"Account DB ID Could Not Be Found While Attempting To Remove Account.\n"
                                     f" * Local ID: {localID}"
                                     ), 
                          logType = 'Error', 
                          color   = 'light_red')
            return
        sqlCursor.execute(f"DROP TABLE {aDesc['assetsTableName']}")
        sqlCursor.execute(f"DROP TABLE {aDesc['positionsTableName']}")
        sqlCursor.execute(f"DROP TABLE {aDesc['tradeLogsTableName']}")
        sqlCursor.execute(f"DROP TABLE {aDesc['periodicReportsTableName']}")
        sqlCursor.execute("DELETE from accountDescriptions where localID = ?", (localID,))
        sqlConn.commit()
        del lIDs_byID[aDBID]
        del aDescs[localID]
  
    def __th_fetchTradeLogs(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        ipcA    = self.__ipcA
        aDescs  = self.__accountDescriptions
        tParams = task['params']
        localID = tParams['localID']

        #[2]: Account Check
        aDesc = aDescs.get(localID, None)
        if aDesc is None:
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':      False,
                                            'localID':     localID,
                                            'tradeLogs':   None,
                                            'failureType': 'ACCOUNTLOCALID'}, 
                          requestID      = task['requestID'],
                          complete       = True)
            return
        
        #[3]: Trade Log Table Check
        tlTableName = aDesc['tradeLogsTableName']
        if tlTableName is None:
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':      False,
                                            'localID':     localID,
                                            'tradeLogs':   None,
                                            'failureType': 'TRADELOGSTABLENOTFOUND'}, 
                          requestID      = task['requestID'],
                          complete       = True)
            return
        
        #[4]: Trade Logs Fetch Attempt
        try:
            sqlCursor.execute(f'SELECT * FROM {tlTableName}')
            tLogs_db = sqlCursor.fetchall()
            tLogs    = list()
            for tLog_db in tLogs_db:
                tl = json.loads(tLog_db[1])
                tl['logIndex'] = tLog_db[0]
                tLogs.append(tl)
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':         True,
                                            'localID':        localID,
                                            'tradeLogs':      tLogs,
                                            'failureType':    None}, 
                          requestID      = task['requestID'],
                          complete       = True)
        except Exception as e:
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':         False,
                                            'localID':        localID,
                                            'tradeLogs':      None,
                                            'failureType':    str(e)}, 
                          requestID      = task['requestID'],
                          complete       = True)
            return
    
    def __th_fetchPeriodicReports(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        ipcA    = self.__ipcA
        aDescs  = self.__accountDescriptions
        tParams = task['params']
        localID = tParams['localID']
        
        #[2]: Simulation Check
        aDesc = aDescs.get(localID, None)
        if aDesc is None:
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':          False,
                                            'localID':         localID,
                                            'periodicReports': None,
                                            'failureType':     'SIMULATIONCODE'}, 
                          requestID      = task['requestID'],
                          complete       = True)
            return
        
        #[3]: Periodic Reports Table Check
        prTableName = aDesc['periodicReportsTableName']
        if prTableName is None:
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':          False,
                                            'localID':         localID,
                                            'periodicReports': None,
                                            'failureType':     'PERIODICREPORTSTABLENOTFOUND'}, 
                          requestID      = task['requestID'],
                          complete       = True)
            return
        
        #[4]: Periodic Reports Fetch Attempt
        try:
            sqlCursor.execute(f'SELECT * FROM {prTableName}')
            prs_db = sqlCursor.fetchall()
            prs    = dict()
            for pr_db in prs_db:
                prTS = pr_db[0]
                pr   = json.loads(pr_db[1])
                prs[prTS] = pr
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':          True,
                                            'localID':         localID,
                                            'periodicReports': prs,
                                            'failureType':     None}, 
                          requestID      = task['requestID'],
                          complete       = True)
        except Exception as e:
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':          False,
                                            'localID':         localID,
                                            'periodicReports': None,
                                            'failureType':     str(e)}, 
                          requestID      = task['requestID'],
                          complete       = True)
            return
    #Task Handlers END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #FAR & FARR Handlers ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __far_readDBStatus(self, requester, requestID):
        #[1]: Source Check
        if requester != 'GUI':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'type':     'account',
                                                   'result':   None, 
                                                   'dbStatus': None, 
                                                   'message':  'Invalid Requester'}, 
                                 requestID      = requestID,
                                 complete       = True)
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'readDBStatus',
                'requester': requester,
                'requestID': requestID,
                'params':    None
               }
        self.__taskQueue.put(task)
    
    def __far_loadDescriptions(self, requester, requestID):
        #[1]: Source Check
        if requester != 'TRADEMANAGER':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = None, 
                                 requestID      = requestID,
                                 complete       = True)
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'loadDescriptions',
                'requester': requester,
                'requestID': requestID,
                'params':    None
               }
        self.__taskQueue.put(task)
    
    def __far_addDescription(self, requester, localID, accountDescription):
        #[1]: Source Check
        if requester != 'TRADEMANAGER':
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'addDescription',
                'requester': requester,
                'requestID': None,
                'params':    {'localID':            localID,
                              'accountDescription': accountDescription}
               }
        self.__taskQueue.put(task)
    
    def __far_removeDescription(self, requester, localID):
        #[1]: Source Check
        if requester != 'TRADEMANAGER':
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'removeDescription',
                'requester': requester,
                'requestID': None,
                'params':    {'localID': localID}
               }
        self.__taskQueue.put(task)
    
    def __far_editData(self, requester, updates):
        #[1]: Requester Check
        if requester != 'TRADEMANAGER': 
            return

        #[2]: Queue Update
        self.__ppQueue_editData.extend(updates)
    
    def __far_addTradeLog(self, requester, localID, tradeLog):
        #[1]: Requester Check
        if requester != 'TRADEMANAGER': 
            return

        #[2]: Queue Update
        tlAppendRequest = (localID, tradeLog)
        self.__ppQueue_addTradeLog.append(tlAppendRequest)
    
    def __far_updatePeriodicReport(self, requester, localID, timestamp, periodicReport):
        #[1]: Requester Check
        if requester != 'TRADEMANAGER': 
            return

        #[2]: Queue Update
        prUpdateRequest = (localID, timestamp, periodicReport)
        self.__ppQueue_addPeriodicReport.append(prUpdateRequest)

    def __far_fetchTradeLog(self, requester, requestID, localID):
        #[1]: Source Check
        if requester != 'GUI':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'result':      False,
                                                   'localID':     localID,
                                                   'tradeLogs':   None,
                                                   'failureType': 'INVALIDREQUESTER'}, 
                                 requestID      = requestID,
                                 complete       = True)
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'fetchTradeLogs',
                'requester': requester,
                'requestID': requestID,
                'params':    {'localID': localID}
               }
        self.__taskQueue.put(task)
    
    def __far_fetchPeriodicReports(self, requester, requestID, localID):
        #[1]: Source Check
        if requester != 'GUI':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'result':          False,
                                                   'localID':         localID,
                                                   'periodicReports': None,
                                                   'failureType':     'INVALIDREQUESTER'}, 
                                 requestID      = requestID,
                                 complete       = True)
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'fetchPeriodicReports',
                'requester': requester,
                'requestID': requestID,
                'params':    {'localID': localID}
               }
        self.__taskQueue.put(task)
    #FAR & FARR Handlers END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------