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
ANALYSIS_CODE = 'SWING'
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
    if cac['SWING_Master']:
        for lineIndex in range (NMAXLINES):
            analysisCode = f'SWING_{lineIndex}'
            #[2-1]: Check Line Existence & Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue

            #[2-2]: nSamples
            swingRange = cac[f'{analysisCode}_SwingRange']
            if   not type(swingRange) in (int, float): invalidLines[analysisCode].append("swingRange: Must be type 'int' or 'float'")
            elif not (0.0001 <= swingRange):           invalidLines[analysisCode].append("swingRange: Must be greater than or equal to 0.0001")
            if analysisCode in invalidLines:
                continue

            #[2-3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex':    lineIndex,
                                 'swingRange':   swingRange}  

    #[3]: Return The Constructed Analysis Parameters & Invalid Lines
    return cap, invalidLines



def generate(intervalID, timestamp, klines, swingRange, analysisResults, **_):
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
#ANALYSIS GENERATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#LINEARIZATION ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def linearize(intervalID, analysisCode, analysisResult):
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
#LINEARIZATION END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#ANALYZER FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_maximum_market_data_reference_length(cac_iID):
    #[1]: Master Check
    if not cac_iID['SWING_Master']:
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
    oc['SWING_Master'] = False
    for lIdx in range (NMAXLINES):
        oc[f'SWING_{lIdx}_LineActive'] = False
        oc[f'SWING_{lIdx}_SwingRange'] = 0.005*(lIdx+1)
        oc[f'SWING_{lIdx}_Width'] = 1
        oc[f'SWING_{lIdx}_ColorR%DARK'] =random.randint(64,255); oc[f'SWING_{lIdx}_ColorG%DARK'] =random.randint(64,255); oc[f'SWING_{lIdx}_ColorB%DARK'] =random.randint(64, 255); oc[f'SWING_{lIdx}_ColorA%DARK'] =255
        oc[f'SWING_{lIdx}_ColorR%LIGHT']=random.randint(64,255); oc[f'SWING_{lIdx}_ColorG%LIGHT']=random.randint(64,255); oc[f'SWING_{lIdx}_ColorB%LIGHT']=random.randint(64, 255); oc[f'SWING_{lIdx}_ColorA%LIGHT']=255
        oc[f'SWING_{lIdx}_Display'] = True

    #[3]: Configuration Return
    return oc



def cd_initialize_settings_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'INDICATORINDEX_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:INDEX'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORSWINGRANGE_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1100, 'yPos': -300, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:SWINGRANGE'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORWIDTH_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2300, 'yPos': -300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:WIDTH'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORCOLOR_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2900, 'yPos': -300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORDISPLAY_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3500, 'yPos': -300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('GUIO_CHARTDRAWER:DISPLAY'), 'fontSize': 90}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"INDICATOR_SWING{lIdx}",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'SWING {lIdx}', 'fontSize': 80, 'name': f'SWING_LineActivationSwitch_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_SWING{lIdx}_SWINGRANGEINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1100, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'SWING_SwingRangeTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_SWING{lIdx}_WIDTHINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint1-350*(lIdx+1), 'width':  500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'SWING_WidthTextInputBox_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_SWING{lIdx}_LINECOLOR",
                       'TYPE':               'LED_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2900, 'yPos': yPosPoint1-350*(lIdx+1), 'width':  500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'mode': True}))
        gList.append(({'NAME':               f"INDICATOR_SWING{lIdx}_DISPLAY",
                       'TYPE':               'switch_typeB',
                       'PAGEOBJECTFUNCTION': ['releaseFunction',],
                       'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint1-350*(lIdx+1), 'width':  500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': f'SWING_DisplaySwitch_{lIdx}'}))

    #[3]: Return GUIO Generation List
    return gList



def cd_initialize_settings_subpage_setup(subpage, fn_get_text_pack):
    subpage.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList  = {f"{lIdx}": {'text': f"SWING {lIdx}"} for lIdx in range (NMAXLINES)}, 
                                                                     displayTargets = 'all')



