#Imports
import constants
import auxiliaries
import random
import math
from collections import defaultdict, deque



#Constants
FORMATTEDDATATYPE_FETCHED    = constants.FORMATTEDDATATYPE_FETCHED
FORMATTEDDATATYPE_EMPTY      = constants.FORMATTEDDATATYPE_EMPTY
FORMATTEDDATATYPE_DUMMY      = constants.FORMATTEDDATATYPE_DUMMY
FORMATTEDDATATYPE_STREAMED   = constants.FORMATTEDDATATYPE_STREAMED
FORMATTEDDATATYPE_INCOMPLETE = constants.FORMATTEDDATATYPE_INCOMPLETE
KLINDEX_OPENTIME              = constants.KLINDEX_OPENTIME
KLINDEX_CLOSETIME             = constants.KLINDEX_CLOSETIME
KLINDEX_OPENPRICE             = constants.KLINDEX_OPENPRICE
KLINDEX_HIGHPRICE             = constants.KLINDEX_HIGHPRICE
KLINDEX_LOWPRICE              = constants.KLINDEX_LOWPRICE
KLINDEX_CLOSEPRICE            = constants.KLINDEX_CLOSEPRICE
KLINDEX_NTRADES               = constants.KLINDEX_NTRADES
KLINDEX_VOLBASE               = constants.KLINDEX_VOLBASE
KLINDEX_VOLQUOTE              = constants.KLINDEX_VOLQUOTE
KLINDEX_VOLBASETAKERBUY       = constants.KLINDEX_VOLBASETAKERBUY
KLINDEX_VOLQUOTETAKERBUY      = constants.KLINDEX_VOLQUOTETAKERBUY
KLINDEX_CLOSED                = constants.KLINDEX_CLOSED
KLINDEX_SOURCE                = constants.KLINDEX_SOURCE
DEPTHINDEX_OPENTIME           = constants.DEPTHINDEX_OPENTIME
DEPTHINDEX_CLOSETIME          = constants.DEPTHINDEX_CLOSETIME
DEPTHINDEX_BIDS5              = constants.DEPTHINDEX_BIDS5
DEPTHINDEX_BIDS4              = constants.DEPTHINDEX_BIDS4
DEPTHINDEX_BIDS3              = constants.DEPTHINDEX_BIDS3
DEPTHINDEX_BIDS2              = constants.DEPTHINDEX_BIDS2
DEPTHINDEX_BIDS1              = constants.DEPTHINDEX_BIDS1
DEPTHINDEX_BIDS0              = constants.DEPTHINDEX_BIDS0
DEPTHINDEX_ASKS0              = constants.DEPTHINDEX_ASKS0
DEPTHINDEX_ASKS1              = constants.DEPTHINDEX_ASKS1
DEPTHINDEX_ASKS2              = constants.DEPTHINDEX_ASKS2
DEPTHINDEX_ASKS3              = constants.DEPTHINDEX_ASKS3
DEPTHINDEX_ASKS4              = constants.DEPTHINDEX_ASKS4
DEPTHINDEX_ASKS5              = constants.DEPTHINDEX_ASKS5
DEPTHINDEX_CLOSED             = constants.DEPTHINDEX_CLOSED
DEPTHINDEX_SOURCE             = constants.DEPTHINDEX_SOURCE
ATINDEX_OPENTIME              = constants.ATINDEX_OPENTIME
ATINDEX_CLOSETIME             = constants.ATINDEX_CLOSETIME
ATINDEX_QUANTITYBUY           = constants.ATINDEX_QUANTITYBUY
ATINDEX_QUANTITYSELL          = constants.ATINDEX_QUANTITYSELL
ATINDEX_NTRADESBUY            = constants.ATINDEX_NTRADESBUY
ATINDEX_NTRADESSELL           = constants.ATINDEX_NTRADESSELL
ATINDEX_NOTIONALBUY           = constants.ATINDEX_NOTIONALBUY
ATINDEX_NOTIONALSELL          = constants.ATINDEX_NOTIONALSELL
ATINDEX_CLOSED                = constants.ATINDEX_CLOSED
ATINDEX_SOURCE                = constants.ATINDEX_SOURCE
METRICINDEX_OPENTIME          = constants.METRICINDEX_OPENTIME
METRICINDEX_CLOSETIME         = constants.METRICINDEX_CLOSETIME
METRICINDEX_OPENINTEREST      = constants.METRICINDEX_OPENINTEREST
METRICINDEX_OPENINTERESTVALUE = constants.METRICINDEX_OPENINTERESTVALUE
METRICINDEX_LONGSHORTRATIO    = constants.METRICINDEX_LONGSHORTRATIO
METRICINDEX_CLOSED            = constants.METRICINDEX_CLOSED
METRICINDEX_SOURCE            = constants.METRICINDEX_SOURCE
DEPTHBINS     = constants.DEPTHBINS
DEPTHBINS_MIN = constants.DEPTHBINS
DEPTHBINS_MAX = constants.DEPTHBINS





