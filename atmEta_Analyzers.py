import atmEta_Auxillaries
import atmEta_NeuralNetworks
import atmEta_Constants

import random
import math
import numpy
import datetime
import pprint
import torch
import time
import scipy
from collections import defaultdict

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

ANALYSIS_MITYPES = ('SMA', 'WMA', 'EMA', 'PSAR', 'BOL', 'IVP', 'SWING')
ANALYSIS_SITYPES = ('VOL', 'NNA', 'MMACDSHORT', 'MMACDLONG', 'DMIxADX', 'MFI', 'WOI', 'NES')

ANALYSIS_GENERATIONORDER = ('SMA', 'WMA', 'EMA', 'PSAR', 'BOL', 'IVP', 'SWING', 'VOL', 'NNA', 'MMACDSHORT', 'MMACDLONG', 'DMIxADX', 'MFI')

AGGTRADESAMPLINGINTERVAL_S    = atmEta_Constants.AGGTRADESAMPLINGINTERVAL_S
BIDSANDASKSSAMPLINGINTERVAL_S = atmEta_Constants.BIDSANDASKSSAMPLINGINTERVAL_S
NMAXAGGTRADESSAMPLES          = atmEta_Constants.NMAXAGGTRADESSAMPLES
NMAXBIDSANDASKSSAMPLES        = atmEta_Constants.NMAXBIDSANDASKSSAMPLES
WOIALPHA                      = atmEta_Constants.WOIALPHA

def analysisGenerator_SMA(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    #[1]: Instances
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']
    klines_raw   = klineAccess['raw']
    pPrecision   = precisions['price']

    #[2]: Previous Analysis & Analysis Count
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    sma_prev      = klineAccess[analysisCode].get(timestamp_previous, None)
    analysisCount = 0 if sma_prev is None else sma_prev['_analysisCount']+1

    #[3]: SMA Compuation
    if analysisCount < nSamples-1:
        priceSum = None
        sma      = None
    elif nSamples-1 == analysisCount:
        priceSum = sum(klines_raw[ts][KLINDEX_CLOSEPRICE] for ts in atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, 
                                                                                                                 timestamp  = timestamp, 
                                                                                                                 nTicks     = nSamples, 
                                                                                                                 direction  = False, 
                                                                                                                 mrktReg    = mrktRegTS))
        sma = round(priceSum / nSamples, pPrecision)
    else:
        timestamp_expired = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -nSamples)
        priceSum_prev = sma_prev['PRICESUM']
        priceSum      = priceSum_prev - klines_raw[timestamp_expired][KLINDEX_CLOSEPRICE] + klines_raw[timestamp][KLINDEX_CLOSEPRICE]
        sma = round(priceSum / nSamples, pPrecision)

    #[4]: Result formatting & Saving
    smaResult = {'PRICESUM': priceSum,
                 'SMA':      sma,
                 '_analysisCount': analysisCount}
    klineAccess[analysisCode][timestamp] = smaResult

    #[5]: Memory Optimization References
    return (2,        #nAnalysisToKeep
            nSamples) #nKlinesToKeep

def analysisGenerator_WMA(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    #[1]: Instances
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']
    klines_raw   = klineAccess['raw']
    pPrecision   = precisions['price']

    #[2]: Previous Analysis & Analysis Count
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    wma_prev      = klineAccess[analysisCode].get(timestamp_previous, None)
    analysisCount = 0 if wma_prev is None else wma_prev['_analysisCount']+1

    #[3]: WMA computation
    if analysisCount < nSamples-1:
        priceSum_simple   = None
        priceSum_weighted = None
        wma               = None
    elif nSamples-1 == analysisCount:
        tsList = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, 
                                                              timestamp  = timestamp, 
                                                              nTicks     = nSamples, 
                                                              direction  = False, 
                                                              mrktReg    = mrktRegTS)
        priceSum_simple   = sum(klines_raw[ts][KLINDEX_CLOSEPRICE]                   for ts         in tsList)
        priceSum_weighted = sum(klines_raw[ts][KLINDEX_CLOSEPRICE]*(nSamples-tIndex) for tIndex, ts in enumerate(tsList))
        baseSum = nSamples*(nSamples+1)/2
        wma = round(priceSum_weighted / baseSum, pPrecision)
    else:
        timestamp_expired = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -nSamples)
        price_expired = klines_raw[timestamp_expired][KLINDEX_CLOSEPRICE]
        price_new     = klines_raw[timestamp][KLINDEX_CLOSEPRICE]
        priceSum_simple_prev   = wma_prev['PRICESUM_SIMPLE']
        priceSum_weighted_prev = wma_prev['PRICESUM_WEIGHTED']
        priceSum_simple   = priceSum_simple_prev - price_expired + price_new
        priceSum_weighted = priceSum_weighted_prev + (nSamples*price_new) - priceSum_simple_prev
        baseSum = nSamples*(nSamples+1)/2
        wma = round(priceSum_weighted / baseSum, pPrecision)

    #[4]: Result formatting & Saving
    wmaResult = {'PRICESUM_SIMPLE':   priceSum_simple,
                 'PRICESUM_WEIGHTED': priceSum_weighted,
                 'WMA':               wma,
                 '_analysisCount': analysisCount}
    klineAccess[analysisCode][timestamp] = wmaResult

    #[5]: Memory Optimization References
    return (2,        #nAnalysisToKeep
            nSamples) #nKlinesToKeep

def analysisGenerator_EMA(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    #[1]: Instances
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']
    kValue       = 2/(analysisParams['nSamples']+1)
    klines_raw   = klineAccess['raw']
    pPrecision   = precisions['price']

    #[2]: Previous Analysis & Analysis Count
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    ema_prev      = klineAccess[analysisCode].get(timestamp_previous, None)
    analysisCount = 0 if ema_prev is None else ema_prev['_analysisCount']+1

    #[3]: EMA computation
    if analysisCount < nSamples-1:
        ema = None
    elif nSamples-1 == analysisCount:
        priceSum = sum(klines_raw[ts][KLINDEX_CLOSEPRICE] for ts in atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, 
                                                                                                                 timestamp  = timestamp, 
                                                                                                                 nTicks     = nSamples, 
                                                                                                                 direction  = False, 
                                                                                                                 mrktReg    = mrktRegTS))
        ema = round(priceSum / nSamples, pPrecision)
    else:
        ema = (klines_raw[timestamp][KLINDEX_CLOSEPRICE]*kValue) + (ema_prev['EMA']*(1-kValue))
        ema = round(ema, pPrecision)

    #[4]: Result formatting & Saving
    emaResult = {'EMA': ema,
                 '_analysisCount': analysisCount}
    klineAccess[analysisCode][timestamp] = emaResult

    #[5]: Memory Optimization References
    return (2,        #nAnalysisToKeep
            nSamples) #nKlinesToKeep

def analysisGenerator_PSAR(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    #[1]: Instances
    analysisCode      = analysisParams['analysisCode']
    psar_start        = analysisParams['start']
    psar_acceleration = analysisParams['acceleration']
    psar_maximum      = analysisParams['maximum']
    klines_raw        = klineAccess['raw']
    pPrecision        = precisions['price']

    #[2]: Previous Analysis & Analysis Count
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    psar_prev     = klineAccess[analysisCode].get(timestamp_previous, None)
    analysisCount = 0 if psar_prev is None else psar_prev['_analysisCount']+1

    #[3]: PSAR computation
    if analysisCount == 0:
        pd          = None
        pd_reversed = None
        af          = None
        ep          = None
        psar        = None
        dcc         = None

    elif analysisCount == 1:
        kline_prev   = klines_raw[timestamp_previous]
        kline_this   = klines_raw[timestamp]
        p_low_prev   = kline_prev[KLINDEX_LOWPRICE]
        p_high_prev  = kline_prev[KLINDEX_HIGHPRICE]
        p_low_this   = kline_this[KLINDEX_LOWPRICE]
        p_high_this  = kline_this[KLINDEX_HIGHPRICE]
        p_high_delta = p_high_this-p_high_prev if p_high_prev <= p_high_this else 0
        p_low_delta  = p_low_prev -p_low_this  if p_low_this  <= p_low_prev  else 0
        pd = (p_low_delta <= p_high_delta)
        pd_reversed = False
        af          = None
        ep          = None
        psar        = None
        dcc         = 0

    elif analysisCount == 2:
        timestamp_previous2 = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -2)
        kline_prev1 = klines_raw[timestamp_previous]
        kline_prev2 = klines_raw[timestamp_previous2]
        if psar_prev['PD']: 
            psar = min(kline_prev1[KLINDEX_LOWPRICE],  kline_prev2[KLINDEX_LOWPRICE])
            ep   = max(kline_prev1[KLINDEX_HIGHPRICE], kline_prev2[KLINDEX_HIGHPRICE])
        else:
            psar = max(kline_prev1[KLINDEX_HIGHPRICE], kline_prev2[KLINDEX_HIGHPRICE])
            ep   = min(kline_prev1[KLINDEX_LOWPRICE],  kline_prev2[KLINDEX_LOWPRICE])
        af = psar_start
        pd = psar_prev['PD']
        pd_reversed = False
        dcc = 0

    elif 3 <= analysisCount:
        timestamp_previous2 = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -2)
        kline_this  = klines_raw[timestamp]
        kline_prev1 = klines_raw[timestamp_previous]
        kline_prev2 = klines_raw[timestamp_previous2]

        _psar = psar_prev['PSAR'] + psar_prev['AF']*(psar_prev['EP']-psar_prev['PSAR'])

        if psar_prev['PD']:
            #Limit Check
            _psar = min(_psar, kline_prev1[KLINDEX_LOWPRICE], kline_prev2[KLINDEX_LOWPRICE])
            #Reverse Detect
            pd_reversed = (kline_this[KLINDEX_LOWPRICE] < _psar)
            #AF Update
            if psar_prev['EP'] < kline_this[KLINDEX_HIGHPRICE]:
                ep = kline_this[KLINDEX_HIGHPRICE]
                af = psar_prev['AF'] + psar_acceleration
                if psar_maximum < af: af = psar_maximum
            else: 
                ep = psar_prev['EP']
                af = psar_prev['AF']
        else:
            #Limit Check
            _psar = max(_psar, kline_prev1[KLINDEX_HIGHPRICE], kline_prev2[KLINDEX_HIGHPRICE])
            #Reverse Detect
            pd_reversed = (_psar < kline_this[KLINDEX_HIGHPRICE])
            #AF Update
            if (kline_this[KLINDEX_LOWPRICE] < psar_prev['EP']):
                ep = kline_this[KLINDEX_LOWPRICE]
                af = psar_prev['AF'] + psar_acceleration
                if psar_maximum < af: af = psar_maximum
            else: 
                ep = psar_prev['EP']
                af = psar_prev['AF']

        #PD Reversal Handling
        if pd_reversed:
            pd    = not(psar_prev['PD'])
            af    = psar_start
            psar  = psar_prev['EP']
            ep    = kline_this[KLINDEX_HIGHPRICE] if pd else kline_this[KLINDEX_LOWPRICE]
            dcc   = 0
        else: 
            pd  = psar_prev['PD']
            dcc = psar_prev['DCC']+1
            psar = _psar

        #Precision Rounding
        psar = round(psar, pPrecision)

    #[4]: Result formatting & Saving
    psarResult = {'PD':         pd,          # Progression Direction (True: Incremental, False: Decremental)
                  'PDReversed': pd_reversed, # Progression Direction Reversal
                  'AF':         af,          # Acceleration Factor
                  'EP':         ep,          # Extreme Point
                  'PSAR':       psar,        # PSAR Value
                  'DCC':        dcc,         # Direction Continuity Counter
                  '_analysisCount': analysisCount}
    klineAccess[analysisCode][timestamp] = psarResult

    #[5]: Memory Optimization References
    return (2, #nAnalysisToKeep
            3) #nKlinesToKeep

