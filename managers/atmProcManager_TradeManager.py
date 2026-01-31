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
from cryptography.fernet import Fernet
import base64
import hashlib
import traceback
from collections import deque

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

KLINTERVAL   = atmEta_Constants.KLINTERVAL
KLINTERVAL_S = atmEta_Constants.KLINTERVAL_S

_ANALYSISGENERATIONCOMPUTATIONINTERVAL_NS = 1e9

_ACCOUNT_ACCOUNTTYPE_VIRTUAL = 'VIRTUAL'
_ACCOUNT_ACCOUNTTYPE_ACTUAL  = 'ACTUAL'
_ACCOUNT_ACCOUNTSTATUS_INACTIVE = 'INACTIVE'
_ACCOUNT_ACCOUNTSTATUS_ACTIVE   = 'ACTIVE'
_ACCOUNT_UPDATEINTERVAL_NS                   = 200e6
_ACCOUNT_PERIODICREPORTANNOUNCEMENTINTERVAL_NS = 60*1e9
_ACCOUNT_PERIODICREPORTFORMATTINGTINTERVAL_S   = 60*60
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
                                     'tradeControlTracker',
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

_TRADE_ANALYSISHANDLINGFILTER_KLINECLOSEPRICE = 0.005
_TRADE_MAXIMUMOCRGENERATIONATTEMPTS           = 5

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
                                    'averageAnalysisGenerationTime_ns':       None}
        self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus = False
        self.__analyzers_central_recomputeAverageAnalysisGenerationTime   = False
        self.__analyzers_central_averageAnalysisGenerationLastComputed_ns = 0

        #Analyzers
        self.__analyzers = list()
        for analyzerProcessName in analyzerProcessNames:
            analyzerIndex = int(analyzerProcessName[8:])
            analyzerDescription = {'processName': analyzerProcessName,
                                   'allocated_currencyAnalysisCodes':  set(),
                                   'allocated_currencySymbols':        set(),
                                   'averageAnalysisGenerationTime_ns': None}
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

        #Read Analysis List
        self.__currencyAnalysis                 = dict()
        self.__currencyAnalysis_bySymbol        = dict()
        self.__currencyAnalysis_analysisResults = dict()

        #Read Trade Configurations
        self.__tradeConfigurations        = dict()
        self.__tradeConfigurations_loaded = dict()

        #Accounts & Trade
        self.__accounts                          = dict()
        self.__accountInstanceGenerationRequests = dict()
        self.__accounts_virtualServer            = dict()
        
        #Configurations Import
        self.__readCurrencyAnalysisConfigurationsList()
        self.__readCurrencyAnalysisList()
        self.__readTradeConfigurationsList()

        #Initial Data Share
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'ACCOUNTS',      prdContent = self.__accounts)
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CONFIGURATION', prdContent = self.__config_TradeManager.copy())
        for targetProcessName in ('GUI', 'SIMULATIONMANAGER'): self.ipcA.sendPRDEDIT(targetProcess = targetProcessName, prdAddress = 'CURRENCYANALYSISCONFIGURATIONS', prdContent = self.__currencyAnalysisConfigurations)
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'CURRENCYANALYSIS', prdContent = self.__currencyAnalysis)
        for targetProcessName in ('GUI', 'SIMULATIONMANAGER'): self.ipcA.sendPRDEDIT(targetProcess = targetProcessName, prdAddress = 'TRADECONFIGURATIONS', prdContent = self.__tradeConfigurations)

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
        self.ipcA.addFARHandler('resetTradeControlTracker',            self.__far_resetTradeControlTracker,            executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('verifyPassword',                      self.__far_verifyPassword,                      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        #---ANALYZERS
        self.ipcA.addFARHandler('onAnalyzerSummaryUpdate',        self.__far_onAnalyzerSummaryUpdate,        executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onCurrencyAnalysisStatusUpdate', self.__far_onCurrencyAnalysisStatusUpdate, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
        self.ipcA.addFARHandler('onAnalysisGeneration',           self.__far_onAnalysisGeneration,           executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
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
        for symbol in self.__currencies: self.ipcA.sendFAR(targetProcess = 'BINANCEAPI', functionID = 'registerKlineStreamSubscription', functionParams = {'subscriptionID': None, 'currencySymbol': symbol}, farrHandler = None)
        #---Update the status of any existing currencyAnalysis
        for currencySymbol in self.__currencyAnalysis_bySymbol:
            if currencySymbol not in self.__currencies: continue
            for caCode in self.__currencyAnalysis_bySymbol[currencySymbol]:
                ca = self.__currencyAnalysis[caCode]
                if self.__currencies[currencySymbol]['info_server'] is None: newStatus = None
                else:                                                        newStatus = self.__currencies[currencySymbol]['info_server']['status']
                if newStatus == 'TRADING':
                    ca['status'] = 'WAITINGSTREAM'
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', caCode, 'status'), prdContent = ca['status'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_STATUS', 'currencyAnalysisCode': caCode}, farrHandler = None)
                    self.__allocateCurrencyAnalysisToAnAnalzer(caCode)
                else:
                    ca['status'] = 'WAITINGTRADING'
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', caCode, 'status'), prdContent = ca['status'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_STATUS', 'currencyAnalysisCode': caCode}, farrHandler = None)
        #Get Account Data from DATAMANAGER
        self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'loadAccountDescriptions', functionParams = None, farrHandler = self.__farr_onAccountDescriptionLoadRequestResponse)
        #Set Number of Currency Analysis By Status Computation Flag to be True
        self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus = True
        #Start Process Loop
        while self.__processLoopContinue:
            #Process any existing FAR and FARRs
            self.ipcA.processFARs()
            self.ipcA.processFARRs()
            #Process Any Virtual Order Requests
            self.__trade_processVirtualServer()
            #Compute Number Of Currency Analysis By Status
            self.__computeNumberOfCurrencyAnalysisByStatus()
            #Compute Average Analysis Generation Time
            self.__computeAverageAnalysisGenerationTime()
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
        #[1]: Configuration File Read
        try:
            config_dir = os.path.join(self.path_project, 'configs', 'tmConfig.config')
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

        #[3]: Update and save the configuration
        self.__config_TradeManager = {'print_Update':  print_update,
                                      'print_Warning': print_warning,
                                      'print_Error':   print_error}
        self.__saveTradeManagerConfig()
    def __saveTradeManagerConfig(self):
        #[1]: Reformat config for save
        config = self.__config_TradeManager
        config_toSave = {'print_Update':  config['print_Update'],
                         'print_Warning': config['print_Warning'],
                         'print_Error':   config['print_Error']}

        #[2]: Save the reformatted configuration file
        config_dir = os.path.join(self.path_project, 'configs', 'tmConfig.config')
        try:
            with open(config_dir, 'w') as f:
                json.dump(config_toSave, f, indent=4)
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Save Trade Manager Configuration. User Attention Strongly Advised"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')

    #---Currency Analysis Configurations
    def __readCurrencyAnalysisConfigurationsList(self):
        #[1]: Read Currency Analysis Configurations List
        cacConfig_dir = os.path.join(self.path_project, 'data', 'tm', 'cacl.json')
        try:
            with open(cacConfig_dir, 'r') as f:
                cacConfig = json.load(f)
        except:
            cacConfig = dict()
        #[2]: Add Currency Analysis Configurations
        for cacCode, cac in cacConfig.items():
            self.__addCurrencyAnalysisConfiguration(currencyAnalysisConfigurationCode = cacCode, currencyAnalysisConfiguration = cac, saveConfig = False, sendIPCM = False)
        #[3]: Save Currency Analysis Configurations List (In case of format changes due to manual edits)
        self.__saveCurrencyAnalysisConfigurationsList()
    def __saveCurrencyAnalysisConfigurationsList(self):
        cacConfig_dir = os.path.join(self.path_project, 'data', 'tm', 'cacl.json')
        try:
            with open(cacConfig_dir, 'w') as f:
                json.dump(self.__currencyAnalysisConfigurations, f, indent=4)
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Save Currency Analysis Configurations List. User Attention Strongly Advised"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')
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
        #[1]: Read Currency Analysis List
        cal_dir = os.path.join(self.path_project, 'data', 'tm', 'cal.json')
        try:
            with open(cal_dir, 'r') as f:
                cal = json.load(f)
        except:
            cal = dict()
        #[2]: Add Currency Analysis
        for caCode, ca in cal.items():
            self.__addCurrencyAnalysis(currencyAnalysisCode              = caCode, 
                                       currencySymbol                    = ca['currencySymbol'],
                                       currencyAnalysisConfigurationCode = ca['currencyAnalysisConfigurationCode'], 
                                       saveConfig = False, silentTerminal = True, sendIPCM = False)
        #[3]: Save Currency Analysis List (In case of format changes due to manual edits)
        self.__saveCurrencyAnalysisList()
    def __saveCurrencyAnalysisList(self):
        #[1]: Format currency analysis for saving
        ca_copy = dict()
        for caCode, ca in self.__currencyAnalysis.items():
            ca_copy[caCode] = {'currencySymbol':                    ca['currencySymbol'],
                               'currencyAnalysisConfigurationCode': ca['currencyAnalysisConfigurationCode']}
        #[2]: Save currency analysis list
        cal_dir = os.path.join(self.path_project, 'data', 'tm', 'cal.json')
        try:
            with open(cal_dir, 'w') as f:
                json.dump(ca_copy, f, indent=4)
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Save Currency Analysis List. User Attention Strongly Advised"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')
    def __addCurrencyAnalysis(self, currencyAnalysisCode, currencySymbol, currencyAnalysisConfigurationCode, saveConfig = True, silentTerminal = False, sendIPCM = True):
        #[1}: Currency Analysis Code Generation or validity test
        if (currencyAnalysisCode is None):
            uacIdx = 0
            currencyAnalysisCode = f"UAC{uacIdx}"
            while (currencyAnalysisCode in self.__currencyAnalysis):
                uacIdx += 1
                currencyAnalysisCode = f"UAC{uacIdx}"
        elif (currencyAnalysisCode in self.__currencyAnalysis): 
            if not silentTerminal: self.__logger(message = f"Currency Analysis '{currencyAnalysisCode}' Add Failed. 'The Analysis Code Already Exists'", logType = 'Warning', color = 'light_red')
            if sendIPCM:           return {'result': False, 'message': f"Currency Analysis '{currencyAnalysisCode}' Add Failed. 'The Analysis Code Already Exists'"}

        #[2]: The currency analysis generation
        #---[2-1]: Currency Analysis By Symbol Update
        if (currencySymbol not in self.__currencyAnalysis_bySymbol): self.__currencyAnalysis_bySymbol[currencySymbol] = set()
        self.__currencyAnalysis_bySymbol[currencySymbol].add(currencyAnalysisCode)

        #---[2-2]: Determine initial analysis status based on the currency status
        currencyData = self.__currencies.get(currencySymbol, None)
        if (currencyData is None): initialStatus = 'CURRENCYNOTFOUND'
        else:
            currencyData_info_server = currencyData['info_server']
            if (currencyData_info_server is not None) and (currencyData_info_server['status'] == 'TRADING'): initialStatus = 'WAITINGSTREAM'
            else:                                                                                            initialStatus = 'WAITINGTRADING'

        #---[2-3]: Get currency analysis configuration
        if (currencyAnalysisConfigurationCode in self.__currencyAnalysisConfigurations): currencyAnalysisConfiguration = self.__currencyAnalysisConfigurations[currencyAnalysisConfigurationCode].copy()
        else:                                                                            currencyAnalysisConfiguration = None
        if (initialStatus == 'WAITINGSTREAM') and (currencyAnalysisConfiguration is None): initialStatus = 'CONFIGNOTFOUND'

        #---[2-4]: Initialize currency analysis trackers 
        _currencyAnalysis = {'currencySymbol':                    currencySymbol,
                             'currencyAnalysisConfigurationCode': currencyAnalysisConfigurationCode,
                             'currencyAnalysisConfiguration':     currencyAnalysisConfiguration,
                             'status':                            initialStatus,
                             'allocatedAnalyzer':                 None,
                             'appliedAccounts':                   set()}
        _currencyAnalysis_analysisResults = {'data':                dict(),
                                             'timestamps':          deque(),
                                             'timestamps_handling': dict(),
                                             'lastReceived': None}
        self.__currencyAnalysis[currencyAnalysisCode]                 = _currencyAnalysis
        self.__currencyAnalysis_analysisResults[currencyAnalysisCode] = _currencyAnalysis_analysisResults

        #---[2-5]: If the config needs to be saved, save the updated currency analysis list
        if saveConfig: 
            self.__saveCurrencyAnalysisList()

        #---[2-6]: If this needs to be sent via PRD and FAR separately, send it
        if sendIPCM:
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode), prdContent = self.__currencyAnalysis[currencyAnalysisCode])
            self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'ADDED', 'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)

        #---[2-7]: If the initial status is 'WAITINGSTREAM', allocate the analysis to an analyzer
        if (initialStatus == 'WAITINGSTREAM'): self.__allocateCurrencyAnalysisToAnAnalzer(currencyAnalysisCode, sendIPCM = sendIPCM)

        #---[2-8]: If there exist any account positions that refer to this currency analysis, register
        for localID in self.__accounts:
            position = self.__accounts[localID]['positions'][currencySymbol]

            if (position['currencyAnalysisCode'] != currencyAnalysisCode): 
                continue

            position_tradable_prev    = position['tradable']
            position_tradeStatus_prev = position['tradeStatus']
            self.__registerPositionToCurrencyAnalysis(localID = localID, positionSymbol = currencySymbol, currencyAnalysisCode = currencyAnalysisCode)
            self.__checkPositionTradability(localID = localID, positionSymbol = currencySymbol)
            if sendIPCM: 
                if (position['tradable'] != position_tradable_prev):
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', currencySymbol, 'tradable'), prdContent = position['tradable'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, currencySymbol, 'tradable')}, farrHandler = None)
                if (position['tradeStatus'] != position_tradeStatus_prev):
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', currencySymbol, 'tradeStatus'), prdContent = position['tradeStatus'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, currencySymbol, 'tradeStatus')}, farrHandler = None)
        
        #[3]: Raise Number of Currency Analysis By Status Recomputation Flag
        self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus = True

        #[4]: FInally
        if not silentTerminal: self.__logger(message = f"Currency Analysis '{currencyAnalysisCode}' Successfully Added!", logType = 'Update',  color = 'light_green')
        if sendIPCM:           return {'result': True,  'message': f"Currency Analysis '{currencyAnalysisCode}' Successfully Added!"}
    def __removeCurrencyAnalysis(self, currencyAnalysisCode):
        #[1]: Existence Check
        if currencyAnalysisCode not in self.__currencyAnalysis: 
            return

        #[2]: Currency Symbol & Allocated Analyzer
        currencySymbol    = self.__currencyAnalysis[currencyAnalysisCode]['currencySymbol']
        allocatedAnalyzer = self.__currencyAnalysis[currencyAnalysisCode]['allocatedAnalyzer']

        #[3]: Command the analyzer to remove the currency analysis
        if allocatedAnalyzer is not None: 
            self.ipcA.sendFAR(targetProcess  = self.__analyzers[allocatedAnalyzer]['processName'], 
                              functionID     = 'removeCurrencyAnalysis', 
                              functionParams = {'currencyAnalysisCode': currencyAnalysisCode}, 
                              farrHandler    = None)
        
        #[4]: Remove the currency analysis data
        del self.__currencyAnalysis[currencyAnalysisCode]
        del self.__currencyAnalysis_analysisResults[currencyAnalysisCode]
        self.__currencyAnalysis_bySymbol[currencySymbol].remove(currencyAnalysisCode)
        if not self.__currencyAnalysis_bySymbol[currencySymbol]: del self.__currencyAnalysis_bySymbol[currencySymbol]

        #[5]: Update the local analyzers tracker
        if allocatedAnalyzer is not None:
            self.__analyzers[allocatedAnalyzer]['allocated_currencyAnalysisCodes'].remove(currencyAnalysisCode)
            if not any(self.__currencyAnalysis[caCode_other]['currencySymbol'] == currencySymbol for caCode_other in self.__analyzers[allocatedAnalyzer]['allocated_currencyAnalysisCodes']):
                self.__analyzers[allocatedAnalyzer]['allocated_currencySymbols'].remove(currencySymbol)

        #[6]: Save the config file
        self.__saveCurrencyAnalysisList()

        #[7]: If there exist any account positions that referred to this currency analysis, unregister
        for localID in self.__accounts:
            position = self.__accounts[localID]['positions'][currencySymbol]

            if (position['currencyAnalysisCode'] != currencyAnalysisCode):
                continue

            position_tradable_prev    = position['tradable']
            position_tradeStatus_prev = position['tradeStatus']
            #Unregister currency analysis
            self.__unregisterPositionFromCurrencyAnalysis(localID = localID, positionSymbol = currencySymbol)
            #Update tradability & trade status and announce
            self.__checkPositionTradability(localID = localID, positionSymbol = currencySymbol)
            if (position['tradable'] != position_tradable_prev):
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', currencySymbol, 'tradable'), prdContent = position['tradable'])
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, currencySymbol, 'tradable')}, farrHandler = None)
            if (position['tradeStatus'] != position_tradeStatus_prev):
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', currencySymbol, 'tradeStatus'), prdContent = position['tradeStatus'])
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, currencySymbol, 'tradeStatus')}, farrHandler = None)
        
        #[8]: Send the updated contents via PRDREMOVE and FAR
        self.ipcA.sendPRDREMOVE(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode))
        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'REMOVED', 'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)
        
        #[9]: Raise Number of Currency Analysis By Status Recomputation Flag
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
    def __computeAverageAnalysisGenerationTime(self):
        t_current_ns = time.perf_counter_ns()
        if not self.__analyzers_central_recomputeAverageAnalysisGenerationTime:                                                             return
        if not _ANALYSISGENERATIONCOMPUTATIONINTERVAL_NS <= t_current_ns-self.__analyzers_central_averageAnalysisGenerationLastComputed_ns: return
        aagt_ns_sum   = 0
        nContributors = 0
        for analyzer in self.__analyzers:
            aagt_ns = analyzer['averageAnalysisGenerationTime_ns']
            if aagt_ns is None: continue
            aagt_ns_sum   += aagt_ns
            nContributors += 1
        if nContributors == 0: aagt_ns = None
        else:                  aagt_ns = round(aagt_ns_sum/nContributors)
        self.__analyzers_central['averageAnalysisGenerationTime_ns'] = aagt_ns
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ANALYZERCENTRAL', 'averageAnalysisGenerationTime_ns'), prdContent = aagt_ns)
        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAnalyzerCentralUpdate', functionParams = {'updatedContents': ['averageAnalysisGenerationTime_ns',]}, farrHandler = None)
        self.__analyzers_central_recomputeAverageAnalysisGenerationTime   = False
        self.__analyzers_central_averageAnalysisGenerationLastComputed_ns = t_current_ns

    #---Trade Configurations
    def __readTradeConfigurationsList(self):
        #[1]: Read Trade Configurations List
        tcConfig_dir = os.path.join(self.path_project, 'data', 'tm', 'tcl.json')
        try:
            with open(tcConfig_dir, 'r') as f:
                tcConfig = json.load(f)
        except:
            tcConfig = dict()
        #[2]: Add Trade Configurations
        for tcCode, tc in tcConfig.items():
            self.__addTradeConfiguration(tradeConfigurationCode = tcCode, tradeConfiguration = tc, saveConfig = False, sendIPCM = False)
        #[3]: Save Trade Configurations List (In case of format changes due to manual edits)
        self.__saveTradeConfigurationsList()
    def __saveTradeConfigurationsList(self):
        tcConfig_dir = os.path.join(self.path_project, 'data', 'tm', 'tcl.json')
        try:
            with open(tcConfig_dir, 'w') as f:
                json.dump(self.__tradeConfigurations, f, indent=4)
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting to Save Trade Configurations List. User Attention Strongly Advised"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}\n"),
                          logType = 'Error', 
                          color   = 'light_red')
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
    def __addAccount(self, localID, buid, accountType, password, newAccount = True, assets = None, positions = None, lastPeriodicReport = None, silentTerminal = False, sendIPCM = True):
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
                            '_periodicReport':                  None,
                            '_periodicReport_timestamp':        None,
                            '_periodicReport_lastAnnounced_ns': 0}
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
                #If is not a new account, import assets & positions, and last periodic report if needed
                if (newAccount == False): 
                    self.__updateAccount(localID             = localID, importedData = {'source': 'DB', 'positions': positions, 'assets': assets})
                    self.__updateAccountPeriodicReport(localID = localID, importedData = lastPeriodicReport)
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
                                                 'tradeControlTracker': self.__getInitializedTradeControlTracker(),
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
                                                 '_analysisHandling_Queue':     list(),
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
    def __getInitializedTradeControlTracker(self):
        _tc_initialized = {'slExited':      None,
                           'rqpm_model':    dict()}
        return _tc_initialized
    def __copyTradeControlTracker(self, tradeControlTracker):
        tcTracker_copy = {'slExited':   tradeControlTracker['slExited'],
                          'rqpm_model': tradeControlTracker['rqpm_model'].copy()}
        return tcTracker_copy
    def __updateTradeControlTracker(self, localID, positionSymbol, tradeControlTrackerUpdate, updateMode):
        #Account & Position Instances
        account  = self.__accounts[localID]
        position = account['positions'][positionSymbol]
        #Updated Trade Control
        tcTracker = position['tradeControlTracker']
        #---[1]: SL Exited
        if ('slExited' in tradeControlTrackerUpdate):
            tcTracker['slExited'] = tradeControlTrackerUpdate['slExited'][updateMode]
    def __updateAccounts(self):
        for localID in self.__accounts_virtualServer:
            #[1]: Instances
            account               = self.__accounts[localID]
            account_virtualServer = self.__accounts_virtualServer[localID]

            #[2]: Account Data Update
            if not (_ACCOUNT_UPDATEINTERVAL_NS < time.perf_counter_ns()-account['_lastUpdated']): 
                continue

            #[3]: Account Data Update
            self.__updateAccount(localID      = localID, 
                                 importedData = {'source':    'VIRTUALSERVER', 
                                                 'positions': account_virtualServer['positions'], 
                                                 'assets':    account_virtualServer['assets']})
            self.__updateAccountPeriodicReport(localID      = localID, 
                                               importedData = None)
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
                    _tcTracker = _position_imported['tradeControlTracker']
                    _tcTracker['rqpm_model'] = dict()
                    _position['tradeControlTracker'] = _tcTracker
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
            self.__handleAnalysisResults(localID  = localID)
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
    def __updateAccountPeriodicReport(self, localID, importedData = None):
        _account = self.__accounts[localID]
        _assets  = _account['assets']
        #Data import from DB
        if (importedData != None):
            _importedReport_timestamp = importedData['timestamp']
            _importedReport_report    = importedData['report']
            _t_current_hour = int(time.time()/3600)*3600
            if (_importedReport_timestamp == _t_current_hour): 
                _account['_periodicReport']                  = _importedReport_report
                _account['_periodicReport_timestamp']        = _t_current_hour
                _account['_periodicReport_lastAnnounced_ns'] = time.perf_counter_ns()
            else:
                _account['_periodicReport'] = dict()
                for _assetName in _account['assets']:
                    _asset = _account['assets'][_assetName]
                    _mb = _asset['marginBalance']
                    _wb = _asset['walletBalance']
                    if (_asset['commitmentRate'] == None): _commimtmentRate = 0
                    else:                                  _commimtmentRate = _asset['commitmentRate']
                    if (_asset['riskLevel'] == None): _riskLevel = 0
                    else:                             _riskLevel = _asset['riskLevel']
                    _account['_periodicReport'][_assetName] = {'nTrades':             0,
                                                               'nTrades_buy':         0,
                                                               'nTrades_sell':        0,
                                                               'nTrades_entry':       0,
                                                               'nTrades_clear':       0,
                                                               'nTrades_exit':        0,
                                                               'nTrades_fslImmed':    0,
                                                               'nTrades_fslClose':    0,
                                                               'nTrades_liquidation': 0,
                                                               'nTrades_forceClear':  0,
                                                               'nTrades_unknown':     0,
                                                               'nTrades_gain':        0,
                                                               'nTrades_loss':        0,
                                                               'marginBalance_open': _mb, 'marginBalance_min': _mb, 'marginBalance_max': _mb, 'marginBalance_close': _mb,
                                                               'walletBalance_open': _wb, 'walletBalance_min': _wb, 'walletBalance_max': _wb, 'walletBalance_close': _wb,
                                                               'commitmentRate_open': _commimtmentRate, 'commitmentRate_min': _commimtmentRate, 'commitmentRate_max': _commimtmentRate, 'commitmentRate_close': _commimtmentRate,
                                                               'riskLevel_open':      _riskLevel,       'riskLevel_min':      _riskLevel,       'riskLevel_max':      _riskLevel,       'riskLevel_close':      _riskLevel}
                _account['_periodicReport_timestamp']        = _t_current_hour
                _account['_periodicReport_lastAnnounced_ns'] = time.perf_counter_ns()
        #No imported data, internal handling (+announcement if needed)
        else:
            
            _t_current_hour = (time.time()//_ACCOUNT_PERIODICREPORTFORMATTINGTINTERVAL_S)*_ACCOUNT_PERIODICREPORTFORMATTINGTINTERVAL_S
            if (_t_current_hour == _account['_periodicReport_timestamp']):
                #Report Update
                for _assetName in _assets:
                    _asset             = _assets[_assetName]
                    _hReport_thisAsset = _account['_periodicReport'][_assetName]
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
                if (_ACCOUNT_PERIODICREPORTANNOUNCEMENTINTERVAL_NS <= time.perf_counter_ns()-_account['_periodicReport_lastAnnounced_ns']):
                    _periodicReport_copy = dict()
                    for _assetName in _account['_periodicReport']: _periodicReport_copy[_assetName] = _account['_periodicReport'][_assetName].copy()
                    #Announcement
                    self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'updateAccountPeriodicReport', functionParams = {'localID': localID, 'timestamp': _t_current_hour, 'periodicReport': _periodicReport_copy}, farrHandler = None)
                    _account['_periodicReport_lastAnnounced_ns'] = time.perf_counter_ns()
            #If new interval, create a copy of the previous and format new
            else:
                #Previous report copy
                if (_account['_periodicReport'] == None): _periodicReport_prevCopy = None
                else:
                    _periodicReport_prevCopy = dict()
                    for _assetName in _account['_periodicReport']: _periodicReport_prevCopy[_assetName] = _account['_periodicReport'][_assetName].copy()
                #New interval formatting
                _account['_periodicReport'] = dict()
                for _assetName in _account['assets']:
                    _asset = _account['assets'][_assetName]
                    _mb = _asset['marginBalance']
                    _wb = _asset['walletBalance']
                    if (_asset['commitmentRate'] == None): _commimtmentRate = 0
                    else:                                  _commimtmentRate = _asset['commitmentRate']
                    if (_asset['riskLevel'] == None): _riskLevel = 0
                    else:                             _riskLevel = _asset['riskLevel']
                    _account['_periodicReport'][_assetName] = {'nTrades':             0,
                                                               'nTrades_buy':         0,
                                                               'nTrades_sell':        0,
                                                               'nTrades_entry':       0,
                                                               'nTrades_clear':       0,
                                                               'nTrades_exit':        0,
                                                               'nTrades_fslImmed':    0,
                                                               'nTrades_fslClose':    0,
                                                               'nTrades_liquidation': 0,
                                                               'nTrades_forceClear':  0,
                                                               'nTrades_unknown':     0,
                                                               'nTrades_gain':        0,
                                                               'nTrades_loss':        0,
                                                               'marginBalance_open': _mb, 'marginBalance_min': _mb, 'marginBalance_max': _mb, 'marginBalance_close': _mb,
                                                               'walletBalance_open': _wb, 'walletBalance_min': _wb, 'walletBalance_max': _wb, 'walletBalance_close': _wb,
                                                               'commitmentRate_open': _commimtmentRate, 'commitmentRate_min': _commimtmentRate, 'commitmentRate_max': _commimtmentRate, 'commitmentRate_close': _commimtmentRate,
                                                               'riskLevel_open':      _riskLevel,       'riskLevel_min':      _riskLevel,       'riskLevel_max':      _riskLevel,       'riskLevel_close':      _riskLevel}
                _account['_periodicReport_timestamp'] = _t_current_hour
                #New interval copy
                _periodicReport_newCopy = dict()
                for _assetName in _account['_periodicReport']: _periodicReport_newCopy[_assetName] = _account['_periodicReport'][_assetName].copy()
                #Announcement
                if (_periodicReport_prevCopy is not None): self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'updateAccountPeriodicReport', functionParams = {'localID': localID, 'timestamp': _t_current_hour-3600, 'periodicReport': _periodicReport_prevCopy}, farrHandler = None)
                self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'updateAccountPeriodicReport', functionParams = {'localID': localID, 'timestamp': _t_current_hour, 'periodicReport': _periodicReport_newCopy}, farrHandler = None)
                _account['_periodicReport_lastAnnounced_ns'] = time.perf_counter_ns()
    def __updateAccountPeriodicReport_onTrade(self, localID, positionSymbol, side, logicSource, profit):
        #[1]: Instances
        account  = self.__accounts[localID]
        position = account['positions'][positionSymbol]
        qAsset   = position['quoteAsset']
        asset    = account['assets'][qAsset]
        pReport  = account['_periodicReport'][qAsset]

        #[2]: Report Update
        #---[2-1]: Counters
        pReport['nTrades'] += 1
        if   side == 'BUY':  pReport['nTrades_buy']  += 1
        elif side == 'SELL': pReport['nTrades_sell'] += 1
        if   logicSource == 'ENTRY':       pReport['nTrades_entry']       += 1
        elif logicSource == 'CLEAR':       pReport['nTrades_clear']       += 1
        elif logicSource == 'EXIT':        pReport['nTrades_exit']        += 1
        elif logicSource == 'FSLIMMED':    pReport['nTrades_fslImmed']    += 1
        elif logicSource == 'FSLCLOSE':    pReport['nTrades_fslClose']    += 1
        elif logicSource == 'LIQUIDATION': pReport['nTrades_liquidation'] += 1
        elif logicSource == 'FORCECLEAR':  pReport['nTrades_forceClear']  += 1
        elif logicSource == 'UNKNOWN':     pReport['nTrades_unknown']     += 1
        if profit is not None:
            if   0 < profit:  pReport['nTrades_gain'] += 1
            elif profit <= 0: pReport['nTrades_loss'] += 1

        #---[2-2]: Balances & Commitment Rate & Risk Level
        #------[2-2-1]: Margin Balance
        asset_mb = asset['marginBalance']
        if asset_mb is not None:
            if pReport['marginBalance_open'] is None: pReport['marginBalance_open'] = asset_mb
            if (pReport['marginBalance_min'] is None) or (asset_mb < pReport['marginBalance_min']): pReport['marginBalance_min'] = asset_mb
            if (pReport['marginBalance_max'] is None) or (pReport['marginBalance_max'] < asset_mb): pReport['marginBalance_max'] = asset_mb
            pReport['marginBalance_close'] = asset_mb
        #------[2-2-2]: Wallet Balance
        asset_wb = asset['walletBalance']
        if asset_wb is not None:
            if pReport['walletBalance_open'] is None: pReport['walletBalance_open'] = asset_wb
            if (pReport['walletBalance_min'] is None) or (asset_wb < pReport['walletBalance_min']): pReport['walletBalance_min'] = asset_wb
            if (pReport['walletBalance_max'] is None) or (pReport['walletBalance_max'] < asset_wb): pReport['walletBalance_max'] = asset_wb
            pReport['walletBalance_close'] = asset_wb
        #------[2-2-3]: Commitment Rate
        asset_cr = asset['commitmentRate']
        cr = 0 if asset_cr is None else asset_cr
        pReport['commitmentRate_min'] = min(cr, pReport['commitmentRate_min'])
        pReport['commitmentRate_max'] = max(cr, pReport['commitmentRate_max'])
        pReport['commitmentRate_close'] = cr
        #------[2-2-4]: Risk Level
        asset_rl = asset['riskLevel']
        rl = 0 if asset_rl is None else asset_rl
        pReport['riskLevel_min'] = min(rl, pReport['riskLevel_min'])
        pReport['riskLevel_max'] = max(rl, pReport['riskLevel_max'])
        pReport['riskLevel_close'] = rl

        #[3]: Announcement Timer Update To Force Announcement
        account['_periodicReport_lastAnnounced_ns'] = 0

    #---Trade Controls
    def __handleAnalysisResults(self, localID):
        account   = self.__accounts[localID]
        positions = account['positions']
        for pSymbol, position in positions.items():
            #[1]: Currency Analysis Code
            caCode = position['currencyAnalysisCode']
            if (caCode is None):                         continue
            if (caCode  not in self.__currencyAnalysis): continue
            #[2]: Local Kline Data Check
            if (pSymbol not in self.__currencies_lastKline): continue
            #[3]: Analysis Handling
            ca_analysisResults                     = self.__currencyAnalysis_analysisResults[caCode]
            ca_analysisResults_deta                = ca_analysisResults['data']
            ca_analysisResults_timestamps_handling = ca_analysisResults['timestamps_handling']
            for ts in position['_analysisHandling_Queue']:
                analysisResult = ca_analysisResults_deta[ts]
                self.__handleAnalysisResult(localID = localID, positionSymbol = pSymbol, analysisResult = analysisResult)
                ca_analysisResults_timestamps_handling[ts].remove(localID)
            position['_analysisHandling_Queue'].clear()
    def __handleAnalysisResult(self, localID, positionSymbol, analysisResult):
        #Instances
        account  = self.__accounts[localID]
        position = account['positions'][positionSymbol]

        #Trade Configuration Code Check
        tcCode = position['tradeConfigurationCode']
        if tcCode not in self.__tradeConfigurations_loaded: 
            return
        tcConfig  = self.__tradeConfigurations_loaded[tcCode]['config']
        tcTracker = position['tradeControlTracker']

        #Last Kline & AnalysisResult
        lastkline = self.__currencies_lastKline[positionSymbol]
        (linearizedAnalysis, kline_onAnalysis) = analysisResult

        #Analysis Result Expiration Check (Whether this was historical / current)
        t_current_s = time.time()
        mrktRegTS   = self.__currencies[positionSymbol]['kline_firstOpenTS']
        kline_onAnalysis_TS = kline_onAnalysis[KLINDEX_OPENTIME]
        pDelta_onDispatch   = abs(lastkline[KLINDEX_CLOSEPRICE]/kline_onAnalysis[KLINDEX_CLOSEPRICE]-1)
        tsInterval_prev = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = t_current_s, mrktReg = mrktRegTS, nTicks = -1)
        tsInterval_this = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = t_current_s, mrktReg = mrktRegTS, nTicks =  0)
        if (kline_onAnalysis_TS == tsInterval_prev):
            if (_TRADE_ANALYSISHANDLINGFILTER_KLINECLOSEPRICE <= pDelta_onDispatch): ar_expired = True
            else:                                                                    ar_expired = False
        elif (kline_onAnalysis_TS == tsInterval_this): ar_expired = False
        else:                                          ar_expired = True

        #RQP Value
        tcConfig_rqpm_functionType   = tcConfig['rqpm_functionType']
        tcConfig_rqpm_functionParams = tcConfig['rqpm_functionParams']
        try:
            rqpValue = atmEta_RQPMFunctions.RQPMFUNCTIONS_GET_RQPVAL[tcConfig_rqpm_functionType](params             = tcConfig_rqpm_functionParams, 
                                                                                                 kline              = kline_onAnalysis, 
                                                                                                 linearizedAnalysis = linearizedAnalysis, 
                                                                                                 tcTracker_model    = tcTracker['rqpm_model'])
            if (rqpValue is None): return
        except Exception as e:
            self.__logger(message = (f"An unexpected error occurred during RQP value calculation. User attention strongly advised.\n"
                                     f" * Local ID:            {localID}\n"
                                     f" * Position Symbol:     {positionSymbol}\n"
                                     f" * RQP Function Type:   {tcConfig_rqpm_functionType}\n"
                                     f" * RQP Function Params: {tcConfig_rqpm_functionParams}\n"
                                     f" * Kline Timestamp:     {kline_onAnalysis_TS}\n"
                                     f" * Linearized Analysis: {linearizedAnalysis}\n"
                                     f" * Time:                {time.time()}\n"
                                     f" * Error:               {e}\n"
                                     f" * Detailed Trace:      {traceback.format_exc()}"), 
                          logType = 'Error',
                          color   = 'light_red')
            return
        if (not type(rqpValue) in (float, int) or not (-1 <= rqpValue <= 1)):
            self.__logger(message = (f"An unexpected RQP value detected. RQP value must be an integer or float in range [-1.0, 1.0]. User attention strongly advised.\n"
                                     f" * Local ID:            {localID}\n"
                                     f" * Position Symbol:     {positionSymbol}\n"
                                     f" * RQP Function Type:   {tcConfig_rqpm_functionType}\n"
                                     f" * RQP Function Params: {tcConfig_rqpm_functionParams}\n"
                                     f" * RQP Value:           {rqpValue}\n"
                                     f" * Kline Timestamp:     {kline_onAnalysis_TS}\n"
                                     f" * Linearized Analysis: {linearizedAnalysis}\n"
                                     f" * Time:                {time.time()}"), 
                          logType = 'Warning',
                          color   = 'light_red')
            return

        #SL Exit Flag
        tct_sle = tcTracker['slExited']
        if tct_sle is not None and not ar_expired:
            tct_sle_side, tct_sle_time = tct_sle
            if tct_sle_time < kline_onAnalysis_TS and \
               ((tct_sle_side == 'SHORT' and 0 < rqpValue) or \
                (tct_sle_side == 'LONG'  and rqpValue < 0)):
                tcTracker['slExited'] = None
        if not ar_expired:
            tcTracker_copied = self.__copyTradeControlTracker(tradeControlTracker = tcTracker)
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                                  prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol, 'tradeControlTracker'), 
                                  prdContent = tcTracker_copied)
            self.ipcA.sendFAR(targetProcess  = 'GUI', 
                              functionID     = 'onAccountUpdate', 
                              functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, positionSymbol, 'tradeControlTracker')}, 
                              farrHandler    = None)
            self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER',
                              functionID     = 'editAccountData',
                              functionParams = {'updates': [((localID, 'positions', positionSymbol, 'tradeControlTracker'), tcTracker_copied),]}, 
                              farrHandler    = None)
            
        #Trade Status Check
        if ar_expired:                   return
        if not (account['tradeStatus']):  return
        if not (position['tradeStatus']): return

        #Trade Handlers Determination
        tradeHandler_checkList = {'ENTRY': None,
                                  'CLEAR': None,
                                  'EXIT':  None}
        #---CheckList 1: CLEAR
        if   ((position['quantity'] < 0) and (0 < rqpValue)): tradeHandler_checkList['CLEAR'] = 'BUY'
        elif ((0 < position['quantity']) and (rqpValue < 0)): tradeHandler_checkList['CLEAR'] = 'SELL'
        #---CheckList 2: ENTRY & EXIT
        pslCheck = (tcConfig['postStopLossReentry'] == True) or (tcTracker['slExited'] is None)
        if (rqpValue < 0):  
            if ((pslCheck == True) and ((tcConfig['direction'] == 'BOTH') or (tcConfig['direction'] == 'SHORT'))): tradeHandler_checkList['ENTRY'] = 'SELL'
            tradeHandler_checkList['EXIT'] = 'BUY'
        elif (0 < rqpValue):
            if ((pslCheck == True) and ((tcConfig['direction'] == 'BOTH') or (tcConfig['direction'] == 'LONG'))): tradeHandler_checkList['ENTRY'] = 'BUY'
            tradeHandler_checkList['EXIT'] = 'SELL'
        elif (rqpValue == 0):
            if   (position['quantity'] < 0): tradeHandler_checkList['EXIT'] = 'BUY'
            elif (0 < position['quantity']): tradeHandler_checkList['EXIT'] = 'SELL'

        #---Trade Handlers Determination
        tradeHandlers = list()
        if (tradeHandler_checkList['CLEAR'] is not None): tradeHandlers.append('CLEAR')
        if (tradeHandler_checkList['EXIT']  is not None): tradeHandlers.append('EXIT')
        if (tradeHandler_checkList['ENTRY'] is not None): tradeHandlers.append('ENTRY')

        position['_tradeHandlers'] += [{'type':              thType, 
                                        'side':              tradeHandler_checkList[thType],
                                        'rqpVal':            rqpValue,
                                        'generationTime_ns': time.time_ns()} 
                                        for thType in tradeHandlers]
    def __processTradeHandlers(self, localID):
        account   = self.__accounts[localID]
        positions = account['positions']
        for pSymbol in positions:
            position      = positions[pSymbol]
            precisions    = position['precisions']
            tradeHandlers = position['_tradeHandlers']
            tcTracker     = position['tradeControlTracker']

            #[1]: Status Check
            if not(tradeHandlers):                              continue #If there exists no tradeHandlers, continue
            if (position['_orderCreationRequest'] is not None): continue #If there exists a generated order creation request, continue
            if (position['_marginTypeControlRequested']):       continue #If there exists a margin type control request, continue
            if (position['_leverageControlRequested']):         continue #If there exists a leverage control request, continue

            #[2]: Position Preparation Check
            if ((position['tradeConfigurationCode'] is None) or (position['tradeConfigurationCode'] not in self.__tradeConfigurations_loaded)): continue
            if (self.__currencies[pSymbol]['info_server'] is None):                                                                             continue
            if (pSymbol not in self.__currencies_lastKline):                                                                                    continue
            tcConfig      = self.__tradeConfigurations_loaded[position['tradeConfigurationCode']]['config']
            serverFilters = self.__currencies[pSymbol]['info_server']['filters']
            kline         = self.__currencies_lastKline[pSymbol]
            
            #[3]: Trade Handler Selection & Expiration Check
            tradeHandler = tradeHandlers.pop(0)
            th_type       = tradeHandler['type']
            th_side       = tradeHandler['side']
            th_rqpVal     = tradeHandler['rqpVal']
            th_genTime_ns = tradeHandler['generationTime_ns']
            if (_TRADE_TRADEHANDLER_LIFETIME_NS < time.time_ns()-th_genTime_ns):
                self.__logger(message = (f"A trade handler For {localID}-{pSymbol} is expired and will be discarded.\n"
                                         f" * Type:                 {th_type}\n"
                                         f" * Side:                 {th_side}\n"
                                         f" * RQP Value:            {th_rqpVal}\n"
                                         f" * Generation Time [ns]: {th_genTime_ns}\n"), 
                              logType = 'Warning',
                              color   = 'light_magenta')
                continue

            #[4]: Handling
            #---[4-1]: ENTRY
            if (th_type == 'ENTRY'):
                #Balance Commitment Check
                _balance_allocated = position['allocatedBalance']                                          if (position['allocatedBalance'] is not None) else 0
                _balance_committed = abs(position['quantity'])*position['entryPrice']/tcConfig['leverage'] if (position['entryPrice']       is not None) else 0
                _balance_toCommit  = _balance_allocated*abs(th_rqpVal)
                _balance_toEnter   = _balance_toCommit-_balance_committed
                if not(0 < _balance_toEnter): continue
                #Quantity Determination
                _quantity_minUnit = pow(10, -precisions['quantity'])
                _quantity         = round(int((_balance_toEnter/kline[KLINDEX_CLOSEPRICE]*tcConfig['leverage'])/_quantity_minUnit)*_quantity_minUnit, precisions['quantity'])
                if (_quantity < 0): 
                    self.__logger(message = (f"A trade handler for {localID}-{pSymbol} failed quantity test and will be discarded. - 'NEGATIVE QUANTITY'\n"
                                             f" * type:             {th_type}\n"
                                             f" * side:             {th_side}\n"
                                             f" * rqpVal:           {th_rqpVal}\n"
                                             f" * genTime_ns:       {th_genTime_ns}\n"
                                             f" * quantity_current: {position['quantity']}\n"
                                             f" * quantity_trade:   {_quantity}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue
                if (_quantity == 0): 
                    self.__logger(message = (f"A trade handler for {localID}-{pSymbol} failed quantity test and will be discarded. - 'ZERO QUANTITY'\n"
                                             f" * type:             {th_type}\n"
                                             f" * side:             {th_side}\n"
                                             f" * rqpVal:           {th_rqpVal}\n"
                                             f" * genTime_ns:       {th_genTime_ns}\n"
                                             f" * quantity_current: {position['quantity']}\n"
                                             f" * quantity_trade:   {_quantity}"), 
                                  logType = 'Update',
                                  color   = 'light_yellow')
                    continue
                #Server Filter Test
                serverFilterTest = None
                for serverFilter in serverFilters:
                    sf_ft = serverFilter['filterType']
                    if (sf_ft == 'PRICE_FILTER'): 
                        continue
                    elif (sf_ft == 'LOT_SIZE'):     
                        continue
                    elif (sf_ft == 'MARKET_LOT_SIZE'):
                        _minQty   = float(serverFilter['minQty'])
                        _maxQty   = float(serverFilter['maxQty'])
                        _stepSize = float(serverFilter['stepSize'])
                        if not(_minQty <= _quantity):
                            serverFilterTest = {'type':   'MINQTY',
                                                'minQty': _minQty}
                            break
                        if not(_quantity <= _maxQty):
                            serverFilterTest = {'type':   'MAXQTY',
                                                'minQty': _maxQty}
                            break
                        if not(_quantity == round(_quantity, -math.floor(math.log10(_stepSize)))): 
                            serverFilterTest = {'type':               'STEPSIZE',
                                                'stepSize':           _stepSize,
                                                'stepSize_val':       math.floor(math.log10(_stepSize)),
                                                'quantity_stepSized': round(_quantity, -math.floor(math.log10(_stepSize)))}
                            break
                    elif (sf_ft == 'MAX_NUM_ORDERS'): 
                        continue
                    elif (sf_ft == 'MAX_NUM_ALGO_ORDERS'): 
                        continue
                    elif (sf_ft == 'MIN_NOTIONAL'):
                        _notional_min = float(serverFilter['notional'])
                        _notional = kline[KLINDEX_CLOSEPRICE]*_quantity
                        if not(_notional_min <= _notional):
                            serverFilterTest = {'type':        'MINNOTIONAL',
                                                'notional':     _notional,
                                                'notional_min': _notional_min}
                            break
                    elif (sf_ft == 'PERCENT_PRICE'): 
                        continue
                if (serverFilterTest is not None):
                    self.__logger(message = (f"A trade handler for {localID}-{pSymbol} failed server filter test and will be discarded.\n"
                                             f" * type:             {th_type}\n"
                                             f" * side:             {th_side}\n"
                                             f" * rqpVal:           {th_rqpVal}\n"
                                             f" * genTime_ns:       {th_genTime_ns}\n"
                                             f" * quantity_current: {position['quantity']}\n"
                                             f" * quantity_trade:   {_quantity}\n"
                                             f" * serverFilterTest: {serverFilterTest}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue
                #Side Confirm
                if not(((position['quantity'] <= 0) and (th_side == 'SELL')) or \
                       ((0 <= position['quantity']) and (th_side == 'BUY'))): 
                    self.__logger(message = (f"A trade handler for {localID}-{pSymbol} failed side test and will be discarded.\n"
                                             f" * type:             {th_type}\n"
                                             f" * side:             {th_side}\n"
                                             f" * rqpVal:           {th_rqpVal}\n"
                                             f" * genTime_ns:       {th_genTime_ns}\n"
                                             f" * quantity_current: {position['quantity']}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue
                #Finally
                self.__orderCreationRequest_generate(localID         = localID,
                                                     positionSymbol  = pSymbol,
                                                     logicSource     = 'ENTRY',
                                                     side            = th_side,
                                                     quantity        = _quantity,
                                                     tcTrackerUpdate = None,
                                                     ipcRID          = None)
            #---[4-2]: CLEAR
            elif (th_type == 'CLEAR'):
                #Quantity Determination
                _quantity = round(abs(position['quantity']), precisions['quantity'])
                if not(0 < _quantity): 
                    self.__logger(message = (f"A trade handler for {localID}-{pSymbol} failed quantity test and will be discarded.\n"
                                             f" * type:             {th_type}\n"
                                             f" * side:             {th_side}\n"
                                             f" * rqpVal:           {th_rqpVal}\n"
                                             f" * genTime_ns:       {th_genTime_ns}\n"
                                             f" * quantity_current: {position['quantity']}\n"
                                             f" * quantity_trade:   {_quantity}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue
                #Side Confirm
                if not(((position['quantity'] < 0) and (th_side == 'BUY')) or \
                       ((0 < position['quantity']) and (th_side == 'SELL'))): 
                    self.__logger(message = (f"A trade handler for {localID}-{pSymbol} failed side test and will be discarded.\n"
                                             f" * type:             {th_type}\n"
                                             f" * side:             {th_side}\n"
                                             f" * rqpVal:           {th_rqpVal}\n"
                                             f" * genTime_ns:       {th_genTime_ns}\n"
                                             f" * quantity_current: {position['quantity']}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue
                #Finally
                self.__orderCreationRequest_generate(localID         = localID,
                                                     positionSymbol  = pSymbol,
                                                     logicSource     = 'CLEAR',
                                                     side            = th_side,
                                                     quantity        = _quantity,
                                                     tcTrackerUpdate = None,
                                                     ipcRID          = None)
            #---[4-3]: EXIT
            elif (th_type == 'EXIT'):
                #Balance Commitment Check
                _balance_allocated = position['allocatedBalance']                                          if (position['allocatedBalance'] is not None) else 0
                _balance_committed = abs(position['quantity'])*position['entryPrice']/tcConfig['leverage'] if (position['entryPrice']       is not None) else 0
                _balance_toCommit  = _balance_allocated*abs(th_rqpVal)
                _balance_toEnter   = _balance_toCommit-_balance_committed
                if not(_balance_toEnter < 0): continue
                #Quantity Determination
                _quantity_minUnit = pow(10, -precisions['quantity'])
                _quantity         = round(int((-_balance_toEnter/position['entryPrice']*tcConfig['leverage'])/_quantity_minUnit)*_quantity_minUnit, precisions['quantity'])
                if (_quantity < 0): 
                    self.__logger(message = (f"A trade handler for {localID}-{pSymbol} failed quantity test and will be discarded. - 'NEGATIVE QUANTITY'\n"
                                             f" * type:             {th_type}\n"
                                             f" * side:             {th_side}\n"
                                             f" * rqpVal:           {th_rqpVal}\n"
                                             f" * genTime_ns:       {th_genTime_ns}\n"
                                             f" * quantity_current: {position['quantity']}\n"
                                             f" * quantity_trade:   {_quantity}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue
                if (_quantity == 0): 
                    self.__logger(message = (f"A trade handler for {localID}-{pSymbol} failed quantity test and will be discarded. - 'ZERO QUANTITY'\n"
                                             f" * type:             {th_type}\n"
                                             f" * side:             {th_side}\n"
                                             f" * rqpVal:           {th_rqpVal}\n"
                                             f" * genTime_ns:       {th_genTime_ns}\n"
                                             f" * quantity_current: {position['quantity']}\n"
                                             f" * quantity_trade:   {_quantity}"), 
                                  logType = 'Update',
                                  color   = 'light_yellow')
                    continue
                #Side Confirm
                if not(((position['quantity'] < 0) and (th_side == 'BUY')) or \
                       ((0 < position['quantity']) and (th_side == 'SELL'))): 
                    self.__logger(message = (f"A trade handler for {localID}-{pSymbol} failed side test and will be discarded.\n"
                                             f" * type:             {th_type}\n"
                                             f" * side:             {th_side}\n"
                                             f" * rqpVal:           {th_rqpVal}\n"
                                             f" * genTime_ns:       {th_genTime_ns}\n"
                                             f" * quantity_current: {position['quantity']}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue
                #Finally
                self.__orderCreationRequest_generate(localID         = localID,
                                                     positionSymbol  = pSymbol,
                                                     logicSource     = 'EXIT',
                                                     side            = th_side,
                                                     quantity        = _quantity,
                                                     tcTrackerUpdate = None,
                                                     ipcRID          = None)
            #---[4-4]: FSLIMMED & FSLCLOSE
            elif (th_type == 'FSLIMMED') or (th_type == 'FSLCLOSE'):
                #Quantity Determination
                _quantity = round(abs(position['quantity']), precisions['quantity'])
                if not(0 < _quantity): 
                    self.__logger(message = (f"A trade handler for {localID}-{pSymbol} failed quantity test and will be discarded.\n"
                                             f" * type:             {th_type}\n"
                                             f" * side:             {th_side}\n"
                                             f" * rqpVal:           {th_rqpVal}\n"
                                             f" * genTime_ns:       {th_genTime_ns}\n"
                                             f" * quantity_current: {position['quantity']}\n"
                                             f" * quantity_trade:   {_quantity}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue
                #Side Confirm
                if not(((position['quantity'] < 0) and (th_side == 'BUY')) or \
                       ((0 < position['quantity']) and (th_side == 'SELL'))): 
                    self.__logger(message = (f"A trade handler for {localID}-{pSymbol} failed side test and will be discarded.\n"
                                             f" * type:             {th_type}\n"
                                             f" * side:             {th_side}\n"
                                             f" * rqpVal:           {th_rqpVal}\n"
                                             f" * genTime_ns:       {th_genTime_ns}\n"
                                             f" * quantity_current: {position['quantity']}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue
                #Finally
                if   (position['quantity'] < 0): slTriggeredSide = 'SHORT'
                elif (0 < position['quantity']): slTriggeredSide = 'LONG'
                self.__orderCreationRequest_generate(localID         = localID,
                                                     positionSymbol  = pSymbol,
                                                     logicSource     = th_type,
                                                     side            = th_side,
                                                     quantity        = _quantity,
                                                     tcTrackerUpdate = {'slExited': {'onComplete': (slTriggeredSide, kline[KLINDEX_OPENTIME]), 
                                                                                     'onPartial':  (slTriggeredSide, kline[KLINDEX_OPENTIME]), 
                                                                                     'onFail':     (slTriggeredSide, kline[KLINDEX_OPENTIME])}},
                                                     ipcRID          = None)
    def __orderCreationRequest_generate(self, localID, positionSymbol, logicSource, side, quantity, tcTrackerUpdate = None, ipcRID = None):
        account    = self.__accounts[localID]
        position   = account['positions'][positionSymbol]
        precisions = position['precisions']
        #[1]: OCR Check
        if (position['_orderCreationRequest'] is not None): 
            self.__logger(message = f"OCR Generation Rejected - OCR Not Empty. [localID: {localID}, positionSymbol: {positionSymbol}, logicSource: {logicSource}, side: {side}, quantity: {quantity}, tcTrackerUpdate: {tcTrackerUpdate}, ipcRID: {ipcRID}]", 
                          logType = 'Warning', 
                          color   = 'light_red')
            return False
        #[2]: OCR Generation
        if   (side == 'BUY'):  targetQuantity = round(position['quantity']+quantity, precisions['quantity'])
        elif (side == 'SELL'): targetQuantity = round(position['quantity']-quantity, precisions['quantity'])
        ocr = {'logicSource':          logicSource,
               'forceClearRID':        ipcRID,
               'originalQuantity':     position['quantity'],
               'targetQuantity':       targetQuantity,
               'orderParams':          {'symbol':     positionSymbol,
                                        'side':       side,
                                        'type':       'MARKET',
                                        'quantity':   quantity,
                                        'reduceOnly': not(logicSource == 'ENTRY')},
               'tcTrackerUpdate':      tcTrackerUpdate,
               'dispatchID':           None,
               'lastRequestReceived':  False,
               'results':              list(),
               'nAttempts':            1}
        position['_orderCreationRequest'] = ocr
        #[3]: Request Dispatch
        #---[2-1]: Virtual
        if (account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL): 
            ocr['dispatchID'] = time.perf_counter_ns()
            self.__accounts_virtualServer[localID]['_orderCreationRequests'][ocr['dispatchID']] = {'positionSymbol': positionSymbol,
                                                                                                   'orderParams':    ocr['orderParams'].copy()}
        #---[2-2]: Actual
        elif (account['accountType'] == _ACCOUNT_ACCOUNTTYPE_ACTUAL):
            ocr['dispatchID'] = self.ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                                                  functionID     = 'createOrder', 
                                                  functionParams = {'localID':        localID, 
                                                                    'positionSymbol': positionSymbol, 
                                                                    'orderParams':    ocr['orderParams'].copy()}, 
                                                  farrHandler    = self.__far_onPositionControlResponse)
        #[4]: Finally
        return True
    def __orderCreationRequest_regenerate(self, localID, positionSymbol, quantity_unfilled):
        account  = self.__accounts[localID]
        position = account['positions'][positionSymbol]
        ocr      = position['_orderCreationRequest']
        #[1]: OCR Update
        ocr['orderParams']['quantity'] = quantity_unfilled
        ocr['lastRequestReceived']     = False
        ocr['nAttempts']               += 1
        #---[1-1]: Virtual
        if (account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL): 
            ocr['dispatchID'] = time.perf_counter_ns()
            self.__accounts_virtualServer[localID]['_orderCreationRequests'][ocr['dispatchID']] = {'positionSymbol': positionSymbol,
                                                                                                   'orderParams':    ocr['orderParams'].copy()}
        #---[1-2]: Actual
        elif (account['accountType'] == _ACCOUNT_ACCOUNTTYPE_ACTUAL):
            ocr['dispatchID'] = self.ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                                                  functionID     = 'createOrder', 
                                                  functionParams = {'localID':        localID, 
                                                                    'positionSymbol': positionSymbol, 
                                                                    'orderParams':    ocr['orderParams'].copy()}, 
                                                  farrHandler    = self.__far_onPositionControlResponse)
    def __orderCreationRequest_terminate(self, localID, positionSymbol, quantity_new):
        account  = self.__accounts[localID]
        position = account['positions'][positionSymbol]
        ocr      = position['_orderCreationRequest']
        #[1]: Update Mode Determination
        if (quantity_new == ocr['targetQuantity']): updateMode = 'onComplete'
        else:
            if (ocr['targetQuantity'] < ocr['originalQuantity']):
                if (ocr['targetQuantity'] < quantity_new) and (quantity_new < ocr['originalQuantity']): updateMode = 'onPartial'
                else:                                                                                   updateMode = 'onFail'
            elif (ocr['originalQuantity'] < ocr['targetQuantity']):
                if (ocr['originalQuantity'] < quantity_new) and (quantity_new < ocr['targetQuantity']): updateMode = 'onPartial'
                else:                                                                                   updateMode = 'onFail'
        #[2]: Trade Control Tracker Update
        if (ocr['tcTrackerUpdate'] is not None):
            self.__updateTradeControlTracker(localID = localID, positionSymbol = positionSymbol, tradeControlTrackerUpdate = ocr['tcTrackerUpdate'], updateMode = updateMode)
            tcTracker_copied = self.__copyTradeControlTracker(tradeControlTracker = position['tradeControlTracker'])
            self.ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                                  prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol, 'tradeControlTracker'), 
                                  prdContent = tcTracker_copied)
            self.ipcA.sendFAR(targetProcess  = 'GUI', 
                              functionID     = 'onAccountUpdate', 
                              functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, positionSymbol, 'tradeControlTracker')}, 
                              farrHandler    = None)
            self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', 
                              functionID = 'editAccountData', 
                              functionParams = {'updates': [((localID, 'positions', positionSymbol, 'tradeControlTracker'), tcTracker_copied),]}, 
                              farrHandler = None)
        #[3]: Force Clear Response    
        if (ocr['forceClearRID'] is not None):
            _fcComplete = (updateMode == 'onComplete')
            if (_fcComplete == True): _forceClearResponseMessage = f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Successful!"
            else:                     _forceClearResponseMessage = f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Failed"
            self.ipcA.sendFARR(targetProcess  = 'GUI', 
                               functionResult = {'localID':        localID, 
                                                 'positionSymbol': positionSymbol, 
                                                 'responseOn':     'FORCECLEARPOSITION',
                                                 'result':         _fcComplete,
                                                 'message':        _forceClearResponseMessage}, 
                               requestID      = ocr['forceClearRID'], 
                               complete       = True)
        #[4]: OCR Initialization
        position['_orderCreationRequest'] = None
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
                    _tradeLog = {'timestamp':          time.time(),
                                 'positionSymbol':     positionSymbol,
                                 'logicSource':        _ocr['logicSource'],
                                 'requestComplete':    ((_ocr_result['result'] == True) and (_ocr_orderResult['originalQuantity'] == _ocr_orderResult['executedQuantity'])),
                                 'side':               _ocr_orderParams['side'],
                                 'quantity':           _ocr_orderResult['executedQuantity'],
                                 'price':              _ocr_orderResult['averagePrice'],
                                 'profit':             _profit,
                                 'tradingFee':         _tradingFee,
                                 'totalQuantity':      _quantity_new,
                                 'entryPrice':         _entryPrice_new,
                                 'walletBalance':      _walletBalance_new,
                                 'tradeControlTracker': self.__copyTradeControlTracker(tradeControlTracker = _position['tradeControlTracker'])}
                    self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'addAccountTradeLog', functionParams = {'localID': localID, 'tradeLog': _tradeLog}, farrHandler = None)
                    #Update Periodic Report
                    self.__updateAccountPeriodicReport_onTrade(localID = localID, positionSymbol = positionSymbol, side = _ocr_orderParams['side'], logicSource = _ocr['logicSource'], profit = _profit)
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
                _tradeLog = {'timestamp':           time.time(),
                             'positionSymbol':      positionSymbol,
                             'logicSource':         'UNKNOWN',
                             'requestComplete':     None,
                             'side':                _side,
                             'quantity':            abs(_quantity_delta_unknown),
                             'price':               None,
                             'profit':              None,
                             'tradingFee':          None,
                             'totalQuantity':       quantity_new,
                             'entryPrice':          entryPrice_new,
                             'walletBalance':       None,
                             'tradeControlTracker': self.__copyTradeControlTracker(tradeControlTracker = _position['tradeControlTracker'])}
                self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'addAccountTradeLog', functionParams = {'localID': localID, 'tradeLog': _tradeLog}, farrHandler = None)
            #Update Periodic Report
            self.__updateAccountPeriodicReport_onTrade(localID = localID, positionSymbol = positionSymbol, side = _side, logicSource = 'UNKNOWN', profit = None)
            #External Clearing Handling (Stop trading, assume the user is taking control / liquidation occurred)
            self.__trade_onAbruptClearing(localID = localID, positionSymbol = positionSymbol, clearingType = 'UNKNOWNTRADE')
            #Trade Handlers Clearing & Trade Control Initialization (In Case No Processing OCR Exists. Otherwise, in will be handlded along with the OCR)
            if (_ocr is None):
                _position['_tradeHandlers'].clear()
                _position['tradeControlTracker'] = self.__getInitializedTradeControlTracker()
                self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', 
                                  functionID = 'editAccountData', 
                                  functionParams = {'updates': [((localID, 'positions', positionSymbol, 'tradeControlTracker'), self.__copyTradeControlTracker(tradeControlTracker = _position['tradeControlTracker'])),]}, 
                                  farrHandler = None)
            #Console Print
            if (True): 
                _message = f"Unknown Trade Detected For {localID}-{positionSymbol}.\n"\
                          +f" * LogicSource: {_tradeLog['logicSource']}\n"\
                          +f" * Side:        {_tradeLog['side']}\n"\
                          +f" * Q_Delta:     {atmEta_Auxillaries.floatToString(number = _tradeLog['quantity'], precision = _precisions['quantity'])}"
                self.__logger(message = _message, logType = 'Update', color = 'light_blue')
    def __trade_checkConditionalExits(self, localID, positionSymbol, kline, kline_closed):
        account    = self.__accounts[localID]
        position   = account['positions'][positionSymbol]
        precisions = position['precisions']

        #[1]: Status Check
        if not(account['tradeStatus'])                  or \
           not(position['tradeStatus'])                 or \
           (position['tradeConfigurationCode'] is None): return

        #[2]: Trade Control Instances
        tcConfig  = self.__tradeConfigurations_loaded[position['tradeConfigurationCode']]['config']

        #[3]: Trade Handlers Determination
        tradeHandler_checkList = {'FSLIMMED': None,
                                  'FSLCLOSE': None}
        #---[3-1]: FSLIMMED
        fslImmed = tcConfig['fullStopLossImmediate']
        if (position['quantity'] != 0) and (fslImmed is not None):
            if (position['quantity'] < 0):
                _price_FSL = round(position['entryPrice']*(1+fslImmed), precisions['price'])
                if (_price_FSL <= kline[KLINDEX_HIGHPRICE]): tradeHandler_checkList['FSLIMMED'] = 'BUY'
            elif (0 < position['quantity']):
                _price_FSL = round(position['entryPrice']*(1-fslImmed), precisions['price'])
                if (kline[KLINDEX_LOWPRICE] <= _price_FSL): tradeHandler_checkList['FSLIMMED'] = 'SELL'
        #---[3-2]: FSLCLOSE
        fslClose = tcConfig['fullStopLossClose']
        if (position['quantity'] != 0) and (fslClose is not None) and (kline_closed):
            if (position['quantity'] < 0):
                _price_FSL = round(position['entryPrice']*(1+fslClose), precisions['price'])
                if (_price_FSL <= kline[KLINDEX_CLOSEPRICE]): tradeHandler_checkList['FSLCLOSE'] = 'BUY'
            elif (0 < position['quantity']):
                _price_FSL = round(position['entryPrice']*(1-fslClose), precisions['price'])
                if (kline[KLINDEX_CLOSEPRICE] <= _price_FSL): tradeHandler_checkList['FSLCLOSE'] = 'SELL'
        
        #[4]: Trade Handlers Determination
        tradeHandlers = list()
        if   (tradeHandler_checkList['FSLIMMED'] is not None): tradeHandlers = ['FSLIMMED',]
        elif (tradeHandler_checkList['FSLCLOSE'] is not None): tradeHandlers = ['FSLCLOSE',]

        #[5]: Finally
        position['_tradeHandlers'] += [{'type':               _thType, 
                                        'side':               tradeHandler_checkList[_thType],
                                        'rqpVal':             None,
                                        'generationTime_ns':  time.time_ns()} 
                                        for _thType in tradeHandlers]
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
    def __activateAccount(self, localID, password, apiKey, secretKey, encrypted, requestID):
        #[1]: Account Check
        if (localID not in self.__accounts):
            return {'result': False, 'message': f"Account '{localID}' Activation Failed. 'The Account Does Not Exist'"}
        account = self.__accounts[localID]
        
        #[2]: Password Check
        if not(bcrypt.checkpw(password.encode(encoding = "utf-8"), account['hashedPassword'])):
            return {'result': False, 'message': f"Account '{localID}' Activation Failed. 'Incorrect Password'"}

        #[3]: Account Type Check
        if (account['accountType'] == _ACCOUNT_ACCOUNTTYPE_VIRTUAL):
            return {'result': False, 'message': f"Account '{localID}' Activation Failed. 'VIRTUAL Type Account Need Not Be Activated'"}
        
        #[4]: Decryption (If needed)
        if encrypted:
            try:
                password_hash = hashlib.sha256(password.encode()).digest()
                fernet_key    = base64.urlsafe_b64encode(password_hash)
                cipher        = Fernet(fernet_key)
                apiKey    = cipher.decrypt(apiKey.encode()).decode()
                secretKey = cipher.decrypt(secretKey.encode()).decode()
            except Exception as e:
                return {'result': False, 'message': f"Account '{localID}' Activation Failed. An unexpected error occurred during decryption: {str(e)}"}

        #[5]: Account Instance Generation Request
        dispatchID = self.ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                                       functionID     = 'generateAccountInstance', 
                                       functionParams = {'localID':   localID,
                                                         'uid':       account['buid'],
                                                         'apiKey':    apiKey,
                                                         'secretKey': secretKey},
                                       farrHandler    = self.__farr_onAccountInstanceGenerationRequestResponse)
        self.__accountInstanceGenerationRequests[dispatchID] = (localID, requestID)

        #[6]: Return None to indicate processing
        return None
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
        #[1]: Unregister position from currency analysis
        self.__unregisterPositionFromCurrencyAnalysis(localID = localID, positionSymbol = positionSymbol)
        #[2]: Currency Analysis Check & Update
        if (currencyAnalysisCode not in self.__currencyAnalysis): 
            return
        ca = self.__currencyAnalysis[currencyAnalysisCode]
        if (ca['currencySymbol'] != positionSymbol):
            return
        self.__currencyAnalysis[currencyAnalysisCode]['appliedAccounts'].add(localID)
        #[3]: Position Update
        position = self.__accounts[localID]['positions'][positionSymbol]
        position['currencyAnalysisCode'] = currencyAnalysisCode
        #[4]: Position Queue Update
        ca_aResults = self.__currencyAnalysis_analysisResults[currencyAnalysisCode]
        ca_aResults_TSs          = ca_aResults['timestamps']
        ca_aResults_TSs_handling = ca_aResults['timestamps_handling']
        position['_analysisHandling_Queue'].extend(ca_aResults_TSs)
        for ts in ca_aResults_TSs:
            if ts not in ca_aResults_TSs_handling: ca_aResults_TSs_handling[ts] = set()
            ca_aResults_TSs_handling[ts].add(localID)
    def __unregisterPositionFromCurrencyAnalysis(self, localID, positionSymbol):
        position = self.__accounts[localID]['positions'][positionSymbol]
        caCode   = position['currencyAnalysisCode']
        #[1]: Conditions Check
        if (caCode is None):                                                    return
        if (caCode  not in self.__currencyAnalysis):                            return
        if (localID not in self.__currencyAnalysis[caCode]['appliedAccounts']): return
        #[2]: Currency Analysis
        ca                       = self.__currencyAnalysis[caCode]
        ca_aResults_TSs_handling = self.__currencyAnalysis_analysisResults[caCode]['timestamps_handling']
        ca['appliedAccounts'].remove(localID)
        for ts in ca_aResults_TSs_handling:
            if localID in ca_aResults_TSs_handling[ts]: ca_aResults_TSs_handling[ts].remove(localID)
        #[3]: Position
        position['currencyAnalysisCode'] = None
        position['_analysisHandling_Queue'].clear()
    def __registerPositionTradeConfiguration(self, localID, positionSymbol, tradeConfigurationCode):
        #[1]: Unregister position trade configuration
        self.__unregisterPositionTradeConfiguration(localID = localID, positionSymbol = positionSymbol)
        #[2]: Trade Configuration Check & Update
        if (tradeConfigurationCode not in self.__tradeConfigurations):
            return
        if (tradeConfigurationCode not in self.__tradeConfigurations_loaded): 
            self.__loadTradeConfiguration(tradeConfigurationCode = tradeConfigurationCode)
        tc_loaded = self.__tradeConfigurations_loaded[tradeConfigurationCode]
        if (localID in tc_loaded['subscribers']): tc_loaded['subscribers'][localID].add(positionSymbol)
        else:                                     tc_loaded['subscribers'][localID] = {positionSymbol}
        #[3]: Position Update
        position = self.__accounts[localID]['positions'][positionSymbol]
        position['tradeConfigurationCode'] = tradeConfigurationCode
        #[4]: Position Queue Update
        caCode = position['currencyAnalysisCode']
        if caCode is None: return
        ca_aResults = self.__currencyAnalysis_analysisResults[caCode]
        ca_aResults_TSs          = ca_aResults['timestamps']
        ca_aResults_TSs_handling = ca_aResults['timestamps_handling']
        position['_analysisHandling_Queue'].extend(ca_aResults_TSs)
        for ts in ca_aResults_TSs:
            if ts not in ca_aResults_TSs_handling: ca_aResults_TSs_handling[ts] = set()
            ca_aResults_TSs_handling[ts].add(localID)
    def __unregisterPositionTradeConfiguration(self, localID, positionSymbol):
        #[1]: Position Update
        position = self.__accounts[localID]['positions'][positionSymbol]
        tcCode = position['tradeConfigurationCode']
        position['tradeConfigurationCode'] = None
        position['_tradabilityTests'] &= ~0b010
        position['_analysisHandling_Queue'].clear()
        #[2]: TC Code Check
        if (tcCode is None):                                  return
        if (tcCode not in self.__tradeConfigurations_loaded): return
        #[3]: TC Update
        tc_loaded = self.__tradeConfigurations_loaded[tcCode]
        if ((localID in tc_loaded['subscribers']) and (positionSymbol in tc_loaded['subscribers'][localID])): 
            tc_loaded['subscribers'][localID].remove(positionSymbol)
            if not tc_loaded['subscribers'][localID]: del tc_loaded['subscribers'][localID]
    def __loadTradeConfiguration(self, tradeConfigurationCode):
        #[1]: Existence Check
        if (tradeConfigurationCode not in self.__tradeConfigurations): return
        #[2]: Previous Subscribers Check
        if (tradeConfigurationCode in self.__tradeConfigurations_loaded): 
            subscribers = self.__tradeConfigurations_loaded[tradeConfigurationCode]['subscribers']
        else: subscribers = dict()
        #[3]: TC Load
        tc = self.__tradeConfigurations[tradeConfigurationCode]
        tc_copied = {'leverage':              tc['leverage'],
                     'isolated':              tc['isolated'],
                     'direction':             tc['direction'],
                     'fullStopLossImmediate': tc['fullStopLossImmediate'],
                     'fullStopLossClose':     tc['fullStopLossClose'],
                     'postStopLossReentry':   tc['postStopLossReentry'],
                     'rqpm_functionType':     tc['rqpm_functionType'],
                     'rqpm_functionParams':   tc['rqpm_functionParams'].copy()}
        self.__tradeConfigurations_loaded[tradeConfigurationCode] = {'subscribers': subscribers, 'config': tc_copied}
        #[4]: TC Reload for Subscribers
        rTargets = [(localID, positionSymbol) for localID, positionSymbols in subscribers.items() for positionSymbol in positionSymbols]
        for localID, positionSymbol in rTargets:
            self.__unregisterPositionTradeConfiguration(localID = localID, positionSymbol = positionSymbol)
            self.__registerPositionTradeConfiguration(localID   = localID, positionSymbol = positionSymbol, tradeConfigurationCode = tradeConfigurationCode)
    def __checkPositionTradability(self, localID, positionSymbol):
        _position = self.__accounts[localID]['positions'][positionSymbol]
        #[1]: Currency Analysis
        if (_position['currencyAnalysisCode'] is not None):
            if (_position['currencyAnalysisCode'] in self.__currencyAnalysis):
                if (localID in self.__currencyAnalysis[_position['currencyAnalysisCode']]['appliedAccounts']): _position['_tradabilityTests'] |=  0b001
            else:                                                                                              _position['_tradabilityTests'] &= ~0b001
        else:                                                                                                  _position['_tradabilityTests'] &= ~0b001
        #[2]: Trade Configuration
        if (_position['tradeConfigurationCode'] is not None):
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
                self.__addAccount(localID            = _localID, 
                                  buid               = _ad['buid'],
                                  accountType        = _ad['accountType'],
                                  password           = _ad['hashedPassword'],
                                  newAccount         = False,
                                  assets             = _ad['assets'],
                                  positions          = _ad['positions'],
                                  lastPeriodicReport = _ad['lastPeriodicReport'],
                                  sendIPCM           = False)
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
            _result = self.__addAccount(localID = localID, buid = buid, accountType = accountType, password = password, newAccount = True, silentTerminal = False, lastPeriodicReport = None, sendIPCM = True)
            return {'localID': localID, 'responseOn': 'ADDACCOUNT', 'result': _result['result'], 'message': _result['message']}
    def __far_removeAccount(self, requester, requestID, localID, password):
        if (requester == 'GUI'): 
            _result = self.__removeAccount(localID = localID, password = password)
            return {'localID': localID, 'responseOn': 'REMOVEACCOUNT', 'result': _result['result'], 'message': _result['message']}
    def __far_activateAccount(self, requester, requestID, localID, password, apiKey, secretKey, encrypted):
        if (requester != 'GUI'): return
        activationResult = self.__activateAccount(localID   = localID, 
                                                  password  = password, 
                                                  apiKey    = apiKey, 
                                                  secretKey = secretKey, 
                                                  encrypted = encrypted, 
                                                  requestID = requestID)
        if (activationResult is not None): 
            self.ipcA.sendFARR(targetProcess = 'GUI', 
                               functionResult = {'localID':    localID, 
                                                 'responseOn': 'ACTIVATEACCOUNT', 
                                                 'result':     False, 
                                                 'message':    activationResult['message']}, 
                               requestID = requestID, 
                               complete = True)
    def __far_deactivateAccount(self, requester, requestID, localID, password):
        if (requester != 'GUI'): return
        deactivationResult = self.__deactivateAccount(localID  = localID, 
                                                      password = password)
        return {'localID':    localID, 
                'responseOn': 'DEACTIVATEACCOUNT', 
                'result':     deactivationResult['result'], 
                'message':    deactivationResult['message']}
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
        #[1]: Requester Check
        if (requester != 'GUI'): return

        #[2]: Acocunt Check
        if (localID not in self.__accounts):
            self.ipcA.sendFARR(targetProcess = 'GUI', 
                               functionResult = {'localID': localID, 
                                                 'positionSymbol': positionSymbol, 
                                                 'responseOn': 'FORCECLEARPOSITION', 
                                                 'result': False, 
                                                 'message': f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Failed. 'Account Not Found'"},         
                               requestID = requestID, 
                               complete = True)
            return
        account = self.__accounts[localID]

        #[3]: Password Check
        if not(bcrypt.checkpw(password.encode(encoding = "utf-8"), account['hashedPassword'])):
            self.ipcA.sendFARR(targetProcess = 'GUI', 
                               functionResult = {'localID': localID, 
                                                 'positionSymbol': positionSymbol, 
                                                 'responseOn': 'FORCECLEARPOSITION', 
                                                 'result': False, 
                                                 'message': f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Failed. 'Incorrect Password'"},         
                               requestID = requestID, 
                               complete  = True)
            return
        
        #[4]: OCR Check
        position = account['positions'][positionSymbol]
        ocr      = position['_orderCreationRequest']
        if (ocr is not None):
            self.ipcA.sendFARR(targetProcess = 'GUI', 
                               functionResult = {'localID': localID, 
                                                 'positionSymbol': positionSymbol, 
                                                 'responseOn': 'FORCECLEARPOSITION', 
                                                 'result': False, 
                                                 'message': f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Failed. 'OCR Not Empty'"},              
                               requestID = requestID, 
                               complete = True)
            return
        
        #[5]: Quantity Check
        if ((position['quantity'] is None) or (position['quantity'] == 0)):
            self.ipcA.sendFARR(targetProcess = 'GUI', 
                               functionResult = {'localID': localID, 
                                                 'positionSymbol': positionSymbol, 
                                                 'responseOn': 'FORCECLEARPOSITION', 
                                                 'result': False, 
                                                 'message': f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Failed. 'Check The Quantity'"},         
                               requestID = requestID, 
                               complete = True)
            return
        
        #[6]: Force Clearing
        #---[6-1]: Side & Quantity Determination
        if   (position['quantity'] < 0): _side = 'BUY';  _quantity = -position['quantity']
        elif (0 < position['quantity']): _side = 'SELL'; _quantity =  position['quantity']
        #---[6-2]: Trade Control Update
        if   (position['quantity'] < 0): tcTracker_slExited = 'SHORT'
        elif (0 < position['quantity']): tcTracker_slExited = 'LONG'
        tcTracker = position['tradeControlTracker']
        kline_TS  = self.__currencies_lastKline[positionSymbol][KLINDEX_OPENTIME]
        tcTrackerUpdate = {'slExited': {'onComplete': (tcTracker_slExited, kline_TS), 
                                        'onPartial':  (tcTracker_slExited, kline_TS),  
                                        'onFail':     tcTracker['slExited']}}
        #---[6-3]: OCR Generation
        ocrGenResult = self.__orderCreationRequest_generate(localID         = localID, 
                                                            positionSymbol  = positionSymbol, 
                                                            logicSource     = 'FORCECLEAR', 
                                                            side            = _side,
                                                            quantity        = _quantity,
                                                            tcTrackerUpdate = tcTrackerUpdate,
                                                            ipcRID          = requestID)
        if (ocrGenResult == False):
            self.ipcA.sendFARR(targetProcess = 'GUI', 
                               functionResult = {'localID': localID, 
                                                 'positionSymbol': positionSymbol, 
                                                 'responseOn': 'FORCECLEARPOSITION', 
                                                 'result': False, 
                                                 'message': f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Failed. 'OCR Generation Rejected'"},         
                               requestID = requestID, 
                               complete = True)
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
        #[1]: Requester Check
        if (requester != 'GUI'): return

        #[2]: Account Check
        if (localID not in self.__accounts):
            return {'localID':        localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn':     'UPDATEPOSITIONTRADERPARAMS', 
                    'result':         False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'The Account Does Not Exist'"}
        account = self.__accounts[localID]
        
        #[3]: Position Check
        if (positionSymbol not in account['positions']):
            return {'localID':        localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn':     'UPDATEPOSITIONTRADERPARAMS', 
                    'result':         False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'The Position Does Not Exist'"}
        
        #[4]: Password Check
        if not(bcrypt.checkpw(password.encode(encoding = "utf-8"), account['hashedPassword'])):
            return {'localID':        localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn':     'UPDATEPOSITIONTRADERPARAMS', 
                    'result':         False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'Incorrect Password'"}
        
        #[5]: Quantity Check
        position = account['positions'][positionSymbol]
        if (position['quantity'] != 0):
            return {'localID': localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn': 'UPDATEPOSITIONTRADERPARAMS', 
                    'result': False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'Non-Zero Quantity'"}
        
        #[6]: Update
        position_prev = position.copy()
        assetName     = position['quoteAsset']
        asset         = account['assets'][assetName]
        asset_prev    = asset.copy()
        _toRequestDBUpdate = list()
        #---[6-1]: Currency Analysis Code
        if ((position['currencyAnalysisCode'] != newCurrencyAnalysisCode)):
            #New Parameter Validity Test
            if   (newCurrencyAnalysisCode == None):                    _testPassed = True
            elif (newCurrencyAnalysisCode in self.__currencyAnalysis): _testPassed = True
            else:                                                      _testPassed = False
            #Finally
            if (_testPassed == True):
                self.__registerPositionToCurrencyAnalysis(localID = localID, positionSymbol = positionSymbol, currencyAnalysisCode = newCurrencyAnalysisCode)
                _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'currencyAnalysisCode'), position['currencyAnalysisCode']))
        #---[6-2]: Trade Configuration Code
        if (position['tradeConfigurationCode'] != newTradeConfigurationCode):
            #New Parameter Validity Test
            if   (newTradeConfigurationCode == None):                       _testPassed = True
            elif (newTradeConfigurationCode in self.__tradeConfigurations): _testPassed = True
            else:                                                           _testPassed = False
            #Finally
            if (_testPassed == True):
                #Apply Change & Announce
                self.__registerPositionTradeConfiguration(localID = localID, positionSymbol = positionSymbol, tradeConfigurationCode = newTradeConfigurationCode)
                position['tradeControlTracker'] = self.__getInitializedTradeControlTracker()
                _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'tradeConfigurationCode'), position['tradeConfigurationCode']))
                _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'tradeControlTracker'),    self.__copyTradeControlTracker(position['tradeControlTracker'])))
        #---[6-3]: Priority
        if (position['priority'] != newPriority):
            #New Parameter Validity Test
            try:
                if ((1 <= newPriority) and (newPriority <= len(account['positions']))): _testPassed = True
                else:                                                                   _testPassed = False
            except:                                                                     _testPassed = False
            #Finally
            if (_testPassed == True):
                #Effected Positions
                priorityUpdatedPositions = list()
                if (position['priority'] < newPriority): 
                    _target = (position['priority']+1, newPriority)
                    for _pSymbol in account['positions']:
                        __position = account['positions'][_pSymbol]
                        if ((_target[0] <= __position['priority']) and (__position['priority'] <= _target[1])): __position['priority'] -= 1; priorityUpdatedPositions.append(_pSymbol)
                elif (newPriority < position['priority']): 
                    _target = (newPriority, position['priority']-1)
                    for _pSymbol in account['positions']:
                        __position = account['positions'][_pSymbol]
                        if ((_target[0] <= __position['priority']) and (__position['priority'] <= _target[1])): __position['priority'] += 1; priorityUpdatedPositions.append(_pSymbol)
                for _pSymbol in priorityUpdatedPositions:
                    self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', _pSymbol, 'priority'), prdContent = account['positions'][_pSymbol]['priority'])
                    self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, _pSymbol, 'priority')}, farrHandler = None)
                #Target Position
                position['priority'] = newPriority
                _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'priority'), position['priority']))
        #---[6-4]: Assumed Ratio
        if (position['assumedRatio'] != newAssumedRatio):
            #New Parameter Validity Test
            try:
                if (0 <= newAssumedRatio): _testPassed = True
                else:                      _testPassed = False
            except: _testPassed = False
            #Finally
            if (_testPassed == True): 
                position['assumedRatio'] = newAssumedRatio
                _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'assumedRatio'), position['assumedRatio']))
        #---[6-5]: Max Allocated Balance
        if (position['maxAllocatedBalance'] != newMaxAllocatedBalance):
            #New Parameter Validity Test
            try:
                if (0 <= newMaxAllocatedBalance): _testPassed = True
                else:                             _testPassed = False
            except: _testPassed = False
            #Finally
            if (_testPassed == True): 
                position['maxAllocatedBalance'] = newMaxAllocatedBalance
                _toRequestDBUpdate.append(((localID, 'positions', positionSymbol, 'maxAllocatedBalance'), position['maxAllocatedBalance']))

        #[7]: Tradability Check & MarginType and Leverage Update
        self.__checkPositionTradability(localID = localID, positionSymbol = positionSymbol)
        self.__requestMarginTypeAndLeverageUpdate(localID = localID, positionSymbol = positionSymbol) #If this needs to be done will be determined internally
        if (position['tradeConfigurationCode'] in self.__tradeConfigurations_loaded): position['weightedAssumedRatio'] = position['assumedRatio']*self.__tradeConfigurations_loaded[position['tradeConfigurationCode']]['config']['leverage']
        else:                                                                         position['weightedAssumedRatio'] = None
        
        #[8]: DB & GUI Annoucement
        if (0 < len(_toRequestDBUpdate)): self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'editAccountData', functionParams = {'updates': _toRequestDBUpdate}, farrHandler = None)
        for _dataName in position:
            if ((_dataName in _GUIANNOUCEMENT_POSITIONDATANAMES) and (position[_dataName] != position_prev[_dataName])): 
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol, _dataName), prdContent = position[_dataName])
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, positionSymbol, _dataName)}, farrHandler = None)
        for _dataName in asset:
            if ((_dataName in _GUIANNOUCEMENT_ASSETDATANAMES) and (asset[_dataName] != asset_prev[_dataName])): 
                self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', localID, 'assets', assetName, _dataName), prdContent = asset[_dataName])
                self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_ASSET', 'updatedContent': (localID, assetName, _dataName)}, farrHandler = None)
        
        #[9]: Result Return
        return {'localID':        localID, 
                'positionSymbol': positionSymbol, 
                'responseOn':     'UPDATEPOSITIONTRADERPARAMS', 
                'result':         True,  
                'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Successful!"}
    def __far_resetTradeControlTracker(self, requester, requestID, localID, password, positionSymbol):
        #[1]: Requester Check
        if (requester != 'GUI'): return

        #[2]: Account Check
        if (localID not in self.__accounts):
            return {'localID':        localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn':     'RESETTRADECONTROLTRACKER', 
                    'result':         False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'The Account Does Not Exist'"}
        account = self.__accounts[localID]
        
        #[3]: Position Check
        if (positionSymbol not in account['positions']):
            return {'localID':        localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn':     'RESETTRADECONTROLTRACKER', 
                    'result':         False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'The Position Does Not Exist'"}
        
        #[4]: Password Check
        if not(bcrypt.checkpw(password.encode(encoding = "utf-8"), account['hashedPassword'])):
            return {'localID':        localID, 
                    'positionSymbol': positionSymbol, 
                    'responseOn':     'RESETTRADECONTROLTRACKER', 
                    'result':         False, 
                    'message': f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'Incorrect Password'"}
        
        #[5]: Trade Control Reset (Run-time specific parameters are not reset)
        position = account['positions'][positionSymbol]
        tcTracker_prev = self.__copyTradeControlTracker(tradeControlTracker = position['tradeControlTracker'])
        tcTracker_new  = self.__getInitializedTradeControlTracker()
        tcTracker_new['rqpm_model']    = tcTracker_prev['rqpm_model'].copy()
        position['tradeControlTracker'] = tcTracker_new

        #[6]: Announcement
        tcTracker_copied = self.__copyTradeControlTracker(tradeControlTracker = position['tradeControlTracker'])
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                              prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol, 'tradeControlTracker'), 
                              prdContent = tcTracker_copied)
        self.ipcA.sendFAR(targetProcess  = 'GUI', 
                          functionID     = 'onAccountUpdate', 
                          functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (localID, positionSymbol, 'tradeControlTracker')}, 
                          farrHandler    = None)
        self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER',
                          functionID     = 'editAccountData',
                          functionParams = {'updates': [((localID, 'positions', positionSymbol, 'tradeControlTracker'), tcTracker_copied),]}, 
                          farrHandler    = None)
            
        #[7]: Result Return
        return {'localID':        localID, 
                'positionSymbol': positionSymbol, 
                'responseOn':     'RESETTRADECONTROLTRACKER', 
                'result':         True,
                'message': f"Account '{localID}' Position '{positionSymbol}' Trade Control Tracker Initialization Successful!"}
    def __far_verifyPassword(self, requester, requestID, localID, password):
        #[1]: Requester Check
        if (requester != 'GUI'): return

        #[2]: Account Check
        if (localID not in self.__accounts):
            return {'localID':         localID, 
                    'responseOn':      'VERIFYPASSWORD', 
                    'result':          False, 
                    'result_detailed': None,
                    'message': f"Account '{localID}' Password Verification Failed. 'The Account Does Not Exist'"}
        account = self.__accounts[localID]
        
        #[3]: Password Check
        ispasswordCorrect = bcrypt.checkpw(password.encode(encoding = "utf-8"), account['hashedPassword'])
        return {'localID':         localID,
                'responseOn':      'VERIFYPASSWORD', 
                'result':          True, 
                'result_detailed': {'isPasswordCorrect': ispasswordCorrect},
                'message': None}

    #<ANALYZER>
    def __far_onAnalyzerSummaryUpdate(self, requester, updatedSummary):
        if not requester.startswith('ANALYZER'):                 return
        if updatedSummary != 'averageAnalysisGenerationTime_ns': return
        analyzerIndex = int(requester[8:])
        aagt_ns = self.ipcA.getPRD(processName = requester, prdAddress = ('ANALYZERSUMMARY', 'averageAnalysisGenerationTime_ns'))
        self.__analyzers[analyzerIndex]['averageAnalysisGenerationTime_ns'] = aagt_ns
        self.__analyzers_central_recomputeAverageAnalysisGenerationTime = True
    def __far_onCurrencyAnalysisStatusUpdate(self, requester, currencyAnalysisCode, newStatus):
        if not requester.startswith('ANALYZER'): return
        if   newStatus == _CURRENCYANALYSIS_STATUS_WAITINGNEURALNETWORKCONNECTIONSDATA: newStatus = 'WAITINGNNCDATA'
        elif newStatus == _CURRENCYANALYSIS_STATUS_WAITINGSTREAM:                       newStatus = 'WAITINGSTREAM'
        elif newStatus == _CURRENCYANALYSIS_STATUS_WAITINGDATAAVAILABLE:                newStatus = 'WAITINGDATAAVAILABLE'
        elif newStatus == _CURRENCYANALYSIS_STATUS_PREPARING_QUEUED:                    newStatus = 'PREP_QUEUED'
        elif newStatus == _CURRENCYANALYSIS_STATUS_PREPARING_ANALYZINGKLINES:           newStatus = 'PREP_ANALYZINGKLINES'
        elif newStatus == _CURRENCYANALYSIS_STATUS_ANALYZINGREALTIME:                   newStatus = 'ANALYZINGREALTIME'
        elif newStatus == _CURRENCYANALYSIS_STATUS_ERROR:                               newStatus = 'ERROR'
        self.__currencyAnalysis[currencyAnalysisCode]['status'] = newStatus
        self.ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'status'), prdContent = self.__currencyAnalysis[currencyAnalysisCode]['status'])
        self.ipcA.sendFAR(targetProcess = 'GUI', functionID = 'onCurrencyAnalysisUpdate', functionParams = {'updateType': 'UPDATE_STATUS', 'currencyAnalysisCode': currencyAnalysisCode}, farrHandler = None)
        self.__analyzers_central_recomputeNumberOfCurrencyAnalysisByStatus = True
    def __far_onAnalysisGeneration(self, requester, currencyAnalysisCode, kline, linearizedAnalysis):
        #[1]: Requester Check
        if not requester.startswith('ANALYZER'): return

        #[2]: Currency Analysis Check
        if currencyAnalysisCode not in self.__currencyAnalysis:
            return
        ca                 = self.__currencyAnalysis[currencyAnalysisCode]
        ca_symbol          = ca['currencySymbol']
        ca_analysisResults = self.__currencyAnalysis_analysisResults[currencyAnalysisCode]

        #[2]: Expected Check
        received_klineTS = kline[KLINDEX_OPENTIME]
        received_kline   = kline
        if ca_analysisResults['lastReceived'] is not None:
            lr_klineTS = ca_analysisResults['lastReceived']
            #[2-1]: Timestamp Older
            if received_klineTS < lr_klineTS: 
                self.__logger(message = (f"An Analysis Result Older Than Expected Received From {currencyAnalysisCode}."
                                         f"\n * Symbol:        {ca_symbol}"
                                         f"\n * Last Received: {lr_klineTS}"
                                         f"\n * Received:      {received_klineTS}"),
                              logType = 'Warning', 
                              color   = 'light_red')
                return
            #[2-2]: Timestamp same
            if lr_klineTS == received_klineTS:
                self.__logger(message = (f"An Analysis Result On Already Closed Kline Received From {currencyAnalysisCode}."
                                         f"\n * Symbol:        {ca_symbol}"
                                         f"\n * Last Received: {lr_klineTS}"
                                         f"\n * Received:      {received_klineTS}"),
                              logType = 'Warning', 
                              color   = 'light_red')
                return
            #[2-3]: Timestamp newer, and skipped expected
            klineTS_expected = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = lr_klineTS, mrktReg = self.__currencies[ca['currencySymbol']]['kline_firstOpenTS'], nTicks = 1)
            if (klineTS_expected < received_klineTS):
                self.__logger(message = (f"An Analysis Result Loss Detected From {currencyAnalysisCode}."
                                         f"\n * Symbol:        {ca_symbol}"
                                         f"\n * Last Received: {lr_klineTS}"
                                         f"\n * Received:      {received_klineTS}"),
                              logType = 'Warning', 
                              color   = 'light_red')
        ca_analysisResults['lastReceived'] = received_klineTS
        
        #[3]: Analysis Result Save
        ca_ar_data                = ca_analysisResults['data']
        ca_ar_timestamps          = ca_analysisResults['timestamps']
        ca_ar_timestamps_handling = ca_analysisResults['timestamps_handling']
        if (received_klineTS not in ca_ar_data): ca_ar_timestamps.append(received_klineTS)
        ca_ar_data[received_klineTS] = (linearizedAnalysis, received_kline)

        #[4]: Expired Analysis Results Handling
        ca_ar_timestamps_handling[received_klineTS] = set()
        while (86400*90/KLINTERVAL_S) < len(ca_ar_timestamps): #90 days worth
            rtTS = ca_ar_timestamps[0]
            if rtTS == received_klineTS:          break
            if (ca_ar_timestamps_handling[rtTS]): break
            ca_ar_timestamps.popleft()
            del ca_ar_data[rtTS]
            del ca_ar_timestamps_handling[rtTS]
        #---Forceful removal to avoid memory leak
        while (86400*365*2/KLINTERVAL_S) < len(ca_ar_timestamps): #2 years worth
            rtTS = ca_ar_timestamps.popleft()
            del ca_ar_data[rtTS]
            del ca_ar_timestamps_handling[rtTS]
            self.__logger(message = (f"A Stored Analysis Result Forcefully Removed To Avoid Memory Leak {currencyAnalysisCode}."
                                     f"\n * Currency Analysis: {currencyAnalysisCode}"
                                     f"\n * Symbol:            {ca_symbol}"
                                     f"\n * Timestamp:         {rtTS}"),
                          logType = 'Warning', 
                          color   = 'light_red')

        #[5]: Account Queue Appending
        for localID in ca['appliedAccounts']:
            #[2-1]: Account Check
            if (localID not in self.__accounts): 
                self.__logger(message = (f"A Analysis Result For A Non-Existing Account '{localID}' Received From '{requester}'."
                                         f"\n * Timestamp: {received_klineTS}"
                                         f"\n * Symbol:    {ca_symbol}"),
                              logType = 'Warning', 
                              color   = 'light_red')
                continue
            account = self.__accounts[localID]
            #[2-2]: Position Currency Analysis Code Check
            position        = account['positions'][ca_symbol]
            position_caCode = position['currencyAnalysisCode']
            if (position_caCode != currencyAnalysisCode):
                self.__logger(message = (f"A Analysis Result Received From '{requester}' Detected Currency Analysis Code Mismatch."
                                         f"\n * Timestamp:                       {received_klineTS}"
                                         f"\n * Symbol:                          {ca_symbol}"
                                         f"\n * LocalID:                         {localID}"
                                         f"\n * Position Currency Analysis Code: {position_caCode}"
                                         f"\n * Received Currency Analysis Code: {currencyAnalysisCode}"),
                              logType = 'Warning', 
                              color   = 'light_red')
                continue
            #[2-3]: Queue Appending
            position['_analysisHandling_Queue'].append(received_klineTS)
            #[2-4]: Handling Flag Raise
            ca_ar_timestamps_handling[received_klineTS].add(localID)

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
                    if ((_position['quantity'] is not None) and (_position['quantity'] != 0)): self.__trade_checkConditionalExits(localID = _localID, positionSymbol = symbol, kline = kline, kline_closed = closed)
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
                self.__updateAccountPeriodicReport(localID = localID, importedData = None)
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