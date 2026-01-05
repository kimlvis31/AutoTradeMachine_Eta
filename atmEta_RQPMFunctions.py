import math

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

RQPMFUNCTIONS_GET_RQPVAL  = dict()
RQPMFUNCTIONS_DESCRIPTORS = dict()

"""
Rotational Gaussian version 1
"""
def rqpmFunction_ROTATIONALGAUSSIAN1_get_RQPVal(params, kline, pipResult, tcTracker_model):
    #Params
    (_param_delta,
     _param_theta_SHORT,
     _param_alpha_SHORT,
     _param_beta0_SHORT,
     _param_beta1_SHORT,
     _param_gamma_SHORT,
     _param_theta_LONG,
     _param_alpha_LONG,
     _param_beta0_LONG,
     _param_beta1_LONG,
     _param_gamma_LONG
    ) = params

    #PIP Signal
    _pr_csf = pipResult['CLASSICALSIGNAL_FILTERED']
    if (_pr_csf is None): return None

    #TC Tracker
    #---Model Verification & Tracker Initialization
    if (tcTracker_model):
        if (tcTracker_model['id'] != 'ROTATIONALGAUSSIAN1'): return None
    else:
        tcTracker_model['id'] = 'ROTATIONALGAUSSIAN1'
        tcTracker_model['pr_csf_prev']      = None
        tcTracker_model['cycle_contIndex']  = -1
        tcTracker_model['cycle_beginPrice'] = None
        tcTracker_model['rqpVal_prev']      = None
    #---Cycle Check
    isShort_prev = None if (tcTracker_model['pr_csf_prev'] is None) else (tcTracker_model['pr_csf_prev'] < _param_delta)
    isShort_this = (_pr_csf < _param_delta)
    if ((isShort_prev is None) or (isShort_prev^isShort_this)):
        tcTracker_model['cycle_contIndex']  = 0
        tcTracker_model['cycle_beginPrice'] = kline[KLINDEX_CLOSEPRICE]
    tcTracker_model['pr_csf_prev'] = _pr_csf

    #Effective Params
    if (isShort_this == True):
        _param_theta_eff = _param_theta_SHORT
        _param_alpha_eff = _param_alpha_SHORT
        _param_beta0_eff = _param_beta0_SHORT
        _param_beta1_eff = _param_beta1_SHORT
        _param_gamma_eff = _param_gamma_SHORT
    else:
        _param_theta_eff = _param_theta_LONG
        _param_alpha_eff = _param_alpha_LONG
        _param_beta0_eff = _param_beta0_LONG
        _param_beta1_eff = _param_beta1_LONG
        _param_gamma_eff = _param_gamma_LONG

    #RQP Value
    _x = tcTracker_model['cycle_contIndex']*0.0001                       #Scaled Cycle Continuation Index
    _y = kline[KLINDEX_CLOSEPRICE]/tcTracker_model['cycle_beginPrice']-1 #Price Deviation
    _x_shift = _x
    _y_shift = _y
    _angle = (_param_theta_eff+0.5)*math.pi
    _x_rot =  math.cos(_angle)*_x_shift + math.sin(_angle)*_y_shift
    _y_rot = -math.sin(_angle)*_x_shift + math.cos(_angle)*_y_shift
    _x_numerator = _x_rot**2
    _y_numerator = _y_rot**2
    _x_denominator = max(2*_param_alpha_eff**2, 1e-12)
    if (_y_rot < 0): _y_denominator = max(2*_param_beta0_eff**2, 1e-12)
    else:            _y_denominator = max(2*_param_beta1_eff**2, 1e-12)
    _q = _x_numerator/_x_denominator + _y_numerator/_y_denominator
    _rqpVal_abs      = math.exp(-_q**_param_gamma_eff)
    if (tcTracker_model['cycle_contIndex'] == 0) or (_rqpVal_abs < abs(tcTracker_model['rqpVal_prev'])): _rqpVal_abs = _rqpVal_abs
    else:                                                                                                _rqpVal_abs = abs(tcTracker_model['rqpVal_prev'])
    if (isShort_this == True): _rqpVal = -_rqpVal_abs
    else:                      _rqpVal =  _rqpVal_abs

    #TC Tracker Update
    tcTracker_model['cycle_contIndex'] += 1
    tcTracker_model['rqpVal_prev']     = _rqpVal

    #Finally
    return _rqpVal