def analysisGenerator_BOL(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    #[1]: Instances
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']
    maType       = analysisParams['MAType']
    bandWidth    = analysisParams['bandWidth']
    klines_raw   = klineAccess['raw']
    pPrecision   = precisions['price']

    #[2]: Previous Analysis & Analysis Count
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    bol_prev      = klineAccess[analysisCode].get(timestamp_previous, None)
    analysisCount = 0 if bol_prev is None else bol_prev['_analysisCount']+1

    #[3]: BOL computation
    if nSamples-1 <= analysisCount:
        tsList = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, 
                                                              timestamp  = timestamp, 
                                                              nTicks     = nSamples, 
                                                              direction  = False, 
                                                              mrktReg    = mrktRegTS)
    else:
        tsList = None
    #---[3-1]: MA
    #------[3-1-1]: SMA
    if maType == 'SMA':
        if analysisCount < nSamples-1:
            priceSum = None
            ma       = None
        elif nSamples-1 == analysisCount:
            priceSum = sum(klines_raw[ts][KLINDEX_CLOSEPRICE] for ts in tsList)
            ma = round(priceSum / nSamples, pPrecision)
        else:
            timestamp_expired = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -nSamples)
            priceSum_prev = bol_prev['MACOMPUTATION']
            priceSum      = priceSum_prev - klines_raw[timestamp_expired][KLINDEX_CLOSEPRICE] + klines_raw[timestamp][KLINDEX_CLOSEPRICE]
            ma = round(priceSum / nSamples, pPrecision)
        maComputation = priceSum
    #------[3-1-1]: WMA
    elif maType == 'WMA':
        if analysisCount < nSamples-1:
            priceSum_simple   = None
            priceSum_weighted = None
            ma                = None
        elif nSamples-1 == analysisCount:
            priceSum_simple   = sum(klines_raw[ts][KLINDEX_CLOSEPRICE]                   for ts         in tsList)
            priceSum_weighted = sum(klines_raw[ts][KLINDEX_CLOSEPRICE]*(nSamples-tIndex) for tIndex, ts in enumerate(tsList))
            baseSum = nSamples*(nSamples+1)/2
            ma = round(priceSum_weighted / baseSum, pPrecision)
        else:
            timestamp_expired = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -nSamples)
            price_expired = klines_raw[timestamp_expired][KLINDEX_CLOSEPRICE]
            price_new     = klines_raw[timestamp][KLINDEX_CLOSEPRICE]
            priceSum_simple_prev, priceSum_weighted_prev = bol_prev['MACOMPUTATION']
            priceSum_simple   = priceSum_simple_prev - price_expired + price_new
            priceSum_weighted = priceSum_weighted_prev + (nSamples*price_new) - priceSum_simple_prev
            baseSum = nSamples*(nSamples+1)/2
            ma = round(priceSum_weighted / baseSum, pPrecision)
        maComputation = (priceSum_simple, priceSum_weighted)
    #------[3-1-1]: EMA
    elif maType == 'EMA':
        if analysisCount < nSamples-1:
            ma = None
        elif nSamples-1 == analysisCount:
            priceSum = sum(klines_raw[ts][KLINDEX_CLOSEPRICE] for ts in tsList)
            ma = round(priceSum / nSamples, pPrecision)
        else:
            kValue = 2/(nSamples+1)
            ma = (klines_raw[timestamp][KLINDEX_CLOSEPRICE]*kValue) + (bol_prev['MA']*(1-kValue))
            ma = round(ma, pPrecision)
        maComputation = None
    #---[3-2]: BOL
    if analysisCount < nSamples-1:
        bol = None
    else:
        deviationSquaredSum = sum(math.pow(klines_raw[ts][KLINDEX_CLOSEPRICE]-ma, 2) for ts in tsList)
        sd  = math.sqrt(deviationSquaredSum/nSamples)
        bol = (round(ma-sd*bandWidth, pPrecision), 
               round(ma+sd*bandWidth, pPrecision))

    #[4]: Result formatting & Saving
    bolResult = {'MACOMPUTATION': maComputation,
                 'MA':            ma,
                 'BOL':           bol,
                 '_analysisCount': analysisCount}
    klineAccess[analysisCode][timestamp] = bolResult

    #[5]: Memory Optimization References
    return (2,        #nAnalysisToKeep
            nSamples) #nKlinesToKeep

def __IVP_addPriceLevelProfile(priceLevelProfileWeight, priceLevelProfilePosition_low, priceLevelProfilePosition_high, priceLevelProfile, divisionHeight, pricePrecision, mode = True):
    #[1]: Instances
    plpw       = priceLevelProfileWeight
    plpp_low   = priceLevelProfilePosition_low
    plpp_high  = priceLevelProfilePosition_high
    plp        = priceLevelProfile
    dHeight    = divisionHeight
    pPrecision = pricePrecision
    dIndex_floor   = int(plpp_low /divisionHeight)
    dIndex_ceiling = int(plpp_high/divisionHeight)
    nDivisions = len(plp)
    director   = 1 if mode else -1

    #[2]: Updater
    #---[2-1]: The floor dIndex and the ceiling dIndex is the same
    if dIndex_floor == dIndex_ceiling:
        if dIndex_floor < nDivisions: 
            plp[dIndex_floor] += plpw*director
            if plp[dIndex_floor] < 0: plp[dIndex_floor] = 0
    #---[2-2]: The ceiling division is right above the floor division
    elif dIndex_ceiling == dIndex_floor+1:
        vpDensity   = plpw/(plpp_high-plpp_low)
        dPos_center = round(dIndex_ceiling*dHeight, pPrecision)
        #[2-2-1]: Floor Part
        if dIndex_floor < nDivisions: 
            plp[dIndex_floor] += vpDensity*(dPos_center-plpp_low)*director
            if plp[dIndex_floor] < 0: plp[dIndex_floor] = 0
        #[2-2-2]: Ceiling Part
        if dIndex_ceiling < nDivisions: 
            plp[dIndex_ceiling] += vpDensity*(plpp_high-dPos_center)*director
            if plp[dIndex_ceiling] < 0: plp[dIndex_ceiling] = 0
    #---[2-3]: There exist at least one divisions between the floor and the ceiling division
    else:
        vpDensity = plpw/(plpp_high-plpp_low)
        #[2-3-1]: Floor Part
        dPos = round((dIndex_floor+1)*dHeight, pPrecision)
        dVol = vpDensity*(dPos-plpp_low)
        plp[dIndex_floor] += dVol*director
        if plp[dIndex_floor] < 0: plp[dIndex_floor] = 0
        #[2-3-2]: Middle Part
        dVol = vpDensity*dHeight
        plIdx_beg = dIndex_floor+1
        plIdx_end = min(dIndex_ceiling, nDivisions)
        for plIndex in range (plIdx_beg, plIdx_end): 
            plp[plIndex] += dVol*director
            if plp[plIndex] < 0: plp[plIndex] = 0
        #[2-3-3]: Ceiling Part
        if dIndex_ceiling < nDivisions:
            dPos = round(dIndex_ceiling*dHeight, pPrecision)
            dVol = vpDensity*(plpp_high-dPos)
            plp[dIndex_ceiling] += dVol*director
            if plp[dIndex_ceiling] < 0: plp[dIndex_ceiling] = 0

