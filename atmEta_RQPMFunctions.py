import math

RQPMFUNCTIONS             = dict()
RQPMFUNCTIONS_DESCRIPTORS = dict()

"""
Rotational Gaussian version 1
"""
def rqpmFunction_ROTATIONALGAUSSIAN1(params, contIndex, pDPerc, pDPerc_LS, sigStrength):
    _param_theta = params[0]
    _param_alpha = params[1]
    _param_beta0 = params[2]
    _param_beta1 = params[3]
    _param_gamma = params[4]

    _x_shift = contIndex*0.0001
    _y_shift = pDPerc

    _angle = (_param_theta+0.5)*math.pi
    _x_rot =  math.cos(_angle)*_x_shift + math.sin(_angle)*_y_shift
    _y_rot = -math.sin(_angle)*_x_shift + math.cos(_angle)*_y_shift

    _x_numerator = _x_rot**2
    _y_numerator = _y_rot**2

    _x_denominator = max(2*_param_alpha**2, 1e-12)
    if (_y_rot < 0): _y_denominator = max(2*_param_beta0**2, 1e-12)
    else:            _y_denominator = max(2*_param_beta1**2, 1e-12)

    rqpmValue = math.exp(-(_x_numerator/_x_denominator + _y_numerator/_y_denominator)**_param_gamma)
    return rqpmValue

RQPMFUNCTIONS['ROTATIONALGAUSSIAN1'] = rqpmFunction_ROTATIONALGAUSSIAN1
RQPMFUNCTIONS_DESCRIPTORS['ROTATIONALGAUSSIAN1'] = [{'name': 'theta', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (( 0.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'alpha', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (0.0000 <= x),                      'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'beta0', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (0.0000 <= x),                      'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'beta1', 'defaultValue': 0.5000, 'isAcceptable': lambda x: (0.0000 <= x),                      'str_to_val': lambda x: round(float(x), 4), 'val_to_str': lambda x: f"{x:.4f}"},
                                                    {'name': 'gamma', 'defaultValue': 1,      'isAcceptable': lambda x: ((1 <= x)      and (x <= 10)),      'str_to_val': lambda x: int(x),             'val_to_str': lambda x: f"{x:d}"}]





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

RQPMFUNCTIONS['ROTATIONALGAUSSIAN2'] = rqpmFunction_ROTATIONALGAUSSIAN2
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