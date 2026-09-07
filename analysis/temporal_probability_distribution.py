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

DEPTHBINS = constants.DEPTHBINS
DEPTHBINS_MIN = min(db[0] for db in DEPTHBINS.values())
DEPTHBINS_MAX = max(db[1] for db in DEPTHBINS.values())




#DEFINING PARAMETERS ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ANALYSIS_CODE = 'TPD'
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
    if cac['TPD_Master']:
        for lineIndex in range (NMAXLINES):
            analysisCode = f'TPD_{lineIndex}'
            #[1]: Check Line Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue
            #[2]: Parameters
            viewLength = cac[f'{analysisCode}_ViewLength']
            nSamples   = cac[f'{analysisCode}_NSamples']
            nSamplesMA = cac[f'{analysisCode}_NSamplesMA']
            if   type(viewLength) is not int: invalidLines[analysisCode].append("viewLength: Must be type 'int'")
            elif not 1 < viewLength:          invalidLines[analysisCode].append("viewLength: Must be greater than 1")
            if   type(nSamples) is not int:   invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < nSamples:            invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if   type(nSamplesMA) is not int: invalidLines[analysisCode].append("nSamplesMA: Must be type 'int'")
            elif not 1 < nSamplesMA:          invalidLines[analysisCode].append("nSamplesMA: Must be greater than 1")
            if analysisCode in invalidLines: continue
            #[3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex':    lineIndex,
                                 'viewLength':   viewLength,
                                 'nSamples':     nSamples,
                                 'nSamplesMA':   nSamplesMA}

    #[3]: Return The Constructed Analysis Parameters & Invalid Lines
    return cap, invalidLines



def generate(intervalID, timestamp, klines, viewLength, nSamples, nSamplesMA, analysisResults, **_):
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
#ANALYSIS GENERATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#LINEARIZATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def linearize(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_TPD':         analysisResult['TPD'],
            f'{intervalID}_{analysisCode}_TPDABSMA':    analysisResult['TPD_ABSMA'],
            f'{intervalID}_{analysisCode}_TPDABSMAREL': analysisResult['TPD_ABSMAREL']}
    return lRes
#LINEARIZATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYZER FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_maximum_market_data_reference_length(cac_iID):
    #[1]: Master Check
    if not cac_iID['TPD_Master']:
        return 0
    
    #[2]: MMDRL
    mmdrl = 0
    for lIdx in range (NMAXLINES):
        #[2-1]: Line Active Check
        if not cac_iID.get(f'TPD_{lIdx}_LineActive', False): 
            continue

        #[2-2]: MMDRL Update
        viewLength = cac_iID[f'TPD_{lIdx}_ViewLength']
        nSamples   = cac_iID[f'TPD_{lIdx}_NSamples']
        nSamplesMA = cac_iID[f'TPD_{lIdx}_NSamplesMA']
        mmdrl = max(mmdrl, 
                    viewLength+nSamples+nSamplesMA-1)

    #[3]: Return MMDRL
    return mmdrl
#ANALYZER FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#CHART DRAWER FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
CD_FULL_DRAW_SIGNALS        = 0b1
CD_VVR_PRECISIONCOMPENSATOR = -2
CD_VVR_CENTERVALUE          = {('TPD', 'TPD'):          0,
                               ('TPD', 'TPD_ABSMA'):    0,
                               ('TPD', 'TPD_ABSMAREL'): 0}
CD_VVR_DEFAULT              = {('TPD', 'TPD'):          (-1, 1),
                               ('TPD', 'TPD_ABSMA'):    ( 0, 1),
                               ('TPD', 'TPD_ABSMAREL'): (-1, 1)}



