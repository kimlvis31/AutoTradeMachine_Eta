#ATM Modules
from analyzers import KLINDEX_OPENTIME, KLINDEX_CLOSETIME, KLINDEX_OPENPRICE, KLINDEX_CLOSEPRICE, KLINDEX_HIGHPRICE, KLINDEX_LOWPRICE
import ipc
import auxiliaries
import constants
import rqpfunctions
import managers.workers.currency_analysis.currency_analysis as caWorker


#Python Modules
import time
import termcolor
import json
import os
import pprint
import bcrypt
import math
import random
import base64
import hashlib
import traceback
from datetime            import datetime
from collections         import deque
from cryptography.fernet import Fernet



#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT

KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S

_CURRENCYANALYSIS_STATUSINTERPRETATIONS = {caWorker.STATUS_WAITINGNEURALNETWORK: 'WAITINGNEURALNETWORK',
                                           caWorker.STATUS_WAITINGSTREAM:        'WAITINGSTREAM',
                                           caWorker.STATUS_WAITINGDATAAVAILABLE: 'WAITINGDATAAVAILABLE',
                                           caWorker.STATUS_QUEUED:               'QUEUED',
                                           caWorker.STATUS_FETCHING:             'FETCHING',
                                           caWorker.STATUS_INITIALANALYZING:     'INITIALANALYZING',
                                           caWorker.STATUS_ANALYZING:            'ANALYZING',
                                           caWorker.STATUS_ERROR:                'ERROR'}

_ACCOUNT_ACCOUNTTYPE_VIRTUAL    = 'VIRTUAL'
_ACCOUNT_ACCOUNTTYPE_ACTUAL     = 'ACTUAL'
_ACCOUNT_ACCOUNTSTATUS_INACTIVE = 'INACTIVE'
_ACCOUNT_ACCOUNTSTATUS_ACTIVE   = 'ACTIVE'
_ACCOUNT_UPDATEINTERVAL_NS                      = 200e6
_ACCOUNT_PERIODICREPORT_ANNOUNCEMENTINTERVAL_NS = 60*1e9
_ACCOUNT_PERIODICREPORT_INTERVALID              = auxiliaries.KLINE_INTERVAL_ID_5m
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

