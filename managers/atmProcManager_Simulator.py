#ATM Modules
import atmEta_IPC
from managers.workers_simulator import apw_simulator_simulation

#Python Modules
import time
import torch
import gc
from collections import deque

#Constants
_IPC_THREADTYPE_MT         = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT         = atmEta_IPC._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = atmEta_IPC._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = atmEta_IPC._FAR_INVALIDFUNCTIONID

class Simulator:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA, simulatorIndex):
        #IPC Assistance
        self.ipcA = ipcA
        
        #Simulator ID
        self.simulatorIndex = simulatorIndex

        #Simulation Control
        self.__activation  = False
        self.__simulations = dict()
        self.__simulations_currentlyHandling = None
        self.__simulations_handlingQueue     = deque()
        self.__simulations_removalQueue      = deque()

        #Project Path
        self.path_project = path_project

        #FAR Registration
        #---SIMULATIONMANAGER
        self.ipcA.addFARHandler('setActivation',    self.__far_setActivation,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('addSimulation',    self.__far_addSimulation,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('removeSimulation', self.__far_removeSimulation, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

        #Process Control
        self.__processLoopContinue = True
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Process Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        while self.__processLoopContinue:
            #Process any existing FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()
            #Process Simulations
            self.__processSimulation()
            self.__processSimulationRemovalQueue()
            #Process Loop Control
            if self.__loopSleepDeterminer(): 
                time.sleep(0.001)
    
    def __loopSleepDeterminer(self):
        #[1]: Check Activation
        if not self.__activation:
            return True
        
        #[2]: Check Simulation Status
        sim = self.__simulations.get(self.__simulations_currentlyHandling, None)
        if sim is not None and sim.isProcessing():
            return False
        
        #[3]: If Reached Here, Means System Is Not Busy. Return True
        return True
    
    def terminate(self, requester):
        self.__processLoopContinue = False
    #Manager Process Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Internal Functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __processSimulation(self):
        #[1]: Activation Check
        if not self.__activation: return

        #[2]: Currently Handling Simulation Check
        if self.__simulations_currentlyHandling is None and self.__simulations_handlingQueue:
            simCode = self.__simulations_handlingQueue.popleft()
            sim     = self.__simulations[simCode]
            sim.start()
            self.__simulations_currentlyHandling = simCode

        #[3]: Simulation Handling
        simCode = self.__simulations_currentlyHandling
        sim     = self.__simulations.get(simCode, None)
        if sim is None:
            return
        sim.process()

        #[4]: Simulations Status Check
        for simCode, sim in self.__simulations.items():
            sim_status = sim.getStatus()
            #---[4-1]: Error Handling
            if sim_status == 'ERROR':
                self.__simulations_removalQueue.append(simCode)
                if self.__simulations_currentlyHandling == simCode: 
                    self.__simulations_currentlyHandling = None

            #---[4-2]: Completion Handling
            elif sim_status == 'COMPLETED':
                self.__simulations_removalQueue.append(simCode)
                self.__simulations_currentlyHandling = None

    def __processSimulationRemovalQueue(self):
        sims    = self.__simulations
        rQueue  = self.__simulations_removalQueue
        removed = False
        while rQueue:
            simCode = rQueue.popleft()
            del sims[simCode]
            removed = True
        if removed:
            gc.collect()
            torch.cuda.empty_cache()
    #Manager Internal Functions END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #FAR Handlers -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<SIMULATIONMANAGER>
    def __far_setActivation(self, requester, activation):
        #[1]: Source Check
        if requester != 'SIMULATIONMANAGER':
            return

        #[2]: Activation Update
        self.__activation = activation

        #[3]: Current Target Simulation Update
        ctSim = self.__simulations.get(self.__simulations_currentlyHandling, None)
        if ctSim is None:
            return
        ctSim.setActivation(activation = activation)
    
    def __far_addSimulation(self, requester, simulationCode, simulationRange, analysisExport, assets, positions, currencyAnalysisConfigurations, tradeConfigurations, creationTime):
        #[1]: Requester Check
        if requester != 'SIMULATIONMANAGER': return
        
        #[2]: Simulation Generation
        sim = apw_simulator_simulation.Simulation(path_project                   = self.path_project,
                                                  simulatorIndex                 = self.simulatorIndex,
                                                  ipcA                           = self.ipcA,
                                                  simulationCode                 = simulationCode, 
                                                  simulationRange                = simulationRange, 
                                                  analysisExport                 = analysisExport, 
                                                  assets                         = assets, 
                                                  positions                      = positions, 
                                                  currencyAnalysisConfigurations = currencyAnalysisConfigurations, 
                                                  tradeConfigurations            = tradeConfigurations, 
                                                  creationTime                   = creationTime)
        self.__simulations[simulationCode] = sim
        self.__simulations_handlingQueue.append(simulationCode)
    
    def __far_removeSimulation(self, requester, simulationCode):
        #[1]: Requester Check
        if requester != 'SIMULATIONMANAGER': return

        #[2]: Simulation Removal
        sims   = self.__simulations
        hQueue = self.__simulations_handlingQueue
        rQueue = self.__simulations_removalQueue
        if simulationCode in sims:
            sim = sims[simulationCode]
            sim_status = sim.getStatus()
            #[2-1]: Queue Update
            rQueue.append(simulationCode)
            if sim_status == 'QUEUED':
                hQueue.remove(simulationCode)
            #[2-2]: Currently Handling Target Update
            if self.__simulations_currentlyHandling == simulationCode: 
                self.__simulations_currentlyHandling = None

        #[3]: Response 
        self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                          functionID     = 'removeSimulationData', 
                          functionParams = {'simulationCode': simulationCode}, 
                          farrHandler    = None)
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------