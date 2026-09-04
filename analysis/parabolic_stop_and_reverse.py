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
ANALYSIS_CODE = 'PSAR'
ANALYSIS_TYPE = 'MAIN' #('MAIN' or 'SUB')
NMAXLINES     = 10
#DEFINING PARAMETERS END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYSIS GENERATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def construct_analysis_parameters(configuration):
    #[1]: Instances & Initialization
    cac = configuration
    cap          = dict()
    invalidLines = defaultdict(list)

    #[2]: Analysis Parameters Construction
    if cac['PSAR_Master']:
        for lineIndex in range (NMAXLINES):
            analysisCode = f'PSAR_{lineIndex}'
            #[2-1]: Check Line Existence & Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue

            #[2-2]: nSamples
            AF_initial      = cac[f'{analysisCode}_AF0']
            AF_acceleration = cac[f'{analysisCode}_AF+']
            AF_maximum      = cac[f'{analysisCode}_AFMax']
            if not type(AF_initial)      in (int, float): invalidLines[analysisCode].append("AF_initial: Must be type 'int' or 'float'")
            if not type(AF_acceleration) in (int, float): invalidLines[analysisCode].append("AF_acceleration: Must be type 'int' or 'float'")
            if not type(AF_maximum)      in (int, float): invalidLines[analysisCode].append("AF_maximum: Must be type 'int' or 'float'")
            if analysisCode in invalidLines: continue
            if not (0 < AF_initial < AF_maximum): invalidLines[analysisCode].append("AF_initial: Must be greater than 0 and less than 'AF_maximum'")
            if not (0 < AF_acceleration):         invalidLines[analysisCode].append("AF_acceleration: Must be greater than 0")
            if not (0 < AF_maximum):              invalidLines[analysisCode].append("AF_maximum: Must be greater than 0")
            if analysisCode in invalidLines: 
                continue

            #[2-3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex':    lineIndex,
                                 'start':        AF_initial,
                                 'acceleration': AF_acceleration,
                                 'maximum':      AF_maximum}

    #[3]: Return The Constructed Analysis Parameters & Invalid Lines
    return cap, invalidLines



