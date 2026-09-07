#Imports
import auxiliaries
import random
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
ANALYSIS_CODE = 'BOL'
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
    if cac['BOL_Master']:
        for lineIndex in range (NMAXLINES):
            analysisCode = f'BOL_{lineIndex}'
            #[2-1]: Check Line Existence & Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue

            #[2-2]: nSamples & bandWidth & MAType
            nSamples  = cac[f'{analysisCode}_NSamples']
            bandWidth = cac[f'{analysisCode}_BandWidth']
            maType    = cac['BOL_MAType']
            if   type(nSamples) is not int:           invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < nSamples:                    invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if   not type(bandWidth) in (int, float): invalidLines[analysisCode].append("bandWidth: Must be type 'int' or 'float'")
            elif not (0 < bandWidth):                 invalidLines[analysisCode].append("bandWidth: Must be greater than 0")
            if   type(maType) is not str:             invalidLines[analysisCode].append("BOL_MAType: Must be type 'str'")
            elif maType not in ('SMA', 'WMA', 'EMA'): invalidLines[analysisCode].append("BOL_MAType: Must be 'SMA', 'WMA', or 'EMA'")
            if analysisCode in invalidLines: 
                continue

            #[2-3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex':    lineIndex,
                                 'MAType':       maType,
                                 'nSamples':     nSamples,
                                 'bandWidth':    bandWidth}

    #[3]: Return The Constructed Analysis Parameters & Invalid Lines
    return cap, invalidLines



def generate(intervalID, precisions, timestamp, klines, nSamples, MAType, bandWidth, analysisResults, **_):
    #[1]: Instances
    bols       = analysisResults
    pPrecision = precisions['price']
    func_gnitt = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl  = auxiliaries.getTimestampList_byNTicks

    #[2]: Previous Analysis & Analysis Count
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    bol_prev       = bols.get(timestamp_prev, None)
    mode           = 0 if bol_prev is None else bol_prev['mode']

    #[3]: BOL computation
    prices = [klines[ts][KLINDEX_CLOSEPRICE] if ts in klines else None
              for ts in func_gtsl(intervalID = intervalID,
                                  timestamp  = timestamp,
                                  nTicks     = nSamples,
                                  direction  = False)]

    #---[3-1]: MA
    #------[3-1-1]: SMA
    if MAType == 'SMA':
        if mode == 0:
            if any(p is None for p in prices):
                if bol_prev is None:
                    maComputation = None
                    ma            = None
                    mode          = 0
                else:
                    maComputation = bol_prev['MACOMPUTATION']
                    ma            = bol_prev['MA']
                    mode          = 0
            else:
                maComputation = sum(prices)
                ma            = round(maComputation / nSamples, pPrecision)
                mode          = 1
        else:
            timestamp_exp      = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -nSamples)
            maComputation_prev = bol_prev['MACOMPUTATION']
            price_exp  = klines[timestamp_exp][KLINDEX_CLOSEPRICE]
            price_this = klines[timestamp][KLINDEX_CLOSEPRICE]
            if price_exp is None or price_this is None:
                maComputation = None
                ma            = bol_prev['MA']
                mode          = 0
            else:
                maComputation = maComputation_prev - price_exp + price_this
                ma            = round(maComputation / nSamples, pPrecision)
                mode          = 1

    #------[3-1-2]: WMA
    elif MAType == 'WMA':
        if mode == 0:
            if any(p is None for p in prices):
                if bol_prev is None:
                    maComputation = (None, None)
                    ma            = None
                    mode          = 0
                else:
                    maComputation = bol_prev['MACOMPUTATION']
                    ma            = bol_prev['MA']
                    mode          = 0
            else:
                priceSum_simple   = sum(prices)
                priceSum_weighted = sum(p*(nSamples-pIdx) for pIdx, p in enumerate(prices))
                maComputation     = (priceSum_simple, priceSum_weighted)
                ma                = round(priceSum_weighted / (nSamples*(nSamples+1)/2), pPrecision)
                mode              = 1
        else:
            timestamp_exp                         = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -nSamples)
            priceSum_prev, priceSum_weighted_prev = bol_prev['MACOMPUTATION']
            price_exp  = klines[timestamp_exp][KLINDEX_CLOSEPRICE]
            price_this = klines[timestamp][KLINDEX_CLOSEPRICE]
            if price_exp is None or price_this is None:
                maComputation = (None, None)
                ma            = bol_prev['MA']
                mode          = 0
            else:
                priceSum_simple   = priceSum_prev          - price_exp     + price_this
                priceSum_weighted = priceSum_weighted_prev - priceSum_prev + (nSamples*price_this)
                maComputation     = (priceSum_simple, priceSum_weighted)
                ma                = round(priceSum_weighted / (nSamples*(nSamples+1)/2), pPrecision)
                mode              = 1

    #------[3-1-3]: EMA
    elif MAType == 'EMA':
        if mode == 0:
            if any(p is None for p in prices):
                if bol_prev is None:
                    ma   = None
                    mode = 0
                else:
                    ma   = bol_prev['MA']
                    mode = 0
            else:
                priceSum = sum(prices)
                ma       = round(priceSum / nSamples, pPrecision)
                mode     = 1
        else:
            emaVal_prev = bol_prev['MA']
            price_this  = klines[timestamp][KLINDEX_CLOSEPRICE]
            if price_this is None:
                ma   = emaVal_prev
                mode = 0
            else:
                kValue = 2/(nSamples+1)
                ma     = round((price_this*kValue) + (emaVal_prev*(1-kValue)), pPrecision)
                mode   = 1
        maComputation = None

    #---[3-2]: BOL
    if mode == 0:
        bol = None if bol_prev is None else bol_prev['BOL']
    elif mode == 1:
        dsSum = sum(math.pow(p-ma, 2) for p in prices)
        sd    = math.sqrt(dsSum/nSamples)
        bol    = (round(ma-sd*bandWidth, pPrecision), 
                    round(ma+sd*bandWidth, pPrecision))

    #[4]: Result formatting & Saving
    bolResult = {'MACOMPUTATION': maComputation,
                 'MA':            ma,
                 'BOL':           bol,
                 'mode':          mode}
    bols[timestamp] = bolResult

    #[5]: Memory Optimization References
    return (2,        #nAnalysisToKeep
            nSamples) #nKlinesToKeep
