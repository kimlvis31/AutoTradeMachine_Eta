#Imports
import auxiliaries
import random
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
ANALYSIS_CODE = 'SMA'
ANALYSIS_TYPE = 'MAIN' #('MAIN' or 'SUB')
NMAXLINES     = 10

"""
_NMAXLINES = {'IVP':     None,
              'SWING':   constants.NLINES_SWING,
              'NNA':     constants.NLINES_NNA,
              'MMACD':   constants.NLINES_MMACD,
              'DMIxADX': constants.NLINES_DMIxADX,
              'MFI':     constants.NLINES_MFI,
              'TPD':     constants.NLINES_TPD,
              'WOI':     constants.NLINES_WOI,
              'NES':     constants.NLINES_NES}
"""
#DEFINING PARAMETERS END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYSIS GENERATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def construct_analysis_parameters(configuration):
    #[1]: Instances & Initialization
    cac = configuration
    cap          = dict()
    invalidLines = defaultdict(list)

    #[2]: Analysis Parameters Construction
    if cac['SMA_Master']:
        for lineIndex in range (NMAXLINES):
            analysisCode = f'SMA_{lineIndex}'
            #[2-1]: Check Line Existence & Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue

            #[2-2]: nSamples
            nSamples = cac[f'{analysisCode}_NSamples']
            if   type(nSamples) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < nSamples:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if analysisCode in invalidLines:
                continue

            #[2-3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex':    lineIndex,
                                 'nSamples':     nSamples}

    #[3]: Return The Constructed Analysis Parameters & Invalid Lines
    return cap, invalidLines



"""
if cac['IVP_Master']:
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

if cac['SWING_Master']:
    for lineIndex in range (constants.NLINES_SWING):
        analysisCode = f'SWING_{lineIndex}'
        #[1]: Check Line Active
        lineActive = cac.get(f'{analysisCode}_LineActive', False)
        if not lineActive: continue
        #[2]: Parameters
        swingRange = cac[f'{analysisCode}_SwingRange']
        if   not type(swingRange) in (int, float): invalidLines[analysisCode].append("swingRange: Must be type 'int' or 'float'")
        elif not (0.0001 <= swingRange):           invalidLines[analysisCode].append("swingRange: Must be greater than or equal to 0.0001")
        if analysisCode in invalidLines: continue
        #[3]: Analysis Params
        cap[analysisCode] = {'analysisCode': analysisCode,
                                'lineIndex':    lineIndex,
                                'swingRange':   swingRange}  

if cac['NNA_Master']:
    for lineIndex in range (constants.NLINES_NNA):
        analysisCode = f'NNA_{lineIndex}'
        #[1]: Check Line Active
        lineActive = cac.get(f'{analysisCode}_LineActive', False)
        if not lineActive: continue
        #[2]: Parameters
        nnCode = cac[f'{analysisCode}_NeuralNetworkCode']
        alpha  = cac[f'{analysisCode}_Alpha']
        beta   = cac[f'{analysisCode}_Beta']
        if   type(nnCode) is not str:     invalidLines[analysisCode].append("nnCode: Must be type 'str'")
        if   type(alpha)  is not float:   invalidLines[analysisCode].append("alpha: Must be type 'float'")
        elif not (0.01 <= alpha <= 1.00): invalidLines[analysisCode].append("alpha: Must be greater than or equal to 0.01 and less than or equal to 1.00")
        if   type(beta) is not int:       invalidLines[analysisCode].append("beta: Must be type 'int'")
        elif not (2 <= beta <= 20):       invalidLines[analysisCode].append("beta: Must be greater than or equal to 2 and less than or equal to 20")
        if analysisCode in invalidLines: continue
        #[3]: Analysis Params
        cap[analysisCode] = {'analysisCode': analysisCode,
                                'lineIndex':    lineIndex,
                                'nnCode':       nnCode,
                                'alpha':        alpha,
                                'beta':         beta}
            
if cac['MMACD_Master']:
    analysisCode = 'MMACD'
    #[1]: Signal nSamples
    signal_nSamples = cac[f'{analysisCode}_SignalNSamples']
    if   type(signal_nSamples) is not int: invalidLines[analysisCode].append("signal_nSamples: Must be type 'int'")
    elif not 1 < signal_nSamples:          invalidLines[analysisCode].append("signal_nSamples: Must be greater than 1")
    #[2]: Activated MAs
    activatedMAs = []
    for lineIndex in range (constants.NLINES_MMACD):
        #[1]: Check Line Active
        lineActive = cac.get(f'MMACD_MA{lineIndex}_LineActive', False)
        if not lineActive: continue
        #[2]: Parameters
        nSamples = cac[f'MMACD_MA{lineIndex}_NSamples']
        if   type(nSamples) is not int: invalidLines[analysisCode].append(f"MA{lineIndex}_nSamples: Must be type 'int'")
        elif not 1 < nSamples:          invalidLines[analysisCode].append(f"MA{lineIndex}_nSamples: Must be greater than 1")
        else: activatedMAs.append(nSamples)
    #[3]: Activated MAs Sort & Params Update
    if (2 <= len(activatedMAs)) and (analysisCode not in invalidLines):
        activatedMAs.sort()
        activatedMAPairs = [(activatedMAs[maptIndex_S], activatedMAs[maptIndex_L]) for maptIndex_S in range (0, len(activatedMAs)-1) for maptIndex_L in range (maptIndex_S+1, len(activatedMAs))]
        maxMANSamples = max(activatedMAs)
        cap['MMACD'] = {'analysisCode': analysisCode,
                        'signal_nSamples':  signal_nSamples,
                        'activatedMAs':     activatedMAs,
                        'activatedMAPairs': activatedMAPairs,
                        'maxMANSamples':    maxMANSamples}
        
if cac['DMIxADX_Master']:
    for lineIndex in range (constants.NLINES_DMIxADX):
        analysisCode = f'DMIxADX_{lineIndex}'
        #[1]: Check Line Active
        lineActive = cac.get(f'{analysisCode}_LineActive', False)
        if not lineActive: continue
        #[2]: Parameters
        nSamples = cac[f'{analysisCode}_NSamples']
        if   type(nSamples) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
        elif not 1 < nSamples:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
        if analysisCode in invalidLines: continue
        #[3]: Analysis Params
        cap[analysisCode] = {'analysisCode': analysisCode,
                                'lineIndex':    lineIndex,
                                'nSamples':     nSamples}

if cac['MFI_Master']:
    for lineIndex in range (constants.NLINES_MFI):
        analysisCode = f'MFI_{lineIndex}'
        #[1]: Check Line Active
        lineActive = cac.get(f'{analysisCode}_LineActive', False)
        if not lineActive: continue
        #[2]: Parameters
        nSamples = cac[f'{analysisCode}_NSamples']
        if   type(nSamples) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
        elif not 1 < nSamples:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
        if analysisCode in invalidLines: continue
        #[3]: Analysis Params
        cap[analysisCode] = {'analysisCode': analysisCode,
                                'lineIndex':    lineIndex,
                                'nSamples':     nSamples}

if cac['TPD_Master']:
    for lineIndex in range (constants.NLINES_TPD):
        analysisCode = f'TPD_{lineIndex}'
        #[1]: Check Line Active
        lineActive = cac.get(f'{analysisCode}_LineActive', False)
        if not lineActive: continue
        #[2]: Parameters
        viewLength = cac[f'{analysisCode}_ViewLength']
        nSamples   = cac[f'{analysisCode}_NSamples']
        nSamplesMA = cac[f'{analysisCode}_NSamplesMA']
        if   type(viewLength) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
        elif not 1 < viewLength:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
        if   type(nSamples) is not int:   invalidLines[analysisCode].append("nSamples: Must be type 'int'")
        elif not 1 < nSamples:            invalidLines[analysisCode].append("nSamples: Must be greater than 1")
        if   type(nSamplesMA) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
        elif not 1 < nSamplesMA:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
        if analysisCode in invalidLines: continue
        #[3]: Analysis Params
        cap[analysisCode] = {'analysisCode': analysisCode,
                                'lineIndex':    lineIndex,
                                'viewLength':   viewLength,
                                'nSamples':     nSamples,
                                'nSamplesMA':   nSamplesMA}

if cac['WOI_Master']:
    for lineIndex in range (constants.NLINES_WOI):
        analysisCode = f'WOI_{lineIndex}'
        #[1]: Check Line Active
        lineActive = cac.get(f'{analysisCode}_LineActive', False)
        if not lineActive: continue
        #[2]: Parameters
        nSamples = cac[f'{analysisCode}_NSamples']
        if   type(nSamples) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
        elif not 1 < nSamples:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
        if analysisCode in invalidLines: continue
        #[3]: Analysis Params
        cap[analysisCode] = {'analysisCode': analysisCode,
                                'lineIndex':    lineIndex,
                                'nSamples':     nSamples}
        
if cac['NES_Master']:
    for lineIndex in range (constants.NLINES_NES):
        analysisCode = f'NES_{lineIndex}'
        #[1]: Check Line Active
        lineActive = cac.get(f'{analysisCode}_LineActive', False)
        if not lineActive: continue
        #[2]: Parameters
        nSamples   = cac[f'{analysisCode}_NSamples']
        if   type(nSamples) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
        elif not 1 < nSamples:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
        if analysisCode in invalidLines: continue
        #[3]: Analysis Params
        cap[analysisCode] = {'analysisCode': analysisCode,
                                'lineIndex':    lineIndex,
                                'nSamples':     nSamples}

#[3]: Return The Constructed Analysis Parameters & Invalid Lines
if invalidLines:
    cap = None
return cap, invalidLines
"""

def generate(intervalID, precisions, timestamp, klines, nSamples, analysisResults, **_):
    #[1]: Instances
    smas       = analysisResults
    pPrecision = precisions['price']
    func_gnitt = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl  = auxiliaries.getTimestampList_byNTicks

    #[2]: Previous Analysis & Analysis Count
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    sma_prev       = smas.get(timestamp_prev, None)

    #[3]: SMA Compuation
    if sma_prev is None or sma_prev['SMA'] is None or sma_prev['fullCompute']:
        prices = [klines[ts][KLINDEX_CLOSEPRICE] if ts in klines else None
                  for ts in func_gtsl(intervalID = intervalID,
                                      timestamp  = timestamp,
                                      nTicks     = nSamples,
                                      direction  = False)]
        if any(p is None for p in prices):
            if sma_prev is None:
                priceSum    = None
                sma         = None
                fullCompute = True
            else:
                priceSum    = sma_prev['PRICESUM']
                sma         = sma_prev['SMA']
                fullCompute = True
        else:
            priceSum    = sum(prices)
            sma         = round(priceSum / nSamples, pPrecision)
            fullCompute = False
    else:
        timestamp_exp = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -nSamples)
        priceSum_prev = sma_prev['PRICESUM']
        price_exp  = klines[timestamp_exp][KLINDEX_CLOSEPRICE]
        price_this = klines[timestamp][KLINDEX_CLOSEPRICE]
        if price_exp is None or price_this is None:
            priceSum    = None
            sma         = sma_prev['SMA']
            fullCompute = True
        else:
            priceSum    = priceSum_prev - price_exp + price_this
            sma         = round(priceSum / nSamples, pPrecision)
            fullCompute = False

    #[4]: Result formatting & Saving
    smaResult = {'PRICESUM':    priceSum,
                 'SMA':         sma,
                 'fullCompute': fullCompute}
    smas[timestamp] = smaResult

    #[5]: Memory Optimization References
    return (2,        #nAnalysisToKeep
            nSamples) #nKlinesToKeep
#ANALYSIS GENERATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#LINEARIZATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def linearize(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_SMA': analysisResult['SMA']}
    return lRes


"""
def linearizeAnalysis_IVP(intervalID, analysisCode, analysisResult):
    nearBoundaries = analysisResult['volumePriceLevelProfile_NearBoundaries']
    lRes = {f'{intervalID}_{analysisCode}_NB{nbIndex}': nearBoundaries[nbIndex] for nbIndex in range (len(nearBoundaries))}
    return lRes

def linearizeAnalysis_SWING(intervalID, analysisCode, analysisResult):
    swings = analysisResult['SWINGS']
    if swings:
        ls_TS, ls_Price, ls_Type = swings[-1]
        lRes = {f'{intervalID}_{analysisCode}_LSTIMESTAMP': ls_TS,
                f'{intervalID}_{analysisCode}_LSPRICE':     ls_Price,
                f'{intervalID}_{analysisCode}_LSTYPE':      ls_Type}
    else:
        lRes = {f'{intervalID}_{analysisCode}_LSTIMESTAMP': None,
                f'{intervalID}_{analysisCode}_LSPRICE':     None,
                f'{intervalID}_{analysisCode}_LSTYPE':      None}
    return lRes

def linearizeAnalysis_NNA(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_NNA': analysisResult['NNA']}
    return lRes

def linearizeAnalysis_MMACD(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_MSDELTA':         analysisResult['MSDELTA'],
            f'{intervalID}_{analysisCode}_MSDELTAABSMA':    analysisResult['MSDELTA_ABSMA'],
            f'{intervalID}_{analysisCode}_MSDELTAABSMAREL': analysisResult['MSDELTA_ABSMAREL']}
    return lRes

def linearizeAnalysis_DMIxADX(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_DMIxADX':         analysisResult['DMIxADX'],
            f'{intervalID}_{analysisCode}_DMIxADXABSMA':    analysisResult['DMIxADX_ABSMA'],
            f'{intervalID}_{analysisCode}_DMIxADXABSMAREL': analysisResult['DMIxADX_ABSMAREL']}
    return lRes

def linearizeAnalysis_MFI(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_MFI':            analysisResult['MFI'],
            f'{intervalID}_{analysisCode}_MFIDEVABSMA':    analysisResult['MFI_DEVABSMA'],
            f'{intervalID}_{analysisCode}_MFIDEVABSMAREL': analysisResult['MFI_DEVABSMAREL']}
    return lRes

def linearizeAnalysis_TPD(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_TPD':         analysisResult['TPD'],
            f'{intervalID}_{analysisCode}_TPDABSMA':    analysisResult['TPD_ABSMA'],
            f'{intervalID}_{analysisCode}_TPDABSMAREL': analysisResult['TPD_ABSMAREL']}
    return lRes

def linearizeAnalysis_WOI(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_WOI':         analysisResult['WOI'],
            f'{intervalID}_{analysisCode}_WOIABSMA':    analysisResult['WOI_ABSMA'],
            f'{intervalID}_{analysisCode}_WOIABSMAREL': analysisResult['WOI_ABSMAREL']}
    return lRes

def linearizeAnalysis_NES(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_NES':         analysisResult['NES'],
            f'{intervalID}_{analysisCode}_NESABSMA':    analysisResult['NES_ABSMA'],
            f'{intervalID}_{analysisCode}_NESABSMAREL': analysisResult['NES_ABSMAREL']}
    return lRes
"""

#LINEARIZATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYZER FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_maximum_market_data_reference_length(cac_iID):
    #[1]: Master Check
    if not cac_iID['SMA_Master']:
        return 0
    
    #[2]: MMDRL
    mmdrl = 0
    for lIdx in range (NMAXLINES):
        #[2-1]: Line Active Check
        if not cac_iID.get(f'SMA_{lIdx}_LineActive', False): 
            continue

        #[2-2]: MMDRL Update
        mmdrl = max(mmdrl, 
                    cac_iID[f'SMA_{lIdx}_NSamples'])

    #[3]: Return MMDRL
    return mmdrl

"""
#---IVP
if cac_iID['IVP_Master']:
    nSamples = cac_iID['IVP_NSamples']
    mmdrl = max(mmdrl, nSamples)
#---MMACD
if cac_iID['MMACD_Master']:
    for lineIndex in range (constants.NLINES_MMACD):
        lineActive = cac_iID.get(f'MMACD_MA{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'MMACD_MA{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
#---DMIxADX
if cac_iID['DMIxADX_Master']:
    for lineIndex in range (constants.NLINES_DMIxADX):
        lineActive = cac_iID.get(f'DMIxADX_{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'DMIxADX_{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
#---MFI
if cac_iID['MFI_Master']:
    for lineIndex in range (constants.NLINES_MFI):
        lineActive = cac_iID.get(f'MFI_{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'MFI_{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
#---TPD
if cac_iID['TPD_Master']:
    for lineIndex in range (constants.NLINES_TPD):
        lineActive = cac_iID.get(f'TPD_{lineIndex}_LineActive', False)
        if not lineActive: continue
        viewLength = cac_iID[f'TPD_{lineIndex}_ViewLength']
        nSamples   = cac_iID[f'TPD_{lineIndex}_NSamples']
        nSamplesMA = cac_iID[f'TPD_{lineIndex}_NSamplesMA']
        mmdrl = max(mmdrl, viewLength+nSamples+nSamplesMA-1)
#---WOI
if cac_iID['WOI_Master']:
    for lineIndex in range (constants.NLINES_WOI):
        lineActive = cac_iID.get(f'WOI_{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'WOI_{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
#---NES
if cac_iID['NES_Master']:
    for lineIndex in range (constants.NLINES_NES):
        lineActive = cac_iID.get(f'NES_{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'NES_{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
"""
#ANALYZER FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#CHART DRAWER FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
CD_FULL_DRAW_SIGNALS        = 0b1
CD_VVR_PRECISIONCOMPENSATOR = None
CD_VVR_CENTERVALUE          = None
CD_VVR_DEFAULT              = None

"""
_FULLDRAWSIGNALS = {'IVP':          0b11,
                    'SWING':        0b1,
                    'NNA':          0b1,
                    'MMACD':        0b111,
                    'DMIxADX':      0b1,
                    'MFI':          0b1,
                    'TPD':          0b1,
                    'WOI':          0b1,
                    'NES':          0b1}
_VVR_PRECISIONCOMPENSATOR = {'NNA':         -2,
                             'MMACD':       -2,
                             'DMIxADX':     -2,
                             'MFI':         -2,
                             'TPD':         -2,
                             'WOI':         -2,
                             'NES':         -2
                            }
_VVR_CENTERVALUE = {'NNA':                           0,
                    'MMACD':                         0,
                    ('DMIxADX', 'DMIxADX'):          0,
                    ('DMIxADX', 'DMIxADX_ABSMA'):    0,
                    ('DMIxADX', 'DMIxADX_ABSMAREL'): 0,
                    ('MFI',     'MFI'):              0.5,
                    ('MFI',     'MFI_DEVABSMA'):     0,
                    ('MFI',     'MFI_DEVABSMAREL'):  0,
                    ('TPD',     'TPD'):              0,
                    ('TPD',     'TPD_ABSMA'):        0,
                    ('TPD',     'TPD_ABSMAREL'):     0,
                    ('WOI',     'WOI'):              0,
                    ('WOI',     'WOI_ABSMA'):        0,
                    ('WOI',     'WOI_ABSMAREL'):     0,
                    ('NES',     'NES'):              0,
                    ('NES',     'NES_ABSMA'):        0,
                    ('NES',     'NES_ABSMAREL'):     0
                    }
_VVR_DEFAULT = {'MMACD':                         (-1, 1),
                ('DMIxADX', 'DMIxADX'):          (-1, 1),
                ('DMIxADX', 'DMIxADX_ABSMA'):    ( 0, 1),
                ('DMIxADX', 'DMIxADX_ABSMAREL'): (-1, 1),
                ('MFI',     'MFI'):              ( 0, 1),
                ('MFI',     'MFI_DEVABSMA'):     ( 0, 1),
                ('MFI',     'MFI_DEVABSMAREL'):  (-1, 1),
                ('TPD',     'TPD'):              (-1, 1),
                ('TPD',     'TPD_ABSMA'):        ( 0, 1),
                ('TPD',     'TPD_ABSMAREL'):     (-1, 1),
                ('WOI',     'WOI'):              (-1, 1),
                ('WOI',     'WOI_ABSMA'):        ( 0, 1),
                ('WOI',     'WOI_ABSMAREL'):     (-1, 1),
                ('NES',     'NES'):              (-1, 1),
                ('NES',     'NES_ABSMA'):        ( 0, 1),
                ('NES',     'NES_ABSMAREL'):     (-1, 1)
               }
"""

def cd_get_initial_configuration():
    #[1]: Indicator Configuration
    oc = dict()

    #[2]: Configuration Setup
    oc['SMA_Master'] = False
    for lIdx in range (NMAXLINES):
        oc[f'SMA_{lIdx}_LineActive'] = False
        oc[f'SMA_{lIdx}_NSamples']   = 10*(lIdx+1)
        oc[f'SMA_{lIdx}_Width'] = 1
        oc[f'SMA_{lIdx}_ColorR%DARK'] =random.randint(64,255); oc[f'SMA_{lIdx}_ColorG%DARK'] =random.randint(64,255); oc[f'SMA_{lIdx}_ColorB%DARK'] =random.randint(64, 255); oc[f'SMA_{lIdx}_ColorA%DARK'] =255
        oc[f'SMA_{lIdx}_ColorR%LIGHT']=random.randint(64,255); oc[f'SMA_{lIdx}_ColorG%LIGHT']=random.randint(64,255); oc[f'SMA_{lIdx}_ColorB%LIGHT']=random.randint(64, 255); oc[f'SMA_{lIdx}_ColorA%LIGHT']=255
        oc[f'SMA_{lIdx}_Display'] = True

    #[3]: Configuration Return
    return oc

"""
#--- IVP Config
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
#--- SWING Config
oc['SWING_Master'] = False
for lineIndex in range (_NMAXLINES['SWING']):
    oc[f'SWING_{lineIndex}_LineActive'] = False
    oc[f'SWING_{lineIndex}_SwingRange'] = 0.005*(lineIndex+1)
    oc[f'SWING_{lineIndex}_Width'] = 1
    oc[f'SWING_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'SWING_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'SWING_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'SWING_{lineIndex}_ColorA%DARK'] =255
    oc[f'SWING_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'SWING_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'SWING_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'SWING_{lineIndex}_ColorA%LIGHT']=255
    oc[f'SWING_{lineIndex}_Display'] = True
#---NNA Config
oc['NNA_Master'] = False
for lineIndex in range (_NMAXLINES['NNA']):
    oc[f'NNA_{lineIndex}_LineActive'] = False
    oc[f'NNA_{lineIndex}_NeuralNetworkCode'] = None
    oc[f'NNA_{lineIndex}_Alpha']             = 0.50
    oc[f'NNA_{lineIndex}_Beta']              = 2
    oc[f'NNA_{lineIndex}_Width'] = 1
    oc[f'NNA_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'NNA_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'NNA_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'NNA_{lineIndex}_ColorA%DARK'] =255
    oc[f'NNA_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'NNA_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'NNA_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'NNA_{lineIndex}_ColorA%LIGHT']=255
    oc[f'NNA_{lineIndex}_Display'] = True
#---MMACD Config
oc['MMACD_Master'] = False
oc['MMACD_SignalNSamples']      = 10
oc['MMACD_MMACD_Display']       = True
oc['MMACD_SIGNAL_Display']      = True
oc['MMACD_HISTOGRAM_Display']   = True
oc['MMACD_HISTOGRAM_Type']      = 'MSDELTA'
oc['MMACD_MMACD_ColorR%DARK']   = random.randint(64,255); oc['MMACD_MMACD_ColorG%DARK']   = random.randint(64,255); oc['MMACD_MMACD_ColorB%DARK']   = random.randint(64,255); oc['MMACD_MMACD_ColorA%DARK']   = 255
oc['MMACD_MMACD_ColorR%LIGHT']  = random.randint(64,255); oc['MMACD_MMACD_ColorG%LIGHT']  = random.randint(64,255); oc['MMACD_MMACD_ColorB%LIGHT']  = random.randint(64,255); oc['MMACD_MMACD_ColorA%LIGHT']  = 255
oc['MMACD_SIGNAL_ColorR%DARK']  = random.randint(64,255); oc['MMACD_SIGNAL_ColorG%DARK']  = random.randint(64,255); oc['MMACD_SIGNAL_ColorB%DARK']  = random.randint(64,255); oc['MMACD_SIGNAL_ColorA%DARK']  = 255
oc['MMACD_SIGNAL_ColorR%LIGHT'] = random.randint(64,255); oc['MMACD_SIGNAL_ColorG%LIGHT'] = random.randint(64,255); oc['MMACD_SIGNAL_ColorB%LIGHT'] = random.randint(64,255); oc['MMACD_SIGNAL_ColorA%LIGHT'] = 255
oc['MMACD_HISTOGRAM+_ColorR%DARK']  = 100; oc['MMACD_HISTOGRAM+_ColorG%DARK']  = 255; oc['MMACD_HISTOGRAM+_ColorB%DARK']  = 180; oc['MMACD_HISTOGRAM+_ColorA%DARK']  = 255
oc['MMACD_HISTOGRAM+_ColorR%LIGHT'] =  80; oc['MMACD_HISTOGRAM+_ColorG%LIGHT'] = 200; oc['MMACD_HISTOGRAM+_ColorB%LIGHT'] = 150; oc['MMACD_HISTOGRAM+_ColorA%LIGHT'] = 255
oc['MMACD_HISTOGRAM-_ColorR%DARK']  = 255; oc['MMACD_HISTOGRAM-_ColorG%DARK']  = 100; oc['MMACD_HISTOGRAM-_ColorB%DARK']  = 100; oc['MMACD_HISTOGRAM-_ColorA%DARK']  = 255
oc['MMACD_HISTOGRAM-_ColorR%LIGHT'] = 240; oc['MMACD_HISTOGRAM-_ColorG%LIGHT'] =  80; oc['MMACD_HISTOGRAM-_ColorB%LIGHT'] =  80; oc['MMACD_HISTOGRAM-_ColorA%LIGHT'] = 255
for lineIndex in range (_NMAXLINES['MMACD']):
    oc[f'MMACD_MA{lineIndex}_LineActive'] = False
    oc[f'MMACD_MA{lineIndex}_NSamples']   = 20*(lineIndex+1)
#---DMIxADX Config
oc['DMIxADX_Master']      = False
oc['DMIxADX_DisplayType'] = 'DMIxADX'
for lineIndex in range (_NMAXLINES['DMIxADX']):
    oc[f'DMIxADX_{lineIndex}_LineActive'] = False
    oc[f'DMIxADX_{lineIndex}_NSamples']   = 10*(lineIndex+1)
    oc[f'DMIxADX_{lineIndex}_Width'] = 1
    oc[f'DMIxADX_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'DMIxADX_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'DMIxADX_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'DMIxADX_{lineIndex}_ColorA%DARK'] =255
    oc[f'DMIxADX_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'DMIxADX_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'DMIxADX_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'DMIxADX_{lineIndex}_ColorA%LIGHT']=255
    oc[f'DMIxADX_{lineIndex}_Display'] = True
#---MFI Config
oc['MFI_Master']      = False
oc['MFI_DisplayType'] = 'MFI'
for lineIndex in range (_NMAXLINES['MFI']):
    oc[f'MFI_{lineIndex}_LineActive'] = False
    oc[f'MFI_{lineIndex}_NSamples']   = 10*(lineIndex+1)
    oc[f'MFI_{lineIndex}_Width'] = 1
    oc[f'MFI_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'MFI_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'MFI_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'MFI_{lineIndex}_ColorA%DARK'] =255
    oc[f'MFI_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'MFI_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'MFI_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'MFI_{lineIndex}_ColorA%LIGHT']=255
    oc[f'MFI_{lineIndex}_Display'] = True
#---TPD Config
oc['TPD_Master']      = False
oc['TPD_DisplayType'] = 'TPD'
for lineIndex in range (_NMAXLINES['TPD']):
    oc[f'TPD_{lineIndex}_LineActive'] = False
    oc[f'TPD_{lineIndex}_ViewLength'] = 10 *(lineIndex+1)
    oc[f'TPD_{lineIndex}_NSamples']   = 100*(lineIndex+1)
    oc[f'TPD_{lineIndex}_NSamplesMA'] = 20 *(lineIndex+1)
    oc[f'TPD_{lineIndex}_Width'] = 1
    oc[f'TPD_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'TPD_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'TPD_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'TPD_{lineIndex}_ColorA%DARK'] =255
    oc[f'TPD_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'TPD_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'TPD_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'TPD_{lineIndex}_ColorA%LIGHT']=255
    oc[f'TPD_{lineIndex}_Display'] = True
#---WOI Config
oc['WOI_Master']      = False
oc['WOI_DisplayType'] = 'WOI'
for lineIndex in range (_NMAXLINES['WOI']):
    oc[f'WOI_{lineIndex}_LineActive'] = False
    oc[f'WOI_{lineIndex}_NSamples'] = 10*(lineIndex+1)
    oc[f'WOI_{lineIndex}_Width']    = 1
    oc[f'WOI_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'WOI_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'WOI_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'WOI_{lineIndex}_ColorA%DARK'] =255
    oc[f'WOI_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'WOI_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'WOI_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'WOI_{lineIndex}_ColorA%LIGHT']=255
    oc[f'WOI_{lineIndex}_Display'] = True
#---NES Config
oc['NES_Master']      = False
oc['NES_DisplayType'] = 'NES'
for lineIndex in range (_NMAXLINES['NES']):
    oc[f'NES_{lineIndex}_LineActive'] = False
    oc[f'NES_{lineIndex}_NSamples'] = 10*(lineIndex+1)
    oc[f'NES_{lineIndex}_Width']    = 1
    oc[f'NES_{lineIndex}_ColorR%DARK'] =random.randint(64,255); oc[f'NES_{lineIndex}_ColorG%DARK'] =random.randint(64,255); oc[f'NES_{lineIndex}_ColorB%DARK'] =random.randint(64, 255); oc[f'NES_{lineIndex}_ColorA%DARK'] =255
    oc[f'NES_{lineIndex}_ColorR%LIGHT']=random.randint(64,255); oc[f'NES_{lineIndex}_ColorG%LIGHT']=random.randint(64,255); oc[f'NES_{lineIndex}_ColorB%LIGHT']=random.randint(64, 255); oc[f'NES_{lineIndex}_ColorA%LIGHT']=255
    oc[f'NES_{lineIndex}_Display'] = True
"""