def generate(intervalID, precisions, timestamp, klines, start, acceleration, maximum, analysisResults, **_):
    #[1]: Instances
    psars      = analysisResults
    pPrecision = precisions['price']
    func_gnitt = auxiliaries.getNextIntervalTickTimestamp

    #[2]: Previous Analysis & Analysis Count
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    psar_prev      = psars.get(timestamp_prev, None)
    mode           = 0 if psar_prev is None else psar_prev['mode']

    #[3]: PSAR computation
    if mode == 0:
        kline_prev = klines.get(timestamp_prev, None)
        kline_this = klines.get(timestamp,      None)
        if any(kl is None or kl[KLINDEX_LOWPRICE] is None or kl[KLINDEX_HIGHPRICE] is None for kl in (kline_prev, kline_this)):
            if psar_prev is None:
                pd          = None
                pd_reversed = False
                af          = None
                ep          = None
                psar        = None
                dcc         = 0
                mode        = 0
            else:
                pd          = None
                pd_reversed = False
                af          = None
                ep          = None
                psar        = psar_prev['PSAR']
                dcc         = psar_prev['DCC']+1
                mode        = 0
        else:
            p_high_delta = kline_this[KLINDEX_HIGHPRICE]-kline_prev[KLINDEX_HIGHPRICE] if kline_prev[KLINDEX_HIGHPRICE] <= kline_this[KLINDEX_HIGHPRICE] else 0
            p_low_delta  = kline_prev[KLINDEX_LOWPRICE] -kline_this[KLINDEX_LOWPRICE]  if kline_this[KLINDEX_LOWPRICE]  <= kline_prev[KLINDEX_LOWPRICE]  else 0
            pd          = (p_low_delta <= p_high_delta)
            pd_reversed = False
            af          = None
            ep          = None
            psar        = None if psar_prev is None else psar_prev['PSAR']
            dcc         = 0
            mode        = 1
    else:
        timestamp_prev2 = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -2)
        kline_prev2 = klines[timestamp_prev2]
        kline_prev1 = klines[timestamp_prev]
        kline_this  = klines[timestamp]
        if any(kl[KLINDEX_LOWPRICE] is None or kl[KLINDEX_HIGHPRICE] is None for kl in (kline_prev2, kline_prev1, kline_this)):
            pd          = None
            pd_reversed = False
            af          = None
            ep          = None
            psar        = psar_prev['PSAR']
            dcc         = psar_prev['DCC']+1
            mode        = 0
        else:
            if mode == 1:
                pd          = psar_prev['PD']
                pd_reversed = False
                af          = start
                if psar_prev['PD']: 
                    ep   = max(kline_prev1[KLINDEX_HIGHPRICE], kline_prev2[KLINDEX_HIGHPRICE])
                    psar = min(kline_prev1[KLINDEX_LOWPRICE],  kline_prev2[KLINDEX_LOWPRICE])
                else:
                    ep   = min(kline_prev1[KLINDEX_LOWPRICE],  kline_prev2[KLINDEX_LOWPRICE])
                    psar = max(kline_prev1[KLINDEX_HIGHPRICE], kline_prev2[KLINDEX_HIGHPRICE])
                dcc         = 0
                mode        = 2
            elif mode == 2:
                psar = round(psar_prev['PSAR'] + psar_prev['AF']*(psar_prev['EP']-psar_prev['PSAR']), pPrecision)
                if psar_prev['PD']:
                    #Limit Check
                    psar = min(psar, kline_prev1[KLINDEX_LOWPRICE], kline_prev2[KLINDEX_LOWPRICE])
                    #Reverse Detect
                    pd_reversed = (kline_this[KLINDEX_LOWPRICE] < psar)
                    #AF Update
                    if psar_prev['EP'] < kline_this[KLINDEX_HIGHPRICE]:
                        ep = kline_this[KLINDEX_HIGHPRICE]
                        af = psar_prev['AF'] + acceleration
                        if maximum < af: af = maximum
                    else: 
                        ep = psar_prev['EP']
                        af = psar_prev['AF']
                else:
                    #Limit Check
                    psar = max(psar, kline_prev1[KLINDEX_HIGHPRICE], kline_prev2[KLINDEX_HIGHPRICE])
                    #Reverse Detect
                    pd_reversed = (psar < kline_this[KLINDEX_HIGHPRICE])
                    #AF Update
                    if kline_this[KLINDEX_LOWPRICE] < psar_prev['EP']:
                        ep = kline_this[KLINDEX_LOWPRICE]
                        af = psar_prev['AF'] + acceleration
                        if maximum < af: af = maximum
                    else: 
                        ep = psar_prev['EP']
                        af = psar_prev['AF']
                #PD Reversal Handling
                if pd_reversed:
                    pd    = not(psar_prev['PD'])
                    af    = start
                    ep    = kline_this[KLINDEX_HIGHPRICE] if pd else kline_this[KLINDEX_LOWPRICE]
                    dcc   = 0
                    psar  = psar_prev['EP']
                else: 
                    pd  = psar_prev['PD']
                    dcc = psar_prev['DCC']+1
                    psar = psar
                mode = 2

    #[4]: Result formatting & Saving
    psarResult = {'PD':          pd,          # Progression Direction (True: Incremental, False: Decremental)
                  'PDReversed':  pd_reversed, # Progression Direction Reversal
                  'AF':          af,          # Acceleration Factor
                  'EP':          ep,          # Extreme Point
                  'PSAR':        psar,        # PSAR Value
                  'DCC':         dcc,         # Direction Continuity Counter
                  'mode':        mode         # Computation Mode (0, 1, 2)
                 }
    psars[timestamp] = psarResult

    #[5]: Memory Optimization References
    return (2, #nAnalysisToKeep
            3) #nKlinesToKeep
#ANALYSIS GENERATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#LINEARIZATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def linearize(intervalID, analysisCode, analysisResult):
    psar = analysisResult['PSAR']
    if psar is None:
        lRes = {f'{intervalID}_{analysisCode}_PSAR': None,
                f'{intervalID}_{analysisCode}_DCC':  None}
    else:
        lRes = {f'{intervalID}_{analysisCode}_PSAR': analysisResult['PSAR'],
                f'{intervalID}_{analysisCode}_DCC':  analysisResult['DCC']}
    return lRes
#LINEARIZATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYZER FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_maximum_market_data_reference_length(cac_iID):
    #[1]: Master Check
    if not cac_iID['PSAR_Master']:
        return 0
    
    
    #[2]: MMDRL
    mmdrl = 2

    #[3]: Return MMDRL
    return mmdrl
