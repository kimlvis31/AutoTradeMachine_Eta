#Imports
import auxiliaries
import random
import math
from collections import defaultdict, deque

import constants

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
ANALYSIS_CODE = 'MMACD'
ANALYSIS_TYPE = 'SUB'
NMAXLINES     = 10
#DEFINING PARAMETERS END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYSIS GENERATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def construct_analysis_parameters(configuration):
    #[1]: Instances & Initialization
    cac = configuration
    cap          = dict()
    invalidLines = defaultdict(list)

    #[2]: Analysis Parameters Construction
    if cac['MMACD_Master']:
        analysisCode = 'MMACD'
        #[2-1]: Signal nSamples
        signal_nSamples = cac[f'{analysisCode}_SignalNSamples']
        if   type(signal_nSamples) is not int: invalidLines[analysisCode].append("signal_nSamples: Must be type 'int'")
        elif not 1 < signal_nSamples:          invalidLines[analysisCode].append("signal_nSamples: Must be greater than 1")
        #[2-2]: Activated MAs
        activatedMAs = []
        for lineIndex in range (NMAXLINES):
            #[2-2-1]: Check Line Active
            lineActive = cac.get(f'MMACD_MA{lineIndex}_LineActive', False)
            if not lineActive: continue
            #[2-2-2]: Parameters
            nSamples = cac[f'MMACD_MA{lineIndex}_NSamples']
            if   type(nSamples) is not int: invalidLines[analysisCode].append(f"MA{lineIndex}_nSamples: Must be type 'int'")
            elif not 1 < nSamples:          invalidLines[analysisCode].append(f"MA{lineIndex}_nSamples: Must be greater than 1")
            else: activatedMAs.append(nSamples)
        #[2-3]: Activated MAs Sort & Params Update
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
    return cap, invalidLines



def generate(intervalID, precisions, timestamp, klines, signal_nSamples, activatedMAs, activatedMAPairs, maxMANSamples, analysisResults, **_):
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
#ANALYSIS GENERATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#LINEARIZATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def linearize(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_MSDELTA':         analysisResult['MSDELTA'],
            f'{intervalID}_{analysisCode}_MSDELTAABSMA':    analysisResult['MSDELTA_ABSMA'],
            f'{intervalID}_{analysisCode}_MSDELTAABSMAREL': analysisResult['MSDELTA_ABSMAREL']}
    return lRes
#LINEARIZATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYZER FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_maximum_market_data_reference_length(cac_iID):
    #[1]: Master Check
    if not cac_iID['MMACD_Master']:
        return 0
    
    #[2]: MMDRL
    mmdrl = 0
    for lIdx in range (NMAXLINES):
        #[2-1]: Line Active Check
        if not cac_iID.get(f'MMACD_MA{lIdx}_LineActive', False): 
            continue

        #[2-2]: MMDRL Update
        mmdrl = max(mmdrl, 
                    cac_iID[f'MMACD_MA{lIdx}_NSamples'])

    #[3]: Return MMDRL
    return mmdrl
#ANALYZER FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#CHART DRAWER FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
CD_FULL_DRAW_SIGNALS        = 0b111
CD_VVR_PRECISIONCOMPENSATOR = -2
CD_VVR_CENTERVALUE          = {'MMACD': 0}
CD_VVR_DEFAULT              = {'MMACD': (-1, 1)}



def cd_get_initial_configuration():
    #[1]: Indicator Configuration
    oc = dict()

    #[2]: Configuration Setup
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
    for lineIndex in range (NMAXLINES):
        oc[f'MMACD_MA{lineIndex}_LineActive'] = False
        oc[f'MMACD_MA{lineIndex}_NSamples']   = 20*(lineIndex+1)

    #[3]: Configuration Return
    return oc



