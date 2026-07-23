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

"""
#---SMA
if cac_iID['SMA_Master']:
    for lineIndex in range (constants.NLINES_SMA):
        lineActive = cac_iID.get(f'SMA_{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'SMA_{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
#---WMA
if cac_iID['WMA_Master']:
    for lineIndex in range (constants.NLINES_WMA):
        lineActive = cac_iID.get(f'WMA_{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'WMA_{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
#---EMA
if cac_iID['EMA_Master']:
    for lineIndex in range (constants.NLINES_EMA):
        lineActive = cac_iID.get(f'EMA_{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'EMA_{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
#---BOL
if cac_iID['BOL_Master']:
    for lineIndex in range (constants.NLINES_BOL):
        lineActive = cac_iID.get(f'BOL_{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'BOL_{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
#---IVP
if cac_iID['IVP_Master']:
    nSamples = cac_iID['IVP_NSamples']
    mmdrl = max(mmdrl, nSamples)
#---VOL
if cac_iID['VOL_Master']:
    for lineIndex in range (constants.NLINES_VOL):
        lineActive = cac_iID.get(f'VOL_{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'VOL_{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
#---MMACD
if cac_iID['MMACD_Master']:
    for lineIndex in range (constants.NLINES_MMACD):
        lineActive = cac_iID.get(f'MMACD_MA{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'MMACD_MA{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
#---DMIxADX
if cac_iID['DMIxADX_Master']:
    for lineIndex in range (constants.NLINES_DMIxADX):
        lineActive = cac_iID.get(f'DMIxADX_{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'DMIxADX_{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
#---MFI
if cac_iID['MFI_Master']:
    for lineIndex in range (constants.NLINES_MFI):
        lineActive = cac_iID.get(f'MFI_{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'MFI_{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
#---TPD
if cac_iID['TPD_Master']:
    for lineIndex in range (constants.NLINES_TPD):
        lineActive = cac_iID.get(f'TPD_{lineIndex}_LineActive', False)
        if not lineActive: continue
        viewLength = cac_iID[f'TPD_{lineIndex}_ViewLength']
        nSamples   = cac_iID[f'TPD_{lineIndex}_NSamples']
        nSamplesMA = cac_iID[f'TPD_{lineIndex}_NSamplesMA']
        mmdrl = max(mmdrl, viewLength+nSamples+nSamplesMA-1)
#---WOI
if cac_iID['WOI_Master']:
    for lineIndex in range (constants.NLINES_WOI):
        lineActive = cac_iID.get(f'WOI_{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'WOI_{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
#---NES
if cac_iID['NES_Master']:
    for lineIndex in range (constants.NLINES_NES):
        lineActive = cac_iID.get(f'NES_{lineIndex}_LineActive', False)
        if not lineActive: continue
        nSamples = cac_iID[f'NES_{lineIndex}_NSamples']
        mmdrl = max(mmdrl, nSamples)
"""
#ANALYZER FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#CHART DRAWER FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
CD_FULL_DRAW_SIGNALS        = 0b00
CD_VVR_PRECISIONCOMPENSATOR = -2
CD_VVR_CENTERVALUE          = {'DEFAULT': 0.0}
CD_VVR_DEFAULT              = {'DEFAULT': 0.0}

def cd_get_initialized_config():
    pass



