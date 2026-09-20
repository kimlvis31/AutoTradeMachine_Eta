#ATM Modules
import auxiliaries_trade
import constants

#Python Modules
import time
import termcolor
import random
from datetime    import datetime
from collections import deque

#Constants
FORMATTEDDATATYPE_EMPTY = constants.FORMATTEDDATATYPE_EMPTY
FORMATTEDDATATYPE_DUMMY = constants.FORMATTEDDATATYPE_DUMMY
KLINDEX_OPENTIME         = constants.KLINDEX_OPENTIME
KLINDEX_CLOSETIME        = constants.KLINDEX_CLOSETIME
KLINDEX_OPENPRICE        = constants.KLINDEX_OPENPRICE
KLINDEX_HIGHPRICE        = constants.KLINDEX_HIGHPRICE
KLINDEX_LOWPRICE         = constants.KLINDEX_LOWPRICE
KLINDEX_CLOSEPRICE       = constants.KLINDEX_CLOSEPRICE
KLINDEX_NTRADES          = constants.KLINDEX_NTRADES
KLINDEX_VOLBASE          = constants.KLINDEX_VOLBASE
KLINDEX_VOLQUOTE         = constants.KLINDEX_VOLQUOTE
KLINDEX_VOLBASETAKERBUY  = constants.KLINDEX_VOLBASETAKERBUY
KLINDEX_VOLQUOTETAKERBUY = constants.KLINDEX_VOLQUOTETAKERBUY
KLINDEX_CLOSED           = constants.KLINDEX_CLOSED
KLINDEX_SOURCE           = constants.KLINDEX_SOURCE
DEPTHINDEX_OPENTIME      = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_CLOSETIME     = constants.DEPTHINDEX_CLOSETIME
DEPTHINDEX_BIDS5         = constants.DEPTHINDEX_BIDS5
DEPTHINDEX_BIDS4         = constants.DEPTHINDEX_BIDS4
DEPTHINDEX_BIDS3         = constants.DEPTHINDEX_BIDS3
DEPTHINDEX_BIDS2         = constants.DEPTHINDEX_BIDS2
DEPTHINDEX_BIDS1         = constants.DEPTHINDEX_BIDS1
DEPTHINDEX_BIDS0         = constants.DEPTHINDEX_BIDS0
DEPTHINDEX_ASKS0         = constants.DEPTHINDEX_ASKS0
DEPTHINDEX_ASKS1         = constants.DEPTHINDEX_ASKS1
DEPTHINDEX_ASKS2         = constants.DEPTHINDEX_ASKS2
DEPTHINDEX_ASKS3         = constants.DEPTHINDEX_ASKS3
DEPTHINDEX_ASKS4         = constants.DEPTHINDEX_ASKS4
DEPTHINDEX_ASKS5         = constants.DEPTHINDEX_ASKS5
DEPTHINDEX_CLOSED        = constants.DEPTHINDEX_CLOSED
DEPTHINDEX_SOURCE        = constants.DEPTHINDEX_SOURCE
KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S
_ACCOUNT_READABLEASSETS = ('USDT', 'USDC')
_ACCOUNT_ASSETPRECISIONS = {'USDT': 8,
                            'USDC': 8}

_VIRTUALTRADE_TRADINGFEE                             = auxiliaries_trade.TRADINGFEE
_VIRTUALTRADE_MARKETOPENLOSSRATE                     = 0.0015
_VIRTUALTRADE_SERVER_PROBABILITY_SUCCESS             = 0.95
_VIRTUALTRADE_SERVER_PROBABILITY_INCOMPLETEEXECUTION = 0.10