class Account:
    def __init__(self, path_project, ipcA, tmConfig):
        pass

    
    def __handleAnalysisResults(self, localID):
        account   = self.__accounts[localID]
        positions = account['positions']
        for pSymbol, position in positions.items():
            #[1]: Currency Analysis Code
            caCode = position['currencyAnalysisCode']
            if caCode is None:                         continue
            if caCode  not in self.__currencyAnalysis: continue
            #[2]: Local Kline Data Check
            if pSymbol not in self.__currencies_lastKline: continue
            #[3]: Analysis Handling
            ca_analysisResults                     = self.__currencyAnalysis_analysisResults[caCode]
            ca_analysisResults_deta                = ca_analysisResults['data']
            ca_analysisResults_timestamps_handling = ca_analysisResults['timestamps_handling']
            for ts in position['_analysisHandling_Queue']:
                self.__handleAnalysisResult(localID            = localID, 
                                            positionSymbol     = pSymbol, 
                                            linearizedAnalysis = ca_analysisResults_deta[ts])
                ca_analysisResults_timestamps_handling[ts].remove(localID)
            position['_analysisHandling_Queue'].clear()
    
    def __handleAnalysisResult(self, localID, positionSymbol, linearizedAnalysis):
        #[1]: Instances
        account  = self.__accounts[localID]
        position = account['positions'][positionSymbol]

        #[2]: Trade Configuration Code Check
        tcCode = position['tradeConfigurationCode']
        if tcCode not in self.__tradeConfigurations_loaded: 
            return
        tcConfig  = self.__tradeConfigurations_loaded[tcCode]['config']
        tcTracker = position['tradeControlTracker']

        #[3]: Last Kline & AnalysisResult
        lastkline = self.__currencies_lastKline[positionSymbol]

        #[4]: Analysis Result Expiration Check (Whether this was historical / current)
        t_current_s       = time.time()
        la_openTime       = linearizedAnalysis['OPENTIME']
        la_closePrice     = linearizedAnalysis['KLINE_CLOSEPRICE']
        pDelta_onDispatch = abs(lastkline[KLINDEX_CLOSEPRICE]/la_closePrice-1)
        tsInterval_prev   = auxiliaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = t_current_s, nTicks = -1)
        tsInterval_this   = auxiliaries.getNextIntervalTickTimestamp(intervalID = KLINTERVAL, timestamp = t_current_s, nTicks =  0)
        if la_openTime == tsInterval_prev:
            if _TRADE_ANALYSISHANDLINGFILTER_KLINECLOSEPRICE <= pDelta_onDispatch: ar_expired = True
            else:                                                                  ar_expired = False
        elif la_openTime == tsInterval_this: ar_expired = False
        else:                                ar_expired = True

        #[5]: RQP Value
        tcConfig_rqpm_functionType   = tcConfig['rqpm_functionType']
        tcConfig_rqpm_functionParams = tcConfig['rqpm_functionParams']
        try:
            rqps = rqpfunctions.RQPMFUNCTIONS_GET_RQPVAL[tcConfig_rqpm_functionType](params             = tcConfig_rqpm_functionParams,
                                                                                             linearizedAnalysis = linearizedAnalysis, 
                                                                                             tcTracker_model    = tcTracker['rqpm_model'])
            rqpDirection, rqpValue = rqps
            print(linearizedAnalysis)
            print(f"DIRECTION: {rqpDirection}, VALUE: {rqpValue}")
            print()
        except Exception as e:
            self.__logger(message = (f"An unexpected error occurred during RQP value calculation. User attention strongly advised.\n"
                                     f" * Local ID:            {localID}\n"
                                     f" * Position Symbol:     {positionSymbol}\n"
                                     f" * RQP Function Type:   {tcConfig_rqpm_functionType}\n"
                                     f" * RQP Function Params: {tcConfig_rqpm_functionParams}\n"
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
                                     f" * Linearized Analysis: {linearizedAnalysis}\n"
                                     f" * Time:                {time.time()}"), 
                          logType = 'Warning',
                          color   = 'light_red')
            return

        #[6]: SL Exit Flag
        tct_sle = tcTracker['slExited']
        if tct_sle is not None and not ar_expired:
            tct_sle_side, tct_sle_time = tct_sle
            if (tct_sle_time < la_openTime) and (tct_sle_side != rqpDirection):
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
            
        #[7]: Trade Status Check
        if ar_expired:                  return
        if not account['tradeStatus']:  return
        if not position['tradeStatus']: return

        #[8]: Trade Handlers Determination
        tradeHandler_checkList = {'ENTRY': None,
                                  'CLEAR': None,
                                  'EXIT':  None}
        #---[8-1]: CheckList 1: CLEAR
        if   (position['quantity'] < 0) and (rqpDirection != 'SHORT'): tradeHandler_checkList['CLEAR'] = 'BUY'
        elif (0 < position['quantity']) and (rqpDirection != 'LONG'):  tradeHandler_checkList['CLEAR'] = 'SELL'
        #---[8-2]: CheckList 2: ENTRY & EXIT
        pslCheck = tcConfig['postStopLossReentry'] or (tcTracker['slExited'] is None)
        if rqpDirection == 'SHORT':  
            if pslCheck and tcConfig['direction'] in ('BOTH', 'SHORT'): 
                tradeHandler_checkList['ENTRY'] = 'SELL'
            tradeHandler_checkList['EXIT'] = 'BUY'
        elif rqpDirection == 'LONG':
            if pslCheck and tcConfig['direction'] in ('BOTH', 'LONG'): 
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
                                  +f" * Traded   Quantity: {auxiliaries.floatToString(number = _ocr_orderResult['executedQuantity'], precision = _precisions['quantity'])}\n"\
                                  +f" * Unfilled Quantity: {auxiliaries.floatToString(number = _quantity_unfilled,                   precision = _precisions['quantity'])}\n"\
                                  +f" * Price:             {auxiliaries.floatToString(number = _ocr_orderResult['averagePrice'],     precision = _precisions['price'])} {_position['quoteAsset']}\n"\
                                  +f" * Profit:            {auxiliaries.floatToString(number = _profit,                              precision = _precisions['quote'])} {_position['quoteAsset']}\n"\
                                  +f" * TradingFee:        {auxiliaries.floatToString(number = _tradingFee,                          precision = _precisions['quote'])} {_position['quoteAsset']}"
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
                          +f" * Q_Delta:     {auxiliaries.floatToString(number = _tradeLog['quantity'], precision = _precisions['quantity'])}"
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
        tc_initialized = {'slExited':   None,
                          'rqpm_model': dict()}
        return tc_initialized
    
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
            self.__handleAnalysisResults(localID = localID)
            self.__processTradeHandlers(localID  = localID)
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
        #[1]: Instances
        account     = self.__accounts[localID]
        assets      = account['assets']
        t_current_s = time.time()

        #[2]: Format Periodic Report (If needed)
        prTS, prTS_prev, pr_prev = self.__formatAccountPeriodicReport(localID = localID, timestamp = t_current_s)

        #[3]: Previous Report Announcement
        if prTS_prev is not None:
            self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER',
                              functionID     = 'updateAccountPeriodicReport', 
                              functionParams = {'localID':        localID, 
                                                'timestamp':      prTS_prev, 
                                                'periodicReport': pr_prev}, 
                              farrHandler    = None)

        #[4]: Data Import
        if importedData is not None:
            #[4-1]: Timestamp Match Check
            pr_import   = importedData['report']
            prTS_import = importedData['timestamp']
            #[4-2]: Import
            if prTS == prTS_import:
                account['_periodicReport'] = pr_import

        #[5]: Report Update
        pr_assets = account['_periodicReport']
        for assetName in assets:
            asset    = assets[assetName]
            pr_asset = pr_assets[assetName]
            #---Margin Balance
            if asset['marginBalance'] is not None:
                if pr_asset['marginBalance_open'] is None: pr_asset['marginBalance_open'] = asset['marginBalance']
                if (pr_asset['marginBalance_min'] is None) or (asset['marginBalance'] < pr_asset['marginBalance_min']): pr_asset['marginBalance_min'] = asset['marginBalance']
                if (pr_asset['marginBalance_max'] is None) or (pr_asset['marginBalance_max'] < asset['marginBalance']): pr_asset['marginBalance_max'] = asset['marginBalance']
                pr_asset['marginBalance_close'] = asset['marginBalance']
            #---Wallet Balance
            if asset['walletBalance'] is not None:
                if pr_asset['walletBalance_open'] is None: pr_asset['walletBalance_open'] = asset['walletBalance']
                if (pr_asset['walletBalance_min'] is None) or (asset['walletBalance'] < pr_asset['walletBalance_min']): pr_asset['walletBalance_min'] = asset['walletBalance']
                if (pr_asset['walletBalance_max'] is None) or (pr_asset['walletBalance_max'] < asset['walletBalance']): pr_asset['walletBalance_max'] = asset['walletBalance']
                pr_asset['walletBalance_close'] = asset['walletBalance']
            #---Commitment Rate
            cr = 0 if asset['commitmentRate'] is None else asset['commitmentRate']
            if cr < pr_asset['commitmentRate_min']: pr_asset['commitmentRate_min'] = cr
            if pr_asset['commitmentRate_max'] < cr: pr_asset['commitmentRate_max'] = cr
            pr_asset['commitmentRate_close'] = cr
            #---Risk Level
            rl = 0 if asset['riskLevel'] is None else asset['riskLevel']
            if rl < pr_asset['riskLevel_min']: pr_asset['riskLevel_min'] = rl
            if pr_asset['riskLevel_max'] < rl: pr_asset['riskLevel_max'] = rl
            pr_asset['riskLevel_close'] = rl

        #[6]: Current Report Announcement
        if _ACCOUNT_PERIODICREPORT_ANNOUNCEMENTINTERVAL_NS <= time.perf_counter_ns()-account['_periodicReport_lastAnnounced_ns']:
            #[6-1]: Copy Periodic Report
            pr_copy = {assetName: pr_assets[assetName].copy() for assetName in assets}

            #[6-2]: Announcement
            self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                              functionID     = 'updateAccountPeriodicReport', 
                              functionParams = {'localID':        localID, 
                                                'timestamp':      prTS, 
                                                'periodicReport': pr_copy}, 
                              farrHandler    = None)
            
            #[6-3]: Update Last Announced Time
            account['_periodicReport_lastAnnounced_ns'] = time.perf_counter_ns()
   
    def __formatAccountPeriodicReport(self, localID, timestamp):
        #[1]: Instances
        account = self.__accounts[localID]
        assets  = account['assets']

        #[2]: Report Timestamp Check
        prTS = auxiliaries.getNextIntervalTickTimestamp(intervalID = _ACCOUNT_PERIODICREPORT_INTERVALID, timestamp = timestamp, mrktReg = None, nTicks = 0)
        if account['_periodicReport_timestamp'] == prTS: return (prTS, None, None)

        #[3]: Previous Report Save
        if account['_periodicReport_timestamp'] is None:
            pr_prev   = None
            prTS_prev = None
        else:
            pr_prev   = account['_periodicReport']
            prTS_prev = account['_periodicReport_timestamp']
            account['_periodicReport'] = None

        #[4]: New Report Formatting
        pr_assets_new = dict()
        for assetName in assets:
            asset = assets[assetName]
            mb = asset['marginBalance']
            wb = asset['walletBalance']
            cr = 0 if (asset['commitmentRate'] is None) else asset['commitmentRate']
            rl = 0 if (asset['riskLevel']      is None) else asset['riskLevel']
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
        account['_periodicReport']                  = pr_assets_new
        account['_periodicReport_timestamp']        = prTS
        account['_periodicReport_lastAnnounced_ns'] = 0

        #[6]: Result Return
        return (prTS, prTS_prev, pr_prev)
   
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
        if caCode is None:                                                    return
        if caCode  not in self.__currencyAnalysis:                            return
        if localID not in self.__currencyAnalysis[caCode]['appliedAccounts']: return
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
    

    
    def __computeLiquidationPrice(self, positionSymbol, walletBalance, quantity, entryPrice, currentPrice, maintenanceMargin, upnl, isolated = True, mm_crossTotal = 0, upnl_crossTotal = 0):
        if ((quantity == 0) or (currentPrice is None) or (maintenanceMargin is None)): return None
        else:
            _quantity_abs = abs(quantity)
            _maintenanceMarginRate, _maintenanceAmount = constants.getMaintenanceMarginRateAndAmount(positionSymbol = positionSymbol, notional = _quantity_abs*currentPrice)
            if (isolated == True): mm_others = 0;                               upnl_others = 0
            else:                  mm_others = mm_crossTotal-maintenanceMargin; upnl_others = upnl_crossTotal-upnl
            if   (quantity < 0):  _side = -1
            elif (0 < quantity):  _side =  1
            _liquidationPrice = (walletBalance-mm_others+upnl_others-maintenanceMargin+_quantity_abs*(currentPrice*_maintenanceMarginRate-entryPrice*_side))/(_quantity_abs*(_maintenanceMarginRate-_side))
            if (_liquidationPrice <= 0): _liquidationPrice = None
            return _liquidationPrice