#ANALYSIS GENERATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#LINEARIZATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def linearize(intervalID, analysisCode, analysisResult):
    bol = analysisResult['BOL']
    if bol is None:
        lRes = {f'{intervalID}_{analysisCode}_BOLLOW':  None,
                f'{intervalID}_{analysisCode}_BOLHIGH': None,
                f'{intervalID}_{analysisCode}_MA':      None}
    else:
        lRes = {f'{intervalID}_{analysisCode}_BOLLOW':  bol[0],
                f'{intervalID}_{analysisCode}_BOLHIGH': bol[1],
                f'{intervalID}_{analysisCode}_MA':      analysisResult['MA']}
    return lRes
#LINEARIZATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYZER FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_maximum_market_data_reference_length(cac_iID):
    #[1]: Master Check
    if not cac_iID['BOL_Master']:
        return 0
    
    #[2]: MMDRL
    mmdrl = 0
    for lIdx in range (NMAXLINES):
        #[2-1]: Line Active Check
        if not cac_iID.get(f'BOL_{lIdx}_LineActive', False): 
            continue

        #[2-2]: MMDRL Update
        mmdrl = max(mmdrl, 
                    cac_iID[f'BOL_{lIdx}_NSamples'])

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
    oc['BOL_Master'] = False
    for lIdx in range (NMAXLINES):
        oc[f'BOL_{lIdx}_LineActive'] = False
        oc[f'BOL_{lIdx}_NSamples']   = 10*(lIdx+1)
        oc[f'BOL_{lIdx}_BandWidth']  = 2.0
        oc[f'BOL_{lIdx}_Width'] = 1
        oc[f'BOL_{lIdx}_ColorR%DARK'] =random.randint(64,255); oc[f'BOL_{lIdx}_ColorG%DARK'] =random.randint(64,255); oc[f'BOL_{lIdx}_ColorB%DARK'] =random.randint(64, 255); oc[f'BOL_{lIdx}_ColorA%DARK'] =255
        oc[f'BOL_{lIdx}_ColorR%LIGHT']=random.randint(64,255); oc[f'BOL_{lIdx}_ColorG%LIGHT']=random.randint(64,255); oc[f'BOL_{lIdx}_ColorB%LIGHT']=random.randint(64, 255); oc[f'BOL_{lIdx}_ColorA%LIGHT']=255
        oc[f'BOL_{lIdx}_Display'] = True
    oc['BOL_MAType']            = 'SMA'
    oc['BOL_DisplayCenterLine'] = True
    oc['BOL_DisplayBand']       = True

    #[3]: Configuration Return
    return oc



