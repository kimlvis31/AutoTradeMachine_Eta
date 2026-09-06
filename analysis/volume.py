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

FORMATTEDDATATYPE_FETCHED    = 0
FORMATTEDDATATYPE_EMPTY      = 1
FORMATTEDDATATYPE_DUMMY      = 2
FORMATTEDDATATYPE_STREAMED   = 3
FORMATTEDDATATYPE_INCOMPLETE = 4




#DEFINING PARAMETERS ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ANALYSIS_CODE = 'VOL'
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
    if cac['VOL_Master']:
        for lineIndex in range (NMAXLINES):
            analysisCode = f'VOL_{lineIndex}'
            #[1]: Check Line Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue
            #[2]: Parameters
            nSamples = cac[f'{analysisCode}_NSamples']
            maType   = cac[f'VOL_MAType']
            if   type(nSamples) is not int:           invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < nSamples:                    invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if   type(maType) is not str:             invalidLines[analysisCode].append("maType: Must be type 'str'")
            elif maType not in ('SMA', 'WMA', 'EMA'): invalidLines[analysisCode].append("maType: Must be 'SMA', 'WMA', or 'EMA'")
            if analysisCode in invalidLines: continue
            #[3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex':  lineIndex,
                                 'nSamples':   nSamples,
                                 'MAType':     maType}   

    #[3]: Return The Constructed Analysis Parameters & Invalid Lines
    return cap, invalidLines



def generate(intervalID, precisions, timestamp, klines, nSamples, MAType, analysisResults, **_):
    #[1]: Instances
    vols      = analysisResults
    vaIndices = {'BASE':    KLINDEX_VOLBASE,
                 'QUOTE':   KLINDEX_VOLQUOTE,
                 'BASETB':  KLINDEX_VOLBASETAKERBUY,
                 'QUOTETB': KLINDEX_VOLQUOTETAKERBUY}
    vps = {'BASE':    precisions['quantity'],
           'QUOTE':   precisions['quote'],
           'BASETB':  precisions['quantity'],
           'QUOTETB': precisions['quote']}
    func_gnitt = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl  = auxiliaries.getTimestampList_byNTicks
    
    #[2]: Previous Analysis & Analysis Count
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    vol_prev       = vols.get(timestamp_prev, None)
    modes          = {vType: 0 for vType in ('BASE', 'QUOTE', 'BASETB', 'QUOTETB')} if vol_prev is None else vol_prev['modes'].copy()

    #[3]: Compute VOLMAs
    maComputations = dict()
    mas            = dict()
    for volType, vaIdx in vaIndices.items():
        mode      = modes[volType]
        precision = vps[volType]
        if mode == 0:
            vals = [klines[ts][vaIdx] if ts in klines else None
                    for ts in func_gtsl(intervalID = intervalID,
                                        timestamp  = timestamp,
                                        nTicks     = nSamples,
                                        direction  = False)]
        else:
            vals = None

        #[3-2-1]: SMA
        if MAType == 'SMA':
            if mode == 0:
                if any(v is None for v in vals):
                    if vol_prev is None:
                        valSum = None
                        ma     = None
                        mode   = 0
                    else:
                        valSum = vol_prev[f'MACOMPUTATION_{volType}']
                        ma     = vol_prev[f'MA_{volType}']
                        mode   = 0
                else:
                    valSum = sum(vals)
                    ma     = round(valSum / nSamples, precision)
                    mode   = 1
            else:
                timestamp_exp = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -nSamples)
                valSum_prev = vol_prev[f'MACOMPUTATION_{volType}']
                vol_exp  = klines[timestamp_exp][vaIdx]
                vol_this = klines[timestamp][vaIdx]
                if vol_exp is None or vol_this is None:
                    valSum = None
                    ma     = vol_prev[f'MA_{volType}']
                    mode   = 0
                else:
                    valSum = valSum_prev - vol_exp + vol_this
                    ma     = round(valSum / nSamples, precision)
                    mode   = 1
            maComputation = valSum

        #[3-2-2]: WMA
        elif MAType == 'WMA':
            if mode == 0:
                if any(v is None for v in vals):
                    if vol_prev is None:
                        valSum_simple   = None
                        valSum_weighted = None
                        ma              = None
                        mode            = 0
                    else:
                        valSum_simple, valSum_weighted = vol_prev[f'MACOMPUTATION_{volType}']
                        ma                             = vol_prev[f'MA_{volType}']
                        mode                           = 0
                else:
                    valSum_simple   = sum(vals)
                    valSum_weighted = sum(p*(nSamples-pIdx) for pIdx, p in enumerate(vals))
                    ma              = round(valSum_weighted / (nSamples*(nSamples+1)/2), precision)
                    mode            = 1
            else:
                timestamp_exp                     = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -nSamples)
                valSum_prev, valSum_weighted_prev = vol_prev[f'MACOMPUTATION_{volType}']
                val_exp  = klines[timestamp_exp][vaIdx]
                val_this = klines[timestamp][vaIdx]
                if val_exp is None or val_this is None:
                    valSum_simple   = None
                    valSum_weighted = None
                    ma              = vol_prev[f'MA_{volType}']
                    mode            = 0
                else:
                    valSum_simple   = valSum_prev          - val_exp     + val_this
                    valSum_weighted = valSum_weighted_prev - valSum_prev + (nSamples*val_this)
                    ma              = round(valSum_weighted / (nSamples*(nSamples+1)/2), precision)
                    mode            = 1
            maComputation = (valSum_simple, valSum_weighted)

        #[3-2-3]: EMA
        elif MAType == 'EMA':
            if mode == 0:
                if any(v is None for v in vals):
                    if vol_prev is None:
                        ma   = None
                        mode = 0
                    else:
                        ma   = vol_prev[f'MA_{volType}']
                        mode = 0
                else:
                    valSum = sum(vals)
                    ma     = round(valSum / nSamples, precision)
                    mode   = 1
            else:
                emaVal_prev = vol_prev[f'MA_{volType}']
                val_this    = klines[timestamp][vaIdx]
                if val_this is None:
                    ma   = emaVal_prev
                    mode = 0
                else:
                    kValue = 2/(nSamples+1)
                    ma     = round((val_this*kValue) + (emaVal_prev*(1-kValue)), precision)
                    mode   = 1
            maComputation = None

        #[3-2-4]: Finally
        maComputations[volType] = maComputation
        mas[volType]            = ma
        modes[volType]          = mode

    #[4]: Result formatting & Saving
    volResult = {'MACOMPUTATION_BASE':    maComputations['BASE'],
                    'MACOMPUTATION_QUOTE':   maComputations['QUOTE'],
                    'MACOMPUTATION_BASETB':  maComputations['BASETB'],
                    'MACOMPUTATION_QUOTETB': maComputations['QUOTETB'],
                    'MA_BASE':               mas['BASE'],
                    'MA_QUOTE':              mas['QUOTE'],
                    'MA_BASETB':             mas['BASETB'],
                    'MA_QUOTETB':            mas['QUOTETB'],
                    'modes':                 modes}
    vols[timestamp] = volResult

    #[5]: Memory Optimization References
    return (2,        #nAnalysisToKeep
            nSamples) #nKlinesToKeep
