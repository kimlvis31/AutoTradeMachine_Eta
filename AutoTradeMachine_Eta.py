#ATM Modules
import multiprocessing.shared_memory
import atmEta_IPC
from managers import atmProcManager_GUI, atmProcManager_BinanceAPI, atmProcManager_DataManager, atmProcManager_TradeManager, atmProcManager_SimulationManager, atmProcManager_Analyzer, atmProcManager_Simulator, atmProcManager_NeuralNetworkManager

#Python Modules
import multiprocessing
import os
import time
import termcolor
import psutil
import shutil
import colorama
import json
from datetime import datetime, timedelta, timezone

#Paths
path_PROJECT = os.path.dirname(os.path.realpath(__file__))
path_DRIVE   = path_PROJECT.split("\\")[0]

#Program Config
#---Configuration File Read
config_dir = os.path.join(path_PROJECT, 'configs', 'programConfig.config')
try:
    with open(config_dir, 'r') as f:
        config_loaded = json.load(f)
except:
    config_loaded = dict()
#---Configuration Tests
#------SAC (Singular Application Check) Max Attempts
sacMaxAttempts = config_loaded.get('SACMaxAttempts', 10)
if not isinstance(sacMaxAttempts, int): sacMaxAttempts = 10
if not 1 <= sacMaxAttempts:             sacMaxAttempts = 10
#------SAC (Singular Application Check) Interval
sacInterval_s = config_loaded.get('SACInterval_s', 0.2)
if type(sacInterval_s) not in (float, int): sacInterval_s = 0.1
if not (0.0 < sacInterval_s):               sacInterval_s = 0.1
#------Number of Analyzers
nAnalyzers = config_loaded.get('nAnalyzers', 1)
if not isinstance(nAnalyzers, int): nAnalyzers = 1
if not 1 <= nAnalyzers:             nAnalyzers = 1
#------Number of Simulators
nSimulators = config_loaded.get('nSimulators', 1)
if not isinstance(nSimulators, int): nSimulators = 1
if not 1 <= nSimulators:             nSimulators = 1
#------Finally
programConfig = {'SACMaxAttempts': sacMaxAttempts,
                 'SACInterval_s':  sacInterval_s,
                 'nAnalyzers':     nAnalyzers,
                 'nSimulators':    nSimulators}
#---Configuration Save
with open(config_dir, 'w') as f:
    json.dump(programConfig, f, indent=4)

#ATM Constants
_PROCESSES_SUBS = ['GUI', 'BINANCEAPI', 'DATAMANAGER', 'TRADEMANAGER', 'SIMULATIONMANAGER', 'NEURALNETWORKMANAGER']
if (True): #nAnalyzers and nSimulators Determination
    nRem = max(os.cpu_count()-len(_PROCESSES_SUBS)-2, 0)
    nRem_Analyzers  = min(nRem,                programConfig['nAnalyzers']-1)
    nRem_Simulators = min(nRem-nRem_Analyzers, programConfig['nSimulators']-1)
    nAnalyzers  = 1+nRem_Analyzers
    nSimulators = 1+nRem_Simulators
_PROCESSES_ANALYZERS  = [f"ANALYZER{analyzerIndex}"   for analyzerIndex  in range (0, nAnalyzers)]
_PROCESSES_SIMULATORS = [f"SIMULATOR{simulatorIndex}" for simulatorIndex in range (0, nSimulators)]
_SYS_SINGULARAPPLICATIONCHECKMAXATTEMPTS = programConfig['SACMaxAttempts']
_SYS_SINGULARAPPLICATIONCHECKINTERVAL    = programConfig['SACInterval_s']
_SYSREQ_MINPROCESSORTHREADS  = 8
_SYSREQ_MINTOTALMEMORY_GB    = 12.00
_SYSREQ_MINTOTALDISKSPACE_GB = 256.00
_SYSREQ_MINFREEDISKSPACE_GB  = 64.00
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