#DEFINING PARAMETERS ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ANALYSIS_CODE = 'NES'
ANALYSIS_TYPE = 'SUB'
NMAXLINES     = 10
#DEFINING PARAMETERS END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#TEXTPACK -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
TEXTPACK = {}

TEXTPACK['GUIO_CHARTDRAWER:TITLE_SI_NES'] = {'ENG': "SUB INDICATOR SETUP - NES",
                                             'KOR': "보조지표 설정 - NES"}
TEXTPACK['GUIO_CHARTDRAWER:NESDISPLAY'] = {'ENG': "NES DISPLAY",
                                           'KOR': "NES 디스플레이"}

TEXTPACK['AUTOTRADE:BLOCKSUBTITLE_NESSETUP'] = {'ENG': "SUB INDICATOR SETUP - NES",
                                                'KOR': "보조지표 설정 - NES"}

TEXTPACK['SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_NESSETUP'] = {'ENG': "SUB INDICATOR SETUP - NES",
                                                                                       'KOR': "보조지표 설정 - NES"}
#TEXTPACK END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYSIS GENERATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def construct_analysis_parameters(configuration):
    #[1]: Instances & Initialization
    cac = configuration
    cap          = dict()
    invalidLines = defaultdict(list)

    #[2]: Analysis Parameters Construction
    if cac['NES_Master']:
        for lineIndex in range (NMAXLINES):
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
    return cap, invalidLines



def generate(intervalID, precisions, timestamp, aggTrades, nSamples, analysisResults, **_):
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
#ANALYSIS GENERATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#LINEARIZATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def linearize(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_NES':         analysisResult['NES'],
            f'{intervalID}_{analysisCode}_NESABSMA':    analysisResult['NES_ABSMA'],
            f'{intervalID}_{analysisCode}_NESABSMAREL': analysisResult['NES_ABSMAREL']}
    return lRes
#LINEARIZATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYZER FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_maximum_market_data_reference_length(cac_iID):
    #[1]: Master Check
    if not cac_iID['NES_Master']:
        return 0
    
    #[2]: MMDRL
    mmdrl = 0
    for lIdx in range (NMAXLINES):
        #[2-1]: Line Active Check
        if not cac_iID.get(f'NES_{lIdx}_LineActive', False): 
            continue

        #[2-2]: MMDRL Update
        mmdrl = max(mmdrl, 
                    cac_iID[f'NES_{lIdx}_NSamples'])

    #[3]: Return MMDRL
    return mmdrl
#ANALYZER FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#CHART DRAWER FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
CD_FULL_DRAW_SIGNALS        = 0b1
CD_VVR_PRECISIONCOMPENSATOR = -2
CD_VVR_CENTERVALUE          = {('NES', 'NES'):          0,
                               ('NES', 'NES_ABSMA'):    0,
                               ('NES', 'NES_ABSMAREL'): 0}
CD_VVR_DEFAULT              = {('NES', 'NES'):          (-1, 1),
                               ('NES', 'NES_ABSMA'):    ( 0, 1),
                               ('NES', 'NES_ABSMAREL'): (-1, 1)}



