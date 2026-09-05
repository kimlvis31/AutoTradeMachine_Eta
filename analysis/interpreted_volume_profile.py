#Imports
import auxiliaries
import random
import scipy
import numpy
import math
from collections import defaultdict, deque

#Constants
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
KLINDEX_CLOSED           = 11
KLINDEX_SOURCE           = 12

DEPTHINDEX_OPENTIME  = 0
DEPTHINDEX_CLOSETIME = 1
DEPTHINDEX_BIDS5     = 2
DEPTHINDEX_BIDS4     = 3 
DEPTHINDEX_BIDS3     = 4
DEPTHINDEX_BIDS2     = 5 
DEPTHINDEX_BIDS1     = 6 
DEPTHINDEX_BIDS0     = 7 
DEPTHINDEX_ASKS0     = 8 
DEPTHINDEX_ASKS1     = 9 
DEPTHINDEX_ASKS2     = 10 
DEPTHINDEX_ASKS3     = 11
DEPTHINDEX_ASKS4     = 12
DEPTHINDEX_ASKS5     = 13
DEPTHINDEX_CLOSED    = 14
DEPTHINDEX_SOURCE    = 15

ATINDEX_OPENTIME     = 0
ATINDEX_CLOSETIME    = 1
ATINDEX_QUANTITYBUY  = 2
ATINDEX_QUANTITYSELL = 3
ATINDEX_NTRADESBUY   = 4
ATINDEX_NTRADESSELL  = 5
ATINDEX_NOTIONALBUY  = 6
ATINDEX_NOTIONALSELL = 7
ATINDEX_CLOSED       = 8
ATINDEX_SOURCE       = 9





#DEFINING PARAMETERS ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ANALYSIS_CODE = 'IVP'
ANALYSIS_TYPE = 'MAIN'
NMAXLINES     = None
#DEFINING PARAMETERS END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYSIS GENERATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def construct_analysis_parameters(configuration):
    #[1]: Instances & Initialization
    cac = configuration
    cap          = dict()
    invalidLines = defaultdict(list)

    #[2]: Analysis Parameters Construction
    analysisCode = 'IVP'
    #[1]: Parameters
    nSamples    = cac[f'{analysisCode}_NSamples']
    gammaFactor = cac[f'{analysisCode}_GammaFactor']
    deltaFactor = cac[f'{analysisCode}_DeltaFactor']
    prominence = cac[f'{analysisCode}_Prominence']
    distance = cac[f'{analysisCode}_Distance']
    height = cac[f'{analysisCode}_Height']
    if   type(nSamples) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
    elif not 1 < nSamples:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
    if   not type(gammaFactor) in (int, float): invalidLines[analysisCode].append("gammaFactor: Must be type 'int' or 'float'")
    elif not (0.001 <= gammaFactor):            invalidLines[analysisCode].append("gammaFactor: Must be greater than or equal to 0.001")
    if   not type(deltaFactor) in (int, float): invalidLines[analysisCode].append("deltaFactor: Must be type 'int' or 'float'")
    elif not (0.01 <= deltaFactor):             invalidLines[analysisCode].append("deltaFactor: Must be greater than or equal to 0.01")
    if   type(nSamples) is not int:             invalidLines[analysisCode].append("nSamples: Must be type 'int'")
    elif not 1 < nSamples:                      invalidLines[analysisCode].append("nSamples: Must be greater than 1")
    if   not type(gammaFactor) in (int, float): invalidLines[analysisCode].append("gammaFactor: Must be type 'int' or 'float'")
    elif not (0.005 <= gammaFactor <= 0.100):   invalidLines[analysisCode].append("gammaFactor: Must be between 0.005 and 0.100")
    if   not type(deltaFactor) in (int, float): invalidLines[analysisCode].append("deltaFactor: Must be type 'int' or 'float'")
    elif not (0.1 <= deltaFactor <= 10.0):      invalidLines[analysisCode].append("deltaFactor: Must be between 0.1 and 10.0")
    if   not type(prominence) in (int, float):  invalidLines[analysisCode].append("prominence: Must be type 'int' or 'float'")
    elif not (0.01 <= prominence <= 1.00):      invalidLines[analysisCode].append("prominence: Must be between 0.01 and 1.00")
    if   not type(distance) is int:             invalidLines[analysisCode].append("distance: Must be type 'int'")
    elif not (1 <= distance <= 100):            invalidLines[analysisCode].append("distance: Must be between 1 and 100")
    if   not type(height) in (int, float):      invalidLines[analysisCode].append("height: Must be type 'int' or 'float'")
    elif not (0.0 <= height <= 1.0):            invalidLines[analysisCode].append("height: Must be between 0.0 and 1.0")
    #[2]: Analysis Params
    if analysisCode not in invalidLines:
        cap[analysisCode] = {'analysisCode': analysisCode,
                             'nSamples':    nSamples,
                             'gammaFactor': gammaFactor,
                             'deltaFactor': deltaFactor,
                             'prominence':  prominence,
                             'distance':    distance,
                             'height':      height}

    #[3]: Return The Constructed Analysis Parameters & Invalid Lines
    return cap, invalidLines



def __addPriceLevelProfile(priceLevelProfileWeight, priceLevelProfilePosition_low, priceLevelProfilePosition_high, priceLevelProfile, divisionHeight, pricePrecision, mode = True):
    #[1]: Instances
    plpw       = priceLevelProfileWeight
    plpp_low   = priceLevelProfilePosition_low
    plpp_high  = priceLevelProfilePosition_high
    plp        = priceLevelProfile
    dHeight    = divisionHeight
    pPrecision = pricePrecision
    dIndex_floor   = int(plpp_low /divisionHeight)
    dIndex_ceiling = int(plpp_high/divisionHeight)
    nDivisions = len(plp)
    director   = 1 if mode else -1

    #[2]: Updater
    #---[2-1]: The floor dIndex and the ceiling dIndex is the same
    if dIndex_floor == dIndex_ceiling:
        if dIndex_floor < nDivisions: 
            plp[dIndex_floor] += plpw*director
            if plp[dIndex_floor] < 0: plp[dIndex_floor] = 0
    #---[2-2]: The ceiling division is right above the floor division
    elif dIndex_ceiling == dIndex_floor+1:
        vpDensity   = plpw/(plpp_high-plpp_low)
        dPos_center = round(dIndex_ceiling*dHeight, pPrecision)
        #[2-2-1]: Floor Part
        if dIndex_floor < nDivisions: 
            plp[dIndex_floor] += vpDensity*(dPos_center-plpp_low)*director
            if plp[dIndex_floor] < 0: plp[dIndex_floor] = 0
        #[2-2-2]: Ceiling Part
        if dIndex_ceiling < nDivisions: 
            plp[dIndex_ceiling] += vpDensity*(plpp_high-dPos_center)*director
            if plp[dIndex_ceiling] < 0: plp[dIndex_ceiling] = 0
    #---[2-3]: There exist at least one divisions between the floor and the ceiling division
    else:
        vpDensity = plpw/(plpp_high-plpp_low)
        #[2-3-1]: Floor Part
        dPos = round((dIndex_floor+1)*dHeight, pPrecision)
        dVol = vpDensity*(dPos-plpp_low)
        plp[dIndex_floor] += dVol*director
        if plp[dIndex_floor] < 0: plp[dIndex_floor] = 0
        #[2-3-2]: Middle Part
        dVol = vpDensity*dHeight
        plIdx_beg = dIndex_floor+1
        plIdx_end = min(dIndex_ceiling, nDivisions)
        for plIndex in range (plIdx_beg, plIdx_end): 
            plp[plIndex] += dVol*director
            if plp[plIndex] < 0: plp[plIndex] = 0
        #[2-3-3]: Ceiling Part
        if dIndex_ceiling < nDivisions:
            dPos = round(dIndex_ceiling*dHeight, pPrecision)
            dVol = vpDensity*(plpp_high-dPos)
            plp[dIndex_ceiling] += dVol*director
            if plp[dIndex_ceiling] < 0: plp[dIndex_ceiling] = 0

