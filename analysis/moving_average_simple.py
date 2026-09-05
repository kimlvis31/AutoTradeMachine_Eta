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
        for lIdx in range (NMAXLINES):
            if ac[f'SMA_{lIdx}_LineActive']:
                nSamples = ac[f'SMA_{lIdx}_NSamples']
                width    = oc[f'SMA_{lIdx}_Width']
                display  = oc[f'SMA_{lIdx}_Display']
                guios_THIS[f"INDICATOR_SMA{lIdx}"].setStatus(status = True, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_SMA{lIdx}_INTERVALINPUT"].updateText(f"{nSamples}")
                guios_THIS[f"INDICATOR_SMA{lIdx}_WIDTHINPUT"].activate()
                guios_THIS[f"INDICATOR_SMA{lIdx}_WIDTHINPUT"].updateText(f"{width}")
                guios_THIS[f"INDICATOR_SMA{lIdx}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_SMA{lIdx}_DISPLAY"].activate()
            else:
                guios_THIS[f"INDICATOR_SMA{lIdx}"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_SMA{lIdx}_INTERVALINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_SMA{lIdx}_WIDTHINPUT"].deactivate()
                guios_THIS[f"INDICATOR_SMA{lIdx}_DISPLAY"].deactivate()
                guios_THIS[f"INDICATOR_SMA{lIdx}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
    else:
        guios_MAIN["MAININDICATOR_SMA"].setStatus(status = False, callStatusUpdateFunction = False)
        guios_MAIN["MAININDICATOR_SMA"].deactivate()
        guios_MAIN["MAININDICATORSETUP_SMA"].deactivate()



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



def cd_remove_expired_drawings(display_box_graphics, si_viewer_index, analysis_code, timestamp):
    #[1]: Drawings Removal
    display_box_graphics['KLINESPRICE']['RCLCG'].removeShape(shapeName = timestamp, groupName = analysis_code)



def cd_remove_drawings(drawn, display_box_graphics, si_viewer_index, analysis_code, graphics_removal_signal):
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
        sp.GUIOs[f"INDICATOR_SMA{lIdx}_LINECOLOR"].updateColor(oc[f'SMA_{lIdx}_ColorR%{cgt}'], 
                                                               oc[f'SMA_{lIdx}_ColorG%{cgt}'], 
                                                               oc[f'SMA_{lIdx}_ColorB%{cgt}'], 
                                                               oc[f'SMA_{lIdx}_ColorA%{cgt}'])



def cd_update_si_type_analysis_codes(analysis_parameters):
    return None



def cd_type_init(subPage):
    #[1]: Instances
    guios_THIS = subPage.GUIOs

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        guios_THIS[f"INDICATOR_SMA{lIdx}"].deactivate()
        guios_THIS[f"INDICATOR_SMA{lIdx}_INTERVALINPUT"].deactivate()
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
#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------