#ANALYSIS GENERATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#LINEARIZATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def linearize(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_MABASE':    analysisResult['MA_BASE'],
            f'{intervalID}_{analysisCode}_MAQUOTE':   analysisResult['MA_QUOTE'],
            f'{intervalID}_{analysisCode}_MABASETB':  analysisResult['MA_BASETB'],
            f'{intervalID}_{analysisCode}_MAQUOTETB': analysisResult['MA_QUOTETB']}
    return lRes
#LINEARIZATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYZER FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_maximum_market_data_reference_length(cac_iID):
    #[1]: Master Check
    if not cac_iID['VOL_Master']:
        return 0
    
    #[2]: MMDRL
    mmdrl = 0
    for lIdx in range (NMAXLINES):
        #[2-1]: Line Active Check
        if not cac_iID.get(f'VOL_{lIdx}_LineActive', False): 
            continue

        #[2-2]: MMDRL Update
        mmdrl = max(mmdrl, 
                    cac_iID[f'VOL_{lIdx}_NSamples'])

    #[3]: Return MMDRL
    return mmdrl
#ANALYZER FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#CHART DRAWER FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
CD_FULL_DRAW_SIGNALS        = 0b1
CD_VVR_PRECISIONCOMPENSATOR = -2
CD_VVR_CENTERVALUE          = {'VOL': 0}
CD_VVR_DEFAULT              = {'VOL': (0, 1)}

def cd_get_initial_configuration():
    #[1]: Indicator Configuration
    oc = dict()

    #[2]: Configuration Setup
    oc['VOL_Master'] = False
    for lIdx in range (NMAXLINES):
        oc[f'VOL_{lIdx}_LineActive'] = False
        oc[f'VOL_{lIdx}_NSamples']   = 10*(lIdx+1)
        oc[f'VOL_{lIdx}_Width'] = 1
        oc[f'VOL_{lIdx}_ColorR%DARK'] =random.randint(64,255); oc[f'VOL_{lIdx}_ColorG%DARK'] =random.randint(64,255); oc[f'VOL_{lIdx}_ColorB%DARK'] =random.randint(64, 255); oc[f'VOL_{lIdx}_ColorA%DARK'] =255
        oc[f'VOL_{lIdx}_ColorR%LIGHT']=random.randint(64,255); oc[f'VOL_{lIdx}_ColorG%LIGHT']=random.randint(64,255); oc[f'VOL_{lIdx}_ColorB%LIGHT']=random.randint(64, 255); oc[f'VOL_{lIdx}_ColorA%LIGHT']=255
        oc[f'VOL_{lIdx}_Display'] = True
    oc['VOL_VolumeType'] = 'BASE'
    oc['VOL_MAType']     = 'SMA'

    #[3]: Configuration Return
    return oc