def cd_initialize_settings_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'INDICATORINDEX_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': 800, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INDEX'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORINTERVAL_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':  900, 'yPos': -300, 'width': 900, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORWIDTH_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1900, 'yPos': -300, 'width': 750, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:WIDTH'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORCOLOR_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2750, 'yPos': -300, 'width': 650, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORDISPLAY_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3500, 'yPos': -300, 'width': 500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAY'), 'fontSize': 90}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"INDICATOR_SMA{lIdx}",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 800, 'height': 250, 'style': 'styleB', 'text': f'SMA {lIdx}', 'fontSize': 80, 'name': f'SMA_LineActivationSwitch_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_SMA{lIdx}_INTERVALINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos':  900, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
        gList.append(({'NAME':               f"INDICATOR_SMA{lIdx}_WIDTHINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 1900, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 750, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
        gList.append(({'NAME':               f"INDICATOR_SMA{lIdx}_LINECOLOR",
                       'TYPE':               'LED_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2750, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 650, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'mode': True}))
        gList.append(({'NAME':               f"INDICATOR_SMA{lIdx}_DISPLAY",
                       'TYPE':               'switch_typeB',
                       'PAGEOBJECTFUNCTION': ['releaseFunction',],
                       'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': f'SMA_DisplaySwitch_{lIdx}'}))

    #[3]: Return GUIO Generation List
    return gList



def cd_initialize_settings_subpage_setup(subpage, fn_get_text_pack):
    subpage.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList  = {f"{lIdx}": {'text': f"SMA {lIdx}"} for lIdx in range (NMAXLINES)}, 
                                                                     displayTargets = 'all')



"""
#<IVP Settings>
if (True):
    ssp = self.settingsSubPages['IVP']
    ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_IVP'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width':                  1500, 'height': 250, 'style': 'styleA', 'name': 'IVP_LineSelectionBox', 'nDisplay': 9, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':                   950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':                   650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'IVP_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'IVP_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ivpLineTargets = {'VPLP':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLP')},
                        'VPLPB': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPB')}}
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = ivpLineTargets, displayTargets = 'all')
    ssp.addGUIO("INDICATOR_BLOCKTITLE_IVPDISPLAY", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_VPLP_DISPLAYTEXT",             generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPDISPLAY'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLP_DISPLAYSWITCH",           generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'IVP_DisplaySwitch_VPLP', 'statusUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_VPLP_COLORTEXT",               generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7200, 'width':  700, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLP_COLOR",                   generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3300, 'yPos': 7200, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATOR_VPLP_DISPLAYWIDTHTEXT",        generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYWIDTH'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLP_DISPLAYWIDTHSLIDER",      generals.slider_typeA,  {'groupOrder': 0, 'xPos': 1300, 'yPos': 6900, 'width': 2000, 'height': 150, 'style': 'styleA', 'name': 'IVP_DisplayWidthSlider_VPLP', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_VPLP_DISPLAYWIDTHVALUETEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3400, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLPB_DISPLAYTEXT",            generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPBDISPLAY'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLPB_DISPLAYSWITCH",          generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1900, 'yPos': 6500, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'IVP_DisplaySwitch_VPLPB', 'statusUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_VPLPB_COLORTEXT",              generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLPB_COLOR",                  generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3300, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATOR_VPLPB_DISPLAYREGIONTEXT",      generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6150, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYREGION'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLPB_DISPLAYREGIONSLIDER",    generals.slider_typeA,  {'groupOrder': 0, 'xPos': 1400, 'yPos': 6200, 'width': 1800, 'height': 150, 'style': 'styleA', 'name': 'IVP_VPLPBDisplayRegion', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT", generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 6150, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_BLOCKTITLE_IVPPARAMS", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 5800, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPPARAMS'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_INTERVAL_DISPLAYTEXT",    generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 5450, 'width': 1900, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_INTERVAL_INPUTTEXT",      generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 5450, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'IVP_Interval', 'textUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_GAMMAFACTOR_DISPLAYTEXT", generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 5100, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPGAMMAFACTOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_GAMMAFACTOR_SLIDER",      generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 5150, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_GammaFactor', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_GAMMAFACTOR_VALUETEXT",   generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 5100, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DELTAFACTOR_DISPLAYTEXT", generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 4750, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPDELTAFACTOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DELTAFACTOR_SLIDER",      generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 4800, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_DeltaFactor', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_DELTAFACTOR_VALUETEXT",   generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 4750, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    
    ssp.addGUIO("INDICATOR_PROMINENCE_DISPLAYTEXT",  generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 4400, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPPROMINENCE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_PROMINENCE_SLIDER",       generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 4450, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_Prominence', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_PROMINENCE_VALUETEXT",    generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 4400, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISTANCE_DISPLAYTEXT",    generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 4050, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPDISTANCE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISTANCE_SLIDER",         generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 4100, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_Distance', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_DISTANCE_VALUETEXT",      generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 4050, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_HEIGHT_DISPLAYTEXT",      generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 3700, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPHEIGHT'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_HEIGHT_SLIDER",           generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 3750, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_Height', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_HEIGHT_VALUETEXT",        generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 3700, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': 3350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'IVP_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
#<SWING Settings>
if (True):
    ssp = self.settingsSubPages['SWING']
    ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_SWING'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'SWING_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'SWING_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'SWING_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),      'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORSWINGRANGE_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7550, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SWINGRANGE'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2300, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),      'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2900, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),      'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),    'fontSize': 90, 'anchor': 'SW'})
    swingList = dict()
    for lineIndex in range (_NMAXLINES['SWING']):
        ssp.addGUIO(f"INDICATOR_SWING{lineIndex}",                 generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'SWING_LineActivationSwitch_{lineIndex}', 'text': f'SWING {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7200-350*lineIndex, 'width': 1100, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'SWING_SwingRangeTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_WIDTHINPUT",      generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2300, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'SWING_WidthTextInputBox_{lineIndex}', 'text': "", 'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_LINECOLOR",       generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2900, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_DISPLAY",         generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'SWING_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
        swingList[f"{lineIndex}"] = {'text': f"SWING {lineIndex}"}
    yPosPoint0 = 7200-350*(_NMAXLINES['SWING']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'SWING_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = swingList, displayTargets = 'all')
#<NNA Settings>
if (True):
    ssp = self.settingsSubPages['NNA']
    ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_NNA'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'NNA_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'NNA_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'NNA_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),             'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORNNCODE_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  700, 'yPos': 7550, 'width':  900, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NEURALNETWORKCODE'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORALPHA_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1700, 'yPos': 7550, 'width':  400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:ALPHA'),             'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORBETA_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2200, 'yPos': 7550, 'width':  300, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BETA'),              'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORSIZE_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2600, 'yPos': 7550, 'width':  300, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SIZE'),              'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3000, 'yPos': 7550, 'width':  400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),             'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),           'fontSize': 90, 'anchor': 'SW'})
    nnaList = dict()
    for lineIndex in range (_NMAXLINES['NNA']):
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}",             generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleB', 'name': f'NNA_LineActivationSwitch_{lineIndex}', 'text': f'NNA {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_NNCODEINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  700, 'yPos': 7200-350*lineIndex, 'width':  900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_NNCodeTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_ALPHAINPUT",  generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1700, 'yPos': 7200-350*lineIndex, 'width':  400, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_AlphaTextInputBox_{lineIndex}',  'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_BETAINPUT",   generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2200, 'yPos': 7200-350*lineIndex, 'width':  300, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_BetaTextInputBox_{lineIndex}',   'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_WIDTHINPUT",  generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2600, 'yPos': 7200-350*lineIndex, 'width':  300, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_WidthTextInputBox_{lineIndex}',  'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_LINECOLOR",   generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3000, 'yPos': 7200-350*lineIndex, 'width':  400, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_DISPLAY",     generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'NNA_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
        nnaList[f"{lineIndex}"] = {'text': f"NNA {lineIndex}"}
    yPosPoint0 = 7200-350*(_NMAXLINES['NNA']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'NNA_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = nnaList, displayTargets = 'all')
#<MMACD Settings>
if (True):
    ssp = self.settingsSubPages['MMACD']
    ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_MMACD'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':                   550, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width':                  1500, 'height': 250, 'style': 'styleA', 'name': 'MMACD_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':                   950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':                   650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'MMACD_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'MMACD_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    mmacdLineTargets = {'MMACD':      {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACD')},
                        'SIGNAL':     {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNAL')},
                        'HISTOGRAM+': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM+')},
                        'HISTOGRAM-': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM-')}}
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = mmacdLineTargets, displayTargets = 'all')
    ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",        generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_MMACD_DISPLAYTEXT",         generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACDDISPLAY'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_MMACD_DISPLAYSWITCH",       generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 7200, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACD_DisplaySwitch_MMACD', 'statusUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_MMACD_COLORTEXT",           generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 7200, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_MMACD_COLOR",               generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 7200, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATOR_SIGNAL_DISPLAYTEXT",        generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALDISPLAY'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_SIGNAL_DISPLAYSWITCH",      generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 6850, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACD_DisplaySwitch_SIGNAL', 'statusUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_SIGNAL_COLORTEXT",          generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 6850, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_SIGNAL_COLOR",              generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 6850, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATOR_HISTOGRAM_DISPLAYTEXT",     generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAMDISPLAY'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_HISTOGRAM_DISPLAYSWITCH",   generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACD_DisplaySwitch_HISTOGRAM', 'statusUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_HISTOGRAM_COLORTEXT",       generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 6500, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_HISTOGRAM+_COLOR",          generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATOR_HISTOGRAM-_COLOR",          generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATOR_HISTOGRAMTYPE_DISPLAYTEXT", generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 6150, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAMTYPE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_HISTOGRAMTYPE_SELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1600, 'yPos': 6150, 'width':                  2400, 'height': 250, 'style': 'styleA', 'name': 'MMACD_HistrogramTypeSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    histogramTypes = {'MSDELTA':          {'text': 'MSDELTA'},
                        'MSDELTA_ABSMA':    {'text': 'MSDELTA_ABSMA'},
                        'MSDELTA_ABSMAREL': {'text': 'MSDELTA_ABSMAREL'}}
    ssp.GUIOs["INDICATOR_HISTOGRAMTYPE_SELECTION"].setSelectionList(selectionList = histogramTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATOR_BLOCKTITLE_MMACDSETTINGS",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 5800, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSETTINGS'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_SIGNALINTERVALTEXT",         generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 5450, 'width':                  3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALINTERVAL'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_SIGNALINTERVALTEXTINPUT",    generals.textInputBox_typeA,           {'groupOrder': 0, 'xPos': 3100, 'yPos': 5450, 'width':                   900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACD_SignalIntervalTextInputBox', 'textUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE1",          generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE1",       generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE2",          generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2050, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE2",       generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3150, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
    for lineIndex in range (_NMAXLINES['MMACD']):
        rowNumber = math.ceil((lineIndex+1)/2)
        if (lineIndex%2 == 0): coordX = 0
        else:                  coordX = 2050
        ssp.addGUIO(f"INDICATOR_MMACDMA{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos': coordX,      'yPos': 5100-rowNumber*350, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'MMACD_LineActivationSwitch_{lineIndex}', 'text': f'MA {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': coordX+1100, 'yPos': 5100-rowNumber*350, 'width':  850, 'height': 250, 'style': 'styleA', 'name': f'MMACD_IntervalTextInputBox_{lineIndex}', 'text': "",                'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
    yPosPoint0 = 5100-math.ceil(_NMAXLINES['MMACD']/2)*350
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'MMACD_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
#<DMIxADX Settings>
if (True):
    ssp = self.settingsSubPages['DMIxADX']
    ssp.addGUIO("SUBPAGETITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_DMIxADX'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",        generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'DMIxADX_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'DMIxADX_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'DMIxADX_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DMIXADXDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_DISPLAYTEXT", generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTYPE'),    'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_SELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1600, 'yPos': 7200, 'width':                  2400, 'height': 250, 'style': 'styleA', 'name': 'DMIxADX_DisplayTypeSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    displayTypes = {'DMIxADX':          {'text': 'DMIxADX'},
                    'DMIxADX_ABSMA':    {'text': 'DMIxADX_ABSMA'},
                    'DMIxADX_ABSMAREL': {'text': 'DMIxADX_ABSMAREL'}}
    ssp.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].setSelectionList(selectionList = displayTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1300, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2000, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 6850, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    dmixadxList = dict()
    for lineIndex in range (_NMAXLINES['DMIxADX']):
        ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*lineIndex, 'width': 1200, 'height': 250, 'style': 'styleB', 'name': f'DMIxADX_LineActivationSwitch_{lineIndex}', 'text': f'DMIxADX {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'DMIxADX_IntervalTextInputBox_{lineIndex}', 'text': "",                     'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'DMIxADX_WidthTextInputBox_{lineIndex}',    'text': "",                     'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 6500-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'DMIxADX_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
        dmixadxList[f"{lineIndex}"] = {'text': f"DMIxADX {lineIndex}"}
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = dmixadxList, displayTargets = 'all')
    yPosPoint0 = 6500-350*(_NMAXLINES['DMIxADX']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'DMIxADX_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
#<MFI Settings>
if (True):
    ssp = self.settingsSubPages['MFI']
    ssp.addGUIO("SUBPAGETITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_MFI'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",        generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'MFI_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'MFI_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'MFI_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MFIDISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_DISPLAYTEXT", generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTYPE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_SELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1600, 'yPos': 7200, 'width':                  2400, 'height': 250, 'style': 'styleA', 'name': 'MFI_DisplayTypeSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    displayTypes = {'MFI':             {'text': 'MFI'},
                    'MFI_DEVABSMA':    {'text': 'MFI_DEVABSMA'},
                    'MFI_DEVABSMAREL': {'text': 'MFI_DEVABSMAREL'}}
    ssp.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].setSelectionList(selectionList = displayTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6850, 'width':  800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2000, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 6850, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    mfiList = dict()
    for lineIndex in range (_NMAXLINES['MFI']):
        ssp.addGUIO(f"INDICATOR_MFI{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'MFI_LineActivationSwitch_{lineIndex}', 'text': f'MFI {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6500-350*lineIndex, 'width':  800, 'height': 250, 'style': 'styleA', 'name': f'MFI_IntervalTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'MFI_WidthTextInputBox_{lineIndex}',    'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 6500-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'MFI_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
        mfiList[f"{lineIndex}"] = {'text': f"MFI {lineIndex}"}
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = mfiList, displayTargets = 'all')
    yPosPoint0 = 6500-350*(_NMAXLINES['MFI']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'MFI_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
#<TPD Settings>
if (True):
    ssp = self.settingsSubPages['TPD']
    ssp.addGUIO("SUBPAGETITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_TPD'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",        generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'TPD_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'TPD_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'TPD_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TPDDISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_DISPLAYTEXT", generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTYPE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_SELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1600, 'yPos': 7200, 'width':                  2400, 'height': 250, 'style': 'styleA', 'name': 'TPD_DisplayTypeSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    displayTypes = {'TPD':          {'text': 'TPD'},
                    'TPD_ABSMA':    {'text': 'TPD_ABSMA'},
                    'TPD_ABSMAREL': {'text': 'TPD_ABSMAREL'}}
    ssp.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].setSelectionList(selectionList = displayTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),         'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORVIEWLENGTH_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  700, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VIEWLENGTH'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1300, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVALSHORT'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORMAINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MAINTERVAL'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2500, 'yPos': 6850, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),         'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3000, 'yPos': 6850, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),         'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),       'fontSize': 90, 'anchor': 'SW'})
    tpdList = dict()
    for lineIndex in range (_NMAXLINES['TPD']):
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}",                 generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleB', 'name': f'TPD_LineActivationSwitch_{lineIndex}',   'text': f'TPD {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  700, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'TPD_ViewLengthTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_INTERVALINPUT",   generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'TPD_IntervalTextInputBox_{lineIndex}',   'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'TPD_MAIntervalTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_WIDTHINPUT",      generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 6500-350*lineIndex, 'width': 400, 'height': 250, 'style': 'styleA', 'name': f'TPD_WidthTextInputBox_{lineIndex}',      'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_LINECOLOR",       generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3000, 'yPos': 6500-350*lineIndex, 'width': 400, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_DISPLAY",         generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'TPD_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
        tpdList[f"{lineIndex}"] = {'text': f"TPD {lineIndex}"}
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = tpdList, displayTargets = 'all')
    yPosPoint0 = 6500-350*(_NMAXLINES['TPD']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'TPD_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
#<WOI Settings>
if (True):
    ssp = self.settingsSubPages['WOI']
    ssp.addGUIO("SUBPAGETITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_WOI'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",        generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'WOI_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'WOI_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'WOI_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WOIDISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_DISPLAYTEXT", generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTYPE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_SELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1600, 'yPos': 7200, 'width':                  2400, 'height': 250, 'style': 'styleA', 'name': 'WOI_DisplayTypeSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    displayTypes = {'WOI':          {'text': 'WOI'},
                    'WOI_ABSMA':    {'text': 'WOI_ABSMA'},
                    'WOI_ABSMAREL': {'text': 'WOI_ABSMAREL'}}
    ssp.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].setSelectionList(selectionList = displayTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6850, 'width':  900, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2100, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2800, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    for lineIndex in range (_NMAXLINES['WOI']):
        ssp.addGUIO(f"INDICATOR_WOI{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'WOI_LineActivationSwitch_{lineIndex}', 'text': f'WOI {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_WOI{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6500-350*lineIndex, 'width':  900, 'height': 250, 'style': 'styleA', 'name': f'WOI_IntervalTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_WOI{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'WOI_WidthTextInputBox_{lineIndex}',    'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_WOI{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2800, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_WOI{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'WOI_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList  = {f"{lIdx}": {'text': f"WOI {lIdx}"} for lIdx in range (_NMAXLINES['WOI'])},
                                                                    displayTargets = 'all')
    yPosPoint0 = 6500-350*(_NMAXLINES['WOI']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'WOI_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
#<NES Settings>
if (True):
    ssp = self.settingsSubPages['NES']
    ssp.addGUIO("SUBPAGETITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_NES'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",        generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'NES_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'NES_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'NES_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NESDISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_DISPLAYTEXT", generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTYPE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_SELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1600, 'yPos': 7200, 'width':                  2400, 'height': 250, 'style': 'styleA', 'name': 'NES_DisplayTypeSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    displayTypes = {'NES':          {'text': 'NES'},
                    'NES_ABSMA':    {'text': 'NES_ABSMA'},
                    'NES_ABSMAREL': {'text': 'NES_ABSMAREL'}}
    ssp.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].setSelectionList(selectionList = displayTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6850, 'width':  900, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2100, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2800, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    for lineIndex in range (_NMAXLINES['NES']):
        ssp.addGUIO(f"INDICATOR_NES{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'NES_LineActivationSwitch_{lineIndex}', 'text': f'NES {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NES{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6500-350*lineIndex, 'width':  900, 'height': 250, 'style': 'styleA', 'name': f'NES_IntervalTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NES{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'NES_WidthTextInputBox_{lineIndex}',    'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NES{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2800, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_NES{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'NES_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList  = {f"{lIdx}": {'text': f"NES {lIdx}"} for lIdx in range (_NMAXLINES['NES'])},
                                                                    displayTargets = 'all')
    yPosPoint0 = 6500-350*(_NMAXLINES['NES']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'NES_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
"""

def cd_match_guios_to_config(mainPage, subPage, current_GUI_Theme, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    cgt        = current_GUI_Theme
    oc         = object_configuration

    #[2]: GUIOs Update
    guios_MAIN["MAININDICATOR_SMA"].setStatus(oc['SMA_Master'], callStatusUpdateFunction = False)
    for lIdx in range (NMAXLINES):
        lActive  = oc[f'SMA_{lIdx}_LineActive']
        nSamples = oc[f'SMA_{lIdx}_NSamples']
        width    = oc[f'SMA_{lIdx}_Width']
        color    = (oc[f'SMA_{lIdx}_ColorR%{cgt}'],
                    oc[f'SMA_{lIdx}_ColorG%{cgt}'],
                    oc[f'SMA_{lIdx}_ColorB%{cgt}'],
                    oc[f'SMA_{lIdx}_ColorA%{cgt}'])
        display  = oc[f'SMA_{lIdx}_Display']
        guios_THIS[f"INDICATOR_SMA{lIdx}"].setStatus(status = lActive, callStatusUpdateFunction = False)
        guios_THIS[f"INDICATOR_SMA{lIdx}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_THIS[f"INDICATOR_SMA{lIdx}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_THIS[f"INDICATOR_SMA{lIdx}_LINECOLOR"].updateColor(*color)
        guios_THIS[f"INDICATOR_SMA{lIdx}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
    guios_THIS["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_THIS["APPLYNEWSETTINGS"].deactivate()


"""
guios_IVP      = ssps['IVP'].GUIOs
guios_SWING    = ssps['SWING'].GUIOs
guios_NNA      = ssps['NNA'].GUIOs
guios_MMACD    = ssps['MMACD'].GUIOs
guios_DMIxADX  = ssps['DMIxADX'].GUIOs
guios_MFI      = ssps['MFI'].GUIOs
guios_TPD      = ssps['TPD'].GUIOs
guios_WOI      = ssps['WOI'].GUIOs
guios_NES      = ssps['NES'].GUIOs
#<IVP>
if (True):
    guios_MAIN["MAININDICATOR_IVP"].setStatus(oc['IVP_Master'],                 callStatusUpdateFunction = False)
    guios_IVP["INDICATOR_VPLP_DISPLAYSWITCH"].setStatus(oc['IVP_VPLP_Display'], callStatusUpdateFunction = False)
    guios_IVP["INDICATOR_VPLP_COLOR"].updateColor(oc[f'IVP_VPLP_ColorR%{cgt}'], 
                                                    oc[f'IVP_VPLP_ColorG%{cgt}'], 
                                                    oc[f'IVP_VPLP_ColorB%{cgt}'], 
                                                    oc[f'IVP_VPLP_ColorA%{cgt}'])
    guios_IVP["INDICATOR_VPLP_DISPLAYWIDTHSLIDER"].setSliderValue(newValue = (oc['IVP_VPLP_DisplayWidth']-0.1)/0.9*100, callValueUpdateFunction = False)
    guios_IVP["INDICATOR_VPLP_DISPLAYWIDTHVALUETEXT"].updateText(str(oc['IVP_VPLP_DisplayWidth']))
    guios_IVP["INDICATOR_VPLPB_DISPLAYSWITCH"].setStatus(oc['IVP_VPLPB_Display'], callStatusUpdateFunction = False)
    guios_IVP["INDICATOR_VPLPB_COLOR"].updateColor(oc[f'IVP_VPLPB_ColorR%{cgt}'], 
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
    guios_IVP["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].setSliderValue(newValue = (vplpb_dRegion-0.050)*(100/0.950), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT"].updateText(f"{vplpb_dRegion*100:.1f} %")
    guios_IVP["INDICATOR_INTERVAL_INPUTTEXT"].updateText(text = f"{nSamples}")
    guios_IVP["INDICATOR_GAMMAFACTOR_SLIDER"].setSliderValue(newValue = (gammaFactor-0.005)*(100/0.095), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(text = f"{gammaFactor*100:.1f} %")
    guios_IVP["INDICATOR_DELTAFACTOR_SLIDER"].setSliderValue(newValue = (deltaFactor-0.1)*(100/9.9), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(text = f"{int(deltaFactor*100)} %")

    guios_IVP["INDICATOR_PROMINENCE_SLIDER"].setSliderValue(newValue = (prominence - 0.01) * (100 / 0.99), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_PROMINENCE_VALUETEXT"].updateText(text = f"{int(prominence * 100)} %")
    guios_IVP["INDICATOR_DISTANCE_SLIDER"].setSliderValue(newValue = (distance - 1) * (100 / 99), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_DISTANCE_VALUETEXT"].updateText(text = f"{int(distance)}") 
    guios_IVP["INDICATOR_HEIGHT_SLIDER"].setSliderValue(newValue = height * 100.0, callValueUpdateFunction = False)
    guios_IVP["INDICATOR_HEIGHT_VALUETEXT"].updateText(text = f"{int(height * 100)} %")


    guios_IVP["INDICATORCOLOR_TARGETSELECTION"].setSelected('VPLP')
    guios_IVP["APPLYNEWSETTINGS"].deactivate()
#<SWING>
if (True):
    guios_MAIN["MAININDICATOR_SWING"].setStatus(oc['SWING_Master'], callStatusUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['SWING']):
        lineActive = oc[f'SWING_{lineIndex}_LineActive']
        swingRange = oc[f'SWING_{lineIndex}_SwingRange']
        width      = oc[f'SWING_{lineIndex}_Width']
        color      = (oc[f'SWING_{lineIndex}_ColorR%{cgt}'], 
                        oc[f'SWING_{lineIndex}_ColorG%{cgt}'], 
                        oc[f'SWING_{lineIndex}_ColorB%{cgt}'], 
                        oc[f'SWING_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'SWING_{lineIndex}_Display']
        guios_SWING[f"INDICATOR_SWING{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_SWING[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].updateText(text = f"{swingRange:.4f}")
        guios_SWING[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_SWING[f"INDICATOR_SWING{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_SWING["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_SWING["APPLYNEWSETTINGS"].deactivate()
#<NNA>
if (True):
    guios_MAIN["SUBINDICATOR_NNA"].setStatus(oc['NNA_Master'], callStatusUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['NNA']):
        lineActive = oc[f'NNA_{lineIndex}_LineActive']
        nnCode     = oc[f'NNA_{lineIndex}_NeuralNetworkCode']
        alpha      = oc[f'NNA_{lineIndex}_Alpha']
        beta       = oc[f'NNA_{lineIndex}_Beta']
        width      = oc[f'NNA_{lineIndex}_Width']
        color      = (oc[f'NNA_{lineIndex}_ColorR%{cgt}'], 
                        oc[f'NNA_{lineIndex}_ColorG%{cgt}'], 
                        oc[f'NNA_{lineIndex}_ColorB%{cgt}'], 
                        oc[f'NNA_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'NNA_{lineIndex}_Display']
        guios_NNA[f"INDICATOR_NNA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        nnCode_str = "" if nnCode is None else f"{nnCode}"
        guios_NNA[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].updateText(text = nnCode_str)
        guios_NNA[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].updateText(text = f"{alpha:.2f}")
        guios_NNA[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].updateText(text  = f"{beta}")
        guios_NNA[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_NNA[f"INDICATOR_NNA{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_NNA["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_NNA["APPLYNEWSETTINGS"].deactivate()
#<MMACD>
if (True):
    guios_MAIN["SUBINDICATOR_MMACD"].setStatus(oc['MMACD_Master'], callStatusUpdateFunction = False)
    guios_MMACD["INDICATOR_MMACD_DISPLAYSWITCH"].setStatus(oc['MMACD_MMACD_Display'], callStatusUpdateFunction = False)
    guios_MMACD["INDICATOR_SIGNAL_DISPLAYSWITCH"].setStatus(oc['MMACD_SIGNAL_Display'], callStatusUpdateFunction = False)
    guios_MMACD["INDICATOR_HISTOGRAM_DISPLAYSWITCH"].setStatus(oc['MMACD_HISTOGRAM_Display'], callStatusUpdateFunction = False)
    guios_MMACD["INDICATOR_MMACD_COLOR"].updateColor(oc[f'MMACD_MMACD_ColorR%{cgt}'], 
                                                            oc[f'MMACD_MMACD_ColorG%{cgt}'], 
                                                            oc[f'MMACD_MMACD_ColorB%{cgt}'], 
                                                            oc[f'MMACD_MMACD_ColorA%{cgt}'])
    guios_MMACD["INDICATOR_SIGNAL_COLOR"].updateColor(oc[f'MMACD_SIGNAL_ColorR%{cgt}'], 
                                                            oc[f'MMACD_SIGNAL_ColorG%{cgt}'], 
                                                            oc[f'MMACD_SIGNAL_ColorB%{cgt}'], 
                                                            oc[f'MMACD_SIGNAL_ColorA%{cgt}'])
    guios_MMACD["INDICATOR_HISTOGRAM+_COLOR"].updateColor(oc[f'MMACD_HISTOGRAM+_ColorR%{cgt}'], 
                                                                oc[f'MMACD_HISTOGRAM+_ColorG%{cgt}'], 
                                                                oc[f'MMACD_HISTOGRAM+_ColorB%{cgt}'], 
                                                                oc[f'MMACD_HISTOGRAM+_ColorA%{cgt}'])
    guios_MMACD["INDICATOR_HISTOGRAM-_COLOR"].updateColor(oc[f'MMACD_HISTOGRAM-_ColorR%{cgt}'], 
                                                                oc[f'MMACD_HISTOGRAM-_ColorG%{cgt}'], 
                                                                oc[f'MMACD_HISTOGRAM-_ColorB%{cgt}'], 
                                                                oc[f'MMACD_HISTOGRAM-_ColorA%{cgt}'])
    guios_MMACD["INDICATOR_HISTOGRAMTYPE_SELECTION"].setSelected(itemKey = oc['MMACD_HISTOGRAM_Type'], callSelectionUpdateFunction = False)
    signalNSamples = oc['MMACD_SignalNSamples']
    guios_MMACD["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(text = f"{signalNSamples}")
    for lineIndex in range (_NMAXLINES['MMACD']):
        lineActive = oc[f'MMACD_MA{lineIndex}_LineActive']
        nSamples   = oc[f'MMACD_MA{lineIndex}_NSamples']
        guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
    guios_MMACD["INDICATORCOLOR_TARGETSELECTION"].setSelected('MMACD')
    guios_MMACD["APPLYNEWSETTINGS"].deactivate()
#<DMIxADX>
if (True):
    guios_MAIN["SUBINDICATOR_DMIxADX"].setStatus(oc['DMIxADX_Master'], callStatusUpdateFunction = False)
    guios_DMIxADX["INDICATOR_DISPLAYTYPE_SELECTION"].setSelected(itemKey = oc['DMIxADX_DisplayType'], callSelectionUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['DMIxADX']):
        lineActive = oc[f'DMIxADX_{lineIndex}_LineActive']
        nSamples   = oc[f'DMIxADX_{lineIndex}_NSamples']
        width      = oc[f'DMIxADX_{lineIndex}_Width']
        color      = (oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'],
                        oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'],
                        oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'],
                        oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'DMIxADX_{lineIndex}_Display']
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_DMIxADX["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_DMIxADX["APPLYNEWSETTINGS"].deactivate()
#<MFI>
if (True):
    guios_MAIN["SUBINDICATOR_MFI"].setStatus(oc['MFI_Master'], callStatusUpdateFunction = False)
    guios_MFI["INDICATOR_DISPLAYTYPE_SELECTION"].setSelected(itemKey = oc['MFI_DisplayType'], callSelectionUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['MFI']):
        lineActive = oc[f'MFI_{lineIndex}_LineActive']
        nSamples   = oc[f'MFI_{lineIndex}_NSamples']
        width      = oc[f'MFI_{lineIndex}_Width']
        color      = (oc[f'MFI_{lineIndex}_ColorR%{cgt}'],
                        oc[f'MFI_{lineIndex}_ColorG%{cgt}'],
                        oc[f'MFI_{lineIndex}_ColorB%{cgt}'],
                        oc[f'MFI_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'MFI_{lineIndex}_Display']
        guios_MFI[f"INDICATOR_MFI{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_MFI[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_MFI[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_MFI[f"INDICATOR_MFI{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_MFI["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_MFI["APPLYNEWSETTINGS"].deactivate()
    #<MFI>
#<TPD>
if (True):
    guios_MAIN["SUBINDICATOR_TPD"].setStatus(oc['TPD_Master'], callStatusUpdateFunction = False)
    guios_TPD["INDICATOR_DISPLAYTYPE_SELECTION"].setSelected(itemKey = oc['TPD_DisplayType'], callSelectionUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['TPD']):
        lineActive = oc[f'TPD_{lineIndex}_LineActive']
        viewLength = oc[f'TPD_{lineIndex}_ViewLength']
        nSamples   = oc[f'TPD_{lineIndex}_NSamples']
        nSamplesMA = oc[f'TPD_{lineIndex}_NSamplesMA']
        width      = oc[f'TPD_{lineIndex}_Width']
        color      = (oc[f'TPD_{lineIndex}_ColorR%{cgt}'],
                        oc[f'TPD_{lineIndex}_ColorG%{cgt}'],
                        oc[f'TPD_{lineIndex}_ColorB%{cgt}'],
                        oc[f'TPD_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'TPD_{lineIndex}_Display']
        guios_TPD[f"INDICATOR_TPD{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_TPD[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].updateText(text = f"{viewLength}")
        guios_TPD[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].updateText(text   = f"{nSamples}")
        guios_TPD[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].updateText(text = f"{nSamplesMA}")
        guios_TPD[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_TPD[f"INDICATOR_TPD{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_TPD["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_TPD["APPLYNEWSETTINGS"].deactivate()
#<WOI>
if (True):
    guios_MAIN["SUBINDICATOR_WOI"].setStatus(oc['WOI_Master'], callStatusUpdateFunction = False)
    guios_WOI["INDICATOR_DISPLAYTYPE_SELECTION"].setSelected(itemKey = oc['WOI_DisplayType'], callSelectionUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['WOI']):
        lineActive = oc[f'WOI_{lineIndex}_LineActive']
        nSamples   = oc[f'WOI_{lineIndex}_NSamples']
        width      = oc[f'WOI_{lineIndex}_Width']
        color      = (oc[f'WOI_{lineIndex}_ColorR%{cgt}'],
                        oc[f'WOI_{lineIndex}_ColorG%{cgt}'],
                        oc[f'WOI_{lineIndex}_ColorB%{cgt}'],
                        oc[f'WOI_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'WOI_{lineIndex}_Display']
        guios_WOI[f"INDICATOR_WOI{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_WOI[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].updateText(text    = f"{width}")
        guios_WOI[f"INDICATOR_WOI{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_WOI["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_WOI["APPLYNEWSETTINGS"].deactivate()
#<NES>
if (True):
    guios_MAIN["SUBINDICATOR_NES"].setStatus(oc['NES_Master'], callStatusUpdateFunction = False)
    guios_NES["INDICATOR_DISPLAYTYPE_SELECTION"].setSelected(itemKey = oc['NES_DisplayType'], callSelectionUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['NES']):
        lineActive = oc[f'NES_{lineIndex}_LineActive']
        nSamples   = oc[f'NES_{lineIndex}_NSamples']
        width      = oc[f'NES_{lineIndex}_Width']
        color      = (oc[f'NES_{lineIndex}_ColorR%{cgt}'],
                        oc[f'NES_{lineIndex}_ColorG%{cgt}'],
                        oc[f'NES_{lineIndex}_ColorB%{cgt}'],
                        oc[f'NES_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'NES_{lineIndex}_Display']
        guios_NES[f"INDICATOR_NES{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_NES[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].updateText(text    = f"{width}")
        guios_NES[f"INDICATOR_NES{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_NES["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_NES["APPLYNEWSETTINGS"].deactivate()

"""

def cd_load_analysis_configuration(mainPage, subPage, analysis_configuration, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    ac = analysis_configuration
    oc = object_configuration

    #[2]: GUIOs Update
    if ac is not None and ac['SMA_Master']:
        guios_MAIN["MAININDICATOR_SMA"].activate()
        guios_MAIN["MAININDICATOR_SMA"].setStatus(status = oc['SMA_Master'], callStatusUpdateFunction = False)
        guios_MAIN["MAININDICATORSETUP_SMA"].activate()
        for lineIndex in range (NMAXLINES['SMA']):
            if ac[f'SMA_{lineIndex}_LineActive']:
                nSamples = ac[f'SMA_{lineIndex}_NSamples']
                width    = oc[f'SMA_{lineIndex}_Width']
                display  = oc[f'SMA_{lineIndex}_Display']
                guios_THIS[f"INDICATOR_SMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                guios_THIS[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].activate()
                guios_THIS[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                guios_THIS[f"INDICATOR_SMA{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_SMA{lineIndex}_DISPLAY"].activate()
            else:
                guios_THIS[f"INDICATOR_SMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].deactivate()
                guios_THIS[f"INDICATOR_SMA{lineIndex}_DISPLAY"].deactivate()
                guios_THIS[f"INDICATOR_SMA{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
    else:
        guios_MAIN["MAININDICATOR_SMA"].setStatus(status = False, callStatusUpdateFunction = False)
        guios_MAIN["MAININDICATOR_SMA"].deactivate()
        guios_MAIN["MAININDICATORSETUP_SMA"].deactivate()



"""
guios_IVP     = self.settingsSubPages['IVP'].GUIOs
guios_SWING   = self.settingsSubPages['SWING'].GUIOs
guios_NNA     = self.settingsSubPages['NNA'].GUIOs
guios_MMACD   = self.settingsSubPages['MMACD'].GUIOs
guios_DMIxADX = self.settingsSubPages['DMIxADX'].GUIOs
guios_MFI     = self.settingsSubPages['MFI'].GUIOs
guios_TPD     = self.settingsSubPages['TPD'].GUIOs
guios_WOI     = self.settingsSubPages['WOI'].GUIOs
guios_NES     = self.settingsSubPages['NES'].GUIOs

#IVP
if cac is not None and cac['IVP_Master']:
    guios_MAIN["MAININDICATOR_IVP"].activate()
    guios_MAIN["MAININDICATOR_IVP"].setStatus(status = oc['IVP_Master'], callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATORSETUP_IVP"].activate()
    guios_IVP["INDICATOR_INTERVAL_INPUTTEXT"].updateText(text = f"{cac['IVP_NSamples']}")
    guios_IVP["INDICATOR_GAMMAFACTOR_SLIDER"].setSliderValue(newValue = (cac['IVP_GammaFactor']-0.005)*(100/0.095), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(f"{cac['IVP_GammaFactor']*100:.1f} %")
    guios_IVP["INDICATOR_DELTAFACTOR_SLIDER"].setSliderValue(newValue = (cac['IVP_DeltaFactor']-0.1)*(100/9.9), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(f"{int(cac['IVP_DeltaFactor']*100):d} %")
else:
    guios_MAIN["MAININDICATOR_IVP"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATOR_IVP"].deactivate()
    guios_MAIN["MAININDICATORSETUP_IVP"].deactivate()

#SWING
if cac is not None and cac['SWING_Master']:
    guios_MAIN["MAININDICATOR_SWING"].activate()
    guios_MAIN["MAININDICATOR_SWING"].setStatus(status = oc['SWING_Master'], callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATORSETUP_SWING"].activate()
    for lineIndex in range (_NMAXLINES['SWING']):
        if cac[f'SWING_{lineIndex}_LineActive']:
            swingRange = cac[f'SWING_{lineIndex}_SwingRange']
            width      = oc[f'SWING_{lineIndex}_Width']
            display    = oc[f'SWING_{lineIndex}_Display']
            guios_SWING[f"INDICATOR_SWING{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_SWING[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].updateText(f"{swingRange:.4f}")
            guios_SWING[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].activate()
            guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].activate()
        else:
            guios_SWING[f"INDICATOR_SWING{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_SWING[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].updateText("-")
            guios_SWING[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].deactivate()
            guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].deactivate()
else:
    guios_MAIN["MAININDICATOR_SWING"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATOR_SWING"].deactivate()
    guios_MAIN["MAININDICATORSETUP_SWING"].deactivate()

#NNA
if cac is not None and cac['NNA_Master']:
    guios_MAIN["SUBINDICATOR_NNA"].activate()
    guios_MAIN["SUBINDICATOR_NNA"].setStatus(status = oc['NNA_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_NNA"].activate()
    for lineIndex in range (_NMAXLINES['NNA']):
        if cac[f'NNA_{lineIndex}_LineActive']:
            nnCode   = cac[f'NNA_{lineIndex}_NeuralNetworkCode']
            nnCode_str = "" if nnCode is None else f"{nnCode}"
            alpha    = cac[f'NNA_{lineIndex}_Alpha']
            beta     = cac[f'NNA_{lineIndex}_Beta']
            width    = oc[f'NNA_{lineIndex}_Width']
            display  = oc[f'NNA_{lineIndex}_Display']
            guios_NNA[f"INDICATOR_NNA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_NNA[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].updateText(nnCode_str)
            guios_NNA[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].updateText(f"{alpha:.2f}")
            guios_NNA[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].updateText(f"{beta}")
            guios_NNA[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].activate()
            guios_NNA[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].activate()
        else:
            guios_NNA[f"INDICATOR_NNA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_NNA[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].updateText("-")
            guios_NNA[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].updateText("-")
            guios_NNA[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].updateText("-")
            guios_NNA[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].deactivate()
            guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].deactivate()
            guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
else:
    guios_MAIN["SUBINDICATOR_NNA"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_NNA"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_NNA"].deactivate()

#MMACD
if cac is not None and cac['MMACD_Master']:
    guios_MAIN["SUBINDICATOR_MMACD"].activate()
    guios_MAIN["SUBINDICATOR_MMACD"].setStatus(status = oc['MMACD_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_MMACD"].activate()
    for lineIndex in range (_NMAXLINES['MMACD']):
        if cac[f'MMACD_MA{lineIndex}_LineActive']:
            nSamples = cac[f'MMACD_MA{lineIndex}_NSamples']
            guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
        else:
            guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText("-")
    signalNSamples = cac['MMACD_SignalNSamples']
    guios_MMACD["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(f"{signalNSamples}")
else:
    guios_MAIN["SUBINDICATOR_MMACD"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_MMACD"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_MMACD"].deactivate()

#DMIxADX
if cac is not None and cac['DMIxADX_Master']:
    guios_MAIN["SUBINDICATOR_DMIxADX"].activate()
    guios_MAIN["SUBINDICATOR_DMIxADX"].setStatus(status = oc['DMIxADX_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_DMIxADX"].activate()
    for lineIndex in range (_NMAXLINES['DMIxADX']):
        if cac[f'DMIxADX_{lineIndex}_LineActive']:
            nSamples = cac[f'DMIxADX_{lineIndex}_NSamples']
            width    = oc[f'DMIxADX_{lineIndex}_Width']
            display  = oc[f'DMIxADX_{lineIndex}_Display']
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].activate()
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].activate()
        else:
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].deactivate()
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].deactivate()
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
else:
    guios_MAIN["SUBINDICATOR_DMIxADX"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_DMIxADX"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_DMIxADX"].deactivate()

#MFI
if cac is not None and cac['MFI_Master']:
    guios_MAIN["SUBINDICATOR_MFI"].activate()
    guios_MAIN["SUBINDICATOR_MFI"].setStatus(status = oc['MFI_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_MFI"].activate()
    for lineIndex in range (_NMAXLINES['MFI']):
        if cac[f'MFI_{lineIndex}_LineActive']:
            nSamples = cac[f'MFI_{lineIndex}_NSamples']
            width    = oc[f'MFI_{lineIndex}_Width']
            display  = oc[f'MFI_{lineIndex}_Display']
            guios_MFI[f"INDICATOR_MFI{lineIndex}"].setStatus(status = True)
            guios_MFI[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_MFI[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].activate()
            guios_MFI[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].activate()
        else:
            guios_MFI[f"INDICATOR_MFI{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MFI[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_MFI[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].deactivate()
            guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].deactivate()
else:
    guios_MAIN["SUBINDICATOR_MFI"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_MFI"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_MFI"].deactivate()

#TPD
if cac is not None and cac['TPD_Master']:
    guios_MAIN["SUBINDICATOR_TPD"].activate()
    guios_MAIN["SUBINDICATOR_TPD"].setStatus(status = oc['TPD_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_TPD"].activate()
    for lineIndex in range (_NMAXLINES['TPD']):
        if cac[f'TPD_{lineIndex}_LineActive']:
            viewLength = cac[f'TPD_{lineIndex}_ViewLength']
            nSamples   = cac[f'TPD_{lineIndex}_NSamples']
            nSamplesMA = cac[f'TPD_{lineIndex}_NSamplesMA']
            width      = oc[f'TPD_{lineIndex}_Width']
            display    = oc[f'TPD_{lineIndex}_Display']
            guios_TPD[f"INDICATOR_TPD{lineIndex}"].setStatus(status = True)
            guios_TPD[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].updateText(f"{viewLength}")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].updateText(f"{nSamplesMA}")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].activate()
            guios_TPD[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].activate()
        else:
            guios_TPD[f"INDICATOR_TPD{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_TPD[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].updateText("-")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].updateText("-")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].deactivate()
            guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].deactivate()
else:
    guios_MAIN["SUBINDICATOR_TPD"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_TPD"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_TPD"].deactivate()

#WOI
if cac is not None and cac['WOI_Master']:
    guios_MAIN["SUBINDICATOR_WOI"].activate()
    guios_MAIN["SUBINDICATOR_WOI"].setStatus(status = oc['WOI_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_WOI"].activate()
    for lineIndex in range (_NMAXLINES['WOI']):
        if cac[f'WOI_{lineIndex}_LineActive']:
            nSamples = cac[f'WOI_{lineIndex}_NSamples']
            width    = oc[f'WOI_{lineIndex}_Width']
            display  = oc[f'WOI_{lineIndex}_Display']
            guios_WOI[f"INDICATOR_WOI{lineIndex}"].setStatus(status = True)
            guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_WOI[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].activate()
            guios_WOI[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].activate()
        else:
            guios_WOI[f"INDICATOR_WOI{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_WOI[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].deactivate()
            guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].deactivate()
else:
    guios_MAIN["SUBINDICATOR_WOI"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_WOI"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_WOI"].deactivate()

#NES
if cac is not None and cac['NES_Master']:
    guios_MAIN["SUBINDICATOR_NES"].activate()
    guios_MAIN["SUBINDICATOR_NES"].setStatus(status = oc['NES_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_NES"].activate()
    for lineIndex in range (_NMAXLINES['NES']):
        if cac[f'NES_{lineIndex}_LineActive']:
            nSamples = cac[f'NES_{lineIndex}_NSamples']
            width    = oc[f'NES_{lineIndex}_Width']
            display  = oc[f'NES_{lineIndex}_Display']
            guios_NES[f"INDICATOR_NES{lineIndex}"].setStatus(status = True)
            guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_NES[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].activate()
            guios_NES[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].activate()
        else:
            guios_NES[f"INDICATOR_NES{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_NES[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].deactivate()
            guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].deactivate()
else:
    guios_MAIN["SUBINDICATOR_NES"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_NES"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_NES"].deactivate()
"""

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
        color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_SMA{lineSelected}_LINECOLOR"].getColor()
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
        sub_page.GUIOs[f"INDICATOR_SMA{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        sub_page.GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        sub_page.GUIOs['APPLYNEWSETTINGS'].activate()

    #---[2-4]: WidthTextInputBox
    elif setter == 'WidthTextInputBox': 
        sub_page.GUIOs['APPLYNEWSETTINGS'].activate()
        
    #---[2-5]: DisplaySwitch
    elif setter == 'DisplaySwitch':     
        sub_page.GUIOs['APPLYNEWSETTINGS'].activate()
        
    #---[2-6]: ApplySettings
    elif setter == 'ApplySettings':     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (NMAXLINES):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'SMA_{lineIndex}_Width']
            reset = False
            try:
                width = int(sub_page.GUIOs[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'SMA_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'SMA_{lineIndex}_Width'] = 1
                sub_page.GUIOs[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'SMA_{lineIndex}_Width']))
            if width_previous != oc[f'SMA_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'SMA_{lineIndex}_ColorR%{cgt}'], 
                              oc[f'SMA_{lineIndex}_ColorG%{cgt}'], 
                              oc[f'SMA_{lineIndex}_ColorB%{cgt}'], 
                              oc[f'SMA_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_SMA{lineIndex}_LINECOLOR"].getColor()
            oc[f'SMA_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'SMA_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'SMA_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'SMA_{lineIndex}_ColorA%{cgt}'] = color_a
            if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'SMA_{lineIndex}_Display']
            oc[f'SMA_{lineIndex}_Display'] = sub_page.GUIOs[f"INDICATOR_SMA{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'SMA_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #MA Master
        maMaster_previous = oc[f'SMA_Master']
        oc[f'SMA_Master'] = main_page.GUIOs[f"MAININDICATOR_SMA"].getStatus()
        if maMaster_previous != oc[f'SMA_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Queue Update
        for line in [aCode for aCode in analysis_parameters if aCode.startswith('SMA')]:
            lineIndex = analysis_parameters[line]['lineIndex']
            if not updateTracker[lineIndex]: continue
            chart_drawer._drawer_RemoveDrawings(analysisCode    = line, gRemovalSignal = CD_FULL_DRAW_SIGNALS) #Remove previous graphics
            chart_drawer.addBufferZone_toDrawQueue(analysisCode = line, drawSignal     = CD_FULL_DRAW_SIGNALS) #Update draw queue
        #Control Buttons Handling
        sub_page.GUIOs['APPLYNEWSETTINGS'].deactivate()
        activate_save_configuration = True

    #[3]: Analysis Related
    #---[3-1]: Line Activation Switch
    elif setter == 'LineActivationSwitch': 
        lineIndex = int(guio_name_split[2])
        #Get new switch status
        _newStatus = sub_page.GUIOs[f"INDICATOR_SMA{lineIndex}"].getStatus()
        oc[f'SMA_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True
    
    #---[3-2]: Interval Text Input Box
    elif setter == 'IntervalTextInputBox': 
        lineIndex = int(guio_name_split[2])
        #Get new nSamples
        try:    _nSamples = int(sub_page.GUIOs[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].getText())
        except: _nSamples = None
        #Save the new value to the object config dictionary
        oc[f'SMA_{lineIndex}_NSamples'] = _nSamples
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #[3]: Return Status Flag
    return activate_save_configuration

"""
#Subpage 'IVP'
elif indicatorType == 'IVP':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):     
        lineSelected = ssps['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['IVP'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].getColor()
        ssps['IVP'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['IVP'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['IVP'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['IVP'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['IVP'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['IVP'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['IVP'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['IVP'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['IVP'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['IVP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):              
        cType = guioName_split[2]
        ssps['IVP'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['IVP'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['IVP'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['IVP'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['IVP'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['IVP'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['IVP'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['IVP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):         
        lineSelected = ssps['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['IVP'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['IVP'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['IVP'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['IVP'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['IVP'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['IVP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayWidthSlider'): 
        lineTarget = guioName_split[2]
        sliderValue = ssps['IVP'].GUIOs[f"INDICATOR_{lineTarget}_DISPLAYWIDTHSLIDER"].getSliderValue()
        ssps['IVP'].GUIOs[f"INDICATOR_{lineTarget}_DISPLAYWIDTHVALUETEXT"].updateText(str(round(sliderValue/100*0.9+0.1, 2)))
        ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):      
        ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'VPLPBDisplayRegion'): 
        #Get new VPLPBDisplayRegion
        sliderValue = ssps['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].getSliderValue()
        drValue = sliderValue/100*0.950+0.050
        ssps['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT"].updateText(f"{drValue*100:.1f} %")
        ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):
        #UpdateTracker Initialization
        updateTracker = [False, False] #[0]: VPLP, [1]: VPLPB
        #Check for any changes in the configuration
        #---IVP Master
        ivpMaster_previous = oc['IVP_Master']
        oc['IVP_Master'] = ssps['MAIN'].GUIOs["MAININDICATOR_IVP"].getStatus()
        if ivpMaster_previous != oc['IVP_Master']: updateTracker = [True, True]
        #---displaySwitch - VPLP
        vplpDisplay_prev = oc['IVP_VPLP_Display']
        oc['IVP_VPLP_Display'] = ssps['IVP'].GUIOs["INDICATOR_VPLP_DISPLAYSWITCH"].getStatus()
        if vplpDisplay_prev != oc['IVP_VPLP_Display']: updateTracker[0] = True
        #---displaySwitch - VPLB
        vplpbDisplay_prev = oc['IVP_VPLPB_Display']
        oc['IVP_VPLPB_Display'] = ssps['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYSWITCH"].getStatus()
        if vplpbDisplay_prev != oc['IVP_VPLPB_Display']: updateTracker[1] = True
        #---displayWidth - VPLP
        vplpDisplayWidth_prev = oc['IVP_VPLP_DisplayWidth']
        oc['IVP_VPLP_DisplayWidth'] = round(ssps['IVP'].GUIOs["INDICATOR_VPLP_DISPLAYWIDTHSLIDER"].getSliderValue()/100*0.9+0.1, 2)
        if vplpDisplayWidth_prev != oc['IVP_VPLP_DisplayWidth']: updateTracker[0] = True
        #---VPLPB Display Region
        vplpbDisplayRegion_prev = oc['IVP_VPLPB_DisplayRegion']
        oc['IVP_VPLPB_DisplayRegion'] = round(ssps['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].getSliderValue()/100*0.950+0.050, 3)
        if vplpbDisplayRegion_prev != oc['IVP_VPLPB_DisplayRegion']: updateTracker[1] = True
        #---Colors
        for targetLine in ('VPLP', 'VPLPB'):
            color_previous = (oc[f'IVP_{targetLine}_ColorR%{cgt}'],
                                oc[f'IVP_{targetLine}_ColorG%{cgt}'],
                                oc[f'IVP_{targetLine}_ColorB%{cgt}'],
                                oc[f'IVP_{targetLine}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['IVP'].GUIOs[f"INDICATOR_{targetLine}_COLOR"].getColor()
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
            self._drawer_RemoveDrawings(analysisCode      = 'IVP', gRemovalSignal = drawSignal) #Remove previous graphics
            self.__addBufferZone_toDrawQueue(analysisCode = 'IVP', drawSignal     = drawSignal) #Update draw queue
        #Settings Control Button
        ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'Interval'):
        #Get new nSamples
        try:    _nSamples = int(ssps['IVP'].GUIOs["INDICATOR_INTERVAL_INPUTTEXT"].getText())
        except: _nSamples = None
        #Save the new value to the object config dictionary
        oc['IVP_NSamples'] = _nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'GammaFactor'):
        #Get new Gamma Factor
        gammaFactor = round(ssps['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_SLIDER"].getSliderValue()/100*0.095+0.005, 3)
        ssps['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(f"{gammaFactor*100:.1f} %")
        oc['IVP_GammaFactor'] = gammaFactor
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'DeltaFactor'):
        #Get new Delta Factor
        deltaFactor = round(ssps['IVP'].GUIOs["INDICATOR_DELTAFACTOR_SLIDER"].getSliderValue()/100*9.9+0.1, 1)
        ssps['IVP'].GUIOs["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(f"{int(deltaFactor*100)} %")
        oc['IVP_DeltaFactor'] = deltaFactor
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'Prominence'):
        #Get new Prominence
        prominence = round(ssps['IVP'].GUIOs["INDICATOR_PROMINENCE_SLIDER"].getSliderValue()/100*0.99+0.01, 2)
        ssps['IVP'].GUIOs["INDICATOR_PROMINENCE_VALUETEXT"].updateText(f"{int(prominence*100)} %")
        oc['IVP_Prominence'] = prominence
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'Distance'):
        #Get new Distance
        distance = int(round(ssps['IVP'].GUIOs["INDICATOR_DISTANCE_SLIDER"].getSliderValue()/100*99+1))
        ssps['IVP'].GUIOs["INDICATOR_DISTANCE_VALUETEXT"].updateText(f"{distance}")
        oc['IVP_Distance'] = distance
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'Height'):
        #Get new Height
        height = round(ssps['IVP'].GUIOs["INDICATOR_HEIGHT_SLIDER"].getSliderValue()/100, 2)
        ssps['IVP'].GUIOs["INDICATOR_HEIGHT_VALUETEXT"].updateText(f"{int(height*100)} %")
        oc['IVP_Height'] = height
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'SWING'
elif indicatorType == 'SWING':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['SWING'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineSelected}_LINECOLOR"].getColor()
        ssps['SWING'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['SWING'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['SWING'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['SWING'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['SWING'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['SWING'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['SWING'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['SWING'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['SWING'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['SWING'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['SWING'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['SWING'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                gValue = int(ssps['SWING'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                bValue = int(ssps['SWING'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                aValue = int(ssps['SWING'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['SWING'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['SWING'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['SWING'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['SWING'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['SWING'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['SWING'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['SWING'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['SWING'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['SWING'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['SWING'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['SWING'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['SWING'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['SWING']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'SWING_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'SWING_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'SWING_{lineIndex}_Width'] = 1
                ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'SWING_{lineIndex}_Width']))
            if width_previous != oc[f'SWING_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'SWING_{lineIndex}_ColorR%{cgt}'],
                                oc[f'SWING_{lineIndex}_ColorG%{cgt}'],
                                oc[f'SWING_{lineIndex}_ColorB%{cgt}'],
                                oc[f'SWING_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_LINECOLOR"].getColor()
            oc[f'SWING_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'SWING_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'SWING_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'SWING_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'SWING_{lineIndex}_Display']
            oc[f'SWING_{lineIndex}_Display'] = ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'SWING_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---SWING Master
        swingMaster_previous = oc['SWING_Master']
        oc['SWING_Master'] = ssps['MAIN'].GUIOs["MAININDICATOR_SWING"].getStatus()
        if swingMaster_previous != oc['SWING_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredSWING in (aCode for aCode in ap_iID if aCode.startswith('SWING')):
            lineIndex = ap_iID[configuredSWING]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredSWING, gRemovalSignal = _FULLDRAWSIGNALS['SWING']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredSWING, drawSignal     = _FULLDRAWSIGNALS['SWING']) #Update draw queue
        #Control Buttons Handling
        ssps['SWING'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        _newStatus = ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}"].getStatus()
        oc[f'SWING_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'SwingRangeTextInputBox'):
        lineIndex = int(guioName_split[2])
        #Get new Swing Range
        try:    swingRange = round(float(ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].getText()), 4)
        except: swingRange = None
        #Save the new value to the object config dictionary
        oc[f'SWING_{lineIndex}_SwingRange'] = swingRange
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'NNA'
elif indicatorType == 'NNA':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['NNA'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineSelected}_LINECOLOR"].getColor()
        ssps['NNA'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['NNA'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['NNA'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['NNA'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['NNA'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['NNA'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['NNA'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['NNA'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['NNA'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['NNA'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['NNA'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['NNA'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['NNA'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['NNA'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['NNA'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['NNA'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['NNA'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['NNA'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['NNA'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['NNA'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['NNA'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['NNA'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['NNA'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['NNA'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['NNA'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['NNA'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['NNA'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['NNA']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'NNA_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'NNA_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'NNA_{lineIndex}_Width'] = 1
                ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'NNA_{lineIndex}_Width']))
            if width_previous != oc[f'NNA_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'NNA_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'NNA_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'NNA_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'NNA_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_LINECOLOR"].getColor()
            oc[f'NNA_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'NNA_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'NNA_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'NNA_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'NNA_{lineIndex}_Display']
            oc[f'NNA_{lineIndex}_Display'] = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'NNA_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---NNA Master
        mfiMaster_previous = oc['NNA_Master']
        oc['NNA_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_NNA"].getStatus()
        if mfiMaster_previous != oc['NNA_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['NNA']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['NNA'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredNNA in (aCode for aCode in ap_iID if aCode.startswith('NNA')):
            lineIndex = ap_iID[configuredNNA]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredNNA, gRemovalSignal = _FULLDRAWSIGNALS['NNA']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredNNA, drawSignal     = _FULLDRAWSIGNALS['NNA']) #Update draw queue
        #Control Buttons Handling
        ssps['NNA'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}"].getStatus()
        oc[f'NNA_{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'NNCodeTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new Neural Network Code
        try:    nnCode = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].getText()
        except: nnCode = None
        #Save the new value to the object config dictionary
        oc[f'NNA_{lineIndex}_NeuralNetworkCode'] = nnCode
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'AlphaTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new Alpha
        try:    alpha = round(float(ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].getText()), 2)
        except: alpha = None
        #Save the new value to the object config dictionary
        oc[f'NNA_{lineIndex}_Alpha'] = alpha
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'BetaTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new Beta
        try:    beta = int(ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].getText())
        except: beta = None
        #Save the new value to the object config dictionary
        oc[f'NNA_{lineIndex}_Beta'] = beta
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'MMACD'
elif indicatorType == 'MMACD':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'): 
        lineSelected = ssps['MMACD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['MMACD'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].getColor()
        ssps['MMACD'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['MMACD'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['MMACD'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['MMACD'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['MMACD'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['MMACD'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['MMACD'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['MMACD'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['MMACD'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['MMACD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):          
        cType = guioName_split[2]
        ssps['MMACD'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                gValue = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                bValue = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                aValue = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['MMACD'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['MMACD'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['MMACD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):     
        lineSelected = ssps['MMACD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['MMACD'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['MMACD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['MMACD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):  
        ssps['MMACD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'HistrogramTypeSelectionBox'):
        ssps['MMACD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):  
        #UpdateTracker Initialization
        updateTracker = [False, False, False] #[0]: Draw MMACD, [1]: Draw SIGNAL, [2]: Draw HISTOGRAM
        #Check for any changes in the configuration
        #---MMACD Master
        mmacdMaster_previous = oc['MMACD_Master']
        oc['MMACD_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_MMACD"].getStatus()
        if mmacdMaster_previous != oc['MMACD_Master']: 
            updateTracker[0] = True
            updateTracker[1] = True
            updateTracker[2] = True
        #---Colors
        for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
            color_previous = (oc[f'MMACD_{targetLine}_ColorR%{cgt}'],
                                oc[f'MMACD_{targetLine}_ColorG%{cgt}'],
                                oc[f'MMACD_{targetLine}_ColorB%{cgt}'],
                                oc[f'MMACD_{targetLine}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['MMACD'].GUIOs[f"INDICATOR_{targetLine}_COLOR"].getColor()
            oc[f'MMACD_{targetLine}_ColorR%{cgt}'] = color_r
            oc[f'MMACD_{targetLine}_ColorG%{cgt}'] = color_g
            oc[f'MMACD_{targetLine}_ColorB%{cgt}'] = color_b
            oc[f'MMACD_{targetLine}_ColorA%{cgt}'] = color_a
            if (color_previous != (color_r, color_g, color_b, color_a)): 
                if   (targetLine == 'MMACD'):      updateTracker[0] = True
                elif (targetLine == 'SIGNAL'):     updateTracker[1] = True
                elif (targetLine == 'HISTOGRAM+'): updateTracker[2] = True
                elif (targetLine == 'HISTOGRAM-'): updateTracker[2] = True
        #---Line Display
        for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM'):
            displayStatus_prev = oc[f'MMACD_{targetLine}_Display']
            oc[f'MMACD_{targetLine}_Display'] = ssps['MMACD'].GUIOs[f"INDICATOR_{targetLine}_DISPLAYSWITCH"].getStatus()
            if displayStatus_prev != oc[f'MMACD_{targetLine}_Display']:
                if   targetLine == 'MMACD':     updateTracker[0] = True
                elif targetLine == 'SIGNAL':    updateTracker[1] = True
                elif targetLine == 'HISTOGRAM': updateTracker[2] = True
        #---Histogram Type
        histogramType_prev = oc['MMACD_HISTOGRAM_Type']
        oc['MMACD_HISTOGRAM_Type'] = ssps['MMACD'].GUIOs["INDICATOR_HISTOGRAMTYPE_SELECTION"].getSelected()
        if histogramType_prev != oc['MMACD_HISTOGRAM_Type']:
            updateTracker[2] = True
        #Extrema Recomputation
        if any(updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['MMACD']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['MMACD'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        drawSignal = 0
        drawSignal += 0b001*updateTracker[0] #MMACD
        drawSignal += 0b010*updateTracker[1] #SIGNAL
        drawSignal += 0b100*updateTracker[2] #HISTOGRAM
        if drawSignal:
            self._drawer_RemoveDrawings(analysisCode = 'MMACD', gRemovalSignal = drawSignal) #Remove previous graphics
            self.__addBufferZone_toDrawQueue(analysisCode  = 'MMACD', drawSignal     = drawSignal) #Update draw queue
        #Control Buttons Handling
        ssps['MMACD'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'):          
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['MMACD'].GUIOs[f"INDICATOR_MMACDMA{lineIndex}"].getStatus()
        oc[f'MMACD_MA{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'):          
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamples = int(ssps['MMACD'].GUIOs[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'MMACD_MA{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'SignalIntervalTextInputBox'):    
        #Get new nSamples
        try:    nSamples = int(ssps['MMACD'].GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc['MMACD_SignalNSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'DMIxADX'
elif indicatorType == 'DMIxADX':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineSelected}_LINECOLOR"].getColor()
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['DMIxADX'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['DMIxADX'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['DMIxADX'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['DMIxADX'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                gValue = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                bValue = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                aValue = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['DMIxADX'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['DMIxADX'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayTypeSelectionBox'):
        ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['DMIxADX']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'DMIxADX_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'DMIxADX_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'DMIxADX_{lineIndex}_Width'] = 1
                ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'DMIxADX_{lineIndex}_Width']))
            if width_previous != oc[f'DMIxADX_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_LINECOLOR"].getColor()
            oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'DMIxADX_{lineIndex}_Display']
            oc[f'DMIxADX_{lineIndex}_Display'] = ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'DMIxADX_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---DMIxADX Master
        dmixadxMaster_previous = oc['DMIxADX_Master']
        oc['DMIxADX_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_DMIxADX"].getStatus()
        if dmixadxMaster_previous != oc['DMIxADX_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #---Display Type
        displayType_prev = oc['DMIxADX_DisplayType']
        oc['DMIxADX_DisplayType'] = ssps['DMIxADX'].GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].getSelected()
        if displayType_prev != oc['DMIxADX_DisplayType']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['DMIxADX']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['DMIxADX'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredDMIxADX in (aCode for aCode in ap_iID if aCode.startswith('DMIxADX')):
            lineIndex = ap_iID[configuredDMIxADX]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredDMIxADX, gRemovalSignal = _FULLDRAWSIGNALS['DMIxADX']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredDMIxADX, drawSignal     = _FULLDRAWSIGNALS['DMIxADX']) #Update draw queue
        #Control Buttons Handling
        ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}"].getStatus()
        oc[f'DMIxADX_{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamples = int(ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'DMIxADX_{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'MFI'
elif indicatorType == 'MFI':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineSelected}_LINECOLOR"].getColor()
        ssps['MFI'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['MFI'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['MFI'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['MFI'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['MFI'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['MFI'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['MFI'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['MFI'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['MFI'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['MFI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['MFI'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['MFI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['MFI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['MFI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['MFI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['MFI'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['MFI'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['MFI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['MFI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['MFI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['MFI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['MFI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['MFI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayTypeSelectionBox'):
        ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['MFI']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'MFI_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'MFI_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'MFI_{lineIndex}_Width'] = 1
                ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'MFI_{lineIndex}_Width']))
            if width_previous != oc[f'MFI_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'MFI_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'MFI_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'MFI_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'MFI_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_LINECOLOR"].getColor()
            oc[f'MFI_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'MFI_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'MFI_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'MFI_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'MFI_{lineIndex}_Display']
            oc[f'MFI_{lineIndex}_Display'] = ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'MFI_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---MFI Master
        mfiMaster_previous = oc['MFI_Master']
        oc['MFI_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_MFI"].getStatus()
        if mfiMaster_previous != oc['MFI_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #---Display Type
        displayType_prev = oc['MFI_DisplayType']
        oc['MFI_DisplayType'] = ssps['MFI'].GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].getSelected()
        if displayType_prev != oc['MFI_DisplayType']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['MFI']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['MFI'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredMFI in (aCode for aCode in ap_iID if aCode.startswith('MFI')):
            lineIndex = ap_iID[configuredMFI]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredMFI, gRemovalSignal = _FULLDRAWSIGNALS['MFI']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredMFI, drawSignal     = _FULLDRAWSIGNALS['MFI']) #Update draw queue
        #Control Buttons Handling
        ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}"].getStatus()
        oc[f'MFI_{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamples = int(ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'MFI_{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'TPD'
elif indicatorType == 'TPD':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['TPD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineSelected}_LINECOLOR"].getColor()
        ssps['TPD'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['TPD'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['TPD'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['TPD'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['TPD'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['TPD'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['TPD'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['TPD'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['TPD'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['TPD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['TPD'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['TPD'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['TPD'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['TPD'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['TPD'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['TPD'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['TPD'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['TPD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['TPD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['TPD'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['TPD'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['TPD'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['TPD'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['TPD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayTypeSelectionBox'):
        ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['TPD']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'TPD_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'TPD_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'TPD_{lineIndex}_Width'] = 1
                ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'TPD_{lineIndex}_Width']))
            if width_previous != oc[f'TPD_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'TPD_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'TPD_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'TPD_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'TPD_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_LINECOLOR"].getColor()
            oc[f'TPD_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'TPD_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'TPD_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'TPD_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'TPD_{lineIndex}_Display']
            oc[f'TPD_{lineIndex}_Display'] = ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'TPD_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---TPD Master
        tpdMaster_previous = oc['TPD_Master']
        oc['TPD_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_TPD"].getStatus()
        if tpdMaster_previous != oc['TPD_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #---Display Type
        displayType_prev = oc['TPD_DisplayType']
        oc['TPD_DisplayType'] = ssps['TPD'].GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].getSelected()
        if displayType_prev != oc['TPD_DisplayType']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['TPD']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['TPD'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredTPD in (aCode for aCode in ap_iID if aCode.startswith('TPD')):
            lineIndex = ap_iID[configuredTPD]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredTPD, gRemovalSignal = _FULLDRAWSIGNALS['TPD']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredTPD, drawSignal     = _FULLDRAWSIGNALS['TPD']) #Update draw queue
        #Control Buttons Handling
        ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}"].getStatus()
        oc[f'TPD_{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'ViewLengthTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    viewLength = int(ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].getText())
        except: viewLength = None
        #Save the new value to the object config dictionary
        oc[f'TPD_{lineIndex}_ViewLength'] = viewLength
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamples = int(ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'TPD_{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'MAIntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamplesMA = int(ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].getText())
        except: nSamplesMA = None
        #Save the new value to the object config dictionary
        oc[f'TPD_{lineIndex}_NSamplesMA'] = nSamplesMA
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'WOI'
elif indicatorType == 'WOI':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['WOI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineSelected}_LINECOLOR"].getColor()
        ssps['WOI'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['WOI'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['WOI'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['WOI'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['WOI'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['WOI'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['WOI'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['WOI'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['WOI'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['WOI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['WOI'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['WOI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['WOI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['WOI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['WOI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['WOI'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['WOI'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['WOI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['WOI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['WOI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['WOI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['WOI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['WOI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['WOI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayTypeSelectionBox'):
        ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['WOI']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'WOI_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'WOI_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'WOI_{lineIndex}_Width'] = 1
                ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'WOI_{lineIndex}_Width']))
            if width_previous != oc[f'WOI_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'WOI_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'WOI_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'WOI_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'WOI_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_LINECOLOR"].getColor()
            oc[f'WOI_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'WOI_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'WOI_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'WOI_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'WOI_{lineIndex}_Display']
            oc[f'WOI_{lineIndex}_Display'] = ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'WOI_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---WOI Master
        WOIMaster_previous = oc['WOI_Master']
        oc['WOI_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_WOI"].getStatus()
        if WOIMaster_previous != oc['WOI_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #---Display Type
        displayType_prev = oc['WOI_DisplayType']
        oc['WOI_DisplayType'] = ssps['WOI'].GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].getSelected()
        if displayType_prev != oc['WOI_DisplayType']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['WOI']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['WOI'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredWOI in (aCode for aCode in ap_iID if aCode.startswith('WOI')):
            lineIndex = ap_iID[configuredWOI]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredWOI, gRemovalSignal = _FULLDRAWSIGNALS['WOI']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredWOI, drawSignal     = _FULLDRAWSIGNALS['WOI']) #Update draw queue
        #Control Buttons Handling
        ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}"].getStatus()
        oc[f'WOI_{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamples = int(ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'WOI_{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'NES'
elif indicatorType == 'NES':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['NES'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['NES'].GUIOs[f"INDICATOR_NES{lineSelected}_LINECOLOR"].getColor()
        ssps['NES'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['NES'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['NES'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['NES'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['NES'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['NES'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['NES'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['NES'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['NES'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['NES'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['NES'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['NES'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['NES'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['NES'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['NES'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['NES'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['NES'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['NES'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['NES'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['NES'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['NES'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['NES'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['NES'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['NES'].GUIOs[f"INDICATOR_NES{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['NES'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayTypeSelectionBox'):
        ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['NES']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'NES_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'NES_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'NES_{lineIndex}_Width'] = 1
                ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'NES_{lineIndex}_Width']))
            if width_previous != oc[f'NES_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'NES_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'NES_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'NES_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'NES_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_LINECOLOR"].getColor()
            oc[f'NES_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'NES_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'NES_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'NES_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'NES_{lineIndex}_Display']
            oc[f'NES_{lineIndex}_Display'] = ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'NES_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---NES Master
        NESMaster_previous = oc['NES_Master']
        oc['NES_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_NES"].getStatus()
        if NESMaster_previous != oc['NES_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #---Display Type
        displayType_prev = oc['NES_DisplayType']
        oc['NES_DisplayType'] = ssps['NES'].GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].getSelected()
        if displayType_prev != oc['NES_DisplayType']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['NES']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['NES'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredNES in (aCode for aCode in ap_iID if aCode.startswith('NES')):
            lineIndex = ap_iID[configuredNES]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredNES, gRemovalSignal = _FULLDRAWSIGNALS['NES']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredNES, drawSignal = _FULLDRAWSIGNALS['NES']) #Update draw queue
        #Control Buttons Handling
        ssps['NES'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}"].getStatus()
        oc[f'NES_{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamples = int(ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'NES_{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
"""


def cd_on_position_highlight_update(chart_drawer):
    pass

"""
def __onPHU_IVP(self):
        #[1]: Instances
        oc        = self.objectConfig
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg      = self._data_agg[self.intervalID]
        dBox_g_kp_dt2 = self.displayBox_graphics['KLINESPRICE']['DESCRIPTIONTEXT2']
        
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

def __onPHU_NNA(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID]
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg      = self._data_agg[self.intervalID]
        siViewerIndex   = self.siTypes_siViewerAlloc['NNA']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - NNA]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if oc['NNA_Master']:
            for aCode in self.siTypes_analysisCodes['NNA']:
                #[3-1]: Existence Check
                if tsHovered not in dAgg[aCode]: continue

                #[3-2]: Display Check
                lineIndex     = ap[aCode]['lineIndex']
                lineIndex_str = f"{lineIndex}"
                if not oc[f'NNA_{lineIndex}_Display']: continue

                #TextStyle Check
                currentLine_style = dBox_g_this_dt1.getTextStyle(lineIndex_str)
                newLine_color = (oc[f'NNA_{lineIndex}_ColorR%{cgt}'],
                                 oc[f'NNA_{lineIndex}_ColorG%{cgt}'],
                                 oc[f'NNA_{lineIndex}_ColorB%{cgt}'],
                                 oc[f'NNA_{lineIndex}_ColorA%{cgt}'])
                if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                    newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                    newLine_style['color'] = newLine_color
                    dBox_g_this_dt1.addTextStyle(lineIndex_str, newLine_style)

                #Text & Format Array Construction
                value_nna = dAgg[aCode][tsHovered]['NNA']
                if value_nna is None: textBlock = f" {aCode}: NONE"
                else:                 textBlock = f" {aCode}: {value_nna:.2f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_MMACD(self):
        #[1]: Instances
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg      = self._data_agg[self.intervalID]
        siViewerIndex   = self.siTypes_siViewerAlloc['MMACD']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - MMACD]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        aCode = 'MMACD'
        if oc['MMACD_Master'] and aCode in dAgg and tsHovered in dAgg[aCode]:
            for line, valCode in (('MMACD',     'MMACD'), 
                                  ('SIGNAL',    'SIGNAL'), 
                                  ('HISTOGRAM', oc['MMACD_HISTOGRAM_Type'])
                                  ):
                #[3-1]: Display Check
                if not oc[f'MMACD_{line}_Display']: continue

                #[3-2]: Display Value
                value_display = dAgg[aCode][tsHovered][valCode]

                #[3-2]: Text Style Check
                if line == 'HISTOGRAM':
                    if value_display is None: newLine_colType = None
                    else:
                        if   0 < value_display: newLine_colType = 'HISTOGRAM+'
                        elif value_display < 0: newLine_colType = 'HISTOGRAM-'
                        else:                   newLine_colType = None
                else: newLine_colType = line
                if newLine_colType is None: newLine_colType = 'DEFAULT'
                else:
                    currentLine_style = dBox_g_this_dt1.getTextStyle(newLine_colType)
                    newLine_color = (oc[f'MMACD_{newLine_colType}_ColorR%{cgt}'],
                                     oc[f'MMACD_{newLine_colType}_ColorG%{cgt}'],
                                     oc[f'MMACD_{newLine_colType}_ColorB%{cgt}'],
                                     oc[f'MMACD_{newLine_colType}_ColorA%{cgt}'])
                    if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                        newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                        newLine_style['color'] = newLine_color
                        dBox_g_this_dt1.addTextStyle(newLine_colType, newLine_style)
                #[3-3]: Text & Format Array Construction
                if value_display is None: textBlock = f" {line}: NONE"
                else:                     textBlock = f" {line}: {auxiliaries.simpleValueFormatter(value = value_display, precision = 3)}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(line)+3),      'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), newLine_colType))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_DMIxADX(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID]
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg      = self._data_agg[self.intervalID]
        siViewerIndex   = self.siTypes_siViewerAlloc['DMIxADX']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - DMIxADX]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if oc['DMIxADX_Master']:
            for aCode in self.siTypes_analysisCodes['DMIxADX']:
                #[3-1]: Existence Check
                if tsHovered not in dAgg[aCode]: continue

                #[3-2]: Display Check
                lineIndex     = ap[aCode]['lineIndex']
                lineIndex_str = f"{lineIndex}"
                if not oc[f'DMIxADX_{lineIndex}_Display']: continue

                #[3-3]: TextStyle Check
                currentLine_style = dBox_g_this_dt1.getTextStyle(lineIndex_str)
                newLine_color = (oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'],
                                 oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'],
                                 oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'],
                                 oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'])
                if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                    newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                    newLine_style['color'] = newLine_color
                    dBox_g_this_dt1.addTextStyle(lineIndex_str, newLine_style)

                #[3-4]: Text & Format Array Construction
                value_display = dAgg[aCode][tsHovered][oc['DMIxADX_DisplayType']]
                if value_display is None: textBlock = f" {aCode}: NONE"
                else:                     textBlock = f" {aCode}: {value_display:.3f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)
        
    def __onPHU_MFI(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID]
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg      = self._data_agg[self.intervalID]
        siViewerIndex   = self.siTypes_siViewerAlloc['MFI']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - MFI]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if oc['MFI_Master']:
            for aCode in self.siTypes_analysisCodes['MFI']:
                #[3-1]: Existence Check
                if tsHovered not in dAgg[aCode]: continue

                #[3-2]: Display Check
                lineIndex     = ap[aCode]['lineIndex']
                lineIndex_str = f"{lineIndex}"
                if not oc[f'MFI_{lineIndex}_Display']: continue

                #[3-3]: TextStyle Check
                currentLine_style = dBox_g_this_dt1.getTextStyle(lineIndex_str)
                newLine_color = (oc[f'MFI_{lineIndex}_ColorR%{cgt}'],
                                 oc[f'MFI_{lineIndex}_ColorG%{cgt}'],
                                 oc[f'MFI_{lineIndex}_ColorB%{cgt}'],
                                 oc[f'MFI_{lineIndex}_ColorA%{cgt}'])
                if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                    newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                    newLine_style['color'] = newLine_color
                    dBox_g_this_dt1.addTextStyle(lineIndex_str, newLine_style)

                #[3-4]: Text & Format Array Construction
                value_display = dAgg[aCode][tsHovered][oc['MFI_DisplayType']]
                if value_display is None: textBlock = f" {aCode}: NONE"
                else:                     textBlock = f" {aCode}: {value_display:.3f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_TPD(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID]
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg      = self._data_agg[self.intervalID]
        siViewerIndex   = self.siTypes_siViewerAlloc['TPD']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - TPD]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if oc['TPD_Master']:
            for aCode in self.siTypes_analysisCodes['TPD']:
                #[3-1]: Existence Check
                if tsHovered not in dAgg[aCode]: continue

                #[3-2]: Display Check
                lineIndex     = ap[aCode]['lineIndex']
                lineIndex_str = f"{lineIndex}"
                if not oc[f'TPD_{lineIndex}_Display']: continue

                #[3-3]: TextStyle Check
                currentLine_style = dBox_g_this_dt1.getTextStyle(lineIndex_str)
                newLine_color = (oc[f'TPD_{lineIndex}_ColorR%{cgt}'],
                                 oc[f'TPD_{lineIndex}_ColorG%{cgt}'],
                                 oc[f'TPD_{lineIndex}_ColorB%{cgt}'],
                                 oc[f'TPD_{lineIndex}_ColorA%{cgt}'])
                if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                    newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                    newLine_style['color'] = newLine_color
                    dBox_g_this_dt1.addTextStyle(lineIndex_str, newLine_style)

                #[3-4]: Text & Format Array Construction
                value_display = dAgg[aCode][tsHovered][oc['TPD_DisplayType']]
                if value_display is None: textBlock = f" {aCode}: NONE"
                else:                     textBlock = f" {aCode}: {value_display:.3f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_WOI(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID]
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg      = self._data_agg[self.intervalID]
        siViewerIndex   = self.siTypes_siViewerAlloc['WOI']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - WOI]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if oc['WOI_Master']:
            for aCode in self.siTypes_analysisCodes['WOI']:
                #[3-1]: Existence Check
                if tsHovered not in dAgg[aCode]: continue

                #[3-2]: Display Check
                lineIndex     = ap[aCode]['lineIndex']
                lineIndex_str = f"{lineIndex}"
                if not oc[f'WOI_{lineIndex}_Display']: continue

                #[3-3]: TextStyle Check
                currentLine_style = dBox_g_this_dt1.getTextStyle(lineIndex_str)
                newLine_color = (oc[f'WOI_{lineIndex}_ColorR%{cgt}'],
                                 oc[f'WOI_{lineIndex}_ColorG%{cgt}'],
                                 oc[f'WOI_{lineIndex}_ColorB%{cgt}'],
                                 oc[f'WOI_{lineIndex}_ColorA%{cgt}'])
                if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                    newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                    newLine_style['color'] = newLine_color
                    dBox_g_this_dt1.addTextStyle(lineIndex_str, newLine_style)

                #[3-4]: Text & Format Array Construction
                dType         = oc['WOI_DisplayType']
                value_display = dAgg[aCode][tsHovered][dType]
                if value_display is None: textBlock = f" {aCode}: NONE"
                else:                     
                    if dType in ('WOI', 'WOI_ABSMA'):
                        textBlock = f" {aCode}: {auxiliaries.simpleValueFormatter(value = value_display, precision = 3)}"
                    elif dType == 'WOI_ABSMAREL':
                        textBlock = f" {aCode}: {value_display:.3f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    def __onPHU_NES(self):
        #[1]: Instances
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID]
        cgt = self.currentGUITheme
        tsHovered = self.posHighlight_hoveredPos[0]
        dAgg      = self._data_agg[self.intervalID]
        siViewerIndex   = self.siTypes_siViewerAlloc['NES']
        dBox_g_this_dt1 = self.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

        #[2]: Base Text & Styles
        text_display = f" [SI{siViewerIndex} - NES]"
        text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

        #[3]: Text Construction
        if oc['NES_Master']:
            for aCode in self.siTypes_analysisCodes['NES']:
                #[3-1]: Existence Check
                if tsHovered not in dAgg[aCode]: continue

                #[3-2]: Display Check
                lineIndex     = ap[aCode]['lineIndex']
                lineIndex_str = f"{lineIndex}"
                if not oc[f'NES_{lineIndex}_Display']: continue

                #[3-3]: TextStyle Check
                currentLine_style = dBox_g_this_dt1.getTextStyle(lineIndex_str)
                newLine_color = (oc[f'NES_{lineIndex}_ColorR%{cgt}'],
                                 oc[f'NES_{lineIndex}_ColorG%{cgt}'],
                                 oc[f'NES_{lineIndex}_ColorB%{cgt}'],
                                 oc[f'NES_{lineIndex}_ColorA%{cgt}'])
                if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                    newLine_style = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                    newLine_style['color'] = newLine_color
                    dBox_g_this_dt1.addTextStyle(lineIndex_str, newLine_style)

                #[3-4]: Text & Format Array Construction
                dType         = oc['NES_DisplayType']
                value_display = dAgg[aCode][tsHovered][dType]
                if value_display is None: textBlock = f" {aCode}: NONE"
                else:                     
                    if dType in ('NES', 'NES_ABSMA'):
                        textBlock = f" {aCode}: {auxiliaries.simpleValueFormatter(value = value_display, precision = 3)}"
                    elif dType == 'NES_ABSMAREL':
                        textBlock = f" {aCode}: {value_display:.3f}"
                text_display += textBlock
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(aCode)+3),     'DEFAULT'))
                text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1), lineIndex_str))

        #[4]: Text Update
        dBox_g_this_dt1.setText(text_display, text_styles)

    
"""

def cd_on_position_selection_update(chart_drawer):
    pass
 
"""
ph_selPos = self.posHighlight_selectedPos
dAgg      = self._data_agg[self.intervalID]
aParams   = self.analysisParams[self.intervalID]
dQueue    = self.__drawQueue
#IVP Update
if 'IVP' in aParams:
    if   ph_selPos is None: self._drawer_RemoveDrawings(analysisCode = 'IVP', gRemovalSignal = 0b01)
    elif ph_selPos in dAgg['IVP']: 
        if ph_selPos in dQueue: 
            if 'IVP' in dQueue[ph_selPos]: 
                if dQueue[ph_selPos]['IVP'] is not None: dQueue[ph_selPos]['IVP'] |= 0b01
            else:                                        dQueue[ph_selPos]['IVP'] = 0b01
        else:                                            dQueue[ph_selPos] = {'IVP': 0b01}
#SWING Update
for lineIndex in range (_NMAXLINES['SWING']):
    aCode = f'SWING_{lineIndex}'
    if aCode in aParams:
        if ph_selPos is None: self._drawer_RemoveDrawings(analysisCode = aCode, gRemovalSignal = 0b1)
        elif ph_selPos in dAgg[aCode]:
            if ph_selPos in dQueue: 
                if aCode in dQueue[ph_selPos]: 
                    if dQueue[ph_selPos][aCode] is not None: dQueue[ph_selPos][aCode] |= 0b1
                else:                                        dQueue[ph_selPos][aCode] = 0b1
            else:                                            dQueue[ph_selPos] = {aCode: 0b1}
"""


def cd_check_vertical_extremas(chart_drawer):
    pass

"""
def __checkVerticalExtremas_NNA(self):
        #[1]: References
        oc          = self.objectConfig
        ap          = self.analysisParams[self.intervalID]
        dAgg        = self._data_agg[self.intervalID]
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['NNA']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        #---Analysis Codes To Consider
        searchTargets = [(dType, 'NNA') 
                        for dType in self.siTypes_analysisCodes['NNA'] 
                        if ((dType in dAgg) and 
                            oc[f"NNA_{ap[dType]['lineIndex']}_Display"])]
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        for dType, valCode in searchTargets:
            tData = dAgg[dType]
            for ts in hvr_tssInVR:
                if ts not in tData: continue
                value = tData[ts][valCode]
                if value is None: continue
                if value < valMin: valMin = value
                if valMax < value: valMax = value
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        valMin, valMax = vvr_extrema_converter_centered(val_min = valMin, val_max = valMax, center = _VVR_CENTERVALUE['NNA'])

        #[4]: Change Check & Result Return
        return self.__cve_check_new_vertical_values(val_min               = valMin,
                                                    val_max               = valMax,
                                                    target                = siViewerCode,
                                                    precision_compensator = _VVR_PRECISIONCOMPENSATOR['NNA'])

    def __checkVerticalExtremas_MMACD(self):
        #[1]: References
        oc          = self.objectConfig
        hDispType   = oc['MMACD_HISTOGRAM_Type']
        dAgg        = self._data_agg[self.intervalID]
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['MMACD']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Data Check
        if "MMACD" not in dAgg: return False

        #[4]: Extremas Search
        #---Analysis Codes To Consider
        searchTargets = [valCode
                         for valCode, lineCode in (('MMACD', 'MMACD'), ('SIGNAL', 'SIGNAL'), (hDispType, 'HISTOGRAM'))
                         if oc[f"MMACD_{lineCode}_Display"]]
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        tData = dAgg["MMACD"]
        for valCode in searchTargets:
            for ts in hvr_tssInVR:
                if ts not in tData: continue
                value = tData[ts][valCode]
                if value is None: continue
                if value < valMin: valMin = value
                if valMax < value: valMax = value
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        if searchTargets == ['MSDELTA_ABSMA',]:
            valMin, valMax = vvr_extrema_converter_above_zero(val_min = valMin, val_max = valMax)
        else:
            valMin, valMax = vvr_extrema_converter_centered(val_min = valMin, val_max = valMax, center = _VVR_CENTERVALUE['MMACD'])

        #[5]: Change Check & Result Return
        return self.__cve_check_new_vertical_values(val_min               = valMin,
                                                    val_max               = valMax,
                                                    target                = siViewerCode,
                                                    precision_compensator = _VVR_PRECISIONCOMPENSATOR['MMACD'])

    def __checkVerticalExtremas_DMIxADX(self):
        #[1]: References
        oc          = self.objectConfig
        dispType    = oc['DMIxADX_DisplayType']
        ap          = self.analysisParams[self.intervalID]
        dAgg        = self._data_agg[self.intervalID]
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['DMIxADX']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        #---Analysis Codes To Consider
        searchTargets = [(dType, dispType) 
                        for dType in self.siTypes_analysisCodes['DMIxADX'] 
                        if ((dType in dAgg) and 
                            oc[f"DMIxADX_{ap[dType]['lineIndex']}_Display"])]
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        for dType, valCode in searchTargets:
            tData = dAgg[dType]
            for ts in hvr_tssInVR:
                if ts not in tData: continue
                value = tData[ts][valCode]
                if value is None: continue
                if value < valMin: valMin = value
                if valMax < value: valMax = value
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        if dispType in ('DMIxADX', 'DMIxADX_ABSMAREL'):
            valMin, valMax = vvr_extrema_converter_centered(val_min = valMin, val_max = valMax, center = _VVR_CENTERVALUE[('DMIxADX', dispType)])
        elif dispType == 'DMIxADX_ABSMA':
            valMin, valMax = vvr_extrema_converter_above_zero(val_min = valMin, val_max = valMax)

        #[4]: Change Check & Result Return
        return self.__cve_check_new_vertical_values(val_min               = valMin,
                                                    val_max               = valMax,
                                                    target                = siViewerCode,
                                                    precision_compensator = _VVR_PRECISIONCOMPENSATOR['DMIxADX'])

    def __checkVerticalExtremas_MFI(self):
        #[1]: References
        oc          = self.objectConfig
        dispType    = oc['MFI_DisplayType']
        ap          = self.analysisParams[self.intervalID]
        dAgg        = self._data_agg[self.intervalID]
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['MFI']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        #---Analysis Codes To Consider
        searchTargets = [(dType, dispType) 
                        for dType in self.siTypes_analysisCodes['MFI'] 
                        if ((dType in dAgg) and 
                            oc[f"MFI_{ap[dType]['lineIndex']}_Display"])]
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        for dType, valCode in searchTargets:
            tData = dAgg[dType]
            for ts in hvr_tssInVR:
                if ts not in tData: continue
                value = tData[ts][valCode]
                if value is None: continue
                if value < valMin: valMin = value
                if valMax < value: valMax = value
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        if dispType in ('MFI', 'MFI_DEVABSMAREL'):
            valMin, valMax = vvr_extrema_converter_centered(val_min = valMin, val_max = valMax, center = _VVR_CENTERVALUE[('MFI', dispType)])
        elif dispType == 'MFI_DEVABSMA':
            valMin, valMax = vvr_extrema_converter_above_zero(val_min = valMin, val_max = valMax)

        #[4]: Change Check & Result Return
        return self.__cve_check_new_vertical_values(val_min               = valMin,
                                                    val_max               = valMax,
                                                    target                = siViewerCode,
                                                    precision_compensator = _VVR_PRECISIONCOMPENSATOR['MFI'])

    def __checkVerticalExtremas_TPD(self):
        #[1]: References
        oc          = self.objectConfig
        dispType    = oc['TPD_DisplayType']
        ap          = self.analysisParams[self.intervalID]
        dAgg        = self._data_agg[self.intervalID]
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['TPD']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        #---Analysis Codes To Consider
        searchTargets = [(dType, dispType) 
                        for dType in self.siTypes_analysisCodes['TPD'] 
                        if ((dType in dAgg) and 
                            oc[f"TPD_{ap[dType]['lineIndex']}_Display"])]
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        for dType, valCode in searchTargets:
            tData = dAgg[dType]
            for ts in hvr_tssInVR:
                if ts not in tData: continue
                value = tData[ts][valCode]
                if value is None: continue
                if value < valMin: valMin = value
                if valMax < value: valMax = value
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        if dispType in ('TPD', 'TPD_ABSMAREL'):
            valMin, valMax = vvr_extrema_converter_centered(val_min = valMin, val_max = valMax, center = _VVR_CENTERVALUE[('TPD', dispType)])
        elif dispType == 'TPD_ABSMA':
            valMin, valMax = vvr_extrema_converter_above_zero(val_min = valMin, val_max = valMax)

        #[4]: Change Check & Result Return
        return self.__cve_check_new_vertical_values(val_min               = valMin,
                                                    val_max               = valMax,
                                                    target                = siViewerCode,
                                                    precision_compensator = _VVR_PRECISIONCOMPENSATOR['TPD'])

    def __checkVerticalExtremas_WOI(self):
        #[1]: References
        oc          = self.objectConfig
        dispType    = oc['WOI_DisplayType']
        ap          = self.analysisParams[self.intervalID]
        dAgg        = self._data_agg[self.intervalID]
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['WOI']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        #---Analysis Codes To Consider
        searchTargets = [(dType, dispType) 
                        for dType in self.siTypes_analysisCodes['WOI'] 
                        if ((dType in dAgg) and 
                            oc[f"WOI_{ap[dType]['lineIndex']}_Display"])]
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        for dType, valCode in searchTargets:
            tData = dAgg[dType]
            for ts in hvr_tssInVR:
                if ts not in tData: continue
                value = tData[ts][valCode]
                if value is None: continue
                if value < valMin: valMin = value
                if valMax < value: valMax = value
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        if dispType in ('WOI', 'WOI_ABSMAREL'):
            valMin, valMax = vvr_extrema_converter_centered(val_min = valMin, val_max = valMax, center = _VVR_CENTERVALUE[('WOI', dispType)])
        elif dispType == 'WOI_ABSMA':
            valMin, valMax = vvr_extrema_converter_above_zero(val_min = valMin, val_max = valMax)

        #[4]: Change Check & Result Return
        return self.__cve_check_new_vertical_values(val_min               = valMin,
                                                    val_max               = valMax,
                                                    target                = siViewerCode,
                                                    precision_compensator = _VVR_PRECISIONCOMPENSATOR['WOI'])

    def __checkVerticalExtremas_NES(self):
        #[1]: References
        oc          = self.objectConfig
        dispType    = oc['NES_DisplayType']
        ap          = self.analysisParams[self.intervalID]
        dAgg        = self._data_agg[self.intervalID]
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange
        siViewerIndex = self.siTypes_siViewerAlloc['NES']
        siViewerCode  = f"SIVIEWER{siViewerIndex}"

        #[2]: Timestamps Check
        if not hvr_tssInVR: return False

        #[3]: Extremas Search
        #---Analysis Codes To Consider
        searchTargets = [(dType, dispType) 
                        for dType in self.siTypes_analysisCodes['NES'] 
                        if ((dType in dAgg) and 
                            oc[f"NES_{ap[dType]['lineIndex']}_Display"])]
        #---Initial Extrema
        valMin = float('inf')
        valMax = float('-inf')
        #---Search Loop
        for dType, valCode in searchTargets:
            tData = dAgg[dType]
            for ts in hvr_tssInVR:
                if ts not in tData: continue
                value = tData[ts][valCode]
                if value is None: continue
                if value < valMin: valMin = value
                if valMax < value: valMax = value
        #---Extrema Check
        if math.isinf(valMin): return False
        if math.isinf(valMax): return False
        #---Extremas Filtering
        if dispType in ('NES', 'NES_ABSMAREL'):
            valMin, valMax = vvr_extrema_converter_centered(val_min = valMin, val_max = valMax, center = _VVR_CENTERVALUE[('NES', dispType)])
        elif dispType == 'NES_ABSMA':
            valMin, valMax = vvr_extrema_converter_above_zero(val_min = valMin, val_max = valMax)

        #[4]: Change Check & Result Return
        return self.__cve_check_new_vertical_values(val_min               = valMin,
                                                    val_max               = valMax,
                                                    target                = siViewerCode,
                                                    precision_compensator = _VVR_PRECISIONCOMPENSATOR['NES'])

"""

def cd_draw(chart_drawer, drawSignal, timestamp, analysisCode):
    #[1]: Parameters
    oc    = chart_drawer.objectConfig
    ap    = chart_drawer.analysisParams[chart_drawer.intervalID][analysisCode]
    cgt   = chart_drawer.currentGUITheme
    rclcg = chart_drawer.displayBox_graphics['KLINESPRICE']['RCLCG']
    lineIndex = ap['lineIndex']

    #[2]: Master & Display Status
    if not oc['SMA_Master']:               return 0b0
    if not oc[f'SMA_{lineIndex}_Display']: return 0b0

    #[3]: Draw Signal
    if drawSignal is None: drawSignal = 0b1
    if not drawSignal:     return 0b0

    #[4]: Data Acquisition
    smas = chart_drawer._data_agg[chart_drawer.intervalID][analysisCode]
    timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = chart_drawer.intervalID, timestamp = timestamp, nTicks = -1)
    smaResult_prev = smas.get(timestamp_prev, None)
    smaResult      = smas[timestamp]

    #[5]: Drawing
    drawn = 0b0
    #---[5-1]: SMA
    if drawSignal&0b1:
        #[5-1-1]: Previous Drawing Removal
        rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
        #[5-1-2]: Drawing
        if (smaResult_prev is not None) and (smaResult_prev['SMA'] is not None):
            #Shape Object Params
            timestampWidth = timestamp-timestamp_prev
            shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
            shape_x2 = round(timestamp     +timestampWidth/2, 1)
            shape_y1 = smaResult_prev['SMA']
            shape_y2 = smaResult['SMA']
            width    = oc[f'SMA_{lineIndex}_Width']
            color = (oc[f'SMA_{lineIndex}_ColorR%{cgt}'], 
                        oc[f'SMA_{lineIndex}_ColorG%{cgt}'], 
                        oc[f'SMA_{lineIndex}_ColorB%{cgt}'], 
                        oc[f'SMA_{lineIndex}_ColorA%{cgt}'])
            #Shape Adding
            rclcg.addShape_Line(x  = shape_x1, y  = shape_y1, 
                                x2 = shape_x2, y2 = shape_y2,
                                width = width,
                                color = color,
                                shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = 13+lineIndex)
        #[5-1-3]: Drawn Flag Update
        drawn += 0b1
        
    #[6]: Return Drawn Flag
    return drawn

"""

    def __drawer_IVP(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        rclcg        = self.displayBox_graphics['KLINESPRICE']['RCLCG']
        rclcg_xFixed = self.displayBox_graphics['KLINESPRICE']['RCLCG_XFIXED']

        #[2]: Master & Display Status
        if not oc['IVP_Master']: return 0b00

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b11
        if not drawSignal:     return 0b00

        #[4]: Data Acquisition
        dAgg = self._data_agg[self.intervalID]
        kline = dAgg['kline'][timestamp]
        ivp   = dAgg[analysisCode][timestamp]

        #[5]: Drawing
        drawn = 0b00
        #---[5-1]: Volume Price Level Profile
        if drawSignal&0b01 and oc['IVP_VPLP_Display'] and timestamp == self.posHighlight_selectedPos:
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

    def __drawer_SWING(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc    = self.objectConfig
        ap    = self.analysisParams[self.intervalID][analysisCode]
        cgt   = self.currentGUITheme
        rclcg = self.displayBox_graphics['KLINESPRICE']['RCLCG']
        lineIndex = ap['lineIndex']

        #[2]: Master & Display Status
        if not oc['SWING_Master']:               return 0b0
        if not oc[f'SWING_{lineIndex}_Display']: return 0b0

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        swing = self._data_agg[self.intervalID][analysisCode][timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: SWINGS
        if drawSignal&0b1:
            if timestamp == self.posHighlight_selectedPos:
                #[5-1]: Previous Drawing Removal
                rclcg.removeGroup(groupName = f'{analysisCode}_SWINGS')
                #[5-1-2]: Drawing
                swing_swings = swing['SWINGS']
                timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
                timestampWidth = timestamp-timestamp_prev
                color = (oc[f'SWING_{lineIndex}_ColorR%{cgt}'], 
                         oc[f'SWING_{lineIndex}_ColorG%{cgt}'], 
                         oc[f'SWING_{lineIndex}_ColorB%{cgt}'], 
                         oc[f'SWING_{lineIndex}_ColorA%{cgt}'])
                width = oc[f'SWING_{lineIndex}_Width']
                for sIndex in range (1, len(swing_swings)):
                    swing_prev    = swing_swings[sIndex-1]
                    swing_current = swing_swings[sIndex]
                    shape_x  = round(swing_prev[0]   +timestampWidth/2, 1)
                    shape_x2 = round(swing_current[0]+timestampWidth/2, 1)
                    shape_y  = swing_prev[1]
                    shape_y2 = swing_current[1]
                    rclcg.addShape_Line(x  = shape_x,  y  = shape_y,
                                        x2 = shape_x2, y2 = shape_y2,
                                        color = color,
                                        width = width,
                                        shapeName = sIndex, shapeGroupName = f'{analysisCode}_SWINGS', layerNumber = 13+lineIndex)
                #[5-1-3]: Drawn Flag Update
                drawn += 0b1
        
        #[6]: Return Drawn Flag
        return drawn

def __drawer_NNA(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID][analysisCode]
        cgt = self.currentGUITheme
        lineIndex = ap['lineIndex']
        siViewerIndex = self.siTypes_siViewerAlloc['NNA']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg         = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
        if not oc['NNA_Master']:                      return 0b0
        if not oc[f'NNA_{lineIndex}_Display']:        return 0b0
        
        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        nnas = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        nna_prev = nnas.get(timestamp_prev, None)
        nna      = nnas[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: ABSATHREL
        if drawSignal&0b1:
            #[5-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            if (nna_prev is not None) and (nna_prev['NNA'] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = nna_prev['NNA']
                shape_y2 = nna['NNA']
                width    = oc[f'NNA_{lineIndex}_Width']*3
                lineColor = (oc[f'NNA_{lineIndex}_ColorR%{cgt}'],
                             oc[f'NNA_{lineIndex}_ColorG%{cgt}'],
                             oc[f'NNA_{lineIndex}_ColorB%{cgt}'],
                             oc[f'NNA_{lineIndex}_ColorA%{cgt}'])
                #Shape Object Params
                rclcg.addShape_Line(x  = shape_x1, 
                                    x2 = shape_x2, 
                                    y  = shape_y1, 
                                    y2 = shape_y2, 
                                    width = width, 
                                    color = lineColor, 
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

    def __drawer_MMACD(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        siViewerIndex = self.siTypes_siViewerAlloc['MMACD']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b000
        if not oc['MMACD_Master']:                    return 0b000

        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b111
        if not drawSignal:     return 0b000

        #[4]: Data Acquisition
        mmacds = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev   = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        mmacd_prev = mmacds.get(timestamp_prev, None)
        mmacd      = mmacds[timestamp]

        #[5]: Common Coordinates
        tsWidth = timestamp-timestamp_prev
        shape_x1 = round(timestamp_prev+tsWidth/2, 1)
        shape_x2 = round(timestamp     +tsWidth/2, 1)

        #[6]: Drawing
        drawn = 0b000
        #---[6-1]: MMACD
        if drawSignal&0b001 and oc['MMACD_MMACD_Display']:
            #[6-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'MMACD_MMACD')
            #[6-1-2]: Drawing
            if (mmacd_prev is not None) and (mmacd_prev['MMACD'] is not None):
                #Shape Object Params
                shape_y     = mmacd_prev['MMACD']
                shape_y2    = mmacd['MMACD']
                shape_width = 1
                color = (oc[f'MMACD_MMACD_ColorR%{cgt}'],
                         oc[f'MMACD_MMACD_ColorG%{cgt}'],
                         oc[f'MMACD_MMACD_ColorB%{cgt}'],
                         oc[f'MMACD_MMACD_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x = shape_x1, x2 = shape_x2, 
                                    y = shape_y,  y2 = shape_y2, 
                                    width = shape_width, 
                                    color = color, 
                                    shapeName = timestamp, shapeGroupName = 'MMACD_MMACD', layerNumber = 1)
            #[6-1-3]: Drawn Flag Update
            drawn += 0b001
        #---[6-2]: SIGNAL
        if drawSignal&0b010 and oc['MMACD_SIGNAL_Display']:
            #[6-2-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'MMACD_SIGNAL')
            #[6-2-2]: Drawing
            if (mmacd_prev is not None) and (mmacd_prev['SIGNAL'] is not None):
                #Shape Object Params
                shape_y     = mmacd_prev['SIGNAL']
                shape_y2    = mmacd['SIGNAL']
                shape_width = 3
                color = (oc[f'MMACD_SIGNAL_ColorR%{cgt}'],
                         oc[f'MMACD_SIGNAL_ColorG%{cgt}'],
                         oc[f'MMACD_SIGNAL_ColorB%{cgt}'],
                         oc[f'MMACD_SIGNAL_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x = shape_x1, x2 = shape_x2,
                                    y = shape_y,  y2 = shape_y2,
                                    width = shape_width,
                                    color = color,
                                    shapeName = timestamp, shapeGroupName = 'MMACD_SIGNAL', layerNumber = 1)
            #[6-2-3]: Drawn Flag Update
            drawn += 0b010
        #---[6-3]: HISTOGRAM
        if drawSignal&0b100 and oc['MMACD_HISTOGRAM_Display']:
            #[6-3-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = 'MMACD_HISTOGRAM')
            #[6-3-2]: Drawing
            mr_mmacd     = mmacd['MMACD']
            mr_histogram = mmacd[oc['MMACD_HISTOGRAM_Type']]
            if mr_histogram is not None:
                #Shape Object Params
                shape_width = round(tsWidth*0.9, 1)
                shape_xPos  = round(timestamp+(tsWidth-shape_width)/2, 1)
                if 0 <= mr_histogram:
                    if 0 <= mr_mmacd:
                        color = (oc[f'MMACD_HISTOGRAM+_ColorR%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM+_ColorG%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM+_ColorB%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM+_ColorA%{cgt}'])
                    else:
                        color = (oc[f'MMACD_HISTOGRAM+_ColorR%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM+_ColorG%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM+_ColorB%{cgt}'],
                                 int(oc[f'MMACD_HISTOGRAM+_ColorA%{cgt}']/2))
                else:
                    if 0 <= mr_mmacd:
                        color = (oc[f'MMACD_HISTOGRAM-_ColorR%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM-_ColorG%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM-_ColorB%{cgt}'],
                                 int(oc[f'MMACD_HISTOGRAM-_ColorA%{cgt}']/2))
                    else:
                        color = (oc[f'MMACD_HISTOGRAM-_ColorR%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM-_ColorG%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM-_ColorB%{cgt}'],
                                 oc[f'MMACD_HISTOGRAM-_ColorA%{cgt}'])
                body_y      = 0
                body_height = mr_histogram
                #Shape Adding
                rclcg.addShape_Rectangle(x = shape_xPos, y = body_y, 
                                         width = shape_width, height = body_height, 
                                         color = color, 
                                         shapeName = timestamp, shapeGroupName = 'MMACD_HISTOGRAM', layerNumber = 0)
            #[6-3-3]: Drawn Flag Update
            drawn += 0b100

        #[7]: Return Drawn Flag
        return drawn

    def __drawer_DMIxADX(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID][analysisCode]
        cgt = self.currentGUITheme
        lineIndex = ap['lineIndex']
        siViewerIndex = self.siTypes_siViewerAlloc['DMIxADX']; 
        siViewerCode = f'SIVIEWER{siViewerIndex}'
        rclcg        = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
        if not oc['DMIxADX_Master']:                  return 0b0
        if not oc[f'DMIxADX_{lineIndex}_Display']:    return 0b0
        
        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        dmixadxs = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev     = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        dmixadx_prev = dmixadxs.get(timestamp_prev, None)
        dmixadx      = dmixadxs[timestamp]
        

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: ABSATHREL
        if drawSignal&0b1:
            #[5-1-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            dType = oc['DMIxADX_DisplayType']
            if (dmixadx_prev is not None) and (dmixadx_prev[dType] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = dmixadx_prev[dType]
                shape_y2 = dmixadx[dType]
                width    = oc[f'DMIxADX_{lineIndex}_Width']*3
                lineColor = (oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'],
                             oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'],
                             oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'],
                             oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'])
                #Shape Adding
                rclcg.addShape_Line(x  = shape_x1, 
                                    x2 = shape_x2, 
                                    y  = shape_y1, 
                                    y2 = shape_y2, 
                                    width = width, 
                                    color = lineColor, 
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

    def __drawer_MFI(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID][analysisCode]
        cgt = self.currentGUITheme
        lineIndex = ap['lineIndex']
        siViewerIndex = self.siTypes_siViewerAlloc['MFI']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg         = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
        if not oc['MFI_Master']:                      return 0b0
        if not oc[f'MFI_{lineIndex}_Display']:        return 0b0
        
        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        mfis = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        mfi_prev = mfis.get(timestamp_prev, None)
        mfi      = mfis[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: ABSATHREL
        if drawSignal&0b1:
            #[5-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            dType = oc['MFI_DisplayType']
            if (mfi_prev is not None) and (mfi_prev[dType] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = mfi_prev[dType]
                shape_y2 = mfi[dType]
                width    = oc[f'MFI_{lineIndex}_Width']*3
                lineColor = (oc[f'MFI_{lineIndex}_ColorR%{cgt}'],
                             oc[f'MFI_{lineIndex}_ColorG%{cgt}'],
                             oc[f'MFI_{lineIndex}_ColorB%{cgt}'],
                             oc[f'MFI_{lineIndex}_ColorA%{cgt}'])
                #Shape Object Params
                rclcg.addShape_Line(x  = shape_x1, 
                                    x2 = shape_x2, 
                                    y  = shape_y1, 
                                    y2 = shape_y2, 
                                    width = width, 
                                    color = lineColor, 
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

    def __drawer_TPD(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID][analysisCode]
        cgt = self.currentGUITheme
        lineIndex = ap['lineIndex']
        siViewerIndex = self.siTypes_siViewerAlloc['TPD']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg         = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
        if not oc['TPD_Master']:                      return 0b0
        if not oc[f'TPD_{lineIndex}_Display']:        return 0b0
        
        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        tpds = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        tpd_prev = tpds.get(timestamp_prev, None)
        tpd      = tpds[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: ABSATHREL
        if drawSignal&0b1:
            #[5-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            dType = oc['TPD_DisplayType']
            if (tpd_prev is not None) and (tpd_prev[dType] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = tpd_prev[dType]
                shape_y2 = tpd[dType]
                width    = oc[f'TPD_{lineIndex}_Width']*3
                lineColor = (oc[f'TPD_{lineIndex}_ColorR%{cgt}'],
                             oc[f'TPD_{lineIndex}_ColorG%{cgt}'],
                             oc[f'TPD_{lineIndex}_ColorB%{cgt}'],
                             oc[f'TPD_{lineIndex}_ColorA%{cgt}'])
                #Shape Object Params
                rclcg.addShape_Line(x  = shape_x1, 
                                    x2 = shape_x2, 
                                    y  = shape_y1, 
                                    y2 = shape_y2, 
                                    width = width, 
                                    color = lineColor, 
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

    def __drawer_WOI(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID][analysisCode]
        cgt = self.currentGUITheme
        lineIndex = ap['lineIndex']
        siViewerIndex = self.siTypes_siViewerAlloc['WOI']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg         = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
        if not oc['WOI_Master']:                      return 0b0
        if not oc[f'WOI_{lineIndex}_Display']:        return 0b0
        
        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        wois = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        woi_prev = wois.get(timestamp_prev, None)
        woi      = wois[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: ABSATHREL
        if drawSignal&0b1:
            #[5-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            dType = oc['WOI_DisplayType']
            if (woi_prev is not None) and (woi_prev[dType] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = woi_prev[dType]
                shape_y2 = woi[dType]
                width    = oc[f'WOI_{lineIndex}_Width']*3
                lineColor = (oc[f'WOI_{lineIndex}_ColorR%{cgt}'],
                             oc[f'WOI_{lineIndex}_ColorG%{cgt}'],
                             oc[f'WOI_{lineIndex}_ColorB%{cgt}'],
                             oc[f'WOI_{lineIndex}_ColorA%{cgt}'])
                #Shape Object Params
                rclcg.addShape_Line(x  = shape_x1, 
                                    x2 = shape_x2, 
                                    y  = shape_y1, 
                                    y2 = shape_y2, 
                                    width = width, 
                                    color = lineColor, 
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

    def __drawer_NES(self, drawSignal, timestamp, analysisCode):
        #[1]: Parameters
        oc  = self.objectConfig
        ap  = self.analysisParams[self.intervalID][analysisCode]
        cgt = self.currentGUITheme
        lineIndex = ap['lineIndex']
        siViewerIndex = self.siTypes_siViewerAlloc['NES']
        siViewerCode  = f'SIVIEWER{siViewerIndex}'
        rclcg         = self.displayBox_graphics[siViewerCode]['RCLCG']

        #[2]: Master & Display Status
        if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
        if not oc['NES_Master']:                      return 0b0
        if not oc[f'NES_{lineIndex}_Display']:        return 0b0
        
        #[3]: Draw Signal
        if drawSignal is None: drawSignal = 0b1
        if not drawSignal:     return 0b0

        #[4]: Data Acquisition
        ness = self._data_agg[self.intervalID][analysisCode]
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, nTicks = -1)
        nes_prev = ness.get(timestamp_prev, None)
        nes      = ness[timestamp]

        #[5]: Drawing
        drawn = 0b0
        #---[5-1]: ABSATHREL
        if drawSignal&0b1:
            #[5-1]: Previous Drawing Removal
            rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
            #[5-1-2]: Drawing
            dType = oc['NES_DisplayType']
            if (nes_prev is not None) and (nes_prev[dType] is not None):
                #Shape Object Params
                timestampWidth = timestamp-timestamp_prev
                shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
                shape_x2 = round(timestamp     +timestampWidth/2, 1)
                shape_y1 = nes_prev[dType]
                shape_y2 = nes[dType]
                width    = oc[f'NES_{lineIndex}_Width']*3
                lineColor = (oc[f'NES_{lineIndex}_ColorR%{cgt}'],
                             oc[f'NES_{lineIndex}_ColorG%{cgt}'],
                             oc[f'NES_{lineIndex}_ColorB%{cgt}'],
                             oc[f'NES_{lineIndex}_ColorA%{cgt}'])
                #Shape Object Params
                rclcg.addShape_Line(x  = shape_x1, 
                                    x2 = shape_x2, 
                                    y  = shape_y1, 
                                    y2 = shape_y2, 
                                    width   = width, 
                                    color   = lineColor, 
                                    shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = lineIndex)
            #[5-1-3]: Drawn Flag Update
            drawn += 0b1

        #[6]: Return Drawn Flag
        return drawn

"""

def cd_remove_expired_drawings(display_box_graphics, si_viewer_index, analysis_code, timestamp):
    #[1]: Drawings Removal
    display_box_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysis_code)

"""

            elif targetType == 'IVP':
                self.displayBox_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = f'IVP_VPLPB_{timestamp}')

            elif targetType == 'SWING':
                pass

            elif targetType == 'NNA':
                sivIdx = self.siTypes_siViewerAlloc['NNA']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'MMACD':
                sivIdx = self.siTypes_siViewerAlloc['MMACD']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACD_MMACD')
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACD_SIGNAL')
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACD_HISTOGRAM')

            elif targetType == 'DMIxADX':
                sivIdx = self.siTypes_siViewerAlloc['DMIxADX']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'MFI':
                sivIdx = self.siTypes_siViewerAlloc['MFI']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'TPD':
                sivIdx = self.siTypes_siViewerAlloc['TPD']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'WOI':
                sivIdx = self.siTypes_siViewerAlloc['WOI']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)

            elif targetType == 'NES':
                sivIdx = self.siTypes_siViewerAlloc['NES']
                if sivIdx is not None: 
                    sivCode = f"SIVIEWER{sivIdx}"
                    self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = aCode)
"""

def cd_remove_drawings(display_box_graphics, si_viewer_index, analysis_code, graphics_removal_signal):
    #[1]: Drawings Removal
    if graphics_removal_signal&0b1: 
        display_box_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysis_code)

"""
        #---[3-8]: IVP
        elif analysisType == 'IVP':
            if gRemovalSignal&0b01: dBox_g['KLINESPRICE']['RCLCG_XFIXED'].removeGroup(groupName = 'IVP_VPLP')
            rclcg = dBox_g['KLINESPRICE']['RCLCG']
            for ts in drawn:
                if 'IVP' not in drawn[ts]: continue
                if gRemovalSignal&0b10: rclcg.removeGroup(groupName = f'IVP_VPLPB_{ts}')

        #---[3-9]: SWING
        elif analysisType == 'SWING':
            if gRemovalSignal&0b1: dBox_g['KLINESPRICE']['RCLCG'].removeGroup(groupName = f"{analysisCode}_SWINGS")

        #---[3-13]: NNA
        elif analysisType == 'NNA':
            sivIdx = self.siTypes_siViewerAlloc['NNA']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b1: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-14]: MMACD
        elif analysisType == 'MMACD':
            sivIdx = self.siTypes_siViewerAlloc['MMACD']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b001: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = 'MMACD_MMACD')
                if gRemovalSignal&0b010: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = 'MMACD_SIGNAL')
                if gRemovalSignal&0b100: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = 'MMACD_HISTOGRAM')

        #---[3-15]: DMIxADX
        elif analysisType == 'DMIxADX':
            sivIdx = self.siTypes_siViewerAlloc['DMIxADX']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b1: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-16]: MFI
        elif analysisType == 'MFI':
            sivIdx = self.siTypes_siViewerAlloc['MFI']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b1: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-17]: TPD
        elif analysisType == 'TPD':
            sivIdx = self.siTypes_siViewerAlloc['TPD']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b1: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-19]: WOI
        elif analysisType == 'WOI':
            sivIdx = self.siTypes_siViewerAlloc['WOI']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b1: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = analysisCode)

        #---[3-20]: NES
        elif analysisType == 'NES':
            sivIdx = self.siTypes_siViewerAlloc['NES']
            if sivIdx is not None:
                sivCode = f"SIVIEWER{sivIdx}"
                if gRemovalSignal&0b1: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = analysisCode)

"""

def cd_get_vertical_magnitude_anchor(object_configuration):
    return None

"""
#[2-1-4]: NNA
elif siAlloc == 'NNA':
    anchor = 'CENTER'

#[2-1-5]: MMACD
elif siAlloc == 'MMACD':
    if oc['MMACD_HISTOGRAM_Type'] == 'MSDELTA_ABSMA' and not oc[f"MMACD_MMACD_Display"] and not oc[f"MMACD_SIGNAL_Display"]:
        anchor = 'BOTTOM'
    else:
        anchor = 'CENTER'

#[2-1-6]: DMIxADX
elif siAlloc == 'DMIxADX':
    dispType = oc['DMIxADX_DisplayType']
    if   dispType == 'DMIxADX':          anchor = 'CENTER'
    elif dispType == 'DMIxADX_ABSMA':    anchor = 'BOTTOM'
    elif dispType == 'DMIxADX_ABSMAREL': anchor = 'CENTER'

#[2-1-7]: MFI
elif siAlloc == 'MFI':
    dispType = oc['MFI_DisplayType']
    if   dispType == 'MFI':             anchor = 'CENTER'
    elif dispType == 'MFI_DEVABSMA':    anchor = 'BOTTOM'
    elif dispType == 'MFI_DEVABSMAREL': anchor = 'CENTER'

#[2-1-8]: TPD
elif siAlloc == 'TPD':
    dispType = oc['TPD_DisplayType']
    if   dispType == 'TPD':          anchor = 'CENTER'
    elif dispType == 'TPD_ABSMA':    anchor = 'BOTTOM'
    elif dispType == 'TPD_ABSMAREL': anchor = 'CENTER'

#[2-1-9]: WOI
elif siAlloc == 'WOI':
    dispType = oc['WOI_DisplayType']
    if   dispType == 'WOI':          anchor = 'CENTER'
    elif dispType == 'WOI_ABSMA':    anchor = 'BOTTOM'
    elif dispType == 'WOI_ABSMAREL': anchor = 'CENTER'

#[2-1-10]: NES
elif siAlloc == 'NES':
    dispType = oc['NES_DisplayType']
    if   dispType == 'NES':          anchor = 'CENTER'
    elif dispType == 'NES_ABSMA':    anchor = 'BOTTOM'
    elif dispType == 'NES_ABSMAREL': anchor = 'CENTER'
"""

def cd_on_GUI_theme_update(subpage, object_configuration, current_GUI_theme):
    #[1]: Instances
    sp  = subpage
    oc  = object_configuration
    cgt = current_GUI_theme

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        sp.GUIOs[f"INDICATOR_SMA{lIdx}_LINECOLOR"].updateColor(oc[f'SMA_{lIdx}_ColorR%{cgt}'], 
                                                               oc[f'SMA_{lIdx}_ColorG%{cgt}'], 
                                                               oc[f'SMA_{lIdx}_ColorB%{cgt}'], 
                                                               oc[f'SMA_{lIdx}_ColorA%{cgt}'])

"""
#---[8-6]: IVP
ssps['IVP'].GUIOs["INDICATOR_VPLP_COLOR"].updateColor(oc[f'IVP_VPLP_ColorR%{cgt}'],
                                                        oc[f'IVP_VPLP_ColorG%{cgt}'],
                                                        oc[f'IVP_VPLP_ColorB%{cgt}'],
                                                        oc[f'IVP_VPLP_ColorA%{cgt}'])
ssps['IVP'].GUIOs["INDICATOR_VPLPB_COLOR"].updateColor(oc[f'IVP_VPLPB_ColorR%{cgt}'],
                                                        oc[f'IVP_VPLPB_ColorG%{cgt}'],
                                                        oc[f'IVP_VPLPB_ColorB%{cgt}'],
                                                        oc[f'IVP_VPLPB_ColorA%{cgt}'])
self.__onSettingsContentUpdate(ssps['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
#---[8-8]: MMACD
for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
    ssps['MMACD'].GUIOs[f"INDICATOR_{targetLine}_COLOR"].updateColor(oc[f'MMACD_{targetLine}_ColorR%{cgt}'], 
                                                                        oc[f'MMACD_{targetLine}_ColorG%{cgt}'], 
                                                                        oc[f'MMACD_{targetLine}_ColorB%{cgt}'], 
                                                                        oc[f'MMACD_{targetLine}_ColorA%{cgt}'])
self.__onSettingsContentUpdate(ssps['MMACD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
#---[8-9]: DMIxADX
for lineIndex in range (_NMAXLINES['DMIxADX']):
    ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_LINECOLOR"].updateColor(oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'], 
                                                                                    oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'], 
                                                                                    oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'], 
                                                                                    oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'])
self.__onSettingsContentUpdate(ssps['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
#---[8-10]: MFI
for lineIndex in range (_NMAXLINES['MFI']):
    ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_LINECOLOR"].updateColor(oc[f'MFI_{lineIndex}_ColorR%{cgt}'], 
                                                                            oc[f'MFI_{lineIndex}_ColorG%{cgt}'], 
                                                                            oc[f'MFI_{lineIndex}_ColorB%{cgt}'], 
                                                                            oc[f'MFI_{lineIndex}_ColorA%{cgt}'])
self.__onSettingsContentUpdate(ssps['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
#---[8-11]: TPD
for lineIndex in range (_NMAXLINES['TPD']):
    ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_LINECOLOR"].updateColor(oc[f'TPD_{lineIndex}_ColorR%{cgt}'], 
                                                                            oc[f'TPD_{lineIndex}_ColorG%{cgt}'], 
                                                                            oc[f'TPD_{lineIndex}_ColorB%{cgt}'], 
                                                                            oc[f'TPD_{lineIndex}_ColorA%{cgt}'])
self.__onSettingsContentUpdate(ssps['TPD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
"""


def cd_update_si_type_analysis_codes(analysis_parameters):
    return None

"""
aParams_iID = self.analysisParams.get(self.intervalID)
if aParams_iID is not None:
    if 'MMACD' in aParams_iID: sit_aCodes['MMACD'].add('MMACD')
    for aCode in aParams_iID:
        if   aCode.startswith('VOL'):     sit_aCodes['VOL'].add(aCode)
        elif aCode.startswith('NNA'):     sit_aCodes['NNA'].add(aCode)
        elif aCode.startswith('DMIxADX'): sit_aCodes['DMIxADX'].add(aCode)
        elif aCode.startswith('MFI'):     sit_aCodes['MFI'].add(aCode)
        elif aCode.startswith('TPD'):     sit_aCodes['TPD'].add(aCode)
        elif aCode.startswith('WOI'):     sit_aCodes['WOI'].add(aCode)
        elif aCode.startswith('NES'):     sit_aCodes['NES'].add(aCode)
"""

def cd_type_init(subPage):
    #[1]: Instances
    guios_THIS = subPage.GUIOs

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        guios_THIS[f"INDICATOR_SMA{lIdx}"].deactivate()
        guios_THIS[f"INDICATOR_SMA{lIdx}_INTERVALINPUT"].deactivate()

    """
    #SMA
    for lineIndex in range (_NMAXLINES['SMA']):
        guios_SMA[f"INDICATOR_SMA{lineIndex}"].deactivate()
        guios_SMA[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].deactivate()

    #WMA
    for lineIndex in range (_NMAXLINES['WMA']):
        guios_WMA[f"INDICATOR_WMA{lineIndex}"].deactivate()
        guios_WMA[f"INDICATOR_WMA{lineIndex}_INTERVALINPUT"].deactivate()

    #EMA
    for lineIndex in range (_NMAXLINES['EMA']):
        guios_EMA[f"INDICATOR_EMA{lineIndex}"].deactivate()
        guios_EMA[f"INDICATOR_EMA{lineIndex}_INTERVALINPUT"].deactivate()

    #PSAR
    for lineIndex in range (_NMAXLINES['PSAR']):
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}"].deactivate()
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF0INPUT"].deactivate()
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF+INPUT"].deactivate()
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT"].deactivate()

    #BOL
    guios_BOL["INDICATOR_MATYPESELECTION"].deactivate()
    for lineIndex in range (_NMAXLINES['BOL']):
        guios_BOL[f"INDICATOR_BOL{lineIndex}"].deactivate()
        guios_BOL[f"INDICATOR_BOL{lineIndex}_INTERVALINPUT"].deactivate()
        guios_BOL[f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT"].deactivate()

    #IVP
    guios_IVP["INDICATOR_INTERVAL_INPUTTEXT"].deactivate()
    guios_IVP["INDICATOR_GAMMAFACTOR_SLIDER"].deactivate()
    guios_IVP["INDICATOR_DELTAFACTOR_SLIDER"].deactivate()

    #SWING
    for lineIndex in range (_NMAXLINES['SWING']):
        guios_SWING[f"INDICATOR_SWING{lineIndex}"].deactivate()
        guios_SWING[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].deactivate()

    #VOL
    guios_VOL["INDICATOR_MATYPESELECTION"].deactivate()
    for lineIndex in range (_NMAXLINES['VOL']):
        guios_VOL[f"INDICATOR_VOL{lineIndex}"].deactivate()
        guios_VOL[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].deactivate()

    #NNA
    for lineIndex in range (_NMAXLINES['NNA']):
        guios_NNA[f"INDICATOR_NNA{lineIndex}"].deactivate()
        guios_NNA[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].deactivate()
        guios_NNA[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].deactivate()
        guios_NNA[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].deactivate()

    #MMACD
    guios_MMACD["INDICATOR_SIGNALINTERVALTEXTINPUT"].deactivate()
    for lineIndex in range (_NMAXLINES['MMACD']):
        guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}"].deactivate()
        guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].deactivate()

    #DMIxADX
    for lineIndex in range (_NMAXLINES['DMIxADX']):
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}"].deactivate()
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].deactivate()

    #MFI
    for lineIndex in range (_NMAXLINES['MFI']):
        guios_MFI[f"INDICATOR_MFI{lineIndex}"].deactivate()
        guios_MFI[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].deactivate()

    #TPD
    for lineIndex in range (_NMAXLINES['TPD']):
        guios_TPD[f"INDICATOR_TPD{lineIndex}"].deactivate()
        guios_TPD[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].deactivate()
        guios_TPD[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].deactivate()
        guios_TPD[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].deactivate()

    #WOI
    for lineIndex in range (_NMAXLINES['WOI']):
        guios_WOI[f"INDICATOR_WOI{lineIndex}"].deactivate()
        guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].deactivate()

    #NES
    for lineIndex in range (_NMAXLINES['NES']):
        guios_NES[f"INDICATOR_NES{lineIndex}"].deactivate()
        guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].deactivate()
    """
#CHART DRAWER FUNCTIONS END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUTOTRADE PAGE FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_autotrade_get_default_analysis_configuration():
    #[1]: Default Analysis Configuration
    dac = dict()

    #[2]: Setup
    dac['SMA_Master'] = False
    for lIdx in range (NMAXLINES):
        dac[f'SMA_{lIdx}_LineActive'] = False
        dac[f'SMA_{lIdx}_NSamples']   = 10*(lIdx+1)

    #[3]: Return
    return dac

"""
#IVP
ac_def['IVP_Master'] = False
ac_def['IVP_NSamples']    = 500
ac_def['IVP_GammaFactor'] = 0.010
ac_def['IVP_DeltaFactor'] = 1.0
ac_def['IVP_Prominence']  = 0.10
ac_def['IVP_Distance']    = 5
ac_def['IVP_Height']      = 0.50
#SWING
ac_def['SWING_Master'] = False
for lineIndex in range (constants.NLINES_SWING):
    ac_def[f'SWING_{lineIndex}_LineActive'] = False
    ac_def[f'SWING_{lineIndex}_SwingRange'] = 0.005*(lineIndex+1)
#NNA
ac_def['NNA_Master'] = False
for lineIndex in range (constants.NLINES_NNA):
    ac_def[f'NNA_{lineIndex}_LineActive'] = False
    ac_def[f'NNA_{lineIndex}_NeuralNetworkCode'] = None
    ac_def[f'NNA_{lineIndex}_Alpha']             = 0.50
    ac_def[f'NNA_{lineIndex}_Beta']              = 2
#MMACD
ac_def['MMACD_Master'] = False
ac_def['MMACD_SignalNSamples'] = 10
for lineIndex in range (constants.NLINES_MMACD):
    ac_def[f'MMACD_MA{lineIndex}_LineActive'] = False
    ac_def[f'MMACD_MA{lineIndex}_NSamples']   = 20*(lineIndex+1)
#DMIxADX
ac_def['DMIxADX_Master'] = False
for lineIndex in range (constants.NLINES_DMIxADX):
    ac_def[f'DMIxADX_{lineIndex}_LineActive'] = False
    ac_def[f'DMIxADX_{lineIndex}_NSamples']   = 10*(lineIndex+1)
#MFI
ac_def['MFI_Master'] = False
for lineIndex in range (constants.NLINES_MFI):
    ac_def[f'MFI_{lineIndex}_LineActive'] = False
    ac_def[f'MFI_{lineIndex}_NSamples']   = 10*(lineIndex+1)
#TPD
ac_def['TPD_Master'] = False
for lineIndex in range (constants.NLINES_TPD):
    ac_def[f'TPD_{lineIndex}_LineActive'] = False
    ac_def[f'TPD_{lineIndex}_ViewLength'] = 10 *(lineIndex+1)
    ac_def[f'TPD_{lineIndex}_NSamples']   = 100*(lineIndex+1)
    ac_def[f'TPD_{lineIndex}_NSamplesMA'] = 20 *(lineIndex+1)
#WOI
ac_def['WOI_Master'] = False
for lineIndex in range (constants.NLINES_WOI):
    ac_def[f'WOI_{lineIndex}_LineActive'] = False
    ac_def[f'WOI_{lineIndex}_NSamples']   = 10*(lineIndex+1)
#NES
ac_def['NES_Master'] = False
for lineIndex in range (constants.NLINES_NES):
    ac_def[f'NES_{lineIndex}_LineActive'] = False
    ac_def[f'NES_{lineIndex}_NSamples']   = 10*(lineIndex+1)
"""


def pg_autotrade_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'COLUMNTITLE_INDEX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2325, 'yPos': -300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"SMA_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'SMA {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"SMA_{lIdx}_NSAMPLES",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2225, 'height': 250, 'style': 'styleA', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_autotrade_configure_subpage_setup(subpage, fn_get_text_pack):
    pass
      
"""
if (True): #Configuration/IVP
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_IVPSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("NSAMPLESTITLETEXT",             textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("NSAMPLESTEXTINPUTBOX",          textInputBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': yPosPoint0- 350, 'width': 2450, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("GAMMAFACTORTITLETEXT",          textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 700, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_GAMMAFACTOR'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("GAMMAFACTORSLIDER",             slider_typeA,       {'groupOrder': 0, 'xPos': 1400, 'yPos': yPosPoint0- 650, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_GammaFactor', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
    self.GUIOs[_objName].addGUIO("GAMMAFACTORDISPLAYTEXT",        textBox_typeA,      {'groupOrder': 0, 'xPos': 3950, 'yPos': yPosPoint0- 700, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("DELTAFACTORTITLETEXT",          textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1050, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_DELTAFACTOR'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("DELTAFACTORSLIDER",             slider_typeA,       {'groupOrder': 0, 'xPos': 1400, 'yPos': yPosPoint0-1000, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_DeltaFactor', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
    self.GUIOs[_objName].addGUIO("DELTAFACTORDISPLAYTEXT",        textBox_typeA,      {'groupOrder': 0, 'xPos': 3950, 'yPos': yPosPoint0-1050, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("PROMINENCETITLETEXT",           textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1400, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_PROMINENCE'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("PROMINENCESLIDER",              slider_typeA,       {'groupOrder': 0, 'xPos': 1400, 'yPos': yPosPoint0-1350, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_Prominence', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
    self.GUIOs[_objName].addGUIO("PROMINENCEDISPLAYTEXT",         textBox_typeA,      {'groupOrder': 0, 'xPos': 3950, 'yPos': yPosPoint0-1400, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("DISTANCETITLETEXT",             textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1750, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_DISTANCE'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("DISTANCESLIDER",                slider_typeA,       {'groupOrder': 0, 'xPos': 1400, 'yPos': yPosPoint0-1700, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_Distance', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
    self.GUIOs[_objName].addGUIO("DISTANCEDISPLAYTEXT",           textBox_typeA,      {'groupOrder': 0, 'xPos': 3950, 'yPos': yPosPoint0-1750, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("HEIGHTTITLETEXT",               textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-2100, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_HEIGHT'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("HEIGHTSLIDER",                  slider_typeA,       {'groupOrder': 0, 'xPos': 1400, 'yPos': yPosPoint0-2050, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_Height', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
    self.GUIOs[_objName].addGUIO("HEIGHTDISPLAYTEXT",             textBox_typeA,      {'groupOrder': 0, 'xPos': 3950, 'yPos': yPosPoint0-2100, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    yPosPoint1 = yPosPoint0-2450
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/SWING
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SWING"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",        passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0,     'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_SWINGSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),      'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_SWINGRANGE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1350, 'yPos': yPosPoint0-300, 'width': 3200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_SWINGRANGE'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_SWING):
        self.GUIOs[_objName].addGUIO(f"SWING_{lineIndex}_LINE",       switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'SWING {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"SWING_{lineIndex}_SWINGRANGE", textInputBox_typeA, {'groupOrder': 0, 'xPos': 1350, 'yPos': yPosPoint1-350*lineIndex, 'width': 3200, 'height': 250, 'style': 'styleA', 'text': "",                   'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_SWING
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/NNA
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_NNASETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",  passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),             'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NNCODE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint0-300, 'width': 2250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NEURALNETWORKCODE'), 'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_ALPHA",  passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3450, 'yPos': yPosPoint0-300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_ALPHA'),             'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_BETA",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 4050, 'yPos': yPosPoint0-300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_BETA'),              'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_NNA):
        self.GUIOs[_objName].addGUIO(f"NNA_{lineIndex}_LINE",   switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'NNA {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"NNA_{lineIndex}_NNCODE", textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint1-350*lineIndex, 'width': 2250, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"NNA_{lineIndex}_ALPHA",  textInputBox_typeA, {'groupOrder': 0, 'xPos': 3450, 'yPos': yPosPoint1-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"NNA_{lineIndex}_BETA",   textInputBox_typeA, {'groupOrder': 0, 'xPos': 4050, 'yPos': yPosPoint1-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_NNA
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/MMACD
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_MMACDSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("MMACDSIGNALINTERVALTITLETEXT",    textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-350, 'width': 3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_MMACDSIGNALINTERVAL'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("MMACDSIGNALINTERVALTEXTINPUTBOX", textInputBox_typeA, {'groupOrder': 0, 'xPos': 3100, 'yPos': yPosPoint0-350, 'width': 1450, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("INDEX_COLUMNTITLE1",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-700, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("NSAMPLES_COLUMNTITLE1", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint0-700, 'width': 1125, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("INDEX_COLUMNTITLE2",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-700, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("NSAMPLES_COLUMNTITLE2", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3425, 'yPos': yPosPoint0-700, 'width': 1125, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    nMaxLines = constants.NLINES_MMACD
    for lineIndex in range (nMaxLines):
        rowNumber = math.ceil((lineIndex+1)/2)
        if (lineIndex%2 == 0): coordX = 0
        else:                  coordX = 2325
        self.GUIOs[_objName].addGUIO(f"MA{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos': coordX,      'yPos': yPosPoint0-700-rowNumber*350, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'MA {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"MA{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': coordX+1100, 'yPos': yPosPoint0-700-rowNumber*350, 'width': 1125, 'height': 250, 'style': 'styleA', 'text': "",                  'fontSize': 80})
    yPosPoint1 = yPosPoint0-700-math.ceil(nMaxLines/2)*350
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/DMIxADX
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_DMIxADXSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_DMIxADX):
        self.GUIOs[_objName].addGUIO(f"DMIxADX_{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'DMIxADX {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"DMIxADX_{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                       'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_DMIxADX
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/MFI
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_MFISETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_MFI):
        self.GUIOs[_objName].addGUIO(f"MFI_{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'MFI {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"MFI_{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                   'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_MFI
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/TPD
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",        passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_TPDSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),      'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_VIEWLENGTH", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint0-300, 'width':  800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_VIEWLENGTH'), 'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2000, 'yPos': yPosPoint0-300, 'width': 1225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'),   'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLESMA", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3325, 'yPos': yPosPoint0-300, 'width': 1225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLESMA'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_TPD):
        self.GUIOs[_objName].addGUIO(f"TPD_{lineIndex}_LINE",       switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'TPD {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"TPD_{lineIndex}_VIEWLENGTH", textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint1-350*lineIndex, 'width':  800, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"TPD_{lineIndex}_NSAMPLES",   textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': yPosPoint1-350*lineIndex, 'width': 1225, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"TPD_{lineIndex}_NSAMPLESMA", textInputBox_typeA, {'groupOrder': 0, 'xPos': 3325, 'yPos': yPosPoint1-350*lineIndex, 'width': 1225, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_TPD
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/WOI
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_WOISETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_WOI):
        self.GUIOs[_objName].addGUIO(f"WOI_{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'WOI {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"WOI_{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_WOI
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/NES
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_NESSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_NES):
        self.GUIOs[_objName].addGUIO(f"NES_{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'NES {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"NES_{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_NES
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
"""



def pg_autotrade_load_analysis_configuration(mainPage, subPage, analysis_configuration):
    #[1]: Main Page
    mainPage.GUIOs["INDICATORMASTERSWITCH_SMA"].setStatus(status = analysis_configuration['SMA_Master'], callStatusUpdateFunction = False)

    #[2]: Sub Page
    for lIdx in range (NMAXLINES):
        #[2-1]: Configuration Retrieval
        if f'SMA_{lIdx}_LineActive' in analysis_configuration:
            lineActive = analysis_configuration[f'SMA_{lIdx}_LineActive']
            nSamples   = analysis_configuration[f'SMA_{lIdx}_NSamples']
        else:
            lineActive = False
            nSamples   = 10*(lIdx+1)

        #[2-2]: GUIOs Update
        subPage.GUIOs[f"SMA_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        subPage.GUIOs[f"SMA_{lIdx}_NSAMPLES"].updateText(text = f"{nSamples}")

"""
#MAIN
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_IVP"].setStatus(status      = configuration['IVP_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_SWING"].setStatus(status    = configuration['SWING_Master'],   callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_NNA"].setStatus(status      = configuration['NNA_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MMACD"].setStatus(status    = configuration['MMACD_Master'],   callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_DMIxADX"].setStatus(status  = configuration['DMIxADX_Master'], callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MFI"].setStatus(status      = configuration['MFI_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_TPD"].setStatus(status      = configuration['TPD_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_WOI"].setStatus(status      = configuration['WOI_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_NES"].setStatus(status      = configuration['NES_Master'],     callStatusUpdateFunction = False)

#IVP
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["NSAMPLESTEXTINPUTBOX"].updateText(text = str(configuration['IVP_NSamples']))
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["GAMMAFACTORSLIDER"].setSliderValue(newValue = (configuration['IVP_GammaFactor']-0.005)*(100/0.095))
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["GAMMAFACTORDISPLAYTEXT"].updateText(text = f"{configuration['IVP_GammaFactor']*100:.1f} %")
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DELTAFACTORSLIDER"].setSliderValue(newValue = (configuration['IVP_DeltaFactor']-0.1)*(100/9.9))
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DELTAFACTORDISPLAYTEXT"].updateText(text = f"{int(configuration['IVP_DeltaFactor']*100)} %")
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["PROMINENCESLIDER"].setSliderValue(newValue = (configuration['IVP_Prominence']-0.01)*(100/0.99))
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["PROMINENCEDISPLAYTEXT"].updateText(text = f"{int(configuration['IVP_Prominence']*100)} %")
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DISTANCESLIDER"].setSliderValue(newValue = (configuration['IVP_Distance']-1)*(100/99))
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DISTANCEDISPLAYTEXT"].updateText(text = f"{int(configuration['IVP_Distance'])}")
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["HEIGHTSLIDER"].setSliderValue(newValue = configuration['IVP_Height']*100)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["HEIGHTDISPLAYTEXT"].updateText(text = f"{int(configuration['IVP_Height']*100)} %")
#SWING
for lineIndex in range (constants.NLINES_SWING):
    if f'SWING_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'SWING_{lineIndex}_LineActive']
        swingRange = configuration[f'SWING_{lineIndex}_SwingRange']
    else:
        lineActive = False
        swingRange = 0.005*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SWING"].GUIOs[f"SWING_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SWING"].GUIOs[f"SWING_{lineIndex}_SWINGRANGE"].updateText(text = f"{swingRange:.4f}")
#NNA
for lineIndex in range (constants.NLINES_NNA):
    if f'NNA_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'NNA_{lineIndex}_LineActive']
        nnCode     = configuration[f'NNA_{lineIndex}_NeuralNetworkCode']
        alpha      = configuration[f'NNA_{lineIndex}_Alpha']
        beta       = configuration[f'NNA_{lineIndex}_Beta']
    else:
        lineActive = False
        nnCode     = None
        alpha      = 0.50
        beta       = 2
    nnCode_str = "" if nnCode is None else f"{nnCode}"
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_LINE"].setStatus(status  = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_NNCODE"].updateText(text = nnCode_str)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_ALPHA"].updateText(text  = f"{alpha:.2f}")
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_BETA"].updateText(text   = f"{beta}")
#MMACD
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs["MMACDSIGNALINTERVALTEXTINPUTBOX"].updateText(text = "{:d}".format(configuration['MMACD_SignalNSamples']))
for lineIndex in range (constants.NLINES_MMACD):
    if f'MMACD_MA{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'MMACD_MA{lineIndex}_LineActive']
        nSamples   = configuration[f'MMACD_MA{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 20*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs[f"MA{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs[f"MA{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
#DMIxADX
for lineIndex in range (constants.NLINES_DMIxADX):
    if f'DMIxADX_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'DMIxADX_{lineIndex}_LineActive']
        nSamples   = configuration[f'DMIxADX_{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 10*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"].GUIOs[f"DMIxADX_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"].GUIOs[f"DMIxADX_{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
#MFI
for lineIndex in range (constants.NLINES_MFI):
    if f'MFI_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'MFI_{lineIndex}_LineActive']
        nSamples   = configuration[f'MFI_{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 10*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"].GUIOs[f"MFI_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"].GUIOs[f"MFI_{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
#TPD
for lineIndex in range (constants.NLINES_TPD):
    if f'TPD_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'TPD_{lineIndex}_LineActive']
        viewLength = configuration[f'TPD_{lineIndex}_ViewLength']
        nSamples   = configuration[f'TPD_{lineIndex}_NSamples']
        nSamplesMA = configuration[f'TPD_{lineIndex}_NSamplesMA']
    else:
        lineActive = False
        viewLength = 15  *(lineIndex+1)
        nSamples   = 1000*(lineIndex+1)
        nSamplesMA = 20  *(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_VIEWLENGTH"].updateText(text = f"{viewLength}")
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_NSAMPLES"].updateText(text   = f"{nSamples}")
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_NSAMPLESMA"].updateText(text = f"{nSamplesMA}")
#WOI
for lineIndex in range (constants.NLINES_WOI):
    if f'WOI_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'WOI_{lineIndex}_LineActive']
        nSamples   = configuration[f'WOI_{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 10*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs[f"WOI_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs[f"WOI_{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
#NES
for lineIndex in range (constants.NLINES_NES):
    if f'NES_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'NES_{lineIndex}_LineActive']
        nSamples   = configuration[f'NES_{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 10*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs[f"NES_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs[f"NES_{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
"""

def pg_autotrade_format_analysis_configuration_from_guios(mainPage, subPage):
    #[1]: Instances
    configuration = dict()

    #[2]: Configuration Construction
    configuration['SMA_Master'] = mainPage.GUIOs["INDICATORMASTERSWITCH_SMA"].getStatus()
    for lineIndex in range (NMAXLINES):
        configuration[f'SMA_{lineIndex}_LineActive'] = subPage.GUIOs[f"SMA_{lineIndex}_LINE"].getStatus()
        configuration[f'SMA_{lineIndex}_NSamples']   = int(subPage.GUIOs[f"SMA_{lineIndex}_NSAMPLES"].getText())

    #[3]: Return Configuration
    return configuration

"""
#IVP
configuration['IVP_Master']      = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_IVP"].getStatus()
configuration['IVP_NSamples']    = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["NSAMPLESTEXTINPUTBOX"].getText())
configuration['IVP_GammaFactor'] = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["GAMMAFACTORSLIDER"].getSliderValue()/100*(0.095)+0.005), 3)
configuration['IVP_DeltaFactor'] = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DELTAFACTORSLIDER"].getSliderValue()/100*(9.9)  +0.1),   1)
configuration['IVP_Prominence']  = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["PROMINENCESLIDER"].getSliderValue()/100*(0.99)  +0.01),  2)
configuration['IVP_Distance']    = int(round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DISTANCESLIDER"].getSliderValue()/100*(99)  +1)))
configuration['IVP_Height']      = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["HEIGHTSLIDER"].getSliderValue()/100), 2)
#SWING
configuration['SWING_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_SWING"].getStatus()
for lineIndex in range (constants.NLINES_SWING):
    configuration[f'SWING_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SWING"].GUIOs[f"SWING_{lineIndex}_LINE"].getStatus()
    configuration[f'SWING_{lineIndex}_SwingRange'] = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SWING"].GUIOs[f"SWING_{lineIndex}_SWINGRANGE"].getText()), 4)
#NNA
configuration['NNA_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_NNA"].getStatus()
for lineIndex in range (constants.NLINES_NNA):
    configuration[f'NNA_{lineIndex}_LineActive']        = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_LINE"].getStatus()
    nnCode_input = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_NNCODE"].getText().strip()
    configuration[f'NNA_{lineIndex}_NeuralNetworkCode'] = None if not nnCode_input else nnCode_input
    configuration[f'NNA_{lineIndex}_Alpha']             = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_ALPHA"].getText()), 2)
    configuration[f'NNA_{lineIndex}_Beta']              = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_BETA"].getText())
#MMACD
configuration['MMACD_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MMACD"].getStatus()
configuration['MMACD_SignalNSamples'] = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs["MMACDSIGNALINTERVALTEXTINPUTBOX"].getText())
for lineIndex in range (constants.NLINES_MMACD):
    configuration[f'MMACD_MA{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs[f"MA{lineIndex}_LINE"].getStatus()
    configuration[f'MMACD_MA{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs[f"MA{lineIndex}_NSAMPLES"].getText())
#DMIxADX
configuration['DMIxADX_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_DMIxADX"].getStatus()
for lineIndex in range (constants.NLINES_DMIxADX):
    configuration[f'DMIxADX_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"].GUIOs[f"DMIxADX_{lineIndex}_LINE"].getStatus()
    configuration[f'DMIxADX_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"].GUIOs[f"DMIxADX_{lineIndex}_NSAMPLES"].getText())
#MFI
configuration['MFI_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MFI"].getStatus()
for lineIndex in range (constants.NLINES_MFI):
    configuration[f'MFI_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"].GUIOs[f"MFI_{lineIndex}_LINE"].getStatus()
    configuration[f'MFI_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"].GUIOs[f"MFI_{lineIndex}_NSAMPLES"].getText())
#TPD
configuration['TPD_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_TPD"].getStatus()
for lineIndex in range (constants.NLINES_TPD):
    configuration[f'TPD_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_LINE"].getStatus()
    configuration[f'TPD_{lineIndex}_ViewLength'] = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_VIEWLENGTH"].getText())
    configuration[f'TPD_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_NSAMPLES"].getText())
    configuration[f'TPD_{lineIndex}_NSamplesMA'] = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_NSAMPLESMA"].getText())
#WOI
configuration['WOI_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_WOI"].getStatus()
for lineIndex in range (constants.NLINES_WOI):
    configuration[f'WOI_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs[f"WOI_{lineIndex}_LINE"].getStatus()
    configuration[f'WOI_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs[f"WOI_{lineIndex}_NSAMPLES"].getText())
#NES
configuration['NES_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_NES"].getStatus()
for lineIndex in range (constants.NLINES_NES):
    configuration[f'NES_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs[f"NES_{lineIndex}_LINE"].getStatus()
    configuration[f'NES_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs[f"NES_{lineIndex}_NSAMPLES"].getText())
"""
#AUTOTRADE PAGE FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SIMULATION RESULTS PAGE FUNCTIONS ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_simulation_result_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'COLUMNTITLE_INDEX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 0, 'yPos': -300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2625, 'yPos': -300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"SMA_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'SMA {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"SMA_{lIdx}_NSAMPLES",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2625, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2525, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_simulation_result_configure_subpage_setup(subpage, fn_get_text_pack):
    for lIdx in range (NMAXLINES):
        subpage.GUIOs[f"SMA_{lIdx}_LINE"].deactivate()

"""
if (True): #Configuration/IVP
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_IVP"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_IVPSETUP'), 'fontSize': 80})
    spo.addGUIO("NSAMPLESTITLETEXT",      textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0- 350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80})
    spo.addGUIO("NSAMPLESDISPLAYTEXT",    textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0- 350, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    spo.addGUIO("GAMMAFACTORTITLETEXT",   textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0- 700, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_GAMMAFACTOR'), 'fontSize': 80})
    spo.addGUIO("GAMMAFACTORDISPLAYTEXT", textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0- 700, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    spo.addGUIO("DELTAFACTORTITLETEXT",   textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-1050, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_DELTAFACTOR'), 'fontSize': 80})
    spo.addGUIO("DELTAFACTORDISPLAYTEXT", textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0-1050, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    spo.addGUIO("PROMINENCETITLETEXT",    textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-1400, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_PROMINENCE'),  'fontSize': 80})
    spo.addGUIO("PROMINENCEDISPLAYTEXT",  textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0-1400, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    spo.addGUIO("DISTANCETITLETEXT",      textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-1750, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_DISTANCE'),    'fontSize': 80})
    spo.addGUIO("DISTANCEDISPLAYTEXT",    textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0-1750, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    spo.addGUIO("HEIGHTTITLETEXT",        textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-2100, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_HEIGHT'),      'fontSize': 80})
    spo.addGUIO("HEIGHTDISPLAYTEXT",      textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0-2100, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    _yPosPoint1 = _yPosPoint0-2450
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint1, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/SWING
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SWING"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",        passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0,     'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_SWINGSETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),      'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_SWINGRANGE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint0-300, 'width': 3800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_SWINGRANGE'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_SWING):
        spo.addGUIO(f"SWING_{lineIndex}_LINE",       switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'SWING {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"SWING_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"SWING_{lineIndex}_SWINGRANGE", textBox_typeA, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint1-350*lineIndex, 'width': 3800, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_SWING
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/NNA
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NNA"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",        passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_NNASETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),             'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_SWINGRANGE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint0-300, 'width': 2600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NEURALNETWORKCODE'), 'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_ALPHA",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 4050, 'yPos': _yPosPoint0-300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_ALPHA'),             'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_BETA",       passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 4650, 'yPos': _yPosPoint0-300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_BETA'),              'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_NNA):
        spo.addGUIO(f"NNA_{lineIndex}_LINE",   switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'NNA {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"NNA_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"NNA_{lineIndex}_NNCODE", textBox_typeA, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2600, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
        spo.addGUIO(f"NNA_{lineIndex}_ALPHA",  textBox_typeA, {'groupOrder': 0, 'xPos': 4050, 'yPos': _yPosPoint1-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
        spo.addGUIO(f"NNA_{lineIndex}_BETA",   textBox_typeA, {'groupOrder': 0, 'xPos': 4650, 'yPos': _yPosPoint1-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_NNA
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/MMACD
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MMACD"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_MMACDSETUP'), 'fontSize': 80})
    spo.addGUIO("MMACDSIGNALINTERVALTITLETEXT",   textBox_typeA,       {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-350, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MMACDSIGNALINTERVAL'), 'fontSize': 80})
    spo.addGUIO("MMACDSIGNALINTERVALDISPLAYTEXT", textBox_typeA,       {'groupOrder': 0, 'xPos': 3150, 'yPos': _yPosPoint0-350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                    'fontSize': 80})
    spo.addGUIO("INDEX_COLUMNTITLE1",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-700, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("NSAMPLES_COLUMNTITLE1", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1200, 'yPos': _yPosPoint0-700, 'width': 1325, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("INDEX_COLUMNTITLE2",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-700, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("NSAMPLES_COLUMNTITLE2", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3825, 'yPos': _yPosPoint0-700, 'width': 1325, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    _nMaxLines = constants.NLINES_MMACD
    for lineIndex in range (_nMaxLines):
        rowNumber = math.ceil((lineIndex+1)/2)
        if (lineIndex%2 == 0): coordX = 0
        else:                  coordX = 2625
        spo.addGUIO(f"MA{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos': coordX,      'yPos': _yPosPoint0-700-rowNumber*350, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': f'MA {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"MA{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"MA{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': coordX+1200, 'yPos': _yPosPoint0-700-rowNumber*350, 'width': 1325, 'height': 250, 'style': 'styleA', 'text': "-",                 'fontSize': 80})
    _yPosPoint1 = _yPosPoint0-700-math.ceil(_nMaxLines/2)*350
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint1-350, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/DMIxADX
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_DMIxADX"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_DMIxADXSETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_DMIxADX):
        spo.addGUIO(f"DMIxADX_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'DMIxADX {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"DMIxADX_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"DMIxADX_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                      'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_DMIxADX
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/MFI
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MFI"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_MFISETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_MFI):
        spo.addGUIO(f"MFI_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'MFI {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"MFI_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"MFI_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_MFI
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/TPD
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_TPD"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_TPDSETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_VIEWLENGTH", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': _yPosPoint0-300, 'width': 1050, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_VIEWLENGTH'), 'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2250, 'yPos': _yPosPoint0-300, 'width': 1400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'),   'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLESMA", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3750, 'yPos': _yPosPoint0-300, 'width': 1400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLESMA'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_TPD):
        spo.addGUIO(f"TPD_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'TPD {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"TPD_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"TPD_{lineIndex}_VIEWLENGTH", textBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
        spo.addGUIO(f"TPD_{lineIndex}_NSAMPLES",   textBox_typeA, {'groupOrder': 0, 'xPos': 2250, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1400, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
        spo.addGUIO(f"TPD_{lineIndex}_NSAMPLESMA", textBox_typeA, {'groupOrder': 0, 'xPos': 3750, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1400, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_TPD
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/WOI
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_WOI"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_WOISETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_WOI):
        spo.addGUIO(f"WOI_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'WOI {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"WOI_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"WOI_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_WOI
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/NES
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NES"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_NESSETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_NES):
        spo.addGUIO(f"NES_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'NES {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"NES_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"NES_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_NES
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
"""

def pg_simulation_result_load_analysis_configuration(mainPage, subPage, analysis_configuration, simulation_selected, fn_get_text_pack):
    if simulation_selected:
        mainPage.GUIOs["INDICATORMASTERSWITCH_SMA"].setStatus(status = analysis_configuration['SMA_Master'], callStatusUpdateFunction = False)
        for lIdx in range (NMAXLINES):
            lineActive = analysis_configuration.get(f'SMA_{lIdx}_LineActive', False)
            if lineActive: nSamples_str = f"{analysis_configuration[f'SMA_{lIdx}_NSamples']}"
            else:          nSamples_str = "-"
            subPage.GUIOs[f"SMA_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
            subPage.GUIOs[f"SMA_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    else:
        mainPage.GUIOs["INDICATORMASTERSWITCH_SMA"].setStatus(status = False, callStatusUpdateFunction = False)
        for lIdx in range (NMAXLINES):
            subPage.GUIOs[f"SMA_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
            subPage.GUIOs[f"SMA_{lIdx}_NSAMPLES"].updateText(text = "-")

"""
#---[2-1]: Simulation Not Selected
if any(val is None for val in (sim, cac, iID)):
    #MAIN
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MAIN"].GUIOs
    sp_GUIOs["INDICATORMASTERSWITCH_IVP"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_SWING"].setStatus(status   = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_NNA"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_MMACD"].setStatus(status   = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_DMIxADX"].setStatus(status = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_MFI"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_TPD"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_WOI"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_NES"].setStatus(status     = False, callStatusUpdateFunction = False)
    
    #IVP
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_IVP"].GUIOs
    sp_GUIOs["NSAMPLESDISPLAYTEXT"].updateText(text    = "-")
    sp_GUIOs["GAMMAFACTORDISPLAYTEXT"].updateText(text = "-")
    sp_GUIOs["DELTAFACTORDISPLAYTEXT"].updateText(text = "-")
    sp_GUIOs["PROMINENCEDISPLAYTEXT"].updateText(text  = "-")
    sp_GUIOs["DISTANCEDISPLAYTEXT"].updateText(text    = "-")
    sp_GUIOs["HEIGHTDISPLAYTEXT"].updateText(text      = "-")
    #SWING
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SWING"].GUIOs
    for lIdx in range (constants.NLINES_SWING):
        sp_GUIOs[f"SWING_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"SWING_{lIdx}_SWINGRANGE"].updateText(text = "-")
    #NNA
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NNA"].GUIOs
    for lIdx in range (constants.NLINES_NNA):
        sp_GUIOs[f"NNA_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"NNA_{lIdx}_NNCODE"].updateText(text = "-")
        sp_GUIOs[f"NNA_{lIdx}_ALPHA"].updateText(text  = "-")
        sp_GUIOs[f"NNA_{lIdx}_BETA"].updateText(text   = "-")
    #MMACD
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MMACD"].GUIOs
    sp_GUIOs["MMACDSIGNALINTERVALDISPLAYTEXT"].updateText(text = "-")
    for lIdx in range (constants.NLINES_MMACD):
        sp_GUIOs[f"MA{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"MA{lIdx}_NSAMPLES"].updateText(text = "-")
    #DMIxADX
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_DMIxADX"].GUIOs
    for lIdx in range (constants.NLINES_DMIxADX):
        sp_GUIOs[f"DMIxADX_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"DMIxADX_{lIdx}_NSAMPLES"].updateText(text = "-")
    #MFI
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MFI"].GUIOs
    for lIdx in range (constants.NLINES_MFI):
        sp_GUIOs[f"MFI_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"MFI_{lIdx}_NSAMPLES"].updateText(text = "-")
    #TPD
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_TPD"].GUIOs
    for lIdx in range (constants.NLINES_TPD):
        sp_GUIOs[f"TPD_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"TPD_{lIdx}_VIEWLENGTH"].updateText(text = "-")
        sp_GUIOs[f"TPD_{lIdx}_NSAMPLES"].updateText(text   = "-")
        sp_GUIOs[f"TPD_{lIdx}_NSAMPLESMA"].updateText(text = "-")
    #WOI
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_WOI"].GUIOs
    for lIdx in range (constants.NLINES_WOI):
        sp_GUIOs[f"WOI_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"WOI_{lIdx}_NSAMPLES"].updateText(text = "-")
    #NES
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NES"].GUIOs
    for lIdx in range (constants.NLINES_NES):
        sp_GUIOs[f"NES_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"NES_{lIdx}_NSAMPLES"].updateText(text = "-")

#---[2-2]: Simulation Selected
else:
    cac_iID = cac[iID]
    #MAIN
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MAIN"].GUIOs
    sp_GUIOs["INDICATORMASTERSWITCH_IVP"].setStatus(status     = cac_iID['IVP_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_SWING"].setStatus(status   = cac_iID['SWING_Master'],   callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_NNA"].setStatus(status     = cac_iID['NNA_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_MMACD"].setStatus(status   = cac_iID['MMACD_Master'],   callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_DMIxADX"].setStatus(status = cac_iID['DMIxADX_Master'], callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_MFI"].setStatus(status     = cac_iID['MFI_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_TPD"].setStatus(status     = cac_iID['TPD_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_WOI"].setStatus(status     = cac_iID['WOI_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_NES"].setStatus(status     = cac_iID['NES_Master'],     callStatusUpdateFunction = False)
    
    #IVP
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_IVP"].GUIOs
    sp_GUIOs["NSAMPLESDISPLAYTEXT"].updateText(text = f"{cac_iID['IVP_NSamples']}")
    sp_GUIOs["GAMMAFACTORDISPLAYTEXT"].updateText(text = f"{cac_iID['IVP_GammaFactor']*100:.1f} %")
    sp_GUIOs["DELTAFACTORDISPLAYTEXT"].updateText(text = f"{cac_iID['IVP_DeltaFactor']*100:.0f} %")
    sp_GUIOs["PROMINENCEDISPLAYTEXT"].updateText(text  = f"{cac_iID['IVP_Prominence']*100:.0f} %")
    sp_GUIOs["DISTANCEDISPLAYTEXT"].updateText(text    = f"{cac_iID['IVP_Distance']}")
    sp_GUIOs["HEIGHTDISPLAYTEXT"].updateText(text      = f"{cac_iID['IVP_Height']*100:.0f} %")
    #SWING
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SWING"].GUIOs
    for lIdx in range (constants.NLINES_SWING):
        lineActive = cac_iID.get(f'SWING_{lIdx}_LineActive', False)
        if lineActive: 
            swingRange_str = f"{cac_iID[f'SWING_{lIdx}_SwingRange']:.4f}"
        else:          
            swingRange_str = "-"
        sp_GUIOs[f"SWING_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"SWING_{lIdx}_SWINGRANGE"].updateText(text = swingRange_str)
    #NNA
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NNA"].GUIOs
    for lIdx in range (constants.NLINES_NNA):
        lineActive = cac_iID.get(f'NNA_{lIdx}_LineActive', False)
        if lineActive: 
            nnCode = cac_iID[f'NNA_{lIdx}_NeuralNetworkCode']
            nnCode_str = "" if nnCode is None else f"{nnCode}"
            alpha_str  = f"{cac_iID[f'NNA_{lIdx}_Alpha']:.2f}"
            beta_str   = f"{cac_iID[f'NNA_{lIdx}_Beta']}"
        else:          
            nnCode_str = "-"
            alpha_str  = "-"
            beta_str   = "-"
        sp_GUIOs[f"NNA_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"NNA_{lIdx}_NNCODE"].updateText(text = nnCode_str)
        sp_GUIOs[f"NNA_{lIdx}_ALPHA"].updateText(text  = alpha_str)
        sp_GUIOs[f"NNA_{lIdx}_BETA"].updateText(text   = beta_str)
    #MMACD
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MMACD"].GUIOs
    signalNSamples = cac_iID['MMACD_SignalNSamples']
    sp_GUIOs["MMACDSIGNALINTERVALDISPLAYTEXT"].updateText(text = f"{signalNSamples}")
    for lIdx in range (constants.NLINES_MMACD):
        lineActive = cac_iID.get(f'MMACD_MA{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'MMACD_MA{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"MA{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"MA{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    #DMIxADX
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_DMIxADX"].GUIOs
    for lIdx in range (constants.NLINES_DMIxADX):
        lineActive = cac_iID.get(f'DMIxADX_{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'DMIxADX_{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"DMIxADX_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"DMIxADX_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    #MFI
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MFI"].GUIOs
    for lIdx in range (constants.NLINES_MFI):
        lineActive = cac_iID.get(f'MFI_{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'MFI_{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"MFI_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"MFI_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    #TPD
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_TPD"].GUIOs
    for lIdx in range (constants.NLINES_TPD):
        lineActive = cac_iID.get(f'TPD_{lIdx}_LineActive', False)
        if lineActive: 
            viewLength_str = f"{cac_iID[f'TPD_{lIdx}_ViewLength']}"
            nSamples_str   = f"{cac_iID[f'TPD_{lIdx}_NSamples']}"
            nSamplesMA_str = f"{cac_iID[f'TPD_{lIdx}_NSamplesMA']}"
        else:          
            viewLength_str = "-"
            nSamples_str   = "-"
            nSamplesMA_str = "-"
        sp_GUIOs[f"TPD_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"TPD_{lIdx}_VIEWLENGTH"].updateText(text = viewLength_str)
        sp_GUIOs[f"TPD_{lIdx}_NSAMPLES"].updateText(text   = nSamples_str)
        sp_GUIOs[f"TPD_{lIdx}_NSAMPLESMA"].updateText(text = nSamplesMA_str)
    #WOI
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_WOI"].GUIOs
    for lIdx in range (constants.NLINES_WOI):
        lineActive = cac_iID.get(f'WOI_{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'WOI_{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"WOI_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"WOI_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    #NES
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NES"].GUIOs
    for lIdx in range (constants.NLINES_NES):
        lineActive = cac_iID.get(f'NES_{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'NES_{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"NES_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"NES_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
"""
#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



"""
def __IVP_addPriceLevelProfile(priceLevelProfileWeight, priceLevelProfilePosition_low, priceLevelProfilePosition_high, priceLevelProfile, divisionHeight, pricePrecision, mode = True):
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

def analysisGenerator_IVP(intervalID, precisions, timestamp, klines, nSamples, gammaFactor, deltaFactor, prominence, distance, height, analysisResults, **_):
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
                    __IVP_addPriceLevelProfile(vb, lp, hp, vplp, divHeight, pPrecision)
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
                    __IVP_addPriceLevelProfile(vplp_prev[dIdx_prev], divPos_low_prev, divPos_high_prev, vplp, divHeight, pPrecision)

    #[5]: Volume Price Level Profile Update
    if vplp is not None and ivp_prev['volumePriceLevelProfile'] is not None:
        vplp = vplp*(1-1/nSamples) 
        vb   = kl_this[KLINDEX_VOLBASE]
        lp   = kl_this[KLINDEX_LOWPRICE]
        hp   = kl_this[KLINDEX_HIGHPRICE]
        if vb is not None and lp is not None and hp is not None:
            __IVP_addPriceLevelProfile(vb, lp, hp, vplp, divHeight, pPrecision)
        
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

def analysisGenerator_SWING(intervalID, timestamp, klines, swingRange, analysisResults, **_):
    #[1]: Instances
    kline      = klines[timestamp]
    swings     = analysisResults
    func_gnitt = auxiliaries.getNextIntervalTickTimestamp

    #[2]: Analysis counter
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    swing_prev     = swings.get(timestamp_prev, None)
    mode           = 0 if swing_prev is None else swing_prev['mode']

    #[3]: Swing Search
    #---[3-1]: Klines
    kl_hp = kline[KLINDEX_HIGHPRICE]
    kl_lp = kline[KLINDEX_LOWPRICE]

    #---[3-2]: Initialization
    if mode == 0:
        if kl_hp is None or kl_lp is None:
            swings_rec  = None
            swingSearch = None
            mode        = 0
        else:
            swings_rec  = deque(maxlen = 100)
            swingSearch = {'lastExtreme': True, 
                           'max':         kl_hp, 
                           'min':         kl_lp, 
                           'max_ts':      timestamp, 
                           'min_ts':      timestamp}
            mode = 1
        
    #---[3-3]: Swing Search
    else:
        #[3-3-1]: Previous Swings
        swings_rec  = swing_prev['SWINGS'].copy()
        swingSearch = swing_prev['SWINGSEARCH'].copy()

        #[3-3-2]: Swing Update Check
        if kl_hp is not None and kl_lp is not None:
            #[3-3-2-1]: Last Swing Was HIGH
            if swingSearch['lastExtreme']:
                #[3-3-2-1-1]: Update Min (Lowest Low)
                if kl_lp < swingSearch['min']: 
                    swingSearch['min']    = kl_lp
                    swingSearch['min_ts'] = timestamp
                #[3-3-2-1-2]: Check Reversal
                elif swingSearch['min']*(1+swingRange) < kl_hp:
                    newSwing = (swingSearch['min_ts'], swingSearch['min'], -1)
                    swings_rec.append(newSwing)
                    swingSearch['lastExtreme'] = False
                    swingSearch['max']         = kl_hp
                    swingSearch['max_ts']      = timestamp

            #[3-3-2-2]: Last Swing Was Low
            else:
                #[3-3-2-2-1]: Update Max (Highest High)
                if swingSearch['max'] < kl_hp: 
                    swingSearch['max']    = kl_hp
                    swingSearch['max_ts'] = timestamp
                #[3-3-2-2-2]: Check Reversal
                elif kl_lp < swingSearch['max']*(1-swingRange):
                    newSwing = (swingSearch['max_ts'], swingSearch['max'], 1)
                    swings_rec.append(newSwing)
                    swingSearch['lastExtreme'] = True
                    swingSearch['min']         = kl_lp
                    swingSearch['min_ts']      = timestamp

        #[3-3-3]: Mode
        mode = 1

    #[4]: Result Formatting & Save
    swingResult = {'SWINGS':      swings_rec, 
                   'SWINGSEARCH': swingSearch,
                   'mode':        mode}
    swings[timestamp] = swingResult

    #[5]: Memory Optimization References
    return (2, #nAnalysisToKeep
            2) #nKlinesToKeep

def analysisGenerator_NNA(intervalID, timestamp, klines, neuralNetworks, nnCode, alpha, beta, analysisResults, **_):
    #[1]: Instances
    nnas       = analysisResults
    func_gnitt = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl  = auxiliaries.getTimestampList_byNTicks

    #[2]: Analysis counter
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    nna_prev       = nnas.get(timestamp_prev, None)
    analysisCount  = 0 if nna_prev is None else nna_prev['analysisCount']+1
    
    #[3]: NNA
    nn  = neuralNetworks.get(nnCode, None)
    nna = None
    if nn is not None:
        nSamples = nn.getNKlines()
        if analysisCount < nSamples-1:
            nna = None
        else:
            kl0 = klines.get(func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -(nSamples-1)), None)
            #[2-1]: Invalid Input
            if (kl0 is None or 
                kl0[KLINDEX_OPENPRICE]       is None or
                kl0[KLINDEX_HIGHPRICE]       is None or
                kl0[KLINDEX_LOWPRICE]        is None or
                kl0[KLINDEX_CLOSEPRICE]      is None or
                kl0[KLINDEX_VOLBASE]         is None or
                kl0[KLINDEX_VOLBASETAKERBUY] is None
                ): 
                nna = 0
            #[2-2]: Valid Input
            else:
                #[2-2-1]: Input Tensor Construction
                values_raw = []
                cp_last    = None
                p_max      = None
                p_min      = None
                vol_max    = None
                volTB_max  = None
                for ts in reversed(func_gtsl(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False)):
                    kl = klines.get(ts, None)
                    if kl is None:
                        op   = cp_last
                        hp   = cp_last
                        lp   = cp_last
                        cp   = cp_last
                        vb   = 0
                        vbtb = 0
                    else:
                        op   = kl[KLINDEX_OPENPRICE]
                        hp   = kl[KLINDEX_HIGHPRICE]
                        lp   = kl[KLINDEX_LOWPRICE]
                        cp   = kl[KLINDEX_CLOSEPRICE]
                        vb   = kl[KLINDEX_VOLBASE]
                        vbtb = kl[KLINDEX_VOLBASETAKERBUY]
                    if cp is not None:
                        cp_last = cp
                    if op   is None: op   = cp_last
                    if hp   is None: hp   = cp_last
                    if lp   is None: lp   = cp_last
                    if cp   is None: cp   = cp_last
                    if vb   is None: vb   = 0
                    if vbtb is None: vbtb = 0
                    if p_max     is None or p_max     < hp:    p_max     = hp
                    if p_min     is None or lp        < p_min: p_min     = lp
                    if vol_max   is None or vol_max   < vb:    vol_max   = vb
                    if volTB_max is None or volTB_max < vbtb:  volTB_max = vbtb
                    values_raw.append((op, hp, lp, cp, vb, vbtb))
                p_range = p_max-p_min
                iTensor_2d = torch.tensor(data = values_raw, dtype = torch.float32, device = 'cpu', requires_grad = False)
                if p_range != 0.0:   iTensor_2d[:, 0:4] = (iTensor_2d[:, 0:4] - p_min) / p_range
                else:                iTensor_2d[:, 0:4] = 0.5
                if vol_max != 0.0:   iTensor_2d[:, 4]   /= vol_max
                else:                iTensor_2d[:, 4]   = 0.0
                if volTB_max != 0.0: iTensor_2d[:, 5]   /= volTB_max
                else:                iTensor_2d[:, 5]   = 0.0
                iTensor_flat = iTensor_2d.flatten()

                #[2-2-2]: Forwarding
                nn_out = float(nn.forward(inputData = iTensor_flat)[0])*2-1
                nna    = abs(round(math.atan(pow(nn_out/alpha, beta))*2/math.pi, 5))
                if 0 <= nn_out: nna =  nna
                else:           nna = -nna

    #[4]: Result formatting & saving
    nnaResult = {'NNA':           nna,
                 'analysisCount': analysisCount}
    nnas[timestamp] = nnaResult

    #[5]: Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    if nn is None: return (2, 2)
    else:          return (nSamples, nSamples)

def analysisGenerator_MMACD(intervalID, precisions, timestamp, klines, signal_nSamples, activatedMAs, activatedMAPairs, maxMANSamples, analysisResults, **_):
    #[1]: Instances
    mmacds            = analysisResults
    kline             = klines[timestamp]
    signal_kValue     = 2/(signal_nSamples+1)
    absoluteMA_kValue = 2/(maxMANSamples+1)
    pPrecision        = precisions['price']
    func_gnitt        = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl         = auxiliaries.getTimestampList_byNTicks

    #[2]: Analysis counter
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    mmacd_prev     = mmacds.get(timestamp_prev, None)
    analysisCount  = 0 if mmacd_prev is None else mmacd_prev['analysisCount']+1

    #[3]: MMACD Computation
    #---[3-1]: MAs Generation
    mas_prev = None if mmacd_prev is None else mmacd_prev['MAs']
    mas      = {}
    for ma_nSamples in activatedMAs:
        #[3-1-1]: Mode & K-Value
        ma_mode   = 0 if mas_prev is None else mas_prev[ma_nSamples]['mode']
        ma_kValue = 2/(ma_nSamples+1)

        #[3-1-2]: Computation
        if ma_mode == 0:
            prices = [klines[ts][KLINDEX_CLOSEPRICE] if ts in klines else None
                      for ts in func_gtsl(intervalID = intervalID,
                                          timestamp  = timestamp,
                                          nTicks     = ma_nSamples,
                                          direction  = False)]
            if any(p is None for p in prices):
                if mas_prev is None:
                    ma_ma   = None
                    ma_mode = 0
                else:
                    ma_ma   = mas_prev[ma_nSamples]['MA']
                    ma_mode = 0
            else:
                priceSum = sum(prices)
                ma_ma    = round(priceSum / ma_nSamples, pPrecision)
                ma_mode  = 1
        elif ma_mode == 1:
            ma_ma_prev = mas_prev[ma_nSamples]['MA']
            price_this = kline[KLINDEX_CLOSEPRICE]
            if price_this is None:
                ma_ma   = ma_ma_prev
                ma_mode = 1
            else:
                ma_ma   = round((price_this*ma_kValue) + (ma_ma_prev*(1-ma_kValue)), pPrecision)
                ma_mode = 1
        mas[ma_nSamples] = {'MA':   ma_ma,
                            'mode': ma_mode}

    #---[3-2]: MA Pair Delta Sum & MMACD
    if analysisCount < (maxMANSamples-1): 
        mmacd = None
    else:
        if any(mas[ma0]['MA'] is None or mas[ma1]['MA'] is None for ma0, ma1 in activatedMAPairs):
            mmacd = None
        else:
            mmacd = sum(mas[ma0]['MA']-mas[ma1]['MA'] for ma0, ma1 in activatedMAPairs)

    #---[3-3]: Signal
    if analysisCount < (maxMANSamples+signal_nSamples-1): 
        signal = None
    else:
        signal_prev = mmacd_prev['SIGNAL']
        if signal_prev is None:
            signal = mmacd
        else:
            signal = (mmacd*signal_kValue) + (signal_prev*(1-signal_kValue))

    #---[3-4]: MSDelta
    if signal is None:
        msDelta = None
    else:
        msDelta = mmacd-signal

    #---[3-5]: MSDelta Absolute MA
    if msDelta is None: 
        msDelta_AbsMA = None
    else:
        msDelta_prev = mmacd_prev['MSDELTA']
        if msDelta_prev is None: 
            msDelta_AbsMA = None
        else:
            msDelta_AbsMA_prev = mmacd_prev['MSDELTA_ABSMA']
            if msDelta_AbsMA_prev is None: msDelta_AbsMA = abs(msDelta)*absoluteMA_kValue + abs(msDelta_prev) *(1-absoluteMA_kValue)
            else:                          msDelta_AbsMA = abs(msDelta)*absoluteMA_kValue + msDelta_AbsMA_prev*(1-absoluteMA_kValue)

    #---[3-6]: MSDelta Absolute MA Relative
    if   msDelta_AbsMA is None: msDelta_AbsMARel = None
    elif msDelta_AbsMA == 0:    msDelta_AbsMARel = 0.0
    else:                       msDelta_AbsMARel = round(msDelta/msDelta_AbsMA, 5)

    #[4]: Result Formatting & Saving
    mmacdResult = {'MAs':              mas, 
                   'MMACD':            mmacd, 
                   'SIGNAL':           signal, 
                   'MSDELTA':          msDelta, 
                   'MSDELTA_ABSMA':    msDelta_AbsMA, 
                   'MSDELTA_ABSMAREL': msDelta_AbsMARel,
                   'analysisCount': analysisCount}
    mmacds[timestamp] = mmacdResult

    #[5]: Memory Optimization References
    return (signal_nSamples+1, #nAnalysisToKeep
            maxMANSamples)     #nKlinesToKeep
    
def analysisGenerator_DMIxADX(intervalID, timestamp, klines, nSamples, analysisResults, **_):
    #[1]: Instances
    dmixadxs          = analysisResults
    absoluteMA_kValue = 2/(nSamples*10+1)
    func_gnitt        = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl         = auxiliaries.getTimestampList_byNTicks

    #[2]: Analysis counter
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    dmixadx_prev   = dmixadxs.get(timestamp_prev, None)
    analysisCount  = 0 if dmixadx_prev is None else dmixadx_prev['analysisCount']+1

    #[3]: DMIxADX computation
    #---[3-1]: DM+, DM-, TR
    if analysisCount == 0:
        dmPlus  = None
        dmMinus = None
        tr      = None
    else:
        kline_this = klines[timestamp]
        kline_prev = klines[timestamp_prev]
        hp_prev = kline_prev[KLINDEX_HIGHPRICE]
        lp_prev = kline_prev[KLINDEX_LOWPRICE]
        cp_prev = kline_prev[KLINDEX_CLOSEPRICE]
        hp_this = kline_this[KLINDEX_HIGHPRICE]
        lp_this = kline_this[KLINDEX_LOWPRICE]
        if any(v is None for v in (hp_prev, lp_prev, cp_prev, hp_this, lp_this)):
            dmPlus  = None
            dmMinus = None
            tr      = None
        else:
            move_up   = hp_this-hp_prev
            move_down = lp_prev-lp_this
            if move_down < move_up and 0 < move_up:
                dmPlus  = move_up
                dmMinus = 0.0
            elif move_up < move_down and 0 < move_down:
                dmPlus  = 0.0
                dmMinus = move_down
            else:
                dmPlus  = 0.0
                dmMinus = 0.0
            tr = max(hp_this-lp_this, abs(hp_this-cp_prev), abs(lp_this-cp_prev))
        
    #---[3-2]: DM+Sum, DM-Sum, TRSum
    if analysisCount < nSamples:
        dmPlusSum  = None
        dmMinusSum = None
        trSum      = None
    elif nSamples == analysisCount:
        tsList = func_gtsl(intervalID = intervalID, 
                           timestamp  = timestamp, 
                           nTicks     = nSamples, 
                           direction  = False)
        dmPlusSum  = 0
        dmMinusSum = 0
        trSum      = 0
        for ts in tsList:
            if ts == timestamp:
                dmPlus_ts    = dmPlus
                dmMinus_ts   = dmMinus
                tr_ts        = tr
            else:
                dmixadx_this = dmixadxs[ts]
                dmPlus_ts    = dmixadx_this['DM+']
                dmMinus_ts   = dmixadx_this['DM-']
                tr_ts        = dmixadx_this['TR']
            if tr_ts is not None:
                dmPlusSum  += dmPlus_ts
                dmMinusSum += dmMinus_ts
                trSum      += tr_ts
    elif nSamples < analysisCount:
        dmPlusSum_prev  = dmixadx_prev['DM+Sum']
        dmMinusSum_prev = dmixadx_prev['DM-Sum']
        trSum_prev      = dmixadx_prev['TRSum']
        dmPlusSum  = dmPlusSum_prev  - (dmPlusSum_prev  / nSamples)
        dmMinusSum = dmMinusSum_prev - (dmMinusSum_prev / nSamples)
        trSum      = trSum_prev      - (trSum_prev      / nSamples)
        if tr is not None:
            dmPlusSum  += dmPlus
            dmMinusSum += dmMinus
            trSum      += tr

    #---[3-3]: DI+, DI-, DX
    if nSamples <= analysisCount:
        if trSum == 0:
            diPlus  = 0.0
            diMinus = 0.0
        else:
            diPlus  = dmPlusSum /trSum
            diMinus = dmMinusSum/trSum
        if diPlus+diMinus == 0: dx = 0.0
        else:                   dx = abs(diPlus-diMinus)/(diPlus+diMinus)
    else:
        diPlus  = None
        diMinus = None
        dx      = None

    #---[3-4]: ADX
    if analysisCount < nSamples*2-1:
        adx = None
    elif analysisCount == nSamples*2-1:
        dxs = [dmixadxs[ts]['DX'] for ts in func_gtsl(intervalID = intervalID, 
                                                      timestamp  = timestamp_prev, 
                                                      nTicks     = nSamples-1, 
                                                      direction  = False)]
        dxSum = dx + sum(dxs)
        adx = dxSum/nSamples
    else:
        adx = ((dmixadx_prev['ADX']*(nSamples-1))+dx)/nSamples

    #---[3-5]: DMIxADX
    if any(v is None for v in (diPlus, diMinus, adx)):
        dmixadx = None
    else:
        dmixadx = (diPlus-diMinus)*adx

    #---[3-6]: DMIxADX Absolute Moving Average
    if dmixadx is None: 
        dmixadx_absMA = None
    else:
        dmixadx_dmixadx_prev = dmixadx_prev['DMIxADX']
        if dmixadx_dmixadx_prev is None: 
            dmixadx_absMA = None
        else:
            dmixadx_absMA_prev = dmixadx_prev['DMIxADX_ABSMA']
            if dmixadx_absMA_prev is None: dmixadx_absMA = abs(dmixadx)*absoluteMA_kValue + abs(dmixadx_dmixadx_prev)*(1-absoluteMA_kValue)
            else:                          dmixadx_absMA = abs(dmixadx)*absoluteMA_kValue + dmixadx_absMA_prev       *(1-absoluteMA_kValue)

    #---[3-7]: DMIxADX Absolute Moving Average Relative
    if   dmixadx_absMA is None: dmixadx_absMARel = None
    elif dmixadx_absMA == 0:    dmixadx_absMARel = 0.0
    else:                       dmixadx_absMARel = round(dmixadx/dmixadx_absMA, 5)

    #[4]: Result Formatting & Saving
    dmixadxResult = {'DM+':              dmPlus, 
                     'DM-':              dmMinus, 
                     'TR':               tr, 
                     'DM+Sum':           dmPlusSum, 
                     'DM-Sum':           dmMinusSum, 
                     'TRSum':            trSum,
                     'DI+':              diPlus, 
                     'DI-':              diMinus,
                     'DX':               dx,
                     'ADX':              adx, 
                     'DMIxADX':          dmixadx, 
                     'DMIxADX_ABSMA':    dmixadx_absMA, 
                     'DMIxADX_ABSMAREL': dmixadx_absMARel,
                     'analysisCount':    analysisCount}
    dmixadxs[timestamp] = dmixadxResult

    #[5]: Memory Optimization References
    return (nSamples, #nAnalysisToKeep
            2)        #nKlinesToKeep
    
def analysisGenerator_MFI(intervalID, timestamp, klines, nSamples, analysisResults, **_):
    #[1]: Instances
    mfis              = analysisResults
    absoluteMA_kValue = 2/(nSamples*10+1)
    kline             = klines[timestamp]
    func_gnitt        = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl         = auxiliaries.getTimestampList_byNTicks

    #[2]: Analysis counter
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    mfi_prev       = mfis.get(timestamp_prev, None)
    analysisCount  = 0 if mfi_prev is None else mfi_prev['analysisCount']+1
    
    #[3]: MFI computation
    #---[3-1]: TP (Typical Price) & MF (Money Flow)
    if any(kline[daIdx] is None for daIdx in (KLINDEX_HIGHPRICE, KLINDEX_LOWPRICE, KLINDEX_CLOSEPRICE, KLINDEX_VOLBASE)):
        tp = None
        mf = None
    else:
        tp = (kline[KLINDEX_HIGHPRICE]+kline[KLINDEX_LOWPRICE]+kline[KLINDEX_CLOSEPRICE])/3
        mf = tp*kline[KLINDEX_VOLBASE]

    #---[3-2]: MFI
    #------[3-2-1]: nSamples Not Reached
    if analysisCount < nSamples: 
        mfi = None

    #------[3-2-2]: nSamples Reached
    else:
        #[3-2-2-1]: Directional Money Flow
        tsList = func_gtsl(intervalID = intervalID, 
                           timestamp  = timestamp, 
                           nTicks     = nSamples+1, 
                           direction  = False)
        mfPlusSum  = 0
        mfMinusSum = 0
        nValid     = 0
        for tsIndex in range (nSamples-1, -1, -1):
            if tsIndex == 0: 
                tp_current = tp
                mf_current = mf
            else:
                mfi_ts = mfis[tsList[tsIndex]]
                tp_current = mfi_ts['TP']
                mf_current = mfi_ts['MF']
            tp_prev = mfis[tsList[tsIndex+1]]['TP']
            if tp_current is not None and mf_current is not None and tp_prev is not None:
                tpDelta = tp_current-tp_prev
                if   tpDelta < 0: mfMinusSum += mf_current
                elif 0 < tpDelta: mfPlusSum  += mf_current
                nValid += 1

        #[3-2-2-2]: MFR (Money Flow Ratio)
        if   nValid == 0:       mfr = None
        elif mfMinusSum == 0.0: mfr = float('inf')
        else:                   mfr = mfPlusSum/mfMinusSum

        #[3-2-2-3]: MFI (Money Flow Index)
        if mfr is None: mfi = 0.5
        else:           mfi = 1.0-(1.0/(1.0+mfr))
        confidence = nValid/nSamples
        mfi        = 0.5+((mfi-0.5)*confidence)

    #---[3-3]: MFI Deviation Absolute MA
    if mfi is None: 
        mfi_devAbsMA = None
    else:
        mfi_mfi_prev = mfi_prev['MFI']
        if mfi_mfi_prev is None: 
            mfi_devAbsMA = None
        else:
            mfi_devAbsMA_prev = mfi_prev['MFI_DEVABSMA']
            if mfi_devAbsMA_prev is None: mfi_devAbsMA = abs(mfi-0.5)*absoluteMA_kValue + abs(mfi_mfi_prev-0.5)*(1-absoluteMA_kValue)
            else:                         mfi_devAbsMA = abs(mfi-0.5)*absoluteMA_kValue + mfi_devAbsMA_prev    *(1-absoluteMA_kValue)

    #---[3-4]: MFI Deviation Absolute MA Relative
    if   mfi_devAbsMA is None: mfi_devAbsMARel = None
    elif mfi_devAbsMA == 0:    mfi_devAbsMARel = 0.0
    else:                      mfi_devAbsMARel = round((mfi-0.5)/mfi_devAbsMA, 5)

    #[4]: Result Formatting & Saving
    mfiResult = {'TP':              tp, 
                 'MF':              mf, 
                 'MFI':             mfi, 
                 'MFI_DEVABSMA':    mfi_devAbsMA, 
                 'MFI_DEVABSMAREL': mfi_devAbsMARel,
                 'analysisCount':   analysisCount}
    mfis[timestamp] = mfiResult

    #[5]: Memory Optimization References
    return (nSamples+1, #nAnalysisToKeep
            1)          #nKlinesToKeep

def analysisGenerator_TPD(intervalID, timestamp, klines, viewLength, nSamples, nSamplesMA, analysisResults, **_):
    #[1]: Params & Instances
    tpds              = analysisResults
    kValueMA          = 2/(nSamplesMA+1)
    absoluteMA_kValue = 2/(nSamplesMA*10+1)
    kline             = klines[timestamp]
    func_gnitt        = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl         = auxiliaries.getTimestampList_byNTicks

    #[2]: Analysis counter
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    tpd_prev       = tpds.get(timestamp_prev, None)
    analysisCount  = 0 if tpd_prev is None else tpd_prev['analysisCount']+1

    #[3]: TPD Computation
    #---[3-1]: Last Termination
    lastTerm_TS = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -viewLength)
    cp_lastTerm = None if lastTerm_TS not in klines else klines[lastTerm_TS][KLINDEX_CLOSEPRICE]
    cp_this     = kline[KLINDEX_CLOSEPRICE]
    if cp_lastTerm is None or cp_this is None:
        lastTerm_pd = None
    else:
        lastTerm_pd = (cp_this / cp_lastTerm)-1

    #---[3-2]: Update Histogram Counts (Sliding Window O(1))
    if analysisCount == 0:
        termSum_dec = 0
        termSum_inc = 0
    else:
        termSum_dec = tpd_prev['TERMSUM_DECREMENTAL']
        termSum_inc = tpd_prev['TERMSUM_INCREMENTAL']
    #[3-2-1]: Add New Count
    if lastTerm_pd is not None:
        if   lastTerm_pd < 0: termSum_dec += abs(lastTerm_pd)
        elif 0 < lastTerm_pd: termSum_inc += abs(lastTerm_pd)
    #[3-2-2]: Remove Expired
    expired_TS = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -nSamples)
    expired_pd = None if expired_TS not in tpds else tpds[expired_TS]['LASTERM_PD']
    if expired_pd is not None:
        if   expired_pd < 0: termSum_dec -= abs(expired_pd)
        elif 0 < expired_pd: termSum_inc -= abs(expired_pd)

    #---[3-3]: Bias
    if analysisCount < viewLength+nSamples-1:
        bias = None
    else:
        bias = (termSum_inc-termSum_dec)/nSamples

    #---[3-4]: TPD
    if analysisCount < viewLength+nSamples+nSamplesMA-2:
        tpd = None
    elif analysisCount == viewLength+nSamples+nSamplesMA-2:
        biasSum = sum(tpds[ts]['BIAS'] for ts in func_gtsl(intervalID = intervalID, 
                                                           timestamp  = timestamp_prev, 
                                                           nTicks     = nSamplesMA-1,
                                                           direction  = False)) + bias
        tpd = round(biasSum / nSamplesMA, 5)
    else:
        tpd = round((bias*kValueMA) + (tpd_prev['TPD'] * (1-kValueMA)), 5)

    #---[3-5]: TPD Absolute Moving Average
    if tpd is None: 
        tpd_absMA = None
    else:
        tpd_tpd_prev = tpd_prev['TPD']
        if tpd_tpd_prev is None: 
            tpd_absMA = None
        else:
            tpd_absMA_prev = tpd_prev['TPD_ABSMA']
            if tpd_absMA_prev is None: tpd_absMA = abs(tpd)*absoluteMA_kValue + abs(tpd_tpd_prev)*(1-absoluteMA_kValue)
            else:                      tpd_absMA = abs(tpd)*absoluteMA_kValue + tpd_absMA_prev   *(1-absoluteMA_kValue)

    #---[3-6]: TPD Absolute Moving Average Relative
    if   tpd_absMA is None: tpd_absMARel = None
    elif tpd_absMA == 0:    tpd_absMARel = 0.0
    else:                   tpd_absMARel = round(tpd/tpd_absMA, 5)

    #[4]: Result Formatting & Saving
    tpdResult = {'LASTERM_PD':          lastTerm_pd,
                 'TERMSUM_INCREMENTAL': termSum_inc,
                 'TERMSUM_DECREMENTAL': termSum_dec,
                 'BIAS':                bias,
                 'TPD':                 tpd,
                 'TPD_ABSMA':           tpd_absMA,
                 'TPD_ABSMAREL':        tpd_absMARel,
                 'analysisCount':       analysisCount}
    tpds[timestamp] = tpdResult

    #[5]: Memory Optimization References
    return (max(nSamples, nSamplesMA)+1, #nAnalysisToKeep
            viewLength+1)                #nKlinesToKeep

def analysisGenerator_WOI(intervalID, precisions, timestamp, depths, nSamples, analysisResults, **_):
    #[1]: Instances
    wois              = analysisResults
    kValue            = 2/(nSamples+1)
    absoluteMA_kValue = 2/(nSamples*10+1)
    qPrecision = precisions['quote']
    func_gnitt        = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl         = auxiliaries.getTimestampList_byNTicks

    #[2]: Previous Analysis & Analysis Count
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    woi_prev       = wois.get(timestamp_prev, None)
    mode           = 0 if woi_prev is None else woi_prev['mode']

    #[3]: WOI computation
    #---[3-1]: Imbalance
    depth = depths[timestamp]
    if any(depth[vIdx] is None for vIdx in (DEPTHINDEX_BIDS5,
                                            DEPTHINDEX_BIDS4,
                                            DEPTHINDEX_BIDS3,
                                            DEPTHINDEX_BIDS2,
                                            DEPTHINDEX_BIDS1,
                                            DEPTHINDEX_BIDS0,
                                            DEPTHINDEX_ASKS0,
                                            DEPTHINDEX_ASKS1,
                                            DEPTHINDEX_ASKS2,
                                            DEPTHINDEX_ASKS3,
                                            DEPTHINDEX_ASKS4,
                                            DEPTHINDEX_ASKS5)):
        imbalance = None
    else:
        wBids_sum = sum(depth[vIdx]/abs((DEPTHBINS[vIdx][1]+DEPTHBINS[vIdx][0])/2) 
                        for vIdx in (DEPTHINDEX_BIDS5, DEPTHINDEX_BIDS4, DEPTHINDEX_BIDS3, DEPTHINDEX_BIDS2, DEPTHINDEX_BIDS1, DEPTHINDEX_BIDS0))
        wAsks_sum = sum(depth[vIdx]/abs((DEPTHBINS[vIdx][1]+DEPTHBINS[vIdx][0])/2) 
                        for vIdx in (DEPTHINDEX_ASKS5, DEPTHINDEX_ASKS4, DEPTHINDEX_ASKS3, DEPTHINDEX_ASKS2, DEPTHINDEX_ASKS1, DEPTHINDEX_ASKS0))
        imbalance = wBids_sum-wAsks_sum

    #---[3-2]: WOI
    if mode == 0:
        imbalances = [imbalance,] + [wois[ts]['IMBALANCE'] if ts in wois else None
                                     for ts in func_gtsl(intervalID = intervalID,
                                                         timestamp  = timestamp_prev,
                                                         nTicks     = (nSamples-1),
                                                         direction  = False)]
        if any(val is None for val in imbalances):
            woi = None
        else:
            imbalances_sum = sum(imbalances)
            woi            = round(imbalances_sum / nSamples, qPrecision)
            mode           = 1
    elif mode == 1:
        if imbalance is None:
            woi = woi_prev['WOI']
        else:
            woi = round((imbalance*kValue) + (woi_prev['WOI']*(1-kValue)), qPrecision)

    #---[3-3]: WOI Absolute Moving Average
    if woi is None: 
        woi_absMA = None
    else:
        woi_woi_prev = woi_prev['WOI']
        if woi_woi_prev is None:
            woi_absMA = None
        else:
            woi_absMA_prev = woi_prev['WOI_ABSMA']
            if woi_absMA_prev is None: woi_absMA = abs(woi)*absoluteMA_kValue + abs(woi_woi_prev)*(1-absoluteMA_kValue)
            else:                      woi_absMA = abs(woi)*absoluteMA_kValue + woi_absMA_prev   *(1-absoluteMA_kValue)

    #---[3-4]: WOI Absolute Moving Average Relative
    if   woi_absMA is None: woi_absMARel = None
    elif woi_absMA == 0:    woi_absMARel = 0.0
    else:                   woi_absMARel = round(woi/woi_absMA, 5)

    #[4]: Result formatting & Saving
    woiResult = {'IMBALANCE':    imbalance,
                 'WOI':          woi,
                 'WOI_ABSMA':    woi_absMA,
                 'WOI_ABSMAREL': woi_absMARel,
                 'mode':         mode}
    wois[timestamp] = woiResult

    #[5]: Memory Optimization References
    return (nSamples, #nAnalysisToKeep
            nSamples) #nKlinesToKeep

def analysisGenerator_NES(intervalID, precisions, timestamp, aggTrades, nSamples, analysisResults, **_):
    #[1]: Instances
    ness              = analysisResults
    kValue            = 2/(nSamples+1)
    absoluteMA_kValue = 2/(nSamples*10+1)
    qPrecision        = precisions['quote']
    func_gnitt        = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl         = auxiliaries.getTimestampList_byNTicks

    #[2]: Previous Analysis & Analysis Count
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    nes_prev       = ness.get(timestamp_prev, None)
    mode           = 0 if nes_prev is None else nes_prev['mode']

    #[3]: NES computation
    #---[3-1]: Net Notional
    at = aggTrades[timestamp]
    notional_buy  = at[ATINDEX_NOTIONALBUY]
    notional_sell = at[ATINDEX_NOTIONALSELL]
    if notional_buy is None or notional_sell is None:
        netNotional = None
    else:
        netNotional = notional_buy-notional_sell

    #---[3-2]: NES
    if mode == 0:
        netNotionals = [netNotional,] + [ness[ts]['NETNOTIONAL'] if ts in ness else None
                                         for ts in func_gtsl(intervalID = intervalID,
                                                             timestamp  = timestamp_prev,
                                                             nTicks     = (nSamples-1),
                                                             direction  = False)]
        if any(val is None for val in netNotionals):
            nes = None
        else:
            netNotionals_sum = sum(netNotionals)
            nes              = round(netNotionals_sum / nSamples, qPrecision)
            mode             = 1
    elif mode == 1:
        if netNotional is None:
            nes = nes_prev['NES']
        else:
            nes = round((netNotional*kValue) + (nes_prev['NES']*(1-kValue)), qPrecision)

    #---[3-3]: NES Absolute Moving Average
    if nes is None: 
        nes_absMA = None
    else:
        nes_nes_prev = nes_prev['NES']
        if nes_nes_prev is None: 
            nes_absMA = None
        else:
            nes_absMA_prev = nes_prev['NES_ABSMA']
            if nes_absMA_prev is None: nes_absMA = abs(nes)*absoluteMA_kValue + abs(nes_nes_prev)*(1-absoluteMA_kValue)
            else:                      nes_absMA = abs(nes)*absoluteMA_kValue + nes_absMA_prev   *(1-absoluteMA_kValue)

    #---[3-4]: NES Absolute Moving Average Relative
    if   nes_absMA is None: nes_absMARel = None
    elif nes_absMA == 0:    nes_absMARel = 0.0
    else:                   nes_absMARel = round(nes/nes_absMA, 5)

    #[4]: Result formatting & Saving
    nesResult = {'NETNOTIONAL':  netNotional,
                 'NES':          nes,
                 'NES_ABSMA':    nes_absMA,
                 'NES_ABSMAREL': nes_absMARel,
                 'mode':         mode}
    ness[timestamp] = nesResult

    #[5]: Memory Optimization References
    return (nSamples, #nAnalysisToKeep
            nSamples) #nKlinesToKeep

"""