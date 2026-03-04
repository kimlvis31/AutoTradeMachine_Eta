#ATM Modules
import atmEta_IPC
import atmEta_Auxillaries
import atmEta_Constants

#Python Modules
import time
import os
import termcolor
import sqlite3
import json
import traceback
from datetime import datetime, timedelta, timezone
from collections import deque

import subprocess
import psycopg2
import platform
import socket
from psycopg2 import pool
from psycopg2.extras import execute_values, execute_batch

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

COMMONDATAINDEXES = {'openTime':  {'kline': KLINDEX_OPENTIME,  'depth': DEPTHINDEX_OPENTIME,  'aggTrade': ATINDEX_OPENTIME},
                     'closeTime': {'kline': KLINDEX_CLOSETIME, 'depth': DEPTHINDEX_CLOSETIME, 'aggTrade': ATINDEX_CLOSETIME},
                     'closed':    {'kline': KLINDEX_CLOSED,    'depth': DEPTHINDEX_CLOSED,    'aggTrade': ATINDEX_CLOSED},
                     'source':    {'kline': KLINDEX_SOURCE,    'depth': DEPTHINDEX_SOURCE,    'aggTrade': ATINDEX_SOURCE}}

KLINTERVAL   = atmEta_Constants.KLINTERVAL
KLINTERVAL_S = atmEta_Constants.KLINTERVAL_S

_STREAMEDDATASAVEINTERVAL_NS = 1e9

_MARKETDATA_ANNOUNCEMENT_KEYS = {'precisions', 'baseAsset', 'quoteAsset', 'kline_firstOpenTS', 'klines_availableRanges', 'depths_availableRanges', 'aggTrades_availableRanges', 'info_server'}

_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