def cd_initialize_settings_subpage_generate(subPageViewSpaceWidth):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'INDICATORINDEX_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'TEXTPACK':           'GUIO_CHARTDRAWER:INDEX',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': 800, 'height': 250, 'style': 'styleB', 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORINTERVAL_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'TEXTPACK':           'GUIO_CHARTDRAWER:INTERVAL',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':  900, 'yPos': -300, 'width': 900, 'height': 250, 'style': 'styleB', 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORWIDTH_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'TEXTPACK':           'GUIO_CHARTDRAWER:WIDTH',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 1900, 'yPos': -300, 'width': 750, 'height': 250, 'style': 'styleB', 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORCOLOR_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'TEXTPACK':           'GUIO_CHARTDRAWER:COLOR',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2750, 'yPos': -300, 'width': 650, 'height': 250, 'style': 'styleB', 'fontSize': 90}))
    gList.append(({'NAME':               'INDICATORDISPLAY_COLUMNTITLE',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'TEXTPACK':           'GUIO_CHARTDRAWER:DISPLAY',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 3500, 'yPos': -300, 'width': 500, 'height': 250, 'style': 'styleB', 'fontSize': 90}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"INDICATOR_SMA{lIdx}",
                       'TYPE':               'switch_typeC',
                       'TEXT':               f'SMA {lIdx}',
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': ['statusUpdateFunction',],
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 800, 'height': 250, 'style': 'styleB', 'fontSize': 80, 'name': f'SMA_LineActivationSwitch_{lIdx}'}))
        gList.append(({'NAME':               f"INDICATOR_SMA{lIdx}_INTERVALINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'TEXT':               "",
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos':  900, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 900, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
        gList.append(({'NAME':               f"INDICATOR_SMA{lIdx}_WIDTHINPUT",
                       'TYPE':               'textInputBox_typeA',
                       'TEXT':               "",
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': ['textUpdateFunction',],
                       'groupOrder': 0, 'xPos': 1900, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 750, 'height': 250, 'style': 'styleA', 'fontSize': 80}))
        gList.append(({'NAME':               f"INDICATOR_SMA{lIdx}_LINECOLOR",
                       'TYPE':               'LED_typeA',
                       'TEXT':               "",
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2750, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 650, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'mode': True}))
        gList.append(({'NAME':               f"INDICATOR_SMA{lIdx}_DISPLAY",
                       'TYPE':               'switch_typeB',
                       'TEXT':               "",
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': ['releaseFunction',],
                       'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 500, 'height': 250, 'style': 'styleA', 'fontSize': 80, 'name': f'SMA_DisplaySwitch_{lIdx}'}))

    #[3]: Return GUIO Generation List
    return gList



def cd_initialize_settings_subpage_setup(subpage):
    maList = {lIdx: {'text': f"SMA {lIdx}"} for lIdx in range (NMAXLINES)}
    subpage.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = maList, displayTargets = 'all')



"""
#<SMA & WMA & EMA Settings>
if (True):
    for miType in ('SMA', 'WMA', 'EMA'):
        ssp = self.settingsSubPages[miType]
        ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack(f'GUIO_CHARTDRAWER:TITLE_MI_{miType}'), 'fontSize': 100})
        ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width':                   400, 'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
        ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
        ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
        ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': f'{miType}_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': f'{miType}_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
        for index, componentType in enumerate(('R', 'G', 'B', 'A')):
            ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
            ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'{miType}_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
        ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
        ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  900, 'yPos': 7550, 'width': 900, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
        ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7550, 'width': 750, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
        ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2750, 'yPos': 7550, 'width': 650, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
        ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
        maList = dict()
        for lineIndex in range (_NMAXLINES[miType]):
            ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 800, 'height': 250, 'style': 'styleB', 'name': f'{miType}_LineActivationSwitch_{lineIndex}', 'text': f'{miType} {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  900, 'yPos': 7200-350*lineIndex, 'width': 900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'{miType}_IntervalTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200-350*lineIndex, 'width': 750, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'{miType}_WidthTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
            ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2750, 'yPos': 7200-350*lineIndex, 'width': 650, 'height': 250, 'style': 'styleA', 'mode': True})
            ssp.addGUIO(f"INDICATOR_{miType}{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'{miType}_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
            maList[f"{lineIndex}"] = {'text': f"{miType} {lineIndex}"}
        ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = maList, displayTargets = 'all')
        ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': 7200-350*(_NMAXLINES[miType]-1)-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': f'{miType}_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
#<PSAR Settings>
if (True):
    ssp = self.settingsSubPages['PSAR']
    ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_PSAR'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'PSAR_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'PSAR_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'PSAR_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",        generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),            'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORSTART_COLUMNTITLE",        generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  700, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PSARSTART'),        'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORACCELERATION_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PSARACCELERATION'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORMAXIMUM_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:PSARMAXIMUM'),      'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORSIZE_COLUMNTITLE",         generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7550, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SIZE'),             'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",        generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3000, 'yPos': 7550, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),            'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),          'fontSize': 90, 'anchor': 'SW'})
    psarList = dict()
    for lineIndex in range (_NMAXLINES['PSAR']):
        ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}",            generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleB', 'name': f'PSAR_LineActivationSwitch_{lineIndex}', 'text': f'PSAR {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_AF0INPUT",   generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  700, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'PSAR_AF0TextInputBox_{lineIndex}',   'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_AF+INPUT",   generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'PSAR_AF+TextInputBox_{lineIndex}',   'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'PSAR_AFMaxTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7200-350*lineIndex, 'width': 400, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'PSAR_WidthTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_LINECOLOR",  generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3000, 'yPos': 7200-350*lineIndex, 'width': 400, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_PSAR{lineIndex}_DISPLAY",    generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'PSAR_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
        psarList[f"{lineIndex}"] = {'text': f"PSAR {lineIndex}"}
    yPosPoint0 = 7200-350*(_NMAXLINES['PSAR']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'PSAR_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = psarList, displayTargets = 'all')
#<BOL Settings>
if (True):
    ssp = self.settingsSubPages['BOL']
    ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_BOL'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'BOL_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'BOL_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'BOL_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_BLOCKTITLE_MATYPE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_MATYPETEXT",        generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1550, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_MATYPESELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1650, 'yPos': 7200, 'width':                  2350, 'height': 250, 'style': 'styleA', 'name': 'BOL_MATypeSelection', 'nDisplay': 3, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    maTypes = {'SMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_SMA')},
                'WMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_WMA')},
                'EMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_EMA')}}
    ssp.GUIOs["INDICATOR_MATYPESELECTION"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),         'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  900, 'yPos': 6850, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVALSHORT'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORBANDWIDTH_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1600, 'yPos': 6850, 'width': 550, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BANDWIDTH'),     'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2250, 'yPos': 6850, 'width': 550, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),         'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2900, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),         'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),       'fontSize': 90, 'anchor': 'SW'})
    bolList = dict()
    for lineIndex in range (_NMAXLINES['BOL']):
        ssp.addGUIO(f"INDICATOR_BOL{lineIndex}",                generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*lineIndex, 'width': 800, 'height': 250, 'style': 'styleB', 'name': f'BOL_LineActivationSwitch_{lineIndex}', 'text': f'BOL {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_INTERVALINPUT",  generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  900, 'yPos': 6500-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'BOL_IntervalTextInputBox_{lineIndex}',  'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1600, 'yPos': 6500-350*lineIndex, 'width': 550, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'BOL_BandWidthTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_WIDTHINPUT",     generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2250, 'yPos': 6500-350*lineIndex, 'width': 550, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'BOL_WidthTextInputBox_{lineIndex}',     'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_LINECOLOR",      generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2900, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_BOL{lineIndex}_DISPLAY",        generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'BOL_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
        bolList[f"{lineIndex}"] = {'text': f"BOL {lineIndex}"}
    yPosPoint0 = 6500-350*(_NMAXLINES['BOL']-1)
    ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAYCONTENTS",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYCONTENTS'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_DISPLAYCONTENTS_BOLCENTERTEXT",   generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 700, 'width':                  3400, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYBOLCENTER'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISPLAYCONTENTS_BOLCENTERSWITCH", generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint0- 700, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'BOL_DisplayContentsSwitch_BolCenter', 'releaseFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_DISPLAYCONTENTS_BOLBANDTEXT",     generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1050, 'width':                  3400, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYBOLBAND'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISPLAYCONTENTS_BOLBANDSWITCH",   generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 3500, 'yPos': yPosPoint0-1050, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'BOL_DisplayContentsSwitch_BolBand', 'releaseFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-1400, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'BOL_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = bolList, displayTargets = 'all')
#<IVP Settings>
if (True):
    ssp = self.settingsSubPages['IVP']
    ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_IVP'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width':                  1500, 'height': 250, 'style': 'styleA', 'name': 'IVP_LineSelectionBox', 'nDisplay': 9, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':                   950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':                   650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'IVP_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'IVP_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ivpLineTargets = {'VPLP':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLP')},
                        'VPLPB': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPB')}}
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = ivpLineTargets, displayTargets = 'all')
    ssp.addGUIO("INDICATOR_BLOCKTITLE_IVPDISPLAY", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_VPLP_DISPLAYTEXT",             generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPDISPLAY'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLP_DISPLAYSWITCH",           generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1900, 'yPos': 7200, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'IVP_DisplaySwitch_VPLP', 'statusUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_VPLP_COLORTEXT",               generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 7200, 'width':  700, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLP_COLOR",                   generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3300, 'yPos': 7200, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATOR_VPLP_DISPLAYWIDTHTEXT",        generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYWIDTH'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLP_DISPLAYWIDTHSLIDER",      generals.slider_typeA,  {'groupOrder': 0, 'xPos': 1300, 'yPos': 6900, 'width': 2000, 'height': 150, 'style': 'styleA', 'name': 'IVP_DisplayWidthSlider_VPLP', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_VPLP_DISPLAYWIDTHVALUETEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3400, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLPB_DISPLAYTEXT",            generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VPLPBDISPLAY'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLPB_DISPLAYSWITCH",          generals.switch_typeB,  {'groupOrder': 0, 'xPos': 1900, 'yPos': 6500, 'width':  500, 'height': 250, 'style': 'styleA', 'name': 'IVP_DisplaySwitch_VPLPB', 'statusUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_VPLPB_COLORTEXT",              generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLPB_COLOR",                  generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3300, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATOR_VPLPB_DISPLAYREGIONTEXT",      generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 6150, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYREGION'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VPLPB_DISPLAYREGIONSLIDER",    generals.slider_typeA,  {'groupOrder': 0, 'xPos': 1400, 'yPos': 6200, 'width': 1800, 'height': 150, 'style': 'styleA', 'name': 'IVP_VPLPBDisplayRegion', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT", generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 6150, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_BLOCKTITLE_IVPPARAMS", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': 5800, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPPARAMS'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_INTERVAL_DISPLAYTEXT",    generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 5450, 'width': 1900, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_INTERVAL_INPUTTEXT",      generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 5450, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'IVP_Interval', 'textUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_GAMMAFACTOR_DISPLAYTEXT", generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 5100, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPGAMMAFACTOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_GAMMAFACTOR_SLIDER",      generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 5150, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_GammaFactor', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_GAMMAFACTOR_VALUETEXT",   generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 5100, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DELTAFACTOR_DISPLAYTEXT", generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 4750, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPDELTAFACTOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DELTAFACTOR_SLIDER",      generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 4800, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_DeltaFactor', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_DELTAFACTOR_VALUETEXT",   generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 4750, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    
    ssp.addGUIO("INDICATOR_PROMINENCE_DISPLAYTEXT",  generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 4400, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPPROMINENCE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_PROMINENCE_SLIDER",       generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 4450, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_Prominence', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_PROMINENCE_VALUETEXT",    generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 4400, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISTANCE_DISPLAYTEXT",    generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 4050, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPDISTANCE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISTANCE_SLIDER",         generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 4100, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_Distance', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_DISTANCE_VALUETEXT",      generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 4050, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_HEIGHT_DISPLAYTEXT",      generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 3700, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:IVPHEIGHT'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_HEIGHT_SLIDER",           generals.slider_typeA,       {'groupOrder': 0, 'xPos': 1100, 'yPos': 3750, 'width': 2100, 'height': 150, 'style': 'styleA', 'name': 'IVP_Height', 'valueUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_HEIGHT_VALUETEXT",        generals.textBox_typeA,      {'groupOrder': 0, 'xPos': 3300, 'yPos': 3700, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': 3350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'IVP_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
#<SWING Settings>
if (True):
    ssp = self.settingsSubPages['SWING']
    ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_MI_SWING'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'SWING_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'SWING_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'SWING_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),      'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORSWINGRANGE_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7550, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SWINGRANGE'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2300, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),      'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2900, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),      'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),    'fontSize': 90, 'anchor': 'SW'})
    swingList = dict()
    for lineIndex in range (_NMAXLINES['SWING']):
        ssp.addGUIO(f"INDICATOR_SWING{lineIndex}",                 generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'SWING_LineActivationSwitch_{lineIndex}', 'text': f'SWING {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 7200-350*lineIndex, 'width': 1100, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'SWING_SwingRangeTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_WIDTHINPUT",      generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2300, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'SWING_WidthTextInputBox_{lineIndex}', 'text': "", 'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_LINECOLOR",       generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2900, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_SWING{lineIndex}_DISPLAY",         generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'SWING_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
        swingList[f"{lineIndex}"] = {'text': f"SWING {lineIndex}"}
    yPosPoint0 = 7200-350*(_NMAXLINES['SWING']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'SWING_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = swingList, displayTargets = 'all')
#<VOL Settings>
if (True):
    ssp = self.settingsSubPages['VOL']
    ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_VOL'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'VOL_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'VOL_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'VOL_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATORINDEX_BLOCKTITLE_MA",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLSETTINGS'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_VOLTYPETEXT",      generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_VOLTYPESELECTION", generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1900, 'yPos': 7200, 'width': 2100, 'height': 250, 'style': 'styleA', 'name': 'VOL_VolTypeSelection', 'nDisplay': 4, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    volTypes = {'BASE':    {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_BASE')},
                'QUOTE':   {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_QUOTE')},
                'BASETB':  {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_BASETB')},
                'QUOTETB': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VOLTYPE_QUOTETB')}}
    ssp.GUIOs["INDICATOR_VOLTYPESELECTION"].setSelectionList(selectionList = volTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATOR_MATYPETEXT",       generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1800, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_MATYPESELECTION",  generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1900, 'yPos': 6850, 'width': 2100, 'height': 250, 'style': 'styleA', 'name': 'VOL_MATypeSelection', 'nDisplay': 3, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    maTypes = {'SMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_SMA')},
                'WMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_WMA')},
                'EMA': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MATYPE_EMA')}}
    ssp.GUIOs["INDICATOR_MATYPESELECTION"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 6500, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    volMAList = dict()
    for lineIndex in range (_NMAXLINES['VOL']):
        ssp.addGUIO(f"INDICATOR_VOL{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6150-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'VOL_LineActivationSwitch_{lineIndex}', 'text': f'VOLMA {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_VOL{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6150-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'VOL_IntervalTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_VOL{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 6150-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'VOL_WidthTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_VOL{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 6150-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_VOL{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6150-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'VOL_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
        volMAList[f"{lineIndex}"] = {'text': f"VOLMA {lineIndex}"}
    yPosPoint0 = 6150-350*(_NMAXLINES['VOL']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'VOL_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = volMAList, displayTargets = 'all')

#<NNA Settings>
if (True):
    ssp = self.settingsSubPages['NNA']
    ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_NNA'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'NNA_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'NNA_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'NNA_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),             'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORNNCODE_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  700, 'yPos': 7550, 'width':  900, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NEURALNETWORKCODE'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORALPHA_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1700, 'yPos': 7550, 'width':  400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:ALPHA'),             'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORBETA_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2200, 'yPos': 7550, 'width':  300, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:BETA'),              'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORSIZE_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2600, 'yPos': 7550, 'width':  300, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:SIZE'),              'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3000, 'yPos': 7550, 'width':  400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),             'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 7550, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),           'fontSize': 90, 'anchor': 'SW'})
    nnaList = dict()
    for lineIndex in range (_NMAXLINES['NNA']):
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}",             generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 7200-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleB', 'name': f'NNA_LineActivationSwitch_{lineIndex}', 'text': f'NNA {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_NNCODEINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  700, 'yPos': 7200-350*lineIndex, 'width':  900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_NNCodeTextInputBox_{lineIndex}', 'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_ALPHAINPUT",  generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1700, 'yPos': 7200-350*lineIndex, 'width':  400, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_AlphaTextInputBox_{lineIndex}',  'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_BETAINPUT",   generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2200, 'yPos': 7200-350*lineIndex, 'width':  300, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_BetaTextInputBox_{lineIndex}',   'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_WIDTHINPUT",  generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2600, 'yPos': 7200-350*lineIndex, 'width':  300, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': f'NNA_WidthTextInputBox_{lineIndex}',  'textUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_LINECOLOR",   generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3000, 'yPos': 7200-350*lineIndex, 'width':  400, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_NNA{lineIndex}_DISPLAY",     generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 7200-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'NNA_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
        nnaList[f"{lineIndex}"] = {'text': f"NNA {lineIndex}"}
    yPosPoint0 = 7200-350*(_NMAXLINES['NNA']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'NNA_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = nnaList, displayTargets = 'all')
#<MMACD Settings>
if (True):
    ssp = self.settingsSubPages['MMACD']
    ssp.addGUIO("SUBPAGETITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_MMACD'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",    generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':                   550, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width':                  1500, 'height': 250, 'style': 'styleA', 'name': 'MMACD_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':                   950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':                   650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'MMACD_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'MMACD_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    mmacdLineTargets = {'MMACD':      {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACD')},
                        'SIGNAL':     {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNAL')},
                        'HISTOGRAM+': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM+')},
                        'HISTOGRAM-': {'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAM-')}}
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = mmacdLineTargets, displayTargets = 'all')
    ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",        generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_MMACD_DISPLAYTEXT",         generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDMMACDDISPLAY'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_MMACD_DISPLAYSWITCH",       generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 7200, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACD_DisplaySwitch_MMACD', 'statusUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_MMACD_COLORTEXT",           generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 7200, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_MMACD_COLOR",               generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 7200, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATOR_SIGNAL_DISPLAYTEXT",        generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALDISPLAY'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_SIGNAL_DISPLAYSWITCH",      generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 6850, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACD_DisplaySwitch_SIGNAL', 'statusUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_SIGNAL_COLORTEXT",          generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 6850, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_SIGNAL_COLOR",              generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 6850, 'width':                  1100, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATOR_HISTOGRAM_DISPLAYTEXT",     generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 6500, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAMDISPLAY'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_HISTOGRAM_DISPLAYSWITCH",   generals.switch_typeB,                 {'groupOrder': 0, 'xPos': 1600, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'name': 'MMACD_DisplaySwitch_HISTOGRAM', 'statusUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATOR_HISTOGRAM_COLORTEXT",       generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2200, 'yPos': 6500, 'width':                   600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_HISTOGRAM+_COLOR",          generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2900, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATOR_HISTOGRAM-_COLOR",          generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500, 'width':                   500, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATOR_HISTOGRAMTYPE_DISPLAYTEXT", generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 6150, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDHISTOGRAMTYPE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_HISTOGRAMTYPE_SELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1600, 'yPos': 6150, 'width':                  2400, 'height': 250, 'style': 'styleA', 'name': 'MMACD_HistrogramTypeSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    histogramTypes = {'MSDELTA':          {'text': 'MSDELTA'},
                        'MSDELTA_ABSMA':    {'text': 'MSDELTA_ABSMA'},
                        'MSDELTA_ABSMAREL': {'text': 'MSDELTA_ABSMAREL'}}
    ssp.GUIOs["INDICATOR_HISTOGRAMTYPE_SELECTION"].setSelectionList(selectionList = histogramTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATOR_BLOCKTITLE_MMACDSETTINGS",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 5800, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSETTINGS'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_SIGNALINTERVALTEXT",         generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 5450, 'width':                  3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MMACDSIGNALINTERVAL'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_SIGNALINTERVALTEXTINPUT",    generals.textInputBox_typeA,           {'groupOrder': 0, 'xPos': 3100, 'yPos': 5450, 'width':                   900, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80, 'name': 'MMACD_SignalIntervalTextInputBox', 'textUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE1",          generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE1",       generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE2",          generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2050, 'yPos': 5100, 'width':                  1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE2",       generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3150, 'yPos': 5100, 'width':                   850, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
    for lineIndex in range (_NMAXLINES['MMACD']):
        rowNumber = math.ceil((lineIndex+1)/2)
        if (lineIndex%2 == 0): coordX = 0
        else:                  coordX = 2050
        ssp.addGUIO(f"INDICATOR_MMACDMA{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos': coordX,      'yPos': 5100-rowNumber*350, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'MMACD_LineActivationSwitch_{lineIndex}', 'text': f'MA {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': coordX+1100, 'yPos': 5100-rowNumber*350, 'width':  850, 'height': 250, 'style': 'styleA', 'name': f'MMACD_IntervalTextInputBox_{lineIndex}', 'text': "",                'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
    yPosPoint0 = 5100-math.ceil(_NMAXLINES['MMACD']/2)*350
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'MMACD_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
#<DMIxADX Settings>
if (True):
    ssp = self.settingsSubPages['DMIxADX']
    ssp.addGUIO("SUBPAGETITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_DMIxADX'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",        generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'DMIxADX_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'DMIxADX_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'DMIxADX_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DMIXADXDISPLAY'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_DISPLAYTEXT", generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTYPE'),    'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_SELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1600, 'yPos': 7200, 'width':                  2400, 'height': 250, 'style': 'styleA', 'name': 'DMIxADX_DisplayTypeSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    displayTypes = {'DMIxADX':          {'text': 'DMIxADX'},
                    'DMIxADX_ABSMA':    {'text': 'DMIxADX_ABSMA'},
                    'DMIxADX_ABSMAREL': {'text': 'DMIxADX_ABSMAREL'}}
    ssp.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].setSelectionList(selectionList = displayTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1300, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2000, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 6850, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    dmixadxList = dict()
    for lineIndex in range (_NMAXLINES['DMIxADX']):
        ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*lineIndex, 'width': 1200, 'height': 250, 'style': 'styleB', 'name': f'DMIxADX_LineActivationSwitch_{lineIndex}', 'text': f'DMIxADX {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'DMIxADX_IntervalTextInputBox_{lineIndex}', 'text': "",                     'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'DMIxADX_WidthTextInputBox_{lineIndex}',    'text': "",                     'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 6500-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_DMIxADX{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'DMIxADX_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
        dmixadxList[f"{lineIndex}"] = {'text': f"DMIxADX {lineIndex}"}
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = dmixadxList, displayTargets = 'all')
    yPosPoint0 = 6500-350*(_NMAXLINES['DMIxADX']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'DMIxADX_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
#<MFI Settings>
if (True):
    ssp = self.settingsSubPages['MFI']
    ssp.addGUIO("SUBPAGETITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_MFI'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",        generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'MFI_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'MFI_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'MFI_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MFIDISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_DISPLAYTEXT", generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTYPE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_SELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1600, 'yPos': 7200, 'width':                  2400, 'height': 250, 'style': 'styleA', 'name': 'MFI_DisplayTypeSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    displayTypes = {'MFI':             {'text': 'MFI'},
                    'MFI_DEVABSMA':    {'text': 'MFI_DEVABSMA'},
                    'MFI_DEVABSMAREL': {'text': 'MFI_DEVABSMAREL'}}
    ssp.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].setSelectionList(selectionList = displayTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6850, 'width':  800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2000, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2700, 'yPos': 6850, 'width':  700, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    mfiList = dict()
    for lineIndex in range (_NMAXLINES['MFI']):
        ssp.addGUIO(f"INDICATOR_MFI{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'MFI_LineActivationSwitch_{lineIndex}', 'text': f'MFI {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6500-350*lineIndex, 'width':  800, 'height': 250, 'style': 'styleA', 'name': f'MFI_IntervalTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'MFI_WidthTextInputBox_{lineIndex}',    'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2700, 'yPos': 6500-350*lineIndex, 'width':  700, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_MFI{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'MFI_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
        mfiList[f"{lineIndex}"] = {'text': f"MFI {lineIndex}"}
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = mfiList, displayTargets = 'all')
    yPosPoint0 = 6500-350*(_NMAXLINES['MFI']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'MFI_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
#<TPD Settings>
if (True):
    ssp = self.settingsSubPages['TPD']
    ssp.addGUIO("SUBPAGETITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_TPD'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",        generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'TPD_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'TPD_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'TPD_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TPDDISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_DISPLAYTEXT", generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTYPE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_SELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1600, 'yPos': 7200, 'width':                  2400, 'height': 250, 'style': 'styleA', 'name': 'TPD_DisplayTypeSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    displayTypes = {'TPD':          {'text': 'TPD'},
                    'TPD_ABSMA':    {'text': 'TPD_ABSMA'},
                    'TPD_ABSMAREL': {'text': 'TPD_ABSMAREL'}}
    ssp.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].setSelectionList(selectionList = displayTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),         'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORVIEWLENGTH_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':  700, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:VIEWLENGTH'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE",   generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1300, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVALSHORT'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORMAINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1900, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:MAINTERVAL'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2500, 'yPos': 6850, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),         'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3000, 'yPos': 6850, 'width': 400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),         'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width': 500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),       'fontSize': 90, 'anchor': 'SW'})
    tpdList = dict()
    for lineIndex in range (_NMAXLINES['TPD']):
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}",                 generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*lineIndex, 'width': 600, 'height': 250, 'style': 'styleB', 'name': f'TPD_LineActivationSwitch_{lineIndex}',   'text': f'TPD {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos':  700, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'TPD_ViewLengthTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_INTERVALINPUT",   generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'TPD_IntervalTextInputBox_{lineIndex}',   'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1900, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'TPD_MAIntervalTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_WIDTHINPUT",      generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2500, 'yPos': 6500-350*lineIndex, 'width': 400, 'height': 250, 'style': 'styleA', 'name': f'TPD_WidthTextInputBox_{lineIndex}',      'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_LINECOLOR",       generals.LED_typeA,          {'groupOrder': 0, 'xPos': 3000, 'yPos': 6500-350*lineIndex, 'width': 400, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_TPD{lineIndex}_DISPLAY",         generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*lineIndex, 'width': 500, 'height': 250, 'style': 'styleA', 'name': f'TPD_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
        tpdList[f"{lineIndex}"] = {'text': f"TPD {lineIndex}"}
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList = tpdList, displayTargets = 'all')
    yPosPoint0 = 6500-350*(_NMAXLINES['TPD']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'TPD_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
#<WOI Settings>
if (True):
    ssp = self.settingsSubPages['WOI']
    ssp.addGUIO("SUBPAGETITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_WOI'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",        generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'WOI_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'WOI_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'WOI_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WOIDISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_DISPLAYTEXT", generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTYPE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_SELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1600, 'yPos': 7200, 'width':                  2400, 'height': 250, 'style': 'styleA', 'name': 'WOI_DisplayTypeSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    displayTypes = {'WOI':          {'text': 'WOI'},
                    'WOI_ABSMA':    {'text': 'WOI_ABSMA'},
                    'WOI_ABSMAREL': {'text': 'WOI_ABSMAREL'}}
    ssp.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].setSelectionList(selectionList = displayTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6850, 'width':  900, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2100, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2800, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    for lineIndex in range (_NMAXLINES['WOI']):
        ssp.addGUIO(f"INDICATOR_WOI{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'WOI_LineActivationSwitch_{lineIndex}', 'text': f'WOI {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_WOI{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6500-350*lineIndex, 'width':  900, 'height': 250, 'style': 'styleA', 'name': f'WOI_IntervalTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_WOI{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'WOI_WidthTextInputBox_{lineIndex}',    'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_WOI{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2800, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_WOI{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'WOI_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList  = {f"{lIdx}": {'text': f"WOI {lIdx}"} for lIdx in range (_NMAXLINES['WOI'])},
                                                                    displayTargets = 'all')
    yPosPoint0 = 6500-350*(_NMAXLINES['WOI']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'WOI_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
#<NES Settings>
if (True):
    ssp = self.settingsSubPages['NES']
    ssp.addGUIO("SUBPAGETITLE",     generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 10000, 'width': subPageViewSpaceWidth, 'height': 300, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:TITLE_SI_NES'), 'fontSize': 100})
    ssp.addGUIO("NAGBUTTON",        generals.button_typeB,                 {'groupOrder': 0, 'xPos': 3600, 'yPos': 10050, 'width': 400,                   'height': 200, 'style': 'styleB', 'image': 'returnIcon_512x512.png', 'imageSize': (170, 170), 'imageRGBA': self.visualManager.getFromColorTable('ICON_COLORING'), 'name': 'navButton_toHome', 'releaseFunction': self.__onSettingsNavButtonClick})
    ssp.addGUIO("INDICATORCOLOR_TITLE",           generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 9650, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINECOLOR'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_TEXT",            generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 9300, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
    ssp.addGUIO("INDICATORCOLOR_TARGETSELECTION", generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos':  700, 'yPos': 9300, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'NES_LineSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    ssp.addGUIO("INDICATORCOLOR_LED",             generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 2300, 'yPos': 9300, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
    ssp.addGUIO("INDICATORCOLOR_APPLYCOLOR",      generals.button_typeA,                 {'groupOrder': 0, 'xPos': 3350, 'yPos': 9300, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'NES_ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
    for index, componentType in enumerate(('R', 'G', 'B', 'A')):
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_TEXT",   generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': 8950-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_SLIDER", generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': 8950-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'NES_Color_{componentType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATORCOLOR_{componentType}_VALUE",  generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': 8950-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    ssp.addGUIO("INDICATOR_BLOCKTITLE_DISPLAY",      generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 7550, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:NESDISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_DISPLAYTEXT", generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': 7200, 'width':                  1500, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAYTYPE'), 'fontSize': 80})
    ssp.addGUIO("INDICATOR_DISPLAYTYPE_SELECTION",   generals.selectionBox_typeB,           {'groupOrder': 2, 'xPos': 1600, 'yPos': 7200, 'width':                  2400, 'height': 250, 'style': 'styleA', 'name': 'NES_DisplayTypeSelectionBox', 'nDisplay': 10, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
    displayTypes = {'NES':          {'text': 'NES'},
                    'NES_ABSMA':    {'text': 'NES_ABSMA'},
                    'NES_ABSMAREL': {'text': 'NES_ABSMAREL'}}
    ssp.GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].setSelectionList(selectionList = displayTypes, displayTargets = 'all')
    ssp.addGUIO("INDICATORINDEX_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': 6850, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INDEX'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORINTERVAL_COLUMNTITLE", generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6850, 'width':  900, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:INTERVAL'), 'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORWIDTH_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2100, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:WIDTH'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORCOLOR_COLUMNTITLE",    generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2800, 'yPos': 6850, 'width':  600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:COLOR'),    'fontSize': 90, 'anchor': 'SW'})
    ssp.addGUIO("INDICATORDISPLAY_COLUMNTITLE",  generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': 6850, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:DISPLAY'),  'fontSize': 90, 'anchor': 'SW'})
    for lineIndex in range (_NMAXLINES['NES']):
        ssp.addGUIO(f"INDICATOR_NES{lineIndex}",               generals.switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': 6500-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'name': f'NES_LineActivationSwitch_{lineIndex}', 'text': f'NES {lineIndex}', 'fontSize': 80, 'statusUpdateFunction': self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NES{lineIndex}_INTERVALINPUT", generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': 6500-350*lineIndex, 'width':  900, 'height': 250, 'style': 'styleA', 'name': f'NES_IntervalTextInputBox_{lineIndex}', 'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NES{lineIndex}_WIDTHINPUT",    generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'name': f'NES_WidthTextInputBox_{lineIndex}',    'text': "",                 'fontSize': 80, 'textUpdateFunction':   self.__onSettingsContentUpdate})
        ssp.addGUIO(f"INDICATOR_NES{lineIndex}_LINECOLOR",     generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2800, 'yPos': 6500-350*lineIndex, 'width':  600, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp.addGUIO(f"INDICATOR_NES{lineIndex}_DISPLAY",       generals.switch_typeB,       {'groupOrder': 0, 'xPos': 3500, 'yPos': 6500-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'name': f'NES_DisplaySwitch_{lineIndex}', 'releaseFunction': self.__onSettingsContentUpdate})
    ssp.GUIOs["INDICATORCOLOR_TARGETSELECTION"].setSelectionList(selectionList  = {f"{lIdx}": {'text': f"NES {lIdx}"} for lIdx in range (_NMAXLINES['NES'])},
                                                                    displayTargets = 'all')
    yPosPoint0 = 6500-350*(_NMAXLINES['NES']-1)
    ssp.addGUIO("APPLYNEWSETTINGS", generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'NES_ApplySettings', 'releaseFunction': self.__onSettingsContentUpdate})
"""

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


"""
guios_SMA      = ssps['SMA'].GUIOs
guios_WMA      = ssps['WMA'].GUIOs
guios_EMA      = ssps['EMA'].GUIOs
guios_PSAR     = ssps['PSAR'].GUIOs
guios_BOL      = ssps['BOL'].GUIOs
guios_IVP      = ssps['IVP'].GUIOs
guios_SWING    = ssps['SWING'].GUIOs
guios_VOL      = ssps['VOL'].GUIOs
guios_NNA      = ssps['NNA'].GUIOs
guios_MMACD    = ssps['MMACD'].GUIOs
guios_DMIxADX  = ssps['DMIxADX'].GUIOs
guios_MFI      = ssps['MFI'].GUIOs
guios_TPD      = ssps['TPD'].GUIOs
guios_WOI      = ssps['WOI'].GUIOs
guios_NES      = ssps['NES'].GUIOs
#<SMA>
if (True):
    guios_MAIN["MAININDICATOR_SMA"].setStatus(oc['SMA_Master'], callStatusUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['SMA']):
        lineActive = oc[f'SMA_{lineIndex}_LineActive']
        nSamples   = oc[f'SMA_{lineIndex}_NSamples']
        width      = oc[f'SMA_{lineIndex}_Width']
        color      = (oc[f'SMA_{lineIndex}_ColorR%{cgt}'],
                        oc[f'SMA_{lineIndex}_ColorG%{cgt}'],
                        oc[f'SMA_{lineIndex}_ColorB%{cgt}'],
                        oc[f'SMA_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'SMA_{lineIndex}_Display']
        guios_SMA[f"INDICATOR_SMA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_SMA[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_SMA[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_SMA[f"INDICATOR_SMA{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_SMA[f"INDICATOR_SMA{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_SMA["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_SMA["APPLYNEWSETTINGS"].deactivate()
#<WMA>
if (True):
    guios_MAIN["MAININDICATOR_WMA"].setStatus(oc['WMA_Master'], callStatusUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['WMA']):
        lineActive = oc[f'WMA_{lineIndex}_LineActive']
        nSamples   = oc[f'WMA_{lineIndex}_NSamples']
        width      = oc[f'WMA_{lineIndex}_Width']
        color      = (oc[f'WMA_{lineIndex}_ColorR%{cgt}'],
                        oc[f'WMA_{lineIndex}_ColorG%{cgt}'],
                        oc[f'WMA_{lineIndex}_ColorB%{cgt}'],
                        oc[f'WMA_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'WMA_{lineIndex}_Display']
        guios_WMA[f"INDICATOR_WMA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_WMA[f"INDICATOR_WMA{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_WMA[f"INDICATOR_WMA{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_WMA[f"INDICATOR_WMA{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_WMA[f"INDICATOR_WMA{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_WMA["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_WMA["APPLYNEWSETTINGS"].deactivate()
#<EMA>
if (True):
    guios_MAIN["MAININDICATOR_EMA"].setStatus(oc['EMA_Master'], callStatusUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['EMA']):
        lineActive = oc[f'EMA_{lineIndex}_LineActive']
        nSamples   = oc[f'EMA_{lineIndex}_NSamples']
        width      = oc[f'EMA_{lineIndex}_Width']
        color      = (oc[f'EMA_{lineIndex}_ColorR%{cgt}'],
                        oc[f'EMA_{lineIndex}_ColorG%{cgt}'],
                        oc[f'EMA_{lineIndex}_ColorB%{cgt}'],
                        oc[f'EMA_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'EMA_{lineIndex}_Display']
        guios_EMA[f"INDICATOR_EMA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_EMA[f"INDICATOR_EMA{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_EMA[f"INDICATOR_EMA{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_EMA[f"INDICATOR_EMA{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_EMA[f"INDICATOR_EMA{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_EMA["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_EMA["APPLYNEWSETTINGS"].deactivate()
#<PSAR>
if (True):
    guios_MAIN["MAININDICATOR_PSAR"].setStatus(oc['PSAR_Master'], callStatusUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['PSAR']):
        lineActive = oc[f'PSAR_{lineIndex}_LineActive']
        af0        = oc[f'PSAR_{lineIndex}_AF0']
        afPlus     = oc[f'PSAR_{lineIndex}_AF+']
        afMax      = oc[f'PSAR_{lineIndex}_AFMax']
        width      = oc[f'PSAR_{lineIndex}_Width']
        color      = (oc[f'PSAR_{lineIndex}_ColorR%{cgt}'], 
                        oc[f'PSAR_{lineIndex}_ColorG%{cgt}'], 
                        oc[f'PSAR_{lineIndex}_ColorB%{cgt}'], 
                        oc[f'PSAR_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'PSAR_{lineIndex}_Display']
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF0INPUT"].updateText(text   = f"{af0:.3f}")
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF+INPUT"].updateText(text   = f"{afPlus:.3f}")
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT"].updateText(text = f"{afMax:.3f}")
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_PSAR["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_PSAR["APPLYNEWSETTINGS"].deactivate()
#<BOL>
if (True):
    guios_MAIN["MAININDICATOR_BOL"].setStatus(oc['BOL_Master'], callStatusUpdateFunction = False)
    guios_BOL["INDICATOR_MATYPESELECTION"].setSelected(oc['BOL_MAType'], callSelectionUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['BOL']):
        lineActive = oc[f'BOL_{lineIndex}_LineActive']
        nSamples   = oc[f'BOL_{lineIndex}_NSamples']
        bandWidth  = oc[f'BOL_{lineIndex}_BandWidth']
        width      = oc[f'BOL_{lineIndex}_Width']
        color      = (oc[f'BOL_{lineIndex}_ColorR%{cgt}'], 
                        oc[f'BOL_{lineIndex}_ColorG%{cgt}'], 
                        oc[f'BOL_{lineIndex}_ColorB%{cgt}'], 
                        oc[f'BOL_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'BOL_{lineIndex}_Display']
        guios_BOL[f"INDICATOR_BOL{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_BOL[f"INDICATOR_BOL{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_BOL[f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT"].updateText(text = f"{bandWidth:.1f}")
        guios_BOL[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_BOL[f"INDICATOR_BOL{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_BOL[f"INDICATOR_BOL{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_BOL["INDICATOR_DISPLAYCONTENTS_BOLCENTERSWITCH"].setStatus(oc['BOL_DisplayCenterLine'], callStatusUpdateFunction = False)
    guios_BOL["INDICATOR_DISPLAYCONTENTS_BOLBANDSWITCH"].setStatus(oc['BOL_DisplayBand'], callStatusUpdateFunction = False)
    guios_BOL["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_BOL["APPLYNEWSETTINGS"].deactivate()
#<IVP>
if (True):
    guios_MAIN["MAININDICATOR_IVP"].setStatus(oc['IVP_Master'],                 callStatusUpdateFunction = False)
    guios_IVP["INDICATOR_VPLP_DISPLAYSWITCH"].setStatus(oc['IVP_VPLP_Display'], callStatusUpdateFunction = False)
    guios_IVP["INDICATOR_VPLP_COLOR"].updateColor(oc[f'IVP_VPLP_ColorR%{cgt}'], 
                                                    oc[f'IVP_VPLP_ColorG%{cgt}'], 
                                                    oc[f'IVP_VPLP_ColorB%{cgt}'], 
                                                    oc[f'IVP_VPLP_ColorA%{cgt}'])
    guios_IVP["INDICATOR_VPLP_DISPLAYWIDTHSLIDER"].setSliderValue(newValue = (oc['IVP_VPLP_DisplayWidth']-0.1)/0.9*100, callValueUpdateFunction = False)
    guios_IVP["INDICATOR_VPLP_DISPLAYWIDTHVALUETEXT"].updateText(str(oc['IVP_VPLP_DisplayWidth']))
    guios_IVP["INDICATOR_VPLPB_DISPLAYSWITCH"].setStatus(oc['IVP_VPLPB_Display'], callStatusUpdateFunction = False)
    guios_IVP["INDICATOR_VPLPB_COLOR"].updateColor(oc[f'IVP_VPLPB_ColorR%{cgt}'], 
                                                    oc[f'IVP_VPLPB_ColorG%{cgt}'], 
                                                    oc[f'IVP_VPLPB_ColorB%{cgt}'], 
                                                    oc[f'IVP_VPLPB_ColorA%{cgt}'])
    
    vplpb_dRegion = oc['IVP_VPLPB_DisplayRegion']
    nSamples      = oc['IVP_NSamples']
    gammaFactor   = oc['IVP_GammaFactor']
    deltaFactor   = oc['IVP_DeltaFactor']
    prominence    = oc['IVP_Prominence']
    distance      = oc['IVP_Distance']
    height        = oc['IVP_Height']
    guios_IVP["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].setSliderValue(newValue = (vplpb_dRegion-0.050)*(100/0.950), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT"].updateText(f"{vplpb_dRegion*100:.1f} %")
    guios_IVP["INDICATOR_INTERVAL_INPUTTEXT"].updateText(text = f"{nSamples}")
    guios_IVP["INDICATOR_GAMMAFACTOR_SLIDER"].setSliderValue(newValue = (gammaFactor-0.005)*(100/0.095), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(text = f"{gammaFactor*100:.1f} %")
    guios_IVP["INDICATOR_DELTAFACTOR_SLIDER"].setSliderValue(newValue = (deltaFactor-0.1)*(100/9.9), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(text = f"{int(deltaFactor*100)} %")

    guios_IVP["INDICATOR_PROMINENCE_SLIDER"].setSliderValue(newValue = (prominence - 0.01) * (100 / 0.99), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_PROMINENCE_VALUETEXT"].updateText(text = f"{int(prominence * 100)} %")
    guios_IVP["INDICATOR_DISTANCE_SLIDER"].setSliderValue(newValue = (distance - 1) * (100 / 99), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_DISTANCE_VALUETEXT"].updateText(text = f"{int(distance)}") 
    guios_IVP["INDICATOR_HEIGHT_SLIDER"].setSliderValue(newValue = height * 100.0, callValueUpdateFunction = False)
    guios_IVP["INDICATOR_HEIGHT_VALUETEXT"].updateText(text = f"{int(height * 100)} %")


    guios_IVP["INDICATORCOLOR_TARGETSELECTION"].setSelected('VPLP')
    guios_IVP["APPLYNEWSETTINGS"].deactivate()
#<SWING>
if (True):
    guios_MAIN["MAININDICATOR_SWING"].setStatus(oc['SWING_Master'], callStatusUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['SWING']):
        lineActive = oc[f'SWING_{lineIndex}_LineActive']
        swingRange = oc[f'SWING_{lineIndex}_SwingRange']
        width      = oc[f'SWING_{lineIndex}_Width']
        color      = (oc[f'SWING_{lineIndex}_ColorR%{cgt}'], 
                        oc[f'SWING_{lineIndex}_ColorG%{cgt}'], 
                        oc[f'SWING_{lineIndex}_ColorB%{cgt}'], 
                        oc[f'SWING_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'SWING_{lineIndex}_Display']
        guios_SWING[f"INDICATOR_SWING{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_SWING[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].updateText(text = f"{swingRange:.4f}")
        guios_SWING[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_SWING[f"INDICATOR_SWING{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_SWING["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_SWING["APPLYNEWSETTINGS"].deactivate()
#<VOL>
if (True):
    guios_MAIN["SUBINDICATOR_VOL"].setStatus(oc['VOL_Master'], callStatusUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['VOL']):
        lineActive = oc[f'VOL_{lineIndex}_LineActive']
        nSamples   = oc[f'VOL_{lineIndex}_NSamples']
        width      = oc[f'VOL_{lineIndex}_Width']
        color      = (oc[f'VOL_{lineIndex}_ColorR%{cgt}'],
                        oc[f'VOL_{lineIndex}_ColorG%{cgt}'],
                        oc[f'VOL_{lineIndex}_ColorB%{cgt}'],
                        oc[f'VOL_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'VOL_{lineIndex}_Display']
        guios_VOL[f"INDICATOR_VOL{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_VOL[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_VOL[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_VOL[f"INDICATOR_VOL{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_VOL[f"INDICATOR_VOL{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_VOL["INDICATOR_VOLTYPESELECTION"].setSelected(oc['VOL_VolumeType'], callSelectionUpdateFunction = False)
    guios_VOL["INDICATOR_MATYPESELECTION"].setSelected(oc['VOL_MAType'],      callSelectionUpdateFunction = False)
    guios_VOL["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_VOL["APPLYNEWSETTINGS"].deactivate()
#<NNA>
if (True):
    guios_MAIN["SUBINDICATOR_NNA"].setStatus(oc['NNA_Master'], callStatusUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['NNA']):
        lineActive = oc[f'NNA_{lineIndex}_LineActive']
        nnCode     = oc[f'NNA_{lineIndex}_NeuralNetworkCode']
        alpha      = oc[f'NNA_{lineIndex}_Alpha']
        beta       = oc[f'NNA_{lineIndex}_Beta']
        width      = oc[f'NNA_{lineIndex}_Width']
        color      = (oc[f'NNA_{lineIndex}_ColorR%{cgt}'], 
                        oc[f'NNA_{lineIndex}_ColorG%{cgt}'], 
                        oc[f'NNA_{lineIndex}_ColorB%{cgt}'], 
                        oc[f'NNA_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'NNA_{lineIndex}_Display']
        guios_NNA[f"INDICATOR_NNA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        nnCode_str = "" if nnCode is None else f"{nnCode}"
        guios_NNA[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].updateText(text = nnCode_str)
        guios_NNA[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].updateText(text = f"{alpha:.2f}")
        guios_NNA[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].updateText(text  = f"{beta}")
        guios_NNA[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_NNA[f"INDICATOR_NNA{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_NNA["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_NNA["APPLYNEWSETTINGS"].deactivate()
#<MMACD>
if (True):
    guios_MAIN["SUBINDICATOR_MMACD"].setStatus(oc['MMACD_Master'], callStatusUpdateFunction = False)
    guios_MMACD["INDICATOR_MMACD_DISPLAYSWITCH"].setStatus(oc['MMACD_MMACD_Display'], callStatusUpdateFunction = False)
    guios_MMACD["INDICATOR_SIGNAL_DISPLAYSWITCH"].setStatus(oc['MMACD_SIGNAL_Display'], callStatusUpdateFunction = False)
    guios_MMACD["INDICATOR_HISTOGRAM_DISPLAYSWITCH"].setStatus(oc['MMACD_HISTOGRAM_Display'], callStatusUpdateFunction = False)
    guios_MMACD["INDICATOR_MMACD_COLOR"].updateColor(oc[f'MMACD_MMACD_ColorR%{cgt}'], 
                                                            oc[f'MMACD_MMACD_ColorG%{cgt}'], 
                                                            oc[f'MMACD_MMACD_ColorB%{cgt}'], 
                                                            oc[f'MMACD_MMACD_ColorA%{cgt}'])
    guios_MMACD["INDICATOR_SIGNAL_COLOR"].updateColor(oc[f'MMACD_SIGNAL_ColorR%{cgt}'], 
                                                            oc[f'MMACD_SIGNAL_ColorG%{cgt}'], 
                                                            oc[f'MMACD_SIGNAL_ColorB%{cgt}'], 
                                                            oc[f'MMACD_SIGNAL_ColorA%{cgt}'])
    guios_MMACD["INDICATOR_HISTOGRAM+_COLOR"].updateColor(oc[f'MMACD_HISTOGRAM+_ColorR%{cgt}'], 
                                                                oc[f'MMACD_HISTOGRAM+_ColorG%{cgt}'], 
                                                                oc[f'MMACD_HISTOGRAM+_ColorB%{cgt}'], 
                                                                oc[f'MMACD_HISTOGRAM+_ColorA%{cgt}'])
    guios_MMACD["INDICATOR_HISTOGRAM-_COLOR"].updateColor(oc[f'MMACD_HISTOGRAM-_ColorR%{cgt}'], 
                                                                oc[f'MMACD_HISTOGRAM-_ColorG%{cgt}'], 
                                                                oc[f'MMACD_HISTOGRAM-_ColorB%{cgt}'], 
                                                                oc[f'MMACD_HISTOGRAM-_ColorA%{cgt}'])
    guios_MMACD["INDICATOR_HISTOGRAMTYPE_SELECTION"].setSelected(itemKey = oc['MMACD_HISTOGRAM_Type'], callSelectionUpdateFunction = False)
    signalNSamples = oc['MMACD_SignalNSamples']
    guios_MMACD["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(text = f"{signalNSamples}")
    for lineIndex in range (_NMAXLINES['MMACD']):
        lineActive = oc[f'MMACD_MA{lineIndex}_LineActive']
        nSamples   = oc[f'MMACD_MA{lineIndex}_NSamples']
        guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
    guios_MMACD["INDICATORCOLOR_TARGETSELECTION"].setSelected('MMACD')
    guios_MMACD["APPLYNEWSETTINGS"].deactivate()
#<DMIxADX>
if (True):
    guios_MAIN["SUBINDICATOR_DMIxADX"].setStatus(oc['DMIxADX_Master'], callStatusUpdateFunction = False)
    guios_DMIxADX["INDICATOR_DISPLAYTYPE_SELECTION"].setSelected(itemKey = oc['DMIxADX_DisplayType'], callSelectionUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['DMIxADX']):
        lineActive = oc[f'DMIxADX_{lineIndex}_LineActive']
        nSamples   = oc[f'DMIxADX_{lineIndex}_NSamples']
        width      = oc[f'DMIxADX_{lineIndex}_Width']
        color      = (oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'],
                        oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'],
                        oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'],
                        oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'DMIxADX_{lineIndex}_Display']
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_DMIxADX["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_DMIxADX["APPLYNEWSETTINGS"].deactivate()
#<MFI>
if (True):
    guios_MAIN["SUBINDICATOR_MFI"].setStatus(oc['MFI_Master'], callStatusUpdateFunction = False)
    guios_MFI["INDICATOR_DISPLAYTYPE_SELECTION"].setSelected(itemKey = oc['MFI_DisplayType'], callSelectionUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['MFI']):
        lineActive = oc[f'MFI_{lineIndex}_LineActive']
        nSamples   = oc[f'MFI_{lineIndex}_NSamples']
        width      = oc[f'MFI_{lineIndex}_Width']
        color      = (oc[f'MFI_{lineIndex}_ColorR%{cgt}'],
                        oc[f'MFI_{lineIndex}_ColorG%{cgt}'],
                        oc[f'MFI_{lineIndex}_ColorB%{cgt}'],
                        oc[f'MFI_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'MFI_{lineIndex}_Display']
        guios_MFI[f"INDICATOR_MFI{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_MFI[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_MFI[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_MFI[f"INDICATOR_MFI{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_MFI["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_MFI["APPLYNEWSETTINGS"].deactivate()
    #<MFI>
#<TPD>
if (True):
    guios_MAIN["SUBINDICATOR_TPD"].setStatus(oc['TPD_Master'], callStatusUpdateFunction = False)
    guios_TPD["INDICATOR_DISPLAYTYPE_SELECTION"].setSelected(itemKey = oc['TPD_DisplayType'], callSelectionUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['TPD']):
        lineActive = oc[f'TPD_{lineIndex}_LineActive']
        viewLength = oc[f'TPD_{lineIndex}_ViewLength']
        nSamples   = oc[f'TPD_{lineIndex}_NSamples']
        nSamplesMA = oc[f'TPD_{lineIndex}_NSamplesMA']
        width      = oc[f'TPD_{lineIndex}_Width']
        color      = (oc[f'TPD_{lineIndex}_ColorR%{cgt}'],
                        oc[f'TPD_{lineIndex}_ColorG%{cgt}'],
                        oc[f'TPD_{lineIndex}_ColorB%{cgt}'],
                        oc[f'TPD_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'TPD_{lineIndex}_Display']
        guios_TPD[f"INDICATOR_TPD{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_TPD[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].updateText(text = f"{viewLength}")
        guios_TPD[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].updateText(text   = f"{nSamples}")
        guios_TPD[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].updateText(text = f"{nSamplesMA}")
        guios_TPD[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].updateText(text = f"{width}")
        guios_TPD[f"INDICATOR_TPD{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_TPD["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_TPD["APPLYNEWSETTINGS"].deactivate()
#<WOI>
if (True):
    guios_MAIN["SUBINDICATOR_WOI"].setStatus(oc['WOI_Master'], callStatusUpdateFunction = False)
    guios_WOI["INDICATOR_DISPLAYTYPE_SELECTION"].setSelected(itemKey = oc['WOI_DisplayType'], callSelectionUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['WOI']):
        lineActive = oc[f'WOI_{lineIndex}_LineActive']
        nSamples   = oc[f'WOI_{lineIndex}_NSamples']
        width      = oc[f'WOI_{lineIndex}_Width']
        color      = (oc[f'WOI_{lineIndex}_ColorR%{cgt}'],
                        oc[f'WOI_{lineIndex}_ColorG%{cgt}'],
                        oc[f'WOI_{lineIndex}_ColorB%{cgt}'],
                        oc[f'WOI_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'WOI_{lineIndex}_Display']
        guios_WOI[f"INDICATOR_WOI{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_WOI[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].updateText(text    = f"{width}")
        guios_WOI[f"INDICATOR_WOI{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_WOI["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_WOI["APPLYNEWSETTINGS"].deactivate()
#<NES>
if (True):
    guios_MAIN["SUBINDICATOR_NES"].setStatus(oc['NES_Master'], callStatusUpdateFunction = False)
    guios_NES["INDICATOR_DISPLAYTYPE_SELECTION"].setSelected(itemKey = oc['NES_DisplayType'], callSelectionUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['NES']):
        lineActive = oc[f'NES_{lineIndex}_LineActive']
        nSamples   = oc[f'NES_{lineIndex}_NSamples']
        width      = oc[f'NES_{lineIndex}_Width']
        color      = (oc[f'NES_{lineIndex}_ColorR%{cgt}'],
                        oc[f'NES_{lineIndex}_ColorG%{cgt}'],
                        oc[f'NES_{lineIndex}_ColorB%{cgt}'],
                        oc[f'NES_{lineIndex}_ColorA%{cgt}'])
        display    = oc[f'NES_{lineIndex}_Display']
        guios_NES[f"INDICATOR_NES{lineIndex}"].setStatus(lineActive, callStatusUpdateFunction = False)
        guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].updateText(text = f"{nSamples}")
        guios_NES[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].updateText(text    = f"{width}")
        guios_NES[f"INDICATOR_NES{lineIndex}_LINECOLOR"].updateColor(*color)
        guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].setStatus(display, callStatusUpdateFunction = False)
    guios_NES["INDICATORCOLOR_TARGETSELECTION"].setSelected('0')
    guios_NES["APPLYNEWSETTINGS"].deactivate()

"""

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
        for lineIndex in range (NMAXLINES['SMA']):
            if ac[f'SMA_{lineIndex}_LineActive']:
                nSamples = ac[f'SMA_{lineIndex}_NSamples']
                width    = oc[f'SMA_{lineIndex}_Width']
                display  = oc[f'SMA_{lineIndex}_Display']
                guios_THIS[f"INDICATOR_SMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
                guios_THIS[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].activate()
                guios_THIS[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
                guios_THIS[f"INDICATOR_SMA{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_SMA{lineIndex}_DISPLAY"].activate()
            else:
                guios_THIS[f"INDICATOR_SMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
                guios_THIS[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].updateText("-")
                guios_THIS[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].deactivate()
                guios_THIS[f"INDICATOR_SMA{lineIndex}_DISPLAY"].deactivate()
                guios_THIS[f"INDICATOR_SMA{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
    else:
        guios_MAIN["MAININDICATOR_SMA"].setStatus(status = False, callStatusUpdateFunction = False)
        guios_MAIN["MAININDICATOR_SMA"].deactivate()
        guios_MAIN["MAININDICATORSETUP_SMA"].deactivate()



"""
guios_SMA     = self.settingsSubPages['SMA'].GUIOs
guios_WMA     = self.settingsSubPages['WMA'].GUIOs
guios_EMA     = self.settingsSubPages['EMA'].GUIOs
guios_PSAR    = self.settingsSubPages['PSAR'].GUIOs
guios_BOL     = self.settingsSubPages['BOL'].GUIOs
guios_IVP     = self.settingsSubPages['IVP'].GUIOs
guios_SWING   = self.settingsSubPages['SWING'].GUIOs
guios_VOL     = self.settingsSubPages['VOL'].GUIOs
guios_NNA     = self.settingsSubPages['NNA'].GUIOs
guios_MMACD   = self.settingsSubPages['MMACD'].GUIOs
guios_DMIxADX = self.settingsSubPages['DMIxADX'].GUIOs
guios_MFI     = self.settingsSubPages['MFI'].GUIOs
guios_TPD     = self.settingsSubPages['TPD'].GUIOs
guios_WOI     = self.settingsSubPages['WOI'].GUIOs
guios_NES     = self.settingsSubPages['NES'].GUIOs

#SMA
if cac is not None and cac['SMA_Master']:
    guios_MAIN["MAININDICATOR_SMA"].activate()
    guios_MAIN["MAININDICATOR_SMA"].setStatus(status = oc['SMA_Master'], callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATORSETUP_SMA"].activate()
    for lineIndex in range (_NMAXLINES['SMA']):
        if cac[f'SMA_{lineIndex}_LineActive']:
            nSamples = cac[f'SMA_{lineIndex}_NSamples']
            width    = oc[f'SMA_{lineIndex}_Width']
            display  = oc[f'SMA_{lineIndex}_Display']
            guios_SMA[f"INDICATOR_SMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_SMA[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_SMA[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].activate()
            guios_SMA[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_SMA[f"INDICATOR_SMA{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_SMA[f"INDICATOR_SMA{lineIndex}_DISPLAY"].activate()
        else:
            guios_SMA[f"INDICATOR_SMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_SMA[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_SMA[f"INDICATOR_SMA{lineIndex}_WIDTHINPUT"].deactivate()
            guios_SMA[f"INDICATOR_SMA{lineIndex}_DISPLAY"].deactivate()
            guios_SMA[f"INDICATOR_SMA{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
else:
    guios_MAIN["MAININDICATOR_SMA"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATOR_SMA"].deactivate()
    guios_MAIN["MAININDICATORSETUP_SMA"].deactivate()

#WMA
if cac is not None and cac['WMA_Master']:
    guios_MAIN["MAININDICATOR_WMA"].activate()
    guios_MAIN["MAININDICATOR_WMA"].setStatus(status = oc['WMA_Master'], callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATORSETUP_WMA"].activate()
    for lineIndex in range (_NMAXLINES['WMA']):
        if cac[f'WMA_{lineIndex}_LineActive']:
            nSamples = cac[f'WMA_{lineIndex}_NSamples']
            width    = oc[f'WMA_{lineIndex}_Width']
            display  = oc[f'WMA_{lineIndex}_Display']
            guios_WMA[f"INDICATOR_WMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_WMA[f"INDICATOR_WMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_WMA[f"INDICATOR_WMA{lineIndex}_WIDTHINPUT"].activate()
            guios_WMA[f"INDICATOR_WMA{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_WMA[f"INDICATOR_WMA{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_WMA[f"INDICATOR_WMA{lineIndex}_DISPLAY"].activate()
        else:
            guios_WMA[f"INDICATOR_WMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_WMA[f"INDICATOR_WMA{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_WMA[f"INDICATOR_WMA{lineIndex}_WIDTHINPUT"].deactivate()
            guios_WMA[f"INDICATOR_WMA{lineIndex}_DISPLAY"].deactivate()
            guios_WMA[f"INDICATOR_WMA{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
else:
    guios_MAIN["MAININDICATOR_WMA"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATOR_WMA"].deactivate()
    guios_MAIN["MAININDICATORSETUP_WMA"].deactivate()

#EMA
if cac is not None and cac['EMA_Master']:
    guios_MAIN["MAININDICATOR_EMA"].activate()
    guios_MAIN["MAININDICATOR_EMA"].setStatus(status = oc['EMA_Master'], callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATORSETUP_EMA"].activate()
    for lineIndex in range (_NMAXLINES['EMA']):
        if cac[f'EMA_{lineIndex}_LineActive']:
            nSamples = cac[f'EMA_{lineIndex}_NSamples']
            width    = oc[f'EMA_{lineIndex}_Width']
            display  = oc[f'EMA_{lineIndex}_Display']
            guios_EMA[f"INDICATOR_EMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_EMA[f"INDICATOR_EMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_EMA[f"INDICATOR_EMA{lineIndex}_WIDTHINPUT"].activate()
            guios_EMA[f"INDICATOR_EMA{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_EMA[f"INDICATOR_EMA{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_EMA[f"INDICATOR_EMA{lineIndex}_DISPLAY"].activate()
        else:
            guios_EMA[f"INDICATOR_EMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_EMA[f"INDICATOR_EMA{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_EMA[f"INDICATOR_EMA{lineIndex}_WIDTHINPUT"].deactivate()
            guios_EMA[f"INDICATOR_EMA{lineIndex}_DISPLAY"].deactivate()
            guios_EMA[f"INDICATOR_EMA{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
else:
    guios_MAIN["MAININDICATOR_EMA"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATOR_EMA"].deactivate()
    guios_MAIN["MAININDICATORSETUP_EMA"].deactivate()

#PSAR
if cac is not None and cac['PSAR_Master']:
    guios_MAIN["MAININDICATOR_PSAR"].activate()
    guios_MAIN["MAININDICATOR_PSAR"].setStatus(status = oc['PSAR_Master'], callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATORSETUP_PSAR"].activate()
    for lineIndex in range (_NMAXLINES['PSAR']):
        if cac[f'PSAR_{lineIndex}_LineActive']:
            af0     = cac[f'PSAR_{lineIndex}_AF0']
            afPlus  = cac[f'PSAR_{lineIndex}_AF+']
            afMax   = cac[f'PSAR_{lineIndex}_AFMax']
            width   = oc[f'PSAR_{lineIndex}_Width']
            display = oc[f'PSAR_{lineIndex}_Display']
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF0INPUT"].updateText(f"{af0:.3f}")
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF+INPUT"].updateText(f"{afPlus:.3f}")
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT"].updateText(f"{afMax:.3f}")
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT"].activate()
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_DISPLAY"].activate()
        else:
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF0INPUT"].updateText("-")
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF+INPUT"].updateText("-")
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT"].updateText("-")
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT"].deactivate()
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_PSAR[f"INDICATOR_PSAR{lineIndex}_DISPLAY"].deactivate()
else:
    guios_MAIN["MAININDICATOR_PSAR"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATOR_PSAR"].deactivate()
    guios_MAIN["MAININDICATORSETUP_PSAR"].deactivate()

#BOL
if cac is not None and cac['BOL_Master']:
    guios_MAIN["MAININDICATOR_BOL"].activate()
    guios_MAIN["MAININDICATOR_BOL"].setStatus(status = oc['BOL_Master'], callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATORSETUP_BOL"].activate()
    for lineIndex in range (_NMAXLINES['BOL']):
        if cac[f'BOL_{lineIndex}_LineActive']:
            nSamples  = cac[f'BOL_{lineIndex}_NSamples']
            bandWidth = cac[f'BOL_{lineIndex}_BandWidth']
            width     = oc[f'BOL_{lineIndex}_Width']
            display   = oc[f'BOL_{lineIndex}_Display']
            guios_BOL[f"INDICATOR_BOL{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_BOL[f"INDICATOR_BOL{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_BOL[f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT"].updateText(f"{bandWidth:.1f}")
            guios_BOL[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].activate()
            guios_BOL[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_BOL[f"INDICATOR_BOL{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_BOL[f"INDICATOR_BOL{lineIndex}_DISPLAY"].activate()
        else:
            guios_BOL[f"INDICATOR_BOL{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_BOL[f"INDICATOR_BOL{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_BOL[f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT"].updateText("-")
            guios_BOL[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].deactivate()
            guios_BOL[f"INDICATOR_BOL{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_BOL[f"INDICATOR_BOL{lineIndex}_DISPLAY"].deactivate()
    guios_BOL["INDICATOR_MATYPESELECTION"].setSelected(itemKey = cac['BOL_MAType'], callSelectionUpdateFunction = False)
else:
    guios_BOL["INDICATOR_MATYPESELECTION"].setSelected(itemKey = 'SMA', callSelectionUpdateFunction = False)
    guios_MAIN["MAININDICATOR_BOL"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATOR_BOL"].deactivate()
    guios_MAIN["MAININDICATORSETUP_BOL"].deactivate()

#IVP
if cac is not None and cac['IVP_Master']:
    guios_MAIN["MAININDICATOR_IVP"].activate()
    guios_MAIN["MAININDICATOR_IVP"].setStatus(status = oc['IVP_Master'], callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATORSETUP_IVP"].activate()
    guios_IVP["INDICATOR_INTERVAL_INPUTTEXT"].updateText(text = f"{cac['IVP_NSamples']}")
    guios_IVP["INDICATOR_GAMMAFACTOR_SLIDER"].setSliderValue(newValue = (cac['IVP_GammaFactor']-0.005)*(100/0.095), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(f"{cac['IVP_GammaFactor']*100:.1f} %")
    guios_IVP["INDICATOR_DELTAFACTOR_SLIDER"].setSliderValue(newValue = (cac['IVP_DeltaFactor']-0.1)*(100/9.9), callValueUpdateFunction = False)
    guios_IVP["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(f"{int(cac['IVP_DeltaFactor']*100):d} %")
else:
    guios_MAIN["MAININDICATOR_IVP"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATOR_IVP"].deactivate()
    guios_MAIN["MAININDICATORSETUP_IVP"].deactivate()

#SWING
if cac is not None and cac['SWING_Master']:
    guios_MAIN["MAININDICATOR_SWING"].activate()
    guios_MAIN["MAININDICATOR_SWING"].setStatus(status = oc['SWING_Master'], callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATORSETUP_SWING"].activate()
    for lineIndex in range (_NMAXLINES['SWING']):
        if cac[f'SWING_{lineIndex}_LineActive']:
            swingRange = cac[f'SWING_{lineIndex}_SwingRange']
            width      = oc[f'SWING_{lineIndex}_Width']
            display    = oc[f'SWING_{lineIndex}_Display']
            guios_SWING[f"INDICATOR_SWING{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_SWING[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].updateText(f"{swingRange:.4f}")
            guios_SWING[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].activate()
            guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].activate()
        else:
            guios_SWING[f"INDICATOR_SWING{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_SWING[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].updateText("-")
            guios_SWING[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].deactivate()
            guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_SWING[f"INDICATOR_SWING{lineIndex}_DISPLAY"].deactivate()
else:
    guios_MAIN["MAININDICATOR_SWING"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["MAININDICATOR_SWING"].deactivate()
    guios_MAIN["MAININDICATORSETUP_SWING"].deactivate()

#VOL
if cac is not None and cac['VOL_Master']:
    for lineIndex in range (_NMAXLINES['VOL']):
        if cac[f'VOL_{lineIndex}_LineActive']:
            nSamples = cac[f'VOL_{lineIndex}_NSamples']
            width    = oc[f'VOL_{lineIndex}_Width']
            display  = oc[f'VOL_{lineIndex}_Display']
            guios_VOL[f"INDICATOR_VOL{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_VOL[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_VOL[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].activate()
            guios_VOL[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_VOL[f"INDICATOR_VOL{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_VOL[f"INDICATOR_VOL{lineIndex}_DISPLAY"].activate()
        else:
            guios_VOL[f"INDICATOR_VOL{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_VOL[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_VOL[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].deactivate()
            guios_VOL[f"INDICATOR_VOL{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_VOL[f"INDICATOR_VOL{lineIndex}_DISPLAY"].deactivate()
    guios_VOL["INDICATOR_VOLTYPESELECTION"].setSelected(itemKey = oc['VOL_VolumeType'], callSelectionUpdateFunction = False)
    guios_VOL["INDICATOR_MATYPESELECTION"].setSelected(itemKey  = cac['VOL_MAType'],    callSelectionUpdateFunction = False)
else:
    guios_VOL["INDICATOR_VOLTYPESELECTION"].setSelected(itemKey = oc['VOL_VolumeType'], callSelectionUpdateFunction = False)
    guios_VOL["INDICATOR_MATYPESELECTION"].setSelected(itemKey  = 'SMA',                callSelectionUpdateFunction = False)
    for lineIndex in range (_NMAXLINES['VOL']):
        guios_VOL[f"INDICATOR_VOL{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
        guios_VOL[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].updateText("-")
        guios_VOL[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].deactivate()
        guios_VOL[f"INDICATOR_VOL{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
        guios_VOL[f"INDICATOR_VOL{lineIndex}_DISPLAY"].deactivate()
oc['VOL_MAType'] = 'SMA' if cac is None else cac['VOL_MAType']

#NNA
if cac is not None and cac['NNA_Master']:
    guios_MAIN["SUBINDICATOR_NNA"].activate()
    guios_MAIN["SUBINDICATOR_NNA"].setStatus(status = oc['NNA_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_NNA"].activate()
    for lineIndex in range (_NMAXLINES['NNA']):
        if cac[f'NNA_{lineIndex}_LineActive']:
            nnCode   = cac[f'NNA_{lineIndex}_NeuralNetworkCode']
            nnCode_str = "" if nnCode is None else f"{nnCode}"
            alpha    = cac[f'NNA_{lineIndex}_Alpha']
            beta     = cac[f'NNA_{lineIndex}_Beta']
            width    = oc[f'NNA_{lineIndex}_Width']
            display  = oc[f'NNA_{lineIndex}_Display']
            guios_NNA[f"INDICATOR_NNA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_NNA[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].updateText(nnCode_str)
            guios_NNA[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].updateText(f"{alpha:.2f}")
            guios_NNA[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].updateText(f"{beta}")
            guios_NNA[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].activate()
            guios_NNA[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].activate()
        else:
            guios_NNA[f"INDICATOR_NNA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_NNA[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].updateText("-")
            guios_NNA[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].updateText("-")
            guios_NNA[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].updateText("-")
            guios_NNA[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].deactivate()
            guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].deactivate()
            guios_NNA[f"INDICATOR_NNA{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
else:
    guios_MAIN["SUBINDICATOR_NNA"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_NNA"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_NNA"].deactivate()

#MMACD
if cac is not None and cac['MMACD_Master']:
    guios_MAIN["SUBINDICATOR_MMACD"].activate()
    guios_MAIN["SUBINDICATOR_MMACD"].setStatus(status = oc['MMACD_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_MMACD"].activate()
    for lineIndex in range (_NMAXLINES['MMACD']):
        if cac[f'MMACD_MA{lineIndex}_LineActive']:
            nSamples = cac[f'MMACD_MA{lineIndex}_NSamples']
            guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
        else:
            guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].updateText("-")
    signalNSamples = cac['MMACD_SignalNSamples']
    guios_MMACD["INDICATOR_SIGNALINTERVALTEXTINPUT"].updateText(f"{signalNSamples}")
else:
    guios_MAIN["SUBINDICATOR_MMACD"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_MMACD"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_MMACD"].deactivate()

#DMIxADX
if cac is not None and cac['DMIxADX_Master']:
    guios_MAIN["SUBINDICATOR_DMIxADX"].activate()
    guios_MAIN["SUBINDICATOR_DMIxADX"].setStatus(status = oc['DMIxADX_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_DMIxADX"].activate()
    for lineIndex in range (_NMAXLINES['DMIxADX']):
        if cac[f'DMIxADX_{lineIndex}_LineActive']:
            nSamples = cac[f'DMIxADX_{lineIndex}_NSamples']
            width    = oc[f'DMIxADX_{lineIndex}_Width']
            display  = oc[f'DMIxADX_{lineIndex}_Display']
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}"].setStatus(status = True, callStatusUpdateFunction = False)
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].activate()
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].activate()
        else:
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].deactivate()
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].deactivate()
            guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
else:
    guios_MAIN["SUBINDICATOR_DMIxADX"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_DMIxADX"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_DMIxADX"].deactivate()

#MFI
if cac is not None and cac['MFI_Master']:
    guios_MAIN["SUBINDICATOR_MFI"].activate()
    guios_MAIN["SUBINDICATOR_MFI"].setStatus(status = oc['MFI_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_MFI"].activate()
    for lineIndex in range (_NMAXLINES['MFI']):
        if cac[f'MFI_{lineIndex}_LineActive']:
            nSamples = cac[f'MFI_{lineIndex}_NSamples']
            width    = oc[f'MFI_{lineIndex}_Width']
            display  = oc[f'MFI_{lineIndex}_Display']
            guios_MFI[f"INDICATOR_MFI{lineIndex}"].setStatus(status = True)
            guios_MFI[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_MFI[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].activate()
            guios_MFI[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].activate()
        else:
            guios_MFI[f"INDICATOR_MFI{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MFI[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_MFI[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].deactivate()
            guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_MFI[f"INDICATOR_MFI{lineIndex}_DISPLAY"].deactivate()
else:
    guios_MAIN["SUBINDICATOR_MFI"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_MFI"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_MFI"].deactivate()

#TPD
if cac is not None and cac['TPD_Master']:
    guios_MAIN["SUBINDICATOR_TPD"].activate()
    guios_MAIN["SUBINDICATOR_TPD"].setStatus(status = oc['TPD_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_TPD"].activate()
    for lineIndex in range (_NMAXLINES['TPD']):
        if cac[f'TPD_{lineIndex}_LineActive']:
            viewLength = cac[f'TPD_{lineIndex}_ViewLength']
            nSamples   = cac[f'TPD_{lineIndex}_NSamples']
            nSamplesMA = cac[f'TPD_{lineIndex}_NSamplesMA']
            width      = oc[f'TPD_{lineIndex}_Width']
            display    = oc[f'TPD_{lineIndex}_Display']
            guios_TPD[f"INDICATOR_TPD{lineIndex}"].setStatus(status = True)
            guios_TPD[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].updateText(f"{viewLength}")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].updateText(f"{nSamplesMA}")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].activate()
            guios_TPD[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].activate()
        else:
            guios_TPD[f"INDICATOR_TPD{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_TPD[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].updateText("-")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].updateText("-")
            guios_TPD[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].deactivate()
            guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_TPD[f"INDICATOR_TPD{lineIndex}_DISPLAY"].deactivate()
else:
    guios_MAIN["SUBINDICATOR_TPD"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_TPD"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_TPD"].deactivate()

#WOI
if cac is not None and cac['WOI_Master']:
    guios_MAIN["SUBINDICATOR_WOI"].activate()
    guios_MAIN["SUBINDICATOR_WOI"].setStatus(status = oc['WOI_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_WOI"].activate()
    for lineIndex in range (_NMAXLINES['WOI']):
        if cac[f'WOI_{lineIndex}_LineActive']:
            nSamples = cac[f'WOI_{lineIndex}_NSamples']
            width    = oc[f'WOI_{lineIndex}_Width']
            display  = oc[f'WOI_{lineIndex}_Display']
            guios_WOI[f"INDICATOR_WOI{lineIndex}"].setStatus(status = True)
            guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_WOI[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].activate()
            guios_WOI[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].activate()
        else:
            guios_WOI[f"INDICATOR_WOI{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_WOI[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].deactivate()
            guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_WOI[f"INDICATOR_WOI{lineIndex}_DISPLAY"].deactivate()
else:
    guios_MAIN["SUBINDICATOR_WOI"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_WOI"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_WOI"].deactivate()

#NES
if cac is not None and cac['NES_Master']:
    guios_MAIN["SUBINDICATOR_NES"].activate()
    guios_MAIN["SUBINDICATOR_NES"].setStatus(status = oc['NES_Master'], callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATORSETUP_NES"].activate()
    for lineIndex in range (_NMAXLINES['NES']):
        if cac[f'NES_{lineIndex}_LineActive']:
            nSamples = cac[f'NES_{lineIndex}_NSamples']
            width    = oc[f'NES_{lineIndex}_Width']
            display  = oc[f'NES_{lineIndex}_Display']
            guios_NES[f"INDICATOR_NES{lineIndex}"].setStatus(status = True)
            guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].updateText(f"{nSamples}")
            guios_NES[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].activate()
            guios_NES[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].updateText(f"{width}")
            guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].setStatus(status = display, callStatusUpdateFunction = False)
            guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].activate()
        else:
            guios_NES[f"INDICATOR_NES{lineIndex}"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].updateText("-")
            guios_NES[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].deactivate()
            guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].setStatus(status = False, callStatusUpdateFunction = False)
            guios_NES[f"INDICATOR_NES{lineIndex}_DISPLAY"].deactivate()
else:
    guios_MAIN["SUBINDICATOR_NES"].setStatus(status = False, callStatusUpdateFunction = False)
    guios_MAIN["SUBINDICATOR_NES"].deactivate()
    guios_MAIN["SUBINDICATORSETUP_NES"].deactivate()
"""

def cd_on_settings_content_update():
    #[1]: Instances
    miType     = indicatorType
    setterType = guioName_split[1]

    #[2]: Graphics Related
    #---[2-1]: LineSelectionBox
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps[miType].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps[miType].GUIOs[f"INDICATOR_{miType}{lineSelected}_LINECOLOR"].getColor()
        ssps[miType].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps[miType].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps[miType].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps[miType].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps[miType].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps[miType].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps[miType].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps[miType].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps[miType].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps[miType].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()

    #---[2-2]: Color
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps[miType].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps[miType].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                gValue = int(ssps[miType].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                bValue = int(ssps[miType].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                aValue = int(ssps[miType].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps[miType].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps[miType].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps[miType].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()

    #---[2-3]: ApplyColor
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps[miType].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps[miType].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps[miType].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps[miType].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps[miType].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps[miType].GUIOs[f"INDICATOR_{miType}{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps[miType].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps[miType].GUIOs['APPLYNEWSETTINGS'].activate()

    #---[2-4]: WidthTextInputBox
    elif (setterType == 'WidthTextInputBox'): 
        ssps[miType].GUIOs['APPLYNEWSETTINGS'].activate()
        
    #---[2-5]: DisplaySwitch
    elif (setterType == 'DisplaySwitch'):     
        ssps[miType].GUIOs['APPLYNEWSETTINGS'].activate()
        
    #---[2-6]: ApplySettings
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES[miType]):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'{miType}_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'{miType}_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'{miType}_{lineIndex}_Width'] = 1
                ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'{miType}_{lineIndex}_Width']))
            if width_previous != oc[f'{miType}_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'{miType}_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'{miType}_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'{miType}_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'{miType}_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_LINECOLOR"].getColor()
            oc[f'{miType}_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'{miType}_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'{miType}_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'{miType}_{lineIndex}_ColorA%{cgt}'] = color_a
            if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'{miType}_{lineIndex}_Display']
            oc[f'{miType}_{lineIndex}_Display'] = ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'{miType}_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #MA Master
        maMaster_previous = oc[f'{miType}_Master']
        oc[f'{miType}_Master'] = ssps['MAIN'].GUIOs[f"MAININDICATOR_{miType}"].getStatus()
        if maMaster_previous != oc[f'{miType}_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Queue Update
        ap_iID        = self.analysisParams[self.intervalID]
        configuredMAs = set([aCode for aCode in ap_iID if aCode.startswith(miType)])
        for configuredMA in configuredMAs:
            lineIndex = ap_iID[configuredMA]['lineIndex']
            if not updateTracker[lineIndex]: continue
            self._drawer_RemoveDrawings(analysisCode = configuredMA, gRemovalSignal = _FULLDRAWSIGNALS[miType]) #Remove previous graphics
            self.__addBufferZone_toDrawQueue(analysisCode  = configuredMA, drawSignal     = _FULLDRAWSIGNALS[miType]) #Update draw queue
        #Control Buttons Handling
        ssps[miType].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True

    #[3]: Analysis Related
    #---[3-1]: Line Activation Switch
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        _newStatus = ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}"].getStatus()
        oc[f'{miType}_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    
    #---[3-2]: Interval Text Input Box
    elif (setterType == 'IntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    _nSamples = int(ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_INTERVALINPUT"].getText())
        except: _nSamples = None
        #Save the new value to the object config dictionary
        oc[f'{miType}_{lineIndex}_NSamples'] = _nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

    #[4]: Return Status Flag
    return activateSaveConfigButton

"""
#Subpage 'SMA' 'WMA' 'EMA'
elif indicatorType in ('SMA', 'WMA', 'EMA'):
    miType = indicatorType
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps[miType].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps[miType].GUIOs[f"INDICATOR_{miType}{lineSelected}_LINECOLOR"].getColor()
        ssps[miType].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps[miType].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps[miType].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps[miType].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps[miType].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps[miType].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps[miType].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps[miType].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps[miType].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps[miType].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps[miType].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps[miType].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                gValue = int(ssps[miType].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                bValue = int(ssps[miType].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                aValue = int(ssps[miType].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps[miType].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps[miType].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps[miType].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps[miType].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps[miType].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps[miType].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps[miType].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps[miType].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps[miType].GUIOs[f"INDICATOR_{miType}{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps[miType].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps[miType].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps[miType].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps[miType].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES[miType]):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'{miType}_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'{miType}_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'{miType}_{lineIndex}_Width'] = 1
                ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'{miType}_{lineIndex}_Width']))
            if width_previous != oc[f'{miType}_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'{miType}_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'{miType}_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'{miType}_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'{miType}_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_LINECOLOR"].getColor()
            oc[f'{miType}_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'{miType}_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'{miType}_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'{miType}_{lineIndex}_ColorA%{cgt}'] = color_a
            if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'{miType}_{lineIndex}_Display']
            oc[f'{miType}_{lineIndex}_Display'] = ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'{miType}_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #MA Master
        maMaster_previous = oc[f'{miType}_Master']
        oc[f'{miType}_Master'] = ssps['MAIN'].GUIOs[f"MAININDICATOR_{miType}"].getStatus()
        if maMaster_previous != oc[f'{miType}_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Queue Update
        ap_iID        = self.analysisParams[self.intervalID]
        configuredMAs = set([aCode for aCode in ap_iID if aCode.startswith(miType)])
        for configuredMA in configuredMAs:
            lineIndex = ap_iID[configuredMA]['lineIndex']
            if not updateTracker[lineIndex]: continue
            self._drawer_RemoveDrawings(analysisCode = configuredMA, gRemovalSignal = _FULLDRAWSIGNALS[miType]) #Remove previous graphics
            self.__addBufferZone_toDrawQueue(analysisCode  = configuredMA, drawSignal     = _FULLDRAWSIGNALS[miType]) #Update draw queue
        #Control Buttons Handling
        ssps[miType].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        _newStatus = ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}"].getStatus()
        oc[f'{miType}_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    _nSamples = int(ssps[miType].GUIOs[f"INDICATOR_{miType}{lineIndex}_INTERVALINPUT"].getText())
        except: _nSamples = None
        #Save the new value to the object config dictionary
        oc[f'{miType}_{lineIndex}_NSamples'] = _nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'PSAR'
elif indicatorType == 'PSAR':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['PSAR'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineSelected}_LINECOLOR"].getColor()
        ssps['PSAR'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['PSAR'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['PSAR'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['PSAR'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['PSAR'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['PSAR'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['PSAR'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['PSAR'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['PSAR'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['PSAR'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['PSAR'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                gValue = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                bValue = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                aValue = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['PSAR'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['PSAR'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['PSAR'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['PSAR'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['PSAR'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['PSAR'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['PSAR'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['PSAR'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['PSAR'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['PSAR']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'PSAR_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'PSAR_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'PSAR_{lineIndex}_Width'] = 1
                ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'PSAR_{lineIndex}_Width']))
            if width_previous != oc[f'PSAR_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'PSAR_{lineIndex}_ColorR%{cgt}'],
                                oc[f'PSAR_{lineIndex}_ColorG%{cgt}'],
                                oc[f'PSAR_{lineIndex}_ColorB%{cgt}'],
                                oc[f'PSAR_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_LINECOLOR"].getColor()
            oc[f'PSAR_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'PSAR_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'PSAR_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'PSAR_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'PSAR_{lineIndex}_Display']
            oc[f'PSAR_{lineIndex}_Display'] = ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'PSAR_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---PSAR Master
        psarMaster_previous = oc['PSAR_Master']
        oc['PSAR_Master'] = ssps['MAIN'].GUIOs["MAININDICATOR_PSAR"].getStatus()
        if psarMaster_previous != oc['PSAR_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Queue Update
        ap_iID          = self.analysisParams[self.intervalID]
        configuredPSARs = set(aCode for aCode in ap_iID if aCode.startswith('PSAR'))
        for configuredPSAR in configuredPSARs:
            lineIndex = ap_iID[configuredPSAR]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredPSAR, gRemovalSignal = _FULLDRAWSIGNALS['PSAR']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode = configuredPSAR, drawSignal = _FULLDRAWSIGNALS['PSAR']) #Update draw queue
        #Control Buttons Handling
        ssps['PSAR'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        _newStatus = ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}"].getStatus()
        oc[f'PSAR_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'AF0TextInputBox'):      
        lineIndex = int(guioName_split[2])
        #Get new AF0
        try:    _af0 = round(float(ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_AF0INPUT"].getText()), 3)
        except: _af0 = None
        #Save the new value to the object config dictionary
        oc[f'PSAR_{lineIndex}_AF0'] = _af0
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'AF+TextInputBox'):      
        lineIndex = int(guioName_split[2])
        #Get new AF+
        try:    _afAccel = round(float(ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_AF+INPUT"].getText()), 3)
        except: _afAccel = None
        #Save the new value to the object config dictionary
        oc[f'PSAR_{lineIndex}_AF+'] = _afAccel
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'AFMaxTextInputBox'):    
        lineIndex = int(guioName_split[2])
        #Get new AFMax
        try:    _afMax = round(float(ssps['PSAR'].GUIOs[f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT"].getText()), 3)
        except: _afMax = None
        #Save the new value to the object config dictionary
        oc[f'PSAR_{lineIndex}_AFMAX'] = _afMax
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'BOL'
elif indicatorType == 'BOL':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):        
        lineSelected = ssps['BOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineSelected}_LINECOLOR"].getColor()
        ssps['BOL'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['BOL'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['BOL'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['BOL'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['BOL'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['BOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['BOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['BOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['BOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['BOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):                 
        cType = guioName_split[2]
        ssps['BOL'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['BOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['BOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['BOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['BOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['BOL'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['BOL'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['BOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):            
        lineSelected = ssps['BOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['BOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['BOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['BOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['BOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['BOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['BOL'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'):     
        ssps['BOL'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):         
        ssps['BOL'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayContentsSwitch'): 
        ssps['BOL'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):         
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['BOL']):
            updateTracker[lineIndex] = [False, False] #[1]: Draw CenterLine, [2]: Draw Band
            #Width
            width_previous = oc[f'BOL_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'BOL_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset == True:
                oc[f'BOL_{lineIndex}_Width'] = 1
                ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'BOL_{lineIndex}_Width']))
            if (width_previous != oc[f'BOL_{lineIndex}_Width']): 
                updateTracker[lineIndex][0] = True
            #Color
            color_previous = (oc[f'BOL_{lineIndex}_ColorR%{cgt}'],
                                oc[f'BOL_{lineIndex}_ColorG%{cgt}'],
                                oc[f'BOL_{lineIndex}_ColorB%{cgt}'],
                                oc[f'BOL_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_LINECOLOR"].getColor()
            oc[f'BOL_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'BOL_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'BOL_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'BOL_{lineIndex}_ColorA%{cgt}'] = color_a
            if (color_previous != (color_r, color_g, color_b, color_a)): 
                updateTracker[lineIndex][0] = True
                updateTracker[lineIndex][1] = True
            #Line Display
            display_previous = oc[f'BOL_{lineIndex}_Display']
            oc[f'BOL_{lineIndex}_Display'] = ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_DISPLAY"].getStatus()
            if (display_previous != oc[f'BOL_{lineIndex}_Display']): 
                updateTracker[lineIndex][0] = True
                updateTracker[lineIndex][1] = True
        #---BOL Master
        bolMaster_previous = oc['BOL_Master']
        oc['BOL_Master'] = ssps['MAIN'].GUIOs["MAININDICATOR_BOL"].getStatus()
        if bolMaster_previous != oc['BOL_Master']:
            for lineIndex in updateTracker: 
                updateTracker[lineIndex][0] = True
                updateTracker[lineIndex][1] = True
        #---CenterLine Display Switch
        display_bolCenter_previous = oc['BOL_DisplayCenterLine']
        oc['BOL_DisplayCenterLine'] = ssps['BOL'].GUIOs["INDICATOR_DISPLAYCONTENTS_BOLCENTERSWITCH"].getStatus()
        if display_bolCenter_previous != oc['BOL_DisplayCenterLine']: 
            for lineIndex in updateTracker: updateTracker[lineIndex][0] = True
        #---Band Display Switch
        display_bolBand_previous = oc['BOL_DisplayBand']
        oc['BOL_DisplayBand'] = ssps['BOL'].GUIOs["INDICATOR_DISPLAYCONTENTS_BOLBANDSWITCH"].getStatus()
        if display_bolBand_previous != oc['BOL_DisplayBand']: 
            for lineIndex in updateTracker: updateTracker[lineIndex][1] = True
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredBOL in (aCode for aCode in ap_iID if aCode.startswith('BOL')):
            lineIndex = ap_iID[configuredBOL]['lineIndex']
            drawSignal = 0
            drawSignal += 0b01*updateTracker[lineIndex][0] #CenterLine
            drawSignal += 0b10*updateTracker[lineIndex][1] #Band
            if drawSignal:
                self._drawer_RemoveDrawings(analysisCode = configuredBOL, gRemovalSignal = drawSignal) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredBOL, drawSignal     = drawSignal) #Update draw queue
        #Control Buttons Handling
        ssps['BOL'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'):  
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}"].getStatus()
        oc[f'BOL_{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'):  
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamples = int(ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'BOL_{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'BandWidthTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new bandwidth
        try:    bandWidth = int(ssps['BOL'].GUIOs[f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT"].getText())
        except: bandWidth = None
        #Save the new value to the object config dictionary
        oc[f'BOL_{lineIndex}_BandWidth'] = bandWidth
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'MATypeSelection'): 
        #Get new MAType
        maType = ssps['BOL'].GUIOs["INDICATOR_MATYPESELECTION"].getSelected()
        #Save the new value to the object config dictionary
        oc['BOL_MAType'] = maType
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'IVP'
elif indicatorType == 'IVP':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):     
        lineSelected = ssps['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['IVP'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].getColor()
        ssps['IVP'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['IVP'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['IVP'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['IVP'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['IVP'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['IVP'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['IVP'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['IVP'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['IVP'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['IVP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):              
        cType = guioName_split[2]
        ssps['IVP'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['IVP'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['IVP'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['IVP'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['IVP'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['IVP'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['IVP'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['IVP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):         
        lineSelected = ssps['IVP'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['IVP'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['IVP'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['IVP'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['IVP'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['IVP'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['IVP'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayWidthSlider'): 
        lineTarget = guioName_split[2]
        sliderValue = ssps['IVP'].GUIOs[f"INDICATOR_{lineTarget}_DISPLAYWIDTHSLIDER"].getSliderValue()
        ssps['IVP'].GUIOs[f"INDICATOR_{lineTarget}_DISPLAYWIDTHVALUETEXT"].updateText(str(round(sliderValue/100*0.9+0.1, 2)))
        ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):      
        ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'VPLPBDisplayRegion'): 
        #Get new VPLPBDisplayRegion
        sliderValue = ssps['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].getSliderValue()
        drValue = sliderValue/100*0.950+0.050
        ssps['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONVALUETEXT"].updateText(f"{drValue*100:.1f} %")
        ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):
        #UpdateTracker Initialization
        updateTracker = [False, False] #[0]: VPLP, [1]: VPLPB
        #Check for any changes in the configuration
        #---IVP Master
        ivpMaster_previous = oc['IVP_Master']
        oc['IVP_Master'] = ssps['MAIN'].GUIOs["MAININDICATOR_IVP"].getStatus()
        if ivpMaster_previous != oc['IVP_Master']: updateTracker = [True, True]
        #---displaySwitch - VPLP
        vplpDisplay_prev = oc['IVP_VPLP_Display']
        oc['IVP_VPLP_Display'] = ssps['IVP'].GUIOs["INDICATOR_VPLP_DISPLAYSWITCH"].getStatus()
        if vplpDisplay_prev != oc['IVP_VPLP_Display']: updateTracker[0] = True
        #---displaySwitch - VPLB
        vplpbDisplay_prev = oc['IVP_VPLPB_Display']
        oc['IVP_VPLPB_Display'] = ssps['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYSWITCH"].getStatus()
        if vplpbDisplay_prev != oc['IVP_VPLPB_Display']: updateTracker[1] = True
        #---displayWidth - VPLP
        vplpDisplayWidth_prev = oc['IVP_VPLP_DisplayWidth']
        oc['IVP_VPLP_DisplayWidth'] = round(ssps['IVP'].GUIOs["INDICATOR_VPLP_DISPLAYWIDTHSLIDER"].getSliderValue()/100*0.9+0.1, 2)
        if vplpDisplayWidth_prev != oc['IVP_VPLP_DisplayWidth']: updateTracker[0] = True
        #---VPLPB Display Region
        vplpbDisplayRegion_prev = oc['IVP_VPLPB_DisplayRegion']
        oc['IVP_VPLPB_DisplayRegion'] = round(ssps['IVP'].GUIOs["INDICATOR_VPLPB_DISPLAYREGIONSLIDER"].getSliderValue()/100*0.950+0.050, 3)
        if vplpbDisplayRegion_prev != oc['IVP_VPLPB_DisplayRegion']: updateTracker[1] = True
        #---Colors
        for targetLine in ('VPLP', 'VPLPB'):
            color_previous = (oc[f'IVP_{targetLine}_ColorR%{cgt}'],
                                oc[f'IVP_{targetLine}_ColorG%{cgt}'],
                                oc[f'IVP_{targetLine}_ColorB%{cgt}'],
                                oc[f'IVP_{targetLine}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['IVP'].GUIOs[f"INDICATOR_{targetLine}_COLOR"].getColor()
            oc[f'IVP_{targetLine}_ColorR%{cgt}'] = color_r
            oc[f'IVP_{targetLine}_ColorG%{cgt}'] = color_g
            oc[f'IVP_{targetLine}_ColorB%{cgt}'] = color_b
            oc[f'IVP_{targetLine}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): 
                if   targetLine == 'VPLP':  updateTracker[0] = True
                elif targetLine == 'VPLPB': updateTracker[1] = True
        #Content Update Handling
        drawSignal = 0
        drawSignal += 0b01*updateTracker[0] #VPLP
        drawSignal += 0b10*updateTracker[1] #VPLPB
        if drawSignal:
            self._drawer_RemoveDrawings(analysisCode      = 'IVP', gRemovalSignal = drawSignal) #Remove previous graphics
            self.__addBufferZone_toDrawQueue(analysisCode = 'IVP', drawSignal     = drawSignal) #Update draw queue
        #Settings Control Button
        ssps['IVP'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'Interval'):
        #Get new nSamples
        try:    _nSamples = int(ssps['IVP'].GUIOs["INDICATOR_INTERVAL_INPUTTEXT"].getText())
        except: _nSamples = None
        #Save the new value to the object config dictionary
        oc['IVP_NSamples'] = _nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'GammaFactor'):
        #Get new Gamma Factor
        gammaFactor = round(ssps['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_SLIDER"].getSliderValue()/100*0.095+0.005, 3)
        ssps['IVP'].GUIOs["INDICATOR_GAMMAFACTOR_VALUETEXT"].updateText(f"{gammaFactor*100:.1f} %")
        oc['IVP_GammaFactor'] = gammaFactor
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'DeltaFactor'):
        #Get new Delta Factor
        deltaFactor = round(ssps['IVP'].GUIOs["INDICATOR_DELTAFACTOR_SLIDER"].getSliderValue()/100*9.9+0.1, 1)
        ssps['IVP'].GUIOs["INDICATOR_DELTAFACTOR_VALUETEXT"].updateText(f"{int(deltaFactor*100)} %")
        oc['IVP_DeltaFactor'] = deltaFactor
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'Prominence'):
        #Get new Prominence
        prominence = round(ssps['IVP'].GUIOs["INDICATOR_PROMINENCE_SLIDER"].getSliderValue()/100*0.99+0.01, 2)
        ssps['IVP'].GUIOs["INDICATOR_PROMINENCE_VALUETEXT"].updateText(f"{int(prominence*100)} %")
        oc['IVP_Prominence'] = prominence
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'Distance'):
        #Get new Distance
        distance = int(round(ssps['IVP'].GUIOs["INDICATOR_DISTANCE_SLIDER"].getSliderValue()/100*99+1))
        ssps['IVP'].GUIOs["INDICATOR_DISTANCE_VALUETEXT"].updateText(f"{distance}")
        oc['IVP_Distance'] = distance
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'Height'):
        #Get new Height
        height = round(ssps['IVP'].GUIOs["INDICATOR_HEIGHT_SLIDER"].getSliderValue()/100, 2)
        ssps['IVP'].GUIOs["INDICATOR_HEIGHT_VALUETEXT"].updateText(f"{int(height*100)} %")
        oc['IVP_Height'] = height
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'SWING'
elif indicatorType == 'SWING':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['SWING'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineSelected}_LINECOLOR"].getColor()
        ssps['SWING'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['SWING'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['SWING'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['SWING'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['SWING'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['SWING'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['SWING'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['SWING'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['SWING'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['SWING'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['SWING'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['SWING'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                gValue = int(ssps['SWING'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                bValue = int(ssps['SWING'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                aValue = int(ssps['SWING'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['SWING'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['SWING'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['SWING'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['SWING'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['SWING'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['SWING'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['SWING'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['SWING'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['SWING'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['SWING'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['SWING'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['SWING'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['SWING']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'SWING_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'SWING_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'SWING_{lineIndex}_Width'] = 1
                ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'SWING_{lineIndex}_Width']))
            if width_previous != oc[f'SWING_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'SWING_{lineIndex}_ColorR%{cgt}'],
                                oc[f'SWING_{lineIndex}_ColorG%{cgt}'],
                                oc[f'SWING_{lineIndex}_ColorB%{cgt}'],
                                oc[f'SWING_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_LINECOLOR"].getColor()
            oc[f'SWING_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'SWING_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'SWING_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'SWING_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'SWING_{lineIndex}_Display']
            oc[f'SWING_{lineIndex}_Display'] = ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'SWING_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---SWING Master
        swingMaster_previous = oc['SWING_Master']
        oc['SWING_Master'] = ssps['MAIN'].GUIOs["MAININDICATOR_SWING"].getStatus()
        if swingMaster_previous != oc['SWING_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredSWING in (aCode for aCode in ap_iID if aCode.startswith('SWING')):
            lineIndex = ap_iID[configuredSWING]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredSWING, gRemovalSignal = _FULLDRAWSIGNALS['SWING']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredSWING, drawSignal     = _FULLDRAWSIGNALS['SWING']) #Update draw queue
        #Control Buttons Handling
        ssps['SWING'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        _newStatus = ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}"].getStatus()
        oc[f'SWING_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'SwingRangeTextInputBox'):
        lineIndex = int(guioName_split[2])
        #Get new Swing Range
        try:    swingRange = round(float(ssps['SWING'].GUIOs[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].getText()), 4)
        except: swingRange = None
        #Save the new value to the object config dictionary
        oc[f'SWING_{lineIndex}_SwingRange'] = swingRange
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'VOL'
elif indicatorType == 'VOL':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['VOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineSelected}_LINECOLOR"].getColor()
        ssps['VOL'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['VOL'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['VOL'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['VOL'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['VOL'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['VOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['VOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['VOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['VOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['VOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['VOL'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['VOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['VOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['VOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['VOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['VOL'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['VOL'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['VOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['VOL'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['VOL'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['VOL'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['VOL'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['VOL'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['VOL'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['VOL'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['VOL'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['VOL'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'VolTypeSelection'):
        ssps['VOL'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = {'VOL': False}
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['VOL']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'VOL_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'VOL_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset == True:
                oc[f'VOL_{lineIndex}_Width'] = 1
                ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'VOL_{lineIndex}_Width']))
            if width_previous != oc[f'VOL_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'VOL_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'VOL_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'VOL_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'VOL_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}_LINECOLOR"].getColor()
            oc[f'VOL_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'VOL_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'VOL_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'VOL_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'VOL_{lineIndex}_Display']
            oc[f'VOL_{lineIndex}_Display'] = ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'VOL_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---VOL Master
        volMaster_previous = oc['VOL_Master']
        oc['VOL_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_VOL"].getStatus()
        volMaster_updated = (volMaster_previous != oc['VOL_Master'])
        if volMaster_updated:
            for targetLine in updateTracker: updateTracker[targetLine] = True
        #---VOL Type
        volType_previous = oc['VOL_VolumeType']
        oc['VOL_VolumeType'] = ssps['VOL'].GUIOs["INDICATOR_VOLTYPESELECTION"].getSelected()
        volumeType_updated = (volType_previous != oc['VOL_VolumeType'])
        if volumeType_updated:
            for targetLine in updateTracker: updateTracker[targetLine] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['VOL']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['VOL'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        if updateTracker['VOL']:
            self._drawer_RemoveDrawings(analysisCode = 'VOL', gRemovalSignal = _FULLDRAWSIGNALS['VOL']) #Remove previous graphics
            self.__addBufferZone_toDrawQueue(analysisCode  = 'VOL', drawSignal     = _FULLDRAWSIGNALS['VOL']) #Update draw queue
        ap_iID = self.analysisParams[self.intervalID]
        for configuredVOL in (aCode for aCode in ap_iID if aCode.startswith('VOL')):
            lineIndex = ap_iID[configuredVOL]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredVOL, gRemovalSignal = _FULLDRAWSIGNALS['VOL']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredVOL, drawSignal     = _FULLDRAWSIGNALS['VOL']) #Update draw queue
        #Control Buttons Handling
        ssps['VOL'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        _newStatus = ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}"].getStatus()
        oc[f'VOL_{lineIndex}_LineActive'] = _newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    _nSamples = int(ssps['VOL'].GUIOs[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].getText())
        except: _nSamples = None
        #Save the new value to the object config dictionary
        oc[f'VOL_{lineIndex}_NSamples'] = _nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'MATypeSelection'): 
        #Get new MAType
        maType = ssps['VOL'].GUIOs["INDICATOR_MATYPESELECTION"].getSelected()
        #Save the new value to the object config dictionary
        oc['VOL_MAType'] = maType
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'DEPTH'
elif indicatorType == 'DEPTH':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['DEPTH'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['DEPTH'].GUIOs[f"INDICATOR_{lineSelected}_LINECOLOR"].getColor()
        ssps['DEPTH'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['DEPTH'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['DEPTH'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['DEPTH'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['DEPTH'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['DEPTH'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['DEPTH'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['DEPTH'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['DEPTH'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['DEPTH'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['DEPTH'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                gValue = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                bValue = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                aValue = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['DEPTH'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['DEPTH'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['DEPTH'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['DEPTH'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['DEPTH'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['DEPTH'].GUIOs[f"INDICATOR_{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['DEPTH'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['DEPTH'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = [False, False]
        #Check for any changes in the configuration siTypes_analysisCodes
        #---Bids Color
        bidsColor_previous = (oc[f'DEPTH_BIDS_ColorR%{cgt}'], 
                                oc[f'DEPTH_BIDS_ColorG%{cgt}'], 
                                oc[f'DEPTH_BIDS_ColorB%{cgt}'], 
                                oc[f'DEPTH_BIDS_ColorA%{cgt}'])
        color_r, color_g, color_b, color_a = ssps['DEPTH'].GUIOs["INDICATOR_BIDS_LINECOLOR"].getColor()
        oc[f'DEPTH_BIDS_ColorR%{cgt}'] = color_r
        oc[f'DEPTH_BIDS_ColorG%{cgt}'] = color_g
        oc[f'DEPTH_BIDS_ColorB%{cgt}'] = color_b
        oc[f'DEPTH_BIDS_ColorA%{cgt}'] = color_a
        if bidsColor_previous != (color_r, color_g, color_b, color_a): updateTracker[0] = True
        #---Asks Color
        asksColor_previous = (oc[f'DEPTH_ASKS_ColorR%{cgt}'], 
                                oc[f'DEPTH_ASKS_ColorG%{cgt}'], 
                                oc[f'DEPTH_ASKS_ColorB%{cgt}'], 
                                oc[f'DEPTH_ASKS_ColorA%{cgt}'])
        color_r, color_g, color_b, color_a = ssps['DEPTH'].GUIOs["INDICATOR_ASKS_LINECOLOR"].getColor()
        oc[f'DEPTH_ASKS_ColorR%{cgt}'] = color_r
        oc[f'DEPTH_ASKS_ColorG%{cgt}'] = color_g
        oc[f'DEPTH_ASKS_ColorB%{cgt}'] = color_b
        oc[f'DEPTH_ASKS_ColorA%{cgt}'] = color_a
        if asksColor_previous != (color_r, color_g, color_b, color_a): updateTracker[1] = True
        #---Display
        depthMaster_previous = oc['DEPTH_Master']
        oc['DEPTH_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_DEPTH"].getStatus()
        depthMaster_updated = (depthMaster_previous != oc['DEPTH_Master'])
        if depthMaster_updated:
            updateTracker[0] = True
            updateTracker[1] = True
        #Extrema Recomputation
        if any(updateTracker):
            sivIdx  = self.siTypes_siViewerAlloc['DEPTH']
            sivCode = f"SIVIEWER{sivIdx}"
            if sivCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['DEPTH'](): self._editVVR_toExtremaCenter(displayBoxName = sivCode)
        #Queue Update
        drawSignal = 0
        drawSignal += 0b01*updateTracker[0] #Bids
        drawSignal += 0b10*updateTracker[1] #Asks
        if drawSignal:
            self._drawer_RemoveDrawings(analysisCode     = 'DEPTH', gRemovalSignal = drawSignal)
            self.__addBufferZone_toDrawQueue(analysisCode = 'DEPTH', drawSignal     = drawSignal)
        #Control Buttons Handling
        ssps['DEPTH'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True

#Subpage 'AGGTRADE'
elif indicatorType == 'AGGTRADE':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['AGGTRADE'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['AGGTRADE'].GUIOs[f"INDICATOR_{lineSelected}_LINECOLOR"].getColor()
        ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['AGGTRADE'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['AGGTRADE'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['AGGTRADE'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['AGGTRADE'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                    gValue = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                    bValue = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                    aValue = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['AGGTRADE'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['AGGTRADE'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['AGGTRADE'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['AGGTRADE'].GUIOs[f"INDICATOR_{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['AGGTRADE'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['AGGTRADE'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayTypeSelection'):
        ssps['AGGTRADE'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = [False, False]
        #Check for any changes in the configuration siTypes_analysisCodes
        #---Buy Color
        buyColor_previous = (oc[f'AGGTRADE_BUY_ColorR%{cgt}'], 
                                oc[f'AGGTRADE_BUY_ColorG%{cgt}'], 
                                oc[f'AGGTRADE_BUY_ColorB%{cgt}'], 
                                oc[f'AGGTRADE_BUY_ColorA%{cgt}'])
        color_r, color_g, color_b, color_a = ssps['AGGTRADE'].GUIOs["INDICATOR_BUY_LINECOLOR"].getColor()
        oc[f'AGGTRADE_BUY_ColorR%{cgt}'] = color_r
        oc[f'AGGTRADE_BUY_ColorG%{cgt}'] = color_g
        oc[f'AGGTRADE_BUY_ColorB%{cgt}'] = color_b
        oc[f'AGGTRADE_BUY_ColorA%{cgt}'] = color_a
        if buyColor_previous != (color_r, color_g, color_b, color_a): updateTracker[0] = True
        #---Sell Color
        sellColor_previous = (oc[f'AGGTRADE_SELL_ColorR%{cgt}'], 
                                oc[f'AGGTRADE_SELL_ColorG%{cgt}'], 
                                oc[f'AGGTRADE_SELL_ColorB%{cgt}'], 
                                oc[f'AGGTRADE_SELL_ColorA%{cgt}'])
        color_r, color_g, color_b, color_a = ssps['AGGTRADE'].GUIOs["INDICATOR_SELL_LINECOLOR"].getColor()
        oc[f'AGGTRADE_SELL_ColorR%{cgt}'] = color_r
        oc[f'AGGTRADE_SELL_ColorG%{cgt}'] = color_g
        oc[f'AGGTRADE_SELL_ColorB%{cgt}'] = color_b
        oc[f'AGGTRADE_SELL_ColorA%{cgt}'] = color_a
        if sellColor_previous != (color_r, color_g, color_b, color_a): updateTracker[1] = True
        #---Display Type
        displayType_previous = oc['AGGTRADE_DisplayType']
        oc['AGGTRADE_DisplayType'] = ssps['AGGTRADE'].GUIOs["INDICATOR_DISPLAYTYPESELECTION"].getSelected()
        displayType_updated = (displayType_previous != oc['AGGTRADE_DisplayType'])
        if displayType_updated:
            updateTracker[0] = True
            updateTracker[1] = True
        #---Display
        aggTradeMaster_previous = oc['AGGTRADE_Master']
        oc['AGGTRADE_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_AGGTRADE"].getStatus()
        aggTradeMaster_updated = (aggTradeMaster_previous != oc['AGGTRADE_Master'])
        if aggTradeMaster_updated:
            updateTracker[0] = True
            updateTracker[1] = True
        #Extrema Recomputation
        if any(updateTracker):
            sivIdx  = self.siTypes_siViewerAlloc['AGGTRADE']
            sivCode = f"SIVIEWER{sivIdx}"
            if sivCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['AGGTRADE'](): self._editVVR_toExtremaCenter(displayBoxName = sivCode)
        #Queue Update
        drawSignal = 0
        drawSignal += 0b01*updateTracker[0] #Buy
        drawSignal += 0b10*updateTracker[1] #Sell
        if drawSignal:
            self._drawer_RemoveDrawings(analysisCode     = 'AGGTRADE', gRemovalSignal = drawSignal)
            self.__addBufferZone_toDrawQueue(analysisCode = 'AGGTRADE', drawSignal     = drawSignal)
        #Control Buttons Handling
        ssps['AGGTRADE'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True

#Subpage 'NNA'
elif indicatorType == 'NNA':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['NNA'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineSelected}_LINECOLOR"].getColor()
        ssps['NNA'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['NNA'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['NNA'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['NNA'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['NNA'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['NNA'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['NNA'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['NNA'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['NNA'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['NNA'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['NNA'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['NNA'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['NNA'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['NNA'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['NNA'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['NNA'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['NNA'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['NNA'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['NNA'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['NNA'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['NNA'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['NNA'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['NNA'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['NNA'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['NNA'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['NNA'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['NNA'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['NNA']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'NNA_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'NNA_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'NNA_{lineIndex}_Width'] = 1
                ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'NNA_{lineIndex}_Width']))
            if width_previous != oc[f'NNA_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'NNA_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'NNA_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'NNA_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'NNA_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_LINECOLOR"].getColor()
            oc[f'NNA_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'NNA_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'NNA_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'NNA_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'NNA_{lineIndex}_Display']
            oc[f'NNA_{lineIndex}_Display'] = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'NNA_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---NNA Master
        mfiMaster_previous = oc['NNA_Master']
        oc['NNA_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_NNA"].getStatus()
        if mfiMaster_previous != oc['NNA_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['NNA']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['NNA'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredNNA in (aCode for aCode in ap_iID if aCode.startswith('NNA')):
            lineIndex = ap_iID[configuredNNA]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredNNA, gRemovalSignal = _FULLDRAWSIGNALS['NNA']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredNNA, drawSignal     = _FULLDRAWSIGNALS['NNA']) #Update draw queue
        #Control Buttons Handling
        ssps['NNA'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}"].getStatus()
        oc[f'NNA_{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'NNCodeTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new Neural Network Code
        try:    nnCode = ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].getText()
        except: nnCode = None
        #Save the new value to the object config dictionary
        oc[f'NNA_{lineIndex}_NeuralNetworkCode'] = nnCode
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'AlphaTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new Alpha
        try:    alpha = round(float(ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].getText()), 2)
        except: alpha = None
        #Save the new value to the object config dictionary
        oc[f'NNA_{lineIndex}_Alpha'] = alpha
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'BetaTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new Beta
        try:    beta = int(ssps['NNA'].GUIOs[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].getText())
        except: beta = None
        #Save the new value to the object config dictionary
        oc[f'NNA_{lineIndex}_Beta'] = beta
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'MMACD'
elif indicatorType == 'MMACD':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'): 
        lineSelected = ssps['MMACD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['MMACD'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].getColor()
        ssps['MMACD'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['MMACD'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['MMACD'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['MMACD'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['MMACD'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['MMACD'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['MMACD'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['MMACD'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['MMACD'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['MMACD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):          
        cType = guioName_split[2]
        ssps['MMACD'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                gValue = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                bValue = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                aValue = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['MMACD'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['MMACD'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['MMACD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):     
        lineSelected = ssps['MMACD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['MMACD'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['MMACD'].GUIOs[f"INDICATOR_{lineSelected}_COLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['MMACD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['MMACD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):  
        ssps['MMACD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'HistrogramTypeSelectionBox'):
        ssps['MMACD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):  
        #UpdateTracker Initialization
        updateTracker = [False, False, False] #[0]: Draw MMACD, [1]: Draw SIGNAL, [2]: Draw HISTOGRAM
        #Check for any changes in the configuration
        #---MMACD Master
        mmacdMaster_previous = oc['MMACD_Master']
        oc['MMACD_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_MMACD"].getStatus()
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
            color_r, color_g, color_b, color_a = ssps['MMACD'].GUIOs[f"INDICATOR_{targetLine}_COLOR"].getColor()
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
            oc[f'MMACD_{targetLine}_Display'] = ssps['MMACD'].GUIOs[f"INDICATOR_{targetLine}_DISPLAYSWITCH"].getStatus()
            if displayStatus_prev != oc[f'MMACD_{targetLine}_Display']:
                if   targetLine == 'MMACD':     updateTracker[0] = True
                elif targetLine == 'SIGNAL':    updateTracker[1] = True
                elif targetLine == 'HISTOGRAM': updateTracker[2] = True
        #---Histogram Type
        histogramType_prev = oc['MMACD_HISTOGRAM_Type']
        oc['MMACD_HISTOGRAM_Type'] = ssps['MMACD'].GUIOs["INDICATOR_HISTOGRAMTYPE_SELECTION"].getSelected()
        if histogramType_prev != oc['MMACD_HISTOGRAM_Type']:
            updateTracker[2] = True
        #Extrema Recomputation
        if any(updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['MMACD']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['MMACD'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        drawSignal = 0
        drawSignal += 0b001*updateTracker[0] #MMACD
        drawSignal += 0b010*updateTracker[1] #SIGNAL
        drawSignal += 0b100*updateTracker[2] #HISTOGRAM
        if drawSignal:
            self._drawer_RemoveDrawings(analysisCode = 'MMACD', gRemovalSignal = drawSignal) #Remove previous graphics
            self.__addBufferZone_toDrawQueue(analysisCode  = 'MMACD', drawSignal     = drawSignal) #Update draw queue
        #Control Buttons Handling
        ssps['MMACD'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'):          
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['MMACD'].GUIOs[f"INDICATOR_MMACDMA{lineIndex}"].getStatus()
        oc[f'MMACD_MA{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'):          
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamples = int(ssps['MMACD'].GUIOs[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'MMACD_MA{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'SignalIntervalTextInputBox'):    
        #Get new nSamples
        try:    nSamples = int(ssps['MMACD'].GUIOs["INDICATOR_SIGNALINTERVALTEXTINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc['MMACD_SignalNSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'DMIxADX'
elif indicatorType == 'DMIxADX':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineSelected}_LINECOLOR"].getColor()
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['DMIxADX'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['DMIxADX'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['DMIxADX'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['DMIxADX'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                gValue = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                bValue = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                aValue = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['DMIxADX'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['DMIxADX'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['DMIxADX'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['DMIxADX'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['DMIxADX'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayTypeSelectionBox'):
        ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['DMIxADX']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'DMIxADX_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'DMIxADX_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'DMIxADX_{lineIndex}_Width'] = 1
                ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'DMIxADX_{lineIndex}_Width']))
            if width_previous != oc[f'DMIxADX_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_LINECOLOR"].getColor()
            oc[f'DMIxADX_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'DMIxADX_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'DMIxADX_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'DMIxADX_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'DMIxADX_{lineIndex}_Display']
            oc[f'DMIxADX_{lineIndex}_Display'] = ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'DMIxADX_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---DMIxADX Master
        dmixadxMaster_previous = oc['DMIxADX_Master']
        oc['DMIxADX_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_DMIxADX"].getStatus()
        if dmixadxMaster_previous != oc['DMIxADX_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #---Display Type
        displayType_prev = oc['DMIxADX_DisplayType']
        oc['DMIxADX_DisplayType'] = ssps['DMIxADX'].GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].getSelected()
        if displayType_prev != oc['DMIxADX_DisplayType']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['DMIxADX']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['DMIxADX'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredDMIxADX in (aCode for aCode in ap_iID if aCode.startswith('DMIxADX')):
            lineIndex = ap_iID[configuredDMIxADX]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredDMIxADX, gRemovalSignal = _FULLDRAWSIGNALS['DMIxADX']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredDMIxADX, drawSignal     = _FULLDRAWSIGNALS['DMIxADX']) #Update draw queue
        #Control Buttons Handling
        ssps['DMIxADX'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}"].getStatus()
        oc[f'DMIxADX_{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamples = int(ssps['DMIxADX'].GUIOs[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'DMIxADX_{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'MFI'
elif indicatorType == 'MFI':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineSelected}_LINECOLOR"].getColor()
        ssps['MFI'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['MFI'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['MFI'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['MFI'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['MFI'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['MFI'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['MFI'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['MFI'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['MFI'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['MFI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['MFI'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['MFI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['MFI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['MFI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['MFI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['MFI'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['MFI'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['MFI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['MFI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['MFI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['MFI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['MFI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['MFI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['MFI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayTypeSelectionBox'):
        ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['MFI']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'MFI_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'MFI_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'MFI_{lineIndex}_Width'] = 1
                ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'MFI_{lineIndex}_Width']))
            if width_previous != oc[f'MFI_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'MFI_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'MFI_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'MFI_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'MFI_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_LINECOLOR"].getColor()
            oc[f'MFI_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'MFI_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'MFI_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'MFI_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'MFI_{lineIndex}_Display']
            oc[f'MFI_{lineIndex}_Display'] = ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'MFI_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---MFI Master
        mfiMaster_previous = oc['MFI_Master']
        oc['MFI_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_MFI"].getStatus()
        if mfiMaster_previous != oc['MFI_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #---Display Type
        displayType_prev = oc['MFI_DisplayType']
        oc['MFI_DisplayType'] = ssps['MFI'].GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].getSelected()
        if displayType_prev != oc['MFI_DisplayType']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['MFI']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['MFI'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredMFI in (aCode for aCode in ap_iID if aCode.startswith('MFI')):
            lineIndex = ap_iID[configuredMFI]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredMFI, gRemovalSignal = _FULLDRAWSIGNALS['MFI']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredMFI, drawSignal     = _FULLDRAWSIGNALS['MFI']) #Update draw queue
        #Control Buttons Handling
        ssps['MFI'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}"].getStatus()
        oc[f'MFI_{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamples = int(ssps['MFI'].GUIOs[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'MFI_{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'TPD'
elif indicatorType == 'TPD':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['TPD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineSelected}_LINECOLOR"].getColor()
        ssps['TPD'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['TPD'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['TPD'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['TPD'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['TPD'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['TPD'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['TPD'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['TPD'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['TPD'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['TPD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['TPD'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['TPD'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['TPD'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['TPD'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['TPD'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['TPD'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['TPD'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['TPD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['TPD'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['TPD'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['TPD'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['TPD'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['TPD'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['TPD'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayTypeSelectionBox'):
        ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['TPD']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'TPD_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'TPD_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'TPD_{lineIndex}_Width'] = 1
                ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'TPD_{lineIndex}_Width']))
            if width_previous != oc[f'TPD_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'TPD_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'TPD_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'TPD_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'TPD_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_LINECOLOR"].getColor()
            oc[f'TPD_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'TPD_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'TPD_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'TPD_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'TPD_{lineIndex}_Display']
            oc[f'TPD_{lineIndex}_Display'] = ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'TPD_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---TPD Master
        tpdMaster_previous = oc['TPD_Master']
        oc['TPD_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_TPD"].getStatus()
        if tpdMaster_previous != oc['TPD_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #---Display Type
        displayType_prev = oc['TPD_DisplayType']
        oc['TPD_DisplayType'] = ssps['TPD'].GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].getSelected()
        if displayType_prev != oc['TPD_DisplayType']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['TPD']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['TPD'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredTPD in (aCode for aCode in ap_iID if aCode.startswith('TPD')):
            lineIndex = ap_iID[configuredTPD]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredTPD, gRemovalSignal = _FULLDRAWSIGNALS['TPD']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredTPD, drawSignal     = _FULLDRAWSIGNALS['TPD']) #Update draw queue
        #Control Buttons Handling
        ssps['TPD'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}"].getStatus()
        oc[f'TPD_{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'ViewLengthTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    viewLength = int(ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].getText())
        except: viewLength = None
        #Save the new value to the object config dictionary
        oc[f'TPD_{lineIndex}_ViewLength'] = viewLength
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamples = int(ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'TPD_{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'MAIntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamplesMA = int(ssps['TPD'].GUIOs[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].getText())
        except: nSamplesMA = None
        #Save the new value to the object config dictionary
        oc[f'TPD_{lineIndex}_NSamplesMA'] = nSamplesMA
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'WOI'
elif indicatorType == 'WOI':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['WOI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineSelected}_LINECOLOR"].getColor()
        ssps['WOI'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['WOI'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['WOI'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['WOI'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['WOI'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['WOI'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['WOI'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['WOI'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['WOI'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['WOI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['WOI'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['WOI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['WOI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['WOI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['WOI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['WOI'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['WOI'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['WOI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['WOI'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['WOI'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['WOI'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['WOI'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['WOI'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['WOI'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayTypeSelectionBox'):
        ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['WOI']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'WOI_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'WOI_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'WOI_{lineIndex}_Width'] = 1
                ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'WOI_{lineIndex}_Width']))
            if width_previous != oc[f'WOI_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'WOI_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'WOI_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'WOI_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'WOI_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_LINECOLOR"].getColor()
            oc[f'WOI_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'WOI_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'WOI_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'WOI_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'WOI_{lineIndex}_Display']
            oc[f'WOI_{lineIndex}_Display'] = ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'WOI_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---WOI Master
        WOIMaster_previous = oc['WOI_Master']
        oc['WOI_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_WOI"].getStatus()
        if WOIMaster_previous != oc['WOI_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #---Display Type
        displayType_prev = oc['WOI_DisplayType']
        oc['WOI_DisplayType'] = ssps['WOI'].GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].getSelected()
        if displayType_prev != oc['WOI_DisplayType']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['WOI']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['WOI'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredWOI in (aCode for aCode in ap_iID if aCode.startswith('WOI')):
            lineIndex = ap_iID[configuredWOI]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredWOI, gRemovalSignal = _FULLDRAWSIGNALS['WOI']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredWOI, drawSignal     = _FULLDRAWSIGNALS['WOI']) #Update draw queue
        #Control Buttons Handling
        ssps['WOI'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}"].getStatus()
        oc[f'WOI_{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamples = int(ssps['WOI'].GUIOs[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'WOI_{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True

#Subpage 'NES'
elif indicatorType == 'NES':
    setterType = guioName_split[1]
    #Graphics Related
    if (setterType == 'LineSelectionBox'):    
        lineSelected = ssps['NES'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r, color_g, color_b, color_a = ssps['NES'].GUIOs[f"INDICATOR_NES{lineSelected}_LINECOLOR"].getColor()
        ssps['NES'].GUIOs['INDICATORCOLOR_LED'].updateColor(color_r, color_g, color_b, color_a)
        ssps['NES'].GUIOs["INDICATORCOLOR_R_VALUE"].updateText(str(color_r))
        ssps['NES'].GUIOs["INDICATORCOLOR_G_VALUE"].updateText(str(color_g))
        ssps['NES'].GUIOs["INDICATORCOLOR_B_VALUE"].updateText(str(color_b))
        ssps['NES'].GUIOs["INDICATORCOLOR_A_VALUE"].updateText(str(color_a))
        ssps['NES'].GUIOs['INDICATORCOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
        ssps['NES'].GUIOs['INDICATORCOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
        ssps['NES'].GUIOs['INDICATORCOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
        ssps['NES'].GUIOs['INDICATORCOLOR_A_SLIDER'].setSliderValue(color_a/255*100)
        ssps['NES'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
    elif (setterType == 'Color'):             
        cType = guioName_split[2]
        ssps['NES'].GUIOs['INDICATORCOLOR_LED'].updateColor(rValue = int(ssps['NES'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                            gValue = int(ssps['NES'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                            bValue = int(ssps['NES'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                            aValue = int(ssps['NES'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100))
        color_target_new = int(ssps['NES'].GUIOs[f'INDICATORCOLOR_{cType}_SLIDER'].getSliderValue()*255/100)
        ssps['NES'].GUIOs[f"INDICATORCOLOR_{cType}_VALUE"].updateText(text = f"{color_target_new}")
        ssps['NES'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].activate()
    elif (setterType == 'ApplyColor'):        
        lineSelected = ssps['NES'].GUIOs["INDICATORCOLOR_TARGETSELECTION"].getSelected()
        color_r = int(ssps['NES'].GUIOs['INDICATORCOLOR_R_SLIDER'].getSliderValue()*255/100)
        color_g = int(ssps['NES'].GUIOs['INDICATORCOLOR_G_SLIDER'].getSliderValue()*255/100)
        color_b = int(ssps['NES'].GUIOs['INDICATORCOLOR_B_SLIDER'].getSliderValue()*255/100)
        color_a = int(ssps['NES'].GUIOs['INDICATORCOLOR_A_SLIDER'].getSliderValue()*255/100)
        ssps['NES'].GUIOs[f"INDICATOR_NES{lineSelected}_LINECOLOR"].updateColor(color_r, color_g, color_b, color_a)
        ssps['NES'].GUIOs['INDICATORCOLOR_APPLYCOLOR'].deactivate()
        ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'WidthTextInputBox'): 
        ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplaySwitch'):     
        ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'DisplayTypeSelectionBox'):
        ssps['NES'].GUIOs['APPLYNEWSETTINGS'].activate()
    elif (setterType == 'ApplySettings'):     
        #UpdateTracker Initialization
        updateTracker = dict()
        #Check for any changes in the configuration
        for lineIndex in range (_NMAXLINES['NES']):
            updateTracker[lineIndex] = False
            #Width
            width_previous = oc[f'NES_{lineIndex}_Width']
            reset = False
            try:
                width = int(ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].getText())
                if 0 < width: oc[f'NES_{lineIndex}_Width'] = width
                else: reset = True
            except: reset = True
            if reset:
                oc[f'NES_{lineIndex}_Width'] = 1
                ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_WIDTHINPUT"].updateText(str(oc[f'NES_{lineIndex}_Width']))
            if width_previous != oc[f'NES_{lineIndex}_Width']: updateTracker[lineIndex] = True
            #Color
            color_previous = (oc[f'NES_{lineIndex}_ColorR%{cgt}'], 
                                oc[f'NES_{lineIndex}_ColorG%{cgt}'], 
                                oc[f'NES_{lineIndex}_ColorB%{cgt}'], 
                                oc[f'NES_{lineIndex}_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_LINECOLOR"].getColor()
            oc[f'NES_{lineIndex}_ColorR%{cgt}'] = color_r
            oc[f'NES_{lineIndex}_ColorG%{cgt}'] = color_g
            oc[f'NES_{lineIndex}_ColorB%{cgt}'] = color_b
            oc[f'NES_{lineIndex}_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker[lineIndex] = True
            #Line Display
            display_previous = oc[f'NES_{lineIndex}_Display']
            oc[f'NES_{lineIndex}_Display'] = ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_DISPLAY"].getStatus()
            if display_previous != oc[f'NES_{lineIndex}_Display']: updateTracker[lineIndex] = True
        #---NES Master
        NESMaster_previous = oc['NES_Master']
        oc['NES_Master'] = ssps['MAIN'].GUIOs["SUBINDICATOR_NES"].getStatus()
        if NESMaster_previous != oc['NES_Master']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #---Display Type
        displayType_prev = oc['NES_DisplayType']
        oc['NES_DisplayType'] = ssps['NES'].GUIOs["INDICATOR_DISPLAYTYPE_SELECTION"].getSelected()
        if displayType_prev != oc['NES_DisplayType']:
            for lineIndex in updateTracker: updateTracker[lineIndex] = True
        #Extrema Recomputation
        if any(updateTracker[lIndex] for lIndex in updateTracker):
            siViewerIndex = self.siTypes_siViewerAlloc['NES']
            siViewerCode  = f"SIVIEWER{siViewerIndex}"
            if siViewerCode in self.displayBox_graphics_visibleSIViewers:
                if self.checkVerticalExtremas_SIs['NES'](): self._editVVR_toExtremaCenter(displayBoxName = siViewerCode)
        #Queue Update
        ap_iID = self.analysisParams[self.intervalID]
        for configuredNES in (aCode for aCode in ap_iID if aCode.startswith('NES')):
            lineIndex = ap_iID[configuredNES]['lineIndex']
            if updateTracker[lineIndex]:
                self._drawer_RemoveDrawings(analysisCode = configuredNES, gRemovalSignal = _FULLDRAWSIGNALS['NES']) #Remove previous graphics
                self.__addBufferZone_toDrawQueue(analysisCode  = configuredNES, drawSignal = _FULLDRAWSIGNALS['NES']) #Update draw queue
        #Control Buttons Handling
        ssps['NES'].GUIOs['APPLYNEWSETTINGS'].deactivate()
        activateSaveConfigButton = True
    #Analysis Related
    elif (setterType == 'LineActivationSwitch'): 
        lineIndex = int(guioName_split[2])
        #Get new switch status
        newStatus = ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}"].getStatus()
        oc[f'NES_{lineIndex}_LineActive'] = newStatus
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
    elif (setterType == 'IntervalTextInputBox'): 
        lineIndex = int(guioName_split[2])
        #Get new nSamples
        try:    nSamples = int(ssps['NES'].GUIOs[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].getText())
        except: nSamples = None
        #Save the new value to the object config dictionary
        oc[f'NES_{lineIndex}_NSamples'] = nSamples
        #Analysis Configuration Update Response
        self._onAnalysisConfigurationUpdate()
        activateSaveConfigButton = True
"""


def cd_on_position_highlight_update():
    pass



def cd_on_position_selection_update():
    pass



def cd_check_vertical_extremas():
    pass



def cd_draw(chartDrawer, drawSignal, timestamp, analysisCode):
    pass



def cd_type_init(subPage):
    #[1]: Instances
    guios_THIS = subPage.GUIOs

    #[2]: GUIOs Update
    for lIdx in range (NMAXLINES):
        guios_THIS[f"INDICATOR_SMA{lIdx}"].deactivate()
        guios_THIS[f"INDICATOR_SMA{lIdx}_INTERVALINPUT"].deactivate()

    """
    #SMA
    for lineIndex in range (_NMAXLINES['SMA']):
        guios_SMA[f"INDICATOR_SMA{lineIndex}"].deactivate()
        guios_SMA[f"INDICATOR_SMA{lineIndex}_INTERVALINPUT"].deactivate()

    #WMA
    for lineIndex in range (_NMAXLINES['WMA']):
        guios_WMA[f"INDICATOR_WMA{lineIndex}"].deactivate()
        guios_WMA[f"INDICATOR_WMA{lineIndex}_INTERVALINPUT"].deactivate()

    #EMA
    for lineIndex in range (_NMAXLINES['EMA']):
        guios_EMA[f"INDICATOR_EMA{lineIndex}"].deactivate()
        guios_EMA[f"INDICATOR_EMA{lineIndex}_INTERVALINPUT"].deactivate()

    #PSAR
    for lineIndex in range (_NMAXLINES['PSAR']):
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}"].deactivate()
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF0INPUT"].deactivate()
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AF+INPUT"].deactivate()
        guios_PSAR[f"INDICATOR_PSAR{lineIndex}_AFMAXINPUT"].deactivate()

    #BOL
    guios_BOL["INDICATOR_MATYPESELECTION"].deactivate()
    for lineIndex in range (_NMAXLINES['BOL']):
        guios_BOL[f"INDICATOR_BOL{lineIndex}"].deactivate()
        guios_BOL[f"INDICATOR_BOL{lineIndex}_INTERVALINPUT"].deactivate()
        guios_BOL[f"INDICATOR_BOL{lineIndex}_BANDWIDTHINPUT"].deactivate()

    #IVP
    guios_IVP["INDICATOR_INTERVAL_INPUTTEXT"].deactivate()
    guios_IVP["INDICATOR_GAMMAFACTOR_SLIDER"].deactivate()
    guios_IVP["INDICATOR_DELTAFACTOR_SLIDER"].deactivate()

    #SWING
    for lineIndex in range (_NMAXLINES['SWING']):
        guios_SWING[f"INDICATOR_SWING{lineIndex}"].deactivate()
        guios_SWING[f"INDICATOR_SWING{lineIndex}_SWINGRANGEINPUT"].deactivate()

    #VOL
    guios_VOL["INDICATOR_MATYPESELECTION"].deactivate()
    for lineIndex in range (_NMAXLINES['VOL']):
        guios_VOL[f"INDICATOR_VOL{lineIndex}"].deactivate()
        guios_VOL[f"INDICATOR_VOL{lineIndex}_INTERVALINPUT"].deactivate()

    #NNA
    for lineIndex in range (_NMAXLINES['NNA']):
        guios_NNA[f"INDICATOR_NNA{lineIndex}"].deactivate()
        guios_NNA[f"INDICATOR_NNA{lineIndex}_NNCODEINPUT"].deactivate()
        guios_NNA[f"INDICATOR_NNA{lineIndex}_ALPHAINPUT"].deactivate()
        guios_NNA[f"INDICATOR_NNA{lineIndex}_BETAINPUT"].deactivate()

    #MMACD
    guios_MMACD["INDICATOR_SIGNALINTERVALTEXTINPUT"].deactivate()
    for lineIndex in range (_NMAXLINES['MMACD']):
        guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}"].deactivate()
        guios_MMACD[f"INDICATOR_MMACDMA{lineIndex}_INTERVALINPUT"].deactivate()

    #DMIxADX
    for lineIndex in range (_NMAXLINES['DMIxADX']):
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}"].deactivate()
        guios_DMIxADX[f"INDICATOR_DMIxADX{lineIndex}_INTERVALINPUT"].deactivate()

    #MFI
    for lineIndex in range (_NMAXLINES['MFI']):
        guios_MFI[f"INDICATOR_MFI{lineIndex}"].deactivate()
        guios_MFI[f"INDICATOR_MFI{lineIndex}_INTERVALINPUT"].deactivate()

    #TPD
    for lineIndex in range (_NMAXLINES['TPD']):
        guios_TPD[f"INDICATOR_TPD{lineIndex}"].deactivate()
        guios_TPD[f"INDICATOR_TPD{lineIndex}_VIEWLENGTHINPUT"].deactivate()
        guios_TPD[f"INDICATOR_TPD{lineIndex}_INTERVALINPUT"].deactivate()
        guios_TPD[f"INDICATOR_TPD{lineIndex}_MAINTERVALINPUT"].deactivate()

    #WOI
    for lineIndex in range (_NMAXLINES['WOI']):
        guios_WOI[f"INDICATOR_WOI{lineIndex}"].deactivate()
        guios_WOI[f"INDICATOR_WOI{lineIndex}_INTERVALINPUT"].deactivate()

    #NES
    for lineIndex in range (_NMAXLINES['NES']):
        guios_NES[f"INDICATOR_NES{lineIndex}"].deactivate()
        guios_NES[f"INDICATOR_NES{lineIndex}_INTERVALINPUT"].deactivate()
    """
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

"""
#SMA 3
ac_def['SMA_Master'] = False
for lineIndex in range (constants.NLINES_SMA):
    ac_def[f'SMA_{lineIndex}_LineActive'] = False
    ac_def[f'SMA_{lineIndex}_NSamples']   = 10*(lineIndex+1)
#EMA
ac_def['EMA_Master'] = False
for lineIndex in range (constants.NLINES_EMA):
    ac_def[f'EMA_{lineIndex}_LineActive'] = False
    ac_def[f'EMA_{lineIndex}_NSamples']   = 10*(lineIndex+1)
#WMA
ac_def['WMA_Master'] = False
for lineIndex in range (constants.NLINES_WMA):
    ac_def[f'WMA_{lineIndex}_LineActive'] = False
    ac_def[f'WMA_{lineIndex}_NSamples']   = 10*(lineIndex+1)
#PSAR
ac_def['PSAR_Master'] = False
for lineIndex in range (constants.NLINES_PSAR):
    ac_def[f'PSAR_{lineIndex}_LineActive'] = False
    ac_def[f'PSAR_{lineIndex}_AF0']        = 0.020
    ac_def[f'PSAR_{lineIndex}_AF+']        = 0.005*(lineIndex+1)
    ac_def[f'PSAR_{lineIndex}_AFMax']      = 0.200
#BOL
ac_def['BOL_Master'] = False
ac_def['BOL_MAType'] = 'SMA'
for lineIndex in range (constants.NLINES_BOL):
    ac_def[f'BOL_{lineIndex}_LineActive'] = False
    ac_def[f'BOL_{lineIndex}_NSamples']   = 10*(lineIndex+1)
    ac_def[f'BOL_{lineIndex}_BandWidth']  = 2.0
#IVP
ac_def['IVP_Master'] = False
ac_def['IVP_NSamples']    = 500
ac_def['IVP_GammaFactor'] = 0.010
ac_def['IVP_DeltaFactor'] = 1.0
ac_def['IVP_Prominence']  = 0.10
ac_def['IVP_Distance']    = 5
ac_def['IVP_Height']      = 0.50
#SWING
ac_def['SWING_Master'] = False
for lineIndex in range (constants.NLINES_SWING):
    ac_def[f'SWING_{lineIndex}_LineActive'] = False
    ac_def[f'SWING_{lineIndex}_SwingRange'] = 0.005*(lineIndex+1)
#VOL
ac_def['VOL_Master'] = False
for lineIndex in range (constants.NLINES_VOL):
    ac_def[f'VOL_{lineIndex}_LineActive'] = False
    ac_def[f'VOL_{lineIndex}_NSamples']   = 20*(lineIndex+1)
ac_def['VOL_MAType'] = 'SMA'
#NNA
ac_def['NNA_Master'] = False
for lineIndex in range (constants.NLINES_NNA):
    ac_def[f'NNA_{lineIndex}_LineActive'] = False
    ac_def[f'NNA_{lineIndex}_NeuralNetworkCode'] = None
    ac_def[f'NNA_{lineIndex}_Alpha']             = 0.50
    ac_def[f'NNA_{lineIndex}_Beta']              = 2
#MMACD
ac_def['MMACD_Master'] = False
ac_def['MMACD_SignalNSamples'] = 10
for lineIndex in range (constants.NLINES_MMACD):
    ac_def[f'MMACD_MA{lineIndex}_LineActive'] = False
    ac_def[f'MMACD_MA{lineIndex}_NSamples']   = 20*(lineIndex+1)
#DMIxADX
ac_def['DMIxADX_Master'] = False
for lineIndex in range (constants.NLINES_DMIxADX):
    ac_def[f'DMIxADX_{lineIndex}_LineActive'] = False
    ac_def[f'DMIxADX_{lineIndex}_NSamples']   = 10*(lineIndex+1)
#MFI
ac_def['MFI_Master'] = False
for lineIndex in range (constants.NLINES_MFI):
    ac_def[f'MFI_{lineIndex}_LineActive'] = False
    ac_def[f'MFI_{lineIndex}_NSamples']   = 10*(lineIndex+1)
#TPD
ac_def['TPD_Master'] = False
for lineIndex in range (constants.NLINES_TPD):
    ac_def[f'TPD_{lineIndex}_LineActive'] = False
    ac_def[f'TPD_{lineIndex}_ViewLength'] = 10 *(lineIndex+1)
    ac_def[f'TPD_{lineIndex}_NSamples']   = 100*(lineIndex+1)
    ac_def[f'TPD_{lineIndex}_NSamplesMA'] = 20 *(lineIndex+1)
#WOI
ac_def['WOI_Master'] = False
for lineIndex in range (constants.NLINES_WOI):
    ac_def[f'WOI_{lineIndex}_LineActive'] = False
    ac_def[f'WOI_{lineIndex}_NSamples']   = 10*(lineIndex+1)
#NES
ac_def['NES_Master'] = False
for lineIndex in range (constants.NLINES_NES):
    ac_def[f'NES_{lineIndex}_LineActive'] = False
    ac_def[f'NES_{lineIndex}_NSamples']   = 10*(lineIndex+1)
"""


def pg_autotrade_configure_subpage_generate(subPageViewSpaceWidth):
    #[1]: GUIO List
    gList = []

    #[2]: List Appending
    gList.append(({'NAME':               'COLUMNTITLE_INDEX',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'TEXTPACK':           'AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos':    0, 'yPos': -300, 'width': 2225, 'height': 250, 'style': 'styleB', 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'TEXTPACK':           'AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2325, 'yPos': -300, 'width': 2225, 'height': 250, 'style': 'styleB', 'fontSize': 80}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"SMA_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'TEXT':               f'SMA {lIdx}',
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2225, 'height': 250, 'style': 'styleB', 'fontSize': 80}))
        gList.append(({'NAME':               f"SMA_{lIdx}_NSAMPLES",
                       'TYPE':               'textInputBox_typeA',
                       'TEXT':               "",
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2225, 'height': 250, 'style': 'styleA', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_autotrade_configure_subpage_setup(subpage):
    pass
      
"""
if (True): #Configuration/SMA
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SMA"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0,     'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_SMASETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_SMA):
        self.GUIOs[_objName].addGUIO(f"SMA_{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'SMA {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"SMA_{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                   'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_SMA
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/WMA
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WMA"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0,     'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_WMASETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_WMA):
        self.GUIOs[_objName].addGUIO(f"WMA_{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'WMA {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"WMA_{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                   'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_WMA
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/EMA
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_EMA"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0,     'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_EMASETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_EMA):
        self.GUIOs[_objName].addGUIO(f"EMA_{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'EMA {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"EMA_{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                   'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_EMA
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/PSAR
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0,     'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_PSARSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'), 'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_AF0",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1350, 'yPos': yPosPoint0-300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_AF0'),   'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_AF+",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2450, 'yPos': yPosPoint0-300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_AF+'),   'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_AFMAX", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3550, 'yPos': yPosPoint0-300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_AFMAX'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_PSAR):
        self.GUIOs[_objName].addGUIO(f"PSAR_{lineIndex}_LINE",  switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'PSAR {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"PSAR_{lineIndex}_AF0",   textInputBox_typeA, {'groupOrder': 0, 'xPos': 1350, 'yPos': yPosPoint1-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': "",                    'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"PSAR_{lineIndex}_AF+",   textInputBox_typeA, {'groupOrder': 0, 'xPos': 2450, 'yPos': yPosPoint1-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': "",                    'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"PSAR_{lineIndex}_AFMAX", textInputBox_typeA, {'groupOrder': 0, 'xPos': 3550, 'yPos': yPosPoint1-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': "",                    'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_PSAR
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/BOL
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",       passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0,     'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_BOLSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("BOLMATYPETITLETEXT",    textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-350, 'width': 2450, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_BOLMATYPE'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("BOLMATYPESELECTIONBOX", selectionBox_typeB,           {'groupOrder': 2, 'xPos': 2550, 'yPos': yPosPoint0-350, 'width': 2000, 'height': 250, 'style': 'styleA', 'nDisplay': 3, 'fontSize': 80})
    maTypes = {'SMA': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_SMA')},
                'WMA': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_WMA')},
                'EMA': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_EMA')}}
    self.GUIOs[_objName].GUIOs["BOLMATYPESELECTIONBOX"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",     passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-650, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),     'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES",  passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1750, 'yPos': yPosPoint0-650, 'width': 1350, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'),  'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_BANDWIDTH", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3200, 'yPos': yPosPoint0-650, 'width': 1350, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_BANDWIDTH'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-1000
    for lineIndex in range (constants.NLINES_BOL):
        self.GUIOs[_objName].addGUIO(f"BOL_{lineIndex}_LINE",      switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': f'BOL {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"BOL_{lineIndex}_NSAMPLES",  textInputBox_typeA, {'groupOrder': 0, 'xPos': 1750, 'yPos': yPosPoint1-350*lineIndex, 'width': 1350, 'height': 250, 'style': 'styleA', 'text': "",                   'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"BOL_{lineIndex}_BANDWIDTH", textInputBox_typeA, {'groupOrder': 0, 'xPos': 3200, 'yPos': yPosPoint1-350*lineIndex, 'width': 1350, 'height': 250, 'style': 'styleA', 'text': "",                   'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_BOL
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/IVP
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_IVPSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("NSAMPLESTITLETEXT",             textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("NSAMPLESTEXTINPUTBOX",          textInputBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': yPosPoint0- 350, 'width': 2450, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("GAMMAFACTORTITLETEXT",          textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 700, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_GAMMAFACTOR'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("GAMMAFACTORSLIDER",             slider_typeA,       {'groupOrder': 0, 'xPos': 1400, 'yPos': yPosPoint0- 650, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_GammaFactor', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
    self.GUIOs[_objName].addGUIO("GAMMAFACTORDISPLAYTEXT",        textBox_typeA,      {'groupOrder': 0, 'xPos': 3950, 'yPos': yPosPoint0- 700, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("DELTAFACTORTITLETEXT",          textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1050, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_DELTAFACTOR'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("DELTAFACTORSLIDER",             slider_typeA,       {'groupOrder': 0, 'xPos': 1400, 'yPos': yPosPoint0-1000, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_DeltaFactor', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
    self.GUIOs[_objName].addGUIO("DELTAFACTORDISPLAYTEXT",        textBox_typeA,      {'groupOrder': 0, 'xPos': 3950, 'yPos': yPosPoint0-1050, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("PROMINENCETITLETEXT",           textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1400, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_PROMINENCE'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("PROMINENCESLIDER",              slider_typeA,       {'groupOrder': 0, 'xPos': 1400, 'yPos': yPosPoint0-1350, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_Prominence', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
    self.GUIOs[_objName].addGUIO("PROMINENCEDISPLAYTEXT",         textBox_typeA,      {'groupOrder': 0, 'xPos': 3950, 'yPos': yPosPoint0-1400, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("DISTANCETITLETEXT",             textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1750, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_DISTANCE'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("DISTANCESLIDER",                slider_typeA,       {'groupOrder': 0, 'xPos': 1400, 'yPos': yPosPoint0-1700, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_Distance', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
    self.GUIOs[_objName].addGUIO("DISTANCEDISPLAYTEXT",           textBox_typeA,      {'groupOrder': 0, 'xPos': 3950, 'yPos': yPosPoint0-1750, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("HEIGHTTITLETEXT",               textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-2100, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_HEIGHT'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("HEIGHTSLIDER",                  slider_typeA,       {'groupOrder': 0, 'xPos': 1400, 'yPos': yPosPoint0-2050, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_Height', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
    self.GUIOs[_objName].addGUIO("HEIGHTDISPLAYTEXT",             textBox_typeA,      {'groupOrder': 0, 'xPos': 3950, 'yPos': yPosPoint0-2100, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    yPosPoint1 = yPosPoint0-2450
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/SWING
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SWING"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",        passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0,     'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_SWINGSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),      'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_SWINGRANGE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1350, 'yPos': yPosPoint0-300, 'width': 3200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_SWINGRANGE'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_SWING):
        self.GUIOs[_objName].addGUIO(f"SWING_{lineIndex}_LINE",       switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'SWING {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"SWING_{lineIndex}_SWINGRANGE", textInputBox_typeA, {'groupOrder': 0, 'xPos': 1350, 'yPos': yPosPoint1-350*lineIndex, 'width': 3200, 'height': 250, 'style': 'styleA', 'text': "",                   'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_SWING
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/VOL
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_VOLSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("MATYPETITLETEXT",    textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-350, 'width': 2450, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLMATYPE'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("MATYPESELECTIONBOX", selectionBox_typeB, {'groupOrder': 2, 'xPos': 2550, 'yPos': yPosPoint0-350, 'width': 2000, 'height': 250, 'style': 'styleA', 'nDisplay': 3, 'fontSize': 80})
    maTypes = {'SMA': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_SMA')},
                'WMA': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_WMA')},
                'EMA': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_EMA')}}
    self.GUIOs[_objName].GUIOs["MATYPESELECTIONBOX"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-650, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),     'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-650, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'),  'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-1000
    for lineIndex in range (constants.NLINES_VOL):
        self.GUIOs[_objName].addGUIO(f"VOL_{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'VOL {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"VOL_{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                   'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_VOL
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/NNA
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_NNASETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",  passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),             'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NNCODE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint0-300, 'width': 2250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NEURALNETWORKCODE'), 'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_ALPHA",  passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3450, 'yPos': yPosPoint0-300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_ALPHA'),             'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_BETA",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 4050, 'yPos': yPosPoint0-300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_BETA'),              'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_NNA):
        self.GUIOs[_objName].addGUIO(f"NNA_{lineIndex}_LINE",   switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'NNA {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"NNA_{lineIndex}_NNCODE", textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint1-350*lineIndex, 'width': 2250, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"NNA_{lineIndex}_ALPHA",  textInputBox_typeA, {'groupOrder': 0, 'xPos': 3450, 'yPos': yPosPoint1-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"NNA_{lineIndex}_BETA",   textInputBox_typeA, {'groupOrder': 0, 'xPos': 4050, 'yPos': yPosPoint1-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_NNA
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/MMACD
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_MMACDSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("MMACDSIGNALINTERVALTITLETEXT",    textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-350, 'width': 3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_MMACDSIGNALINTERVAL'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("MMACDSIGNALINTERVALTEXTINPUTBOX", textInputBox_typeA, {'groupOrder': 0, 'xPos': 3100, 'yPos': yPosPoint0-350, 'width': 1450, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("INDEX_COLUMNTITLE1",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-700, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("NSAMPLES_COLUMNTITLE1", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint0-700, 'width': 1125, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("INDEX_COLUMNTITLE2",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-700, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("NSAMPLES_COLUMNTITLE2", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3425, 'yPos': yPosPoint0-700, 'width': 1125, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    nMaxLines = constants.NLINES_MMACD
    for lineIndex in range (nMaxLines):
        rowNumber = math.ceil((lineIndex+1)/2)
        if (lineIndex%2 == 0): coordX = 0
        else:                  coordX = 2325
        self.GUIOs[_objName].addGUIO(f"MA{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos': coordX,      'yPos': yPosPoint0-700-rowNumber*350, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'MA {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"MA{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': coordX+1100, 'yPos': yPosPoint0-700-rowNumber*350, 'width': 1125, 'height': 250, 'style': 'styleA', 'text': "",                  'fontSize': 80})
    yPosPoint1 = yPosPoint0-700-math.ceil(nMaxLines/2)*350
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/DMIxADX
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_DMIxADXSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_DMIxADX):
        self.GUIOs[_objName].addGUIO(f"DMIxADX_{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'DMIxADX {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"DMIxADX_{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                       'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_DMIxADX
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/MFI
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_MFISETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_MFI):
        self.GUIOs[_objName].addGUIO(f"MFI_{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'MFI {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"MFI_{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                   'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_MFI
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/TPD
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",        passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_TPDSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),      'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_VIEWLENGTH", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint0-300, 'width':  800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_VIEWLENGTH'), 'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2000, 'yPos': yPosPoint0-300, 'width': 1225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'),   'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLESMA", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3325, 'yPos': yPosPoint0-300, 'width': 1225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLESMA'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_TPD):
        self.GUIOs[_objName].addGUIO(f"TPD_{lineIndex}_LINE",       switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'TPD {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"TPD_{lineIndex}_VIEWLENGTH", textInputBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint1-350*lineIndex, 'width':  800, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"TPD_{lineIndex}_NSAMPLES",   textInputBox_typeA, {'groupOrder': 0, 'xPos': 2000, 'yPos': yPosPoint1-350*lineIndex, 'width': 1225, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"TPD_{lineIndex}_NSAMPLESMA", textInputBox_typeA, {'groupOrder': 0, 'xPos': 3325, 'yPos': yPosPoint1-350*lineIndex, 'width': 1225, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_TPD
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/WOI
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_WOISETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_WOI):
        self.GUIOs[_objName].addGUIO(f"WOI_{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'WOI {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"WOI_{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_WOI
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
if (True): #Configuration/NES
    _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"
    yPosPoint0 = yPos_beg-200
    self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_NESSETUP'), 'fontSize': 80})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    yPosPoint1 = yPosPoint0-650
    for lineIndex in range (constants.NLINES_NES):
        self.GUIOs[_objName].addGUIO(f"NES_{lineIndex}_LINE",     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': f'NES {lineIndex}', 'fontSize': 80})
        self.GUIOs[_objName].addGUIO(f"NES_{lineIndex}_NSAMPLES", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                 'fontSize': 80})
    yPosPoint2 = yPosPoint1-350*constants.NLINES_NES
    self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
"""



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

"""
#MAIN
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_SMA"].setStatus(status      = configuration['SMA_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_EMA"].setStatus(status      = configuration['EMA_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_WMA"].setStatus(status      = configuration['WMA_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_PSAR"].setStatus(status     = configuration['PSAR_Master'],    callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_BOL"].setStatus(status      = configuration['BOL_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_IVP"].setStatus(status      = configuration['IVP_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_SWING"].setStatus(status    = configuration['SWING_Master'],   callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_VOL"].setStatus(status      = configuration['VOL_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_NNA"].setStatus(status      = configuration['NNA_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MMACD"].setStatus(status    = configuration['MMACD_Master'],   callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_DMIxADX"].setStatus(status  = configuration['DMIxADX_Master'], callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MFI"].setStatus(status      = configuration['MFI_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_TPD"].setStatus(status      = configuration['TPD_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_WOI"].setStatus(status      = configuration['WOI_Master'],     callStatusUpdateFunction = False)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_NES"].setStatus(status      = configuration['NES_Master'],     callStatusUpdateFunction = False)

#SMA
for lineIndex in range (constants.NLINES_SMA):
    if f'SMA_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'SMA_{lineIndex}_LineActive']
        nSamples   = configuration[f'SMA_{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 10*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SMA"].GUIOs[f"SMA_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SMA"].GUIOs[f"SMA_{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
#WMA
for lineIndex in range (constants.NLINES_WMA):
    if f'WMA_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'WMA_{lineIndex}_LineActive']
        nSamples   = configuration[f'WMA_{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 10*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WMA"].GUIOs[f"WMA_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WMA"].GUIOs[f"WMA_{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
#EMA
for lineIndex in range (constants.NLINES_EMA):
    if f'EMA_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'EMA_{lineIndex}_LineActive']
        nSamples   = configuration[f'EMA_{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 10*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_EMA"].GUIOs[f"EMA_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_EMA"].GUIOs[f"EMA_{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
#PSAR
for lineIndex in range (constants.NLINES_PSAR):
    if f'PSAR_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'PSAR_{lineIndex}_LineActive']
        af0    = configuration[f'PSAR_{lineIndex}_AF0']
        afPlus = configuration[f'PSAR_{lineIndex}_AF+']
        afMax  = configuration[f'PSAR_{lineIndex}_AFMax']
    else:
        lineActive = False
        af0    = 0.020
        afPlus = 0.005*(lineIndex+1)
        afMax  = 0.200
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs[f"PSAR_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs[f"PSAR_{lineIndex}_AF0"].updateText(text   = f"{af0:.3f}")
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs[f"PSAR_{lineIndex}_AF+"].updateText(text   = f"{afPlus:.3f}")
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs[f"PSAR_{lineIndex}_AFMAX"].updateText(text = f"{afMax:.3f}")
#BOL
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs["BOLMATYPESELECTIONBOX"].setSelected(itemKey = configuration['BOL_MAType'], callSelectionUpdateFunction = False)
for lineIndex in range (constants.NLINES_BOL):
    if f'BOL_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'BOL_{lineIndex}_LineActive']
        nSamples  = configuration[f'BOL_{lineIndex}_NSamples']
        bandwidth = configuration[f'BOL_{lineIndex}_BandWidth']
    else:
        lineActive = False
        nSamples  = 10*(lineIndex+1)
        bandwidth = 2.0
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs[f"BOL_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs[f"BOL_{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs[f"BOL_{lineIndex}_BANDWIDTH"].updateText(text = f"{bandwidth:.1f}")
#IVP
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["NSAMPLESTEXTINPUTBOX"].updateText(text = str(configuration['IVP_NSamples']))
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["GAMMAFACTORSLIDER"].setSliderValue(newValue = (configuration['IVP_GammaFactor']-0.005)*(100/0.095))
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["GAMMAFACTORDISPLAYTEXT"].updateText(text = f"{configuration['IVP_GammaFactor']*100:.1f} %")
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DELTAFACTORSLIDER"].setSliderValue(newValue = (configuration['IVP_DeltaFactor']-0.1)*(100/9.9))
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DELTAFACTORDISPLAYTEXT"].updateText(text = f"{int(configuration['IVP_DeltaFactor']*100)} %")
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["PROMINENCESLIDER"].setSliderValue(newValue = (configuration['IVP_Prominence']-0.01)*(100/0.99))
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["PROMINENCEDISPLAYTEXT"].updateText(text = f"{int(configuration['IVP_Prominence']*100)} %")
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DISTANCESLIDER"].setSliderValue(newValue = (configuration['IVP_Distance']-1)*(100/99))
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DISTANCEDISPLAYTEXT"].updateText(text = f"{int(configuration['IVP_Distance'])}")
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["HEIGHTSLIDER"].setSliderValue(newValue = configuration['IVP_Height']*100)
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["HEIGHTDISPLAYTEXT"].updateText(text = f"{int(configuration['IVP_Height']*100)} %")
#SWING
for lineIndex in range (constants.NLINES_SWING):
    if f'SWING_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'SWING_{lineIndex}_LineActive']
        swingRange = configuration[f'SWING_{lineIndex}_SwingRange']
    else:
        lineActive = False
        swingRange = 0.005*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SWING"].GUIOs[f"SWING_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SWING"].GUIOs[f"SWING_{lineIndex}_SWINGRANGE"].updateText(text = f"{swingRange:.4f}")
#VOL
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs["MATYPESELECTIONBOX"].setSelected(itemKey = configuration['VOL_MAType'], callSelectionUpdateFunction = False)
for lineIndex in range (constants.NLINES_VOL):
    if f'VOL_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'VOL_{lineIndex}_LineActive']
        nSamples   = configuration[f'VOL_{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 20*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs[f"VOL_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs[f"VOL_{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
#NNA
for lineIndex in range (constants.NLINES_NNA):
    if f'NNA_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'NNA_{lineIndex}_LineActive']
        nnCode     = configuration[f'NNA_{lineIndex}_NeuralNetworkCode']
        alpha      = configuration[f'NNA_{lineIndex}_Alpha']
        beta       = configuration[f'NNA_{lineIndex}_Beta']
    else:
        lineActive = False
        nnCode     = None
        alpha      = 0.50
        beta       = 2
    nnCode_str = "" if nnCode is None else f"{nnCode}"
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_LINE"].setStatus(status  = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_NNCODE"].updateText(text = nnCode_str)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_ALPHA"].updateText(text  = f"{alpha:.2f}")
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_BETA"].updateText(text   = f"{beta}")
#MMACD
self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs["MMACDSIGNALINTERVALTEXTINPUTBOX"].updateText(text = "{:d}".format(configuration['MMACD_SignalNSamples']))
for lineIndex in range (constants.NLINES_MMACD):
    if f'MMACD_MA{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'MMACD_MA{lineIndex}_LineActive']
        nSamples   = configuration[f'MMACD_MA{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 20*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs[f"MA{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs[f"MA{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
#DMIxADX
for lineIndex in range (constants.NLINES_DMIxADX):
    if f'DMIxADX_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'DMIxADX_{lineIndex}_LineActive']
        nSamples   = configuration[f'DMIxADX_{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 10*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"].GUIOs[f"DMIxADX_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"].GUIOs[f"DMIxADX_{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
#MFI
for lineIndex in range (constants.NLINES_MFI):
    if f'MFI_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'MFI_{lineIndex}_LineActive']
        nSamples   = configuration[f'MFI_{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 10*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"].GUIOs[f"MFI_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"].GUIOs[f"MFI_{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
#TPD
for lineIndex in range (constants.NLINES_TPD):
    if f'TPD_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'TPD_{lineIndex}_LineActive']
        viewLength = configuration[f'TPD_{lineIndex}_ViewLength']
        nSamples   = configuration[f'TPD_{lineIndex}_NSamples']
        nSamplesMA = configuration[f'TPD_{lineIndex}_NSamplesMA']
    else:
        lineActive = False
        viewLength = 15  *(lineIndex+1)
        nSamples   = 1000*(lineIndex+1)
        nSamplesMA = 20  *(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_VIEWLENGTH"].updateText(text = f"{viewLength}")
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_NSAMPLES"].updateText(text   = f"{nSamples}")
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_NSAMPLESMA"].updateText(text = f"{nSamplesMA}")
#WOI
for lineIndex in range (constants.NLINES_WOI):
    if f'WOI_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'WOI_{lineIndex}_LineActive']
        nSamples   = configuration[f'WOI_{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 10*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs[f"WOI_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs[f"WOI_{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
#NES
for lineIndex in range (constants.NLINES_NES):
    if f'NES_{lineIndex}_LineActive' in configuration:
        lineActive = configuration[f'NES_{lineIndex}_LineActive']
        nSamples   = configuration[f'NES_{lineIndex}_NSamples']
    else:
        lineActive = False
        nSamples   = 10*(lineIndex+1)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs[f"NES_{lineIndex}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
    self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs[f"NES_{lineIndex}_NSAMPLES"].updateText(text = f"{nSamples}")
"""

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

"""
#SMA
configuration['SMA_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_SMA"].getStatus()
for lineIndex in range (constants.NLINES_SMA):
    configuration[f'SMA_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SMA"].GUIOs[f"SMA_{lineIndex}_LINE"].getStatus()
    configuration[f'SMA_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SMA"].GUIOs[f"SMA_{lineIndex}_NSAMPLES"].getText())
#EMA
configuration['EMA_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_EMA"].getStatus()
for lineIndex in range (constants.NLINES_EMA):
    configuration[f'EMA_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_EMA"].GUIOs[f"EMA_{lineIndex}_LINE"].getStatus()
    configuration[f'EMA_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_EMA"].GUIOs[f"EMA_{lineIndex}_NSAMPLES"].getText())
#WMA
configuration['WMA_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_WMA"].getStatus()
for lineIndex in range (constants.NLINES_WMA):
    configuration[f'WMA_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WMA"].GUIOs[f"WMA_{lineIndex}_LINE"].getStatus()
    configuration[f'WMA_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WMA"].GUIOs[f"WMA_{lineIndex}_NSAMPLES"].getText())
#PSAR
configuration['PSAR_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_PSAR"].getStatus()
for lineIndex in range (constants.NLINES_PSAR):
    configuration[f'PSAR_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs[f"PSAR_{lineIndex}_LINE"].getStatus()
    configuration[f'PSAR_{lineIndex}_AF0']   = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs[f"PSAR_{lineIndex}_AF0"].getText()),   3)
    configuration[f'PSAR_{lineIndex}_AF+']   = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs[f"PSAR_{lineIndex}_AF+"].getText()),   3)
    configuration[f'PSAR_{lineIndex}_AFMax'] = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs[f"PSAR_{lineIndex}_AFMAX"].getText()), 3)
#BOL
configuration['BOL_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_BOL"].getStatus()
configuration['BOL_MAType'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs["BOLMATYPESELECTIONBOX"].getSelected()
for lineIndex in range (constants.NLINES_BOL):
    configuration[f'BOL_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs[f"BOL_{lineIndex}_LINE"].getStatus()
    configuration[f'BOL_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs[f"BOL_{lineIndex}_NSAMPLES"].getText())
    configuration[f'BOL_{lineIndex}_BandWidth']  = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs[f"BOL_{lineIndex}_BANDWIDTH"].getText()), 1)
#IVP
configuration['IVP_Master']      = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_IVP"].getStatus()
configuration['IVP_NSamples']    = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["NSAMPLESTEXTINPUTBOX"].getText())
configuration['IVP_GammaFactor'] = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["GAMMAFACTORSLIDER"].getSliderValue()/100*(0.095)+0.005), 3)
configuration['IVP_DeltaFactor'] = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DELTAFACTORSLIDER"].getSliderValue()/100*(9.9)  +0.1),   1)
configuration['IVP_Prominence']  = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["PROMINENCESLIDER"].getSliderValue()/100*(0.99)  +0.01),  2)
configuration['IVP_Distance']    = int(round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DISTANCESLIDER"].getSliderValue()/100*(99)  +1)))
configuration['IVP_Height']      = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["HEIGHTSLIDER"].getSliderValue()/100), 2)
#SWING
configuration['SWING_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_SWING"].getStatus()
for lineIndex in range (constants.NLINES_SWING):
    configuration[f'SWING_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SWING"].GUIOs[f"SWING_{lineIndex}_LINE"].getStatus()
    configuration[f'SWING_{lineIndex}_SwingRange'] = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SWING"].GUIOs[f"SWING_{lineIndex}_SWINGRANGE"].getText()), 4)
#VOL
configuration['VOL_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_VOL"].getStatus()
configuration['VOL_MAType'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs["MATYPESELECTIONBOX"].getSelected()
for lineIndex in range (constants.NLINES_VOL):
    configuration[f'VOL_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs[f"VOL_{lineIndex}_LINE"].getStatus()
    configuration[f'VOL_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs[f"VOL_{lineIndex}_NSAMPLES"].getText())
#NNA
configuration['NNA_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_NNA"].getStatus()
for lineIndex in range (constants.NLINES_NNA):
    configuration[f'NNA_{lineIndex}_LineActive']        = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_LINE"].getStatus()
    nnCode_input = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_NNCODE"].getText().strip()
    configuration[f'NNA_{lineIndex}_NeuralNetworkCode'] = None if not nnCode_input else nnCode_input
    configuration[f'NNA_{lineIndex}_Alpha']             = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_ALPHA"].getText()), 2)
    configuration[f'NNA_{lineIndex}_Beta']              = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NNA"].GUIOs[f"NNA_{lineIndex}_BETA"].getText())
#MMACD
configuration['MMACD_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MMACD"].getStatus()
configuration['MMACD_SignalNSamples'] = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs["MMACDSIGNALINTERVALTEXTINPUTBOX"].getText())
for lineIndex in range (constants.NLINES_MMACD):
    configuration[f'MMACD_MA{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs[f"MA{lineIndex}_LINE"].getStatus()
    configuration[f'MMACD_MA{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACD"].GUIOs[f"MA{lineIndex}_NSAMPLES"].getText())
#DMIxADX
configuration['DMIxADX_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_DMIxADX"].getStatus()
for lineIndex in range (constants.NLINES_DMIxADX):
    configuration[f'DMIxADX_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"].GUIOs[f"DMIxADX_{lineIndex}_LINE"].getStatus()
    configuration[f'DMIxADX_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"].GUIOs[f"DMIxADX_{lineIndex}_NSAMPLES"].getText())
#MFI
configuration['MFI_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MFI"].getStatus()
for lineIndex in range (constants.NLINES_MFI):
    configuration[f'MFI_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"].GUIOs[f"MFI_{lineIndex}_LINE"].getStatus()
    configuration[f'MFI_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"].GUIOs[f"MFI_{lineIndex}_NSAMPLES"].getText())
#TPD
configuration['TPD_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_TPD"].getStatus()
for lineIndex in range (constants.NLINES_TPD):
    configuration[f'TPD_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_LINE"].getStatus()
    configuration[f'TPD_{lineIndex}_ViewLength'] = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_VIEWLENGTH"].getText())
    configuration[f'TPD_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_NSAMPLES"].getText())
    configuration[f'TPD_{lineIndex}_NSamplesMA'] = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_TPD"].GUIOs[f"TPD_{lineIndex}_NSAMPLESMA"].getText())
#WOI
configuration['WOI_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_WOI"].getStatus()
for lineIndex in range (constants.NLINES_WOI):
    configuration[f'WOI_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs[f"WOI_{lineIndex}_LINE"].getStatus()
    configuration[f'WOI_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs[f"WOI_{lineIndex}_NSAMPLES"].getText())
#NES
configuration['NES_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_NES"].getStatus()
for lineIndex in range (constants.NLINES_NES):
    configuration[f'NES_{lineIndex}_LineActive'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs[f"NES_{lineIndex}_LINE"].getStatus()
    configuration[f'NES_{lineIndex}_NSamples']   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs[f"NES_{lineIndex}_NSAMPLES"].getText())
"""
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
                   'groupOrder': 0, 'xPos': 0, 'yPos': -300, 'width': 2525, 'height': 250, 'style': 'styleB', 'fontSize': 80}))
    gList.append(({'NAME':               'COLUMNTITLE_NSAMPLES',
                   'TYPE':               'passiveGraphics_wrapperTypeC',
                   'TEXTPACK':           'AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES',
                   'PAGEOBJECTFUNCTION': None,
                   'groupOrder': 0, 'xPos': 2625, 'yPos': -300, 'width': 2525, 'height': 250, 'style': 'styleB', 'fontSize': 80}))
    yPosPoint1 = -300
    for lIdx in range (NMAXLINES):
        gList.append(({'NAME':               f"SMA_{lIdx}_LINE",
                       'TYPE':               'switch_typeC',
                       'TEXT':               f'SMA {lIdx}',
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2525, 'height': 250, 'style': 'styleB', 'fontSize': 80}))
        gList.append(({'NAME':               f"SMA_{lIdx}_NSAMPLES",
                       'TYPE':               'textInputBox_typeA',
                       'TEXT':               '-',
                       'TEXTPACK':           None,
                       'PAGEOBJECTFUNCTION': None,
                       'groupOrder': 0, 'xPos': 2625, 'yPos': yPosPoint1-350*(lIdx+1), 'width': 2525, 'height': 250, 'style': 'styleA', 'fontSize': 80}))

    #[3]: Return GUIO Generation List
    return gList



def pg_simulation_result_configure_subpage_setup(subpage):
    for lIdx in range (NMAXLINES):
        subpage.GUIOs[f"SMA_{lIdx}_LINE"].deactivate()

"""
if (True): #Configuration/SMA
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SMA"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0,     'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_SMASETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_SMA):
        spo.addGUIO(f"SMA_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'SMA {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"SMA_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"SMA_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_SMA
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/WMA
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_WMA"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0,     'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_WMASETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_WMA):
        spo.addGUIO(f"WMA_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'WMA {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"WMA_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"WMA_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_WMA
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/EMA
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_EMA"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0,     'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_EMASETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_EMA):
        spo.addGUIO(f"EMA_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'EMA {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"EMA_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"EMA_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_EMA
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/PSAR
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_PSAR"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0,     'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_PSARSETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'), 'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_AF0",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint0-300, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_AF0'),   'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_AF+",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2650, 'yPos': _yPosPoint0-300, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_AF+'),   'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_AFMAX", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3950, 'yPos': _yPosPoint0-300, 'width': 1200, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_AFMAX'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_PSAR):
        spo.addGUIO(f"PSAR_{lineIndex}_LINE",  switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'PSAR {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"PSAR_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"PSAR_{lineIndex}_AF0",   textBox_typeA, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': "-",                   'fontSize': 80})
        spo.addGUIO(f"PSAR_{lineIndex}_AF+",   textBox_typeA, {'groupOrder': 0, 'xPos': 2650, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': "-",                   'fontSize': 80})
        spo.addGUIO(f"PSAR_{lineIndex}_AFMAX", textBox_typeA, {'groupOrder': 0, 'xPos': 3950, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': "-",                   'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_PSAR
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/BOL
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_BOL"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",       passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0,     'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_BOLSETUP'), 'fontSize': 80})
    spo.addGUIO("BOLMATYPETITLETEXT",    textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-350, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_BOLMATYPE'), 'fontSize': 80})
    spo.addGUIO("BOLMATYPEDISPLAYTEXT",  textBox_typeA,                {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-350, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                          'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",     passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-650, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),     'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES",  passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1750, 'yPos': _yPosPoint0-650, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'),  'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_BANDWIDTH", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3500, 'yPos': _yPosPoint0-650, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_BANDWIDTH'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-1000
    for lineIndex in range (constants.NLINES_BOL):
        spo.addGUIO(f"BOL_{lineIndex}_LINE",      switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': f'BOL {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"BOL_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"BOL_{lineIndex}_NSAMPLES",  textBox_typeA, {'groupOrder': 0, 'xPos': 1750, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1650, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
        spo.addGUIO(f"BOL_{lineIndex}_BANDWIDTH", textBox_typeA, {'groupOrder': 0, 'xPos': 3500, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1650, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_BOL
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/IVP
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_IVP"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_IVPSETUP'), 'fontSize': 80})
    spo.addGUIO("NSAMPLESTITLETEXT",      textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0- 350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80})
    spo.addGUIO("NSAMPLESDISPLAYTEXT",    textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0- 350, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    spo.addGUIO("GAMMAFACTORTITLETEXT",   textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0- 700, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_GAMMAFACTOR'), 'fontSize': 80})
    spo.addGUIO("GAMMAFACTORDISPLAYTEXT", textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0- 700, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    spo.addGUIO("DELTAFACTORTITLETEXT",   textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-1050, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_DELTAFACTOR'), 'fontSize': 80})
    spo.addGUIO("DELTAFACTORDISPLAYTEXT", textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0-1050, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    spo.addGUIO("PROMINENCETITLETEXT",    textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-1400, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_PROMINENCE'),  'fontSize': 80})
    spo.addGUIO("PROMINENCEDISPLAYTEXT",  textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0-1400, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    spo.addGUIO("DISTANCETITLETEXT",      textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-1750, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_DISTANCE'),    'fontSize': 80})
    spo.addGUIO("DISTANCEDISPLAYTEXT",    textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0-1750, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    spo.addGUIO("HEIGHTTITLETEXT",        textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-2100, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_HEIGHT'),      'fontSize': 80})
    spo.addGUIO("HEIGHTDISPLAYTEXT",      textBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': _yPosPoint0-2100, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    _yPosPoint1 = _yPosPoint0-2450
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint1, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/SWING
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SWING"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",        passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0,     'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_SWINGSETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),      'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_SWINGRANGE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint0-300, 'width': 3800, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_SWINGRANGE'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_SWING):
        spo.addGUIO(f"SWING_{lineIndex}_LINE",       switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'SWING {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"SWING_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"SWING_{lineIndex}_SWINGRANGE", textBox_typeA, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint1-350*lineIndex, 'width': 3800, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_SWING
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/VOL
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_VOL"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_VOLSETUP'), 'fontSize': 80})
    spo.addGUIO("MATYPETITLETEXT",      textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-350, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_VOLMATYPE'),  'fontSize': 80})
    spo.addGUIO("MATYPEDISPLAYTEXT",    textBox_typeA,                {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-350, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                           'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-650, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),      'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-650, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'),   'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-1000
    for lineIndex in range (constants.NLINES_VOL):
        spo.addGUIO(f"VOL_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'VOL {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"VOL_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"VOL_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_VOL
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/NNA
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NNA"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",        passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_NNASETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),             'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_SWINGRANGE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint0-300, 'width': 2600, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NEURALNETWORKCODE'), 'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_ALPHA",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 4050, 'yPos': _yPosPoint0-300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_ALPHA'),             'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_BETA",       passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 4650, 'yPos': _yPosPoint0-300, 'width':  500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_BETA'),              'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_NNA):
        spo.addGUIO(f"NNA_{lineIndex}_LINE",   switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': f'NNA {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"NNA_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"NNA_{lineIndex}_NNCODE", textBox_typeA, {'groupOrder': 0, 'xPos': 1350, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2600, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
        spo.addGUIO(f"NNA_{lineIndex}_ALPHA",  textBox_typeA, {'groupOrder': 0, 'xPos': 4050, 'yPos': _yPosPoint1-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
        spo.addGUIO(f"NNA_{lineIndex}_BETA",   textBox_typeA, {'groupOrder': 0, 'xPos': 4650, 'yPos': _yPosPoint1-350*lineIndex, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_NNA
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/MMACD
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MMACD"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_MMACDSETUP'), 'fontSize': 80})
    spo.addGUIO("MMACDSIGNALINTERVALTITLETEXT",   textBox_typeA,       {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-350, 'width': 3050, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_MMACDSIGNALINTERVAL'), 'fontSize': 80})
    spo.addGUIO("MMACDSIGNALINTERVALDISPLAYTEXT", textBox_typeA,       {'groupOrder': 0, 'xPos': 3150, 'yPos': _yPosPoint0-350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': "-",                                                                                                    'fontSize': 80})
    spo.addGUIO("INDEX_COLUMNTITLE1",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-700, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("NSAMPLES_COLUMNTITLE1", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1200, 'yPos': _yPosPoint0-700, 'width': 1325, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("INDEX_COLUMNTITLE2",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-700, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("NSAMPLES_COLUMNTITLE2", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3825, 'yPos': _yPosPoint0-700, 'width': 1325, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    _nMaxLines = constants.NLINES_MMACD
    for lineIndex in range (_nMaxLines):
        rowNumber = math.ceil((lineIndex+1)/2)
        if (lineIndex%2 == 0): coordX = 0
        else:                  coordX = 2625
        spo.addGUIO(f"MA{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos': coordX,      'yPos': _yPosPoint0-700-rowNumber*350, 'width': 1100, 'height': 250, 'style': 'styleB', 'text': f'MA {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"MA{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"MA{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': coordX+1200, 'yPos': _yPosPoint0-700-rowNumber*350, 'width': 1325, 'height': 250, 'style': 'styleA', 'text': "-",                 'fontSize': 80})
    _yPosPoint1 = _yPosPoint0-700-math.ceil(_nMaxLines/2)*350
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint1-350, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/DMIxADX
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_DMIxADX"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_DMIxADXSETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_DMIxADX):
        spo.addGUIO(f"DMIxADX_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'DMIxADX {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"DMIxADX_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"DMIxADX_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                      'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_DMIxADX
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/MFI
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MFI"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_MFISETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_MFI):
        spo.addGUIO(f"MFI_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'MFI {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"MFI_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"MFI_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_MFI
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/TPD
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_TPD"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_TPDSETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_VIEWLENGTH", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': _yPosPoint0-300, 'width': 1050, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_VIEWLENGTH'), 'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2250, 'yPos': _yPosPoint0-300, 'width': 1400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'),   'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLESMA", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3750, 'yPos': _yPosPoint0-300, 'width': 1400, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLESMA'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_TPD):
        spo.addGUIO(f"TPD_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': f'TPD {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"TPD_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"TPD_{lineIndex}_VIEWLENGTH", textBox_typeA, {'groupOrder': 0, 'xPos': 1100, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1050, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
        spo.addGUIO(f"TPD_{lineIndex}_NSAMPLES",   textBox_typeA, {'groupOrder': 0, 'xPos': 2250, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1400, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
        spo.addGUIO(f"TPD_{lineIndex}_NSAMPLESMA", textBox_typeA, {'groupOrder': 0, 'xPos': 3750, 'yPos': _yPosPoint1-350*lineIndex, 'width': 1400, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_TPD
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/WOI
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_WOI"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_WOISETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_WOI):
        spo.addGUIO(f"WOI_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'WOI {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"WOI_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"WOI_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_WOI
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
if (True): #Configuration/NES
    spo = self.GUIOs["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NES"]
    _yPosPoint0 = _yPos_beg-200
    spo.addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint0, 'width': _subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:BLOCKSUBTITLE_SIMULATIONDETAIL_CONFIGURATIONS_NESSETUP'), 'fontSize': 80})
    spo.addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
    spo.addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint0-300, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
    _yPosPoint1 = _yPosPoint0-650
    for lineIndex in range (constants.NLINES_NES):
        spo.addGUIO(f"NES_{lineIndex}_LINE",     switch_typeC,  {'groupOrder': 0, 'xPos':    0, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleB', 'text': f'NES {lineIndex}', 'fontSize': 80})
        spo.GUIOs[f"NES_{lineIndex}_LINE"].deactivate()
        spo.addGUIO(f"NES_{lineIndex}_NSAMPLES", textBox_typeA, {'groupOrder': 0, 'xPos': 2625, 'yPos': _yPosPoint1-350*lineIndex, 'width': 2525, 'height': 250, 'style': 'styleA', 'text': "-",                  'fontSize': 80})
    _yPosPoint2 = _yPosPoint1-350*constants.NLINES_NES
    spo.addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': _yPosPoint2, 'width': _subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_SIMULATIONDETAIL_CONFIGURATIONS_MOVETOSUBPAGE']})
"""

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

"""
#---[2-1]: Simulation Not Selected
if any(val is None for val in (sim, cac, iID)):
    #MAIN
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MAIN"].GUIOs
    sp_GUIOs["INDICATORMASTERSWITCH_SMA"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_EMA"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_WMA"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_PSAR"].setStatus(status    = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_BOL"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_IVP"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_SWING"].setStatus(status   = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_VOL"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_NNA"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_MMACD"].setStatus(status   = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_DMIxADX"].setStatus(status = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_MFI"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_TPD"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_WOI"].setStatus(status     = False, callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_NES"].setStatus(status     = False, callStatusUpdateFunction = False)
    
    #SMA
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SMA"].GUIOs
    for lIdx in range (constants.NLINES_SMA):
        sp_GUIOs[f"SMA_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"SMA_{lIdx}_NSAMPLES"].updateText(text = "-")
    #WMA
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_WMA"].GUIOs
    for lIdx in range (constants.NLINES_WMA):
        sp_GUIOs[f"WMA_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"WMA_{lIdx}_NSAMPLES"].updateText(text = "-")
    #EMA
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_EMA"].GUIOs
    for lIdx in range (constants.NLINES_EMA):
        sp_GUIOs[f"EMA_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"EMA_{lIdx}_NSAMPLES"].updateText(text = "-")
    #PSAR
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_PSAR"].GUIOs
    for lIdx in range (constants.NLINES_PSAR):
        sp_GUIOs[f"PSAR_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"PSAR_{lIdx}_AF0"].updateText(text   = "-")
        sp_GUIOs[f"PSAR_{lIdx}_AF+"].updateText(text   = "-")
        sp_GUIOs[f"PSAR_{lIdx}_AFMAX"].updateText(text = "-")
    #BOL
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_BOL"].GUIOs
    sp_GUIOs["BOLMATYPEDISPLAYTEXT"].updateText(text = "-")
    for lIdx in range (constants.NLINES_BOL):
        sp_GUIOs[f"BOL_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"BOL_{lIdx}_NSAMPLES"].updateText(text  = "-")
        sp_GUIOs[f"BOL_{lIdx}_BANDWIDTH"].updateText(text = "-")
    #IVP
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_IVP"].GUIOs
    sp_GUIOs["NSAMPLESDISPLAYTEXT"].updateText(text    = "-")
    sp_GUIOs["GAMMAFACTORDISPLAYTEXT"].updateText(text = "-")
    sp_GUIOs["DELTAFACTORDISPLAYTEXT"].updateText(text = "-")
    sp_GUIOs["PROMINENCEDISPLAYTEXT"].updateText(text  = "-")
    sp_GUIOs["DISTANCEDISPLAYTEXT"].updateText(text    = "-")
    sp_GUIOs["HEIGHTDISPLAYTEXT"].updateText(text      = "-")
    #SWING
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SWING"].GUIOs
    for lIdx in range (constants.NLINES_SWING):
        sp_GUIOs[f"SWING_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"SWING_{lIdx}_SWINGRANGE"].updateText(text = "-")
    #VOL
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_VOL"].GUIOs
    sp_GUIOs["MATYPEDISPLAYTEXT"].updateText(text = "-")
    for lIdx in range (constants.NLINES_VOL):
        sp_GUIOs[f"VOL_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"VOL_{lIdx}_NSAMPLES"].updateText(text = "-")
    #NNA
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NNA"].GUIOs
    for lIdx in range (constants.NLINES_NNA):
        sp_GUIOs[f"NNA_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"NNA_{lIdx}_NNCODE"].updateText(text = "-")
        sp_GUIOs[f"NNA_{lIdx}_ALPHA"].updateText(text  = "-")
        sp_GUIOs[f"NNA_{lIdx}_BETA"].updateText(text   = "-")
    #MMACD
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MMACD"].GUIOs
    sp_GUIOs["MMACDSIGNALINTERVALDISPLAYTEXT"].updateText(text = "-")
    for lIdx in range (constants.NLINES_MMACD):
        sp_GUIOs[f"MA{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"MA{lIdx}_NSAMPLES"].updateText(text = "-")
    #DMIxADX
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_DMIxADX"].GUIOs
    for lIdx in range (constants.NLINES_DMIxADX):
        sp_GUIOs[f"DMIxADX_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"DMIxADX_{lIdx}_NSAMPLES"].updateText(text = "-")
    #MFI
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MFI"].GUIOs
    for lIdx in range (constants.NLINES_MFI):
        sp_GUIOs[f"MFI_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"MFI_{lIdx}_NSAMPLES"].updateText(text = "-")
    #TPD
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_TPD"].GUIOs
    for lIdx in range (constants.NLINES_TPD):
        sp_GUIOs[f"TPD_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"TPD_{lIdx}_VIEWLENGTH"].updateText(text = "-")
        sp_GUIOs[f"TPD_{lIdx}_NSAMPLES"].updateText(text   = "-")
        sp_GUIOs[f"TPD_{lIdx}_NSAMPLESMA"].updateText(text = "-")
    #WOI
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_WOI"].GUIOs
    for lIdx in range (constants.NLINES_WOI):
        sp_GUIOs[f"WOI_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"WOI_{lIdx}_NSAMPLES"].updateText(text = "-")
    #NES
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NES"].GUIOs
    for lIdx in range (constants.NLINES_NES):
        sp_GUIOs[f"NES_{lIdx}_LINE"].setStatus(status = False, callStatusUpdateFunction = False)
        sp_GUIOs[f"NES_{lIdx}_NSAMPLES"].updateText(text = "-")

#---[2-2]: Simulation Selected
else:
    cac_iID = cac[iID]
    #MAIN
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MAIN"].GUIOs
    sp_GUIOs["INDICATORMASTERSWITCH_SMA"].setStatus(status     = cac_iID['SMA_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_EMA"].setStatus(status     = cac_iID['EMA_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_WMA"].setStatus(status     = cac_iID['WMA_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_PSAR"].setStatus(status    = cac_iID['PSAR_Master'],    callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_BOL"].setStatus(status     = cac_iID['BOL_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_IVP"].setStatus(status     = cac_iID['IVP_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_SWING"].setStatus(status   = cac_iID['SWING_Master'],   callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_VOL"].setStatus(status     = cac_iID['VOL_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_NNA"].setStatus(status     = cac_iID['NNA_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_MMACD"].setStatus(status   = cac_iID['MMACD_Master'],   callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_DMIxADX"].setStatus(status = cac_iID['DMIxADX_Master'], callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_MFI"].setStatus(status     = cac_iID['MFI_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_TPD"].setStatus(status     = cac_iID['TPD_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_WOI"].setStatus(status     = cac_iID['WOI_Master'],     callStatusUpdateFunction = False)
    sp_GUIOs["INDICATORMASTERSWITCH_NES"].setStatus(status     = cac_iID['NES_Master'],     callStatusUpdateFunction = False)
    
    #SMA
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SMA"].GUIOs
    for lIdx in range (constants.NLINES_SMA):
        lineActive = cac_iID.get(f'SMA_{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'SMA_{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"SMA_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"SMA_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    #WMA
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_WMA"].GUIOs
    for lIdx in range (constants.NLINES_WMA):
        lineActive = cac_iID.get(f'WMA_{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'WMA_{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"WMA_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"WMA_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    #EMA
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_EMA"].GUIOs
    for lIdx in range (constants.NLINES_EMA):
        lineActive = cac_iID.get(f'EMA_{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'EMA_{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"EMA_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"EMA_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    #PSAR
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_PSAR"].GUIOs
    for lIdx in range (constants.NLINES_PSAR):
        lineActive = cac_iID.get(f'PSAR_{lIdx}_LineActive', False)
        if lineActive: 
            af0_str    = f"{cac_iID[f'PSAR_{lIdx}_AF0']:.3f}"
            afPlus_str = f"{cac_iID[f'PSAR_{lIdx}_AF+']:.3f}"
            afMax_str  = f"{cac_iID[f'PSAR_{lIdx}_AFMax']:.3f}"
        else:          
            af0_str    = "-"
            afPlus_str = "-"
            afMax_str  = "-"
        sp_GUIOs[f"PSAR_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"PSAR_{lIdx}_AF0"].updateText(text   = af0_str)
        sp_GUIOs[f"PSAR_{lIdx}_AF+"].updateText(text   = afPlus_str)
        sp_GUIOs[f"PSAR_{lIdx}_AFMAX"].updateText(text = afMax_str)
    #BOL
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_BOL"].GUIOs
    sp_GUIOs["BOLMATYPEDISPLAYTEXT"].updateText(text = self.visualManager.getTextPack('SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_{:s}'.format(cac_iID['BOL_MAType'])))
    for lIdx in range (constants.NLINES_BOL):

        lineActive = cac_iID.get(f'BOL_{lIdx}_LineActive', False)
        if lineActive: 
            nSamples_str  = f"{cac_iID[f'BOL_{lIdx}_NSamples']}"
            bandWidth_str = f"{cac_iID[f'BOL_{lIdx}_BandWidth']:.1f}"
        else:          
            nSamples_str  = "-"
            bandWidth_str = "-"
        sp_GUIOs[f"BOL_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"BOL_{lIdx}_NSAMPLES"].updateText(text  = nSamples_str)
        sp_GUIOs[f"BOL_{lIdx}_BANDWIDTH"].updateText(text = bandWidth_str)
    #IVP
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_IVP"].GUIOs
    sp_GUIOs["NSAMPLESDISPLAYTEXT"].updateText(text = f"{cac_iID['IVP_NSamples']}")
    sp_GUIOs["GAMMAFACTORDISPLAYTEXT"].updateText(text = f"{cac_iID['IVP_GammaFactor']*100:.1f} %")
    sp_GUIOs["DELTAFACTORDISPLAYTEXT"].updateText(text = f"{cac_iID['IVP_DeltaFactor']*100:.0f} %")
    sp_GUIOs["PROMINENCEDISPLAYTEXT"].updateText(text  = f"{cac_iID['IVP_Prominence']*100:.0f} %")
    sp_GUIOs["DISTANCEDISPLAYTEXT"].updateText(text    = f"{cac_iID['IVP_Distance']}")
    sp_GUIOs["HEIGHTDISPLAYTEXT"].updateText(text      = f"{cac_iID['IVP_Height']*100:.0f} %")
    #SWING
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_SWING"].GUIOs
    for lIdx in range (constants.NLINES_SWING):
        lineActive = cac_iID.get(f'SWING_{lIdx}_LineActive', False)
        if lineActive: 
            swingRange_str = f"{cac_iID[f'SWING_{lIdx}_SwingRange']:.4f}"
        else:          
            swingRange_str = "-"
        sp_GUIOs[f"SWING_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"SWING_{lIdx}_SWINGRANGE"].updateText(text = swingRange_str)
    #VOL
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_VOL"].GUIOs
    maType = cac_iID['VOL_MAType']
    sp_GUIOs["MATYPEDISPLAYTEXT"].updateText(text = self.visualManager.getTextPack(f'SIMULATIONRESULT:SIMULATIONDETAIL_CONFIGURATIONS_{maType}'))
    for lIdx in range (constants.NLINES_VOL):
        lineActive = cac_iID.get(f'VOL_{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'VOL_{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"VOL_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"VOL_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    #NNA
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NNA"].GUIOs
    for lIdx in range (constants.NLINES_NNA):
        lineActive = cac_iID.get(f'NNA_{lIdx}_LineActive', False)
        if lineActive: 
            nnCode = cac_iID[f'NNA_{lIdx}_NeuralNetworkCode']
            nnCode_str = "" if nnCode is None else f"{nnCode}"
            alpha_str  = f"{cac_iID[f'NNA_{lIdx}_Alpha']:.2f}"
            beta_str   = f"{cac_iID[f'NNA_{lIdx}_Beta']}"
        else:          
            nnCode_str = "-"
            alpha_str  = "-"
            beta_str   = "-"
        sp_GUIOs[f"NNA_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"NNA_{lIdx}_NNCODE"].updateText(text = nnCode_str)
        sp_GUIOs[f"NNA_{lIdx}_ALPHA"].updateText(text  = alpha_str)
        sp_GUIOs[f"NNA_{lIdx}_BETA"].updateText(text   = beta_str)
    #MMACD
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MMACD"].GUIOs
    signalNSamples = cac_iID['MMACD_SignalNSamples']
    sp_GUIOs["MMACDSIGNALINTERVALDISPLAYTEXT"].updateText(text = f"{signalNSamples}")
    for lIdx in range (constants.NLINES_MMACD):
        lineActive = cac_iID.get(f'MMACD_MA{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'MMACD_MA{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"MA{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"MA{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    #DMIxADX
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_DMIxADX"].GUIOs
    for lIdx in range (constants.NLINES_DMIxADX):
        lineActive = cac_iID.get(f'DMIxADX_{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'DMIxADX_{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"DMIxADX_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"DMIxADX_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    #MFI
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_MFI"].GUIOs
    for lIdx in range (constants.NLINES_MFI):
        lineActive = cac_iID.get(f'MFI_{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'MFI_{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"MFI_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"MFI_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    #TPD
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_TPD"].GUIOs
    for lIdx in range (constants.NLINES_TPD):
        lineActive = cac_iID.get(f'TPD_{lIdx}_LineActive', False)
        if lineActive: 
            viewLength_str = f"{cac_iID[f'TPD_{lIdx}_ViewLength']}"
            nSamples_str   = f"{cac_iID[f'TPD_{lIdx}_NSamples']}"
            nSamplesMA_str = f"{cac_iID[f'TPD_{lIdx}_NSamplesMA']}"
        else:          
            viewLength_str = "-"
            nSamples_str   = "-"
            nSamplesMA_str = "-"
        sp_GUIOs[f"TPD_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"TPD_{lIdx}_VIEWLENGTH"].updateText(text = viewLength_str)
        sp_GUIOs[f"TPD_{lIdx}_NSAMPLES"].updateText(text   = nSamples_str)
        sp_GUIOs[f"TPD_{lIdx}_NSAMPLESMA"].updateText(text = nSamplesMA_str)
    #WOI
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_WOI"].GUIOs
    for lIdx in range (constants.NLINES_WOI):
        lineActive = cac_iID.get(f'WOI_{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'WOI_{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"WOI_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"WOI_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
    #NES
    sp_GUIOs = guios["SIMULATIONDETAIL_CONFIGURATIONS_CURRENCYANALYSISCONFIGURATIONSUBPAGE_NES"].GUIOs
    for lIdx in range (constants.NLINES_NES):
        lineActive = cac_iID.get(f'NES_{lIdx}_LineActive', False)
        if lineActive: nSamples_str = f"{cac_iID[f'NES_{lIdx}_NSamples']}"
        else:          nSamples_str = "-"
        sp_GUIOs[f"NES_{lIdx}_LINE"].setStatus(status = lineActive, callStatusUpdateFunction = False)
        sp_GUIOs[f"NES_{lIdx}_NSAMPLES"].updateText(text = nSamples_str)
"""
#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


