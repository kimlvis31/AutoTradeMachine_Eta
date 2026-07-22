#Imports
import auxiliaries
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
CD_FULL_DRAW_SIGNALS        = 0b00
CD_VVR_PRECISIONCOMPENSATOR = -2
CD_VVR_CENTERVALUE          = {'DEFAULT': 0.0}
CD_VVR_DEFAULT              = {'DEFAULT': 0.0}

def cd_get_initialized_config():
    pass



def cd_initialize_settings_sub_page():
    pass



def cd_match_guios_to_config():
    pass



def cd_on_settings_content_update():
    pass



def cd_on_position_highlight_update():
    pass



def cd_on_position_selection_update():
    pass



def cd_check_vertical_extremas():
    pass



def cd_draw(chartDrawer, drawSignal, timestamp, analysisCode):
    pass
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



def pg_autotrade_configure_subpage_generate(subPageViewSpaceWidth):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'COLUMNTITLE_INDEX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'TEXTPACK':           'AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': 0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'TEXTPACK':           'AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2325, 'yPos': 0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'fontSize': 80}))
    yPosPoint1 = -350
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"SMA_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'TEXT':               f'SMA {lIdx}',
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lIdx, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'fontSize': 80}))
        gList.append(({'NAME':               f"SMA_{lIdx}_NSAMPLES",
                       'TYPE':               'textInputBox_typeA',
                       'TEXT':               "",
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lIdx, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleA', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_autotrade_configure_subpage_setup(subpage):
    pass



def pg_autotrade_load_analysis_configuration(mainPage, subPage, analysis_configuration):
    #[1]: Main Page
    mainPage.GUIOs["INDICATORMASTERSWITCH_SMA"].setStatus(status      = analysis_configuration['SMA_Master'],     callStatusUpdateFunction = False)

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
def pg_simulation_result_configure_subpage_generate(subPageViewSpaceWidth):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'COLUMNTITLE_INDEX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'TEXTPACK':           'AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 0, 'yPos': 0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'TEXTPACK':           'AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2325, 'yPos': 0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'fontSize': 80}))
    yPosPoint1 = -350
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"SMA_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'TEXT':               f'SMA {lIdx}',
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-350*lIdx, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'fontSize': 80}))
        gList.append(({'NAME':               f"SMA_{lIdx}_NSAMPLES",
                       'TYPE':               'textInputBox_typeA',
                       'TEXT':               '-',
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lIdx, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleA', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_simulation_result_configure_subpage_setup(subpage):
    for lIdx in range (NMAXLINES):
        subpage.GUIOs[f"SMA_{lIdx}_LINE"].deactivate()



def pg_simulation_result_load_analysis_configuration(mainPage, subPage, analysis_configuration, simulation_selected):
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