PGSQLDOCKERCONTAINERNAME = 'atmEta'

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
        if not os.path.isdir(self.path_dbFolder): os.mkdir(self.path_dbFolder)
        
        #Read DataManager Configuration File
        self.__config_DataManager = dict()
        self.__readDataManagerConfig()

        #DB Connections & Cursors
        #---Docker
        dbPortNumber = self.__setupDocker()

        #---PostgreSQL
        dmConfig = self.__config_DataManager
        self.__pg_config = {'dbname':   dmConfig['pg_dbName'],
                            'user':     dmConfig['pg_user'],
                            'password': dmConfig['pg_password'],
                            'port':     dbPortNumber,
                            'host':     'localhost'}
        self.__pg_connection = None
        self.__pg_cursor     = None
        if dbPortNumber is not None:
            nAttempts     = 0
            nAttempts_max = 5
            while nAttempts < nAttempts_max:
                try:
                    self.__pg_pool = pool.SimpleConnectionPool(1, 10, **self.__pg_config)
                    self.__pg_connection = self.__pg_pool.getconn()
                    self.__pg_connection.autocommit = False
                    self.__pg_cursor = self.__pg_connection.cursor()
                    print("    * PostgreSQL Connection Established")
                    break
                except Exception as e:
                    print(termcolor.colored((f"    * PostgreSQL Connection Attempt Failed [Attmpt: {nAttempts+1} / {nAttempts_max}].\n"
                                            f"      * Error:          {e}\n"
                                            f"      * Detailed Trace: {traceback.format_exc()}"
                                            ), 
                                            'light_red'))
                    nAttempts += 1
                    time.sleep(10)
        if self.__pg_connection is None:
            print(termcolor.colored(f"    * PostgreSQL Connection Failed.", 'light_red'))

        #---SQLite3
        self.__sql_simulations_connection    = sqlite3.connect(os.path.join(self.path_dbFolder, 'atmEta_simulations.db'));    self.__sql_simulations_cursor    = self.__sql_simulations_connection.cursor()
        self.__sql_accounts_connection       = sqlite3.connect(os.path.join(self.path_dbFolder, 'atmEta_accounts.db'));       self.__sql_accounts_cursor       = self.__sql_accounts_connection.cursor()
        self.__sql_neuralNetworks_connection = sqlite3.connect(os.path.join(self.path_dbFolder, 'atmEta_neuralNetworks.db')); self.__sql_neuralNetworks_cursor = self.__sql_neuralNetworks_connection.cursor()
        print("    * SQLite3 Connections Established")

        #Local Data
        self.__marketData                = dict()
        self.__accountDescriptions       = dict()
        self.__accountLocalIDsByID       = dict()
        self.__simulationDescriptions    = dict()
        self.__simulationCodesByID       = dict()
        self.__neuralNetworkDescriptions = dict()
        self.__neuralNetworCodesByID     = dict()

        #Stream Save Trackers
        self.__streamedData_lastSaved_ns = 0

        #Read From DB
        self.__readFromDB_market()
        self.__readFromDB_account()
        self.__readFromDB_simulation()
        self.__readFromDB_neuralNetwork()

        #Request Queues - Outbound
        self.__requestQueues_ob = {'marketDataFetch_pending':   {dataType: set()  for dataType in ('kline', 'depth', 'aggTrade')},
                                   'marketDataFetch_active':    {dataType: dict() for dataType in ('kline', 'depth', 'aggTrade')},
                                   'marketDataFetch_responses': deque()
                                   }
        self.__marketDataFetch_pauseRequested = False

        #Request Queues - Inbound
        self.__requestQueues_ib = {'marketDataFetch':                       deque(),

                                   'accountDataEdit':                       deque(),
                                   'accountTradeLogAppend':                 deque(),
                                   'accountPeriodicReportUpdate':           deque(),
                                   'neuralNetworkConnectionDataUpdate':     deque(),
                                   'neuralNetworkTrainingLogAppendRequest': deque(),
                                   'neuralNetworkPerformanceTestLogAppend': deque()
                                   }

        self.__accountDataEditRequestQueues                       = deque()
        self.__accountTradeLogAppendRequestQueues                 = deque()
        self.__accountPeriodicReportUpdateRequestQueues           = deque()
        self.__neuralNetworkConnectionDataUpdateRequestQueues     = deque()
        self.__neuralNetworkTrainingLogAppendRequestQueues        = deque()
        self.__neuralNetworkPerformanceTestLogAppendRequestQueues = deque()

        #Initial Data Share
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CONFIGURATION', prdContent = self.__config_DataManager.copy())

        #FAR Registration
        #---BINANCEAPI
        self.ipcA.addFARHandler('registerCurrency',         self.__far_registerCurrency,         executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onCurrencyInfoUpdate',     self.__far_onCurrencyInfoUpdate,     executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onKlineStreamReceival',    self.__far_onKlineStreamReceival,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onDepthStreamReceival',    self.__far_onDepthStreamReceival,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onAggTradeStreamReceival', self.__far_onAggTradeStreamReceival, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
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
        self.ipcA.addFARHandler('fetchMarketData',                    self.__far_fetchMarketData,                    executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        self.ipcA.addFARHandler('registerCurrecnyInfoSubscription',   self.__far_registerCurrecnyInfoSubscription,   executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        self.ipcA.addFARHandler('unregisterCurrecnyInfoSubscription', self.__far_unregisterCurrecnyInfoSubscription, executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)

        #Process Control
        self.__processLoopContinue = True

        print(termcolor.colored("   DATAMANAGER", 'light_blue'), termcolor.colored("Initialization Complete! -----------------------------------------------------------------------------------------------------------", 'green'))
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    
    
    #Manager Process Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        while self.__processLoopContinue:
            #Process any exsiting FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()

            #Process Internal Data & Request Queues
            self.__saveDataFetchResults()                      #Send a market data fetch results (only one is processed at a time to avoid being a bottleneck)
            self.__saveStreamedData()                          #Save any exsiting streamed data
            self.__sendDataFetchRequests()                     #Send any needed fetch requests
            self.__processDataFetchRequestQueue()              #Process a data fetch request queue
            self.__processAccountDataEditRequestQueues()       #Process any account data edit request queues
            self.__processNeuralNetworkDataEditRequestQueues() #Process any neural network data update request queues

            #Loop Sleep
            if self.__loopSleepDeterminer(): time.sleep(0.001)

        #Terminate TWM if it is alive
        try: 
            if self.__binance_TWM.is_alive(): self.__binance_TWM.stop()
            self.__binance_TWM.join()
        except: pass

    def __loopSleepDeterminer(self):
        #[3]: Return True If No Hustle Is Needed
        return True
    
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
        #---[2-4]: PostgreSQL DBName
        pg_dbName = config_loaded.get('pg_dbName', 'atm_eta')
        if not isinstance(pg_dbName, str): pg_dbName = 'atm_eta'
        #---[2-5]: PostgreSQL User
        pg_user = config_loaded.get('pg_user', 'atm_eta')
        if not isinstance(pg_user, str): pg_user = 'atm_eta'
        #---[2-6]: PostgreSQL Password
        pg_password = config_loaded.get('pg_password', 'atmEtaDefault')
        if not isinstance(pg_password, str): pg_password = 'atmEtaDefault'
        #---[2-7]: PostgreSQL Directory
        pg_directory = config_loaded.get('pg_directory', "C:/ATMEta/db_data")
        if not isinstance(pg_directory, str): pg_directory = "C:/ATMEta/db_data"
        #---[2-8]: PostgreSQL Container Memory Limit
        pg_memoryLimit = config_loaded.get('pg_memoryLimit', 4)
        if not isinstance(pg_memoryLimit, int): pg_memoryLimit = 4
        pg_memoryLimit = max(pg_memoryLimit, 1)
        pg_memoryLimit = min(pg_memoryLimit, 32)
        #---[2-9]: PostgreSQL Container Shared Buffer
        pg_sharedBuffer = config_loaded.get('pg_sharedBuffer', 1)
        if not isinstance(pg_sharedBuffer, int): pg_sharedBuffer = 1
        pg_sharedBuffer = max(pg_sharedBuffer, 1)
        pg_sharedBuffer = min(pg_sharedBuffer, 8)

        #[3]: Update and save the configuration
        self.__config_DataManager = {'print_Update':    print_update,
                                     'print_Warning':   print_warning,
                                     'print_Error':     print_error,
                                     'pg_dbName':       pg_dbName,
                                     'pg_user':         pg_user,
                                     'pg_password':     pg_password,
                                     'pg_directory':    pg_directory,
                                     'pg_memoryLimit':  pg_memoryLimit,
                                     'pg_sharedBuffer': pg_sharedBuffer}
        self.__saveDataManagerConfig()
    
    def __saveDataManagerConfig(self):
        #[1]: Configuration
        config = self.__config_DataManager

        #[2]: Save the reformatted configuration file
        config_dir = os.path.join(self.path_project, 'configs', 'dmConfig.config')
        try:
            with open(config_dir, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Save Data Manager Configuration. User Attention Strongly Advised"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')



    #---Initial DataBase Read
    def __getUnavailablePortNumberRanges(self):
        unavailablePortRanges = []
        #[1]: If Windows, Check For Winnat Excluded Port Ranges
        if platform.system() == "Windows":
            try:
                response = subprocess.run(args           = ["netsh", "interface", "ipv4", "show", "excludedportrange", "protocol=tcp"],
                                          capture_output = True, 
                                          text           = True,
                                          errors         = 'ignore',
                                          check          = False)
                for line in response.stdout.splitlines():
                    parts = line.split()
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        unavailablePortRange = (int(parts[0]), int(parts[1]))
                        unavailablePortRanges.append(unavailablePortRange)
            except Exception as e:
                print(termcolor.colored((f"    * An Unexpected Error Occurred While Attempting Parse Winnat Excluded Port Ranges.\n"
                                         f"      * Error:          {e}\n"
                                         f"      * Detailed Trace: {traceback.format_exc()}"
                                         ),
                                        'light_red'))
        #[2]: Return Unavailable Port Number Ranges
        return unavailablePortRanges
    
    def __isPortNumberAvailable(self, portNumber, unavailablePortRanges = None):
        #[1]: Check If The Port Number Is Within The Unavailable Port Ranges
        if unavailablePortRanges is not None:
            if any(start <= portNumber <= end for start, end in unavailablePortRanges):
                return False

        #[2]: Attempt Port Binding To Check Availability
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', portNumber))
                return True
            except OSError:
                return False

    def __getAvailablePortNumber(self):
        #[1]: Search For Available Ports In Range (10000 ~ 49151)
        unavailablePortRanges = self.__getUnavailablePortNumberRanges()
        portNumber = 10000
        while portNumber <= 49151:
            if self.__isPortNumberAvailable(portNumber = portNumber, unavailablePortRanges = unavailablePortRanges):
                return portNumber
            else:
                portNumber += 1

        #[2]: Return None To Indicate No Port Number Being Found
        return None
    
    def __setupDocker(self):
        #[1]: Attempt To Setup Docker
        try:
            #[1-1]: Check If ATMETA Container Exists
            response = subprocess.run(args           = ["docker", "ps", "-a", "--filter", f"name={PGSQLDOCKERCONTAINERNAME}", "--format", "{{.Names}}"],
                                      capture_output = True, 
                                      text           = True, 
                                      check          = True)
            containerExists = (PGSQLDOCKERCONTAINERNAME in response.stdout.splitlines())

            #[1-2]: If Container Exists, Check If It Is Running.
            if containerExists:
                print(f"    * Docker Container '{PGSQLDOCKERCONTAINERNAME}' Is Found!")
                #[1-2-1]: Get Status
                response = subprocess.run(args           = ["docker", "inspect", "--format", "{{.State.Status}}", PGSQLDOCKERCONTAINERNAME], 
                                          capture_output = True, 
                                          text           = True,
                                          check          = True)
                containerRunning = (response.stdout.strip() == 'running')

                #[1-2-2]: Get Port Number
                response = subprocess.run(["docker", "inspect", "--format", '{{(index (index .HostConfig.PortBindings "5432/tcp") 0).HostPort}}', PGSQLDOCKERCONTAINERNAME], capture_output=True, text=True)
                portNumber = int(response.stdout.strip())

                #[1-2-3]: If The Container Is Not Running, Check Used Port Number Availability. Recreate The Container If Taken, And Start Otherwise
                if not containerRunning:
                    print(f"    * The Docker Container Is Not Running. Checking The Port Number Availability...")
                    portTaken             = False
                    unavailablePortRanges = self.__getUnavailablePortNumberRanges()
                    #[1-3-3-1]: Check Within The Unavailable Port Ranges
                    if any(start <= portNumber <= end for start, end in unavailablePortRanges):
                        print(f"    * The Port Number Of The Docker Container Is Taken (Likely By 'Winnat' If In Windows Environment). The Container Will Be Recreated!")
                        portTaken = True
                    #[1-3-3-2]: Check If The Port Is Available By Attempting Binding
                    elif not self.__isPortNumberAvailable(portNumber = portNumber, unavailablePortRanges = None):
                        print(f"    * The Port Number Of The Docker Container Is Unavailable. The Container Will Be Recreated!")
                        portTaken = True
                    #[1-3-3-3]: If The Port Is Taken, 
                    if portTaken:
                        print(f"    * Creating Docker Container '{PGSQLDOCKERCONTAINERNAME}'...")
                        self.__removeDockerContainer()
                        portNumber = self.__getAvailablePortNumber()
                        self.__createDockerContainer(portNumber = portNumber)
                        print(f"    * Docker Container '{PGSQLDOCKERCONTAINERNAME}' Created! Starting...")
                        time.sleep(15)
                    else:
                        print(f"    * Starting The Docker Container...")
                        self.__startDockerContainer()
                        time.sleep(10)

            #[1-3]: Container Not Found. Create It And Start "netsh", "interface", "ipv4", "show", "excludedportrange", "protocol=tcp"
            else:
                print(f"    * Docker Container '{PGSQLDOCKERCONTAINERNAME}' Not Found, Creating...")
                portNumber = self.__getAvailablePortNumber()
                self.__createDockerContainer(portNumber = portNumber)
                print(f"    * Docker Container '{PGSQLDOCKERCONTAINERNAME}' Created! Starting...")
                time.sleep(15)
                
            #[1-4]: Wait Until The Container Is Started
            while True:
                response = subprocess.run(args           = ["docker", "inspect", "-f", "{{.State.Status}}", PGSQLDOCKERCONTAINERNAME], 
                                          capture_output = True, 
                                          text           = True)
                if response.stdout.strip() == "running":
                    print(f"    * Docker Container '{PGSQLDOCKERCONTAINERNAME}' Is Running!")
                    break
                else: time.sleep(1)

            #[1-5]: Return The Port Number
            print(f"    * Docker Container '{PGSQLDOCKERCONTAINERNAME}' Setup Complete! (Port Number: {portNumber})")
            return portNumber

        #[2]: Exception Handling
        except Exception as e:
            print(termcolor.colored((f"    * An Unexpected Error Occurred While Attempting To Setup Docker Container. Make Sure Docker Desktop Is Running.\n"
                                     f"      * Error:          {e}\n"
                                     f"      * Detailed Trace: {traceback.format_exc()}"
                                     ),
                                     'light_red'))
            return None
            
    def __removeDockerContainer(self):
        subprocess.run(args = ["docker", "rm", "-f", PGSQLDOCKERCONTAINERNAME],
                       capture_output = True,
                       text           = True,
                       check          = True)

    def __createDockerContainer(self, portNumber):
        #[1]: Instances
        dmConfig = self.__config_DataManager

        #[2]: Docker Container Creation
        subprocess.run(args = ["docker", "run", "-d",
                               "--name", PGSQLDOCKERCONTAINERNAME,
                               "-m", f"{dmConfig['pg_memoryLimit']}g",
                               "-p", f"{portNumber}:5432",
                               "-e", f"POSTGRES_USER={dmConfig['pg_user']}",
                               "-e", f"POSTGRES_PASSWORD={dmConfig['pg_password']}",
                               "-e", f"POSTGRES_DB={dmConfig['pg_dbName']}",
                               "--restart", "always",
                               "-v", f"{dmConfig['pg_directory']}:/var/lib/postgresql/data",
                               "timescale/timescaledb:latest-pg17",
                               "-c", "shared_preload_libraries=timescaledb",
                               "-c", f"shared_buffers={dmConfig['pg_sharedBuffer']}GB"
                              ], 
                       capture_output = True,
                       check          = True)
        
    def __startDockerContainer(self):
        subprocess.run(args           = ["docker", "start", PGSQLDOCKERCONTAINERNAME], 
                       capture_output = True,
                       check          = True)

    def __readFromDB_market(self):
        #[1]: Instances
        md       = self.__marketData
        pgConn   = self.__pg_connection
        pgCursor = self.__pg_cursor
        func_sendPRDEDIT = self.ipcA.sendPRDEDIT

        #[2]: PostgreSQL Conenction Check
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
                                    aggtrades_availableranges   JSONB
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
        self.__pg_connection.commit()

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
            md[symbol] = {'precisions':                precisions,
                          'baseAsset':                 baseAsset,
                          'quoteAsset':                quoteAsset,
                          'kline_firstOpenTS':         kline_firstOpenTS,
                          'depth_firstOpenTS':         depth_firstOpenTS,
                          'aggTrade_firstOpenTS':      aggTrade_firstOpenTS,
                          'klines_availableRanges':    klines_availableRanges,
                          'depths_availableRanges':    depths_availableRanges,
                          'aggTrades_availableRanges': aggTrades_availableRanges,
                          'info_server':               None,
                          '_stream_klines':            {'klines':    list(), 'range': None, 'firstOpenTS': None},
                          '_stream_depths':            {'depths':    list(), 'range': None, 'firstOpenTS': None},
                          '_stream_aggTrades':         {'aggTrades': list(), 'range': None, 'firstOpenTS': None},
                          '_subscribers':              baseSubscribers.copy()}
        print(f" * {len(md)} Currencies Data Imported!")

        #[5]: Announce The Market (Currency) Info
        md_announce = {symbol: {k: v for k, v in data.items() if k in _MARKETDATA_ANNOUNCEMENT_KEYS} for symbol, data in md.items()}
        for processName in ('GUI', 'TRADEMANAGER', 'SIMULATIONMANAGER', 'NEURALNETWORKMANAGER'):
            func_sendPRDEDIT(targetProcess = processName,
                             prdAddress    = 'CURRENCIES',
                             prdContent    = md_announce)
            
    def __readFromDB_account(self):
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
    
    def __readFromDB_simulation(self):
        #Table Check
        self.__sql_simulations_cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
        tablesInDB = [fetchedElement[0] for fetchedElement in self.__sql_simulations_cursor.fetchall()]
        if ('simulationDescriptions' not in tablesInDB): self.__sql_simulations_cursor.execute("""CREATE TABLE simulationDescriptions (id INTEGER PRIMARY KEY, 
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
        #Currency Data Identification & Read
        self.__sql_simulations_cursor.execute("SELECT * FROM simulationDescriptions")
        dbTableData_simulationDescriptions = self.__sql_simulations_cursor.fetchall()
        for summaryRow in dbTableData_simulationDescriptions:
            #Read SimulationDescription Line
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
    
    def __readFromDB_neuralNetwork(self):
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



    #---Market Data
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
    def __saveDataFetchResults(self):
        #[1]: Response Target
        rqOB       = self.__requestQueues_ob
        fResponses = rqOB['marketDataFetch_responses']
        if not fResponses: return
        response = fResponses.popleft()

        #[2]: Response Contents & Fetch Request
        #---[2-1]: Response Contents
        target  = response['target']
        rID     = response['requestID']
        fResult = response['functionResult']
        fr_fetchedRange = fResult['fetchedRange']
        fr_status       = fResult['status']
        fr_data         = fResult['data']
        #---[2-2]: Fetch Request Check
        fActive = rqOB['marketDataFetch_active'][target]
        request = fActive.get(rID, None)
        if request is None:
            return

        #[3]: Instances
        pgConn           = self.__pg_connection
        pgCursor         = self.__pg_cursor
        md               = self.__marketData
        fPending         = rqOB['marketDataFetch_pending'][target]
        func_gdrc        = self.__dataRange_getClassification
        func_sendPRDEDIT = self.ipcA.sendPRDEDIT
        func_sendFAR     = self.ipcA.sendFAR

        #[4]: Result Interpretation
        if fr_status in ('fetching', 'complete'):
            #[4-1]: Instances
            symbol    = request['symbol']
            md_symbol = md[symbol]
            aRanges = md_symbol[f'{target}s_availableRanges']
            fRange  = fr_fetchedRange

            #[4-2]: Overlap Check
            if aRanges is not None:
                for adr in aRanges:
                    if func_gdrc(adr, fRange) not in (0b0000, 0b1111): 
                        self.__logger(message = (f"A Data Ranges Overlap Detected While Attempting To Save Fetched Data. The Fetch Request Will Be Updated.\n"
                                                 f" * Symbol:           {symbol}\n"
                                                 f" * Target:           {target}\n"
                                                 f" * Available Ranges: {aRanges}\n"
                                                 f" * Fetched Range:    {fRange}"
                                                 ),
                                      logType = 'Warning',
                                      color   = 'light_red')
                        fPending.add(symbol)
                        del fActive[rID]
                        return

            #[4-3]: New Data Ranges
            if aRanges is None: aRanges_new = [fRange,]
            else:
                aRanges_new = aRanges.copy()
                aRanges_new.append(fRange)
                aRanges_new.sort(key = lambda x: x[0])
                aRanges_new_merged = []
                for dr in aRanges_new:
                    if not aRanges_new_merged: 
                        aRanges_new_merged.append(dr)
                    else:
                        if aRanges_new_merged[-1][1]+1 == dr[0]: aRanges_new_merged[-1] = [aRanges_new_merged[-1][0], dr[1]]
                        else:                                    aRanges_new_merged.append(dr)
                aRanges_new = aRanges_new_merged
            
            #[4-4]: DB Update
            #---[4-4-1]: Target == 'kline'
            if target == 'kline':
                pgParams_data = [(kl[KLINDEX_OPENTIME],         # openTS (for to_timestamp(%s))
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
                                 ) for kl in fr_data]
                pgQuery_data = """INSERT INTO klines (time, symbol, t_open, t_close, p_open, p_high, p_low, p_close, ntrades, v, q, v_tb, q_tb, ktype)
                                  VALUES %s
                               """
                pgTemplate_data = "(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            #---[4-4-2]: Target == 'depth'
            elif target == 'depth':
                pgParams_data = [(depth[DEPTHINDEX_OPENTIME],  # openTS (for to_timestamp(%s))
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
                                 ) for depth in fr_data]
                pgQuery_data = """INSERT INTO depths (time, symbol, t_open, t_close, bids5, bids4, bids3, bids2, bids1, bids0, asks0, asks1, asks2, asks3, asks4, asks5, dtype)
                                  VALUES %s
                               """
                pgTemplate_data = "(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            #---[4-4-3]: Target == 'aggTrade'
            elif target == 'aggTrade':
                pgParams_data = [(at[ATINDEX_OPENTIME],     # openTS (for to_timestamp(%s))
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
                                 ) for at in fr_data]
                pgQuery_data = """INSERT INTO aggTrades (time, symbol, t_open, t_close, quantity_buy, quantity_sell, ntrades_buy, ntrades_sell, notional_buy, notional_sell, attype)
                                  VALUES %s
                               """
                pgTemplate_data = "(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            #---[4-4-4]: Available Ranges Params & Query
            pgParams_aRanges = (json.dumps(aRanges_new), symbol)
            if   target == 'kline':    pgQuery_aRanges  = f"UPDATE descriptors SET klines_availableranges = %s WHERE symbol = %s"
            elif target == 'depth':    pgQuery_aRanges  = f"UPDATE descriptors SET depths_availableranges = %s WHERE symbol = %s"
            elif target == 'aggTrade': pgQuery_aRanges  = f"UPDATE descriptors SET aggtrades_availableranges = %s WHERE symbol = %s"

            #---[4-4-5]: DB Update Attempt
            dbUpdated = False
            try:
                execute_values(cur       = pgCursor, 
                               sql       = pgQuery_data, 
                               argslist  = pgParams_data,
                               template  = pgTemplate_data,
                               page_size = 1000)
                pgCursor.execute(pgQuery_aRanges, pgParams_aRanges)
                pgConn.commit()
                dbUpdated = True
            except Exception as e:
                self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Update DB With The Fetched Data. User Attention Advised.\n"
                                         f" * Symbol:         {symbol}\n"
                                         f" * Target:         {target}\n"
                                         f" * Error:          {e}\n"
                                         f" * Detailed Trace: {traceback.format_exc()}"
                                        ), 
                              logType = 'Warning', 
                              color   = 'light_red')
                pgConn.rollback()

            #[4-5]: Available Ranges Update & Announcement
            if dbUpdated:
                md_symbol[f'{target}s_availableRanges'] = aRanges_new
                prdEdit_prdAddress = ('CURRENCIES', symbol, f'{target}s_availableRanges')
                far_functionParams = {'updatedContents': [{'symbol': symbol, 'id': (f'{target}s_availableRanges',)}]}
                for procName in md_symbol['_subscribers']:
                    func_sendPRDEDIT(targetProcess = procName, 
                                     prdAddress    = prdEdit_prdAddress, 
                                     prdContent    = aRanges_new)
                    func_sendFAR(targetProcess  = procName, 
                                 functionID     = 'onCurrenciesUpdate',
                                 functionParams = far_functionParams, 
                                 farrHandler    = None)

        #[5]: Request Update
        if fr_status in ('complete', 'terminate'):
            del fActive[rID]
        
        #[6]: Fetch Pause Release
        if len(fResponses) < 20 and self.__marketDataFetch_pauseRequested:
            self.ipcA.sendFAR(targetProcess  = 'BINANCEAPI',
                              functionID     = 'continueMarketDataFetch',
                              functionParams = None,
                              farrHandler    = None)
            self.__marketDataFetch_pauseRequested = False

    def __onDataStreamReceival(self, symbol, dataType, streamedData):
        #[1]: Closed Check
        if not streamedData[COMMONDATAINDEXES['closed'][dataType]]: return

        #[2]: Instances
        rqOB      = self.__requestQueues_ob
        md_symbol = self.__marketData[symbol]
        sData = md_symbol[f'_stream_{dataType}s']
        sData_data        = sData[f'{dataType}s']
        sData_range       = sData['range']
        sData_firstOpenTS = sData['firstOpenTS']

        #[3]: Range Check
        sRange = [streamedData[KLINDEX_OPENTIME], streamedData[KLINDEX_CLOSETIME]]
        if sData_range is not None:
            drClassification = self.__dataRange_getClassification(dataRange1 = sData_range, 
                                                                  dataRange2 = sRange)
            openTS_expected  = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL,
                                                                               timestamp  = sData_range[0],
                                                                               mrktReg    = None,
                                                                               nTicks     = 1)
            if (drClassification != 0b0000) or (openTS_expected != sRange[0]):
                self.__logger(message = (f"An Unexpected Streamed Data Detected And Will Be Disposed.\n"
                                         f" * Symbol:             {symbol}\n"
                                         f" * Streamed Data:      {streamedData}\n"
                                         f" * Received Timestamp: {streamedData[KLINDEX_OPENTIME]}\n"
                                         f" * Expected Timestamp: {openTS_expected}"
                                         ), 
                              logType = 'Warning', 
                              color   = 'light_yellow')
                if md_symbol[f'{dataType}_firstOpenTS'] is not None: 
                    rqOB['marketDataFetch_pending'][dataType].add(symbol)
                return

        #[4]: First Stream Open TS Update
        if sData_firstOpenTS is None:
            sData['firstOpenTS'] = streamedData[KLINDEX_OPENTIME]
            if md_symbol[f'{dataType}_firstOpenTS'] is not None: 
                rqOB['marketDataFetch_pending'][dataType].add(symbol)

        #[5]: Save The Streamed Data & Update Streamed Range
        sData_data.append(streamedData)
        if sData_range is None: sData['range']    = sRange
        else:                   sData['range'][1] = sRange[1]

    def __saveStreamedData(self):
        #[1]: Timer Check
        t_current_ns = time.perf_counter_ns()
        if t_current_ns-self.__streamedData_lastSaved_ns < _STREAMEDDATASAVEINTERVAL_NS:
            return
        
        #[2]: Instances
        pgConn   = self.__pg_connection
        pgCursor = self.__pg_cursor
        md       = self.__marketData
        func_gdrc        = self.__dataRange_getClassification
        func_sendPRDEDIT = self.ipcA.sendPRDEDIT
        func_sendFAR     = self.ipcA.sendFAR

        #[3]: Streamed Data Collection
        sqlParams_data_total = {'kline':    [],
                                'depth':    [],
                                'aggTrade': []}
        sqlParams_aRanges_total = {'kline':    [],
                                   'depth':    [],
                                   'aggTrade': []}
        aRanges_new_updated = dict()
        for symbol, md_symbol in md.items():
            for dataType in ('kline', 'depth', 'aggTrade'):
                #[3-1]: Stream Range Check
                sData = md_symbol[f'_stream_{dataType}s']
                sData_data  = sData[f'{dataType}s']
                sData_range = sData['range']
                if sData_range is None: continue

                #[3-2]: Overlap Check
                overlapped = False
                aRanges = md_symbol[f'{dataType}s_availableRanges']
                if aRanges is not None:
                    for adr in aRanges:
                        if func_gdrc(adr, sData_range) not in (0b0000, 0b1111):
                            overlapped = True 
                            break
                if overlapped:
                    self.__logger(message = (f"An Overlap Detected Between The Available Data Ranges And The Streamed Data. The Corresponding Data Will Be Disposed"
                                            f" * Symbol:           {symbol}\n"
                                            f" * Data Type:        {dataType}\n"
                                            f" * Available Ranges: {aRanges}\n"
                                            f" * Streamed Range:   {sData_range}"
                                            ), 
                                logType = 'Warning', 
                                color   = 'light_red')
                    continue

                #[3-4]: New Data Range
                if aRanges is None: aRanges_new = [sData_range.copy(),]
                else:
                    aRanges_new = [aRange.copy() for aRange in aRanges]
                    aRanges_new.append(sData_range.copy())
                    aRanges_new.sort(key = lambda x: x[0])
                    aRanges_merged = []
                    for dr in aRanges_new:
                        if not aRanges_merged: 
                            aRanges_merged.append(dr)
                        else:
                            if aRanges_merged[-1][1]+1 == dr[0]: aRanges_merged[-1] = [aRanges_merged[-1][0], dr[1]]
                            else:                                aRanges_merged.append(dr)
                    aRanges_new = aRanges_merged

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
                                      ) for kl in sData_data]
                    sqlParams_aRanges = (json.dumps(aRanges_new), symbol)

                #---[3-5-1]: Depth
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
                                      ) for depth in sData_data]
                    sqlParams_aRanges = (json.dumps(aRanges_new), symbol)

                #---[3-5-1]: AggTrade
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
                                      ) for at in sData_data]
                    sqlParams_aRanges = (json.dumps(aRanges_new), symbol)

                #[3-6]: Collection
                sqlParams_data_total[dataType].extend(sqlParams_data)
                sqlParams_aRanges_total[dataType].append(sqlParams_aRanges)
                if symbol not in aRanges_new_updated: aRanges_new_updated[symbol] = dict()
                aRanges_new_updated[symbol][dataType] = aRanges_new

                #[3-7]: Buffer Clearing
                sData_data.clear()
                sData['range'] = None

        #[4]: DB Update
        #---[4-1]: Queries
        #------[4-1-1]: Kline
        if sqlParams_data_total['kline']:
            pgQuery_klines_data = """INSERT INTO klines (time, symbol, t_open, t_close, p_open, p_high, p_low, p_close, ntrades, v, q, v_tb, q_tb, ktype)
                                     VALUES %s
                                  """
            pgQuery_klines_aRanges = "UPDATE descriptors SET klines_availableranges = %s WHERE symbol = %s"
        else:
            pgQuery_klines_data    = None
            pgQuery_klines_aRanges = None
        #------[4-1-2]: Depth
        if sqlParams_data_total['depth']:
            pgQuery_depths_data = """INSERT INTO depths (time, symbol, t_open, t_close, bids5, bids4, bids3, bids2, bids1, bids0, asks0, asks1, asks2, asks3, asks4, asks5, dtype)
                                     VALUES %s
                                  """
            pgQuery_depths_aRanges = "UPDATE descriptors SET depths_availableranges = %s WHERE symbol = %s"
        else:
            pgQuery_depths_data    = None
            pgQuery_depths_aRanges = None
        #------[4-1-3]: AggTrade
        if sqlParams_data_total['aggTrade']:
            pgQuery_aggTrades_data = """INSERT INTO aggTrades (time, symbol, t_open, t_close, quantity_buy, quantity_sell, ntrades_buy, ntrades_sell, notional_buy, notional_sell, attype)
                                        VALUES %s
                                     """
            pgQuery_aggTrades_aRanges = "UPDATE descriptors SET aggTrades_availableranges = %s WHERE symbol = %s"
        else:
            pgQuery_aggTrades_data    = None
            pgQuery_aggTrades_aRanges = None
        #---[4-2]: Queries Execution
        dbUpdated = False
        if any(cd for cd in sqlParams_data_total.values()):
            try:
                #[4-2-1]: Klines
                if pgQuery_klines_data is not None:
                    execute_values(cur       = pgCursor, 
                                   sql       = pgQuery_klines_data, 
                                   argslist  = sqlParams_data_total['kline'],
                                   template  = "(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                   page_size = 1000)
                    pgCursor.executemany(pgQuery_klines_aRanges, sqlParams_aRanges_total['kline'])
                #[4-2-2]: Depths
                if pgQuery_depths_data is not None:
                    execute_values(cur       = pgCursor, 
                                   sql       = pgQuery_depths_data, 
                                   argslist  = sqlParams_data_total['depth'],
                                   template  = "(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                   page_size = 1000)
                    pgCursor.executemany(pgQuery_depths_aRanges, sqlParams_aRanges_total['depth'])
                #[4-2-3]: AggTrades
                if pgQuery_aggTrades_data is not None:
                    execute_values(cur       = pgCursor, 
                                   sql       = pgQuery_aggTrades_data, 
                                   argslist  = sqlParams_data_total['aggTrade'],
                                   template  = "(to_timestamp(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                   page_size = 1000)
                    pgCursor.executemany(pgQuery_aggTrades_aRanges, sqlParams_aRanges_total['aggTrade'])
                #[4-2-4]: Commit
                pgConn.commit()
                dbUpdated = True
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
            for symbol, updates in aRanges_new_updated.items():
                md_symbol = md[symbol]
                #[5-1-1]: Local Tracker & PRD
                for dataType, aRanges_new in updates.items():
                    md_symbol[f'{dataType}s_availableRanges'] = aRanges_new
                    prdEdit_prdAddress = ('CURRENCIES', symbol, f'{dataType}s_availableRanges')
                    for procName in md_symbol['_subscribers']:
                        func_sendPRDEDIT(targetProcess = procName, 
                                         prdAddress    = prdEdit_prdAddress, 
                                         prdContent    = aRanges_new)
                #[5-1-2]: FAR
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

        #[6]: Update Timer
        self.__streamedData_lastSaved_ns = t_current_ns
    
    def __sendDataFetchRequests(self):
        #[1]: Instances
        md           = self.__marketData
        rqOB         = self.__requestQueues_ob
        func_sendFAR = self.ipcA.sendFAR

        #[2]: Dispath Fetch Requests To BINANCEAPI
        for target in ('kline', 'depth', 'aggTrade'):
            #[2-1]: Instances
            fPending = rqOB['marketDataFetch_pending'][target]
            fActive  = rqOB['marketDataFetch_active'][target]

            #[2-2]: Dispath Fetch Requests To BINANCEAPI
            for symbol in fPending:
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

                #[2-2-3]: Dispath Fetch Request
                dispatchRID = func_sendFAR(targetProcess  = 'BINANCEAPI', 
                                           functionID     = 'fetchData', 
                                           functionParams = {'symbol':            symbol,
                                                             'target':            target,
                                                             'fetchTargetRanges': ftRanges}, 
                                           farrHandler = self.__farr_getDataFetchRequestResult)
                fActive[dispatchRID] = {'symbol':            symbol,
                                        'fetchTargetRanges': ftRanges}

            #[2-3]: Clear Pending Queues
            fPending.clear()

    def __processDataFetchRequestQueue(self):
        #[1]: Instances
        md           = self.__marketData
        rqIB_mdFetch = self.__requestQueues_ib['marketDataFetch']

        #[2]: Queue Check
        if not rqIB_mdFetch: return

        #[3]: Queue Handling
        queue = rqIB_mdFetch.popleft()
        requester  = queue['requester']
        requestID  = queue['requestID']
        symbol     = queue['symbol']
        target     = queue['target']
        fetchRange = queue['fetchRange']

        #[4]: Symbol Check
        md_symbol = md.get(symbol, None)
        if md_symbol is None:
            self.ipcA.sendFARR(targetProcess  = requester, 
                               functionResult = {'result': 'SNF', #SNF: Symbol Not Found
                                                 'data':   None}, 
                               requestID      = requestID, 
                               complete       = True)
            return

        #[5]: Data Availability Check #kline
        dataAvailable = False
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
            self.ipcA.sendFARR(targetProcess  = requester, 
                               functionResult = {'result': 'DNA', #DNA: Data Not Available
                                                 'data':   None}, 
                               requestID      = requestID, 
                               complete       = True)
            return 

        #[6]: Data Fetch Attempt From DB
        try:
            fr_beg, fr_end = fetchRange
            #[6-1]: Kline
            if target == 'kline':
                pgQuery = """SELECT t_open, t_close, p_open, p_high, p_low, p_close, ntrades, v, q, v_tb, q_tb, ktype
                             FROM klines
                             WHERE symbol = %s AND to_timestamp(%s) <= time AND time <= to_timestamp(%s)
                             ORDER BY time ASC;
                          """
                self.__pg_cursor.execute(pgQuery, (symbol, fr_beg, fr_end))
                klines_DB = self.__pg_cursor.fetchall()
                fetchedData = [kl[:11]+(True, kl[11]) for kl in klines_DB]

            #[6-2]: Depth
            elif target == 'depth':
                pgQuery = """SELECT t_open, t_close, bids5, bids4, bids3, bids2, bids1, bids0, asks0, asks1, asks2, asks3, asks4, asks5, dtype
                             FROM depths
                             WHERE symbol = %s AND to_timestamp(%s) <= time AND time <= to_timestamp(%s)
                             ORDER BY time ASC;
                          """
                self.__pg_cursor.execute(pgQuery, (symbol, fr_beg, fr_end))
                depths_DB = self.__pg_cursor.fetchall()
                fetchedData = [depth[:14]+(True, depth[14]) for depth in depths_DB]

            #[6-3]: AggTrade
            elif target == 'aggTrade':
                pgQuery = """SELECT t_open, t_close, quantity_buy, quantity_sell, ntrades_buy, ntrades_sell, notional_buy, notional_sell, attype
                             FROM aggtrades
                             WHERE symbol = %s AND to_timestamp(%s) <= time AND time <= to_timestamp(%s)
                             ORDER BY time ASC;
                          """
                self.__pg_cursor.execute(pgQuery, (symbol, fr_beg, fr_end))
                aggTrades_DB = self.__pg_cursor.fetchall()
                fetchedData = [aggTrade[:8]+(True, aggTrade[8]) for aggTrade in aggTrades_DB]

            #[6-4]: Result Dispatch
            self.ipcA.sendFARR(targetProcess  = requester, 
                               functionResult = {'result':     'SDF', #SDF: Successful Data Fetch
                                                 'data':       fetchedData, 
                                                 'fetchRange': fetchRange}, 
                               requestID      = requestID, 
                               complete       = True)
        except Exception as e:
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
            self.ipcA.sendFARR(targetProcess  = requester, 
                               functionResult = {'result': 'UEO', #UEO: Unexpected Error Occurred
                                                 'data':   None}, 
                               requestID      = requestID, 
                               complete       = True)
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
                address, newValue = queues_ader.popleft()
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
                        ad['positions_dbID'][address[2]] = position_dbID

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
                localID, tradeLog = queues_tlar.popleft()

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
                localID, timestamp, periodicReport = queues_prur.popleft()

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
                queue = self.__neuralNetworkConnectionDataUpdateRequestQueues.popleft()
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
                queue = self.__neuralNetworkTrainingLogAppendRequestQueues.popleft()
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
                queue = self.__neuralNetworkPerformanceTestLogAppendRequestQueues.popleft()
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
        #[1]: Source Check
        if requester != 'BINANCEAPI': return

        #[2]: Instances
        md_symbol = self.__marketData.get(symbol, None)
        pgConn    = self.__pg_connection
        pgCursor  = self.__pg_cursor
        func_sendPRDEDIT = self.ipcA.sendPRDEDIT
        func_sendFAR     = self.ipcA.sendFAR
        
        #[3]: #Symbol does not exist within the database (This is a new symbol)
        if md_symbol is None:
            #[3-1]: Symbol Market Data
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
                         'info_server':               info,
                         '_stream_klines':            {'klines':    list(), 'range': None, 'firstOpenTS': None},
                         '_stream_depths':            {'depths':    list(), 'range': None, 'firstOpenTS': None},
                         '_stream_aggTrades':         {'aggTrades': list(), 'range': None, 'firstOpenTS': None},
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
                          aggTrades_availableRanges
                         ) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                          json.dumps(md_symbol['aggTrades_availableRanges']) if md_symbol['aggTrades_availableRanges'] is not None else None
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

        #[4]: Symbol already exists within the database
        else:
            #[4-1]: Update Server Information
            md_symbol['info_server'] = info

            #[3-2]: Updates Check
            updated = set()
            #---[3-2-1]: Precisions - 0b1
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

            #[3-3]: DB Update
            try:
                #[3-3-1]: Precisions
                if 'precisions' in updated:
                    pgQuery = "UPDATE descriptors SET precisions = %s WHERE symbol = %s"
                    params  = (json.dumps(md_symbol['precisions']), 
                               symbol)
                    pgCursor.execute(pgQuery, params)
                #[3-3-2]: Finally, Commit
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

            #[3-4]: Announce the updated info
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
                
        #[5]: Send First Open Timestamps Search Requests If Needed
        for target in ('kline', 'depth', 'aggTrade'):
            if md_symbol[f'{target}_firstOpenTS'] is not None: continue
            func_sendFAR(targetProcess  = 'BINANCEAPI', 
                         functionID     = 'getFirstOpenTS', 
                         functionParams = {'symbol': symbol, 
                                           'target': target},
                         farrHandler    = self.__farr_getFirstOpenTS)
                
    def __far_onCurrencyInfoUpdate(self, requester, symbol, infoUpdates):
        #[1]: Source Check
        if requester != 'BINANCEAPI':
            return
        
        #[2]: Instances
        md_symbol = self.__marketData[symbol]
        func_sendPRDEDIT = self.ipcA.sendPRDEDIT
        func_sendFAR     = self.ipcA.sendFAR
        baseAddress_prd = ('CURRENCIES', symbol, 'info_server')
        baseAddress_far = ('info_server',)
        
        #[3]: Market Currency Data Update & Announcement
        for infoUpdate in infoUpdates:
            #[3-1]: Instances
            updateID    = infoUpdate['id']
            updateValue = infoUpdate['value']

            #[3-2]: Target Access
            target = md_symbol['info_server']
            for key in updateID[:-1]:
                target = target[key]

            #[3-3]: Data Update
            target[updateID[-1]] = updateValue

            #[3-4]: Announcement
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
    
    def __farr_getFirstOpenTS(self, responder, requestID, functionResult):
        #[1]: Read the function result
        symbol      = functionResult['symbol']
        target      = functionResult['target']
        firstOpenTS = functionResult['firstOpenTS']

        #[2]: Instances
        rqOB      = self.__requestQueues_ob
        md_symbol = self.__marketData[symbol]
        pgConn    = self.__pg_connection
        pgCursor  = self.__pg_cursor
        func_sendPRDEDIT = self.ipcA.sendPRDEDIT
        func_sendFAR     = self.ipcA.sendFAR

        #[3]: Save the found firstOpenTS
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

        #[4]: Currency info update on PRD-GUI via PRD and notification by FAR
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
        
        #[5]: Send Fetch Request If Possible
        stream_target = md_symbol[f'_stream_{target}s']
        if stream_target['firstOpenTS'] is not None:
            rqOB['marketDataFetch_pending'][target].add(symbol)

    def __far_onKlineStreamReceival(self, requester, symbol, kline):
        #[1]: Source Check
        if requester != 'BINANCEAPI': return

        #[2]: Streamed Data Processing
        self.__onDataStreamReceival(symbol = symbol, dataType = 'kline', streamedData = kline)

    def __far_onDepthStreamReceival(self, requester, symbol, depth):
        #[1]: Source Check
        if requester != 'BINANCEAPI': return
        
        #[2]: Streamed Data Processing
        self.__onDataStreamReceival(symbol = symbol, dataType = 'depth', streamedData = depth)

    def __far_onAggTradeStreamReceival(self, requester, symbol, aggTrade):
        #[1]: Source Check
        if requester != 'BINANCEAPI': return
        
        #[2]: Streamed Data Processing
        self.__onDataStreamReceival(symbol = symbol, dataType = 'aggTrade', streamedData = aggTrade)

    def __farr_getDataFetchRequestResult(self, responder, requestID, functionResult):
        #[1]: Source Check
        if responder != 'BINANCEAPI':
            return

        #[2]: Instances
        rqOB = self.__requestQueues_ob
        fr_target  = functionResult['target']
        fActive    = rqOB['marketDataFetch_active'][fr_target]
        fResponses = rqOB['marketDataFetch_responses']

        #[3]: Request Check
        request = fActive.get(requestID, None)
        if request is None:
            return
        
        #[4]: Buffer Update
        response = {'target':         fr_target,
                    'requestID':      requestID,
                    'functionResult': functionResult}
        fResponses.append(response)

        #[5]: Fetch Pause Request
        if 50 <= len(fResponses) and not self.__marketDataFetch_pauseRequested:
            self.ipcA.sendFAR(targetProcess  = 'BINANCEAPI',
                              functionID     = 'pauseMarketDataFetch',
                              functionParams = None, 
                              farrHandler    = None)
            self.__marketDataFetch_pauseRequested = True

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
                                                          1 if analysisExport else 0,
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
    def __far_fetchMarketData(self, requester, requestID, symbol, target, fetchRange):
        #[1]: Generate Queue
        queue = {'requester':  requester,
                 'requestID':  requestID,
                 'symbol':     symbol,
                 'target':     target,
                 'fetchRange': fetchRange}
        
        #[2]: Append Queue
        self.__requestQueues_ib['dataFetch'].append(queue)
    
    def __far_registerCurrecnyInfoSubscription(self, requester, symbol):
        #[1]: Instances
        md = self.__marketData

        #[2]: Symbol Check
        md_symbol = md.get(symbol, None)
        if md_symbol is None:
            return
        
        #[3]: Subscription Add
        md_symbol['_subscribers'].add(requester)

        #[4]: Symbol Market Data Announcement
        md_symbol_announce = {k: md_symbol[k] for k in _MARKETDATA_ANNOUNCEMENT_KEYS}
        self.ipcA.sendPRDEDIT(targetProcess = requester, 
                              prdAddress    = ('CURRENCIES', symbol), 
                              prdContent    = md_symbol_announce)
        self.ipcA.sendFAR(targetProcess  = requester, 
                          functionID     = 'onCurrenciesUpdate', 
                          functionParams = {'updatedContents': [{'symbol': symbol, 'id': '_ONFIRSTSUBSCRIPTION'},]}, 
                          farrHandler    = None)
    
    def __far_unregisterCurrecnyInfoSubscription(self, requester, symbol):
        #[1]: Instances
        md = self.__marketData

        #[2]: Symbol Check
        md_symbol = md.get(symbol, None)
        if md_symbol is None:
            return
        
        #[3]: Subscription Removal
        if requester in md_symbol['_subscribers']: 
            md_symbol['_subscribers'].remove(requester)
            self.ipcA.sendPRDREMOVE(targetProcess = requester, 
                                    prdAddress    = ('CURRENCIES', symbol))
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