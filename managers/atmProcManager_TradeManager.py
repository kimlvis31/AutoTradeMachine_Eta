#ATM Modules
from atmEta_Analyzers import KLINDEX_OPENTIME, KLINDEX_CLOSETIME, KLINDEX_OPENPRICE, KLINDEX_CLOSEPRICE, KLINDEX_HIGHPRICE, KLINDEX_LOWPRICE
import atmEta_IPC
import atmEta_Auxillaries
import atmEta_Constants
import atmEta_RQPMFunctions

from managers.atmProcManager_Analyzer import _CURRENCYANALYSIS_STATUS_WAITINGNEURALNETWORKCONNECTIONSDATA
from managers.atmProcManager_Analyzer import _CURRENCYANALYSIS_STATUS_WAITINGSTREAM
from managers.atmProcManager_Analyzer import _CURRENCYANALYSIS_STATUS_WAITINGDATAAVAILABLE
from managers.atmProcManager_Analyzer import _CURRENCYANALYSIS_STATUS_PREPARING_QUEUED
from managers.atmProcManager_Analyzer import _CURRENCYANALYSIS_STATUS_PREPARING_ANALYZINGKLINES
from managers.atmProcManager_Analyzer import _CURRENCYANALYSIS_STATUS_ANALYZINGREALTIME
from managers.atmProcManager_Analyzer import _CURRENCYANALYSIS_STATUS_ERROR

#Python Modules
import time
import termcolor
import json
import os
import pprint
import bcrypt
import math
import random
from datetime import datetime, timezone, tzinfo

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

KLINTERVAL   = atmEta_Constants.KLINTERVAL
KLINTERVAL_S = atmEta_Constants.KLINTERVAL_S

_PIPGENERATIONCOMPUTATIONINTERVAL_NS = 1e9

_ACCOUNT_ACCOUNTTYPE_VIRTUAL = 'VIRTUAL'
_ACCOUNT_ACCOUNTTYPE_ACTUAL  = 'ACTUAL'
_ACCOUNT_ACCOUNTSTATUS_INACTIVE = 'INACTIVE'
_ACCOUNT_ACCOUNTSTATUS_ACTIVE   = 'ACTIVE'
_ACCOUNT_UPDATEINTERVAL_NS                   = 200e6
_ACCOUNT_HOURLYREPORTANNOUNCEMENTINTERVAL_NS = 60*1e9
_ACCOUNT_READABLEASSETS = ('USDT', 'USDC')
_ACCOUNT_ASSETPRECISIONS = {'USDT': 8,
                            'USDC': 8}
_ACCOUNT_BASEASSETALLOCATABLERATIO = 0.95
_GUIANNOUCEMENT_ASSETDATANAMES = {'marginBalance',
                                  'walletBalance',
                                  'isolatedWalletBalance',
                                  'isolatedPositionInitialMargin',
                                  'crossWalletBalance',
                                  'openOrderInitialMargin',
                                  'crossPositionInitialMargin',
                                  'crossMaintenanceMargin',
                                  'unrealizedPNL',
                                  'isolatedUnrealizedPNL',
                                  'crossUnrealizedPNL',
                                  'availableBalance',
                                  'assumedRatio',
                                  'allocatableBalance',
                                  'allocationRatio',
                                  'allocatedBalance',
                                  'weightedAssumedRatio',
                                  'commitmentRate',
                                  'riskLevel'}
_GUIANNOUCEMENT_POSITIONDATANAMES = {'tradeStatus',
                                     'tradable',
                                     'currencyAnalysisCode',
                                     'tradeConfigurationCode',
                                     'tradeControl',
                                     'quantity',
                                     'entryPrice',
                                     'leverage',
                                     'isolated',
                                     'isolatedWalletBalance',
                                     'positionInitialMargin',
                                     'openOrderInitialMargin',
                                     'maintenanceMargin',
                                     'currentPrice',
                                     'unrealizedPNL',
                                     'liquidationPrice',
                                     'assumedRatio',
                                     'priority',
                                     'allocatedBalance',
                                     'maxAllocatedBalance',
                                     'weightedAssumedRatio',
                                     'commitmentRate',
                                     'riskLevel'}
_VIRTUALACCOUNTDBANNOUNCEMENT_ASSETDATANAMES = {'crossWalletBalance',}
_VIRTUALACCOUNTDBANNOUNCEMENT_POSITIONDATANAMES = {'quantity',
                                                   'entryPrice',
                                                   'leverage',
                                                   'isolated',
                                                   'isolatedWalletBalance'}
_VIRTUALTRADE_MARKETTRADINGFEE = 0.0005
_VIRTUALTRADE_LIQUIDATIONFEE   = 0.0100
_ACTUALTRADE_MARKETTRADINGFEE  = 0.0005

_TRADE_PIPSIGNALFILTER_DISPATCHTIME_S  = 15
_TRADE_PIPSIGNALFILTER_KLINECLOSEPRICE = 0.005
_TRADE_MAXIMUMOCRGENERATIONATTEMPTS    = 5

_TRADE_TRADEHANDLER_LIFETIME_NS = int(KLINTERVAL_S*1e9/5)

_VIRTUALTRADE_SERVER_PROBABILITY_SUCCESS             = 1.00
_VIRTUALTRADE_SERVER_PROBABILITY_INCOMPLETEEXECUTION = 0.00