def cd_initialize_settings_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'INDICATOR_BLOCKTITLE_MATYPE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 90, 'anchor': 'SW'}))
    gList.append(({'NAME':               'INDICATOR_MATYPETEXT',
                   'TYPE':               'textBox_typeA',
                   'TEXTPACK':           'GUIO_CHARTDRAWER:MATYPE',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -650, 'width': 1550, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_MATYPESELECTION',
                   'TYPE':               'selectionBox_typeB',
                   'PAGEOBJECTFUNCTION': ['selectionUpdateFunction',],
                   'groupOrder': 2, 'xPos': 1650, 'yPos': -650, 'width': 2350, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'nDisplay': 4, 'name': 'BOL_MATypeSelection'}))
    gList.append(({'NAME':               'INDICATORINDEX_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1000, 'width': 800, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INDEX'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORINTERVAL_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':  900, 'yPos': -1000, 'width': 600, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORBANDWIDTH_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1600, 'yPos': -1000, 'width': 550, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:WIDTH'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORWIDTH_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2250, 'yPos': -1000, 'width': 550, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:WIDTH'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORCOLOR_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2900, 'yPos': -1000, 'width': 500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORDISPLAY_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3500, 'yPos': -1000, 'width': 500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAY'), 'fontSize': 90}))
    yPosPoint1 = -1000
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"INDICATOR_BOL{lIdx}",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 800, 'height': 250, 'style': 'styleB', 'text': f'BOL {lIdx}', 'fontSize': 80, 'name': f'BOL_LineActivationSwitch_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_BOL{lIdx}_INTERVALINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos':  900, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'BOL_IntervalTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_BOL{lIdx}_BANDWIDTHINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 1600, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 550, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'BOL_BandWidthTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_BOL{lIdx}_WIDTHINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 2250, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 550, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'BOL_WidthTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_BOL{lIdx}_LINECOLOR",
                       'TYPE':               'LED_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2900, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'mode': True}))
        gList.append(({'NAME':               f"INDICATOR_BOL{lIdx}_DISPLAY",
                       'TYPE':               'switch_typeB',
                       'PAGEOBJECTFUNCTION': ['releaseFunction',],
                       'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': f'BOL_DisplaySwitch_{lIdx}'}))
    yPosPoint2 = yPosPoint1-350*NMAXLINES
    gList.append(({'NAME':               'INDICATOR_BLOCKTITLE_DISPLAYCONTENTS',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint2-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAYCONTENTS'), 'fontSize': 90, 'anchor': 'SW'}))
    gList.append(({'NAME':               'INDICATOR_DISPLAYCONTENTS_BOLCENTERTEXT',
                   'TYPE':               'textBox_typeA',
                   'TEXTPACK':           'GUIO_CHARTDRAWER:MATYPE',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint2-700, 'width': 3400, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAYBOLCENTER'), 'fontSize': 80}))
    gList.append(({'NAME':               "INDICATOR_DISPLAYCONTENTS_BOLCENTERSWITCH",
                   'TYPE':               'switch_typeB',
                   'PAGEOBJECTFUNCTION': ['releaseFunction',],
                   'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint2-700, 'width': 500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': 'BOL_DisplayContentsSwitch_BolCenter'}))
    gList.append(({'NAME':               'INDICATOR_DISPLAYCONTENTS_BOLBANDTEXT',
                   'TYPE':               'textBox_typeA',
                   'TEXTPACK':           'GUIO_CHARTDRAWER:MATYPE',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint2-1050, 'width': 3400, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAYBOLBAND'), 'fontSize': 80}))
    gList.append(({'NAME':               "INDICATOR_DISPLAYCONTENTS_BOLBANDSWITCH",
                   'TYPE':               'switch_typeB',
                   'PAGEOBJECTFUNCTION': ['releaseFunction',],
                   'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint2-1050, 'width': 500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': 'BOL_DisplayContentsSwitch_BolBand'}))

    #[3]: Return GUIO Generation List
    return gList



def cd_initialize_settings_subpage_setup(subpage, fn_get_text_pack):
    maTypes = {'SMA': {'text': fn_get_text_pack('GUIO_CHARTDRAWER:MATYPE_SMA')},
               'WMA': {'text': fn_get_text_pack('GUIO_CHARTDRAWER:MATYPE_WMA')},
               'EMA': {'text': fn_get_text_pack('GUIO_CHARTDRAWER:MATYPE_EMA')}}
    subpage.GUIOs["INDICATOR_MATYPESELECTION"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
    subpage.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList  = {f"{lIdx}": {'text': f"BOL {lIdx}"} for lIdx in range (NMAXLINES)}, 
                                                                     displayTargets = 'all')



def cd_match_guios_to_config(mainPage, subPage, current_GUI_Theme, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    cgt        = current_GUI_Theme
    oc         = object_configuration

    #[2]: GUIOs Update
    guios_MAIN["MAININDICATOR_BOL"].setStatus(oc['BOL_Master'], callStatusUpdateFunction = False)
    guios_THIS["INDICATOR_MATYPESELECTION"].setSelected(oc['BOL_MAType'], callSelectionUpdateFunction = False)
    for lIdx in range (NMAXLINES):
        lActive = oc[f'BOL_{lIdx}_LineActive']
        nSamples   = oc[f'BOL_{lIdx}_NSamples']
        bandWidth  = oc[f'BOL_{lIdx}_BandWidth']
        width      = oc[f'BOL_{lIdx}_Width']
        color      = (oc[f'BOL_{lIdx}_ColorR%{cgt}'], 
                      oc[f'BOL_{lIdx}_ColorG%{cgt}'], 
                      oc[f'BOL_{lIdx}_ColorB%{cgt}'], 
                      oc[f'BOL_{lIdx}_ColorA%{cgt}'])
        display    = oc[f'BOL_{lIdx}_Display']
        guios_THIS[f"INDICATOR_BOL{lIdx}"].setStatus(lActive, callStatusUpdateFunction = False)
        guios_THIS[f"INDICATOR_BOL{lIdx}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_THIS[f"INDICATOR_BOL{lIdx}_BANDWIDTHINPUT"].updateText(text = f"{bandWidth:.1f}")
        guios_THIS[f"INDICATOR_BOL{lIdx}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_THIS[f"INDICATOR_BOL{lIdx}_LINECOLOR"].updateColor(*color)
        guios_THIS[f"INDICATOR_BOL{lIdx}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_THIS["INDICATOR_DISPLAYCONTENTS_BOLCENTERSWITCH"].setStatus(oc['BOL_DisplayCenterLine'], callStatusUpdateFunction = False)
    guios_THIS["INDICATOR_DISPLAYCONTENTS_BOLBANDSWITCH"].setStatus(oc['BOL_DisplayBand'], callStatusUpdateFunction = False)
    guios_THIS["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_THIS["APPLYNEWSETTINGS"].deactivate()



def cd_load_analysis_configuration(mainPage, subPage, analysis_configuration, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    ac = analysis_configuration
    oc = object_configuration

    #[2]: GUIOs Update
    if ac is not None and ac['BOL_Master']:
        guios_MAIN["MAININDICATOR_BOL"].activate()
        guios_MAIN["MAININDICATOR_BOL"].setStatus(status = oc['BOL_Master'], callStatusUpdateFunction = False)
        guios_MAIN["MAININDICATORSETUP_BOL"].activate()
        for lIdx in range (NMAXLINES):
            if ac[f'BOL_{lIdx}_LineActive']:
                nSamples = ac[f'BOL_{lIdx}_NSamples']
                bandWidth = ac[f'BOL_{lIdx}_BandWidth']
                width    = oc[f'BOL_{lIdx}_Width']
                display  = oc[f'BOL_{lIdx}_Display']
                guios_THIS[f"INDICATOR_BOL{lIdx}"].setStatus(status = True, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_BOL{lIdx}_INTERVALINPUT"].updateText(f"{nSamples}")
                guios_THIS[f"INDICATOR_BOL{lIdx}_BANDWIDTHINPUT"].updateText(f"{bandWidth:.1f}")
                guios_THIS[f"INDICATOR_BOL{lIdx}_WIDTHINPUT"].activate()
                guios_THIS[f"INDICATOR_BOL{lIdx}_WIDTHINPUT"].updateText(f"{width}")
                guios_THIS[f"INDICATOR_BOL{lIdx}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_BOL{lIdx }_DISPLAY"].activate()
            else:
                guios_THIS[f"INDICATOR_BOL{lIdx}"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_BOL{lIdx}_INTERVALINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_BOL{lIdx}_BANDWIDTHINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_BOL{lIdx}_WIDTHINPUT"].deactivate()
                guios_THIS[f"INDICATOR_BOL{lIdx}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_BOL{lIdx}_DISPLAY"].deactivate()
        guios_THIS["INDICATOR_MATYPESELECTION"].setSelected(itemKey = oc['BOL_MAType'], callSelectionUpdateFunction = False)
    else:
        guios_THIS["INDICATOR_MATYPESELECTION"].setSelected(itemKey = 'SMA', callSelectionUpdateFunction = False)
        guios_MAIN["MAININDICATOR_BOL"].setStatus(status = False, callStatusUpdateFunction = False)
        guios_MAIN["MAININDICATOR_BOL"].deactivate()
        guios_MAIN["MAININDICATORSETUP_BOL"].deactivate()



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
        color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_BOL{lineSelected}_LINECOLOR"].getColor()
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
        sub_page.GUIOs[f"INDICATOR_BOL{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
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
            updateTracker[lineIndex] = [False, False] #[1]: Draw CenterLine, [2]: Draw Band
            #Width
            width_previous = oc[f'BOL_{lineIndex}_Width']
            reset = False
            try:
                width = int(sub_page.GUIOs[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'BOL_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset == True:
                oc[f'BOL_{lineIndex}_Width'] = 1
                sub_page.GUIOs[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'BOL_{lineIndex}_Width']))
            if (width_previous != oc[f'BOL_{lineIndex}_Width']): 
                updateTracker[lineIndex][0] = True
            #Color
            color_previous = (oc[f'BOL_{lineIndex}_ColorR%{cgt}'],
                              oc[f'BOL_{lineIndex}_ColorG%{cgt}'],
                              oc[f'BOL_{lineIndex}_ColorB%{cgt}'],
                              oc[f'BOL_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_BOL{lineIndex}_LINECOLOR"].getColor()
            oc[f'BOL_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'BOL_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'BOL_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'BOL_{lineIndex}_ColorA%{cgt}'] = color_a
            if (color_previous != (color_r, color_g, color_b, color_a)): 
                updateTracker[lineIndex][0] = True
                updateTracker[lineIndex][1] = True
            #Line Display
            display_previous = oc[f'BOL_{lineIndex}_Display']
            oc[f'BOL_{lineIndex}_Display'] = sub_page.GUIOs[f"INDICATOR_BOL{lineIndex}_DISPLAY"].getStatus()
            if (display_previous != oc[f'BOL_{lineIndex}_Display']): 
                updateTracker[lineIndex][0] = True
                updateTracker[lineIndex][1] = True
        #---BOL Master
        bolMaster_previous = oc['BOL_Master']
        oc['BOL_Master'] = main_page.GUIOs["MAININDICATOR_BOL"].getStatus()
        if bolMaster_previous != oc['BOL_Master']:
            for lineIndex in updateTracker: 
                updateTracker[lineIndex][0] = True
                updateTracker[lineIndex][1] = True
        #---CenterLine Display Switch
        display_bolCenter_previous = oc['BOL_DisplayCenterLine']
        oc['BOL_DisplayCenterLine'] = sub_page.GUIOs["INDICATOR_DISPLAYCONTENTS_BOLCENTERSWITCH"].getStatus()
        if display_bolCenter_previous != oc['BOL_DisplayCenterLine']: 
            for lineIndex in updateTracker: updateTracker[lineIndex][0] = True
        #---Band Display Switch
        display_bolBand_previous = oc['BOL_DisplayBand']
        oc['BOL_DisplayBand'] = sub_page.GUIOs["INDICATOR_DISPLAYCONTENTS_BOLBANDSWITCH"].getStatus()
        if display_bolBand_previous != oc['BOL_DisplayBand']: 
            for lineIndex in updateTracker: updateTracker[lineIndex][1] = True
        #Queue Update
        for line in [aCode for aCode in analysis_parameters if aCode.startswith('BOL')]:
            lineIndex = analysis_parameters[line]['lineIndex']
            drawSignal = 0
            drawSignal += 0b01*updateTracker[lineIndex][0] #CenterLine
            drawSignal += 0b10*updateTracker[lineIndex][1] #Band
            if drawSignal:
                chart_drawer._drawer_RemoveDrawings(analysisCode    = line, gRemovalSignal = drawSignal) #Remove previous graphics
                chart_drawer.addBufferZone_toDrawQueue(analysisCode = line, drawSignal     = drawSignal) #Update draw queue
        #Control Buttons Handling
        sub_page.GUIOs['APPLYNEWSETTINGS'].deactivate()
        activate_save_configuration = True

    #[3]: Analysis Related
    #---[3-1]: Line Activation Switch
    elif setter == 'LineActivationSwitch': 
        lineIndex = int(guio_name_split[2])
        #Get new switch status
        _newStatus = sub_page.GUIOs[f"INDICATOR_BOL{lineIndex}"].getStatus()
        oc[f'BOL_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True
    
    #---[3-2]: Interval Text Input Box
    elif setter == 'IntervalTextInputBox': 
        lineIndex = int(guio_name_split[2])
        #Get new nSamples
        try:    _nSamples = int(sub_page.GUIOs[f"INDICATOR_BOL{lineIndex}_INTERVALINPUT"].getText())
        except: _nSamples = None
        #Save the new value to the object config dictionary
        oc[f'BOL_{lineIndex}_NSamples'] = _nSamples
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-3]: BandWidth Text Input Box
    elif setter == 'BandWidthTextInputBox': 
        lineIndex = int(guio_name_split[2])
        #Get new bandwidth
        try:    bandWidth = int(sub_page.GUIOs[f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT"].getText())
        except: bandWidth = None
        #Save the new value to the object config dictionary
        oc[f'BOL_{lineIndex}_BandWidth'] = bandWidth
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-4]: MA Type Selection Box
    elif setter == 'MATypeSelection': 
        #Get new MAType
        maType = sub_page.GUIOs["INDICATOR_MATYPESELECTION"].getSelected()
        #Save the new value to the object config dictionary
        oc['BOL_MAType'] = maType
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #[3]: Return Status Flag
    return activate_save_configuration



def cd_on_position_highlight_update(chart_drawer):
    pass



def cd_on_position_selection_update(chart_drawer):
    pass
 


def cd_check_vertical_extremas(chart_drawer):
    pass



def cd_draw(chart_drawer, drawSignal, timestamp, analysisCode):
    #[1]: Parameters
    oc    = chart_drawer.objectConfig
    ap    = chart_drawer.analysisParams[chart_drawer.intervalID][analysisCode]
    cgt   = chart_drawer.currentGUITheme
    rclcg = chart_drawer.displayBox_graphics['KLINESPRICE']['RCLCG']
    lineIndex = ap['lineIndex']

    #[2]: Master & Display Status
    if not oc['BOL_Master']:               return 0b00
    if not oc[f'BOL_{lineIndex}_Display']: return 0b00

    #[3]: Draw Signal
    if drawSignal is None: drawSignal = 0b11
    if not drawSignal:     return 0b00

    #[4]: Data Acquisition
    bols = chart_drawer._data_agg[chart_drawer.intervalID][analysisCode]
    timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = chart_drawer.intervalID, timestamp = timestamp, nTicks = -1)
    bolResult_prev = bols.get(timestamp_prev, None)
    bolResult      = bols[timestamp]

    #[5]: Drawing
    drawn = 0b00
    #---[5-1]: Center Line
    if drawSignal&0b01 and oc['BOL_DisplayCenterLine']:
        #[5-1-1]: Previous Drawing Removal
        rclcg.removeShape(shapeName = timestamp, groupName = analysisCode+'_LINE')
        #[5-1-2]: Drawing
        if (bolResult_prev is not None) and (bolResult_prev['MA'] is not None):
            #Shape Object Params
            timestampWidth = timestamp-timestamp_prev
            shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
            shape_x2 = round(timestamp     +timestampWidth/2, 1)
            shape_y2 = bolResult['MA']
            width    = oc[f'BOL_{lineIndex}_Width']
            color = (oc[f'BOL_{lineIndex}_ColorR%{cgt}'],
                     oc[f'BOL_{lineIndex}_ColorG%{cgt}'],
                     oc[f'BOL_{lineIndex}_ColorB%{cgt}'],
                     255)
            #Shape Adding
            rclcg.addShape_Line(x  = shape_x1, y  = bolResult_prev['MA'],
                                x2 = shape_x2, y2 = shape_y2,
                                width = width,
                                color = color,
                                shapeName = timestamp, shapeGroupName = f"{analysisCode}_LINE", layerNumber = 13+lineIndex)
        #[5-1-3]: Drawn Flag Update
        drawn += 0b01
    #---[5-2]: Band
    if drawSignal&0b10 and oc['BOL_DisplayBand']:
        #[5-2-1]: Previous Drawing Removal
        rclcg.removeShape(shapeName = timestamp, groupName = analysisCode+'_BAND')
        #[5-2-2]: Drawing
        if (bolResult_prev is not None) and (bolResult_prev['BOL'] is not None):
            #Shape Object Params
            timestampWidth = timestamp-timestamp_prev
            shape_x1 = round(timestamp_prev+timestampWidth/2, 1)
            shape_x2 = round(timestamp     +timestampWidth/2, 1)
            br_bol_prev = bolResult_prev['BOL']
            br_bol      = bolResult['BOL']
            coordinates = ((shape_x1, br_bol_prev[0]),
                           (shape_x2, br_bol[0]),
                           (shape_x2, br_bol[1]),
                           (shape_x1, br_bol_prev[1]))
            color = (oc[f'BOL_{lineIndex}_ColorR%{cgt}'],
                     oc[f'BOL_{lineIndex}_ColorG%{cgt}'],
                     oc[f'BOL_{lineIndex}_ColorB%{cgt}'],
                     oc[f'BOL_{lineIndex}_ColorA%{cgt}'])
            #Shape Adding
            rclcg.addShape_Polygon(coordinates = coordinates, 
                                    color = color,
                                    shapeName = timestamp, shapeGroupName = f"{analysisCode}_BAND", layerNumber = 0+lineIndex)
        #[5-2-3]: Drawn Flag Update
        drawn += 0b10
        
    #[6]: Return Drawn Flag
    return drawn



def cd_remove_expired_drawings(display_box_graphics, si_viewer_index, analysis_code, timestamp):
    #[1]: Drawings Removal
    display_box_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = f"{analysis_code}_LINE")
    display_box_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = f"{analysis_code}_BAND")



def cd_remove_drawings(drawn, display_box_graphics, si_viewer_index, analysis_code, graphics_removal_signal):
    #[1]: Drawings Removal
    if graphics_removal_signal&0b1: 
        if graphics_removal_signal&0b01: display_box_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = f"{analysis_code}_LINE")
        if graphics_removal_signal&0b10: display_box_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = f"{analysis_code}_BAND")



def cd_get_vertical_magnitude_anchor(object_configuration):
    return None



def cd_on_GUI_theme_update(subpage, object_configuration, current_GUI_theme):
    #[1]: Instances
    sp  = subpage
    oc  = object_configuration
    cgt = current_GUI_theme

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        sp.GUIOs[f"INDICATOR_BOL{lIdx}_LINECOLOR"].updateColor(oc[f'BOL_{lIdx}_ColorR%{cgt}'], 
                                                               oc[f'BOL_{lIdx}_ColorG%{cgt}'], 
                                                               oc[f'BOL_{lIdx}_ColorB%{cgt}'], 
                                                               oc[f'BOL_{lIdx}_ColorA%{cgt}'])



def cd_update_si_type_analysis_codes(analysis_parameters):
    return None



def cd_type_init(subPage):
    #[1]: Instances
    guios_THIS = subPage.GUIOs

    #[2]: GUIOs Update
    guios_THIS["INDICATOR_MATYPESELECTION"].deactivate()
    for lIdx in range (NMAXLINES):
        guios_THIS[f"INDICATOR_BOL{lIdx}"].deactivate()
        guios_THIS[f"INDICATOR_BOL{lIdx}_INTERVALINPUT"].deactivate()
        guios_THIS[f"INDICATOR_BOL{lIdx}_BANDWIDTHINPUT"].deactivate()
#CHART DRAWER FUNCTIONS END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUTOTRADE PAGE FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_autotrade_get_default_analysis_configuration():
    #[1]: Default Analysis Configuration
    dac = dict()

    #[2]: Setup
    dac['BOL_Master'] = False
    dac['BOL_MAType'] = 'SMA'
    for lineIndex in range (NMAXLINES):
        dac[f'BOL_{lineIndex}_LineActive'] = False
        dac[f'BOL_{lineIndex}_NSamples']   = 10*(lineIndex+1)
        dac[f'BOL_{lineIndex}_BandWidth']  = 2.0

    #[3]: Return
    return dac



def pg_autotrade_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'BOLMATYPETITLETEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -350, 'width': 2450, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_BOLMATYPE'), 'fontSize': 80}))
    gList.append(({'NAME':               'BOLMATYPESELECTIONBOX',
                   'TYPE':               'selectionBox_typeB',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 2, 'xPos': 2550, 'yPos': -350, 'width': 2000, 'height': 250, 'style': 'styleA', 'nDisplay': 3, 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_INDEX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -650, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1750, 'yPos': -650, 'width': 1350, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_BANDWIDTH',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3200, 'yPos': -650, 'width': 1350, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_BANDWIDTH'), 'fontSize': 80}))
    yPosPoint1 = -650
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"BOL_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1650, 'height': 250, 'style': 'styleB', 'text': f'BOL {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"BOL_{lIdx}_NSAMPLES",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 1750, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1350, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
        gList.append(({'NAME':               f"BOL_{lIdx}_BANDWIDTH",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 3200, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1350, 'height': 250, 'style': 'styleA', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_autotrade_configure_subpage_setup(subpage, fn_get_text_pack):
    maTypes = {'SMA': {'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_SMA')},
               'WMA': {'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_WMA')},
               'EMA': {'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_EMA')}}
    subpage.GUIOs["BOLMATYPESELECTIONBOX"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
      


def pg_autotrade_load_analysis_configuration(mainPage, subPage, analysis_configuration):
    #[1]: Main Page
    mainPage.GUIOs["INDICATORMASTERSWITCH_BOL"].setStatus(status = analysis_configuration['BOL_Master'], callStatusUpdateFunction = False)

    #[2]: Sub Page
    subPage.GUIOs["BOLMATYPESELECTIONBOX"].setSelected(itemKey = analysis_configuration['BOL_MAType'], callSelectionUpdateFunction = False)
    for lIdx in range (NMAXLINES):
        #[2-1]: Configuration Retrieval
        if f'BOL_{lIdx}_LineActive' in analysis_configuration:
            lineActive = analysis_configuration[f'BOL_{lIdx}_LineActive']
            nSamples  = analysis_configuration[f'BOL_{lIdx}_NSamples']
            bandwidth = analysis_configuration[f'BOL_{lIdx}_BandWidth']
        else:
            lineActive = False
            nSamples  = 10*(lIdx+1)
            bandwidth = 2.0

        #[2-2]: GUIOs Update
        subPage.GUIOs[f"BOL_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        subPage.GUIOs[f"BOL_{lIdx}_NSAMPLES"].updateText(text = f"{nSamples}")
        subPage.GUIOs[f"BOL_{lIdx}_BANDWIDTH"].updateText(text = f"{bandwidth:.1f}")



def pg_autotrade_format_analysis_configuration_from_guios(mainPage, subPage):
    #[1]: Instances
    configuration = dict()

    #[2]: Configuration Construction
    configuration['BOL_Master'] = mainPage.GUIOs["INDICATORMASTERSWITCH_BOL"].getStatus()
    configuration['BOL_MAType'] = subPage.GUIOs["BOLMATYPESELECTIONBOX"].getSelected()
    for lineIndex in range (NMAXLINES):
        configuration[f'BOL_{lineIndex}_LineActive'] = subPage.GUIOs[f"BOL_{lineIndex}_LINE"].getStatus()
        configuration[f'BOL_{lineIndex}_NSamples']   = int(subPage.GUIOs[f"BOL_{lineIndex}_NSAMPLES"].getText())
        configuration[f'BOL_{lineIndex}_BandWidth']  = round(float(subPage.GUIOs[f"BOL_{lineIndex}_BANDWIDTH"].getText()), 1)

    #[3]: Return Configuration
    return configuration
#AUTOTRADE PAGE FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SIMULATION RESULTS PAGE FUNCTIONS ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_simulation_result_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'BOLMATYPETITLETEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -350, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_BOLMATYPE'), 'fontSize': 80}))
    gList.append(({'NAME':               'BOLMATYPEDISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 2, 'xPos': 2625, 'yPos': -350, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_INDEX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 0, 'yPos': -650, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1750, 'yPos': -650, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_BANDWIDTH',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3500, 'yPos': -650, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_BANDWIDTH'), 'fontSize': 80}))
    yPosPoint1 = -650
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"BOL_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1650, 'height': 250, 'style': 'styleB', 'text': f'BOL {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"BOL_{lIdx}_NSAMPLES",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 1750, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1650, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
        gList.append(({'NAME':               f"BOL_{lIdx}_BANDWIDTH",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1650, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_simulation_result_configure_subpage_setup(subpage, fn_get_text_pack):
    for lIdx in range (NMAXLINES):
        subpage.GUIOs[f"BOL_{lIdx}_LINE"].deactivate()



def pg_simulation_result_load_analysis_configuration(mainPage, subPage, analysis_configuration, simulation_selected, fn_get_text_pack):
    if simulation_selected:
        #MAIN
        mainPage.GUIOs["INDICATORMASTERSWITCH_BOL"].setStatus(status = analysis_configuration['BOL_Master'], callStatusUpdateFunction = False)
        
        #BOL
        subPage.GUIOs["BOLMATYPEDISPLAYTEXT"].updateText(text = fn_get_text_pack(f'SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_{analysis_configuration["BOL_MAType"]:s}'))
        for lIdx in range (NMAXLINES):
            lineActive = analysis_configuration.get(f'BOL_{lIdx}_LineActive', False)
            if lineActive: 
                nSamples_str  = f"{analysis_configuration[f'BOL_{lIdx}_NSamples']}"
                bandWidth_str = f"{analysis_configuration[f'BOL_{lIdx}_BandWidth']:.1f}"
            else:          
                nSamples_str  = "-"
                bandWidth_str = "-"
            subPage.GUIOs[f"BOL_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
            subPage.GUIOs[f"BOL_{lIdx}_NSAMPLES"].updateText(text  = nSamples_str)
            subPage.GUIOs[f"BOL_{lIdx}_BANDWIDTH"].updateText(text = bandWidth_str)
    else:
        #MAIN
        mainPage.GUIOs["INDICATORMASTERSWITCH_BOL"].setStatus(status = False, callStatusUpdateFunction = False)
        
        #BOL
        subPage.GUIOs["BOLMATYPEDISPLAYTEXT"].updateText(text = "-")
        for lIdx in range (NMAXLINES):
            subPage.GUIOs[f"BOL_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
            subPage.GUIOs[f"BOL_{lIdx}_NSAMPLES"].updateText(text  = "-")
            subPage.GUIOs[f"BOL_{lIdx}_BANDWIDTH"].updateText(text = "-")
#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------