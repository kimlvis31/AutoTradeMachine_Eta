#ATM Modules
import atmEta_IPC
import atmEta_Analyzers
import atmEta_Auxillaries
import atmEta_NeuralNetworks
import atmEta_Constants
from atmEta_Analyzers import KLINDEX_OPENTIME, KLINDEX_OPENPRICE, KLINDEX_CLOSEPRICE, KLINDEX_HIGHPRICE, KLINDEX_LOWPRICE
from managers.workers_currencyAnalysis import apw_analyzer_currencyAnalysis

#Python Modules
import time
import termcolor
import gc
import pprint
import torch
import random
import math
from collections import deque

#Constants
_IPC_THREADTYPE_MT         = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT         = atmEta_IPC._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = atmEta_IPC._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = atmEta_IPC._FAR_INVALIDFUNCTIONID

_AVERAGEANALYSISGENERATIONTIME_ANNOUNCEMENTINTERVAL_NS = 1e9
_AVERAGEANALYSISGENERATIONTIME_NSAMPLES                = 1000
_AVERAGEANALYSISGENERATIONTIME_KVALUE                  = 2/(_AVERAGEANALYSISGENERATIONTIME_NSAMPLES+1)

class Analyzer:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA, analyzerIndex):
        #IPC Assistance
        self.ipcA = ipcA

        #Analyzer ID
        self.analyzerIndex = analyzerIndex

        #Project Path
        self.path_project = path_project

        #Currency Analysis
        self.__currencyAnalysis = dict()
        self.__currencyAnalysis_currentPrep = None
        self.__currencyAnalysis_prepQueue   = deque()
        self.__marketDataSubscription       = dict()

        #Neural Networks
        self.__neuralNetworks_instances                      = dict()
        self.__neuralNetworks_referringAnalysisCodes         = dict()
        self.__neuralNetworks_connectionDataRequests_RIDs    = dict()
        self.__neuralNetworks_connectionDataRequests_CACodes = dict()

        #Analyzer Status Trackers
        self.__analyzerSummary = {'averageAnalysisGenerationTime_ns':   None,
                                  'currentlyPreparingCurrencyAnalysis': self.__currencyAnalysis_currentPrep}
        self.__averageAnalysisGenerationTime_lastAnnounced_ns = 0

        #FAR Registration
        self.ipcA.addFARHandler('addCurrencyAnalysis',                        self.__far_addCurrencyAnalysis,                        executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #TRADEMANAGER
        self.ipcA.addFARHandler('removeCurrencyAnalysis',                     self.__far_removeCurrencyAnalysis,                     executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #TRADEMANAGER
        self.ipcA.addFARHandler('restartCurrencyAnalysis',                    self.__far_restartCurrencyAnalysis,                    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #TRADEMANAGER
        self.ipcA.addFARHandler('onKlineStreamReceival',                      self.__far_onKlineStreamReceival,                      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #BINANCEAPI
        self.ipcA.addFARHandler('onDepthStreamReceival',                      self.__far_onDepthStreamReceival,                      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #BINANCEAPI
        self.ipcA.addFARHandler('onAggTradeStreamReceival',                   self.__far_onAggTradeStreamReceival,                   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #BINANCEAPI
        self.ipcA.addFARHandler('onCurrenciesUpdate',                         self.__far_onCurrenciesUpdate,                         executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #DATAMANAGER
        self.ipcA.addFARHandler('registerCurrencyAnalysisDataSubscription',   self.__far_registerCurrencyAnalysisDataSubscription,   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #GUI
        self.ipcA.addFARHandler('unregisterCurrencyAnalysisDataSubscription', self.__far_unregisterCurrencyAnalysisDataSubscription, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #GUI

        #IPCA PRD Formatting
        self.ipcA.formatPRD('DATAMANAGER', 'CURRENCIES', dict())

        #Process Control
        self.__processLoopContinue = True
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Process Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        self.ipcA.sendPRDEDIT(targetProcess = 'TRADEMANAGER', prdAddress = 'ANALYZERSUMMARY', prdContent = self.__analyzerSummary)
        while self.__processLoopContinue:
            #Process any existing FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()
            #Process Currency Analysis
            self.__process()
            #Process Loop Control
            self.__loopSleeper()

    def __loopSleeper(self):
        for ca in self.__currencyAnalysis.values():
            if ca.isBusy(): return
        time.sleep(0.001)

    def terminate(self, requester):
        self.__processLoopContinue = False
    #Manager Process Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Internal Functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __process(self):
        #[1]: Instances
        aSummary  = self.__analyzerSummary
        cas       = self.__currencyAnalysis
        ca_cPrep  = self.__currencyAnalysis_currentPrep
        ca_pQueue = self.__currencyAnalysis_prepQueue
        func_sendPRDEDIT = self.ipcA.sendPRDEDIT
        func_sendFAR     = self.ipcA.sendFAR

        #[2]: Preparation Queue
        if ca_cPrep is None and ca_pQueue:
            ca_pQueue = ca_pQueue.popleft()
            self.__currencyAnalysis_currentPrep = ca_pQueue
            aSummary['currentlyPreparingCurrencyAnalysis'] = ca_pQueue
            func_sendPRDEDIT(targetProcess = 'TRADEMANAGER', prdAddress = ('ANALYZERSUMMARY', 'currentlyPreparingCurrencyAnalysis'), prdContent = ca_pQueue)
            func_sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'onAnalyzerSummaryUpdate', functionParams = {'updatedSummary': 'currentlyPreparingCurrencyAnalysis'}, farrHandler = None)
            
        #[3]: Currency Analysis Processing
        aGenTimes = []
        for caCode, ca in cas.items():
            preparingCA = (caCode == ca_cPrep)
            #[3-1]: Processing
            aGenTime = ca.process(allowPrep = preparingCA)
            if aGenTime is not None: aGenTimes.append(aGenTime)

            #[3-2]: Preparing Target Update
            if preparingCA and ca.isRunning():
                self.__currencyAnalysis_currentPrep = None
                aSummary['currentlyPreparingCurrencyAnalysis'] = None
                func_sendPRDEDIT(targetProcess = 'TRADEMANAGER', prdAddress = ('ANALYZERSUMMARY', 'currentlyPreparingCurrencyAnalysis'), prdContent = None)
                func_sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'onAnalyzerSummaryUpdate', functionParams = {'updatedSummary': 'currentlyPreparingCurrencyAnalysis'}, farrHandler = None)

        #[4]: Average Analysis Generation Time Computation
        avgAGenTime_new = None
        if aGenTimes:
            avgAGenTime_new  = sum(aGenTimes)/len(aGenTimes)
            avgAGenTime_prev = aSummary['averageAnalysisGenerationTime_ns']
            if avgAGenTime_prev is None: avgAGenTime_new = aGenTime
            else:                        avgAGenTime_new = (aGenTime*_AVERAGEANALYSISGENERATIONTIME_KVALUE) + (avgAGenTime_prev*(1-_AVERAGEANALYSISGENERATIONTIME_KVALUE))
            aSummary['averageAnalysisGenerationTime_ns'] = avgAGenTime_new
            
        #[5]: Average Analysis Generation Time Announcement
        t_current_ns = time.perf_counter_ns()
        if avgAGenTime_new is not None and _AVERAGEANALYSISGENERATIONTIME_ANNOUNCEMENTINTERVAL_NS <= time.perf_counter_ns()-self.__averageAnalysisGenerationTime_lastAnnounced_ns:
            func_sendPRDEDIT(targetProcess = 'TRADEMANAGER',
                             prdAddress    = ('ANALYZERSUMMARY', 'averageAnalysisGenerationTime_ns'), 
                             prdContent    = avgAGenTime_new)
            func_sendFAR(targetProcess  = 'TRADEMANAGER',
                         functionID     = 'onAnalyzerSummaryUpdate', 
                         functionParams = {'updatedSummary': 'averageAnalysisGenerationTime_ns'}, 
                         farrHandler    = None)
            self.__averageAnalysisGenerationTime_lastAnnounced_ns = t_current_ns
    #Manager Internal Functions END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #FAR Handlers -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<TRADEMANAGER>
    def __far_addCurrencyAnalysis(self, requester, currencyAnalysisCode, currencySymbol, currencyAnalysisConfigurationCode, currencyAnalysisConfiguration):
        #[1]: Requester Check
        if requester != 'TRADEMANAGER': return

        #[2]: Instances
        cas          = self.__currencyAnalysis
        nn_instances = self.__neuralNetworks_instances
        nn_racs      = self.__neuralNetworks_referringAnalysisCodes
        nn_cdrs_rids = self.__neuralNetworks_connectionDataRequests_RIDs
        nn_cdrs_cacs = self.__neuralNetworks_connectionDataRequests_CACodes
        func_sendFAR = self.ipcA.sendFAR
        func_onncdrr = self.__farr_onNeuralNetworkConnectionsDataRequestResponse

        #[3]: Currency Analysis Generation
        ca = apw_analyzer_currencyAnalysis.CurrencyAnalysis(ipcA                              = self.ipcA,
                                                            neuralNetworks                    = self.__neuralNetworks_instances,
                                                            currencyAnalysisCode              = currencyAnalysisCode,
                                                            currencySymbol                    = currencySymbol,
                                                            currencyAnalysisConfigurationCode = currencyAnalysisConfigurationCode,
                                                            currencyAnalysisConfiguration     = currencyAnalysisConfiguration)
        cas[currencyAnalysisCode] = ca

        #[4]: Market Data Subscription
        mds = self.__marketDataSubscription
        if currencySymbol in mds:
            mds[currencySymbol].add(currencyAnalysisCode)
        else:
            mds[currencySymbol] = {currencyAnalysisCode,}
            func_sendFAR(targetProcess  = 'BINANCEAPI', 
                         functionID     = 'registerStreamSubscription', 
                         functionParams = {'subscriptionID': None, 
                                           'currencySymbol': currencySymbol}, 
                         farrHandler    = None)
            func_sendFAR(targetProcess  = 'DATAMANAGER', 
                         functionID     = 'registerCurrecnyInfoSubscription', 
                         functionParams = {'symbol': currencySymbol}, 
                         farrHandler    = None)
            
        #[5]: Neural Networks
        nnCodes = ca.getNeuralNetworkCodes()
        for nnCode in nnCodes:
            #[5-1]: Existing Check
            if nnCode in nn_instances: 
                nn_racs[nnCode].add(currencyAnalysisCode)
                continue
            #[5-1]: Requested Check
            if nnCode in nn_cdrs_cacs:
                nn_cdrs_cacs[nnCode].add(currencyAnalysisCode)
                continue
            #[5-2]: Request Dispatch
            rID = func_sendFAR(targetProcess  = "NEURALNETWORKMANAGER",
                               functionID     = 'getNeuralNetworkConnections',
                               functionParams = {'neuralNetworkCode': nnCode},
                               farrHandler    = func_onncdrr)
            nn_cdrs_rids[rID] = nnCode
            nn_cdrs_cacs[nnCode] = {currencyAnalysisCode,}
            
        #[6]: Preparation Queue
        self.__currencyAnalysis_prepQueue.append(currencyAnalysisCode)

    def __far_removeCurrencyAnalysis(self, requester, currencyAnalysisCode):
        #[1]: Requester Check
        if requester != 'TRADEMANAGER': return

        #[2]: Instances
        cas          = self.__currencyAnalysis
        ca_cp        = self.__currencyAnalysis_currentPrep
        ca_pq        = self.__currencyAnalysis_prepQueue
        nn_instances = self.__neuralNetworks_instances
        nn_racs      = self.__neuralNetworks_referringAnalysisCodes
        nn_cdrs_cacs = self.__neuralNetworks_connectionDataRequests_CACodes
        func_sendPRDEDIT = self.ipcA.sendPRDEDIT
        func_sendFAR     = self.ipcA.sendFAR

        #[3]: Currency Analysis Existence Check
        ca = cas.get(currencyAnalysisCode, None)
        if ca is None: return
        cSymbol = ca.getCurrencySymbol()

        #[4]: Market Data Subscription
        mds = self.__marketDataSubscription
        mds[cSymbol].remove(currencyAnalysisCode)
        if not mds[cSymbol]:
            del mds[cSymbol]
            func_sendFAR(targetProcess  = 'BINANCEAPI', 
                         functionID     = 'unregisterStreamSubscription', 
                         functionParams = {'subscriptionID': None, 'currencySymbol': cSymbol}, 
                         farrHandler    = None)
            func_sendFAR(targetProcess  = 'DATAMANAGER', 
                         functionID     = 'unregisterCurrecnyInfoSubscription', 
                         functionParams = {'symbol': cSymbol}, 
                         farrHandler    = None)
        
        #[5]: Neural Networks
        nnCodes = ca.getNeuralNetworkCodes()
        for nnCode in nnCodes:
            #[5-1]: Connection Data Request Tracker Update
            if nnCode in nn_cdrs_cacs:
                nn_cdrs_cacs[nnCode].remove(currencyAnalysisCode)
                if not nn_cdrs_cacs[nnCode]:
                    del nn_cdrs_cacs[nnCode]
            #[5-2]: Neural Network Referrer Update & Clearing
            if nnCode in nn_instances:
                nn_racs[nnCode].remove(currencyAnalysisCode)
                if not nn_racs[nnCode]:
                    del nn_instances[nnCode]
                    del nn_racs[nnCode]
        gc.collect()
        torch.cuda.empty_cache()

        #[6]: Currency Analysis
        del cas[currencyAnalysisCode]
        if ca_cp == currencyAnalysisCode:
            self.__currencyAnalysis_currentPrep                          = None
            self.__analyzerSummary['currentlyPreparingCurrencyAnalysis'] = None
            func_sendPRDEDIT(targetProcess = 'TRADEMANAGER', prdAddress = ('ANALYZERSUMMARY', 'currentlyPreparingCurrencyAnalysis'), prdContent = None)
            func_sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'onAnalyzerSummaryUpdate', functionParams = {'updatedSummary': 'currentlyPreparingCurrencyAnalysis'}, farrHandler = None)
        elif currencyAnalysisCode in ca_pq:
            ca_pq.remove(currencyAnalysisCode)

    def __far_restartCurrencyAnalysis(self, requester, currencyAnalysisCode):
        #[1]: Requester Check
        if requester != 'TRADEMANAGER': return
        
        #[2]: Currency Analysis Check
        ca = self.__currencyAnalysis.get(currencyAnalysisCode, None)
        if ca is None: return

        #[3]: Restart
        ca.restart()

    #<BINANCEAPI>
    def __far_onKlineStreamReceival(self, requester, symbol, kline):
        #[1]: Source Check
        if requester != 'BINANCEAPI':
            return

        #[2]: Instances
        cas = self.__currencyAnalysis
        mds = self.__marketDataSubscription

        #[3]: Subscription Check
        if symbol not in mds:
            return

        #[4]: Data Rerouting
        for caCode in mds[symbol]:
            cas[caCode].onDataStreamReceival(target = 'kline', stream = kline)

    def __far_onDepthStreamReceival(self, requester, symbol, depth):
        #[1]: Source Check
        if requester != 'BINANCEAPI':
            return

        #[2]: Instances
        cas = self.__currencyAnalysis
        mds = self.__marketDataSubscription

        #[3]: Subscription Check
        if symbol not in mds:
            return
        
        #[4]: Data Rerouting
        for caCode in mds[symbol]:
            cas[caCode].onDataStreamReceival(target = 'depth', stream = depth)

    def __far_onAggTradeStreamReceival(self, requester, symbol, aggTrade):
        #[1]: Source Check
        if requester != 'BINANCEAPI':
            return

        #[2]: Instances
        cas = self.__currencyAnalysis
        mds = self.__marketDataSubscription

        #[3]: Subscription Check
        if symbol not in mds:
            return

        #[4]: Data Rerouting
        for caCode in mds[symbol]:
            cas[caCode].onDataStreamReceival(target = 'aggTrade', stream = aggTrade)

    #<DATAMANAGER>
    def __far_onCurrenciesUpdate(self, requester, updatedContents):
        #[1]: Source Check
        if requester != 'DATAMANAGER':
            pass

        #[2]: Instances
        cas = self.__currencyAnalysis
        mds = self.__marketDataSubscription

        #[3]: Update Read
        for uContent in updatedContents:
            symbol = uContent['symbol']
            #[3-1]: Currency Analysis Response
            cInfo = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol))
            for caCode in mds[symbol]:
                cas[caCode].onCurrencyUpdate(currencyInfo = cInfo)

            #[3-2]: Local Read
            contentID      = uContent['id']
            contentID_type = type(contentID)
            if contentID_type == str:
                if contentID == '_ONFIRSTSUBSCRIPTION':
                    pass
            elif contentID_type == tuple: 
                pass
    
    #<GUI>
    def __far_registerCurrencyAnalysisDataSubscription(self, requester, requestID, currencyAnalysisCode, dataReceiver):
        #[1]: Source Check
        if requester != 'GUI':
            return None
        
        #[2]: Currency Analysis
        ca = self.__currencyAnalysis.get(currencyAnalysisCode, None)
        if ca is None:
            return None
        return ca.addSubscriber(subscriber = dataReceiver)
        
    def __far_unregisterCurrencyAnalysisDataSubscription(self, requester, currencyAnalysisCode, dataReceiver):
        #[1]: Source Check
        if requester != 'GUI':
            return
        
        #[2]: Currency Analysis Update
        ca = self.__currencyAnalysis.get(currencyAnalysisCode, None)
        if ca is None:
            return
        ca.removeSubscriber(subscriber = dataReceiver)

    #<NEURALNETWORK>
    def __farr_onNeuralNetworkConnectionsDataRequestResponse(self, responder, requestID, functionResult):
        #[1]: Responder Check
        if responder != 'NEURALNETWORKMANAGER': return

        #[2]: Instances
        cas          = self.__currencyAnalysis
        nn_instances = self.__neuralNetworks_instances
        nn_racs      = self.__neuralNetworks_referringAnalysisCodes
        nn_cdrs_rids = self.__neuralNetworks_connectionDataRequests_RIDs
        nn_cdrs_cacs = self.__neuralNetworks_connectionDataRequests_CACodes

        #[3]: Request ID Check
        if requestID not in nn_cdrs_rids: 
            return

        #[4]: Result Interpretation
        nnCode  = nn_cdrs_rids.pop(requestID)
        caCodes = nn_cdrs_cacs.pop(nnCode)
        #---[4-1]: Request Success
        if functionResult is not None:
            #[4-1-1]: Results
            neuralNetworkCode = functionResult['neuralNetworkCode']
            nKlines           = functionResult['nKlines']
            hiddenLayers      = functionResult['hiddenLayers']
            outputLayer       = functionResult['outputLayer']
            connections       = functionResult['connections']

            #[4-1-2]: Neural Network Code Check
            if neuralNetworkCode == nnCode:
                #[4-1-2-1]: Generate a local Neural Network Instance
                nn = atmEta_NeuralNetworks.neuralNetwork_MLP(nKlines      = nKlines, 
                                                             hiddenLayers = hiddenLayers, 
                                                             outputLayer  = outputLayer, 
                                                             device       = 'cpu')
                nn.importConnectionsData(connections = connections)
                nn.setEvaluationMode()
                nn_instances[nnCode] = nn
                nn_racs[nnCode]      = set()
                #[4-1-2-2]: Currency Analysis
                for caCode in caCodes:
                    ca = cas[caCode]
                    nn_racs[nnCode].add(caCode)
                    ca.onNeuralNetworkConnectionsDataArrival(neuralNetworkCode = nnCode)

        #---[4-2]: Request Fail
        else:
            for caCode in caCodes:
                ca = cas[caCode]
                ca.onNeuralNetworkConnectionsDataArrival(neuralNetworkCode = None)
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------