def cd_match_guios_to_config(mainPage, subPage, current_GUI_Theme, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    cgt        = current_GUI_Theme
    oc         = object_configuration

    #[2]: GUIOs Update
    guios_MAIN["MAININDICATOR_SWING"].setStatus(oc['SWING_Master'], callStatusUpdateFunction = False)
    for lIdx in range (NMAXLINES):
        lineActive = oc[f'SWING_{lIdx}_LineActive']
        swingRange = oc[f'SWING_{lIdx}_SwingRange']
        width      = oc[f'SWING_{lIdx}_Width']
        color      = (oc[f'SWING_{lIdx}_ColorR%{cgt}'], 
                        oc[f'SWING_{lIdx}_ColorG%{cgt}'], 
                        oc[f'SWING_{lIdx}_ColorB%{cgt}'], 
                        oc[f'SWING_{lIdx}_ColorA%{cgt}'])
        display    = oc[f'SWING_{lIdx}_Display']
        guios_THIS[f"INDICATOR_SWING{lIdx}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_THIS[f"INDICATOR_SWING{lIdx}_SWINGRANGEINPUT"].updateText(text = f"{swingRange:.4f}")
        guios_THIS[f"INDICATOR_SWING{lIdx}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_THIS[f"INDICATOR_SWING{lIdx}_LINECOLOR"].updateColor(*color)
        guios_THIS[f"INDICATOR_SWING{lIdx}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_THIS["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_THIS["APPLYNEWSETTINGS"].deactivate()



def cd_load_analysis_configuration(mainPage, subPage, analysis_configuration, object_configuration):
    #[1]: Instances
    guios_MAIN = mainPage.GUIOs
    guios_THIS = subPage.GUIOs
    ac = analysis_configuration
    oc = object_configuration

    #[2]: GUIOs Update
    if ac is not None and ac['SWING_Master']:
        guios_MAIN["MAININDICATOR_SWING"].activate()
        guios_MAIN["MAININDICATOR_SWING"].setStatus(status = oc['SWING_Master'], callStatusUpdateFunction = False)
        guios_MAIN["MAININDICATORSETUP_SWING"].activate()
        for lineIndex in range (NMAXLINES):
            if ac[f'SWING_{lineIndex}_LineActive']:
                swingRange = ac[f'SWING_{lineIndex}_SwingRange']
                width      = oc[f'SWING_{lineIndex}_Width']
                display    = oc[f'SWING_{lineIndex}_Display']
                guios_THIS[f"INDICATOR_SWING{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].updateText(f"{swingRange:.4f}")
                guios_THIS[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].activate()
                guios_THIS[f"INDICATOR_SWING{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_SWING{lineIndex}_DISPLAY"].activate()
            else:
                guios_THIS[f"INDICATOR_SWING{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].deactivate()
                guios_THIS[f"INDICATOR_SWING{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_SWING{lineIndex}_DISPLAY"].deactivate()
    else:
        guios_MAIN["MAININDICATOR_SWING"].setStatus(status = False, callStatusUpdateFunction = False)
        guios_MAIN["MAININDICATOR_SWING"].deactivate()
        guios_MAIN["MAININDICATORSETUP_SWING"].deactivate()



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
        color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_SWING{lineSelected}_LINECOLOR"].getColor()
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
        sub_page.GUIOs[f"INDICATOR_SWING{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
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
            width_previous = oc[f'SWING_{lineIndex}_Width']
            reset = False
            try:
                width = int(sub_page.GUIOs[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'SWING_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'SWING_{lineIndex}_Width'] = 1
                sub_page.GUIOs[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'SWING_{lineIndex}_Width']))
            if width_previous != oc[f'SWING_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'SWING_{lineIndex}_ColorR%{cgt}'],
                              oc[f'SWING_{lineIndex}_ColorG%{cgt}'],
                              oc[f'SWING_{lineIndex}_ColorB%{cgt}'],
                              oc[f'SWING_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = sub_page.GUIOs[f"INDICATOR_SWING{lineIndex}_LINECOLOR"].getColor()
            oc[f'SWING_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'SWING_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'SWING_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'SWING_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'SWING_{lineIndex}_Display']
            oc[f'SWING_{lineIndex}_Display'] = sub_page.GUIOs[f"INDICATOR_SWING{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'SWING_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---SWING Master
        swingMaster_previous = oc['SWING_Master']
        oc['SWING_Master'] = main_page.GUIOs["MAININDICATOR_SWING"].getStatus()
        if swingMaster_previous != oc['SWING_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Queue Update
        for line in [aCode for aCode in analysis_parameters if aCode.startswith('SWING')]:
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
        _newStatus = sub_page.GUIOs[f"INDICATOR_SWING{lineIndex}"].getStatus()
        oc[f'SWING_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #---[3-2]: Swing Range Text Input Box
    elif setter == 'SwingRangeTextInputBox':
        lineIndex = int(guio_name_split[2])
        #Get new Swing Range
        try:    swingRange = round(float(sub_page.GUIOs[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].getText()), 4)
        except: swingRange = None
        #Save the new value to the object config dictionary
        oc[f'SWING_{lineIndex}_SwingRange'] = swingRange
        #Analysis Configuration Update Response
        chart_drawer._onAnalysisConfigurationUpdate()
        activate_save_configuration = True

    #[3]: Return Status Flag
    return activate_save_configuration



def cd_on_position_highlight_update(chart_drawer):
    pass



def cd_on_position_selection_update(chart_drawer):
    ph_selPos = chart_drawer.posHighlight_selectedPos
    dAgg      = chart_drawer._data_agg[chart_drawer.intervalID]
    aParams   = chart_drawer.analysisParams[chart_drawer.intervalID]

    #SWING Update
    for lIdx in range (NMAXLINES):
        aCode = f'SWING_{lIdx}'
        if aCode in aParams:
            if   ph_selPos is None:        chart_drawer._drawer_RemoveDrawings(analysisCode = aCode, gRemovalSignal = 0b1)
            elif ph_selPos in dAgg[aCode]: chart_drawer._drawer_sendDrawSignal(analysisCode = aCode, timestamp = ph_selPos, drawSignal = 0b1)
 


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
    if not oc['SWING_Master']:               return 0b0
    if not oc[f'SWING_{lineIndex}_Display']: return 0b0

    #[3]: Draw Signal
    if drawSignal is None: drawSignal = 0b1
    if not drawSignal:     return 0b0

    #[4]: Data Acquisition
    swing = chart_drawer._data_agg[chart_drawer.intervalID][analysisCode][timestamp]

    #[5]: Drawing
    drawn = 0b0
    #---[5-1]: SWINGS
    if drawSignal&0b1:
        if timestamp == chart_drawer.posHighlight_selectedPos:
            #[5-1]: Previous Drawing Removal
            rclcg.removeGroup(groupName = f'{analysisCode}_SWINGS')
            #[5-1-2]: Drawing
            swing_swings = swing['SWINGS']
            timestamp_prev = auxiliaries.getNextIntervalTickTimestamp(intervalID = chart_drawer.intervalID, timestamp = timestamp, nTicks = -1)
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



def cd_remove_expired_drawings(display_box_graphics, si_viewer_index, analysis_code, timestamp):
    pass



def cd_remove_drawings(drawn, display_box_graphics, si_viewer_index, analysis_code, graphics_removal_signal):
    #[1]: Drawings Removal
    if graphics_removal_signal&0b1: 
        display_box_graphics['KLINESPRICE']['RCLCG'].removeGroup(groupName = f"{analysis_code}_SWINGS")



def cd_get_vertical_magnitude_anchor(object_configuration):
    return None



def cd_on_GUI_theme_update(subpage, object_configuration, current_GUI_theme):
    #[1]: Instances
    sp  = subpage
    oc  = object_configuration
    cgt = current_GUI_theme

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        sp.GUIOs[f"INDICATOR_SWING{lIdx}_LINECOLOR"].updateColor(oc[f'SWING_{lIdx}_ColorR%{cgt}'], 
                                                                 oc[f'SWING_{lIdx}_ColorG%{cgt}'], 
                                                                 oc[f'SWING_{lIdx}_ColorB%{cgt}'], 
                                                                 oc[f'SWING_{lIdx}_ColorA%{cgt}'])



def cd_update_si_type_analysis_codes(analysis_parameters):
    return None



def cd_type_init(subPage):
    #[1]: Instances
    guios_THIS = subPage.GUIOs

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        guios_THIS[f"INDICATOR_SWING{lIdx}"].deactivate()
        guios_THIS[f"INDICATOR_SWING{lIdx}_SWINGRANGEINPUT"].deactivate()
#CHART DRAWER FUNCTIONS END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUTOTRADE PAGE FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def pg_autotrade_get_default_analysis_configuration():
    #[1]: Default Analysis Configuration
    dac = dict()

    #[2]: Setup
    dac['SWING_Master'] = False
    for lIdx in range (NMAXLINES):
        dac[f'SWING_{lIdx}_LineActive'] = False
        dac[f'SWING_{lIdx}_SwingRange'] = 0.005*(lIdx+1)

    #[3]: Return
    return dac



def pg_autotrade_configure_subpage_generate(subPageViewSpaceWidth, fn_get_text_pack):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'COLUMNTITLE_INDEX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1350, 'yPos': -300, 'width': 3200, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_SWINGRANGE'), 'fontSize': 80, 'anchor': 'SW'}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"SWING_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'SWING {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"SWING_{lIdx}_SWINGRANGE",
                       'TYPE':               'textInputBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 1350, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 3200, 'height': 250, 'style': 'styleA', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_autotrade_configure_subpage_setup(subpage, fn_get_text_pack):
    pass



def pg_autotrade_load_analysis_configuration(mainPage, subPage, analysis_configuration):
    #[1]: Main Page
    mainPage.GUIOs["INDICATORMASTERSWITCH_SWING"].setStatus(status = analysis_configuration['SWING_Master'], callStatusUpdateFunction = False)

    #[2]: Sub Page
    for lineIndex in range (NMAXLINES):
        if f'SWING_{lineIndex}_LineActive' in analysis_configuration:
            lineActive = analysis_configuration[f'SWING_{lineIndex}_LineActive']
            swingRange = analysis_configuration[f'SWING_{lineIndex}_SwingRange']
        else:
            lineActive = False
            swingRange = 0.005*(lineIndex+1)
        subPage.GUIOs[f"SWING_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        subPage.GUIOs[f"SWING_{lineIndex}_SWINGRANGE"].updateText(text = f"{swingRange:.4f}")



def pg_autotrade_format_analysis_configuration_from_guios(mainPage, subPage):
    #[1]: Instances
    configuration = dict()

    #[2]: Configuration Construction
    configuration['SWING_Master'] = mainPage.GUIOs["INDICATORMASTERSWITCH_SWING"].getStatus()
    for lineIndex in range (NMAXLINES):
        configuration[f'SWING_{lineIndex}_LineActive'] = subPage.GUIOs[f"SWING_{lineIndex}_LINE"].getStatus()
        configuration[f'SWING_{lineIndex}_SwingRange'] = round(float(subPage.GUIOs[f"SWING_{lineIndex}_SWINGRANGE"].getText()), 4)

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
                   'groupOrder': 0, 'xPos': 0, 'yPos': -300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'), 'fontSize': 80, 'anchor': 'SW'}))
    gList.append(({'NAME':               'COLUMNTITLE_SWINGRANGE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1350, 'yPos': -300, 'width': 3800, 'height': 250, 'style': 'styleB', 'text': fn_get_text_pack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_SWINGRANGE'), 'fontSize': 80, 'anchor': 'SW'}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"SWING_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'SWING {lIdx}', 'fontSize': 80}))
        gList.append(({'NAME':               f"SWING_{lIdx}_SWINGRANGE",
                       'TYPE':               'textBox_typeA',
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 1350, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 3800, 'height': 250, 'style': 'styleA', 'text': '-', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_simulation_result_configure_subpage_setup(subpage, fn_get_text_pack):
    for lIdx in range (NMAXLINES):
        subpage.GUIOs[f"SWING_{lIdx}_LINE"].deactivate()



def pg_simulation_result_load_analysis_configuration(mainPage, subPage, analysis_configuration, simulation_selected, fn_get_text_pack):
    if simulation_selected:
        #MAIN
        mainPage.GUIOs["INDICATORMASTERSWITCH_SWING"].setStatus(status = analysis_configuration['SWING_Master'], callStatusUpdateFunction = False)
        
        #SWING
        for lIdx in range (NMAXLINES):
            lineActive = analysis_configuration.get(f'SWING_{lIdx}_LineActive', False)
            if lineActive: 
                swingRange_str = f"{analysis_configuration[f'SWING_{lIdx}_SwingRange']:.4f}"
            else:          
                swingRange_str = "-"
            subPage.GUIOs[f"SWING_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
            subPage.GUIOs[f"SWING_{lIdx}_SWINGRANGE"].updateText(text = swingRange_str)
    else:
        #MAIN
        mainPage.GUIOs["INDICATORMASTERSWITCH_SWING"].setStatus(status = False, callStatusUpdateFunction = False)
        
        #SWING
        for lIdx in range (NMAXLINES):
            subPage.GUIOs[f"SWING_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
            subPage.GUIOs[f"SWING_{lIdx}_SWINGRANGE"].updateText(text = "-")
#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------