class VirtualAccount:
    #Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 tmConfig,
                 currencies,
                 localID,
                 assets,
                 positions):
        
        #[1]: System
        self.__tmConfig   = tmConfig
        self.__currencies = currencies

        #[2]: Virtual Account
        self.__localID   = localID
        self.__assets    = dict()
        self.__positions = dict()
        self.__requests = {'balance_transfer':   deque(),
                           'margin_type_update': deque(),
                           'leverage_update':    deque(),
                           'order_creation':     deque(),
                           'order_cancellation': deque()}

        #[3]: Assets & Positions Preparation
        assets_ip    = assets
        positions_ip = positions
        assets       = self.__assets
        positions    = self.__positions
        isNew        = ((assets_ip is None) and (positions_ip is None))
        #---[3-1]: Initialization Data Read
        if not isNew:
            self.__update_from_DB(assets    = assets_ip, 
                                  positions = positions_ip)
            
        #---[3-2]: Assets Formatting
        for assetName in _ACCOUNT_READABLEASSETS: 
            if assetName in assets:
                continue
            self.__formatNewAsset(assetName = assetName)

        #---[3-3]: Positions Formatting
        for symbol, currency in self.__currencies.items():
            if currency['quoteAsset'] not in _ACCOUNT_READABLEASSETS:
                continue
            if symbol in positions:
                continue
            self.__formatNewPosition(symbol       = symbol,
                                     contractType = currency['contractType'],
                                     quoteAsset   = currency['quoteAsset'],
                                     precisions   = currency['precisions'])
    #Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    



    #Internal Handlers ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __update_from_DB(self, assets, positions):
        #[1]: Instances
        assets_ip    = assets
        positions_ip = positions
        assets       = self.__assets
        positions    = self.__positions

        #[2]: Assets Formatting
        for assetName in assets_ip:
            self.__formatNewAsset(assetName = assetName)

        #[3]: Positions Formatting
        for symbol, position_ip in positions_ip.items():
            self.__formatNewPosition(symbol       = symbol,
                                     contractType = position_ip['contractType'],
                                     quoteAsset   = position_ip['quoteAsset'],
                                     precisions   = position_ip['precisions'])
            
        #[4]: Read Assets Data
        for assetName, asset_ip in assets_ip.items():
            asset = assets[assetName]
            asset['crossWalletBalance'] = asset_ip['crossWalletBalance']

        #[5]: Read Positions Data
        for symbol, position_ip in positions_ip.items():
            position = positions[symbol]
            position['quantity']               = position_ip['quantity']
            position['entryPrice']             = position_ip['entryPrice']
            position['leverage']               = position_ip['leverage']
            position['isolated']               = position_ip['isolated']
            position['isolatedWalletBalance']  = position_ip['isolatedWalletBalance']
    
    def __formatNewAsset(self, assetName):
        #[1]: Asset Formatting
        asset = {'asset':              assetName,
                 'marginBalance':      None,
                 'walletBalance':      None,
                 'crossWalletBalance': 0,
                 'availableBalance':   None,
                 '_positionSymbols':          set(),
                 '_positionSymbols_crossed':  set(),
                 '_positionSymbols_isolated': set()}
        self.__assets[assetName] = asset

    def __formatNewPosition(self, symbol, contractType, quoteAsset, precisions):
        #[1]: Position Formatting
        positions = self.__positions
        position = {'contractType': contractType,
                    'quoteAsset':   quoteAsset,
                    'precisions':   precisions,
                    #System
                    'lastValidKline': None,
                    'lastValidDepth': None,
                    'openOrders':     dict(),
                    #Base
                    'quantity':               0,
                    'entryPrice':             None,
                    'leverage':               1,
                    'isolated':               True,
                    'isolatedWalletBalance':  0,
                    'positionInitialMargin':  None,
                    'openOrderInitialMargin': 0,
                    'maintenanceMargin':      None,
                    'unrealizedPNL':          None}
        positions[symbol] = position

        #[2]: Asset Update
        asset = self.__assets[quoteAsset]
        asset['_positionSymbols'].add(symbol)
        asset['_positionSymbols_isolated'].add(symbol)

    def __check_liquidations(self):
        #[1]: Instances
        lID              = self.__localID
        assets           = self.__assets
        positions        = self.__positions
        responses        = []
        func_comLiqPrice = auxiliaries_trade.computeLiquidationPrice

        #[2]: Liquidation Price Computation Parameters
        lpcps = {}
        for assetName, asset in assets.items(): 
            symbols_crossed = asset['_positionSymbols_crossed']
            if any((position := positions[symbol])['maintenanceMargin'] is None or 
                    position['unrealizedPNL']                           is None 
                    for symbol in symbols_crossed):
                lpcps[assetName] = None
            else:
                lpcps[assetName] = {'maintenanceMargin_crossed': round(sum(positions[symbol]['maintenanceMargin'] for symbol in symbols_crossed), _ACCOUNT_ASSETPRECISIONS[assetName]), 
                                    'unrealizedPNL_crossed':     round(sum(positions[symbol]['unrealizedPNL']     for symbol in symbols_crossed), _ACCOUNT_ASSETPRECISIONS[assetName])}

        #[3]: Liquidation Checks
        for symbol, position in positions.items():
            #[3-1]: Instances
            quoteAsset = position['quoteAsset']
            precisions = position['precisions']
            quantity   = position['quantity']
            asset      = assets[quoteAsset]
            lpcp       = lpcps[quoteAsset]

            #[3-2]: LPCP Check
            if lpcp is None:
                continue

            #[3-3]: Last Valid Kline Check
            lvkl = position['lastValidKline']
            if lvkl is None:
                continue

            #[3-4]: Liquidation Price
            if position['isolated']: wb = position['isolatedWalletBalance']
            else:                    wb = asset['crossWalletBalance']
            liquidationPrice = func_comLiqPrice(positionSymbol    = symbol,
                                                walletBalance     = wb,
                                                quantity          = position['quantity'],
                                                entryPrice        = position['entryPrice'],
                                                currentPrice      = lvkl[KLINDEX_CLOSEPRICE],
                                                maintenanceMargin = position['maintenanceMargin'],
                                                upnl              = position['unrealizedPNL'],
                                                isolated          = position['isolated'],
                                                mm_crossTotal     = lpcp['maintenanceMargin_crossed'],
                                                upnl_crossTotal   = lpcp['unrealizedPNL_crossed'])
            if liquidationPrice is None:
                continue
            liquidationPrice = round(liquidationPrice, precisions['price'])
            
            #[3-5]: Liquidation Check
            if   quantity < 0: liquidated = (liquidationPrice <= lvkl[KLINDEX_HIGHPRICE])
            elif 0 < quantity: liquidated = (lvkl[KLINDEX_LOWPRICE] <= liquidationPrice)
            if liquidated:
                #[3-5-1]: Profit & Trading Fee
                if   quantity < 0: profit = round(abs(quantity)*(position['entryPrice']-liquidationPrice)-position['maintenanceMargin'], precisions['quote'])
                elif 0 < quantity: profit = round(abs(quantity)*(liquidationPrice-position['entryPrice'])-position['maintenanceMargin'], precisions['quote'])
                tradingFee = round(abs(quantity)*liquidationPrice*_VIRTUALTRADE_TRADINGFEE[position['contractType']]['MARKET']['DEFAULT'], precisions['quote'])

                #[3-5-2]: Cross Wallet Balance
                cwb_new = asset['crossWalletBalance']
                if position['isolated']: 
                    cwb_new += position['isolatedWalletBalance']
                cwb_new = max(round(cwb_new+profit-tradingFee, _ACCOUNT_ASSETPRECISIONS[quoteAsset]), 0)
                asset['crossWalletBalance'] = cwb_new

                #[3-5-3]: Open Orders Cancellation
                for coID in list(position['openOrders']):
                    requestID = position['openOrders'][coID]['requestID']
                    hResult   = self.__cancel_open_order(symbol = symbol, clientOrderID = coID)
                    resp      = {'localID':        lID,
                                 'positionSymbol': symbol,
                                 'responseOn':     'CREATEORDER',
                                 'result':         hResult['result'],
                                 'orderResult':    hResult['orderResult'],
                                 'failType':       hResult['failType'],
                                 'errorMessage':   hResult['errorMessage']}
                    responses.append((resp, requestID))

                #[3-5-4]: Position Clearing
                mm_prev   = position['maintenanceMargin']
                uPNL_prev = position['unrealizedPNL']
                position['quantity']               = 0
                position['entryPrice']             = None
                position['isolatedWalletBalance']  = 0
                position['positionInitialMargin']  = 0
                position['openOrderInitialMargin'] = 0
                position['maintenanceMargin']      = 0
                position['unrealizedPNL']          = 0

                #[3-5-5]: Asset Update
                self.__update_asset(assetName = quoteAsset)

                #[3-5-6]: LPCP Update
                if not position['isolated']: 
                    lpcp['maintenanceMargin_crossed'] = round(lpcp['maintenanceMargin_crossed']-mm_prev,   _ACCOUNT_ASSETPRECISIONS[quoteAsset])
                    lpcp['unrealizedPNL_crossed']     = round(lpcp['unrealizedPNL_crossed']    -uPNL_prev, _ACCOUNT_ASSETPRECISIONS[quoteAsset])

        #[4]: Responses Return
        return responses

    def __handle_requests_update_margin_type(self):
        #[1]: Instances
        lID       = self.__localID
        assets    = self.__assets
        positions = self.__positions
        reqs      = self.__requests['margin_type_update']
        responses = []

        #[2]: Requests
        while reqs:
            #[2-1]: Instances
            req = reqs.popleft()
            requestID  = req['requestID']
            symbol     = req['positionSymbol']
            marginType = req['marginType']

            #[2-2]: Position Check
            position = positions.get(symbol, None)
            if position is None:
                self.__logger(message = (f"A Margin Type Update Request Received On An Non-Existing Position. The Request Will Be Disposed.\n"
                                         f" * Local ID:        {lID}\n"
                                         f" * Request ID:      {requestID}\n"
                                         f" * Position Symbol: {symbol}\n"
                                         f" * Margin Type:     {marginType}"), 
                              logType = 'Warning',
                              color   = 'light_magenta')
                resp = {'localID':        lID,
                        'positionSymbol': symbol,
                        'responseOn':     'MARGINTYPEUPDATE',
                        'result':         False,
                        'failType':       'POSITIONNOTFOUND', 
                        'errorMessage':   'Non-Existing Position'}
                responses.append((resp, requestID))
                continue

            #[2-3]: Random Failing
            randFail = (_VIRTUALTRADE_SERVER_PROBABILITY_SUCCESS < random.random())

            #[2-4]: Margin Type Update
            if not randFail:
                asset = assets[position['quoteAsset']]
                if marginType == 'ISOLATED': 
                    position['isolated'] = True
                    asset['_positionSymbols_crossed'].discard(symbol)
                    asset['_positionSymbols_isolated'].add(symbol)

                elif marginType == 'CROSSED':  
                    position['isolated'] = False
                    asset['_positionSymbols_crossed'].add(symbol)
                    asset['_positionSymbols_isolated'].discard(symbol)

            #[2-5]: Result Appending
            if randFail:
                resp = {'localID':        lID, 
                        'positionSymbol': symbol, 
                        'responseOn':     'MARGINTYPEUPDATE', 
                        'result':         False, 
                        'failType':       'VIRTUALRANDOM', 
                        'errorMessage':   'Virtual Random Failure Return'}
            else:
                resp = {'localID':        lID, 
                        'positionSymbol': symbol, 
                        'responseOn':     'MARGINTYPEUPDATE', 
                        'result':         True, 
                        'failType':       None, 
                        'errorMessage':   None}
            responses.append((resp, requestID))

        #[3]: Return Responses
        return responses

    def __handle_requests_update_leverage(self):
        #[1]: Instances
        lID       = self.__localID
        positions = self.__positions
        reqs      = self.__requests['leverage_update']
        responses = []

        #[2]: Requests
        while reqs:
            #[2-1]: Instances
            req = reqs.popleft()
            requestID = req['requestID']
            symbol    = req['positionSymbol']
            leverage  = req['leverage']

            #[2-2]: Position Check
            position = positions.get(symbol, None)
            if position is None:
                self.__logger(message = (f"A Leverage Update Request Received On An Non-Existing Position. The Request Will Be Disposed.\n"
                                         f" * Local ID:        {lID}\n"
                                         f" * Request ID:      {requestID}\n"
                                         f" * Position Symbol: {symbol}\n"
                                         f" * Leverage:        {leverage}"), 
                              logType = 'Warning',
                              color   = 'light_magenta')
                resp = {'localID':        lID,
                        'positionSymbol': symbol,
                        'responseOn':     'LEVERAGEUPDATE',
                        'result':         False,
                        'failType':       'POSITIONNOTFOUND', 
                        'errorMessage':   'Non-Existing Position'}
                responses.append((resp, requestID))
                continue
            
            #[2-3]: Random Failing
            randFail = (_VIRTUALTRADE_SERVER_PROBABILITY_SUCCESS < round(random.randint(0, 100)/100, 2))

            #[2-4]: Margin Type Update
            if not randFail:
                position['leverage'] = leverage

            #[2-5]: Result Appending
            if randFail:
                resp = {'localID':        lID, 
                        'positionSymbol': symbol, 
                        'responseOn':     'LEVERAGEUPDATE', 
                        'result':         False, 
                        'failType':       'VIRTUALRANDOM', 
                        'errorMessage':   'Virtual Random Failure Return'}
            else:
                resp = {'localID':        lID, 
                        'positionSymbol': symbol, 
                        'responseOn':     'LEVERAGEUPDATE', 
                        'result':         True, 
                        'failType':       None, 
                        'errorMessage':   None}
            responses.append((resp, requestID))

        #[3]: Return Responses
        return responses

    def __handle_requests_order_creation(self):
        #[1]: Instances
        lID       = self.__localID
        positions = self.__positions
        reqs      = self.__requests['order_creation']
        reqs_wait = []
        responses = []

        #[2]: Requests Handling
        while reqs:
            #[2-1]: Instances
            req = reqs.popleft()
            requestID   = req['requestID']
            symbol      = req['positionSymbol']
            orderParams = req['orderParams']

            #[2-2]: Position Check
            position = positions.get(symbol, None)
            if position is None:
                self.__logger(message = (f"An Order Creation Request Received On An Non-Existing Position. The Request Will Be Disposed.\n"
                                         f" * Local ID:        {lID}\n"
                                         f" * Request ID:      {requestID}\n"
                                         f" * Position Symbol: {symbol}\n"
                                         f" * Order Params:    {orderParams}"), 
                              logType = 'Warning',
                              color   = 'light_magenta')
                resp = {'localID':        lID,
                        'positionSymbol': symbol,
                        'responseOn':     'CREATEORDER',
                        'result':         False,
                        'orderResult':    None,
                        'failType':       'POSITIONNOTFOUND', 
                        'errorMessage':   'Non-Existing Position'}
                responses.append((resp, requestID))
                continue

            #[2-3]: Kline Check
            lvkl = position['lastValidKline']
            if lvkl is None:
                reqs_wait.append(req)
                continue
            cp = lvkl[KLINDEX_CLOSEPRICE]

            #[2-4]: Order Params
            o_coID     = orderParams['newClientOrderId']
            o_side     = orderParams['side']
            o_type     = orderParams['type']
            o_quantity = orderParams['quantity']
            o_price    = orderParams['price']

            #[2-5]: Random Failing
            randFail = (_VIRTUALTRADE_SERVER_PROBABILITY_SUCCESS < round(random.randint(0, 100)/100, 2))
            if randFail:
                resp = {'localID':        lID, 
                        'positionSymbol': symbol, 
                        'responseOn':     'CREATEORDER', 
                        'result':         False, 
                        'orderResult':    None, 
                        'failType':       'VIRTUALRANDOM', 
                        'errorMessage':   'Virtual Random Failure Return'}
                responses.append((resp, requestID))
                continue

            #[2-6]: Order Type Handling
            #---[2-6-1]: MARKET (Trade Price Is Determined On Execution)
            if o_type == 'MARKET':
                o_price = cp

            #---[2-6-2]: LIMIT (Post Only, GTX)
            elif o_type == 'LIMIT':
                #[2-6-2-1]: Crossing Check
                if   o_side == 'BUY':  crossing = (cp <= o_price)
                elif o_side == 'SELL': crossing = (o_price <= cp)
                if crossing:
                    resp = {'localID':        lID, 
                            'positionSymbol': symbol, 
                            'responseOn':     'CREATEORDER', 
                            'result':         False, 
                            'orderResult':    None, 
                            'failType':       'APIERROR',
                            'errorMessage':   ('[Mimic] APIError(code=-5022): Due to the order could not be executed as maker, the Post Only order will be rejected. The order will not be recorded in the order history')}
                    responses.append((resp, requestID))
                    continue

            #---[2-6-3]: Unsupported Order Type
            else:
                self.__logger(message = (f"An Order Creation Request Received With An Unsupported Order Type. The Request Will Be Disposed.\n"
                                         f" * Local ID:        {lID}\n"
                                         f" * Request ID:      {requestID}\n"
                                         f" * Position Symbol: {symbol}\n"
                                         f" * Order Type:      {o_type}"), 
                              logType = 'Warning',
                              color   = 'light_magenta')
                resp = {'localID':        lID, 
                        'positionSymbol': symbol, 
                        'responseOn':     'CREATEORDER', 
                        'result':         False, 
                        'orderResult':    None, 
                        'failType':       'UNSUPPORTEDORDERTYPE', 
                        'errorMessage':   f"Unsupported Order Type: {o_type}"}
                responses.append((resp, requestID))
                continue

            #[2-7]: Open Order Registration
            order = {'clientOrderID':    o_coID,
                     'requestID':        requestID,
                     'type':             o_type,
                     'side':             o_side,
                     'quantity':         o_quantity,
                     'price':            o_price,
                     'executedQuantity': 0.0,
                     'averagePrice':     0.0,
                     '_klineOpenTS':     lvkl[KLINDEX_OPENTIME],
                     '_high':            lvkl[KLINDEX_HIGHPRICE],
                     '_low':             lvkl[KLINDEX_LOWPRICE]}
            position['openOrders'][o_coID] = order

            #[2-8]: Response Appending
            resp = {'localID':        lID, 
                    'positionSymbol': symbol, 
                    'responseOn':     'CREATEORDER', 
                    'result':         True, 
                    'orderResult':    {'clientOrderId':    o_coID,
                                       'status':           'NEW',
                                       'type':             o_type,
                                       'side':             o_side,
                                       'averagePrice':     None,
                                       'originalQuantity': o_quantity,
                                       'executedQuantity': 0.0}, 
                    'failType':       None, 
                    'errorMessage':   None}
            responses.append((resp, requestID))

        #[3]: Add Back Requests That Need To Wait
        reqs.extend(reqs_wait)

        #[4]: Responses Return
        return responses

    def __handle_requests_order_cancellation(self):
        #[1]: Instances
        lID       = self.__localID
        positions = self.__positions
        reqs      = self.__requests['order_cancellation']
        responses = []

        #[2]: Requests Handling
        while reqs:
            #[2-1]: Instances
            req = reqs.popleft()
            requestID = req['requestID']
            symbol    = req['positionSymbol']
            coID      = req['clientOrderID']

            #[2-2]: Position Check
            position = positions.get(symbol, None)
            if position is None:
                self.__logger(message = (f"An Order Cancellation Request Received On An Non-Existing Position. The Request Will Be Disposed.\n"
                                         f" * Local ID:        {lID}\n"
                                         f" * Request ID:      {requestID}\n"
                                         f" * Position Symbol: {symbol}\n"
                                         f" * Client Order ID: {coID}"), 
                              logType = 'Warning',
                              color   = 'light_magenta')
                resp = {'localID':        lID,
                        'positionSymbol': symbol,
                        'responseOn':     'CANCELORDER',
                        'result':         False,
                        'orderResult':    None,
                        'failType':       'POSITIONNOTFOUND', 
                        'errorMessage':   'Non-Existing Position'}
                responses.append((resp, requestID))
                continue

            #[2-3]: Random Failing
            randFail = (_VIRTUALTRADE_SERVER_PROBABILITY_SUCCESS < round(random.randint(0, 100)/100, 2))

            #[2-4]: Request Handling
            if not randFail:
                hResult = self.__cancel_open_order(symbol = symbol, clientOrderID = coID)

            #[2-5]: Response Appending
            if randFail:
                resp = {'localID':        lID, 
                        'positionSymbol': symbol, 
                        'responseOn':     'CANCELORDER', 
                        'result':         False, 
                        'orderResult':    None, 
                        'failType':       'VIRTUALRANDOM', 
                        'errorMessage':   'Virtual Random Failure Return'}
            else:
                resp = {'localID':        lID, 
                        'positionSymbol': symbol, 
                        'responseOn':     'CANCELORDER', 
                        'result':         hResult['result'], 
                        'orderResult':    hResult['orderResult'], 
                        'failType':       hResult['failType'], 
                        'errorMessage':   hResult['errorMessage']}
            responses.append((resp, requestID))

        #[3]: Responses Return
        return responses

    def __cancel_open_order(self, symbol, clientOrderID):
        #[1]: Instances
        position = self.__positions[symbol]
        order    = position['openOrders'].get(clientOrderID, None)

        #[2]: Order Existence Check
        if order is None:
            return {'result':       False,
                    'orderResult':  None,
                    'failType':     'ORDERNOTFOUND',
                    'errorMessage': 'Non-Existing Order'}

        #[3]: Order Removal
        del position['openOrders'][clientOrderID]

        #[4]: Result Return
        return {'result':      True,
                'orderResult': {'clientOrderId':    clientOrderID,
                                'status':           'CANCELED',
                                'type':             order['type'],
                                'side':             order['side'],
                                'averagePrice':     order['averagePrice'] if 0 < order['executedQuantity'] else None,
                                'originalQuantity': order['quantity'],
                                'executedQuantity': order['executedQuantity']},
                'failType':     None,
                'errorMessage': None}

    def __evaluate_open_orders(self):
        #[1]: Instances
        lID       = self.__localID
        positions = self.__positions
        responses = []
        func_gsp  = auxiliaries_trade.getSlippedPrice

        #[2]: Positions Loop
        for symbol, position in positions.items():
            #[2-1]: Open Orders Check
            openOrders = position['openOrders']
            if not openOrders:
                continue

            #[2-2]: Kline Check
            lvkl = position['lastValidKline']
            if lvkl is None:
                continue
            kl_openTS    = lvkl[KLINDEX_OPENTIME]
            kl_highPrice = lvkl[KLINDEX_HIGHPRICE]
            kl_lowPrice  = lvkl[KLINDEX_LOWPRICE]
            kl_closePrice = lvkl[KLINDEX_CLOSEPRICE]

            #[2-3]: Orders Loop
            precisions       = position['precisions']
            coIDs_terminated = []
            for coID, order in openOrders.items():
                #[2-3-1]: Instances
                o_type     = order['type']
                o_side     = order['side']
                o_price    = order['price']
                o_quantity = order['quantity']

                #[2-3-2]: Effective Price Range Determination
                #---(On the same kline, only the price movement beyond the registration point is considered)
                if o_type == 'LIMIT':
                    if kl_openTS == order['_klineOpenTS']:
                        range_high = kl_highPrice if order['_high'] < kl_highPrice else None
                        range_low  = kl_lowPrice  if kl_lowPrice < order['_low']   else None
                    else:
                        range_high = kl_highPrice
                        range_low  = kl_lowPrice
                    if   o_side == 'BUY':  executable = (range_low  is not None) and (range_low <= o_price)
                    elif o_side == 'SELL': executable = (range_high is not None) and (o_price <= range_high)
                    if not executable:
                        continue

                #[2-3-3]: Executed Quantity Determination
                quantity_remaining = round(o_quantity-order['executedQuantity'], precisions['quantity'])
                if quantity_remaining <= 0:
                    coIDs_terminated.append(coID)
                    continue
                if o_type == 'MARKET':
                    quantity_executed = quantity_remaining
                else:
                    icExec = (random.random() < _VIRTUALTRADE_SERVER_PROBABILITY_INCOMPLETEEXECUTION)
                    if icExec:
                        quantity_minUnit  = pow(10, -precisions['quantity'])
                        quantity_executed = round(int((quantity_remaining*random.uniform(0.1, 0.9))/quantity_minUnit)*quantity_minUnit, precisions['quantity'])
                        if quantity_executed <= 0:
                            continue
                    else:
                        quantity_executed = quantity_remaining

                #[2-3-4]: Trade Price Determination
                if o_type == 'MARKET':
                    t_price = func_gsp(side            = o_side,
                                       quantity        = quantity_executed,
                                       reference_price = o_price,
                                       depth           = position['lastValidDepth'],
                                       precision_price = precisions['price'])
                else:
                    t_price = o_price

                #[2-3-5]: Trade Execution
                self.__execute_trade(symbol    = symbol,
                                     side      = o_side,
                                     orderType = o_type,
                                     quantity  = quantity_executed,
                                     price     = t_price)

                #[2-3-6]: Order Update
                eq_prev = order['executedQuantity']
                eq_new  = round(eq_prev+quantity_executed, precisions['quantity'])
                order['averagePrice']     = round((order['averagePrice']*eq_prev+t_price*quantity_executed)/eq_new, precisions['price'])
                order['executedQuantity'] = eq_new

                #[2-3-7]: Completion Check
                if quantity_executed:
                    isFilled = (o_quantity <= eq_new)
                    if isFilled:
                        coIDs_terminated.append(coID)
                    resp = {'localID':        lID,
                            'positionSymbol': symbol,
                            'responseOn':     'CREATEORDER',
                            'result':         True,
                            'orderResult':    {'clientOrderId':    coID,
                                               'status':           'FILLED' if isFilled else 'PARTIALLY_FILLED',
                                               'type':             o_type,
                                               'side':             o_side,
                                               'averagePrice':     order['averagePrice'],
                                               'originalQuantity': o_quantity,
                                               'executedQuantity': eq_new},
                            'failType':       None,
                            'errorMessage':   None}
                    responses.append((resp, order['requestID']))

            #[2-4]: Terminated Orders Removal
            for coID in coIDs_terminated: 
                del openOrders[coID]

        #[3]: Responses Return
        return responses

    def __execute_trade(self, symbol, side, orderType, quantity, price):
        #[1]: Instances
        position   = self.__positions[symbol]
        quoteAsset = position['quoteAsset']
        asset      = self.__assets[quoteAsset]
        precisions = position['precisions']

        #[2]: Compute New Values
        #---[2-1]: Quantity
        if   side == 'BUY':  quantity_new = round(position['quantity']+quantity, precisions['quantity'])
        elif side == 'SELL': quantity_new = round(position['quantity']-quantity, precisions['quantity'])
        quantity_dirDelta = round(abs(quantity_new)-abs(position['quantity']), precisions['quantity'])

        #---[2-2]: Entry Price & Profit
        #------[2-2-1]: Entry
        if 0 <= quantity_dirDelta:
            if quantity_new == 0: 
                entryPrice_new = None
            else:
                if position['quantity'] == 0: notional_prev = 0
                else:                         notional_prev = abs(position['quantity'])*position['entryPrice']
                notional_new   = notional_prev+quantity_dirDelta*price
                entryPrice_new = round(notional_new/abs(quantity_new), precisions['price'])
            profit = 0

        #------[2-2-2]: Exit
        elif quantity_dirDelta < 0:
            if quantity_new == 0: entryPrice_new = None
            else:                 entryPrice_new = position['entryPrice']
            if   side == 'BUY':  profit = round(quantity*(position['entryPrice']-price), precisions['quote'])
            elif side == 'SELL': profit = round(quantity*(price-position['entryPrice']), precisions['quote'])

        #---[2-3]: Trading Fee
        tradingFee = round(quantity*price*_VIRTUALTRADE_TRADINGFEE[position['contractType']][orderType][quoteAsset], precisions['quote'])

        #[3]: Apply Values
        #---[3-1]: Realized PnL & Trading Fee
        position['quantity']        = quantity_new
        position['entryPrice']      = entryPrice_new
        asset['crossWalletBalance'] = round(asset['crossWalletBalance']+profit-tradingFee, precisions['quote'])

        #---[3-2]: Isolated Mode: Cross <-> Isolated Wallet Transfer
        if position['isolated']:
            if 0 <= quantity_dirDelta:   #Entry
                wb_transfer = round(quantity*price*((1/position['leverage'])+_VIRTUALTRADE_MARKETOPENLOSSRATE), precisions['quote'])
            elif quantity_dirDelta < 0:  #Exit
                if quantity_new == 0: wb_transfer = -position['isolatedWalletBalance']
                else:                 wb_transfer = -round(quantity*position['entryPrice']/position['leverage'], precisions['quote'])
            position['isolatedWalletBalance'] = round(position['isolatedWalletBalance']+wb_transfer, precisions['quote'])
            asset['crossWalletBalance']       = round(asset['crossWalletBalance']      -wb_transfer, precisions['quote'])

    def __handle_requests_transfer_balance(self):
        #[1]: Instances
        lID    = self.__localID
        assets = self.__assets
        reqs   = self.__requests['balance_transfer']

        #[2]: Requests
        assetNames_handled = set()
        while reqs:
            #[2-1]: Instances
            req = reqs.popleft()
            assetName = req['assetName']
            amount    = req['amount']
            asset     = assets.get(assetName, None)
            if asset is None:
                self.__logger(message = (f"A Balance Trasnfer Update Request Received On An Non-Existing Asset. The Request Will Be Disposed.\n"
                                         f" * Local ID:   {lID}\n"
                                         f" * Asset Name: {assetName}\n"
                                         f" * Amount:     {amount}"), 
                              logType = 'Warning',
                              color   = 'light_magenta')
                continue

            #[2-2]: Balance Update
            aBalance = asset['availableBalance']
            if aBalance is None or aBalance < 0:
                self.__logger(message = (f"A Balance Trasnfer Update Failed. None Or Negative Available Balance.\n"
                                         f" * Local ID:          {lID}\n"
                                         f" * Asset Name:        {assetName}\n"
                                         f" * Available Balance: {aBalance}\n"
                                         f" * Amount:            {amount}"), 
                              logType = 'Warning',
                              color   = 'light_magenta')
                continue
            amount                      = max(amount, -aBalance)
            asset['crossWalletBalance'] = max(0, round(asset['crossWalletBalance']+amount, _ACCOUNT_ASSETPRECISIONS[assetName]))

            #[2-3]: Updated Asset Name Collection
            assetNames_handled.add(assetName)

    def __update(self):
        #[1]: Instances
        currencies = self.__currencies
        positions  = self.__positions
        assets     = self.__assets

        #[2]: Positions
        for symbol, position in positions.items():
            #[2-1]: Instances
            asset      = assets[position['quoteAsset']]
            precisions = position['precisions']

            #[2-2]: Delisted Check
            cData       = currencies.get(symbol, None)
            info_server = None if cData       is None else cData['info_server']
            status      = None if info_server is None else info_server['status']
            if (cData is None or status == 'REMOVED') and position['quantity'] != 0:
                if not position['isolated']:
                    notionalValue               = round(abs(position['quantity'])*position['entryPrice'], precisions['quote'])
                    asset['crossWalletBalance'] = round(asset['crossWalletBalance']-notionalValue,        precisions['quote'])
                position['quantity']               = 0
                position['entryPrice']             = None
                position['isolatedWalletBalance']  = 0
                position['positionInitialMargin']  = 0
                position['openOrderInitialMargin'] = 0
                position['maintenanceMargin']      = 0
                position['unrealizedPNL']          = 0
                asset['_positionSymbols'].discard(symbol)
                asset['_positionSymbols_crossed'].discard(symbol)
                asset['_positionSymbols_isolated'].discard(symbol)

            #[2-3]: Position Data Computation
            self.__update_position(symbol = symbol)

        #[3]: Assets Data Computation
        for assetName in assets: 
            self.__update_asset(assetName = assetName)

    def __update_position(self, symbol):
        #[1]: Instances
        position   = self.__positions[symbol]
        precisions = position['precisions']
        quantity   = position['quantity']
        lvkl       = position['lastValidKline']

        #[2]: Position Initial Margin & Unrealized PNL Computation
        if quantity == 0:
            position['positionInitialMargin'] = 0
            position['maintenanceMargin']     = 0
            position['unrealizedPNL']         = 0
        elif lvkl is None:
            position['positionInitialMargin'] = None
            position['maintenanceMargin']     = None
            position['unrealizedPNL']         = None
        else:
            cp               = lvkl[KLINDEX_CLOSEPRICE]
            ep               = position['entryPrice']
            qt_abs           = abs(quantity)
            notional_current = cp*qt_abs
            position['positionInitialMargin'] = round(notional_current/position['leverage'], precisions['quote'])
            if quantity < 0: 
                position['unrealizedPNL'] = round((ep-cp)*qt_abs, precisions['quote'])
            elif 0 < quantity: 
                position['unrealizedPNL'] = round((cp-ep)*qt_abs, precisions['quote'])
            mmr, ma = auxiliaries_trade.getMaintenanceMarginRateAndAmount(positionSymbol = symbol, notional = notional_current)
            position['maintenanceMargin'] = round(notional_current*mmr-ma, precisions['quote'])

        #[3]: Open Order Initial Margin Computation
        ooim = 0.0
        for order in position['openOrders'].values():
            quantity_remaining = order['quantity']-order['executedQuantity']
            if quantity_remaining <= 0: 
                continue
            ooim += quantity_remaining*order['price']/position['leverage']
        position['openOrderInitialMargin'] = round(ooim, precisions['quote'])

    def __update_asset(self, assetName):
        #[1]: Instances
        positions = self.__positions
        asset     = self.__assets[assetName]

        #[2]: None Value Unrealized PNL Check
        if any((position := positions[symbol])['positionInitialMargin'] is None or 
               position['maintenanceMargin']                            is None or 
               position['unrealizedPNL']                                is None 
               for symbol in asset['_positionSymbols']):
            asset['availableBalance'] = None
            asset['walletBalance']    = None
            asset['marginBalance']    = None
            return

        #[3]: Compute Available, Wallet, and Margin Balance
        positionInitialMargin_crossed = sum(positions[symbol]['positionInitialMargin']  for symbol in asset['_positionSymbols_crossed'])
        unrealizedPNL_crossed         = sum(positions[symbol]['unrealizedPNL']          for symbol in asset['_positionSymbols_crossed'])
        unrealizedPNL_isolated        = sum(positions[symbol]['unrealizedPNL']          for symbol in asset['_positionSymbols_isolated'])
        walletBalance_isolated        = sum(positions[symbol]['isolatedWalletBalance']  for symbol in asset['_positionSymbols_isolated'])
        openOrderInitialMargin = sum(positions[symbol]['openOrderInitialMargin'] for symbol in asset['_positionSymbols'])
        asset['availableBalance'] = round(asset['crossWalletBalance']-positionInitialMargin_crossed+unrealizedPNL_crossed-openOrderInitialMargin, _ACCOUNT_ASSETPRECISIONS[assetName])
        asset['walletBalance']    = round(asset['crossWalletBalance']+walletBalance_isolated,                                                     _ACCOUNT_ASSETPRECISIONS[assetName])
        asset['marginBalance']    = round(asset['walletBalance']+unrealizedPNL_crossed+unrealizedPNL_isolated,                                    _ACCOUNT_ASSETPRECISIONS[assetName])
    
    def __logger(self, message, logType, color):
        if not self.__tmConfig[f'print_{logType}']:
            return
        time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
        msg      = f"[TRADEMANAGER-VIRTUALACCOUNT-{time_str}] {message}"
        print(termcolor.colored(msg, color))
    #Internal Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------







    #External Handlers ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #<Processing>
    def process(self):
        #[1]: Update Account
        self.__update()

        #[2]: Handle Requests
        responses = []
        responses.extend(self.__check_liquidations())
        responses.extend(self.__handle_requests_update_margin_type())
        responses.extend(self.__handle_requests_update_leverage())
        responses.extend(self.__handle_requests_order_creation())
        responses.extend(self.__handle_requests_order_cancellation())
        responses.extend(self.__evaluate_open_orders())
        self.__handle_requests_transfer_balance()

        #[3]: Update Account Again
        self.__update()

        #[4]: Return Responses
        return responses
    
    #<System Response>
    def onNewCurrency(self, symbol):
        #[1]: Instances
        currency = self.__currencies[symbol]

        #[2]: Quote Asset Check
        if currency['quoteAsset'] not in _ACCOUNT_READABLEASSETS:
            return

        #[3]: New Position Formatting
        self.__formatNewPosition(symbol       = symbol, 
                                 contractType = currency['contractType'],
                                 quoteAsset   = currency['quoteAsset'], 
                                 precisions   = currency['precisions'])

    def onKlineStreamReceival(self, symbol, kline):
        #[1]: Position Check
        position = self.__positions.get(symbol, None)
        if position is None:
            return
        
        #[2]: Kline Validity Check
        if (kline[KLINDEX_OPENPRICE]  is None or 
            kline[KLINDEX_HIGHPRICE]  is None or
            kline[KLINDEX_LOWPRICE]   is None or
            kline[KLINDEX_CLOSEPRICE] is None):
            return

        #[3]: Last Valid Kline Record
        position['lastValidKline'] = kline

    def onDepthStreamReceival(self, symbol, depth):
        #[1]: Position Check
        position = self.__positions.get(symbol, None)
        if position is None:
            return
        
        #[2]: Kline Validity Check
        if depth[DEPTHINDEX_SOURCE] in (FORMATTEDDATATYPE_DUMMY, FORMATTEDDATATYPE_EMPTY):
            return

        #[3]: Last Valid Kline Record
        position['lastValidDepth'] = depth



    #<Getters> 
    def getAssets(self):
        #[1]: Copy Assets
        assets_list = [{'asset': assetName,
                        'marginBalance':      asset['marginBalance'],
                        'walletBalance':      asset['walletBalance'],
                        'crossWalletBalance': asset['crossWalletBalance'],
                        'availableBalance':   asset['availableBalance']
                       } for assetName, asset in self.__assets.items()]

        #[2]: Return The Copied Assets
        return assets_list

    def getPositions(self):
        #[1]: Copy Positions
        positions_list = [{'symbol':                 symbol,
                           'positionAmt':            position['quantity'],
                           'entryPrice':             position['entryPrice'],
                           'leverage':               position['leverage'],
                           'isolated':               position['isolated'],
                           'isolatedWallet':         position['isolatedWalletBalance'],
                           'openOrderInitialMargin': position['openOrderInitialMargin'],
                           'positionInitialMargin':  position['positionInitialMargin'],
                           'maintMargin':            position['maintenanceMargin'],
                           'unrealizedProfit':       position['unrealizedPNL'],
                          } for symbol, position in self.__positions.items()]

        #[2]: Return The Copied Assets
        return positions_list





    #<Request Handlers>
    def transferBalance(self, assetName, amount):
        req = {'assetName': assetName,
               'amount':    amount}
        self.__requests['balance_transfer'].append(req)
        
    def updateMarginType(self, symbol, marginType, requestID):
        req = {'requestID':      requestID,
               'positionSymbol': symbol,
               'marginType':     marginType}
        self.__requests['margin_type_update'].append(req)

    def updateLeverage(self, symbol, leverage, requestID):
        req = {'requestID':      requestID,
               'positionSymbol': symbol,
               'leverage':       leverage}
        self.__requests['leverage_update'].append(req)

    def createOrder(self, symbol, orderParams, requestID):
        req = {'requestID':      requestID,
               'positionSymbol': symbol,
               'orderParams':    orderParams}
        self.__requests['order_creation'].append(req)

    def cancelOrder(self, symbol, clientOrderID, requestID):
        req = {'requestID':      requestID,
               'positionSymbol': symbol,
               'clientOrderID':  clientOrderID}
        self.__requests['order_cancellation'].append(req)
    #External Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


















