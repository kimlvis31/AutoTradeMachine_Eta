#ATM Modules
import constants
from managers.workers.trade_manager.account_virtual_server import VirtualAccount


#Python Modules
import time
import termcolor
from datetime    import datetime
from collections import deque

#Constants
KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S

_PROCESS_INTERVAL_NS = 100e9

class VirtualServer:
    #Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, tmConfig, currencies, currencies_lastKline):
        #[1]: System
        self.__tmConfig             = tmConfig
        self.__currencies           = currencies
        self.__currencies_lastKline = currencies_lastKline

        #[2]: Accounts
        self.__accounts = dict()

        #[3]: Request Results
        self.__positionControlRequestResponses = deque()

        #[4]: Process Control
        self.__processed_last_ns = 0
    #Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    
    
    #Internal Handlers ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __logger(self, message, logType, color):
        if not self.__tmConfig[f'print_{logType}']:
            return
        time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
        msg      = f"[TRADEMANAGER-VIRTUALSERVER-{time_str}] {message}"
        print(termcolor.colored(msg, color))
    #Internal Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    
    #External Handlers ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def process(self):
        #[1]: Process Virtual Accounts
        t_current_ns = time.perf_counter_ns()
        if _PROCESS_INTERVAL_NS <= t_current_ns-self.__processed_last_ns:
            #[1-1]: Process Accounts & Get Position Control Request Responses
            for vAccount in self.__accounts.values():
                self.__positionControlRequestResponses.extend(vAccount.process())

            #[1-2]: Update Process Timer
            self.__processed_last_ns = t_current_ns

    def onNewCurrency(self, symbol):
        #[1]: Accounts Response
        for vAccount in self.__accounts.values():
            vAccount.onNewCurrency(symbol = symbol)

    def getPositionControlRequestResponses(self):
        #[1]: Buffer Copy
        pcrrs = self.__positionControlRequestResponses.copy()

        #[2]: Buffer Clearing
        self.__positionControlRequestResponses.clear()

        #[3]: Return
        return pcrrs

    def getAccount(self, localID):
        #[1]: Account Check
        vAccount = self.__accounts.get(localID, None)
        if vAccount is None:
            return
        
        #[2]: Return Account Instance
        return vAccount
    
    def addAccount(self, localID, assets, positions):
        #[1]: Account ID Check
        accounts = self.__accounts
        if localID in accounts:
            self.__logger(message = (f"A Virtual Account Could Not Be Added To The Virtual Server. Local ID Already Exists.\n"
                                     f" * Local ID: {localID}"), 
                          logType = 'Warning',
                          color   = 'light_red')
            return
        
        #[2]: Account Generation
        vAccount = VirtualAccount(tmConfig             = self.__tmConfig,
                                  currencies           = self.__currencies,
                                  currencies_lastKline = self.__currencies_lastKline,
                                  localID              = localID,
                                  assets               = assets,
                                  positions            = positions)
        accounts[localID] = vAccount

    def removeAccount(self, localID):
        #[1]: Account Check
        vAccount = self.__accounts.get(localID, None)
        if vAccount is None:
            self.__logger(message = (f"A Virtual Account Could Not Be Removed To The Virtual Server. Account Not Found.\n"
                                     f" * Local ID: {localID}"), 
                          logType = 'Warning',
                          color   = 'light_red')
            return
        
        #[2]: Account Removal
        del self.__accounts[localID]

    def onNewPosition(self, symbol, position):
        #[1]: Virtual Accounts Update
        for vAccount in self.__accounts.values():
            vAccount.onNewPosition(symbol = symbol, position = position)

    def transferBalance(self, localID, assetName, amount):
        #[1]: Account Check
        vAccount = self.__accounts.get(localID, None)
        if vAccount is None:
            self.__logger(message = (f"A Virtual Account Could Not Be Added To The Virtual Server. Account Not Found.\n"
                                     f" * Local ID: {localID}"), 
                          logType = 'Warning',
                          color   = 'light_red')
            return

        #[2]: Balance Transfer Request
        vAccount.transferBalance(assetName = assetName, amount = amount)

    def updateMarginType(self, localID, symbol, marginType):
        #[1]: Account Check
        vAccount = self.__accounts.get(localID, None)
        if vAccount is None:
            self.__logger(message = (f"A Virtual Account Margin Type Could Not Be Updated. Account Not Found.\n"
                                     f" * Local ID: {localID}"), 
                          logType = 'Warning',
                          color   = 'light_red')
            return None
        
        #[2]: Margin Type Update Request
        rID = vAccount.updateMarginType(symbol = symbol, marginType = marginType)

        #[3]: Return RID
        return rID

    def updateLeverage(self, localID, symbol, leverage):
        #[1]: Account Check
        vAccount = self.__accounts.get(localID, None)
        if vAccount is None:
            self.__logger(message = (f"A Virtual Account Leverage Could Not Be Updated. Account Not Found.\n"
                                     f" * Local ID: {localID}"), 
                          logType = 'Warning',
                          color   = 'light_red')
            return None
        
        #[2]: Leverage Update Request
        rID = vAccount.updateLeverage(symbol = symbol, leverage = leverage)

        #[3]: Return RID
        return rID

    def createOrder(self, localID, symbol, orderParams):
        #[1]: Account Check
        vAccount = self.__accounts.get(localID, None)
        if vAccount is None:
            self.__logger(message = (f"A Virtual Account Could Not Create Order. Account Not Found.\n"
                                     f" * Local ID: {localID}"), 
                          logType = 'Warning',
                          color   = 'light_red')
            return None
        
        #[2]: Order Creation Request
        rID = vAccount.createOrder(symbol = symbol, orderParams = orderParams)

        #[3]: Return 
        return rID
    #External Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------