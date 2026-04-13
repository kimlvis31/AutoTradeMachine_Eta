#ATM Modules
from analyzers import KLINDEX_OPENTIME, KLINDEX_CLOSETIME, KLINDEX_OPENPRICE, KLINDEX_CLOSEPRICE, KLINDEX_HIGHPRICE, KLINDEX_LOWPRICE, KLINDEX_CLOSED
import ipc
import auxiliaries
import auxiliaries_trade
import constants
import rqpfunctions

#Python Modules
import time
import termcolor
import bcrypt
import math
import base64
import traceback
import hashlib
import random
from datetime            import datetime
from collections         import deque
from cryptography.fernet import Fernet

#Constants
#System -------------------------------------------------------------------------------------------
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT

KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S
#System END ---------------------------------------------------------------------------------------



#Account Identity & Control -----------------------------------------------------------------------
ACCOUNT_TYPE_VIRTUAL    = 'VIRTUAL'
ACCOUNT_TYPE_ACTUAL     = 'ACTUAL'
ACCOUNT_STATUS_INACTIVE = 'INACTIVE'
ACCOUNT_STATUS_ACTIVE   = 'ACTIVE'
_ACCOUNT_READABLEASSETS  = ('USDT', 'USDC')
_ACCOUNT_ASSETPRECISIONS = {'USDT': 8,
                            'USDC': 8}
_ACCOUNT_BASEASSETALLOCATABLERATIO              = 0.95
_ACCOUNT_PERIODICREPORT_ANNOUNCEMENTINTERVAL_NS = 60*1e9
_ACCOUNT_PERIODICREPORT_INTERVALID              = auxiliaries.KLINE_INTERVAL_ID_5m
#Account Identity & Control END -------------------------------------------------------------------



#Announcement Auxilliaries ------------------------------------------------------------------------
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
#Announcement Auxilliaries END --------------------------------------------------------------------



#Trade Constants ----------------------------------------------------------------------------------
_ACTUALTRADE_MARKETTRADINGFEE                 = 0.0005
_TRADE_ANALYSISHANDLINGFILTER_KLINECLOSEPRICE = 0.01
_TRADE_MAXIMUMOCRGENERATIONATTEMPTS           = 5
_TRADE_TRADEHANDLER_LIFETIME_NS               = int(KLINTERVAL_S*1e9/5)
#Trade Constants END ------------------------------------------------------------------------------