def generate(intervalID, precisions, timestamp, klines, nSamples, gammaFactor, deltaFactor, prominence, distance, height, analysisResults, **_):
    #[1]: Parameters
    ivps       = analysisResults
    pPrecision = precisions['price']
    baseUnit   = pow(10, -pPrecision)
    func_gnitt = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl  = auxiliaries.getTimestampList_byNTicks

    #[2]: Analysis counter
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    ivp_prev       = ivps.get(timestamp_prev, None)
    analysisCount  = 0 if ivp_prev is None else ivp_prev['analysisCount']+1

    #[3]: Klines
    kl_this    = klines[timestamp]
    kl_this_op = kl_this[KLINDEX_OPENPRICE]
    kl_this_hp = kl_this[KLINDEX_HIGHPRICE]
    kl_this_cp = kl_this[KLINDEX_CLOSEPRICE]
    if ivp_prev is None:
        lastOpenPrice  = kl_this_op
        lastClosePrice = kl_this_cp
        priceMax       = kl_this_hp
    else:
        lastOpenPrice  = ivp_prev['lastOpenPrice']
        lastClosePrice = ivp_prev['lastClosePrice']
        priceMax       = ivp_prev['priceMax']
        if kl_this_op is not None:
            lastOpenPrice = kl_this_op
        if kl_this_cp is not None:
            lastClosePrice = kl_this_cp
        if kl_this_hp is not None and (priceMax is None or priceMax < kl_this_hp):
            priceMax = kl_this_hp

    #[4]: Division Height & Volume Price Level Profiles Preparation
    if analysisCount < nSamples-1 or priceMax is None or lastClosePrice is None:
        betaFactor  = None
        divHeight   = None
        vplp        = None
    else:
        betaFactor = round(lastClosePrice*gammaFactor, pPrecision)
        p_max     = priceMax
        p_max_OOM = math.floor(math.log(p_max, 10))
        p_max_MSD = int(p_max/pow(10, p_max_OOM))
        if p_max_MSD == 10: 
            p_max_MSD = 1
            p_max_OOM += 1
        dCeiling_MSD = (int(p_max_MSD/1)+1)*1
        dCeiling_OOM = p_max_OOM
        if dCeiling_MSD == 10: 
            dCeiling_MSD = 1
            dCeiling_OOM += 1
        dCeiling = dCeiling_MSD*pow(10, dCeiling_OOM)

        divHeight_min = betaFactor/10
        divHeight_min_OOM = math.floor(math.log(divHeight_min, 10))
        divHeight_min_MSD = int(divHeight_min/pow(10, divHeight_min_OOM))
        if divHeight_min_MSD == 10: 
            divHeight_min_MSD = 1
            divHeight_min_OOM += 1
        divHeight_MSD = int(divHeight_min_MSD)
        divHeight_OOM = divHeight_min_OOM
        if divHeight_MSD == 0: 
            divHeight_MSD = 1
        _divHeight = divHeight_MSD*pow(10, divHeight_OOM)
        nBaseUnitsWithinDivHeight = int(_divHeight/baseUnit)
        if nBaseUnitsWithinDivHeight == 0: divHeight = round(baseUnit,                           pPrecision)
        else:                              divHeight = round(baseUnit*nBaseUnitsWithinDivHeight, pPrecision)

        nDivisions = math.ceil(dCeiling/divHeight)

        vplp_prev = ivp_prev['volumePriceLevelProfile']
        if vplp_prev is None:
            vals = []
            for ts in func_gtsl(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False):
                kl = klines[ts]
                vb = kl[KLINDEX_VOLBASE]
                lp = kl[KLINDEX_LOWPRICE]
                hp = kl[KLINDEX_HIGHPRICE]
                if vb is None or lp is None or hp is None:
                    vals = None
                    break
                vals.append((vb, lp, hp))
            if vals:
                vplp = numpy.zeros(nDivisions)
                for vb, lp, hp in vals:
                    __addPriceLevelProfile(vb, lp, hp, vplp, divHeight, pPrecision)
            else:
                vplp = None
        else:
            nDivs_prev     = len(vplp_prev)
            divHeight_prev = ivp_prev['divisionHeight']
            if divHeight_prev == divHeight and nDivs_prev == nDivisions: 
                vplp = numpy.copy(vplp_prev)
            else:
                vplp = numpy.zeros(nDivisions)
                for dIdx_prev in range (nDivs_prev):
                    divPos_low_prev  = round(divHeight_prev*dIdx_prev,     pPrecision)
                    divPos_high_prev = round(divHeight_prev*(dIdx_prev+1), pPrecision)
                    __addPriceLevelProfile(vplp_prev[dIdx_prev], divPos_low_prev, divPos_high_prev, vplp, divHeight, pPrecision)

    #[5]: Volume Price Level Profile Update
    if vplp is not None and ivp_prev['volumePriceLevelProfile'] is not None:
        vplp = vplp*(1-1/nSamples) 
        vb   = kl_this[KLINDEX_VOLBASE]
        lp   = kl_this[KLINDEX_LOWPRICE]
        hp   = kl_this[KLINDEX_HIGHPRICE]
        if vb is not None and lp is not None and hp is not None:
            __addPriceLevelProfile(vb, lp, hp, vplp, divHeight, pPrecision)
        
    #[6]: Volume Price Level Profile Boundaries
    if vplp is None or numpy.sum(vplp) == 0:
        vplp_Filtered     = None
        vplp_Filtered_Max = None
        vplp_Boundaries   = None
    else:
        #[6-1]: Gaussian Smoothing
        vplp_Filtered = scipy.ndimage.gaussian_filter1d(input = vplp, sigma = deltaFactor)
        vplp_Filtered_Max = numpy.max(vplp_Filtered)
        
        #[6-2]: Strict Search
        prominence_eff    = vplp_Filtered_Max * prominence
        height_peak_eff   = vplp_Filtered_Max * height
        height_valley_eff = vplp_Filtered_Max * (1.0 - height)
        p_curr, _ = scipy.signal.find_peaks( vplp_Filtered, prominence = prominence_eff,       distance = distance, height =  height_peak_eff)
        v_curr, _ = scipy.signal.find_peaks(-vplp_Filtered, prominence = prominence_eff * 0.5, distance = distance, height = -height_valley_eff)

        #[6-3]: Boundaries Extraction
        vplp_Boundaries = sorted(p_curr.tolist() + v_curr.tolist())

    #[7]: Near VPLP Boundaries
    if vplp_Boundaries is None:
        vplp_nearBoundaries = [None]*10
    else:
        vplp_nearBoundaries_down = [None]*5
        vplp_nearBoundaries_up   = [None]*5
        dIndex_openPrice    = lastOpenPrice//divHeight
        bIndex_nearestAbove = None
        for bIndex, dIndex in enumerate(vplp_Boundaries):
            if dIndex_openPrice <= dIndex: 
                bIndex_nearestAbove = bIndex
                break
        if bIndex_nearestAbove is None:
            idx_up_beg   = len(vplp_Boundaries)
            idx_down_beg = len(vplp_Boundaries)-5
        else:
            idx_up_beg   = bIndex_nearestAbove
            idx_down_beg = bIndex_nearestAbove-5
        for i in range (5):
            idx_down_target = idx_down_beg+i
            idx_up_target   = idx_up_beg  +i
            if 0 <= idx_down_target < len(vplp_Boundaries):
                dIndex = vplp_Boundaries[idx_down_target]
                vplp_nearBoundaries_down[i] = round((dIndex+0.5)*divHeight, pPrecision)
            if 0 <= idx_up_target < len(vplp_Boundaries):
                dIndex = vplp_Boundaries[idx_up_target]
                vplp_nearBoundaries_up[i] = round((dIndex+0.5)*divHeight, pPrecision)
        vplp_nearBoundaries = tuple(vplp_nearBoundaries_down+vplp_nearBoundaries_up)

    #[8]: Result Formatting & Saving
    ivpResult = {'lastOpenPrice':                          lastOpenPrice,
                 'lastClosePrice':                         lastClosePrice,
                 'priceMax':                               priceMax,
                 'gammaFactor':                            gammaFactor, 
                 'betaFactor':                             betaFactor,
                 'divisionHeight':                         divHeight, 
                 'volumePriceLevelProfile':                vplp,
                 'volumePriceLevelProfile_Filtered':       vplp_Filtered, 
                 'volumePriceLevelProfile_Filtered_Max':   vplp_Filtered_Max, 
                 'volumePriceLevelProfile_Boundaries':     vplp_Boundaries,
                 'volumePriceLevelProfile_NearBoundaries': vplp_nearBoundaries,
                 'analysisCount':                          analysisCount}
    ivps[timestamp] = ivpResult

    #[9]: Memory Optimization References
    return (2, nSamples+1)