def cd_get_initial_configuration():
    #[1]: Indicator Configuration
    oc = dict()

    #[2]: Configuration Setup
    oc['NES_Master']      = False
    oc['NES_DisplayType'] = 'NES'
    for lIdx in range (NMAXLINES):
        oc[f'NES_{lIdx}_LineActive'] = False
        oc[f'NES_{lIdx}_NSamples'] = 10*(lIdx+1)
        oc[f'NES_{lIdx}_Width']    = 1
        oc[f'NES_{lIdx}_ColorR%DARK'] =random.randint(64,255); oc[f'NES_{lIdx}_ColorG%DARK'] =random.randint(64,255); oc[f'NES_{lIdx}_ColorB%DARK'] =random.randint(64, 255); oc[f'NES_{lIdx}_ColorA%DARK'] =255
        oc[f'NES_{lIdx}_ColorR%LIGHT']=random.randint(64,255); oc[f'NES_{lIdx}_ColorG%LIGHT']=random.randint(64,255); oc[f'NES_{lIdx}_ColorB%LIGHT']=random.randint(64, 255); oc[f'NES_{lIdx}_ColorA%LIGHT']=255
        oc[f'NES_{lIdx}_Display'] = True

    #[3]: Configuration Return
    return oc



def cd_initialize_settings_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'INDICATOR_BLOCKTITLE_DISPLAY',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:NESDISPLAY'), 'fontSize': 90, 'anchor': 'SW'}))
    gList.append(({'NAME':               'INDICATOR_DISPLAYTYPE_DISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -650, 'width': 1500, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAYTYPE'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_DISPLAYTYPE_SELECTION',
                   'TYPE':               'selectionBox_typeB',
                   'PAGEOBJECTFUNCTION': ['selectionUpdateFunction',],
                   'groupOrder': 2, 'xPos': 1600, 'yPos': -650, 'width': 2400, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'nDisplay': 3, 'name': 'NES_DisplayTypeSelectionBox'}))
    gList.append(({'NAME':               'INDICATORINDEX_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -950, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INDEX'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORINTERVAL_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1100, 'yPos': -950, 'width':  900, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORWIDTH_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2100, 'yPos': -950, 'width':  600, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:WIDTH'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORCOLOR_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2800, 'yPos': -950, 'width':  600, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORDISPLAY_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3500, 'yPos': -950, 'width':  500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAY'), 'fontSize': 90}))
    yPosPoint1 = -950
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"INDICATOR_NES{lIdx}",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'NES {lIdx}', 'fontSize': 80, 'name': f'NES_LineActivationSwitch_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_NES{lIdx}_INTERVALINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint1-350*(lIdx+1), 'width':  900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NES_IntervalTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_NES{lIdx}_WIDTHINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 2100, 'yPos': yPosPoint1-350*(lIdx+1), 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NES_WidthTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_NES{lIdx}_LINECOLOR",
                       'TYPE':               'LED_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2800, 'yPos': yPosPoint1-350*(lIdx+1), 'width':  600, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'mode': True}))
        gList.append(({'NAME':               f"INDICATOR_NES{lIdx}_DISPLAY",
                       'TYPE':               'switch_typeB',
                       'PAGEOBJECTFUNCTION': ['releaseFunction',],
                       'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint1-350*(lIdx+1), 'width':  500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': f'NES_DisplaySwitch_{lIdx}'}))

    #[3]: Return GUIO Generation List
    return gList



def cd_initialize_settings_subpage_setup(subpage, fn_get_text_pack):
    displayTypes = {'NES':          {'text': 'NES'},
                    'NES_ABSMA':    {'text': 'NES_ABSMA'},
                    'NES_ABSMAREL': {'text': 'NES_ABSMAREL'}}
    subpage.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].setSelectionList(selectionList = displayTypes, displayTargets = 'all')
    subpage.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList  = {f"{lIdx}": {'text': f"NES {lIdx}"} for lIdx in range (NMAXLINES)}, 
                                                                     displayTargets = 'all')



