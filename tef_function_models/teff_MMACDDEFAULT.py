import math

"""
FUNCTION MODEL: MMACDDEFAULT
"""

DESCRIPTOR = [{'name': 'alpha',             'defaultValue': 1.0000,   'isAcceptable': lambda x: (( 0.0001 <= x)   and (x <= 5.0000)),   'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
              {'name': 'beta',              'defaultValue': 1.00,     'isAcceptable': lambda x: (( 1.00   <= x)   and (x <= 10.00)),    'str_to_val': lambda x: round(float(x), 2), 'val_to_str': lambda x: f"{x:.2f}"},
              {'name': 'delta',             'defaultValue': 0.0000,   'isAcceptable': lambda x: ((-1.0000 <= x)   and (x <= 1.0000)),   'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
              {'name': 'shortStrength',     'defaultValue': 1.000000, 'isAcceptable': lambda x: (( 0.000000 <= x) and (x <= 1.000000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
              {'name': 'longStrength',      'defaultValue': 1.000000, 'isAcceptable': lambda x: (( 0.000000 <= x) and (x <= 1.000000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
              {'name': 'downHillThreshold', 'defaultValue': 0.8000,   'isAcceptable': lambda x: (( 0.000000 <= x) and (x <= 1.000000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"}]

"""
[1]: params: (type: tuple)
 * Function parameters tuple given in the order defined in the descriptor

[2]: linearizedAnalysis: (type: dict)
 * Linearized Analysis Result For The Current Target
 * Structure:
    Base Data Key: {baseType}_{dataCode}                   = value
    Analysis Key:  {intervalID}_{analysisCode}_{valueCode} = value
 * Example:
    linearizedAnalysis = {'OPENTIME':                1776218640,
                          'CLOSETIME':               1776218699,
                          'KLINE_OPENPRICE':         74561.7,
                          'KLINE_HIGHPRICE':         74561.7,
                          'KLINE_LOWPRICE':          74560.0,
                          'KLINE_CLOSEPRICE':        74560.0,
                          'KLINE_NTRADES':           25,
                          'KLINE_VOLBASE':           0.423,
                          'KLINE_VOLQUOTE':          31539.3973,
                          'KLINE_VOLBASETAKERBUY':   0.008,
                          'KLINE_VOLQUOTETAKERBUY':  596.4864,
                          'DEPTH_BIDS5':             2742561.4592,
                          'DEPTH_BIDS4':             3335360.4765,
                          'DEPTH_BIDS3':             14647296.9113,
                          'DEPTH_BIDS0':             34591953.26870001,
                          'DEPTH_BIDS2':             134494000.51040018,
                          'DEPTH_BIDS1':             66670079.09960014,
                          'DEPTH_ASKS0':             25050698.4003,
                          'DEPTH_ASKS1':             83887715.33460012,
                          'DEPTH_ASKS2':             105261764.56909998,
                          'DEPTH_ASKS3':             33873157.07539998,
                          'DEPTH_ASKS4':             28326176.9374,
                          'DEPTH_ASKS5':             25443558.7908,
                          'AGGTRADE_QUANTITYBUY':    0.008,
                          'AGGTRADE_QUANTITYSELL':   0.352,
                          'AGGTRADE_NTRADESBUY':     3,
                          'AGGTRADE_NTRADESSELL':    21,
                          'AGGTRADE_NOTIONALBUY':    596.4864,
                          'AGGTRADE_NOTIONALSELL':   26245.6309,
                          '0_MMACD_MSDELTA':         -1.8079873705384522,
                          '0_MMACD_MSDELTAABSMA':    4.240728027887122,
                          '0_MMACD_MSDELTAABSMAREL': -0.42634
                          '3_MMACD_MSDELTA':         50.18804994517422,
                          '3_MMACD_MSDELTAABSMA':    45.89798404630567,
                          '3_MMACD_MSDELTAABSMAREL': 1.09347
                         }

[3]: tcTracker_model <type: dict>
 * Trade Control Tracker Designated For The TEF Function Model. This Can Be Setup And Edited Freely By The Function To Keep Track Of The TEF Computation State.
"""

def getTEF(params: tuple, linearizedAnalysis: dict, tcTracker_model: dict) -> float | None:
    #[1]: Params
    (param_alpha,
     param_beta,
     param_delta,
     param_strength_SHORT,
     param_strength_LONG,
     param_downHillThreshold,
    ) = params



    #[2]: Analysis Reference
    la_mmacd_msDeltaAbsMARel = linearizedAnalysis.get('0_MMACD_MSDELTAABSMAREL', None)
    if la_mmacd_msDeltaAbsMARel is None: return (None, 0)



    #[3]: TC Tracker
    #---[3-1]: Model Verification & Initialization
    if not tcTracker_model:
        tcTracker_model['tefVal_prev']                   = 0
        tcTracker_model['tefVal_absMax']                 = 0
        tcTracker_model['la_mmacd_msDeltaAbsMARel_prev'] = 0
        tcTracker_model['isDownhill']                    = False

    #---[3-2]: Cycle Check
    isShort_prev = (tcTracker_model['la_mmacd_msDeltaAbsMARel_prev'] < param_delta)
    isShort_this = (la_mmacd_msDeltaAbsMARel                         < param_delta)
    cycleReset   = (isShort_prev ^ isShort_this)



    #[4]: TEF Value Calculation
    #---[4-1]: Effective Parameter
    if isShort_this: param_strength_eff = param_strength_SHORT
    else:            param_strength_eff = param_strength_LONG
    
    #---[4-2]: MSDeltaAbsMARel Normalization
    x_sign = -1.0 if la_mmacd_msDeltaAbsMARel < 0 else 1.0
    x_abs  = pow(abs(la_mmacd_msDeltaAbsMARel/param_alpha), param_beta)
    y_norm = math.tanh(x_abs)*x_sign

    #---[4-3]: TEF Value
    width = param_delta+1.0 if isShort_this else 1.0-param_delta
    dist  = abs(y_norm-param_delta)
    tefVal_abs = dist/max(width, 1e-9)*param_strength_eff
    if width == 0: tefVal_abs = 0.0

    #---[4-4]: TEF Value Cyclic Maximum
    if cycleReset: tefVal_absMax = tefVal_abs
    else:          tefVal_absMax = max(tcTracker_model['tefVal_absMax'], tefVal_abs)

    #---[4-5]: Mode
    if cycleReset: isDownhill = False
    else:          isDownhill = tcTracker_model['isDownhill']
    if tefVal_abs < tefVal_absMax*param_downHillThreshold:
        isDownhill = True

    #---[4-6]: Effective TEF Value
    if isDownhill:
        tefVal_abs = min(tefVal_abs, abs(tcTracker_model['tefVal_prev']))

    #---[4-7]: Direction
    if isShort_this: tefVal = -tefVal_abs
    else:            tefVal =  tefVal_abs



    #[5]: TC Tracker Update
    tcTracker_model['tefVal_prev']                   = tefVal
    tcTracker_model['tefVal_absMax']                 = tefVal_absMax
    tcTracker_model['la_mmacd_msDeltaAbsMARel_prev'] = la_mmacd_msDeltaAbsMARel
    tcTracker_model['isDownhill']                    = isDownhill



    #[6]: Finally
    tefDir = 'SHORT' if isShort_this else 'LONG'
    return tefDir, tefVal