#ANALYSIS GENERATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#LINEARIZATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def linearize(intervalID, analysisCode, analysisResult):
    nearBoundaries = analysisResult['volumePriceLevelProfile_NearBoundaries']
    lRes = {f'{intervalID}_{analysisCode}_NB{nbIndex}': nearBoundaries[nbIndex] for nbIndex in range (len(nearBoundaries))}
    return lRes
#LINEARIZATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYZER FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_maximum_market_data_reference_length(cac_iID):
    #[1]: Master Check
    if not cac_iID['IVP_Master']:
        return 0
    
    #[2]: MMDRL
    nSamples = cac_iID['IVP_NSamples']
    mmdrl = nSamples

    #[3]: Return MMDRL
    return mmdrl
#ANALYZER FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#CHART DRAWER FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
CD_FULL_DRAW_SIGNALS        = 0b11
CD_VVR_PRECISIONCOMPENSATOR = None
CD_VVR_CENTERVALUE          = None
CD_VVR_DEFAULT              = None



def cd_get_initial_configuration():
    #[1]: Indicator Configuration
    oc = dict()

    #[2]: Configuration Setup
    oc['IVP_Master'] = False
    oc['IVP_NSamples']    = 288
    oc['IVP_GammaFactor'] = 0.010 #0.005 ~ 0.100
    oc['IVP_DeltaFactor'] = 1.0   #0.1   ~ 10.0
    oc['IVP_Prominence']  = 0.10  #0.01  ~ 1.00
    oc['IVP_Distance']    = 5     #1     ~ 100
    oc['IVP_Height']      = 0.50  #0.00  ~ 1.00
    oc['IVP_VPLP_Display']      = True
    oc['IVP_VPLP_DisplayWidth'] = 0.2
    oc['IVP_VPLP_ColorR%DARK']  = random.randint(64,255); oc['IVP_VPLP_ColorG%DARK']  = random.randint(64,255); oc['IVP_VPLP_ColorB%DARK']  = random.randint(64,255); oc['IVP_VPLP_ColorA%DARK']  = 30
    oc['IVP_VPLP_ColorR%LIGHT'] = random.randint(64,255); oc['IVP_VPLP_ColorG%LIGHT'] = random.randint(64,255); oc['IVP_VPLP_ColorB%LIGHT'] = random.randint(64,255); oc['IVP_VPLP_ColorA%LIGHT'] = 30
    oc['IVP_VPLPB_Display'] = True
    oc['IVP_VPLPB_ColorR%DARK']  = random.randint(64,255); oc['IVP_VPLPB_ColorG%DARK']  = random.randint(64,255); oc['IVP_VPLPB_ColorB%DARK']  = random.randint(64,255); oc['IVP_VPLPB_ColorA%DARK']  = 150
    oc['IVP_VPLPB_ColorR%LIGHT'] = random.randint(64,255); oc['IVP_VPLPB_ColorG%LIGHT'] = random.randint(64,255); oc['IVP_VPLPB_ColorB%LIGHT'] = random.randint(64,255); oc['IVP_VPLPB_ColorA%LIGHT'] = 150
    oc['IVP_VPLPB_DisplayRegion'] = 0.100

    #[3]: Configuration Return
    return oc



