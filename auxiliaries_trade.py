import os
import json
import constants
import auxiliaries

#<_LEVERAGEMARGINTABLE Example>
""" 
_LEVERAGEMARGINTABLE = {'XRPUSDT': [(1,         0,     40000, 100, 0.0050,        0),
                                    (2,     40000,     80000,  75, 0.0060,       40),
                                    (3,     80000,    150000,  50, 0.0100,      360),
                                    (4,    150000,    400000,  40, 0.0125,      735),
                                    (5,    400000,   1000000,  25, 0.0200,     3735),
                                    (6,   1000000,   2000000,  20, 0.0250,     8735),
                                    (7,   2000000,  10000000,  10, 0.0500,    58735),
                                    (8,  10000000,  20000000,   5, 0.1000,   558735),
                                    (9,  20000000,  25000000,   4, 0.1250,  1058735),
                                    (10, 25000000,  50000000,   2, 0.2500,  4183735),
                                    (11, 50000000, 100000000,   1, 0.5000, 16683735)],
                        }
"""
with open(file     = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'binance_futures_leverage_margin_table.json'), 
          mode     = 'r', 
          encoding = 'utf-8') as f:
    _LEVERAGEMARGINTABLE = json.load(f)['table']





def getMaintenanceMarginRateAndAmount(positionSymbol, notional):
    #[1]: Not Registered, Return Default
    mmRateAndAmount = (0.005, 0)
    if positionSymbol not in _LEVERAGEMARGINTABLE:
        return mmRateAndAmount
    
    #[2]: Return The Values In The Valid Range
    for row in _LEVERAGEMARGINTABLE[positionSymbol]:
        mmRateAndAmount = (row[4], row[5])
        if row[1] <= notional < row[2]: 
            break
    return mmRateAndAmount





def computeLiquidationPrice(positionSymbol, walletBalance, quantity, entryPrice, currentPrice, maintenanceMargin, upnl, isolated = True, mm_crossTotal = 0, upnl_crossTotal = 0):
    #[1]: Quantity Check
    if quantity == 0: 
        return None

    #[2]: Current Price Check
    if currentPrice is None:
        return None

    #[3]: Maintenance Margin Check
    if maintenanceMargin is None:
        return None
    
    #[4]: Liquidation Price Computation
    quantity_abs              = abs(quantity)
    maintMarginRate, maintAmt = getMaintenanceMarginRateAndAmount(positionSymbol = positionSymbol, notional = quantity_abs*currentPrice)
    if isolated: 
        mm_others   = 0
        upnl_others = 0
    else:                  
        mm_others   = mm_crossTotal-maintenanceMargin
        upnl_others = upnl_crossTotal-upnl
    if   quantity < 0:  _side = -1
    elif 0 < quantity:  _side =  1
    liqPrice = (walletBalance-mm_others+upnl_others-maintenanceMargin+quantity_abs*(currentPrice*maintMarginRate-entryPrice*_side))/(quantity_abs*(maintMarginRate-_side))
    if liqPrice <= 0: liqPrice = None
    return liqPrice





FORMATTEDDATATYPE_FETCHED    = constants.FORMATTEDDATATYPE_FETCHED
FORMATTEDDATATYPE_EMPTY      = constants.FORMATTEDDATATYPE_EMPTY
FORMATTEDDATATYPE_DUMMY      = constants.FORMATTEDDATATYPE_DUMMY
FORMATTEDDATATYPE_STREAMED   = constants.FORMATTEDDATATYPE_STREAMED
FORMATTEDDATATYPE_INCOMPLETE = constants.FORMATTEDDATATYPE_INCOMPLETE
DEPTHINDEX_OPENTIME          = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_CLOSETIME         = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_BIDS5             = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_BIDS4             = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_BIDS3             = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_BIDS2             = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_BIDS1             = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_BIDS0             = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_ASKS0             = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_ASKS1             = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_ASKS2             = constants.DEPTHINDEX_OPENTIME 
DEPTHINDEX_ASKS3             = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_ASKS4             = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_ASKS5             = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_CLOSED            = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_SOURCE            = constants.DEPTHINDEX_OPENTIME
DEPTHBINS = constants.DEPTHBINS
GSP_INDICES = {'BUY':  [DEPTHINDEX_ASKS0, DEPTHINDEX_ASKS1, DEPTHINDEX_ASKS2, DEPTHINDEX_ASKS3, DEPTHINDEX_ASKS4, DEPTHINDEX_ASKS5],
               'SELL': [DEPTHINDEX_BIDS0, DEPTHINDEX_BIDS1, DEPTHINDEX_BIDS2, DEPTHINDEX_BIDS3, DEPTHINDEX_BIDS4, DEPTHINDEX_BIDS5]}
