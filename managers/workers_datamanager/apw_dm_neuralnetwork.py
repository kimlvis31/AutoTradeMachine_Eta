#ATM Modules
import atmEta_IPC

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
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

class Worker:
    def __init__(self, path_project, dmConfig, ipcA):
        #[1]: Base Parameters & Instances
        path_dbFolder = os.path.join(path_project, 'data', 'db')
        self.__path_dbFolder = path_dbFolder
        self.__dmConfig      = dmConfig
        self.__ipcA          = ipcA

        #[2]: Task Data
        self.__neuralNetworkDescriptions = dict()
        self.__neuralNetworkCodesByID    = dict()

        #[3]: FAR Handlers Setup
        ipcA.addFARHandler('readNeuralNetworkDBStatus',          self.__far_readDBStatus,          executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #GUI
        ipcA.addFARHandler('loadNeuralNetworkDescriptions',      self.__far_loadDescriptions,      executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #NEURALNETWORKMANAGER
        ipcA.addFARHandler('addNeuralNetworkDescription',        self.__far_addDescription,        executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #NEURALNETWORKMANAGER
        ipcA.addFARHandler('removeNeuralNetworkDescription',     self.__far_removeDescription,     executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #NEURALNETWORKMANAGER
        ipcA.addFARHandler('updateNeuralNetworkConnectionData',  self.__far_updateConnectionData,  executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #NEURALNETWORKMANAGER
        ipcA.addFARHandler('addNeuralNetworkTrainingLog',        self.__far_addTrainingLog,        executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #NEURALNETWORKMANAGER
        ipcA.addFARHandler('addNeuralNetworkPerformanceTestLog', self.__far_addPerformanceTestLog, executionThread = _IPC_THREADTYPE_AT, immediateResponse = False) #NEURALNETWORKMANAGER

        #[4]: Task Handling Thread Setup
        self.__taskQueue = queue.Queue()
        self.__wThread   = threading.Thread(target = self.__processLoop, args = (), daemon = False)
        self.__taskHandlers = {'initialDBRead':         self.__th_initialDBRead,
                               'readDBStatus':          self.__th_readDBStatus,
                               'loadDescriptions':      self.__th_loadDescriptions,
                               'addDescription':        self.__th_addDescription,
                               'removeDescription':     self.__th_removeDescription,
                               'updateConnectionData':  self.__th_updateConnectionData,
                               'addTrainingLog':        self.__th_addTrainingLog,
                               'addPerformanceTestLog': self.__th_addPerformanceTestLog}
        
        #[5]: Initial Task Completion Flag
        self.__initialTaskComplete = False

    #System -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __processLoop(self):
        #[1]: Instances
        tQueue    = self.__taskQueue
        tHandlers = self.__taskHandlers
        logger    = self.__logger

        #[2]: Sqlite3 Connection & Cursor
        sqlConn   = sqlite3.connect(os.path.join(self.__path_dbFolder, 'atmEta_neuralNetworks.db'))
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
        msg      = f"[DATAMANAGER-NEURALNETWORKDATAWORKER-{time_str}] {message}"
        print(termcolor.colored(msg, color))
    
    def initialTaskComplete(self):
        return self.__initialTaskComplete
    #System END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Task Handlers ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __th_initialDBRead(self, sqlConn, sqlCursor, task):
        #[1]: Table Check & Creation
        sqlCursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
        tables = set(fetchedElement[0] for fetchedElement in sqlCursor.fetchall())
        if 'neuralNetworkDescriptions' not in tables: 
            sqlCursor.execute("""CREATE TABLE neuralNetworkDescriptions 
                              (id                             INTEGER PRIMARY KEY,
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
            msg      = f"Neural Network Sqlite3 DB Size Succesfully Read!"
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Read Sqlite3 DB Size.\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"
                                    ), 
                            logType = 'Error', 
                            color   = 'light_red')
            result   = False
            dbStatus = None
            msg      = f"An Unexpected Error Occurred While Attempting To Read Neural Network Sqlite3 DB Size. ({str(e)})"
            
        #[2]: Return Result
        self.__ipcA.sendFARR(targetProcess  = task['requester'], 
                             functionResult = {'type':     'neuralNetwork',
                                               'result':   result, 
                                               'dbStatus': dbStatus, 
                                               'message':  msg}, 
                             requestID      = task['requestID'],
                             complete       = True)
        
    def __th_loadDescriptions(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        nnDescs      = self.__neuralNetworkDescriptions
        nnCodes_byID = self.__neuralNetworkCodesByID

        #[2]: Descriptions Fetch
        nnDescs_announce = dict()
        sqlCursor.execute("SELECT * FROM neuralNetworkDescriptions")
        dbTableData_neuralNetworkDescriptions = sqlCursor.fetchall()
        for summaryRow in dbTableData_neuralNetworkDescriptions:
            #[2-1]: Neural Network Description
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

            #[2-2]: Connection Data
            networkConnectionData = list()
            if networkConnectionDataTableName is not None: 
                sqlCursor.execute(f'SELECT * FROM {networkConnectionDataTableName}')
                ncData_db = sqlCursor.fetchall()
                for ncData in ncData_db: 
                    networkConnectionData.append((ncData[1], 
                                                  ncData[2], 
                                                  json.loads(ncData[3]), 
                                                  ncData[4]))
            
            #[2-3]: Training Logs
            trainingLogs = list()
            if trainingLogsTableName is not None:
                sqlCursor.execute(f'SELECT * FROM {trainingLogsTableName}')
                tls_db = sqlCursor.fetchall()
                for tl_db in tls_db: 
                    trainingLogs.append(json.loads(tl_db[1]))

            #[2-4]: Performance Test Logs
            performanceTestLogs = list()
            if performanceTestLogsTableName is not None:
                sqlCursor.execute(f'SELECT * FROM {performanceTestLogsTableName}')
                ptls_db = sqlCursor.fetchall()
                for ptl_db in ptls_db: 
                    performanceTestLogs.append(json.loads(ptl_db[1]))

            #[2-5]: Descriptions
            nnDescs[neuralNetworkCode] = {'dbID':                           dbID,
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
            nnCodes_byID[dbID] = neuralNetworkCode

            #[2-6]: Announcing Description
            nnDescs_announce[neuralNetworkCode] = {'neuralNetworkType':           neuralNetworkType,
                                                   'nKlines':                     nKlines,
                                                   'hiddenLayers':                hiddenLayers,
                                                   'outputLayer':                 outputLayer,
                                                   'generationTime':              generationTime,
                                                   'hashedControlKey':            hashedControlKey, 
                                                   'neuralNetworkConnectionData': networkConnectionData,
                                                   'trainingLogs':                trainingLogs,
                                                   'performanceTestLogs':         performanceTestLogs}
            
        #[3]: Result Return
        self.__ipcA.sendFARR(targetProcess  = task['requester'], 
                             functionResult = nnDescs_announce, 
                             requestID      = task['requestID'],
                             complete       = True)

    def __th_addDescription(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        nnDescs      = self.__neuralNetworkDescriptions
        nnCodes_byID = self.__neuralNetworkCodesByID
        tParams      = task['params']
        neuralNetworkCode        = tParams['neuralNetworkCode']
        neuralNetworkDescription = tParams['neuralNetworkDescription']

        #[2]: Description Setup
        neuralNetworkDescription_dbID = 0
        while neuralNetworkDescription_dbID in nnCodes_byID: 
            neuralNetworkDescription_dbID += 1
        networkConnectionDataTableName = f"ncdt_{neuralNetworkCode}"
        trainingLogsTableName          = f"tlt_{neuralNetworkCode}"
        performanceTestLogsTableName   = f"ptlt_{neuralNetworkCode}"
        nnDesc = {'dbID':                           neuralNetworkDescription_dbID,
                  'neuralNetworkType':              neuralNetworkDescription['type'],
                  'nKlines':                        neuralNetworkDescription['nKlines'],
                  'hiddenLayers':                   neuralNetworkDescription['hiddenLayers'],
                  'outputLayer':                    neuralNetworkDescription['outputLayer'],
                  'generationTime':                 neuralNetworkDescription['generationTime'],
                  'hashedControlKey':               neuralNetworkDescription['hashedControlKey'], 
                  'neuralNetworkConnectionData':    neuralNetworkDescription['connections'],
                  'trainingLogs':                   list(),
                  'performanceTestLogs':            list(),
                  'networkConnectionDataTableName': networkConnectionDataTableName,
                  'trainingLogsTableName':          trainingLogsTableName,
                  'performanceTestLogsTableName':   performanceTestLogsTableName}

        #[3]: Data Save Attempt
        try:
            #[3-1]: Create Data Tables
            sqlCursor.execute(f"""CREATE TABLE {networkConnectionDataTableName} (id INTEGER PRIMARY KEY,
                                                                                 type          TEXT,
                                                                                 layerAddress  TEXT,
                                                                                 tensorAddress TEXT,
                                                                                 value         TEXT
                                                                                )""")
            sqlCursor.execute(f"""CREATE TABLE {trainingLogsTableName} (id INTEGER PRIMARY KEY,
                                                                        trainingLog TEXT
                                                                       )""")
            sqlCursor.execute(f"""CREATE TABLE {performanceTestLogsTableName} (id INTEGER PRIMARY KEY,
                                                                               performanceTestLog TEXT
                                                                              )""")
            
            #[3-2]: Save Network Connection Data
            nnConnectionData = list()
            for index, cData in enumerate(neuralNetworkDescription['connections']): 
                nnConnectionData.append((index, cData[0], cData[1], json.dumps(cData[2]), cData[3]))
            sqlCursor.executemany(f"""INSERT INTO {networkConnectionDataTableName} 
                                  (id, 
                                   type, 
                                   layerAddress, 
                                   tensorAddress, 
                                   value) 
                                  VALUES (?,?,?,?,?)""",
                                  nnConnectionData)

            #[3-3]: Save The Description
            sqlCursor.execute("""INSERT INTO neuralNetworkDescriptions 
                              (id,
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
                               (neuralNetworkDescription_dbID,
                                neuralNetworkCode,
                                neuralNetworkDescription['type'],
                                neuralNetworkDescription['nKlines'],
                                json.dumps(neuralNetworkDescription['hiddenLayers']),
                                json.dumps(neuralNetworkDescription['outputLayer']),
                                neuralNetworkDescription['generationTime'],
                                neuralNetworkDescription['hashedControlKey'],
                                networkConnectionDataTableName,
                                trainingLogsTableName,
                                performanceTestLogsTableName
                               ))
            
            #[3-4]: Commit
            sqlConn.commit()

            #[3-5]: Save The Temporarily Created Neural Network Instance
            nnDescs[neuralNetworkCode]                  = nnDesc
            nnCodes_byID[neuralNetworkDescription_dbID] = neuralNetworkCode

        #[4]: Exception Handling
        except Exception as e:
            #[4-1]: Tables Clearing
            try:    sqlCursor.execute(f"DROP TABLE {networkConnectionDataTableName}")
            except: pass
            try:    sqlCursor.execute(f"DROP TABLE {trainingLogsTableName}")
            except: pass
            try:    sqlCursor.execute(f"DROP TABLE {performanceTestLogsTableName}")
            except: pass
            try:    sqlCursor.execute("DELETE from neuralNetworkDescriptions where neuralNetworkCode = ?", (neuralNetworkCode,))
            except: pass
            sqlConn.commit()

            #[4-2]: Description Clearing
            nnCodes_byID.pop(neuralNetworkDescription_dbID, None)
            nnDescs.pop(neuralNetworkCode, None)
            
            #[4-3]: Logging
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Save A Neural Network Description.\n"
                                     f" * Neural Network Code: {neuralNetworkCode}\n"
                                     f" * Error:               {e}\n"
                                     f" * Detailed Trace:      {traceback.format_exc()}"),
                          logType = 'Error', 
                          color   = 'light_red')

    def __th_removeDescription(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        nnDescs      = self.__neuralNetworkDescriptions
        nnCodes_byID = self.__neuralNetworkCodesByID
        tParams      = task['params']
        neuralNetworkCode = tParams['neuralNetworkCode']

        #[2]: Neural Network Check
        nnDesc = nnDescs.get(neuralNetworkCode, None)
        if nnDesc is None:
            return

        #[3]: Data Removal
        for nnDBID, nnCode in nnCodes_byID.items():
            if nnCode == neuralNetworkCode:
                break
        sqlCursor.execute(f"DROP TABLE {nnDesc['networkConnectionDataTableName']}")
        sqlCursor.execute(f"DROP TABLE {nnDesc['trainingLogsTableName']}")
        sqlCursor.execute(f"DROP TABLE {nnDesc['performanceTestLogsTableName']}")
        sqlCursor.execute("DELETE from neuralNetworkDescriptions where neuralNetworkCode = ?", (neuralNetworkCode,))
        sqlConn.commit()
        del nnCodes_byID[nnDBID]
        del nnDescs[neuralNetworkCode]

    def __th_updateConnectionData(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        nnDescs      = self.__neuralNetworkDescriptions
        tParams      = task['params']
        neuralNetworkCode              = tParams['neuralNetworkCode']
        newNeuralNetworkConnectionData = tParams['newNeuralNetworkConnectionData']

        #[2]: Neural Network Check
        nnDesc = nnDescs.get(neuralNetworkCode, None)
        if nnDesc is None:
            return
        nnConnTableName = nnDesc['networkConnectionDataTableName']
        
        #[3]: Previous Connections Data Clearing
        sqlCursor.execute(f"DELETE FROM {nnConnTableName}")

        #[4]: Data Insertion
        nnConnData_new = [(i, cd[0], cd[1], json.dumps(cd[2]), cd[3]) for i, cd in enumerate(newNeuralNetworkConnectionData)]
        sqlCursor.executemany(f"""INSERT INTO {nnConnTableName} 
                                  (id, type, layerAddress, tensorAddress, value) 
                                   VALUES (?,?,?,?,?)
                               """,
                               nnConnData_new)
        nnDesc['neuralNetworkConnectionData'] = newNeuralNetworkConnectionData

        #[5]: Commit
        sqlConn.commit()

    def __th_addTrainingLog(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        nnDescs      = self.__neuralNetworkDescriptions
        tParams      = task['params']
        neuralNetworkCode = tParams['neuralNetworkCode']
        trainingLog       = tParams['trainingLog']

        #[2]: Neural Network Check
        nnDesc = nnDescs.get(neuralNetworkCode, None)
        if nnDesc is None:
            return
        tlTableName = nnDesc['trainingLogsTableName']
        tls         = nnDesc['trainingLogs']
        
        #[3]: Data Insertion
        sqlCursor.execute(f"""INSERT INTO {tlTableName} 
                              (id, trainingLog) 
                              VALUES (?, ?)
                           """,
                           (len(tls), json.dumps(trainingLog)))
        tls.append(trainingLog)

        #[4]: Commit
        sqlConn.commit()

    def __th_addPerformanceTestLog(self, sqlConn, sqlCursor, task):
        #[1]: Instances
        nnDescs      = self.__neuralNetworkDescriptions
        tParams      = task['params']
        neuralNetworkCode  = tParams['neuralNetworkCode']
        performanceTestLog = tParams['performanceTestLog']

        #[2]: Neural Network Check
        nnDesc = nnDescs.get(neuralNetworkCode, None)
        if nnDesc is None:
            return
        ptlTableName = nnDesc['performanceTestLogsTableName']
        ptls         = nnDesc['performanceTestLogs']
        
        #[3]: Data Insertion
        sqlCursor.execute(f"""INSERT INTO {ptlTableName} 
                              (id, performanceTestLog) 
                              VALUES (?, ?)
                           """,
                           (len(ptls), json.dumps(performanceTestLog)))
        ptls.append(performanceTestLog)

        #[4]: Commit
        sqlConn.commit()
    #Task Handlers END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #FAR & FARR Handlers ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __far_readDBStatus(self, requester, requestID):
        #[1]: Source Check
        if requester != 'GUI':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'type':     'neuralNetwork',
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
        if requester != 'NEURALNETWORKMANAGER':
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
    
    def __far_addDescription(self, requester, neuralNetworkCode, neuralNetworkDescription):
        #[1]: Source Check
        if requester != 'NEURALNETWORKMANAGER':
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'addDescription',
                'requester': requester,
                'requestID': None,
                'params':    {'neuralNetworkCode':        neuralNetworkCode,
                              'neuralNetworkDescription': neuralNetworkDescription}
               }
        self.__taskQueue.put(task)
    
    def __far_removeDescription(self, requester, neuralNetworkCode):
        #[1]: Source Check
        if requester != 'NEURALNETWORKMANAGER':
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'removeDescription',
                'requester': requester,
                'requestID': None,
                'params':    {'neuralNetworkCode': neuralNetworkCode}
               }
        self.__taskQueue.put(task)
    
    def __far_updateConnectionData(self, requester, neuralNetworkCode, newNeuralNetworkConnectionData):
        #[1]: Source Check
        if requester != 'NEURALNETWORKMANAGER':
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'updateConnectionData',
                'requester': requester,
                'requestID': None,
                'params':    {'neuralNetworkCode':              neuralNetworkCode,
                              'newNeuralNetworkConnectionData': newNeuralNetworkConnectionData}
               }
        self.__taskQueue.put(task)
    
    def __far_addTrainingLog(self, requester, neuralNetworkCode, trainingLog):
        #[1]: Source Check
        if requester != 'NEURALNETWORKMANAGER':
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'addTrainingLog',
                'requester': requester,
                'requestID': None,
                'params':    {'neuralNetworkCode': neuralNetworkCode,
                              'trainingLog':       trainingLog}
               }
        self.__taskQueue.put(task)
    
    def __far_addPerformanceTestLog(self, requester, neuralNetworkCode, performanceTestLog):
        #[1]: Source Check
        if requester != 'NEURALNETWORKMANAGER':
            return
        
        #[2]: Task Generation & Add
        task = {'type':      'addPerformanceTestLog',
                'requester': requester,
                'requestID': None,
                'params':    {'neuralNetworkCode':  neuralNetworkCode,
                              'performanceTestLog': performanceTestLog}
               }
        self.__taskQueue.put(task)
    #FAR & FARR Handlers END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------