def analysisGenerator_IVP(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    #[1]: Parameters
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']
    gammaFactor  = analysisParams['gammaFactor']
    deltaFactor  = analysisParams['deltaFactor']
    pPrecision   = precisions['price']
    baseUnit = pow(10, -pPrecision)

    #[2]: Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    ivp_prev      = klineAccess[analysisCode].get(timestamp_previous, None)
    analysisCount = 0 if ivp_prev is None else ivp_prev['_analysisCount']+1

    #[3]: Klines
    kl_this = klineAccess['raw'][timestamp]
    kl_this_cp  = kl_this[KLINDEX_CLOSEPRICE]
    kl_this_hp  = kl_this[KLINDEX_HIGHPRICE]
    kl_this_lp  = kl_this[KLINDEX_LOWPRICE]
    kl_this_vol = kl_this[KLINDEX_VOLBASE]

    #[4]: Division Height & Volume Price Level Profiles Preparation
    if analysisCount < nSamples-1:
        divisionHeight          = None
        gammaFactor             = None
        betaFactor              = None
        volumePriceLevelProfile = None
    else:
        betaFactor = round(kl_this_cp*gammaFactor, pPrecision)
        #---divisionCeiling determination
        p_max = klineAccess['raw_status'][timestamp]['p_max']
        p_max_OOM = math.floor(math.log(p_max, 10))
        p_max_MSD = int(p_max/pow(10, p_max_OOM))
        if (p_max_MSD == 10): 
            p_max_MSD = 1
            p_max_OOM += 1
        dCeiling_MSD = (int(p_max_MSD/1)+1)*1
        if dCeiling_MSD == 10: 
            dCeiling_MSD = 1
            dCeiling_OOM = p_max_OOM+1
        else:                    
            dCeiling_MSD = dCeiling_MSD
            dCeiling_OOM = p_max_OOM
        dCeiling = dCeiling_MSD*pow(10, dCeiling_OOM)
        #---divisionHeight determination
        divisionHeight_min = betaFactor/10
        divisionHeight_min_OOM = math.floor(math.log(divisionHeight_min, 10))
        divisionHeight_min_MSD = int(divisionHeight_min/pow(10, divisionHeight_min_OOM))
        if divisionHeight_min_MSD == 10: 
            divisionHeight_min_MSD = 1
            divisionHeight_min_OOM += 1
        divisionHeight_MSD = int(divisionHeight_min_MSD)
        if divisionHeight_MSD == 0: 
            divisionHeight_MSD = 1
            divisionHeight_OOM = divisionHeight_min_OOM
        else:                       
            divisionHeight_MSD = divisionHeight_MSD
            divisionHeight_OOM = divisionHeight_min_OOM
        _divisionHeight = divisionHeight_MSD*pow(10, divisionHeight_OOM)
        nBaseUnitsWithinDivisionHeight = int(_divisionHeight/baseUnit)
        if nBaseUnitsWithinDivisionHeight == 0: divisionHeight = round(baseUnit,                                pPrecision)
        else:                                   divisionHeight = round(baseUnit*nBaseUnitsWithinDivisionHeight, pPrecision)
        #---nDivisions
        nDivisions = math.ceil(dCeiling/divisionHeight)
        #---Price Level Profiles
        if analysisCount == nSamples-1: 
            volumePriceLevelProfile = numpy.zeros(nDivisions)
        else:
            volumePriceLevelProfile_prev = ivp_prev['volumePriceLevelProfile']
            nDivisions_prev     = len(volumePriceLevelProfile_prev)
            divisionHeight_prev = ivp_prev['divisionHeight']
            if (divisionHeight_prev == divisionHeight) and (nDivisions_prev == nDivisions): 
                volumePriceLevelProfile = numpy.copy(volumePriceLevelProfile_prev)
            else:
                volumePriceLevelProfile = numpy.zeros(nDivisions)
                for divisionIndex_prev in range (nDivisions_prev):
                    divisionPosition_low_prev  = round(divisionHeight_prev*divisionIndex_prev,     pPrecision)
                    divisionPosition_high_prev = round(divisionHeight_prev*(divisionIndex_prev+1), pPrecision)
                    __IVP_addPriceLevelProfile(priceLevelProfileWeight        = volumePriceLevelProfile_prev[divisionIndex_prev], 
                                               priceLevelProfilePosition_low  = divisionPosition_low_prev, 
                                               priceLevelProfilePosition_high = divisionPosition_high_prev, 
                                               priceLevelProfile              = volumePriceLevelProfile, 
                                               divisionHeight                 = divisionHeight,
                                               pricePrecision                 = pPrecision)
    #[5]: Volume Price Level Profile
    if analysisCount == nSamples-1:
        for ts in atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False, mrktReg = mrktRegTS):
            kl_target = klineAccess['raw'][ts]
            __IVP_addPriceLevelProfile(priceLevelProfileWeight        = kl_target[KLINDEX_VOLBASE], 
                                       priceLevelProfilePosition_low  = kl_target[KLINDEX_LOWPRICE], 
                                       priceLevelProfilePosition_high = kl_target[KLINDEX_HIGHPRICE], 
                                       priceLevelProfile              = volumePriceLevelProfile, 
                                       divisionHeight                 = divisionHeight, 
                                       pricePrecision                 = pPrecision)
    elif nSamples-1 < analysisCount:
        __IVP_addPriceLevelProfile(priceLevelProfileWeight        = kl_this_vol, 
                                   priceLevelProfilePosition_low  = kl_this_lp, 
                                   priceLevelProfilePosition_high = kl_this_hp, 
                                   priceLevelProfile              = volumePriceLevelProfile, 
                                   divisionHeight                 = divisionHeight,
                                   pricePrecision                 = pPrecision)
    if nSamples < analysisCount:
        kl_expired = klineAccess['raw'][atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -nSamples)]
        __IVP_addPriceLevelProfile(priceLevelProfileWeight        = kl_expired[KLINDEX_VOLBASE], 
                                   priceLevelProfilePosition_low  = kl_expired[KLINDEX_LOWPRICE], 
                                   priceLevelProfilePosition_high = kl_expired[KLINDEX_HIGHPRICE], 
                                   priceLevelProfile              = volumePriceLevelProfile, 
                                   divisionHeight                 = divisionHeight,
                                   pricePrecision                 = pPrecision,
                                   mode                           = False)
        
    #[6]: Volume Price Level Profile Boundaries
    #---[6-1]: Not Yet Compuatable
    if analysisCount < nSamples-1:
        volumePriceLevelProfile_Filtered     = None
        volumePriceLevelProfile_Filtered_Max = None
        volumePriceLevelProfile_Boundaries   = None
    #---[6-1]: Boundaries Search
    else:
        #[6-1-1]: Filtering & Boundaries Search
        volumePriceLevelProfile_Filtered     = scipy.ndimage.gaussian_filter1d(input = volumePriceLevelProfile, 
                                                                               sigma = round(len(volumePriceLevelProfile)/(3.3*1000)*deltaFactor, 10))
        volumePriceLevelProfile_Filtered_Max = numpy.max(volumePriceLevelProfile_Filtered)
        volumePriceLevelProfile_Boundaries   = []
        #[6-1-2]: Extremas Search
        direction_prev = None
        volHeight_prev = None
        for plIndex, volHeight in enumerate(volumePriceLevelProfile_Filtered):
            #[6-1-2-1]: Initial
            if direction_prev is None:
                direction_prev = True
                volHeight_prev = volHeight
                continue
            #[6-1-2-2]: Local Maximum
            if direction_prev and (volHeight < volHeight_prev): 
                direction_prev = False
                volumePriceLevelProfile_Boundaries.append(plIndex-1)
            #[6-1-2-3]: Local Minimum
            elif not direction_prev and (volHeight_prev < volHeight): 
                direction_prev = True
                volumePriceLevelProfile_Boundaries.append(plIndex-1) 
            volHeight_prev = volHeight

    #[7]: Near VPLP Boundaries
    if volumePriceLevelProfile_Boundaries is None:
        volumePriceLevelProfile_nearBoundaries = [None]*10
    else:
        vplp_nearBoundaries_down = [None]*5
        vplp_nearBoundaries_up   = [None]*5
        #Find the nearest above boundary index
        dIndex_closePrice  = kl_this_cp//divisionHeight
        bIndex_nearestAbove = None
        for bIndex, dIndex in enumerate(volumePriceLevelProfile_Boundaries):
            if dIndex_closePrice <= dIndex: 
                bIndex_nearestAbove = bIndex
                break
        #Convert nearest down and up boundaries into price center values
        if bIndex_nearestAbove is None:
            idx_up_beg   = len(volumePriceLevelProfile_Boundaries)
            idx_down_beg = len(volumePriceLevelProfile_Boundaries)-5
        else:
            idx_up_beg   = bIndex_nearestAbove
            idx_down_beg = bIndex_nearestAbove-5
        for i in range (5):
            idx_down_target = idx_down_beg+i
            idx_up_target   = idx_up_beg  +i
            if 0 <= idx_down_target < len(volumePriceLevelProfile_Boundaries):
                dIndex = volumePriceLevelProfile_Boundaries[idx_down_target]
                vplp_nearBoundaries_down[i] = round((dIndex+0.5)*divisionHeight, pPrecision)
            if 0 <= idx_up_target < len(volumePriceLevelProfile_Boundaries):
                dIndex = volumePriceLevelProfile_Boundaries[idx_up_target]
                vplp_nearBoundaries_up[i] = round((dIndex+0.5)*divisionHeight, pPrecision)
        #Finally
        volumePriceLevelProfile_nearBoundaries = tuple(vplp_nearBoundaries_down)+tuple(vplp_nearBoundaries_up)
        volumePriceLevelProfile_nearBoundaries = tuple(vplp_nearBoundaries_down+vplp_nearBoundaries_up)

    #[8]: Result Formatting & Save
    ivpResult = {'divisionHeight': divisionHeight, 
                 'gammaFactor':    gammaFactor, 
                 'betaFactor':     betaFactor,
                 'volumePriceLevelProfile':                volumePriceLevelProfile,
                 'volumePriceLevelProfile_Filtered':       volumePriceLevelProfile_Filtered, 
                 'volumePriceLevelProfile_Filtered_Max':   volumePriceLevelProfile_Filtered_Max, 
                 'volumePriceLevelProfile_Boundaries':     volumePriceLevelProfile_Boundaries,
                 'volumePriceLevelProfile_NearBoundaries': volumePriceLevelProfile_nearBoundaries,
                 '_analysisCount': analysisCount}
    klineAccess[analysisCode][timestamp] = ivpResult

    #[9]: Memory Optimization References
    return (2,          #nAnalysisToKeep
            nSamples+1) #nKlinesToKeep

