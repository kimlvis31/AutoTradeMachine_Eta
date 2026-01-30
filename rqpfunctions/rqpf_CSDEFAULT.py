"""
FUNCTION MODEL: CSDEFAULT (Classical Signal Default)

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

DESCRIPTOR = [{'name': 'delta',         'defaultValue': 0.0000, 'isAcceptable': lambda x: ((-1.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
              {'name': 'shortStrength', 'defaultValue': 1.0000, 'isAcceptable': lambda x: (( 0.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
              {'name': 'longStrength',  'defaultValue': 1.0000, 'isAcceptable': lambda x: (( 0.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"}]

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

[3]: pipResult: (type: dict)
 * PIP analysis result for the current rqp value computation target
 * Structure:
    Key 'SWINGS':       List of swing high and lows. Each element is a tuple representing a swing point. The tuple consists of three elements; point position (timestamp in seconds), point price, and swing type ('LOW'/'HIGH')
    Key '_SWINGSEARCH': Internal swing search reference data              
    Key 'CLASSICALSIGNAL':                Raw classical signal value (None, [-1, 1])
    Key 'CLASSICALSIGNAL_DELTA':          Raw classical signal value delta from the previous (None, [-1, 1])
    Key 'CLASSICALSIGNAL_FILTERED':       Filtered classical signal value (None, [-1, 1])
    Key 'CLASSICALSIGNAL_FILTERED_DELTA': Filtered classical signal valu delta (None, [-1, 1])
    Key 'CLASSICALSIGNAL_CYCLE':          Classical signal cycle type (None/'LOW'/'HIGH')
    Key 'CLASSICALSIGNAL_CYCLEUPDATED':   Whether classical signal cycle has reversed (False, True)
    Key 'NEARIVPBOUNDARIES': 10 Closest IVP boundaries as relative price deviation (= (price_boundary/price_current)-1) in a tuple. The first 5 are the boundaries below, and the later 5 are the boundaries above, respect to the current kline close price     
    Key '_analysisCount': Internal analysis counter

[4]: tcTracker_model <type: dict>
 * Trade Control Tracker designated for rqp function model. This can be setup and edited freely by the function to keep track of the rqp value computation state.
"""
def getRQPValue(params: tuple, kline: tuple, linearizedAnalysis: dict, tcTracker_model: dict) -> float | None:
    #[1]: Params
    (param_delta,
     param_strength_SHORT,
     param_strength_LONG,
    ) = params

    #[2]: PIP Signal
    _pr_csf = pipResult['CLASSICALSIGNAL_FILTERED']
    if (_pr_csf is None): return None

    #[3]: TC Tracker
    #---[3-1]: Model Verification & Initialization
    if (tcTracker_model):
        if (tcTracker_model['id'] != 'CSDEFAULT'): return None
    else:
        tcTracker_model['id'] = 'CSDEFAULT'
        tcTracker_model['pr_csf_prev']      = None
        tcTracker_model['cycle_contIndex']  = -1
        tcTracker_model['rqpVal_prev']      = None
    #---[3-2]: Cycle Check
    isShort_prev = None if (tcTracker_model['pr_csf_prev'] is None) else (tcTracker_model['pr_csf_prev'] < param_delta)
    isShort_this = (_pr_csf < param_delta)
    if (isShort_prev is None) or (isShort_prev^isShort_this):
        tcTracker_model['cycle_contIndex']  = 0
    tcTracker_model['pr_csf_prev'] = _pr_csf

    #[4]: RQP Value Calculation
    #---[4-1]: Effective Parameter
    if isShort_this: param_strength_eff = param_strength_SHORT
    else:            param_strength_eff = param_strength_LONG
    #---[4-2]: RQP Value
    direction = -1 if isShort_this else 1
    width = 1-param_delta*direction
    dist  = (_pr_csf-param_delta)*direction
    rqpVal_abs = max((1-dist/max(width, 1e-9))*param_strength_eff, 0.0)
    if width == 0: rqpVal_abs = 0.0
    #---[4-3]: Cyclic Minimum
    if (0 < tcTracker_model['cycle_contIndex']): rqpVal_abs = min(rqpVal_abs, abs(tcTracker_model['rqpVal_prev']))
    #---[4-4]: Direction
    if isShort_this: rqpVal = -rqpVal_abs
    else:            rqpVal =  rqpVal_abs

    #[5]: TC Tracker Update
    tcTracker_model['cycle_contIndex'] += 1
    tcTracker_model['rqpVal_prev'] = rqpVal

    #[6]: Finally
    return rqpVal