#ANALYZER FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#CHART DRAWER FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
CD_FULL_DRAW_SIGNALS        = 0b1
CD_VVR_PRECISIONCOMPENSATOR = None
CD_VVR_CENTERVALUE          = None
CD_VVR_DEFAULT              = None



def cd_get_initial_configuration():
    #[1]: Indicator Configuration
    oc = dict()

    #[2]: Configuration Setup
    oc['PSAR_Master'] = False
    for lIdx in range (NMAXLINES):
        oc[f'PSAR_{lIdx}_LineActive'] = False
        oc[f'PSAR_{lIdx}_AF0']   = 0.020
        oc[f'PSAR_{lIdx}_AF+']   = 0.005*(lIdx+1)
        oc[f'PSAR_{lIdx}_AFMax'] = 0.200
        oc[f'PSAR_{lIdx}_Width'] = 1
        oc[f'PSAR_{lIdx}_ColorR%DARK'] =random.randint(64,255); oc[f'PSAR_{lIdx}_ColorG%DARK'] =random.randint(64,255); oc[f'PSAR_{lIdx}_ColorB%DARK'] =random.randint(64, 255); oc[f'PSAR_{lIdx}_ColorA%DARK'] =255
        oc[f'PSAR_{lIdx}_ColorR%LIGHT']=random.randint(64,255); oc[f'PSAR_{lIdx}_ColorG%LIGHT']=random.randint(64,255); oc[f'PSAR_{lIdx}_ColorB%LIGHT']=random.randint(64, 255); oc[f'PSAR_{lIdx}_ColorA%LIGHT']=255
        oc[f'PSAR_{lIdx}_Display'] = True

    #[3]: Configuration Return
    return oc