class procManager_TradeManager:
    #Manager Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, path_project, ipcA, analyzerProcessNames):
        print(termcolor.colored("   Initializing", 'green'), termcolor.colored("TRADEMANAGER Manager", 'light_blue'), termcolor.colored("--------------------------------------------------------------------------------------------------------------", 'green'))
        #IPC Assistance
        self.ipcA = ipcA
        #Project Path
        self.path_project = path_project

        #Analyzers Central
        self.__analyzers_central = {'nAnalyzers': len(analyzerProcessNames),
                                    'nCurrencyAnalysis_total':                {'total': 0},
                                    'nCurrencyAnalysis_unallocated':          0,
                                    'nCurrencyAnalysis_allocated':            0,
                                    'nCurrencyAnalysis_CONFIGNOTFOUND':       0,
                                    'nCurrencyAnalysis_CURRENCYNOTFOUND':     0,
                                    'nCurrencyAnalysis_WAITINGTRADING':       0,
                                    'nCurrencyAnalysis_WAITINGSTREAM':        {'total': 0},
                                    'nCurrencyAnalysis_WAITINGDATAAVAILABLE': {'total': 0},
                                    'nCurrencyAnalysis_PREPARING':            {'total': 0},
                                    'nCurrencyAnalysis_ANALYZINGREALTIME':    {'total': 0},
                                    'nCurrencyAnalysis_ERROR':                {'total': 0},
                                    'averagePIPGenerationTime_ns':   None}
        self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus = False
        self.__analyzers_central_recomputeAveragePIPGenerationTime   = False
        self.__analyzers_central_averagePIPGenerationLastComputed_ns = 0

        #Analyzers
        self.__analyzers = list()
        for analyzerProcessName in analyzerProcessNames:
            analyzerIndex = int(analyzerProcessName[8:])
            analyzerDescription = {'processName': analyzerProcessName,
                                   'allocated_currencyAnalysisCodes': set(),
                                   'allocated_currencySymbols':       set(),
                                   'averagePIPGenerationTime_ns':     None}
            self.__analyzers.append(analyzerDescription)
            self.__analyzers_central['nCurrencyAnalysis_total'][analyzerIndex]                = 0
            self.__analyzers_central['nCurrencyAnalysis_WAITINGSTREAM'][analyzerIndex]        = 0
            self.__analyzers_central['nCurrencyAnalysis_WAITINGDATAAVAILABLE'][analyzerIndex] = 0
            self.__analyzers_central['nCurrencyAnalysis_PREPARING'][analyzerIndex]            = 0
            self.__analyzers_central['nCurrencyAnalysis_ANALYZINGREALTIME'][analyzerIndex]    = 0
            self.__analyzers_central['nCurrencyAnalysis_ERROR'][analyzerIndex]                = 0
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'ANALYZERCENTRAL', prdContent = self.__analyzers_central)

        #Read TradeManager Configuration File
        self.__config_TradeManager = {'print_Update':  True,
                                      'print_Warning': True,
                                      'print_Error':   True}
        self.__readTradeManagerConfig()

        #Market Currencies
        self.__currencies           = dict()
        self.__currencies_lastKline = dict()

        #Read Analysis Configurations
        self.__currencyAnalysisConfigurations = dict()
        self.__readCurrencyAnalysisConfigurationsList()
        if (True): pass #---Print a summary of the imported analysis configurations
        for targetProcessName in ('GUI', 'SIMULATIONMANAGER'): self.ipcA.sendPRDEDIT(targetProcess = targetProcessName, prdAddress = 'CURRENCYANALYSISCONFIGURATIONS', prdContent = self.__currencyAnalysisConfigurations)

        #Read Analysis List
        self.__currencyAnalysis          = dict()
        self.__currencyAnalysis_bySymbol = dict()
        self.__readCurrencyAnalysisList()
        if (True): pass #---Print a summary of the imported analysis list
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CURRENCYANALYSIS', prdContent = self.__currencyAnalysis)

        #Read Trade Configurations
        self.__tradeConfigurations        = dict()
        self.__tradeConfigurations_loaded = dict()
        self.__readTradeConfigurationsList()
        if (): pass #---Print a summary of the imported trade configurations list
        for targetProcessName in ('GUI', 'SIMULATIONMANAGER'): self.ipcA.sendPRDEDIT(targetProcess = targetProcessName, prdAddress = 'TRADECONFIGURATIONS', prdContent = self.__tradeConfigurations)

        #Accounts & Trade
        self.__accounts                          = dict()
        self.__accountInstanceGenerationRequests = dict()
        self.__accounts_virtualServer            = dict()
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'ACCOUNTS', prdContent = self.__accounts)
        
        #Initial Data Share
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CONFIGURATION', prdContent = self.__config_TradeManager.copy())

        #FAR Registration
        #---DATAMANAGER
        self.ipcA.addFARHandler('onCurrenciesUpdate', self.__far_onCurrenciesUpdate, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---GUI
        self.ipcA.addFARHandler('updateConfiguration',                 self.__far_updateConfiguration,                 executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('addCurrencyAnalysisConfiguration',    self.__far_addCurrencyAnalysisConfiguration,    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('removeCurrencyAnalysisConfiguration', self.__far_removeCurrencyAnalysisConfiguration, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('addCurrencyAnalysis',                 self.__far_addCurrencyAnalysis,                 executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('removeCurrencyAnalysis',              self.__far_removeCurrencyAnalysis,              executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('restartCurrencyAnalysis',             self.__far_restartCurrencyAnalysis,             executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('addTradeConfiguration',               self.__far_addTradeConfiguration,               executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('removeTradeConfiguration',            self.__far_removeTradeConfiguration,            executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('addAccount',                          self.__far_addAccount,                          executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('removeAccount',                       self.__far_removeAccount,                       executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('activateAccount',                     self.__far_activateAccount,                     executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        self.ipcA.addFARHandler('deactivateAccount',                   self.__far_deactivateAccount,                   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('setAccountTradeStatus',               self.__far_setAccountTradeStatus,               executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('transferBalance',                     self.__far_transferBalance,                     executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('updateAllocationRatio',               self.__far_updateAllocationRatio,               executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('forceClearPosition',                  self.__far_forceClearPosition,                  executionThread = _IPC_THREADTYPE_MT, immediateResponse = False)
        self.ipcA.addFARHandler('updatePositionTradeStatus',           self.__far_updatePositionTradeStatus,           executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('updatePositionReduceOnly',            self.__far_updatePositionReduceOnly,            executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('updatePositionTraderParams',          self.__far_updatePositionTraderParams,          executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---ANALYZERS
        self.ipcA.addFARHandler('onAnalyzerSummaryUpdate',        self.__far_onAnalyzerSummaryUpdate,        executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onCurrencyAnalysisStatusUpdate', self.__far_onCurrencyAnalysisStatusUpdate, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onPIPGeneration',                self.__far_onPIPGeneration,                executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---BINANCEAPI
        self.ipcA.addFARHandler('onKlineStreamReceival', self.__far_onKlineStreamReceival, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onAccountDataReceival', self.__far_onAccountDataReceival, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

        #Process Control
        self.__processLoopContinue = True
        print(termcolor.colored("   TRADEMANAGER Manager", 'light_blue'), termcolor.colored("Initialization Complete! --------------------------------------------------------------------------------------------------", 'green'))
    #Manager Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    
    
    #Manager Process Functions ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def start(self):
        #Get currency info from DATAMANGER and register kline stream subscription to BINANCEAPI
        self.__currencies = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = 'CURRENCIES')
        for _symbol in self.__currencies: self.ipcA.sendFAR(targetProcess = 'BINANCEAPI', functionID = 'registerKlineStreamSubscription', functionParams = {'subscriptionID': None, 'currencySymbol': _symbol}, farrHandler = None)
        #---Update the status of any existing currencyAnalysis
        for currencySymbol in self.__currencyAnalysis_bySymbol:
            if (currencySymbol in self.__currencies):
                for currencyAnalysisCode in self.__currencyAnalysis_bySymbol[currencySymbol]:
                    _currencyAnalysis = self.__currencyAnalysis[currencyAnalysisCode]
                    if (self.__currencies[currencySymbol]['info_server'] == None): newStatus = None
                    else:                                                          newStatus = self.__currencies[currencySymbol]['info_server']['status']
                    if (newStatus == 'TRADING'):
                        _currencyAnalysis['status'] = 'WAITINGSTREAM'
                        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'status'), prdContent = _currencyAnalysis['status'])
                        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_STATUS', 'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)
                        self.__allocateCurrencyAnalysisToAnAnalzer(currencyAnalysisCode)
                    else:
                        _currencyAnalysis['status'] = 'WAITINGTRADING'
                        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'status'), prdContent = _currencyAnalysis['status'])
                        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_STATUS', 'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)
        #Get Account Data from DATAMANAGER
        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'loadAccountDescriptions', functionParams = None, farrHandler = self.__farr_onAccountDescriptionLoadRequestResponse)
        #Set Number of Currency Analysis By Status Computation Flag to be True
        self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus = True
        #Start Process Loop
        while (self.__processLoopContinue == True):
            #Process any existing FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()
            #Process Any Virtual Order Requests
            self.__trade_processVirtualServer()
            #Compute Number Of Currency Analysis By Status
            self.__computeNumberOfCurrencyAnalysisByStatus()
            #Compute Average PIP Generation Time
            self.__computeAveragePIPGenerationTime()
            #Update Accounts
            self.__updateAccounts()
            #Loop Sleep
            time.sleep(0.001)
    def terminate(self, requester):
        self.__processLoopContinue = False
    #Manager Process Functions END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Manager Internal Functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #---Process Configuration
    def __readTradeManagerConfig(self):
        #Configuration File Read
        try:
            configFile = open(os.path.join(self.path_project, 'configs', 'tmConfig.config'), 'r')
            self.__config_TradeManager = json.loads(configFile.read())
            configFile.close()
        except: self.__saveTradeManagerConfig()
        #Contents Verification
        if (('print_Update'  not in self.__config_TradeManager) or (self.__config_TradeManager['print_Update']  != True)): self.__config_TradeManager['print_Update']  = False
        if (('print_Warning' not in self.__config_TradeManager) or (self.__config_TradeManager['print_Warning'] != True)): self.__config_TradeManager['print_Warning'] = False
        if (('print_Error'   not in self.__config_TradeManager) or (self.__config_TradeManager['print_Error']   != True)): self.__config_TradeManager['print_Error']   = False
    def __saveTradeManagerConfig(self):
        configFile = open(os.path.join(self.path_project, 'configs', 'tmConfig.config'), 'w')
        configFile.write(json.dumps(self.__config_TradeManager))
        configFile.close()

    #---Currency Analysis Configurations
    def __readCurrencyAnalysisConfigurationsList(self):
        try:
            configFile = open(os.path.join(self.path_project, 'data', 'tm', 'cacl.bin'), 'r')
            for currencyAnalysisConfigurations_json in configFile.readlines():
                currencyAnalysisConfigurations_formatted = json.loads(currencyAnalysisConfigurations_json)
                currencyAnalysisConfigurationCode = currencyAnalysisConfigurations_formatted[0]
                currencyAnalysisConfiguration     = currencyAnalysisConfigurations_formatted[1]
                self.__addCurrencyAnalysisConfiguration(currencyAnalysisConfigurationCode = currencyAnalysisConfigurationCode, currencyAnalysisConfiguration = currencyAnalysisConfiguration, saveConfig = False, sendIPCM = False)
            configFile.close()
        except: self.__saveCurrencyAnalysisConfigurationsList()
    def __saveCurrencyAnalysisConfigurationsList(self):
        configFile = open(os.path.join(self.path_project, 'data', 'tm', 'cacl.bin'), 'w')
        currencyAnalysisConfigurations_formatted = [json.dumps((currencyAnalysisConfigurationCode, self.__currencyAnalysisConfigurations[currencyAnalysisConfigurationCode]))+"\n" for currencyAnalysisConfigurationCode in self.__currencyAnalysisConfigurations]
        configFile.writelines(currencyAnalysisConfigurations_formatted)
        configFile.close()
    def __addCurrencyAnalysisConfiguration(self, currencyAnalysisConfigurationCode, currencyAnalysisConfiguration, saveConfig = True, sendIPCM = True):
        #Check the configuration code. If 'None' is passed, generated an indexed and unnamed code
        if (currencyAnalysisConfigurationCode == None):
            unnamedCurrencyAnalysisConfigurationIndex = 0
            while (currencyAnalysisConfigurationCode == None):
                _currencyAnalysisConfigurationCode = "UACC{:d}".format(unnamedCurrencyAnalysisConfigurationIndex) #UACC: Unnamed Analysis Configuration Code
                if (_currencyAnalysisConfigurationCode not in self.__currencyAnalysisConfigurations): currencyAnalysisConfigurationCode = _currencyAnalysisConfigurationCode
                else: unnamedCurrencyAnalysisConfigurationIndex += 1
            currencyAnalysisConfigurationCodeTestPass = True
        elif (currencyAnalysisConfigurationCode not in self.__currencyAnalysisConfigurations): currencyAnalysisConfigurationCodeTestPass = True
        else:                                                                                  currencyAnalysisConfigurationCodeTestPass = False
        #If configuration code test passed
        if (currencyAnalysisConfigurationCodeTestPass == True):
            try:
                #Save the currency analysis configuration
                self.__currencyAnalysisConfigurations[currencyAnalysisConfigurationCode] = currencyAnalysisConfiguration
                if (saveConfig == True): self.__saveCurrencyAnalysisConfigurationsList()
                #Check for any currency analysis that uses this configuration code
                for currencyAnalysisCode in self.__currencyAnalysis:
                    _currencyAnalysis = self.__currencyAnalysis[currencyAnalysisCode]
                    if ((_currencyAnalysis['currencyAnalysisConfigurationCode'] == currencyAnalysisConfigurationCode) and (_currencyAnalysis['currencyAnalysisConfiguration'] == None)):
                        _currencyAnalysis['currencyAnalysisConfiguration'] = self.__currencyAnalysisConfigurations[currencyAnalysisConfigurationCode].copy()
                        if (_currencyAnalysis['status'] == 'CONFIGNOTFOUND'):
                            currencySymbol = _currencyAnalysis['currencySymbol']
                            if (currencySymbol in self.__currencies):
                                if (self.__currencies[currencySymbol]['info_server'] != None) and (self.__currencies[currencySymbol]['info_server']['status'] == 'TRADING'): _currencyAnalysis['status'] = 'WAITINGSTREAM'
                                else:                                                                                                                                        _currencyAnalysis['status'] = 'WAITINGTRADING'
                            else:                                                                                                                                            _currencyAnalysis['status'] = 'CURRENCYNOTFOUND'
                            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'currencyAnalysisConfiguration'), prdContent = _currencyAnalysis['currencyAnalysisConfiguration'])
                            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'status'),                        prdContent = _currencyAnalysis['status'])
                            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_STATUS', 'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)
                            if (_currencyAnalysis['status'] == 'WAITINGSTREAM'): self.__allocateCurrencyAnalysisToAnAnalzer(currencyAnalysisCode)
                            #Raise Number of Currency Analysis By Status Recomputation Flag
                            self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus = True
                #If 'sendIPCM' is True, announce the updated information individually
                if (sendIPCM == True):
                    for targetProcessName in ('GUI', 'SIMULATIONMANAGER'):
                        self.ipcA.sendPRDEDIT(targetProcess = targetProcessName, prdAddress = ('CURRENCYANALYSISCONFIGURATIONS', currencyAnalysisConfigurationCode), prdContent = self.__currencyAnalysisConfigurations[currencyAnalysisConfigurationCode])
                        self.ipcA.sendFAR(targetProcess = targetProcessName, functionID = 'onCurrencyAnalysisConfigurationUpdate', functionParams = {'updateType': 'ADDED', 'currencyAnalysisConfigurationCode': currencyAnalysisConfigurationCode}, farrHandler = None)
                return                    {'result': True,  'message': "Currency Analysis Configuration '{:s}' Successfully Added!".format(currencyAnalysisConfigurationCode)}
            except Exception as e: return {'result': False, 'message': "Currency Analysis Configuration '{:s}' Add Failed Due To An Unexpected Error. '{:s}'".format(currencyAnalysisConfigurationCode, str(e))}
        return                            {'result': False, 'message': "Currency Analysis Configuration '{:s}' Add Failed. 'The Configuration Code Already Exists'".format(currencyAnalysisConfigurationCode)}
    def __removeCurrencyAnalysisConfiguration(self, currencyAnalysisConfigurationCode):
        #Check if the currecny analysis configuraiton code exists
        if (currencyAnalysisConfigurationCode in self.__currencyAnalysisConfigurations):
            del self.__currencyAnalysisConfigurations[currencyAnalysisConfigurationCode]
            self.__saveCurrencyAnalysisConfigurationsList()
            for targetProcessName in ('GUI', 'SIMULATIONMANAGER'):
                self.ipcA.sendPRDREMOVE(targetProcess = targetProcessName, prdAddress = ('CURRENCYANALYSISCONFIGURATIONS', currencyAnalysisConfigurationCode))
                self.ipcA.sendFAR(targetProcess = targetProcessName, functionID = 'onCurrencyAnalysisConfigurationUpdate', functionParams = {'updateType': 'REMOVED', 'currencyAnalysisConfigurationCode': currencyAnalysisConfigurationCode}, farrHandler = None)
            return {'result': True, 'message': "Currency Analysis Configuration '{:s}' Removal Succcessful!".format(currencyAnalysisConfigurationCode)}
        else: return {'result': False, 'message': "Currency Analysis Configuration '{:s}' Removal Failed. 'The Configuration Code Does Not Exist'".format(currencyAnalysisConfigurationCode)}

    #---Currency Analysis
    def __readCurrencyAnalysisList(self):
        try:
            configFile = open(os.path.join(self.path_project, 'data', 'tm', 'cal.bin'), 'r')
            for currencyAnalysis_json in configFile.readlines():
                currencyAnalysis_formatted = json.loads(currencyAnalysis_json)
                analysisCode     = currencyAnalysis_formatted[0]
                analysisSettings = currencyAnalysis_formatted[1]
                self.__addCurrencyAnalysis(currencyAnalysisCode              = analysisCode, 
                                           currencySymbol                    = analysisSettings['currencySymbol'],
                                           currencyAnalysisConfigurationCode = analysisSettings['currencyAnalysisConfigurationCode'], 
                                           saveConfig = False, silentTerminal = True, sendIPCM = False)
            configFile.close()
        except: self.__saveCurrencyAnalysisList()
    def __saveCurrencyAnalysisList(self):
        configFile = open(os.path.join(self.path_project, 'data', 'tm', 'cal.bin'), 'w')
        currencyAnalysis_formatted = list()
        for currencyAnalysisCode in self.__currencyAnalysis:
            _currencyAnalysis = self.__currencyAnalysis[currencyAnalysisCode]
            _currencyAnalysis_toSave_json = json.dumps((currencyAnalysisCode, {'currencySymbol':                    _currencyAnalysis['currencySymbol'],
                                                                               'currencyAnalysisConfigurationCode': _currencyAnalysis['currencyAnalysisConfigurationCode']}))
            currencyAnalysis_formatted.append(_currencyAnalysis_toSave_json+"\n")
        configFile.writelines(currencyAnalysis_formatted)
        configFile.close()
    def __addCurrencyAnalysis(self, currencyAnalysisCode, currencySymbol, currencyAnalysisConfigurationCode, saveConfig = True, silentTerminal = False, sendIPCM = True):
        #[1}: Currency Analysis Code Generation or validity test
        if (currencyAnalysisCode == None):
            unnamedAnalysisCodeIndex = 0
            while (currencyAnalysisCode == None):
                _currencyAnalysisCode = "UAC{:d}".format(unnamedAnalysisCodeIndex) #UAC: Unnamed Analysis Code
                if (_currencyAnalysisCode not in self.__currencyAnalysis): currencyAnalysisCode = _currencyAnalysisCode
                else: unnamedAnalysisCodeIndex += 1
            validityTest_currencyAnalysisCode = True
        elif (currencyAnalysisCode not in self.__currencyAnalysis): validityTest_currencyAnalysisCode = True
        #[2]: The currency analysis code validity test has passed
        if (validityTest_currencyAnalysisCode == True):
            try:
                #Update currency analysis set by currency symbols
                if (currencySymbol not in self.__currencyAnalysis_bySymbol): self.__currencyAnalysis_bySymbol[currencySymbol] = set()
                self.__currencyAnalysis_bySymbol[currencySymbol].add(currencyAnalysisCode)
                #Determine initial analysis status based on the currency status
                if (currencySymbol in self.__currencies):
                    if (self.__currencies[currencySymbol]['info_server'] != None) and (self.__currencies[currencySymbol]['info_server']['status'] == 'TRADING'): initialStatus = 'WAITINGSTREAM'
                    else:                                                                                                                                        initialStatus = 'WAITINGTRADING'
                else:                                                                                                                                            initialStatus = 'CURRENCYNOTFOUND'
                #Get currency analysis configuration
                if (currencyAnalysisConfigurationCode in self.__currencyAnalysisConfigurations): currencyAnalysisConfiguration = self.__currencyAnalysisConfigurations[currencyAnalysisConfigurationCode].copy()
                else:                                                                            currencyAnalysisConfiguration = None
                if ((initialStatus == 'WAITINGSTREAM') and (currencyAnalysisConfiguration == None)): initialStatus = 'CONFIGNOTFOUND'
                #Construct currency analysis trackers 
                _currencyAnalysis = {'currencySymbol':                    currencySymbol,
                                     'currencyAnalysisConfigurationCode': currencyAnalysisConfigurationCode,
                                     'currencyAnalysisConfiguration':     currencyAnalysisConfiguration,
                                     'status':                            initialStatus,
                                     'allocatedAnalyzer':                 None,
                                     'appliedAccounts':                   set()}
                self.__currencyAnalysis[currencyAnalysisCode] = _currencyAnalysis
                #If the config needs to be saved, save the updated currency analysis list
                if (saveConfig == True): self.__saveCurrencyAnalysisList()
                #If this needs to be sent via PRD and FAR separately, send it
                if (sendIPCM == True):
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode), prdContent = self.__currencyAnalysis[currencyAnalysisCode])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'ADDED', 'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)
                #If thie initial status is 'WAITINGSTREAM', allocate the analysis to an analyzer
                if (initialStatus == 'WAITINGSTREAM'): self.__allocateCurrencyAnalysisToAnAnalzer(currencyAnalysisCode, sendIPCM = sendIPCM)
                #If there exist any account positions that refer to this currency analysis, register
                for _localID in self.__accounts:
                    _position = self.__accounts[_localID]['positions'][currencySymbol]
                    if (_position['currencyAnalysisCode'] == currencyAnalysisCode):
                        _tradable_prev    = _position['tradable']
                        _tradeStatus_prev = _position['tradeStatus']
                        self.__registerPositionToCurrencyAnalysis(localID = _localID, positionSymbol = currencySymbol, currencyAnalysisCode = currencyAnalysisCode)
                        self.__checkPositionTradability(localID = _localID, positionSymbol = currencySymbol)
                        if (sendIPCM == True): 
                            if (_position['tradable'] != _tradable_prev):
                                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', _localID, 'positions', currencySymbol, 'tradable'), prdContent = _position['tradable'])
                                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (_localID, currencySymbol, 'tradable')}, farrHandler = None)
                            if (_position['tradeStatus'] != _tradeStatus_prev):
                                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', _localID, 'positions', currencySymbol, 'tradeStatus'), prdContent = _position['tradeStatus'])
                                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (_localID, currencySymbol, 'tradeStatus')}, farrHandler = None)
                #Raise Number of Currency Analysis By Status Recomputation Flag
                self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus = True
                #Result
                _addResult = 1
            except Exception as e: _addResult = -1; _addResult_exception = e
        else:                      _addResult = -2
        #[3}: Result Announcing
        if (silentTerminal == False):
            if   (_addResult ==  1): self.__logger(message = f"Currency Analysis '{currencyAnalysisCode}' Successfully Added!",                                                   logType = 'Update',  color = 'light_green')
            elif (_addResult == -1): self.__logger(message = f"Currency Analysis '{currencyAnalysisCode}' Add Failed Due To An Unexpected Error\n * {str(_addResult_exception)}", logType = 'Error',   color = 'light_red')
            elif (_addResult == -2): self.__logger(message = f"Currency Analysis '{currencyAnalysisCode}' Add Failed. 'The Analysis Code Already Exists'",                        logType = 'Warning', color = 'light_red')
        if (sendIPCM == True):
            if   (_addResult ==  1): return {'result': True,  'message': "Currency Analysis '{:s}' Successfully Added!".format(currencyAnalysisCode)}
            elif (_addResult == -1): return {'result': False, 'message': "Currency Analysis '{:s}' Add Failed Due To An Unexpected Error. '{:s}'".format(currencyAnalysisCode, str(_addResult_exception))}
            elif (_addResult == -2): return {'result': False, 'message': "Currency Analysis '{:s}' Add Failed. 'Check Analysis Code'".format(currencyAnalysisCode)}
    def __removeCurrencyAnalysis(self, currencyAnalysisCode):
        if (currencyAnalysisCode in self.__currencyAnalysis):
            #Retreive some neccessary data for temporary purpose
            currencySymbol    = self.__currencyAnalysis[currencyAnalysisCode]['currencySymbol']
            allocatedAnalyzer = self.__currencyAnalysis[currencyAnalysisCode]['allocatedAnalyzer']
            #Command the analyzer to remove the currency analysis
            if (allocatedAnalyzer != None): self.ipcA.sendFAR(targetProcess = self.__analyzers[allocatedAnalyzer]['processName'], functionID = 'removeCurrencyAnalysis', functionParams = {'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)
            #Remove the currency analysis data
            del self.__currencyAnalysis[currencyAnalysisCode]
            self.__currencyAnalysis_bySymbol[currencySymbol].remove(currencyAnalysisCode)
            if (len(self.__currencyAnalysis_bySymbol[currencySymbol]) == 0): del self.__currencyAnalysis_bySymbol[currencySymbol]
            #Update the local analyzers tracker
            if (allocatedAnalyzer != None):
                self.__analyzers[allocatedAnalyzer]['allocated_currencyAnalysisCodes'].remove(currencyAnalysisCode)
                _removeCurrencySymbol = True
                for otherAnalysisCode in self.__analyzers[allocatedAnalyzer]['allocated_currencyAnalysisCodes']:
                    if (self.__currencyAnalysis[otherAnalysisCode]['currencySymbol'] == currencySymbol): _removeCurrencySymbol = False; break
                if (_removeCurrencySymbol == True): self.__analyzers[allocatedAnalyzer]['allocated_currencySymbols'].remove(currencySymbol)
            #Save the config file
            self.__saveCurrencyAnalysisList()
            #If there exist any account positions that referred to this currency analysis, unregister
            for _localID in self.__accounts:
                _position = self.__accounts[_localID]['positions'][currencySymbol]
                if (_position['currencyAnalysisCode'] == currencyAnalysisCode):
                    _tradable_prev    = _position['tradable']
                    _tradeStatus_prev = _position['tradeStatus']
                    #Unregister currency analysis
                    self.__unregisterPositionFromCurrencyAnalysis(localID = _localID, positionSymbol = currencySymbol)
                    #Update tradability & trade status and announce
                    self.__checkPositionTradability(localID = _localID, positionSymbol = currencySymbol)
                    if (_position['tradable'] != _tradable_prev):
                        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', _localID, 'positions', currencySymbol, 'tradable'), prdContent = _position['tradable'])
                        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (_localID, currencySymbol, 'tradable')}, farrHandler = None)
                    if (_position['tradeStatus'] != _tradeStatus_prev):
                        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', _localID, 'positions', currencySymbol, 'tradeStatus'), prdContent = _position['tradeStatus'])
                        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (_localID, currencySymbol, 'tradeStatus')}, farrHandler = None)
            #Send the updated contents via PRDREMOVE and FAR
            self.ipcA.sendPRDREMOVE(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode))
            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'REMOVED', 'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)
            #Raise Number of Currency Analysis By Status Recomputation Flag
            self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus = True
    def __restartCurrencyAnalysis(self, currencyAnalysisCode):
        if (currencyAnalysisCode in self.__currencyAnalysis):
            pass
    def __allocateCurrencyAnalysisToAnAnalzer(self, currencyAnalysisCode, sendIPCM = True):
        #Get currency analysis info
        currencySymbol                    = self.__currencyAnalysis[currencyAnalysisCode]['currencySymbol']
        currencyAnalysisConfigurationCode = self.__currencyAnalysis[currencyAnalysisCode]['currencyAnalysisConfigurationCode']
        currencyAnalysisConfiguration     = self.__currencyAnalysis[currencyAnalysisCode]['currencyAnalysisConfiguration']
        #Determine analyzer to allocate
        analyzerIndex_toAllocate = None
        #---Seek for any analyzer that already has the corresponding symbol analyzing
        for analyzerIndex in range (len(self.__analyzers)):
            if (currencySymbol in self.__analyzers[analyzerIndex]['allocated_currencySymbols']): analyzerIndex_toAllocate = analyzerIndex; break
        #---If this currency symbol is not allocated to any of the analyzers, find one with the minimum number of currency analysis
        if (analyzerIndex_toAllocate == None):
            nCurrencyAnalysis_min = min([len(self.__analyzers[analyzerIndex]['allocated_currencyAnalysisCodes']) for analyzerIndex in range (len(self.__analyzers))])
            for analyzerIndex in range (len(self.__analyzers)):
                if (len(self.__analyzers[analyzerIndex]['allocated_currencyAnalysisCodes']) == nCurrencyAnalysis_min): analyzerIndex_toAllocate = analyzerIndex; break
        #Allocate analyzer and command the analyzer the preapre the currency analysis
        self.__currencyAnalysis[currencyAnalysisCode]['allocatedAnalyzer'] = analyzerIndex_toAllocate
        self.ipcA.sendFAR(targetProcess  = self.__analyzers[analyzerIndex_toAllocate]['processName'],
                          functionID     = 'addCurrencyAnalysis',
                          functionParams = {'currencyAnalysisCode':              currencyAnalysisCode,
                                            'currencySymbol':                    currencySymbol,
                                            'currencyAnalysisConfigurationCode': currencyAnalysisConfigurationCode,
                                            'currencyAnalysisConfiguration':     currencyAnalysisConfiguration},
                          farrHandler = None)
        self.__analyzers[analyzerIndex_toAllocate]['allocated_currencyAnalysisCodes'].add(currencyAnalysisCode)
        self.__analyzers[analyzerIndex_toAllocate]['allocated_currencySymbols'].add(currencySymbol)
        if (sendIPCM == True):
            #Notify currencyAnalysis update to GUI
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'allocatedAnalyzer'), prdContent = self.__currencyAnalysis[currencyAnalysisCode]['allocatedAnalyzer'])
            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_ANALYZER', 'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)
        #Raise Number of Currency Analysis By Status Recomputation Flag
        self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus = True
    def __computeNumberOfCurrencyAnalysisByStatus(self):
        if (self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus == True):
            #New tracker formatting
            newTracker = {'nCurrencyAnalysis_total':                {'total': 0},
                          'nCurrencyAnalysis_unallocated':          0,
                          'nCurrencyAnalysis_allocated':            0,
                          'nCurrencyAnalysis_CONFIGNOTFOUND':       0,
                          'nCurrencyAnalysis_CURRENCYNOTFOUND':     0,
                          'nCurrencyAnalysis_WAITINGTRADING':       0,
                          'nCurrencyAnalysis_WAITINGSTREAM':        {'total': 0},
                          'nCurrencyAnalysis_WAITINGDATAAVAILABLE': {'total': 0},
                          'nCurrencyAnalysis_PREPARING':            {'total': 0},
                          'nCurrencyAnalysis_ANALYZINGREALTIME':    {'total': 0},
                          'nCurrencyAnalysis_ERROR':                {'total': 0}}
            for analyzerIndex in range (len(self.__analyzers)):
                newTracker['nCurrencyAnalysis_total'][analyzerIndex]                = 0
                newTracker['nCurrencyAnalysis_WAITINGSTREAM'][analyzerIndex]        = 0
                newTracker['nCurrencyAnalysis_WAITINGDATAAVAILABLE'][analyzerIndex] = 0
                newTracker['nCurrencyAnalysis_PREPARING'][analyzerIndex]            = 0
                newTracker['nCurrencyAnalysis_ANALYZINGREALTIME'][analyzerIndex]    = 0
                newTracker['nCurrencyAnalysis_ERROR'][analyzerIndex]                = 0
            #New tracker update
            for currencyAnalysisCode in self.__currencyAnalysis:
                _currencyAnalysis = self.__currencyAnalysis[currencyAnalysisCode]
                _currencyAnalysis_allocatedAnalyzer = _currencyAnalysis['allocatedAnalyzer']
                _currencyAnalysis_status            = _currencyAnalysis['status']
                newTracker['nCurrencyAnalysis_total']['total'] += 1
                if (_currencyAnalysis_allocatedAnalyzer == None): newTracker['nCurrencyAnalysis_unallocated'] += 1
                else:                                             newTracker['nCurrencyAnalysis_allocated']   += 1
                if   (_currencyAnalysis_status == 'CONFIGNOTFOUND'):   newTracker['nCurrencyAnalysis_CONFIGNOTFOUND']   += 1
                elif (_currencyAnalysis_status == 'CURRENCYNOTFOUND'): newTracker['nCurrencyAnalysis_CURRENCYNOTFOUND'] += 1
                elif (_currencyAnalysis_status == 'WAITINGTRADING'):   newTracker['nCurrencyAnalysis_WAITINGTRADING']   += 1
                elif (_currencyAnalysis_status == 'WAITINGSTREAM'):        newTracker['nCurrencyAnalysis_WAITINGSTREAM']['total']        += 1; newTracker['nCurrencyAnalysis_WAITINGSTREAM'][_currencyAnalysis_allocatedAnalyzer]        += 1; newTracker['nCurrencyAnalysis_total'][_currencyAnalysis_allocatedAnalyzer] += 1
                elif (_currencyAnalysis_status == 'WAITINGDATAAVAILABLE'): newTracker['nCurrencyAnalysis_WAITINGDATAAVAILABLE']['total'] += 1; newTracker['nCurrencyAnalysis_WAITINGDATAAVAILABLE'][_currencyAnalysis_allocatedAnalyzer] += 1; newTracker['nCurrencyAnalysis_total'][_currencyAnalysis_allocatedAnalyzer] += 1
                elif (_currencyAnalysis_status == 'PREP_QUEUED'):          newTracker['nCurrencyAnalysis_PREPARING']['total']            += 1; newTracker['nCurrencyAnalysis_PREPARING'][_currencyAnalysis_allocatedAnalyzer]            += 1; newTracker['nCurrencyAnalysis_total'][_currencyAnalysis_allocatedAnalyzer] += 1
                elif (_currencyAnalysis_status == 'PREP_ANALYZINGKLINES'): newTracker['nCurrencyAnalysis_PREPARING']['total']            += 1; newTracker['nCurrencyAnalysis_PREPARING'][_currencyAnalysis_allocatedAnalyzer]            += 1; newTracker['nCurrencyAnalysis_total'][_currencyAnalysis_allocatedAnalyzer] += 1
                elif (_currencyAnalysis_status == 'ANALYZINGREALTIME'):    newTracker['nCurrencyAnalysis_ANALYZINGREALTIME']['total']    += 1; newTracker['nCurrencyAnalysis_ANALYZINGREALTIME'][_currencyAnalysis_allocatedAnalyzer]    += 1; newTracker['nCurrencyAnalysis_total'][_currencyAnalysis_allocatedAnalyzer] += 1
                elif (_currencyAnalysis_status == 'ERROR'):                newTracker['nCurrencyAnalysis_ERROR']['total']                += 1; newTracker['nCurrencyAnalysis_ERROR'][_currencyAnalysis_allocatedAnalyzer]                += 1; newTracker['nCurrencyAnalysis_total'][_currencyAnalysis_allocatedAnalyzer] += 1
            #Previous & new tracker comparison
            updatedContents = list()
            for sortType in ('total', 'WAITINGSTREAM', 'WAITINGDATAAVAILABLE', 'PREPARING', 'ANALYZINGREALTIME', 'ERROR'):
                dataName = 'nCurrencyAnalysis_{:s}'.format(sortType)
                for alloc in self.__analyzers_central[dataName]:
                    if (self.__analyzers_central[dataName][alloc] != newTracker[dataName][alloc]):
                        self.__analyzers_central[dataName][alloc] = newTracker[dataName][alloc]
                        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ANALYZERCENTRAL', dataName, alloc), prdContent = self.__analyzers_central[dataName][alloc])
                        updatedContents.append((dataName, alloc))
            for sortType in ('unallocated', 'allocated', 'CONFIGNOTFOUND', 'CURRENCYNOTFOUND', 'WAITINGTRADING'):
                dataName = 'nCurrencyAnalysis_{:s}'.format(sortType)
                if (self.__analyzers_central[dataName] != newTracker[dataName]):
                    self.__analyzers_central[dataName] = newTracker[dataName]
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ANALYZERCENTRAL', dataName), prdContent = self.__analyzers_central[dataName])
                    updatedContents.append(dataName)
            if (0 < len(updatedContents)): self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAnalyzerCentralUpdate', functionParams = {'updatedContents': updatedContents}, farrHandler = None)
            #Lower the flag
            self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus = False
    def __computeAveragePIPGenerationTime(self):
        t_current_ns = time.perf_counter_ns()
        if (self.__analyzers_central_recomputeAveragePIPGenerationTime == True) and (_PIPGENERATIONCOMPUTATIONINTERVAL_NS <= t_current_ns-self.__analyzers_central_averagePIPGenerationLastComputed_ns):
            averagePIPGenerationTime_ns_sum = 0
            nEffectiveAnalyzers             = 0
            for _analyzer in self.__analyzers:
                if (_analyzer['averagePIPGenerationTime_ns'] != None): 
                    nEffectiveAnalyzers += 1
                    averagePIPGenerationTime_ns_sum += _analyzer['averagePIPGenerationTime_ns']
            if (nEffectiveAnalyzers == 0): averagePIPGenerationTime_ns = None
            else:                          averagePIPGenerationTime_ns = round(averagePIPGenerationTime_ns_sum/nEffectiveAnalyzers)
            self.__analyzers_central['averagePIPGenerationTime_ns'] = averagePIPGenerationTime_ns
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ANALYZERCENTRAL', 'averagePIPGenerationTime_ns'), prdContent = averagePIPGenerationTime_ns)
            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAnalyzerCentralUpdate', functionParams = {'updatedContents': ['averagePIPGenerationTime_ns',]}, farrHandler = None)
            self.__analyzers_central_recomputeAveragePIPGenerationTime   = False
            self.__analyzers_central_averagePIPGenerationLastComputed_ns = t_current_ns

    #---Trade Configurations
    def __readTradeConfigurationsList(self):
        try:
            configFile = open(os.path.join(self.path_project, 'data', 'tm', 'tcl.bin'), 'r')
            for tradeConfigurations_json in configFile.readlines():
                tradeConfigurations_formatted = json.loads(tradeConfigurations_json)
                tradeConfigurationCode = tradeConfigurations_formatted[0]
                tradeConfiguration     = tradeConfigurations_formatted[1]
                self.__addTradeConfiguration(tradeConfigurationCode = tradeConfigurationCode, tradeConfiguration = tradeConfiguration, saveConfig = False, sendIPCM = False)
            configFile.close()
        except: self.__saveTradeConfigurationsList()
    def __saveTradeConfigurationsList(self):
        configFile = open(os.path.join(self.path_project, 'data', 'tm', 'tcl.bin'), 'w')
        tradeConfigurations_formatted = [json.dumps((tradeConfigurationCode, self.__tradeConfigurations[tradeConfigurationCode]))+"\n" for tradeConfigurationCode in self.__tradeConfigurations]
        configFile.writelines(tradeConfigurations_formatted)
        configFile.close()
    def __addTradeConfiguration(self, tradeConfigurationCode, tradeConfiguration, saveConfig = True, sendIPCM = True):
        #Check the configuration code. If 'None' is passed, generated an indexed and unnamed code
        if (tradeConfigurationCode == None):
            unnamedTradeConfigurationIndex = 0
            while (tradeConfigurationCode == None):
                _tradeConfigurationCode = "UTCC{:d}".format(unnamedTradeConfigurationIndex) #UTCC: Unnamed Trade Configuration Code
                if (_tradeConfigurationCode not in self.__tradeConfigurations): tradeConfigurationCode = _tradeConfigurationCode
                else: unnamedTradeConfigurationIndex += 1
            tradeConfigurationCodeTestPass = True
        elif (tradeConfigurationCode not in self.__tradeConfigurations): tradeConfigurationCodeTestPass = True
        else:                                                            tradeConfigurationCodeTestPass = False
        #If configuration code test passed
        if (tradeConfigurationCodeTestPass == True):
            try:
                #Save the trade configuration
                self.__tradeConfigurations[tradeConfigurationCode] = tradeConfiguration
                if (saveConfig == True): self.__saveTradeConfigurationsList()
                #If there exist any account positions that refer to this trade configuration, register
                for _localID in self.__accounts:
                    for _positionSymbol in self.__accounts[_localID]['positions']:
                        _position = self.__accounts[_localID]['positions'][_positionSymbol]
                        if (_position['tradeConfigurationCode'] == tradeConfigurationCode):
                            _tradable_prev    = _position['tradable']
                            _tradeStatus_prev = _position['tradeStatus']
                            self.__registerPositionTradeConfiguration(localID = _localID, positionSymbol = _positionSymbol, tradeConfigurationCode = tradeConfigurationCode)
                            self.__checkPositionTradability(localID = _localID, positionSymbol = _positionSymbol)
                            if (sendIPCM == True): 
                                if (_position['tradable'] != _tradable_prev):
                                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', _localID, 'positions', _positionSymbol, 'tradable'), prdContent = _position['tradable'])
                                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (_localID, _positionSymbol, 'tradable')}, farrHandler = None)
                                if (_position['tradeStatus'] != _tradeStatus_prev):
                                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', _localID, 'positions', _positionSymbol, 'tradeStatus'), prdContent = _position['tradeStatus'])
                                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (_localID, _positionSymbol, 'tradeStatus')}, farrHandler = None)
                #If 'sendIPCM' is True, announce the updated information individually
                if (sendIPCM == True):
                    for targetProcessName in ('GUI', 'SIMULATIONMANAGER'):
                        self.ipcA.sendPRDEDIT(targetProcess = targetProcessName, prdAddress = ('TRADECONFIGURATIONS', tradeConfigurationCode), prdContent = self.__tradeConfigurations[tradeConfigurationCode])
                        self.ipcA.sendFAR(targetProcess = targetProcessName, functionID = 'onTradeConfigurationUpdate', functionParams = {'updateType': 'ADDED', 'tradeConfigurationCode': tradeConfigurationCode}, farrHandler = None)
                return                    {'result': True,  'message': "Trade Configuration '{:s}' Successfully Added!".format(tradeConfigurationCode)}
            except Exception as e: return {'result': False, 'message': "Trade Configuration '{:s}' Add Failed Due To An Unexpected Error. '{:s}'".format(tradeConfigurationCode, str(e))}
        return                            {'result': False, 'message': "Trade Configuration '{:s}' Add Failed. 'The Configuration Code Already Exists'".format(tradeConfigurationCode)}
    def __removeTradeConfiguration(self, tradeConfigurationCode):
        #Check if the currecny analysis configuraiton code exists
        if (tradeConfigurationCode in self.__tradeConfigurations):
            del self.__tradeConfigurations[tradeConfigurationCode]
            self.__saveTradeConfigurationsList()
            for targetProcessName in ('GUI', 'SIMULATIONMANAGER'):
                self.ipcA.sendPRDREMOVE(targetProcess = targetProcessName, prdAddress = ('TRADECONFIGURATIONS', tradeConfigurationCode))
                self.ipcA.sendFAR(targetProcess = targetProcessName, functionID = 'onTradeConfigurationUpdate', functionParams = {'updateType': 'REMOVED', 'tradeConfigurationCode': tradeConfigurationCode}, farrHandler = None)
            return {'result': True, 'message': "Trade Configuration '{:s}' Removal Succcessful!".format(tradeConfigurationCode)}
        else: return {'result': False, 'message': "Trade Configuration '{:s}' Removal Failed. 'The Configuration Code Does Not Exist'".format(tradeConfigurationCode)}

    #---Accounts
    def __addAccount(self, localID, buid, accountType, password, newAccount = True, assets = None, positions = None, lastHourlyReport = None, silentTerminal = False, sendIPCM = True):
        #[1]: Account Name Validity Test
        if ((localID != None) and (localID not in self.__accounts)): validityTest_accountName = True
        else:                                                        validityTest_accountName = False
        #[2]: Account Generation
        if (validityTest_accountName == True):
            try:
                #Initial Format
                _account = {'accountType':    accountType,
                            'buid':           None,
                            'hashedPassword': None,
                            'assets':         dict(),
                            'positions':      dict(),
                            'status':         None,
                            'tradeStatus':    False,
                            '_lastUpdated':   0,
                            '_generatedPIPs': dict(),
                            '_expectedPIPTS': dict(),
                            '_hourlyReport':                  None,
                            '_hourlyReport_hourTS':           None,
                            '_hourlyReport_lastAnnounced_ns': 0}
                self.__accounts[localID] = _account
                if (accountType == _ACCOUNT_ACCOUNTTYPE_VIRTUAL):
                    _account_virtualServer = {'assets':    dict(),
                                              'positions': dict(),
                                              '_marginTypeControlRequests': list(),
                                              '_leverageControlRequests':   list(),
                                              '_orderCreationRequests':     dict(),
                                              '_nonZeroQuantityPositions_isolated': list(),
                                              '_nonZeroQuantityPositions_cross':    list(),
                                              '_lastUpdated':               0}
                    self.__accounts_virtualServer[localID] = _account_virtualServer
                #BUID (Binance User ID)
                if   (accountType == _ACCOUNT_ACCOUNTTYPE_VIRTUAL): _account['buid'] = None
                elif (accountType == _ACCOUNT_ACCOUNTTYPE_ACTUAL):  _account['buid'] = int(buid)
                #Password
                if (newAccount == True): _account['hashedPassword'] = bcrypt.hashpw(password=password.encode(encoding = "utf-8"), salt=bcrypt.gensalt())
                else:                    _account['hashedPassword'] = password
                #Status
                if   (accountType == _ACCOUNT_ACCOUNTTYPE_VIRTUAL): _account['status'] = _ACCOUNT_ACCOUNTSTATUS_ACTIVE
                elif (accountType == _ACCOUNT_ACCOUNTTYPE_ACTUAL):  _account['status'] = _ACCOUNT_ACCOUNTSTATUS_INACTIVE
                #Assets & Positions Formatting
                for _assetName in _ACCOUNT_READABLEASSETS: self.__formatNewAccountAsset(localID = localID, assetName = _assetName)
                for _currencySymbol in self.__currencies:
                    if (self.__currencies[_currencySymbol]['quoteAsset'] in _ACCOUNT_READABLEASSETS): self.__formatNewAccountPosition(localID = localID, currencySymbol = _currencySymbol)
                for _assetName in _ACCOUNT_READABLEASSETS: self.__sortPositionSymbolsByPriority(localID = localID, assetName = _assetName)
                #If is not a new account, import assets & positions, and last hourly report if needed
                if (newAccount == False): 
                    self.__updateAccount(localID             = localID, importedData = {'source': 'DB', 'positions': positions, 'assets': assets})
                    self.__updateAccountHourlyReport(localID = localID, importedData = lastHourlyReport)
                #If new account, send account data save request to DATAMANAGER
                if (newAccount == True): self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'addAccountDescription', functionParams = {'localID': localID, 'accountDescription': _account}, farrHandler = None)
                #If this needs to be sent via PRD and FAR separately, send it
                if (sendIPCM == True):
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID), prdContent = self.__accounts[localID])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'ADDED', 'updatedContent': localID}, farrHandler = None)
                _addResult = 1
            except Exception as e: _addResult = -1; _addResult_exception = e
        else:                      _addResult = -2
        #[3]: Result Announcing
        if (silentTerminal == False):
            if   (_addResult ==  1): self.__logger(message = f"Account '{localID}' Successfully Added!",                                                   logType = 'Update',  color = 'light_green')
            elif (_addResult == -1): self.__logger(message = f"Account '{localID}' Add Failed Due To An Unexpected Error\n * {str(_addResult_exception)}", logType = 'Error',   color = 'light_red')
            elif (_addResult == -2): self.__logger(message = f"Account '{localID}' Add Failed. 'Check Account Name'",                                      logType = 'Warning', color = 'light_red')
        if (sendIPCM == True):
            if   (_addResult ==  1): return {'result': True,  'message': "Account '{:s}' Successfully Added!".format(localID)}
            elif (_addResult == -1): return {'result': False, 'message': "Account '{:s}' Add Failed Due To An Unexpected Error. '{:s}'".format(localID, str(_addResult_exception))}
            elif (_addResult == -2): return {'result': False, 'message': "Account '{:s}' Add Failed. 'Check Account Name'".format(localID)}
    def __formatNewAccountAsset(self, localID, assetName):
        _account = self.__accounts[localID]
        _account['assets'][assetName] = {'marginBalance':                 0,
                                         'walletBalance':                 0,
                                         'isolatedWalletBalance':         0,
                                         'isolatedPositionInitialMargin': 0,
                                         'crossWalletBalance':            0,
                                         'openOrderInitialMargin':        0,
                                         'crossPositionInitialMargin':    0,
                                         'crossMaintenanceMargin':        0, 
                                         'unrealizedPNL':                 0,
                                         'isolatedUnrealizedPNL':         0,
                                         'crossUnrealizedPNL':            0,
                                         'availableBalance':              0,
                                         #Positional Distribution
                                         'assumedRatio':       0,
                                         'allocatableBalance': 0,
                                         'allocationRatio':    0.500,
                                         'allocatedBalance':   0,
                                         #Risk Management
                                         'weightedAssumedRatio': 0,
                                         'commitmentRate':       None,
                                         'riskLevel':            None,
                                         #Internal Management
                                         '_positionSymbols':                set(),
                                         '_positionSymbols_crossed':        set(),
                                         '_positionSymbols_isolated':       set(),
                                         '_positionSymbols_prioritySorted': list()}
        if (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL):
            _account_virtualServer = self.__accounts_virtualServer[localID]
            _account_virtualServer['assets'][assetName] = {'marginBalance':      0,
                                                           'walletBalance':      0,
                                                           'crossWalletBalance': 0,
                                                           'availableBalance':   0}
    def __formatNewAccountPosition(self, localID, currencySymbol):
        _account  = self.__accounts[localID]
        _currency = self.__currencies[currencySymbol]
        _account['positions'][currencySymbol] = {'quoteAsset': _currency['quoteAsset'],
                                                 'precisions': _currency['precisions'],
                                                 'tradeStatus':             False,
                                                 'reduceOnly':              False,
                                                 'tradable':                False,
                                                 'currencyAnalysisCode':    None,
                                                 'tradeConfigurationCode':  None,
                                                 #Base
                                                 'quantity':                0,
                                                 'entryPrice':              None,
                                                 'leverage':                1,
                                                 'isolated':                True,
                                                 'isolatedWalletBalance':   0,
                                                 'positionInitialMargin':   0,
                                                 'openOrderInitialMargin':  0,
                                                 'maintenanceMargin':       0,
                                                 'currentPrice':            None,
                                                 'unrealizedPNL':           None,
                                                 'liquidationPrice':        None,
                                                 #Trade Control
                                                 'tradeControl': self.__getInitializedTradeControl(tradeControlMode = None),
                                                 #Positional Distribution
                                                 'assumedRatio':        0,
                                                 'priority':            len(_account['positions'])+1,
                                                 'allocatedBalance':    0,
                                                 'maxAllocatedBalance': float('inf'),
                                                 #Risk Management
                                                 'weightedAssumedRatio':  None,
                                                 'commitmentRate':        None,
                                                 'riskLevel':             None,
                                                 'abruptClearingRecords': list(),
                                                 #Server Interaction Control
                                                 '_tradabilityTests':           0b000,
                                                 '_marginTypeControlRequested': False,
                                                 '_leverageControlRequested':   False,
                                                 '_tradeHandlers':              list(),
                                                 '_orderCreationRequest':       None}
        _account['assets'][_currency['quoteAsset']]['_positionSymbols'].add(currencySymbol)
        _account['assets'][_currency['quoteAsset']]['_positionSymbols_isolated'].add(currencySymbol)
        _account['assets'][_currency['quoteAsset']]['_positionSymbols_prioritySorted'].append(currencySymbol)
        if (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL):
            _account_virtualServer = self.__accounts_virtualServer[localID]
            _account_virtualServer['positions'][currencySymbol] = {'quantity':               0,
                                                                   'entryPrice':             None,
                                                                   'leverage':               1,
                                                                   'isolated':               True,
                                                                   'isolatedWalletBalance':  0,
                                                                   'positionInitialMargin':  0,
                                                                   'openOrderInitialMargin': 0,
                                                                   'maintenanceMargin':      0,
                                                                   'unrealizedPNL':          0}
    def __getInitializedTradeControl(self, tradeControlMode):
        _tc_initialized = {'tcMode': tradeControlMode}
        if (tradeControlMode == 'TS'): 
            _tc_initialized['ts_maximumProfitPrice']        = None
            _tc_initialized['ts_takeProfitPrice']           = None
            _tc_initialized['ts_stopLossPrice']             = None
            _tc_initialized['ts_partialTakeProfitExecuted'] = False
            _tc_initialized['ts_initialQuantity']           = None
            _tc_initialized['ts_fslcTrigger']               = None
        elif (tradeControlMode == 'RQPM'):
            _tc_initialized['rqpm_entryTimestamp']  = None
            _tc_initialized['rqpm_initialQuantity'] = None
            _tc_initialized['rqpm_fslcTrigger']     = None
        return _tc_initialized
    def __copyTradeControl(self, tradeControl):
        _tc_copied = {'tcMode': tradeControl['tcMode']}
        if (tradeControl['tcMode'] == 'TS'):
            _tc_copied['ts_maximumProfitPrice']        = tradeControl['ts_maximumProfitPrice']
            _tc_copied['ts_takeProfitPrice']           = tradeControl['ts_takeProfitPrice']
            _tc_copied['ts_stopLossPrice']             = tradeControl['ts_stopLossPrice']
            _tc_copied['ts_partialTakeProfitExecuted'] = tradeControl['ts_partialTakeProfitExecuted']
            _tc_copied['ts_initialQuantity']           = tradeControl['ts_initialQuantity']
            _tc_copied['ts_fslcTrigger']               = tradeControl['ts_fslcTrigger']
        elif (tradeControl['tcMode'] == 'RQPM'):
            _tc_copied['rqpm_entryTimestamp']  = tradeControl['rqpm_entryTimestamp']
            _tc_copied['rqpm_initialQuantity'] = tradeControl['rqpm_initialQuantity']
            _tc_copied['rqpm_fslcTrigger']     = tradeControl['rqpm_fslcTrigger']
        return _tc_copied
    def __getUpdatedTradeControl(self, localID, positionSymbol, tradeControlUpdate, updateMode):
        #Account & Position Instances
        _account  = self.__accounts[localID]
        _position = _account['positions'][positionSymbol]
        #Updated Trade Control
        _updatedTradeControl = {'tcMode': tradeControlUpdate['tcMode']}
        #---[1]: TCMode: Trade Scenario
        if (tradeControlUpdate['tcMode'] == 'TS'):
            _updatedTradeControl['ts_maximumProfitPrice']        = tradeControlUpdate['ts_maximumProfitPrice'][updateMode]
            _updatedTradeControl['ts_takeProfitPrice']           = tradeControlUpdate['ts_takeProfitPrice'][updateMode]
            _updatedTradeControl['ts_stopLossPrice']             = tradeControlUpdate['ts_stopLossPrice'][updateMode]
            _updatedTradeControl['ts_partialTakeProfitExecuted'] = tradeControlUpdate['ts_partialTakeProfitExecuted'][updateMode]
            _updatedTradeControl['ts_initialQuantity']           = tradeControlUpdate['ts_initialQuantity'][updateMode]
            _updatedTradeControl['ts_fslcTrigger']               = tradeControlUpdate['ts_fslcTrigger'][updateMode]
        #---[2]: TCMode: RQPM
        elif (tradeControlUpdate['tcMode'] == 'RQPM'):
            #[1]: Entry Timestamp
            _updatedTradeControl['rqpm_entryTimestamp'] = tradeControlUpdate['rqpm_entryTimestamp'][updateMode]
            #[2]: Initial Quantity
            _newVal = tradeControlUpdate['rqpm_initialQuantity'][updateMode]
            if (_newVal == '#ABSQUANTITY#'): _updatedTradeControl['rqpm_initialQuantity'] = abs(_position['quantity'])
            else:                            _updatedTradeControl['rqpm_initialQuantity'] = _newVal
            #[3]: Full Stop Loss Close Timestamp
            _updatedTradeControl['rqpm_fslcTrigger'] = tradeControlUpdate['rqpm_fslcTrigger'][updateMode]
        #Finally
        return _updatedTradeControl
    def __updateAccounts(self):
        for localID in self.__accounts_virtualServer:
            _account               = self.__accounts[localID]
            _account_virtualServer = self.__accounts_virtualServer[localID]
            #Account Data Update
            if (_ACCOUNT_UPDATEINTERVAL_NS < time.perf_counter_ns()-_account['_lastUpdated']): 
                self.__updateAccount(localID = localID, importedData = {'source': 'VIRTUALSERVER', 'positions': _account_virtualServer['positions'], 'assets': _account_virtualServer['assets']})
                self.__updateAccountHourlyReport(localID = localID, importedData = None)
    def __updateAccount(self, localID, importedData):
        _account = self.__accounts[localID]
        _account['_lastUpdated'] = time.perf_counter_ns()
        _assets    = _account['assets']
        _positions = _account['positions']
        if (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL): _account_virtualServer = self.__accounts_virtualServer[localID]; _account_virtualServer_assets = _account_virtualServer['assets']; _account_virtualServer_positions = _account_virtualServer['positions']
        else:                                                         _account_virtualServer = None;                                   _account_virtualServer_assets = None;                             _account_virtualServer_positions = None
        #[1]: Imported Data Check
        _importSource = importedData['source']; _assets_imported = importedData['assets']; _positions_imported = importedData['positions']
        #[2]: Account Update
        #---[2-1]: Initial Import From DB
        if (_importSource == 'DB'):
            #[1]: Read Positions Data
            for _pSymbol in _positions_imported:
                if (_pSymbol in _positions):
                    _position          = _positions[_pSymbol]
                    _position_imported = _positions_imported[_pSymbol]
                    #[1-1]: Direct values import & Formatting
                    _position['tradeStatus']  = _position_imported['tradeStatus']
                    _position['reduceOnly']   = _position_imported['reduceOnly']
                    self.__registerPositionToCurrencyAnalysis(localID = localID, positionSymbol = _pSymbol, currencyAnalysisCode   = _position_imported['currencyAnalysisCode'])
                    self.__registerPositionTradeConfiguration(localID = localID, positionSymbol = _pSymbol, tradeConfigurationCode = _position_imported['tradeConfigurationCode'])
                    _position['tradeControl'] = _position_imported['tradeControl']
                    _position['quantity']               = None
                    _position['entryPrice']             = None
                    _position['leverage']               = None
                    _position['isolated']               = None
                    _position['isolatedWalletBalance']  = None
                    _position['openOrderInitialMargin'] = None
                    _position['positionInitialMargin']  = None
                    _position['currentPrice']           = None
                    _position['unrealizedPNL']          = None
                    _position['liquidationPrice']       = None
                    _position['assumedRatio']           = _position_imported['assumedRatio']
                    _position['priority']               = _position_imported['priority']
                    _position['maxAllocatedBalance']    = _position_imported['maxAllocatedBalance']
                    _position['abruptClearingRecords']  = _position_imported['abruptClearingRecords']
                    if (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL):
                        _position_virtualServer = _account_virtualServer_positions[_pSymbol]
                        _position_virtualServer['quantity']               = _position_imported['quantity']
                        _position_virtualServer['entryPrice']             = _position_imported['entryPrice']
                        _position_virtualServer['leverage']               = _position_imported['leverage']
                        _position_virtualServer['isolated']               = _position_imported['isolated']
                        _position_virtualServer['isolatedWalletBalance']  = _position_imported['isolatedWalletBalance']
                        _position_virtualServer['openOrderInitialMargin'] = 0
                        _position_virtualServer['maintenanceMargin']      = None
                        _position_virtualServer['unrealizedPNL'] = None
                    #[1-2]: Compute others
                    _position['maintenanceMargin'] = None
                    if (_position['tradeConfigurationCode'] in self.__tradeConfigurations_loaded): _position['weightedAssumedRatio'] = _position['assumedRatio']*self.__tradeConfigurations_loaded[_position['tradeConfigurationCode']]['config']['leverage']
                    else:                                                                          _position['weightedAssumedRatio'] = None
                    _position['commitmentRate'] = None
                    _position['riskLevel']      = None
                    #[1-3]: Asset position symbols tracker update
                    _asset = _account['assets'][_position['quoteAsset']]
                    if (_pSymbol not in _asset['_positionSymbols']): _asset['_positionSymbols'].add(_pSymbol)
            #[2]: Sort position symbols by priority
            for _assetName in _assets: self.__sortPositionSymbolsByPriority(localID = localID, assetName = _assetName)
            #[3]: Read Assets Data
            for _assetName in _assets_imported:
                if (_assetName in _assets):
                    _asset          = _assets[_assetName]
                    _asset_imported = _assets_imported[_assetName]
                    #[3-1]: Direct values import
                    _asset['marginBalance']      = None
                    _asset['walletBalance']      = None
                    _asset['crossWalletBalance'] = None
                    _asset['availableBalance']   = None
                    _asset['allocationRatio']    = _asset_imported['allocationRatio']
                    #[3-2]: Compute others
                    _asset['isolatedWalletBalance']         = None
                    _asset['openOrderInitialMargin']        = None
                    _asset['crossMaintenanceMargin']        = None
                    _asset['isolatedPositionInitialMargin'] = None
                    _asset['crossPositionInitialMargin']    = None
                    _asset['isolatedUnrealizedPNL']         = None
                    _asset['crossUnrealizedPNL']            = None
                    _asset['assumedRatio']                  = sum(_positions[_pSymbol]['assumedRatio']         for _pSymbol in _asset['_positionSymbols'])
                    _asset['weightedAssumedRatio']          = sum(_positions[_pSymbol]['weightedAssumedRatio'] for _pSymbol in _asset['_positionSymbols'] if (_positions[_pSymbol]['weightedAssumedRatio'] is not None))
                    _asset['unrealizedPNL']                 = None
                    _asset['allocatableBalance']            = None
                    if (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL):
                        _asset_virtualServer = _account_virtualServer_assets[_assetName]
                        _asset_virtualServer['crossWalletBalance'] = _asset_imported['crossWalletBalance']
                        _asset_virtualServer['availableBalance']   = None
                        _asset_virtualServer['walletBalance']      = None
                        _asset_virtualServer['marginBalance']      = None
        #---[2-2]: Binance & Virtual Update
        else:
            _toRequestDBUpdate = list()
            #[1]: Save previous data
            _assets_prev    = dict()
            _positions_prev = dict()
            for _assetName in _assets:
                _assets_prev[_assetName] = dict()
                for _dataKey in _GUIANNOUCEMENT_ASSETDATANAMES: _assets_prev[_assetName][_dataKey] = _assets[_assetName][_dataKey]
            for _pSymbol in _positions:
                _positions_prev[_pSymbol] = dict()
                for _dataKey in _GUIANNOUCEMENT_POSITIONDATANAMES: _positions_prev[_pSymbol][_dataKey] = _positions[_pSymbol][_dataKey]
            #[2]: Read Positions Data
            for _pSymbol in _positions_imported:
                _position          = _positions[_pSymbol]
                _position_imported = _positions_imported[_pSymbol]
                if (_pSymbol in self.__currencies_lastKline): _lastKline = self.__currencies_lastKline[_pSymbol]
                else:                                         _lastKline = None
                #[1]: Values Update & Trade Check
                #---Current Price
                if (_lastKline != None): _position['currentPrice'] = _lastKline[KLINDEX_CLOSEPRICE]
                else:                    _position['currentPrice'] = None
                #---Trade Check
                _ocr = _position['_orderCreationRequest']
                if (((_ocr is not None) and (_ocr['lastRequestReceived'] == True)) or (_ocr is None)): #If the OCR has received the result or does not exist
                    if (_position['quantity'] is not None): self.__trade_checkTrade(localID = localID, positionSymbol = _pSymbol, quantity_new = _position_imported['quantity'], entryPrice_new = _position_imported['entryPrice'])
                    _position['quantity']               = _position_imported['quantity']
                    _position['entryPrice']             = _position_imported['entryPrice']
                    _position['isolatedWalletBalance']  = _position_imported['isolatedWalletBalance']
                    _position['positionInitialMargin']  = _position_imported['positionInitialMargin']
                    _position['openOrderInitialMargin'] = _position_imported['openOrderInitialMargin']
                    _position['maintenanceMargin']      = _position_imported['maintenanceMargin']
                    _position['unrealizedPNL']          = _position_imported['unrealizedPNL']
                #---Trade Control
                _tradeControl = _position['tradeControl']
                if ((_lastKline is not None) and (_tradeControl['tcMode'] == 'TS') and (_tradeControl['ts_maximumProfitPrice'] is not None)):
                    _updated = False
                    if   ((_position['quantity'] < 0) and (_lastKline[KLINDEX_LOWPRICE] < _position['ts_maximumProfitPrice'])):  _position['ts_maximumProfitPrice'] = _lastKline[KLINDEX_LOWPRICE];  _updated = True
                    elif ((0 < _position['quantity']) and (_position['ts_maximumProfitPrice'] < _lastKline[KLINDEX_HIGHPRICE])): _position['ts_maximumProfitPrice'] = _lastKline[KLINDEX_HIGHPRICE]; _updated = True
                    if (_updated == True): _toRequestDBUpdate.append(((localID, 'positions', _pSymbol, 'tradeControl'), self.__copyTradeControl(_tradeControl)))
                #[2]: Position Setup Identity
                _position['leverage'] = _position_imported['leverage']
                _position['isolated'] = _position_imported['isolated']
                self.__checkPositionTradability(localID = localID, positionSymbol = _pSymbol)
                self.__requestMarginTypeAndLeverageUpdate(localID = localID, positionSymbol = _pSymbol) #If this needs to be done will be determined internally
                _asset = _account['assets'][_position['quoteAsset']]
                if (_position['isolated'] == True):
                    if (_pSymbol not in _asset['_positionSymbols_isolated']): _asset['_positionSymbols_isolated'].add(_pSymbol)
                    if (_pSymbol     in _asset['_positionSymbols_crossed']):  _asset['_positionSymbols_crossed'].remove(_pSymbol)
                else:
                    if (_pSymbol not in _asset['_positionSymbols_crossed']):  _asset['_positionSymbols_crossed'].add(_pSymbol)
                    if (_pSymbol     in _asset['_positionSymbols_isolated']): _asset['_positionSymbols_isolated'].remove(_pSymbol)
            #[3]: Read Assets Data
            for _assetName in _assets_imported:
                _asset          = _assets[_assetName]
                _asset_imported = _assets_imported[_assetName]
                #[3-1]: Direct values import
                _asset['marginBalance']      = _asset_imported['marginBalance']
                _asset['walletBalance']      = _asset_imported['walletBalance']
                _asset['crossWalletBalance'] = _asset_imported['crossWalletBalance']
                _asset['availableBalance']   = _asset_imported['availableBalance']
                #[3-2]: Compute others
                _asset['isolatedWalletBalance']         = sum(_positions[_pSymbol]['isolatedWalletBalance']  for _pSymbol in _asset['_positionSymbols_isolated'] if (_positions[_pSymbol]['isolatedWalletBalance']  is not None))
                _asset['isolatedPositionInitialMargin'] = sum(_positions[_pSymbol]['positionInitialMargin']  for _pSymbol in _asset['_positionSymbols_isolated'] if (_positions[_pSymbol]['positionInitialMargin']  is not None))
                _asset['openOrderInitialMargin']        = sum(_positions[_pSymbol]['openOrderInitialMargin'] for _pSymbol in _asset['_positionSymbols']          if (_positions[_pSymbol]['openOrderInitialMargin'] is not None))
                _asset['crossPositionInitialMargin']    = sum(_positions[_pSymbol]['positionInitialMargin']  for _pSymbol in _asset['_positionSymbols_crossed']  if (_positions[_pSymbol]['positionInitialMargin']  is not None))
                _asset['crossMaintenanceMargin']        = sum(_positions[_pSymbol]['maintenanceMargin']      for _pSymbol in _asset['_positionSymbols_crossed']  if (_positions[_pSymbol]['maintenanceMargin']      is not None))
                _asset['isolatedUnrealizedPNL']         = sum(_positions[_pSymbol]['unrealizedPNL']          for _pSymbol in _asset['_positionSymbols_isolated'] if (_positions[_pSymbol]['unrealizedPNL'] is not None))
                _asset['crossUnrealizedPNL']            = sum(_positions[_pSymbol]['unrealizedPNL']          for _pSymbol in _asset['_positionSymbols_crossed']  if (_positions[_pSymbol]['unrealizedPNL'] is not None))
                _asset['assumedRatio']                  = sum(_positions[_pSymbol]['assumedRatio']           for _pSymbol in _asset['_positionSymbols'])
                _asset['weightedAssumedRatio']          = sum(_positions[_pSymbol]['weightedAssumedRatio']   for _pSymbol in _asset['_positionSymbols'] if (_positions[_pSymbol]['weightedAssumedRatio'] is not None))
                _asset['unrealizedPNL']                 = _asset['isolatedUnrealizedPNL']+_asset['crossUnrealizedPNL']
                if (_asset['walletBalance'] is None): _asset['allocatableBalance'] = None
                else:                                 _asset['allocatableBalance'] = round((_asset['walletBalance']-_asset['openOrderInitialMargin'])*_ACCOUNT_BASEASSETALLOCATABLERATIO*_asset['allocationRatio'], _ACCOUNT_ASSETPRECISIONS[_assetName])
            #[4]: Balance Allocation
            self.__allocateBalance(localID = localID, asset = 'all')
            #[5]: Update Secondary Position Data
            for _pSymbol in _positions:
                _position = _positions[_pSymbol]
                _asset    = _assets[_position['quoteAsset']]
                if (_position['quantity'] == None):
                    _position['commitmentRate']   = None
                    _position['liquidationPrice'] = None
                    _position['riskLevel']        = None
                else:
                    _quantity_abs = abs(_position['quantity'])
                    #[1]: Commitment Rate
                    if ((0 < _quantity_abs) and (_position['leverage'] != None) and (_position['allocatedBalance'] != 0)): _position['commitmentRate'] = round((_quantity_abs*_position['entryPrice']/_position['leverage'])/_position['allocatedBalance'], 5)
                    else:                                                                                                  _position['commitmentRate'] = None
                    #[2]: Liquidation Price
                    if (_position['isolated'] == True): _wb = _position['isolatedWalletBalance']
                    else:                               _wb = _asset['crossWalletBalance']
                    _position['liquidationPrice'] = self.__computeLiquidationPrice(positionSymbol    = _pSymbol,
                                                                                   walletBalance     = _wb,
                                                                                   quantity          = _position['quantity'],
                                                                                   entryPrice        = _position['entryPrice'],
                                                                                   currentPrice      = _position['currentPrice'],
                                                                                   maintenanceMargin = _position['maintenanceMargin'],
                                                                                   upnl              = _position['unrealizedPNL'],
                                                                                   isolated          = _position['isolated'],
                                                                                   mm_crossTotal     = _asset['crossMaintenanceMargin'],
                                                                                   upnl_crossTotal   = _asset['crossUnrealizedPNL'])
                    #[3]: Risk Level
                    if ((_position['entryPrice'] != None) and (_position['currentPrice'] != None)):
                        if (_position['liquidationPrice'] == None): _position['riskLevel'] = 0
                        else:
                            if   (0 < _position['quantity']): _lp = (_position['entryPrice']-_position['currentPrice'])/(_position['entryPrice']-_position['liquidationPrice'])
                            elif (_position['quantity'] < 0): _lp = (_position['currentPrice']-_position['entryPrice'])/(_position['liquidationPrice']-_position['entryPrice'])
                            if (_lp < 0): _lp = 0
                            if (_position['commitmentRate'] == None): _position['riskLevel'] = _lp
                            else:                                     _position['riskLevel'] = _position['commitmentRate']*_lp
                    else: _position['riskLevel'] = None
            #[6]: Update Secondary Asset Data
            for _assetName in _assets:
                _asset = _assets[_assetName]
                #[1]: Allocated Balance
                allocatedBalanceSum = sum([_positions[_positionSymbol]['allocatedBalance'] for _positionSymbol in _asset['_positionSymbols']])
                _asset['allocatedBalance'] = allocatedBalanceSum
                #[2]: Commitment Rate
                _commitmentRate_pSymbols = [_pSymbol for _pSymbol in _asset['_positionSymbols'] if (_positions[_pSymbol]['commitmentRate'] is not None)]
                _commitmentRate_pSymbols_n = len(_commitmentRate_pSymbols)
                if (0 < _commitmentRate_pSymbols_n):
                    _commitmentRate_sum = sum(_positions[_pSymbol]['commitmentRate'] for _pSymbol in _commitmentRate_pSymbols)
                    _commitmentRate_average = round(_commitmentRate_sum/_commitmentRate_pSymbols_n, 5)
                else: _commitmentRate_average = None
                _asset['commitmentRate'] = _commitmentRate_average
                #[3]: Risk Level
                _riskLevel_pSymbols = [_pSymbol for _pSymbol in _asset['_positionSymbols'] if (_positions[_pSymbol]['riskLevel'] is not None)]
                _riskLevel_pSymbols_n = len(_riskLevel_pSymbols)
                if (0 < _riskLevel_pSymbols_n):
                    _riskLevel_sum     = sum(_positions[_pSymbol]['riskLevel'] for _pSymbol in _riskLevel_pSymbols)
                    _riskLevel_average = round(_riskLevel_sum/_riskLevel_pSymbols_n, 5)
                else: _riskLevel_average = None
                _asset['riskLevel'] = _riskLevel_average
            #[7]: Trade Handling
            self.__handleGeneratedPIPs(localID  = localID)
            self.__processTradeHandlers(localID = localID)
            #[8]: Announce Updated Data
            for _assetName in _assets_prev: 
                for _dataKey in _assets_prev[_assetName]:
                    if (_assets[_assetName][_dataKey] != _assets_prev[_assetName][_dataKey]):
                        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'assets', _assetName, _dataKey), prdContent = _assets[_assetName][_dataKey])
                        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_ASSET', 'updatedContent': (localID, _assetName, _dataKey)}, farrHandler = None)
            for _pSymbol in _positions_prev:
                for _dataKey in _positions_prev[_pSymbol]:
                    if (_positions[_pSymbol][_dataKey] != _positions_prev[_pSymbol][_dataKey]):
                        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', _pSymbol, _dataKey), prdContent = _positions[_pSymbol][_dataKey])
                        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, _pSymbol, _dataKey)}, farrHandler = None)
            #[9]: DB Update Requests
            if (0 < len(_toRequestDBUpdate)): self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': _toRequestDBUpdate}, farrHandler = None)
    def __updateAccountHourlyReport(self, localID, importedData = None):
        _account = self.__accounts[localID]
        _assets  = _account['assets']
        #Data import from DB
        if (importedData != None):
            _importedReport_hourTS = importedData['hourTS']
            _importedReport_report = importedData['report']
            _t_current_hour = int(time.time()/3600)*3600
            if (_importedReport_hourTS == _t_current_hour): 
                _account['_hourlyReport']                  = _importedReport_report
                _account['_hourlyReport_hourTS']           = _t_current_hour
                _account['_hourlyReport_lastAnnounced_ns'] = time.perf_counter_ns()
            else:
                _account['_hourlyReport'] = dict()
                for _assetName in _account['assets']:
                    _asset = _account['assets'][_assetName]
                    _mb = _asset['marginBalance']
                    _wb = _asset['walletBalance']
                    if (_asset['commitmentRate'] == None): _commimtmentRate = 0
                    else:                                  _commimtmentRate = _asset['commitmentRate']
                    if (_asset['riskLevel'] == None): _riskLevel = 0
                    else:                             _riskLevel = _asset['riskLevel']
                    _account['_hourlyReport'][_assetName] = {'nTrades':             0,
                                                             'nTrades_buy':         0,
                                                             'nTrades_sell':        0,
                                                             'nTrades_liquidation': 0,
                                                             'nTrades_entry':       0,
                                                             'nTrades_exit':        0,
                                                             'nTrades_psl':         0,
                                                             'nTrades_fsl':         0,
                                                             'nTrades_raf':         0,
                                                             'nTrades_wr':          0,
                                                             'nTrades_forceClear':  0,
                                                             'nTrades_unknown':     0,
                                                             'nTrades_gain':        0,
                                                             'nTrades_loss':        0,
                                                             'marginBalance_open': _mb, 'marginBalance_min': _mb, 'marginBalance_max': _mb, 'marginBalance_close': _mb,
                                                             'walletBalance_open': _wb, 'walletBalance_min': _wb, 'walletBalance_max': _wb, 'walletBalance_close': _wb,
                                                             'commitmentRate_open': _commimtmentRate, 'commitmentRate_min': _commimtmentRate, 'commitmentRate_max': _commimtmentRate, 'commitmentRate_close': _commimtmentRate,
                                                             'riskLevel_open':      _riskLevel,       'riskLevel_min':      _riskLevel,       'riskLevel_max':      _riskLevel,       'riskLevel_close':      _riskLevel}
                _account['_hourlyReport_hourTS']           = _t_current_hour
                _account['_hourlyReport_lastAnnounced_ns'] = time.perf_counter_ns()
        #No imported data, internal handling (+announcement if needed)
        else:
            _t_current_hour = int(time.time()/3600)*3600
            if (_t_current_hour == _account['_hourlyReport_hourTS']):
                #Report Update
                for _assetName in _assets:
                    _asset             = _assets[_assetName]
                    _hReport_thisAsset = _account['_hourlyReport'][_assetName]
                    #---Margin Balance
                    if (_asset['marginBalance'] is not None):
                        if (_hReport_thisAsset['marginBalance_open'] is None): _hReport_thisAsset['marginBalance_open'] = _asset['marginBalance']
                        if ((_hReport_thisAsset['marginBalance_min'] is None) or (_asset['marginBalance'] < _hReport_thisAsset['marginBalance_min'])): _hReport_thisAsset['marginBalance_min'] = _asset['marginBalance']
                        if ((_hReport_thisAsset['marginBalance_max'] is None) or (_hReport_thisAsset['marginBalance_max'] < _asset['marginBalance'])): _hReport_thisAsset['marginBalance_max'] = _asset['marginBalance']
                        _hReport_thisAsset['marginBalance_close'] = _asset['marginBalance']
                    #---Wallet Balance
                    if (_asset['walletBalance'] is not None):
                        if (_hReport_thisAsset['walletBalance_open'] is None): _hReport_thisAsset['walletBalance_open'] = _asset['walletBalance']
                        if ((_hReport_thisAsset['walletBalance_min'] is None) or (_asset['walletBalance'] < _hReport_thisAsset['walletBalance_min'])): _hReport_thisAsset['walletBalance_min'] = _asset['walletBalance']
                        if ((_hReport_thisAsset['walletBalance_max'] is None) or (_hReport_thisAsset['walletBalance_max'] < _asset['walletBalance'])): _hReport_thisAsset['walletBalance_max'] = _asset['walletBalance']
                        _hReport_thisAsset['walletBalance_close'] = _asset['walletBalance']
                    #---Commitment Rate
                    if (_asset['commitmentRate'] is not None): _cr = _asset['commitmentRate']
                    else:                                      _cr = 0
                    if (_cr < _hReport_thisAsset['commitmentRate_min']): _hReport_thisAsset['commitmentRate_min'] = _cr
                    if (_hReport_thisAsset['commitmentRate_max'] < _cr): _hReport_thisAsset['commitmentRate_max'] = _cr
                    _hReport_thisAsset['commitmentRate_close'] = _cr
                    #---Risk Level
                    if (_asset['riskLevel'] is not None): _rl = _asset['riskLevel']
                    else:                                 _rl = 0
                    if (_rl < _hReport_thisAsset['riskLevel_min']): _hReport_thisAsset['riskLevel_min'] = _rl
                    if (_hReport_thisAsset['riskLevel_max'] < _rl): _hReport_thisAsset['riskLevel_max'] = _rl
                    _hReport_thisAsset['riskLevel_close'] = _rl
                #Announcement
                if (_ACCOUNT_HOURLYREPORTANNOUNCEMENTINTERVAL_NS <= time.perf_counter_ns()-_account['_hourlyReport_lastAnnounced_ns']):
                    _hourlyReport_copy = dict()
                    for _assetName in _account['_hourlyReport']: _hourlyReport_copy[_assetName] = _account['_hourlyReport'][_assetName].copy()
                    #Announcement
                    self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'updateAccountHourlyReport', functionParams = {'localID': localID, 'hourTimestamp': _t_current_hour, 'hourlyReport': _hourlyReport_copy}, farrHandler = None)
                    _account['_hourlyReport_lastAnnounced_ns'] = time.perf_counter_ns()
            #If new hour, create a copy of the previous and format new
            else:
                #Previous report copy
                if (_account['_hourlyReport'] == None): _hourlyReport_prevCopy = None
                else:
                    _hourlyReport_prevCopy = dict()
                    for _assetName in _account['_hourlyReport']: _hourlyReport_prevCopy[_assetName] = _account['_hourlyReport'][_assetName].copy()
                #New hour formatting
                _account['_hourlyReport'] = dict()
                for _assetName in _account['assets']:
                    _asset = _account['assets'][_assetName]
                    _mb = _asset['marginBalance']
                    _wb = _asset['walletBalance']
                    if (_asset['commitmentRate'] == None): _commimtmentRate = 0
                    else:                                  _commimtmentRate = _asset['commitmentRate']
                    if (_asset['riskLevel'] == None): _riskLevel = 0
                    else:                             _riskLevel = _asset['riskLevel']
                    _account['_hourlyReport'][_assetName] = {'nTrades':             0,
                                                             'nTrades_buy':         0,
                                                             'nTrades_sell':        0,
                                                             'nTrades_liquidation': 0,
                                                             'nTrades_entry':       0,
                                                             'nTrades_exit':        0,
                                                             'nTrades_psl':         0,
                                                             'nTrades_fsl':         0,
                                                             'nTrades_raf':         0,
                                                             'nTrades_wr':          0,
                                                             'nTrades_forceClear':  0,
                                                             'nTrades_unknown':     0,
                                                             'nTrades_gain':        0,
                                                             'nTrades_loss':        0,
                                                             'marginBalance_open': _mb, 'marginBalance_min': _mb, 'marginBalance_max': _mb, 'marginBalance_close': _mb,
                                                             'walletBalance_open': _wb, 'walletBalance_min': _wb, 'walletBalance_max': _wb, 'walletBalance_close': _wb,
                                                             'commitmentRate_open': _commimtmentRate, 'commitmentRate_min': _commimtmentRate, 'commitmentRate_max': _commimtmentRate, 'commitmentRate_close': _commimtmentRate,
                                                             'riskLevel_open':      _riskLevel,       'riskLevel_min':      _riskLevel,       'riskLevel_max':      _riskLevel,       'riskLevel_close':      _riskLevel}
                _account['_hourlyReport_hourTS'] = _t_current_hour
                #New hour copy
                _hourlyReport_newCopy = dict()
                for _assetName in _account['_hourlyReport']: _hourlyReport_newCopy[_assetName] = _account['_hourlyReport'][_assetName].copy()
                #Announcement
                if (_hourlyReport_prevCopy is not None): self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'updateAccountHourlyReport', functionParams = {'localID': localID, 'hourTimestamp': _t_current_hour-3600, 'hourlyReport': _hourlyReport_prevCopy}, farrHandler = None)
                self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'updateAccountHourlyReport', functionParams = {'localID': localID, 'hourTimestamp': _t_current_hour, 'hourlyReport': _hourlyReport_newCopy}, farrHandler = None)
                _account['_hourlyReport_lastAnnounced_ns'] = time.perf_counter_ns()
    def __updateAccountHourlyReport_onTrade(self, localID, positionSymbol, side, logicSource, profit):
        _account  = self.__accounts[localID]
        _position = _account['positions'][positionSymbol]
        _hourlyReport = _account['_hourlyReport'][_position['quoteAsset']]
        _hourlyReport['nTrades'] += 1
        if   (side == 'BUY'):  _hourlyReport['nTrades_buy']  += 1
        elif (side == 'SELL'): _hourlyReport['nTrades_sell'] += 1
        if   (logicSource == 'PIP_ENTRY'):  _hourlyReport['nTrades_entry']      += 1
        elif (logicSource == 'PIP_EXIT'):   _hourlyReport['nTrades_exit']       += 1
        elif (logicSource == 'PIP_PSL'):    _hourlyReport['nTrades_psl']        += 1
        elif (logicSource == 'FSL'):        _hourlyReport['nTrades_fsl']        += 1
        elif (logicSource == 'WR'):         _hourlyReport['nTrades_wr']         += 1
        elif (logicSource == 'RAF'):        _hourlyReport['nTrades_raf']        += 1
        elif (logicSource == 'FORCECLEAR'): _hourlyReport['nTrades_forceClear'] += 1
        elif (logicSource == 'UNKNOWN'):    _hourlyReport['nTrades_unknown']    += 1
        if (profit is not None):
            if   (0 < profit):  _hourlyReport['nTrades_gain'] += 1
            elif (profit <= 0): _hourlyReport['nTrades_loss'] += 1
        _account['_hourlyReport_lastAnnounced_ns'] = 0

    #---Trade Controls
    def __handleGeneratedPIPs(self, localID):
        _account       = self.__accounts[localID]
        _positions     = _account['positions']
        _generatedPIPs = _account['_generatedPIPs']
        _expectedPIPTS = _account['_expectedPIPTS']
        for _pSymbol in _generatedPIPs:
            if (_pSymbol not in _expectedPIPTS): _expectedPIPTS[_pSymbol] = None
            _klineOpenTS_sorted = list(_generatedPIPs[_pSymbol].keys()); _klineOpenTS_sorted.sort()
            for _klineOpenTS in _klineOpenTS_sorted:
                _generatedPIP = _generatedPIPs[_pSymbol][_klineOpenTS]
                _lastKline    = self.__currencies_lastKline[_pSymbol]
                #Expected PIP TS Check
                if (_expectedPIPTS[_pSymbol] is None):
                    if (_generatedPIP['klineClosed'] == True): _expectedPIPTS[_pSymbol] = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = _klineOpenTS, mrktReg = self.__currencies[_pSymbol]['kline_firstOpenTS'], nTicks = 1)
                    else:                                      _expectedPIPTS[_pSymbol] = _klineOpenTS
                    _pipExpected = True
                else:
                    if (_expectedPIPTS[_pSymbol] <= _klineOpenTS):
                        if (_expectedPIPTS[_pSymbol] < _klineOpenTS): self.__logger(message = f"A PIP Signal Loss Detected For {localID}-{_pSymbol}. \n * Expected: {_expectedPIPTS[_pSymbol]}\n * Received: {_klineOpenTS}", logType = 'Warning', color = 'light_red')
                        if (_generatedPIP['klineClosed'] == True): _expectedPIPTS[_pSymbol] = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = _klineOpenTS, mrktReg = self.__currencies[_pSymbol]['kline_firstOpenTS'], nTicks = 1)
                        else:                                      _expectedPIPTS[_pSymbol] = _klineOpenTS
                        _pipExpected = True
                    else: _pipExpected = False
                #Expiration Check & Interpretation
                if (_pipExpected == True):
                    #Expiration Check
                    _sinceDispatch_t      = time.time()-_generatedPIP['dispatchTime']
                    _sinceDispatch_pDelta = abs(_lastKline[KLINDEX_CLOSEPRICE]/_generatedPIP['kline'][KLINDEX_CLOSEPRICE]-1)
                    _pipExpired_dispatchTime    = (_TRADE_PIPSIGNALFILTER_DISPATCHTIME_S  <= _sinceDispatch_t)
                    _pipExpired_klineClosePrice = (_TRADE_PIPSIGNALFILTER_KLINECLOSEPRICE <= _sinceDispatch_pDelta)
                    #PIP Interpretation
                    if ((_pipExpired_dispatchTime == False) and (_pipExpired_klineClosePrice == False)):
                        _position = _positions[_pSymbol]
                        if ((_account['tradeStatus'] == True) and (_position['tradeStatus'] == True) and (_position['tradeConfigurationCode'] != None)):
                            _tc      = self.__tradeConfigurations_loaded[_position['tradeConfigurationCode']]['config']
                            _tc_tcm  = _tc['tcMode']
                            _pip_asm = _generatedPIP['pipResult']['ACTIONSIGNALMODE']
                            if   ((_tc_tcm == 'TS')   and (_pip_asm == 'IMPULSIVE')): self.__handleGeneratedPIP_TS(localID   = localID, positionSymbol = _pSymbol, generatedPIP = _generatedPIP) #[1]: Trade Control Mode - Trade Scenario
                            elif ((_tc_tcm == 'RQPM') and (_pip_asm == 'CYCLIC')):    self.__handleGeneratedPIP_RQPM(localID = localID, positionSymbol = _pSymbol, generatedPIP = _generatedPIP) #[2]: Trade Control Mode - Remaining Quantity Percentage Map
                    else:
                        _msg = f"A PIP Signal Expired and Disposed For {localID}-{_pSymbol}."
                        if (_pipExpired_dispatchTime    == True): _msg += f"\n * Dispatch Time: {_TRADE_PIPSIGNALFILTER_DISPATCHTIME_S} s <= {_sinceDispatch_t:.3f} s"
                        if (_pipExpired_klineClosePrice == True): _msg += f"\n * Dispatch pDelta: {_TRADE_PIPSIGNALFILTER_KLINECLOSEPRICE*100} % <= {_sinceDispatch_pDelta*100:.3f} %"
                        self.__logger(message = _msg, logType = 'Warning', color = 'light_magenta')
        _account['_generatedPIPs'].clear()
    def __handleGeneratedPIP_TS(self, localID, positionSymbol, generatedPIP):
        #Instances Call
        _account    = self.__accounts[localID]
        _position   = _account['positions'][pSymbol]
        _asset      = _account['assets'][_position['quoteAsset']]
        _tc         = _account['tradeConfigurations'][_position['tradeConfigurationCode']]
        _precisions = _position['precisions']
        _serverFilters = self.__currencies[pSymbol]['info_server']['filters']
        _kline = self.__currencies_lastKline[pSymbol]
        #PIP Action Signal
        pipResult = generatedPIP['pipResult']
        if (pipResult['ACTIONSIGNAL'] == None): _pas_side = None
        else:                                   _pas_side = pipResult['ACTIONSIGNAL']['side']



        if (_position['quantity'] == 0):
            if ((_pipActionSignal != None) and (_position['reduceOnly'] == False)):
                if (_pipActionSignal[1] == True):
                    if (_pipActionSignal[0] == 'BUY'):
                        if ((_tc['direction'] == 'LONG') or (_tc['direction'] == 'BOTH')): _tradeHandler = 'PIP_ENTRY'
                    elif (_pipActionSignal[0] == 'SELL'):
                        if ((_tc['direction'] == 'SHORT') or (_tc['direction'] == 'BOTH')): _tradeHandler = 'PIP_ENTRY'
        else:
            #[1]: ESCAPE Check
            if ((_pipActionSignal != None) and (_pipActionSignal[2] != None)):
                if (0 < _position['quantity']):
                    if (_pipActionSignal[2] == 'LONGESCAPE'): _tradeHandler = 'ESCAPE'
                elif (_position['quantity'] < 0):
                    if (_pipActionSignal[2] == 'SHORTESCAPE'): _tradeHandler = 'ESCAPE'
            #[2]: FSL (Full-Stop-Loss) Check
            if (_tradeHandler == None):
                if (0 < _position['quantity']):
                    if (_tc['fullStopLoss'] != None):
                        _price_FSL = round(_position['entryPrice']*(1-_tc['fullStopLoss']), _precisions['price'])
                        if (_lowPrice <= _price_FSL): _tradeHandler = 'FSL'
                elif (_position['quantity'] < 0):
                    if (_tc['fullStopLoss'] != None):
                        _price_FSL = round(_position['entryPrice']*(1+_tc['fullStopLoss']), _precisions['price'])
                        if (_price_FSL <= _highPrice): _tradeHandler = 'FSL'
            #[3]: WR (Weight Reduce) Check
            if ((_tradeHandler == None) and (_tc['weightReduce'] != None)):
                #WR Price Test
                _wrPriceTestPassed = False
                if (0 < _position['quantity']):
                    _price_WR = round(_position['entryPrice']*(1+_tc['weightReduce'][0]), _precisions['price'])
                    if (_price_WR <= _highPrice): _wrPriceTestPassed = True
                elif (_position['quantity'] < 0):
                    _price_WR = round(_position['entryPrice']*(1-_tc['weightReduce'][0]), _precisions['price'])
                    if (_lowPrice <= _price_WR): _wrPriceTestPassed = True
                #Quantity Test
                if (_wrPriceTestPassed == True):
                    _quantity_minUnit = pow(10, -_precisions['quantity'])
                    _quantity_postWR  = round(int((_position['allocatedBalance']*_tc['weightReduce'][1]/_price_WR*_tc['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                    _quantity_WR      = round(abs(_position['quantity'])-_quantity_postWR, _precisions['quantity'])
                    if (0 < _quantity_WR): _tradeHandler = 'WR'
            #[4]: RAF (Reach-And-Fall) Check
            if ((_tradeHandler == None) and (_tc['reachAndFall'] != None) and (_position['maximumProfitPrice'] != None)):
                if (0 < _position['quantity']):
                    _activationPoint1 = round(_position['entryPrice']*(1+_tc['reachAndFall'][0]), _precisions['price'])
                    _activationPoint2 = round(_position['entryPrice']*(1+_tc['reachAndFall'][1]), _precisions['price'])
                    if ((_activationPoint1 <= _position['maximumProfitPrice']) and (_closePrice <= _activationPoint2)): _tradeHandler = 'RAF'
                elif (_position['quantity'] < 0):
                    _activationPoint1 = round(_position['entryPrice']*(1-_tc['reachAndFall'][0]), _precisions['price'])
                    _activationPoint2 = round(_position['entryPrice']*(1-_tc['reachAndFall'][1]), _precisions['price'])
                    if ((_position['maximumProfitPrice'] <= _activationPoint1) and (_activationPoint2 <= _closePrice)): _tradeHandler = 'RAF'
            #[5]: PIP BUY & SELL Check
            if (_tradeHandler == None):
                if (_pipActionSignal != None):
                    #Holding LONG
                    if (0 < _position['quantity']):
                        if (_pipActionSignal[0] == 'BUY'):
                            if ((_pipActionSignal[1] == True) and (_position['reduceOnly'] == False) and ((_tc['direction'] == 'LONG') or (_tc['direction'] == 'BOTH'))): _tradeHandler = 'PIP_ENTRY'
                        elif (_pipActionSignal[0] == 'SELL'):
                            if   (_position['entryPrice'] <= _closePrice): _tradeHandler = 'PIP_EXIT'
                            else:                                          _tradeHandler = 'PIP_PSL'
                    #Holding Short
                    elif (_position['quantity'] < 0):
                        if (_pipActionSignal[0] == 'SELL'): 
                            if ((_pipActionSignal[1] == True) and (_position['reduceOnly'] == False) and ((_tc['direction'] == 'SHORT') or (_tc['direction'] == 'BOTH'))): _tradeHandler = 'PIP_ENTRY'
                        elif (_pipActionSignal[0] == 'BUY'):
                            if   (_closePrice <= _position['entryPrice']): _tradeHandler = 'PIP_EXIT'
                            else:                                          _tradeHandler = 'PIP_PSL'
        #Handling
        if (_tradeHandler != None):
            #PIP BUY
            if (_tradeHandler == 'PIP_ENTRY'):
                #[1]: Allocated / Committed Balance / Initial Entry Price
                if (_position['allocatedBalance'] == None): _allocatedBalance = 0
                else:                                       _allocatedBalance = _position['allocatedBalance']
                if (_position['entryPrice'] == None): _committedBalance = 0
                else:                                 _committedBalance = abs(_position['quantity'])*_position['entryPrice']/_position['leverage']
                if ((_position['quantity'] != 0) and (_position['initialEntryPrice'] == None)): _position['initialEntryPrice'] = _position['entryPrice']
                #[2]: Quantity Determination
                _quantity_minUnit = pow(10, -_precisions['quantity'])
                _quantity         = None
                #---Initial Entry
                if (_position['initialEntryPrice'] == None):
                    if (0 < len(_tc['method_entry'])): 
                        _sd = _tc['method_entry'][0]
                        _targetCommittedBalance = round(_allocatedBalance*_sd[1], _precisions['quote'])
                        _quantity = round(int((_targetCommittedBalance/_closePrice*_tc['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                #---Additional Entry
                else:
                    #From all the satisfied trade scenarios, find the maximum targeting quantity
                    _targetMaxQuantity_perc = None
                    for _sd in _tc['method_entry']:
                        if (((0 < _position['quantity']) and (_sd[0] <= -(_closePrice/_position['initialEntryPrice']-1))) or ((_position['quantity'] < 0) and (_sd[0] <= (_closePrice/_position['initialEntryPrice']-1)))):
                            if ((_targetMaxQuantity_perc == None) or (_targetMaxQuantity_perc < _sd[1])): _targetMaxQuantity_perc = _sd[1]
                    #Determine the quantity to enter additionally
                    if (_targetMaxQuantity_perc != None):
                        _targetCommittedBalance      = round(_allocatedBalance*_targetMaxQuantity_perc, _precisions['quote'])
                        _additionallyRequiredBalance = _targetCommittedBalance-_committedBalance
                        if (0 < _additionallyRequiredBalance): _quantity = round(int((_additionallyRequiredBalance/_closePrice*_tc['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                #[3]: Quantity Check
                _test_quantity          = True
                _test_quantity_failType = None
                if ((_quantity != None) and (0 < _quantity)):
                    #---Filters
                    for _serverFilter in _serverFilters:
                        if (_serverFilter['filterType'] == 'PRICE_FILTER'): pass
                        elif (_serverFilter['filterType'] == 'LOT_SIZE'): pass
                        elif (_serverFilter['filterType'] == 'MARKET_LOT_SIZE'):
                            _minQty   = float(_serverFilter['minQty'])
                            _maxQty   = float(_serverFilter['maxQty'])
                            _stepSize = float(_serverFilter['stepSize'])
                            if not(_minQty <= _quantity):                                              _test_quantity = False; _test_quantity_failType = ('MINQTY',   _minQty, _quantity)
                            if not(_quantity <= _maxQty):                                              _test_quantity = False; _test_quantity_failType = ('MAXQTY',   _maxQty, _quantity)
                            if not(_quantity == round(_quantity, -math.floor(math.log10(_stepSize)))): _test_quantity = False; _test_quantity_failType = ('STEPSIZE', _stepSize, math.floor(math.log10(_stepSize)), round(_quantity, -math.floor(math.log10(_stepSize))), _quantity)
                        elif (_serverFilter['filterType'] == 'MAX_NUM_ORDERS'): pass
                        elif (_serverFilter['filterType'] == 'MAX_NUM_ALGO_ORDERS'): pass
                        elif (_serverFilter['filterType'] == 'MIN_NOTIONAL'):
                            _notional_min = float(_serverFilter['notional'])
                            _notional = _closePrice*_quantity
                            if not(_notional_min <= _notional): _test_quantity = False; _test_quantity_failType = ('MINNOTIONAL', _notional_min, _notional)
                        elif (_serverFilter['filterType'] == 'PERCENT_PRICE'): pass
                    _test_quantity = True
                else: _test_quantity = False; _test_quantity_failType = ('ZEROQUANTITY',)
                if (_test_quantity_failType != None): self.__logger(message = f"Quantity Filter Test Failed For {localID}-{currencySymbol}\n * {str(_test_quantity_failType)}", logType = 'Warning', color = 'light_magenta')
                #[4]: If the quantity check passed, send an order creation request
                if (_test_quantity == True):
                    if   (_pipActionSignal[0] == 'BUY'):  self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'PIP_ENTRY', side = 'BUY',  quantity = _quantity)
                    elif (_pipActionSignal[0] == 'SELL'): self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'PIP_ENTRY', side = 'SELL', quantity = _quantity)
                    _position['_orderCreationRequest']['initialEntryPriceUpdate'] = _closePrice
            #PIP SELL
            elif (_tradeHandler == 'PIP_EXIT'):
                #[1]: Allocated / Committed Balance
                if (_position['allocatedBalance'] == None): _allocatedBalance = 0
                else:                                       _allocatedBalance = _position['allocatedBalance']
                if (_position['entryPrice'] == None): _committedBalance = 0
                else:                                 _committedBalance = abs(_position['quantity'])*_position['entryPrice']/_position['leverage']
                #[2]: Quantity Determination
                _quantity_minUnit = pow(10, -_precisions['quantity'])
                _quantity         = None
                #---From all the satisfied trade scenarios, find the minimum targeting quantity
                _targetMinQuantity_perc = None
                for _sd in _tc['method_exit']:
                    if (((0 < _position['quantity']) and (_sd[0] <= (_closePrice/_position['entryPrice']-1))) or ((_position['quantity'] < 0) and (_sd[0] <= -(_closePrice/_position['entryPrice']-1)))):
                        if ((_targetMinQuantity_perc == None) or (_sd[1] < _targetMinQuantity_perc)): _targetMinQuantity_perc = _sd[1]
                #---Determine the quantity to exit
                if (_targetMinQuantity_perc != None):
                    _targetCommittedBalance = round(_allocatedBalance*_targetMinQuantity_perc, _precisions['quote'])
                    _exitRequiredBalance    = _committedBalance-_targetCommittedBalance
                    if (0 < _exitRequiredBalance): _quantity = round(math.ceil((_exitRequiredBalance/_position['entryPrice']*_tc['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                #[3]: Quantity Check & Order Creation Request
                if ((_quantity != None) and (0 < _quantity)):
                    #---Small quantity handling
                    _quantity_remaining = abs(_position['quantity'])
                    if ((_quantity < pow(10, -_precisions['quantity'])) or (_quantity_remaining <= _quantity)): _quantity = _quantity_remaining
                    #---Order creation request
                    if   (0 < _position['quantity']): self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'PIP_EXIT', side = 'SELL', quantity = _quantity)
                    elif (_position['quantity'] < 0): self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'PIP_EXIT', side = 'BUY',  quantity = _quantity)
            #PIP PSL
            elif (_tradeHandler == 'PIP_PSL'):
                #[1]: Allocated / Committed Balance
                if (_position['allocatedBalance'] == None): _allocatedBalance = 0
                else:                                       _allocatedBalance = _position['allocatedBalance']
                if (_position['entryPrice'] == None): _committedBalance = 0
                else:                                 _committedBalance = abs(_position['quantity'])*_position['entryPrice']/_position['leverage']
                #[2]: Quantity Determination
                _quantity_minUnit = pow(10, -_precisions['quantity'])
                _quantity         = None
                #---From all the satisfied trade scenarios, find the minimum targeting quantity
                _targetMinQuantity_perc = None
                for _sd in _tc['method_psl']:
                    if (((0 < _position['quantity']) and (_sd[0] <= -(_closePrice/_position['entryPrice']-1))) or ((_position['quantity'] < 0) and (_sd[0] <=  (_closePrice/_position['entryPrice']-1)))):
                        if ((_targetMinQuantity_perc == None) or (_sd[1] < _targetMinQuantity_perc)): _targetMinQuantity_perc = _sd[1]
                #---Determine the quantity to exit
                if (_targetMinQuantity_perc != None):
                    _targetCommittedBalance = round(_allocatedBalance*_targetMinQuantity_perc, _precisions['quote'])
                    _exitRequiredBalance    = _committedBalance-_targetCommittedBalance
                    if (0 < _exitRequiredBalance): _quantity = round(math.ceil((_exitRequiredBalance/_position['entryPrice']*_tc['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                #[3]: Quantity Check & Order Creation Request
                if ((_quantity != None) and (0 < _quantity)):
                    #---Small quantity handling
                    _quantity_remaining = abs(_position['quantity'])
                    if ((_quantity < pow(10, -_precisions['quantity'])) or (_quantity_remaining <= _quantity)): _quantity = _quantity_remaining
                    #---Order creation request
                    if   (0 < _position['quantity']): self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'PIP_PSL', side = 'SELL', quantity = _quantity)
                    elif (_position['quantity'] < 0): self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'PIP_PSL', side = 'BUY',  quantity = _quantity)
            #ESCAPE
            elif (_tradeHandler == 'ESCAPE'):
                if   (0 < _position['quantity']): self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'ESCAPE', side = 'SELL', quantity =  _position['quantity'])
                elif (_position['quantity'] < 0): self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'ESCAPE', side = 'BUY',  quantity = -_position['quantity'])
                self.__updateAbruptClearing(localID = localID, positionSymbol = currencySymbol, clearingType = 'ESCAPE')
            #FSL (Full-Stop_Loss)
            elif (_tradeHandler == 'FSL'):
                if   (0 < _position['quantity']): self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'FSL', side = 'SELL', quantity =  _position['quantity'])
                elif (_position['quantity'] < 0): self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'FSL', side = 'BUY',  quantity = -_position['quantity'])
                self.__updateAbruptClearing(localID = localID, positionSymbol = currencySymbol, clearingType = 'FSL')
            #RAF (Reach-And-Fall)
            elif (_tradeHandler == 'RAF'):
                if   (0 < _position['quantity']): self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'RAF', side = 'SELL', quantity =  _position['quantity'])
                elif (_position['quantity'] < 0): self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'RAF', side = 'BUY',  quantity = -_position['quantity'])
            #WR (Weight Reduce)
            elif (_tradeHandler == 'WR'):
                if   (0 < _position['quantity']): self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'WR', side = 'SELL', quantity = _quantity_WR)
                elif (_position['quantity'] < 0): self.__sendOrderCreateRequest(localID = localID, positionSymbol = currencySymbol, logicSource = 'WR', side = 'BUY',  quantity = _quantity_WR)
    def __handleGeneratedPIP_RQPM(self, localID, positionSymbol, generatedPIP):
        #Instances
        _account    = self.__accounts[localID]
        _position   = _account['positions'][positionSymbol]
        _precisions = _position['precisions']
        _asset      = _account['assets'][_position['quoteAsset']]
        _tc         = self.__tradeConfigurations_loaded[_position['tradeConfigurationCode']]['config']
        _kline      = self.__currencies_lastKline[positionSymbol]
        #Kline On PIP Generation
        _klineOnPIPGeneration       = generatedPIP['kline']
        _klineOnPIPGenerationClosed = generatedPIP['klineClosed']
        #PIP Action Signal
        _pipResult = generatedPIP['pipResult']
        if (_pipResult['ACTIONSIGNAL'] == None):
            _pas_allowEntry = None
            _pas_side       = None
        else:
            _pas_allowEntry = _pipResult['ACTIONSIGNAL']['allowEntry']
            _pas_side       = _pipResult['ACTIONSIGNAL']['side']
        #PIP Action Signal Interpretation & Trade Handlers Determination
        _tradeHandler_checkList = {'RQP_ENTRY': None,
                                   'RQP_CLEAR': None,
                                   'RQP_EXIT':  None}
        #---CheckList 1: RQP ENTRY & RQP CLEAR
        if ((_pipResult['ACTIONSIGNAL'] != None) and (_pas_allowEntry == True) and (_klineOnPIPGenerationClosed == True)):
            if (_pas_side == 'BUY'):
                if (_position['quantity'] <= 0):
                    if (((_tc['direction'] == 'LONG') or (_tc['direction'] == 'BOTH')) and (_position['reduceOnly'] == False)): _tradeHandler_checkList['RQP_ENTRY'] = 'BUY'
                    if (_position['quantity'] < 0):                                                                             _tradeHandler_checkList['RQP_CLEAR'] = 'BUY'
            elif (_pas_side == 'SELL'):
                if (0 <= _position['quantity']):
                    if (((_tc['direction'] == 'SHORT') or (_tc['direction'] == 'BOTH')) and (_position['reduceOnly'] == False)): _tradeHandler_checkList['RQP_ENTRY'] = 'SELL'
                    if (0 < _position['quantity']):                                                                              _tradeHandler_checkList['RQP_CLEAR'] = 'SELL'
        #---CheckList 2: RQP_EXIT
        if ((_pipResult['ACTIONSIGNAL'] != None) and (_pas_allowEntry == False) and (_klineOnPIPGenerationClosed == True)):
            if (_position['quantity'] != 0):
                #Exit Conditions Check
                #---Impulse
                if (_tc['rqpm_exitOnImpulse'] == None): _rqpExitTest_impulse = True
                else:
                    if   (_position['quantity'] < 0): _rqpExitTest_impulse = (_pipResult['CLASSICALSIGNAL_CYCLEIMPULSE'] <= -_tc['rqpm_exitOnImpulse'])
                    elif (0 < _position['quantity']): _rqpExitTest_impulse = (_tc['rqpm_exitOnImpulse'] <= _pipResult['CLASSICALSIGNAL_CYCLEIMPULSE'])
                #---Aligned
                if (_tc['rqpm_exitOnAligned'] == None): _rqpExitTest_aligned = True
                else:
                    _pdp_this = _kline[KLINDEX_CLOSEPRICE]/_kline[KLINDEX_OPENPRICE]-1
                    if   (_position['quantity'] < 0): _rqpExitTest_aligned = (_pdp_this <= -_tc['rqpm_exitOnAligned'])
                    elif (0 < _position['quantity']): _rqpExitTest_aligned = (_tc['rqpm_exitOnAligned'] <= _pdp_this)
                #---Profitable
                if (_tc['rqpm_exitOnProfitable'] == None): _rqpExitTest_profitable = True
                else:
                    _pdp = _kline[KLINDEX_CLOSEPRICE]/_position['entryPrice']-1
                    if   (_position['quantity'] < 0): _rqpExitTest_profitable = (_pdp <= -_tc['rqpm_exitOnProfitable'])
                    elif (0 < _position['quantity']): _rqpExitTest_profitable = (_tc['rqpm_exitOnProfitable'] <= _pdp)
                #Finally
                if ((_rqpExitTest_impulse == True) and (_rqpExitTest_aligned == True) and (_rqpExitTest_profitable == True)):
                    if   (_position['quantity'] < 0): _tradeHandler_checkList['RQP_EXIT'] = 'BUY'
                    elif (0 < _position['quantity']): _tradeHandler_checkList['RQP_EXIT'] = 'SELL'
        #---Trade Handlers Determination
        _tradeHandlers = list()
        if (True):
            if (_tradeHandler_checkList['RQP_ENTRY'] is not None):
                if (_tradeHandler_checkList['RQP_CLEAR'] is not None): _tradeHandlers = ['RQP_CLEAR', 'RQP_ENTRY']
                else:                                                  _tradeHandlers = ['RQP_ENTRY',]
            else:
                if   (_tradeHandler_checkList['RQP_CLEAR'] is not None): _tradeHandlers = ['RQP_CLEAR',]
                elif (_tradeHandler_checkList['RQP_EXIT']  is not None): _tradeHandlers = ['RQP_EXIT',]
        _t_current_ns = time.time_ns()
        _position['_tradeHandlers'] += [{'type': _thType, 'side': _tradeHandler_checkList[_thType], 'generationTime_ns': _t_current_ns, 'pipResult': _pipResult.copy(), 'kline': _kline} for _thType in _tradeHandlers]
    def __processTradeHandlers(self, localID):
        _account   = self.__accounts[localID]
        _positions = _account['positions']
        for _pSymbol in _positions:
            _position      = _positions[_pSymbol]
            _precisions    = _position['precisions']
            _tradeHandlers = _position['_tradeHandlers']
            _tradeControl  = _position['tradeControl']
            if ((0 < len(_tradeHandlers)) and (_position['_orderCreationRequest'] is None) and (_position['_marginTypeControlRequested'] == False) and (_position['_leverageControlRequested'] == False)):
                _tradeHandler = _tradeHandlers[0]
                if (time.time_ns()-_tradeHandler['generationTime_ns'] <= _TRADE_TRADEHANDLER_LIFETIME_NS):
                    #Position Data Preparation Status Check
                    if ((_position['tradeConfigurationCode'] is not None) and (_position['tradeConfigurationCode'] in self.__tradeConfigurations_loaded)): _tc = self.__tradeConfigurations_loaded[_position['tradeConfigurationCode']]['config']
                    else:                                                                                                                                  _tc = None
                    if (self.__currencies[_pSymbol]['info_server'] is not None): _serverFilters = self.__currencies[_pSymbol]['info_server']['filters']
                    else:                                                        _serverFilters = None
                    if (_pSymbol in self.__currencies_lastKline): _kline = self.__currencies_lastKline[_pSymbol]
                    else:                                         _kline = None
                    #If Can Process TradeHandlers
                    if ((_tc is not None) and (_serverFilters is not None) and (_kline is not None)):
                        #TS
                        if (_tradeHandler['type'] == 'PIP_ENTRY'):
                            pass
                        #RQPM
                        elif (_tradeHandler['type'] == 'RQP_ENTRY'):
                            #Allocated / Committed Balance
                            if (_position['allocatedBalance'] == None): _allocatedBalance = 0
                            else:                                       _allocatedBalance = _position['allocatedBalance']
                            if (_position['entryPrice'] == None): _committedBalance = 0
                            else:                                 _committedBalance = abs(_position['quantity'])*_position['entryPrice']/_tc['leverage']
                            #Quantity Determination
                            _test_quantity          = True
                            _test_quantity_failType = None
                            _quantity_minUnit = pow(10, -_precisions['quantity'])
                            _quantity = round(int(((_allocatedBalance-_committedBalance)/_kline[KLINDEX_CLOSEPRICE]*_tc['leverage'])/_quantity_minUnit)*_quantity_minUnit, _precisions['quantity'])
                            if (0 < _quantity):
                                for _serverFilter in _serverFilters:
                                    if (_serverFilter['filterType'] == 'PRICE_FILTER'): 
                                        pass
                                    elif (_serverFilter['filterType'] == 'LOT_SIZE'):     
                                        pass
                                    elif (_serverFilter['filterType'] == 'MARKET_LOT_SIZE'):
                                        _minQty   = float(_serverFilter['minQty'])
                                        _maxQty   = float(_serverFilter['maxQty'])
                                        _stepSize = float(_serverFilter['stepSize'])
                                        if not(_minQty <= _quantity):                                              _test_quantity = False; _test_quantity_failType = ('MINQTY',   _minQty, _quantity)
                                        if not(_quantity <= _maxQty):                                              _test_quantity = False; _test_quantity_failType = ('MAXQTY',   _maxQty, _quantity)
                                        if not(_quantity == round(_quantity, -math.floor(math.log10(_stepSize)))): _test_quantity = False; _test_quantity_failType = ('STEPSIZE', _stepSize, math.floor(math.log10(_stepSize)), round(_quantity, -math.floor(math.log10(_stepSize))), _quantity)
                                    elif (_serverFilter['filterType'] == 'MAX_NUM_ORDERS'): 
                                        pass
                                    elif (_serverFilter['filterType'] == 'MAX_NUM_ALGO_ORDERS'): 
                                        pass
                                    elif (_serverFilter['filterType'] == 'MIN_NOTIONAL'):
                                        _notional_min = float(_serverFilter['notional'])
                                        _notional = _kline[KLINDEX_CLOSEPRICE]*_quantity
                                        if not(_notional_min <= _notional): _test_quantity = False; _test_quantity_failType = ('MINNOTIONAL', _notional_min, _notional)
                                    elif (_serverFilter['filterType'] == 'PERCENT_PRICE'): 
                                        pass
                            else: _test_quantity = False; _test_quantity_failType = ('ZEROQUANTITY', _quantity)
                            if (_test_quantity_failType is not None): self.__logger(message = f"Quantity Filter Test Failed For {localID}-{_pSymbol}\n * {str(_test_quantity_failType)}", logType = 'Warning', color = 'light_magenta')
                            #Side Confirm
                            _side_confirmed = False
                            if   ((_position['quantity'] <= 0) and (_tradeHandler['side'] == 'SELL')): _side_confirmed = True
                            elif ((0 <= _position['quantity']) and (_tradeHandler['side'] == 'BUY')):  _side_confirmed = True
                            #Finally
                            if ((_test_quantity == True) and (_side_confirmed == True)):
                                self.__orderCreationRequest_generate(localID            = localID,
                                                                     positionSymbol     = _pSymbol,
                                                                     logicSource        = 'RQP_ENTRY',
                                                                     side               = _tradeHandler['side'],
                                                                     quantity           = _quantity,
                                                                     tradeControlUpdate = {'tcMode':               'RQPM',
                                                                                           'rqpm_entryTimestamp':  {'onComplete': _kline[KLINDEX_OPENTIME],          'onPartial': _kline[KLINDEX_OPENTIME],          'onFail': None},
                                                                                           'rqpm_initialQuantity': {'onComplete': _quantity,                         'onPartial': '#ABSQUANTITY#',                   'onFail': None},
                                                                                           'rqpm_fslcTrigger':     {'onComplete': _tradeControl['rqpm_fslcTrigger'], 'onPartial': _tradeControl['rqpm_fslcTrigger'], 'onFail': _tradeControl['rqpm_fslcTrigger']}},
                                                                     ipcRID             = None)
                        elif (_tradeHandler['type'] == 'RQP_CLEAR'):
                            #Quantity Determination
                            if   (_position['quantity'] < 0):  _quantity = -_position['quantity']
                            elif (0 < _position['quantity']):  _quantity =  _position['quantity']
                            elif (_position['quantity'] == 0): _quantity = 0
                            #Side Confirm
                            _side_confirmed = False
                            if   ((_position['quantity'] < 0) and (_tradeHandler['side'] == 'BUY')):  _side_confirmed = True
                            elif ((0 < _position['quantity']) and (_tradeHandler['side'] == 'SELL')): _side_confirmed = True
                            #Finally
                            if ((0 < _quantity) and (_side_confirmed == True)):
                                self.__orderCreationRequest_generate(localID             = localID,
                                                                     positionSymbol      = _pSymbol,
                                                                     logicSource         = 'RQP_CLEAR',
                                                                     side                = _tradeHandler['side'],
                                                                     quantity            = _quantity,
                                                                     tradeControlUpdate  = {'tcMode':               'RQPM',
                                                                                            'rqpm_entryTimestamp':  {'onComplete': None, 'onPartial': _tradeControl['rqpm_entryTimestamp'],  'onFail': _tradeControl['rqpm_entryTimestamp']},
                                                                                            'rqpm_initialQuantity': {'onComplete': None, 'onPartial': _tradeControl['rqpm_initialQuantity'], 'onFail': _tradeControl['rqpm_initialQuantity']},
                                                                                            'rqpm_fslcTrigger':     {'onComplete': None, 'onPartial': _tradeControl['rqpm_fslcTrigger'],     'onFail': _tradeControl['rqpm_fslcTrigger']}},
                                                                     ipcRID              = None)
                        elif (_tradeHandler['type'] == 'RQP_EXIT'):
                            #RQP Value
                            _rqpfp_contIndex = int((_kline[KLINDEX_OPENTIME]-_position['tradeControl']['rqpm_entryTimestamp'])/KLINTERVAL_S)
                            _rqpfp_pdp       = round(_kline[KLINDEX_CLOSEPRICE]/_position['entryPrice']-1, 4)
                            if   (_position['quantity'] < 0):  _rqpmValue = atmEta_RQPMFunctions.RQPMFUNCTIONS[_tc['rqpm_functionType']](params = _tc['rqpm_functionParams_SHORT'], continuationIndex = _rqpfp_contIndex, priceDeltaPercentage = _rqpfp_pdp)
                            elif (0 < _position['quantity']):  _rqpmValue = atmEta_RQPMFunctions.RQPMFUNCTIONS[_tc['rqpm_functionType']](params = _tc['rqpm_functionParams_LONG'],  continuationIndex = _rqpfp_contIndex, priceDeltaPercentage = _rqpfp_pdp)
                            elif (_position['quantity'] == 0): _rqpmValue = 0
                            #Quantity Determination
                            _quantity_minUnit = pow(10, -_precisions['quantity'])
                            _quantity_target  = round(_position['tradeControl']['rqpm_initialQuantity']*_rqpmValue, _precisions['quantity'])
                            _quantity = round(abs(_position['quantity'])-_quantity_target, _precisions['quantity'])
                            #Side Confirm
                            _side_confirmed = False
                            if   ((_position['quantity'] < 0) and (_tradeHandler['side'] == 'BUY')):  _side_confirmed = True
                            elif ((0 < _position['quantity']) and (_tradeHandler['side'] == 'SELL')): _side_confirmed = True
                            #Finally
                            if ((0 < _quantity) and (_side_confirmed == True)):
                                if (_quantity < _quantity_minUnit):          _quantity = round(_quantity_minUnit, _precisions['quantity'])
                                if (abs(_position['quantity']) < _quantity): _quantity = abs(_position['quantity'])
                                if (_quantity_target == 0):
                                    _tcUpdate = {'tcMode':               'RQPM',
                                                 'rqpm_entryTimestamp':  {'onComplete': None, 'onPartial': _tradeControl['rqpm_entryTimestamp'],  'onFail': _tradeControl['rqpm_entryTimestamp']},
                                                 'rqpm_initialQuantity': {'onComplete': None, 'onPartial': _tradeControl['rqpm_initialQuantity'], 'onFail': _tradeControl['rqpm_initialQuantity']},
                                                 'rqpm_fslcTrigger':     {'onComplete': None, 'onPartial': _tradeControl['rqpm_fslcTrigger'],     'onFail': _tradeControl['rqpm_fslcTrigger']}}
                                else:       
                                    _tcUpdate = {'tcMode':               'RQPM',
                                                 'rqpm_entryTimestamp':  {'onComplete': _tradeControl['rqpm_entryTimestamp'],  'onPartial': _tradeControl['rqpm_entryTimestamp'],  'onFail': _tradeControl['rqpm_entryTimestamp']},
                                                 'rqpm_initialQuantity': {'onComplete': _tradeControl['rqpm_initialQuantity'], 'onPartial': _tradeControl['rqpm_initialQuantity'], 'onFail': _tradeControl['rqpm_initialQuantity']},
                                                 'rqpm_fslcTrigger':     {'onComplete': _tradeControl['rqpm_fslcTrigger'],     'onPartial': _tradeControl['rqpm_fslcTrigger'],     'onFail': _tradeControl['rqpm_fslcTrigger']}}
                                self.__orderCreationRequest_generate(localID             = localID,
                                                                     positionSymbol      = _pSymbol,
                                                                     logicSource         = 'RQP_EXIT',
                                                                     side                = _tradeHandler['side'],
                                                                     quantity            = _quantity,
                                                                     tradeControlUpdate  = _tcUpdate,
                                                                     ipcRID              = None)
                        elif (_tradeHandler['type'] == 'RQP_FSLIMMED'):
                            #Quantity Determination
                            if   (_position['quantity'] < 0):  _quantity = -_position['quantity']
                            elif (0 < _position['quantity']):  _quantity =  _position['quantity']
                            elif (_position['quantity'] == 0): _quantity = 0
                            #Side Confirm
                            _side_confirmed = False
                            if   ((_position['quantity'] < 0) and (_tradeHandler['side'] == 'BUY')):  _side_confirmed = True
                            elif ((0 < _position['quantity']) and (_tradeHandler['side'] == 'SELL')): _side_confirmed = True
                            #Finally
                            if ((0 < _quantity) and (_side_confirmed == True)):
                                self.__orderCreationRequest_generate(localID            = localID,
                                                                     positionSymbol     = _pSymbol,
                                                                     logicSource        = 'RQP_FSLIMMED',
                                                                     side               = _tradeHandler['side'],
                                                                     quantity           = _quantity,
                                                                     tradeControlUpdate = {'tcMode':               'RQPM',
                                                                                           'rqpm_entryTimestamp':  {'onComplete': None, 'onPartial': _tradeControl['rqpm_entryTimestamp'],  'onFail': _tradeControl['rqpm_entryTimestamp']},
                                                                                           'rqpm_initialQuantity': {'onComplete': None, 'onPartial': _tradeControl['rqpm_initialQuantity'], 'onFail': _tradeControl['rqpm_initialQuantity']},
                                                                                           'rqpm_fslcTrigger':     {'onComplete': None, 'onPartial': _tradeControl['rqpm_fslcTrigger'],     'onFail': _tradeControl['rqpm_fslcTrigger']}},
                                                                     ipcRID             = None)
                        elif (_tradeHandler['type'] == 'RQP_FSLCLOSE'):
                            #Quantity Determination
                            if   (_position['quantity'] < 0):  _quantity = -_position['quantity']
                            elif (0 < _position['quantity']):  _quantity =  _position['quantity']
                            elif (_position['quantity'] == 0): _quantity = 0
                            #Side Confirm
                            _side_confirmed = False
                            if   ((_position['quantity'] < 0) and (_tradeHandler['side'] == 'BUY')):  _side_confirmed = True
                            elif ((0 < _position['quantity']) and (_tradeHandler['side'] == 'SELL')): _side_confirmed = True
                            #Finally
                            if ((0 < _quantity) and (_side_confirmed == True)):
                                self.__orderCreationRequest_generate(localID            = localID,
                                                                     positionSymbol     = _pSymbol,
                                                                     logicSource        = 'RQP_FSLCLOSE',
                                                                     side               = _tradeHandler['side'],
                                                                     quantity           = _quantity,
                                                                     tradeControlUpdate = {'tcMode':               'RQPM',
                                                                                           'rqpm_entryTimestamp':  {'onComplete': None, 'onPartial': _tradeControl['rqpm_entryTimestamp'],  'onFail': _tradeControl['rqpm_entryTimestamp']},
                                                                                           'rqpm_initialQuantity': {'onComplete': None, 'onPartial': _tradeControl['rqpm_initialQuantity'], 'onFail': _tradeControl['rqpm_initialQuantity']},
                                                                                           'rqpm_fslcTrigger':     {'onComplete': None, 'onPartial': _tradeControl['rqpm_fslcTrigger'],     'onFail': _tradeControl['rqpm_fslcTrigger']}},
                                                                     ipcRID             = None)
                        #Handled Trade Handler Removal
                        _tradeHandlers.pop(0)
                else: _tradeHandlers.pop(0)
    def __orderCreationRequest_generate(self, localID, positionSymbol, logicSource, side, quantity, tradeControlUpdate = None, ipcRID = None):
        _account    = self.__accounts[localID]
        _position   = _account['positions'][positionSymbol]
        _precisions = _position['precisions']
        #OCR Generation
        if   (side == 'BUY'):  _targetQuantity = round(_position['quantity']+quantity, _precisions['quantity'])
        elif (side == 'SELL'): _targetQuantity = round(_position['quantity']-quantity, _precisions['quantity'])
        _ocr = {'logicSource':          logicSource,
                'forceClearRID':        ipcRID,
                'originalQuantity':     _position['quantity'],
                'targetQuantity':       _targetQuantity,
                'orderParams':          {'symbol':     positionSymbol,
                                         'side':       side,
                                         'type':       'MARKET',
                                         'quantity':   quantity,
                                         'reduceOnly': not((logicSource == 'PIP_ENTRY') or (logicSource == 'RQP_ENTRY'))},
                'tradeControlUpdate':   tradeControlUpdate,
                'dispatchID':           None,
                'lastRequestReceived':  False,
                'results':              list(),
                'nAttempts':            1}
        _position['_orderCreationRequest'] = _ocr
        #Request Dispatch
        #---Virtual
        if (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL): 
            _account_virtualServer = self.__accounts_virtualServer[localID]
            _ocr['dispatchID'] = time.perf_counter_ns()
            _account_virtualServer['_orderCreationRequests'][_ocr['dispatchID']] = {'positionSymbol': positionSymbol,
                                                                                    'orderParams':    _ocr['orderParams'].copy()}
        #---Actual
        elif (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_ACTUAL):
            _ocr['dispatchID'] = self.ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                                                   functionID     = 'createOrder', 
                                                   functionParams = {'localID':        localID, 
                                                                     'positionSymbol': positionSymbol, 
                                                                     'orderParams':    _ocr['orderParams'].copy()}, 
                                                   farrHandler    = self.__far_onPositionControlResponse)
    def __orderCreationRequest_regenerate(self, localID, positionSymbol, quantity_unfilled):
        #Instances
        _account  = self.__accounts[localID]
        _position = _account['positions'][positionSymbol]
        _ocr = _position['_orderCreationRequest']
        #OCR Update
        _ocr['orderParams'] = {'symbol':     positionSymbol,
                               'side':       _ocr['orderParams']['side'],
                               'type':       'MARKET',
                               'quantity':   quantity_unfilled,
                               'reduceOnly': _ocr['orderParams']['reduceOnly']}
        _ocr['lastRequestReceived'] = False
        if (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL): 
            _account_virtualServer = self.__accounts_virtualServer[localID]
            _ocr['dispatchID'] = time.perf_counter_ns()
            _account_virtualServer['_orderCreationRequests'][_ocr['dispatchID']] = {'positionSymbol': positionSymbol,
                                                                                    'orderParams':    _ocr['orderParams'].copy()}
        elif (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_ACTUAL):
            _ocr['dispatchID'] = self.ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                                                   functionID     = 'createOrder', 
                                                   functionParams = {'localID':        localID, 
                                                                     'positionSymbol': positionSymbol, 
                                                                     'orderParams':    _ocr['orderParams'].copy()}, 
                                                   farrHandler    = self.__far_onPositionControlResponse)
        _ocr['nAttempts'] += 1
    def __orderCreationRequest_terminate(self, localID, positionSymbol, quantity_new):
        #Instances
        _account  = self.__accounts[localID]
        _position = _account['positions'][positionSymbol]
        _ocr      = _position['_orderCreationRequest']
        #Update Mode Determination
        if (quantity_new == _ocr['targetQuantity']): _updateMode = 'onComplete'
        else:
            if (_ocr['targetQuantity'] < _ocr['originalQuantity']):
                if (_ocr['targetQuantity'] < quantity_new) and (quantity_new < _ocr['originalQuantity']): _updateMode = 'onPartial'
                else:                                                                                     _updateMode = 'onFail'
            elif (_ocr['originalQuantity'] < _ocr['targetQuantity']):
                if (_ocr['originalQuantity'] < quantity_new) and (quantity_new < _ocr['targetQuantity']): _updateMode = 'onPartial'
                else:                                                                                     _updateMode = 'onFail'
        #Trade Control Update
        if (_ocr['tradeControlUpdate'] is not None):
            _position['tradeControl'] = self.__getUpdatedTradeControl(localID = localID, positionSymbol = positionSymbol, tradeControlUpdate = _ocr['tradeControlUpdate'], updateMode = _updateMode)
            self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'positions', positionSymbol, 'tradeControl'), self.__copyTradeControl(tradeControl = _position['tradeControl'])),]}, farrHandler = None)
        #Force Clear Response    
        if (_ocr['forceClearRID'] != None):
            _fcComplete = (_updateMode == 'onComplete')
            if (_fcComplete == True): _forceClearResponseMessage = "Account '{:s}' Position '{:s}' Position Force Clear Successful!".format(localID, positionSymbol)
            else:                     _forceClearResponseMessage = "Account '{:s}' Position '{:s}' Position Force Clear Failed".format(localID,      positionSymbol)
            self.ipcA.sendFARR(targetProcess  = 'GUI', 
                               functionResult = {'localID':        localID, 
                                                 'positionSymbol': positionSymbol, 
                                                 'responseOn':     'FORCECLEARPOSITION',
                                                 'result':         _fcComplete,
                                                 'message':        _forceClearResponseMessage}, 
                               requestID      = _ocr['forceClearRID'], 
                               complete       = True)
        #OCR Initialization
        _position['_orderCreationRequest'] = None
    def __trade_processVirtualServer(self):
        _toRequestDBUpdate = list()
        for _localID in self.__accounts_virtualServer:
            _account_virtualServer   = self.__accounts_virtualServer[_localID]
            if (_ACCOUNT_UPDATEINTERVAL_NS < time.perf_counter_ns()-_account_virtualServer['_lastUpdated']): 
                _account_virtualServer['_lastUpdated'] = time.perf_counter_ns()
                _account   = self.__accounts[_localID]
                _positions = _account['positions']
                _assets_virtualServer    = _account_virtualServer['assets']
                _positions_virtualServer = _account_virtualServer['positions']
                #[1]: Previous Data Copy
                _assets_virtualServer_prev    = dict()
                _positions_virtualServer_prev = dict()
                for _assetName in _assets_virtualServer:
                    _assets_virtualServer_prev[_assetName] = dict()
                    for _dataKey in _VIRTUALACCOUNTDBANNOUNCEMENT_ASSETDATANAMES: _assets_virtualServer_prev[_assetName][_dataKey] = _assets_virtualServer[_assetName][_dataKey]
                for _pSymbol in _positions_virtualServer:
                    _positions_virtualServer_prev[_pSymbol] = dict()
                    for _dataKey in _VIRTUALACCOUNTDBANNOUNCEMENT_POSITIONDATANAMES: _positions_virtualServer_prev[_pSymbol][_dataKey] = _positions_virtualServer[_pSymbol][_dataKey]
                #[2]: Margin Type Control Requests
                for _mcr in _account_virtualServer['_marginTypeControlRequests']:
                    _pSymbol       = _mcr['positionSymbol']
                    _newMarginType = _mcr['newMarginType']
                    if   (_newMarginType == 'ISOLATED'): _positions_virtualServer[_pSymbol]['isolated'] = True
                    elif (_newMarginType == 'CROSSED'):  _positions_virtualServer[_pSymbol]['isolated'] = False
                _account_virtualServer['_marginTypeControlRequests'].clear()
                #[3]: Leverage Control Requests
                for _lcr in _account_virtualServer['_leverageControlRequests']:
                    _pSymbol     = _lcr['positionSymbol']
                    _newLeverage = _lcr['newLeverage']
                    _positions_virtualServer[_pSymbol]['leverage'] = _newLeverage
                _account_virtualServer['_leverageControlRequests'].clear()
                #[4]: Non-Zero Positions
                _pSymbols_holdingPosition = [_pSymbol for _pSymbol in _positions_virtualServer  if (_positions_virtualServer[_pSymbol]['quantity'] != 0)]
                _account_virtualServer['_nonZeroQuantityPositions_isolated'] = set(_pSymbol for _pSymbol in _pSymbols_holdingPosition if (_positions_virtualServer[_pSymbol]['isolated'] == True))
                _account_virtualServer['_nonZeroQuantityPositions_crossed']  = set(_pSymbol for _pSymbol in _pSymbols_holdingPosition if (_positions_virtualServer[_pSymbol]['isolated'] == False))
                #[5]: Positions
                for _pSymbol in _positions_virtualServer:
                    _position               = _positions[_pSymbol]
                    _position_virtualServer = _positions_virtualServer[_pSymbol]
                    _asset_virtualServer    = _assets_virtualServer[_position['quoteAsset']]
                    _precisions = _position['precisions']
                    #---Delisted Position Clearing
                    if (_pSymbol in self.__currencies): _currencyData = self.__currencies[_pSymbol]
                    else:                               _currencyData = None
                    if (((_currencyData is None) or ((_currencyData['info_server'] != None) and (_currencyData['info_server']['status'] == 'REMOVED'))) and (_position_virtualServer['quantity'] != 0)):
                        if (_position['isolated'] == False):
                            _notionalValue                             = round(abs(_position_virtualServer['quantity'])*_position_virtualServer['entryPrice'], _precisions['quote'])
                            _asset_virtualServer['crossWalletBalance'] = round(_asset_virtualServer['crossWalletBalance']-_notionalValue,                      _precisions['quote'])
                        _position_virtualServer['quantity']               = 0
                        _position_virtualServer['entryPrice']             = None
                        _position_virtualServer['isolatedWalletBalance']  = 0
                        _position_virtualServer['positionInitialMargin']  = 0
                        _position_virtualServer['openOrderInitialMargin'] = 0
                        _position_virtualServer['maintenanceMargin']      = 0
                        _position_virtualServer['unrealizedPNL']          = 0
                        if (_position['isolated'] == True): _account_virtualServer['_nonZeroQuantityPositions_isolated'].remove(_pSymbol)
                        else:                               _account_virtualServer['_nonZeroQuantityPositions_crossed'].remove(_pSymbol)
                    #---Position Data Computation
                    self.__trade_processVirtualServer_computePosition(localID = _localID, positionSymbol = _pSymbol)
                #[6]: Assets
                for _assetName in _assets_virtualServer: self.__trade_processVirtualServer_computeAsset(localID = _localID, assetName = _assetName)
                #[7]: Check Liquidations
                _liqPriceComputeParams = dict()
                for _assetName in _assets_virtualServer: _liqPriceComputeParams[_assetName] = {'compute': True, 'maintenanceMargin_crossed': 0, 'unrealizedPNL_crossed': 0}
                for _pSymbol in _positions_virtualServer:
                    _position               = _positions[_pSymbol]
                    _position_virtualServer = _positions_virtualServer[_pSymbol]
                    _assetName              = _position['quoteAsset']
                    _asset_virtualServer    = _assets_virtualServer[_assetName]
                    _precisions             = _position['precisions']
                    #Liquidation Price Params Computation
                    if (_liqPriceComputeParams[_assetName]['compute'] == True): 
                        _liqPriceComputeParams[_assetName]['maintenanceMargin_crossed'] = sum(_positions_virtualServer[__pSymbol]['maintenanceMargin'] for __pSymbol in _account_virtualServer['_nonZeroQuantityPositions_crossed'] if (_positions[__pSymbol]['quoteAsset'] == _assetName))
                        _liqPriceComputeParams[_assetName]['unrealizedPNL_crossed']     = sum(_positions_virtualServer[__pSymbol]['unrealizedPNL']     for __pSymbol in _account_virtualServer['_nonZeroQuantityPositions_crossed'] if (_positions[__pSymbol]['quoteAsset'] == _assetName))
                        _liqPriceComputeParams[_assetName]['compute'] = False
                    #Liquidation Handling
                    if (_pSymbol in self.__currencies_lastKline): _lastKline = self.__currencies_lastKline[_pSymbol]
                    else:                                         _lastKline = None
                    if (_lastKline != None):
                        if (_position['isolated'] == True): _wb = _position_virtualServer['isolatedWalletBalance']
                        else:                               _wb = _asset_virtualServer['crossWalletBalance']
                        _liquidationPrice = self.__computeLiquidationPrice(positionSymbol    = _pSymbol,
                                                                           walletBalance     = _wb,
                                                                           quantity          = _position_virtualServer['quantity'],
                                                                           entryPrice        = _position_virtualServer['entryPrice'],
                                                                           currentPrice      = _lastKline[KLINDEX_CLOSEPRICE],
                                                                           maintenanceMargin = _position_virtualServer['maintenanceMargin'],
                                                                           upnl              = _position_virtualServer['unrealizedPNL'],
                                                                           isolated          = _position['isolated'],
                                                                           mm_crossTotal     = _liqPriceComputeParams[_assetName]['maintenanceMargin_crossed'],
                                                                           upnl_crossTotal   = _liqPriceComputeParams[_assetName]['unrealizedPNL_crossed'])
                        if (_liquidationPrice != None):
                            if (((0 < _position_virtualServer['quantity']) and (_lastKline[KLINDEX_LOWPRICE] <= _liquidationPrice)) or ((_position_virtualServer['quantity'] < 0) and (_liquidationPrice <= _lastKline[KLINDEX_HIGHPRICE]))):
                                _profit     = round(_position_virtualServer['quantity']*(_liquidationPrice-_position_virtualServer['entryPrice']), _precisions['quote'])
                                _tradingFee = round(abs(_position_virtualServer['quantity'])*_liquidationPrice*_VIRTUALTRADE_LIQUIDATIONFEE,       _precisions['quote'])
                                if (_position['isolated'] == True): _asset_virtualServer['crossWalletBalance'] = round(_asset_virtualServer['crossWalletBalance']+_position_virtualServer['isolatedWalletBalance'], _ACCOUNT_ASSETPRECISIONS[_assetName])
                                _asset_virtualServer['crossWalletBalance'] = round(_asset_virtualServer['crossWalletBalance']+_profit-_tradingFee, _ACCOUNT_ASSETPRECISIONS[_assetName])
                                if (_asset_virtualServer['crossWalletBalance'] < 0): _asset_virtualServer['crossWalletBalance'] = 0
                                _position_virtualServer['quantity']               = 0
                                _position_virtualServer['entryPrice']             = None
                                _position_virtualServer['isolatedWalletBalance']  = 0
                                _position_virtualServer['positionInitialMargin']  = 0
                                _position_virtualServer['openOrderInitialMargin'] = 0
                                _position_virtualServer['maintenanceMargin']      = 0
                                _position_virtualServer['unrealizedPNL']          = 0
                                if (_position['isolated'] == True): _account_virtualServer['_nonZeroQuantityPositions_isolated'].remove(_pSymbol)
                                else:                               _account_virtualServer['_nonZeroQuantityPositions_crossed'].remove(_pSymbol)
                                self.__trade_processVirtualServer_computeAsset(localID = _localID, assetName = _assetName)
                                if (_position['isolated'] == False): _liqPriceComputeParams[_assetName]['compute'] = True
                #[8]: Order Creation Requests
                _ocrIDs_handled = set()
                for _ocrID in _account_virtualServer['_orderCreationRequests']:
                    #Order Creation Request
                    _ocr         = _account_virtualServer['_orderCreationRequests'][_ocrID]
                    _pSymbol     = _ocr['positionSymbol']
                    _orderParams = _ocr['orderParams']
                    #Kline Check
                    if (_pSymbol in self.__currencies_lastKline): _lastKline = self.__currencies_lastKline[_pSymbol]
                    else:                                         _lastKline = None
                    if (_lastKline != None):
                        #Instances
                        _position               = _positions[_pSymbol]
                        _position_virtualServer = _positions_virtualServer[_pSymbol]
                        _asset_virtualServer    = _assets_virtualServer[_position['quoteAsset']]
                        _precisions             = _position['precisions']
                        _lastKline              = self.__currencies_lastKline[_pSymbol]
                        #Request Handling
                        #---Randomized Result Generator
                        _result = (random.randint(a = 1, b = 100) <= int(_VIRTUALTRADE_SERVER_PROBABILITY_SUCCESS*100))
                        if (_result == True):
                            _incompleteExecution = (random.randint(a = 1, b = 100) <= int(_VIRTUALTRADE_SERVER_PROBABILITY_INCOMPLETEEXECUTION*100))
                            if (_incompleteExecution == True): _quantity_executed = round(_orderParams['quantity']*random.randint(a = 0, b = 0)/100, _precisions['quantity'])
                            else:                              _quantity_executed = _orderParams['quantity']
                            #---Quantity
                            if   (_orderParams['side'] == 'BUY'):  _quantity_new = round(_position_virtualServer['quantity']+_quantity_executed, _precisions['quantity'])
                            elif (_orderParams['side'] == 'SELL'): _quantity_new = round(_position_virtualServer['quantity']-_quantity_executed, _precisions['quantity'])
                            _quantity_dirDelta = round(abs(_quantity_new)-abs(_position_virtualServer['quantity']), _precisions['quantity'])
                            #---Cost, Profit & Entry Price
                            if (0 <= _quantity_dirDelta):
                                #Entry Price
                                if (_quantity_new == 0): _entryPrice_new = None
                                else:
                                    if (_position_virtualServer['quantity'] == 0): _notional_prev = 0
                                    else:                                          _notional_prev = abs(_position_virtualServer['quantity'])*_position_virtualServer['entryPrice']
                                    _notional_new = _notional_prev+_quantity_dirDelta*_lastKline[KLINDEX_CLOSEPRICE]
                                    _entryPrice_new = round(_notional_new/abs(_quantity_new), _precisions['price'])
                                #Profit
                                _profit = 0
                            elif (_quantity_dirDelta < 0):
                                #Entry Price
                                if (_quantity_new == 0): _entryPrice_new = None
                                else:                    _entryPrice_new = _position_virtualServer['entryPrice']
                                #Profit
                                if   (_orderParams['side'] == 'BUY'):  _profit = round(_quantity_executed*(_position_virtualServer['entryPrice']-_lastKline[KLINDEX_CLOSEPRICE]), _precisions['quote'])
                                elif (_orderParams['side'] == 'SELL'): _profit = round(_quantity_executed*(_lastKline[KLINDEX_CLOSEPRICE]-_position_virtualServer['entryPrice']), _precisions['quote'])
                            _tradingFee = round(_quantity_executed*_lastKline[KLINDEX_CLOSEPRICE]*_VIRTUALTRADE_MARKETTRADINGFEE, _precisions['quote'])
                            #Apply Values
                            _position_virtualServer['quantity']        = _quantity_new
                            _position_virtualServer['entryPrice']      = _entryPrice_new
                            _asset_virtualServer['crossWalletBalance'] = round(_asset_virtualServer['crossWalletBalance']+_profit-_tradingFee, _precisions['quote'])
                            if (_position_virtualServer['isolated'] == True):
                                # _walletBalanceToTransfer = Balance from 'CrossWalletBalance' -> 'IsolatedWalletBalance' (Assuming all the other additional parameters (Insurance Fund, Open-Loss, etc) to be 1% of the notional value)
                                #---Entry
                                if (0 <= _quantity_dirDelta): _walletBalanceToTransfer = round(_quantity_executed*_lastKline[KLINDEX_CLOSEPRICE]*((1/_position_virtualServer['leverage'])+0.01), _precisions['quote'])
                                #---Exit
                                elif (_quantity_dirDelta < 0):
                                    if (_quantity_new == 0): _walletBalanceToTransfer = -_position_virtualServer['isolatedWalletBalance']
                                    else:                    _walletBalanceToTransfer = -round(_quantity_executed*_position_virtualServer['entryPrice']/_position_virtualServer['leverage'], _precisions['quote'])
                                _position_virtualServer['isolatedWalletBalance'] = round(_position_virtualServer['isolatedWalletBalance']+_walletBalanceToTransfer, _precisions['quote'])
                                _asset_virtualServer['crossWalletBalance']       = round(_asset_virtualServer['crossWalletBalance']      -_walletBalanceToTransfer, _precisions['quote'])
                            #Non-Zero Quantity Position Symbols Control
                            if (_quantity_new == 0):
                                if (_position['isolated'] == True): _account_virtualServer['_nonZeroQuantityPositions_isolated'].remove(_pSymbol)
                                else:                               _account_virtualServer['_nonZeroQuantityPositions_crossed'].remove(_pSymbol)
                            else:
                                if (_position['isolated'] == True): _account_virtualServer['_nonZeroQuantityPositions_isolated'].add(_pSymbol)
                                else:                               _account_virtualServer['_nonZeroQuantityPositions_crossed'].add(_pSymbol)
                            self.__trade_processVirtualServer_computePosition(localID = _localID, positionSymbol = _pSymbol)
                            self.__trade_processVirtualServer_computeAsset(localID    = _localID, assetName      = _position['quoteAsset'])
                        #Result Posting
                        _ocr_local = _position['_orderCreationRequest']
                        if (_ocr_local is not None):
                            if (_ocr_local['dispatchID'] == _ocrID):
                                if (_result == True):
                                    _failType = None
                                    _orderResult = {'type':             _orderParams['type'],
                                                    'side':             _orderParams['side'],
                                                    'averagePrice':     _lastKline[KLINDEX_CLOSEPRICE],
                                                    'originalQuantity': _orderParams['quantity'],
                                                    'executedQuantity': _quantity_executed}
                                else:
                                    _failType    = 'VIRTUALRANDOMFAIL'
                                    _orderResult = None
                                #Finally
                                _requestResult = {'resultReceivalTime': time.time(), 
                                                  'result':             _result,
                                                  'failType':           _failType,
                                                  'orderResult':        _orderResult,
                                                  'errorMessage':       None}
                                _ocr_local['results'].append(_requestResult)
                                _ocr_local['lastRequestReceived'] = True
                        #Handlded OCR ID
                        _ocrIDs_handled.add(_ocrID)
                for _ocrID_handled in _ocrIDs_handled: del _account_virtualServer['_orderCreationRequests'][_ocrID_handled]
                #[9]: Data Comparison & DB Update Append
                for _assetName in _assets_virtualServer_prev: 
                    for _dataKey in _assets_virtualServer_prev[_assetName]:
                        if (_assets_virtualServer[_assetName][_dataKey] != _assets_virtualServer_prev[_assetName][_dataKey]): _toRequestDBUpdate.append(((_localID, 'assets', _assetName, _dataKey), _assets_virtualServer[_assetName][_dataKey]))
                for _pSymbol in _positions_virtualServer_prev: 
                    for _dataKey in _positions_virtualServer_prev[_pSymbol]:
                        if (_positions_virtualServer[_pSymbol][_dataKey] != _positions_virtualServer_prev[_pSymbol][_dataKey]): _toRequestDBUpdate.append(((_localID, 'positions', _pSymbol, _dataKey), _positions_virtualServer[_pSymbol][_dataKey]))
        #DB Update Requests
        if (0 < len(_toRequestDBUpdate)): self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': _toRequestDBUpdate}, farrHandler = None)
    def __trade_processVirtualServer_computePosition(self, localID, positionSymbol):
        _account                = self.__accounts[localID]
        _account_virtualServer  = self.__accounts_virtualServer[localID]
        _position               = _account['positions'][positionSymbol]
        _position_virtualServer = _account_virtualServer['positions'][positionSymbol]
        _precisions = _position['precisions']
        #---Last Kline
        if (positionSymbol in self.__currencies_lastKline): _lastKline = self.__currencies_lastKline[positionSymbol]
        else:                                               _lastKline = None
        #---Position Initial Margin & Unrealized PNL Computation
        if (_position_virtualServer['quantity'] == 0):
            _position_virtualServer['positionInitialMargin'] = 0
            _position_virtualServer['unrealizedPNL']         = 0
            _position_virtualServer['maintenanceMargin']     = 0
        elif (_lastKline is None):
            _position_virtualServer['positionInitialMargin'] = None
            _position_virtualServer['unrealizedPNL']         = None
            _position_virtualServer['maintenanceMargin']     = None
        else:
            _currentNotional = _lastKline[KLINDEX_CLOSEPRICE]*abs(_position['quantity'])
            _position_virtualServer['positionInitialMargin'] = round(_currentNotional/_position['leverage'], _precisions['quote'])
            if   (_position_virtualServer['quantity'] < 0): _position_virtualServer['unrealizedPNL'] = round((_position_virtualServer['entryPrice']-_lastKline[KLINDEX_CLOSEPRICE])*abs(_position_virtualServer['quantity']), _precisions['quote'])
            elif (0 < _position_virtualServer['quantity']): _position_virtualServer['unrealizedPNL'] = round((_lastKline[KLINDEX_CLOSEPRICE]-_position_virtualServer['entryPrice'])*abs(_position_virtualServer['quantity']), _precisions['quote'])
            _maintenanceMarginRate, _maintenanceAmount = atmEta_Constants.getMaintenanceMarginRateAndAmount(positionSymbol = positionSymbol, notional = _currentNotional)
            _position_virtualServer['maintenanceMargin'] = round(_currentNotional*_maintenanceMarginRate-_maintenanceAmount, _precisions['quote'])
    def __trade_processVirtualServer_computeAsset(self, localID, assetName):
        _account                 = self.__accounts[localID]
        _positions               = _account['positions']
        _account_virtualServer   = self.__accounts_virtualServer[localID]
        _positions_virtualServer = _account_virtualServer['positions']
        _asset_virtualServer     = _account_virtualServer['assets'][assetName]
        try:
            _nzqPositions_crossed_thisAsset  = [_pSymbol for _pSymbol in _account_virtualServer['_nonZeroQuantityPositions_crossed']  if (_positions[_pSymbol]['quoteAsset'] == assetName)]
            _nzqPositions_isolated_thisAsset = [_pSymbol for _pSymbol in _account_virtualServer['_nonZeroQuantityPositions_isolated'] if (_positions[_pSymbol]['quoteAsset'] == assetName)]
            _positionInitialMargin_crossed = sum(_positions_virtualServer[_pSymbol]['positionInitialMargin'] for _pSymbol in _nzqPositions_crossed_thisAsset)
            _unrealizedPNL_crossed         = sum(_positions_virtualServer[_pSymbol]['unrealizedPNL']         for _pSymbol in _nzqPositions_crossed_thisAsset)
            _unrealizedPNL_isolated        = sum(_positions_virtualServer[_pSymbol]['unrealizedPNL']         for _pSymbol in _nzqPositions_isolated_thisAsset)
            _walletBalance_isolated        = sum(_positions_virtualServer[_pSymbol]['isolatedWalletBalance'] for _pSymbol in _nzqPositions_isolated_thisAsset)
            _asset_virtualServer['availableBalance'] = round(_asset_virtualServer['crossWalletBalance']-_positionInitialMargin_crossed+_unrealizedPNL_crossed, _ACCOUNT_ASSETPRECISIONS[assetName])
            _asset_virtualServer['walletBalance']    = round(_asset_virtualServer['crossWalletBalance']+_walletBalance_isolated,                               _ACCOUNT_ASSETPRECISIONS[assetName])
            _asset_virtualServer['marginBalance']    = round(_asset_virtualServer['walletBalance']+_unrealizedPNL_crossed+_unrealizedPNL_isolated,             _ACCOUNT_ASSETPRECISIONS[assetName])
        except:
            _asset_virtualServer['availableBalance'] = None
            _asset_virtualServer['walletBalance']    = None
            _asset_virtualServer['marginBalance']    = None
    def __trade_checkTrade(self, localID, positionSymbol, quantity_new, entryPrice_new):
        _account    = self.__accounts[localID]
        _position   = _account['positions'][positionSymbol]
        _asset      = _account['assets'][_position['quoteAsset']]
        _precisions = _position['precisions']
        _ocr        = _position['_orderCreationRequest']
        #[1]: Trade Quantity Tracking
        if (_ocr is None):
            #Quantity Deltas
            _quantity_delta_filled  = 0
            _quantity_unfilled      = 0
            _quantity_delta_unknown = round(quantity_new-_position['quantity'], _position['precisions']['quantity'])
        else:
            _ocr_result      = _ocr['results'][-1]
            _ocr_orderResult = _ocr_result['orderResult']
            _ocr_orderParams = _ocr['orderParams']
            _quantity_delta = round(quantity_new-_position['quantity'], _precisions['quantity'])
            if (_ocr_result['result'] == True):
                _quantity_unfilled = round(_ocr_orderResult['originalQuantity']-_ocr_orderResult['executedQuantity'], _precisions['quantity'])
                if   (_ocr_orderResult['side'] == 'BUY'):  _quantity_delta_filled =  _ocr_orderResult['executedQuantity']
                elif (_ocr_orderResult['side'] == 'SELL'): _quantity_delta_filled = -_ocr_orderResult['executedQuantity']
                _quantity_delta_unknown = round(_quantity_delta-_quantity_delta_filled, _precisions['quantity'])
            else:
                _quantity_delta_filled  = 0
                _quantity_unfilled      = _ocr_orderParams['quantity']
                _quantity_delta_unknown = _quantity_delta
        #[2]: Quantity Deltas Handling
        #---[2-1]: Known Trade
        if (_ocr is not None):
            _ocr_result       = _ocr['results'][-1]
            _ocr_orderResult  = _ocr_result['orderResult']
            _ocr_orderParams  = _ocr['orderParams']
            _ocrHandler = None
            if (_ocr_result['result'] == True):
                #Trade Result Interpretation
                if (_quantity_delta_filled != 0):
                    _quantity_new      = round(_position['quantity']+_quantity_delta_filled,  _precisions['quantity'])
                    _quantity_dirDelta = round(abs(_quantity_new)-abs(_position['quantity']), _precisions['quantity'])
                    #---Cost, Profit & Entry Price (New values computed here are not in account of an unknown trade quantity, hence being the reason why quantity_new and entryPrice_new is computed, rather than being imported)
                    if (0 < _quantity_dirDelta): #Position Size Increased
                        #Entry Price
                        if (_position['quantity'] == 0): _notional_prev = 0
                        else:                            _notional_prev = abs(_position['quantity'])*_position['entryPrice']
                        _notional_new = _notional_prev+_quantity_dirDelta*_ocr_orderResult['averagePrice']
                        _entryPrice_new = round(_notional_new/abs(_quantity_new), _precisions['price'])
                        #Profit
                        _profit = 0
                    elif (_quantity_dirDelta < 0): #Position Size Decreased
                        #Entry Price
                        if (_quantity_new == 0): _entryPrice_new = None
                        else:                    _entryPrice_new = _position['entryPrice']
                        #Profit
                        if   (_ocr_orderParams['side'] == 'BUY'):  _profit = round(_ocr_orderResult['executedQuantity']*(_position['entryPrice']-_ocr_orderResult['averagePrice']), _precisions['quote'])
                        elif (_ocr_orderParams['side'] == 'SELL'): _profit = round(_ocr_orderResult['executedQuantity']*(_ocr_orderResult['averagePrice']-_position['entryPrice']), _precisions['quote'])
                    _tradingFee        = round(_ocr_orderResult['executedQuantity']*_ocr_orderResult['averagePrice']*_ACTUALTRADE_MARKETTRADINGFEE, _precisions['quote'])
                    _walletBalance_new = round(_asset['walletBalance']+_profit-_tradingFee,                                                         _precisions['quote'])
                    #Send Trade Log Save Request to DATAMANAGER
                    if (True):
                        _tradeLog = {'timestamp':       time.time(),
                                     'positionSymbol':  positionSymbol,
                                     'logicSource':     _ocr['logicSource'],
                                     'requestComplete': ((_ocr_result['result'] == True) and (_ocr_orderResult['originalQuantity'] == _ocr_orderResult['executedQuantity'])),
                                     'side':            _ocr_orderParams['side'],
                                     'quantity':        _ocr_orderResult['executedQuantity'],
                                     'price':           _ocr_orderResult['averagePrice'],
                                     'profit':          _profit,
                                     'tradingFee':      _tradingFee,
                                     'totalQuantity':   _quantity_new,
                                     'entryPrice':      _entryPrice_new,
                                     'walletBalance':   _walletBalance_new,
                                     'tradeControl':    self.__copyTradeControl(tradeControl = _position['tradeControl'])}
                        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'addAccountTradeLog', functionParams = {'localID': localID, 'tradeLog': _tradeLog}, farrHandler = None)
                    #Update Hourly Report
                    self.__updateAccountHourlyReport_onTrade(localID = localID, positionSymbol = positionSymbol, side = _ocr_orderParams['side'], logicSource = _ocr['logicSource'], profit = _profit)
                    #Console Print
                    if (True):
                        _message = f"Successful OCR Result Received For {localID}-{positionSymbol}.\n"\
                                  +f" * LogicSource:       {_tradeLog['logicSource']}\n"\
                                  +f" * Request Complete:  {str(_tradeLog['requestComplete'])}\n"\
                                  +f" * Side:              {_tradeLog['side']}\n"\
                                  +f" * Traded   Quantity: {atmEta_Auxillaries.floatToString(number = _ocr_orderResult['executedQuantity'], precision = _precisions['quantity'])}\n"\
                                  +f" * Unfilled Quantity: {atmEta_Auxillaries.floatToString(number = _quantity_unfilled,                   precision = _precisions['quantity'])}\n"\
                                  +f" * Price:             {atmEta_Auxillaries.floatToString(number = _ocr_orderResult['averagePrice'],     precision = _precisions['price'])} {_position['quoteAsset']}\n"\
                                  +f" * Profit:            {atmEta_Auxillaries.floatToString(number = _profit,                              precision = _precisions['quote'])} {_position['quoteAsset']}\n"\
                                  +f" * TradingFee:        {atmEta_Auxillaries.floatToString(number = _tradingFee,                          precision = _precisions['quote'])} {_position['quoteAsset']}"
                        self.__logger(message = _message, logType = 'Update', color = 'light_cyan')
                #OCR Handler Determination
                if   (_quantity_unfilled == 0):                                       _ocrHandler = ('TERMINATE',  'COMPLETION')            #Terminate on Success
                elif (_ocr['nAttempts'] < _TRADE_MAXIMUMOCRGENERATIONATTEMPTS):       _ocrHandler = ('REGENERATE', 'PARTIALCOMPLETION')     #Regenerate
                else:                                                                 _ocrHandler = ('TERMINATE',  'LIMITREACHED_PC')       #Terminate on Failure
            elif (_ocr['nAttempts'] < _TRADE_MAXIMUMOCRGENERATIONATTEMPTS):           _ocrHandler = ('REGENERATE', 'REJECTED')              #Regenerate
            else:                                                                     _ocrHandler = ('TERMINATE',  'LIMITREACHED_RJ')       #Terminate on Failure
            if ((_quantity_delta_unknown != 0) and (_ocrHandler[0] == 'REGENERATE')): _ocrHandler = ('TERMINATE',  'UNKNOWNTRADEDETECTED')  #Terminate on Disruption
            #OCR Handling
            if   (_ocrHandler[0] == 'TERMINATE'):  self.__orderCreationRequest_terminate(localID  = localID, positionSymbol = positionSymbol, quantity_new      = quantity_new)
            elif (_ocrHandler[0] == 'REGENERATE'): self.__orderCreationRequest_regenerate(localID = localID, positionSymbol = positionSymbol, quantity_unfilled = _quantity_unfilled)
            #---Console Print
            if (True):
                if (_ocrHandler[0] == 'TERMINATE'):
                    if   (_ocrHandler[1] == 'COMPLETION'):           self.__logger(message = f"OCR Terminated For {localID}-{positionSymbol} On Completion.",                     logType = 'Update', color = 'light_green')
                    elif (_ocrHandler[1] == 'LIMITREACHED_PC'):      self.__logger(message = f"OCR Terminated For {localID}-{positionSymbol} On Partial Completion Limit Reach.", logType = 'Update', color = 'light_magenta')
                    elif (_ocrHandler[1] == 'LIMITREACHED_RJ'):      self.__logger(message = f"OCR Terminated For {localID}-{positionSymbol} On Rejection Limit Reach.",          logType = 'Update', color = 'light_magenta')
                    elif (_ocrHandler[1] == 'UNKNOWNTRADEDETECTED'): self.__logger(message = f"OCR Terminated For {localID}-{positionSymbol} On Interruption.",                   logType = 'Update', color = 'light_magenta')
                elif (_ocrHandler[0] == 'REGENERATE'):
                    if   (_ocrHandler[1] == 'PARTIALCOMPLETION'): self.__logger(message = f"OCR Regenerated For {localID}-{positionSymbol} On Re-Attempt For Partial Completion.", logType = 'Update', color = 'light_blue')
                    elif (_ocrHandler[1] == 'REJECTED'):          self.__logger(message = f"OCR Regenerated For {localID}-{positionSymbol} On Re-Attempt For Rejection.",          logType = 'Update', color = 'light_blue')
        #---[2-2]: Unknown Trade
        if (_quantity_delta_unknown != 0):
            #Trade Log Save
            if (True):
                if   (_quantity_delta_unknown < 0): _side = 'SELL'
                elif (0 < _quantity_delta_unknown): _side = 'BUY'
                _tradeLog = {'timestamp':       time.time(),
                             'positionSymbol':  positionSymbol,
                             'logicSource':     'UNKNOWN',
                             'requestComplete': None,
                             'side':            _side,
                             'quantity':        abs(_quantity_delta_unknown),
                             'price':           None,
                             'profit':          None,
                             'tradingFee':      None,
                             'totalQuantity':   quantity_new,
                             'entryPrice':      entryPrice_new,
                             'walletBalance':   None,
                             'tradeControl':    self.__copyTradeControl(tradeControl = _position['tradeControl'])}
                self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'addAccountTradeLog', functionParams = {'localID': localID, 'tradeLog': _tradeLog}, farrHandler = None)
            #Update Hourly Report
            self.__updateAccountHourlyReport_onTrade(localID = localID, positionSymbol = positionSymbol, side = _side, logicSource = 'UNKNOWN', profit = None)
            #External Clearing Handling (Stop trading, assume the user is taking control / liquidation occurred)
            self.__trade_onAbruptClearing(localID = localID, positionSymbol = positionSymbol, clearingType = 'UNKNOWNTRADE')
            #Trade Handlers Clearing & Trade Control Initialization (In Case No Processing OCR Exists. Otherwise, in will be handlded along with the OCR)
            if (_ocr is None):
                _position['_tradeHandlers'].clear()
                if ((_position['tradeConfigurationCode'] is not None) and (_position['tradeConfigurationCode'] in self.__tradeConfigurations_loaded)): _tcMode = self.__tradeConfigurations_loaded[_position['tradeConfigurationCode']]['config']['tcMode']
                else:                                                                                                                                  _tcMode = None
                _position['tradeControl'] = self.__getInitializedTradeControl(tradeControlMode = _tcMode)
                self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'positions', positionSymbol, 'tradeControl'), self.__copyTradeControl(tradeControl = _position['tradeControl'])),]}, farrHandler = None)
            #Console Print
            if (True): 
                _message = f"Unknown Trade Detected For {localID}-{positionSymbol}.\n"\
                          +f" * LogicSource: {_tradeLog['logicSource']}\n"\
                          +f" * Side:        {_tradeLog['side']}\n"\
                          +f" * Q_Delta:     {atmEta_Auxillaries.floatToString(number = _tradeLog['quantity'], precision = _precisions['quantity'])}"
                self.__logger(message = _message, logType = 'Update', color = 'light_blue')
    def __trade_checkConditionalExits(self, localID, positionSymbol):
        _account    = self.__accounts[localID]
        _position   = _account['positions'][positionSymbol]
        _precisions = _position['precisions']
        _kline      = self.__currencies_lastKline[positionSymbol]
        if ((_account['tradeStatus'] == True) and (_position['tradeStatus'] == True) and (_position['tradeConfigurationCode'] is not None) and (_kline is not None)):
            _tc           = self.__tradeConfigurations_loaded[_position['tradeConfigurationCode']]['config']
            _tc_tcm       = _tc['tcMode']
            _tradeControl = _position['tradeControl']
            if   (_tc_tcm == 'TS'):
                #TP
                #SL
                #FSL
                #WR
                #RAF
                pass
            elif (_tc_tcm == 'RQPM'):
                #Kline Interpretation & Trade Handlers Determination
                _tradeHandler_checkList = {'RQP_FSLIMMED': None,
                                           'RQP_FSLCLOSE': None}
                #---CheckList 1: RQP_FSLIMMED
                if (True):
                    if (_position['quantity'] != 0):
                        if (_tc['rqpm_fullStopLossImmediate'] is not None):
                            if (_position['quantity'] < 0):
                                _price_FSL = round(_position['entryPrice']*(1+_tc['rqpm_fullStopLossImmediate']), _precisions['price'])
                                if (_price_FSL <= _kline[KLINDEX_HIGHPRICE]): _tradeHandler_checkList['RQP_FSLIMMED'] = 'BUY'
                            elif (0 < _position['quantity']):
                                _price_FSL = round(_position['entryPrice']*(1-_tc['rqpm_fullStopLossImmediate']), _precisions['price'])
                                if (_kline[KLINDEX_LOWPRICE] <= _price_FSL): _tradeHandler_checkList['RQP_FSLIMMED'] = 'SELL'
                #---CheckList 2: RQP_FSLCLOSE
                if (True):
                    if (_position['quantity'] != 0):
                        if (_tc['rqpm_fullStopLossClose'] is not None):
                            if (_tradeControl['rqpm_fslcTrigger'] is None):
                                #FSLClose Triggering Check
                                _fslcTrigger = None
                                if (_position['quantity'] < 0):
                                    _price_FSL = round(_position['entryPrice']*(1+_tc['rqpm_fullStopLossClose']), _precisions['price'])
                                    if (_price_FSL <= _kline[KLINDEX_HIGHPRICE]): _fslcTrigger = ('BUY', _kline[KLINDEX_OPENTIME])
                                elif (0 < _position['quantity']):
                                    _price_FSL = round(_position['entryPrice']*(1-_tc['rqpm_fullStopLossClose']), _precisions['price'])
                                    if (_kline[KLINDEX_LOWPRICE] <= _price_FSL): _fslcTrigger = ('SELL', _kline[KLINDEX_OPENTIME])
                                #If Triggerred, save updated trade control
                                if ((_fslcTrigger is not None) and (_tradeHandler_checkList['RQP_FSLIMMED'] is None)): 
                                    _tradeControl['rqpm_fslcTrigger'] = _fslcTrigger
                                    self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'positions', positionSymbol, 'tradeControl'), self.__copyTradeControl(tradeControl = _position['tradeControl'])),]}, farrHandler = None)
                            else:
                                if (_tradeControl['rqpm_fslcTrigger'] < _kline[KLINDEX_OPENTIME]):
                                    if   ((_position['quantity'] < 0) and (_tradeControl['rqpm_fslcTrigger'][0] == 'BUY')):  _tradeHandler_checkList['RQP_FSLCLOSE'] = 'BUY'
                                    elif ((0 < _position['quantity']) and (_tradeControl['rqpm_fslcTrigger'][0] == 'SELL')): _tradeHandler_checkList['RQP_FSLCLOSE'] = 'SELL'
                                    else:
                                        _tradeControl['rqpm_fslcTrigger'] = None
                                        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'positions', positionSymbol, 'tradeControl'), self.__copyTradeControl(tradeControl = _position['tradeControl'])),]}, farrHandler = None)
                #---Trade Handlers Determination & Appending
                _tradeHandlers = list()
                if   (_tradeHandler_checkList['RQP_FSLIMMED'] is not None): _tradeHandlers = ['RQP_FSLIMMED',]
                elif (_tradeHandler_checkList['RQP_FSLCLOSE'] is not None): _tradeHandlers = ['RQP_FSLCLOSE',]
                _t_current_ns = time.time_ns()
                _position['_tradeHandlers'] += [{'type': _thType, 'side': _tradeHandler_checkList[_thType], 'generationTime_ns': _t_current_ns, 'pipResult': None, 'kline': _kline} for _thType in _tradeHandlers]
    def __trade_onAbruptClearing(self, localID, positionSymbol, clearingType):
        #Instances
        _account  = self.__accounts[localID]
        _position = _account['positions'][positionSymbol]
        #Current Time
        _t_current_s = int(time.time())
        #Record Update
        _position['abruptClearingRecords'].append((_t_current_s, clearingType))
        while (86400 <= _t_current_s-_position['abruptClearingRecords'][0][0]): _position['abruptClearingRecords'].pop(0)
        #Trade Stop Evaluation
        _tradeStop = False
        if (clearingType == 'ESCAPE'):
            nESCAPEs = 0
            for _acRec in _position['abruptClearingRecords']:
                if (_acRec[1] == 'ESCAPE'): nESCAPEs += 1
            if (5 <= nESCAPEs): _tradeStop = True
        elif (clearingType == 'FSL'):
            nFSLs = 0
            for _acRec in _position['abruptClearingRecords']:
                if (_acRec[1] == 'FSL'): nFSLs += 1
            if (2 <= nFSLs): _tradeStop = True
        elif (clearingType == 'LIQUIDATION'):  _tradeStop = True
        elif (clearingType == 'UNKNOWNTRADE'): _tradeStop = True
        #Announcement
        if (_tradeStop == True):
            _position['tradeStatus'] = False
            _position['abruptClearingRecords'].clear()
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol, 'tradeStatus'), prdContent = _position['tradeStatus'])
            self.ipcA.sendFAR(targetProcess = 'GUI',         functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, positionSymbol, 'tradeStatus')},   farrHandler = None)

            self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'positions', positionSymbol, 'tradeStatus'), _position['tradeStatus'])]}, farrHandler = None)
        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'positions', positionSymbol, 'abruptClearingRecords'), _position['abruptClearingRecords'].copy())]}, farrHandler = None)
    def __computeLiquidationPrice(self, positionSymbol, walletBalance, quantity, entryPrice, currentPrice, maintenanceMargin, upnl, isolated = True, mm_crossTotal = 0, upnl_crossTotal = 0):
        if ((quantity == 0) or (currentPrice is None) or (maintenanceMargin is None)): return None
        else:
            _quantity_abs = abs(quantity)
            _maintenanceMarginRate, _maintenanceAmount = atmEta_Constants.getMaintenanceMarginRateAndAmount(positionSymbol = positionSymbol, notional = _quantity_abs*currentPrice)
            if (isolated == True): mm_others = 0;                               upnl_others = 0
            else:                  mm_others = mm_crossTotal-maintenanceMargin; upnl_others = upnl_crossTotal-upnl
            if   (quantity < 0):  _side = -1
            elif (0 < quantity):  _side =  1
            _liquidationPrice = (walletBalance-mm_others+upnl_others-maintenanceMargin+_quantity_abs*(currentPrice*_maintenanceMarginRate-entryPrice*_side))/(_quantity_abs*(_maintenanceMarginRate-_side))
            if (_liquidationPrice <= 0): _liquidationPrice = None
            return _liquidationPrice
    #---Account Controls
    def __removeAccount(self, localID, password):
        #Check if the account of the given localID exists
        if (localID in self.__accounts):
            _account = self.__accounts[localID]
            #Check Password
            passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
            if (passwordTest == True):
                #References Update
                for _positionSymbol in _account['positions']:
                    self.__unregisterPositionFromCurrencyAnalysis(localID = localID, positionSymbol = _positionSymbol)
                    self.__unregisterPositionTradeConfiguration(localID = localID, positionSymbol = _positionSymbol)
                #Remove the account data and save account descriptions
                del self.__accounts[localID]
                #Send account description removal request to DATAMANAGER
                self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'removeAccountDescription', functionParams = {'localID': localID}, farrHandler = None)
                #Send account instance removal request to BINANCEAPI
                self.ipcA.sendFAR(targetProcess = 'BINANCEAPI', functionID = 'removeAccountInstance', functionParams = {'localID': localID}, farrHandler = None)
                #Announce the account removal
                self.ipcA.sendPRDREMOVE(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID))
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'REMOVED', 'updatedContent': localID}, farrHandler = None)
                return {'result': True, 'message': "Account '{:s}' Removal Succcessful!".format(localID)}
            else: return {'result': False, 'message': "Account '{:s}' Removal Failed. 'Incorrect Password'".format(localID)}
        else:     return {'result': False, 'message': "Account '{:s}' Removal Failed. 'The Account Does Not Exist'".format(localID)}
    def __activateAccount(self, localID, password, apiKey, secretKey, requestID):
        #Check if the account of the given localID exists
        if (localID in self.__accounts):
            _account = self.__accounts[localID]
            #Check Password
            passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
            if (passwordTest == True):
                _accountType = _account['accountType']
                if (_accountType == _ACCOUNT_ACCOUNTTYPE_ACTUAL):
                    dispatchID = self.ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                                                   functionID     = 'generateAccountInstance', 
                                                   functionParams = {'localID':   localID,
                                                                     'uid':       _account['buid'],
                                                                     'apiKey':    apiKey,
                                                                     'secretKey': secretKey},
                                                   farrHandler    = self.__farr_onAccountInstanceGenerationRequestResponse)
                    self.__accountInstanceGenerationRequests[dispatchID] = (localID, requestID)
                    return None
                else: return {'result': False, 'message': "Account '{:s}' Activation Failed. 'VIRTUAL Type Account Need Not Be Activated'".format(localID)}
            else:     return {'result': False, 'message': "Account '{:s}' Activation Failed. 'Incorrect Password'".format(localID)}
        else:         return {'result': False, 'message': "Account '{:s}' Activation Failed. 'The Account Does Not Exist'".format(localID)}
    def __deactivateAccount(self, localID, password):
        #Check if the account of the given localID exists
        if (localID in self.__accounts):
            _account = self.__accounts[localID]
            #Check Password
            passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
            if (passwordTest == True):
                _accountType = _account['accountType']
                if (_accountType == _ACCOUNT_ACCOUNTTYPE_ACTUAL):
                    #Send an account instance removal request to BINANCEAPI
                    self.ipcA.sendFAR(targetProcess = 'BINANCEAPI', functionID = 'removeAccountInstance', functionParams = {'localID': localID}, farrHandler = None)
                    #Update the account status and signal it
                    _account['status'] = _ACCOUNT_ACCOUNTSTATUS_INACTIVE
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'status'), prdContent = _account['status'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_STATUS', 'updatedContent': localID}, farrHandler = None)
                    return   {'result': True,  'message': "Account '{:s}' Deactivation Successful!".format(localID)}
                else: return {'result': False, 'message': "Account '{:s}' Activation Failed. 'VIRTUAL Type Account Cannot Be Deactivated'".format(localID)}
            else:     return {'result': False, 'message': "Account '{:s}' Activation Failed. 'Incorrect Password'".format(localID)}
        else:         return {'result': False, 'message': "Account '{:s}' Activation Failed. 'The Account Does Not Exist'".format(localID)}
    def __registerPositionToCurrencyAnalysis(self, localID, positionSymbol, currencyAnalysisCode):
        _position = self.__accounts[localID]['positions'][positionSymbol]
        self.__unregisterPositionFromCurrencyAnalysis(localID = localID, positionSymbol = positionSymbol)
        _position['currencyAnalysisCode'] = currencyAnalysisCode
        if (currencyAnalysisCode in self.__currencyAnalysis): self.__currencyAnalysis[currencyAnalysisCode]['appliedAccounts'].add(localID)
    def __unregisterPositionFromCurrencyAnalysis(self, localID, positionSymbol):
         _position = self.__accounts[localID]['positions'][positionSymbol]
         if (    (_position['currencyAnalysisCode'] != None) 
             and (_position['currencyAnalysisCode'] in self.__currencyAnalysis) 
             and (localID in self.__currencyAnalysis[_position['currencyAnalysisCode']]['appliedAccounts'])): self.__currencyAnalysis[_position['currencyAnalysisCode']]['appliedAccounts'].remove(localID)
         _position['currencyAnalysisCode'] = None
    def __registerPositionTradeConfiguration(self, localID, positionSymbol, tradeConfigurationCode):
        _position = self.__accounts[localID]['positions'][positionSymbol]
        self.__unregisterPositionTradeConfiguration(localID = localID, positionSymbol = positionSymbol)
        _position['tradeConfigurationCode'] = tradeConfigurationCode
        if (tradeConfigurationCode in self.__tradeConfigurations):
            if (tradeConfigurationCode not in self.__tradeConfigurations_loaded): self.__loadTradeConfiguration(tradeConfigurationCode = tradeConfigurationCode)
            _tc_loaded = self.__tradeConfigurations_loaded[tradeConfigurationCode]
            if (localID in _tc_loaded['subscribers']): _tc_loaded['subscribers'][localID].add(positionSymbol)
            else:                                      _tc_loaded['subscribers'][localID] = {positionSymbol}
    def __unregisterPositionTradeConfiguration(self, localID, positionSymbol):
        _position = self.__accounts[localID]['positions'][positionSymbol]
        if (_position['tradeConfigurationCode'] != None):
            if (_position['tradeConfigurationCode'] in self.__tradeConfigurations_loaded): 
                _tc_loaded = self.__tradeConfigurations_loaded[_position['tradeConfigurationCode']]
                if ((localID in _tc_loaded['subscribers']) and (positionSymbol in _tc_loaded['subscribers'][localID])): 
                    _tc_loaded['subscribers'][localID].remove(positionSymbol)
                    if (len(_tc_loaded['subscribers'][localID]) == 0): del _tc_loaded['subscribers'][localID]
        _position['tradeConfigurationCode'] = None
        _position['_tradabilityTests'] &= ~0b010
    def __loadTradeConfiguration(self, tradeConfigurationCode):
        if (tradeConfigurationCode in self.__tradeConfigurations):
            if (tradeConfigurationCode in self.__tradeConfigurations_loaded): _subscribers = self.__tradeConfigurations_loaded[tradeConfigurationCode]['subscribers']
            else:                                                             _subscribers = dict()
            _tc = self.__tradeConfigurations[tradeConfigurationCode]
            _tc_copied = {'leverage':  _tc['leverage'],
                          'isolated':  _tc['isolated'],
                          'direction': _tc['direction'],
                          'tcMode':    _tc['tcMode'],
                          #TS Only
                          'ts_fullStopLossImmediate': _tc['ts_fullStopLossImmediate'],
                          'ts_fullStopLossClose':     _tc['ts_fullStopLossClose'],
                          'ts_weightReduce':          _tc['ts_weightReduce'],
                          'ts_reachAndFall':          _tc['ts_reachAndFall'],
                          'ts_ts_entry':              _tc['ts_ts_entry'].copy(),
                          'ts_ts_exit':               _tc['ts_ts_exit'].copy(),
                          'ts_ts_psl':                _tc['ts_ts_psl'].copy(),
                          #RQPM Only
                          'rqpm_exitOnImpulse':         _tc['rqpm_exitOnImpulse'],
                          'rqpm_exitOnAligned':         _tc['rqpm_exitOnAligned'],
                          'rqpm_exitOnProfitable':      _tc['rqpm_exitOnProfitable'],
                          'rqpm_fullStopLossImmediate': _tc['rqpm_fullStopLossImmediate'],
                          'rqpm_fullStopLossClose':     _tc['rqpm_fullStopLossClose'],
                          'rqpm_functionType':          _tc['rqpm_functionType'],
                          'rqpm_functionParams_LONG':   _tc['rqpm_functionParams_LONG'].copy(),
                          'rqpm_functionParams_SHORT':  _tc['rqpm_functionParams_SHORT'].copy()}
            self.__tradeConfigurations_loaded[tradeConfigurationCode] = {'subscribers': _subscribers, 'config': _tc_copied}
    def __checkPositionTradability(self, localID, positionSymbol):
        _position = self.__accounts[localID]['positions'][positionSymbol]
        #[1]: Currency Analysis
        if (_position['currencyAnalysisCode'] != None):
            if (_position['currencyAnalysisCode'] in self.__currencyAnalysis):
                if (localID in self.__currencyAnalysis[_position['currencyAnalysisCode']]['appliedAccounts']): _position['_tradabilityTests'] |=  0b001
            else:                                                                                              _position['_tradabilityTests'] &= ~0b001
        else:                                                                                                  _position['_tradabilityTests'] &= ~0b001
        #[2]: Trade Configuration
        if (_position['tradeConfigurationCode'] != None):
            if (_position['tradeConfigurationCode'] in self.__tradeConfigurations_loaded):
                _tc_loaded = self.__tradeConfigurations_loaded[_position['tradeConfigurationCode']]
                _subscribed        = ((localID in _tc_loaded['subscribers']) and (positionSymbol in _tc_loaded['subscribers'][localID]))
                _marginTypeChecked = (_position['isolated'] == _tc_loaded['config']['isolated'])
                _leverageChecked   = (_position['leverage'] == _tc_loaded['config']['leverage'])
                if ((_subscribed == True) and (_marginTypeChecked == True) and (_leverageChecked == True)): _position['_tradabilityTests'] |=  0b010
                else:                                                                                       _position['_tradabilityTests'] &= ~0b010
            else:                                                                                           _position['_tradabilityTests'] &= ~0b010
        else:                                                                                               _position['_tradabilityTests'] &= ~0b010
        #[3]: Open Order
        if (_position['openOrderInitialMargin'] == 0): _position['_tradabilityTests'] |=  0b100
        else:                                          _position['_tradabilityTests'] &= ~0b100
        #Finally, update tradable and tradeStatus
        if (_position['_tradabilityTests'] == 0b111): _position['tradable'] = True
        else:                                         _position['tradable'] = False
        if ((_position['tradable'] == False) and (_position['quantity'] != None)): _position['tradeStatus'] = False
    def __requestMarginTypeAndLeverageUpdate(self, localID, positionSymbol):
        _account  = self.__accounts[localID]
        _position = _account['positions'][positionSymbol]
        if   (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL): _account_virtualServer = self.__accounts_virtualServer[localID]; _position_virtualServer = _account_virtualServer['positions'][positionSymbol]
        elif (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_ACTUAL):  _account_virtualServer = None;                                   _position_virtualServer = None
        if ((_position['_tradabilityTests']&0b010 == 0) and (_position['tradeConfigurationCode'] in self.__tradeConfigurations_loaded)):
            _tc_loaded_config = self.__tradeConfigurations_loaded[_position['tradeConfigurationCode']]['config']
            _tests = 0b000
            _tests |= 0b001*(_account['status'] == _ACCOUNT_ACCOUNTSTATUS_ACTIVE)             #Account Status Test
            _tests |= 0b010*(_position['openOrderInitialMargin'] == 0)                        #Open Order Test
            _tests |= 0b100*((_position['quantity'] is None) or (_position['quantity'] == 0)) #Quantity Test
            if (_tests == 0b111):
                #Margin Type
                if ((_position['isolated'] != _tc_loaded_config['isolated']) and (_position['_marginTypeControlRequested'] == False)):
                    if (_tc_loaded_config['isolated'] == True): _newMarginType = 'ISOLATED'
                    else:                                       _newMarginType = 'CROSSED'
                    if   (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL): _account_virtualServer['_marginTypeControlRequests'].append({'positionSymbol': positionSymbol, 'newMarginType': _newMarginType})
                    elif (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_ACTUAL):  self.ipcA.sendFAR(targetProcess = 'BINANCEAPI', functionID = 'setPositionMarginType', functionParams = {'localID': localID, 'positionSymbol': positionSymbol, 'newMarginType': _newMarginType}, farrHandler = self.__far_onPositionControlResponse)
                    _position['_marginTypeControlRequested'] = True
                #Leverage
                if ((_position['leverage'] != _tc_loaded_config['leverage']) and (_position['_leverageControlRequested'] == False)): 
                    if   (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL): _account_virtualServer['_leverageControlRequests'].append({'positionSymbol': positionSymbol, 'newLeverage': _tc_loaded_config['leverage']})
                    elif (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_ACTUAL):  self.ipcA.sendFAR(targetProcess = 'BINANCEAPI', functionID = 'setPositionLeverage', functionParams = {'localID': localID, 'positionSymbol': positionSymbol, 'newLeverage': _tc_loaded_config['leverage']}, farrHandler = self.__far_onPositionControlResponse)
                    _position['_leverageControlRequested'] = True
    def __sortPositionSymbolsByPriority(self, localID, assetName):
        _account   = self.__accounts[localID]
        _asset     = _account['assets'][assetName]
        _positions = _account['positions']
        _positionSymbols_forSort = [(_pSymbol, _positions[_pSymbol]['priority']) for _pSymbol in _asset['_positionSymbols']]
        _positionSymbols_forSort.sort(key = lambda x: x[1])
        _asset['_positionSymbols_prioritySorted'] = [_sortPair[0] for _sortPair in _positionSymbols_forSort]
    def __allocateBalance(self, localID, asset = 'all'):
        _account = self.__accounts[localID]
        if (_account['status'] == _ACCOUNT_ACCOUNTSTATUS_ACTIVE):
            if   (asset == 'all'):              _assetTargets = _ACCOUNT_READABLEASSETS
            elif (asset in _account['assets']): _assetTargets = (asset,)
            for _assetName in _assetTargets:
                _asset     = _account['assets'][_assetName]
                _positions = _account['positions']
                if ((_asset['allocatableBalance'] is not None) and (0 < _asset['allocatableBalance'])):
                    _allocatedAssumedRatio = 0
                    #Zero Quantity Allocation Zero
                    for _pSymbol in _asset['_positionSymbols']: 
                        _position = _positions[_pSymbol]
                        if (_position['quantity'] == 0): _assumedRatio_effective = 0; _position['allocatedBalance'] = 0
                        else:                            _assumedRatio_effective = round(_position['allocatedBalance']/_asset['allocatableBalance'], 3)
                        _allocatedAssumedRatio += _assumedRatio_effective
                    #Zero Quantity Re-Allocation
                    for _pSymbol in _asset['_positionSymbols_prioritySorted']:
                        _position = _positions[_pSymbol]
                        if ((_position['quantity'] == 0) or ((_position['assumedRatio'] != 0) and (_position['allocatedBalance'] == 0))):
                            _allocatedBalance = round(_asset['allocatableBalance']*_position['assumedRatio'], _ACCOUNT_ASSETPRECISIONS[_assetName])
                            if (_position['maxAllocatedBalance'] < _allocatedBalance): _allocatedBalance = _position['maxAllocatedBalance']
                            _assumedRatio_effective = round(_allocatedBalance/_asset['allocatableBalance'], 3)
                            if (_allocatedAssumedRatio+_assumedRatio_effective <= 1):
                                _allocatedAssumedRatio += _assumedRatio_effective
                                _position['allocatedBalance'] = _allocatedBalance
                            else: break
    #---System
    def __logger(self, message, logType, color):
        if (self.__config_TradeManager[f'print_{logType}'] == True): 
            _time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
            print(termcolor.colored(f"[TRADEMANAGER-{_time_str}] {message}", color))
    #Manager Internal Functions END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #FAR Handlers -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<DATAMANAGER>
    def __far_onCurrenciesUpdate(self, requester, updatedContents):
        if (requester == 'DATAMANAGER'):
            for updatedContent in updatedContents:
                symbol    = updatedContent['symbol']
                contentID = updatedContent['id']
                self.__currencies[symbol] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol))
                #Sort and determine the updated contents on this end
                _statusUpdated = False
                if (contentID == '_ADDED'):
                    if (self.__currencies[symbol]['quoteAsset'] in _ACCOUNT_READABLEASSETS):
                        for localID in self.__accounts:
                            self.__formatNewAccountPosition(localID = localID, currencySymbol = symbol)
                            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', symbol), prdContent = self.__accounts[localID]['positions'][symbol])
                            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION_ADDED', 'updatedContent': (localID, symbol)}, farrHandler = None)
                    _statusUpdated = True
                else:
                    if (contentID[0] == 'info_server'):
                        try:    contentID_1 = contentID[1]
                        except: contentID_1 = None
                        if   (contentID_1 == None):     _statusUpdated = True
                        elif (contentID_1 == 'status'): _statusUpdated = True
                        else: pass
                #Handle the updated contents
                if (_statusUpdated == True):
                    #Get new status
                    if (self.__currencies[symbol]['info_server'] == None): newStatus = None
                    else:                                                  newStatus = self.__currencies[symbol]['info_server']['status']
                    #If this currency is in the currency analysis list
                    if (symbol in self.__currencyAnalysis_bySymbol):
                        for currencyAnalysisCode in self.__currencyAnalysis_bySymbol[symbol]:
                            _currencyAnalysis = self.__currencyAnalysis[currencyAnalysisCode]
                            if (_currencyAnalysis['status'] == 'CURRENCYNOTFOUND'): 
                                if (newStatus == 'TRADING'): 
                                    if (_currencyAnalysis['currencyAnalysisConfiguration'] == None): _currencyAnalysis['status'] = 'CONFIGNOTFOUND'
                                    else:                                                            _currencyAnalysis['status'] = 'WAITINGSTREAM'
                                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'status'), prdContent = _currencyAnalysis['status'])
                                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_STATUS', 'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)
                                    if (_currencyAnalysis['status'] == 'WAITINGSTREAM'): self.__allocateCurrencyAnalysisToAnAnalzer(currencyAnalysisCode)
                                else:
                                    _currencyAnalysis['status'] = 'WAITINGTRADING'
                                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'status'), prdContent = _currencyAnalysis['status'])
                                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_STATUS', 'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)
                            elif (_currencyAnalysis['status'] == 'WAITINGTRADING'):
                                if (newStatus == 'TRADING'): 
                                    if (_currencyAnalysis['currencyAnalysisConfiguration'] == None): _currencyAnalysis['status'] = 'CONFIGNOTFOUND'
                                    else:                                                            _currencyAnalysis['status'] = 'WAITINGSTREAM'
                                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'status'), prdContent = _currencyAnalysis['status'])
                                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_STATUS', 'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)
                                    if (_currencyAnalysis['status'] == 'WAITINGSTREAM'): self.__allocateCurrencyAnalysisToAnAnalzer(currencyAnalysisCode)
                            #Raise Number of Currency Analysis By Status Recomputation Flag
                            self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus = True
    def __farr_onAccountDescriptionLoadRequestResponse(self, responder, requestID, functionResult):
        if (responder == 'DATAMANAGER'):
            accountDescriptions = functionResult
            for _localID in accountDescriptions:
                _ad = accountDescriptions[_localID]
                self.__addAccount(localID          = _localID, 
                                  buid             = _ad['buid'],
                                  accountType      = _ad['accountType'],
                                  password         = _ad['hashedPassword'],
                                  newAccount       = False,
                                  assets           = _ad['assets'],
                                  positions        = _ad['positions'],
                                  lastHourlyReport = _ad['lastHourlyReport'],
                                  sendIPCM         = False)
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', _localID), prdContent = self.__accounts[_localID])
            #Format new positions for any non-registered currencies (that are in Market but not in DB)
            #---Local formatting
            _newPositions = list()
            for currencySymbol in self.__currencies:
                if (self.__currencies[currencySymbol]['quoteAsset'] in _ACCOUNT_READABLEASSETS):
                    for _localID in self.__accounts:
                        _account = self.__accounts[_localID]
                        if (currencySymbol not in _account['positions']): self.__formatNewAccountPosition(localID = _localID, currencySymbol = currencySymbol); _newPositions.append((_localID, currencySymbol))
            #---Update Requests
            if (0 < len(_newPositions)):
                _dbUpdateRequests = list()
                for _localID, _pSymbol in _newPositions:
                    _account  = self.__accounts[_localID]
                    _position = _account['positions'][_pSymbol]
                    _asset    = _account['assets'][_position['quoteAsset']]
                    _dbUpdateRequests.append(((_localID, 'positions', _pSymbol, '#NEW#'), _position))
                if (0 < len(_dbUpdateRequests)): self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': _dbUpdateRequests}, farrHandler = None)
    #<GUI>
    #---Manager Configuration
    def __far_updateConfiguration(self, requester, requestID, newConfiguration):
        if (requester == 'GUI'):
            #Print Update
            self.__config_TradeManager['print_Update'] = newConfiguration['print_Update']
            #Print Warning
            self.__config_TradeManager['print_Warning'] = newConfiguration['print_Warning']
            #Print Error
            self.__config_TradeManager['print_Error'] = newConfiguration['print_Error']
            #Save Config # Update Announcement
            self.__saveTradeManagerConfig()
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CONFIGURATION', prdContent = self.__config_TradeManager)
            return {'result': True, 'message': "Configuration Successfully Updated!", 'configuration': self.__config_TradeManager}
    #---Currency Analysis Configuration
    def __far_addCurrencyAnalysisConfiguration(self, requester, requestID, currencyAnalysisConfigurationCode, currencyAnalysisConfiguration):
        if (requester == 'GUI'): return self.__addCurrencyAnalysisConfiguration(currencyAnalysisConfigurationCode = currencyAnalysisConfigurationCode, currencyAnalysisConfiguration = currencyAnalysisConfiguration, saveConfig = True, sendIPCM = True)
    def __far_removeCurrencyAnalysisConfiguration(self, requester, requestID, currencyAnalysisConfigurationCode):
        if (requester == 'GUI'): return self.__removeCurrencyAnalysisConfiguration(currencyAnalysisConfigurationCode = currencyAnalysisConfigurationCode)
    #---Currency Analysis
    def __far_addCurrencyAnalysis(self, requester, requestID, currencySymbol, currencyAnalysisCode, currencyAnalysisConfigurationCode):
        if (requester == 'GUI'): return self.__addCurrencyAnalysis(currencyAnalysisCode              = currencyAnalysisCode,
                                                                   currencySymbol                    = currencySymbol,
                                                                   currencyAnalysisConfigurationCode = currencyAnalysisConfigurationCode,
                                                                   saveConfig = True, silentTerminal = False, sendIPCM = True)
    def __far_removeCurrencyAnalysis(self, requester, currencyAnalysisCode):
        if (requester == 'GUI'): self.__removeCurrencyAnalysis(currencyAnalysisCode = currencyAnalysisCode)
    def __far_restartCurrencyAnalysis(self, requester, currencyAnalysisCode):
        if (requester == 'GUI'): self.__restartCurrencyAnalysis(currencyAnalysisCode = currencyAnalysisCode)
    #---Trade Configuration
    def __far_addTradeConfiguration(self, requester, requestID, tradeConfigurationCode, tradeConfiguration):
        if (requester == 'GUI'): return self.__addTradeConfiguration(tradeConfigurationCode = tradeConfigurationCode, tradeConfiguration = tradeConfiguration, saveConfig = True, sendIPCM = True)
    def __far_removeTradeConfiguration(self, requester, requestID, tradeConfigurationCode):
        if (requester == 'GUI'): return self.__removeTradeConfiguration(tradeConfigurationCode = tradeConfigurationCode)
    #---Account
    def __far_addAccount(self, requester, requestID, localID, buid, accountType, password):
        if (requester == 'GUI'): 
            _result = self.__addAccount(localID = localID, buid = buid, accountType = accountType, password = password, newAccount = True, silentTerminal = False, lastHourlyReport = None, sendIPCM = True)
            return {'localID': localID, 'responseOn': 'ADDACCOUNT', 'result': _result['result'], 'message': _result['message']}
    def __far_removeAccount(self, requester, requestID, localID, password):
        if (requester == 'GUI'): 
            _result = self.__removeAccount(localID = localID, password = password)
            return {'localID': localID, 'responseOn': 'REMOVEACCOUNT', 'result': _result['result'], 'message': _result['message']}
    def __far_activateAccount(self, requester, requestID, localID, password, apiKey, secretKey):
        if (requester == 'GUI'): 
            _result = self.__activateAccount(localID = localID, password = password, apiKey = apiKey, secretKey = secretKey, requestID = requestID)
            if (_result != None): self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'responseOn': 'ACTIVATEACCOUNT', 'result': False, 'message': _result['message']}, requestID = requestID, complete = True)
    def __far_deactivateAccount(self, requester, requestID, localID, password):
        if (requester == 'GUI'): 
            _result = self.__deactivateAccount(localID = localID, password = password)
            return {'localID': localID, 'responseOn': 'DEACTIVATEACCOUNT', 'result': _result['result'], 'message': _result['message']}
    def __far_setAccountTradeStatus(self, requester, requestID, localID, password, newStatus):
        if (requester == 'GUI'):
            if (localID in self.__accounts):
                _account = self.__accounts[localID]
                #Check Password
                passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
                if (passwordTest == True):
                    self.__accounts[localID]['tradeStatus'] = newStatus
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'tradeStatus'), prdContent = self.__accounts[localID]['tradeStatus'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_TRADESTATUS', 'updatedContent': localID}, farrHandler = None)
                    return   {'localID': localID, 'responseOn': 'SETACCOUNTTRADESTATUS', 'result': True,  'message': "Account '{:s}' Trade Status Update Sucessful!".format(localID)}
                else: return {'localID': localID, 'responseOn': 'SETACCOUNTTRADESTATUS', 'result': False, 'message': "Account '{:s}' Trade Status Update Failed. 'Incorrect Password'".format(localID)}
            else:     return {'localID': localID, 'responseOn': 'SETACCOUNTTRADESTATUS', 'result': False, 'message': "Account '{:s}' Trade Status Update Failed. 'The Account Does Not Exist'".format(localID)}
    def __far_transferBalance(self, requester, requestID, localID, password, asset, amount):
        if (requester == 'GUI'):
            if (localID in self.__accounts):
                _account = self.__accounts[localID]
                #Check Password
                passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
                if (passwordTest == True):
                    if (_account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL):
                        _account_virtualServer = self.__accounts_virtualServer[localID]
                        _asset_virtualServer   = _account_virtualServer['assets'][asset]
                        #If this is a withdrawl and the amount is more than the available, set the amount equal to the available
                        if ((amount < 0) and (_asset_virtualServer['availableBalance'] < -amount)): amount = -_asset_virtualServer['availableBalance']
                        #Update the crossWallet balance
                        _asset_virtualServer['crossWalletBalance'] += amount
                        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'assets', asset, 'crossWalletBalance'), _asset_virtualServer['crossWalletBalance'])]}, farrHandler = None)
                        return   {'localID': localID, 'responseOn': 'BALANCETRANSFER', 'result': True,  'message': "Account '{:s}' Asset '{:s}' Balance Transfer Successful!".format(localID, asset)}
                    else: return {'localID': localID, 'responseOn': 'BALANCETRANSFER', 'result': False, 'message': "Account '{:s}' Asset '{:s}' Balance Transfer Failed. 'Internal Balance Transfer Is Only Available For 'VIRTUAL' Type Account'".format(localID, asset)}
                else: return     {'localID': localID, 'responseOn': 'BALANCETRANSFER', 'result': False, 'message': "Account '{:s}' Asset '{:s}' Balance Transfer Failed. 'Incorrect Password'".format(localID, asset)}
            else: return         {'localID': localID, 'responseOn': 'BALANCETRANSFER', 'result': False, 'message': "Account '{:s}' Asset '{:s}' Balance Transfer Failed. 'The Account Does Not Exist'".format(localID, asset)}
    def __far_updateAllocationRatio(self, requester, requestID, localID, password, asset, newAllocationRatio):
        if (requester == 'GUI'):
            if (localID in self.__accounts):
                _account = self.__accounts[localID]
                #Check Password
                passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
                if (passwordTest == True):
                    _asset = _account['assets'][asset]
                    if (newAllocationRatio < 0): newAllocationRatio = 0
                    if (1 < newAllocationRatio): newAllocationRatio = 1
                    _asset['allocationRatio'] = newAllocationRatio
                    #Annoucement
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'assets', asset, 'allocationRatio'), prdContent = _asset['allocationRatio'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_ASSET', 'updatedContent': (localID, asset, 'allocationRatio')}, farrHandler = None)
                    self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'assets', asset, 'allocationRatio'), _asset['allocationRatio']),]}, farrHandler = None)
                    #Return update result
                    return   {'localID': localID, 'asset': asset, 'responseOn': 'ALLOCATIONRATIOUPDATE', 'result': True,  'message': "Account '{:s}' Asset {:s} Allocation Ratio Update Successful!".format(localID, asset)}
                else: return {'localID': localID, 'asset': asset, 'responseOn': 'ALLOCATIONRATIOUPDATE', 'result': False, 'message': "Account '{:s}' Asset {:s} Allocation Ratio UpdateFailed. 'Incorrect Password'".format(localID, asset)}
            else: return     {'localID': localID, 'asset': asset, 'responseOn': 'ALLOCATIONRATIOUPDATE', 'result': False, 'message': "Account '{:s}' Asset {:s} Allocation Ratio UpdateFailed. 'The Account Does Not Exist'".format(localID, asset)}
    def __far_forceClearPosition(self, requester, requestID, localID, password, positionSymbol):
        if (requester == 'GUI'):
            if (localID in self.__accounts):
                _account = self.__accounts[localID]
                #Check Password
                passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
                if (passwordTest == True):
                    _position = _account['positions'][positionSymbol]
                    _ocr      = _position['_orderCreationRequest']
                    if (_ocr is None):
                        if ((_position['quantity'] is not None) and (_position['quantity'] != 0)):
                            #Side & Quantity Determination
                            if   (_position['quantity'] < 0): _side = 'BUY';  _quantity = -_position['quantity']
                            elif (0 < _position['quantity']): _side = 'SELL'; _quantity =  _position['quantity']
                            #Trade Control Update
                            if ((_position['tradeConfigurationCode'] is not None) and (_position['tradeConfigurationCode'] in self.__tradeConfigurations_loaded)): _tcMode = self.__tradeConfigurations_loaded[_position['tradeConfigurationCode']]['config']['tcMode']
                            else:                                                                                                                                  _tcMode = None
                            _tradeControl = _position['tradeControl']
                            if (_tcMode == 'TS'):
                                _tcUpdate = {'tcMode': 'TS'}
                            elif (_tcMode == 'RQPM'):
                                _tcUpdate = {'tcMode': 'RQPM',
                                             'rqpm_entryTimestamp':  {'onComplete': None, 'onPartial': _tradeControl['rqpm_entryTimestamp'],  'onFail': _tradeControl['rqpm_entryTimestamp']},
                                             'rqpm_initialQuantity': {'onComplete': None, 'onPartial': _tradeControl['rqpm_initialQuantity'], 'onFail': _tradeControl['rqpm_initialQuantity']}}
                            elif (_tcMode == None): _tcUpdate = {'tcMode': None}
                            #OCR Generation
                            self.__orderCreationRequest_generate(localID            = localID, 
                                                                 positionSymbol     = positionSymbol, 
                                                                 logicSource        = 'FORCECLEAR', 
                                                                 side               = _side,
                                                                 quantity           = _quantity,
                                                                 tradeControlUpdate = _tcUpdate,
                                                                 ipcRID             = requestID)
                        else: self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'FORCECLEARPOSITION', 'result': False, 'message': "Account '{:s}' Position '{:s}' Position Force Clear Failed. 'Check The Quantity'".format(localID, positionSymbol)},         requestID = requestID, complete = True)
                    else:     self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'FORCECLEARPOSITION', 'result': False, 'message': "Account '{:s}' Position '{:s}' Position Force Clear Failed. 'OCR Not Empty'".format(localID, positionSymbol)},              requestID = requestID, complete = True)
                else:         self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'FORCECLEARPOSITION', 'result': False, 'message': "Account '{:s}' Position '{:s}' Position Force Clear Failed. 'Incorrect Password'".format(localID, positionSymbol)},         requestID = requestID, complete = True)
            else:             self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'FORCECLEARPOSITION', 'result': False, 'message': "Account '{:s}' Position '{:s}' Position Force Clear Failed. 'The Account Does Not Exist'".format(localID, positionSymbol)}, requestID = requestID, complete = True)
    def __far_updatePositionTradeStatus(self, requester, requestID, localID, password, positionSymbol, newTradeStatus):
        if (requester == 'GUI'):
            if (localID in self.__accounts):
                _account = self.__accounts[localID]
                if (positionSymbol in _account['positions']):
                    _position = _account['positions'][positionSymbol]
                    #Check Password
                    passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
                    if (passwordTest == True):
                        if (_position['tradable'] == True):
                            _position['tradeStatus'] = newTradeStatus
                            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol, 'tradeStatus'), prdContent = newTradeStatus)
                            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, positionSymbol, 'tradeStatus')}, farrHandler = None)
                            self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'positions', positionSymbol, 'tradeStatus'), _position['tradeStatus'])]}, farrHandler = None)
                            if (newTradeStatus == True):
                                _position['abruptClearingRecords'].clear()
                                self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'positions', positionSymbol, 'abruptClearingRecords'), _position['abruptClearingRecords'].copy())]}, farrHandler = None)
                            return   {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADESTATUS', 'result': True,  'message': "Account '{:s}' Position '{:s}' Trade Status Update Successful!".format(localID, positionSymbol)}
                        else: return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADESTATUS', 'result': False, 'message': "Account '{:s}' Position '{:s}' Trade Status Update Failed. 'The Position Is Not Tradable'".format(localID, positionSymbol)}
                    else: return     {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADESTATUS', 'result': False, 'message': "Account '{:s}' Position '{:s}' Trade Status Update Failed. 'Incorrect Password'".format(localID, positionSymbol)}
                else: return         {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADESTATUS', 'result': False, 'message': "Account '{:s}' Position '{:s}' Trade Status Update Failed. 'The Position Does Not Exist'".format(localID, positionSymbol)}
            else: return             {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADESTATUS', 'result': False, 'message': "Account '{:s}' Position '{:s}' Trade Status Update Failed. 'The Account Does Not Exist'".format(localID, positionSymbol)}
    def __far_updatePositionReduceOnly(self, requester, requestID, localID, password, positionSymbol, newReduceOnly):
        if (requester == 'GUI'):
            if (localID in self.__accounts):
                _account = self.__accounts[localID]
                if (positionSymbol in _account['positions']):
                    _position = _account['positions'][positionSymbol]
                    #Check Password
                    passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
                    if (passwordTest == True):
                        _position['reduceOnly'] = newReduceOnly
                        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol, 'reduceOnly'), prdContent = newReduceOnly)
                        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, positionSymbol, 'reduceOnly')}, farrHandler = None)
                        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': [((localID, 'positions', positionSymbol, 'reduceOnly'), _position['reduceOnly'])]}, farrHandler = None)
                        return   {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONREDUCEONLY', 'result': True,  'message': "Account '{:s}' Position '{:s}' Reduce-Only Update Successful!".format(localID, positionSymbol)}
                    else: return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONREDUCEONLY', 'result': False, 'message': "Account '{:s}' Position '{:s}' Reduce-Only Update Failed. 'Incorrect Password'".format(localID, positionSymbol)}
                else: return     {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONREDUCEONLY', 'result': False, 'message': "Account '{:s}' Position '{:s}' Reduce-Only Update Failed. 'The Position Does Not Exist'".format(localID, positionSymbol)}
            else: return         {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONREDUCEONLY', 'result': False, 'message': "Account '{:s}' Position '{:s}' Reduce-Only Update Failed. 'The Account Does Not Exist'".format(localID, positionSymbol)}
    def __far_updatePositionTraderParams(self, requester, requestID, localID, password, positionSymbol, newCurrencyAnalysisCode, newTradeConfigurationCode, newPriority, newAssumedRatio, newMaxAllocatedBalance):
        if (requester == 'GUI'):
            if (localID in self.__accounts):
                _account = self.__accounts[localID]
                if (positionSymbol in _account['positions']):
                    #Check Password
                    passwordTest = bcrypt.checkpw(password.encode(encoding = "utf-8"), _account['hashedPassword'])
                    if (passwordTest == True):
                        _position      = _account['positions'][positionSymbol]
                        _position_prev = _position.copy()
                        _assetName     = _position['quoteAsset']
                        _asset         = _account['assets'][_assetName]
                        _asset_prev    = _asset.copy()
                        if (_position['quantity'] == 0):
                            _toRequestDBUpdate = list()
                            #Main Updates
                            #---[1]: Currency Analysis Code
                            if ((_position['currencyAnalysisCode'] != newCurrencyAnalysisCode)):
                                #New Parameter Validity Test
                                if   (newCurrencyAnalysisCode == None):                    _testPassed = True
                                elif (newCurrencyAnalysisCode in self.__currencyAnalysis): _testPassed = True
                                else:                                                      _testPassed = False
                                #Finally
                                if (_testPassed == True):
                                    self.__registerPositionToCurrencyAnalysis(localID = localID, positionSymbol = positionSymbol, currencyAnalysisCode = newCurrencyAnalysisCode)
                                    _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'currencyAnalysisCode'), _position['currencyAnalysisCode']))
                            #---[2]: Trade Configuration Code
                            if (_position['tradeConfigurationCode'] != newTradeConfigurationCode):
                                #New Parameter Validity Test
                                if   (newTradeConfigurationCode == None):                       _testPassed = True
                                elif (newTradeConfigurationCode in self.__tradeConfigurations): _testPassed = True
                                else:                                                           _testPassed = False
                                #Finally
                                if (_testPassed == True):
                                    #Apply Change & Announce
                                    self.__registerPositionTradeConfiguration(localID = localID, positionSymbol = positionSymbol, tradeConfigurationCode = newTradeConfigurationCode)
                                    if (_position['tradeConfigurationCode'] is None): _position['tradeControl'] = self.__getInitializedTradeControl(tradeControlMode = None)
                                    else:                                             _position['tradeControl'] = self.__getInitializedTradeControl(tradeControlMode = self.__tradeConfigurations_loaded[_position['tradeConfigurationCode']]['config']['tcMode'])
                                    _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'tradeConfigurationCode'), _position['tradeConfigurationCode']))
                                    _toRequestDBUpdate.append(((localID, 'positions', positionSymbol,           'tradeControl'), self.__copyTradeControl(_position['tradeControl'])))
                            #---[3]: Priority
                            if (_position['priority'] != newPriority):
                                #New Parameter Validity Test
                                try:
                                    if ((1 <= newPriority) and (newPriority <= len(_account['positions']))): _testPassed = True
                                    else:                                                                    _testPassed = False
                                except:                                                                      _testPassed = False
                                #Finally
                                if (_testPassed == True):
                                    #Effected Positions
                                    priorityUpdatedPositions = list()
                                    if (_position['priority'] < newPriority): 
                                        _target = (_position['priority']+1, newPriority)
                                        for _pSymbol in _account['positions']:
                                            __position = _account['positions'][_pSymbol]
                                            if ((_target[0] <= __position['priority']) and (__position['priority'] <= _target[1])): __position['priority'] -= 1; priorityUpdatedPositions.append(_pSymbol)
                                    elif (newPriority < _position['priority']): 
                                        _target = (newPriority, _position['priority']-1)
                                        for _pSymbol in _account['positions']:
                                            __position = _account['positions'][_pSymbol]
                                            if ((_target[0] <= __position['priority']) and (__position['priority'] <= _target[1])): __position['priority'] += 1; priorityUpdatedPositions.append(_pSymbol)
                                    for _pSymbol in priorityUpdatedPositions:
                                        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', _pSymbol, 'priority'), prdContent = _account['positions'][_pSymbol]['priority'])
                                        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, _pSymbol, 'priority')}, farrHandler = None)
                                    #Target Position
                                    _position['priority'] = newPriority
                                    _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'priority'), _position['priority']))
                            #---[4]: Assumed Ratio
                            if (_position['assumedRatio'] != newAssumedRatio):
                                #New Parameter Validity Test
                                try:
                                    if (0 <= newAssumedRatio): _testPassed = True
                                    else:                      _testPassed = False
                                except: _testPassed = False
                                #Finally
                                if (_testPassed == True): 
                                    _position['assumedRatio'] = newAssumedRatio
                                    _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'assumedRatio'), _position['assumedRatio']))
                            #---[5]: Max Allocated Balance
                            if (_position['maxAllocatedBalance'] != newMaxAllocatedBalance):
                                #New Parameter Validity Test
                                try:
                                    if (0 <= newMaxAllocatedBalance): _testPassed = True
                                    else:                             _testPassed = False
                                except: _testPassed = False
                                #Finally
                                if (_testPassed == True): 
                                    _position['maxAllocatedBalance'] = newMaxAllocatedBalance
                                    _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'maxAllocatedBalance'), _position['maxAllocatedBalance']))
                            #Tradability Check & MarginType and Leverage Update
                            self.__checkPositionTradability(localID = localID, positionSymbol = positionSymbol)
                            self.__requestMarginTypeAndLeverageUpdate(localID = localID, positionSymbol = positionSymbol) #If this needs to be done will be determined internally
                            if (_position['tradeConfigurationCode'] in self.__tradeConfigurations_loaded): _position['weightedAssumedRatio'] = _position['assumedRatio']*self.__tradeConfigurations_loaded[_position['tradeConfigurationCode']]['config']['leverage']
                            else:                                                                          _position['weightedAssumedRatio'] = None
                            #DB & GUI Annoucement
                            if (0 < len(_toRequestDBUpdate)): self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': _toRequestDBUpdate}, farrHandler = None)
                            for _dataName in _position:
                                if ((_dataName in _GUIANNOUCEMENT_POSITIONDATANAMES) and (_position[_dataName] != _position_prev[_dataName])): 
                                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol, _dataName), prdContent = _position[_dataName])
                                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, positionSymbol, _dataName)}, farrHandler = None)
                            for _dataName in _asset:
                                if ((_dataName in _GUIANNOUCEMENT_ASSETDATANAMES) and (_asset[_dataName] != _asset_prev[_dataName])): 
                                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'assets', _assetName, _dataName), prdContent = _asset[_dataName])
                                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_ASSET', 'updatedContent': (localID, _assetName, _dataName)}, farrHandler = None)
                            #Result Return
                            return   {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADERPARAMS', 'result': True,  'message': "Account '{:s}' Position '{:s}' Trader Params Update Successful!".format(localID, positionSymbol)}
                        else: return {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADERPARAMS', 'result': False, 'message': "Account '{:s}' Position '{:s}' Trader Params Update Failed. 'Non-Zero Quantity'".format(localID, positionSymbol)}
                    else: return     {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADERPARAMS', 'result': False, 'message': "Account '{:s}' Position '{:s}' Trader Params Update Failed. 'Incorrect Password'".format(localID, positionSymbol)}
                else: return         {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADERPARAMS', 'result': False, 'message': "Account '{:s}' Position '{:s}' Trader Params Update Failed. 'The Position Does Not Exist'".format(localID, positionSymbol)}
            else: return             {'localID': localID, 'positionSymbol': positionSymbol, 'responseOn': 'UPDATEPOSITIONTRADERPARAMS', 'result': False, 'message': "Account '{:s}' Position '{:s}' Trader Params Update Failed. 'The Account Does Not Exist'".format(localID, positionSymbol)}

    #<ANALYZER>
    def __far_onAnalyzerSummaryUpdate(self, requester, updatedSummary):
        if (requester[:8] == 'ANALYZER'):
            analyzerIndex = int(requester[8])
            if (updatedSummary == 'averagePIPGenerationTime_ns'):
                averagePIPGenerationTime_ns = self.ipcA.getPRD(processName = requester, prdAddress = ('ANALYZERSUMMARY', 'averagePIPGenerationTime_ns'))
                self.__analyzers[analyzerIndex]['averagePIPGenerationTime_ns'] = averagePIPGenerationTime_ns
                self.__analyzers_central_recomputeAveragePIPGenerationTime = True
    def __far_onCurrencyAnalysisStatusUpdate(self, requester, currencyAnalysisCode, newStatus):
        if (requester[:8] == 'ANALYZER'):
            if   (newStatus == _CURRENCYANALYSIS_STATUS_WAITINGNEURALNETWORKCONNECTIONSDATA): newStatus = 'WAITINGNNCDATA'
            elif (newStatus == _CURRENCYANALYSIS_STATUS_WAITINGSTREAM):                       newStatus = 'WAITINGSTREAM'
            elif (newStatus == _CURRENCYANALYSIS_STATUS_WAITINGDATAAVAILABLE):                newStatus = 'WAITINGDATAAVAILABLE'
            elif (newStatus == _CURRENCYANALYSIS_STATUS_PREPARING_QUEUED):                    newStatus = 'PREP_QUEUED'
            elif (newStatus == _CURRENCYANALYSIS_STATUS_PREPARING_ANALYZINGKLINES):           newStatus = 'PREP_ANALYZINGKLINES'
            elif (newStatus == _CURRENCYANALYSIS_STATUS_ANALYZINGREALTIME):                   newStatus = 'ANALYZINGREALTIME'
            elif (newStatus == _CURRENCYANALYSIS_STATUS_ERROR):                               newStatus = 'ERROR'
            self.__currencyAnalysis[currencyAnalysisCode]['status'] = newStatus
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'status'), prdContent = self.__currencyAnalysis[currencyAnalysisCode]['status'])
            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_STATUS', 'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)
            self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus = True
    def __far_onPIPGeneration(self, requester, currencyAnalysisCode, dispatchTime, kline, klineClosed, pipResult):
        if (requester[:8] == 'ANALYZER'):
            _currencyAnalysis = self.__currencyAnalysis[currencyAnalysisCode]
            _currencySymbol = _currencyAnalysis['currencySymbol']
            for localID in _currencyAnalysis['appliedAccounts']:
                if (localID in self.__accounts): 
                    if (_currencySymbol not in self.__accounts[localID]['_generatedPIPs']): self.__accounts[localID]['_generatedPIPs'][_currencySymbol] = dict()
                    self.__accounts[localID]['_generatedPIPs'][_currencySymbol][kline[KLINDEX_OPENTIME]] = {'dispatchTime': dispatchTime,
                                                                                                            'kline':        kline,
                                                                                                            'klineClosed':  klineClosed,
                                                                                                            'pipResult':    pipResult}
    #<BINANCEAPI>
    def __far_onKlineStreamReceival(self, requester, symbol, kline, streamConnectionTime, closed):
        if (requester == 'BINANCEAPI'):
            #Record the last close price
            self.__currencies_lastKline[symbol] = kline
            #Position Responses
            for _localID in self.__accounts:
                _account = self.__accounts[_localID]
                if (symbol in _account['positions']):
                    _position = _account['positions'][symbol]
                    #---Conditional Exits Check
                    if ((_position['quantity'] is not None) and (_position['quantity'] != 0)): self.__trade_checkConditionalExits(localID = _localID, positionSymbol = symbol)
    def __farr_onAccountInstanceGenerationRequestResponse(self, responder, requestID, functionResult):
        if (responder == 'BINANCEAPI'):
            if (requestID in self.__accountInstanceGenerationRequests):
                localID         = self.__accountInstanceGenerationRequests[requestID][0]
                requestID_toGUI = self.__accountInstanceGenerationRequests[requestID][1]
                if (functionResult['result'] == True):
                    _account = self.__accounts[localID]
                    #Update the account status and signal it
                    _account['status'] = _ACCOUNT_ACCOUNTSTATUS_ACTIVE
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'status'), prdContent = _account['status'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_STATUS', 'updatedContent': localID}, farrHandler = None)
                    #Send FARR signaling account activaion success
                    self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'responseOn': 'ACTIVATEACCOUNT', 'result': True, 'message': "Account '{:s}' Activation Successful!".format(localID)}, requestID = requestID_toGUI, complete = True)
                else:
                    failType = functionResult['failType']
                    if   (failType == 'FUTURESDISABLED'):   self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'responseOn': 'ACTIVATEACCOUNT', 'result': False, 'message': "Account '{:s}' Activation Failed. 'Futures Disabled, Check API Permissions'".format(localID)},                              requestID = requestID_toGUI, complete = True)
                    elif (failType == 'UIDMISMATCH'):       self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'responseOn': 'ACTIVATEACCOUNT', 'result': False, 'message': "Account '{:s}' Activation Failed. 'BUID Mismatch'".format(localID)},                                                        requestID = requestID_toGUI, complete = True)
                    elif (failType == 'UNEXPECTEDERROR'):   self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'responseOn': 'ACTIVATEACCOUNT', 'result': False, 'message': "Account '{:s}' Activation Failed Due To An Unexpected Error. '{:s}'".format(localID, str(functionResult['errorMessage']))}, requestID = requestID_toGUI, complete = True)
                    elif (failType == 'SERVERUNAVAILABLE'): self.ipcA.sendFARR(targetProcess = 'GUI', functionResult = {'localID': localID, 'responseOn': 'ACTIVATEACCOUNT', 'result': False, 'message': "Account '{:s}' Activation Failed. 'Server Unavailable'".format(localID)},                                                   requestID = requestID_toGUI, complete = True)
                del self.__accountInstanceGenerationRequests[requestID]
    def __far_onAccountDataReceival(self, requester, localID, accountData):
        if (requester == 'BINANCEAPI'):
            if (localID in self.__accounts):
                #Format assets and positions data for internal interpretation
                _assetsData    = dict()
                _positionsData = dict()
                for _asset in accountData['assets']:
                    if (_asset['asset'] in _ACCOUNT_READABLEASSETS): 
                        _assetsData[_asset['asset']] = {'marginBalance':      float(_asset['marginBalance']),
                                                        'walletBalance':      float(_asset['walletBalance']),
                                                        'crossWalletBalance': float(_asset['crossWalletBalance']),
                                                        'availableBalance':   float(_asset['availableBalance'])}
                for _position in accountData['positions']:
                    if (_position['symbol'] in self.__currencies):
                        if (self.__currencies[_position['symbol']]['quoteAsset'] in _ACCOUNT_READABLEASSETS):
                            _entryPrice = float(_position['entryPrice'])
                            if (_entryPrice == 0): _entryPrice = None
                            _positionsData[_position['symbol']] = {'quantity':               float(_position['positionAmt']),
                                                                   'entryPrice':             _entryPrice,
                                                                   'leverage':               int(_position['leverage']),
                                                                   'isolated':               bool(_position['isolated']),
                                                                   'isolatedWalletBalance':  float(_position['isolatedWallet']),
                                                                   'openOrderInitialMargin': float(_position['openOrderInitialMargin']),
                                                                   'positionInitialMargin':  float(_position['positionInitialMargin']),
                                                                   'maintenanceMargin':      float(_position['maintMargin']),
                                                                   'unrealizedPNL':          float(_position['unrealizedProfit'])}
                #Update the account using the imported data
                self.__updateAccount(localID = localID, importedData = {'source': 'BINANCE', 'positions': _positionsData, 'assets': _assetsData})
                self.__updateAccountHourlyReport(localID = localID, importedData = None)
    def __far_onPositionControlResponse(self, responder, requestID, functionResult):
        localID        = functionResult['localID']
        positionSymbol = functionResult['positionSymbol']
        responseOn     = functionResult['responseOn']
        result         = functionResult['result']
        if (localID in self.__accounts):
            if (positionSymbol in self.__accounts[localID]['positions']):
                _position = self.__accounts[localID]['positions'][positionSymbol]
                #MarginType Update Request Response
                if (responseOn == 'MARGINTYPEUPDATE'):
                    if (result == True): pass
                    else:
                        failType = functionResult['failType']
                        if (failType == 'SERVERUNAVAILABLE'):     pass
                        elif (failType == 'LOCALIDNOTFOUND'):     pass
                        elif (failType == 'ACCOUNTNOTACTIVATED'): pass
                        elif (failType == 'MARGINTYPEERROR'):     pass
                        elif (failType == 'APIERROR'):            pass
                    _position['_marginTypeControlRequested'] = False
                #Leverage Update Request Response
                elif (responseOn == 'LEVERAGEUPDATE'):
                    if (result == True): pass
                    else:
                        failType = functionResult['failType']
                        if (failType == 'SERVERUNAVAILABLE'):     pass
                        elif (failType == 'LOCALIDNOTFOUND'):     pass
                        elif (failType == 'ACCOUNTNOTACTIVATED'): pass
                        elif (failType == 'APIERROR'):            pass
                    _position['_leverageControlRequested'] = False
                #Order Creation Request Response
                elif (responseOn == 'CREATEORDER'):
                    _ocr = _position['_orderCreationRequest']
                    if (_ocr is not None):
                        if (_ocr['dispatchID'] == requestID):
                            _requestResult = {'resultReceivalTime': time.time(), 
                                              'result':             result,
                                              'failType':           functionResult['failType'],
                                              'orderResult':        functionResult['orderResult'],
                                              'errorMessage':       functionResult['errorMessage']}
                            _ocr['results'].append(_requestResult)
                            _ocr['lastRequestReceived'] = True
    #FAR Handlers END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------