GSP_DEFAULTPENALTY = {'BUY': 0.05, 'SELL': -0.05}
def getSlippedPrice(side, quantity, reference_price, depth_prev, precision_price):
    #[1]: Depth Check
    if depth_prev[DEPTHINDEX_SOURCE] in (FORMATTEDDATATYPE_DUMMY, FORMATTEDDATATYPE_EMPTY):
        return reference_price

    #[2]: Computation Variables
    quantity_rem            = quantity
    total_executed_notional = 0.0

    #[3]: Computation Parameters
    default_penalty     = GSP_DEFAULTPENALTY[side]
    price_worst_reached = reference_price * (1.0 + default_penalty)

    #[4]: Depth Bins Iteration & Liquidity Consumption
    for idx in GSP_INDICES[side]:
        #[4-1]: Bin
        bin_notional = depth_prev.get(idx, 0.0)
        if bin_notional <= 0:
            continue
        binRange = DEPTHBINS[idx]
        if   side == 'BUY':  pct_start = binRange[0]; pct_end = binRange[1]
        elif side == 'SELL': pct_start = binRange[1]; pct_end = binRange[0]
        p_start = reference_price * (1.0 + (pct_start / 100.0))
        p_end   = reference_price * (1.0 + (pct_end   / 100.0))
        bin_avg_price = (p_start + p_end) / 2.0
        bin_max_qty   = bin_notional / bin_avg_price
        
        #[4-2]: Worst Price Reached
        price_worst_reached = p_end
        
        #[4-3]: Execution check
        #---[4-3-1]: The Remaining Order Is Fully Filled Within This Current Bin
        if quantity_rem <= bin_max_qty:
            ratio     = quantity_rem / bin_max_qty
            p_reached = p_start + ratio * (p_end - p_start)
            chunk_avg = (p_start + p_reached) / 2.0
            total_executed_notional += (quantity_rem * chunk_avg)
            quantity_rem = 0.0
            break
        #---[4-3-2]: The Entire Bin Is Exhausted
        else:
            total_executed_notional += bin_notional
            quantity_rem -= bin_max_qty
            
    #[5]: Fat Finger Penalty Handling
    if 0 < quantity_rem:
        total_executed_notional += (quantity_rem * price_worst_reached)
        
    #[6]: Return The Final Volume-Weighted Average Execution Price
    return round(total_executed_notional / quantity, precision_price)





def getInitializedTradeControlTracker():
    tc_initialized = {'slExited':   None,
                      'teff_model': dict()}
    return tc_initialized

def updateTradeControlTracker(position, tradeControlTrackerUpdate, updateMode):
    #[1]: Instances
    tcTracker = position['tradeControlTracker']

    #[2]: Trade Control Tracker Update
    #---[2-1]: SL Exited
    if 'slExited' in tradeControlTrackerUpdate:
        tcTracker['slExited'] = tradeControlTrackerUpdate['slExited'][updateMode]

def copyTradeControlTracker(tradeControlTracker):
    tcTracker_copy = {'slExited':   tradeControlTracker['slExited'],
                      'teff_model': tradeControlTracker['teff_model'].copy()}
    return tcTracker_copy