def analysisGenerator_SWING(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    #[1]: Parameters
    analysisCode    = analysisParams['analysisCode']
    swingRange      = analysisParams['swingRange']
    klineAccess_raw = klineAccess['raw']
    kline = klineAccess_raw[timestamp]

    #[2]: Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    swing_prev    = klineAccess[analysisCode].get(timestamp_previous, None)
    analysisCount = 0 if swing_prev is None else swing_prev['_analysisCount']+1

    #[3]: Swing Search
    #---[3-1]: Klines
    kl_hp = kline[KLINDEX_HIGHPRICE]
    kl_lp = kline[KLINDEX_LOWPRICE]

    #---[3-2]: Initialization
    if analysisCount == 0:
        swings      = []
        swingSearch = {'lastExtreme': True, 
                       'max':         kl_hp, 
                       'min':         kl_lp, 
                       'max_ts':      timestamp, 
                       'min_ts':      timestamp}
        
    #---[3-3]: Swing Search
    else:
        #[3-3-1]: Previous Swings
        swings      = swing_prev['SWINGS'].copy()
        swingSearch = swing_prev['_SWINGSEARCH'].copy()

        #[3-3-2]: Swing Update Check
        #---[3-3-2-1]: Last Swing Was HIGH
        if swingSearch['lastExtreme']:
            #[3-3-2-1-1]: Update Min (Lowest Low)
            if kl_lp < swingSearch['min']: 
                swingSearch['min']    = kl_lp
                swingSearch['min_ts'] = timestamp
            #[3-3-2-1-2]: Check Reversal
            if swingSearch['min']*(1+swingRange) < kl_hp:
                newSwing = (swingSearch['min_ts'], swingSearch['min'], -1)
                swings.append(newSwing)
                swingSearch['lastExtreme'] = False
                swingSearch['max']         = kl_hp
                swingSearch['max_ts']      = timestamp
                if 100 < len(swings): swings.pop(0)
        #---[3-3-2-2]: Last Swing Was Low
        else:
            #[3-3-2-2-1]: Update Max (Highest High)
            if swingSearch['max'] < kl_hp: 
                swingSearch['max']    = kl_hp
                swingSearch['max_ts'] = timestamp
            #[3-3-2-2-2]: Check Reversal
            if kl_lp < swingSearch['max']*(1-swingRange):
                newSwing = (swingSearch['max_ts'], swingSearch['max'], 1)
                swings.append(newSwing)
                swingSearch['lastExtreme'] = True
                swingSearch['min']         = kl_lp
                swingSearch['min_ts']      = timestamp
                if 100 < len(swings): swings.pop(0)

    #[4]: Result Formatting & Save
    swingResult = {'SWINGS': swings, 
                   '_SWINGSEARCH': swingSearch,
                   #Process
                   '_analysisCount': analysisCount}
    klineAccess[analysisCode][timestamp] = swingResult

    #[5]: Memory Optimization References
    return (2, #nAnalysisToKeep
            2) #nKlinesToKeep

def analysisGenerator_VOL(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    #[1]: Instances
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']
    MAType       = analysisParams['MAType']
    vaIndices = {'BASE':    KLINDEX_VOLBASE,
                 'QUOTE':   KLINDEX_VOLQUOTE,
                 'BASETB':  KLINDEX_VOLBASETAKERBUY,
                 'QUOTETB': KLINDEX_VOLQUOTETAKERBUY}
    vps = {'BASE':    precisions['quantity'],
           'QUOTE':   precisions['quote'],
           'BASETB':  precisions['quantity'],
           'QUOTETB': precisions['quote']}
    klines_raw = klineAccess['raw']
    
    #[2]: Previous Analysis & Analysis Count
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    vol_prev      = klineAccess[analysisCode].get(timestamp_previous, None)
    analysisCount = 0 if vol_prev is None else vol_prev['_analysisCount']+1

    #[3]: Compute VOLMAs
    maComputations = dict()
    mas            = dict()
    #---[3-1]: Timestamps List
    if nSamples-1 <= analysisCount:
        tsList = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, 
                                                              timestamp  = timestamp, 
                                                              nTicks     = nSamples, 
                                                              direction  = False, 
                                                              mrktReg    = mrktRegTS)
    else:
        tsList = None
    #---[3-2]: VolType Loop
    for volType, vaIdx in vaIndices.items():
        precision = vps[volType]
        #[3-2-1]: SMA
        if MAType == 'SMA':
            if analysisCount < nSamples-1:
                valSum = None
                ma     = None
            elif nSamples-1 == analysisCount:
                valSum = sum(klines_raw[ts][vaIdx] for ts in tsList)
                ma = round(valSum / nSamples, precision)
            else:
                timestamp_expired = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -nSamples)
                valSum_prev = vol_prev[f'MACOMPUTATION_{volType}']
                valSum      = valSum_prev - klines_raw[timestamp_expired][vaIdx] + klines_raw[timestamp][vaIdx]
                ma = round(valSum / nSamples, precision)
            maComputation = valSum
        #[3-2-2]: WMA
        elif MAType == 'WMA':
            if analysisCount < nSamples-1:
                valSum_simple   = None
                valSum_weighted = None
                ma                = None
            elif nSamples-1 == analysisCount:
                valSum_simple   = sum(klines_raw[ts][vaIdx]                   for ts         in tsList)
                valSum_weighted = sum(klines_raw[ts][vaIdx]*(nSamples-tIndex) for tIndex, ts in enumerate(tsList))
                baseSum = nSamples*(nSamples+1)/2
                ma = round(valSum_weighted / baseSum, precision)
            else:
                timestamp_expired = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -nSamples)
                price_expired = klines_raw[timestamp_expired][vaIdx]
                price_new     = klines_raw[timestamp][vaIdx]
                valSum_simple_prev, valSum_weighted_prev = vol_prev[f'MACOMPUTATION_{volType}']
                valSum_simple   = valSum_simple_prev - price_expired + price_new
                valSum_weighted = valSum_weighted_prev + (nSamples*price_new) - valSum_simple_prev
                baseSum = nSamples*(nSamples+1)/2
                ma = round(valSum_weighted / baseSum, precision)
            maComputation = (valSum_simple, valSum_weighted)
        #[3-2-3]: EMA
        elif MAType == 'EMA':
            if analysisCount < nSamples-1:
                ma = None
            elif nSamples-1 == analysisCount:
                valSum = sum(klines_raw[ts][vaIdx] for ts in tsList)
                ma = round(valSum / nSamples, precision)
            else:
                kValue = 2/(nSamples+1)
                ma = (klines_raw[timestamp][vaIdx]*kValue) + (vol_prev[f'MA_{volType}']*(1-kValue))
                ma = round(ma, precision)
            maComputation = None
        #[3-2-4]: Finally
        maComputations[volType] = maComputation
        mas[volType]            = ma

    #[4]: Result formatting & Saving
    volResult = {'MACOMPUTATION_BASE':    maComputations['BASE'],
                 'MACOMPUTATION_QUOTE':   maComputations['QUOTE'],
                 'MACOMPUTATION_BASETB':  maComputations['BASETB'],
                 'MACOMPUTATION_QUOTETB': maComputations['QUOTETB'],
                 'MA_BASE':               mas['BASE'],
                 'MA_QUOTE':              mas['QUOTE'],
                 'MA_BASETB':             mas['BASETB'],
                 'MA_QUOTETB':            mas['QUOTETB'],
                 '_analysisCount': analysisCount}
    klineAccess[analysisCode][timestamp] = volResult

    #[5]: Memory Optimization References
    return (2,        #nAnalysisToKeep
            nSamples) #nKlinesToKeep

def analysisGenerator_NNA(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode = analysisParams['analysisCode']
    nnCode  = analysisParams['nnCode']
    alpha   = analysisParams['alpha']
    beta    = analysisParams['beta']

    klineAccess_raw = klineAccess['raw']
    kline = klineAccess_raw[timestamp]
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    nna_prev    = klineAccess[analysisCode].get(timestamp_previous, None)
    analysisCount = 0 if nna_prev is None else nna_prev['_analysisCount']+1
    
    #NNA
    nn  = neuralNetworks.get(nnCode, None)
    nna = None
    if nn is not None:
        nn_nKlines = nn.getNKlines()
        if (nn_nKlines-1) <= analysisCount:
            #Formatting
            nnInputTensor = torch.zeros(size = (nn_nKlines*6,), device = 'cpu', dtype = torch.float32, requires_grad = False)
            klineTSs      = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = nn_nKlines, direction = False, mrktReg = mrktRegTS)
            #Klines
            p_max     = max(klineAccess_raw[ts][KLINDEX_HIGHPRICE] for ts in klineTSs)
            p_min     = min(klineAccess_raw[ts][KLINDEX_LOWPRICE]  for ts in klineTSs)
            p_range   = p_max-p_min
            vol_max   = min(klineAccess_raw[ts][KLINDEX_VOLBASE]         for ts in klineTSs)
            volTB_max = min(klineAccess_raw[ts][KLINDEX_VOLBASETAKERBUY] for ts in klineTSs)
            for relKLIdx in range (nn_nKlines):
                kline = klineAccess_raw[klineTSs[-(1+relKLIdx)]]
                if p_range != 0:
                    nnInputTensor[relKLIdx*6+0] = (kline[KLINDEX_OPENPRICE] -p_min)/p_range
                    nnInputTensor[relKLIdx*6+1] = (kline[KLINDEX_HIGHPRICE] -p_min)/p_range
                    nnInputTensor[relKLIdx*6+2] = (kline[KLINDEX_LOWPRICE]  -p_min)/p_range
                    nnInputTensor[relKLIdx*6+3] = (kline[KLINDEX_CLOSEPRICE]-p_min)/p_range
                else:
                    nnInputTensor[relKLIdx*6+0] = 0.5
                    nnInputTensor[relKLIdx*6+1] = 0.5
                    nnInputTensor[relKLIdx*6+2] = 0.5
                    nnInputTensor[relKLIdx*6+3] = 0.5
                if vol_max != 0: nnInputTensor[relKLIdx*6+4] = (kline[KLINDEX_VOLBASE])/vol_max
                else:            nnInputTensor[relKLIdx*6+4] = 0.0
                if volTB_max != 0: nnInputTensor[relKLIdx*6+5] = (kline[KLINDEX_VOLBASETAKERBUY])/volTB_max
                else:              nnInputTensor[relKLIdx*6+5] = 0.0
            #Forwarding
            nn_out = float(nn.forward(inputData = nnInputTensor)[0])*2-1
            nna    = abs(round(math.atan(pow(nn_out/alpha, beta))*2/math.pi, 5))*100
            if 0 <= nn_out: nna =  nna
            else:           nna = -nna

    #Result formatting & saving
    nnaResult = {#Neural Network
                 'NNA': nna,
                 #Process
                 '_analysisCount': analysisCount}
    klineAccess[analysisCode][timestamp] = nnaResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    if nn is None: return (2, 2)
    else:          return (nn_nKlines, nn_nKlines)