class Account:
    #Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, 
                 ipcA, 
                 tmConfig, 
                 currencies, 
                 currencies_lastKline, 
                 virtualServer,
                 currencyAnalyses,
                 tradeConfigurations,
                 localID,
                 accountType,
                 buid,
                 hashedPassword,
                 assets             = None,
                 positions          = None,
                 lastPeriodicReport = None):
        
        #[1]: System
        self.__ipcA                 = ipcA
        self.__tmConfig             = tmConfig
        self.__currencies           = currencies
        self.__currencies_lastKline = currencies_lastKline
        self.__virtualServer        = virtualServer
        self.__currencyAnalyses     = currencyAnalyses
        self.__tradeConfigurations  = tradeConfigurations

        #[2]: Identity
        self.__localID        = localID
        self.__accountType    = accountType
        self.__buid           = buid
        self.__hashedPassword = hashedPassword

        #[3]: Trade Control
        self.__assets                       = dict()
        self.__positions                    = dict()
        self.__status                       = ACCOUNT_STATUS_ACTIVE if accountType == ACCOUNT_TYPE_VIRTUAL else ACCOUNT_STATUS_INACTIVE
        self.__tradeStatus                  = False
        self.__tradeConfigurations_loaded   = dict()
        self.__tradeConfigurations_attached = dict()

        #[4]: Request Control
        self.__binanceInstanceGeneration_rID    = None
        self.__binanceInstanceGeneration_result = None

        #[5]: Periodic Report
        self.__periodicReport                  = None
        self.__periodicReport_timestamp        = None
        self.__periodicReport_lastAnnounced_ns = 0

        #[6]: Assets & Positions Preparation
        assets_ip    = assets
        positions_ip = positions
        assets       = self.__assets
        positions    = self.__positions
        db_uReqs = []
        isNew    = ((assets_ip is None) and (positions_ip is None) and (lastPeriodicReport is None))
        #---[6-1]: Initialization Data Read
        if not isNew:
            self.__update_from_DB(assets             = assets_ip, 
                                  positions          = positions_ip,
                                  lastPeriodicReport = lastPeriodicReport)
            
        #---[6-2]: Assets Formatting
        for assetName in _ACCOUNT_READABLEASSETS: 
            if assetName in assets:
                continue
            self.__formatNewAsset(assetName = assetName)
            db_uReqs.append(((localID, 'assets', assetName, '#NEW#'), assets[assetName].copy()))

        #---[6-3]: Positions Formatting
        for symbol, currency in self.__currencies.items():
            if currency['quoteAsset'] not in _ACCOUNT_READABLEASSETS:
                continue
            if symbol in positions:
                continue
            self.__formatNewPosition(symbol     = symbol,
                                     quoteAsset = currency['quoteAsset'],
                                     precisions = currency['precisions'])
            db_uReqs.append(((localID, 'positions', symbol, '#NEW#'), positions[symbol].copy()))

        #---[6-4]: Priority Sort
        for assetName in _ACCOUNT_READABLEASSETS: 
            self.__sortPositionSymbolsByPriority(assetName = assetName)

        #---[6-5]: Database Update Request Dispatch
        if isNew:
            ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                         functionID     = 'addAccountDescription', 
                         functionParams = {'localID':            localID, 
                                           'accountDescription': self.getAccountDescription()}, 
                         farrHandler    = None)
        elif db_uReqs:
            ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                         functionID     = 'editAccountData', 
                         functionParams = {'updates': db_uReqs}, 
                         farrHandler    = None)
    #Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    #IPC Handlers ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __farr_onBinanceInstanceGenerationRequestResponse(self, responder, requestID, functionResult):
        #[1]: Source Check
        if responder != 'BINANCEAPI':
            return
        
        #[2]: Request ID Check
        if requestID != self.__binanceInstanceGeneration_rID:
            return

        #[3]: Result Handling
        fr_result   = functionResult['result']
        fr_failType = functionResult.get('failType',     None)
        fr_eMsg     = functionResult.get('errorMessage', None)
        if fr_result:
            self.__status = ACCOUNT_STATUS_ACTIVE
            self.__ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                                    prdAddress    = ('ACCOUNTS', self.__localID, 'status'), 
                                    prdContent    = ACCOUNT_STATUS_ACTIVE)
            self.__ipcA.sendFAR(targetProcess  = 'GUI', 
                                functionID     = 'onAccountUpdate', 
                                functionParams = {'updateType':     'UPDATED_STATUS', 
                                                  'updatedContent': self.__localID}, 
                                farrHandler    = None)
        self.__binanceInstanceGeneration_rID = None

        #[4]: Result Buffer Update
        if fr_result: 
            rb_msg = None
        else:
            if   fr_failType == 'FUTURESDISABLED':   rb_msg = "Futures Disabled, Check API Permissions"
            elif fr_failType == 'UIDMISMATCH':       rb_msg = "BUID Mismatch"
            elif fr_failType == 'UNEXPECTEDERROR':   rb_msg = f"Unexpected Error: {fr_eMsg}"
            elif fr_failType == 'SERVERUNAVAILABLE': rb_msg = "Server Unavailable"
            else:                                    rb_msg = fr_failType
        self.__binanceInstanceGeneration_result = {'result':  fr_result,
                                                   'message': rb_msg}
    
    def __farr_onPositionControlResponse(self, responder, requestID, functionResult):
        #[1]: Source Check
        if responder != 'BINANCEAPI':
            return
        
        #[2]: ID Check
        if functionResult['localID'] != self.__localID:
            return
        
        #[3]: Response Handling
        self.__onPositionControlResponse(functionResult = functionResult,
                                         requestID      = requestID)
    #IPC Handlers END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




    
    #Internal Handlers ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<Account Update>
    def __update_from_DB(self, assets, positions, lastPeriodicReport):
        #[1]: Instances
        assets_ip    = assets
        positions_ip = positions
        assets       = self.__assets
        positions    = self.__positions
        tcs_loaded   = self.__tradeConfigurations_loaded
        func_rptca = self.__registerPositionToCurrencyAnalysis
        func_rptc  = self.__registerPositionTradeConfiguration
        func_cpt   = self.__checkPositionTradability

        #[2]: Assets Formatting
        for assetName in assets_ip:
            self.__formatNewAsset(assetName = assetName)

        #[3]: Positions Formatting
        for symbol, position_ip in positions_ip.items():
            self.__formatNewPosition(symbol     = symbol,
                                     quoteAsset = position_ip['quoteAsset'],
                                     precisions = position_ip['precisions'])

        #[4]: Read Positions Data
        for symbol, position_ip in positions_ip.items():
            #[4-1]: Instances
            asset    = assets[position_ip['quoteAsset']]
            position = positions[symbol]

            #[4-2]: Direct Values Import & Formatting
            position['tradeStatus'] = position_ip['tradeStatus']
            position['reduceOnly']  = position_ip['reduceOnly']
            func_rptca(symbol = symbol, currencyAnalysisCode   = position_ip['currencyAnalysisCode'])
            func_rptc(symbol  = symbol, tradeConfigurationCode = position_ip['tradeConfigurationCode'])
            func_cpt(symbol   = symbol)
            tcTracker = position_ip['tradeControlTracker']
            tcTracker['rqpm_model'] = dict()
            position['tradeControlTracker']   = tcTracker
            position['assumedRatio']          = position_ip['assumedRatio']
            position['priority']              = position_ip['priority']
            position['maxAllocatedBalance']   = position_ip['maxAllocatedBalance']
            position['abruptClearingRecords'] = deque(position_ip['abruptClearingRecords'])

            #[4-3]: Compute others
            tc = tcs_loaded.get(position['tradeConfigurationCode'], None)
            if tc is not None: 
                position['weightedAssumedRatio'] = position['assumedRatio']*tc['leverage']

        #[5]: Sort position symbols by priority
        for assetName in assets: 
            self.__sortPositionSymbolsByPriority(assetName = assetName)

        #[6]: Read Assets Data
        for assetName, asset_ip in assets_ip.items():
            #[6-1]: Instances
            asset = assets[assetName]

            #[6-2]: Direct values import
            asset['allocationRatio'] = asset_ip['allocationRatio']

            #[6-3]: Compute others
            asset['assumedRatio']         = sum(positions[symbol]['assumedRatio']         for symbol in asset['_positionSymbols'])
            asset['weightedAssumedRatio'] = sum(positions[symbol]['weightedAssumedRatio'] for symbol in asset['_positionSymbols'] if (positions[symbol]['weightedAssumedRatio'] is not None))

        #[7]: Last Periodic Report
        self.__updatePeriodicReport(lastPeriodicReport = lastPeriodicReport)
    
    def __update(self, assets, positions):
        #[1]: Instances
        lID                  = self.__localID
        aType                = self.__accountType
        currencies_lastKline = self.__currencies_lastKline
        assets_ip            = assets
        positions_ip         = positions
        assets               = self.__assets
        positions            = self.__positions
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR
        compute_liqPrice = auxiliaries_trade.computeLiquidationPrice

        #[2]: Save previous data
        assets_prev    = {assetName: {dKey: asset[dKey]    for dKey in _GUIANNOUCEMENT_ASSETDATANAMES}    for assetName, asset    in assets.items()}
        positions_prev = {symbol:    {dKey: position[dKey] for dKey in _GUIANNOUCEMENT_POSITIONDATANAMES} for symbol,    position in positions.items()}

        #[2]: Read Positions Data
        for symbol, position_ip in positions_ip.items():
            #[2-1]: Instances
            position  = positions[symbol]
            asset     = assets[position['quoteAsset']]
            lastKline = currencies_lastKline.get(symbol, None)

            #[2-2]: Current Price Update
            lk_cp = None if lastKline is None else lastKline[KLINDEX_CLOSEPRICE]
            if lk_cp is not None:
                position['currentPrice'] = lk_cp

            #[2-3]: Trade Check
            ocr = position['_orderCreationRequest']
            if ocr is None or ocr['lastRequestReceived']:
                if position['quantity'] is not None:
                    self.__trade_checkTrade(symbol         = symbol, 
                                            quantity_new   = position_ip['quantity'], 
                                            entryPrice_new = position_ip['entryPrice'])
                position['quantity']               = position_ip['quantity']
                position['entryPrice']             = position_ip['entryPrice']
                position['isolatedWalletBalance']  = position_ip['isolatedWalletBalance']
                position['positionInitialMargin']  = position_ip['positionInitialMargin']
                position['openOrderInitialMargin'] = position_ip['openOrderInitialMargin']
                position['maintenanceMargin']      = position_ip['maintenanceMargin']
                position['unrealizedPNL']          = position_ip['unrealizedPNL']

            #[2-4]: Position Setup Identity
            position['leverage'] = position_ip['leverage']
            position['isolated'] = position_ip['isolated']
            self.__checkPositionTradability(symbol           = symbol)
            self.__requestMarginTypeAndLeverageUpdate(symbol = symbol)
            if position['isolated']:
                asset['_positionSymbols_isolated'].add(symbol)
                asset['_positionSymbols_crossed'].discard(symbol)
            else:
                asset['_positionSymbols_crossed'].add(symbol)
                asset['_positionSymbols_isolated'].discard(symbol)
                
        #[3]: Read Assets Data
        for assetName, asset_ip in assets_ip.items():
            #[3-1]: Asset
            asset = assets[assetName]

            #[3-2]: Base Balances
            asset['marginBalance']      = asset_ip['marginBalance']
            asset['walletBalance']      = asset_ip['walletBalance']
            asset['crossWalletBalance'] = asset_ip['crossWalletBalance']
            asset['availableBalance']   = asset_ip['availableBalance']

            #[3-3]: Computed Values
            asset['isolatedWalletBalance']         = sum(val                               for symbol in asset['_positionSymbols_isolated'] if (val := positions[symbol]['isolatedWalletBalance'])  is not None)
            asset['isolatedPositionInitialMargin'] = sum(val                               for symbol in asset['_positionSymbols_isolated'] if (val := positions[symbol]['positionInitialMargin'])  is not None)
            asset['openOrderInitialMargin']        = sum(val                               for symbol in asset['_positionSymbols']          if (val := positions[symbol]['openOrderInitialMargin']) is not None)
            asset['crossPositionInitialMargin']    = sum(val                               for symbol in asset['_positionSymbols_crossed']  if (val := positions[symbol]['positionInitialMargin'])  is not None)
            asset['crossMaintenanceMargin']        = sum(val                               for symbol in asset['_positionSymbols_crossed']  if (val := positions[symbol]['maintenanceMargin'])      is not None)
            asset['isolatedUnrealizedPNL']         = sum(val                               for symbol in asset['_positionSymbols_isolated'] if (val := positions[symbol]['unrealizedPNL']) is not None)
            asset['crossUnrealizedPNL']            = sum(val                               for symbol in asset['_positionSymbols_crossed']  if (val := positions[symbol]['unrealizedPNL']) is not None)
            asset['assumedRatio']                  = sum(positions[symbol]['assumedRatio'] for symbol in asset['_positionSymbols'])
            asset['weightedAssumedRatio']          = sum(val                               for symbol in asset['_positionSymbols'] if (val := positions[symbol]['weightedAssumedRatio']) is not None)
            asset['unrealizedPNL']                 = asset['isolatedUnrealizedPNL']+asset['crossUnrealizedPNL']
            if asset['walletBalance'] is None: asset['allocatableBalance'] = None
            else:                              asset['allocatableBalance'] = round((asset['walletBalance']-asset['openOrderInitialMargin'])*_ACCOUNT_BASEASSETALLOCATABLERATIO*asset['allocationRatio'], _ACCOUNT_ASSETPRECISIONS[assetName])

        #[4]: Balance Allocation
        self.__allocateBalance(assetNames = 'all')
        
        #[5]: Update Secondary Position Data
        for symbol, position in positions.items():
            #[5-1]: Instances
            asset = assets[position['quoteAsset']]

            #[5-2]: None Quantity
            if position['quantity'] is None:
                position['commitmentRate']   = None
                position['liquidationPrice'] = None
                position['riskLevel']        = None

            #[5-3]: Valid Quantity
            else:
                #[5-3-1]: Absolute Quantity
                quantity     = position['quantity']
                quantity_abs = abs(quantity)

                #[5-3-2]: Commitment Rate
                if quantity_abs != 0 and position['leverage'] is not None and position['allocatedBalance'] != 0: position['commitmentRate'] = round((quantity_abs*position['entryPrice']/position['leverage'])/position['allocatedBalance'], 5)
                else:                                                                                            position['commitmentRate'] = None
                
                #[5-3-3]: Liquidation Price
                if position['isolated']: wb = position['isolatedWalletBalance']
                else:                    wb = asset['crossWalletBalance']
                position['liquidationPrice'] = compute_liqPrice(positionSymbol    = symbol,
                                                                walletBalance     = wb,
                                                                quantity          = position['quantity'],
                                                                entryPrice        = position['entryPrice'],
                                                                currentPrice      = position['currentPrice'],
                                                                maintenanceMargin = position['maintenanceMargin'],
                                                                upnl              = position['unrealizedPNL'],
                                                                isolated          = position['isolated'],
                                                                mm_crossTotal     = asset['crossMaintenanceMargin'],
                                                                upnl_crossTotal   = asset['crossUnrealizedPNL'])
                
                #[5-3-4]: Risk Level
                ep = position['entryPrice']
                cp = position['currentPrice']
                lp = position['liquidationPrice']
                cr = position['commitmentRate']
                if ep is not None and cp is not None:
                    if lp is None: lp = 0
                    if   0 < quantity: rl = (ep-cp)/(ep-lp)
                    elif quantity < 0: rl = (cp-ep)/(lp-ep)
                    if rl < 0: rl = 0
                    if cr is None: position['riskLevel'] = rl
                    else:          position['riskLevel'] = position['commitmentRate']*rl
                else: 
                    position['riskLevel'] = None
                
        #[6]: Update Secondary Asset Data
        for asset in assets.values():
            #[6-1]: Allocated Balance
            allocatedBalanceSum = sum(positions[symbol]['allocatedBalance'] for symbol in asset['_positionSymbols'])
            asset['allocatedBalance'] = allocatedBalanceSum

            #[6-2]: Commitment Rate
            cRates = [cRate for symbol in asset['_positionSymbols'] if (cRate := positions[symbol]['commitmentRate']) is not None]
            asset['commitmentRate'] = round(sum(cRates)/len(cRates), 5) if cRates else None

            #[6-3]: Risk Level
            rls = [rl for symbol in asset['_positionSymbols'] if (rl := positions[symbol]['riskLevel']) is not None]
            asset['riskLevel'] = round(sum(rls)/len(rls), 5) if rls else None

        #[7]: Trade Handling
        self.__handleAnalysisResults()
        self.__processTradeHandlers()
        
        #[8]: Announce Updated Data
        db_uReqs = []
        for assetName, asset_prev in assets_prev.items(): 
            asset = assets[assetName]
            for dKey, val_prev in asset_prev.items():
                val = asset[dKey]
                if val == val_prev:
                    continue
                func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', lID, 'assets', assetName, dKey), prdContent = val)
                func_sendFAR(targetProcess     = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_ASSET', 'updatedContent': (lID, assetName, dKey)}, farrHandler = None)
                if dKey in _VIRTUALACCOUNTDBANNOUNCEMENT_ASSETDATANAMES:
                    db_uReqs.append(((lID, 'assets', assetName, dKey), val))

        for symbol, position_prev in positions_prev.items():
            position = positions[symbol]
            for dKey, val_prev in position_prev.items():
                val = position[dKey]
                if val == val_prev:
                    continue
                func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', lID, 'positions', symbol, dKey), prdContent = val)
                func_sendFAR(targetProcess     = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (lID, symbol, dKey)}, farrHandler = None)
                if dKey in _VIRTUALACCOUNTDBANNOUNCEMENT_POSITIONDATANAMES:
                    db_uReqs.append(((lID, 'positions', symbol, dKey), val))

        #[9]: DB Update Request
        if aType == ACCOUNT_TYPE_VIRTUAL and db_uReqs: 
            func_sendFAR(targetProcess  = 'DATAMANAGER', 
                         functionID     = 'editAccountData', 
                         functionParams = {'updates': db_uReqs}, 
                         farrHandler    = None)

    def __formatPeriodicReport(self, timestamp):
        #[1]: Instances
        assets     = self.__assets
        func_gnitt = auxiliaries.getNextIntervalTickTimestamp

        #[2]: Report Timestamp Check
        prTS = func_gnitt(intervalID = _ACCOUNT_PERIODICREPORT_INTERVALID, 
                          timestamp  = timestamp,
                          mrktReg    = None,
                          nTicks     = 0)
        if self.__periodicReport_timestamp == prTS: 
            return (prTS, None, None)

        #[3]: Previous Report Save
        if self.__periodicReport_timestamp is None:
            pr_prev   = None
            prTS_prev = None
        else:
            pr_prev   = self.__periodicReport
            prTS_prev = self.__periodicReport_timestamp

        #[4]: New Report Formatting
        pr_assets_new = dict()
        for assetName, asset in assets.items():
            mb = asset['marginBalance']
            wb = asset['walletBalance']
            cr = 0 if asset['commitmentRate'] is None else asset['commitmentRate']
            rl = 0 if asset['riskLevel']      is None else asset['riskLevel']
            pr_assets_new[assetName] = {'nTrades':             0,
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
                                        'marginBalance_open':  mb, 'marginBalance_min':  mb, 'marginBalance_max':  mb, 'marginBalance_close':  mb,
                                        'walletBalance_open':  wb, 'walletBalance_min':  wb, 'walletBalance_max':  wb, 'walletBalance_close':  wb,
                                        'commitmentRate_open': cr, 'commitmentRate_min': cr, 'commitmentRate_max': cr, 'commitmentRate_close': cr,
                                        'riskLevel_open':      rl, 'riskLevel_min':      rl, 'riskLevel_max':      rl, 'riskLevel_close':      rl,
                                        '_intervalID': _ACCOUNT_PERIODICREPORT_INTERVALID}
            
        #[5]: Report Update
        self.__periodicReport                  = pr_assets_new
        self.__periodicReport_timestamp        = prTS
        self.__periodicReport_lastAnnounced_ns = 0

        #[6]: Result Return
        return (prTS, prTS_prev, pr_prev)
   
    def __updatePeriodicReport(self, lastPeriodicReport = None):
        #[1]: Instances
        assets = self.__assets

        #[2]: Format Periodic Report
        prTS, prTS_prev, pr_prev = self.__formatPeriodicReport(timestamp = time.time())

        #[3]: Previous Report Announcement
        if prTS_prev is not None:
            self.__ipcA.sendFAR(targetProcess  = 'DATAMANAGER',
                                functionID     = 'updateAccountPeriodicReport', 
                                functionParams = {'localID':        self.__localID, 
                                                  'timestamp':      prTS_prev, 
                                                  'periodicReport': pr_prev}, 
                                farrHandler    = None)

        #[4]: Data Import
        if lastPeriodicReport is not None:
            #[4-1]: Timestamp Match Check
            pr_import   = lastPeriodicReport['report']
            prTS_import = lastPeriodicReport['timestamp']
            
            #[4-2]: Import
            if prTS == prTS_import:
                self.__periodicReport = pr_import

        #[5]: Report Update
        pr = self.__periodicReport
        for assetName, asset in assets.items():
            pr_asset = pr[assetName]
            
            #[5-1]: Margin Balance
            if asset['marginBalance'] is not None:
                if pr_asset['marginBalance_open'] is None: pr_asset['marginBalance_open'] = asset['marginBalance']
                if pr_asset['marginBalance_min'] is None or asset['marginBalance'] < pr_asset['marginBalance_min']: pr_asset['marginBalance_min'] = asset['marginBalance']
                if pr_asset['marginBalance_max'] is None or pr_asset['marginBalance_max'] < asset['marginBalance']: pr_asset['marginBalance_max'] = asset['marginBalance']
                pr_asset['marginBalance_close'] = asset['marginBalance']

            #[5-2]: Wallet Balance
            if asset['walletBalance'] is not None:
                if pr_asset['walletBalance_open'] is None: pr_asset['walletBalance_open'] = asset['walletBalance']
                if pr_asset['walletBalance_min'] is None or asset['walletBalance'] < pr_asset['walletBalance_min']: pr_asset['walletBalance_min'] = asset['walletBalance']
                if pr_asset['walletBalance_max'] is None or pr_asset['walletBalance_max'] < asset['walletBalance']: pr_asset['walletBalance_max'] = asset['walletBalance']
                pr_asset['walletBalance_close'] = asset['walletBalance']

            #[5-3]: Commitment Rate
            cr = 0 if asset['commitmentRate'] is None else asset['commitmentRate']
            if cr < pr_asset['commitmentRate_min']: pr_asset['commitmentRate_min'] = cr
            if pr_asset['commitmentRate_max'] < cr: pr_asset['commitmentRate_max'] = cr
            pr_asset['commitmentRate_close'] = cr
            
            #[5-4]: Risk Level
            rl = 0 if asset['riskLevel'] is None else asset['riskLevel']
            if rl < pr_asset['riskLevel_min']: pr_asset['riskLevel_min'] = rl
            if pr_asset['riskLevel_max'] < rl: pr_asset['riskLevel_max'] = rl
            pr_asset['riskLevel_close'] = rl

        #[6]: Current Report Announcement
        t_current_ns = time.perf_counter_ns()
        if _ACCOUNT_PERIODICREPORT_ANNOUNCEMENTINTERVAL_NS <= t_current_ns-self.__periodicReport_lastAnnounced_ns:
            #[6-1]: Copy Periodic Report
            pr_copy = {assetName: pr_asset.copy() for assetName, pr_asset in pr.items()}

            #[6-2]: Announcement
            self.__ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                functionID     = 'updateAccountPeriodicReport', 
                                functionParams = {'localID':        self.__localID, 
                                                  'timestamp':      prTS, 
                                                  'periodicReport': pr_copy}, 
                                farrHandler    = None)
            
            #[6-3]: Update Timer
            self.__periodicReport_lastAnnounced_ns = t_current_ns

    def __updatePeriodicReport_onTrade(self, symbol, side, logicSource, profit):
        #[1]: Instances
        qAsset  = self.__positions[symbol]['quoteAsset']
        asset   = self.__assets[qAsset]
        pReport = self.__periodicReport[qAsset]

        #[2]: Counters
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

        #[3]: Balances & Commitment Rate & Risk Level
        #---[3-1]: Margin Balance
        asset_mb = asset['marginBalance']
        if asset_mb is not None:
            if pReport['marginBalance_open'] is None: pReport['marginBalance_open'] = asset_mb
            if pReport['marginBalance_min'] is None or asset_mb < pReport['marginBalance_min']: pReport['marginBalance_min'] = asset_mb
            if pReport['marginBalance_max'] is None or pReport['marginBalance_max'] < asset_mb: pReport['marginBalance_max'] = asset_mb
            pReport['marginBalance_close'] = asset_mb
        #---[3-2]: Wallet Balance
        asset_wb = asset['walletBalance']
        if asset_wb is not None:
            if pReport['walletBalance_open'] is None: pReport['walletBalance_open'] = asset_wb
            if pReport['walletBalance_min'] is None or asset_wb < pReport['walletBalance_min']: pReport['walletBalance_min'] = asset_wb
            if pReport['walletBalance_max'] is None or pReport['walletBalance_max'] < asset_wb: pReport['walletBalance_max'] = asset_wb
            pReport['walletBalance_close'] = asset_wb
        #---[3-3]: Commitment Rate
        asset_cr = asset['commitmentRate']
        cr = 0 if asset_cr is None else asset_cr
        pReport['commitmentRate_min'] = min(cr, pReport['commitmentRate_min'])
        pReport['commitmentRate_max'] = max(cr, pReport['commitmentRate_max'])
        pReport['commitmentRate_close'] = cr
        #---[3-4]: Risk Level
        asset_rl = asset['riskLevel']
        rl = 0 if asset_rl is None else asset_rl
        pReport['riskLevel_min'] = min(rl, pReport['riskLevel_min'])
        pReport['riskLevel_max'] = max(rl, pReport['riskLevel_max'])
        pReport['riskLevel_close'] = rl

        #[4]: Announcement Timer Update To Force Announcement
        self.__periodicReport_lastAnnounced_ns = 0

    def __formatNewAsset(self, assetName):
        asset = {'marginBalance':                 0,
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
        self.__assets[assetName] = asset
    
    def __formatNewPosition(self, symbol, quoteAsset, precisions):
        asset     = self.__assets[quoteAsset]
        positions = self.__positions
        position = {'quoteAsset':              quoteAsset,
                    'precisions':              precisions,
                    'tradeStatus':             False,
                    'reduceOnly':              False,
                    'tradable':                False,
                    'currencyAnalysisCode':    None,
                    'tradeConfigurationCode':  None,
                    #Base
                    'quantity':                None,
                    'entryPrice':              None,
                    'leverage':                1,
                    'isolated':                True,
                    'isolatedWalletBalance':   None,
                    'positionInitialMargin':   None,
                    'openOrderInitialMargin':  None,
                    'maintenanceMargin':       None,
                    'currentPrice':            None,
                    'unrealizedPNL':           None,
                    'liquidationPrice':        None,
                    #Trade Control
                    'tradeControlTracker': self.__getInitializedTradeControlTracker(),
                    #Positional Distribution
                    'assumedRatio':        0,
                    'priority':            len(positions)+1,
                    'allocatedBalance':    0,
                    'maxAllocatedBalance': float('inf'),
                    #Risk Management
                    'weightedAssumedRatio':  None,
                    'commitmentRate':        None,
                    'riskLevel':             None,
                    'abruptClearingRecords': deque(),
                    #Server Interaction Control
                    '_tradabilityTests': {'currencyAnalysis':   False,
                                          'tradeConfiguration': False,
                                          'openOrder':          False},
                    '_marginTypeControlRequest': None,
                    '_leverageControlRequest':   None,
                    '_linearizedAnalyses':       None,
                    '_tradeHandlers':            deque(),
                    '_orderCreationRequest':     None}
        positions[symbol] = position
        asset['_positionSymbols'].add(symbol)
        asset['_positionSymbols_isolated'].add(symbol)
        asset['_positionSymbols_prioritySorted'].append(symbol)
    
    def __onPositionControlResponse(self, functionResult, requestID):
        #[1]: Instances
        lID        = self.__localID
        symbol     = functionResult['positionSymbol']
        responseOn = functionResult['responseOn']
        result     = functionResult['result']
        position   = self.__positions[symbol]

        #[2]: Response Handling
        #---[2-1]: MarginType Update Request Response
        if responseOn == 'MARGINTYPEUPDATE':
            #[2-1-1]: Expected Check
            if position['_marginTypeControlRequest'] != requestID:
                return
            
            #[2-1-2]: Result Interpretation
            if result: #Placeholder for future expansion
                pass
            else:
                failType = functionResult['failType']
                if   failType == 'SERVERUNAVAILABLE':   pass #Placeholder for future expansion
                elif failType == 'LOCALIDNOTFOUND':     pass #Placeholder for future expansion
                elif failType == 'ACCOUNTNOTACTIVATED': pass #Placeholder for future expansion
                elif failType == 'MARGINTYPEERROR':     pass #Placeholder for future expansion
                elif failType == 'APIERROR':            pass #Placeholder for future expansion
                self.__logger(message = (f"A Margin Type Update Request Received Failure Response.\n"
                                         f" * Local ID:  {lID}\n"
                                         f" * Symbol:    {symbol}\n"
                                         f" * Fail Type: {fr_fType}\n"
                                        ), 
                              logType = 'Update',
                              color   = 'light_yellow')

            #[2-1-3]: Flag Update
            position['_marginTypeControlRequest'] = None

        #---[2-2]: Leverage Update Request Response
        elif responseOn == 'LEVERAGEUPDATE':
            #[2-2-1]: Expected Check
            if position['_leverageControlRequest'] != requestID:
                return
            
            #[2-2-2]: Result Interpretation
            if result: #Placeholder for future expansion
                pass
            else:
                failType = functionResult['failType']
                if   failType == 'SERVERUNAVAILABLE':   pass #Placeholder for future expansion
                elif failType == 'LOCALIDNOTFOUND':     pass #Placeholder for future expansion
                elif failType == 'ACCOUNTNOTACTIVATED': pass #Placeholder for future expansion
                elif failType == 'APIERROR':            pass #Placeholder for future expansion
                self.__logger(message = (f"A Leverage Update Request Received Failure Response.\n"
                                         f" * Local ID:  {lID}\n"
                                         f" * Symbol:    {symbol}\n"
                                         f" * Fail Type: {fr_fType}\n"
                                        ), 
                              logType = 'Update',
                              color   = 'light_yellow')

            #[2-2-3]: Flag Update
            position['_leverageControlRequest'] = None

        #---[2-3]: Order Creation Request Response
        elif responseOn == 'CREATEORDER':
            #[2-3-1]: Expected Check
            ocr = position['_orderCreationRequest']
            if ocr is None:
                return

            #[2-3-2]: Result Interpretation
            if requestID is None or ocr['dispatchID'] == requestID:
                #[2-3-2-1]: Instances
                fr_fType   = functionResult['failType']
                fr_oResult = functionResult['orderResult']
                fr_eMsg    = functionResult['errorMessage']

                #[2-3-2-2]: Failure Logging
                if not result:
                    self.__logger(message = (f"An Order Creation Request Received Failure Response.\n"
                                             f" * Local ID:      {lID}\n"
                                             f" * Symbol:        {symbol}\n"
                                             f" * Fail Type:     {fr_fType}\n"
                                             f" * Order Result:  {fr_oResult}\n"
                                             f" * Error Message: {fr_eMsg}"
                                            ), 
                                  logType = 'Update',
                                  color   = 'light_yellow')
                    
                #[2-3-2-3]: Result Recording & Flag Update
                requestResult = {'resultReceivalTime': time.time(), 
                                 'result':             result,
                                 'failType':           fr_fType,
                                 'orderResult':        fr_oResult,
                                 'errorMessage':       fr_eMsg}
                ocr['results'].append(requestResult)
                ocr['lastRequestReceived'] = True

    def __sortPositionSymbolsByPriority(self, assetName):
        #[1]: Instances
        asset     = self.__assets[assetName]
        positions = self.__positions

        #[2]: Sorting
        asset['_positionSymbols_prioritySorted'] = sorted(asset['_positionSymbols'], key = lambda symbol: positions[symbol]['priority'])
    
    def __allocateBalance(self, assetNames = 'all'):
        #[1]: Status Check
        if self.__status != ACCOUNT_STATUS_ACTIVE:
            return
        
        #[2]: Instances
        assets    = self.__assets
        positions = self.__positions
        
        #[3]: Targets Determination
        if assetNames == 'all': 
            assetNames = list(assets)

        #[4]: Balance Allocation
        for assetName in assetNames:
            #[4-1]: Instances & Balance Check
            asset = assets[assetName]
            if asset['allocatableBalance'] is None:
                continue
            allocatedAssumedRatio = 0

            #[4-2]: Zero Quantity Allocation Zero
            for symbol in asset['_positionSymbols']:
                #[4-2-1]: Instances
                position = positions[symbol]

                #[4-2-2]: Zero quantity
                if position['quantity'] == 0: 
                    assumedRatio_effective       = 0
                    position['allocatedBalance'] = 0

                #[4-2-3]: Non-Zero Quantity
                else:
                    if 0 < asset['allocatableBalance']:
                        assumedRatio_effective = round(position['allocatedBalance']/asset['allocatableBalance'], 4)
                    else:
                        assumedRatio_effective = 0

                #[4-2-4]: Effective Assumed Ratio Update
                allocatedAssumedRatio += assumedRatio_effective

            #[4-3]: Zero Quantity Re-Allocation
            for symbol in asset['_positionSymbols_prioritySorted']:
                #[4-3-1]: Instances
                position = positions[symbol]

                #[4-3-2]: Condition Check (Zero Quantity)
                if not(position['quantity'] == 0 or (position['assumedRatio'] != 0 and position['allocatedBalance'] == 0)): 
                    continue

                #[4-3-3]: Allocated Balance & Effective Assumed Ratio Update
                if 0 < asset['allocatableBalance']:
                    allocatedBalance       = min(round(asset['allocatableBalance']*position['assumedRatio'], position['precisions']['quote']),
                                                 position['maxAllocatedBalance'])
                    assumedRatio_effective = round(allocatedBalance/asset['allocatableBalance'], 4)
                else:
                    allocatedBalance       = 0
                    assumedRatio_effective = 0

                #[4-3-4]: Allocatability Check
                if allocatedAssumedRatio+assumedRatio_effective <= 1:
                    allocatedAssumedRatio += assumedRatio_effective
                    position['allocatedBalance'] = allocatedBalance
                else: break

    def __checkPositionTradability(self, symbol):
        #[1]: Instances
        iID      = self.__localID
        position = self.__positions[symbol]
        tTests = position['_tradabilityTests']
        caCode = position['currencyAnalysisCode']
        tcCode = position['tradeConfigurationCode']
        ooim   = position['openOrderInitialMargin']

        #[2]: Currency Analysis
        tTests['currencyAnalysis'] = self.__currencyAnalyses.isAttached(code = caCode, accountID = iID)

        #[3]: Trade Configuration
        tc = self.__tradeConfigurations_loaded.get(tcCode, None)
        if tc is None:
            tTests['tradeConfiguration'] = False
        else:
            tTest_attached = self.__tradeConfigurations.isAttached(code = tcCode, accountID = iID)
            tTest_mType    = (position['isolated'] == tc['isolated'])
            tTest_leverage = (position['leverage'] == tc['leverage'])
            tTests['tradeConfiguration'] = (tTest_attached and tTest_mType and tTest_leverage)

        #[4]: Open Order
        tTests['openOrder'] = (ooim == 0.0)

        #[5]: Tradable Update
        position['tradable'] = all(test for test in tTests.values())

        #[6]: Trade Status Update
        if not position['tradable'] and position['quantity'] is not None:
            position['tradeStatus'] = False
    
    def __requestMarginTypeAndLeverageUpdate(self, symbol):
        #[1]: Instances
        iID      = self.__localID
        aType    = self.__accountType
        vs       = self.__virtualServer
        position = self.__positions[symbol]
        tc       = self.__tradeConfigurations_loaded.get(position['tradeConfigurationCode'], None)
        func_sendFAR = self.__ipcA.sendFAR
        
        #[2]: Tradability & TC Check
        if position['_tradabilityTests']['tradeConfiguration'] or tc is None:
            return

        #[3]: Status Check
        if self.__status != ACCOUNT_STATUS_ACTIVE:
            return

        #[4]: Open Order Check
        if position['openOrderInitialMargin'] != 0.0:
            return

        #[5]: Quantity Test
        if position['quantity']:
            return
        
        #[6]: Updates Request
        #---[6-1]: Margin Type
        if position['isolated'] != tc['isolated'] and position['_marginTypeControlRequest'] is None:
            #[6-1-1]: New Margin Type
            if tc['isolated']: newMarginType = 'ISOLATED'
            else:              newMarginType = 'CROSSED'

            #[6-1-2]: Virtual Type
            if aType == ACCOUNT_TYPE_VIRTUAL: 
                rID = vs.updateMarginType(localID    = iID,
                                          symbol     = symbol,
                                          marginType = newMarginType)

            #[6-1-3]: Actual Type
            elif aType == ACCOUNT_TYPE_ACTUAL:  
                rID = func_sendFAR(targetProcess  = 'BINANCEAPI', 
                                   functionID     = 'setPositionMarginType', 
                                   functionParams = {'localID':        iID, 
                                                     'positionSymbol': symbol, 
                                                     'newMarginType':  newMarginType}, 
                                   farrHandler    = self.__farr_onPositionControlResponse)

            #[6-1-4]: Flag Raise
            position['_marginTypeControlRequest'] = rID

        #---[6-2]: Leverage
        if position['leverage'] != tc['leverage'] and position['_leverageControlRequest'] is None: 
            #[6-2-1]: Virtual Type
            if aType == ACCOUNT_TYPE_VIRTUAL: 
                rID = vs.updateLeverage(localID  = iID,
                                        symbol   = symbol,
                                        leverage = tc['leverage'])

            #[6-2-2]: Actual Type
            elif aType == ACCOUNT_TYPE_ACTUAL:  
                rID = func_sendFAR(targetProcess  = 'BINANCEAPI', 
                                   functionID     = 'setPositionLeverage', 
                                   functionParams = {'localID':        iID, 
                                               'positionSymbol': symbol, 
                                               'newLeverage':    tc['leverage']}, 
                             farrHandler    = self.__farr_onPositionControlResponse)
                
            #[6-2-3]: Flag Raise
            position['_leverageControlRequest'] = rID
    




    #<Currency Analysis>
    def __registerPositionToCurrencyAnalysis(self, symbol, currencyAnalysisCode, announce = True):
        #[1]: Instances
        lID      = self.__localID
        position = self.__positions[symbol]
        caCode   = currencyAnalysisCode
        cas      = self.__currencyAnalyses

        #[2]: Unregister Position From Currency Analysis
        self.__unregisterPositionFromCurrencyAnalysis(symbol = symbol)

        #[3]: Currency Analysis Check & Update
        cas.attachAccount(code = caCode, accountID = lID, receiver = self.onAnalysisGeneration)
        if not cas.isAttached(code = caCode, accountID = lID):
            return

        #[4]: Position Update
        position['currencyAnalysisCode'] = caCode
        position['_linearizedAnalyses']  = None
    
    def __unregisterPositionFromCurrencyAnalysis(self, symbol):
        #[1]: Instances
        lID      = self.__localID
        position = self.__positions[symbol]
        caCode   = position['currencyAnalysisCode']
        cas      = self.__currencyAnalyses

        #[2]: Currency Analysis Update
        if caCode is None:
            return
        cas.detachAccount(code = caCode, accountID = lID)
        
        #[3]: Position Update
        position['currencyAnalysisCode'] = None
        position['_linearizedAnalyses']  = None





    #<Trade Configuration>
    def __registerPositionTradeConfiguration(self, symbol, tradeConfigurationCode):
        #[1]: Instances
        lID          = self.__localID
        position     = self.__positions[symbol]
        tcCode       = tradeConfigurationCode
        tcs          = self.__tradeConfigurations
        tcs_attached = self.__tradeConfigurations_attached

        #[2]: Unregister Position Trade Configuration
        self.__unregisterPositionTradeConfiguration(symbol = symbol)

        #[3]: Trade Configuration Check & Update
        loaded = self.__loadTradeConfiguration(tradeConfigurationCode = tcCode)
        if loaded:
            tcs.attachAccount(code = tcCode, accountID = lID)
            tcs_attached[tcCode].add(symbol)

        #[4]: Position Update
        position['tradeConfigurationCode'] = tcCode
        position['_linearizedAnalyses']    = None
    
    def __unregisterPositionTradeConfiguration(self, symbol):
        #[1]: Instances
        lID          = self.__localID
        position     = self.__positions[symbol]
        tcCode       = position['tradeConfigurationCode']
        tcs          = self.__tradeConfigurations
        tcs_loaded   = self.__tradeConfigurations_loaded
        tcs_attached = self.__tradeConfigurations_attached

        #[2]: Trade Configuration Update
        if tcCode is None:
            return
        tcs.detachAccount(code = tcCode, accountID = lID)
        tc_attached = tcs_attached[tcCode]
        tc_attached.remove(symbol)
        if not tc_attached:
            del tcs_loaded[tcCode]
            del tcs_attached[tcCode]

        #[3]: Position Update
        position['tradeConfigurationCode'] = None
        position['_linearizedAnalyses']    = None
    
    def __loadTradeConfiguration(self, tradeConfigurationCode):
        #[1]: Instances
        tcCode = tradeConfigurationCode
        tcs          = self.__tradeConfigurations
        tcs_loaded   = self.__tradeConfigurations_loaded
        tcs_attached = self.__tradeConfigurations_attached

        #[2]: Loaded Check
        if tcCode in tcs_loaded:
            return True

        #[3]: TC Load
        tc = tcs.getConfiguration(code = tcCode)
        if tc is None:
            return False
        tcs_loaded[tcCode]   = tc
        tcs_attached[tcCode] = set()

        #[4]: Result Return
        return True





    #<Trade Control Tracker>
    def __getInitializedTradeControlTracker(self):
        tc_initialized = {'slExited':   None,
                          'rqpm_model': dict()}
        return tc_initialized
    
    def __copyTradeControlTracker(self, tradeControlTracker):
        tcTracker_copy = {'slExited':   tradeControlTracker['slExited'],
                          'rqpm_model': tradeControlTracker['rqpm_model'].copy()}
        return tcTracker_copy
    
    def __updateTradeControlTracker(self, symbol, tradeControlTrackerUpdate, updateMode):
        #[1]: Instances
        position  = self.__positions[symbol]
        tcTracker = position['tradeControlTracker']

        #[2]: Trade Control Tracker Update
        #---[2-1]: SL Exited
        if 'slExited' in tradeControlTrackerUpdate:
            tcTracker['slExited'] = tradeControlTrackerUpdate['slExited'][updateMode]





    #<Trade Processing>
    def __handleAnalysisResults(self):
        #[1]: Instances
        currencies = self.__currencies
        positions  = self.__positions
        func_hAR   = self.__handleAnalysisResult

        #[2]: Positions Processing
        for symbol, position in positions.items():
            #[2-1]: Current Price Check
            if position['currentPrice'] is None:
                continue

            #[2-2]: Server Data Check
            currency = currencies.get(symbol, None)
            if currency is None or currency['info_server'] is None:
                continue

            #[2-3]: Analysis Handling
            las = position['_linearizedAnalyses']
            while las:
                func_hAR(symbol = symbol, linearizedAnalysis = las.popleft())
    
    def __handleAnalysisResult(self, symbol, linearizedAnalysis):
        #[1]: Instances
        lID       = self.__localID
        position  = self.__positions[symbol]
        tc        = self.__tradeConfigurations_loaded.get(position['tradeConfigurationCode'], None)
        tcTracker = position['tradeControlTracker']
        la        = linearizedAnalysis
        func_gnitt = auxiliaries.getNextIntervalTickTimestamp

        #[2]: Trade Configuraion Check
        if tc is None: 
            return

        #[3]: Analysis Result Expiration Check (Whether this was historical / current)
        la_cp           = la['KLINE_CLOSEPRICE']
        priceExpired    = la_cp is None or _TRADE_ANALYSISHANDLINGFILTER_KLINECLOSEPRICE <= abs(position['currentPrice']/la_cp-1)
        t_current_s     = time.time()
        la_openTime     = la['OPENTIME']
        tsInterval_prev = func_gnitt(intervalID = KLINTERVAL, timestamp = t_current_s, nTicks = -1)
        tsInterval_this = func_gnitt(intervalID = KLINTERVAL, timestamp = t_current_s, nTicks =  0)
        if la_openTime == tsInterval_prev: ar_expired = priceExpired
        else:                              ar_expired = priceExpired or la_openTime != tsInterval_this

        #[4]: RQP Value
        tc_rqpm_fType   = tc['rqpm_functionType']
        tc_rqpm_fParams = tc['rqpm_functionParams']
        try:
            rqps = rqpfunctions.RQPMFUNCTIONS_GET_RQPVAL[tc_rqpm_fType](params             = tc_rqpm_fParams,
                                                                        linearizedAnalysis = la, 
                                                                        tcTracker_model    = tcTracker['rqpm_model'])
            rqpDirection, rqpValue = rqps

            #REMOVE BELOW LATER
            rqpValue = random.random()*2-1
            if rqpValue < 0:
                rqpDirection = 'SHORT'
            else:
                rqpDirection = 'LONG'
            rqpValue = abs(rqpValue)
            print(la_openTime, ar_expired, rqpDirection, rqpValue)
            #REMOVE ABOVE LATER
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred During RQP Value Calculation. User Attention Strongly Advised.\n"
                                     f" * Local ID:            {lID}\n"
                                     f" * Position Symbol:     {symbol}\n"
                                     f" * RQP Function Type:   {tc_rqpm_fType}\n"
                                     f" * RQP Function Params: {tc_rqpm_fParams}\n"
                                     f" * Linearized Analysis: {la}\n"
                                     f" * Time:                {time.time()}\n"
                                     f" * Error:               {e}\n"
                                     f" * Detailed Trace:      {traceback.format_exc()}"), 
                          logType = 'Error',
                          color   = 'light_red')
            return
        if not isinstance(rqpValue, (int, float)) or not (-1 <= rqpValue <= 1):
            self.__logger(message = (f"An Unexpected RQP Value Detected. RQP Value Must Be An Integer Or Float In Range [-1.0, 1.0]. User Attention Strongly Advised.\n"
                                     f" * Local ID:            {lID}\n"
                                     f" * Position Symbol:     {symbol}\n"
                                     f" * RQP Function Type:   {tc_rqpm_fType}\n"
                                     f" * RQP Function Params: {tc_rqpm_fParams}\n"
                                     f" * RQP Value:           {rqpValue}\n"
                                     f" * Linearized Analysis: {la}\n"
                                     f" * Time:                {time.time()}"), 
                          logType = 'Warning',
                          color   = 'light_red')
            return

        #[5]: SL Exit Flag
        #---[5-1]: Reset Check
        tct_sle = tcTracker['slExited']
        if tct_sle is not None and not ar_expired:
            tct_sle_side, tct_sle_time = tct_sle
            if tct_sle_time < la_openTime and tct_sle_side != rqpDirection:
                tcTracker['slExited'] = None
        #---[5-2]: Control Tracker Save (If Not Based On Expired Linearized Analysis Result)
        if not ar_expired:
            tcTracker_copied = self.__copyTradeControlTracker(tradeControlTracker = tcTracker)
            self.__ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                                    prdAddress = ('ACCOUNTS', lID, 'positions', symbol, 'tradeControlTracker'), 
                                    prdContent = tcTracker_copied)
            self.__ipcA.sendFAR(targetProcess  = 'GUI', 
                                functionID     = 'onAccountUpdate', 
                                functionParams = {'updateType':     'UPDATED_POSITION', 
                                                  'updatedContent': (lID, symbol, 'tradeControlTracker')}, 
                                farrHandler    = None)
            self.__ipcA.sendFAR(targetProcess  = 'DATAMANAGER',
                                functionID     = 'editAccountData',
                                functionParams = {'updates': [((lID, 'positions', symbol, 'tradeControlTracker'), tcTracker_copied),]}, 
                                farrHandler    = None)
            
        #[7]: Trade Continuation Check
        if ar_expired:                  return
        if not self.__tradeStatus:      return
        if not position['tradeStatus']: return

        #[8]: Trade Handlers Determination
        tradeHandler_checkList = {'ENTRY': None,
                                  'CLEAR': None,
                                  'EXIT':  None}
        
        #---[8-1]: CheckList 1: CLEAR
        if   position['quantity'] < 0 and rqpDirection != 'SHORT': tradeHandler_checkList['CLEAR'] = 'BUY'
        elif 0 < position['quantity'] and rqpDirection != 'LONG':  tradeHandler_checkList['CLEAR'] = 'SELL'

        #---[8-2]: CheckList 2: ENTRY & EXIT
        pslCheck = tc['postStopLossReentry'] or (tcTracker['slExited'] is None)
        if rqpDirection == 'SHORT':  
            if pslCheck and tc['direction'] in ('BOTH', 'SHORT'): 
                tradeHandler_checkList['ENTRY'] = 'SELL'
            tradeHandler_checkList['EXIT'] = 'BUY'
        elif rqpDirection == 'LONG':
            if pslCheck and tc['direction'] in ('BOTH', 'LONG'): 
                tradeHandler_checkList['ENTRY'] = 'BUY'
            tradeHandler_checkList['EXIT'] = 'SELL'
        elif rqpDirection is None:
            if   position['quantity'] < 0: tradeHandler_checkList['EXIT'] = 'BUY'
            elif 0 < position['quantity']: tradeHandler_checkList['EXIT'] = 'SELL'

        #---[8-3]: Trade Handlers Determination
        tradeHandlers = []
        if tradeHandler_checkList['CLEAR'] is not None: tradeHandlers.append('CLEAR')
        if tradeHandler_checkList['EXIT']  is not None: tradeHandlers.append('EXIT')
        if tradeHandler_checkList['ENTRY'] is not None: tradeHandlers.append('ENTRY')

        #[9]: Update Trade Handlers
        position_ths = position['_tradeHandlers']
        for thType in tradeHandlers:
            th = {'type':              thType, 
                  'side':              tradeHandler_checkList[thType],
                  'rqpVal':            rqpValue,
                  'timestamp':         la_openTime,
                  'generationTime_ns': time.time_ns()}
            position_ths.append(th)
    
    def __processTradeHandlers(self):
        #[1]: Instances
        lID        = self.__localID
        tcs_loaded = self.__tradeConfigurations_loaded
        currencies = self.__currencies

        #[2]: Trade Handlers Processing
        for symbol, position in self.__positions.items():
            #[2-1]: Instances
            precisions    = position['precisions']
            tradeHandlers = position['_tradeHandlers']

            #[2-2]: Status Check
            if not tradeHandlers:                                 continue #If there exists no tradeHandlers, continue
            if position['_orderCreationRequest']     is not None: continue #If there exists a generated order creation request, continue
            if position['_marginTypeControlRequest'] is not None: continue #If there exists a margin type control request, continue
            if position['_leverageControlRequest']   is not None: continue #If there exists a leverage control request, continue

            #[2-3]: Position Preparation Check
            tc            = tcs_loaded[position['tradeConfigurationCode']]
            serverFilters = currencies[symbol]['info_server']['filters']
            
            #[2-4]: Trade Handler Selection & Expiration Check
            th = tradeHandlers.popleft()
            th_type       = th['type']
            th_side       = th['side']
            th_rqpVal     = th['rqpVal']
            th_timestamp  = th['timestamp']
            th_genTime_ns = th['generationTime_ns']
            if _TRADE_TRADEHANDLER_LIFETIME_NS < time.time_ns()-th_genTime_ns:
                self.__logger(message = (f"A Trade Handler Is Expired And Will Be Discarded.\n"
                                         f" * Local ID:             {lID}\n"
                                         f" * Symbol:               {symbol}\n"
                                         f" * Type:                 {th_type}\n"
                                         f" * Side:                 {th_side}\n"
                                         f" * RQP Value:            {th_rqpVal}\n"
                                         f" * Generation Time [ns]: {th_genTime_ns}\n"), 
                              logType = 'Warning',
                              color   = 'light_magenta')
                continue

            #[2-5]: Handling
            #---[2-5-1]: ENTRY
            if th_type == 'ENTRY':
                #[2-5-1-1]: Balance Commitment Check
                balance_allocated = position['allocatedBalance']                                    if position['allocatedBalance'] is not None else 0
                balance_committed = abs(position['quantity'])*position['entryPrice']/tc['leverage'] if position['entryPrice']       is not None else 0
                balance_toCommit  = balance_allocated*abs(th_rqpVal)
                balance_toEnter   = balance_toCommit-balance_committed
                if not (0 < balance_toEnter): 
                    continue

                #[2-5-1-2]: Quantity Determination
                quantity_minUnit = pow(10, -precisions['quantity'])
                quantity         = round(int((balance_toEnter/position['currentPrice']*tc['leverage'])/quantity_minUnit)*quantity_minUnit, precisions['quantity'])
                if quantity < 0: 
                    self.__logger(message = (f"A Trade Handler Failed Quantity Test And Will Be Discarded. - 'NEGATIVE QUANTITY'\n"
                                             f" * Local ID:             {lID}\n"
                                             f" * Symbol:               {symbol}\n"
                                             f" * Type:                 {th_type}\n"
                                             f" * Side:                 {th_side}\n"
                                             f" * RQP Value:            {th_rqpVal}\n"
                                             f" * Generation Time [ns]: {th_genTime_ns}\n"
                                             f" * Quantity - Current:   {position['quantity']}\n"
                                             f" * Quantity - Trade:     {quantity}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue
                if quantity == 0: 
                    self.__logger(message = (f"A Trade Handler Failed Quantity Test And Will Be Discarded. - 'ZERO QUANTITY'\n"
                                             f" * Local ID:             {lID}\n"
                                             f" * Symbol:               {symbol}\n"
                                             f" * Type:                 {th_type}\n"
                                             f" * Side:                 {th_side}\n"
                                             f" * RQP Value:            {th_rqpVal}\n"
                                             f" * Generation Time [ns]: {th_genTime_ns}\n"
                                             f" * Quantity - Current:   {position['quantity']}\n"
                                             f" * Quantity - Trade:     {quantity}"), 
                                  logType = 'Update',
                                  color   = 'light_yellow')
                    continue

                #[2-5-1-3]: Server Filter Test
                serverFilterTest = None
                for serverFilter in serverFilters:
                    sf_ft = serverFilter['filterType']
                    if sf_ft == 'PRICE_FILTER': 
                        continue
                    elif sf_ft == 'LOT_SIZE':     
                        continue
                    elif sf_ft == 'MARKET_LOT_SIZE':
                        _minQty   = float(serverFilter['minQty'])
                        _maxQty   = float(serverFilter['maxQty'])
                        _stepSize = float(serverFilter['stepSize'])
                        if not (_minQty <= quantity):
                            serverFilterTest = {'type':   'MINQTY',
                                                'minQty': _minQty}
                            break
                        if not (quantity <= _maxQty):
                            serverFilterTest = {'type':   'MAXQTY',
                                                'maxQty': _maxQty}
                            break
                        if not (quantity == round(quantity, -math.floor(math.log10(_stepSize)))): 
                            serverFilterTest = {'type':               'STEPSIZE',
                                                'stepSize':           _stepSize,
                                                'stepSize_val':       math.floor(math.log10(_stepSize)),
                                                'quantity_stepSized': round(quantity, -math.floor(math.log10(_stepSize)))}
                            break
                    elif sf_ft == 'MAX_NUM_ORDERS': 
                        continue
                    elif sf_ft == 'MAX_NUM_ALGO_ORDERS': 
                        continue
                    elif sf_ft == 'MIN_NOTIONAL':
                        _notional_min = float(serverFilter['notional'])
                        _notional = position['currentPrice']*quantity
                        if not(_notional_min <= _notional):
                            serverFilterTest = {'type':        'MINNOTIONAL',
                                                'notional':     _notional,
                                                'notional_min': _notional_min}
                            break
                    elif sf_ft == 'PERCENT_PRICE': 
                        continue
                if serverFilterTest is not None:
                    self.__logger(message = (f"A Trade Handler Failed Server Filter Test And Will Be Discarded.\n"
                                             f" * Local ID:             {lID}\n"
                                             f" * Symbol:               {symbol}\n"
                                             f" * Type:                 {th_type}\n"
                                             f" * Side:                 {th_side}\n"
                                             f" * RQP Value:            {th_rqpVal}\n"
                                             f" * Generation Time [ns]: {th_genTime_ns}\n"
                                             f" * Quantity - Current:   {position['quantity']}\n"
                                             f" * Quantity - Trade:     {quantity}\n"
                                             f" * Server Filter Test:   {serverFilterTest}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue

                #[2-5-1-4]: Side Confirm
                if not ((position['quantity'] <= 0 and th_side == 'SELL') or \
                        (0 <= position['quantity'] and th_side == 'BUY')): 
                    self.__logger(message = (f"A Trade Handler Failed Side Test And Will Be Discarded.\n"
                                             f" * Local ID:             {lID}\n"
                                             f" * Symbol:               {symbol}\n"
                                             f" * Type:                 {th_type}\n"
                                             f" * Side:                 {th_side}\n"
                                             f" * RQP Value:            {th_rqpVal}\n"
                                             f" * Generation Time [ns]: {th_genTime_ns}\n"
                                             f" * Quantity - Current:   {position['quantity']}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue

                #[2-5-1-5]: Finally
                self.__orderCreationRequest_generate(symbol          = symbol,
                                                     logicSource     = 'ENTRY',
                                                     side            = th_side,
                                                     quantity        = quantity,
                                                     tcTrackerUpdate = None,
                                                     ipcRID          = None)
                
            #---[2-5-2]: CLEAR
            elif th_type == 'CLEAR':
                #[2-5-2-1]: Quantity Determination
                quantity = round(abs(position['quantity']), precisions['quantity'])
                if not 0 < quantity: 
                    self.__logger(message = (f"A Trade Handler Failed Quantity Test And Will Be Discarded.\n"
                                             f" * Local ID:             {lID}\n"
                                             f" * Symbol:               {symbol}\n"
                                             f" * Type:                 {th_type}\n"
                                             f" * Side:                 {th_side}\n"
                                             f" * RQP Value:            {th_rqpVal}\n"
                                             f" * Generation Time [ns]: {th_genTime_ns}\n"
                                             f" * Quantity - Current:   {position['quantity']}\n"
                                             f" * Quantity - Trade:     {quantity}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue

                #[2-5-2-2]: Side Confirm
                if not ((position['quantity'] < 0 and th_side == 'BUY') or \
                        (0 < position['quantity'] and th_side == 'SELL')): 
                    self.__logger(message = (f"A Trade Handler Failed Side Test And Will Be Discarded.\n"
                                             f" * Local ID:             {lID}\n"
                                             f" * Symbol:               {symbol}\n"
                                             f" * Type:                 {th_type}\n"
                                             f" * Side:                 {th_side}\n"
                                             f" * RQP Value:            {th_rqpVal}\n"
                                             f" * Generation Time [ns]: {th_genTime_ns}\n"
                                             f" * Quantity - Current:   {position['quantity']}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue

                #[2-5-2-3]: Finally
                self.__orderCreationRequest_generate(symbol          = symbol,
                                                     logicSource     = 'CLEAR',
                                                     side            = th_side,
                                                     quantity        = quantity,
                                                     tcTrackerUpdate = None,
                                                     ipcRID          = None)
                
            #---[2-5-3]: EXIT
            elif th_type == 'EXIT':
                #[2-5-3-1]: Balance Commitment Check
                balance_allocated = position['allocatedBalance']                                    if position['allocatedBalance'] is not None else 0
                balance_committed = abs(position['quantity'])*position['entryPrice']/tc['leverage'] if position['entryPrice']       is not None else 0
                balance_toCommit  = balance_allocated*abs(th_rqpVal)
                balance_toEnter   = balance_toCommit-balance_committed
                if not(balance_toEnter < 0): continue

                #[2-5-3-2]: Quantity Determination
                quantity_minUnit = pow(10, -precisions['quantity'])
                quantity         = round(int((-balance_toEnter/position['entryPrice']*tc['leverage'])/quantity_minUnit)*quantity_minUnit, precisions['quantity'])
                if quantity < 0: 
                    self.__logger(message = (f"A Trade Handler Failed Quantity Test And Will Be Discarded. - 'NEGATIVE QUANTITY'\n"
                                             f" * Local ID:             {lID}\n"
                                             f" * Symbol:               {symbol}\n"
                                             f" * Type:                 {th_type}\n"
                                             f" * Side:                 {th_side}\n"
                                             f" * RQP Value:            {th_rqpVal}\n"
                                             f" * Generation Time [ns]: {th_genTime_ns}\n"
                                             f" * Quantity - Current:   {position['quantity']}\n"
                                             f" * Quantity - Trade:     {quantity}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue
                if quantity == 0: 
                    self.__logger(message = (f"A Trade Handler Failed Quantity Test And Will Be Discarded. - 'ZERO QUANTITY'\n"
                                             f" * Local ID:             {lID}\n"
                                             f" * Symbol:               {symbol}\n"
                                             f" * Type:                 {th_type}\n"
                                             f" * Side:                 {th_side}\n"
                                             f" * RQP Value:            {th_rqpVal}\n"
                                             f" * Generation Time [ns]: {th_genTime_ns}\n"
                                             f" * Quantity - Current:   {position['quantity']}\n"
                                             f" * Quantity - Trade:     {quantity}"), 
                                  logType = 'Update',
                                  color   = 'light_yellow')
                    continue

                #[2-5-3-3]: Side Confirm
                if not ((position['quantity'] < 0 and th_side == 'BUY') or \
                        (0 < position['quantity'] and th_side == 'SELL')): 
                    self.__logger(message = (f"A Trade Handler Failed Side Test And Will Be Discarded.\n"
                                             f" * Local ID:             {lID}\n"
                                             f" * Symbol:               {symbol}\n"
                                             f" * Type:                 {th_type}\n"
                                             f" * Side:                 {th_side}\n"
                                             f" * RQP Value:            {th_rqpVal}\n"
                                             f" * Generation Time [ns]: {th_genTime_ns}\n"
                                             f" * Quantity - Current:   {position['quantity']}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue

                #[2-5-3-4]: Finally
                self.__orderCreationRequest_generate(symbol          = symbol,
                                                     logicSource     = 'EXIT',
                                                     side            = th_side,
                                                     quantity        = quantity,
                                                     tcTrackerUpdate = None,
                                                     ipcRID          = None)
            #---[2-5-4]: FSLIMMED & FSLCLOSE
            elif th_type == 'FSLIMMED' or th_type == 'FSLCLOSE':
                #[2-5-4-1]: Quantity Determination
                quantity = round(abs(position['quantity']), precisions['quantity'])
                if not (0 < quantity): 
                    self.__logger(message = (f"A Trade Handler Failed Quantity Test And Will Be Discarded.\n"
                                             f" * Local ID:             {lID}\n"
                                             f" * Symbol:               {symbol}\n"
                                             f" * Type:                 {th_type}\n"
                                             f" * Side:                 {th_side}\n"
                                             f" * RQP Value:            {th_rqpVal}\n"
                                             f" * Generation Time [ns]: {th_genTime_ns}\n"
                                             f" * Quantity - Current:   {position['quantity']}\n"
                                             f" * Quantity - Trade:     {quantity}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue

                #[2-5-4-2]: Side Confirm
                if not ((position['quantity'] < 0 and th_side == 'BUY') or \
                        (0 < position['quantity'] and th_side == 'SELL')): 
                    self.__logger(message = (f"A Trade Handler Failed Side Test And Will Be Discarded.\n"
                                             f" * Local ID:             {lID}\n"
                                             f" * Symbol:               {symbol}\n"
                                             f" * Type:                 {th_type}\n"
                                             f" * Side:                 {th_side}\n"
                                             f" * RQP Value:            {th_rqpVal}\n"
                                             f" * Generation Time [ns]: {th_genTime_ns}\n"
                                             f" * Quantity - Current:   {position['quantity']}"), 
                                  logType = 'Warning',
                                  color   = 'light_magenta')
                    continue

                #[2-5-4-3]: Finally
                if   position['quantity'] < 0: slTriggeredSide = 'SHORT'
                elif 0 < position['quantity']: slTriggeredSide = 'LONG'
                self.__orderCreationRequest_generate(symbol          = symbol,
                                                     logicSource     = th_type,
                                                     side            = th_side,
                                                     quantity        = quantity,
                                                     tcTrackerUpdate = {'slExited': {'onComplete': (slTriggeredSide, th_timestamp), 
                                                                                     'onPartial':  (slTriggeredSide, th_timestamp), 
                                                                                     'onFail':     (slTriggeredSide, th_timestamp)}},
                                                     ipcRID          = None)
    
    def __orderCreationRequest_generate(self, symbol, logicSource, side, quantity, tcTrackerUpdate = None, ipcRID = None):
        #[1]: Instances
        lID        = self.__localID
        aType      = self.__accountType
        position   = self.__positions[symbol]
        precisions = position['precisions']

        #[2]: OCR Check
        if position['_orderCreationRequest'] is not None: 
            self.__logger(message = (f"OCR Generation Rejected - OCR Not Empty.\n"
                                     f" * Local ID:          {lID}\n"
                                     f" * Symbol:            {symbol}\n"
                                     f" * Logic Source:      {logicSource}\n"
                                     f" * Side:              {side}\n"
                                     f" * Quantity:          {quantity}\n"
                                     f" * TC Tracker Update: {tcTrackerUpdate}\n"
                                     f" * IPC RID:           {ipcRID}\n"
                                     ), 
                          logType = 'Warning',
                          color   = 'light_red')
            return False
        
        #[3]: OCR Generation
        if   side == 'BUY':  targetQuantity = round(position['quantity']+quantity, precisions['quantity'])
        elif side == 'SELL': targetQuantity = round(position['quantity']-quantity, precisions['quantity'])
        ocr = {'logicSource':          logicSource,
               'forceClearRID':        ipcRID,
               'originalQuantity':     position['quantity'],
               'targetQuantity':       targetQuantity,
               'orderParams':          {'symbol':     symbol,
                                        'side':       side,
                                        'type':       'MARKET',
                                        'quantity':   quantity,
                                        'reduceOnly': (logicSource != 'ENTRY')},
               'tcTrackerUpdate':      tcTrackerUpdate,
               'dispatchID':           None,
               'lastRequestReceived':  False,
               'results':              [],
               'nAttempts':            1}
        position['_orderCreationRequest'] = ocr

        #[4]: Request Dispatch
        #---[4-1]: Virtual
        if aType == ACCOUNT_TYPE_VIRTUAL:
            ocr['dispatchID'] = self.__virtualServer.createOrder(localID     = lID,
                                                                 symbol      = symbol,
                                                                 orderParams = ocr['orderParams'].copy())
        #---[4-2]: Actual
        elif aType == ACCOUNT_TYPE_ACTUAL:
            ocr['dispatchID'] = self.__ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                                                    functionID     = 'createOrder', 
                                                    functionParams = {'localID':        lID, 
                                                                      'positionSymbol': symbol, 
                                                                      'orderParams':    ocr['orderParams'].copy()}, 
                                                    farrHandler    = self.__farr_onPositionControlResponse)
        #[5]: Finally
        return True
    
    def __orderCreationRequest_regenerate(self, symbol, quantity_unfilled):
        #[1]: Instances
        lID      = self.__localID
        aType    = self.__accountType
        position = self.__positions[symbol]
        ocr      = position['_orderCreationRequest']
        
        #[1]: OCR Update
        ocr['orderParams']['quantity'] = quantity_unfilled
        ocr['lastRequestReceived']     = False
        ocr['nAttempts']               += 1
        #---[1-1]: Virtual
        if aType == ACCOUNT_TYPE_VIRTUAL:
            ocr['dispatchID'] = self.__virtualServer.createOrder(localID     = lID,
                                                                 symbol      = symbol,
                                                                 orderParams = ocr['orderParams'].copy())
        #---[1-2]: Actual
        elif aType == ACCOUNT_TYPE_ACTUAL:
            ocr['dispatchID'] = self.__ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                                                    functionID     = 'createOrder', 
                                                    functionParams = {'localID':        lID, 
                                                                      'positionSymbol': symbol, 
                                                                      'orderParams':    ocr['orderParams'].copy()}, 
                                                    farrHandler    = self.__farr_onPositionControlResponse)
    
    def __orderCreationRequest_terminate(self, symbol, quantity_new):
        #[1]: Instances
        lID      = self.__localID
        position = self.__positions[symbol]
        ocr      = position['_orderCreationRequest']

        #[2]: Update Mode Determination
        ocr_tQuantity = ocr['targetQuantity']
        ocr_oQuantity = ocr['originalQuantity']
        if quantity_new == ocr_tQuantity: 
            updateMode = 'onComplete'
        else:
            if ocr_tQuantity < ocr_oQuantity:
                if ocr_tQuantity < quantity_new and quantity_new < ocr_oQuantity: updateMode = 'onPartial'
                else:                                                             updateMode = 'onFail'
            elif ocr_oQuantity < ocr_tQuantity:
                if ocr_oQuantity < quantity_new and quantity_new < ocr_tQuantity: updateMode = 'onPartial'
                else:                                                             updateMode = 'onFail'
            else: updateMode = 'onFail'

        #[3]: Trade Control Tracker Update
        if ocr['tcTrackerUpdate'] is not None:
            self.__updateTradeControlTracker(symbol                    = symbol, 
                                             tradeControlTrackerUpdate = ocr['tcTrackerUpdate'], 
                                             updateMode                = updateMode)
            tcTracker_copied = self.__copyTradeControlTracker(tradeControlTracker = position['tradeControlTracker'])
            self.__ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                                    prdAddress    = ('ACCOUNTS', lID, 'positions', symbol, 'tradeControlTracker'), 
                                    prdContent    = tcTracker_copied)
            self.__ipcA.sendFAR(targetProcess  = 'GUI', 
                                functionID     = 'onAccountUpdate', 
                                functionParams = {'updateType': 'UPDATED_POSITION', 
                                                  'updatedContent': (lID, symbol, 'tradeControlTracker')}, 
                                farrHandler    = None)
            self.__ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                functionID     = 'editAccountData', 
                                functionParams = {'updates': [((lID, 'positions', symbol, 'tradeControlTracker'), tcTracker_copied),]}, 
                                farrHandler    = None)
            
        #[4]: Force Clear Response    
        if ocr['forceClearRID'] is not None:
            fcComplete = (updateMode == 'onComplete')
            if fcComplete: msg = f"Account '{lID}' Position '{symbol}' Position Force Clear Successful!"
            else:          msg = f"Account '{lID}' Position '{symbol}' Position Force Clear Failed"
            self.__ipcA.sendFARR(targetProcess  = 'GUI', 
                                 functionResult = {'localID':        lID, 
                                                   'positionSymbol': symbol, 
                                                   'responseOn':     'FORCECLEARPOSITION',
                                                   'result':         fcComplete,
                                                   'message':        msg}, 
                                 requestID      = ocr['forceClearRID'], 
                                 complete       = True)
            
        #[5]: OCR Initialization
        position['_orderCreationRequest'] = None
    
    def __trade_checkTrade(self, symbol, quantity_new, entryPrice_new):
        #[1]: Instances
        lID        = self.__localID
        position   = self.__positions[symbol]
        qAsset     = position['quoteAsset']
        precisions = position['precisions']
        ocr        = position['_orderCreationRequest']
        asset      = self.__assets[qAsset]

        #[2]: Trade Quantity Tracking
        if ocr is None:
            quantity_delta_filled  = 0
            quantity_unfilled      = 0
            quantity_delta_unknown = round(quantity_new-position['quantity'], precisions['quantity'])
        else:
            ocr_result      = ocr['results'][-1]
            ocr_orderResult = ocr_result['orderResult']
            ocr_orderParams = ocr['orderParams']
            quantity_delta = round(quantity_new-position['quantity'], precisions['quantity'])
            if ocr_result['result']:
                quantity_unfilled = round(ocr_orderResult['originalQuantity']-ocr_orderResult['executedQuantity'], precisions['quantity'])
                if   ocr_orderResult['side'] == 'BUY':  quantity_delta_filled =  ocr_orderResult['executedQuantity']
                elif ocr_orderResult['side'] == 'SELL': quantity_delta_filled = -ocr_orderResult['executedQuantity']
                quantity_delta_unknown = round(quantity_delta-quantity_delta_filled, precisions['quantity'])
            else:
                quantity_delta_filled  = 0
                quantity_unfilled      = ocr_orderParams['quantity']
                quantity_delta_unknown = quantity_delta

        #[3]: Quantity Deltas Handling
        #---[3-1]: Known Trade
        if ocr is not None:
            #[3-1-1]: OCR Result
            ocr_result      = ocr['results'][-1]
            ocr_orderResult = ocr_result['orderResult']
            ocr_orderParams = ocr['orderParams']
            ocrHandler      = None

            #[3-1-2]: Last Result Successful
            if ocr_result['result']:
                #[3-1-2-1]: Trade Result Interpretation
                if quantity_delta_filled != 0:
                    #[3-1-2-1-1]: Quantity
                    quantity_new      = round(position['quantity']+quantity_delta_filled,  precisions['quantity'])
                    quantity_dirDelta = round(abs(quantity_new)-abs(position['quantity']), precisions['quantity'])

                    #[3-1-2-1-2]: Cost, Profit & Entry Price (New values computed here are not in account of an unknown trade quantity, hence being the reason why quantity_new and entryPrice_new is computed, rather than being imported)
                    if 0 < quantity_dirDelta: #Position Size Increased
                        #Entry Price
                        if position['quantity'] == 0: notional_prev = 0
                        else:                         notional_prev = abs(position['quantity'])*position['entryPrice']
                        notional_new   = notional_prev+quantity_dirDelta*ocr_orderResult['averagePrice']
                        entryPrice_new = round(notional_new/abs(quantity_new), precisions['price'])
                        #Profit
                        profit = 0

                    elif quantity_dirDelta < 0: #Position Size Decreased
                        #Entry Price
                        if quantity_new == 0: entryPrice_new = None
                        else:                 entryPrice_new = position['entryPrice']
                        #Profit
                        if   ocr_orderParams['side'] == 'BUY':  profit = round(ocr_orderResult['executedQuantity']*(position['entryPrice']-ocr_orderResult['averagePrice']), precisions['quote'])
                        elif ocr_orderParams['side'] == 'SELL': profit = round(ocr_orderResult['executedQuantity']*(ocr_orderResult['averagePrice']-position['entryPrice']), precisions['quote'])
                    tradingFee        = round(ocr_orderResult['executedQuantity']*ocr_orderResult['averagePrice']*_ACTUALTRADE_MARKETTRADINGFEE, precisions['quote'])
                    walletBalance_new = round(asset['walletBalance']+profit-tradingFee,                                                          precisions['quote'])

                    #[3-1-2-1-3]: Send Trade Log Save Request to DATAMANAGER
                    tradeLog = {'timestamp':          time.time(),
                                'positionSymbol':     symbol,
                                'logicSource':        ocr['logicSource'],
                                'requestComplete':    (ocr_orderResult['originalQuantity'] == ocr_orderResult['executedQuantity']),
                                'side':               ocr_orderParams['side'],
                                'quantity':           ocr_orderResult['executedQuantity'],
                                'price':              ocr_orderResult['averagePrice'],
                                'profit':             profit,
                                'tradingFee':         tradingFee,
                                'totalQuantity':      quantity_new,
                                'entryPrice':         entryPrice_new,
                                'walletBalance':      walletBalance_new,
                                'tradeControlTracker': self.__copyTradeControlTracker(tradeControlTracker = position['tradeControlTracker'])}
                    self.__ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                        functionID     = 'addAccountTradeLog', 
                                        functionParams = {'localID':  lID, 
                                                          'tradeLog': tradeLog}, 
                                        farrHandler    = None)
                    
                    #[3-1-2-1-4]: Update Periodic Report
                    self.__updatePeriodicReport_onTrade(symbol      = symbol, 
                                                        side        = ocr_orderParams['side'], 
                                                        logicSource = ocr['logicSource'], 
                                                        profit      = profit)
                    
                    #[3-1-2-1-5]: Console Print
                    self.__logger(message = (f"Successful OCR Result Received For {lID}-{symbol}.\n"
                                             f" * LogicSource:       {tradeLog['logicSource']}\n"
                                             f" * Request Complete:  {str(tradeLog['requestComplete'])}\n"
                                             f" * Side:              {tradeLog['side']}\n"
                                             f" * Traded   Quantity: {auxiliaries.floatToString(number = ocr_orderResult['executedQuantity'], precision = precisions['quantity'])}\n"
                                             f" * Unfilled Quantity: {auxiliaries.floatToString(number = quantity_unfilled,                   precision = precisions['quantity'])}\n"
                                             f" * Price:             {auxiliaries.floatToString(number = ocr_orderResult['averagePrice'],     precision = precisions['price'])} {position['quoteAsset']}\n"
                                             f" * Profit:            {auxiliaries.floatToString(number = profit,                              precision = precisions['quote'])} {position['quoteAsset']}\n"
                                             f" * TradingFee:        {auxiliaries.floatToString(number = tradingFee,                          precision = precisions['quote'])} {position['quoteAsset']}"), 
                                  logType = 'Update', 
                                  color   = 'light_cyan')

                #[3-1-2-2]: OCR Handler Determination
                if   quantity_unfilled == 0:                                 ocrHandler = ('TERMINATE',  'COMPLETION')        #Terminate on Success
                elif ocr['nAttempts'] < _TRADE_MAXIMUMOCRGENERATIONATTEMPTS: ocrHandler = ('REGENERATE', 'PARTIALCOMPLETION') #Regenerate
                else:                                                        ocrHandler = ('TERMINATE',  'LIMITREACHED_PC')   #Terminate on Failure

            #[3-1-3]: Last Result Failed, Can Still Regenerate
            elif ocr['nAttempts'] < _TRADE_MAXIMUMOCRGENERATIONATTEMPTS:
                ocrHandler = ('REGENERATE', 'REJECTED') #Regenerate

            #[3-1-4]: Last Result Failed, Can No Longer Regenerate
            else:
                ocrHandler = ('TERMINATE', 'LIMITREACHED_RJ') #Terminate on Failure

            #[3-1-5]: Disruption Detected, Terminate
            if quantity_delta_unknown != 0 and ocrHandler[0] == 'REGENERATE': 
                ocrHandler = ('TERMINATE', 'UNKNOWNTRADEDETECTED')  #Terminate on Disruption

            #[3-1-6]: OCR Handling
            oh_type, oh_cause = ocrHandler
            #---[3-1-6-1]: Termination
            if oh_type == 'TERMINATE':  
                self.__orderCreationRequest_terminate(symbol = symbol, quantity_new = quantity_new)
                if   oh_cause == 'COMPLETION':           self.__logger(message = f"OCR Terminated For {lID}-{symbol} On Completion.",                     logType = 'Update', color = 'light_green')
                elif oh_cause == 'LIMITREACHED_PC':      self.__logger(message = f"OCR Terminated For {lID}-{symbol} On Partial Completion Limit Reach.", logType = 'Update', color = 'light_magenta')
                elif oh_cause == 'LIMITREACHED_RJ':      self.__logger(message = f"OCR Terminated For {lID}-{symbol} On Rejection Limit Reach.",          logType = 'Update', color = 'light_magenta')
                elif oh_cause == 'UNKNOWNTRADEDETECTED': self.__logger(message = f"OCR Terminated For {lID}-{symbol} On Interruption.",                   logType = 'Update', color = 'light_magenta')
            #---[3-1-6-1]: Regeneration
            elif oh_type == 'REGENERATE': 
                self.__orderCreationRequest_regenerate(symbol = symbol, quantity_unfilled = quantity_unfilled)
                if   oh_cause == 'PARTIALCOMPLETION': self.__logger(message = f"OCR Regenerated For {lID}-{symbol} On Re-Attempt For Partial Completion.", logType = 'Update', color = 'light_blue')
                elif oh_cause == 'REJECTED':          self.__logger(message = f"OCR Regenerated For {lID}-{symbol} On Re-Attempt For Rejection.",          logType = 'Update', color = 'light_blue')

        #---[3-2]: Unknown Trade
        if quantity_delta_unknown != 0:
            #[3-2-1]: Trade Log Save
            if   quantity_delta_unknown < 0: side = 'SELL'
            elif 0 < quantity_delta_unknown: side = 'BUY'
            tradeLog = {'timestamp':           time.time(),
                        'positionSymbol':      symbol,
                        'logicSource':         'UNKNOWN',
                        'requestComplete':     None,
                        'side':                side,
                        'quantity':            abs(quantity_delta_unknown),
                        'price':               None,
                        'profit':              None,
                        'tradingFee':          None,
                        'totalQuantity':       quantity_new,
                        'entryPrice':          entryPrice_new,
                        'walletBalance':       None,
                        'tradeControlTracker': self.__copyTradeControlTracker(tradeControlTracker = position['tradeControlTracker'])}
            self.__ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                functionID     = 'addAccountTradeLog', 
                                functionParams = {'localID':  lID, 
                                                  'tradeLog': tradeLog}, 
                                farrHandler    = None)

            #[3-2-2]: Update Periodic Report
            self.__updatePeriodicReport_onTrade(symbol      = symbol,
                                                side        = side,
                                                logicSource = 'UNKNOWN',
                                                profit      = None)

            #[3-2-3]: External Clearing Handling (Stop trading, assume the user is taking control / liquidation occurred)
            self.__trade_onAbruptClearing(symbol       = symbol, 
                                          clearingType = 'UNKNOWNTRADE')

            #[3-2-4]: Trade Handlers Clearing & Trade Control Initialization (In Case No Processing OCR Exists. Otherwise, in will be handlded along with the OCR)
            if ocr is None:
                position['_tradeHandlers'].clear()
                position['tradeControlTracker'] = self.__getInitializedTradeControlTracker()
                self.__ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                    functionID     = 'editAccountData', 
                                    functionParams = {'updates': [((lID, 'positions', symbol, 'tradeControlTracker'), self.__copyTradeControlTracker(tradeControlTracker = position['tradeControlTracker'])),]}, 
                                    farrHandler    = None)
                
            #[3-2-5]: Console Print
            self.__logger(message = (f"Unknown Trade Detected For {lID}-{symbol}.\n"
                                     f" * LogicSource: {tradeLog['logicSource']}\n"
                                     f" * Side:        {tradeLog['side']}\n"
                                     f" * Q_Delta:     {auxiliaries.floatToString(number = tradeLog['quantity'], precision = precisions['quantity'])}"), 
                          logType = 'Update', 
                          color   = 'light_blue')
    
    def __trade_checkConditionalExits(self, symbol, kline):
        #[1]: Instances
        position   = self.__positions[symbol]
        precisions = position['precisions']
        tc         = self.__tradeConfigurations_loaded.get(position['tradeConfigurationCode'], None)

        #[2]: System Status Check
        if not self.__tradeStatus or not position['tradeStatus'] or tc is None:
            return

        #[3]: Trade Handlers Determination
        tradeHandler_checkList = {'FSLIMMED': None,
                                  'FSLCLOSE': None}
        #---[3-1]: FSLIMMED
        fslImmed = tc['fullStopLossImmediate']
        if position['quantity'] != 0 and fslImmed is not None:
            #[3-1-1]: Holding SHORT
            if position['quantity'] < 0:
                price_FSL = round(position['entryPrice']*(1+fslImmed), precisions['price'])
                if price_FSL <= kline[KLINDEX_HIGHPRICE]: 
                    tradeHandler_checkList['FSLIMMED'] = 'BUY'

            #[3-1-2]: Holding LONG
            elif 0 < position['quantity']:
                price_FSL = round(position['entryPrice']*(1-fslImmed), precisions['price'])
                if kline[KLINDEX_LOWPRICE] <= price_FSL: 
                    tradeHandler_checkList['FSLIMMED'] = 'SELL'

        #---[3-2]: FSLCLOSE
        fslClose = tc['fullStopLossClose']
        if position['quantity'] != 0 and fslClose is not None and kline[KLINDEX_CLOSED]:
            #[3-2-1]: Holding SHORT
            if position['quantity'] < 0:
                price_FSL = round(position['entryPrice']*(1+fslClose), precisions['price'])
                if price_FSL <= kline[KLINDEX_CLOSEPRICE]: 
                    tradeHandler_checkList['FSLCLOSE'] = 'BUY'

            #[3-2-2]: Holding LONG
            elif 0 < position['quantity']:
                price_FSL = round(position['entryPrice']*(1-fslClose), precisions['price'])
                if kline[KLINDEX_CLOSEPRICE] <= price_FSL: 
                    tradeHandler_checkList['FSLCLOSE'] = 'SELL'

        #[4]: Trade Handlers Determination
        tradeHandlers = []
        if   tradeHandler_checkList['FSLIMMED'] is not None: tradeHandlers = ['FSLIMMED',]
        elif tradeHandler_checkList['FSLCLOSE'] is not None: tradeHandlers = ['FSLCLOSE',]

        #[5]: Finally
        position_ths = position['_tradeHandlers']
        for thType in tradeHandlers:
            th = {'type':              thType, 
                  'side':              tradeHandler_checkList[thType],
                  'rqpVal':            None,
                  'timestamp':         kline[KLINDEX_OPENTIME],
                  'generationTime_ns': time.time_ns()}
            position_ths.append(th)
    
    def __trade_onAbruptClearing(self, symbol, clearingType):
        #[1]: Instances
        lID         = self.__localID
        position    = self.__positions[symbol]
        acrs        = position['abruptClearingRecords']
        t_current_s = int(time.time())
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR

        #[2]: Record Update
        #---[2-1]: New Record
        acr = (t_current_s, clearingType)
        acrs.append(acr)

        #---[2-2]: Expired Removal
        t_expired_s = t_current_s-86400
        while acrs[0][0] <= t_expired_s: 
            acrs.popleft()

        #[3]: Trade Stop Evaluation
        tradeStop = False
        if clearingType == 'ESCAPE':
            nESCAPEs = sum(1 for rTime, cType in acrs if cType == 'ESCAPE')
            if 5 <= nESCAPEs: 
                tradeStop = True

        elif clearingType == 'FSL':
            nFSLs = sum(1 for rTime, cType in acrs if cType == 'FSL')
            if 2 <= nFSLs: 
                tradeStop = True

        elif clearingType == 'LIQUIDATION':  
            tradeStop = True

        elif clearingType == 'UNKNOWNTRADE':  
            tradeStop = True

        #Announcement
        if tradeStop:
            position['tradeStatus'] = False
            acrs.clear()
            func_sendPRDEDIT(targetProcess = 'GUI', 
                             prdAddress    = ('ACCOUNTS', lID, 'positions', symbol, 'tradeStatus'), 
                             prdContent    = False)
            func_sendFAR(targetProcess  = 'GUI',
                         functionID     = 'onAccountUpdate',
                         functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (lID, symbol, 'tradeStatus')},   
                         farrHandler    = None)
            func_sendFAR(targetProcess  = 'DATAMANAGER', 
                         functionID     = 'editAccountData', 
                         functionParams = {'updates': [((lID, 'positions', symbol, 'tradeStatus'), False)]}, 
                         farrHandler    = None)
        func_sendFAR(targetProcess  = 'DATAMANAGER', 
                     functionID     = 'editAccountData', 
                     functionParams = {'updates': [((lID, 'positions', symbol, 'abruptClearingRecords'), acrs.copy())]}, 
                     farrHandler    = None)
    




    #<System>
    def __logger(self, message, logType, color):
        if not self.__tmConfig[f'print_{logType}']:
            return
        time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
        msg      = f"[TRADEMANAGER-ACCOUNTWORKER-{time_str}] {message}"
        print(termcolor.colored(msg, color))
    #Internal Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #External Handlers ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<System Response>
    def onNewCurrency(self, symbol):
        #[1]: Instances
        lID      = self.__localID
        currency = self.__currencies[symbol]
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR

        #[2]: Quote Asset Check
        if currency['quoteAsset'] not in _ACCOUNT_READABLEASSETS:
            return

        #[3]: New Position Formatting
        self.__formatNewPosition(symbol     = symbol, 
                                 quoteAsset = currency['quoteAsset'], 
                                 precisions = currency['precisions'])
        position_copy = self.__positions[symbol].copy()

        #[4]: DB Update Request        
        func_sendFAR(targetProcess  = 'DATAMANAGER', 
                     functionID     = 'editAccountData', 
                     functionParams = {'updates': [((lID, 'positions', symbol, '#NEW#'), position_copy)]}, 
                     farrHandler    = None)
        
        #[5]: Announce New Position
        func_sendPRDEDIT(targetProcess = 'GUI', 
                         prdAddress    = ('ACCOUNTS', lID, 'positions', symbol), 
                         prdContent    = position_copy)
        func_sendFAR(targetProcess  = 'GUI', 
                     functionID     = 'onAccountUpdate', 
                     functionParams = {'updateType': 'UPDATED_POSITION_ADDED', 
                                       'updatedContent': (lID, symbol)}, 
                     farrHandler    = None)
        
    def onKlineStreamReceival(self, symbol, kline):
        #[1]: Position Check
        position = self.__positions.get(symbol, None)
        quantity = None if position is None else position['quantity']
        if quantity is None or quantity == 0:
            return
        
        #[2]: Kline Validity Check
        if (kline[KLINDEX_OPENPRICE]  is None or 
            kline[KLINDEX_HIGHPRICE]  is None or
            kline[KLINDEX_LOWPRICE]   is None or
            kline[KLINDEX_CLOSEPRICE] is None or
            kline[KLINDEX_CLOSED]     is None):
            return

        #[3]: Conditional Exists Check
        self.__trade_checkConditionalExits(symbol = symbol, kline = kline)
                
    def onTradeConfigurationAdd(self, tradeConfigurationCode):
        #[1]: Instances
        lID       = self.__localID
        positions = self.__positions
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR

        #[2]: Position Trade Configurations Check
        for symbol, position in positions.items():
            #[2-1]: Trade Configuration Code Check
            if position['tradeConfigurationCode'] != tradeConfigurationCode:
                continue

            #[2-2]: Previous Tradability & Traded Status Check
            pos_prevs = {'tradable':    position['tradable'],
                         'tradeStatus': position['tradeStatus']}
            
            #[2-3]: Trade Configuration Registration
            self.__registerPositionTradeConfiguration(symbol = symbol, tradeConfigurationCode = tradeConfigurationCode)
            self.__checkPositionTradability(symbol = symbol)

            #[2-4]: Updated Position Data Announcement
            for dType, val_prev in pos_prevs.items():
                val_new = position[dType]
                if val_new == val_prev:
                    continue
                func_sendPRDEDIT(targetProcess = 'GUI', 
                                 prdAddress    = ('ACCOUNTS', lID, 'positions', symbol, dType), 
                                 prdContent    = val_new)
                func_sendFAR(targetProcess  = 'GUI',
                             functionID     = 'onAccountUpdate', 
                             functionParams = {'updateType':     'UPDATED_POSITION', 
                                               'updatedContent': (lID, symbol, dType)}, 
                             farrHandler    = None)

    def onCurrencyAnalysisAdd(self, currencyAnalysisCode):
        #[1]: Instances
        lID = self.__localID
        cas = self.__currencyAnalyses
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR

        #[2]: Symbol & Position
        symbol = cas.getCurrencyAnalysisSymbol(code = currencyAnalysisCode)

        #[3]: Position Check
        position = self.__positions[symbol]
        if position['currencyAnalysisCode'] != currencyAnalysisCode:
            return
        pos_prevs = {'tradable':    position['tradable'],
                     'tradeStatus': position['tradeStatus']}
        
        #[4]: Register Currency Analysis & Check Tradability
        self.__registerPositionToCurrencyAnalysis(symbol = symbol, currencyAnalysisCode = currencyAnalysisCode)
        self.__checkPositionTradability(symbol = symbol)

        #[5]: Update Tradability & Announce
        for dType, val_prev in pos_prevs.items():
            val_new = position[dType]
            if val_new == val_prev:
                continue
            func_sendPRDEDIT(targetProcess = 'GUI', 
                             prdAddress    = ('ACCOUNTS', lID, 'positions', symbol, dType), 
                             prdContent    = val_new)
            func_sendFAR(targetProcess  = 'GUI',
                         functionID     = 'onAccountUpdate', 
                         functionParams = {'updateType':     'UPDATED_POSITION', 
                                           'updatedContent': (lID, symbol, dType)}, 
                         farrHandler    = None)
        
    def onPositionControlRequestsResponse(self, functionResult, requestID):
        #[1]: Response Handling
        self.__onPositionControlResponse(functionResult = functionResult,
                                         requestID      = requestID)

    def onAnalysisGeneration(self, currencyAnalysisCode, symbol, linearizedAnalysis):
        #[1]: Currency Analysis Code Check
        position = self.__positions[symbol]
        if position['currencyAnalysisCode'] != currencyAnalysisCode:
            return
        
        #[2]: Position Trade Status Check
        if not position['tradeStatus']:
            return

        #[3]: Update Linearized Analyses Buffer
        position_las = position['_linearizedAnalyses']
        if   position_las is None:       position['_linearizedAnalyses'] = self.__currencyAnalyses.getLinearizedAnalysis(code = position['currencyAnalysisCode'])
        elif linearizedAnalysis is None: position_las.clear()
        else:                            position_las.append(linearizedAnalysis)





    #<Getters>
    def isVirtual(self):
        return (self.__accountType == ACCOUNT_TYPE_VIRTUAL)

    def verifyPassword(self, password):
        #[1]: Password Check
        verified = bcrypt.checkpw(password.encode(encoding = "utf-8"), self.__hashedPassword)

        #[2]: Result Return
        return verified

    def getAccountDescription(self):
        ad_assets    = {assetName: asset.copy()    for assetName, asset    in self.__assets.items()}
        ad_positions = {symbol:    position.copy() for symbol,    position in self.__positions.items()}
        accountDescription = {'accountType':    self.__accountType,
                              'buid':           self.__buid,
                              'hashedPassword': self.__hashedPassword,
                              'assets':         ad_assets,
                              'positions':      ad_positions,
                              'status':         self.__status,
                              'tradeStatus':    self.__tradeStatus}
        return accountDescription
    
    def getActivationResult(self):
        #[1]: Get Result Buffer
        rb = self.__binanceInstanceGeneration_result

        #[2]: Reset Result Buffer
        self.__binanceInstanceGeneration_result = None

        #[3]: Return Result
        return rb





    #<System Control>
    def remove(self, password):
        #[1]: Password Check
        if not self.verifyPassword(password = password):
            return {'result':  False, 
                    'message': "Invalid Password"}

        #[2]: Ongoing Requests Check
        if self.__binanceInstanceGeneration_rID is not None:
            return {'result':  False, 
                    'message': "Ongoing Request: Binance Instance Generation"}
        for symbol, position in self.__positions.items():
            if position['_marginTypeControlRequest'] is not None:
                return {'result':  False, 
                        'message': "Ongoing Request: Margin Type Control"}
            elif position['_leverageControlRequest'] is not None:
                return {'result':  False, 
                        'message': "Ongoing Request: Leverage Control"}
            elif position['_orderCreationRequest'] is not None:
                return {'result':  False, 
                        'message': "Ongoing Request: Order Creation"}
        
        #[3]: Detach From All References
        for symbol in self.__positions:
            self.__unregisterPositionFromCurrencyAnalysis(symbol = symbol)
            self.__unregisterPositionTradeConfiguration(symbol   = symbol)
        
        #[4]: Binance Account Instance Removal Request
        self.__ipcA.sendFAR(targetProcess  = 'BINANCEAPI',  
                            functionID     = 'removeAccountInstance', 
                            functionParams = {'localID': self.__localID}, 
                            farrHandler    = None)

        #[5]: Database Account Instance Removal Request
        self.__ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                            functionID     = 'removeAccountDescription', 
                            functionParams = {'localID': self.__localID}, 
                            farrHandler    = None)

        #[6]: Return Result
        return {'result':  True, 
                'message': None}

    def activate(self, password, apiKey, secretKey, encrypted):
        #[1]: Password Check
        if not self.verifyPassword(password = password):
            return {'result':  False, 
                    'message': "Invalid Password"}
        
        #[2]: Type Check
        if self.__status == ACCOUNT_STATUS_ACTIVE:
            return {'result':  False, 
                    'message': "Already Activated"}
        
        #[3]: Requested Check
        if self.__binanceInstanceGeneration_rID is not None:
            return {'result':  False, 
                    'message': "Ongoing Request"}
        
        #[4]: Result Buffer Retrieval Check
        if self.__binanceInstanceGeneration_result is not None:
            return {'result':  False, 
                    'message': "Result Buffer Not Retrieved"}

        #[5]: Decryption
        if encrypted:
            try:
                fernet_key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
                cipher     = Fernet(fernet_key)
                apiKey     = cipher.decrypt(apiKey.encode()).decode()
                secretKey  = cipher.decrypt(secretKey.encode()).decode()
            except Exception as e:
                return {'result':  False, 
                        'message': f"Decryption Failed: {str(e)}"}

        #[6]: Binance Account Instance Generation Request
        dispatchID = self.__ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                                         functionID     = 'generateAccountInstance', 
                                         functionParams = {'localID':   self.__localID,
                                                           'uid':       self.__buid,
                                                           'apiKey':    apiKey,
                                                           'secretKey': secretKey},
                                         farrHandler    = self.__farr_onBinanceInstanceGenerationRequestResponse)
        self.__binanceInstanceGeneration_rID = dispatchID

        #[7]: Result Return
        return {'result':  True, 
                'message': None}

    def deactivate(self, password):
        #[1]: Password Check
        if not self.verifyPassword(password = password):
            return {'result':  False, 
                    'message': "Invalid Password"}
        
        #[2]: Type Check
        if self.__status == ACCOUNT_STATUS_INACTIVE:
            return {'result':  False, 
                    'message': "Already Deactivated"}
        
        #[3]: Requested Check
        if self.__binanceInstanceGeneration_rID is not None:
            return {'result':  False, 
                    'message': "Ongoing Request"}
        
        #[4]: Result Buffer Retrieval Check
        if self.__binanceInstanceGeneration_result is not None:
            return {'result':  False, 
                    'message': "Result Buffer Not Retrieved"}
        
        #[5]: Binance Account Instance Removal Request
        self.__ipcA.sendFAR(targetProcess  = 'BINANCEAPI', 
                            functionID     = 'removeAccountInstance', 
                            functionParams = {'localID': self.__localID}, 
                            farrHandler    = None)
        
        #[6]: Activation Update & Announcement
        self.__status = ACCOUNT_STATUS_INACTIVE
        self.__ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                                prdAddress    = ('ACCOUNTS', self.__localID, 'status'),
                                prdContent    = ACCOUNT_STATUS_INACTIVE)
        self.__ipcA.sendFAR(targetProcess  = 'GUI', 
                            functionID     = 'onAccountUpdate', 
                            functionParams = {'updateType':     'UPDATED_STATUS', 
                                              'updatedContent': self.__localID}, 
                            farrHandler    = None)

        #[7]: Result Return
        return {'result':  True, 
                'message': None}

    def update(self, assets, positions):
        #[1]: Instances
        currencies = self.__currencies

        #[2]: Preprocess Assets And Positions Data For Internal Update
        assets_pp    = {}
        positions_pp = {}
        #---[2-1]: Assets
        for asset in assets:
            #[2-1-1]: Asset Check
            assetName = asset['asset']
            if assetName not in _ACCOUNT_READABLEASSETS:
                continue

            #[2-2-2]: Wallet, Cross
            mb = asset['marginBalance']
            wb = asset['walletBalance']
            ab = asset['availableBalance']
            if mb is not None: mb = float(mb)
            if wb is not None: wb = float(wb)
            if ab is not None: ab = float(ab)

            #[2-2-3]: Finally
            assets_pp[assetName] = {'marginBalance':      mb,
                                    'walletBalance':      wb,
                                    'crossWalletBalance': float(asset['crossWalletBalance']),
                                    'availableBalance':   ab}

        #---[2-2]: Positions
        for position in positions:
            #[2-2-1]: Quote Asset Check
            symbol = position['symbol']
            if currencies[symbol]['quoteAsset'] not in _ACCOUNT_READABLEASSETS:
                continue

            #[2-2-2]: Entry Price
            ep = position['entryPrice']
            if ep is not None: ep = float(ep)
            if ep == 0:        ep = None

            #[2-2-3]: Position Initial Margin, Maintenance Margin, Unrealized PNL
            pim  = position['positionInitialMargin']
            mm   = position['maintMargin']
            uPNL = position['unrealizedProfit']
            if pim  is not None: pim  = float(pim)
            if mm   is not None: mm   = float(mm)
            if uPNL is not None: uPNL = float(uPNL)

            #[2-2-4]: Finally
            positions_pp[symbol] = {'quantity':               float(position['positionAmt']),
                                    'entryPrice':             ep,
                                    'leverage':               int(position['leverage']),
                                    'isolated':               bool(position['isolated']),
                                    'isolatedWalletBalance':  float(position['isolatedWallet']),
                                    'openOrderInitialMargin': float(position['openOrderInitialMargin']),
                                    'positionInitialMargin':  pim,
                                    'maintenanceMargin':      mm,
                                    'unrealizedPNL':          uPNL}
                    
        #[3]: Update the account using the imported data
        self.__update(assets = assets_pp, positions = positions_pp)

        #[4]: Periodic Report Update
        self.__updatePeriodicReport(lastPeriodicReport = None)
    
    def setAccountTradeStatus(self, password, newStatus):
        #[1]: Password Check
        if not self.verifyPassword(password = password):
            return {'result':  False, 
                    'message': "Invalid Password"}

        #[2]: Trade Status Update & Announcement
        self.__tradeStatus = newStatus
        self.__ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                                prdAddress    = ('ACCOUNTS', self.__localID, 'tradeStatus'), 
                                prdContent    = newStatus)
        self.__ipcA.sendFAR(targetProcess  = 'GUI', 
                            functionID     = 'onAccountUpdate', 
                            functionParams = {'updateType':     'UPDATED_TRADESTATUS', 
                                              'updatedContent': self.__localID}, 
                            farrHandler    = None)

        #[3]: Result Return
        return {'result':  True,
                'message': None}
    
    def transferBalance(self, password, assetName, amount):
        #[1]: Password Check
        if not self.verifyPassword(password = password):
            return {'result':  False, 
                    'message': "Invalid Password"}

        #[2]: Account Type Check
        if self.__accountType != ACCOUNT_TYPE_VIRTUAL:
            return {'result':  False,
                    'message': "Not A Virtual Account"}

        #[3]: Balance Transfer
        vs = self.__virtualServer
        vs.transferBalance(localID   = self.__localID, 
                           assetName = assetName, 
                           amount    = amount)

        #[4]: Result Return
        return {'result':  True,
                'message': None}
    
    def updateAllocationRatio(self, password, assetName, newAllocationRatio):
        #[1]: Password Check
        if not self.verifyPassword(password = password):
            return {'result':  False, 
                    'message': "Invalid Password"}
        
        #[2]: Allocation Update & Announcement
        asset = self.__assets[assetName]
        if newAllocationRatio < 0: newAllocationRatio = 0
        if 1 < newAllocationRatio: newAllocationRatio = 1
        asset['allocationRatio'] = newAllocationRatio
        self.__ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                                prdAddress    = ('ACCOUNTS', self.__localID, 'assets', assetName, 'allocationRatio'), 
                                prdContent    = newAllocationRatio)
        self.__ipcA.sendFAR(targetProcess  = 'GUI', 
                            functionID     = 'onAccountUpdate', 
                            functionParams = {'updateType': 'UPDATED_ASSET', 'updatedContent': (self.__localID, assetName, 'allocationRatio')}, 
                            farrHandler    = None)
        self.__ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                            functionID     = 'editAccountData', 
                            functionParams = {'updates': [((self.__localID, 'assets', assetName, 'allocationRatio'), newAllocationRatio),]}, 
                            farrHandler    = None)

        #[3]: Result Return
        return {'result':  True,
                'message': None}
    
    def forceClearPosition(self, password, symbol, requestID):
        #[1]: Password Check
        if not self.verifyPassword(password = password):
            return {'result':  False, 
                    'message': "Invalid Password"}
        
        #[2]: OCR Check
        position = self.__positions[symbol]
        ocr      = position['_orderCreationRequest']
        if ocr is not None:
            return {'result':  False, 
                    'message': "OCR Not Empty"}
        
        #[3]: Quantity Check
        quantity = position['quantity']
        if quantity is None or quantity == 0.0:
            return {'result':  False, 
                    'message': "None/Zero-Quantity"}
        
        #[4]: Force Clearing
        #---[4-1]: Side & Quantity Determination
        if quantity < 0: 
            ocr_side     = 'BUY'
            ocr_quantity = -position['quantity']
        elif 0 < quantity: 
            ocr_side     = 'SELL'
            ocr_quantity = position['quantity']
        
        #---[4-2]: OCR Generation
        ocrGenResult = self.__orderCreationRequest_generate(symbol          = symbol, 
                                                            logicSource     = 'FORCECLEAR', 
                                                            side            = ocr_side,
                                                            quantity        = ocr_quantity,
                                                            tcTrackerUpdate = None,
                                                            ipcRID          = requestID)
        
        #[5]: Result Return
        if ocrGenResult:
            return {'result':  True, 
                    'message': None}
        else:
            return {'result':  False, 
                    'message': "OCR Generation Rejected"}
    
    def updatePositionTradeStatus(self, password, symbol, newTradeStatus):
        #[1]: Password Check
        if not self.verifyPassword(password = password):
            return {'result':  False, 
                    'message': "Invalid Password"}
        
        #[2]: New Trade Status Check
        position = self.__positions[symbol]
        if newTradeStatus and not position['tradable']:
            return {'result':  False,
                    'message': "Position Not Tradable"}
        
        #[3]: Trade Status Update & Announcement
        #---[3-1]: Trade Status
        position['tradeStatus'] = newTradeStatus
        self.__ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                                prdAddress = ('ACCOUNTS', self.__localID, 'positions', symbol, 'tradeStatus'), 
                                prdContent = newTradeStatus)
        self.__ipcA.sendFAR(targetProcess  = 'GUI', 
                            functionID     = 'onAccountUpdate', 
                            functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (self.__localID, symbol, 'tradeStatus')}, 
                            farrHandler    = None)
        self.__ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                            functionID     = 'editAccountData', 
                            functionParams = {'updates': [((self.__localID, 'positions', symbol, 'tradeStatus'), newTradeStatus)]}, 
                            farrHandler    = None)
        #---[3-2]: Abrupt Clearing Records Reset
        if newTradeStatus:
            acr = position['abruptClearingRecords']
            acr.clear()
            self.__ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                functionID     = 'editAccountData', 
                                functionParams = {'updates': [((self.__localID, 'positions', symbol, 'abruptClearingRecords'), acr.copy())]}, 
                                farrHandler    = None)
            
        #[4]: Linearized Analyses Request
        position['_linearizedAnalyses'] = None

        #[5]: Result Return
        return {'result':  True,
                'message': None}
    
    def updatePositionReduceOnly(self, password, symbol, newReduceOnly):
        #[1]: Password Check
        if not self.verifyPassword(password = password):
            return {'result':  False, 
                    'message': "Invalid Password"}

        #[2]: Reduce Only Update & Announcement
        position = self.__positions[symbol]
        position['reduceOnly'] = newReduceOnly
        self.__ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                                prdAddress = ('ACCOUNTS', self.__localID, 'positions', symbol, 'reduceOnly'), 
                                prdContent = newReduceOnly)
        self.__ipcA.sendFAR(targetProcess = 'GUI', 
                            functionID = 'onAccountUpdate', 
                            functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (self.__localID, symbol, 'reduceOnly')}, 
                            farrHandler = None)
        self.__ipcA.sendFAR(targetProcess = 'DATAMANAGER', 
                            functionID = 'editAccountData', 
                            functionParams = {'updates': [((self.__localID, 'positions', symbol, 'reduceOnly'), newReduceOnly)]}, 
                            farrHandler = None)

        #[3]: Result Return
        return {'result':  True,
                'message': None}
    
    def updatePositionTraderParams(self, password, symbol, newCurrencyAnalysisCode, newTradeConfigurationCode, newPriority, newAssumedRatio, newMaxAllocatedBalance):
        #[1]: Password Check
        if not self.verifyPassword(password = password):
            return {'result':  False, 
                    'message': "Invalid Password"}
        
        #[2]: Instances
        lID       = self.__localID
        cas       = self.__currencyAnalyses
        tcs       = self.__tradeConfigurations
        positions = self.__positions
        position  = positions[symbol]
        assetName = position['quoteAsset']
        asset     = self.__assets[assetName]
        func_sendPRDEDIT = self.__ipcA.sendPRDEDIT
        func_sendFAR     = self.__ipcA.sendFAR

        #[3]: Quantity Check
        if position['quantity'] != 0:
            return {'result':  False, 
                    'message': "Non-Zero Quantity"}
        
        #[4]: Update
        position_prev = {dKey: position[dKey] for dKey in _GUIANNOUCEMENT_POSITIONDATANAMES}
        asset_prev    = {dKey: asset[dKey]    for dKey in _GUIANNOUCEMENT_ASSETDATANAMES}
        db_uReqs      = []

        #---[4-1]: Currency Analysis Code
        if position['currencyAnalysisCode'] != newCurrencyAnalysisCode:
            if newCurrencyAnalysisCode is None or cas.exists(code = newCurrencyAnalysisCode):
                self.__registerPositionToCurrencyAnalysis(symbol = symbol, currencyAnalysisCode = newCurrencyAnalysisCode)
                db_uReqs.append(((lID, 'positions', symbol, 'currencyAnalysisCode'), position['currencyAnalysisCode']))

        #---[4-2]: Trade Configuration Code
        if position['tradeConfigurationCode'] != newTradeConfigurationCode:
            if newTradeConfigurationCode is None or tcs.exists(code = newTradeConfigurationCode):
                self.__registerPositionTradeConfiguration(symbol = symbol, tradeConfigurationCode = newTradeConfigurationCode)
                position['tradeControlTracker'] = self.__getInitializedTradeControlTracker()
                db_uReqs.append(((lID, 'positions', symbol, 'tradeConfigurationCode'), position['tradeConfigurationCode']))
                db_uReqs.append(((lID, 'positions', symbol, 'tradeControlTracker'),    self.__copyTradeControlTracker(position['tradeControlTracker'])))

        #---[4-3]: Priority
        if position['priority'] != newPriority:
            if isinstance(newPriority, int) and 1 <= newPriority <= len(positions):
                #[4-3-1]: Effected Positions Update
                puSymbols = []
                if position['priority'] < newPriority: 
                    tp0   = position['priority']+1
                    tp1   = newPriority
                    delta = -1
                elif newPriority < position['priority']: 
                    tp0   = newPriority
                    tp1   = position['priority']-1
                    delta = 1
                for _symbol, _position in positions.items():
                    if not (tp0 <= _position['priority'] <= tp1):
                        continue
                    _position['priority'] += delta
                    puSymbols.append(_symbol)
                for _symbol in puSymbols:
                    func_sendPRDEDIT(targetProcess = 'GUI', 
                                     prdAddress    = ('ACCOUNTS', lID, 'positions', _symbol, 'priority'), 
                                     prdContent    = positions[_symbol]['priority'])
                    func_sendFAR(targetProcess  = 'GUI', 
                                 functionID     = 'onAccountUpdate', 
                                 functionParams = {'updateType': 'UPDATED_POSITION', 
                                                   'updatedContent': (lID, _symbol, 'priority')}, 
                                 farrHandler    = None)

                #[4-3-2]: Target Position Update
                position['priority'] = newPriority
                db_uReqs.append(((lID, 'positions', symbol, 'priority'), position['priority']))

        #---[4-4]: Assumed Ratio
        if position['assumedRatio'] != newAssumedRatio:
            if isinstance(newAssumedRatio, (int, float)):
                if newAssumedRatio < 0: newAssumedRatio = 0
                if 1 < newAssumedRatio: newAssumedRatio = 1
                position['assumedRatio'] = newAssumedRatio
                db_uReqs.append(((lID, 'positions', symbol, 'assumedRatio'), newAssumedRatio))

        #---[4-5]: Max Allocated Balance
        if position['maxAllocatedBalance'] != newMaxAllocatedBalance:
            if isinstance(newMaxAllocatedBalance, (int, float)):
                newMaxAllocatedBalance = max(0, newMaxAllocatedBalance)
                position['maxAllocatedBalance'] = newMaxAllocatedBalance
                db_uReqs.append(((lID, 'positions', symbol, 'maxAllocatedBalance'), newMaxAllocatedBalance))

        #[5]: Tradability Check & MarginType and Leverage Update
        self.__checkPositionTradability(symbol           = symbol)
        self.__requestMarginTypeAndLeverageUpdate(symbol = symbol)
        tc = self.__tradeConfigurations_loaded.get(position['tradeConfigurationCode'], None)
        if tc is None: position['weightedAssumedRatio'] = None
        else:          position['weightedAssumedRatio'] = position['assumedRatio']*tc['leverage']
        
        #[6]: DB Update Request
        if db_uReqs: 
            func_sendFAR(targetProcess  = 'DATAMANAGER', 
                         functionID     = 'editAccountData', 
                         functionParams = {'updates': db_uReqs}, 
                         farrHandler    = None)

        #[7]: GUI Announcement
        for dKey, val_prev in position_prev.items():
            val_new = position[dKey]
            if val_prev == val_new:
                continue
            func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', lID, 'positions', symbol, dKey), prdContent = val_new)
            func_sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (lID, symbol, dKey)}, farrHandler = None)
        for dKey, val_prev in asset_prev.items():
            val_new = asset[dKey]
            if val_prev == val_new:
                continue
            func_sendPRDEDIT(targetProcess = 'GUI', prdAddress = ('ACCOUNTS', lID, 'assets', assetName, dKey), prdContent = val_new)
            func_sendFAR(targetProcess = 'GUI', functionID = 'onAccountUpdate', functionParams = {'updateType': 'UPDATED_ASSET', 'updatedContent': (lID, assetName, dKey)}, farrHandler = None)
        
        #[8]: Result Return
        return {'result':  True,
                'message': None}
    
    def resetTradeControlTracker(self, password, symbol):
        #[1]: Password Check
        if not self.verifyPassword(password = password):
            return {'result':  False, 
                    'message': f"Invalid Password"}
        
        #[2]: Trade Control Reset (Run-Time Specific Parameters Are Not Reset)
        position = self.__positions[symbol]
        tcTracker_prev              = self.__copyTradeControlTracker(tradeControlTracker = position['tradeControlTracker'])
        tcTracker_new               = self.__getInitializedTradeControlTracker()
        tcTracker_new['rqpm_model'] = tcTracker_prev['rqpm_model'].copy()
        position['tradeControlTracker'] = tcTracker_new

        #[3]: Announcement
        tcTracker_copied = self.__copyTradeControlTracker(tradeControlTracker = position['tradeControlTracker'])
        self.__ipcA.sendPRDEDIT(targetProcess = 'GUI', 
                                prdAddress = ('ACCOUNTS', self.__localID, 'positions', symbol, 'tradeControlTracker'), 
                                prdContent = tcTracker_copied)
        self.__ipcA.sendFAR(targetProcess  = 'GUI', 
                            functionID     = 'onAccountUpdate', 
                            functionParams = {'updateType': 'UPDATED_POSITION', 'updatedContent': (self.__localID, symbol, 'tradeControlTracker')}, 
                            farrHandler    = None)
        self.__ipcA.sendFAR(targetProcess  = 'DATAMANAGER',
                            functionID     = 'editAccountData',
                            functionParams = {'updates': [((self.__localID, 'positions', symbol, 'tradeControlTracker'), tcTracker_copied),]}, 
                            farrHandler    = None)
            
        #[4]: Result Return
        return {'result':  True,
                'message': None}
    #External Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