def cd_initialize_settings_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'INDICATORINDEX_BLOCKTITLE_MA',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:VOLSETTINGS'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATOR_VOLTYPETEXT',
                   'TYPE':               'textBox_typeA',
                   'TEXTPACK':           'GUIO_CHARTDRAWER:VOLTYPE',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -650, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:VOLTYPE'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_VOLTYPESELECTION',
                   'TYPE':               'selectionBox_typeB',
                   'PAGEOBJECTFUNCTION': ['selectionUpdateFunction',],
                   'groupOrder': 2, 'xPos': 1900, 'yPos': -650, 'width': 2100, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'nDisplay': 4, 'name': 'VOL_VolTypeSelection'}))
    gList.append(({'NAME':               'INDICATOR_MATYPETEXT',
                   'TYPE':               'textBox_typeA',
                   'TEXTPACK':           'GUIO_CHARTDRAWER:MATYPE',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1000, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 80}))
    gList.append(({'NAME':               'INDICATOR_MATYPESELECTION',
                   'TYPE':               'selectionBox_typeB',
                   'PAGEOBJECTFUNCTION': ['selectionUpdateFunction',],
                   'groupOrder': 2, 'xPos': 1900, 'yPos': -1000, 'width': 2100, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'nDisplay': 3, 'name': 'VOL_MATypeSelection'}))
    gList.append(({'NAME':               'INDICATORINDEX_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -1300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INDEX'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORINTERVAL_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1100, 'yPos': -1300, 'width': 700, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORWIDTH_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1900, 'yPos': -1300, 'width': 700, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:WIDTH'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORCOLOR_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2700, 'yPos': -1300, 'width': 700, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORDISPLAY_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3500, 'yPos': -1300, 'width': 500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAY'), 'fontSize': 90}))
    yPosPoint1 = -1300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"INDICATOR_VOL{lIdx}",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'VOL {lIdx}', 'fontSize': 80, 'name': f'VOL_LineActivationSwitch_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_VOL{lIdx}_INTERVALINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
        gList.append(({'NAME':               f"INDICATOR_VOL{lIdx}_WIDTHINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 1900, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))
        gList.append(({'NAME':               f"INDICATOR_VOL{lIdx}_LINECOLOR",
                       'TYPE':               'LED_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2700, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 700, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'mode': True}))
        gList.append(({'NAME':               f"INDICATOR_VOL{lIdx}_DISPLAY",
                       'TYPE':               'switch_typeB',
                       'PAGEOBJECTFUNCTION': ['releaseFunction',],
                       'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': f'VOL_DisplaySwitch_{lIdx}'}))

    #[3]: Return GUIO Generation List
    return gList



def cd_initialize_settings_subpage_setup(subpage, fn_get_text_pack):
    volTypes = {'BASE':    {'text': fn_get_text_pack('GUIO_CHARTDRAWER:VOLTYPE_BASE')},
                'QUOTE':   {'text': fn_get_text_pack('GUIO_CHARTDRAWER:VOLTYPE_QUOTE')},
                'BASETB':  {'text': fn_get_text_pack('GUIO_CHARTDRAWER:VOLTYPE_BASETB')},
                'QUOTETB': {'text': fn_get_text_pack('GUIO_CHARTDRAWER:VOLTYPE_QUOTETB')}}
    maTypes = {'SMA': {'text': fn_get_text_pack('GUIO_CHARTDRAWER:MATYPE_SMA')},
               'WMA': {'text': fn_get_text_pack('GUIO_CHARTDRAWER:MATYPE_WMA')},
               'EMA': {'text': fn_get_text_pack('GUIO_CHARTDRAWER:MATYPE_EMA')}}
    volMAList = {f"{lIdx}": {'text': f"VOLMA {lIdx}"} for lIdx in range (NMAXLINES)}
    subpage.GUIOs["INDICATOR_VOLTYPESELECTION"].setSelectionList(selectionList     = volTypes,  displayTargets = 'all')
    subpage.GUIOs["INDICATOR_MATYPESELECTION"].setSelectionList(selectionList      = maTypes,   displayTargets = 'all')
    subpage.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = volMAList, displayTargets = 'all')



def cd_match_guios_to_config(mainPage, subPage, current_GUI_Theme, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    cgt        = current_GUI_Theme
    oc         = object_configuration

    #[2]: GUIOs Update
    guios_MAIN["SUBINDICATOR_VOL"].setStatus(oc['VOL_Master'], callStatusUpdateFunction = False)
    for lineIndex in range (NMAXLINES):
        lineActive = oc[f'VOL_{lineIndex}_LineActive']
        nSamples   = oc[f'VOL_{lineIndex}_NSamples']
        width      = oc[f'VOL_{lineIndex}_Width']
        color      = (oc[f'VOL_{lineIndex}_ColorR%{cgt}'],
                        oc[f'VOL_{lineIndex}_ColorG%{cgt}'],
                        oc[f'VOL_{lineIndex}_ColorB%{cgt}'],
                        oc[f'VOL_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'VOL_{lineIndex}_Display']
        guios_THIS[f"INDICATOR_VOL{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_THIS[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_THIS[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_THIS[f"INDICATOR_VOL{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_THIS[f"INDICATOR_VOL{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_THIS["INDICATOR_VOLTYPESELECTION"].setSelected(oc['VOL_VolumeType'], callSelectionUpdateFunction = False)
    guios_THIS["INDICATOR_MATYPESELECTION"].setSelected(oc['VOL_MAType'],      callSelectionUpdateFunction = False)
    guios_THIS["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_THIS["APPLYNEWSETTINGS"].deactivate()



def cd_load_analysis_configuration(mainPage, subPage, analysis_configuration, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    ac = analysis_configuration
    oc = object_configuration

    #[2]: GUIOs Update
    if ac is not None and ac['VOL_Master']:
        for lIdx in range (NMAXLINES):
            if ac[f'VOL_{lIdx}_LineActive']:
                nSamples = ac[f'VOL_{lIdx}_NSamples']
                width    = oc[f'VOL_{lIdx}_Width']
                display  = oc[f'VOL_{lIdx}_Display']
                guios_THIS[f"INDICATOR_VOL{lIdx}"].setStatus(status = True, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_VOL{lIdx}_INTERVALINPUT"].updateText(f"{nSamples}")
                guios_THIS[f"INDICATOR_VOL{lIdx}_WIDTHINPUT"].activate()
                guios_THIS[f"INDICATOR_VOL{lIdx}_WIDTHINPUT"].updateText(f"{width}")
                guios_THIS[f"INDICATOR_VOL{lIdx}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_VOL{lIdx}_DISPLAY"].activate()
            else:
                guios_THIS[f"INDICATOR_VOL{lIdx}"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_VOL{lIdx}_INTERVALINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_VOL{lIdx}_WIDTHINPUT"].deactivate()
                guios_THIS[f"INDICATOR_VOL{lIdx}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_VOL{lIdx}_DISPLAY"].deactivate()
        guios_THIS["INDICATOR_VOLTYPESELECTION"].setSelected(itemKey = oc['VOL_VolumeType'], callSelectionUpdateFunction = False)
        guios_THIS["INDICATOR_MATYPESELECTION"].setSelected(itemKey  = ac['VOL_MAType'],     callSelectionUpdateFunction = False)
    else:
        guios_THIS["INDICATOR_VOLTYPESELECTION"].setSelected(itemKey = oc['VOL_VolumeType'], callSelectionUpdateFunction = False)
        guios_THIS["INDICATOR_MATYPESELECTION"].setSelected(itemKey  = 'SMA',                callSelectionUpdateFunction = False)
        for lIdx in range (NMAXLINES):
            guios_THIS[f"INDICATOR_VOL{lIdx}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_THIS[f"INDICATOR_VOL{lIdx}_INTERVALINPUT"].updateText("-")
            guios_THIS[f"INDICATOR_VOL{lIdx}_WIDTHINPUT"].deactivate()
            guios_THIS[f"INDICATOR_VOL{lIdx}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_THIS[f"INDICATOR_VOL{lIdx}_DISPLAY"].deactivate()
    oc['VOL_MAType'] = 'SMA' if ac is None else ac['VOL_MAType']



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
        color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_VOL{lineSelected}_LINECOLOR"].getColor()
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
        sub_page.GUIOs[f"INDICATOR_VOL{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
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
        updateTracker = {'VOL': False}
        #Check for any changes in the configuration
        for lIdx in range (NMAXLINES):
            updateTracker[lIdx] = False

            #Width
            width_previous = oc[f'VOL_{lIdx}_Width']
            reset = False
            try:
                width = int(sub_page.GUIOs[f"INDICATOR_VOL{lIdx}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'VOL_{lIdx}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'VOL_{lIdx}_Width'] = 1
                sub_page.GUIOs[f"INDICATOR_VOL{lIdx}_WIDTHINPUT"].updateText(str(oc[f'VOL_{lIdx}_Width']))
            if width_previous != oc[f'VOL_{lIdx}_Width']: updateTracker[lIdx] = True

            #Color
            color_previous = (oc[f'VOL_{lIdx}_ColorR%{cgt}'], 
                              oc[f'VOL_{lIdx}_ColorG%{cgt}'], 
                              oc[f'VOL_{lIdx}_ColorB%{cgt}'], 
                              oc[f'VOL_{lIdx}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_VOL{lIdx}_LINECOLOR"].getColor()
            oc[f'VOL_{lIdx}_ColorR%{cgt}'] = color_r
            oc[f'VOL_{lIdx}_ColorG%{cgt}'] = color_g
            oc[f'VOL_{lIdx}_ColorB%{cgt}'] = color_b
            oc[f'VOL_{lIdx}_ColorA%{cgt}'] = color_a
            if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[lIdx] = True

            #Line Display
            display_previous = oc[f'VOL_{lIdx}_Display']
            oc[f'VOL_{lIdx}_Display'] = sub_page.GUIOs[f"INDICATOR_VOL{lIdx}_DISPLAY"].getStatus()
            if display_previous != oc[f'VOL_{lIdx}_Display']: updateTracker[lIdx] = True

        #VOL Master
        volMaster_previous = oc['VOL_Master']
        oc['VOL_Master'] = main_page.GUIOs["SUBINDICATOR_VOL"].getStatus()
        volMaster_updated = (volMaster_previous != oc['VOL_Master'])
        if volMaster_updated:
            for targetLine in updateTracker: updateTracker[targetLine] = True

        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = chart_drawer.siTypes_siViewerAlloc['VOL']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in chart_drawer.displayBox_graphics_visibleSIViewers:
                if cd_check_vertical_extremas(chart_drawer): 
                    chart_drawer._editVVR_toExtremaCenter(displayBoxName = siViewerCode)

        #Queue Update
        if updateTracker['VOL']:
            chart_drawer._drawer_RemoveDrawings(analysisCode    = 'VOL', gRemovalSignal = CD_FULL_DRAW_SIGNALS) #Remove previous graphics
            chart_drawer.addBufferZone_toDrawQueue(analysisCode = 'VOL', drawSignal     = CD_FULL_DRAW_SIGNALS) #Update draw queue
        for configuredVOL in (aCode for aCode in analysis_parameters if aCode.startswith('VOL')):
            lIdx = analysis_parameters[configuredVOL]['lineIndex']
            if updateTracker[lIdx]:
                chart_drawer._drawer_RemoveDrawings(analysisCode    = configuredVOL, gRemovalSignal = CD_FULL_DRAW_SIGNALS) #Remove previous graphics
                chart_drawer.addBufferZone_toDrawQueue(analysisCode = configuredVOL, drawSignal     = CD_FULL_DRAW_SIGNALS) #Update draw queue

        #Control Buttons Handling
        sub_page.GUIOs['APPLYNEWSETTINGS'].deactivate()
        activate_save_configuration = True

    #[3]: Analysis Related
    #---[3-1]: Line Activation Switch
    elif setter == 'LineActivationSwitch': 
        lineIndex = int(guio_name_split[2])
        #Get new switch status
        _newStatus = sub_page.GUIOs[f"INDICATOR_VOL{lineIndex}"].getStatus()
        oc[f'VOL_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True
    
    #---[3-2]: Interval Text Input Box
    elif setter == 'IntervalTextInputBox': 
        lineIndex = int(guio_name_split[2])
        #Get new nSamples
        try:    _nSamples = int(sub_page.GUIOs[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].getText())
        except: _nSamples = None
        #Save the new value to the object config dictionary
        oc[f'VOL_{lineIndex}_NSamples'] = _nSamples
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-3]: MA Type Selection
    elif setter == 'MATypeSelection': 
        #Get new MAType
        maType = sub_page.GUIOs["INDICATOR_MATYPESELECTION"].getSelected()
        #Save the new value to the object config dictionary
        oc['VOL_MAType'] = maType
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #[4]: Return Status Flag
    return activate_save_configuration



def cd_on_position_highlight_update(chart_drawer):
    #[1]: Instances
    oc  = chart_drawer.objectConfig
    ap  = chart_drawer.analysisParams[chart_drawer.intervalID]
    cgt = chart_drawer.currentGUITheme
    tsHovered = chart_drawer.posHighlight_hoveredPos[0]
    dAgg_iID  = chart_drawer._data_agg[chart_drawer.intervalID]
    klines    = dAgg_iID['kline']
    cInfo     = chart_drawer.currencyInfo
    siViewerIndex   = chart_drawer.siTypes_siViewerAlloc['VOL']
    dBox_g_this_dt1 = chart_drawer.displayBox_graphics[f'SIVIEWER{siViewerIndex}']['DESCRIPTIONTEXT1']

    #[2]: Base Text & Styles
    text_display = f" [SI{siViewerIndex} - VOL]"
    text_styles  = [((0, len(text_display)-1), 'DEFAULT'),]

    #[3]: Text Construction
    if tsHovered in klines and oc['VOL_Master']:
        kline = klines[tsHovered]
        #[3-1]: Volume Raw
        volType = oc['VOL_VolumeType']
        if   volType == 'BASE':    value = kline[KLINDEX_VOLBASE];          unit = cInfo['info_server']['baseAsset']
        elif volType == 'QUOTE':   value = kline[KLINDEX_VOLQUOTE];         unit = cInfo['info_server']['quoteAsset']
        elif volType == 'BASETB':  value = kline[KLINDEX_VOLBASETAKERBUY];  unit = cInfo['info_server']['baseAsset']
        elif volType == 'QUOTETB': value = kline[KLINDEX_VOLQUOTETAKERBUY]; unit = cInfo['info_server']['quoteAsset']
        kcType = oc['KlineColorType']
        p_open  = kline[KLINDEX_OPENPRICE]
        p_close = kline[KLINDEX_CLOSEPRICE]
        if   p_open is None:   klineColor = f'CONTENT_NEUTRAL_{kcType}'
        elif p_open < p_close: klineColor = f'CONTENT_POSITIVE_{kcType}'
        elif p_open > p_close: klineColor = f'CONTENT_NEGATIVE_{kcType}'
        else:                  klineColor = f'CONTENT_NEUTRAL_{kcType}'
        textBlock_front = f" VOL_{volType}: "
        textBlock = "-" if value is None else f"{textBlock_front}{auxiliaries.simpleValueFormatter(value = value, precision = 3)} {unit}"
        text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][1]+len(textBlock_front)), 'DEFAULT'))
        text_styles.append(((text_styles[-1][0][1]+1, text_styles[-1][0][0]+len(textBlock)-1),     klineColor))
        text_display += textBlock
        #[3-2]: Volume Analysis
        for aCode in chart_drawer.siTypes_analysisCodes['VOL']:
            #[3-2-1]: Existence Check
            dAgg_aCode = dAgg_iID[aCode]
            if tsHovered not in dAgg_aCode: continue

            #[3-2-2]: Display Check
            lineIndex     = ap[aCode]['lineIndex']
            lineIndex_str = f"{lineIndex}"
            if not oc[f'VOL_{lineIndex}_Display']: continue

            #[3-2-3]: TextStyle Check
            currentLine_style = dBox_g_this_dt1.getTextStyle(lineIndex_str)
            newLine_color = (oc[f'VOL_{lineIndex}_ColorR%{cgt}'],
                                oc[f'VOL_{lineIndex}_ColorG%{cgt}'],
                                oc[f'VOL_{lineIndex}_ColorB%{cgt}'],
                                oc[f'VOL_{lineIndex}_ColorA%{cgt}'])
            if (currentLine_style is None) or (currentLine_style['color'] != newLine_color):
                newLine_style = chart_drawer.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                newLine_style['color'] = newLine_color
                dBox_g_this_dt1.addTextStyle(lineIndex_str, newLine_style)

            #[3-2-4]: Text & Format Array Construction
            value_MA = dAgg_aCode[tsHovered][f'MA_{volType}']
            if value_MA is None: textBlock = f" {aCode}: NONE"
            else:                textBlock = f" {aCode}: {auxiliaries.simpleValueFormatter(value = value_MA, precision = 3)} {unit}"
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
    siViewerIndex = chart_drawer.siTypes_siViewerAlloc['VOL']
    siViewerCode  = f"SIVIEWER{siViewerIndex}"

    #[2]: Timestamps Check
    if not hvr_tssInVR: return False

    #[3]: Extremas Search
    #---Volume Access Index
    volType = oc['VOL_VolumeType']
    if   volType == 'BASE':    aIndex = KLINDEX_VOLBASE
    elif volType == 'QUOTE':   aIndex = KLINDEX_VOLQUOTE
    elif volType == 'BASETB':  aIndex = KLINDEX_VOLBASETAKERBUY
    elif volType == 'QUOTETB': aIndex = KLINDEX_VOLQUOTETAKERBUY
    #---Analysis Codes To Consider
    searchTargets = [('kline', aIndex)]
    searchTargets.extend((dType, f'MA_{volType}') 
                            for dType in chart_drawer.siTypes_analysisCodes['VOL'] 
                            if ((dType != 'VOL') and 
                                (dType in dAgg)  and 
                                oc[f"VOL_{ap[dType]['lineIndex']}_Display"]))
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
            if valMax < value: valMax = value
    #---Extremas Filtering
    valMin, valMax = chart_drawer.vvr_extrema_converters['above_zero'](val_min = valMin, val_max = valMax)

    #[4]: Change Check & Result Return
    return chart_drawer.cve_check_new_vertical_values(val_min               = valMin,
                                                      val_max               = valMax,
                                                      target                = siViewerCode,
                                                      precision_compensator = CD_VVR_PRECISIONCOMPENSATOR)



def cd_draw(chart_drawer, drawSignal, timestamp, analysisCode):
    #[1]: Parameters
    oc    = chart_drawer.objectConfig
    ap    = chart_drawer.analysisParams[chart_drawer.intervalID].get(analysisCode, None)
    cgt   = chart_drawer.currentGUITheme
    rclcg = chart_drawer.displayBox_graphics['KLINESPRICE']['RCLCG']
    
    siViewerIndex = chart_drawer.siTypes_siViewerAlloc['VOL']
    siViewerCode  = f'SIVIEWER{siViewerIndex}'
    rclcg = chart_drawer.displayBox_graphics[siViewerCode]['RCLCG']

    #[2]: Master & Display Status
    if not oc[f'SIVIEWER{siViewerIndex}Display']: return 0b0
    if not oc['VOL_Master']:                      return 0b0
    if analysisCode != 'VOL':
        if not oc[f'VOL_{ap['lineIndex']}_Display']: return 0b0

    #[3]: Draw Signal
    if drawSignal is None: drawSignal = 0b1
    if not drawSignal:     return 0b0

    #[4]: Drawing
    drawn = 0b0
    #---[4-1]: Volume
    if drawSignal&0b1 and analysisCode == 'VOL':
        #[4-1-1]: Kline
        kline = chart_drawer._data_agg[chart_drawer.intervalID]['kline'][timestamp]
        #[4-1-2]: Previous Drawing Removal
        rclcg.removeShape(shapeName = timestamp, groupName = 'VOL')
        #[4-1-3]: Drawing
        if kline[KLINDEX_SOURCE] not in (FORMATTEDDATATYPE_EMPTY, FORMATTEDDATATYPE_DUMMY):
            #---Shape Object Params
            vType = oc['VOL_VolumeType']
            if   vType == 'BASE':    vaIdx = KLINDEX_VOLBASE
            elif vType == 'QUOTE':   vaIdx = KLINDEX_VOLQUOTE
            elif vType == 'BASETB':  vaIdx = KLINDEX_VOLBASETAKERBUY
            elif vType == 'QUOTETB': vaIdx = KLINDEX_VOLQUOTETAKERBUY
            kl_closeTime  = kline[KLINDEX_CLOSETIME]
            kl_openPrice  = kline[KLINDEX_OPENPRICE]
            kl_closePrice = kline[KLINDEX_CLOSEPRICE]
            tsWidth = kl_closeTime-timestamp+1
            shape_width  = round(tsWidth*0.9, 1)
            shape_xPos   = round(timestamp+(tsWidth-shape_width)/2, 1)
            shape_yPos   = 0
            shape_height = kline[vaIdx]
            kcType = oc['KlineColorType']
            if   kl_openPrice < kl_closePrice: color = chart_drawer.visualManager.getFromColorTable(f'CHARTDRAWER_KLINECOLOR_TYPE{kcType}_INCREMENTAL') #Incremental
            elif kl_openPrice > kl_closePrice: color = chart_drawer.visualManager.getFromColorTable(f'CHARTDRAWER_KLINECOLOR_TYPE{kcType}_DECREMENTAL') #Decremental
            else:                              color = chart_drawer.visualManager.getFromColorTable(f'CHARTDRAWER_KLINECOLOR_TYPE{kcType}_NEUTRAL')     #Neutral
            #---Shape Adding
            rclcg.addShape_Rectangle(x = shape_xPos, y = shape_yPos, 
                                    width = shape_width, height = shape_height, 
                                    color = color, 
                                    shapeName = timestamp, shapeGroupName = 'VOL', layerNumber = 0)
        #[4-1-4]: Drawn Flag Update
        drawn += 0b1
        
    #---[4-2]: Volume MA
    if drawSignal&0b1 and analysisCode != 'VOL':
        #[4-2-1]: Analysis Data
        dAgg_ac   = chart_drawer._data_agg[chart_drawer.intervalID][analysisCode]
        lineIndex = ap['lineIndex']
        vType     = oc['VOL_VolumeType']
        maCode    = f'MA_{vType}'
        #[4-2-2]: Previous Drawing Removal
        rclcg.removeShape(shapeName = timestamp, groupName = analysisCode)
        #[4-2-3]: Drawing
        timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = chart_drawer.intervalID, timestamp = timestamp, nTicks = -1)
        volResult_prev = dAgg_ac.get(timestamp_prev, None)
        volResult      = dAgg_ac[timestamp]
        if (volResult_prev is not None) and (volResult_prev[maCode] is not None):
            #Shape Object Params
            tsWidth = timestamp-timestamp_prev
            shape_x1 = round(timestamp_prev+tsWidth/2, 1)
            shape_x2 = round(timestamp     +tsWidth/2, 1)
            shape_y1 = volResult_prev[maCode]
            shape_y2 = volResult[maCode]
            width    = oc[f'VOL_{lineIndex}_Width']*3
            color = (oc[f'VOL_{lineIndex}_ColorR%{cgt}'],
                     oc[f'VOL_{lineIndex}_ColorG%{cgt}'],
                     oc[f'VOL_{lineIndex}_ColorB%{cgt}'],
                     oc[f'VOL_{lineIndex}_ColorA%{cgt}'])
            #Shape Adding
            rclcg.addShape_Line(x = shape_x1, x2 = shape_x2, 
                                y = shape_y1, y2 = shape_y2, 
                                width = width, 
                                color = color, 
                                shapeName = timestamp, shapeGroupName = analysisCode, layerNumber = 1+lineIndex)
        #[4-2-4]: Drawn Flag Update
        drawn += 0b1
        
    #[6]: Return Drawn Flag
    return drawn



def cd_remove_expired_drawings(display_box_graphics, si_viewer_index, analysis_code, timestamp):
    #[1]: Drawings Removal
    if si_viewer_index is not None:
        sivCode = f"SIVIEWER{si_viewer_index}"
        display_box_graphics[sivCode]['RCLCG'].removeShape(shapeName = timestamp, groupName = analysis_code)



def cd_remove_drawings(drawn, display_box_graphics, si_viewer_index, analysis_code, graphics_removal_signal):
    #[1]: Drawings Removal
    if si_viewer_index is not None:
        sivCode = f"SIVIEWER{si_viewer_index}"
        if graphics_removal_signal&0b1: display_box_graphics[sivCode]['RCLCG'].removeGroup(groupName = analysis_code)



def cd_get_vertical_magnitude_anchor(object_configuration):
    #[1]: Anchor Determination
    anchor = 'BOTTOM'

    #[2]: Anchor Return
    return anchor



def cd_on_GUI_theme_update(subpage, object_configuration, current_GUI_theme):
    #[1]: Instances
    sp  = subpage
    oc  = object_configuration
    cgt = current_GUI_theme

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        sp['VOL'].GUIOs[f"INDICATOR_VOL{lIdx}_LINECOLOR"].updateColor(oc[f'VOL_{lIdx}_ColorR%{cgt}'], 
                                                                      oc[f'VOL_{lIdx}_ColorG%{cgt}'], 
                                                                      oc[f'VOL_{lIdx}_ColorB%{cgt}'], 
                                                                      oc[f'VOL_{lIdx}_ColorA%{cgt}'])



def cd_update_si_type_analysis_codes(analysis_parameters):
    #[1]: Identify Analysis Codes Belonging To This Module
    aCodes = []
    for aCode in analysis_parameters:
        if aCode.startswith('VOL'):
            aCodes.append(aCode)

    #[2]: Return Analysis Codes
    return aCodes



def cd_type_init(subPage):
    #[1]: Instances
    guios_THIS = subPage.GUIOs

    #[2]: GUIOs Update
    guios_THIS["INDICATOR_MATYPESELECTION"].deactivate()
    for lIdx in range (NMAXLINES):
        guios_THIS[f"INDICATOR_VOL{lIdx}"].deactivate()
        guios_THIS[f"INDICATOR_VOL{lIdx}_INTERVALINPUT"].deactivate()
#CHART DRAWER FUNCTIONS END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUTOTRADE PAGE FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_autotrade_get_default_analysis_configuration():
    #[1]: Default Analysis Configuration
    dac = dict()

    #[2]: Setup
    dac['VOL_Master'] = False
    for lIdx in range (NMAXLINES):
        dac[f'VOL_{lIdx}_LineActive'] = False
        dac[f'VOL_{lIdx}_NSamples']   = 20*(lIdx+1)
    dac['VOL_MAType'] = 'SMA'

    #[3]: Return
    return dac



def pg_autotrade_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'MATYPETITLETEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -350, 'width': 2450, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLMATYPE'), 'fontSize': 80}))
    gList.append(({'NAME':               'MATYPESELECTIONBOX',
                   'TYPE':               'selectionBox_typeB',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 2, 'xPos': 2550, 'yPos': -350, 'width': 2000, 'height': 250, 'style': 'styleA', 'nDisplay': 3, 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_INDEX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -650, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'), 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2325, 'yPos': -650, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80}))
    yPosPoint1 = -650
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"VOL_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'VOL {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"VOL_{lIdx}_NSAMPLES",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_autotrade_configure_subpage_setup(subpage, fn_get_text_pack):
    maTypes = {'SMA': {'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_SMA')},
               'WMA': {'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_WMA')},
               'EMA': {'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_EMA')}}
    subpage.GUIOs["MATYPESELECTIONBOX"].setSelectionList(selectionList = maTypes, displayTargets = 'all')



def pg_autotrade_load_analysis_configuration(mainPage, subPage, analysis_configuration):
    #[1]: Main Page
    mainPage.GUIOs["INDICATORMASTERSWITCH_VOL"].setStatus(status = analysis_configuration['VOL_Master'], callStatusUpdateFunction = False)

    #[2]: Sub Page
    subPage.GUIOs["MATYPESELECTIONBOX"].setSelected(itemKey = analysis_configuration['VOL_MAType'], callSelectionUpdateFunction = False)
    for lIdx in range (NMAXLINES):
        if f'VOL_{lIdx}_LineActive' in analysis_configuration:
            lineActive = analysis_configuration[f'VOL_{lIdx}_LineActive']
            nSamples   = analysis_configuration[f'VOL_{lIdx}_NSamples']
        else:
            lineActive = False
            nSamples   = 20*(lIdx+1)
        subPage.GUIOs[f"VOL_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        subPage.GUIOs[f"VOL_{lIdx}_NSAMPLES"].updateText(text = f"{nSamples}")



def pg_autotrade_format_analysis_configuration_from_guios(mainPage, subPage):
    #[1]: Instances
    configuration = dict()

    #[2]: Configuration Construction
    configuration['VOL_Master'] = mainPage.GUIOs["INDICATORMASTERSWITCH_VOL"].getStatus()
    for lIdx in range (NMAXLINES):
        configuration[f'VOL_{lIdx}_LineActive'] = subPage.GUIOs[f"VOL_{lIdx}_LINE"].getStatus()
        configuration[f'VOL_{lIdx}_NSamples']   = int(subPage.GUIOs[f"VOL_{lIdx}_NSAMPLES"].getText())
    configuration['VOL_MAType'] = subPage.GUIOs["MATYPESELECTIONBOX"].getSelected()

    #[3]: Return Configuration
    return configuration
#AUTOTRADE PAGE FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SIMULATION RESULTS PAGE FUNCTIONS ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_simulation_result_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'MATYPETITLETEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -350, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_VOLMATYPE'), 'fontSize': 80}))
    gList.append(({'NAME':               'MATYPEDISPLAYTEXT',
                   'TYPE':               'textBox_typeA',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 2, 'xPos': 2625, 'yPos': -350, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_INDEX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -650, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2625, 'yPos': -650, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'}))
    yPosPoint1 = -650
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"VOL_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'TEXT':               f'SMA {lIdx}',
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'SMA {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"VOL_{lIdx}_NSAMPLES",
                       'TYPE':               'textBox_typeA',
                       'TEXT':               '-',
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2625, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2525, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_simulation_result_configure_subpage_setup(subpage, fn_get_text_pack):
    for lIdx in range (NMAXLINES):
        subpage.GUIOs[f"VOL_{lIdx}_LINE"].deactivate()



def pg_simulation_result_load_analysis_configuration(mainPage, subPage, analysis_configuration, simulation_selected, fn_get_text_pack):
    if simulation_selected:
        mainPage.GUIOs["INDICATORMASTERSWITCH_VOL"].setStatus(status = analysis_configuration['VOL_Master'], callStatusUpdateFunction = False)
        maType = analysis_configuration['VOL_MAType']
        subPage.GUIOs["MATYPEDISPLAYTEXT"].updateText(text = fn_get_text_pack(f'SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_{maType}'))
        for lIdx in range (NMAXLINES):
            lineActive = analysis_configuration.get(f'VOL_{lIdx}_LineActive', False)
            if lineActive: nSamples_str = f"{analysis_configuration[f'VOL_{lIdx}_NSamples']}"
            else:          nSamples_str = "-"
            subPage.GUIOs[f"VOL_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
            subPage.GUIOs[f"VOL_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    else:
        mainPage.GUIOs["INDICATORMASTERSWITCH_VOL"].setStatus(status = False, callStatusUpdateFunction = False)
        subPage.GUIOs["MATYPEDISPLAYTEXT"].updateText(text = "-")
        for lIdx in range (NMAXLINES):
            subPage.GUIOs[f"VOL_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
            subPage.GUIOs[f"VOL_{lIdx}_NSAMPLES"].updateText(text = "-")
#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


