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



def cd_draw():
    pass
#CHART DRAWER FUNCTIONS END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUTOTRADE PAGE FUNCTIONS -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#AUTOTRADE PAGE FUNCTIONS END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SIMULATION RESULTS PAGE FUNCTIONS ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#SIMULATION RESULTS PAGE FUNCTIONS END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