def cd_get_initial_configuration():
    #[1]: Indicator Configuration
    oc = dict()

    #[2]: Configuration Setup
    oc['TPD_Master']      = False
    oc['TPD_DisplayType'] = 'TPD'
    for lIdx in range (NMAXLINES):
        oc[f'TPD_{lIdx}_LineActive'] = False
        oc[f'TPD_{lIdx}_ViewLength'] = 10 *(lIdx+1)
        oc[f'TPD_{lIdx}_NSamples']   = 100*(lIdx+1)
        oc[f'TPD_{lIdx}_NSamplesMA'] = 20 *(lIdx+1)
        oc[f'TPD_{lIdx}_Width'] = 1
        oc[f'TPD_{lIdx}_ColorR%DARK'] =random.randint(64,255); oc[f'TPD_{lIdx}_ColorG%DARK'] =random.randint(64,255); oc[f'TPD_{lIdx}_ColorB%DARK'] =random.randint(64, 255); oc[f'TPD_{lIdx}_ColorA%DARK'] =255
        oc[f'TPD_{lIdx}_ColorR%LIGHT']=random.randint(64,255); oc[f'TPD_{lIdx}_ColorG%LIGHT']=random.randint(64,255); oc[f'TPD_{lIdx}_ColorB%LIGHT']=random.randint(64, 255); oc[f'TPD_{lIdx}_ColorA%LIGHT']=255
        oc[f'TPD_{lIdx}_Display'] = True

    #[3]: Configuration Return
    return oc



def cd_initialize_settings_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'INDICATOR_BLOCKTITLE_DISPLAY',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:TPDDISPLAY'), 'fontSize': 90, 'anchor': 'SW'}))
    gList.append(({'NAME':               'INDICATOR_DISPLAYTYPE_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -650, 'width': 1500, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAYTYPE'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_DISPLAYTYPE_SELECTION',
                   'TYPE':               'selectionBox_typeB',
                   'PAGEOBJECTFUNCTION': ['selectionUpdateFunction',],
                   'groupOrder': 2, 'xPos': 1600, 'yPos': -650, 'width': 2400, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'nDisplay': 3, 'name': 'TPD_DisplayTypeSelectionBox'}))
    gList.append(({'NAME':               'INDICATORINDEX_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -950, 'width': 600, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INDEX'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORVIEWLENGTH_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':  700, 'yPos': -950, 'width': 500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:VIEWLENGTH'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORINTERVAL_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1300, 'yPos': -950, 'width': 500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INTERVALSHORT'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORMAINTERVAL_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1900, 'yPos': -950, 'width': 500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:MAINTERVAL'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORWIDTH_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2500, 'yPos': -950, 'width': 400, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:WIDTH'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORCOLOR_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3000, 'yPos': -950, 'width': 400, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORDISPLAY_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3500, 'yPos': -950, 'width': 500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAY'), 'fontSize': 90}))
    yPosPoint1 = -950
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"INDICATOR_TPD{lIdx}",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 600, 'height': 250, 'style': 'styleB', 'text': f'TPD {lIdx}', 'fontSize': 80, 'name': f'TPD_LineActivationSwitch_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_TPD{lIdx}_VIEWLENGTHINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos':  700, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'TPD_ViewLengthTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_TPD{lIdx}_INTERVALINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 1300, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'TPD_IntervalTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_TPD{lIdx}_MAINTERVALINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 1900, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'TPD_MAIntervalTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_TPD{lIdx}_WIDTHINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 2500, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 400, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'TPD_WidthTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_TPD{lIdx}_LINECOLOR",
                       'TYPE':               'LED_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 3000, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 400, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'mode': True}))
        gList.append(({'NAME':               f"INDICATOR_TPD{lIdx}_DISPLAY",
                       'TYPE':               'switch_typeB',
                       'PAGEOBJECTFUNCTION': ['releaseFunction',],
                       'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': f'TPD_DisplaySwitch_{lIdx}'}))

    #[3]: Return GUIO Generation List
    return gList



def cd_initialize_settings_subpage_setup(subpage, fn_get_text_pack):
    displayTypes = {'TPD':          {'text': 'TPD'},
                    'TPD_ABSMA':    {'text': 'TPD_ABSMA'},
                    'TPD_ABSMAREL': {'text': 'TPD_ABSMAREL'}}
    subpage.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].setSelectionList(selectionList = displayTypes, displayTargets = 'all')
    subpage.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList  = {f"{lIdx}": {'text': f"TPD {lIdx}"} for lIdx in range (NMAXLINES)}, 
                                                                     displayTargets = 'all')



