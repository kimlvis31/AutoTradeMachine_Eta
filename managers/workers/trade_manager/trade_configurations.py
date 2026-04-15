#ATM Modules
import ipc

#Python Modules
import time
import termcolor
import json
import traceback
from pathlib     import Path
from datetime    import datetime
from collections import deque

#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT

class TradeConfigurations:
    #Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA, tmConfig):
        #[1]: System
        self.__path_tc  = Path(path_project)/'data'/'tm'/'tc'
        self.__ipcA     = ipcA
        self.__tmConfig = tmConfig

        #[2]: Configurations
        self.__configurations   = dict()
        self.__attachedAccounts = dict()
        self.__updates          = deque()

        #[3]: FAR Handlers
        ipcA.addFARHandler('addTradeConfiguration',    self.__far_addConfiguration,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        ipcA.addFARHandler('removeTradeConfiguration', self.__far_removeConfiguration, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

        #[4]: Read Local Configurations
        self.__read()

        #[5]: Initial Announcement
        for tProcName in ('GUI', 'SIMULATIONMANAGER'): 
            ipcA.sendPRDEDIT(targetProcess = tProcName, 
                             prdAddress    = 'TRADECONFIGURATIONS', 
                             prdContent    = self.__configurations)
    #Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #IPC Handlers ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __far_addConfiguration(self, requester, requestID, tradeConfigurationCode, tradeConfiguration):
        #[1]: Source Check
        if requester != 'GUI':
            return

        #[2]: TC Add
        return self.__addConfiguration(code          = tradeConfigurationCode, 
                                       configuration = tradeConfiguration,
                                       isImport      = False)
    
    def __far_removeConfiguration(self, requester, requestID, tradeConfigurationCode):
        #[1]: Source Check
        if requester != 'GUI':
            return
        
        #[2]: TC Removal
        return self.__removeConfiguration(code = tradeConfigurationCode)
    #IPC Handlers END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Internal Handlers ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __read(self):
        for file_path in self.__path_tc.glob('*.tc'):
            #[1]: File Read
            try:
                with open(file_path, 'r', encoding = 'utf-8') as f:
                    tc = json.load(f)
            except Exception as e:
                self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Read A Trade Configuration."
                                         f" * File:           {file_path}\n"
                                         f" * Error:          {e}\n"
                                         f" * Detailed Trace: {traceback.format_exc()}\n"),
                              logType = 'Error', 
                              color   = 'light_red')
                continue

            #[2]: Local Instance Construction
            tcCode = file_path.stem
            self.__addConfiguration(code          = tcCode, 
                                    configuration = tc,
                                    isImport      = True)
    
    def __save(self, code):
        #[1]: Directory Check
        self.__path_tc.mkdir(parents = True, exist_ok = True)

        #[2]: Save Attempt
        file_path = self.__path_tc / f'{code}.tc'
        try:
            tc = self.__configurations[code]
            with open(file_path, 'w', encoding = 'utf-8') as f:
                json.dump(tc, f, indent=4)

        #[3]: Exception Handling
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Save A Trade Configuration. User Attention Strongly Advised."
                                     f" * Code:           {code}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')
    
    def __delete(self, code):
        #[1]: Path Setup
        file_path = self.__path_tc / f'{code}.tc'

        #[2]: Delete Attempt
        try:
            file_path.unlink(missing_ok = True)

        #[3]: Exception Handling
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Delete A Trade Configuration File.\n"
                                     f" * Code:           {code}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')

    def __addConfiguration(self, code, configuration, isImport):
        #[1]: Instances
        configs          = self.__configurations
        aAccounts        = self.__attachedAccounts
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR
        
        #[2]: Configuration Code Check
        #---[2-1]: Unnamed Code
        if code is None:
            utccIdx = 0
            while code is None:
                _code = f"UTCC{utccIdx}" #UTCC: Unnamed Trade Configuration Code
                if _code not in configs: 
                    code = _code
                    break
                utccIdx += 1

        #---[2-2]: Code Existence Check
        if code in configs:
            return {'result':  False, 
                    'message': f"Trade Configuration '{code}' Add Failed. 'The Configuration Code Already Exists'"}

        #[3]: Configuration Add
        try:
            #[3-1]: Configuration Save
            configs[code]   = configuration
            aAccounts[code] = set()
            if not isImport:
                self.__save(code = code)

            #[3-2]: Update Announcement
            self.__updates.append({'type': 'NEW',
                                   'code': code})
            if not isImport:
                func_sendPRDEDIT(targetProcess = 'GUI', 
                                 prdAddress    = ('TRADECONFIGURATIONS', code), 
                                 prdContent    = self.getConfiguration(code = code))
                func_sendFAR(targetProcess  = 'GUI', 
                             functionID     = 'onTradeConfigurationUpdate', 
                             functionParams = {'updateType': 'ADDED', 
                                               'tradeConfigurationCode': code}, 
                             farrHandler    = None)
            
            #[3-3]: Result Return
            return {'result':  True,
                    'message': f"Trade Configuration '{code}' Successfully Added!"}
        
        #[3-4]: Exception Handling
        except Exception as e: 
            return {'result':  False, 
                    'message': f"Trade Configuration '{code}' Add Failed Due To An Unexpected Error. '{str(e)}'"}
    
    def __removeConfiguration(self, code):
        #[1]: Instances
        configs            = self.__configurations
        aAccounts          = self.__attachedAccounts
        func_sendPRDREMOVE = self.__ipcA.sendPRDREMOVE
        func_sendFAR       = self.__ipcA.sendFAR

        #[2]: Code Check
        if code not in configs:
            return {'result':  False, 
                    'message': f"Trade Configuration '{code}' Removal Failed. 'The Configuration Code Does Not Exist'"}

        #[3]: Attached Check
        if aAccounts[code]:
            aAccounts_code_str = ", ".join(f"'{aID}'" for aID in aAccounts[code])
            return {'result':  False, 
                    'message': f"Trade Configuration '{code}' Removal Failed. 'There Exist 1 Or More Attached Accounts [{aAccounts_code_str}]'"}

        #[4]: TC Removal
        del configs[code]
        del aAccounts[code]
        self.__delete(code = code)

        #[5]: Announcement
        func_sendPRDREMOVE(targetProcess = 'GUI', 
                           prdAddress    = ('TRADECONFIGURATIONS', code))
        func_sendFAR(targetProcess  = 'GUI', 
                     functionID     = 'onTradeConfigurationUpdate', 
                     functionParams = {'updateType':             'REMOVED', 
                                       'tradeConfigurationCode': code}, 
                     farrHandler    = None)

        #[6]: Result Return
        return {'result':  True,
                'message': f"Trade Configuration '{code}' Removal Successful!"}
    
    def __logger(self, message, logType, color):
        if not self.__tmConfig[f'print_{logType}']:
            return
        time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
        msg      = f"[TRADEMANAGER-TCWORKER-{time_str}] {message}"
        print(termcolor.colored(msg, color))
    #Internal Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #External Handlers ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def getUpdates(self):
        #[1]: Updates Copy
        updates = self.__updates.copy()

        #[2]: Local Instance Clearing
        self.__updates.clear()

        #[3]: Result Return
        return updates
    
    def getConfiguration(self, code):
        #[1]: Code Check
        tc = self.__configurations.get(code, None)
        if tc is None:
            return None
        
        #[2]: Configuration Copy
        tc_copied = {'leverage':              tc['leverage'],
                     'isolated':              tc['isolated'],
                     'direction':             tc['direction'],
                     'fullStopLossImmediate': tc['fullStopLossImmediate'],
                     'fullStopLossClose':     tc['fullStopLossClose'],
                     'postStopLossReentry':   tc['postStopLossReentry'],
                     'teff_functionType':     tc['teff_functionType'],
                     'teff_functionParams':   tc['teff_functionParams'].copy()}

        #[3]: Result Return
        return tc_copied
    
    def exists(self, code):
        #[1]: Code Check
        tc = self.__configurations.get(code, None)
        return (tc is not None)

    def isAttached(self, code, accountID):
        #[1]: Code Check
        aAccounts = self.__attachedAccounts.get(code, None)
        if aAccounts is None:
            return
        
        #[2]: Attaching
        return (accountID in aAccounts)

    def attachAccount(self, code, accountID):
        #[1]: Code Check
        aAccounts = self.__attachedAccounts.get(code, None)
        if aAccounts is None:
            return
        
        #[2]: Attaching
        aAccounts.add(accountID)

    def detachAccount(self, code, accountID):
        #[1]: Code Check
        aAccounts = self.__attachedAccounts.get(code, None)
        if aAccounts is None:
            return
        
        #[2]: Detaching
        aAccounts.discard(accountID)
    #External Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------