def cd_match_guios_to_config(mainPage, subPage, current_GUI_Theme, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    cgt        = current_GUI_Theme
    oc         = object_configuration

    #[2]: GUIOs Update
    guios_MAIN["SUBINDICATOR_NES"].setStatus(oc['NES_Master'], callStatusUpdateFunction = False)
    guios_THIS["INDICATOR_DISPLAYTYPE_SELECTION"].setSelected(itemKey = oc['NES_DisplayType'], callSelectionUpdateFunction = False)
    for lIdx in range (NMAXLINES):
        lActive  = oc[f'NES_{lIdx}_LineActive']
        nSamples = oc[f'NES_{lIdx}_NSamples']
        width    = oc[f'NES_{lIdx}_Width']
        color    = (oc[f'NES_{lIdx}_ColorR%{cgt}'],
                    oc[f'NES_{lIdx}_ColorG%{cgt}'],
                    oc[f'NES_{lIdx}_ColorB%{cgt}'],
                    oc[f'NES_{lIdx}_ColorA%{cgt}'])
        display  = oc[f'NES_{lIdx}_Display']
        guios_THIS[f"INDICATOR_NES{lIdx}"].setStatus(status = lActive, callStatusUpdateFunction = False)
        guios_THIS[f"INDICATOR_NES{lIdx}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_THIS[f"INDICATOR_NES{lIdx}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_THIS[f"INDICATOR_NES{lIdx}_LINECOLOR"].updateColor(*color)
        guios_THIS[f"INDICATOR_NES{lIdx}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
    guios_THIS["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_THIS["APPLYNEWSETTINGS"].deactivate()



def cd_load_analysis_configuration(mainPage, subPage, analysis_configuration, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    ac = analysis_configuration
    oc = object_configuration

    #[2]: GUIOs Update
    if ac is not None and ac['NES_Master']:
        guios_MAIN["SUBINDICATOR_NES"].activate()
        guios_MAIN["SUBINDICATOR_NES"].setStatus(status = oc['NES_Master'], callStatusUpdateFunction = False)
        guios_MAIN["SUBINDICATORSETUP_NES"].activate()
        for lineIndex in range (NMAXLINES):
            if ac[f'NES_{lineIndex}_LineActive']:
                nSamples = ac[f'NES_{lineIndex}_NSamples']
                width    = oc[f'NES_{lineIndex}_Width']
                display  = oc[f'NES_{lineIndex}_Display']
                guios_THIS[f"INDICATOR_NES{lineIndex}"].setStatus(status = True)
                guios_THIS[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                guios_THIS[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].activate()
                guios_THIS[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                guios_THIS[f"INDICATOR_NES{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_NES{lineIndex}_DISPLAY"].activate()
            else:
                guios_THIS[f"INDICATOR_NES{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].deactivate()
                guios_THIS[f"INDICATOR_NES{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_NES{lineIndex}_DISPLAY"].deactivate()
    else:
        guios_MAIN["SUBINDICATOR_NES"].setStatus(status = False, callStatusUpdateFunction = False)
        guios_MAIN["SUBINDICATOR_NES"].deactivate()
        guios_MAIN["SUBINDICATORSETUP_NES"].deactivate()



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
        color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_NES{lineSelected}_LINECOLOR"].getColor()
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
        sub_page.GUIOs[f"INDICATOR_NES{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
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
            width_previous = oc[f'NES_{lineIndex}_Width']
            reset = False
            try:
                width = int(sub_page.GUIOs[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'NES_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'NES_{lineIndex}_Width'] = 1
                sub_page.GUIOs[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'NES_{lineIndex}_Width']))
            if width_previous != oc[f'NES_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'NES_{lineIndex}_ColorR%{cgt}'], 
                              oc[f'NES_{lineIndex}_ColorG%{cgt}'], 
                              oc[f'NES_{lineIndex}_ColorB%{cgt}'], 
                              oc[f'NES_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_NES{lineIndex}_LINECOLOR"].getColor()
            oc[f'NES_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'NES_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'NES_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'NES_{lineIndex}_ColorA%{cgt}'] = color_a
            if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'NES_{lineIndex}_Display']
            oc[f'NES_{lineIndex}_Display'] = sub_page.GUIOs[f"INDICATOR_NES{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'NES_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #MA Master
        maMaster_previous = oc[f'NES_Master']
        oc[f'NES_Master'] = main_page.GUIOs[f"SUBINDICATOR_NES"].getStatus()
        if maMaster_previous != oc[f'NES_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Display Type
        displayType_prev = oc['NES_DisplayType']
        oc['NES_DisplayType'] = sub_page.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].getSelected()
        if displayType_prev != oc['NES_DisplayType']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = chart_drawer.siTypes_siViewerAlloc['VOL']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in chart_drawer.displayBox_graphics_visibleSIViewers:
                if cd_check_vertical_extremas(chart_drawer): 
                    chart_drawer._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        for line in [aCode for aCode in analysis_parameters if aCode.startswith('NES')]:
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
        _newStatus = sub_page.GUIOs[f"INDICATOR_NES{lineIndex}"].getStatus()
        oc[f'NES_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True
    
    #---[3-2]: Interval Text Input Box
    elif setter == 'IntervalTextInputBox': 
        lineIndex = int(guio_name_split[2])
        #Get new nSamples
        try:    _nSamples = int(sub_page.GUIOs[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].getText())
        except: _nSamples = None
        #Save the new value to the object config dictionary
        oc[f'NES_{lineIndex}_NSamples'] = _nSamples
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
    siViewerIndex   = chart_drawer.siTypes_siViewerAlloc['NES']
    dBox_g_this_dt1 = chart_drawer.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

    #[2]: Base Text & Styles
    text_display = f" [SI{siViewerIndex} - NES]"
    text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

    #[3]: Text Construction
    if oc['NES_Master']:
        for aCode in chart_drawer.siTypes_analysisCodes['NES']:
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
                newLine_style = chart_drawer.effectiveTextStyle['CONTENT_DEFAULT'].copy()
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



def cd_on_position_selection_update(chart_drawer):
    pass



def cd_check_vertical_extremas(chart_drawer):
    #[1]: References
    oc          = chart_drawer.objectConfig
    dispType    = oc['NES_DisplayType']
    ap          = chart_drawer.analysisParams[chart_drawer.intervalID]
    dAgg        = chart_drawer._data_agg[chart_drawer.intervalID]
    hvr_tssInVR = chart_drawer.horizontalViewRange_timestampsInViewRange
    siViewerIndex = chart_drawer.siTypes_siViewerAlloc['NES']
    siViewerCode  = f"SIVIEWER{siViewerIndex}"

    #[2]: Timestamps Check
    if not hvr_tssInVR: return False

    #[3]: Extremas Search
    #---Analysis Codes To Consider
    searchTargets = [(dType, dispType) 
                     for dType in chart_drawer.siTypes_analysisCodes['NES'] 
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
        valMin, valMax = chart_drawer.vvr_extrema_converters['centered'](val_min = valMin, val_max = valMax, center = CD_VVR_CENTERVALUE[('NES', dispType)])
    elif dispType == 'NES_ABSMA':
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
    siViewerIndex = chart_drawer.siTypes_siViewerAlloc['NES']
    siViewerCode  = f'SIVIEWER{siViewerIndex}'
    rclcg         = chart_drawer.displayBox_graphics[siViewerCode]['RCLCG']

    #[2]: Master & Display Status
    if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
    if not oc['NES_Master']:                      return 0b0
    if not oc[f'NES_{lineIndex}_Display']:        return 0b0

    #[3]: Draw Signal
    if drawSignal is None: drawSignal = 0b1
    if not drawSignal:     return 0b0

    #[4]: Data Acquisition
    ness = chart_drawer._data_agg[chart_drawer.intervalID][analysisCode]
    timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = chart_drawer.intervalID, timestamp = timestamp, nTicks = -1)
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
    dispType = object_configuration['NES_DisplayType']
    if   dispType == 'NES':          anchor = 'CENTER'
    elif dispType == 'NES_ABSMA':    anchor = 'BOTTOM'
    elif dispType == 'NES_ABSMAREL': anchor = 'CENTER'
    return anchor



def cd_on_GUI_theme_update(subpage, object_configuration, current_GUI_theme):
    #[1]: Instances
    sp  = subpage
    oc  = object_configuration
    cgt = current_GUI_theme

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        sp.GUIOs[f"INDICATOR_NES{lIdx}_LINECOLOR"].updateColor(oc[f'NES_{lIdx}_ColorR%{cgt}'], 
                                                               oc[f'NES_{lIdx}_ColorG%{cgt}'], 
                                                               oc[f'NES_{lIdx}_ColorB%{cgt}'], 
                                                               oc[f'NES_{lIdx}_ColorA%{cgt}'])



def cd_update_si_type_analysis_codes(analysis_parameters):
    #[1]: Identify Analysis Codes Belonging To This Module
    aCodes = []
    for aCode in analysis_parameters:
        if aCode.startswith('NES'):
            aCodes.append(aCode)

    #[2]: Return Analysis Codes
    return aCodes



def cd_type_init(subPage):
    #[1]: Instances
    guios_THIS = subPage.GUIOs

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        guios_THIS[f"INDICATOR_NES{lIdx}"].deactivate()
        guios_THIS[f"INDICATOR_NES{lIdx}_INTERVALINPUT"].deactivate()
#CHART DRAWER FUNCTIONS END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUTOTRADE PAGE FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_autotrade_get_default_analysis_configuration():
    #[1]: Default Analysis Configuration
    dac = dict()

    #[2]: Setup
    dac['NES_Master'] = False
    for lIdx in range (NMAXLINES):
        dac[f'NES_{lIdx}_LineActive'] = False
        dac[f'NES_{lIdx}_NSamples']   = 10*(lIdx+1)

    #[3]: Return
    return dac



def pg_autotrade_on_settings_content_update(subpage, object_code):
    pass



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
        gList.append(({'NAME':               f"NES_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'NES {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"NES_{lIdx}_NSAMPLES",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2225, 'height': 250, 'style': 'styleA', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_autotrade_configure_subpage_setup(subpage, fn_get_text_pack):
    pass



def pg_autotrade_load_analysis_configuration(mainPage, subPage, analysis_configuration):
    #[1]: Main Page
    mainPage.GUIOs["INDICATORMASTERSWITCH_NES"].setStatus(status = analysis_configuration['NES_Master'], callStatusUpdateFunction = False)

    #[2]: Sub Page
    for lIdx in range (NMAXLINES):
        #[2-1]: Configuration Retrieval
        if f'NES_{lIdx}_LineActive' in analysis_configuration:
            lineActive = analysis_configuration[f'NES_{lIdx}_LineActive']
            nSamples   = analysis_configuration[f'NES_{lIdx}_NSamples']
        else:
            lineActive = False
            nSamples   = 10*(lIdx+1)

        #[2-2]: GUIOs Update
        subPage.GUIOs[f"NES_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        subPage.GUIOs[f"NES_{lIdx}_NSAMPLES"].updateText(text = f"{nSamples}")



def pg_autotrade_format_analysis_configuration_from_guios(mainPage, subPage):
    #[1]: Instances
    configuration = dict()

    #[2]: Configuration Construction
    configuration['NES_Master'] = mainPage.GUIOs["INDICATORMASTERSWITCH_NES"].getStatus()
    for lineIndex in range (NMAXLINES):
        configuration[f'NES_{lineIndex}_LineActive'] = subPage.GUIOs[f"NES_{lineIndex}_LINE"].getStatus()
        configuration[f'NES_{lineIndex}_NSamples']   = int(subPage.GUIOs[f"NES_{lineIndex}_NSAMPLES"].getText())

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
                   'groupOrder': 0, 'xPos': 0, 'yPos': -300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2625, 'yPos': -300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"NES_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'NES {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"NES_{lIdx}_NSAMPLES",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2625, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2525, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_simulation_result_configure_subpage_setup(subpage, fn_get_text_pack):
    for lIdx in range (NMAXLINES):
        subpage.GUIOs[f"NES_{lIdx}_LINE"].deactivate()



def pg_simulation_result_load_analysis_configuration(mainPage, subPage, analysis_configuration, simulation_selected, fn_get_text_pack):
    if simulation_selected:
        mainPage.GUIOs["INDICATORMASTERSWITCH_NES"].setStatus(status = analysis_configuration['NES_Master'], callStatusUpdateFunction = False)
        for lIdx in range (NMAXLINES):
            lineActive = analysis_configuration.get(f'NES_{lIdx}_LineActive', False)
            if lineActive: nSamples_str = f"{analysis_configuration[f'NES_{lIdx}_NSamples']}"
            else:          nSamples_str = "-"
            subPage.GUIOs[f"NES_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
            subPage.GUIOs[f"NES_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    else:
        mainPage.GUIOs["INDICATORMASTERSWITCH_NES"].setStatus(status = False, callStatusUpdateFunction = False)
        for lIdx in range (NMAXLINES):
            subPage.GUIOs[f"NES_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
            subPage.GUIOs[f"NES_{lIdx}_NSAMPLES"].updateText(text = "-")
#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------