def cd_initialize_settings_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'INDICATOR_BLOCKTITLE_DISPLAY',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos':  -300, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:MMACDDISPLAY'), 'fontSize': 90, 'anchor': 'SW'}))
    gList.append(({'NAME':               'INDICATOR_MMACD_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos':  -650, 'width': 1500, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:MMACDMMACDDISPLAY'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_MMACD_DISPLAYSWITCH',
                   'TYPE':               'switch_typeB',
                   'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                   'groupOrder': 0, 'xPos': 1600, 'yPos':  -650, 'width':  500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': 'MMACD_DisplaySwitch_MMACD'}))
    gList.append(({'NAME':               'INDICATOR_MMACD_COLORTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2200, 'yPos':  -650, 'width':  600, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_MMACD_COLOR',
                   'TYPE':               'LED_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2900, 'yPos':  -650, 'width': 1100, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'mode': True}))
    gList.append(({'NAME':               'INDICATOR_SIGNAL_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1000, 'width': 1500, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:MMACDSIGNALDISPLAY'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_SIGNAL_DISPLAYSWITCH',
                   'TYPE':               'switch_typeB',
                   'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                   'groupOrder': 0, 'xPos': 1600, 'yPos': -1000, 'width':  500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': 'MMACD_DisplaySwitch_SIGNAL'}))
    gList.append(({'NAME':               'INDICATOR_SIGNAL_COLORTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2200, 'yPos': -1000, 'width':  600, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_SIGNAL_COLOR',
                   'TYPE':               'LED_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2900, 'yPos': -1000, 'width': 1100, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'mode': True}))
    gList.append(({'NAME':               'INDICATOR_HISTOGRAM_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1350, 'width': 1500, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:MMACDHISTOGRAMDISPLAY'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_HISTOGRAM_DISPLAYSWITCH',
                   'TYPE':               'switch_typeB',
                   'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                   'groupOrder': 0, 'xPos': 1600, 'yPos': -1350, 'width':  500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': 'MMACD_DisplaySwitch_HISTOGRAM'}))
    gList.append(({'NAME':               'INDICATOR_HISTOGRAM_COLORTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2200, 'yPos': -1350, 'width':  600, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_HISTOGRAM+_COLOR',
                   'TYPE':               'LED_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2900, 'yPos': -1350, 'width':  500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'mode': True}))
    gList.append(({'NAME':               'INDICATOR_HISTOGRAM-_COLOR',
                   'TYPE':               'LED_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3500, 'yPos': -1350, 'width':  500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'mode': True}))
    gList.append(({'NAME':               'INDICATOR_HISTOGRAMTYPE_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1700, 'width': 1500, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:MMACDHISTOGRAMTYPE'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_HISTOGRAMTYPE_SELECTION',
                   'TYPE':               'selectionBox_typeB',
                   'PAGEOBJECTFUNCTION': ['selectionUpdateFunction',],
                   'groupOrder': 0, 'xPos': 1600, 'yPos': -1700, 'width': 2400, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:MMACDHISTOGRAMTYPE'), 'fontSize': 80, 'name': 'MMACD_HistrogramTypeSelectionBox', 'nDisplay': 10}))
    gList.append(({'NAME':               'INDICATOR_BLOCKTITLE_MMACDSETTINGS',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -2000, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:MMACDSETTINGS'), 'fontSize': 90, 'anchor': 'SW'}))
    gList.append(({'NAME':               'INDICATOR_SIGNALINTERVALTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -2350, 'width': 3000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:MMACDSIGNALINTERVAL'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_SIGNALINTERVALTEXTINPUT',
                   'TYPE':               'textInputBox_typeA',
                   'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                   'groupOrder': 0, 'xPos': 3100, 'yPos': -2350, 'width':  900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACD_SignalIntervalTextInputBox'}))
    gList.append(({'NAME':               'INDICATORINDEX_COLUMNTITLE1',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -2650, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'}))
    gList.append(({'NAME':               'INDICATORINTERVAL_COLUMNTITLE1',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1100, 'yPos': -2650, 'width':  850, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'}))
    gList.append(({'NAME':               'INDICATORINDEX_COLUMNTITLE2',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2050, 'yPos': -2650, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'}))
    gList.append(({'NAME':               'INDICATORINTERVAL_COLUMNTITLE2',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3150, 'yPos': -2650, 'width':  850, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'}))
    yPosPoint1 = -2650
    for lIdx in range (NMAXLINES):
        rowNumber = math.ceil((lIdx+1)/2)
        if lIdx%2 == 0: coordX = 0
        else:           coordX = 2050
        gList.append(({'NAME':               f"INDICATOR_MMACDMA{lIdx}",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                       'groupOrder': 0, 'xPos': coordX,      'yPos': yPosPoint1-350*rowNumber, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'MA {lIdx}', 'fontSize': 80, 'name': f'MMACD_LineActivationSwitch_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_MMACDMA{lIdx}_INTERVALINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': coordX+1100, 'yPos': yPosPoint1-350*rowNumber, 'width':  850, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'MMACD_IntervalTextInputBox_{lIdx}'}))

    #[3]: Return GUIO Generation List
    return gList



def cd_initialize_settings_subpage_setup(subpage, fn_get_text_pack):
    histogramTypes = {'MSDELTA':          {'text': 'MSDELTA'},
                      'MSDELTA_ABSMA':    {'text': 'MSDELTA_ABSMA'},
                      'MSDELTA_ABSMAREL': {'text': 'MSDELTA_ABSMAREL'}}
    subpage.GUIOs["INDICATOR_HISTOGRAMTYPE_SELECTION"].setSelectionList(selectionList = histogramTypes, displayTargets = 'all')
    mmacdLineTargets = {'MMACD':      {'text': fn_get_text_pack('GUIO_CHARTDRAWER:MMACDMMACD')},
                        'SIGNAL':     {'text': fn_get_text_pack('GUIO_CHARTDRAWER:MMACDSIGNAL')},
                        'HISTOGRAM+': {'text': fn_get_text_pack('GUIO_CHARTDRAWER:MMACDHISTOGRAM+')},
                        'HISTOGRAM-': {'text': fn_get_text_pack('GUIO_CHARTDRAWER:MMACDHISTOGRAM-')}}
    subpage.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = mmacdLineTargets, displayTargets = 'all')



def cd_match_guios_to_config(mainPage, subPage, current_GUI_Theme, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    cgt        = current_GUI_Theme
    oc         = object_configuration

    #[2]: GUIOs Update
    guios_MAIN["SUBINDICATOR_MMACD"].setStatus(oc['MMACD_Master'], callStatusUpdateFunction = False)
    guios_THIS["INDICATOR_MMACD_DISPLAYSWITCH"].setStatus(oc['MMACD_MMACD_Display'], callStatusUpdateFunction = False)
    guios_THIS["INDICATOR_SIGNAL_DISPLAYSWITCH"].setStatus(oc['MMACD_SIGNAL_Display'], callStatusUpdateFunction = False)
    guios_THIS["INDICATOR_HISTOGRAM_DISPLAYSWITCH"].setStatus(oc['MMACD_HISTOGRAM_Display'], callStatusUpdateFunction = False)
    guios_THIS["INDICATOR_MMACD_COLOR"].updateColor(oc[f'MMACD_MMACD_ColorR%{cgt}'], 
                                                    oc[f'MMACD_MMACD_ColorG%{cgt}'], 
                                                    oc[f'MMACD_MMACD_ColorB%{cgt}'], 
                                                    oc[f'MMACD_MMACD_ColorA%{cgt}'])
    guios_THIS["INDICATOR_SIGNAL_COLOR"].updateColor(oc[f'MMACD_SIGNAL_ColorR%{cgt}'], 
                                                     oc[f'MMACD_SIGNAL_ColorG%{cgt}'], 
                                                     oc[f'MMACD_SIGNAL_ColorB%{cgt}'], 
                                                     oc[f'MMACD_SIGNAL_ColorA%{cgt}'])
    guios_THIS["INDICATOR_HISTOGRAM+_COLOR"].updateColor(oc[f'MMACD_HISTOGRAM+_ColorR%{cgt}'], 
                                                         oc[f'MMACD_HISTOGRAM+_ColorG%{cgt}'], 
                                                         oc[f'MMACD_HISTOGRAM+_ColorB%{cgt}'], 
                                                         oc[f'MMACD_HISTOGRAM+_ColorA%{cgt}'])
    guios_THIS["INDICATOR_HISTOGRAM-_COLOR"].updateColor(oc[f'MMACD_HISTOGRAM-_ColorR%{cgt}'], 
                                                         oc[f'MMACD_HISTOGRAM-_ColorG%{cgt}'], 
                                                         oc[f'MMACD_HISTOGRAM-_ColorB%{cgt}'], 
                                                         oc[f'MMACD_HISTOGRAM-_ColorA%{cgt}'])
    guios_THIS["INDICATOR_HISTOGRAMTYPE_SELECTION"].setSelected(itemKey = oc['MMACD_HISTOGRAM_Type'], callSelectionUpdateFunction = False)
    signalNSamples = oc['MMACD_SignalNSamples']
    guios_THIS["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(text = f"{signalNSamples}")
    for lineIndex in range (NMAXLINES):
        lineActive = oc[f'MMACD_MA{lineIndex}_LineActive']
        nSamples   = oc[f'MMACD_MA{lineIndex}_NSamples']
        guios_THIS[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_THIS[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
    guios_THIS["INDICATORCOLOR_TARGETSELECTION"].setSelected('MMACD')
    guios_THIS["APPLYNEWSETTINGS"].deactivate()



def cd_load_analysis_configuration(mainPage, subPage, analysis_configuration, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    ac = analysis_configuration
    oc = object_configuration

    #[2]: GUIOs Update
    if ac is not None and ac['MMACD_Master']:
        guios_MAIN["SUBINDICATOR_MMACD"].activate()
        guios_MAIN["SUBINDICATOR_MMACD"].setStatus(status = oc['MMACD_Master'], callStatusUpdateFunction = False)
        guios_MAIN["SUBINDICATORSETUP_MMACD"].activate()
        for lineIndex in range (NMAXLINES):
            if ac[f'MMACD_MA{lineIndex}_LineActive']:
                nSamples = ac[f'MMACD_MA{lineIndex}_NSamples']
                guios_THIS[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            else:
                guios_THIS[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText("-")
        signalNSamples = ac['MMACD_SignalNSamples']
        guios_THIS["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(f"{signalNSamples}")
    else:
        guios_MAIN["SUBINDICATOR_MMACD"].setStatus(status = False, callStatusUpdateFunction = False)
        guios_MAIN["SUBINDICATOR_MMACD"].deactivate()
        guios_MAIN["SUBINDICATORSETUP_MMACD"].deactivate()



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

    #---[2-4]: DisplaySwitch
    elif setter == 'DisplaySwitch':  
        sub_page.GUIOs['APPLYNEWSETTINGS'].activate()
        
    #---[2-5]: DisplayType
    elif setter == 'HistrogramTypeSelectionBox':
        sub_page.GUIOs['APPLYNEWSETTINGS'].activate()

    #---[2-6]: ApplySettings
    elif setter == 'ApplySettings':
        #UpdateTracker Initialization
        updateTracker = [False, False, False] #[0]: Draw MMACD, [1]: Draw SIGNAL, [2]: Draw HISTOGRAM
        #Check for any changes in the configuration
        #---MMACD Master
        mmacdMaster_previous = oc['MMACD_Master']
        oc['MMACD_Master'] = main_page.GUIOs["SUBINDICATOR_MMACD"].getStatus()
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
            color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_{targetLine}_COLOR"].getColor()
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
            oc[f'MMACD_{targetLine}_Display'] = sub_page.GUIOs[f"INDICATOR_{targetLine}_DISPLAYSWITCH"].getStatus()
            if displayStatus_prev != oc[f'MMACD_{targetLine}_Display']:
                if   targetLine == 'MMACD':     updateTracker[0] = True
                elif targetLine == 'SIGNAL':    updateTracker[1] = True
                elif targetLine == 'HISTOGRAM': updateTracker[2] = True
        #---Histogram Type
        histogramType_prev = oc['MMACD_HISTOGRAM_Type']
        oc['MMACD_HISTOGRAM_Type'] = sub_page.GUIOs["INDICATOR_HISTOGRAMTYPE_SELECTION"].getSelected()
        if histogramType_prev != oc['MMACD_HISTOGRAM_Type']:
            updateTracker[2] = True
        #Extrema Recomputation
        if any(updateTracker):
            siViewerIndex = chart_drawer.siTypes_siViewerAlloc['MMACD']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in chart_drawer.displayBox_graphics_visibleSIViewers:
                if cd_check_vertical_extremas(chart_drawer): 
                    chart_drawer._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        drawSignal = 0
        drawSignal += 0b001*updateTracker[0] #MMACD
        drawSignal += 0b010*updateTracker[1] #SIGNAL
        drawSignal += 0b100*updateTracker[2] #HISTOGRAM
        if drawSignal:
            chart_drawer._drawer_RemoveDrawings(analysisCode    = 'MMACD', gRemovalSignal = drawSignal) #Remove previous graphics
            chart_drawer.addBufferZone_toDrawQueue(analysisCode = 'MMACD', drawSignal     = drawSignal) #Update draw queue
        #Control Buttons Handling
        sub_page.GUIOs['APPLYNEWSETTINGS'].deactivate()
        activate_save_configuration = True

    #[3]: Analysis Related
    #---[3-1]: Line Activation Switch
    elif setter == 'LineActivationSwitch':          
        lineIndex = int(guio_name_split[2])
        #Get new switch status
        newStatus = sub_page.GUIOs[f"INDICATOR_MMACDMA{lineIndex}"].getStatus()
        oc[f'MMACD_MA{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True
        
    #---[3-2]: Interval Text Input Box
    elif setter == 'IntervalTextInputBox':          
        lineIndex = int(guio_name_split[2])
        #Get new nSamples
        try:    nSamples = int(sub_page.GUIOs[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'MMACD_MA{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True
        
    #---[3-3]: Signal Interval Text Input Box
    elif setter == 'SignalIntervalTextInputBox':    
        #Get new nSamples
        try:    nSamples = int(sub_page.GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc['MMACD_SignalNSamples'] = nSamples
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #[3]: Return Status Flag
    return activate_save_configuration



def cd_on_position_highlight_update(chart_drawer):
    #[1]: Instances
    oc  = chart_drawer.objectConfig
    ap  = chart_drawer.analysisParams[chart_drawer.intervalID]
    cgt = chart_drawer.currentGUITheme
    tsHovered = chart_drawer.posHighlight_hoveredPos[0]
    dAgg      = chart_drawer._data_agg[chart_drawer.intervalID]
    siViewerIndex   = chart_drawer.siTypes_siViewerAlloc['MMACD']
    dBox_g_this_dt1 = chart_drawer.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

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
                    newLine_style = chart_drawer.effectiveTextStyle['CONTENT_DEFAULT'].copy()
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



def cd_on_position_selection_update(chart_drawer):
    pass



def cd_check_vertical_extremas(chart_drawer):
    #[1]: References
    oc          = chart_drawer.objectConfig
    dispType    = oc['MMACD_HISTOGRAM_Type']
    ap          = chart_drawer.analysisParams[chart_drawer.intervalID]
    dAgg        = chart_drawer._data_agg[chart_drawer.intervalID]
    hvr_tssInVR = chart_drawer.horizontalViewRange_timestampsInViewRange
    siViewerIndex = chart_drawer.siTypes_siViewerAlloc['MMACD']
    siViewerCode  = f"SIVIEWER{siViewerIndex}"

    #[2]: Timestamps Check
    if not hvr_tssInVR: return False

    #[3]: Extremas Search
    #---Analysis Codes To Consider
    searchTargets = [valCode
                     for valCode, lineCode in (('MMACD', 'MMACD'), ('SIGNAL', 'SIGNAL'), (dispType, 'HISTOGRAM'))
                     if oc[f"MMACD_{lineCode}_Display"]]
    #---Initial Extrema
    valMin = float('inf')
    valMax = float('-inf')
    #---Search Loop
    tData = dAgg.get("MMACD", {})
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
        valMin, valMax = chart_drawer.vvr_extrema_converters['above_zero'](val_min = valMin, val_max = valMax)
    else:
        valMin, valMax = chart_drawer.vvr_extrema_converters['centered'](val_min = valMin, val_max = valMax, center = CD_VVR_CENTERVALUE['MMACD'])

    #[4]: Change Check & Result Return
    return chart_drawer.cve_check_new_vertical_values(val_min               = valMin,
                                                      val_max               = valMax,
                                                      target                = siViewerCode,
                                                      precision_compensator = CD_VVR_PRECISIONCOMPENSATOR)



def cd_draw(chart_drawer, drawSignal, timestamp, analysisCode):
    #[1]: Parameters
    oc  = chart_drawer.objectConfig
    cgt = chart_drawer.currentGUITheme
    siViewerIndex = chart_drawer.siTypes_siViewerAlloc['MMACD']
    siViewerCode  = f'SIVIEWER{siViewerIndex}'
    rclcg = chart_drawer.displayBox_graphics[siViewerCode]['RCLCG']

    #[2]: Master & Display Status
    if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b000
    if not oc['MMACD_Master']:                    return 0b000

    #[3]: Draw Signal
    if drawSignal is None: drawSignal = 0b111
    if not drawSignal:     return 0b000

    #[4]: Data Acquisition
    mmacds = chart_drawer._data_agg[chart_drawer.intervalID][analysisCode]
    timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = chart_drawer.intervalID, timestamp = timestamp, nTicks = -1)
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



def cd_remove_expired_drawings(display_box_graphics, si_viewer_index, analysis_code, timestamp):
    #[1]: SI Viewer Check
    if si_viewer_index is None:
        return

    #[2]: Drawings Removal
    sivCode = f"SIVIEWER{si_viewer_index}"
    display_box_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACD_MMACD')
    display_box_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACD_SIGNAL')
    display_box_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = 'MMACD_HISTOGRAM')



def cd_remove_drawings(drawn, display_box_graphics, si_viewer_index, analysis_code, graphics_removal_signal):
    #[1]: SI Viewer Check
    if si_viewer_index is None:
        return
    
    #[2]: Drawings Removal
    sivCode = f"SIVIEWER{si_viewer_index}"
    if graphics_removal_signal&0b001: display_box_graphics[sivCode]['RCLCG'].removeGroup(groupName = 'MMACD_MMACD')
    if graphics_removal_signal&0b010: display_box_graphics[sivCode]['RCLCG'].removeGroup(groupName = 'MMACD_SIGNAL')
    if graphics_removal_signal&0b100: display_box_graphics[sivCode]['RCLCG'].removeGroup(groupName = 'MMACD_HISTOGRAM')



def cd_get_vertical_magnitude_anchor(object_configuration):
    if (object_configuration['MMACD_HISTOGRAM_Type'] == 'MSDELTA_ABSMA' and 
        not object_configuration[f"MMACD_MMACD_Display"] and 
        not object_configuration[f"MMACD_SIGNAL_Display"]):
        anchor = 'BOTTOM'
    else:
        anchor = 'CENTER'
    return anchor



def cd_on_GUI_theme_update(subpage, object_configuration, current_GUI_theme):
    #[1]: Instances
    sp  = subpage
    oc  = object_configuration
    cgt = current_GUI_theme

    #[2]: GUIOs Update
    for targetLine in ('MMACD', 'SIGNAL', 'HISTOGRAM+', 'HISTOGRAM-'):
        sp.GUIOs[f"INDICATOR_{targetLine}_COLOR"].updateColor(oc[f'MMACD_{targetLine}_ColorR%{cgt}'], 
                                                              oc[f'MMACD_{targetLine}_ColorG%{cgt}'], 
                                                              oc[f'MMACD_{targetLine}_ColorB%{cgt}'], 
                                                              oc[f'MMACD_{targetLine}_ColorA%{cgt}'])

    

def cd_update_si_type_analysis_codes(analysis_parameters):
    #[1]: Identify Analysis Codes Belonging To This Module
    aCodes = []
    if 'MMACD' in analysis_parameters: aCodes['MMACD'].add('MMACD')

    #[2]: Return Analysis Codes
    return aCodes



def cd_type_init(subPage):
    #[1]: Instances
    guios_THIS = subPage.GUIOs

    #[2]: GUIOs Update
    guios_THIS["INDICATOR_SIGNALINTERVALTEXTINPUT"].deactivate()
    for lIdx in range (NMAXLINES):
        guios_THIS[f"INDICATOR_MMACDMA{lIdx}"].deactivate()
        guios_THIS[f"INDICATOR_MMACDMA{lIdx}_INTERVALINPUT"].deactivate()
#CHART DRAWER FUNCTIONS END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUTOTRADE PAGE FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_autotrade_get_default_analysis_configuration():
    #[1]: Default Analysis Configuration
    dac = dict()

    #[2]: Setup
    dac['MMACD_Master'] = False
    dac['MMACD_SignalNSamples'] = 10
    for lIdx in range (NMAXLINES):
        dac[f'MMACD_MA{lIdx}_LineActive'] = False
        dac[f'MMACD_MA{lIdx}_NSamples']   = 20*(lIdx+1)

    #[3]: Return
    return dac



def pg_autotrade_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               "MMACDSIGNALINTERVALTITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -350, 'width': 3000, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_MMACDSIGNALINTERVAL'), 'fontSize': 80}))
    gList.append(({'NAME':               "MMACDSIGNALINTERVALTEXTINPUTBOX",
                   'TYPE':               'textInputBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3100, 'yPos': -350, 'width': 1450, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
    gList.append(({'NAME':               'INDEX_COLUMNTITLE1',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -650, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'NSAMPLES_COLUMNTITLE1',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1100, 'yPos': -650, 'width': 1125, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'INDEX_COLUMNTITLE2',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2325, 'yPos': -650, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'NSAMPLES_COLUMNTITLE2',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3425, 'yPos': -650, 'width': 1125, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'}))
    yPosPoint1 = -650
    for lIdx in range (NMAXLINES):
        rowNumber = math.ceil((lIdx+1)/2)
        if lIdx%2 == 0: coordX = 0
        else:           coordX = 2325
        gList.append(({'NAME':               f"MA{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': coordX,      'yPos': yPosPoint1-350*rowNumber, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'MA {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"MA{lIdx}_NSAMPLES",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': coordX+1100, 'yPos': yPosPoint1-350*rowNumber, 'width': 1125, 'height': 250, 'style': 'styleA', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_autotrade_configure_subpage_setup(subpage, fn_get_text_pack):
    pass

 

def pg_autotrade_load_analysis_configuration(mainPage, subPage, analysis_configuration):
    #[1]: Main Page
    mainPage.GUIOs["INDICATORMASTERSWITCH_MMACD"].setStatus(status = analysis_configuration['MMACD_Master'], callStatusUpdateFunction = False)

    #[2]: Sub Page
    subPage.GUIOs["MMACDSIGNALINTERVALTEXTINPUTBOX"].updateText(text = f"{analysis_configuration['MMACD_SignalNSamples']:d}")
    for lineIndex in range (constants.NLINES_MMACD):
        if f'MMACD_MA{lineIndex}_LineActive' in analysis_configuration:
            lineActive = analysis_configuration[f'MMACD_MA{lineIndex}_LineActive']
            nSamples   = analysis_configuration[f'MMACD_MA{lineIndex}_NSamples']
        else:
            lineActive = False
            nSamples   = 20*(lineIndex+1)
        subPage.GUIOs[f"MA{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        subPage.GUIOs[f"MA{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")



def pg_autotrade_format_analysis_configuration_from_guios(mainPage, subPage):
    #[1]: Instances
    configuration = dict()

    #[2]: Configuration Construction
    configuration['MMACD_Master'] = mainPage.GUIOs["INDICATORMASTERSWITCH_MMACD"].getStatus()
    configuration['MMACD_SignalNSamples'] = int(subPage.GUIOs["MMACDSIGNALINTERVALTEXTINPUTBOX"].getText())
    for lineIndex in range (constants.NLINES_MMACD):
        configuration[f'MMACD_MA{lineIndex}_LineActive'] = subPage.GUIOs[f"MA{lineIndex}_LINE"].getStatus()
        configuration[f'MMACD_MA{lineIndex}_NSamples']   = int(subPage.GUIOs[f"MA{lineIndex}_NSAMPLES"].getText())

    #[3]: Return Configuration
    return configuration
#AUTOTRADE PAGE FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SIMULATION RESULTS PAGE FUNCTIONS ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_simulation_result_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               "MMACDSIGNALINTERVALTITLETEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -350, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MMACDSIGNALINTERVAL'), 'fontSize': 80}))
    gList.append(({'NAME':               "MMACDSIGNALINTERVALDISPLAYTEXT",
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3150, 'yPos': -350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
    gList.append(({'NAME':               'INDEX_COLUMNTITLE1',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -650, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'NSAMPLES_COLUMNTITLE1',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1200, 'yPos': -650, 'width': 1325, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'INDEX_COLUMNTITLE2',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2625, 'yPos': -650, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'NSAMPLES_COLUMNTITLE2',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3825, 'yPos': -650, 'width': 1325, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'}))
    yPosPoint1 = -650
    for lIdx in range (NMAXLINES):
        rowNumber = math.ceil((lIdx+1)/2)
        if lIdx%2 == 0: coordX = 0
        else:           coordX = 2625
        gList.append(({'NAME':               f"MA{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': coordX,      'yPos': yPosPoint1-350*rowNumber, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': f'MA {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"MA{lIdx}_NSAMPLES",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': coordX+1200, 'yPos': yPosPoint1-350*rowNumber, 'width': 1325, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_simulation_result_configure_subpage_setup(subpage, fn_get_text_pack):
    for lIdx in range (NMAXLINES):
        subpage.GUIOs[f"MA{lIdx}_LINE"].deactivate()



def pg_simulation_result_load_analysis_configuration(mainPage, subPage, analysis_configuration, simulation_selected, fn_get_text_pack):
    if simulation_selected:
        #MAIN
        mainPage.GUIOs["INDICATORMASTERSWITCH_MMACD"].setStatus(status = analysis_configuration['MMACD_Master'], callStatusUpdateFunction = False)
        
        #MMACD
        signalNSamples = analysis_configuration['MMACD_SignalNSamples']
        subPage.GUIOs["MMACDSIGNALINTERVALDISPLAYTEXT"].updateText(text = f"{signalNSamples}")
        for lIdx in range (constants.NLINES_MMACD):
            lineActive = analysis_configuration.get(f'MMACD_MA{lIdx}_LineActive', False)
            if lineActive: nSamples_str = f"{analysis_configuration[f'MMACD_MA{lIdx}_NSamples']}"
            else:          nSamples_str = "-"
            subPage.GUIOs[f"MA{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
            subPage.GUIOs[f"MA{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    else:
        #MAIN
        mainPage.GUIOs["INDICATORMASTERSWITCH_MMACD"].setStatus(status   = False, callStatusUpdateFunction = False)
        
        #MMACD
        subPage.GUIOs["MMACDSIGNALINTERVALDISPLAYTEXT"].updateText(text = "-")
        for lIdx in range (constants.NLINES_MMACD):
            subPage.GUIOs[f"MA{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
            subPage.GUIOs[f"MA{lIdx}_NSAMPLES"].updateText(text = "-")
#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------