def analysisGenerator_MMACDSHORT(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode      = analysisParams['analysisCode']
    signal_nSamples   = analysisParams['signal_nSamples']
    signal_kValue     = 2/(signal_nSamples+1)
    multiplier        = analysisParams['multiplier']
    activatedMAs      = analysisParams['activatedMAs']
    activatedMAPairs  = analysisParams['activatedMAPairs']
    maxMANSamples     = analysisParams['maxMANSamples']
    absoluteMA_kValue = 2/(maxMANSamples+1)
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess[analysisCode]): _analysisCount = klineAccess[analysisCode][timestamp_previous]['_analysisCount']+1
    else:                                                 _analysisCount = 0
    timestamp_multipliedPrevious = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -(1+_analysisCount%multiplier))
    #MMACD Computation
    #---MAs Generation
    mas = dict()
    for ma_nSamples in activatedMAs:
        ma_kValue = 2/(ma_nSamples+1)
        if   (_analysisCount < (ma_nSamples-1)*multiplier): _ema = None
        elif (_analysisCount < ma_nSamples*multiplier):     _ema = (klineAccess['raw'][timestamp][KLINDEX_CLOSEPRICE]*ma_kValue) + (klineAccess['raw'][timestamp_multipliedPrevious][KLINDEX_CLOSEPRICE]       *(1-ma_kValue))
        else:                                               _ema = (klineAccess['raw'][timestamp][KLINDEX_CLOSEPRICE]*ma_kValue) + (klineAccess[analysisCode][timestamp_multipliedPrevious]['MAs'][ma_nSamples]*(1-ma_kValue))
        mas[ma_nSamples] = _ema
    #---MA Pair Delta Sum & MMACD
    if (_analysisCount < (maxMANSamples-1)*multiplier): mmacd = None
    else:                                               mmacd = sum([mas[maPair[0]]-mas[maPair[1]] for maPair in activatedMAPairs])
    #---Signal
    if   (_analysisCount < (maxMANSamples+signal_nSamples-1)*multiplier): signal = None
    elif (_analysisCount < (maxMANSamples+signal_nSamples)  *multiplier): signal = mmacd
    else:                                                                 signal = (mmacd*signal_kValue) + (klineAccess[analysisCode][timestamp_multipliedPrevious]['MMACD']*(1-signal_kValue))
    #---MSDelta
    if   (_analysisCount < (maxMANSamples+signal_nSamples-1)*multiplier): msDelta = None
    elif (_analysisCount < (maxMANSamples+signal_nSamples)  *multiplier): msDelta = 0
    else:                                                                 msDelta = mmacd-signal
    #---MSDelta Absolute MA
    if (msDelta == None): msDelta_AbsMA = None
    else:
        msDelta_prev = klineAccess[analysisCode][timestamp_previous]['MSDELTA']
        if (msDelta_prev == None): msDelta_AbsMA = None
        else:
            msDelta_AbsMA_prev = klineAccess[analysisCode][timestamp_previous]['MSDELTA_ABSMA']
            if (msDelta_AbsMA_prev == None): msDelta_AbsMA = abs(msDelta)*absoluteMA_kValue + abs(msDelta_prev) *(1-absoluteMA_kValue)
            else:                            msDelta_AbsMA = abs(msDelta)*absoluteMA_kValue + msDelta_AbsMA_prev*(1-absoluteMA_kValue)
    #---MSDelta Absolute MA Relative
    if   (msDelta_AbsMA == None): msDelta_AbsMARel = None
    elif (msDelta_AbsMA == 0):    msDelta_AbsMARel = 0
    else:                         msDelta_AbsMARel = round(msDelta/msDelta_AbsMA, 3)
    #Result formatting & saving
    mmacdResult = {'MAs': mas, 'MMACD': mmacd, 'SIGNAL': signal, 
                   'MSDELTA': msDelta, 'MSDELTA_ABSMA': msDelta_AbsMA, 'MSDELTA_ABSMAREL': msDelta_AbsMARel,
                   '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = mmacdResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    return ((signal_nSamples+1)*multiplier, maxMANSamples*multiplier)

def analysisGenerator_MMACDLONG(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode      = analysisParams['analysisCode']
    signal_nSamples   = analysisParams['signal_nSamples']
    signal_kValue     = 2/(signal_nSamples+1)
    multiplier        = analysisParams['multiplier']
    activatedMAs      = analysisParams['activatedMAs']
    activatedMAPairs  = analysisParams['activatedMAPairs']
    maxMANSamples     = analysisParams['maxMANSamples']
    absoluteMA_kValue = 2/(maxMANSamples+1)/10
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess[analysisCode]): _analysisCount = klineAccess[analysisCode][timestamp_previous]['_analysisCount']+1
    else:                                                 _analysisCount = 0
    timestamp_multipliedPrevious = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -(1+_analysisCount%multiplier))
    #MMACD Computation
    #---MAs Generation
    mas = dict()
    for ma_nSamples in activatedMAs:
        ma_kValue = 2/(ma_nSamples+1)
        if   (_analysisCount < (ma_nSamples-1)*multiplier): _ema = None
        elif (_analysisCount < ma_nSamples*multiplier):     _ema = (klineAccess['raw'][timestamp][KLINDEX_CLOSEPRICE]*ma_kValue) + (klineAccess['raw'][timestamp_multipliedPrevious][KLINDEX_CLOSEPRICE]       *(1-ma_kValue))
        else:                                               _ema = (klineAccess['raw'][timestamp][KLINDEX_CLOSEPRICE]*ma_kValue) + (klineAccess[analysisCode][timestamp_multipliedPrevious]['MAs'][ma_nSamples]*(1-ma_kValue))
        mas[ma_nSamples] = _ema
    #---MA Pair Delta Sum & MMACD
    if (_analysisCount < (maxMANSamples-1)*multiplier): mmacd = None
    else:                                               mmacd = sum([mas[maPair[0]]-mas[maPair[1]] for maPair in activatedMAPairs])
    #---Signal
    if   (_analysisCount < (maxMANSamples+signal_nSamples-1)*multiplier): signal = None
    elif (_analysisCount < (maxMANSamples+signal_nSamples)  *multiplier): signal = mmacd
    else:                                                                 signal = (mmacd*signal_kValue) + (klineAccess[analysisCode][timestamp_multipliedPrevious]['MMACD']*(1-signal_kValue))
    #---MSDelta
    if   (_analysisCount < (maxMANSamples+signal_nSamples-1)*multiplier): msDelta = None
    elif (_analysisCount < (maxMANSamples+signal_nSamples)  *multiplier): msDelta = 0
    else:                                                                 msDelta = mmacd-signal
    #---MSDelta Absolute MA
    if (msDelta == None): msDelta_AbsMA = None
    else:
        msDelta_prev = klineAccess[analysisCode][timestamp_previous]['MSDELTA']
        if (msDelta_prev == None): msDelta_AbsMA = None
        else:
            msDelta_AbsMA_prev = klineAccess[analysisCode][timestamp_previous]['MSDELTA_ABSMA']
            if (msDelta_AbsMA_prev == None): msDelta_AbsMA = abs(msDelta)*absoluteMA_kValue + abs(msDelta_prev) *(1-absoluteMA_kValue)
            else:                            msDelta_AbsMA = abs(msDelta)*absoluteMA_kValue + msDelta_AbsMA_prev*(1-absoluteMA_kValue)
    #---MSDelta Absolute MA Relative
    if   (msDelta_AbsMA == None): msDelta_AbsMARel = None
    elif (msDelta_AbsMA == 0):    msDelta_AbsMARel = 0
    else:                         msDelta_AbsMARel = round(msDelta/msDelta_AbsMA, 3)
    #Result formatting & saving
    mmacdResult = {'MAs': mas, 'MMACD': mmacd, 'SIGNAL': signal, 
                   'MSDELTA': msDelta, 'MSDELTA_ABSMA': msDelta_AbsMA, 'MSDELTA_ABSMAREL': msDelta_AbsMARel,
                   '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = mmacdResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    return ((signal_nSamples+1)*multiplier, maxMANSamples*multiplier)
    
def analysisGenerator_DMIxADX(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess[analysisCode]): _analysisCount = klineAccess[analysisCode][timestamp_previous]['_analysisCount']+1
    else:                                                 _analysisCount = 0
    #DMIxADX computation
    #---DM+, DM-, TR
    if (1 <= _analysisCount):
        kline_current = klineAccess['raw'][timestamp]
        kline_prev    = klineAccess['raw'][timestamp_previous]
        dmPlus = kline_current[KLINDEX_HIGHPRICE]-kline_prev[KLINDEX_HIGHPRICE]
        if (dmPlus < 0): dmPlus = 0.0
        dmMinus = kline_prev[KLINDEX_LOWPRICE]-kline_current[KLINDEX_LOWPRICE]
        if (dmMinus < 0): dmMinus = 0.0
        tr = max(abs(kline_current[KLINDEX_HIGHPRICE]-kline_current[KLINDEX_LOWPRICE]),
                 abs(kline_current[KLINDEX_HIGHPRICE]-kline_prev[KLINDEX_CLOSEPRICE]),
                 abs(kline_current[KLINDEX_LOWPRICE] -kline_prev[KLINDEX_CLOSEPRICE]))
    else:
        dmPlus  = None
        dmMinus = None
        tr      = None
    #---DM+Sum, DM-Sum, TRSum
    if (nSamples == _analysisCount):
        timestampsList = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False, mrktReg = mrktRegTS)
        dmPlusSum  = 0
        dmMinusSum = 0
        trSum      = 0
        for ts in timestampsList:
            if (ts == timestamp):
                dmPlusSum  += dmPlus
                dmMinusSum += dmMinus
                trSum      += tr
            else:
                dmixadx_this = klineAccess[analysisCode][ts]
                dmPlusSum  += dmixadx_this['DM+']
                dmMinusSum += dmixadx_this['DM-']
                trSum      += dmixadx_this['TR']
    elif (nSamples < _analysisCount):
        timestampsList = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False, mrktReg = mrktRegTS)
        dmPlusSum_prev  = klineAccess[analysisCode][timestamp_previous]['DM+Sum']
        dmMinusSum_prev = klineAccess[analysisCode][timestamp_previous]['DM-Sum']
        trSum_prev      = klineAccess[analysisCode][timestamp_previous]['TRSum']
        dmPlusSum  = dmPlusSum_prev -dmPlusSum_prev /nSamples+dmPlus
        dmMinusSum = dmMinusSum_prev-dmMinusSum_prev/nSamples+dmMinus
        trSum      = trSum_prev     -trSum_prev     /nSamples+tr
    else:
        dmPlusSum  = None
        dmMinusSum = None
        trSum      = None
    #---DI+, DI-, DX
    if (nSamples <= _analysisCount):
        if ((dmPlusSum == 0.0) and (trSum == 0.0)):  diPlus  = 0.0
        else:                                        diPlus  = dmPlusSum/trSum
        if ((dmMinusSum == 0.0) and (trSum == 0.0)): diMinus = 0.0
        else:                                        diMinus = dmMinusSum/trSum
        if (diPlus+diMinus == 0): dx = 0.0
        else:                     dx = abs(diPlus-diMinus)/(diPlus+diMinus)
    else:
        diPlus  = None
        diMinus = None
        dx      = None
    #---ADX
    if (_analysisCount < nSamples*2-1):
        dxSum = None
        adx   = None
    elif (nSamples*2-1 <= _analysisCount):
        dxSum = 0
        for ts in timestampsList: 
            if (ts == timestamp): dxSum += dx
            else:                 dxSum += klineAccess[analysisCode][ts]['DX']
        adx = dxSum/nSamples
    #---DMIxADX
    if ((diPlus != None) and (diMinus != None) and (adx != None)): dmixadx = (diPlus-diMinus)*adx
    else:                                                          dmixadx = None
    #---DMIxADX All-Time High
    if (dmixadx == None): dmixadx_absAth = None
    else:
        dmixadx_absAth_prev = klineAccess[analysisCode][timestamp_previous]['DMIxADX_ABSATH']
        if (dmixadx_absAth_prev == None): dmixadx_absAth = abs(dmixadx)
        else:
            dmixadx_abs = abs(dmixadx)
            if (dmixadx_absAth_prev < dmixadx_abs): dmixadx_absAth = dmixadx_abs
            else:                                   dmixadx_absAth = dmixadx_absAth_prev
    #---DMIxADX All-Time-High Relative
    if (dmixadx_absAth == None): dmixadx_absAthRel = None
    else:                        
        if (0 < dmixadx_absAth): dmixadx_absAthRel = round(dmixadx/dmixadx_absAth, 5)
        else:                    dmixadx_absAthRel = 0
    #Result formatting & saving
    dmixadxResult = {'DM+': dmPlus, 'DM-': dmMinus, 'TR': tr, 
                     'DM+Sum': dmPlusSum, 'DM-Sum': dmMinusSum, 'TRSum': trSum, 'DI+': diPlus, 'DI-': diMinus,
                     'DX': dx, 'ADX': adx, 
                     'DMIxADX': dmixadx, 'DMIxADX_ABSATH': dmixadx_absAth, 'DMIxADX_ABSATHREL': dmixadx_absAthRel,
                     '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = dmixadxResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    return (nSamples, 2)
    
def analysisGenerator_MFI(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess[analysisCode]): _analysisCount = klineAccess[analysisCode][timestamp_previous]['_analysisCount']+1
    else:                                                 _analysisCount = 0
    #MFI computation
    kline = klineAccess['raw'][timestamp]
    #---TP
    tp = (kline[KLINDEX_HIGHPRICE]+kline[KLINDEX_LOWPRICE]+kline[KLINDEX_CLOSEPRICE])/3 #TP: Typical Price
    #---MF
    mf = tp*kline[KLINDEX_VOLBASE]                                                      #MF: Money Flow
    #---MFI
    if (_analysisCount < nSamples): mfi = None
    else:
        timestampsList = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples+1, direction = False, mrktReg = mrktRegTS)
        mfPlusSum  = 0
        mfMinusSum = 0
        for tsIndex in range (nSamples-1, -1, -1):
            if (tsIndex == 0): tp_current = tp;                                                       mf_current = mf
            else:              tp_current = klineAccess[analysisCode][timestampsList[tsIndex]]['TP']; mf_current = klineAccess[analysisCode][timestampsList[tsIndex]]['MF']
            tp_prev = klineAccess[analysisCode][timestampsList[tsIndex+1]]['TP']
            tpDelta = tp_current-tp_prev
            if (tpDelta < 0):   mfMinusSum += mf_current
            elif (0 < tpDelta): mfPlusSum  += mf_current
        #MFR (Money Flow Ratio)
        if (mfMinusSum == 0): mfr = None
        else:                 mfr = mfPlusSum/mfMinusSum
        #MFI (Money Flow Index)
        if (mfr == None): mfi = 1.0
        else:             mfi = 1.0-(1.0/(1.0+mfr))
    #---MFI All-Time High
    if (mfi == None): mfi_absAth = None
    else:
        mfi_absAth_prev = klineAccess[analysisCode][timestamp_previous]['MFI_ABSATH']
        if (mfi_absAth_prev == None): mfi_absAth = abs(mfi)
        else:
            mfi_abs = abs(mfi)
            if (mfi_absAth_prev < mfi_abs): mfi_absAth = mfi_abs
            else:                           mfi_absAth = mfi_absAth_prev
    #---MFI All-Time-High Relative
    if (mfi_absAth == None): mfi_absAthRel = None
    else:                    
        if (0 < mfi_absAth): mfi_absAthRel = round(mfi/mfi_absAth, 5)
        else:                mfi_absAthRel = 0.0
    #Result formatting & saving
    mfiResult = {'TP': tp, 'MF': mf, 
                 'MFI': mfi, 'MFI_ABSATH': mfi_absAth, 'MFI_ABSATHREL': mfi_absAthRel,
                 '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = mfiResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    return (nSamples+1, 1)

def analysisGenerator_TPD(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']

    klineAccess_raw = klineAccess['raw']
    kline = klineAccess_raw[timestamp]
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    tpd_prev    = klineAccess[analysisCode].get(timestamp_previous, None)
    analysisCount = 0 if tpd_prev is None else tpd_prev['_analysisCount']+1

    #das
    kl_hp = kline[KLINDEX_HIGHPRICE]
    kl_lp = kline[KLINDEX_LOWPRICE]
    kl_cp = kline[KLINDEX_CLOSEPRICE]

    #Result formatting & saving
    tpdResult = {'BIAS': 1, 'SAMPLES': 1,
                 #Process
                 '_analysisCount': analysisCount}
    klineAccess[analysisCode][timestamp] = tpdResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    return (2, 2)

def updateBidsAndAsks(bidsAndAsks, newBidsAndAsks, oldestComputed, latestComputed, analysisLines):
    _newOldestComputed = oldestComputed
    _newLatestComputed = latestComputed
    _updated           = list()
    #Depth Update
    _newBids = newBidsAndAsks[0]
    _newAsks = newBidsAndAsks[1]
    _baa_depth = bidsAndAsks['depth']
    for _pl in _newBids:
        if ((_pl not in _baa_depth) or (_baa_depth[_pl][0] == 'ASK') or (_baa_depth[_pl][1] != _newBids[_pl])): _baa_depth[_pl] = ('BID', _newBids[_pl])
    for _pl in _newAsks:
        if ((_pl not in _baa_depth) or (_baa_depth[_pl][0] == 'BID') or (_baa_depth[_pl][1] != _newAsks[_pl])): _baa_depth[_pl] = ('ASK', _newAsks[_pl])
    #WOI Computation
    #---Midpoint Search
    _pl_bid_max = float('-inf')
    _pl_ask_min = float('inf')
    for _pl in _baa_depth:
        _d = _baa_depth[_pl]
        if   ((_d[0] == 'BID') and (_pl_bid_max < _pl)): _pl_bid_max = _pl
        elif ((_d[0] == 'ASK') and (_pl < _pl_ask_min)): _pl_ask_min = _pl
    _pl_mid = (_pl_bid_max+_pl_ask_min)/2
    #---Weighted WOI Bid & Ask
    _woiSum_bid = 0
    _woiSum_ask = 0
    for _pl in _baa_depth:
        _d = _baa_depth[_pl]
        _distanceIndex = abs((_pl-_pl_mid)/_pl_mid)
        _weightIndex   = math.exp(-WOIALPHA*_distanceIndex)
        _weightedDepth = _weightIndex*_d[1]
        if   (_d[0] == 'BID'): _woiSum_bid += _weightedDepth
        elif (_d[0] == 'ASK'): _woiSum_ask += _weightedDepth
    #---WOI
    _woi = _woiSum_bid-_woiSum_ask
    #---Finally
    _t_intervalOpen = int(time.time()/BIDSANDASKSSAMPLINGINTERVAL_S)*BIDSANDASKSSAMPLINGINTERVAL_S
    bidsAndAsks['WOI'][_t_intervalOpen] = _woi
    #Control Variables Update
    if (_newOldestComputed is None): _newOldestComputed = _t_intervalOpen
    _updated.append((1, 'WOI', _t_intervalOpen))
    #Missing WOI Fill (With the last computed WOI)
    _missingFilledTTs = list()
    if ((_newLatestComputed is not None) and (_newLatestComputed+BIDSANDASKSSAMPLINGINTERVAL_S < _t_intervalOpen)): 
        for _tt in range (_newLatestComputed+BIDSANDASKSSAMPLINGINTERVAL_S, _t_intervalOpen, BIDSANDASKSSAMPLINGINTERVAL_S): 
            bidsAndAsks['WOI'][_tt] = bidsAndAsks['WOI'][_newLatestComputed]
            _updated.append((1, 'WOI', _tt))
            _missingFilledTTs.append(_tt)
    _newLatestComputed = _t_intervalOpen
    #NES WOI & Filtered Gradient Compuation (If needed)
    for _woiType, _nSamples, _sigma in analysisLines:
        for _tt in _missingFilledTTs+[_t_intervalOpen,]:
            generateAnalysis_WOI(bidsAndAsks = bidsAndAsks, woiType = _woiType, nSamples = _nSamples, sigma = _sigma, targetTime = _tt)
            _updated.append((1, _woiType, _tt))
    #BIDSANDASKS Samples Length Control
    _n_samples  = len(bidsAndAsks['WOI'])
    _n_toRemove = _n_samples-NMAXBIDSANDASKSSAMPLES
    for _ in range (_n_toRemove):
        del bidsAndAsks['WOI'][_newOldestComputed]
        del bidsAndAsks['WOI_GD'][_newOldestComputed]
        _updated.append((-1, None, _newOldestComputed))
        _newOldestComputed += BIDSANDASKSSAMPLINGINTERVAL_S
    #Return
    return _newOldestComputed, _newLatestComputed, _updated

def generateAnalysis_WOI(bidsAndAsks, woiType, nSamples, sigma, targetTime):
    _kValue = 2/(nSamples+1)
    #EMA Compute
    if (targetTime-BIDSANDASKSSAMPLINGINTERVAL_S in bidsAndAsks[woiType]): _ema = (bidsAndAsks['WOI'][targetTime]*_kValue) + (bidsAndAsks[woiType][targetTime-BIDSANDASKSSAMPLINGINTERVAL_S][0]*(1-_kValue))
    else:                                                                  _ema = bidsAndAsks['WOI'][targetTime]
    #Filtered
    _sampleTT_beg = targetTime-BIDSANDASKSSAMPLINGINTERVAL_S*(nSamples-1)
    if (_sampleTT_beg in bidsAndAsks[woiType]):
        _WOISamples = [bidsAndAsks[woiType][_tt][0] for _tt in range (_sampleTT_beg, targetTime, BIDSANDASKSSAMPLINGINTERVAL_S)] + [_ema,]
        _WOISamples_gaussianFiltered = scipy.ndimage.gaussian_filter1d(input = _WOISamples, sigma = sigma)
        _gFiltered = _WOISamples_gaussianFiltered[-1]
    else: _gFiltered = None
    #Update
    bidsAndAsks[woiType][targetTime] = (_ema, _gFiltered)

def updateAggTrades(aggTrades, newAggTrade, oldestComputed, latestComputed, analysisLines):
    _newOldestComputed = oldestComputed
    _newLatestComputed = latestComputed
    _updated           = list()
    _aggTrade_t = newAggTrade[0] #Trade Time (in seconds)
    _aggTrade_p = newAggTrade[1] #Price
    _aggTrade_q = newAggTrade[2] #Quantity
    _aggTrade_m = newAggTrade[3] #Is buy? (False if sell)
    #---Interval T
    _t_intervalOpen = int(_aggTrade_t/AGGTRADESAMPLINGINTERVAL_S)*AGGTRADESAMPLINGINTERVAL_S
    #---New
    _agt_volumes = aggTrades['volumes']
    _agt_volumes['samples'].append((_aggTrade_t, _aggTrade_q, _aggTrade_m))
    if (_aggTrade_m == True): _agt_volumes['buy']  += _aggTrade_q
    else:                     _agt_volumes['sell'] += _aggTrade_q
    #---Expired
    while (0 < len(_agt_volumes['samples'])):
        _sample = _agt_volumes['samples'][0]
        if (_sample[0] < _t_intervalOpen):
            if (_sample[2] == True): _agt_volumes['buy']  -= _sample[1]
            else:                    _agt_volumes['sell'] -= _sample[1]
            _agt_volumes['samples'].pop(0)
        else: break
    #NES Update
    _nes = _agt_volumes['buy']-_agt_volumes['sell']
    aggTrades['NES'][_t_intervalOpen] = _nes
    if (_newOldestComputed is None): _newOldestComputed = _t_intervalOpen
    _updated.append((1, 'NES', _t_intervalOpen))
    #Missing NES Fill
    _missingFilledTTs = list()
    if ((_newLatestComputed is not None) and (_newLatestComputed+AGGTRADESAMPLINGINTERVAL_S != _t_intervalOpen)):
        for _tt in range (_newLatestComputed+AGGTRADESAMPLINGINTERVAL_S, _t_intervalOpen, AGGTRADESAMPLINGINTERVAL_S): 
            aggTrades['NES'][_tt] = 0
            _updated.append((1, 'NES', _tt))
            _missingFilledTTs.append(_tt)
    _newLatestComputed = _t_intervalOpen
    #NES EMA & Filtered Gradient Compuation (If needed)
    for _nesType, _nSamples, _sigma in analysisLines:
        for _tt in _missingFilledTTs+[_t_intervalOpen,]:
            generateAnalysis_NES(aggTrades = aggTrades, nesType = _nesType, nSamples = _nSamples, sigma = _sigma, targetTime = _tt)
            _updated.append((1, _nesType, _tt))
    #AggTrades Samples Length Control
    _n_samples  = len(aggTrades['NES'])
    _n_toRemove = _n_samples-NMAXAGGTRADESSAMPLES
    _lineTargets = [_key for _key in aggTrades if (_key != 'volumes')]
    for _ in range (_n_toRemove):
        for _nesType in _lineTargets:
            del aggTrades[_nesType][_newOldestComputed]
        _updated.append((-1, None, _newOldestComputed))
        _newOldestComputed += AGGTRADESAMPLINGINTERVAL_S
    #Return
    return _newOldestComputed, _newLatestComputed, _updated

def generateAnalysis_NES(aggTrades, nesType, nSamples, sigma, targetTime):
    _kValue = 2/(nSamples+1)
    #EMA Compute
    if (targetTime-AGGTRADESAMPLINGINTERVAL_S in aggTrades[nesType]): _ema = (aggTrades['NES'][targetTime]*_kValue) + (aggTrades[nesType][targetTime-AGGTRADESAMPLINGINTERVAL_S][0]*(1-_kValue))
    else:                                                             _ema = aggTrades['NES'][targetTime]
    #Filtered Gradient
    _sampleTT_beg = targetTime-AGGTRADESAMPLINGINTERVAL_S*(nSamples-1)
    if (_sampleTT_beg in aggTrades[nesType]):
        _NESSamples = [aggTrades[nesType][_tt][0] for _tt in range (_sampleTT_beg, targetTime, AGGTRADESAMPLINGINTERVAL_S)] + [_ema,]
        _NESSamples_gaussianFiltered = scipy.ndimage.gaussian_filter1d(input = _NESSamples, sigma = sigma)
        _gFiltered = _NESSamples_gaussianFiltered[-1]
    else: _gFiltered = None
    #Update
    aggTrades[nesType][targetTime] = (_ema, _gFiltered)

__analysisGenerators = {'SMA':        analysisGenerator_SMA,
                        'WMA':        analysisGenerator_WMA,
                        'EMA':        analysisGenerator_EMA,
                        'PSAR':       analysisGenerator_PSAR,
                        'BOL':        analysisGenerator_BOL,
                        'IVP':        analysisGenerator_IVP,
                        'SWING':      analysisGenerator_SWING,
                        'VOL':        analysisGenerator_VOL,
                        'NNA':        analysisGenerator_NNA,
                        'MMACDSHORT': analysisGenerator_MMACDSHORT,
                        'MMACDLONG':  analysisGenerator_MMACDLONG,
                        'DMIxADX':    analysisGenerator_DMIxADX,
                        'MFI':        analysisGenerator_MFI}
def analysisGenerator(analysisType, **params): 
    return __analysisGenerators[analysisType](**params)
def constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(currencyAnalysisConfiguration):
    cac = currencyAnalysisConfiguration
    cap = dict()
    invalidLines = defaultdict(list)
    if cac['SMA_Master']:
        for lineIndex in range (atmEta_Constants.NLINES_SMA):
            analysisCode = f'SMA_{lineIndex}'
            #[1]: Check Line Existence & Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue
            #[2]: nSamples
            nSamples = cac[f'{analysisCode}_NSamples']
            if   type(nSamples) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < nSamples:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if analysisCode in invalidLines: continue
            #[3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex':    lineIndex,
                                 'nSamples':     nSamples}
    
    if cac['WMA_Master']:
        for lineIndex in range (atmEta_Constants.NLINES_WMA):
            analysisCode = f'WMA_{lineIndex}'
            #[1]: Check Line Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue
            #[2]: nSamples
            nSamples = cac[f'{analysisCode}_NSamples']
            if   type(nSamples) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < nSamples:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if analysisCode in invalidLines: continue
            #[3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex': lineIndex,
                                 'nSamples':  nSamples}
    
    if cac['EMA_Master']:
        for lineIndex in range (atmEta_Constants.NLINES_EMA):
            analysisCode = f'EMA_{lineIndex}'
            #[1]: Check Line Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue
            #[2]: Parameters
            nSamples = cac[f'{analysisCode}_NSamples']
            if   type(nSamples) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < nSamples:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if analysisCode in invalidLines: continue
            #[3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex': lineIndex,
                                 'nSamples':  nSamples}
    
    if cac['PSAR_Master']:
        for lineIndex in range (atmEta_Constants.NLINES_PSAR):
            analysisCode = f'PSAR_{lineIndex}'
            #[1]: Check Line Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue
            #[2]: Parameters
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
            if analysisCode in invalidLines: continue
            #[3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex':    lineIndex,
                                 'start':        AF_initial,
                                 'acceleration': AF_acceleration,
                                 'maximum':      AF_maximum}
    
    if cac['BOL_Master']:
        for lineIndex in range (atmEta_Constants.NLINES_BOL):
            analysisCode = f'BOL_{lineIndex}'
            #[1]: Check Line Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue
            #[2]: Parameters
            nSamples  = cac[f'{analysisCode}_NSamples']
            bandWidth = cac[f'{analysisCode}_BandWidth']
            maType    = cac['BOL_MAType']
            if   type(nSamples) is not int:           invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < nSamples:                    invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if   not type(bandWidth) in (int, float): invalidLines[analysisCode].append("bandWidth: Must be type 'int' or 'float'")
            elif not (0 < bandWidth):                 invalidLines[analysisCode].append("bandWidth: Must be greater than 0")
            if   type(maType) is not str:             invalidLines[analysisCode].append("BOL_MAType: Must be type 'str'")
            elif maType not in ('SMA', 'WMA', 'EMA'): invalidLines[analysisCode].append("BOL_MAType: Must be 'SMA', 'WMA', or 'EMA'")
            if analysisCode in invalidLines: continue
            #[3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex':    lineIndex,
                                 'MAType':       maType,
                                 'nSamples':     nSamples,
                                 'bandWidth':    bandWidth}
    
    if cac['IVP_Master']:
        analysisCode = 'IVP'
        #[1]: Parameters
        nSamples    = cac[f'{analysisCode}_NSamples']
        gammaFactor = cac[f'{analysisCode}_GammaFactor']
        deltaFactor = cac[f'{analysisCode}_DeltaFactor']
        if   type(nSamples) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
        elif not 1 < nSamples:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
        if   not type(gammaFactor) in (int, float): invalidLines[analysisCode].append("gammaFactor: Must be type 'int' or 'float'")
        elif not (0.001 <= gammaFactor):            invalidLines[analysisCode].append("gammaFactor: Must be greater than or equal to 0.001")
        if   not type(deltaFactor) in (int, float): invalidLines[analysisCode].append("deltaFactor: Must be type 'int' or 'float'")
        elif not (0.01 <= deltaFactor):             invalidLines[analysisCode].append("deltaFactor: Must be greater than or equal to 0.01")
        #[3]: Analysis Params
        if analysisCode not in invalidLines:
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'nSamples':    nSamples,
                                 'gammaFactor': gammaFactor,
                                 'deltaFactor': deltaFactor}
    
    if cac['SWING_Master']:
        for lineIndex in range (atmEta_Constants.NLINES_SWING):
            analysisCode = f'SWING_{lineIndex}'
            #[1]: Check Line Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue
            #[2]: Parameters
            swingRange = cac[f'{analysisCode}_SwingRange']
            if   not type(swingRange) in (int, float): invalidLines[analysisCode].append("swingRange: Must be type 'int' or 'float'")
            elif not (0.0001 <= swingRange):           invalidLines[analysisCode].append("swingRange: Must be greater than or equal to 0.0001")
            if analysisCode in invalidLines: continue
            #[3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex':    lineIndex,
                                 'swingRange':   swingRange}
    
    if cac['VOL_Master']:
        for lineIndex in range (atmEta_Constants.NLINES_VOL):
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
    
    if cac['NNA_Master']:
        for lineIndex in range (atmEta_Constants.NLINES_NNA):
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
                
    if cac['MMACDSHORT_Master']:
        analysisCode = 'MMACDSHORT'
        #[1]: Multiplier
        signal_nSamples = cac[f'{analysisCode}_SignalNSamples']
        multiplier      = cac[f'{analysisCode}_Multiplier']
        if   type(signal_nSamples) is not int: invalidLines[analysisCode].append("signal_nSamples: Must be type 'int'")
        elif not 1 < signal_nSamples:          invalidLines[analysisCode].append("signal_nSamples: Must be greater than 1")
        if   type(multiplier) is not int:      invalidLines[analysisCode].append("multiplier: Must be type 'int'")
        elif not 0 < multiplier:               invalidLines[analysisCode].append("multiplier: Must be greater than 0")
        #[2]: Activated MAs
        activatedMAs = []
        for lineIndex in range (atmEta_Constants.NLINES_MMACDSHORT):
            #[1]: Check Line Active
            lineActive = cac.get(f'MMACDSHORT_MA{lineIndex}_LineActive', False)
            if not lineActive: continue
            #[2]: Parameters
            nSamples = cac[f'MMACDSHORT_MA{lineIndex}_NSamples']
            if   type(nSamples) is not int: invalidLines[analysisCode].append(f"MA{lineIndex}_nSamples: Must be type 'int'")
            elif not 1 < nSamples:          invalidLines[analysisCode].append(f"MA{lineIndex}_nSamples: Must be greater than 1")
            else: activatedMAs.append(nSamples)
        #[3]: Activated MAs Sort & Params Update
        if (2 <= len(activatedMAs)) and (analysisCode not in invalidLines):
            activatedMAs.sort()
            activatedMAPairs = [(activatedMAs[maptIndex_S], activatedMAs[maptIndex_L]) for maptIndex_S in range (0, len(activatedMAs)-1) for maptIndex_L in range (maptIndex_S+1, len(activatedMAs))]
            maxMANSamples = max(activatedMAs)
            cap['MMACDSHORT'] = {'analysisCode': analysisCode,
                                 'signal_nSamples':  signal_nSamples,
                                 'multiplier':       multiplier,
                                 'activatedMAs':     activatedMAs,
                                 'activatedMAPairs': activatedMAPairs,
                                 'maxMANSamples':    maxMANSamples}
            
    if cac['MMACDLONG_Master']:
        analysisCode = 'MMACDLONG'
        #[1]: Multiplier
        signal_nSamples = cac[f'{analysisCode}_SignalNSamples']
        multiplier      = cac[f'{analysisCode}_Multiplier']
        if   type(signal_nSamples) is not int: invalidLines[analysisCode].append("signal_nSamples: Must be type 'int'")
        elif not 1 < signal_nSamples:          invalidLines[analysisCode].append("signal_nSamples: Must be greater than 1")
        if   type(multiplier) is not int:      invalidLines[analysisCode].append("multiplier: Must be type 'int'")
        elif not 0 < multiplier:               invalidLines[analysisCode].append("multiplier: Must be greater than 0")
        #[2]: Activated MAs
        activatedMAs = []
        for lineIndex in range (atmEta_Constants.NLINES_MMACDLONG):
            #[1]: Check Line Active
            lineActive = cac.get(f'MMACDLONG_MA{lineIndex}_LineActive', False)
            if not lineActive: continue
            #[2]: Parameters
            nSamples = cac[f'MMACDLONG_MA{lineIndex}_NSamples']
            if   type(nSamples) is not int: invalidLines[analysisCode].append(f"MA{lineIndex}_nSamples: Must be type 'int'")
            elif not 1 < nSamples:          invalidLines[analysisCode].append(f"MA{lineIndex}_nSamples: Must be greater than 1")
            else: activatedMAs.append(nSamples)
        #[3]: Activated MAs Sort & Params Update
        if (2 <= len(activatedMAs)) and (analysisCode not in invalidLines):
            activatedMAs.sort()
            activatedMAPairs = [(activatedMAs[maptIndex_S], activatedMAs[maptIndex_L]) for maptIndex_S in range (0, len(activatedMAs)-1) for maptIndex_L in range (maptIndex_S+1, len(activatedMAs))]
            maxMANSamples = max(activatedMAs)
            cap['MMACDLONG'] = {'analysisCode': analysisCode,
                                'signal_nSamples':  signal_nSamples,
                                'multiplier':       multiplier,
                                'activatedMAs':     activatedMAs,
                                'activatedMAPairs': activatedMAPairs,
                                'maxMANSamples':    maxMANSamples}
            
    if cac['DMIxADX_Master']:
        for lineIndex in range (atmEta_Constants.NLINES_DMIxADX):
            analysisCode = f'DMIxADX_{lineIndex}'
            #[1]: Check Line Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue
            #[2]: Parameters
            nSamples = cac[f'{analysisCode}_NSamples']
            if   type(nSamples) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < nSamples:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if analysisCode in invalidLines: continue
            #[3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex':    lineIndex,
                                 'nSamples':     nSamples}
    
    if cac['MFI_Master']:
        for lineIndex in range (atmEta_Constants.NLINES_MFI):
            analysisCode = f'MFI_{lineIndex}'
            #[1]: Check Line Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue
            #[2]: Parameters
            nSamples = cac[f'{analysisCode}_NSamples']
            if   type(nSamples) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < nSamples:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if analysisCode in invalidLines: continue
            #[3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex': lineIndex,
                                 'nSamples':  nSamples}
    
    #Return the constructed analysis params if no invalid line exists
    if invalidLines:
        cap = None
    return cap, invalidLines





