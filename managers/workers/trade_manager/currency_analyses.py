#ATM Modules
import ipc
import auxiliaries
import constants
import managers.workers.currency_analysis.currency_analysis as caWorker

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

KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S

ANALYSISRESULT_BUFFERSIZE = 1440*90

_CURRENCYANALYSIS_STATUSINTERPRETATIONS = {caWorker.STATUS_WAITINGNEURALNETWORK: 'WAITINGNEURALNETWORK',
                                           caWorker.STATUS_WAITINGSTREAM:        'WAITINGSTREAM',
                                           caWorker.STATUS_WAITINGDATAAVAILABLE: 'WAITINGDATAAVAILABLE',
                                           caWorker.STATUS_QUEUED:               'QUEUED',
                                           caWorker.STATUS_FETCHING:             'FETCHING',
                                           caWorker.STATUS_INITIALANALYZING:     'INITIALANALYZING',
                                           caWorker.STATUS_ANALYZING:            'ANALYZING',
                                           caWorker.STATUS_ERROR:                'ERROR'}

class CurrencyAnalyses:
    #Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA, tmConfig, analyzerProcessNames, currencies, currencyAnalysisConfigurations):
        #[1]: System
        self.__path_cal = Path(path_project)/'data'/'tm'/'cal.json'
        self.__ipcA     = ipcA
        self.__tmConfig = tmConfig

        #[2]: External Data Instances
        self.__currencies = currencies
        self.__caConfigs  = currencyAnalysisConfigurations

        #[3]: Analyzers Central
        self.__analyzers         = list()
        self.__analyzers_central = {'nAnalyzers':                       len(analyzerProcessNames),
                                    'nCurrencyAnalysis':                {'UNALLOCATED': 0},
                                    'averageAnalysisGenerationTime_ns': dict()}
        for aProcName in analyzerProcessNames:
            aIdx = int(aProcName[8:])
            aDesc = {'processName':           aProcName,
                     'currencyAnalysisCodes': set(),
                     'currencySymbols':       set()}
            self.__analyzers.append(aDesc)
            self.__analyzers_central['nCurrencyAnalysis'][aIdx]                = 0
            self.__analyzers_central['averageAnalysisGenerationTime_ns'][aIdx] = None
        ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'ANALYZERCENTRAL', prdContent = self.__analyzers_central)

        #[4]: Currency Analyses
        self.__currencyAnalyses          = dict()
        self.__currencyAnalyses_bySymbol = dict()
        self.__linearizedAnalyses        = dict()
        self.__updates                   = deque()

        #[5]: FAR Handlers
        ipcA.addFARHandler('addCurrencyAnalysis',            self.__far_addCurrencyAnalysis,            executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        ipcA.addFARHandler('removeCurrencyAnalysis',         self.__far_removeCurrencyAnalysis,         executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        ipcA.addFARHandler('restartCurrencyAnalysis',        self.__far_restartCurrencyAnalysis,        executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        ipcA.addFARHandler('onAnalyzerSummaryUpdate',        self.__far_onAnalyzerSummaryUpdate,        executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        ipcA.addFARHandler('onCurrencyAnalysisStatusUpdate', self.__far_onCurrencyAnalysisStatusUpdate, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        ipcA.addFARHandler('onAnalysisGeneration',           self.__far_onAnalysisGeneration,           executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

        #[6]: Read Currency Analyses List
        self.__readCurrencyAnalysisList()

        #[7]: Initial Announcement
        ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CURRENCYANALYSIS', prdContent = self.__currencyAnalyses)
    #Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




    
    #IPC Handlers ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __far_addCurrencyAnalysis(self, requester, requestID, currencySymbol, currencyAnalysisCode, currencyAnalysisConfigurationCode):
        #[1]: Source Check
        if requester != 'GUI':
            return {'result':     False,
                    'responseOn': 'ADDCURRENCYANALYSIS',
                    'message':    "INVALID REQUESTER"}

        #[2]: Request Handling
        return self.__addCurrencyAnalysis(code       = currencyAnalysisCode,
                                          symbol     = currencySymbol,
                                          configCode = currencyAnalysisConfigurationCode,
                                          isImport   = False)
    
    def __far_restartCurrencyAnalysis(self, requester, requestID, currencyAnalysisCode):
        #[1]: Source Check
        if requester != 'GUI':
            return {'result':               False,
                    'responseOn':           'RESTARTCURRENCYANALYSIS',
                    'currencyAnalysisCode': currencyAnalysisCode,
                    'message':              "INVALID REQUESTER"}

        #[2]: Request Handling
        return self.__restartCurrencyAnalysis(code = currencyAnalysisCode)
    
    def __far_removeCurrencyAnalysis(self, requester, requestID, currencyAnalysisCode):
        #[1]: Source Check
        if requester != 'GUI':
            return {'result':               False,
                    'responseOn':           'REMOVECURRENCYANALYSIS',
                    'currencyAnalysisCode': currencyAnalysisCode,
                    'message':              "INVALID REQUESTER"}

        #[2]: Request Handling
        return self.__removeCurrencyAnalysis(code = currencyAnalysisCode)
    
    def __far_onAnalyzerSummaryUpdate(self, requester, updatedSummary):
        #[1]: Source Check
        if not requester.startswith('ANALYZER'): 
            return

        #[2]: Content Check
        if updatedSummary != 'averageAnalysisGenerationTime_ns': 
            return
        
        #[3]: Content Read
        aCentral = self.__analyzers_central
        aIdx     = int(requester[8:])
        aagt_ns  = self.__ipcA.getPRD(processName = requester, 
                                      prdAddress  = ('ANALYZERSUMMARY', 'averageAnalysisGenerationTime_ns'))
        aCentral['averageAnalysisGenerationTime_ns'][aIdx] = aagt_ns

        #[4]: New Value Announcement
        self.__ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                                prdAddress    = ('ANALYZERCENTRAL', 'averageAnalysisGenerationTime_ns', aIdx), 
                                prdContent    = aagt_ns)
        self.__ipcA.sendFAR(targetProcess  = 'GUI', 
                            functionID     = 'onAnalyzerCentralUpdate', 
                            functionParams = {'updatedContents': [('averageAnalysisGenerationTime_ns', aIdx),]}, 
                            farrHandler    = None)
    
    def __far_onCurrencyAnalysisStatusUpdate(self, requester, currencyAnalysisCode, newStatus):
        #[1]: Source Check
        if not requester.startswith('ANALYZER'): 
            return

        #[2]: Status Interpretation
        newStatus = _CURRENCYANALYSIS_STATUSINTERPRETATIONS[newStatus]
        self.__currencyAnalyses[currencyAnalysisCode]['status'] = newStatus

        #[3]: New Value Announcement
        self.__ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                              prdAddress    = ('CURRENCYANALYSIS', currencyAnalysisCode, 'status'), 
                              prdContent    = newStatus)
        self.__ipcA.sendFAR(targetProcess  = 'GUI',
                            functionID     = 'onCurrencyAnalysisUpdate', 
                            functionParams = {'updateType': 'UPDATE_STATUS', 
                                              'currencyAnalysisCode': currencyAnalysisCode}, 
                            farrHandler    = None)
    
    def __far_onAnalysisGeneration(self, requester, currencyAnalysisCode, linearizedAnalysis):
        #[1]: Requester Check
        if not requester.startswith('ANALYZER'): 
            return
        
        #[2]: Instances
        caCode = currencyAnalysisCode
        cas    = self.__currencyAnalyses
        las    = self.__linearizedAnalyses
        func_gnitt = auxiliaries.getNextIntervalTickTimestamp

        #[3]: Currency Analysis Check
        if caCode not in cas:
            return
        ca        = cas[caCode]
        ca_symbol = ca['currencySymbol']
        las_ca    = las[caCode]

        #[4]: Expected Check
        la_openTime = linearizedAnalysis['OPENTIME']
        if las_ca['lastReceived'] is not None:
            lr_klineTS = las_ca['lastReceived']
            #[4-1]: Timestamp Older
            if la_openTime < lr_klineTS: 
                self.__logger(message = (f"An Analysis Result Older Than Expected Received From {caCode}."
                                         f"\n * Symbol:        {ca_symbol}"
                                         f"\n * Last Received: {lr_klineTS}"
                                         f"\n * Received:      {la_openTime}"),
                              logType = 'Warning', 
                              color   = 'light_red')
                return
            
            #[4-2]: Timestamp Same, Simply Ignore
            if lr_klineTS == la_openTime:
                return
            
            #[4-3]: Timestamp newer, and skipped expected
            klineTS_expected = func_gnitt(intervalID = KLINTERVAL, timestamp = lr_klineTS, nTicks = 1)
            if klineTS_expected < la_openTime:
                self.__logger(message = (f"An Analysis Result Loss Detected From {caCode}."
                                         f"\n * Symbol:        {ca_symbol}"
                                         f"\n * Last Received: {lr_klineTS}"
                                         f"\n * Received:      {la_openTime}"),
                              logType = 'Warning', 
                              color   = 'light_red')
        las_ca['lastReceived'] = la_openTime
        
        #[5]: Analysis Result Save
        las_ca_data       = las_ca['data']
        las_ca_timestamps = las_ca['timestamps']
        if la_openTime not in las_ca_data: 
            las_ca_timestamps.append(la_openTime)
        las_ca_data[la_openTime] = linearizedAnalysis

        #[6]: Expired Analysis Results Handling
        expiredTS_latest = func_gnitt(intervalID = KLINTERVAL, timestamp = la_openTime, nTicks = -ANALYSISRESULT_BUFFERSIZE)
        while las_ca_timestamps[0] <= expiredTS_latest:
            del las_ca_data[las_ca_timestamps.popleft()]

        #[7]: Announcement
        for receiver in ca['appliedAccounts'].values():
            receiver(currencyAnalysisCode = caCode, 
                     symbol               = ca_symbol, 
                     linearizedAnalysis   = linearizedAnalysis)
    #IPC Handlers END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




    
    #Internal Handlers ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __readCurrencyAnalysisList(self):
        #[1]: Read Currency Analysis List
        #---[1-1]: Expected Read
        try:
            with open(self.__path_cal, 'r', encoding = 'utf-8') as f:
                cal = json.load(f)

        #---[1-2]: File Not Found
        except FileNotFoundError:
            cal = dict()

        #---[1-3]: Unexpected
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Read Currency Analysis List. User Attention Strongly Advised."
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')
            return

        #[2]: Add Currency Analysis
        for caCode, ca in cal.items():
            self.__addCurrencyAnalysis(code       = caCode, 
                                       symbol     = ca['currencySymbol'],
                                       configCode = ca['currencyAnalysisConfigurationCode'], 
                                       isImport   = True)
            
        #[3]: Save Currency Analysis List (In case of format changes due to manual edits)
        self.__saveCurrencyAnalysisList()
    
    def __saveCurrencyAnalysisList(self):
        #[1]: Directory Check
        self.__path_cal.parent.mkdir(parents=True, exist_ok=True)

        #[2]: Format currency analysis for saving
        ca_copy = dict()
        for caCode, ca in self.__currencyAnalyses.items():
            ca_copy[caCode] = {'currencySymbol':                    ca['currencySymbol'],
                               'currencyAnalysisConfigurationCode': ca['currencyAnalysisConfigurationCode']}
            
        #[3]: Save currency analysis list
        try:
            with open(self.__path_cal, 'w', encoding = 'utf-8') as f:
                json.dump(ca_copy, f, indent=4)

        #[4]: Exception Handling
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Save Currency Analysis List. User Attention Strongly Advised"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')
    
    def __addCurrencyAnalysis(self, code, symbol, configCode, isImport):
        #[1]: Instances
        currencies   = self.__currencies
        caConfigs    = self.__caConfigs
        aCentral     = self.__analyzers_central
        cas          = self.__currencyAnalyses
        cas_bySymbol = self.__currencyAnalyses_bySymbol
        las          = self.__linearizedAnalyses
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR
        func_logger      = self.__logger

        #[2]: Currency Analysis Code Check & Generation
        if code is None:
            uacIdx = 0
            code = f"UAC{uacIdx}"
            while code in cas:
                uacIdx += 1
                code = f"UAC{uacIdx}"
        elif code in cas: 
            func_logger(message = f"Currency Analysis '{code}' Add Failed. 'The Analysis Code Already Exists'", 
                        logType = 'Warning', 
                        color   = 'light_red')
            return {'result':     False, 
                    'responseOn': "ADDCURRENCYANALYSIS",
                    'message':    f"Currency Analysis '{code}' Add Failed. 'The Analysis Code Already Exists'"}

        #[3]: Currency Analysis By Symbol
        if symbol not in cas_bySymbol: 
            cas_bySymbol[symbol] = set()
        cas_bySymbol[symbol].add(code)

        #[4]: Initial Analysis Status
        cInfo = currencies.get(symbol, None)
        if cInfo is None: 
            initialStatus = 'CURRENCYNOTFOUND'
        else:
            cInfo_status = None if cInfo['info_server'] is None else cInfo['info_server']['status']
            if cInfo_status == 'TRADING': initialStatus = 'WAITINGSTREAM'
            else:                         initialStatus = 'WAITINGTRADING'

        #[5]: Analysis Configuration
        cac = caConfigs.getConfiguration(code = configCode)
        if initialStatus == 'WAITINGSTREAM' and cac is None: 
            initialStatus = 'CONFIGNOTFOUND'
        if cac is not None:
            caConfigs.attachCurrencyAnalysis(code = configCode, caCode = code)

        #[6]: Currency Analysis & Results
        ca = {'currencySymbol':                    symbol,
              'currencyAnalysisConfigurationCode': configCode,
              'currencyAnalysisConfiguration':     cac,
              'status':                            initialStatus,
              'allocatedAnalyzer':                 None,
              'appliedAccounts':                   dict()}
        las_ca = {'data':         dict(),
                  'timestamps':   deque(),
                  'lastReceived': None}
        cas[code] = ca
        las[code] = las_ca
        self.__updates.append({'type': 'NEW',
                               'code': code})

        #[7]: Analysis Central Update
        aCentral['nCurrencyAnalysis']['UNALLOCATED'] += 1
        func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis', 'UNALLOCATED'), prdContent = aCentral['nCurrencyAnalysis']['UNALLOCATED'])
        func_sendFAR(targetProcess = 'GUI', functionID = 'onAnalyzerCentralUpdate', functionParams = {'updatedContents': [('nCurrencyAnalysis', 'UNALLOCATED'),]}, farrHandler = None)

        #[8]: Configuration Update
        if not isImport: 
            self.__saveCurrencyAnalysisList()

        #[9]: IPC Announcement
        if not isImport:
            func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', code), prdContent = cas[code])
            func_sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'ADDED', 'currencyAnalysisCode': code}, farrHandler = None)

        #[10]: Analyzer Allocation
        if initialStatus == 'WAITINGSTREAM': 
            self.__allocateCurrencyAnalysisToAnAnalyzer(code = code)

        #[11]: Finally
        if not isImport: 
            func_logger(message = f"Currency Analysis '{code}' Successfully Added!", 
                        logType = 'Update',  
                        color   = 'light_green')
        return {'result':     True,  
                'responseOn': "ADDCURRENCYANALYSIS",
                'message':    f"Currency Analysis '{code}' Successfully Added!"}
    
    def __removeCurrencyAnalysis(self, code):
        #[1]: Instances
        caConfigs    = self.__caConfigs
        aCentral     = self.__analyzers_central
        analyzers    = self.__analyzers
        cas          = self.__currencyAnalyses
        cas_bySymbol = self.__currencyAnalyses_bySymbol
        las          = self.__linearizedAnalyses
        func_sendPRDEDIT   = self.__ipcA.sendPRDEDIT
        func_sendPRDREMOVE = self.__ipcA.sendPRDREMOVE
        func_sendFAR       = self.__ipcA.sendFAR

        #[2]: Existence Check
        ca = cas.get(code, None)
        if ca is None: 
            return {'result':               False,
                    'responseOn':           "REMOVECURRENCYANALYSIS",
                    'currencyAnalysisCode': code,
                    'message':              f"Currency Analysis '{code}' Removal Failed. Currency Analysis Does Not Exist."}
        appliedAccounts = ca['appliedAccounts']
        cSymbol         = ca['currencySymbol']
        allocAnalyzer   = ca['allocatedAnalyzer']

        #[3]: Applied Accounts Check
        if appliedAccounts:
            aIDs_str = ", ".join(f"'{aID}'" for aID in appliedAccounts)
            return {'result':               False, 
                    'responseOn':           "REMOVECURRENCYANALYSIS",
                    'currencyAnalysisCode': code,
                    'message':              f"Currency Analysis '{code}' Removal Failed. 'There Exist 1 Or More Attached Accounts [{aIDs_str}]'"}

        #[4]: Command the analyzer to remove the currency analysis
        if allocAnalyzer is not None:
            #[4-1]: Analyzer
            analyzer = analyzers[allocAnalyzer]
            #[4-2]: Command The Analyzer To Remove The Currency Analysis
            func_sendFAR(targetProcess  = analyzers[allocAnalyzer]['processName'], 
                         functionID     = 'removeCurrencyAnalysis', 
                         functionParams = {'currencyAnalysisCode': code}, 
                         farrHandler    = None)
            #[4-3]: Update The Analyzer Local Tracker
            analyzer['currencyAnalysisCodes'].remove(code)
            if not any(cas[caCode_other]['currencySymbol'] == cSymbol for caCode_other in analyzer['currencyAnalysisCodes']):
                analyzer['currencySymbols'].remove(cSymbol)

        #[5]: Detach From Currency Analysis Configuration
        ca_cacCode = ca['currencyAnalysisConfigurationCode']
        if ca_cacCode is not None:
            caConfigs.detachCurrencyAnalysis(code = ca_cacCode, caCode = code)
        
        #[6]: Remove the currency analysis data
        del cas[code]
        del las[code]
        cas_bySymbol[cSymbol].remove(code)
        if not cas_bySymbol[cSymbol]: del cas_bySymbol[cSymbol]

        #[7]: Counter Update
        acTarget = 'UNALLOCATED' if allocAnalyzer is None else allocAnalyzer
        aCentral['nCurrencyAnalysis'][acTarget] -= 1
        func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis', acTarget), prdContent = aCentral['nCurrencyAnalysis'][acTarget])
        func_sendFAR(targetProcess = 'GUI', functionID = 'onAnalyzerCentralUpdate', functionParams = {'updatedContents': [('nCurrencyAnalysis', acTarget),]}, farrHandler = None)

        #[8]: Save the config file
        self.__saveCurrencyAnalysisList()
        
        #[9]: Send the updated contents via PRDREMOVE and FAR
        func_sendPRDREMOVE(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', code))
        func_sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'REMOVED', 'currencyAnalysisCode': code}, farrHandler = None)
        return {'result':               True,
                'responseOn':           "REMOVECURRENCYANALYSIS",
                'currencyAnalysisCode': code,
                'message':              f"Currency Analysis '{code}' Successfully Removed!"}
        
    def __restartCurrencyAnalysis(self, code):
        #[1]: Instances
        caConfigs = self.__caConfigs
        analyzers = self.__analyzers
        cas       = self.__currencyAnalyses
        las       = self.__linearizedAnalyses
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR

        #[2]: Existence Check
        ca = cas.get(code, None)
        if ca is None: 
            return {'result':               False,
                    'responseOn':           "RESTARTCURRENCYANALYSIS",
                    'currencyAnalysisCode': code,
                    'message':              f"Currency Analysis '{code}' Restart Failed. Currency Analysis Does Not Exist."}
        allocAnalyzer = ca['allocatedAnalyzer']

        #[3]: Analyzer Check
        if allocAnalyzer is None:
            return {'result':               False,
                    'responseOn':           "RESTARTCURRENCYANALYSIS",
                    'currencyAnalysisCode': code,
                    'message':              f"Currency Analysis '{code}' Restart Failed. No Analyzer Allocated."}

        #[4]: Currency Analysis Configuration Check
        cacCode = ca['currencyAnalysisConfigurationCode']
        cac     = caConfigs.getConfiguration(code = cacCode)
        if cac is None:
            return {'result':               False,
                    'responseOn':           "RESTARTCURRENCYANALYSIS",
                    'currencyAnalysisCode': code,
                    'message':              f"Currency Analysis '{code}' Restart Failed. Currency Analysis Configuration '{cacCode}' Not Found."}

        #[5]: Currency Analysis Configuration Update
        ca['currencyAnalysisConfiguration'] = cac
        las_ca = las[code]
        las_ca['data'].clear()
        las_ca['timestamps'].clear()
        las_ca['lastReceived'] = None

        #[6]: Accounts Buffer Clearing Signal
        symbol = ca['currencySymbol']
        for receiver in ca['appliedAccounts'].values():
            receiver(currencyAnalysisCode = code, 
                     symbol               = symbol, 
                     linearizedAnalysis   = None)
        
        #[7]: Command The Analyzer To Restart The Currency Analysis
        if allocAnalyzer is not None:
            func_sendFAR(targetProcess  = analyzers[allocAnalyzer]['processName'], 
                         functionID     = 'restartCurrencyAnalysis', 
                         functionParams = {'currencyAnalysisCode':          code,
                                           'currencyAnalysisConfiguration': cac}, 
                         farrHandler    = None)
            
        #[8]: Result Dispatch
        func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', code, 'currencyAnalysisConfiguration'), prdContent = cac)
        func_sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_CURRENCYANALYSISCONFIGURATION', 'currencyAnalysisCode': code}, farrHandler = None)
        return {'result':               True,
                'responseOn':           "RESTARTCURRENCYANALYSIS",
                'currencyAnalysisCode': code,
                'message':              f"Currency Analysis '{code}' Successfully Restarted!"}
    
    def __allocateCurrencyAnalysisToAnAnalyzer(self, code):
        #[1]: Instances
        analyzers = self.__analyzers
        aCentral  = self.__analyzers_central
        ca        = self.__currencyAnalyses[code]
        cSymbol   = ca['currencySymbol']
        cacCode   = ca['currencyAnalysisConfigurationCode']
        cac       = ca['currencyAnalysisConfiguration']
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR

        #[2]: Determine Analyzer To Allocate
        aIdx_toAllocate = None
        #---[2-1]: Seek for any analyzer that already has the corresponding symbol analyzing
        for aIdx in range (len(analyzers)):
            if cSymbol in analyzers[aIdx]['currencySymbols']: 
                aIdx_toAllocate = aIdx
                break

        #---[2-2]: If this currency symbol is not allocated to any of the analyzers, find one with the minimum number of currency analysis
        if aIdx_toAllocate is None:
            nCAs_min = min([len(analyzers[aIdx]['currencyAnalysisCodes']) for aIdx in range (len(analyzers))])
            for aIdx in range (len(analyzers)):
                if len(analyzers[aIdx]['currencyAnalysisCodes']) == nCAs_min: 
                    aIdx_toAllocate = aIdx
                    break

        #[3]: Allocate Currency Analysis
        analyzer                = analyzers[aIdx_toAllocate]
        ca['allocatedAnalyzer'] = aIdx_toAllocate
        func_sendFAR(targetProcess  = analyzers[aIdx_toAllocate]['processName'],
                     functionID     = 'addCurrencyAnalysis',
                     functionParams = {'currencyAnalysisCode':              code,
                                       'currencySymbol':                    cSymbol,
                                       'currencyAnalysisConfigurationCode': cacCode,
                                       'currencyAnalysisConfiguration':     cac},
                     farrHandler = None)
        analyzer['currencyAnalysisCodes'].add(code)
        analyzer['currencySymbols'].add(cSymbol)
        aCentral['nCurrencyAnalysis'][aIdx_toAllocate] += 1
        aCentral['nCurrencyAnalysis']['UNALLOCATED']   -= 1

        #[4]: Analyzer Central Announcement
        func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis', aIdx_toAllocate), prdContent = aCentral['nCurrencyAnalysis'][aIdx_toAllocate])
        func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis', 'UNALLOCATED'),   prdContent = aCentral['nCurrencyAnalysis']['UNALLOCATED'])
        func_sendFAR(targetProcess = 'GUI', functionID = 'onAnalyzerCentralUpdate', functionParams = {'updatedContents': [('nCurrencyAnalysis', aIdx_toAllocate), ('nCurrencyAnalysis', 'UNALLOCATED')]}, farrHandler = None)

        #[5]: Currency Analysis Information Announcement
        func_sendPRDEDIT(targetProcess = 'GUI', 
                         prdAddress    = ('CURRENCYANALYSIS', code, 'allocatedAnalyzer'), 
                         prdContent    = ca['allocatedAnalyzer'])
        func_sendFAR(targetProcess  = 'GUI', 
                     functionID     = 'onCurrencyAnalysisUpdate', 
                     functionParams = {'updateType': 'UPDATE_ANALYZER', 'currencyAnalysisCode': code}, 
                     farrHandler    = None)

    def __logger(self, message, logType, color):
        if not self.__tmConfig[f'print_{logType}']:
            return
        time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
        msg      = f"[TRADEMANAGER-CAWORKER-{time_str}] {message}"
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
    
    def onCurrencyStatusUpdate(self, symbol, status):
        #[1]: Instances
        cas          = self.__currencyAnalyses
        cas_bySymbol = self.__currencyAnalyses_bySymbol
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR

        #[2]: Status Update Handling
        codes = cas_bySymbol.get(symbol, None)
        if not codes:
            return
        for code in codes:
            #[2-1]: Instances
            ca                = cas[code]
            ca_status         = ca['status']
            ca_status_updated = False

            #[2-2]: Currency Was Not Found
            if ca_status == 'CURRENCYNOTFOUND': 
                if status == 'TRADING': 
                    if ca['currencyAnalysisConfiguration'] is None: 
                        ca['status'] = 'CONFIGNOTFOUND'
                    else:                                             
                        ca['status'] = 'WAITINGSTREAM'
                        self.__allocateCurrencyAnalysisToAnAnalyzer(code = code)
                else:
                    ca['status'] = 'WAITINGTRADING'
                ca_status_updated = True

            #[2-3]: Currency Was Not Trading
            elif ca_status == 'WAITINGTRADING':
                if status == 'TRADING': 
                    if ca['currencyAnalysisConfiguration'] is None: 
                        ca['status'] = 'CONFIGNOTFOUND'
                    else: 
                        ca['status'] = 'WAITINGSTREAM'
                        self.__allocateCurrencyAnalysisToAnAnalyzer(code = code)
                    ca_status_updated = True

            #[2-4]: Currency Analysis Status Update Announcement
            if ca_status_updated:
                func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', code, 'status'), prdContent = ca['status'])
                func_sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_STATUS', 'currencyAnalysisCode': code}, farrHandler = None)
    
    def onNewCurrencyAnalysisConfiguration(self, cacCode):
        #[1]: Instances
        currencies = self.__currencies
        caConfigs  = self.__caConfigs
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR

        #[2]: Currency Analyses Update
        for code, ca in self.__currencyAnalyses.items():
            #[2-1]: Previous Configuration Check
            if ca['currencyAnalysisConfigurationCode'] != cacCode: continue
            if ca['currencyAnalysisConfiguration'] is not None:    continue

            #[2-2]: New Configuration Update
            ca['currencyAnalysisConfiguration'] = caConfigs.getConfiguration(code = cacCode)
            caConfigs.attachCurrencyAnalysis(code = cacCode, caCode = code)

            #[2-3]: Status Update
            if ca['status'] == 'CONFIGNOTFOUND':
                symbol = ca['currencySymbol']
                if symbol in currencies:
                    symbol_info_server = currencies[symbol]['info_server']
                    if symbol_info_server is not None and symbol_info_server['status'] == 'TRADING': ca['status'] = 'WAITINGSTREAM'
                    else:                                                                            ca['status'] = 'WAITINGTRADING'
                else:                                                                                ca['status'] = 'CURRENCYNOTFOUND'
                func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', code, 'currencyAnalysisConfiguration'), prdContent = ca['currencyAnalysisConfiguration'])
                func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', code, 'status'),                        prdContent = ca['status'])
                func_sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_STATUS', 'currencyAnalysisCode': code}, farrHandler = None)
                if ca['status'] == 'WAITINGSTREAM': 
                    self.__allocateCurrencyAnalysisToAnAnalyzer(code = code)
    
    def exists(self, code):
        #[1]: Code Check
        ca = self.__currencyAnalyses.get(code, None)
        return (ca is not None)

    def getCurrencyAnalysisSymbol(self, code):
        #[1]: Code Check
        ca = self.__currencyAnalyses.get(code, None)
        if ca is None:
            return None
        
        #[2]: Symbol
        return ca['currencySymbol']
    
    def getLinearizedAnalysis(self, code):
        #[1]: Code Check
        las_ca = self.__linearizedAnalyses.get(code, None)
        if las_ca is None:
            return None
        
        #[2]: Collect Linearized Analyses As Deque
        las_ca_data      = las_ca['data']
        las_ca_data_list = deque(las_ca_data[ts] for ts in las_ca['timestamps'])
        
        #[3]: Return Linearized Analysis
        return las_ca_data_list

    def isAttached(self, code, accountID):
        #[1]: Code Check
        ca = self.__currencyAnalyses.get(code, None)
        if ca is None:
            return False
        
        #[2]: Attachment Check
        return (accountID in ca['appliedAccounts'])

    def attachAccount(self, code, accountID, receiver):
        #[1]: Code Check
        ca = self.__currencyAnalyses.get(code, None)
        if ca is None:
            return
        
        #[2]: Attaching
        ca['appliedAccounts'][accountID] = receiver

    def detachAccount(self, code, accountID):
        #[1]: Code Check
        ca = self.__currencyAnalyses.get(code, None)
        if ca is None:
            return
        
        #[2]: Detaching
        ca['appliedAccounts'].pop(accountID, None)
    #External Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    
