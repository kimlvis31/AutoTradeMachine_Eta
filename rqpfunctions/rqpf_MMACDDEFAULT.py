import math

"""
FUNCTION MODEL: MMACDDEFAULT

"""

KLINDEX_OPENTIME         =  0
KLINDEX_CLOSETIME        =  1
KLINDEX_OPENPRICE        =  2
KLINDEX_HIGHPRICE        =  3
KLINDEX_LOWPRICE         =  4
KLINDEX_CLOSEPRICE       =  5
KLINDEX_NTRADES          =  6
KLINDEX_VOLBASE          =  7
KLINDEX_VOLQUOTE         =  8
KLINDEX_VOLBASETAKERBUY  =  9
KLINDEX_VOLQUOTETAKERBUY = 10

DESCRIPTOR = [{'name': 'alpha',         'defaultValue': 1.0000,   'isAcceptable': lambda x: (( 0.0001 <= x)   and (x <= 5.0000)),   'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
              {'name': 'beta',          'defaultValue': 1.00,     'isAcceptable': lambda x: (( 1.00   <= x)   and (x <= 10.00)),    'str_to_val': lambda x: round(float(x), 2), 'val_to_str': lambda x: f"{x:.2f}"},
              {'name': 'delta',         'defaultValue': 0.0000,   'isAcceptable': lambda x: ((-1.0000 <= x)   and (x <= 1.0000)),   'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
              {'name': 'shortStrength', 'defaultValue': 1.000000, 'isAcceptable': lambda x: (( 0.000000 <= x) and (x <= 1.000000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
              {'name': 'longStrength',  'defaultValue': 1.000000, 'isAcceptable': lambda x: (( 0.000000 <= x) and (x <= 1.000000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"}]

"""
[1]: params: (type: tuple)
 * Function parameters tuple given in the order defined in the descriptor

[2]: kline:  (type: tuple)
 * Kline data for the current rqp value computation target
 * Strcture:
    Index  0: Open Time  (Timestamp, in seconds)
    Index  1: Close Time (Timestamp, in seconds)
    Index  2: Open Price
    Index  3: High Price
    Index  4: Low Price
    Index  5: Close Price
    Index  6: Number of Trades
    Index  7: Volume - Base Asset
    Index  8: Volume - Quote Asset
    Index  9: Volume - Base Asset - Taker Buy
    Index 10: Volume - Quote Asset - Taker Buy

[3]: linearizedAnalysis: (type: dict)
 * Linearized analysis result for the current rqp value computation target
 * Structure:
    Key: {analysisCode}_{valueCode} = value
 * Example:
    linearizedAnalysis = {'SMA_0_MA':            5132.1,
                          'PSAR_0_DCC':          3,
                          'PSAR_0_PSAR':         5214.5,
                          'SWING_0_LSTIMESTAMP': 1770004800,
                          'SWING_0_LSPRICE':     5342.1,
                          'SWING_0_LSTYPE':      1}

[4]: tcTracker_model <type: dict>
 * Trade Control Tracker designated for rqp function model. This can be setup and edited freely by the function to keep track of the rqp value computation state.
"""
def getRQPValue(params: tuple, kline: tuple, linearizedAnalysis: dict, tcTracker_model: dict) -> float | None:
    #[1]: Params
    (param_alpha,
     param_beta,
     param_delta,
     param_strength_SHORT,
     param_strength_LONG,
    ) = params

    #[2]: Analysis Reference
    la_mmacd_msDeltaAbsMARel = linearizedAnalysis.get('MMACD_MSDELTAABSMAREL', None)
    if la_mmacd_msDeltaAbsMARel is None: return (None, 0)

    #[3]: TC Tracker
    #---[3-1]: Model Verification & Initialization
    if not tcTracker_model:
        tcTracker_model['rqpVal_prev']                       = 0
        tcTracker_model['la_mmacd_msDeltaAbsMARel_prev'] = 0
    #---[3-2]: Cycle Check
    isShort_prev = (tcTracker_model['la_mmacd_msDeltaAbsMARel_prev'] < param_delta)
    isShort_this = (la_mmacd_msDeltaAbsMARel                         < param_delta)
    cycleReset   = (isShort_prev ^ isShort_this)

    #[4]: RQP Value Calculation
    #---[4-1]: Effective Parameter
    if isShort_this: param_strength_eff = param_strength_SHORT
    else:            param_strength_eff = param_strength_LONG
    #---[4-2]: MSDeltaAbsMARel Normalization
    x_sign = -1.0 if la_mmacd_msDeltaAbsMARel < 0 else 1.0
    x_abs  = pow(abs(la_mmacd_msDeltaAbsMARel/param_alpha), param_beta)
    y_norm = math.tanh(x_abs)*x_sign
    #---[4-3]: RQP Value
    width = param_delta+1.0 if isShort_this else 1.0-param_delta
    dist  = abs(y_norm-param_delta)
    rqpVal_abs = max(1-dist/max(width, 1e-9), 0.0)*param_strength_eff
    if width == 0: rqpVal_abs = 0.0
    #---[4-4]: Cyclic Minimum
    if not cycleReset: rqpVal_abs = min(rqpVal_abs, abs(tcTracker_model['rqpVal_prev']))
    #---[4-5]: Direction
    if isShort_this: rqpVal = -rqpVal_abs
    else:            rqpVal =  rqpVal_abs

    #[5]: TC Tracker Update
    tcTracker_model['rqpVal_prev']                   = rqpVal
    tcTracker_model['la_mmacd_msDeltaAbsMARel_prev'] = la_mmacd_msDeltaAbsMARel

    #[6]: Finally
    rqpDir = 'SHORT' if isShort_this else 'LONG'
    return rqpDir, rqpVal