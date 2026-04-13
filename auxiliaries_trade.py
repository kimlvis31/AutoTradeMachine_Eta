import os
import json

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
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'binanceFuturesLeverageMarginTable_20250814_0617.json'), 'r') as f:
    _LEVERAGEMARGINTABLE = json.load(f)

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