def linearizeAnalysis_SMA(analysisCode, analysisResult):
    lRes = {f'{analysisCode}_SMA': analysisResult['SMA']}
    return lRes

def linearizeAnalysis_WMA(analysisCode, analysisResult):
    lRes = {f'{analysisCode}_WMA': analysisResult['WMA']}
    return lRes

def linearizeAnalysis_EMA(analysisCode, analysisResult):
    lRes = {f'{analysisCode}_EMA': analysisResult['EMA']}
    return lRes

def linearizeAnalysis_PSAR(analysisCode, analysisResult):
    psar = analysisResult['PSAR']
    if psar is None:
        lRes = {f'{analysisCode}_PSAR': None,
                f'{analysisCode}_DCC':  None}
    else:
        lRes = {f'{analysisCode}_PSAR': analysisResult['PSAR'],
                f'{analysisCode}_DCC':  analysisResult['DCC']}
    return lRes

def linearizeAnalysis_BOL(analysisCode, analysisResult):
    bol = analysisResult['BOL']
    if bol is None:
        lRes = {f'{analysisCode}_BOLLOW':  None,
                f'{analysisCode}_BOLHIGH': None,
                f'{analysisCode}_MA':      None}
    else:
        lRes = {f'{analysisCode}_BOLLOW':  bol[0],
                f'{analysisCode}_BOLHIGH': bol[1],
                f'{analysisCode}_MA':      analysisResult['MA']}
    return lRes

