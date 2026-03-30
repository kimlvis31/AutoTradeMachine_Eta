#ATM Modules
import atmEta_IPC
import atmEta_Analyzers
import atmEta_Auxillaries

#Python Modules
import time
import termcolor
import pprint

#Constants
_IPC_THREADTYPE_MT         = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT         = atmEta_IPC._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = atmEta_IPC._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = atmEta_IPC._FAR_INVALIDFUNCTIONID

class SimulationManager:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA, simulatorProcessNames):
        print(termcolor.colored("   Initializing", 'green'), termcolor.colored("SIMULATIONMANAGER", 'light_blue'), termcolor.colored("-----------------------------------------------------------------------------------------------------------------", 'green'))
        #IPC Assistance
        self.ipcA = ipcA
        
        #Project Path
        self.path_project = path_project

        #Simulators Central
        self.__simulators_central = {'nSimulators': len(simulatorProcessNames),
                                     'nSimulations_total':      {'total': 0},
                                     'nSimulations_QUEUED':     {'total': 0},
                                     'nSimulations_PROCESSING': {'total': 0},
                                     'nSimulations_PAUSED':     {'total': 0},
                                     'nSimulations_ERROR':      {'total': 0},
                                     'nSimulations_COMPLETED':  0,
                                     'simulatorActivation': dict()}
        self.__simulators_central_recomputeNumberOfSimulationsByStatus = False

        #Simulators
        self.__simulators = list()
        for simulatorProcessName in simulatorProcessNames:
            simulatorIndex = int(simulatorProcessName[9:])
            simulatorDescription = {'processName': simulatorProcessName,
                                    'allocated_simulationCodes': set()}
            self.__simulators.append(simulatorDescription)
            self.__simulators_central['nSimulations_total'][simulatorIndex]      = 0
            self.__simulators_central['nSimulations_QUEUED'][simulatorIndex]     = 0
            self.__simulators_central['nSimulations_PROCESSING'][simulatorIndex] = 0
            self.__simulators_central['nSimulations_PAUSED'][simulatorIndex]     = 0
            self.__simulators_central['nSimulations_ERROR'][simulatorIndex]      = 0
            self.__simulators_central['simulatorActivation'][simulatorIndex] = False
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'SIMULATORCENTRAL', prdContent = self.__simulators_central)

        #Simulations
        self.__simulations = dict()
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'SIMULATIONS', prdContent = self.__simulations)

        #FAR Registration
        #---GUI
        self.ipcA.addFARHandler('setSimulatorActivation', self.__far_setSimulatorActivation, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('addSimulation',          self.__far_addSimulation,          executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('removeSimulation',       self.__far_removeSimulation,       executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---SIMULATOR
        self.ipcA.addFARHandler('onSimulationUpdate',     self.__far_onSimulationUpdate,     executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onSimulationCompletion', self.__far_onSimulationCompletion, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---DATAMANAGER
        self.ipcA.addDummyFARHandler('onCurrenciesUpdate')

        #Process Control
        self.__processLoopContinue = True
        print(termcolor.colored("   SIMULATIONMANAGER", 'light_blue'), termcolor.colored("Initialization Complete! -----------------------------------------------------------------------------------------------------", 'green'))
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Process Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        dim_sims = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = 'SIMULATIONS')
        for simCode, sim in dim_sims.items():
            self.__simulations[simCode] = {'simulationRange':                sim['simulationRange'],
                                           'analysisExport':                 sim['analysisExport'],
                                           'assets':                         sim['assets'],
                                           'positions':                      sim['positions'],
                                           'currencyAnalysisConfigurations': sim['currencyAnalysisConfigurations'],
                                           'tradeConfigurations':            sim['tradeConfigurations'],
                                           'creationTime':                   sim['creationTime'],
                                           '_status':                        'COMPLETED',
                                           '_allocatedSimulator':            None,
                                           '_completion':                    None,
                                           '_simulationSummary':             sim['simulationSummary']}
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'SIMULATIONS', prdContent = self.__simulations)
        self.__simulators_central_recomputeNumberOfSimulationsByStatus = True
        while self.__processLoopContinue:
            #Process any existing FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()
            #Compute Number Of Currency Analysis By Status
            self.__computeNumberOfSimulationsByStatus()
            #Process Loop Control
            if self.__loopSleepDeterminer(): 
                time.sleep(0.001)

    def __loopSleepDeterminer(self):
        return True

    def terminate(self, requester):
        self.__processLoopContinue = False
    #Manager Process Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    
    #Manager Internal Functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __setSimulatorActivation(self, targetSimulatorIndex, activation):
        #[1]: Instances
        simCentral = self.__simulators_central
        sims       = self.__simulators
        func_sendPRDEDIT = self.ipcA.sendPRDEDIT
        func_sendFAR     = self.ipcA.sendFAR

        #[2]: Targets Determination
        if targetSimulatorIndex == 'all': tSimIdxes = list(range(simCentral['nSimulators']))
        else:                             tSimIdxes = [targetSimulatorIndex,]

        #[3]: Updates
        updatedContents = []
        for tSimIdx in tSimIdxes:
            activation_current = simCentral['simulatorActivation'][tSimIdx]
            if activation_current == activation:
                continue
            simCentral['simulatorActivation'][tSimIdx] = activation
            func_sendPRDEDIT(targetProcess = 'GUI', 
                             prdAddress    = ('SIMULATORCENTRAL', 'simulatorActivation', tSimIdx), 
                             prdContent    = activation)
            func_sendFAR(targetProcess  = sims[tSimIdx]['processName'], 
                         functionID     = 'setActivation', 
                         functionParams = {'activation': activation}, 
                         farrHandler    = None)
            updatedContents.append(('simulatorActivation', tSimIdx))

        #[4]: Result Dispatch
        if updatedContents: 
            func_sendFAR(targetProcess  = 'GUI', 
                         functionID     = 'onSimulatorCentralUpdate', 
                         functionParams = {'updatedContents': updatedContents}, 
                         farrHandler    = None)
        if targetSimulatorIndex == 'all':
            if activation: responseMessage = "All Simulators Are Now Active!"
            else:          responseMessage = "All Simulators Are Now Inactive!"
        else:
            if activation: responseMessage = f"SIMULATOR{targetSimulatorIndex} Is Now Active!"
            else:          responseMessage = f"SIMULATOR{targetSimulatorIndex} Is Now Inactive!"
        return {'responseOn': 'SIMULATORACTIVATION', 
                'result':     activation, 
                'message':    responseMessage}
    
    def __addSimulation(self, simulationCode, simulationRange, analysisExport, assets, positions, currencyAnalysisConfigurations, tradeConfigurations):
        #[1]: Instances
        simulations = self.__simulations
        simulators  = self.__simulators
        func_sendPRDEDIT = self.ipcA.sendPRDEDIT
        func_sendFAR     = self.ipcA.sendFAR
        simCode  = simulationCode
        simRange = simulationRange

        #[2]: Simulation Code Check & Determination
        if simCode is None:
            uSimIdx = 0
            while simCode is None:
                _simCode = f"USC{uSimIdx}" #USC: Unnamed Simulation Code
                if _simCode not in simulations: 
                    simCode = _simCode
                uSimIdx += 1
        if simCode in simulations:
            return {'responseOn': 'ADDREQUEST', 
                    'result':     False, 
                    'message':    f"Simulation '{simCode}' Add Failed. 'The Simulation Code Already Exists'"}

        #[3]: Simulation Range Check
        if not simRange[0] < simRange[1]:
            return {'responseOn': 'ADDREQUEST', 
                    'result':     False, 
                    'message':    f"Simulation '{simCode}' Add Failed. 'Check Simulation Range'"}

        #[4]: Simulator Allocation
        simIdx_allocate = None
        nSims_min       = min(len(simulators[simIdx]['allocated_simulationCodes']) for simIdx in range (len(simulators)))
        for simIdx in range (len(simulators)):
            if len(simulators[simIdx]['allocated_simulationCodes']) == nSims_min: 
                simIdx_allocate = simIdx
                break

        #[5]: Local Simulation Instance
        cTime = time.time()
        sim = {'simulationRange':                simulationRange,
               'analysisExport':                 analysisExport,
               'assets':                         assets,
               'positions':                      positions,
               'currencyAnalysisConfigurations': currencyAnalysisConfigurations,
               'tradeConfigurations':            tradeConfigurations,
               'creationTime':                   cTime,
               '_status':                        'QUEUED',
               '_allocatedSimulator':            simIdx_allocate,
               '_completion':                    None,
               '_simulationSummary':             None}
        simulations[simCode] = sim

        #[6]: Simulation Generation Command
        func_sendFAR(targetProcess = simulators[simIdx_allocate]['processName'],
                     functionID     = 'addSimulation',
                     functionParams = {'simulationCode':                 simCode,
                                       'simulationRange':                simulationRange,
                                       'analysisExport':                 analysisExport,
                                       'assets':                         assets,
                                       'positions':                      positions,
                                       'currencyAnalysisConfigurations': currencyAnalysisConfigurations,
                                       'tradeConfigurations':            tradeConfigurations,
                                       'creationTime':                   cTime},
                     farrHandler = None)
        simulators[simIdx_allocate]['allocated_simulationCodes'].add(simCode)

        #[7]: Announce Simulation Update
        func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('SIMULATIONS', simCode), prdContent = simulations[simCode])
        func_sendFAR(targetProcess = 'GUI', functionID = 'onSimulationUpdate', functionParams = {'updateType': 'ADDED', 'simulationCode': simCode}, farrHandler = None)

        #[8]: Raise Number of Currency Analysis By Status Recomputation Flag
        self.__simulators_central_recomputeNumberOfSimulationsByStatus = True

        #[9]: Return The Result
        return {'responseOn': 'ADDREQUEST', 
                'result':     True,  
                'message':    f"Simulation '{simCode}' Successfully Added!"}
    
    def __removeSimulation(self, simulationCode):
        #[1]: Instances
        simulations = self.__simulations
        func_sendPRDREMOVE = self.ipcA.sendPRDREMOVE
        func_sendFAR       = self.ipcA.sendFAR
        simCode = simulationCode

        #[2]: Simulation Check
        sim = simulations.get(simCode, None)
        if sim is None:
            return {'responseOn': 'REMOVALREQUEST', 
                    'result':     False, 
                    'message':    f"Simulation '{simCode}' Removal Failed. 'The Simulation Code Does Not Exist'"}
        
        #[3]: Removal
        sim_allocSim = sim['_allocatedSimulator']
        if sim_allocSim is None:
            func_sendFAR(targetProcess  = 'DATAMANAGER',                                          
                         functionID     = 'removeSimulationData', 
                         functionParams = {'simulationCode': simCode}, 
                         farrHandler    = None)
        else:
            func_sendFAR(targetProcess  = f'SIMULATOR{sim_allocSim}', 
                         functionID     = 'removeSimulation',     
                         functionParams = {'simulationCode': simCode}, 
                         farrHandler    = None)
        del simulations[simCode]

        #[4]: Announce Simulation Update
        func_sendPRDREMOVE(targetProcess = 'GUI', prdAddress = ('SIMULATIONS', simCode))
        func_sendFAR(targetProcess = 'GUI', functionID = 'onSimulationUpdate', functionParams = {'updateType': 'REMOVED', 'simulationCode': simCode}, farrHandler = None)

        #[5]: Raise Number of Currency Analysis By Status Recomputation Flag
        self.__simulators_central_recomputeNumberOfSimulationsByStatus = True

        #[6]: Return The Result
        return {'responseOn': 'REMOVALREQUEST', 
                'result':     True,  
                'message':    f"Simulation '{simCode}' Successfully Removed!"}
   
    def __computeNumberOfSimulationsByStatus(self):
        #[1]: Flag Check
        if not self.__simulators_central_recomputeNumberOfSimulationsByStatus:
            return

        #[2]: New tracker formatting
        newTracker = {'nSimulations_total':      {'total': 0},
                      'nSimulations_QUEUED':     {'total': 0},
                      'nSimulations_PROCESSING': {'total': 0},
                      'nSimulations_PAUSED':     {'total': 0},
                      'nSimulations_ERROR':      {'total': 0},
                      'nSimulations_COMPLETED':  0}
        for simIdx in range (len(self.__simulators)):
            newTracker['nSimulations_total'][simIdx]      = 0
            newTracker['nSimulations_QUEUED'][simIdx]     = 0
            newTracker['nSimulations_PROCESSING'][simIdx] = 0
            newTracker['nSimulations_PAUSED'][simIdx]     = 0
            newTracker['nSimulations_ERROR'][simIdx]      = 0

        #[3]: New tracker update
        for sim in self.__simulations.values():
            sim_allocSim = sim['_allocatedSimulator']
            sim_status   = sim['_status']
            if   sim_status == 'QUEUED':     newTracker['nSimulations_QUEUED']['total']     += 1; newTracker['nSimulations_QUEUED'][sim_allocSim]     += 1; newTracker['nSimulations_total'][sim_allocSim] += 1
            elif sim_status == 'PROCESSING': newTracker['nSimulations_PROCESSING']['total'] += 1; newTracker['nSimulations_PROCESSING'][sim_allocSim] += 1; newTracker['nSimulations_total'][sim_allocSim] += 1
            elif sim_status == 'PAUSED':     newTracker['nSimulations_PAUSED']['total']     += 1; newTracker['nSimulations_PAUSED'][sim_allocSim]     += 1; newTracker['nSimulations_total'][sim_allocSim] += 1
            elif sim_status == 'ERROR':      newTracker['nSimulations_ERROR']['total']      += 1; newTracker['nSimulations_ERROR'][sim_allocSim]      += 1; newTracker['nSimulations_total'][sim_allocSim] += 1
            elif sim_status == 'COMPLETED':  newTracker['nSimulations_COMPLETED'] += 1

        #[4]: Variation Check & Announcement
        updatedContents = []
        for sortType in ('total', 'QUEUED', 'PROCESSING', 'PAUSED', 'ERROR'):
            dataName = f'nSimulations_{sortType}'
            for alloc in self.__simulators_central[dataName]:
                if (self.__simulators_central[dataName][alloc] != newTracker[dataName][alloc]):
                    self.__simulators_central[dataName][alloc] = newTracker[dataName][alloc]
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('SIMULATORCENTRAL', dataName, alloc), prdContent = self.__simulators_central[dataName][alloc])
                    updatedContents.append((dataName, alloc))
        for sortType in ('COMPLETED',):
            dataName = f'nSimulations_{sortType}'
            if (self.__simulators_central[dataName] != newTracker[dataName]):
                self.__simulators_central[dataName] = newTracker[dataName]
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('SIMULATORCENTRAL', dataName), prdContent = self.__simulators_central[dataName])
                updatedContents.append(dataName)
        if updatedContents: 
            self.ipcA.sendFAR(targetProcess  = 'GUI', 
                              functionID     = 'onSimulatorCentralUpdate', 
                              functionParams = {'updatedContents': updatedContents}, 
                              farrHandler    = None)

        #[5]: Flag Lowering
        self.__simulators_central_recomputeNumberOfSimulationsByStatus = False
    #Manager Internal Functions END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #FAR Handlers -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<GUI>
    def __far_setSimulatorActivation(self, requester, requestID, targetSimulatorIndex, activation):
        #[1]: Source Check
        if requester != 'GUI': return None

        #[2]: Request Handling
        return self.__setSimulatorActivation(targetSimulatorIndex = targetSimulatorIndex, activation = activation)
    
    def __far_addSimulation(self, requester, requestID, simulationCode, simulationRange, analysisExport, assets, positions, currencyAnalysisConfigurations, tradeConfigurations):
        #[1]: Source Check
        if requester != 'GUI': return None

        #[2]: Request Handling
        return self.__addSimulation(simulationCode                 = simulationCode,
                                    simulationRange                = simulationRange,
                                    analysisExport                 = analysisExport,
                                    assets                         = assets, 
                                    positions                      = positions,
                                    currencyAnalysisConfigurations = currencyAnalysisConfigurations,
                                    tradeConfigurations            = tradeConfigurations)
    
    def __far_removeSimulation(self, requester, requestID, simulationCode):
        #[1]: Source Check
        if requester != 'GUI': return None

        #[2]: Request Handling
        return self.__removeSimulation(simulationCode = simulationCode)

    #<SIMULATOR>
    def __far_onSimulationUpdate(self, requester, simulationCode, updateType, updatedValue):
        if (requester[:9] == 'SIMULATOR'):
            if (simulationCode in self.__simulations):
                if (updateType == 'STATUS'):
                    self.__simulations[simulationCode]['_status'] = updatedValue
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('SIMULATIONS', simulationCode, '_status'), prdContent = updatedValue)
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onSimulationUpdate', functionParams = {'updateType': 'UPDATED_STATUS', 'simulationCode': simulationCode}, farrHandler = None)
                    self.__simulators_central_recomputeNumberOfSimulationsByStatus = True
                elif (updateType == 'COMPLETION'):
                    self.__simulations[simulationCode]['_completion'] = updatedValue
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('SIMULATIONS', simulationCode, '_completion'), prdContent = updatedValue)
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onSimulationUpdate', functionParams = {'updateType': 'UPDATED_COMPLETION', 'simulationCode': simulationCode}, farrHandler = None)
    
    def __far_onSimulationCompletion(self, requester, simulationCode, simulationSummary):
        if (requester[:9] == 'SIMULATOR'):
            _simulation = self.__simulations[simulationCode]
            _simulation['_status']             = 'COMPLETED'
            _simulation['_allocatedSimulator'] = None
            _simulation['_completion']         = None
            _simulation['_simulationSummary']  = simulationSummary
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('SIMULATIONS', simulationCode), prdContent = _simulation)
            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onSimulationUpdate', functionParams = {'updateType': 'COMPLETED', 'simulationCode': simulationCode}, farrHandler = None)
            self.__simulators_central_recomputeNumberOfSimulationsByStatus = True
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------