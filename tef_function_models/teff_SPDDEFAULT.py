"""
FUNCTION MODEL: SPDDEFAULT (Swing Price Deviation Default)
"""

DESCRIPTOR = [{'name': 'shortDelta',    'defaultValue': 0.000000, 'isAcceptable': lambda x: ((-1.000000 <= x) and (x <= 1.000000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
              {'name': 'shortStrength', 'defaultValue': 1.000000, 'isAcceptable': lambda x: (( 0.000000 <= x) and (x <= 1.000000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
              {'name': 'shortLength',   'defaultValue': 1.000000, 'isAcceptable': lambda x: (( 0.000000 <= x) and (x <= 1.000000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
              {'name': 'longDelta',     'defaultValue': 0.000000, 'isAcceptable': lambda x: ((-1.000000 <= x) and (x <= 1.000000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
              {'name': 'longStrength',  'defaultValue': 1.000000, 'isAcceptable': lambda x: (( 0.000000 <= x) and (x <= 1.000000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
              {'name': 'longLength',    'defaultValue': 1.000000, 'isAcceptable': lambda x: (( 0.000000 <= x) and (x <= 1.000000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"}]

"""
[1]: params: (type: tuple)
 * Function parameters tuple given in the order defined in the descriptor

[2]: linearizedAnalysis: (type: dict)
 * Linearized Analysis Result For The Current Target
 * Structure:
    Base Data Key: {baseType}_{dataCode}                   = value
    Analysis Key:  {intervalID}_{analysisCode}_{valueCode} = value
 * Example:
    linearizedAnalysis = {'OPENTIME':               1776218640,
                          'CLOSETIME':              1776218699,
                          'KLINE_OPENPRICE':        74561.7,
                          'KLINE_HIGHPRICE':        74561.7,
                          'KLINE_LOWPRICE':         74560.0,
                          'KLINE_CLOSEPRICE':       74560.0,
                          'KLINE_NTRADES':          25,
                          'KLINE_VOLBASE':          0.423,
                          'KLINE_VOLQUOTE':         31539.3973,
                          'KLINE_VOLBASETAKERBUY':  0.008,
                          'KLINE_VOLQUOTETAKERBUY': 596.4864,
                          'DEPTH_BIDS5':            2742561.4592,
                          'DEPTH_BIDS4':            3335360.4765,
                          'DEPTH_BIDS3':            14647296.9113,
                          'DEPTH_BIDS0':            34591953.26870001,
                          'DEPTH_BIDS2':            134494000.51040018,
                          'DEPTH_BIDS1':            66670079.09960014,
                          'DEPTH_ASKS0':            25050698.4003,
                          'DEPTH_ASKS1':            83887715.33460012,
                          'DEPTH_ASKS2':            105261764.56909998,
                          'DEPTH_ASKS3':            33873157.07539998,
                          'DEPTH_ASKS4':            28326176.9374,
                          'DEPTH_ASKS5':            25443558.7908,
                          'AGGTRADE_QUANTITYBUY':   0.008,
                          'AGGTRADE_QUANTITYSELL':  0.352,
                          'AGGTRADE_NTRADESBUY':    3,
                          'AGGTRADE_NTRADESSELL':   21,
                          'AGGTRADE_NOTIONALBUY':   596.4864,
                          'AGGTRADE_NOTIONALSELL':  26245.6309,
                          '0_SWING_0_LSPRICE':      73766.8,
                          '0_SWING_0_LSTIMESTAMP':  1776205860,
                          '0_SWING_0_LSTYPE':       -1,
                          '0_SWING_1_LSPRICE':      73766.8,
                          '0_SWING_1_LSTIMESTAMP':  1776205860,
                          '0_SWING_1_LSTYPE':       -1,
                          '3_SWING_0_LSPRICE':      74085.0,
                          '3_SWING_0_LSTIMESTAMP':  1776211200,
                          '3_SWING_0_LSTYPE':       -1,
                          '3_SWING_1_LSPRICE':      73766.8,
                          '3_SWING_1_LSTIMESTAMP':  1776205800,
                          '3_SWING_1_LSTYPE':       -1
                         }

[3]: tcTracker_model <type: dict>
 * Trade Control Tracker Designated For The TEF Function Model. This Can Be Setup And Edited Freely By The Function To Keep Track Of The TEF Computation State.
"""

def getTEF(params:             tuple, 
           linearizedAnalysis: dict, 
           tcTracker_model:    dict
           ) -> float | None:
    #[1]: Params
    (param_delta_SHORT,
     param_strength_SHORT,
     param_length_SHORT,
     param_delta_LONG,
     param_strength_LONG,
     param_length_LONG,
    ) = params

    #[2]: Analysis Reference
    la_swing0_lsPrice = linearizedAnalysis.get('0_SWING_0_LSPRICE', None)
    la_swing0_lsType  = linearizedAnalysis.get('0_SWING_0_LSTYPE',  None)
    if la_swing0_lsType is None: return (None, 0)

    #[3]: TC Tracker
    #---[3-1]: Model Verification & Initialization
    if not tcTracker_model:
        tcTracker_model['tefVal_prev']            = 0
        tcTracker_model['la_swing0_lsType_prev']  = -1
    #---[3-2]: Cycle Check
    isShort_prev = (tcTracker_model['la_swing0_lsType_prev'] == 1)
    isShort_this = (la_swing0_lsType                         == 1)
    cycleReset   = (isShort_prev ^ isShort_this)

    #[4]: TEF Value Calculation
    #---[4-1]: Effective Parameters
    if isShort_this:
        param_delta_eff    = param_delta_SHORT
        param_strength_eff = param_strength_SHORT
        param_length_eff   = param_length_SHORT
    else:
        param_delta_eff    = param_delta_LONG
        param_strength_eff = param_strength_LONG
        param_length_eff   = param_length_LONG
    #---[4-2]: TEF Value
    if isShort_this: pd = 1-(linearizedAnalysis['KLINE_CLOSEPRICE']/la_swing0_lsPrice)
    else:            pd = (linearizedAnalysis['KLINE_CLOSEPRICE']/la_swing0_lsPrice)-1
    dist = pd-param_delta_eff
    if param_delta_eff <= pd: tefVal_abs = max((1-dist/max(param_length_eff, 1e-6))*param_strength_eff, 0.0)
    else:                     tefVal_abs = 0.0
    if param_length_eff == 0: tefVal_abs = 0.0
    tefVal_abs = round(tefVal_abs, 6)
    #---[4-3]: Cyclic Minimum
    if not cycleReset: tefVal_abs = min(tefVal_abs, abs(tcTracker_model['tefVal_prev']))
    #---[4-4]: Direction
    if isShort_this: tefVal = -tefVal_abs
    else:            tefVal =  tefVal_abs

    #[5]: TC Tracker Update
    tcTracker_model['tefVal_prev']           = tefVal
    tcTracker_model['la_swing0_lsType_prev'] = la_swing0_lsType

    #[6]: Finally
    tefDir = 'SHORT' if isShort_this else 'LONG'
    return tefDir, tefVal