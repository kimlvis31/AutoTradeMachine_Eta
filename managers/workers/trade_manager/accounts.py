#ATM Modules
import ipc
import constants
from managers.workers.trade_manager.account import Account

#Python Modules
import time
import termcolor
import bcrypt
import traceback
from datetime import datetime

#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT

KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S

_VIRTUALACCOUNTS_UPDATE_INTERVAL_NS = 200e6

class Accounts:
    #Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, ipcA, tmConfig, currencies, currencies_lastKline, virtualServer, currencyAnalyses, tradeConfigurations):
        #[1]: System
        self.__ipcA                 = ipcA
        self.__tmConfig             = tmConfig
        self.__currencies           = currencies
        self.__currencies_lastKline = currencies_lastKline
        self.__virtualServer        = virtualServer
        self.__currencyAnalyses     = currencyAnalyses
        self.__tradeConfigurations  = tradeConfigurations

        #[2]: Accounts
        self.__accounts                       = dict()
        self.__activating                     = dict()
        self.__virtualAccounts_lastUpdated_ns = 0
        
        #[3]: FAR Handlers
        ipcA.addFARHandler('addAccount',                 self.__far_addAccount,                 executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        ipcA.addFARHandler('removeAccount',              self.__far_removeAccount,              executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        ipcA.addFARHandler('activateAccount',            self.__far_activateAccount,            executionThread = _IPC_THREADTYPE_MT, immediateResponse = False) #GUI
        ipcA.addFARHandler('deactivateAccount',          self.__far_deactivateAccount,          executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        ipcA.addFARHandler('setAccountTradeStatus',      self.__far_setAccountTradeStatus,      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        ipcA.addFARHandler('transferBalance',            self.__far_transferBalance,            executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        ipcA.addFARHandler('updateAllocationRatio',      self.__far_updateAllocationRatio,      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        ipcA.addFARHandler('forceClearPosition',         self.__far_forceClearPosition,         executionThread = _IPC_THREADTYPE_MT, immediateResponse = False) #GUI
        ipcA.addFARHandler('updatePositionTradeStatus',  self.__far_updatePositionTradeStatus,  executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        ipcA.addFARHandler('updatePositionReduceOnly',   self.__far_updatePositionReduceOnly,   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        ipcA.addFARHandler('updatePositionTraderParams', self.__far_updatePositionTraderParams, executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        ipcA.addFARHandler('resetTradeControlTracker',   self.__far_resetTradeControlTracker,   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        ipcA.addFARHandler('verifyPassword',             self.__far_verifyPassword,             executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #GUI
        ipcA.addFARHandler('onAccountDataReceival',      self.__far_onAccountDataReceival,      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)  #BINANCEAPI
        
        #[4]: Request Account Data & Announce For Initial PRD Formatting
        ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                     functionID     = 'loadAccountDescriptions',
                     functionParams = None, 
                     farrHandler    = self.__farr_onAccountDescriptionsLoadRequestResponse)
        ipcA.sendPRDEDIT(targetProcess = 'GUI', prdAddress = 'ACCOUNTS', prdContent = dict())
    #Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    #IPC Handlers ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __farr_onAccountDescriptionsLoadRequestResponse(self, responder, requestID, functionResult):
        #[1]: Source Check
        if responder != 'DATAMANAGER':
            return

        #[2]: Descriptions Read
        ads     = functionResult
        func_ac = self.__addAccount
        for lID, ad in ads.items():
            func_ac(localID            = lID, 
                    buid               = ad['buid'],
                    accountType        = ad['accountType'],
                    password           = ad['hashedPassword'],
                    assets             = ad['assets'],
                    positions          = ad['positions'],
                    lastPeriodicReport = ad['lastPeriodicReport'],
                    isImport           = True)
            
    def __far_onAccountDataReceival(self, requester, localID, accountData):
        #[1]: Source Check
        if requester != 'BINANCEAPI':
            return
        
        #[2]: Account Check
        account = self.__accounts.get(localID, None)
        if account is None:
            return
        
        #[3]: Account Update
        account.update(assets    = accountData['assets'], 
                       positions = accountData['positions'])

    def __far_addAccount(self, requester, requestID, localID, buid, accountType, password):
        #[1]: Source Check
        if requester != 'GUI':
            return {'localID':    localID, 
                    'responseOn': 'ADDACCOUNT', 
                    'result':     False, 
                    'message':    'INVALIDREQUESTER'}

        #[2]: Account Add
        result = self.__addAccount(localID            = localID, 
                                   buid               = buid, 
                                   accountType        = accountType, 
                                   password           = password,
                                   assets             = None,
                                   positions          = None,
                                   lastPeriodicReport = None, 
                                   isImport           = False)
        
        #[3]: Result Handling
        if result['result']:
            return {'localID':    localID, 
                    'responseOn': 'ADDACCOUNT', 
                    'result':     True, 
                    'message':    f"Account '{localID}' Add Successful!"}
        else:
            return {'localID':    localID, 
                    'responseOn': 'ADDACCOUNT', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Add Failed! '{result['message']}'"}
    
    def __far_removeAccount(self, requester, requestID, localID, password):
        #[1]: Source Check
        if requester != 'GUI':
            return {'localID':    localID, 
                    'responseOn': 'REMOVEACCOUNT', 
                    'result':     False, 
                    'message':    'INVALIDREQUESTER'}
        
        #[2]: Account Check
        account = self.__accounts.get(localID, None)
        if account is None:
            return {'localID':    localID, 
                    'responseOn': 'REMOVEACCOUNT', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Removal Failed. 'Account Not Found'"}
        isVirtual = account.isVirtual()

        #[3]: Account Removal Attempt
        result = account.remove(password = password)

        #[4]: Result Handling
        #---[4-1]: Account Removed
        if result['result']:
            #[4-1-1]: Instance Removal
            del self.__accounts[localID]
            if isVirtual:
                self.__virtualServer.removeAccount(localID = localID)
            #[4-1-2]: Announcement
            self.__ipcA.sendPRDREMOVE(targetProcess = 'GUI', 
                                      prdAddress    = ('ACCOUNTS', localID))
            self.__ipcA.sendFAR(targetProcess  = 'GUI', 
                                functionID     = 'onAccountUpdate', 
                                functionParams = {'updateType':     'REMOVED', 
                                                  'updatedContent': localID}, 
                                farrHandler    = None)
            #[4-1-3]: Result Return
            return {'localID':    localID, 
                    'responseOn': 'REMOVEACCOUNT', 
                    'result':     True, 
                    'message':    f"Account '{localID}' Removal Succcessful!"}
        #---[4-2]: Account Not Removed
        else:
            return {'localID':    localID, 
                    'responseOn': 'REMOVEACCOUNT', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Removal Failed! '{result['message']}'"}
    
    def __far_verifyPassword(self, requester, requestID, localID, password):
        #[1]: Source Check
        if requester != 'GUI':
            return {'localID':    localID, 
                    'responseOn': 'VERIFYPASSWORD', 
                    'result':     False, 
                    'message':    'INVALIDREQUESTER'}
        
        #[2]: Account Check
        account = self.__accounts.get(localID, None)
        if account is None:
            return {'localID':    localID, 
                    'responseOn': 'VERIFYPASSWORD', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Password Verification Failed. 'Account Not Found'"}
        
        #[3]: Password Check
        isValid = account.verifyPassword(password = password)

        #[4]: Result Return
        return {'localID':         localID,
                'responseOn':      'VERIFYPASSWORD', 
                'result':          True, 
                'result_detailed': {'isPasswordCorrect': isValid},
                'message': None}
    
    def __far_activateAccount(self, requester, requestID, localID, password, apiKey, secretKey, encrypted):
        #[1]: Source Check
        if requester != 'GUI':
            return {'localID':    localID, 
                    'responseOn': 'ACTIVATEACCOUNT', 
                    'result':     False, 
                    'message':    'INVALIDREQUESTER'}
        
        #[2]: Account Check
        account = self.__accounts.get(localID, None)
        if account is None:
            return {'localID':    localID, 
                    'responseOn': 'ACTIVATEACCOUNT', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Activation Failed. 'Account Not Found'"}
        
        #[3]: Activation Attempt & Tracker Update
        result = account.activate(password  = password,
                                  apiKey    = apiKey,
                                  secretKey = secretKey,
                                  encrypted = encrypted)
        
        #[4]: Result Handling
        if not result['result']:
            return {'localID':    localID, 
                    'responseOn': 'ACTIVATEACCOUNT', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Activation Failed. '{result['message']}'"}
        self.__activating[localID] = requestID
    
    def __far_deactivateAccount(self, requester, requestID, localID, password):
        #[1]: Source Check
        if requester != 'GUI':
            return {'localID':    localID, 
                    'responseOn': 'DEACTIVATEACCOUNT', 
                    'result':     False, 
                    'message':    'INVALIDREQUESTER'}
        
        #[2]: Account Check
        account = self.__accounts.get(localID, None)
        if account is None:
            return {'localID':    localID, 
                    'responseOn': 'DEACTIVATEACCOUNT', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Deactivation Failed. 'Account Not Found'"}
        
        #[3]: Deactivation
        result = account.deactivate(password = password)

        #[4]: Result Handling
        if result['result']:
            return {'localID':    localID, 
                    'responseOn': 'DEACTIVATEACCOUNT', 
                    'result':     True, 
                    'message':    f"Account '{localID}' Deactivation Successful!"}
        else:
            return {'localID':    localID, 
                    'responseOn': 'DEACTIVATEACCOUNT', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Deactivation Failed. '{result['message']}'"}
    
    def __far_setAccountTradeStatus(self, requester, requestID, localID, password, newStatus):
        #[1]: Source Check
        if requester != 'GUI':
            return {'localID':    localID, 
                    'responseOn': 'SETACCOUNTTRADESTATUS', 
                    'result':     False, 
                    'message':    'INVALIDREQUESTER'}
        
        #[2]: Account Check
        account = self.__accounts.get(localID, None)
        if account is None:
            return {'localID':    localID, 
                    'responseOn': 'SETACCOUNTTRADESTATUS', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Trade Status Update Failed. 'Account Not Found'"}

        #[3]: Update
        result = account.setAccountTradeStatus(password  = password, 
                                               newStatus = newStatus)

        #[4]: Result Handling
        if result['result']:
            return {'localID':    localID, 
                    'responseOn': 'SETACCOUNTTRADESTATUS', 
                    'result':     True, 
                    'message':    f"Account '{localID}' Trade Status Update Successful!"}
        else:
            return {'localID':    localID, 
                    'responseOn': 'SETACCOUNTTRADESTATUS', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Trade Status Update Failed. '{result['message']}'"}
    
    def __far_transferBalance(self, requester, requestID, localID, password, asset, amount):
        #[1]: Source Check
        if requester != 'GUI':
            return {'localID':    localID, 
                    'responseOn': 'BALANCETRANSFER', 
                    'result':     False, 
                    'message':    'INVALIDREQUESTER'}
        
        #[2]: Account Check
        account = self.__accounts.get(localID, None)
        if account is None:
            return {'localID':    localID, 
                    'responseOn': 'BALANCETRANSFER', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Balance Transfer Failed. 'Account Not Found'"}

        #[3]: Update
        result = account.transferBalance(password  = password, 
                                         assetName = asset, 
                                         amount    = amount)

        #[4]: Result Handling
        if result['result']:
            return {'localID':    localID, 
                    'responseOn': 'BALANCETRANSFER', 
                    'result':     True, 
                    'message':    f"Account '{localID}' Balance Transfer Successful!"}
        else:
            return {'localID':    localID, 
                    'responseOn': 'BALANCETRANSFER', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Balance Transfer Failed. '{result['message']}'"}
    
    def __far_updateAllocationRatio(self, requester, requestID, localID, password, asset, newAllocationRatio):
        #[1]: Source Check
        if requester != 'GUI':
            return {'localID':    localID, 
                    'responseOn': 'ALLOCATIONRATIOUPDATE', 
                    'result':     False, 
                    'message':    'INVALIDREQUESTER'}
        
        #[2]: Account Check
        account = self.__accounts.get(localID, None)
        if account is None:
            return {'localID':    localID, 
                    'responseOn': 'ALLOCATIONRATIOUPDATE', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Allocation Ratio Update Failed. 'Account Not Found'"}

        #[3]: Update
        result = account.updateAllocationRatio(password           = password, 
                                               assetName          = asset, 
                                               newAllocationRatio = newAllocationRatio)

        #[4]: Result Handling
        if result['result']:
            return {'localID':    localID, 
                    'responseOn': 'ALLOCATIONRATIOUPDATE', 
                    'result':     True, 
                    'message':    f"Account '{localID}' Allocation Ratio Update Successful!"}
        else:
            return {'localID':    localID, 
                    'responseOn': 'ALLOCATIONRATIOUPDATE', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Allocation Ratio Update Failed. '{result['message']}'"}
    
    def __far_forceClearPosition(self, requester, requestID, localID, password, positionSymbol):
        #[1]: Source Check
        if requester != 'GUI':
            self.__ipcA.sendFARR(targetProcess  = requester, 
                                 functionResult = {'localID':        localID, 
                                                   'positionSymbol': positionSymbol, 
                                                   'responseOn':     'FORCECLEARPOSITION', 
                                                   'result':         False, 
                                                   'message':        "INVALIDREQUESTER"},         
                                 requestID      = requestID, 
                                 complete       = True)
            return
        
        #[2]: Account Check
        account = self.__accounts.get(localID, None)
        if account is None:
            self.__ipcA.sendFARR(targetProcess  = "GUI", 
                                 functionResult = {'localID':        localID, 
                                                   'positionSymbol': positionSymbol, 
                                                   'responseOn':     'FORCECLEARPOSITION', 
                                                   'result':         False, 
                                                   'message':        f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Failed. 'Account Not Found'"},         
                                 requestID      = requestID,
                                 complete       = True)
            return

        #[3]: Update
        result = account.forceClearPosition(password  = password, 
                                            symbol    = positionSymbol, 
                                            requestID = requestID)

        #[4]: Result Handling
        if not result['result']:
            self.__ipcA.sendFARR(targetProcess  = "GUI", 
                                 functionResult = {'localID':        localID, 
                                                   'positionSymbol': positionSymbol, 
                                                   'responseOn':     'FORCECLEARPOSITION', 
                                                   'result':         False, 
                                                   'message':        f"Account '{localID}' Position '{positionSymbol}' Position Force Clear Failed. '{result['message']}'"},         
                                 requestID      = requestID,
                                 complete       = True)
    
    def __far_updatePositionTradeStatus(self, requester, requestID, localID, password, positionSymbol, newTradeStatus):
        #[1]: Source Check
        if requester != 'GUI':
            return {'localID':    localID, 
                    'responseOn': 'UPDATEPOSITIONTRADESTATUS', 
                    'result':     False, 
                    'message':    'INVALIDREQUESTER'}
        
        #[2]: Account Check
        account = self.__accounts.get(localID, None)
        if account is None:
            return {'localID':    localID, 
                    'responseOn': 'UPDATEPOSITIONTRADESTATUS', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Position '{positionSymbol}' Trade Status Update Failed. 'Account Not Found'"}

        #[3]: Update
        result = account.updatePositionTradeStatus(password       = password, 
                                                   symbol         = positionSymbol, 
                                                   newTradeStatus = newTradeStatus)

        #[4]: Result Handling
        if result['result']:
            return {'localID':    localID, 
                    'responseOn': 'UPDATEPOSITIONTRADESTATUS', 
                    'result':     True, 
                    'message':    f"Account '{localID}' Position '{positionSymbol}' Trade Status Update Successful!"}
        else:
            return {'localID':    localID, 
                    'responseOn': 'UPDATEPOSITIONTRADESTATUS', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Position '{positionSymbol}' Trade Status Update Failed. '{result['message']}'"}
    
    def __far_updatePositionReduceOnly(self, requester, requestID, localID, password, positionSymbol, newReduceOnly):
        #[1]: Source Check
        if requester != 'GUI':
            return {'localID':    localID, 
                    'responseOn': 'UPDATEPOSITIONREDUCEONLY', 
                    'result':     False, 
                    'message':    'INVALIDREQUESTER'}
        
        #[2]: Account Check
        account = self.__accounts.get(localID, None)
        if account is None:
            return {'localID':    localID, 
                    'responseOn': 'UPDATEPOSITIONREDUCEONLY', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Position '{positionSymbol}' Reduce-Only Update Failed. 'Account Not Found'"}

        #[3]: Update
        result = account.updatePositionReduceOnly(password      = password, 
                                                  symbol        = positionSymbol, 
                                                  newReduceOnly = newReduceOnly)

        #[4]: Result Handling
        if result['result']:
            return {'localID':    localID, 
                    'responseOn': 'UPDATEPOSITIONREDUCEONLY', 
                    'result':     True, 
                    'message':    f"Account '{localID}' Position '{positionSymbol}' Reduce-Only Update Successful!"}
        else:
            return {'localID':    localID, 
                    'responseOn': 'UPDATEPOSITIONREDUCEONLY', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Position '{positionSymbol}' Reduce-Only Update Failed. '{result['message']}'"}
    
    def __far_updatePositionTraderParams(self, requester, requestID, localID, password, positionSymbol, newCurrencyAnalysisCode, newTradeConfigurationCode, newPriority, newAssumedRatio, newMaxAllocatedBalance):
        #[1]: Source Check
        if requester != 'GUI':
            return {'localID':    localID, 
                    'responseOn': 'UPDATEPOSITIONTRADERPARAMS', 
                    'result':     False, 
                    'message':    'INVALIDREQUESTER'}
        
        #[2]: Account Check
        account = self.__accounts.get(localID, None)
        if account is None:
            return {'localID':    localID, 
                    'responseOn': 'UPDATEPOSITIONTRADERPARAMS', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. 'Account Not Found'"}

        #[3]: Update
        result = account.updatePositionTraderParams(password                  = password, 
                                                    symbol                    = positionSymbol, 
                                                    newCurrencyAnalysisCode   = newCurrencyAnalysisCode, 
                                                    newTradeConfigurationCode = newTradeConfigurationCode, 
                                                    newPriority               = newPriority, 
                                                    newAssumedRatio           = newAssumedRatio, 
                                                    newMaxAllocatedBalance    = newMaxAllocatedBalance)

        #[4]: Result Handling
        if result['result']:
            return {'localID':    localID, 
                    'responseOn': 'UPDATEPOSITIONTRADERPARAMS', 
                    'result':     True, 
                    'message':    f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Successful!"}
        else:
            return {'localID':    localID, 
                    'responseOn': 'UPDATEPOSITIONTRADERPARAMS', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Position '{positionSymbol}' Trader Params Update Failed. '{result['message']}'"}
    
    def __far_resetTradeControlTracker(self, requester, requestID, localID, password, positionSymbol):
        #[1]: Source Check
        if requester != 'GUI':
            return {'localID':    localID, 
                    'responseOn': 'RESETTRADECONTROLTRACKER', 
                    'result':     False, 
                    'message':    'INVALIDREQUESTER'}
        
        #[2]: Account Check
        account = self.__accounts.get(localID, None)
        if account is None:
            return {'localID':    localID, 
                    'responseOn': 'RESETTRADECONTROLTRACKER', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Position '{positionSymbol}' Trade Control Tracker Reset Failed. 'Account Not Found'"}

        #[3]: Update
        result = account.resetTradeControlTracker(password = password, 
                                                  symbol   = positionSymbol)

        #[4]: Result Handling
        if result['result']:
            return {'localID':    localID, 
                    'responseOn': 'RESETTRADECONTROLTRACKER', 
                    'result':     True, 
                    'message':    f"Account '{localID}' Position '{positionSymbol}' Trade Control Tracker Reset Successful!"}
        else:
            return {'localID':    localID, 
                    'responseOn': 'RESETTRADECONTROLTRACKER', 
                    'result':     False, 
                    'message':    f"Account '{localID}' Position '{positionSymbol}' Trade Control Tracker Reset Failed. '{result['message']}'"}
    #IPC Handlers END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




    
    #Internal Handlers ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __addAccount(self, localID, buid, accountType, password, assets = None, positions = None, lastPeriodicReport = None, isImport = True):
        #[1]: ID Check
        if localID is None or localID in self.__accounts:
            self.__logger(message = f"Account '{localID}' Add Failed. 'Check Account Name'",
                          logType = 'Warning', 
                          color   = 'light_red')
            return {'result':  False, 
                    'message': "Check Account Name"}

        #[2]: Account Generation
        try:
            #[2-1]: Instance Generation
            account = Account(ipcA                 = self.__ipcA, 
                              tmConfig             = self.__tmConfig, 
                              currencies           = self.__currencies, 
                              currencies_lastKline = self.__currencies_lastKline, 
                              virtualServer        = self.__virtualServer,
                              currencyAnalyses     = self.__currencyAnalyses,
                              tradeConfigurations  = self.__tradeConfigurations,
                              localID              = localID,
                              accountType          = accountType,
                              buid                 = buid,
                              hashedPassword       = password if isImport else bcrypt.hashpw(password=password.encode(encoding = "utf-8"), salt=bcrypt.gensalt()),
                              assets               = assets,
                              positions            = positions,
                              lastPeriodicReport   = lastPeriodicReport)
            self.__accounts[localID] = account
            
            #[2-2]: Virtual Account Registration
            if account.isVirtual():
                self.__virtualServer.addAccount(localID   = localID,
                                                assets    = assets,
                                                positions = positions)

            #[2-3]: If This Is A New Account, Dispatch Account Description Save Request & Announce Via PRD and FAR
            accountDescription = account.getAccountDescription()
            self.__ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                                    prdAddress    = ('ACCOUNTS', localID), 
                                    prdContent    = accountDescription)
            if not isImport: 
                self.__ipcA.sendFAR(targetProcess  = 'GUI', 
                                    functionID     = 'onAccountUpdate', 
                                    functionParams = {'updateType': 'ADDED', 'updatedContent': localID}, 
                                    farrHandler    = None)

        #[3]: Exception Handling
        except Exception as e: 
            self.__logger(message = (f"An Account Add Failed Due To An Unexpected Error.\n"
                                     f" * Local ID:       {localID}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"), 
                          logType = 'Error',
                          color   = 'light_red')
            return {'result':  False, 
                    'message': f"{str(e)}"}
        
        #[4]: Result Return
        return {'result':  True,  
                'message': None}
    
    def __logger(self, message, logType, color):
        if not self.__tmConfig[f'print_{logType}']:
            return
        time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
        msg      = f"[TRADEMANAGER-ACCOUNTSWORKER-{time_str}] {message}"
        print(termcolor.colored(msg, color))
    #Internal Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #External Handlers ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def process(self):
        #[1]: Instances
        vs         = self.__virtualServer
        accounts   = self.__accounts
        activating = self.__activating
        func_sendFARR = self.__ipcA.sendFARR

        #[2]: Actual Accounts Activation Check
        cleared = []
        for lID, requestID in activating.items():
            #[2-1]: Result Check
            aResult = accounts[lID].getActivationResult()
            if aResult is None:
                continue
            #[2-2]: Response Dispatch
            result = aResult['result']
            msg    = aResult['message']
            if result: msg = f"Account '{lID}' Activation Successful!"
            else:      msg = f"Account '{lID}' Activation Failed. '{msg}'"
            func_sendFARR(targetProcess  = 'GUI', 
                          functionResult = {'localID':    lID, 
                                            'responseOn': 'ACTIVATEACCOUNT', 
                                            'result':     result, 
                                            'message':    msg}, 
                          requestID      = requestID, 
                          complete       = True)
            #[2-3]: Cleared IDs Collection
            cleared.append(lID)
        #---[2-4]: Tracker Update
        for lID in cleared:
            del self.__activating[lID]

        #[3]: Virtual Accounts Update
        t_current_ns = time.perf_counter_ns()
        if _VIRTUALACCOUNTS_UPDATE_INTERVAL_NS <= t_current_ns-self.__virtualAccounts_lastUpdated_ns:
            #[3-1]: Position Control Request Responses
            for fr, rID in vs.getPositionControlRequestResponses():
                account = accounts.get(fr['localID'], None)
                if account is None:
                    continue
                account.onPositionControlRequestsResponse(functionResult = fr, requestID = rID)

            #[3-2]: Accounts Update
            for lID, account in accounts.items():
                #[3-2-1]: Type Check
                if not account.isVirtual():
                    continue

                #[3-2-2]: Virtual Server Account
                account_vs = vs.getAccount(localID = lID)

                #[3-2-3]: Account Data Update
                account.update(assets    = account_vs.getAssets(), 
                               positions = account_vs.getPositions())
                
            #[3-3]: Timer Update
            self.__virtualAccounts_lastUpdated_ns = t_current_ns
    
    def onNewCurrency(self, symbol):
        #[1]: Accounts Response
        for account in self.__accounts.values():
            account.onNewCurrency(symbol = symbol)

    def onKlineStreamReceival(self, symbol, kline):
        #[1]: Accounts Response
        for account in self.__accounts.values():
            account.onKlineStreamReceival(symbol = symbol, kline = kline)
                
    def onTradeConfigurationAdd(self, tradeConfigurationCode):
        #[1]: Accounts Response
        for account in self.__accounts.values():
            account.onTradeConfigurationAdd(tradeConfigurationCode = tradeConfigurationCode)

    def onCurrencyAnalysisAdd(self, currencyAnalysisCode):
        #[1]: Accounts Response
        for account in self.__accounts.values():
            account.onCurrencyAnalysisAdd(currencyAnalysisCode = currencyAnalysisCode)
    #External Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------