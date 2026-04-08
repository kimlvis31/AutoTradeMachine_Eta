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

class VirtualServer:
    def __init__(self, path_project, ipcA, tmConfig):
        pass


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
            _maintenanceMarginRate, _maintenanceAmount = constants.getMaintenanceMarginRateAndAmount(positionSymbol = positionSymbol, notional = _currentNotional)
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
    