def cd_initialize_settings_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'INDICATOR_BLOCKTITLE_IVPDISPLAY',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:IVPDISPLAY'), 'fontSize': 90, 'anchor': 'SW'}))
    gList.append(({'NAME':               'INDICATOR_VPLP_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -650, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:VPLPDISPLAY'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_VPLP_DISPLAYSWITCH',
                   'TYPE':               'switch_typeB',
                   'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                   'groupOrder': 0, 'xPos': 1900, 'yPos': -650, 'width':  500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': 'IVP_DisplaySwitch_VPLP'}))
    gList.append(({'NAME':               'INDICATOR_VPLP_COLORTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2500, 'yPos': -650, 'width':  700, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_VPLP_COLOR',
                   'TYPE':               'LED_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3300, 'yPos': -650, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True}))
    gList.append(({'NAME':               'INDICATOR_VPLP_DISPLAYWIDTHTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1000, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAYWIDTH'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_VPLP_DISPLAYWIDTHSLIDER',
                   'TYPE':               'slider_typeA',
                   'PAGEOBJECTFUNCTION': ['valueUpdateFunction',],
                   'groupOrder': 0, 'xPos': 1300, 'yPos':  -950, 'width': 2000, 'height': 150, 'style': 'styleA', 'name': 'IVP_DisplayWidthSlider_VPLP'}))
    gList.append(({'NAME':               'INDICATOR_VPLP_DISPLAYWIDTHVALUETEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3400, 'yPos': -1000, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_VPLPB_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1350, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:VPLPBDISPLAY'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_VPLPB_DISPLAYSWITCH',
                   'TYPE':               'switch_typeB',
                   'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                   'groupOrder': 0, 'xPos': 1900, 'yPos': -1350, 'width':  500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': 'IVP_DisplaySwitch_VPLPB'}))
    gList.append(({'NAME':               'INDICATOR_VPLPB_COLORTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2500, 'yPos': -1350, 'width':  700, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_VPLPB_COLOR',
                   'TYPE':               'LED_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3300, 'yPos': -1350, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True}))
    gList.append(({'NAME':               'INDICATOR_VPLPB_DISPLAYREGIONTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1700, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAYREGION'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_VPLPB_DISPLAYREGIONSLIDER',
                   'TYPE':               'slider_typeA',
                   'PAGEOBJECTFUNCTION': ['valueUpdateFunction',],
                   'groupOrder': 0, 'xPos': 1300, 'yPos': -1650, 'width': 2000, 'height': 150, 'style': 'styleA', 'name': 'IVP_VPLPBDisplayRegion'}))
    gList.append(({'NAME':               'INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3400, 'yPos': -1700, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_BLOCKTITLE_IVPPARAMS',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -2000, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:IVPPARAMS'), 'fontSize': 90, 'anchor': 'SW'}))
    gList.append(({'NAME':               'INDICATOR_INTERVAL_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -2350, 'width': 1900, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_INTERVAL_INPUTTEXT',
                   'TYPE':               'textInputBox_typeA',
                   'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                   'groupOrder': 0, 'xPos': 2000, 'yPos': -2350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'IVP_Interval'}))
    gList.append(({'NAME':               'INDICATOR_GAMMAFACTOR_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -2700, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:IVPGAMMAFACTOR'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_GAMMAFACTOR_SLIDER',
                   'TYPE':               'slider_typeA',
                   'PAGEOBJECTFUNCTION': ['valueUpdateFunction',],
                   'groupOrder': 0, 'xPos': 1100, 'yPos': -2650, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_GammaFactor', 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_GAMMAFACTOR_VALUETEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3300, 'yPos': -2700, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_DELTAFACTOR_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -3050, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:IVPDELTAFACTOR'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_DELTAFACTOR_SLIDER',
                   'TYPE':               'slider_typeA',
                   'PAGEOBJECTFUNCTION': ['valueUpdateFunction',],
                   'groupOrder': 0, 'xPos': 1100, 'yPos': -3000, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_DeltaFactor', 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_DELTAFACTOR_VALUETEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3300, 'yPos': -3050, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_PROMINENCE_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -3400, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:IVPPROMINENCE'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_PROMINENCE_SLIDER',
                   'TYPE':               'slider_typeA',
                   'PAGEOBJECTFUNCTION': ['valueUpdateFunction',],
                   'groupOrder': 0, 'xPos': 1100, 'yPos': -3350, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_Prominence', 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_PROMINENCE_VALUETEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3300, 'yPos': -3400, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_DISTANCE_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -3750, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:IVPDISTANCE'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_DISTANCE_SLIDER',
                   'TYPE':               'slider_typeA',
                   'PAGEOBJECTFUNCTION': ['valueUpdateFunction',],
                   'groupOrder': 0, 'xPos': 1100, 'yPos': -3700, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_Distance', 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_DISTANCE_VALUETEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3300, 'yPos': -3750, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_HEIGHT_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -4100, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:IVPHEIGHT'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_HEIGHT_SLIDER',
                   'TYPE':               'slider_typeA',
                   'PAGEOBJECTFUNCTION': ['valueUpdateFunction',],
                   'groupOrder': 0, 'xPos': 1100, 'yPos': -4050, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_Height', 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_HEIGHT_VALUETEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3300, 'yPos': -4100, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def cd_initialize_settings_subpage_setup(subpage, fn_get_text_pack):
    ivpLineTargets = {'VPLP':  {'text': fn_get_text_pack('GUIO_CHARTDRAWER:VPLP')},
                      'VPLPB': {'text': fn_get_text_pack('GUIO_CHARTDRAWER:VPLPB')}}
    subpage.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = ivpLineTargets, displayTargets = 'all')



def cd_match_guios_to_config(mainPage, subPage, current_GUI_Theme, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    cgt        = current_GUI_Theme
    oc         = object_configuration

    #[2]: GUIOs Update
    guios_MAIN["MAININDICATOR_IVP"].setStatus(oc['IVP_Master'],                  callStatusUpdateFunction = False)
    guios_THIS["INDICATOR_VPLP_DISPLAYSWITCH"].setStatus(oc['IVP_VPLP_Display'], callStatusUpdateFunction = False)
    guios_THIS["INDICATOR_VPLP_COLOR"].updateColor(oc[f'IVP_VPLP_ColorR%{cgt}'], 
                                                    oc[f'IVP_VPLP_ColorG%{cgt}'], 
                                                    oc[f'IVP_VPLP_ColorB%{cgt}'], 
                                                    oc[f'IVP_VPLP_ColorA%{cgt}'])
    guios_THIS["INDICATOR_VPLP_DISPLAYWIDTHSLIDER"].setSliderValue(newValue = (oc['IVP_VPLP_DisplayWidth']-0.1)/0.9*100, callValueUpdateFunction = False)
    guios_THIS["INDICATOR_VPLP_DISPLAYWIDTHVALUETEXT"].updateText(str(oc['IVP_VPLP_DisplayWidth']))
    guios_THIS["INDICATOR_VPLPB_DISPLAYSWITCH"].setStatus(oc['IVP_VPLPB_Display'], callStatusUpdateFunction = False)
    guios_THIS["INDICATOR_VPLPB_COLOR"].updateColor(oc[f'IVP_VPLPB_ColorR%{cgt}'], 
                                                    oc[f'IVP_VPLPB_ColorG%{cgt}'], 
                                                    oc[f'IVP_VPLPB_ColorB%{cgt}'], 
                                                    oc[f'IVP_VPLPB_ColorA%{cgt}'])
    vplpb_dRegion = oc['IVP_VPLPB_DisplayRegion']
    nSamples      = oc['IVP_NSamples']
    gammaFactor   = oc['IVP_GammaFactor']
    deltaFactor   = oc['IVP_DeltaFactor']
    prominence    = oc['IVP_Prominence']
    distance      = oc['IVP_Distance']
    height        = oc['IVP_Height']
    guios_THIS["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].setSliderValue(newValue = (vplpb_dRegion-0.050)*(100/0.950), callValueUpdateFunction = False)
    guios_THIS["INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT"].updateText(f"{vplpb_dRegion*100:.1f} %")
    guios_THIS["INDICATOR_INTERVAL_INPUTTEXT"].updateText(text = f"{nSamples}")
    guios_THIS["INDICATOR_GAMMAFACTOR_SLIDER"].setSliderValue(newValue = (gammaFactor-0.005)*(100/0.095), callValueUpdateFunction = False)
    guios_THIS["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(text = f"{gammaFactor*100:.1f} %")
    guios_THIS["INDICATOR_DELTAFACTOR_SLIDER"].setSliderValue(newValue = (deltaFactor-0.1)*(100/9.9), callValueUpdateFunction = False)
    guios_THIS["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(text = f"{int(deltaFactor*100)} %")
    guios_THIS["INDICATOR_PROMINENCE_SLIDER"].setSliderValue(newValue = (prominence - 0.01) * (100 / 0.99), callValueUpdateFunction = False)
    guios_THIS["INDICATOR_PROMINENCE_VALUETEXT"].updateText(text = f"{int(prominence * 100)} %")
    guios_THIS["INDICATOR_DISTANCE_SLIDER"].setSliderValue(newValue = (distance - 1) * (100 / 99), callValueUpdateFunction = False)
    guios_THIS["INDICATOR_DISTANCE_VALUETEXT"].updateText(text = f"{int(distance)}") 
    guios_THIS["INDICATOR_HEIGHT_SLIDER"].setSliderValue(newValue = height * 100.0, callValueUpdateFunction = False)
    guios_THIS["INDICATOR_HEIGHT_VALUETEXT"].updateText(text = f"{int(height * 100)} %")
    guios_THIS["INDICATORCOLOR_TARGETSELECTION"].setSelected('VPLP')
    guios_THIS["APPLYNEWSETTINGS"].deactivate()



def cd_load_analysis_configuration(mainPage, subPage, analysis_configuration, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    ac = analysis_configuration
    oc = object_configuration

    #[2]: GUIOs Update
    if ac is not None and ac['IVP_Master']:
        guios_MAIN["MAININDICATOR_IVP"].activate()
        guios_MAIN["MAININDICATOR_IVP"].setStatus(status = oc['IVP_Master'], callStatusUpdateFunction = False)
        guios_MAIN["MAININDICATORSETUP_IVP"].activate()
        guios_THIS["INDICATOR_INTERVAL_INPUTTEXT"].updateText(text = f"{ac['IVP_NSamples']}")
        guios_THIS["INDICATOR_GAMMAFACTOR_SLIDER"].setSliderValue(newValue = (ac['IVP_GammaFactor']-0.005)*(100/0.095), callValueUpdateFunction = False)
        guios_THIS["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(f"{ac['IVP_GammaFactor']*100:.1f} %")
        guios_THIS["INDICATOR_DELTAFACTOR_SLIDER"].setSliderValue(newValue = (ac['IVP_DeltaFactor']-0.1)*(100/9.9), callValueUpdateFunction = False)
        guios_THIS["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(f"{int(ac['IVP_DeltaFactor']*100):d} %")
    else:
        guios_MAIN["MAININDICATOR_IVP"].setStatus(status = False, callStatusUpdateFunction = False)
        guios_MAIN["MAININDICATOR_IVP"].deactivate()
        guios_MAIN["MAININDICATORSETUP_IVP"].deactivate()



def cd_on_settings_content_update(chart_drawer, main_page, sub_page, guio_name_split):
    #[1]: Instances
    setter                      = guio_name_split[1]
    oc                          = chart_drawer.objectConfig
    cgt                         = chart_drawer.currentGUITheme
    analysis_parameters         = chart_drawer.analysisParams[chart_drawer.intervalID]
    activate_save_configuration = False

    #[2]: Graphics Related
    #---[2-1]: LineSelectionBox
    if setter == 'LineSelectionBox':
        lineSelected = sub_page.GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_{lineSelected}_COLOR"].getColor()
        sub_page.GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        sub_page.GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        sub_page.GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        sub_page.GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        sub_page.GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        sub_page.GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        sub_page.GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        sub_page.GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        sub_page.GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        sub_page.GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()

    #---[2-2]: Color
    elif setter == 'Color':             
        cType = guio_name_split[2]
        sub_page.GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(sub_page.GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                         gValue = int(sub_page.GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                         bValue = int(sub_page.GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                         aValue = int(sub_page.GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(sub_page.GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        sub_page.GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        sub_page.GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()

    #---[2-3]: ApplyColor
    elif setter == 'ApplyColor':        
        lineSelected = sub_page.GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(sub_page.GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(sub_page.GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(sub_page.GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(sub_page.GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        sub_page.GUIOs[f"INDICATOR_{lineSelected}_COLOR"].updateColor(color_r, color_g, color_b, color_a)
        sub_page.GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        sub_page.GUIOs['APPLYNEWSETTINGS'].activate()

    #---[2-4]: DisplayWidthSlider
    elif setter == 'DisplayWidthSlider': 
        lineTarget = guio_name_split[2]
        sliderValue = sub_page.GUIOs[f"INDICATOR_{lineTarget}_DISPLAYWIDTHSLIDER"].getSliderValue()
        sub_page.GUIOs[f"INDICATOR_{lineTarget}_DISPLAYWIDTHVALUETEXT"].updateText(str(round(sliderValue/100*0.9+0.1, 2)))
        sub_page.GUIOs['APPLYNEWSETTINGS'].activate()
        
    #---[2-5]: DisplaySwitch
    elif setter == 'DisplaySwitch':     
        sub_page.GUIOs['APPLYNEWSETTINGS'].activate()

    #---[2-6]: VPLPBDisplayRegion
    elif setter == 'VPLPBDisplayRegion': 
        #Get new VPLPBDisplayRegion
        sliderValue = sub_page.GUIOs["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].getSliderValue()
        drValue = sliderValue/100*0.950+0.050
        sub_page.GUIOs["INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT"].updateText(f"{drValue*100:.1f} %")
        sub_page.GUIOs['APPLYNEWSETTINGS'].activate()
        
    #---[2-7]: ApplySettings
    elif setter == 'ApplySettings':
        #UpdateTracker Initialization
        updateTracker = [False, False] #[0]: VPLP, [1]: VPLPB
        #Check for any changes in the configuration
        #---IVP Master
        ivpMaster_previous = oc['IVP_Master']
        oc['IVP_Master'] = main_page.GUIOs["MAININDICATOR_IVP"].getStatus()
        if ivpMaster_previous != oc['IVP_Master']: updateTracker = [True, True]
        #---displaySwitch - VPLP
        vplpDisplay_prev = oc['IVP_VPLP_Display']
        oc['IVP_VPLP_Display'] = sub_page.GUIOs["INDICATOR_VPLP_DISPLAYSWITCH"].getStatus()
        if vplpDisplay_prev != oc['IVP_VPLP_Display']: updateTracker[0] = True
        #---displaySwitch - VPLB
        vplpbDisplay_prev = oc['IVP_VPLPB_Display']
        oc['IVP_VPLPB_Display'] = sub_page.GUIOs["INDICATOR_VPLPB_DISPLAYSWITCH"].getStatus()
        if vplpbDisplay_prev != oc['IVP_VPLPB_Display']: updateTracker[1] = True
        #---displayWidth - VPLP
        vplpDisplayWidth_prev = oc['IVP_VPLP_DisplayWidth']
        oc['IVP_VPLP_DisplayWidth'] = round(sub_page.GUIOs["INDICATOR_VPLP_DISPLAYWIDTHSLIDER"].getSliderValue()/100*0.9+0.1, 2)
        if vplpDisplayWidth_prev != oc['IVP_VPLP_DisplayWidth']: updateTracker[0] = True
        #---VPLPB Display Region
        vplpbDisplayRegion_prev = oc['IVP_VPLPB_DisplayRegion']
        oc['IVP_VPLPB_DisplayRegion'] = round(sub_page.GUIOs["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].getSliderValue()/100*0.950+0.050, 3)
        if vplpbDisplayRegion_prev != oc['IVP_VPLPB_DisplayRegion']: updateTracker[1] = True
        #---Colors
        for targetLine in ('VPLP', 'VPLPB'):
            color_previous = (oc[f'IVP_{targetLine}_ColorR%{cgt}'],
                              oc[f'IVP_{targetLine}_ColorG%{cgt}'],
                              oc[f'IVP_{targetLine}_ColorB%{cgt}'],
                              oc[f'IVP_{targetLine}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_{targetLine}_COLOR"].getColor()
            oc[f'IVP_{targetLine}_ColorR%{cgt}'] = color_r
            oc[f'IVP_{targetLine}_ColorG%{cgt}'] = color_g
            oc[f'IVP_{targetLine}_ColorB%{cgt}'] = color_b
            oc[f'IVP_{targetLine}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): 
                if   targetLine == 'VPLP':  updateTracker[0] = True
                elif targetLine == 'VPLPB': updateTracker[1] = True
        #Content Update Handling
        drawSignal = 0
        drawSignal += 0b01*updateTracker[0] #VPLP
        drawSignal += 0b10*updateTracker[1] #VPLPB
        if drawSignal:
            chart_drawer._drawer_RemoveDrawings(analysisCode    = 'IVP', gRemovalSignal = drawSignal) #Remove previous graphics
            chart_drawer.addBufferZone_toDrawQueue(analysisCode = 'IVP', drawSignal     = drawSignal) #Update draw queue
        #Settings Control Button
        sub_page.GUIOs['APPLYNEWSETTINGS'].deactivate()
        activate_save_configuration = True

    #[3]: Analysis Related
    #---[3-1]: Interval
    elif setter == 'Interval':
        #Get new nSamples
        try:    _nSamples = int(sub_page.GUIOs["INDICATOR_INTERVAL_INPUTTEXT"].getText())
        except: _nSamples = None
        #Save the new value to the object config dictionary
        oc['IVP_NSamples'] = _nSamples
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-2]: Gamma Factor
    elif setter == 'GammaFactor':
        #Get new Gamma Factor
        gammaFactor = round(sub_page.GUIOs["INDICATOR_GAMMAFACTOR_SLIDER"].getSliderValue()/100*0.095+0.005, 3)
        sub_page.GUIOs["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(f"{gammaFactor*100:.1f} %")
        oc['IVP_GammaFactor'] = gammaFactor
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-3]: Delta Factor
    elif setter == 'DeltaFactor':
        #Get new Delta Factor
        deltaFactor = round(sub_page.GUIOs["INDICATOR_DELTAFACTOR_SLIDER"].getSliderValue()/100*9.9+0.1, 1)
        sub_page.GUIOs["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(f"{int(deltaFactor*100)} %")
        oc['IVP_DeltaFactor'] = deltaFactor
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-4]: Prominence
    elif setter == 'Prominence':
        #Get new Prominence
        prominence = round(sub_page.GUIOs["INDICATOR_PROMINENCE_SLIDER"].getSliderValue()/100*0.99+0.01, 2)
        sub_page.GUIOs["INDICATOR_PROMINENCE_VALUETEXT"].updateText(f"{int(prominence*100)} %")
        oc['IVP_Prominence'] = prominence
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-5]: Distance
    elif setter == 'Distance':
        #Get new Distance
        distance = int(round(sub_page.GUIOs["INDICATOR_DISTANCE_SLIDER"].getSliderValue()/100*99+1))
        sub_page.GUIOs["INDICATOR_DISTANCE_VALUETEXT"].updateText(f"{distance}")
        oc['IVP_Distance'] = distance
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-6]: Height
    elif setter == 'Height':
        #Get new Height
        height = round(sub_page.GUIOs["INDICATOR_HEIGHT_SLIDER"].getSliderValue()/100, 2)
        sub_page.GUIOs["INDICATOR_HEIGHT_VALUETEXT"].updateText(f"{int(height*100)} %")
        oc['IVP_Height'] = height
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #[3]: Return Status Flag
    return activate_save_configuration



def cd_on_position_highlight_update(chart_drawer):
    #[1]: Instances
    oc        = chart_drawer.objectConfig
    tsHovered = chart_drawer.posHighlight_hoveredPos[0]
    dAgg      = chart_drawer._data_agg[chart_drawer.intervalID]
    dBox_g_kp_dt2 = chart_drawer.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2']
    
    #[2]: Existence & Display Check
    if 'IVP' not in dAgg:            return False
    if tsHovered not in dAgg['IVP']: return False
    if not oc['IVP_Master']:         return False

    #[3]: Base Text & Styles
    text_display = f" [IVP]"

    #[4]: Displaying Text & Style Construction
    ivp = dAgg['IVP'][tsHovered]
    ivpr_vplp    = ivp['volumePriceLevelProfile']
    ivpr_gFactor = ivp['gammaFactor']
    ivpr_bFactor = ivp['betaFactor']
    if ivpr_vplp is None: textBlock  = " nDivisions: NONE, Gamma Factor: NONE"
    else:                 textBlock  = f" nDivisions: {len(ivpr_vplp):,}, Gamma Factor: {ivpr_gFactor*100:.2f} % [{ivpr_bFactor}]"
    text_display += textBlock

    #[5]: Update Text Element
    dBox_g_kp_dt2.setText(text_display, 'DEFAULT')

    #[6]: Return Result
    return True



def cd_on_position_selection_update(chart_drawer):
    ph_selPos = chart_drawer.posHighlight_selectedPos
    dAgg      = chart_drawer._data_agg[chart_drawer.intervalID]
    aParams   = chart_drawer.analysisParams[chart_drawer.intervalID]

    #IVP Update
    if 'IVP' in aParams:
        if   ph_selPos is None:        chart_drawer._drawer_RemoveDrawings(analysisCode = 'IVP', gRemovalSignal = 0b01)
        elif ph_selPos in dAgg['IVP']: chart_drawer._drawer_sendDrawSignal(analysisCode = 'IVP', timestamp = ph_selPos, drawSignal = 0b01)



def cd_check_vertical_extremas(chart_drawer):
    pass



def cd_draw(chart_drawer, drawSignal, timestamp, analysisCode):
    #[1]: Parameters
    oc  = chart_drawer.objectConfig
    cgt = chart_drawer.currentGUITheme
    rclcg        = chart_drawer.displayBox_graphics['KLINESPRICE']['RCLCG']
    rclcg_xFixed = chart_drawer.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED']

    #[2]: Master & Display Status
    if not oc['IVP_Master']: return 0b00

    #[3]: Draw Signal
    if drawSignal is None: drawSignal = 0b11
    if not drawSignal:     return 0b00

    #[4]: Data Acquisition
    dAgg = chart_drawer._data_agg[chart_drawer.intervalID]
    kline = dAgg['kline'][timestamp]
    ivp   = dAgg[analysisCode][timestamp]

    #[5]: Drawing
    drawn = 0b00
    #---[5-1]: Volume Price Level Profile
    if drawSignal&0b01 and oc['IVP_VPLP_Display'] and timestamp == chart_drawer.posHighlight_selectedPos:
        #[5-1-1]: Previous Drawing Removal
        rclcg_xFixed.removeGroup(groupName = 'IVP_VPLP')
        #[5-1-2]: Drawing
        vplp_f    = ivp['volumePriceLevelProfile_Filtered']
        vplp_fMax = ivp['volumePriceLevelProfile_Filtered_Max']
        if vplp_fMax is not None:
            dHeight  = ivp['divisionHeight']
            widthMax = 100*oc['IVP_VPLP_DisplayWidth']
            color = (oc[f'IVP_VPLP_ColorR%{cgt}'],
                     oc[f'IVP_VPLP_ColorG%{cgt}'],
                     oc[f'IVP_VPLP_ColorB%{cgt}'],
                     oc[f'IVP_VPLP_ColorA%{cgt}'])
            for dIndex, dStrength in enumerate (vplp_f):
                dWidth = round(widthMax*dStrength/vplp_fMax, 3)
                shape_x      = 100-dWidth
                shape_width  = dWidth
                shape_y      = dHeight*dIndex
                shape_height = dHeight
                rclcg_xFixed.addShape_Rectangle(x = shape_x, width  = shape_width, 
                                                y = shape_y, height = shape_height,
                                                color = color,
                                                shapeName = dIndex, shapeGroupName = 'IVP_VPLP', layerNumber = 10)
        #[5-1-3]: Drawn Flag Update
        drawn += 0b01
    #---[5-2]: Volume Price Level Profile Boundaries
    if drawSignal&0b10 and oc['IVP_VPLPB_Display']:
        #[5-2-1]: Previous Drawing Removal
        rclcg.removeGroup(groupName = f'IVP_VPLPB_{timestamp}')
        #[5-2-2]: Drawing
        vplp_b = ivp['volumePriceLevelProfile_Boundaries']
        if vplp_b is not None:
            ts_open  = kline[KLINDEX_OPENTIME]
            ts_close = kline[KLINDEX_CLOSETIME]
            tsWidth  = ts_close-ts_open+1
            dr       = oc['IVP_VPLPB_DisplayRegion']
            lcp      = ivp['lastClosePrice']
            dHeight  = ivp['divisionHeight']
            pb_dr_beg = lcp*(1-dr)
            pb_dr_end = lcp*(1+dr)
            dIdx_bdr_beg = max(int(pb_dr_beg/dHeight), 0)
            dIdx_bdr_end = min(int(pb_dr_end/dHeight), len(ivp['volumePriceLevelProfile'])-1)
            color_rgb = (oc[f'IVP_VPLPB_ColorR%{cgt}'],
                         oc[f'IVP_VPLPB_ColorG%{cgt}'],
                         oc[f'IVP_VPLPB_ColorB%{cgt}'])
            color_a   = oc[f'IVP_VPLPB_ColorA%{cgt}']
            vplp_f    = ivp['volumePriceLevelProfile_Filtered']
            vplp_fMax = ivp['volumePriceLevelProfile_Filtered_Max']
            shape_x      = ts_open
            shape_width  = tsWidth
            shape_height = dHeight
            for bIndex, dIndex in enumerate(vplp_b):
                if not (dIdx_bdr_beg <= dIndex <= dIdx_bdr_end): continue
                shape_y = dHeight*dIndex
                color_a_eff = int(color_a*(vplp_f[dIndex]/vplp_fMax*0.5+0.5))
                color = color_rgb+(color_a_eff,)
                rclcg.addShape_Rectangle(x = shape_x, width  = shape_width, 
                                            y = shape_y, height = shape_height,
                                            color = color,
                                            shapeName = bIndex, shapeGroupName = f'IVP_VPLPB_{timestamp}', layerNumber = 10)
        #[5-2-3]: Drawn Flag Update
        drawn += 0b10
    #[6]: Return Drawn Flag
    return drawn



def cd_remove_expired_drawings(display_box_graphics, si_viewer_index, analysis_code, timestamp):
    #[1]: Drawings Removal
    display_box_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = f'IVP_VPLPB_{timestamp}')



def cd_remove_drawings(drawn, display_box_graphics, si_viewer_index, analysis_code, graphics_removal_signal):
    #[1]: Drawings Removal
    if graphics_removal_signal&0b01: display_box_graphics['KLINESPRICE']['RCLCG_XFIXED'].removeGroup(groupName = 'IVP_VPLP')
    rclcg = display_box_graphics['KLINESPRICE']['RCLCG']
    for ts in drawn:
        if 'IVP' not in drawn[ts]: continue
        if graphics_removal_signal&0b10: rclcg.removeGroup(groupName = f'IVP_VPLPB_{ts}')



def cd_get_vertical_magnitude_anchor(object_configuration):
    return None



def cd_on_GUI_theme_update(subpage, object_configuration, current_GUI_theme):
    #[1]: Instances
    sp  = subpage
    oc  = object_configuration
    cgt = current_GUI_theme

    #[2]: GUIOs Update
    subpage.GUIOs["INDICATOR_VPLP_COLOR"].updateColor(oc[f'IVP_VPLP_ColorR%{cgt}'],
                                                      oc[f'IVP_VPLP_ColorG%{cgt}'],
                                                      oc[f'IVP_VPLP_ColorB%{cgt}'],
                                                      oc[f'IVP_VPLP_ColorA%{cgt}'])
    subpage.GUIOs["INDICATOR_VPLPB_COLOR"].updateColor(oc[f'IVP_VPLPB_ColorR%{cgt}'],
                                                       oc[f'IVP_VPLPB_ColorG%{cgt}'],
                                                       oc[f'IVP_VPLPB_ColorB%{cgt}'],
                                                       oc[f'IVP_VPLPB_ColorA%{cgt}'])



def cd_update_si_type_analysis_codes(analysis_parameters):
    return None



def cd_type_init(subPage):
    #[1]: Instances
    guios_THIS = subPage.GUIOs

    #[2]: GUIOs Update
    guios_THIS["INDICATOR_INTERVAL_INPUTTEXT"].deactivate()
    guios_THIS["INDICATOR_GAMMAFACTOR_SLIDER"].deactivate()
    guios_THIS["INDICATOR_DELTAFACTOR_SLIDER"].deactivate()
#CHART DRAWER FUNCTIONS END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUTOTRADE PAGE FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_autotrade_get_default_analysis_configuration():
    #[1]: Default Analysis Configuration
    dac = dict()

    #[2]: Setup
    dac['IVP_Master'] = False
    dac['IVP_NSamples']    = 500
    dac['IVP_GammaFactor'] = 0.010
    dac['IVP_DeltaFactor'] = 1.0
    dac['IVP_Prominence']  = 0.10
    dac['IVP_Distance']    = 5
    dac['IVP_Height']      = 0.50

    #[3]: Return
    return dac



def pg_autotrade_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               "NSAMPLESTITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80}))
    gList.append(({'NAME':               "NSAMPLESTEXTINPUTBOX",
                   'TYPE':               'textInputBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2100, 'yPos': -350, 'width': 2450, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
    gList.append(({'NAME':               "GAMMAFACTORTITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -700, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_GAMMAFACTOR'), 'fontSize': 80}))
    gList.append(({'NAME':               "GAMMAFACTORSLIDER",
                   'TYPE':               'slider_typeA',
                   'PAGEOBJECTFUNCTION': [('valueUpdateFunction', 'ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER'),],
                   'groupOrder': 0, 'xPos': 1400, 'yPos': -650, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_GammaFactor', 'fontSize': 80}))
    gList.append(({'NAME':               "GAMMAFACTORDISPLAYTEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3950, 'yPos': -700, 'width':  600, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
    gList.append(({'NAME':               "DELTAFACTORTITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1050, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_DELTAFACTOR'), 'fontSize': 80}))
    gList.append(({'NAME':               "DELTAFACTORSLIDER",
                   'TYPE':               'slider_typeA',
                   'PAGEOBJECTFUNCTION': [('valueUpdateFunction', 'ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER'),],
                   'groupOrder': 0, 'xPos': 1400, 'yPos': -1000, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_DeltaFactor', 'fontSize': 80}))
    gList.append(({'NAME':               "DELTAFACTORDISPLAYTEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3950, 'yPos': -1050, 'width':  600, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
    gList.append(({'NAME':               "PROMINENCETITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1400, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_PROMINENCE'), 'fontSize': 80}))
    gList.append(({'NAME':               "PROMINENCESLIDER",
                   'TYPE':               'slider_typeA',
                   'PAGEOBJECTFUNCTION': [('valueUpdateFunction', 'ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER'),],
                   'groupOrder': 0, 'xPos': 1400, 'yPos': -1350, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_Prominence', 'fontSize': 80}))
    gList.append(({'NAME':               "PROMINENCEDISPLAYTEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3950, 'yPos': -1400, 'width':  600, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
    gList.append(({'NAME':               "DISTANCETITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1750, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_DISTANCE'), 'fontSize': 80}))
    gList.append(({'NAME':               "DISTANCESLIDER",
                   'TYPE':               'slider_typeA',
                   'PAGEOBJECTFUNCTION': [('valueUpdateFunction', 'ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER'),],
                   'groupOrder': 0, 'xPos': 1400, 'yPos': -1700, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_Distance', 'fontSize': 80}))
    gList.append(({'NAME':               "DISTANCEDISPLAYTEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3950, 'yPos': -1750, 'width':  600, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
    gList.append(({'NAME':               "HEIGHTTITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -2100, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_HEIGHT'), 'fontSize': 80}))
    gList.append(({'NAME':               "HEIGHTSLIDER",
                   'TYPE':               'slider_typeA',
                   'PAGEOBJECTFUNCTION': [('valueUpdateFunction', 'ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER'),],
                   'groupOrder': 0, 'xPos': 1400, 'yPos': -2050, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_Height', 'fontSize': 80}))
    gList.append(({'NAME':               "HEIGHTDISPLAYTEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3950, 'yPos': -2100, 'width':  600, 'height': 250, 'style': 'styleA', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_autotrade_configure_subpage_setup(subpage, fn_get_text_pack):
    pass



def pg_autotrade_load_analysis_configuration(mainPage, subPage, analysis_configuration):
    #[1]: Main Page
    mainPage.GUIOs["INDICATORMASTERSWITCH_IVP"].setStatus(status = analysis_configuration['IVP_Master'], callStatusUpdateFunction = False)

    #[2]: Sub Page
    subPage.GUIOs["NSAMPLESTEXTINPUTBOX"].updateText(text = str(analysis_configuration['IVP_NSamples']))
    subPage.GUIOs["GAMMAFACTORSLIDER"].setSliderValue(newValue = (analysis_configuration['IVP_GammaFactor']-0.005)*(100/0.095))
    subPage.GUIOs["GAMMAFACTORDISPLAYTEXT"].updateText(text = f"{analysis_configuration['IVP_GammaFactor']*100:.1f} %")
    subPage.GUIOs["DELTAFACTORSLIDER"].setSliderValue(newValue = (analysis_configuration['IVP_DeltaFactor']-0.1)*(100/9.9))
    subPage.GUIOs["DELTAFACTORDISPLAYTEXT"].updateText(text = f"{int(analysis_configuration['IVP_DeltaFactor']*100)} %")
    subPage.GUIOs["PROMINENCESLIDER"].setSliderValue(newValue = (analysis_configuration['IVP_Prominence']-0.01)*(100/0.99))
    subPage.GUIOs["PROMINENCEDISPLAYTEXT"].updateText(text = f"{int(analysis_configuration['IVP_Prominence']*100)} %")
    subPage.GUIOs["DISTANCESLIDER"].setSliderValue(newValue = (analysis_configuration['IVP_Distance']-1)*(100/99))
    subPage.GUIOs["DISTANCEDISPLAYTEXT"].updateText(text = f"{int(analysis_configuration['IVP_Distance'])}")
    subPage.GUIOs["HEIGHTSLIDER"].setSliderValue(newValue = analysis_configuration['IVP_Height']*100)
    subPage.GUIOs["HEIGHTDISPLAYTEXT"].updateText(text = f"{int(analysis_configuration['IVP_Height']*100)} %")



def pg_autotrade_format_analysis_configuration_from_guios(mainPage, subPage):
    #[1]: Instances
    configuration = dict()

    #[2]: Configuration Construction
    configuration['IVP_Master']      = mainPage.GUIOs["INDICATORMASTERSWITCH_IVP"].getStatus()
    configuration['IVP_NSamples']    = int(subPage.GUIOs["NSAMPLESTEXTINPUTBOX"].getText())
    configuration['IVP_GammaFactor'] = round(float(subPage.GUIOs["GAMMAFACTORSLIDER"].getSliderValue()/100*(0.095)+0.005), 3)
    configuration['IVP_DeltaFactor'] = round(float(subPage.GUIOs["DELTAFACTORSLIDER"].getSliderValue()/100*(9.9)  +0.1),   1)
    configuration['IVP_Prominence']  = round(float(subPage.GUIOs["PROMINENCESLIDER"].getSliderValue()/100*(0.99)  +0.01),  2)
    configuration['IVP_Distance']    = int(round(float(subPage.GUIOs["DISTANCESLIDER"].getSliderValue()/100*(99)  +1)))
    configuration['IVP_Height']      = round(float(subPage.GUIOs["HEIGHTSLIDER"].getSliderValue()/100), 2)

    #[3]: Return Configuration
    return configuration
#AUTOTRADE PAGE FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SIMULATION RESULTS PAGE FUNCTIONS ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_simulation_result_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               "NSAMPLESTITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80}))
    gList.append(({'NAME':               "NSAMPLESDISPLAYTEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2100, 'yPos': -350, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
    gList.append(({'NAME':               "GAMMAFACTORTITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -700, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_GAMMAFACTOR'), 'fontSize': 80}))
    gList.append(({'NAME':               "GAMMAFACTORDISPLAYTEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2100, 'yPos': -700, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
    gList.append(({'NAME':               "DELTAFACTORTITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1050, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_DELTAFACTOR'), 'fontSize': 80}))
    gList.append(({'NAME':               "DELTAFACTORDISPLAYTEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2100, 'yPos': -1050, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
    gList.append(({'NAME':               "PROMINENCETITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1400, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_PROMINENCE'), 'fontSize': 80}))
    gList.append(({'NAME':               "PROMINENCEDISPLAYTEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2100, 'yPos': -1400, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
    gList.append(({'NAME':               "DISTANCETITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1750, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_DISTANCE'), 'fontSize': 80}))
    gList.append(({'NAME':               "DISTANCEDISPLAYTEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2100, 'yPos': -1750, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
    gList.append(({'NAME':               "HEIGHTTITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -2100, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_HEIGHT'), 'fontSize': 80}))
    gList.append(({'NAME':               "HEIGHTDISPLAYTEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2100, 'yPos': -2100, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_simulation_result_configure_subpage_setup(subpage, fn_get_text_pack):
    pass



def pg_simulation_result_load_analysis_configuration(mainPage, subPage, analysis_configuration, simulation_selected, fn_get_text_pack):
    if simulation_selected:
        mainPage.GUIOs["INDICATORMASTERSWITCH_IVP"].setStatus(status = analysis_configuration['IVP_Master'], callStatusUpdateFunction = False)
        subPage.GUIOs["NSAMPLESDISPLAYTEXT"].updateText(text    = f"{analysis_configuration['IVP_NSamples']}")
        subPage.GUIOs["GAMMAFACTORDISPLAYTEXT"].updateText(text = f"{analysis_configuration['IVP_GammaFactor']*100:.1f} %")
        subPage.GUIOs["DELTAFACTORDISPLAYTEXT"].updateText(text = f"{analysis_configuration['IVP_DeltaFactor']*100:.0f} %")
        subPage.GUIOs["PROMINENCEDISPLAYTEXT"].updateText(text  = f"{analysis_configuration['IVP_Prominence']*100:.0f} %")
        subPage.GUIOs["DISTANCEDISPLAYTEXT"].updateText(text    = f"{analysis_configuration['IVP_Distance']}")
        subPage.GUIOs["HEIGHTDISPLAYTEXT"].updateText(text      = f"{analysis_configuration['IVP_Height']*100:.0f} %")
    else:
        mainPage.GUIOs["INDICATORMASTERSWITCH_IVP"].setStatus(status     = False, callStatusUpdateFunction = False)
        subPage.GUIOs["NSAMPLESDISPLAYTEXT"].updateText(text    = "-")
        subPage.GUIOs["GAMMAFACTORDISPLAYTEXT"].updateText(text = "-")
        subPage.GUIOs["DELTAFACTORDISPLAYTEXT"].updateText(text = "-")
        subPage.GUIOs["PROMINENCEDISPLAYTEXT"].updateText(text  = "-")
        subPage.GUIOs["DISTANCEDISPLAYTEXT"].updateText(text    = "-")
        subPage.GUIOs["HEIGHTDISPLAYTEXT"].updateText(text      = "-")
#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------