RQPMFUNCTIONS_GET_RQPVAL['ROTATIONALGAUSSIAN1'] = rqpmFunction_ROTATIONALGAUSSIAN1_get_RQPVal
RQPMFUNCTIONS_DESCRIPTORS['ROTATIONALGAUSSIAN1'] = [{'name': 'delta',   'defaultValue': 0.0000, 'isAcceptable': lambda x: ((-1.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
                                                    {'name': 'theta_S', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (( 0.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
                                                    {'name': 'alpha_S', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (0.0000 <= x),                      'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
                                                    {'name': 'beta0_S', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (0.0000 <= x),                      'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
                                                    {'name': 'beta1_S', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (0.0000 <= x),                      'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
                                                    {'name': 'gamma_S', 'defaultValue': 1,      'isAcceptable': lambda x: ((1 <= x)       and (x <= 10)),     'str_to_val': lambda x: int(x),             'val_to_str': lambda x: f"{x:d}"},
                                                    {'name': 'theta_L', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (( 0.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
                                                    {'name': 'alpha_L', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (0.0000 <= x),                      'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
                                                    {'name': 'beta0_L', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (0.0000 <= x),                      'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
                                                    {'name': 'beta1_L', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (0.0000 <= x),                      'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
                                                    {'name': 'gamma_L', 'defaultValue': 1,      'isAcceptable': lambda x: ((1 <= x)       and (x <= 10)),     'str_to_val': lambda x: int(x),             'val_to_str': lambda x: f"{x:d}"}]





"""
Rotational Gaussian version 2
"""
def rqpmFunction_ROTATIONALGAUSSIAN2(params, contIndex, pDPerc, pDPerc_LS, sigStrength):
    _param_theta0 = params[0]
    _param_theta1 = params[1]
    _param_theta2 = params[2]
    _param_delta0 = params[3]
    _param_delta1 = params[4]
    _param_delta2 = params[5]
    _param_delta3 = params[6]
    _param_sigma0 = params[7]
    _param_sigma1 = params[8]
    _param_sigma2 = params[9]
    _param_sigma3 = params[10]

    _angle0 = _param_theta0*2*math.pi
    _angle1 = _param_theta1*2*math.pi
    _angle2 = _param_theta2*2*math.pi
    _c0, _s0 = math.cos(_angle0), math.sin(_angle0)
    _c1, _s1 = math.cos(_angle1), math.sin(_angle1)
    _c2, _s2 = math.cos(_angle2), math.sin(_angle2)

    _a0_0 = contIndex*0.001+_param_delta0
    _a1_0 = pDPerc         +_param_delta1
    _a2_0 = pDPerc_LS      +_param_delta2
    _a3_0 = sigStrength    +_param_delta3

    _a0_1   =  _c0*_a0_0+_s0*_a1_0
    _a1_rot = -_s0*_a0_0+_c0*_a1_0
    _a0_2   =  _c1*_a0_1+_s1*_a2_0
    _a2_rot = -_s1*_a0_1+_c1*_a2_0
    _a0_rot =  _c2*_a0_2+_s2*_a3_0
    _a3_rot = -_s2*_a0_2+_c2*_a3_0

    _q = 0.5 * ((_a0_rot/_param_sigma0)**2 \
              + (_a1_rot/_param_sigma1)**2 \
              + (_a2_rot/_param_sigma2)**2 \
              + (_a3_rot/_param_sigma3)**2)

    _rqpValue = math.exp(-_q**100)
    return _rqpValue

RQPMFUNCTIONS_GET_RQPVAL['ROTATIONALGAUSSIAN2'] = rqpmFunction_ROTATIONALGAUSSIAN2
RQPMFUNCTIONS_DESCRIPTORS['ROTATIONALGAUSSIAN2'] = [{'name': 'theta0', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (( 0.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'theta1', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (( 0.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'theta2', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (( 0.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'delta0', 'defaultValue': 0.0000, 'isAcceptable': lambda x: ((-1.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'delta1', 'defaultValue': 0.0000, 'isAcceptable': lambda x: ((-1.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'delta2', 'defaultValue': 0.0000, 'isAcceptable': lambda x: ((-1.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'delta3', 'defaultValue': 0.0000, 'isAcceptable': lambda x: ((-1.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'sigma0', 'defaultValue': 0.0001, 'isAcceptable': lambda x: (( 0.0001 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'sigma1', 'defaultValue': 0.0001, 'isAcceptable': lambda x: (( 0.0001 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'sigma2', 'defaultValue': 0.0001, 'isAcceptable': lambda x: (( 0.0001 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'sigma3', 'defaultValue': 0.0001, 'isAcceptable': lambda x: (( 0.0001 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"}]