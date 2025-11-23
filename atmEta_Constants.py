import atmEta_Auxillaries
import binance
import math
import os
import json

KLINTERVAL        = atmEta_Auxillaries.KLINE_INTERVAL_ID_15m
KLINTERVAL_CLIENT = binance.Client.KLINE_INTERVAL_15MINUTE
KLINTERVAL_STREAM = "15m"
KLINTERVAL_S      = 60*15

ORDERBOOKACCEPTANCERANGE = 0.10 #(+-ORDERBOOKACCEPTANCERANGE/2)
WOIALPHA                 = -math.log(0.5, math.e)/(ORDERBOOKACCEPTANCERANGE/4) #Such that y == 0.5 when x == +-0.5 in the range of [-1.0, 1.0]

AGGTRADESAMPLINGINTERVAL_S    = KLINTERVAL_S
BIDSANDASKSSAMPLINGINTERVAL_S = KLINTERVAL_S
NMAXAGGTRADESSAMPLES          = int(86400*24*3/AGGTRADESAMPLINGINTERVAL_S)    #3 days worth
NMAXBIDSANDASKSSAMPLES        = int(86400*24*3/BIDSANDASKSSAMPLINGINTERVAL_S) #3 days worth

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
""" #_LEVERAGEMARGINTABLE Example
_leverageMarginTable_json_file = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'binanceFuturesLeverageMarginTable_20250814_0617.json'), 'r')
_LEVERAGEMARGINTABLE = json.loads(_leverageMarginTable_json_file.read())
_leverageMarginTable_json_file.close()

def getMaintenanceMarginRateAndAmount(positionSymbol, notional):
    if (positionSymbol in _LEVERAGEMARGINTABLE):
        _lastMaintenanceMarginRateAndAmount = None
        for _row in _LEVERAGEMARGINTABLE[positionSymbol]:
            _lastMaintenanceMarginRateAndAmount = (_row[4], _row[5])
            if ((_row[1] <= notional) and (notional < _row[2])): break
        return _lastMaintenanceMarginRateAndAmount
    else: return (0.005, 0)