def cd_match_guios_to_config(mainPage, subPage, current_GUI_Theme, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    cgt        = current_GUI_Theme
    oc         = object_configuration

    #[2]: GUIOs Update
    guios_MAIN["SUBINDICATOR_TPD"].setStatus(oc['TPD_Master'], callStatusUpdateFunction = False)
    guios_THIS["INDICATOR_DISPLAYTYPE_SELECTION"].setSelected(itemKey = oc['TPD_DisplayType'], callSelectionUpdateFunction = False)
    for lIdx in range (NMAXLINES):
        lineActive = oc[f'TPD_{lIdx}_LineActive']
        viewLength = oc[f'TPD_{lIdx}_ViewLength']
        nSamples   = oc[f'TPD_{lIdx}_NSamples']
        nSamplesMA = oc[f'TPD_{lIdx}_NSamplesMA']
        width      = oc[f'TPD_{lIdx}_Width']
        color      = (oc[f'TPD_{lIdx}_ColorR%{cgt}'],
                      oc[f'TPD_{lIdx}_ColorG%{cgt}'],
                      oc[f'TPD_{lIdx}_ColorB%{cgt}'],
                      oc[f'TPD_{lIdx}_ColorA%{cgt}'])
        display    = oc[f'TPD_{lIdx}_Display']
        guios_THIS[f"INDICATOR_TPD{lIdx}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_THIS[f"INDICATOR_TPD{lIdx}_VIEWLENGTHINPUT"].updateText(text = f"{viewLength}")
        guios_THIS[f"INDICATOR_TPD{lIdx}_INTERVALINPUT"].updateText(text   = f"{nSamples}")
        guios_THIS[f"INDICATOR_TPD{lIdx}_MAINTERVALINPUT"].updateText(text = f"{nSamplesMA}")
        guios_THIS[f"INDICATOR_TPD{lIdx}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_THIS[f"INDICATOR_TPD{lIdx}_LINECOLOR"].updateColor(*color)
        guios_THIS[f"INDICATOR_TPD{lIdx}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_THIS["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_THIS["APPLYNEWSETTINGS"].deactivate()



def cd_load_analysis_configuration(mainPage, subPage, analysis_configuration, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    ac = analysis_configuration
    oc = object_configuration

    #[2]: GUIOs Update
    if ac is not None and ac['TPD_Master']:
        guios_MAIN["SUBINDICATOR_TPD"].activate()
        guios_MAIN["SUBINDICATOR_TPD"].setStatus(status = oc['TPD_Master'], callStatusUpdateFunction = False)
        guios_MAIN["SUBINDICATORSETUP_TPD"].activate()
        for lineIndex in range (NMAXLINES):
            if ac[f'TPD_{lineIndex}_LineActive']:
                viewLength = ac[f'TPD_{lineIndex}_ViewLength']
                nSamples   = ac[f'TPD_{lineIndex}_NSamples']
                nSamplesMA = ac[f'TPD_{lineIndex}_NSamplesMA']
                width      = oc[f'TPD_{lineIndex}_Width']
                display    = oc[f'TPD_{lineIndex}_Display']
                guios_THIS[f"INDICATOR_TPD{lineIndex}"].setStatus(status = True)
                guios_THIS[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].updateText(f"{viewLength}")
                guios_THIS[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                guios_THIS[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].updateText(f"{nSamplesMA}")
                guios_THIS[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].activate()
                guios_THIS[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                guios_THIS[f"INDICATOR_TPD{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_TPD{lineIndex}_DISPLAY"].activate()
            else:
                guios_THIS[f"INDICATOR_TPD{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].deactivate()
                guios_THIS[f"INDICATOR_TPD{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_TPD{lineIndex}_DISPLAY"].deactivate()
    else:
        guios_MAIN["SUBINDICATOR_TPD"].setStatus(status = False, callStatusUpdateFunction = False)
        guios_MAIN["SUBINDICATOR_TPD"].deactivate()
        guios_MAIN["SUBINDICATORSETUP_TPD"].deactivate()



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
        color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_TPD{lineSelected}_LINECOLOR"].getColor()
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
        sub_page.GUIOs[f"INDICATOR_TPD{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        sub_page.GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        sub_page.GUIOs['APPLYNEWSETTINGS'].activate()

    #---[2-4]: WidthTextInputBox
    elif setter == 'WidthTextInputBox': 
        sub_page.GUIOs['APPLYNEWSETTINGS'].activate()
        
    #---[2-5]: DisplaySwitch
    elif setter == 'DisplaySwitch':     
        sub_page.GUIOs['APPLYNEWSETTINGS'].activate()
        
    #---[2-6]: DisplayType
    elif setter == 'DisplayTypeSelectionBox':
        sub_page.GUIOs['APPLYNEWSETTINGS'].activate()
        
    #---[2-7]: ApplySettings
    elif setter == 'ApplySettings':     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (NMAXLINES):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'TPD_{lineIndex}_Width']
            reset = False
            try:
                width = int(sub_page.GUIOs[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'TPD_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'TPD_{lineIndex}_Width'] = 1
                sub_page.GUIOs[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'TPD_{lineIndex}_Width']))
            if width_previous != oc[f'TPD_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'TPD_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'TPD_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'TPD_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'TPD_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_TPD{lineIndex}_LINECOLOR"].getColor()
            oc[f'TPD_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'TPD_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'TPD_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'TPD_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'TPD_{lineIndex}_Display']
            oc[f'TPD_{lineIndex}_Display'] = sub_page.GUIOs[f"INDICATOR_TPD{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'TPD_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---TPD Master
        tpdMaster_previous = oc['TPD_Master']
        oc['TPD_Master'] = main_page.GUIOs["SUBINDICATOR_TPD"].getStatus()
        if tpdMaster_previous != oc['TPD_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #---Display Type
        displayType_prev = oc['TPD_DisplayType']
        oc['TPD_DisplayType'] = sub_page.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].getSelected()
        if displayType_prev != oc['TPD_DisplayType']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = chart_drawer.siTypes_siViewerAlloc['VOL']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in chart_drawer.displayBox_graphics_visibleSIViewers:
                if cd_check_vertical_extremas(chart_drawer): 
                    chart_drawer._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        for line in [aCode for aCode in analysis_parameters if aCode.startswith('TPD')]:
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
        _newStatus = sub_page.GUIOs[f"INDICATOR_TPD{lineIndex}"].getStatus()
        oc[f'TPD_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-2]: View Length Text Input Box
    elif setter == 'ViewLengthTextInputBox': 
        lineIndex = int(guio_name_split[2])
        #Get new nSamples
        try:    viewLength = int(sub_page.GUIOs[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].getText())
        except: viewLength = None
        #Save the new value to the object config dictionary
        oc[f'TPD_{lineIndex}_ViewLength'] = viewLength
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-3]: Interval Text Input Box
    elif setter == 'IntervalTextInputBox': 
        lineIndex = int(guio_name_split[2])
        #Get new nSamples
        try:    nSamples = int(sub_page.GUIOs[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'TPD_{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-4]: MA Interval Text Input Box
    elif setter == 'MAIntervalTextInputBox': 
        lineIndex = int(guio_name_split[2])
        #Get new nSamples
        try:    nSamplesMA = int(sub_page.GUIOs[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].getText())
        except: nSamplesMA = None
        #Save the new value to the object config dictionary
        oc[f'TPD_{lineIndex}_NSamplesMA'] = nSamplesMA
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
    siViewerIndex   = chart_drawer.siTypes_siViewerAlloc['TPD']
    dBox_g_this_dt1 = chart_drawer.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

    #[2]: Base Text & Styles
    text_display = f" [SI{siViewerIndex} - TPD]"
    text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

    #[3]: Text Construction
    if oc['TPD_Master']:
        for aCode in chart_drawer.siTypes_analysisCodes['TPD']:
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
                newLine_style = chart_drawer.effectiveTextStyle['CONTENT_DEFAULT'].copy()
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



def cd_on_position_selection_update(chart_drawer):
    pass



def cd_check_vertical_extremas(chart_drawer):
    #[1]: References
    oc          = chart_drawer.objectConfig
    dispType    = oc['TPD_DisplayType']
    ap          = chart_drawer.analysisParams[chart_drawer.intervalID]
    dAgg        = chart_drawer._data_agg[chart_drawer.intervalID]
    hvr_tssInVR = chart_drawer.horizontalViewRange_timestampsInViewRange
    siViewerIndex = chart_drawer.siTypes_siViewerAlloc['TPD']
    siViewerCode  = f"SIVIEWER{siViewerIndex}"

    #[2]: Timestamps Check
    if not hvr_tssInVR: return False

    #[3]: Extremas Search
    #---Analysis Codes To Consider
    searchTargets = [(dType, dispType) 
                    for dType in chart_drawer.siTypes_analysisCodes['TPD'] 
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
        valMin, valMax = chart_drawer.vvr_extrema_converters['centered'](val_min = valMin, val_max = valMax, center = CD_VVR_CENTERVALUE[('TPD', dispType)])
    elif dispType == 'TPD_ABSMA':
        valMin, valMax = chart_drawer.vvr_extrema_converters['above_zero'](val_min = valMin, val_max = valMax)

    #[4]: Change Check & Result Return
    return chart_drawer.cve_check_new_vertical_values(val_min               = valMin,
                                                      val_max               = valMax,
                                                      target                = siViewerCode,
                                                      precision_compensator = CD_VVR_PRECISIONCOMPENSATOR)



def cd_draw(chart_drawer, drawSignal, timestamp, analysisCode):
    #[1]: Parameters
    oc    = chart_drawer.objectConfig
    ap    = chart_drawer.analysisParams[chart_drawer.intervalID][analysisCode]
    cgt   = chart_drawer.currentGUITheme
    rclcg = chart_drawer.displayBox_graphics['KLINESPRICE']['RCLCG']
    lineIndex = ap['lineIndex']
    siViewerIndex = chart_drawer.siTypes_siViewerAlloc['TPD']
    siViewerCode  = f'SIVIEWER{siViewerIndex}'
    rclcg         = chart_drawer.displayBox_graphics[siViewerCode]['RCLCG']

    #[2]: Master & Display Status
    if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
    if not oc['TPD_Master']:                      return 0b0
    if not oc[f'TPD_{lineIndex}_Display']:        return 0b0
    
    #[3]: Draw Signal
    if drawSignal is None: drawSignal = 0b1
    if not drawSignal:     return 0b0

    #[4]: Data Acquisition
    tpds = chart_drawer._data_agg[chart_drawer.intervalID][analysisCode]
    timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = chart_drawer.intervalID, timestamp = timestamp, nTicks = -1)
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



def cd_remove_expired_drawings(display_box_graphics, si_viewer_index, analysis_code, timestamp):
    #[1]: SI Viewer Check
    if si_viewer_index is None:
        return

    #[2]: Drawings Removal
    display_box_graphics[f"SIVIEWER{si_viewer_index}"]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysis_code)



def cd_remove_drawings(drawn, display_box_graphics, si_viewer_index, analysis_code, graphics_removal_signal):
    #[1]: SI Viewer Check
    if si_viewer_index is None:
        return
    
    #[2]: Drawings Removal
    if graphics_removal_signal&0b1:
        display_box_graphics[f"SIVIEWER{si_viewer_index}"]['RCLCG'].removeGroup(groupName = analysis_code)



def cd_get_vertical_magnitude_anchor(object_configuration):
    dispType = object_configuration['TPD_DisplayType']
    if   dispType == 'TPD':          anchor = 'CENTER'
    elif dispType == 'TPD_ABSMA':    anchor = 'BOTTOM'
    elif dispType == 'TPD_ABSMAREL': anchor = 'CENTER'
    return anchor



def cd_on_GUI_theme_update(subpage, object_configuration, current_GUI_theme):
    #[1]: Instances
    sp  = subpage
    oc  = object_configuration
    cgt = current_GUI_theme

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        sp.GUIOs[f"INDICATOR_TPD{lIdx}_LINECOLOR"].updateColor(oc[f'TPD_{lIdx}_ColorR%{cgt}'], 
                                                               oc[f'TPD_{lIdx}_ColorG%{cgt}'], 
                                                               oc[f'TPD_{lIdx}_ColorB%{cgt}'], 
                                                               oc[f'TPD_{lIdx}_ColorA%{cgt}'])



def cd_update_si_type_analysis_codes(analysis_parameters):
    #[1]: Identify Analysis Codes Belonging To This Module
    aCodes = []
    for aCode in analysis_parameters:
        if aCode.startswith('TPD'):
            aCodes.append(aCode)

    #[2]: Return Analysis Codes
    return aCodes



def cd_type_init(subPage):
    #[1]: Instances
    guios_THIS = subPage.GUIOs

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        guios_THIS[f"INDICATOR_TPD{lIdx}"].deactivate()
        guios_THIS[f"INDICATOR_TPD{lIdx}_VIEWLENGTHINPUT"].deactivate()
        guios_THIS[f"INDICATOR_TPD{lIdx}_INTERVALINPUT"].deactivate()
        guios_THIS[f"INDICATOR_TPD{lIdx}_MAINTERVALINPUT"].deactivate()
#CHART DRAWER FUNCTIONS END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUTOTRADE PAGE FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_autotrade_get_default_analysis_configuration():
    #[1]: Default Analysis Configuration
    dac = dict()

    #[2]: Setup
    dac['TPD_Master'] = False
    for lIdx in range (NMAXLINES):
        dac[f'TPD_{lIdx}_LineActive'] = False
        dac[f'TPD_{lIdx}_ViewLength'] = 10 *(lIdx+1)
        dac[f'TPD_{lIdx}_NSamples']   = 100*(lIdx+1)
        dac[f'TPD_{lIdx}_NSamplesMA'] = 20 *(lIdx+1)

    #[3]: Return
    return dac



def pg_autotrade_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'COLUMNTITLE_INDEX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_VIEWLENGTH',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1100, 'yPos': -300, 'width':  800, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_VIEWLENGTH'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2000, 'yPos': -300, 'width': 1225, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLESMA',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3325, 'yPos': -300, 'width': 1225, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLESMA'), 'fontSize': 80, 'anchor': 'SW'}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"TPD_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'TPD {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"TPD_{lIdx}_VIEWLENGTH",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint1-350*(lIdx+1), 'width':  800, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
        gList.append(({'NAME':               f"TPD_{lIdx}_NSAMPLES",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2000, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1225, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
        gList.append(({'NAME':               f"TPD_{lIdx}_NSAMPLESMA",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 3325, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1225, 'height': 250, 'style': 'styleA', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_autotrade_configure_subpage_setup(subpage, fn_get_text_pack):
    pass



def pg_autotrade_load_analysis_configuration(mainPage, subPage, analysis_configuration):
    #[1]: Main Page
    mainPage.GUIOs["INDICATORMASTERSWITCH_TPD"].setStatus(status = analysis_configuration['TPD_Master'], callStatusUpdateFunction = False)

    #[2]: Sub Page
    for lIdx in range (NMAXLINES):
        #[2-1]: Configuration Retrieval
        if f'TPD_{lIdx}_LineActive' in analysis_configuration:
            lineActive = analysis_configuration[f'TPD_{lIdx}_LineActive']
            viewLength = analysis_configuration[f'TPD_{lIdx}_ViewLength']
            nSamples   = analysis_configuration[f'TPD_{lIdx}_NSamples']
            nSamplesMA = analysis_configuration[f'TPD_{lIdx}_NSamplesMA']
        else:
            lineActive = False
            viewLength = 15  *(lIdx+1)
            nSamples   = 1000*(lIdx+1)
            nSamplesMA = 20  *(lIdx+1)

        #[2-2]: GUIOs Update
        subPage.GUIOs[f"TPD_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        subPage.GUIOs[f"TPD_{lIdx}_VIEWLENGTH"].updateText(text = f"{viewLength}")
        subPage.GUIOs[f"TPD_{lIdx}_NSAMPLES"].updateText(text   = f"{nSamples}")
        subPage.GUIOs[f"TPD_{lIdx}_NSAMPLESMA"].updateText(text = f"{nSamplesMA}")



def pg_autotrade_format_analysis_configuration_from_guios(mainPage, subPage):
    #[1]: Instances
    configuration = dict()

    #[2]: Configuration Construction
    configuration['TPD_Master'] = mainPage.GUIOs["INDICATORMASTERSWITCH_TPD"].getStatus()
    for lineIndex in range (NMAXLINES):
        configuration[f'TPD_{lineIndex}_LineActive'] = subPage.GUIOs[f"TPD_{lineIndex}_LINE"].getStatus()
        configuration[f'TPD_{lineIndex}_ViewLength'] = int(subPage.GUIOs[f"TPD_{lineIndex}_VIEWLENGTH"].getText())
        configuration[f'TPD_{lineIndex}_NSamples']   = int(subPage.GUIOs[f"TPD_{lineIndex}_NSAMPLES"].getText())
        configuration[f'TPD_{lineIndex}_NSamplesMA'] = int(subPage.GUIOs[f"TPD_{lineIndex}_NSAMPLESMA"].getText())

    #[3]: Return Configuration
    return configuration
#AUTOTRADE PAGE FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SIMULATION RESULTS PAGE FUNCTIONS ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_simulation_result_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'COLUMNTITLE_INDEX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 0, 'yPos': -300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_VIEWLENGTH',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1100, 'yPos': -300, 'width': 1050, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_VIEWLENGTH'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2250, 'yPos': -300, 'width': 1400, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLESMA',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3750, 'yPos': -300, 'width': 1400, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLESMA'), 'fontSize': 80, 'anchor': 'SW'}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"TPD_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'TPD {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"TPD_{lIdx}_VIEWLENGTH",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1050, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
        gList.append(({'NAME':               f"TPD_{lIdx}_NSAMPLES",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2250, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1400, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
        gList.append(({'NAME':               f"TPD_{lIdx}_NSAMPLESMA",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 3750, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1400, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_simulation_result_configure_subpage_setup(subpage, fn_get_text_pack):
    for lIdx in range (NMAXLINES):
        subpage.GUIOs[f"TPD_{lIdx}_LINE"].deactivate()



def pg_simulation_result_load_analysis_configuration(mainPage, subPage, analysis_configuration, simulation_selected, fn_get_text_pack):
    if simulation_selected:
        #MAIN
        mainPage.GUIOs["INDICATORMASTERSWITCH_TPD"].setStatus(status = analysis_configuration['TPD_Master'], callStatusUpdateFunction = False)
        
        #TPD
        for lIdx in range (constants.NLINES_TPD):
            lineActive = analysis_configuration.get(f'TPD_{lIdx}_LineActive', False)
            if lineActive: 
                viewLength_str = f"{analysis_configuration[f'TPD_{lIdx}_ViewLength']}"
                nSamples_str   = f"{analysis_configuration[f'TPD_{lIdx}_NSamples']}"
                nSamplesMA_str = f"{analysis_configuration[f'TPD_{lIdx}_NSamplesMA']}"
            else:          
                viewLength_str = "-"
                nSamples_str   = "-"
                nSamplesMA_str = "-"
            subPage.GUIOs[f"TPD_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
            subPage.GUIOs[f"TPD_{lIdx}_VIEWLENGTH"].updateText(text = viewLength_str)
            subPage.GUIOs[f"TPD_{lIdx}_NSAMPLES"].updateText(text   = nSamples_str)
            subPage.GUIOs[f"TPD_{lIdx}_NSAMPLESMA"].updateText(text = nSamplesMA_str)
    else:
        #MAIN
        mainPage.GUIOs["INDICATORMASTERSWITCH_TPD"].setStatus(status     = False, callStatusUpdateFunction = False)
        
        #TPD
        for lIdx in range (constants.NLINES_TPD):
            subPage.GUIOs[f"TPD_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
            subPage.GUIOs[f"TPD_{lIdx}_VIEWLENGTH"].updateText(text = "-")
            subPage.GUIOs[f"TPD_{lIdx}_NSAMPLES"].updateText(text   = "-")
            subPage.GUIOs[f"TPD_{lIdx}_NSAMPLESMA"].updateText(text = "-")
#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------