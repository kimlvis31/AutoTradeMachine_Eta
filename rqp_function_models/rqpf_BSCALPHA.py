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

DESCRIPTOR = [{'name': 'delta',   'defaultValue': 0.0000, 'isAcceptable': lambda x: ((-1.0000 <= x) and (x <= 1.0000)), 'str_to_val': lambda x: round(float(x), 6), 'val_to_str': lambda x: f"{x:.6f}"},
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
def getRQPValue(params: tuple, linearizedAnalysis: dict, tcTracker_model: dict):
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
        if (tcTracker_model['id'] != 'CSRG1'): return None
    else:
        tcTracker_model['id'] = 'CSRG1'
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
    rqpVal_abs      = math.exp(-_q**_param_gamma_eff)
    if (0 < tcTracker_model['cycle_contIndex']): rqpVal_abs = min(rqpVal_abs, abs(tcTracker_model['rqpVal_prev']))
    if isShort_this: rqpVal = -rqpVal_abs
    else:            rqpVal =  rqpVal_abs

    #TC Tracker Update
    tcTracker_model['cycle_contIndex'] += 1
    tcTracker_model['rqpVal_prev']     = rqpVal

    #Finally
    return rqpVal



"""
_TORCHDTYPE = atmEta_NeuralNetworks._TORCHDTYPE
_PIP_SWINGTYPE_LOW  = 'LOW'
_PIP_SWINGTYPE_HIGH = 'HIGH'
def analysisGenerator_PIP(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode = analysisParams['analysisCode']
    REFERREDANALYSISCODES = analysisParams['referredAnalysisCodes']
    SWINGRANGE            = analysisParams['swingRange']
    ALPHA_NNA             = analysisParams['alpha_NNA']
    BETA_NNA              = analysisParams['beta_NNA']
    ALPHA_CS              = analysisParams['alpha_CS']
    BETA_CS               = analysisParams['beta_CS']
    NSAMPLES_CS           = analysisParams['nSamples_CS']
    SIGMA_CS              = analysisParams['sigma_CS']

    _klineAccess_raw = klineAccess['raw']
    _kline = _klineAccess_raw[timestamp]
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess['PIP']): _pip_prev = klineAccess['PIP'][timestamp_previous]; _analysisCount = _pip_prev['_analysisCount']+1
    else:                                          _pip_prev = None;                                   _analysisCount = 0

    #[3]: Classical Signal interpretation
    if (True):
        #[1]: Classical Signals Combination
        _classicalSignalSum           = 0
        _nClassicalSignalContributors = 0
        _allContributorsReady         = True
        for analysisType in REFERREDANALYSISCODES:
            #[1]: MMACDSHORT
            if (analysisType == 'MMACDSHORT'):
                _mmacdShort = klineAccess['MMACDSHORT'][timestamp]
                _mmacdShort_MSDelta_MADelta_AbsMARel = _mmacdShort['MSDELTA_ABSMAREL']
                if (_mmacdShort_MSDelta_MADelta_AbsMARel != None):
                    _classicalSignalSum += _mmacdShort_MSDelta_MADelta_AbsMARel
                    _nClassicalSignalContributors += 1
                else: _allContributorsReady = False; break
            #[2]: MMACDLONG
            if (analysisType == 'MMACDLONG'):
                _mmacdLong = klineAccess['MMACDLONG'][timestamp]
                _mmacdLong_MSDelta_MADelta_AbsMARel = _mmacdLong['MSDELTA_ABSMAREL']
                if (_mmacdLong_MSDelta_MADelta_AbsMARel != None):
                    _classicalSignalSum += _mmacdLong_MSDelta_MADelta_AbsMARel
                    _nClassicalSignalContributors += 1
                else: _allContributorsReady = False; break
            #[1]: DMIxADX
            if (analysisType == 'DMIxADX'):
                _signalSum_dmixadx = 0
                for dmixadxCode in REFERREDANALYSISCODES['DMIxADX']:
                    _dmixadx = klineAccess[dmixadxCode][timestamp]
                    _dmiadx_absATHRel = _dmixadx['DMIxADX_ABSATHREL']
                    if (_dmiadx_absATHRel != None): _signalSum_dmixadx += _dmiadx_absATHRel/100
                    else: _allContributorsReady = False; break
                if (_allContributorsReady == False): break
                else:
                    _classicalSignalSum += _signalSum_dmixadx/len(REFERREDANALYSISCODES['DMIxADX'])
                    _nClassicalSignalContributors += 1
            #[2]: MFI
            if (analysisType == 'MFI'):
                _signalSum_mfi = 0
                for mfiCode in REFERREDANALYSISCODES['MFI']: 
                    _mfi = klineAccess[mfiCode][timestamp]
                    _mfi_absATHRel = _mfi['MFI_ABSATHREL']
                    if (_mfi_absATHRel != None): _signalSum_mfi += _mfi_absATHRel/100-0.5
                    else: _allContributorsReady = False; break
                if (_allContributorsReady == False): break
                else:
                    _classicalSignalSum += _signalSum_dmixadx/len(REFERREDANALYSISCODES['DMIxADX'])
                    _nClassicalSignalContributors += 1
        if ((0 < _nClassicalSignalContributors) and (_allContributorsReady == True)):
            if (0 <= _classicalSignalSum): classicalSignal =  abs(round(math.atan(pow(_classicalSignalSum/_nClassicalSignalContributors/ALPHA_CS, BETA_CS))*2/math.pi, 5))
            else:                          classicalSignal = -abs(round(math.atan(pow(_classicalSignalSum/_nClassicalSignalContributors/ALPHA_CS, BETA_CS))*2/math.pi, 5))
        else: classicalSignal = None
        #[2]: CS Delta
        if (_pip_prev == None): _classicalSignal_prev = None
        else:                   _classicalSignal_prev = _pip_prev['CLASSICALSIGNAL']
        if (_classicalSignal_prev == None): classicalSignal_Delta = None
        else:                               classicalSignal_Delta = classicalSignal-_classicalSignal_prev
        #[3]: CS Filtered
        classicalSignal_Filtered = None
        _samplingTSs = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = NSAMPLES_CS, direction = False, mrktReg = mrktRegTS)
        if ((_samplingTSs[-1] in klineAccess['PIP']) and (klineAccess['PIP'][_samplingTSs[-1]]['CLASSICALSIGNAL'] != None)):
            _CSSamples = [klineAccess['PIP'][_samplingTSs[-1-_sTSIndex]]['CLASSICALSIGNAL'] for _sTSIndex in range (NSAMPLES_CS-1)] + [classicalSignal,]
            _CSSamples_gaussianFiltered = scipy.ndimage.gaussian_filter1d(input = _CSSamples, sigma = SIGMA_CS)
            classicalSignal_Filtered = float(_CSSamples_gaussianFiltered[-1])
        #[4]: CS Filtered Delta
        if (_pip_prev is None): _classicalSignal_Filtered_prev = None
        else:                   _classicalSignal_Filtered_prev = _pip_prev['CLASSICALSIGNAL_FILTERED']
        if (_classicalSignal_Filtered_prev is None): classicalSignal_Filtered_Delta = None
        else:                                        classicalSignal_Filtered_Delta = classicalSignal_Filtered-_classicalSignal_Filtered_prev
        #[5]: CS Cycle Base
        if (_pip_prev is None): 
            classicalSignal_Cycle        = None
            classicalSignal_CycleUpdated = False
        else:                   
            classicalSignal_Cycle        = _pip_prev['CLASSICALSIGNAL_CYCLE']
            classicalSignal_CycleUpdated = False
        if ((classicalSignal_Cycle is None) and (classicalSignal_Filtered is not None)):
            if   (classicalSignal_Filtered < 0): classicalSignal_Cycle = 'LOW'
            elif (0 < classicalSignal_Filtered): classicalSignal_Cycle = 'HIGH'
            if (classicalSignal_Cycle is not None):
                classicalSignal_CycleUpdated = True
        elif (classicalSignal_Cycle is not None):
            if   ((classicalSignal_Cycle == 'LOW')  and (0 < classicalSignal_Filtered)): 
                classicalSignal_Cycle        = 'HIGH'
                classicalSignal_CycleUpdated = True
            elif ((classicalSignal_Cycle == 'HIGH') and (classicalSignal_Filtered < 0)): 
                classicalSignal_Cycle        = 'LOW'
                classicalSignal_CycleUpdated = True
    
    #Result formatting & saving
    pipResult = {'SWINGS': swings, '_SWINGSEARCH': swingSearch,
                 #Neural Network
                 'NNASIGNAL': nnaSignal,
                 #Classical Signal
                 'CLASSICALSIGNAL':                classicalSignal, 
                 'CLASSICALSIGNAL_DELTA':          classicalSignal_Delta, 
                 'CLASSICALSIGNAL_FILTERED':       classicalSignal_Filtered, 
                 'CLASSICALSIGNAL_FILTERED_DELTA': classicalSignal_Filtered_Delta, 
                 'CLASSICALSIGNAL_CYCLE':          classicalSignal_Cycle,
                 'CLASSICALSIGNAL_CYCLEUPDATED':   classicalSignal_CycleUpdated,
                 #IVP
                 'NEARIVPBOUNDARIES': nearIVPBoundaries,
                 #Process
                 '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = pipResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    if (neuralNetwork == None): return (NSAMPLES_CS, 2)
    else:                       return (max(NSAMPLES_CS, _nn_nKlines), _nn_nKlines)
"""
"""
    if (currencyAnalysisConfiguration['PIP_Master'] == True):
        _analysisCode = 'PIP'
        _referredAnalysisCodes = dict()
        _bolCodes              = list()
        for _aCode in _currencyAnalysisParams:
            _aType = _aCode.split("_")[0]
            if (_aType in __PIP_REFERREDANALYSISTYPES):
                if (_aType in _referredAnalysisCodes): _referredAnalysisCodes[_aType].append(_aCode)
                else:                                  _referredAnalysisCodes[_aType] = [_aCode,]
            if (_aType == 'BOL'): _bolCodes.append(_aCode)
        _currencyAnalysisParams[_analysisCode] = {'referredAnalysisCodes':  _referredAnalysisCodes,
                                                  'bolCodes':               _bolCodes,
                                                  'swingRange':             currencyAnalysisConfiguration['PIP_SwingRange'],
                                                  'alpha_NNA':              currencyAnalysisConfiguration['PIP_NNAAlpha'],
                                                  'beta_NNA':               currencyAnalysisConfiguration['PIP_NNABeta'],
                                                  'alpha_CS':               currencyAnalysisConfiguration['PIP_ClassicalAlpha'],
                                                  'beta_CS':                currencyAnalysisConfiguration['PIP_ClassicalBeta'],
                                                  'nSamples_CS':            currencyAnalysisConfiguration['PIP_ClassicalNSamples'],
                                                  'sigma_CS':               currencyAnalysisConfiguration['PIP_ClassicalSigma'],
                                                  }
"""