#PROCESSES ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def managerProcess(processType, ipc_Queues, **puParams):
    ipcA = atmEta_IPC.IPCAssistant(processType, ipc_Queues)

    #Wait until manager initialization command is given by MAIN
    while (ipcA.getPRD('MAIN', '_INITIALIZEMANAGER') != True): time.sleep(0.001)
    ipcA.removePRD(targetProcess = 'MAIN', prdAddress = '_INITIALIZEMANAGER')
    #Initialize the process manager
    if   (processType == 'GUI'):                  manager = atmProcManager_GUI.procManager_GUI(path_PROJECT,                                   ipcA)
    elif (processType == 'BINANCEAPI'):           manager = atmProcManager_BinanceAPI.procManager_BinanceAPI(path_PROJECT,                     ipcA)
    elif (processType == 'DATAMANAGER'):          manager = atmProcManager_DataManager.procManager_DataManager(path_PROJECT,                   ipcA)
    elif (processType == 'TRADEMANAGER'):         manager = atmProcManager_TradeManager.procManager_TradeManager(path_PROJECT,                 ipcA, _PROCESSES_ANALYZERS)
    elif (processType == 'SIMULATIONMANAGER'):    manager = atmProcManager_SimulationManager.procManager_SimulationManager(path_PROJECT,       ipcA, _PROCESSES_SIMULATORS)
    elif (processType == 'NEURALNETWORKMANAGER'): manager = atmProcManager_NeuralNetworkManager.procManager_NeuralNetworkManager(path_PROJECT, ipcA)
    elif (processType.startswith('ANALYZER')):    manager = atmProcManager_Analyzer.procManager_Analyzer(path_PROJECT,                         ipcA, int(processType[8:]))
    elif (processType.startswith('SIMULATOR')):   manager = atmProcManager_Simulator.procManager_Simulator(path_PROJECT,                       ipcA, int(processType[9:]))

    #---Register Manager Termination Function
    ipcA.addFARHandler('TERMINATEMANAGER', manager.terminate, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

    #Send initialization completion signal via PRD
    ipcA.sendPRDEDIT(targetProcess = 'MAIN', prdAddress = '_MANAGERINITIALIZED', prdContent = True)

    #Wait until process loop start command is given by MAIN
    while (ipcA.getPRD(processName = 'MAIN', prdAddress = '_STARTPROCESSLOOP') != True): time.sleep(0.001)
    ipcA.removePRD(targetProcess = 'MAIN', prdAddress = '_STARTPROCESSLOOP')

    #Start the manager process
    manager.start()

    #Terminate IPCA (Necessary as it has its own thread running)
    ipcA.terminate()
#PROCESSES END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



#MAIN -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def far_terminateProgram(*functionParams):
    global ipcA
    global continueLoop
    for processName   in _PROCESSES_SUBS:       ipcA.sendFAR(targetProcess = processName,   functionID = 'TERMINATEMANAGER', functionParams = None, farrHandler = None)
    for analyzerName  in _PROCESSES_ANALYZERS:  ipcA.sendFAR(targetProcess = analyzerName,  functionID = 'TERMINATEMANAGER', functionParams = None, farrHandler = None)
    for simulatorName in _PROCESSES_SIMULATORS: ipcA.sendFAR(targetProcess = simulatorName, functionID = 'TERMINATEMANAGER', functionParams = None, farrHandler = None)
    ipcA.terminate()
    continueLoop = False

#'__main__' Function
if __name__ == "__main__":
    #Print out program start time
    t_programStart = time.time()
    print(termcolor.colored("<AUTO TRADE MACHINE - ETA>", 'light_cyan'))
    print(f"Program Start Time: {datetime.fromtimestamp(t_programStart).strftime("%Y-%m-%d %H:%M")} LOCAL")
    print(f"                    {datetime.fromtimestamp(t_programStart, tz = timezone.utc).strftime("%Y-%m-%d %H:%M")} UTC")

    #Console Colorama Initialization
    colorama.init(autoreset = True)

    #Singular Application Instance Check
    saiCheck_nAttempts = 0
    programIDMemory = None
    while (saiCheck_nAttempts < _SYS_SINGULARAPPLICATIONCHECKMAXATTEMPTS):
        try:    programIDMemory = multiprocessing.shared_memory.SharedMemory(name = "ATMETA_PROGRAMID", create = True, size = 4096); break
        except: saiCheck_nAttempts += 1; time.sleep(_SYS_SINGULARAPPLICATIONCHECKINTERVAL)
    if (programIDMemory == None): print(termcolor.colored("The Application is Already Running, Terminating...", 'light_red')); exit()

    #Main Process Loop Control
    global continueLoop
    continueLoop = True

    #Verify System Requirements & Read Program Config File
    try:
        print(termcolor.colored("\n[1/4] Verifying System Requirements...", 'green'))
        verified = True

        #Number of Processor Threads
        sys_nProcessorThreads = os.cpu_count()
        cmt = f"Number of Processor Threads: {sys_nProcessorThreads:d} [{_SYSREQ_MINPROCESSORTHREADS:d} <= ?]"
        if (_SYSREQ_MINPROCESSORTHREADS <= sys_nProcessorThreads): print(" *", termcolor.colored("<PASS>", 'light_green'), cmt)
        else:                                                      print(" *", termcolor.colored("<FAIL>", 'light_red'),   cmt); verified = False

        #Memory
        sys_memory = psutil.virtual_memory()
        sys_memory_total_GB = round(sys_memory.total/pow(1024,3), 2)
        cmt = f"Total System Memory: {sys_memory_total_GB:.2f} GB [{_SYSREQ_MINTOTALMEMORY_GB:.2f} GB <= ?]"
        if (_SYSREQ_MINTOTALMEMORY_GB <= sys_memory_total_GB): print(" *", termcolor.colored("<PASS>", 'light_green'), cmt)
        else:                                                  print(" *", termcolor.colored("<FAIL>", 'light_red'),   cmt); verified = False

        #Disk Space
        diskUsage = shutil.disk_usage(path_DRIVE)
        sys_diskSpace_total_GB = round(diskUsage.total/pow(1024,3), 2)
        cmt = f"Total Disk Space: {sys_diskSpace_total_GB:.2f} GB [{_SYSREQ_MINTOTALDISKSPACE_GB:.2f} GB <= ?]"
        if (_SYSREQ_MINTOTALDISKSPACE_GB <= sys_diskSpace_total_GB): print(" *", termcolor.colored("<PASS>", 'light_green'), cmt)
        else:                                                        print(" *", termcolor.colored("<FAIL>", 'light_red'),   cmt); verified = False
        sys_diskSpace_free_GB  = round(diskUsage.free/pow(1024,3), 2)
        cmt = f"Free Disk Space: {sys_diskSpace_free_GB:.2f} GB [{_SYSREQ_MINFREEDISKSPACE_GB:.2f} GB <= ?]"
        if (_SYSREQ_MINFREEDISKSPACE_GB <= sys_diskSpace_free_GB): print(" *", termcolor.colored("<PASS>", 'light_green'), cmt)
        else:                                                      print(" *", termcolor.colored("<FAIL>", 'light_red'),   cmt); verified = False

        if (verified == True):
            print(f" * {len(_PROCESSES_ANALYZERS)} Analyzers are to be initialized")
            print(f" * {len(_PROCESSES_SIMULATORS)} Simulators are to be initialized")
            print(termcolor.colored("[1/4] System Requirements Verification Complete!", 'light_green'))
        else: print(termcolor.colored("[1/4] System Requirements Not Met, Terminating...", 'light_red')); exit()
    except Exception as e: print(termcolor.colored("[1/4] An unexpected error ocurred while attempting to verify system requirements\n *", 'red'), termcolor.colored(e, 'red')); exit()

    #[2/4]: IPC Preparations
    try:
        print(termcolor.colored("\n[2/4] Preparing IPC Connections...", 'green'))
        #Multiprocessing Freeze Support
        multiprocessing.freeze_support()
        print(" * Multiprocessing Freeze Support Successful")
        #IPC Queues Preparation
        ipc_Queues = dict()
        ipc_Queues['MAIN'] = multiprocessing.Queue()
        for process       in _PROCESSES_SUBS:       ipc_Queues[process]       = multiprocessing.Queue()
        for analyzerName  in _PROCESSES_ANALYZERS:  ipc_Queues[analyzerName]  = multiprocessing.Queue()
        for simulatorName in _PROCESSES_SIMULATORS: ipc_Queues[simulatorName] = multiprocessing.Queue()
        print(" * Multiprocessing Queues Generated")
        #MAIN IPC Assistant Initialization
        global ipcA
        ipcA = atmEta_IPC.IPCAssistant('MAIN', ipc_Queues)
        ipcA.addFARHandler('TERMINATEPROGRAM', far_terminateProgram, executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        print(" * MAIN Process IPCA Initialized")
        #Completion Comment
        print(termcolor.colored("[2/4] IPC Connections Preparations Complete!", 'light_green'))
    except Exception as e: print(termcolor.colored("[2/4] An unexpected error ocurred while attempting to prepare IPC connections\n *", 'red'), termcolor.colored(e, 'red')); exit()

    #[3/4]Processes Generation & Start
    try:
        print(termcolor.colored("\n[3/4] Generating and Starting Processes...", 'green'))
        #Processes Generation
        processes = dict()
        for processName   in _PROCESSES_SUBS:       processes[processName]   = multiprocessing.Process(target = managerProcess, args = (processName,   ipc_Queues)); processes[processName].start();   print(f" * {processName} Process Generated")
        for analyzerName  in _PROCESSES_ANALYZERS:  processes[analyzerName]  = multiprocessing.Process(target = managerProcess, args = (analyzerName,  ipc_Queues)); processes[analyzerName].start();  print(f" * Analyzer Process '{analyzerName}' Generated")
        for simulatorName in _PROCESSES_SIMULATORS: processes[simulatorName] = multiprocessing.Process(target = managerProcess, args = (simulatorName, ipc_Queues)); processes[simulatorName].start(); print(f" * Simulator Process '{simulatorName}' Generated")
        #Completion Comment
        print(termcolor.colored("[3/4] Processes Generation and Start Complete!", 'light_green'))
    except Exception as e: print(termcolor.colored("[3/4] An unexpected error while attempting to generate and start processes\n *", 'red'), termcolor.colored(e, 'red')); exit()

    #[4/4]Initialize Generation & Start
    try:
        print(termcolor.colored("\n[4/4] Initializing Process Managers...", 'green'))
        #Send manager initialization command via PRD and wait until it completes
        for processName in _PROCESSES_SUBS:
            ipcA.sendPRDEDIT(targetProcess = processName, prdAddress = '_INITIALIZEMANAGER', prdContent = True)
            while (ipcA.getPRD(processName = processName, prdAddress = '_MANAGERINITIALIZED') != True): time.sleep(0.001)
            ipcA.removePRD(targetProcess = processName, prdAddress = '_MANAGERINITIALIZED')
            print(f" * Process Manager '{processName}' Initialized")
        for analyzerName in _PROCESSES_ANALYZERS:
            ipcA.sendPRDEDIT(targetProcess = analyzerName, prdAddress = '_INITIALIZEMANAGER', prdContent = True)
            while (ipcA.getPRD(processName = analyzerName, prdAddress = '_MANAGERINITIALIZED') != True): time.sleep(0.001)
            ipcA.removePRD(targetProcess = analyzerName, prdAddress = '_MANAGERINITIALIZED')
            print(f" * Analyzer Process '{analyzerName}' Initialized")
        for simulatorName in _PROCESSES_SIMULATORS:
            ipcA.sendPRDEDIT(targetProcess = simulatorName, prdAddress = '_INITIALIZEMANAGER', prdContent = True)
            while (ipcA.getPRD(processName = simulatorName, prdAddress = '_MANAGERINITIALIZED') != True): time.sleep(0.001)
            ipcA.removePRD(targetProcess = simulatorName, prdAddress = '_MANAGERINITIALIZED')
            print(f" * Simulator Process '{simulatorName}' Initialized")
        #Completion Comment
        print(termcolor.colored("[4/4] Process Managers Initialization Complete!", 'light_green'))
    except Exception as e: print(termcolor.colored("[4/4] An unexpected error while attempting to initialize process managers\n *", 'red'), termcolor.colored(e, 'red')); exit()

    print(termcolor.colored("\n< *** PROGRAM START *** >\n", 'light_cyan'))

    #Send Process Loop Start command and set process termination variable via PRD
    for processName   in _PROCESSES_SUBS:       ipcA.sendPRDEDIT(targetProcess = processName,   prdAddress = '_STARTPROCESSLOOP', prdContent = True)
    for analyzerName  in _PROCESSES_ANALYZERS:  ipcA.sendPRDEDIT(targetProcess = analyzerName,  prdAddress = '_STARTPROCESSLOOP', prdContent = True)
    for simulatorName in _PROCESSES_SIMULATORS: ipcA.sendPRDEDIT(targetProcess = simulatorName, prdAddress = '_STARTPROCESSLOOP', prdContent = True)

    while (continueLoop == True):
        ipcA.processFARs()
        ipcA.processFARRs()
        time.sleep(0.001)

    #Termination
    print(termcolor.colored("<Terminating Program!>", 'cyan'))
    #---Join child processes
    for processName in _PROCESSES_SUBS:
        while (processes[processName].is_alive() == True): time.sleep(0.001)
        print(f" * Process '{processName}' Terminated")
    for analyzerName in _PROCESSES_ANALYZERS:
        while (processes[analyzerName].is_alive() == True): time.sleep(0.001)
        print(f" * Analyzer Process '{analyzerName}' Terminated")
    for simulatorName in _PROCESSES_SIMULATORS:
        while (processes[simulatorName].is_alive() == True): time.sleep(0.001)
        print(f" * Simulator Process '{simulatorName}' Terminated")
    print(termcolor.colored("<Program Terminated!>", 'cyan'))
    exit()
#MAIN END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------