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
ANALYSIS_TYPE = 'MAIN'
NMAXLINES     = 10
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

"""
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
"""
#ANALYSIS GENERATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#LINEARIZATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def linearize(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_SMA': analysisResult['SMA']}
    return lRes


"""
def linearizeAnalysis_MMACD(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_MSDELTA':         analysisResult['MSDELTA'],
            f'{intervalID}_{analysisCode}_MSDELTAABSMA':    analysisResult['MSDELTA_ABSMA'],
            f'{intervalID}_{analysisCode}_MSDELTAABSMAREL': analysisResult['MSDELTA_ABSMAREL']}
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
#---MMACD
if cac_iID['MMACD_Master']:
    for lineIndex in range (constants.NLINES_MMACD):
        lineActive = cac_iID.get(f'MMACD_MA{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'MMACD_MA{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
"""
#ANALYZER FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#CHART DRAWER FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
CD_FULL_DRAW_SIGNALS        = 0b1
CD_VVR_PRECISIONCOMPENSATOR = None
CD_VVR_CENTERVALUE          = None
CD_VVR_DEFAULT              = None

"""
_FULLDRAWSIGNALS = {'MMACD':        0b111}
_VVR_PRECISIONCOMPENSATOR = {'MMACD':       -2,
                            }
_VVR_CENTERVALUE = {'MMACD':                         0}
_VVR_DEFAULT = {'MMACD':                         (-1, 1)}
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
guios_MMACD    = ssps['MMACD'].GUIOs
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
        for lineIndex in range (NMAXLINES):
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
guios_MMACD   = self.settingsSubPages['MMACD'].GUIOs

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
"""


def cd_on_position_highlight_update(chart_drawer):
    pass

"""
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
"""

def cd_on_position_selection_update(chart_drawer):
    pass
 


def cd_check_vertical_extremas(chart_drawer):
    pass

"""
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
"""

def cd_remove_expired_drawings(display_box_graphics, si_viewer_index, analysis_code, timestamp):
    #[1]: Drawings Removal
    display_box_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysis_code)

"""
elif targetType == 'MMACD':
    sivIdx = self.siTypes_siViewerAlloc['MMACD']
    if sivIdx is not None: 
        sivCode = f"SIVIEWER{sivIdx}"
        self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACD_MMACD')
        self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACD_SIGNAL')
        self.displayBox_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACD_HISTOGRAM')
"""

def cd_remove_drawings(drawn, display_box_graphics, si_viewer_index, analysis_code, graphics_removal_signal):
    #[1]: Drawings Removal
    if graphics_removal_signal&0b1: 
        display_box_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysis_code)

"""
#---[3-14]: MMACD
elif analysisType == 'MMACD':
    sivIdx = self.siTypes_siViewerAlloc['MMACD']
    if sivIdx is not None:
        sivCode = f"SIVIEWER{sivIdx}"
        if gRemovalSignal&0b001: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = 'MMACD_MMACD')
        if gRemovalSignal&0b010: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = 'MMACD_SIGNAL')
        if gRemovalSignal&0b100: dBox_g[sivCode]['RCLCG'].removeGroup(groupName = 'MMACD_HISTOGRAM')
"""

def cd_get_vertical_magnitude_anchor(object_configuration):
    return None

"""
#[2-1-5]: MMACD
elif siAlloc == 'MMACD':
    if oc['MMACD_HISTOGRAM_Type'] == 'MSDELTA_ABSMA' and not oc[f"MMACD_MMACD_Display"] and not oc[f"MMACD_SIGNAL_Display"]:
        anchor = 'BOTTOM'
    else:
        anchor = 'CENTER'
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
#---[8-8]: MMACD
for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
    ssps['MMACD'].GUIOs[f"INDICATOR_{targetLine}_COLOR"].updateColor(oc[f'MMACD_{targetLine}_ColorR%{cgt}'], 
                                                                        oc[f'MMACD_{targetLine}_ColorG%{cgt}'], 
                                                                        oc[f'MMACD_{targetLine}_ColorB%{cgt}'], 
                                                                        oc[f'MMACD_{targetLine}_ColorA%{cgt}'])
self.__onSettingsContentUpdate(ssps['MMACD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"])
"""


def cd_update_si_type_analysis_codes(analysis_parameters):
    return None

"""
aParams_iID = self.analysisParams.get(self.intervalID)
if aParams_iID is not None:
    if 'MMACD' in aParams_iID: sit_aCodes['MMACD'].add('MMACD')
"""

def cd_type_init(subPage):
    #[1]: Instances
    guios_THIS = subPage.GUIOs

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        guios_THIS[f"INDICATOR_SMA{lIdx}"].deactivate()
        guios_THIS[f"INDICATOR_SMA{lIdx}_INTERVALINPUT"].deactivate()

"""
#MMACD
guios_MMACD["INDICATOR_SIGNALINTERVALTEXTINPUT"].deactivate()
for lineIndex in range (_NMAXLINES['MMACD']):
    guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}"].deactivate()
    guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].deactivate()
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
#MMACD
ac_def['MMACD_Master'] = False
ac_def['MMACD_SignalNSamples'] = 10
for lineIndex in range (constants.NLINES_MMACD):
    ac_def[f'MMACD_MA{lineIndex}_LineActive'] = False
    ac_def[f'MMACD_MA{lineIndex}_NSamples']   = 20*(lineIndex+1)
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
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MMACD"].setStatus(status    = configuration['MMACD_Master'],   callStatusUpdateFunction = False)

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
#MMACD
configuration['MMACD_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MMACD"].getStatus()
configuration['MMACD_SignalNSamples'] = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs["MMACDSIGNALINTERVALTEXTINPUTBOX"].getText())
for lineIndex in range (constants.NLINES_MMACD):
    configuration[f'MMACD_MA{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs[f"MA{lineIndex}_LINE"].getStatus()
    configuration[f'MMACD_MA{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs[f"MA{lineIndex}_NSAMPLES"].getText())
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
    sp_GUIOs["INDICATORMASTERSWITCH_MMACD"].setStatus(status   = False, callStatusUpdateFunction = False)
    
    #MMACD
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MMACD"].GUIOs
    sp_GUIOs["MMACDSIGNALINTERVALDISPLAYTEXT"].updateText(text = "-")
    for lIdx in range (constants.NLINES_MMACD):
        sp_GUIOs[f"MA{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"MA{lIdx}_NSAMPLES"].updateText(text = "-")

#---[2-2]: Simulation Selected
else:
    cac_iID = cac[iID]
    #MAIN
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MAIN"].GUIOs
    sp_GUIOs["INDICATORMASTERSWITCH_MMACD"].setStatus(status   = cac_iID['MMACD_Master'],   callStatusUpdateFunction = False)
    
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
"""
#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------