def linearizeAnalysis_IVP(analysisCode, analysisResult):
    nearBoundaries = analysisResult['volumePriceLevelProfile_NearBoundaries']
    lRes = {f'{analysisCode}_NB{nbIndex}': nearBoundaries[nbIndex] for nbIndex in range (len(nearBoundaries))}
    return lRes

def linearizeAnalysis_SWING(analysisCode, analysisResult):
    swings = analysisResult['SWINGS']
    if swings:
        ls_TS, ls_Price, ls_Type = swings[-1]
        lRes = {f'{analysisCode}_LSTIMESTAMP': ls_TS,
                f'{analysisCode}_LSPRICE':     ls_Price,
                f'{analysisCode}_LSTYPE':      ls_Type}
    else:
        lRes = {f'{analysisCode}_LSTIMESTAMP': None,
                f'{analysisCode}_LSPRICE':     None,
                f'{analysisCode}_LSTYPE':      None}
    return lRes

def linearizeAnalysis_VOL(analysisCode, analysisResult):
    lRes = {f'{analysisCode}_MABASE':    analysisResult['MA_BASE'],
            f'{analysisCode}_MAQUOTE':   analysisResult['MA_QUOTE'],
            f'{analysisCode}_MABASETB':  analysisResult['MA_BASETB'],
            f'{analysisCode}_MAQUOTETB': analysisResult['MA_QUOTETB']}
    return lRes