def cd_initialize_settings_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'INDICATORINDEX_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': 600, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INDEX'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORSTART_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':  700, 'yPos': -300, 'width': 500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:PSARSTART'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORACCELERATION_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1300, 'yPos': -300, 'width': 500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:PSARACCELERATION'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORMAXIMUM_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1900, 'yPos': -300, 'width': 500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:PSARMAXIMUM'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORSIZE_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2500, 'yPos': -300, 'width': 400, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:SIZE'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORCOLOR_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3000, 'yPos': -300, 'width': 400, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORDISPLAY_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3500, 'yPos': -300, 'width': 500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAY'), 'fontSize': 90}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"INDICATOR_PSAR{lIdx}",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 600, 'height': 250, 'style': 'styleB', 'text': f'PSAR {lIdx}', 'fontSize': 80, 'name': f'PSAR_LineActivationSwitch_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_PSAR{lIdx}_AF0INPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos':  700, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
        gList.append(({'NAME':               f"INDICATOR_PSAR{lIdx}_AF+INPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 1300, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
        gList.append(({'NAME':               f"INDICATOR_PSAR{lIdx}_AFMAXINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 1900, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
        gList.append(({'NAME':               f"INDICATOR_PSAR{lIdx}_WIDTHINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 2500, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 400, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
        gList.append(({'NAME':               f"INDICATOR_PSAR{lIdx}_LINECOLOR",
                       'TYPE':               'LED_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 3000, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 400, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'mode': True}))
        gList.append(({'NAME':               f"INDICATOR_PSAR{lIdx}_DISPLAY",
                       'TYPE':               'switch_typeB',
                       'PAGEOBJECTFUNCTION': ['releaseFunction',],
                       'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': f'PSAR_DisplaySwitch_{lIdx}'}))

    #[3]: Return GUIO Generation List
    return gList



def cd_initialize_settings_subpage_setup(subpage, fn_get_text_pack):
    subpage.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList  = {f"{lIdx}": {'text': f"PSAR {lIdx}"} for lIdx in range (NMAXLINES)}, 
                                                                     displayTargets = 'all')

    

def cd_match_guios_to_config(mainPage, subPage, current_GUI_Theme, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    cgt        = current_GUI_Theme
    oc         = object_configuration

    #[2]: GUIOs Update
    guios_MAIN["MAININDICATOR_PSAR"].setStatus(oc['PSAR_Master'], callStatusUpdateFunction = False)
    for lIdx in range (NMAXLINES):
        lActive  = oc[f'PSAR_{lIdx}_LineActive']
        af0      = oc[f'PSAR_{lIdx}_AF0']
        afPlus   = oc[f'PSAR_{lIdx}_AF+']
        afMax    = oc[f'PSAR_{lIdx}_AFMax']
        width    = oc[f'PSAR_{lIdx}_Width']
        color    = (oc[f'PSAR_{lIdx}_ColorR%{cgt}'],
                    oc[f'PSAR_{lIdx}_ColorG%{cgt}'],
                    oc[f'PSAR_{lIdx}_ColorB%{cgt}'],
                    oc[f'PSAR_{lIdx}_ColorA%{cgt}'])
        display  = oc[f'PSAR_{lIdx}_Display']
        guios_THIS[f"INDICATOR_PSAR{lIdx}"].setStatus(lActive, callStatusUpdateFunction = False)
        guios_THIS[f"INDICATOR_PSAR{lIdx}_AF0INPUT"].updateText(text   = f"{af0:.3f}")
        guios_THIS[f"INDICATOR_PSAR{lIdx}_AF+INPUT"].updateText(text   = f"{afPlus:.3f}")
        guios_THIS[f"INDICATOR_PSAR{lIdx}_AFMAXINPUT"].updateText(text = f"{afMax:.3f}")
        guios_THIS[f"INDICATOR_PSAR{lIdx}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_THIS[f"INDICATOR_PSAR{lIdx}_LINECOLOR"].updateColor(*color)
        guios_THIS[f"INDICATOR_PSAR{lIdx}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_THIS["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_THIS["APPLYNEWSETTINGS"].deactivate()



def cd_load_analysis_configuration(mainPage, subPage, analysis_configuration, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    ac = analysis_configuration
    oc = object_configuration

    #[2]: GUIOs Update
    if ac is not None and ac['PSAR_Master']:
        guios_MAIN["MAININDICATOR_PSAR"].activate()
        guios_MAIN["MAININDICATOR_PSAR"].setStatus(status = oc['PSAR_Master'], callStatusUpdateFunction = False)
        guios_MAIN["MAININDICATORSETUP_PSAR"].activate()
        for lIdx in range (NMAXLINES):
            if ac[f'PSAR_{lIdx}_LineActive']:
                af0     = ac[f'PSAR_{lIdx}_AF0']
                afPlus  = ac[f'PSAR_{lIdx}_AF+']
                afMax   = ac[f'PSAR_{lIdx}_AFMax']
                width   = oc[f'PSAR_{lIdx}_Width']
                display = oc[f'PSAR_{lIdx}_Display']
                guios_THIS[f"INDICATOR_PSAR{lIdx}"].setStatus(status = True, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_PSAR{lIdx}_AF0INPUT"].updateText(f"{af0:.3f}")
                guios_THIS[f"INDICATOR_PSAR{lIdx}_AF+INPUT"].updateText(f"{afPlus:.3f}")
                guios_THIS[f"INDICATOR_PSAR{lIdx}_AFMAXINPUT"].updateText(f"{afMax:.3f}")
                guios_THIS[f"INDICATOR_PSAR{lIdx}_WIDTHINPUT"].activate()
                guios_THIS[f"INDICATOR_PSAR{lIdx}_WIDTHINPUT"].updateText(f"{width}")
                guios_THIS[f"INDICATOR_PSAR{lIdx}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_PSAR{lIdx}_DISPLAY"].activate()
            else:
                guios_THIS[f"INDICATOR_PSAR{lIdx}"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_PSAR{lIdx}_AF0INPUT"].updateText("-")
                guios_THIS[f"INDICATOR_PSAR{lIdx}_AF+INPUT"].updateText("-")
                guios_THIS[f"INDICATOR_PSAR{lIdx}_AFMAXINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_PSAR{lIdx}_WIDTHINPUT"].deactivate()
                guios_THIS[f"INDICATOR_PSAR{lIdx}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_PSAR{lIdx}_DISPLAY"].deactivate()
    else:
        guios_MAIN["MAININDICATOR_PSAR"].setStatus(status = False, callStatusUpdateFunction = False)
        guios_MAIN["MAININDICATOR_PSAR"].deactivate()
        guios_MAIN["MAININDICATORSETUP_PSAR"].deactivate()



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
        color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_PSAR{lineSelected}_LINECOLOR"].getColor()
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
        sub_page.GUIOs[f"INDICATOR_PSAR{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
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
            width_previous = oc[f'PSAR_{lineIndex}_Width']
            reset = False
            try:
                width = int(sub_page.GUIOs[f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'PSAR_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'PSAR_{lineIndex}_Width'] = 1
                sub_page.GUIOs[f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'PSAR_{lineIndex}_Width']))
            if width_previous != oc[f'PSAR_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'PSAR_{lineIndex}_ColorR%{cgt}'], 
                              oc[f'PSAR_{lineIndex}_ColorG%{cgt}'], 
                              oc[f'PSAR_{lineIndex}_ColorB%{cgt}'], 
                              oc[f'PSAR_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_PSAR{lineIndex}_LINECOLOR"].getColor()
            oc[f'PSAR_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'PSAR_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'PSAR_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'PSAR_{lineIndex}_ColorA%{cgt}'] = color_a
            if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'PSAR_{lineIndex}_Display']
            oc[f'PSAR_{lineIndex}_Display'] = sub_page.GUIOs[f"INDICATOR_PSAR{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'PSAR_{lineIndex}_Display']: updateTracker[lineIndex] = True

        #---PSAR Master
        psarMaster_previous = oc['PSAR_Master']
        oc['PSAR_Master'] = main_page.GUIOs["MAININDICATOR_PSAR"].getStatus()
        if psarMaster_previous != oc['PSAR_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Queue Update
        for line in [aCode for aCode in analysis_parameters if aCode.startswith('PSAR')]:
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
        _newStatus = sub_page.GUIOs[f"INDICATOR_PSAR{lineIndex}"].getStatus()
        oc[f'PSAR_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-2]: AF0 Text Input Box
    elif setter == 'AF0TextInputBox':      
        lineIndex = int(guio_name_split[2])
        #Get new AF0
        try:    _af0 = round(float(sub_page.GUIOs[f"INDICATOR_PSAR{lineIndex}_AF0INPUT"].getText()), 3)
        except: _af0 = None
        #Save the new value to the object config dictionary
        oc[f'PSAR_{lineIndex}_AF0'] = _af0
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-2]: AF+ Text Input Box
    elif setter == 'AF+TextInputBox':      
        lineIndex = int(guio_name_split[2])
        #Get new AF+
        try:    _afAccel = round(float(sub_page.GUIOs[f"INDICATOR_PSAR{lineIndex}_AF+INPUT"].getText()), 3)
        except: _afAccel = None
        #Save the new value to the object config dictionary
        oc[f'PSAR_{lineIndex}_AF+'] = _afAccel
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-4]: AF Maximum Text Input Box
    elif setter == 'AFMaxTextInputBox':    
        lineIndex = int(guio_name_split[2])
        #Get new AFMax
        try:    _afMax = round(float(sub_page.GUIOs[f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT"].getText()), 3)
        except: _afMax = None
        #Save the new value to the object config dictionary
        oc[f'PSAR_{lineIndex}_AFMAX'] = _afMax
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
    if not oc['PSAR_Master']:               return 0b0
    if not oc[f'PSAR_{lineIndex}_Display']: return 0b0

    #[3]: Draw Signal
    if drawSignal is None: drawSignal = 0b1
    if not drawSignal:     return 0b0

    #[4]: Data Acquisition
    dAgg = chart_drawer._data_agg[chart_drawer.intervalID]
    psar  = dAgg[analysisCode][timestamp]
    kline = dAgg['kline'][timestamp]

    #[5]: Drawing
    drawn = 0b0
    #---[5-1]: PSAR
    if drawSignal&0b1:
        #[5-1-1]: Previous Drawing Removal
        rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
        #[5-1-2]: Drawing
        if psar['PSAR'] is not None:
            #Shape Object Params
            ts_open  = kline[KLINDEX_OPENTIME]
            ts_close = kline[KLINDEX_CLOSETIME]
            tsWidth = ts_close-ts_open+1
            shape_width = round(tsWidth*0.7, 1)
            shape_xPos  = round(ts_open+(tsWidth-shape_width)/2, 1)
            shape_xPos2 = shape_xPos+shape_width
            shape_yPos  = psar['PSAR']
            shape_yPos2 = psar['PSAR']
            width = oc[f'PSAR_{lineIndex}_Width']*3
            color = (oc[f'PSAR_{lineIndex}_ColorR%{cgt}'],
                     oc[f'PSAR_{lineIndex}_ColorG%{cgt}'],
                     oc[f'PSAR_{lineIndex}_ColorB%{cgt}'],
                     oc[f'PSAR_{lineIndex}_ColorA%{cgt}'])
            #Shape Adding
            rclcg.addShape_Line(x  = shape_xPos,  y  = shape_yPos, 
                                x2 = shape_xPos2, y2 = shape_yPos2,
                                width = width,
                                color = color,
                                shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = 13+lineIndex)
        #[5-1-3]: Drawn Flag Update
        drawn += 0b1
        
    #[6]: Return Drawn Flag
    return drawn



def cd_remove_expired_drawings(display_box_graphics, si_viewer_index, analysis_code, timestamp):
    #[1]: Drawings Removal
    display_box_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysis_code)



def cd_remove_drawings(display_box_graphics, si_viewer_index, analysis_code, graphics_removal_signal):
    #[1]: Drawings Removal
    if graphics_removal_signal&0b1: 
        display_box_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = analysis_code)



def cd_get_vertical_magnitude_anchor(object_configuration):
    return None



def cd_on_GUI_theme_update(subpage, object_configuration, current_GUI_theme):
    #[1]: Instances
    sp  = subpage
    oc  = object_configuration
    cgt = current_GUI_theme

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        sp.GUIOs[f"INDICATOR_PSAR{lIdx}_LINECOLOR"].updateColor(oc[f'PSAR_{lIdx}_ColorR%{cgt}'], 
                                                                oc[f'PSAR_{lIdx}_ColorG%{cgt}'], 
                                                                oc[f'PSAR_{lIdx}_ColorB%{cgt}'], 
                                                                oc[f'PSAR_{lIdx}_ColorA%{cgt}'])



def cd_update_si_type_analysis_codes(analysis_parameters):
    return None



def cd_type_init(subPage):
    #[1]: Instances
    guios_THIS = subPage.GUIOs

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        guios_THIS[f"INDICATOR_PSAR{lIdx}"].deactivate()
        guios_THIS[f"INDICATOR_PSAR{lIdx}_AF0INPUT"].deactivate()
        guios_THIS[f"INDICATOR_PSAR{lIdx}_AF+INPUT"].deactivate()
        guios_THIS[f"INDICATOR_PSAR{lIdx}_AFMAXINPUT"].deactivate()
#CHART DRAWER FUNCTIONS END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUTOTRADE PAGE FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_autotrade_get_default_analysis_configuration():
    #[1]: Default Analysis Configuration
    dac = dict()

    #[2]: Setup
    dac['PSAR_Master'] = False
    for lIdx in range (NMAXLINES):
        dac[f'PSAR_{lIdx}_LineActive'] = False
        dac[f'PSAR_{lIdx}_AF0']        = 0.020
        dac[f'PSAR_{lIdx}_AF+']        = 0.005*(lIdx+1)
        dac[f'PSAR_{lIdx}_AFMax']      = 0.200

    #[3]: Return
    return dac



def pg_autotrade_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'COLUMNTITLE_INDEX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_AF)',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1350, 'yPos': -300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_AF0'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_AF+',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2450, 'yPos': -300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_AF+'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_AFMAX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3550, 'yPos': -300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_AFMAX'), 'fontSize': 80}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"PSAR_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'PSAR {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"PSAR_{lIdx}_AF0",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 1350, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1000, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
        gList.append(({'NAME':               f"PSAR_{lIdx}_AF+",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2450, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1000, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
        gList.append(({'NAME':               f"PSAR_{lIdx}_AFMAX",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 3550, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1000, 'height': 250, 'style': 'styleA', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_autotrade_configure_subpage_setup(subpage, fn_get_text_pack):
    pass
      


def pg_autotrade_load_analysis_configuration(mainPage, subPage, analysis_configuration):
    #[1]: Main Page
    mainPage.GUIOs["INDICATORMASTERSWITCH_PSAR"].setStatus(status = analysis_configuration['PSAR_Master'], callStatusUpdateFunction = False)

    #[2]: Sub Page
    for lIdx in range (NMAXLINES):
        #[2-1]: Configuration Retrieval
        if f'PSAR_{lIdx}_LineActive' in analysis_configuration:
            lineActive = analysis_configuration[f'PSAR_{lIdx}_LineActive']
            af0    = analysis_configuration[f'PSAR_{lIdx}_AF0']
            afPlus = analysis_configuration[f'PSAR_{lIdx}_AF+']
            afMax  = analysis_configuration[f'PSAR_{lIdx}_AFMax']
        else:
            lineActive = False
            af0    = 0.020
            afPlus = 0.005*(lIdx+1)
            afMax  = 0.200

        #[2-2]: GUIOs Update
        subPage.GUIOs[f"PSAR_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        subPage.GUIOs[f"PSAR_{lIdx}_AF0"].updateText(text   = f"{af0:.3f}")
        subPage.GUIOs[f"PSAR_{lIdx}_AF+"].updateText(text   = f"{afPlus:.3f}")
        subPage.GUIOs[f"PSAR_{lIdx}_AFMAX"].updateText(text = f"{afMax:.3f}")



def pg_autotrade_format_analysis_configuration_from_guios(mainPage, subPage):
    #[1]: Instances
    configuration = dict()

    #[2]: Configuration Construction
    configuration['PSAR_Master'] = mainPage.GUIOs["INDICATORMASTERSWITCH_PSAR"].getStatus()
    for lIdx in range (NMAXLINES):
        configuration[f'PSAR_{lIdx}_LineActive'] = subPage.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs[f"PSAR_{lIdx}_LINE"].getStatus()
        configuration[f'PSAR_{lIdx}_AF0']   = round(float(subPage.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs[f"PSAR_{lIdx}_AF0"].getText()),   3)
        configuration[f'PSAR_{lIdx}_AF+']   = round(float(subPage.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs[f"PSAR_{lIdx}_AF+"].getText()),   3)
        configuration[f'PSAR_{lIdx}_AFMax'] = round(float(subPage.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs[f"PSAR_{lIdx}_AFMAX"].getText()), 3)

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
                   'groupOrder': 0, 'xPos': 0, 'yPos': -300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_AF0',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1350, 'yPos': -300, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_AF0'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_AF+',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2650, 'yPos': -300, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_AF+'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_AFMAX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3950, 'yPos': -300, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_AFMAX'), 'fontSize': 80}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"PSAR_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'PSAR {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"PSAR_{lIdx}_AF0",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 1350, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1200, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
        gList.append(({'NAME':               f"PSAR_{lIdx}_AF+",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2650, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1200, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
        gList.append(({'NAME':               f"PSAR_{lIdx}_AFMAX",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 3950, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1200, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_simulation_result_configure_subpage_setup(subpage, fn_get_text_pack):
    for lIdx in range (NMAXLINES):
        subpage.GUIOs[f"PSAR_{lIdx}_LINE"].deactivate()



def pg_simulation_result_load_analysis_configuration(mainPage, subPage, analysis_configuration, simulation_selected, fn_get_text_pack):
    if simulation_selected:
        mainPage.GUIOs["INDICATORMASTERSWITCH_PSAR"].setStatus(status = analysis_configuration['PSAR_Master'], callStatusUpdateFunction = False)
        for lIdx in range (NMAXLINES):
            lineActive = analysis_configuration.get(f'PSAR_{lIdx}_LineActive', False)
            if lineActive: 
                af0_str    = f"{analysis_configuration[f'PSAR_{lIdx}_AF0']:.3f}"
                afPlus_str = f"{analysis_configuration[f'PSAR_{lIdx}_AF+']:.3f}"
                afMax_str  = f"{analysis_configuration[f'PSAR_{lIdx}_AFMax']:.3f}"
            else:          
                af0_str    = "-"
                afPlus_str = "-"
                afMax_str  = "-"
            subPage.GUIOs[f"PSAR_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
            subPage.GUIOs[f"PSAR_{lIdx}_AF0"].updateText(text   = af0_str)
            subPage.GUIOs[f"PSAR_{lIdx}_AF+"].updateText(text   = afPlus_str)
            subPage.GUIOs[f"PSAR_{lIdx}_AFMAX"].updateText(text = afMax_str)
    else:
        mainPage.GUIOs["INDICATORMASTERSWITCH_SMA"].setStatus(status = False, callStatusUpdateFunction = False)
        for lIdx in range (NMAXLINES):
            subPage.GUIOs[f"PSAR_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
            subPage.GUIOs[f"PSAR_{lIdx}_AF0"].updateText(text   = "-")
            subPage.GUIOs[f"PSAR_{lIdx}_AF+"].updateText(text   = "-")
            subPage.GUIOs[f"PSAR_{lIdx}_AFMAX"].updateText(text = "-")
#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------