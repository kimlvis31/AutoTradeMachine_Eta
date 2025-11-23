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

class procManager_SimulationManager:
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

        #Process Control
        self.__processLoopContinue = True
        print(termcolor.colored("   SIMULATIONMANAGER", 'light_blue'), termcolor.colored("Initialization Complete! -----------------------------------------------------------------------------------------------------", 'green'))
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Process Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        _dm_Simulations = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = 'SIMULATIONS')
        for simulationCode in _dm_Simulations:
            _dm_simulation = _dm_Simulations[simulationCode]
            self.__simulations[simulationCode] = {'simulationRange':                _dm_simulation['simulationRange'],
                                                  'assets':                         _dm_simulation['assets'],
                                                  'positions':                      _dm_simulation['positions'],
                                                  'currencyAnalysisConfigurations': _dm_simulation['currencyAnalysisConfigurations'],
                                                  'tradeConfigurations':            _dm_simulation['tradeConfigurations'],
                                                  'creationTime':                   _dm_simulation['creationTime'],
                                                  '_status':                        'COMPLETED',
                                                  '_allocatedSimulator':            None,
                                                  '_completion':                    None,
                                                  '_simulationSummary':             _dm_simulation['simulationSummary'],
                                                  '_detailedReport':                _dm_simulation['detailedReport']}
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'SIMULATIONS', prdContent = self.__simulations)
        self.__simulators_central_recomputeNumberOfSimulationsByStatus = True
        while (self.__processLoopContinue == True):
            #Process any existing FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()
            #Compute Number Of Currency Analysis By Status
            self.__computeNumberOfSimulationsByStatus()
            #Process Loop Control
            if (self.__loopSleepDeterminer() == True): time.sleep(0.001)

    def __loopSleepDeterminer(self):
        sleepLoop = True
        return sleepLoop

    def terminate(self, requester):
        self.__processLoopContinue = False
    #Manager Process Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    
    #Manager Internal Functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __setSimulatorActivation(self, targetSimulatorIndex, activation):
        if (targetSimulatorIndex == 'all'): targetSimulatorIndexes = list(range(self.__simulators_central['nSimulators']))
        else:                               targetSimulatorIndexes = [targetSimulatorIndex,]
        updatedContents = list()
        for _targetSimulatorIndex in targetSimulatorIndexes:
            _currentActivation = self.__simulators_central['simulatorActivation'][_targetSimulatorIndex]
            if (_currentActivation != activation): 
                self.__simulators_central['simulatorActivation'][_targetSimulatorIndex] = activation
                updatedContents.append(('simulatorActivation', _targetSimulatorIndex))
                self.ipcA.sendFAR(targetProcess = self.__simulators[_targetSimulatorIndex]['processName'], functionID = 'setActivation', functionParams = {'activation': activation}, farrHandler = None)
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('SIMULATORCENTRAL', 'simulatorActivation', _targetSimulatorIndex), prdContent = activation)
        nUpdated = len(updatedContents)
        if (0 < nUpdated): self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onSimulatorCentralUpdate', functionParams = {'updatedContents': updatedContents}, farrHandler = None)
        if (targetSimulatorIndex == 'all'):
            if (activation == True): responseMessage = "All Simulators Are Now Active!"
            else:                    responseMessage = "All Simulators Are Now Inactive!"
        else:
            if (activation == True): responseMessage = "SIMULATOR{:d} Is Now Active!".format(targetSimulatorIndex)
            else:                    responseMessage = "SIMULATOR{:d} Is Now Inactive!".format(targetSimulatorIndex)
        return {'responseOn': 'SIMULATORACTIVATION', 'result': activation, 'message': responseMessage}
    def __addSimulation(self, simulationCode, simulationRange, cycleData, assets, positions, currencyAnalysisConfigurations, tradeConfigurations):
        #[1]: Simulation code. If 'None' is passed, generated an indexed and unnamed code
        if (simulationCode == None):
            unnamedSimulationIndex = 0
            while (simulationCode == None):
                _simulationCode = "USC{:d}".format(unnamedSimulationIndex) #USC: Unnamed Simulation Code
                if (_simulationCode not in self.__simulations): simulationCode = _simulationCode
                else: unnamedSimulationIndex += 1
            _test_simulationCode = True
        elif (simulationCode not in self.__simulations): _test_simulationCode = True
        else:                                            _test_simulationCode = False
        #[2]: Simulation Range
        _test_simulationRange = True
        if (simulationRange[0] < simulationRange[1]): _test_simulationRange = True
        else:                                         _test_simulationRange = False
        #If all tests passed, add a simulation
        if ((_test_simulationCode == True) and (_test_simulationRange == True)):
            try:
                #Find the simulator to allocate
                simulatorIndex_toAllocate = None
                nSimulations_min = min([len(self.__simulators[simulatorIndex]['allocated_simulationCodes']) for simulatorIndex in range (len(self.__simulators))])
                for simulatorIndex in range (len(self.__simulators)):
                    if (len(self.__simulators[simulatorIndex]['allocated_simulationCodes']) == nSimulations_min): simulatorIndex_toAllocate = simulatorIndex; break
                #Create Simulation Instance
                _creationTime = time.time()
                self.__simulations[simulationCode] = {'simulationRange':                simulationRange,
                                                      'assets':                         assets,
                                                      'positions':                      positions,
                                                      'currencyAnalysisConfigurations': currencyAnalysisConfigurations,
                                                      'tradeConfigurations':            tradeConfigurations,
                                                      'creationTime':                   _creationTime,
                                                      '_status':                        'QUEUED',
                                                      '_allocatedSimulator':            simulatorIndex_toAllocate,
                                                      '_completion':                    None,
                                                      '_simulationSummary':             None,
                                                      '_detailedReport':                None}
                self.ipcA.sendFAR(targetProcess  = self.__simulators[simulatorIndex_toAllocate]['processName'],
                                  functionID     = 'addSimulation',
                                  functionParams = {'simulationCode':                 simulationCode,
                                                    'simulationRange':                simulationRange,
                                                    'cycleData':                      cycleData,
                                                    'assets':                         assets,
                                                    'positions':                      positions,
                                                    'currencyAnalysisConfigurations': currencyAnalysisConfigurations,
                                                    'tradeConfigurations':            tradeConfigurations,
                                                    'creationTime':                   _creationTime},
                                  farrHandler = None)
                self.__simulators[simulatorIndex_toAllocate]['allocated_simulationCodes'].add(simulationCode)
                #Announce simulation update
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('SIMULATIONS', simulationCode), prdContent = self.__simulations[simulationCode])
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onSimulationUpdate', functionParams = {'updateType': 'ADDED', 'simulationCode': simulationCode}, farrHandler = None)
                #Raise Number of Currency Analysis By Status Recomputation Flag
                self.__simulators_central_recomputeNumberOfSimulationsByStatus = True
                #Return the result
                return                    {'responseOn': 'ADDREQUEST', 'result': True,  'message': "Simulation '{:s}' Successfully Added!".format(simulationCode)}
            except Exception as e: return {'responseOn': 'ADDREQUEST', 'result': False, 'message': "Simulation '{:s}' Add Failed Due To An Unexpected Error. '{:s}'".format(simulationCode, str(e))}
        else: return                      {'responseOn': 'ADDREQUEST', 'result': False, 'message': "Simulation '{:s}' Add Failed. 'The Simulation Code Already Exists'".format(simulationCode)}
    def __removeSimulation(self, simulationCode):
        if (simulationCode in self.__simulations):
            try:
                _simulation = self.__simulations[simulationCode]
                _simulation_allocatedSimulator = _simulation['_allocatedSimulator']
                if (_simulation_allocatedSimulator == None): self.ipcA.sendFAR(targetProcess = 'DATAMANAGER',                                          functionID = 'removeSimulationData', functionParams = {'simulationCode': simulationCode}, farrHandler = None)
                else:                                        self.ipcA.sendFAR(targetProcess = 'SIMULATOR{:d}'.format(_simulation_allocatedSimulator), functionID = 'removeSimulation',     functionParams = {'simulationCode': simulationCode}, farrHandler = None)
                del self.__simulations[simulationCode]
                self.ipcA.sendPRDREMOVE(targetProcess = 'GUI', prdAddress = ('SIMULATIONS', simulationCode))
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onSimulationUpdate', functionParams = {'updateType': 'REMOVED', 'simulationCode': simulationCode}, farrHandler = None)
                self.__simulators_central_recomputeNumberOfSimulationsByStatus = True
                return {'responseOn': 'REMOVALREQUEST', 'result': True,  'message': "Simulation '{:s}' Successfully Removed!".format(simulationCode)}
            except Exception as e: return {'responseOn': 'REMOVALREQUEST', 'result': False, 'message': "Simulation '{:s}' Removal Failed Due To An Unexpected Error. '{:s}'".format(simulationCode, str(e))}
        else: return                      {'responseOn': 'REMOVALREQUEST', 'result': False, 'message': "Simulation '{:s}' Removal Failed. 'The Simulation Code Does Not Exist'".format(simulationCode)}
    def __computeNumberOfSimulationsByStatus(self):
        if (self.__simulators_central_recomputeNumberOfSimulationsByStatus == True):
            #New tracker formatting
            newTracker = {'nSimulations_total':      {'total': 0},
                          'nSimulations_QUEUED':     {'total': 0},
                          'nSimulations_PROCESSING': {'total': 0},
                          'nSimulations_PAUSED':     {'total': 0},
                          'nSimulations_ERROR':      {'total': 0},
                          'nSimulations_COMPLETED':  0}
            for simulatorIndex in range (len(self.__simulators)):
                newTracker['nSimulations_total'][simulatorIndex]      = 0
                newTracker['nSimulations_QUEUED'][simulatorIndex]     = 0
                newTracker['nSimulations_PROCESSING'][simulatorIndex] = 0
                newTracker['nSimulations_PAUSED'][simulatorIndex]     = 0
                newTracker['nSimulations_ERROR'][simulatorIndex]      = 0
            #New tracker update
            for simulationCode in self.__simulations:
                _simulation = self.__simulations[simulationCode]
                _simulation_allocatedSimulator = _simulation['_allocatedSimulator']
                _simulation_status             = _simulation['_status']
                if   (_simulation_status == 'QUEUED'):     newTracker['nSimulations_QUEUED']['total']     += 1; newTracker['nSimulations_QUEUED'][_simulation_allocatedSimulator]     += 1; newTracker['nSimulations_total'][_simulation_allocatedSimulator] += 1
                elif (_simulation_status == 'PROCESSING'): newTracker['nSimulations_PROCESSING']['total'] += 1; newTracker['nSimulations_PROCESSING'][_simulation_allocatedSimulator] += 1; newTracker['nSimulations_total'][_simulation_allocatedSimulator] += 1
                elif (_simulation_status == 'PAUSED'):     newTracker['nSimulations_PAUSED']['total']     += 1; newTracker['nSimulations_PAUSED'][_simulation_allocatedSimulator]     += 1; newTracker['nSimulations_total'][_simulation_allocatedSimulator] += 1
                elif (_simulation_status == 'ERROR'):      newTracker['nSimulations_ERROR']['total']      += 1; newTracker['nSimulations_ERROR'][_simulation_allocatedSimulator]      += 1; newTracker['nSimulations_total'][_simulation_allocatedSimulator] += 1
                elif (_simulation_status == 'COMPLETED'):  newTracker['nSimulations_COMPLETED'] += 1
            #Previous & new tracker comparison
            updatedContents = list()
            for sortType in ('total', 'QUEUED', 'PROCESSING', 'PAUSED', 'ERROR'):
                dataName = 'nSimulations_{:s}'.format(sortType)
                for alloc in self.__simulators_central[dataName]:
                    if (self.__simulators_central[dataName][alloc] != newTracker[dataName][alloc]):
                        self.__simulators_central[dataName][alloc] = newTracker[dataName][alloc]
                        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('SIMULATORCENTRAL', dataName, alloc), prdContent = self.__simulators_central[dataName][alloc])
                        updatedContents.append((dataName, alloc))
            for sortType in ('COMPLETED',):
                dataName = 'nSimulations_{:s}'.format(sortType)
                if (self.__simulators_central[dataName] != newTracker[dataName]):
                    self.__simulators_central[dataName] = newTracker[dataName]
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('SIMULATORCENTRAL', dataName), prdContent = self.__simulators_central[dataName])
                    updatedContents.append(dataName)
            if (0 < len(updatedContents)): self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onSimulatorCentralUpdate', functionParams = {'updatedContents': updatedContents}, farrHandler = None)
            #Lower the flag
            self.__simulators_central_recomputeNumberOfSimulationsByStatus = False
    #Manager Internal Functions END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #FAR Handlers -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<GUI>
    def __far_setSimulatorActivation(self, requester, requestID, targetSimulatorIndex, activation):
        if (requester == 'GUI'): return self.__setSimulatorActivation(targetSimulatorIndex = targetSimulatorIndex, activation = activation)
    def __far_addSimulation(self, requester, requestID, simulationCode, simulationRange, cycleData, assets, positions, currencyAnalysisConfigurations, tradeConfigurations):
        if (requester == 'GUI'): return self.__addSimulation(simulationCode                 = simulationCode,
                                                             simulationRange                = simulationRange,
                                                             cycleData                      = cycleData,
                                                             assets                         = assets, 
                                                             positions                      = positions,
                                                             currencyAnalysisConfigurations = currencyAnalysisConfigurations,
                                                             tradeConfigurations            = tradeConfigurations)
    def __far_removeSimulation(self, requester, requestID, simulationCode):
        if (requester == 'GUI'): return self.__removeSimulation(simulationCode = simulationCode)

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
    def __far_onSimulationCompletion(self, requester, simulationCode, simulationSummary, detailedReport):
        if (requester[:9] == 'SIMULATOR'):
            _simulation = self.__simulations[simulationCode]
            _simulation['_status']             = 'COMPLETED'
            _simulation['_allocatedSimulator'] = None
            _simulation['_completion']         = None
            _simulation['_simulationSummary']  = simulationSummary
            _simulation['_detailedReport']     = detailedReport
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('SIMULATIONS', simulationCode), prdContent = _simulation)
            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onSimulationUpdate', functionParams = {'updateType': 'COMPLETED', 'simulationCode': simulationCode}, farrHandler = None)
            self.__simulators_central_recomputeNumberOfSimulationsByStatus = True
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------