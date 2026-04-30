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
from datetime import datetime

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
        self.__simulationDescriptions = dict()
        self.__simulationCodesByID    = dict()
        
        #[3]: PRD Setup
        ipcA.sendPRDEDIT(targetProcess = 'SIMULATIONMANAGER', prdAddress = 'SIMULATIONS', prdContent = self.__simulationDescriptions)

        #[4]: FAR Handlers Setup
        ipcA.addFARHandler('readSimulationDBStatus',         self.__far_readDBStatus,         executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #GUI
        ipcA.addFARHandler('saveSimulationData',             self.__far_saveData,             executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #SIMULATOR
        ipcA.addFARHandler('removeSimulationData',           self.__far_removeData,           executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #SIMULATIONMANAGER & SIMULATOR
        ipcA.addFARHandler('fetchSimulationTradeLogs',       self.__far_fetchTradeLogs,       executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #GUI
        ipcA.addFARHandler('fetchSimulationPeriodicReports', self.__far_fetchPeriodicReports, executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #GUI

        #[5]: Task Handling Thread Setup
        self.__taskQueue = queue.Queue()
        self.__wThread   = threading.Thread(target = self.__processLoop, args = (), daemon = False)
        self.__taskHandlers = {'initialDBRead':        self.__th_initialDBRead,
                               'readDBStatus':         self.__th_readDBStatus,
                               'saveData':             self.__th_saveData,
                               'removeData':           self.__th_removeData,
                               'fetchTradeLogs':       self.__th_fetchTradeLogs,
                               'fetchPeriodicReports': self.__th_fetchPeriodicReports}
        
        #[5]: Initial Task Completion Flag
        self.__initialTaskComplete = False

    #System -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __processLoop(self):
        #[1]: Instances
        tQueue    = self.__taskQueue
        tHandlers = self.__taskHandlers
        logger    = self.__logger

        #[2]: Sqlite3 Connection & Cursor
        sqlConn   = sqlite3.connect(os.path.join(self.__path_dbFolder, 'atmEta_simulations.db'))
        sqlCursor = sqlConn.cursor()
        
        #[3]: Task Handling Loop
        while True:
            #[3-1]: Handling Attempt
            task = None
            try:
                #[3-1-1]: Task
                task = tQueue.get()
                #[3-1-2]: Termination Check
                if task is None: 
                    tQueue.task_done()
                    break
                #[3-1-3]: Task Handling
                tHandlers[task['type']](sqlConn   = sqlConn,
                                        sqlCursor = sqlCursor,
                                        task      = task)
                tQueue.task_done()
            #[3-2]: Exception Handling
            except Exception as e: 
                if task is not None: tQueue.task_done()
                logger(message = (f"An Unexpected Error Occurred While Attempting To Handle A Task\n"
                                  f" * Error:          {e}\n"
                                  f" * Detailed Trace: {traceback.format_exc()}"),
                       logType = 'Error', 
                       color   = 'light_red')

        #[4]: Sqlite3 Connection Close
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
        msg      = f"[DATAMANAGER-SIMULATIONDATAWORKER-{time_str}] {message}"
        print(termcolor.colored(msg, color))
    
    def initialTaskComplete(self):
        return self.__initialTaskComplete
    #System END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Task Handlers ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __th_initialDBRead(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        sDescs      = self.__simulationDescriptions
        sCodes_byID = self.__simulationCodesByID 

        #[2]: Tables Check & Creation
        sqlCursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
        tables = set(fetchedElement[0] for fetchedElement in sqlCursor.fetchall())
        if 'simulationDescriptions' not in tables: 
            sqlCursor.execute("""CREATE TABLE simulationDescriptions (id INTEGER PRIMARY KEY, 
                                                                      simulationCode                          TEXT, 
                                                                      simulationRange                         TEXT,
                                                                      analysisExport                          INTEGER,
                                                                      creationTime                            REAL,
                                                                      simulationSummary                       TEXT,
                                                                      currencyAnalysisConfigurationsTableName TEXT,
                                                                      tradeConfigurationsTableName            TEXT,
                                                                      assetsTableName                         TEXT,
                                                                      positionsTableName                      TEXT,
                                                                      tradeLogsTableName                      TEXT,
                                                                      periodicReportsTableName                TEXT
                                                                      )""")
            
        #[3]: Currency Data Identification & Read
        sqlCursor.execute("SELECT * FROM simulationDescriptions")
        sDescs_db = sqlCursor.fetchall()
        for summaryRow in sDescs_db:
            #[3-1]: Read SimulationDescription Line
            dbID                                    = summaryRow[0]
            simulationCode                          = summaryRow[1]
            simulationRange                         = json.loads(summaryRow[2])
            analysisExport                          = (summaryRow[3] == 1)
            creationTime                            = summaryRow[4]
            simulationSummary                       = json.loads(summaryRow[5])
            currencyAnalysisConfigurationsTableName = summaryRow[6]
            tradeConfigurationsTableName            = summaryRow[7]
            assetsTableName                         = summaryRow[8]
            positionsTableName                      = summaryRow[9]
            tradeLogsTableName                      = summaryRow[10]
            periodicReportsTableName                = summaryRow[11]
            if currencyAnalysisConfigurationsTableName not in tables: currencyAnalysisConfigurationsTableName = None
            if tradeConfigurationsTableName            not in tables: tradeConfigurationsTableName            = None
            if assetsTableName                         not in tables: assetsTableName                         = None
            if positionsTableName                      not in tables: positionsTableName                      = None
            if tradeLogsTableName                      not in tables: tradeLogsTableName                      = None
            if periodicReportsTableName                not in tables: periodicReportsTableName                = None

            #[3-2]: Read CurrencyAnalysisConfigurations
            currencyAnalysisConfigurations = dict()
            if currencyAnalysisConfigurationsTableName is not None:
                sqlCursor.execute(f"SELECT * FROM {currencyAnalysisConfigurationsTableName}")
                fetchedDBData = sqlCursor.fetchall()
                for cactRow in fetchedDBData:
                    cacCode = cactRow[1]
                    cac_raw = json.loads(cactRow[2])
                    cac = {int(iID_str): cac_iID for iID_str, cac_iID in cac_raw.items()}
                    currencyAnalysisConfigurations[cacCode] = cac

            #[3-3]: Read TradeConfigurations
            tradeConfigurations = dict()
            if tradeConfigurationsTableName is not None:
                sqlCursor.execute(f"SELECT * FROM {tradeConfigurationsTableName}")
                fetchedDBData = sqlCursor.fetchall()
                for tctRow in fetchedDBData:
                    tcCode = tctRow[1]
                    tc     = json.loads(tctRow[2])
                    tradeConfigurations[tcCode] = tc

            #[3-4]: Read Assets
            assets = dict()
            if assetsTableName is not None:
                sqlCursor.execute(f"SELECT * FROM {assetsTableName}")
                fetchedDBData = sqlCursor.fetchall()
                for atRow in fetchedDBData:
                    assetName            = atRow[1]
                    initialWalletBalance = atRow[2]
                    allocatableBalance   = atRow[3]
                    allocationRatio      = atRow[4]
                    assumedRatio         = atRow[5]
                    weightedAssumedRatio = atRow[6]
                    maxAllocatedBalance  = json.loads(atRow[7])
                    positionSymbols      = set(json.loads(atRow[8]))
                    assets[assetName] = {'initialWalletBalance': initialWalletBalance,
                                         'allocatableBalance':   allocatableBalance,
                                         'allocationRatio':      allocationRatio,
                                         'assumedRatio':         assumedRatio,
                                         'weightedAssumedRatio': weightedAssumedRatio,
                                         'maxAllocatedBalance':  maxAllocatedBalance,
                                         '_positionSymbols':     positionSymbols}
                    
            #[3-5]: Read Positions
            positions = dict()
            if positionsTableName is not None:
                sqlCursor.execute(f"SELECT * FROM {positionsTableName}")
                fetchedDBData = sqlCursor.fetchall()
                for ptRow in fetchedDBData:
                    positionSymbol                    = ptRow[1]
                    quoteAsset                        = json.loads(ptRow[2])
                    precisions                        = json.loads(ptRow[3])
                    dataRanges                        = json.loads(ptRow[4])
                    currencyAnalysisConfigurationCode = ptRow[5]
                    tradeConfigurationCode            = ptRow[6]
                    isolated                          = (ptRow[7] == 1)
                    leverage                          = ptRow[8]
                    assumedRatio                      = ptRow[9]
                    weightedAssumedRatio              = ptRow[10]
                    maxAllocatedBalance               = json.loads(ptRow[11])
                    firstOpenTSs                      = json.loads(ptRow[12])
                    positions[positionSymbol] = {'quoteAsset':                        quoteAsset, 
                                                 'precisions':                        precisions, 
                                                 'dataRanges':                        dataRanges, 
                                                 'currencyAnalysisConfigurationCode': currencyAnalysisConfigurationCode, 
                                                 'tradeConfigurationCode':            tradeConfigurationCode, 
                                                 'isolated':                          isolated, 
                                                 'leverage':                          leverage,
                                                 'assumedRatio':                      assumedRatio, 
                                                 'weightedAssumedRatio':              weightedAssumedRatio,
                                                 'maxAllocatedBalance':               maxAllocatedBalance, 
                                                 'firstOpenTSs':                      firstOpenTSs, 
                                                 'tradable':                          True}
                    
            #[3-6]: Save
            sDescs[simulationCode] = {'simulationRange':                         simulationRange,
                                      'currencyAnalysisConfigurations':          currencyAnalysisConfigurations,
                                      'tradeConfigurations':                     tradeConfigurations,
                                      'analysisExport':                          analysisExport,
                                      'assets':                                  assets,
                                      'positions':                               positions,
                                      'creationTime':                            creationTime,
                                      'simulationSummary':                       simulationSummary,
                                      'currencyAnalysisConfigurationsTableName': currencyAnalysisConfigurationsTableName,
                                      'tradeConfigurationsTableName':            tradeConfigurationsTableName,
                                      'assetsTableName':                         assetsTableName,
                                      'positionsTableName':                      positionsTableName,
                                      'tradeLogsTableName':                      tradeLogsTableName,
                                      'periodicReportsTableName':                periodicReportsTableName}
            sCodes_byID[dbID] = simulationCode

        #[4]: Announce the currency info
        self.__ipcA.sendPRDEDIT(targetProcess = 'SIMULATIONMANAGER', 
                                prdAddress    = 'SIMULATIONS', 
                                prdContent    = sDescs)
        
        #[5]: Initial Task Completion Flag
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
            msg      = f"Simulation Sqlite3 DB Size Succesfully Read!"
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Read Sqlite3 DB Size.\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"
                                    ), 
                            logType = 'Error', 
                            color   = 'light_red')
            result   = False
            dbStatus = None
            msg      = f"An Unexpected Error Occurred While Attempting To Read Simulation Sqlite3 DB Size. ({str(e)})"
            
        #[2]: Return Result
        self.__ipcA.sendFARR(targetProcess  = task['requester'], 
                             functionResult = {'type':     'simulation',
                                               'result':   result,
                                               'dbStatus': dbStatus, 
                                               'message':  msg}, 
                             requestID      = task['requestID'],
                             complete       = True)
        
    def __th_saveData(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        sDescs      = self.__simulationDescriptions
        sCodes_byID = self.__simulationCodesByID
        tParams     = task['params']
        simulationCode                 = tParams['simulationCode']
        simulationRange                = tParams['simulationRange']
        currencyAnalysisConfigurations = tParams['currencyAnalysisConfigurations']
        tradeConfigurations            = tParams['tradeConfigurations']
        analysisExport                 = tParams['analysisExport']
        assets                         = tParams['assets']
        positions                      = tParams['positions']
        creationTime                   = tParams['creationTime']
        tradeLogs                      = tParams['tradeLogs']
        periodicReports                = tParams['periodicReports']
        simulationSummary              = tParams['simulationSummary']

        #[2]: Description Setup
        simulationDescription_dbID = 0
        while simulationDescription_dbID in sCodes_byID: 
            simulationDescription_dbID += 1
        currencyAnalysisConfigurationsTableName = f"cact_{simulationCode}"
        tradeConfigurationsTableName            = f"tct_{simulationCode}"
        assetsTableName                         = f"at_{simulationCode}"
        positionsTableName                      = f"pt_{simulationCode}"
        tradeLogsTableName                      = f"tlt_{simulationCode}"
        periodicReportsTableName                = f"drt_{simulationCode}"
        sDesc = {'simulationRange':                simulationRange,
                 'currencyAnalysisConfigurations': currencyAnalysisConfigurations,
                 'tradeConfigurations':            tradeConfigurations,
                 'analysisExport':                 analysisExport,
                 'assets':                         assets,
                 'positions':                      positions,
                 'creationTime':                   creationTime,
                 'simulationSummary':              simulationSummary,
                 'currencyAnalysisConfigurationsTableName': currencyAnalysisConfigurationsTableName,
                 'tradeConfigurationsTableName':            tradeConfigurationsTableName,
                 'assetsTableName':                         assetsTableName,
                 'positionsTableName':                      positionsTableName,
                 'tradeLogsTableName':                      tradeLogsTableName,
                 'periodicReportsTableName':                periodicReportsTableName}

        #[3]: Data Save Attempt
        try:
            #[3-1]: Create Simulation Tables
            sqlCursor.execute(f"CREATE TABLE {currencyAnalysisConfigurationsTableName} (id INTEGER PRIMARY KEY, configurationCode TEXT, configuration TEXT)")
            sqlCursor.execute(f"CREATE TABLE {tradeConfigurationsTableName} (id INTEGER PRIMARY KEY, configurationCode TEXT, configuration TEXT)")
            sqlCursor.execute(f"""CREATE TABLE {assetsTableName} 
                              (id                   INTEGER PRIMARY KEY, 
                               asset                TEXT, 
                               initialWalletBalance REAL, 
                               allocatableBalance   REAL,
                               allocationRatio      REAL, 
                               assumedRatio         REAL, 
                               weightedAssumedRatio REAL, 
                               maxAllocatedBalance  TEXT, 
                               positionSymbols      TEXT
                              )""")
            sqlCursor.execute(f"""CREATE TABLE {positionsTableName} 
                              (id                                INTEGER PRIMARY KEY, 
                               positionSymbol                    TEXT, 
                               quoteAsset                        TEXT, 
                               precisions                        TEXT, 
                               dataRanges                        TEXT, 
                               currencyAnalysisConfigurationCode TEXT,
                               tradeConfigurationCode            TEXT,
                               isolated                          INTEGER,
                               leverage                          INTEGER,
                               assumedRatio                      REAL,
                               weightedAssumedRatio              REAL,
                               maxAllocatedBalance               TEXT,
                               firstOpenTSs                      TEXT
                              )""")
            sqlCursor.execute(f"CREATE TABLE {tradeLogsTableName} (id INTEGER PRIMARY KEY, tradeLog TEXT)")
            sqlCursor.execute(f"CREATE TABLE {periodicReportsTableName} (id INTEGER PRIMARY KEY, dayTimeStamp INTERGER, periodicReport TEXT)")

            #[3-2]: Format And Save Data
            currencyAnalysisConfigurations_formatted = [(index, cacCode, json.dumps(currencyAnalysisConfigurations[cacCode])) for index, cacCode in enumerate(currencyAnalysisConfigurations)]
            tradeConfigurations_formatted            = [(index, tcCode,  json.dumps(tradeConfigurations[tcCode]))             for index, tcCode  in enumerate(tradeConfigurations)]
            assets_formatted = list()
            for index, assetName in enumerate(assets):
                asset = assets[assetName]
                assets_formatted.append((index,
                                         assetName,
                                         asset['initialWalletBalance'],
                                         asset['allocatableBalance'],
                                         asset['allocationRatio'],
                                         asset['assumedRatio'],
                                         asset['weightedAssumedRatio'],
                                         json.dumps(asset['maxAllocatedBalance']),
                                         json.dumps(list(asset['_positionSymbols']))
                                        ))
            positions_formatted = list()
            for index, pSymbol in enumerate(positions):
                position = positions[pSymbol]
                positions_formatted.append((index,
                                            pSymbol,
                                            json.dumps(position['quoteAsset']),
                                            json.dumps(position['precisions']),
                                            json.dumps(position['dataRanges']),
                                            position['currencyAnalysisConfigurationCode'],
                                            position['tradeConfigurationCode'],
                                            int(position['isolated']),
                                            position['leverage'],
                                            position['assumedRatio'],
                                            position['weightedAssumedRatio'],
                                            json.dumps(position['maxAllocatedBalance']),
                                            json.dumps(position['firstOpenTSs']),
                                            ))
            tradeLogs_formatted       = [(index, json.dumps(tradeLog))                                    for index, tradeLog     in enumerate(tradeLogs)]
            periodicReports_formatted = [(index, dayTimeStamp, json.dumps(periodicReports[dayTimeStamp])) for index, dayTimeStamp in enumerate(periodicReports)]
            sqlCursor.executemany(f"INSERT INTO {currencyAnalysisConfigurationsTableName} (id, configurationCode, configuration) VALUES (?,?,?)", currencyAnalysisConfigurations_formatted)
            sqlCursor.executemany(f"INSERT INTO {tradeConfigurationsTableName}            (id, configurationCode, configuration) VALUES (?,?,?)", tradeConfigurations_formatted)
            sqlCursor.executemany(f"""INSERT INTO {assetsTableName} 
                                  (id, 
                                   asset, 
                                   initialWalletBalance, 
                                   allocatableBalance,
                                   allocationRatio,
                                   assumedRatio,
                                   weightedAssumedRatio,
                                   maxAllocatedBalance,
                                   positionSymbols
                                  ) VALUES (?,?,?,?,?,?,?,?,?)""", 
                                  assets_formatted)
            sqlCursor.executemany(f"""INSERT INTO {positionsTableName} 
                                  (id, 
                                   positionSymbol, 
                                   quoteAsset, 
                                   precisions, 
                                   dataRanges,
                                   currencyAnalysisConfigurationCode,
                                   tradeConfigurationCode,
                                   isolated,
                                   leverage,
                                   assumedRatio,
                                   weightedAssumedRatio,
                                   maxAllocatedBalance,
                                   firstOpenTSs
                                  ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                                  positions_formatted)
            sqlCursor.executemany(f"INSERT INTO {tradeLogsTableName}       (id, tradeLog)                     VALUES (?,?)",   tradeLogs_formatted)
            sqlCursor.executemany(f"INSERT INTO {periodicReportsTableName} (id, dayTimeStamp, periodicReport) VALUES (?,?,?)", periodicReports_formatted)
            
            #[3-3]: Save Simulation Description
            sqlCursor.execute("""INSERT INTO simulationDescriptions 
                              (id, 
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
                              ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                              (simulationDescription_dbID, 
                               simulationCode,
                               json.dumps(simulationRange),
                               1 if analysisExport else 0,
                               creationTime,
                               json.dumps(simulationSummary),
                               currencyAnalysisConfigurationsTableName,
                               tradeConfigurationsTableName,
                               assetsTableName,
                               positionsTableName,
                               tradeLogsTableName,
                               periodicReportsTableName))
            
            #[3-4]: Commit
            sqlConn.commit()

            #[3-5]: Save The Temporarily Created Simulation Instance
            sDescs[simulationCode]                  = sDesc
            sCodes_byID[simulationDescription_dbID] = simulationCode

            #[3-6]: Return Successful Save Result
            self.__ipcA.sendFARR(targetProcess  = task['requester'], 
                                 functionResult = {'simulationCode': simulationCode,
                                                   'saveResult':     True,
                                                   'errorMsg':       None}, 
                                 requestID      = task['requestID'],
                                 complete       = True)
        
        #[4]: Exception Handling
        except Exception as e:
            #[4-1]: Tables Clearing
            try:    sqlCursor.execute(f"DROP TABLE {currencyAnalysisConfigurationsTableName}")
            except: pass
            try:    sqlCursor.execute(f"DROP TABLE {tradeConfigurationsTableName}")
            except: pass
            try:    sqlCursor.execute(f"DROP TABLE {assetsTableName}")
            except: pass
            try:    sqlCursor.execute(f"DROP TABLE {positionsTableName}")
            except: pass
            try:    sqlCursor.execute(f"DROP TABLE {tradeLogsTableName}")
            except: pass
            try:    sqlCursor.execute(f"DROP TABLE {periodicReportsTableName}")
            except: pass
            try:    sqlCursor.execute("DELETE from simulationDescriptions where id = ?", (simulationDescription_dbID,))
            except: pass
            sqlConn.commit()
            #[4-2]: Description Clearing
            sCodes_byID.pop(simulationDescription_dbID, None)
            sDescs.pop(simulationCode, None)
            #[4-3]: Logging
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Save Simulation Result.\n"
                                     f" * Simulation Code: {simulationCode}\n"
                                     f" * Error:           {e}\n"
                                     f" * Detailed Trace:  {traceback.format_exc()}"),
                          logType = 'Error', 
                          color   = 'light_red')
            #[4-4]: Result Return
            self.__ipcA.sendFARR(targetProcess  = task['requester'], 
                                 functionResult = {'simulationCode': simulationCode,
                                                   'saveResult':     False,
                                                   'errorMsg':       str(e)}, 
                                 requestID      = task['requestID'],
                                 complete       = True)

    def __th_removeData(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        sDescs      = self.__simulationDescriptions
        sCodes_byID = self.__simulationCodesByID
        tParams     = task['params']
        simulationCode = tParams['simulationCode']

        #[2]: Simulation Check
        sDesc = sDescs.get(simulationCode, None)
        if sDesc is None:
            return

        #[3]: Data Removal
        for simDBID, simCode in sCodes_byID.items():
            if simCode == simulationCode:
                break
        if sDesc['currencyAnalysisConfigurationsTableName'] is not None: sqlCursor.execute(f"DROP TABLE {sDesc['currencyAnalysisConfigurationsTableName']}")
        if sDesc['tradeConfigurationsTableName']            is not None: sqlCursor.execute(f"DROP TABLE {sDesc['tradeConfigurationsTableName']}")
        if sDesc['assetsTableName']                         is not None: sqlCursor.execute(f"DROP TABLE {sDesc['assetsTableName']}")
        if sDesc['positionsTableName']                      is not None: sqlCursor.execute(f"DROP TABLE {sDesc['positionsTableName']}")
        if sDesc['tradeLogsTableName']                      is not None: sqlCursor.execute(f"DROP TABLE {sDesc['tradeLogsTableName']}")
        if sDesc['periodicReportsTableName']                is not None: sqlCursor.execute(f"DROP TABLE {sDesc['periodicReportsTableName']}")
        sqlCursor.execute("DELETE from simulationDescriptions where id = ?", (simDBID,))
        sqlConn.commit()
        del sCodes_byID[simDBID]
        del sDescs[simulationCode]

    def __th_fetchTradeLogs(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        ipcA        = self.__ipcA
        sDescs      = self.__simulationDescriptions
        tParams     = task['params']
        simulationCode = tParams['simulationCode']

        #[2]: Simulation Check
        sDesc = sDescs.get(simulationCode, None)
        if sDesc is None:
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':         False,
                                            'simulationCode': simulationCode,
                                            'tradeLogs':      None,
                                            'failureType':    'SIMULATIONCODE'}, 
                          requestID      = task['requestID'],
                          complete       = True)
            return
        
        #[3]: Trade Log Table Check
        tlTableName = sDesc['tradeLogsTableName']
        if tlTableName is None:
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':         False,
                                            'simulationCode': simulationCode,
                                            'tradeLogs':      None,
                                            'failureType':    'TRADELOGSTABLENOTFOUND'}, 
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
                                            'simulationCode': simulationCode,
                                            'tradeLogs':      tLogs,
                                            'failureType':    None}, 
                          requestID      = task['requestID'],
                          complete       = True)
        except Exception as e:
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':         False,
                                            'simulationCode': simulationCode,
                                            'tradeLogs':      None,
                                            'failureType':    str(e)}, 
                          requestID      = task['requestID'],
                          complete       = True)
            return

    def __th_fetchPeriodicReports(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        ipcA        = self.__ipcA
        sDescs      = self.__simulationDescriptions
        tParams     = task['params']
        simulationCode = tParams['simulationCode']
        
        #[2]: Simulation Check
        sDesc = sDescs.get(simulationCode, None)
        if sDesc is None:
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':          False,
                                            'simulationCode':  simulationCode,
                                            'periodicReports': None,
                                            'failureType':     'SIMULATIONCODE'}, 
                          requestID      = task['requestID'],
                          complete       = True)
            return
        
        #[3]: Periodic Reports Table Check
        prTableName = sDesc['periodicReportsTableName']
        if prTableName is None:
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':          False,
                                            'simulationCode':  simulationCode,
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
                prTS = pr_db[1]
                pr   = json.loads(pr_db[2])
                prs[prTS] = pr
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':          True,
                                            'simulationCode':  simulationCode,
                                            'periodicReports': prs,
                                            'failureType':     None}, 
                          requestID      = task['requestID'],
                          complete       = True)
        except Exception as e:
            ipcA.sendFARR(targetProcess  = task['requester'], 
                          functionResult = {'result':          False,
                                            'simulationCode':  simulationCode,
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
                                 functionResult = {'type':     'simulation',
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
    
    def __far_saveData(self, requester, requestID, simulationCode, simulationRange, currencyAnalysisConfigurations, tradeConfigurations, analysisExport, assets, positions, creationTime, tradeLogs, periodicReports, simulationSummary):
        #[1]: Source Check
        if not requester.startswith('SIMULATOR'):
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'simulationCode': simulationCode,
                                                   'saveResult':     None,
                                                   'errorMsg':       'INVALIDREQUESTER'}, 
                                 requestID      = requestID,
                                 complete       = True)
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'saveData',
                'requester': requester,
                'requestID': requestID,
                'params':    {'simulationCode':                 simulationCode,
                              'simulationRange':                simulationRange,
                              'currencyAnalysisConfigurations': currencyAnalysisConfigurations,
                              'tradeConfigurations':            tradeConfigurations,
                              'analysisExport':                 analysisExport,
                              'assets':                         assets,
                              'positions':                      positions,
                              'creationTime':                   creationTime,
                              'tradeLogs':                      tradeLogs,
                              'periodicReports':                periodicReports,
                              'simulationSummary':              simulationSummary}
               }
        self.__taskQueue.put(task)

    def __far_removeData(self, requester, simulationCode):
        #[1]: Source Check
        if not (requester.startswith('SIMULATOR') or requester == 'SIMULATIONMANAGER'):
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'removeData',
                'requester': requester,
                'requestID': None,
                'params':    {'simulationCode': simulationCode}
               }
        self.__taskQueue.put(task)

    def __far_fetchTradeLogs(self, requester, requestID, simulationCode):
        #[1]: Source Check
        if requester != 'GUI':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'result':         False,
                                                   'simulationCode': simulationCode,
                                                   'tradeLogs':      None,
                                                   'failureType':    'INVALIDREQUESTER'}, 
                                 requestID      = requestID,
                                 complete       = True)
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'fetchTradeLogs',
                'requester': requester,
                'requestID': requestID,
                'params':    {'simulationCode': simulationCode}
               }
        self.__taskQueue.put(task)
    
    def __far_fetchPeriodicReports(self, requester, requestID, simulationCode):
        #[1]: Source Check
        if requester != 'GUI':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'result':          False,
                                                   'simulationCode':  simulationCode,
                                                   'periodicReports': None,
                                                   'failureType':     'INVALIDREQUESTER'}, 
                                 requestID      = requestID,
                                 complete       = True)
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'fetchPeriodicReports',
                'requester': requester,
                'requestID': requestID,
                'params':    {'simulationCode': simulationCode}
               }
        self.__taskQueue.put(task)
    #FAR & FARR Handlers END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------