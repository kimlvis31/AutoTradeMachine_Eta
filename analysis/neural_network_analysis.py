#Imports
import auxiliaries
import random
import math
import torch
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
ANALYSIS_CODE = 'NNA'
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
    if cac['NNA_Master']:
        for lineIndex in range (NMAXLINES):
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

    #[3]: Return The Constructed Analysis Parameters & Invalid Lines
    return cap, invalidLines



def generate(intervalID, timestamp, klines, neuralNetworks, nnCode, alpha, beta, analysisResults, **_):
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
#ANALYSIS GENERATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#LINEARIZATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def linearize(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_NNA': analysisResult['NNA']}
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
CD_VVR_PRECISIONCOMPENSATOR = -2
CD_VVR_CENTERVALUE          = {'NNA': 0}
CD_VVR_DEFAULT              = {'NNA': (-1, 1)}



def cd_get_initial_configuration():
    #[1]: Indicator Configuration
    oc = dict()

    #[2]: Configuration Setup
    oc['NNA_Master'] = False
    for lIdx in range (NMAXLINES):
        oc[f'NNA_{lIdx}_LineActive'] = False
        oc[f'NNA_{lIdx}_NeuralNetworkCode'] = None
        oc[f'NNA_{lIdx}_Alpha']             = 0.50
        oc[f'NNA_{lIdx}_Beta']              = 2
        oc[f'NNA_{lIdx}_Width'] = 1
        oc[f'NNA_{lIdx}_ColorR%DARK'] =random.randint(64,255); oc[f'NNA_{lIdx}_ColorG%DARK'] =random.randint(64,255); oc[f'NNA_{lIdx}_ColorB%DARK'] =random.randint(64, 255); oc[f'NNA_{lIdx}_ColorA%DARK'] =255
        oc[f'NNA_{lIdx}_ColorR%LIGHT']=random.randint(64,255); oc[f'NNA_{lIdx}_ColorG%LIGHT']=random.randint(64,255); oc[f'NNA_{lIdx}_ColorB%LIGHT']=random.randint(64, 255); oc[f'NNA_{lIdx}_ColorA%LIGHT']=255
        oc[f'NNA_{lIdx}_Display'] = True

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
    gList.append(({'NAME':               'INDICATORNNCODE_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':  700, 'yPos': -300, 'width': 900, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:NEURALNETWORKCODE'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORALPHA_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1700, 'yPos': -300, 'width': 400, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:ALPHA'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORBETA_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2200, 'yPos': -300, 'width': 300, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:BETA'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORWIDTH_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2600, 'yPos': -300, 'width': 300, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:WIDTH'), 'fontSize': 90}))
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
        gList.append(({'NAME':               f"INDICATOR_NNA{lIdx}",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 600, 'height': 250, 'style': 'styleB', 'text': f'NNA {lIdx}', 'fontSize': 80, 'name': f'NNA_LineActivationSwitch_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_NNA{lIdx}_NNCODEINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos':  700, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_NNCodeTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_NNA{lIdx}_ALPHAINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 1700, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 400, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_AlphaTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_NNA{lIdx}_BETAINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 2200, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 300, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_BetaTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_NNA{lIdx}_WIDTHINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 2600, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 300, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_WidthTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_NNA{lIdx}_LINECOLOR",
                       'TYPE':               'LED_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 3000, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 400, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'mode': True}))
        gList.append(({'NAME':               f"INDICATOR_NNA{lIdx}_DISPLAY",
                       'TYPE':               'switch_typeB',
                       'PAGEOBJECTFUNCTION': ['releaseFunction',],
                       'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': f'NNA_DisplaySwitch_{lIdx}'}))

    #[3]: Return GUIO Generation List
    return gList



def cd_initialize_settings_subpage_setup(subpage, fn_get_text_pack):
    subpage.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList  = {f"{lIdx}": {'text': f"NNA {lIdx}"} for lIdx in range (NMAXLINES)}, 
                                                                     displayTargets = 'all')



def cd_match_guios_to_config(mainPage, subPage, current_GUI_Theme, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    cgt        = current_GUI_Theme
    oc         = object_configuration

    #[2]: GUIOs Update
    guios_MAIN["SUBINDICATOR_NNA"].setStatus(oc['NNA_Master'], callStatusUpdateFunction = False)
    for lIdx in range (NMAXLINES):
        lineActive = oc[f'NNA_{lIdx}_LineActive']
        nnCode     = oc[f'NNA_{lIdx}_NeuralNetworkCode']
        alpha      = oc[f'NNA_{lIdx}_Alpha']
        beta       = oc[f'NNA_{lIdx}_Beta']
        width      = oc[f'NNA_{lIdx}_Width']
        color      = (oc[f'NNA_{lIdx}_ColorR%{cgt}'], 
                        oc[f'NNA_{lIdx}_ColorG%{cgt}'], 
                        oc[f'NNA_{lIdx}_ColorB%{cgt}'], 
                        oc[f'NNA_{lIdx}_ColorA%{cgt}'])
        display    = oc[f'NNA_{lIdx}_Display']
        guios_THIS[f"INDICATOR_NNA{lIdx}"].setStatus(lineActive, callStatusUpdateFunction = False)
        nnCode_str = "" if nnCode is None else f"{nnCode}"
        guios_THIS[f"INDICATOR_NNA{lIdx}_NNCODEINPUT"].updateText(text = nnCode_str)
        guios_THIS[f"INDICATOR_NNA{lIdx}_ALPHAINPUT"].updateText(text = f"{alpha:.2f}")
        guios_THIS[f"INDICATOR_NNA{lIdx}_BETAINPUT"].updateText(text  = f"{beta}")
        guios_THIS[f"INDICATOR_NNA{lIdx}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_THIS[f"INDICATOR_NNA{lIdx}_LINECOLOR"].updateColor(*color)
        guios_THIS[f"INDICATOR_NNA{lIdx}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_THIS["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_THIS["APPLYNEWSETTINGS"].deactivate()



def cd_load_analysis_configuration(mainPage, subPage, analysis_configuration, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    ac = analysis_configuration
    oc = object_configuration

    #[2]: GUIOs Update
    if ac is not None and ac['NNA_Master']:
        guios_MAIN["SUBINDICATOR_NNA"].activate()
        guios_MAIN["SUBINDICATOR_NNA"].setStatus(status = oc['NNA_Master'], callStatusUpdateFunction = False)
        guios_MAIN["SUBINDICATORSETUP_NNA"].activate()
        for lineIndex in range (NMAXLINES):
            if ac[f'NNA_{lineIndex}_LineActive']:
                nnCode   = ac[f'NNA_{lineIndex}_NeuralNetworkCode']
                nnCode_str = "" if nnCode is None else f"{nnCode}"
                alpha    = ac[f'NNA_{lineIndex}_Alpha']
                beta     = ac[f'NNA_{lineIndex}_Beta']
                width    = oc[f'NNA_{lineIndex}_Width']
                display  = oc[f'NNA_{lineIndex}_Display']
                guios_THIS[f"INDICATOR_NNA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].updateText(nnCode_str)
                guios_THIS[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].updateText(f"{alpha:.2f}")
                guios_THIS[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].updateText(f"{beta}")
                guios_THIS[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].activate()
                guios_THIS[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                guios_THIS[f"INDICATOR_NNA{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_NNA{lineIndex}_DISPLAY"].activate()
            else:
                guios_THIS[f"INDICATOR_NNA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].deactivate()
                guios_THIS[f"INDICATOR_NNA{lineIndex}_DISPLAY"].deactivate()
                guios_THIS[f"INDICATOR_NNA{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
    else:
        guios_MAIN["SUBINDICATOR_NNA"].setStatus(status = False, callStatusUpdateFunction = False)
        guios_MAIN["SUBINDICATOR_NNA"].deactivate()
        guios_MAIN["SUBINDICATORSETUP_NNA"].deactivate()



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
        color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_NNA{lineSelected}_LINECOLOR"].getColor()
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
        sub_page.GUIOs[f"INDICATOR_NNA{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
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
            width_previous = oc[f'NNA_{lineIndex}_Width']
            reset = False
            try:
                width = int(sub_page.GUIOs[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'NNA_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'NNA_{lineIndex}_Width'] = 1
                sub_page.GUIOs[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'NNA_{lineIndex}_Width']))
            if width_previous != oc[f'NNA_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'NNA_{lineIndex}_ColorR%{cgt}'], 
                              oc[f'NNA_{lineIndex}_ColorG%{cgt}'], 
                              oc[f'NNA_{lineIndex}_ColorB%{cgt}'], 
                              oc[f'NNA_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_NNA{lineIndex}_LINECOLOR"].getColor()
            oc[f'NNA_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'NNA_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'NNA_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'NNA_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'NNA_{lineIndex}_Display']
            oc[f'NNA_{lineIndex}_Display'] = sub_page.GUIOs[f"INDICATOR_NNA{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'NNA_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---NNA Master
        mfiMaster_previous = oc['NNA_Master']
        oc['NNA_Master'] = main_page.GUIOs["SUBINDICATOR_NNA"].getStatus()
        if mfiMaster_previous != oc['NNA_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = chart_drawer.siTypes_siViewerAlloc['NNA']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in chart_drawer.displayBox_graphics_visibleSIViewers:
                if cd_check_vertical_extremas(chart_drawer): 
                    chart_drawer._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        for line in [aCode for aCode in analysis_parameters if aCode.startswith('NNA')]:
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
        _newStatus = sub_page.GUIOs[f"INDICATOR_NNA{lineIndex}"].getStatus()
        oc[f'NNA_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-2]: Neural Network Code Text Input Box
    elif setter == 'NNCodeTextInputBox': 
        lineIndex = int(guio_name_split[2])
        #Get new Neural Network Code
        try:    nnCode = sub_page.GUIOs[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].getText()
        except: nnCode = None
        #Save the new value to the object config dictionary
        oc[f'NNA_{lineIndex}_NeuralNetworkCode'] = nnCode
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-3]: Alpha Text Input Box
    elif setter == 'AlphaTextInputBox': 
        lineIndex = int(guio_name_split[2])
        #Get new Alpha
        try:    alpha = round(float(sub_page.GUIOs[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].getText()), 2)
        except: alpha = None
        #Save the new value to the object config dictionary
        oc[f'NNA_{lineIndex}_Alpha'] = alpha
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-4]: Beta Text Input Box
    elif setter == 'BetaTextInputBox': 
        lineIndex = int(guio_name_split[2])
        #Get new Beta
        try:    beta = int(sub_page.GUIOs[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].getText())
        except: beta = None
        #Save the new value to the object config dictionary
        oc[f'NNA_{lineIndex}_Beta'] = beta
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
    siViewerIndex   = chart_drawer.siTypes_siViewerAlloc['NNA']
    dBox_g_this_dt1 = chart_drawer.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

    #[2]: Base Text & Styles
    text_display = f" [SI{siViewerIndex} - NNA]"
    text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

    #[3]: Text Construction
    if oc['NNA_Master']:
        for aCode in chart_drawer.siTypes_analysisCodes['NNA']:
            #[3-1]: Existence Check
            if tsHovered not in dAgg[aCode]: continue

            #[3-2]: Display Check
            lineIndex     = ap[aCode]['lineIndex']
            lineIndex_str = f"{lineIndex}"
            if not oc[f'NNA_{lineIndex}_Display']: continue

            #[3-3]: TextStyle Check
            currentLine_style = dBox_g_this_dt1.getTextStyle(lineIndex_str)
            newLine_color = (oc[f'NNA_{lineIndex}_ColorR%{cgt}'],
                             oc[f'NNA_{lineIndex}_ColorG%{cgt}'],
                             oc[f'NNA_{lineIndex}_ColorB%{cgt}'],
                             oc[f'NNA_{lineIndex}_ColorA%{cgt}'])
            if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                newLine_style = chart_drawer.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                newLine_style['color'] = newLine_color
                dBox_g_this_dt1.addTextStyle(lineIndex_str, newLine_style)

            #[3-4]: Text & Format Array Construction
            value_nna = dAgg[aCode][tsHovered]['NNA']
            if value_nna is None: textBlock = f" {aCode}: NONE"
            else:                 textBlock = f" {aCode}: {value_nna:.2f}"
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
    ap          = chart_drawer.analysisParams[chart_drawer.intervalID]
    dAgg        = chart_drawer._data_agg[chart_drawer.intervalID]
    hvr_tssInVR = chart_drawer.horizontalViewRange_timestampsInViewRange
    siViewerIndex = chart_drawer.siTypes_siViewerAlloc['NNA']
    siViewerCode  = f"SIVIEWER{siViewerIndex}"

    #[2]: Timestamps Check
    if not hvr_tssInVR: return False

    #[3]: Extremas Search
    #---Analysis Codes To Consider
    searchTargets = [(dType, 'NNA') 
                     for dType in chart_drawer.siTypes_analysisCodes['NNA'] 
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
    valMin, valMax = chart_drawer.vvr_extrema_converters['centered'](val_min = valMin, val_max = valMax, center = CD_VVR_CENTERVALUE['NNA'])

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
    siViewerIndex = chart_drawer.siTypes_siViewerAlloc['NNA']
    siViewerCode  = f'SIVIEWER{siViewerIndex}'
    rclcg         = chart_drawer.displayBox_graphics[siViewerCode]['RCLCG']

    #[2]: Master & Display Status
    if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
    if not oc['NNA_Master']:                      return 0b0
    if not oc[f'NNA_{lineIndex}_Display']:        return 0b0

    #[3]: Draw Signal
    if drawSignal is None: drawSignal = 0b1
    if not drawSignal:     return 0b0

    #[4]: Data Acquisition
    nnas = chart_drawer._data_agg[chart_drawer.intervalID][analysisCode]
    timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = chart_drawer.intervalID, timestamp = timestamp, nTicks = -1)
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
    anchor = 'CENTER'
    return anchor



def cd_on_GUI_theme_update(subpage, object_configuration, current_GUI_theme):
    #[1]: Instances
    sp  = subpage
    oc  = object_configuration
    cgt = current_GUI_theme

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        sp.GUIOs[f"INDICATOR_NNA{lIdx}_LINECOLOR"].updateColor(oc[f'NNA_{lIdx}_ColorR%{cgt}'], 
                                                               oc[f'NNA_{lIdx}_ColorG%{cgt}'], 
                                                               oc[f'NNA_{lIdx}_ColorB%{cgt}'], 
                                                               oc[f'NNA_{lIdx}_ColorA%{cgt}'])



def cd_update_si_type_analysis_codes(analysis_parameters):
    #[1]: Identify Analysis Codes Belonging To This Module
    aCodes = []
    for aCode in analysis_parameters:
        if aCode.startswith('NNA'):
            aCodes.append(aCode)

    #[2]: Return Analysis Codes
    return aCodes



def cd_type_init(subPage):
    #[1]: Instances
    guios_THIS = subPage.GUIOs

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        guios_THIS[f"INDICATOR_NNA{lIdx}"].deactivate()
        guios_THIS[f"INDICATOR_NNA{lIdx}_NNCODEINPUT"].deactivate()
        guios_THIS[f"INDICATOR_NNA{lIdx}_ALPHAINPUT"].deactivate()
        guios_THIS[f"INDICATOR_NNA{lIdx}_BETAINPUT"].deactivate()
#CHART DRAWER FUNCTIONS END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUTOTRADE PAGE FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_autotrade_get_default_analysis_configuration():
    #[1]: Default Analysis Configuration
    dac = dict()

    #[2]: Setup
    dac['NNA_Master'] = False
    for lIdx in range (NMAXLINES):
        dac[f'NNA_{lIdx}_LineActive'] = False
        dac[f'NNA_{lIdx}_NeuralNetworkCode'] = None
        dac[f'NNA_{lIdx}_Alpha']             = 0.50
        dac[f'NNA_{lIdx}_Beta']              = 2

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
    gList.append(({'NAME':               'COLUMNTITLE_NNCODE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1100, 'yPos': -300, 'width': 2250, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NEURALNETWORKCODE'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_ALPHA',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3450, 'yPos': -300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_ALPHA'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_BETA',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 4050, 'yPos': -300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_BETA'), 'fontSize': 80, 'anchor': 'SW'}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"NNA_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'NNA {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"NNA_{lIdx}_NNCODE",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2250, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
        gList.append(({'NAME':               f"NNA_{lIdx}_ALPHA",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 3450, 'yPos': yPosPoint1-350*(lIdx+1), 'width':  500, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
        gList.append(({'NAME':               f"NNA_{lIdx}_BETA",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 4050, 'yPos': yPosPoint1-350*(lIdx+1), 'width':  500, 'height': 250, 'style': 'styleA', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_autotrade_configure_subpage_setup(subpage, fn_get_text_pack):
    pass
    


def pg_autotrade_load_analysis_configuration(mainPage, subPage, analysis_configuration):
    #[1]: Main Page
    mainPage.GUIOs["INDICATORMASTERSWITCH_NNA"].setStatus(status = analysis_configuration['NNA_Master'], callStatusUpdateFunction = False)

    #[2]: Sub Page
    for lIdx in range (NMAXLINES):
        #[2-1]: Configuration Retrieval
        if f'NNA_{lIdx}_LineActive' in analysis_configuration:
            lineActive = analysis_configuration[f'NNA_{lIdx}_LineActive']
            nnCode     = analysis_configuration[f'NNA_{lIdx}_NeuralNetworkCode']
            alpha      = analysis_configuration[f'NNA_{lIdx}_Alpha']
            beta       = analysis_configuration[f'NNA_{lIdx}_Beta']
        else:
            lineActive = False
            nnCode     = None
            alpha      = 0.50
            beta       = 2
        nnCode_str = "" if nnCode is None else f"{nnCode}"

        #[2-2]: GUIOs Update
        subPage.GUIOs[f"NNA_{lIdx}_LINE"].setStatus(status  = lineActive, callStatusUpdateFunction = False)
        subPage.GUIOs[f"NNA_{lIdx}_NNCODE"].updateText(text = nnCode_str)
        subPage.GUIOs[f"NNA_{lIdx}_ALPHA"].updateText(text  = f"{alpha:.2f}")
        subPage.GUIOs[f"NNA_{lIdx}_BETA"].updateText(text   = f"{beta}")



def pg_autotrade_format_analysis_configuration_from_guios(mainPage, subPage):
    #[1]: Instances
    configuration = dict()

    #[2]: Configuration Construction
    configuration['NNA_Master'] = mainPage.GUIOs["INDICATORMASTERSWITCH_NNA"].getStatus()
    for lineIndex in range (NMAXLINES):
        configuration[f'NNA_{lineIndex}_LineActive']        = subPage.GUIOs[f"NNA_{lineIndex}_LINE"].getStatus()
        nnCode_input = subPage.GUIOs[f"NNA_{lineIndex}_NNCODE"].getText().strip()
        configuration[f'NNA_{lineIndex}_NeuralNetworkCode'] = None if not nnCode_input else nnCode_input
        configuration[f'NNA_{lineIndex}_Alpha']             = round(float(subPage.GUIOs[f"NNA_{lineIndex}_ALPHA"].getText()), 2)
        configuration[f'NNA_{lineIndex}_Beta']              = int(subPage.GUIOs[f"NNA_{lineIndex}_BETA"].getText())

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
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),                'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_NNCODE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1350, 'yPos': -300, 'width': 2600, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NEURALNETWORKCODE'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_ALPHA',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 4050, 'yPos': -300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_ALPHA'),             'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_BETA',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 4650, 'yPos': -300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_BETA'),              'fontSize': 80, 'anchor': 'SW'}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"NNA_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'NNA {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"NNA_{lIdx}_NNCODE",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 1350, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2600, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
        gList.append(({'NAME':               f"NNA_{lIdx}_ALPHA",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 4050, 'yPos': yPosPoint1-350*(lIdx+1), 'width':  500, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
        gList.append(({'NAME':               f"NNA_{lIdx}_BETA",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 4650, 'yPos': yPosPoint1-350*(lIdx+1), 'width':  500, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_simulation_result_configure_subpage_setup(subpage, fn_get_text_pack):
    for lIdx in range (NMAXLINES):
        subpage.GUIOs[f"NNA_{lIdx}_LINE"].deactivate()



def pg_simulation_result_load_analysis_configuration(mainPage, subPage, analysis_configuration, simulation_selected, fn_get_text_pack):
    if simulation_selected:
        for lIdx in range (NMAXLINES):
            lineActive = analysis_configuration.get(f'NNA_{lIdx}_LineActive', False)
            if lineActive: 
                nnCode = analysis_configuration[f'NNA_{lIdx}_NeuralNetworkCode']
                nnCode_str = "" if nnCode is None else f"{nnCode}"
                alpha_str  = f"{analysis_configuration[f'NNA_{lIdx}_Alpha']:.2f}"
                beta_str   = f"{analysis_configuration[f'NNA_{lIdx}_Beta']}"
            else:
                nnCode_str = "-"
                alpha_str  = "-"
                beta_str   = "-"
            subPage.GUIOs[f"NNA_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
            subPage.GUIOs[f"NNA_{lIdx}_NNCODE"].updateText(text = nnCode_str)
            subPage.GUIOs[f"NNA_{lIdx}_ALPHA"].updateText(text  = alpha_str)
            subPage.GUIOs[f"NNA_{lIdx}_BETA"].updateText(text   = beta_str)
    else:
        mainPage.GUIOs["INDICATORMASTERSWITCH_NNA"].setStatus(status = False, callStatusUpdateFunction = False)
        for lIdx in range (NMAXLINES):
            subPage.GUIOs[f"NNA_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
            subPage.GUIOs[f"NNA_{lIdx}_NNCODE"].updateText(text = "-")
            subPage.GUIOs[f"NNA_{lIdx}_ALPHA"].updateText(text  = "-")
            subPage.GUIOs[f"NNA_{lIdx}_BETA"].updateText(text   = "-")
#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------