#ATM Modules
from analyzers import KLINDEX_OPENTIME, KLINDEX_CLOSETIME, KLINDEX_OPENPRICE, KLINDEX_CLOSEPRICE, KLINDEX_HIGHPRICE, KLINDEX_LOWPRICE
import auxiliaries
import auxiliaries_trade
import constants

#Python Modules
import time
import termcolor
import random
from datetime    import datetime
from collections import deque

#Constants
KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S
_ACCOUNT_READABLEASSETS = ('USDT', 'USDC')
_ACCOUNT_ASSETPRECISIONS = {'USDT': 8,
                            'USDC': 8}
_VIRTUALTRADE_MARKETTRADINGFEE                       = 0.0005
_VIRTUALTRADE_LIQUIDATIONFEE                         = 0.0100
_VIRTUALTRADE_SERVER_PROBABILITY_SUCCESS             = 0.95
_VIRTUALTRADE_SERVER_PROBABILITY_INCOMPLETEEXECUTION = 0.00

class VirtualAccount:
    #Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 tmConfig,
                 currencies,
                 currencies_lastKline,
                 localID,
                 assets,
                 positions):
        
        #[1]: System
        self.__tmConfig             = tmConfig
        self.__currencies           = currencies
        self.__currencies_lastKline = currencies_lastKline

        #[2]: Virtual Account
        self.__localID   = localID
        self.__assets    = dict()
        self.__positions = dict()
        self.__requests = {'balance_transfer':   deque(),
                           'margin_type_update': deque(),
                           'leverage_update':    deque(),
                           'order_creation':     deque()}

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
            self.__formatNewPosition(symbol     = symbol,
                                     quoteAsset = currency['quoteAsset'],
                                     precisions = currency['precisions'])
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
            self.__formatNewPosition(symbol     = symbol,
                                     quoteAsset = position_ip['quoteAsset'],
                                     precisions = position_ip['precisions'])
            
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
        asset = {'marginBalance':      0,
                 'walletBalance':      0,
                 'crossWalletBalance': 0,
                 'availableBalance':   0,
                 '_positionSymbols':          set(),
                 '_positionSymbols_crossed':  set(),
                 '_positionSymbols_isolated': set()}
        self.__assets[assetName] = asset

    def __formatNewPosition(self, symbol, quoteAsset, precisions):
        #[1]: Position Formatting
        positions = self.__positions
        position = {'quoteAsset': quoteAsset,
                    'precisions': precisions,
                    #Base
                    'quantity':               0,
                    'entryPrice':             None,
                    'leverage':               1,
                    'isolated':               True,
                    'isolatedWalletBalance':  0,
                    'positionInitialMargin':  0,
                    'openOrderInitialMargin': 0,
                    'maintenanceMargin':      0,
                    'unrealizedPNL':          None}
        positions[symbol] = position

        #[2]: Asset Update
        asset = self.__assets[quoteAsset]
        asset['_positionSymbols'].add(symbol)
        asset['_positionSymbols_isolated'].add(symbol)

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
            amount                      = max(amount, -asset['availableBalance'])
            asset['crossWalletBalance'] = max(0, round(asset['crossWalletBalance']+amount, _ACCOUNT_ASSETPRECISIONS[assetName]))

            #[2-3]: Updated Asset Name Collection
            assetNames_handled.add(assetName)

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
        currencies_lastKlines = self.__currencies_lastKline
        lID                   = self.__localID
        assets                = self.__assets
        positions             = self.__positions
        reqs                  = self.__requests['order_creation']
        responses             = []

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
            asset      = assets[position['quoteAsset']]
            precisions = position['precisions']

            #[2-3]: Kline Check
            lk = currencies_lastKlines.get(symbol, None)
            if lk is None:
                continue
            cp = lk[KLINDEX_CLOSEPRICE]

            #[2-4]: Random Failing
            randFail = (_VIRTUALTRADE_SERVER_PROBABILITY_SUCCESS < round(random.randint(0, 100)/100, 2))

            #[2-5]: Request Handling
            if not randFail:
                #[2-5-1]: Executed Quantity
                icExec = (random.random() < _VIRTUALTRADE_SERVER_PROBABILITY_INCOMPLETEEXECUTION)
                if icExec: quantity_executed = round(orderParams['quantity']*random.randint(a = 0, b = 0)/100, precisions['quantity'])
                else:      quantity_executed = orderParams['quantity']

                #[2-5-2]: New Quantity
                if   orderParams['side'] == 'BUY':  quantity_new = round(position['quantity']+quantity_executed, precisions['quantity'])
                elif orderParams['side'] == 'SELL': quantity_new = round(position['quantity']-quantity_executed, precisions['quantity'])
                quantity_dirDelta = round(abs(quantity_new)-abs(position['quantity']), precisions['quantity'])

                #[2-5-3]: Entry Price, Proft, And Trading Fee
                #---[2-5-3-1]: Entry
                if 0 <= quantity_dirDelta:
                    #Entry Price
                    if quantity_new == 0: 
                        entryPrice_new = None
                    else:
                        if position['quantity'] == 0: notional_prev = 0
                        else:                         notional_prev = abs(position['quantity'])*position['entryPrice']
                        notional_new   = notional_prev+quantity_dirDelta*cp
                        entryPrice_new = round(notional_new/abs(quantity_new), precisions['price'])
                    #Profit
                    profit = 0
                    
                #---[2-5-3-2]: Exit
                elif quantity_dirDelta < 0:
                    #Entry Price
                    if quantity_new == 0: entryPrice_new = None
                    else:                 entryPrice_new = position['entryPrice']
                    #Profit
                    if   orderParams['side'] == 'BUY':  profit = round(quantity_executed*(position['entryPrice']-cp), precisions['quote'])
                    elif orderParams['side'] == 'SELL': profit = round(quantity_executed*(cp-position['entryPrice']), precisions['quote'])
                tradingFee = round(quantity_executed*cp*_VIRTUALTRADE_MARKETTRADINGFEE, precisions['quote'])

                #[2-5-4]: Apply Values
                position['quantity']        = quantity_new
                position['entryPrice']      = entryPrice_new
                asset['crossWalletBalance'] = round(asset['crossWalletBalance']+profit-tradingFee, precisions['quote'])
                if position['isolated']: # *** wb_transfer = Balance From 'CrossWalletBalance' -> 'IsolatedWalletBalance' (Assuming all the other additional parameters (Insurance Fund, Open-Loss, etc) to be 1% of the notional value) *** #
                    if 0 <= quantity_dirDelta: #Entry
                        wb_transfer = round(quantity_executed*cp*((1/position['leverage'])+0.01), precisions['quote'])

                    elif quantity_dirDelta < 0: #Exit
                        if quantity_new == 0: wb_transfer = -position['isolatedWalletBalance']
                        else:                 wb_transfer = -round(quantity_executed*position['entryPrice']/position['leverage'], precisions['quote'])
                    position['isolatedWalletBalance'] = round(position['isolatedWalletBalance']+wb_transfer, precisions['quote'])
                    asset['crossWalletBalance']       = round(asset['crossWalletBalance']      -wb_transfer, precisions['quote'])

            #[2-5]: Response Appending
            if randFail:
                resp = {'localID':        lID, 
                        'positionSymbol': symbol, 
                        'responseOn':     'CREATEORDER', 
                        'result':         False, 
                        'orderResult':    None, 
                        'failType':       'VIRTUALRANDOM', 
                        'errorMessage':   'Virtual Random Failure Return'}
            else:
                resp = {'localID':        lID, 
                        'positionSymbol': symbol, 
                        'responseOn':     'CREATEORDER', 
                        'result':         True, 
                        'orderResult':    {'type':             orderParams['type'],
                                           'side':             orderParams['side'],
                                           'averagePrice':     cp,
                                           'originalQuantity': orderParams['quantity'],
                                           'executedQuantity': quantity_executed}, 
                        'failType':       None, 
                        'errorMessage':   None}
            responses.append((resp, requestID))

        #[3]: Responses Return
        return responses

    def __update_position(self, symbol):
        #[1]: Instances
        position   = self.__positions[symbol]
        precisions = position['precisions']
        quantity   = position['quantity']
        lk         = self.__currencies_lastKline.get(symbol, None)

        #---Position Initial Margin & Unrealized PNL Computation
        if quantity == 0:
            position['positionInitialMargin'] = 0
            position['maintenanceMargin']     = 0
            position['unrealizedPNL']         = 0
        elif lk is None:
            position['positionInitialMargin'] = None
            position['maintenanceMargin']     = None
            position['unrealizedPNL']         = None
        else:
            cp               = lk[KLINDEX_CLOSEPRICE]
            ep               = position['entryPrice']
            qt_abs           = abs(quantity)
            notional_current = cp*qt_abs
            position['positionInitialMargin'] = round(notional_current/position['leverage'], precisions['quote'])
            if quantity < 0: 
                position['unrealizedPNL'] = round((ep-cp)*qt_abs, precisions['quote'])
            elif 0 < quantity: 
                position['unrealizedPNL'] = round((cp-ep)*qt_abs, precisions['quote'])
            mmr, ma = constants.getMaintenanceMarginRateAndAmount(positionSymbol = symbol, notional = notional_current)
            position['maintenanceMargin'] = round(notional_current*mmr-ma, precisions['quote'])

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
        asset['availableBalance'] = round(asset['crossWalletBalance']-positionInitialMargin_crossed+unrealizedPNL_crossed, _ACCOUNT_ASSETPRECISIONS[assetName])
        asset['walletBalance']    = round(asset['crossWalletBalance']+walletBalance_isolated,                              _ACCOUNT_ASSETPRECISIONS[assetName])
        asset['marginBalance']    = round(asset['walletBalance']+unrealizedPNL_crossed+unrealizedPNL_isolated,             _ACCOUNT_ASSETPRECISIONS[assetName])
    
    def __check_liquidations(self):
        #[1]: Instances
        currencies_lastKline = self.__currencies_lastKline
        assets               = self.__assets
        positions            = self.__positions
        func_comLiqPrice     = auxiliaries_trade.computeLiquidationPrice

        #[2]: Liquidation Price Computation Parameters
        lpcps = {}
        for assetName, asset in assets.items(): 
            symbols_crossed = asset['_positionSymbols_crossed']
            if any((position := positions[symbol])['maintenanceMargin'] is None or 
                   position['unrealizedPNL']                            is None 
                   for symbol in symbols_crossed):
                lpcps[assetName] = None
            else:
                lpcps[assetName] = {'maintenanceMargin_crossed': round(sum(positions[symbol]['maintenanceMargin'] for symbol in symbols_crossed), _ACCOUNT_ASSETPRECISIONS[assetName]), 
                                    'unrealizedPNL_crossed':     round(sum(positions[symbol]['unrealizedPNL']     for symbol in symbols_crossed), _ACCOUNT_ASSETPRECISIONS[assetName])}

        #[3]: Liquidation Checks
        for symbol, position in positions.items():
            #[3-1]: Instances
            assetName  = position['quoteAsset']
            precisions = position['precisions']
            quantity   = position['quantity']
            asset      = assets[assetName]
            lpcp       = lpcps[assetName]

            #[3-2]: LPCP Check
            if lpcp is None:
                continue

            #[3-3]: Last Kline Check
            lk = currencies_lastKline.get(symbol, None)
            if lk is None:
                continue

            #[3-4]: Liquidation Price
            if position['isolated']: wb = position['isolatedWalletBalance']
            else:                    wb = asset['crossWalletBalance']
            liquidationPrice = func_comLiqPrice(positionSymbol    = symbol,
                                                walletBalance     = wb,
                                                quantity          = position['quantity'],
                                                entryPrice        = position['entryPrice'],
                                                currentPrice      = lk[KLINDEX_CLOSEPRICE],
                                                maintenanceMargin = position['maintenanceMargin'],
                                                upnl              = position['unrealizedPNL'],
                                                isolated          = position['isolated'],
                                                mm_crossTotal     = lpcp['maintenanceMargin_crossed'],
                                                upnl_crossTotal   = lpcp['unrealizedPNL_crossed'])
            if liquidationPrice is None:
                continue
            
            #[3-5]: Liquidation Check
            if   quantity < 0: liquidated = (liquidationPrice <= lk[KLINDEX_HIGHPRICE])
            elif 0 < quantity: liquidated = (lk[KLINDEX_LOWPRICE] <= liquidationPrice)
            if liquidated:
                #[3-5-1]: Profit & Trading Fee
                profit     = round(quantity*(liquidationPrice-position['entryPrice']),          precisions['quote'])
                tradingFee = round(abs(quantity)*liquidationPrice*_VIRTUALTRADE_LIQUIDATIONFEE, precisions['quote'])

                #[3-5-2]: Cross Wallet Balance
                cwb_new = asset['crossWalletBalance']
                if position['isolated']: 
                    cwb_new += position['isolatedWalletBalance']
                cwb_new = max(round(cwb_new+profit-tradingFee, _ACCOUNT_ASSETPRECISIONS[assetName]), 0)
                asset['crossWalletBalance'] = cwb_new

                #[3-5-3]: Position Clearing
                mm_prev   = position['maintenanceMargin']
                uPNL_prev = position['unrealizedPNL']
                position['quantity']               = 0
                position['entryPrice']             = None
                position['isolatedWalletBalance']  = 0
                position['positionInitialMargin']  = 0
                position['openOrderInitialMargin'] = 0
                position['maintenanceMargin']      = 0
                position['unrealizedPNL']          = 0

                #[3-5-4]: Asset Update
                self.__update_asset(assetName = assetName)

                #[3-5-5]: LPCP Update
                if not position['isolated']: 
                    lpcp['maintenanceMargin_crossed'] = round(lpcp['maintenanceMargin_crossed']-mm_prev,   _ACCOUNT_ASSETPRECISIONS[assetName])
                    lpcp['unrealizedPNL_crossed']     = round(lpcp['unrealizedPNL_crossed']    -uPNL_prev, _ACCOUNT_ASSETPRECISIONS[assetName])

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
        #[1]: Handle Requests
        responses = []
        self.__handle_requests_transfer_balance()
        responses.extend(self.__handle_requests_update_margin_type())
        responses.extend(self.__handle_requests_update_leverage())
        responses.extend(self.__handle_requests_order_creation())
        self.__update()

        #[2]: Liquidations Check
        self.__check_liquidations()

        #[3]: Return Responses
        return responses
    
    #<System Response>
    def onNewCurrency(self, symbol):
        #[1]: Instances
        currency = self.__currencies[symbol]

        #[2]: Quote Asset Check
        if currency['quoteAsset'] not in _ACCOUNT_READABLEASSETS:
            return

        #[3]: New Position Formatting
        self.__formatNewPosition(currencySymbol = symbol, 
                                 quoteAsset     = currency['quoteAsset'], 
                                 precisions     = currency['precisions'])





    #<Getters> 
    def getAssets(self):
        #[1]: Copy Assets
        assets_copy = {assetName: asset.copy() for assetName, asset in self.__assets.items()}

        #[2]: Return The Copied Assets
        return assets_copy

    def getPositions(self):
        #[1]: Copy Positions
        positions_copy = {symbol: position.copy() for symbol, position in self.__positions.items()}

        #[2]: Return The Copied Assets
        return positions_copy





    #<Request Handlers>
    def transferBalance(self, assetName, amount):
        #[1]: Request Queue Appending
        req = {'assetName': assetName,
               'amount':    amount}
        self.__requests['balance_transfer'].append(req)
        
    def updateMarginType(self, symbol, marginType):
        #[1]: Request ID
        rID = f"VS_MTUR{time.perf_counter_ns():d}"

        #[2]: Request Queue Appending
        req = {'requestID':      rID,
               'positionSymbol': symbol,
               'marginType':     marginType}
        self.__requests['margin_type_update'].append(req)
        
        #[3]: Return Request ID
        return rID

    def updateLeverage(self, symbol, leverage):
        #[1]: Request ID
        rID = f"VS_LUR{time.perf_counter_ns():d}"

        #[2]: Request Queue Appending
        req = {'requestID':      rID,
               'positionSymbol': symbol,
               'leverage':       leverage}
        self.__requests['leverage_update'].append(req)
        
        #[3]: Return Request ID
        return rID

    def createOrder(self, symbol, orderParams):
        #[1]: Request ID
        rID = f"VS_OCR{time.perf_counter_ns():d}"

        #[2]: Request Queue Appending
        req = {'requestID':      rID,
               'positionSymbol': symbol,
               'orderParams':    orderParams}
        self.__requests['order_creation'].append(req)
        
        #[3]: Return Request ID
        return rID
    #External Handlers END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


