def linearizeAnalysis_NNA(analysisCode, analysisResult):
    lRes = {f'{analysisCode}_NNA': analysisResult['NNA']}
    return lRes

def linearizeAnalysis_MMACDSHORT(analysisCode, analysisResult):
    lRes = {f'{analysisCode}_MSDELTA':         analysisResult['MSDELTA'],
            f'{analysisCode}_MSDELTAABSMA':    analysisResult['MSDELTA_ABSMA'],
            f'{analysisCode}_MSDELTAABSMAREL': analysisResult['MSDELTA_ABSMAREL']}
    return lRes

def linearizeAnalysis_MMACDLONG(analysisCode, analysisResult):
    lRes = {f'{analysisCode}_MSDELTA':         analysisResult['MSDELTA'],
            f'{analysisCode}_MSDELTAABSMA':    analysisResult['MSDELTA_ABSMA'],
            f'{analysisCode}_MSDELTAABSMAREL': analysisResult['MSDELTA_ABSMAREL']}
    return lRes

def linearizeAnalysis_DMIxADX(analysisCode, analysisResult):
    lRes = {f'{analysisCode}_ABSATHREL': analysisResult['DMIxADX_ABSATHREL']}
    return lRes

def linearizeAnalysis_MFI(analysisCode, analysisResult):
    lRes = {f'{analysisCode}_ABSATHREL': analysisResult['MFI_ABSATHREL']}
    return lRes

__ANALYSISLINEARIZERS = {'SMA':        linearizeAnalysis_SMA,
                         'WMA':        linearizeAnalysis_WMA,
                         'EMA':        linearizeAnalysis_EMA,
                         'PSAR':       linearizeAnalysis_PSAR,
                         'BOL':        linearizeAnalysis_BOL,
                         'IVP':        linearizeAnalysis_IVP,
                         'SWING':      linearizeAnalysis_SWING,
                         'VOL':        linearizeAnalysis_VOL,
                         'NNA':        linearizeAnalysis_NNA,
                         'MMACDSHORT': linearizeAnalysis_MMACDSHORT,
                         'MMACDLONG':  linearizeAnalysis_MMACDLONG,
                         'DMIxADX':    linearizeAnalysis_DMIxADX,
                         'MFI':        linearizeAnalysis_MFI}
def linearizeAnalysis(klineAccess, analysisPairs, timestamp):
    aLinearized = {}
    als         = __ANALYSISLINEARIZERS
    for aType, aCode in analysisPairs: 
        aLinearized_this = als[aType](analysisCode = aCode, analysisResult = klineAccess[aCode][timestamp])
        aLinearized.update(aLinearized_this)
    return aLinearized
