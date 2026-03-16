#ATM Modules
import atmEta_IPC
import atmEta_Auxillaries
import atmEta_Constants
from managers.workers_datamanager import apw_dm_market, apw_dm_account, apw_dm_simulation, apw_dm_neuralnetwork

#Python Modules
import time
import os
import termcolor
import sqlite3
import json
import traceback
import subprocess
import shutil
import pprint
import platform
import socket
from collections     import deque
from datetime        import datetime, timedelta, timezone
from psycopg2.pool   import ThreadedConnectionPool
from psycopg2.extras import execute_values, execute_batch

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

PGSQLDOCKERCONTAINERNAME = 'atmEta'

class DataManager:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA):
        print(termcolor.colored("   Initializing", 'green'), termcolor.colored("DATAMANAGER", 'light_blue'), termcolor.colored("-----------------------------------------------------------------------------------------------------------------------", 'green'))
        
        #[1]: IPC Assistance
        self.ipcA = ipcA

        #[2]: Paths
        path_dbFolder = os.path.join(path_project, 'data', 'db')
        if not os.path.isdir(path_dbFolder): os.mkdir(path_dbFolder)
        self.path_project  = path_project
        self.path_dbFolder = path_dbFolder
        
        #[3]: Manager Configuration
        self.__config_DataManager = None
        self.__readDataManagerConfig()
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CONFIGURATION', prdContent = self.__config_DataManager.copy())

        #[4]: Setup Docker (PostgreSQL)
        pgPortNumber = self.__setupDocker()

        #[5]: Workers Initialization & Start
        dmConfig = self.__config_DataManager
        self.__workers = {'market':        apw_dm_market.Worker(path_project        = path_project, dmConfig = dmConfig, ipcA = ipcA, portNumber = pgPortNumber),
                          'account':       apw_dm_account.Worker(path_project       = path_project, dmConfig = dmConfig, ipcA = ipcA),
                          'simulation':    apw_dm_simulation.Worker(path_project    = path_project, dmConfig = dmConfig, ipcA = ipcA),
                          'neuralNetwork': apw_dm_neuralnetwork.Worker(path_project = path_project, dmConfig = dmConfig, ipcA = ipcA)}
        for worker in self.__workers.values():
            worker.start()
        print("    * Workers Initialized and Started!")
        while any(not worker.initialTaskComplete() for worker in self.__workers.values()):
            time.sleep(0.01)
        print("    * Workers Initial Tasks Complete!")

        #[6]: FAR Registration
        self.ipcA.addFARHandler('updateConfiguration', self.__far_updateConfiguration, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

        #[7]: Process Control
        self.__processLoopContinue = True

        print(termcolor.colored("   DATAMANAGER", 'light_blue'), termcolor.colored("Initialization Complete! -----------------------------------------------------------------------------------------------------------", 'green'))
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    


    
    #Manager Process Functions ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        while self.__processLoopContinue:
            #Process any exsiting FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()
            
            #Loop Sleep
            time.sleep(0.001)
    
    def terminate(self, requester):
        for worker in self.__workers.values():
            worker.terminate()
        self.__processLoopContinue = False
    #Manager Process Functions END --------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Docker Setup -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
                               "-e", "POSTGRES_HOST_AUTH_METHOD=scram-sha-256",
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
    #Docker Setup -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Manager Internal Functions -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
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

    def __logger(self, message, logType, color):
        if not self.__config_DataManager[f'print_{logType}']:
            return
        time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
        print(termcolor.colored(f"[DATAMANAGER-{time_str}] {message}", color))
    #Manager Internal Functions END -------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #FAR & FARR Handlers ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __far_updateConfiguration(self, requester, requestID, newConfiguration):
        #[1]: Source Check
        if requester != 'GUI':
            return {'result':        True, 
                    'message':       "Invalid Requester!", 
                    'configuration': None}
        
        #[2]: Configuration Update
        config = self.__config_DataManager
        config['print_Update']  = newConfiguration['print_Update']
        config['print_Warning'] = newConfiguration['print_Warning']
        config['print_Error']   = newConfiguration['print_Error']
        self.__saveDataManagerConfig()

        #[3]: Update Announcement
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                              prdAddress    = 'CONFIGURATION', 
                              prdContent    = config)
        return {'result':        True, 
                'message':       "Configuration Successfully Updated!", 
                'configuration': config}
    #FAR & FARR Handlers END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------