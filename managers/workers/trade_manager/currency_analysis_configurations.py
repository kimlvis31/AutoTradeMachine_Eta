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

class CurrencyAnalysisConfigurations:
    #Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA, tmConfig):
        #[1]: System
        self.__path_cac = Path(path_project)/'data'/'tm'/'cac'
        self.__ipcA     = ipcA
        self.__tmConfig = tmConfig

        #[2]: Configurations
        self.__configurations = dict()
        self.__attachedCAs    = dict()
        self.__updates        = deque()

        #[3]: FAR Handlers
        ipcA.addFARHandler('addCurrencyAnalysisConfiguration',    self.__far_addConfiguration,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        ipcA.addFARHandler('removeCurrencyAnalysisConfiguration', self.__far_removeConfiguration, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

        #[4]: Read Local Configurations
        self.__read()

        #[5]: Initial Announcement
        for tProcName in ('GUI', 'SIMULATIONMANAGER'): 
            ipcA.sendPRDEDIT(targetProcess = tProcName, 
                             prdAddress    = 'CURRENCYANALYSISCONFIGURATIONS', 
                             prdContent    = self.__configurations)
    #Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #IPC Handlers ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __far_addConfiguration(self, requester, requestID, currencyAnalysisConfigurationCode, currencyAnalysisConfiguration):
        #[1]: Source Check
        if requester != 'GUI':
            return

        #[2]: CAC Add
        return self.__addConfiguration(code          = currencyAnalysisConfigurationCode, 
                                       configuration = currencyAnalysisConfiguration,
                                       isImport      = False)
    
    def __far_removeConfiguration(self, requester, requestID, currencyAnalysisConfigurationCode):
        #[1]: Source Check
        if requester != 'GUI':
            return
        
        #[2]: CAC Removal
        return self.__removeConfiguration(code = currencyAnalysisConfigurationCode)
    #IPC Handlers END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Internal Handlers ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __read(self):
        for file_path in self.__path_cac.glob('*.cac'):
            #[1]: File Read
            try:
                with open(file_path, 'r', encoding = 'utf-8') as f:
                    cac_iIDs_json = json.load(f)
            except Exception as e:
                self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Read A Currency Analysis Configuration."
                                         f" * File:           {file_path}\n"
                                         f" * Error:          {e}\n"
                                         f" * Detailed Trace: {traceback.format_exc()}\n"),
                              logType = 'Error', 
                              color   = 'light_red')
                continue

            #[2]: Local Instance Construction
            cacCode  = file_path.stem
            cac_iIDs = {int(iID_str): cac_iID.copy() for iID_str, cac_iID in cac_iIDs_json.items()}
            self.__addConfiguration(code          = cacCode, 
                                    configuration = cac_iIDs,
                                    isImport      = True)
    
    def __save(self, code):
        #[1]: Directory Check
        self.__path_cac.mkdir(parents = True, exist_ok = True)

        #[2]: Save Attempt
        file_path = self.__path_cac / f'{code}.cac'
        try:
            cac = self.__configurations[code]
            with open(file_path, 'w', encoding = 'utf-8') as f:
                json.dump(cac, f, indent=4)

        #[3]: Exception Handling
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Save A Currency Analysis Configuration. User Attention Strongly Advised."
                                     f" * Code:           {code}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')
    
    def __delete(self, code):
        #[1]: Path Setup
        file_path = self.__path_cac / f'{code}.cac'

        #[2]: Delete Attempt
        try:
            file_path.unlink(missing_ok = True)

        #[3]: Exception Handling
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Delete A Currency Analysis Configuration File.\n"
                                     f" * Code:           {code}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')

    def __addConfiguration(self, code, configuration, isImport):
        #[1]: Instances
        configs          = self.__configurations
        aCAs             = self.__attachedCAs
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR
        
        #[2]: Configuration Code Check
        #---[2-1]: Unnamed Code
        if code is None:
            ucacIdx = 0
            while code is None:
                _code = f"UACC{ucacIdx}" #UACC: Unnamed Analysis Configuration Code
                if _code not in configs: 
                    code = _code
                    break
                ucacIdx += 1

        #---[2-2]: Code Existence Check
        if code in configs:
            return {'result':  False, 
                    'message': f"Currency Analysis Configuration '{code}' Add Failed. 'The Configuration Code Already Exists'"}

        #[3]: Configuration Add
        try:
            #[3-1]: Configuration Save
            configs[code] = configuration
            aCAs[code]    = set()
            if not isImport:
                self.__save(code = code)

            #[3-2]: Update Announcement
            self.__updates.append({'type': 'NEW',
                                   'code': code})
            if not isImport:
                func_sendPRDEDIT(targetProcess = 'GUI', 
                                 prdAddress    = ('CURRENCYANALYSISCONFIGURATIONS', code), 
                                 prdContent    = self.getConfiguration(code = code))
                func_sendFAR(targetProcess  = 'GUI', 
                             functionID     = 'onCurrencyAnalysisConfigurationUpdate', 
                             functionParams = {'updateType': 'ADDED', 
                                               'currencyAnalysisConfigurationCode': code}, 
                             farrHandler    = None)
            
            #[3-3]: Result Return
            return {'result':  True,
                    'message': f"Currency Analysis Configuration '{code}' Successfully Added!"}
        
        #[3-4]: Exception Handling
        except Exception as e: 
            return {'result':  False, 
                    'message': f"Currency Analysis Configuration '{code}' Add Failed Due To An Unexpected Error. '{str(e)}'"}
    
    def __removeConfiguration(self, code):
        #[1]: Instances
        configs            = self.__configurations
        aCAs               = self.__attachedCAs
        func_sendPRDREMOVE = self.__ipcA.sendPRDREMOVE
        func_sendFAR       = self.__ipcA.sendFAR

        #[2]: Code Check
        if code not in configs:
            return {'result':  False, 
                    'message': f"Currency Analysis Configuration '{code}' Removal Failed. 'The Configuration Code Does Not Exist'"}

        #[3]: Attached Check
        if aCAs[code]:
            aCAs_code_str = ", ".join(f"'{caCode}'" for caCode in aCAs[code])
            return {'result':  False, 
                    'message': f"Currency Analysis Configuration '{code}' Removal Failed. 'There Exist 1 Or More Attached Currency Analyses [{aCAs_code_str}]'"}

        #[4]: CAC Removal
        del configs[code]
        del aCAs[code]
        self.__delete(code = code)

        #[5]: Announcement
        func_sendPRDREMOVE(targetProcess = 'GUI', 
                           prdAddress    = ('CURRENCYANALYSISCONFIGURATIONS', code))
        func_sendFAR(targetProcess  = 'GUI', 
                     functionID     = 'onCurrencyAnalysisConfigurationUpdate', 
                     functionParams = {'updateType':                       'REMOVED', 
                                       'currencyAnalysisConfigurationCode': code}, 
                     farrHandler    = None)

        #[6]: Result Return
        return {'result':  True,
                'message': f"Currency Analysis Configuration '{code}' Removal Successful!"}
    
    def __logger(self, message, logType, color):
        if not self.__tmConfig[f'print_{logType}']:
            return
        time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
        msg      = f"[TRADEMANAGER-CACWORKER-{time_str}] {message}"
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
        configs = self.__configurations
        if code not in configs:
            return None
        
        #[2]: Configuration Copy
        cac = {iID: cac_iID.copy() for iID, cac_iID in configs[code].items()}

        #[3]: Result Return
        return cac
    
    def attachCurrencyAnalysis(self, code, caCode):
        #[1]: Code Check
        aCAs = self.__attachedCAs
        if code not in aCAs:
            return
        
        #[2]: Attaching
        aCAs[code].add(caCode)

    def detachCurrencyAnalysis(self, code, caCode):
        #[1]: Code Check
        aCAs = self.__attachedCAs
        if code not in aCAs:
            return
        
        #[2]: Detaching
        aCAs[code].discard(caCode)
    #External Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    