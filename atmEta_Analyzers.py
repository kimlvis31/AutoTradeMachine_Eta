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
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess[analysisCode]): _analysisCount = klineAccess[analysisCode][timestamp_previous]['_analysisCount']+1
    else:                                                 _analysisCount = 0
    #SMA computation
    if (_analysisCount < nSamples-1):
        sma = None
    elif (nSamples-1 == _analysisCount):
        timestampsList = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False, mrktReg = mrktRegTS)
        priceSum = 0
        for i in range (nSamples): priceSum += klineAccess['raw'][timestampsList[i]][KLINDEX_CLOSEPRICE]
        sma = priceSum / nSamples
    elif (nSamples-1 < _analysisCount):
        timestamp_expired = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -nSamples)
        previousPriceSum = klineAccess[analysisCode][timestamp_previous]['SMA']*nSamples
        newPriceSum      = previousPriceSum - klineAccess['raw'][timestamp_expired][KLINDEX_CLOSEPRICE] + klineAccess['raw'][timestamp][KLINDEX_CLOSEPRICE]
        sma = newPriceSum / nSamples
    #Result formatting & saving
    smaResult = {'SMA': sma, '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = smaResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    return (2, nSamples)

def analysisGenerator_WMA(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess[analysisCode]): _analysisCount = klineAccess[analysisCode][timestamp_previous]['_analysisCount']+1
    else:                                                 _analysisCount = 0
    #WMA computation
    if (_analysisCount < nSamples-1):
        wma = None
    elif (nSamples-1 <= _analysisCount):
        timestampsList = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False, mrktReg = mrktRegTS)
        baseSum     = nSamples*(nSamples+1)/2
        weightedSum = 0
        for index, ts in enumerate(timestampsList): weightedSum += klineAccess['raw'][ts][KLINDEX_CLOSEPRICE]*(nSamples-index)
        wma = weightedSum/baseSum
    #Result formatting & saving
    wmaResult = {'WMA': wma, '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = wmaResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    return (2, nSamples)

def analysisGenerator_EMA(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode = analysisParams['analysisCode']
    kValue       = 2/(analysisParams['nSamples']+1)
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess[analysisCode]): _analysisCount = klineAccess[analysisCode][timestamp_previous]['_analysisCount']+1
    else:                                                 _analysisCount = 0
    #EMA computation
    if   (_analysisCount == 0): ema = None
    elif (_analysisCount == 1): ema = (klineAccess['raw'][timestamp][KLINDEX_CLOSEPRICE]*kValue) + (klineAccess['raw'][timestamp_previous][KLINDEX_CLOSEPRICE]*(1-kValue))
    elif (1 < _analysisCount):  ema = (klineAccess['raw'][timestamp][KLINDEX_CLOSEPRICE]*kValue) + (klineAccess[analysisCode][timestamp_previous]['EMA']      *(1-kValue))
    #Result formatting & saving
    emaResult = {'EMA': ema, '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = emaResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    return (2, 2)

def analysisGenerator_PSAR(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode      = analysisParams['analysisCode']
    psar_start        = analysisParams['start']
    psar_acceleration = analysisParams['acceleration']
    psar_maximum      = analysisParams['maximum']
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess[analysisCode]): _analysisCount = klineAccess[analysisCode][timestamp_previous]['_analysisCount']+1
    else:                                                 _analysisCount = 0
    #PSAR computation
    if (_analysisCount == 0):
        pd          = None
        pd_reversed = None
        af          = None
        ep          = None
        psar        = None
        dcc         = None
    elif (_analysisCount == 1):
        kline_previous = klineAccess['raw'][timestamp_previous]
        kline_current = klineAccess['raw'][timestamp]
        p_high_previous = kline_previous[KLINDEX_HIGHPRICE]
        p_high_current  = kline_current[KLINDEX_HIGHPRICE]
        if (p_high_previous <= p_high_current): p_high_delta = p_high_current-p_high_previous
        else:                                   p_high_delta = 0
        p_low_previous = kline_previous[KLINDEX_LOWPRICE]
        p_low_current  = kline_current[KLINDEX_LOWPRICE]
        if (p_low_current <= p_low_previous): p_low_delta = p_low_previous-p_low_current
        else:                                 p_low_delta = 0
        if (p_low_delta <= p_high_delta): pd = False
        else:                             pd = True
        af   = None
        ep   = None
        psar = None
        pd_reversed = False
        dcc = 0
    elif (_analysisCount == 2):
        psar_previous = klineAccess[analysisCode][timestamp_previous]
        timestamp_previous2 = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -2)
        kline_previous1 = klineAccess['raw'][timestamp_previous]
        kline_previous2 = klineAccess['raw'][timestamp_previous2]
        if (psar_previous['PD'] == True): 
            psar = max([kline_previous1[KLINDEX_HIGHPRICE], kline_previous2[KLINDEX_HIGHPRICE]])
            ep   = min([kline_previous1[KLINDEX_LOWPRICE],  kline_previous2[KLINDEX_LOWPRICE]])
        else:        
            psar = min([kline_previous1[KLINDEX_LOWPRICE],  kline_previous2[KLINDEX_LOWPRICE]])
            ep   = max([kline_previous1[KLINDEX_HIGHPRICE], kline_previous2[KLINDEX_HIGHPRICE]])                     
        af = psar_start
        pd = psar_previous['PD']
        pd_reversed = False
        dcc = 0
    elif (3 <= _analysisCount):
        psar_previous = klineAccess[analysisCode][timestamp_previous]
        timestamp_previous2 = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -2)
        kline_current = klineAccess['raw'][timestamp]
        kline_previous1 = klineAccess['raw'][timestamp_previous]
        kline_previous2 = klineAccess['raw'][timestamp_previous2]
        psar_ = psar_previous['PSAR'] + psar_previous['AF']*(psar_previous['EP']-psar_previous['PSAR'])
        if (psar_previous['PD'] == True):
            #Reverse Detect
            pd_reversed = (kline_current[KLINDEX_LOWPRICE] < psar_)
            #AF Update
            if (psar_previous['EP'] < kline_current[KLINDEX_HIGHPRICE]):
                ep = kline_current[KLINDEX_HIGHPRICE]
                af = psar_previous['AF'] + psar_acceleration
                if (psar_maximum < af): af = psar_maximum
            else: 
                ep = psar_previous['EP']
                af = psar_previous['AF']
            psar_ = min([psar_, kline_previous1[KLINDEX_LOWPRICE], kline_previous2[KLINDEX_LOWPRICE]])
        else:
            #Reverse Detect
            pd_reversed = (psar_ < kline_current[KLINDEX_HIGHPRICE])
            #AF Update
            if (kline_current[KLINDEX_LOWPRICE] < psar_previous['EP']):
                ep = kline_current[KLINDEX_LOWPRICE]
                af = psar_previous['AF'] + psar_acceleration
                if (psar_maximum < af): af = psar_maximum
            else: 
                ep = psar_previous['EP']
                af = psar_previous['AF']
            psar_ = max([psar_, kline_previous1[KLINDEX_HIGHPRICE], kline_previous2[KLINDEX_HIGHPRICE]])
        #PD Reversal Handling
        if (pd_reversed == True):
            psar_ = ep
            af = psar_start
            pd = not(psar_previous['PD'])
            if (pd == True): ep = kline_current[KLINDEX_HIGHPRICE]
            else:            ep = kline_current[KLINDEX_LOWPRICE]
            dcc = 0
        else: 
            pd = psar_previous['PD']
            dcc = psar_previous['DCC']+1
        psar = psar_
    #Result formatting & saving
    #PD:   Progression Direction (True: Incremental, False: Decremental)
    #AF:   Acceleration Factor
    #EP:   Extreme Point
    #PSAR: PSAR Value
    #DCC:  Direction Continuity Counter
    psarResult = {'PD': pd, 'PDReversed': pd_reversed, 'AF': af, 'EP': ep, 'PSAR': psar, 'DCC': dcc, '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = psarResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    return (2, 2)

def analysisGenerator_BOL(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']
    maType       = analysisParams['MAType']
    bandWidth    = analysisParams['bandWidth']
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess[analysisCode]): _analysisCount = klineAccess[analysisCode][timestamp_previous]['_analysisCount']+1
    else:                                                 _analysisCount = 0
    #BOL computation
    timestampsList = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False, mrktReg = mrktRegTS)
    #---MA
    if (maType == 'SMA'):
        if (_analysisCount < nSamples-1):
            sma = None
        elif (nSamples-1 == _analysisCount):
            priceSum = 0
            for i in range (nSamples): priceSum += klineAccess['raw'][timestampsList[i]][KLINDEX_CLOSEPRICE]
            sma = priceSum / nSamples
        elif (nSamples-1 < _analysisCount):
            timestamp_expired = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -nSamples)
            previousPriceSum = klineAccess[analysisCode][timestamp_previous]['MA']*nSamples
            newPriceSum      = previousPriceSum - klineAccess['raw'][timestamp_expired][KLINDEX_CLOSEPRICE] + klineAccess['raw'][timestamp][KLINDEX_CLOSEPRICE]
            sma = newPriceSum / nSamples
        ma = sma
    elif (maType == 'WMA'):
        if (_analysisCount < nSamples-1):
            wma = None
        elif (nSamples-1 <= _analysisCount):
            baseSum = nSamples*(nSamples+1)/2
            weightedSum = 0
            for index, ts in enumerate(timestampsList): weightedSum += klineAccess['raw'][ts][KLINDEX_CLOSEPRICE]*(nSamples-index)
            wma = weightedSum/baseSum
        ma = wma
    elif (maType == 'EMA'):
        kValue = 2/(nSamples+1)
        if   (_analysisCount == 0): ema = None
        elif (_analysisCount == 1): ema = (klineAccess['raw'][timestamp][KLINDEX_CLOSEPRICE]*kValue) + (klineAccess['raw'][timestamp_previous][KLINDEX_CLOSEPRICE]*(1-kValue))
        elif (1 < _analysisCount):  ema = (klineAccess['raw'][timestamp][KLINDEX_CLOSEPRICE]*kValue) + (klineAccess[analysisCode][timestamp_previous]['MA']       *(1-kValue))
        ma = ema
    #---BOL
    if (_analysisCount < nSamples-1):
        bol = None
    else:
        deviationSquaredSum = 0
        for i in range (nSamples): deviationSquaredSum += math.pow((klineAccess['raw'][timestampsList[i]][KLINDEX_CLOSEPRICE])-ma, 2)
        sd = math.sqrt(deviationSquaredSum/nSamples)
        bol = (ma-sd*bandWidth, ma+sd*bandWidth)
    #Result formatting & saving
    bolResult = {'BOL': bol, 'MA': ma, '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = bolResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    return (2, nSamples)

def __IVP_addPriceLevelProfile(priceLevelProfileWeight, priceLevelProfilePosition_low, priceLevelProfilePosition_high, priceLevelProfile, divisionHeight, pricePrecision, mode = True):
    divisionIndex_floor   = int(priceLevelProfilePosition_low /divisionHeight)
    divisionIndex_ceiling = int(priceLevelProfilePosition_high/divisionHeight)
    nDivisions = len(priceLevelProfile)
    if (mode == True): _director =  1
    else:              _director = -1
    #Case [1]: The floor dIndex and the ceiling dIndex is the same
    if (divisionIndex_floor == divisionIndex_ceiling):
        if (divisionIndex_floor < nDivisions): 
            priceLevelProfile[divisionIndex_floor] += priceLevelProfileWeight*_director
            if (priceLevelProfile[divisionIndex_floor] < 0): priceLevelProfile[divisionIndex_floor] = 0
    #Case [2]: The ceiling division is right above the floor division
    elif (divisionIndex_ceiling == divisionIndex_floor+1):
        volumeProfileDensity    = priceLevelProfileWeight/(priceLevelProfilePosition_high-priceLevelProfilePosition_low)
        divisionPosition_center = round(divisionIndex_ceiling*divisionHeight, pricePrecision)
        #Floor Part
        if (divisionIndex_floor < nDivisions): 
            priceLevelProfile[divisionIndex_floor] += volumeProfileDensity*(divisionPosition_center-priceLevelProfilePosition_low)*_director
            if (priceLevelProfile[divisionIndex_floor] < 0): priceLevelProfile[divisionIndex_floor] = 0
        #Ceiling Part
        if (divisionIndex_ceiling < nDivisions): 
            priceLevelProfile[divisionIndex_ceiling] += volumeProfileDensity*(priceLevelProfilePosition_high-divisionPosition_center)*_director
            if (priceLevelProfile[divisionIndex_ceiling] < 0): priceLevelProfile[divisionIndex_ceiling] = 0
    #Case [3]: There exist at least one divisions between the floor and the ceiling division
    else:
        volumeProfileDensity = priceLevelProfileWeight/(priceLevelProfilePosition_high-priceLevelProfilePosition_low)
        #Floor Part
        divisionPosition = round((divisionIndex_floor+1)*divisionHeight, pricePrecision)
        volumeAtDivision = volumeProfileDensity*(divisionPosition-priceLevelProfilePosition_low)
        priceLevelProfile[divisionIndex_floor] += volumeAtDivision*_director
        if (priceLevelProfile[divisionIndex_floor] < 0): priceLevelProfile[divisionIndex_floor] = 0
        #Middle Part
        volumeAtDivision = volumeProfileDensity*divisionHeight
        if (divisionIndex_ceiling-1 < nDivisions): 
            priceLevelProfile[divisionIndex_floor+1:divisionIndex_ceiling] += volumeAtDivision*_director
            for _plIndex in range (divisionIndex_floor+1, divisionIndex_ceiling): 
                if (priceLevelProfile[_plIndex] < 0): priceLevelProfile[_plIndex] = 0
        else:                                      
            priceLevelProfile[divisionIndex_floor+1:nDivisions-1] += volumeAtDivision*_director
            for _plIndex in range (divisionIndex_floor+1, nDivisions-1): 
                if (priceLevelProfile[_plIndex] < 0): priceLevelProfile[_plIndex] = 0
        #Ceiling Part
        if (divisionIndex_ceiling < nDivisions):
            divisionPosition = round(divisionIndex_ceiling*divisionHeight, pricePrecision)
            volumeAtDivision = volumeProfileDensity*(priceLevelProfilePosition_high-divisionPosition)
            priceLevelProfile[divisionIndex_ceiling] += volumeAtDivision*_director
            if (priceLevelProfile[divisionIndex_ceiling] < 0): priceLevelProfile[divisionIndex_ceiling] = 0

def analysisGenerator_IVP(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    #Parameters
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']
    gammaFactor  = analysisParams['gammaFactor']
    deltaFactor  = analysisParams['deltaFactor']
    baseUnit = pow(10, -precisions['price'])

    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    ivp_prev      = klineAccess[analysisCode].get(timestamp_previous, None)
    analysisCount = 0 if ivp_prev is None else ivp_prev['_analysisCount']+1

    #Klines
    kl_this = klineAccess['raw'][timestamp]
    kl_this_cp  = kl_this[KLINDEX_CLOSEPRICE]
    kl_this_hp  = kl_this[KLINDEX_HIGHPRICE]
    kl_this_lp  = kl_this[KLINDEX_LOWPRICE]
    kl_this_vol = kl_this[KLINDEX_VOLBASE]

    #[1]: Division Height & Volume Price Level Profiles Preparation
    if analysisCount < nSamples-1:
        divisionHeight          = None
        gammaFactor             = None
        betaFactor              = None
        volumePriceLevelProfile = None
    else:
        betaFactor = round(kl_this_cp*gammaFactor, precisions['price'])
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
        if nBaseUnitsWithinDivisionHeight == 0: divisionHeight = round(baseUnit,                                precisions['price'])
        else:                                   divisionHeight = round(baseUnit*nBaseUnitsWithinDivisionHeight, precisions['price'])
        #---nDivisions
        nDivisions = math.ceil(dCeiling/divisionHeight)
        #---Price Level Profiles
        if analysisCount == nSamples-1: 
            volumePriceLevelProfile = numpy.zeros(nDivisions)
        else:
            volumePriceLevelProfile_prev = ivp_prev['volumePriceLevelProfile']
            nDivisions_prev     = len(volumePriceLevelProfile_prev)
            divisionHeight_prev = ivp_prev['divisionHeight']
            if (divisionHeight_prev == divisionHeight) and (nDivisions_prev == nDivisions): volumePriceLevelProfile = numpy.copy(volumePriceLevelProfile_prev)
            else:
                volumePriceLevelProfile = numpy.zeros(nDivisions)
                for divisionIndex_prev in range (nDivisions_prev):
                    divisionPosition_low_prev  = round(divisionHeight_prev*divisionIndex_prev,     precisions['price'])
                    divisionPosition_high_prev = round(divisionHeight_prev*(divisionIndex_prev+1), precisions['price'])
                    __IVP_addPriceLevelProfile(priceLevelProfileWeight        = volumePriceLevelProfile_prev[divisionIndex_prev], 
                                               priceLevelProfilePosition_low  = divisionPosition_low_prev, 
                                               priceLevelProfilePosition_high = divisionPosition_high_prev, 
                                               priceLevelProfile              = volumePriceLevelProfile, 
                                               divisionHeight                 = divisionHeight,
                                               pricePrecision                 = precisions['price'])
    #[2]: Volume Price Level Profile
    if analysisCount == nSamples-1:
        for ts in atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False, mrktReg = mrktRegTS):
            _kline = klineAccess['raw'][ts]
            __IVP_addPriceLevelProfile(priceLevelProfileWeight        = _kline[KLINDEX_VOLBASE], 
                                       priceLevelProfilePosition_low  = _kline[KLINDEX_LOWPRICE], 
                                       priceLevelProfilePosition_high = _kline[KLINDEX_HIGHPRICE], 
                                       priceLevelProfile              = volumePriceLevelProfile, 
                                       divisionHeight                 = divisionHeight, 
                                       pricePrecision                 = precisions['price'])
    elif nSamples-1 < analysisCount:
        __IVP_addPriceLevelProfile(priceLevelProfileWeight         = kl_this_vol, 
                                   priceLevelProfilePosition_low  = kl_this_lp, 
                                   priceLevelProfilePosition_high = kl_this_hp, 
                                   priceLevelProfile              = volumePriceLevelProfile, 
                                   divisionHeight                 = divisionHeight,
                                   pricePrecision                 = precisions['price'])
    if nSamples < analysisCount:
        _expiredKline = klineAccess['raw'][atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -nSamples)]
        __IVP_addPriceLevelProfile(priceLevelProfileWeight        = _expiredKline[KLINDEX_VOLBASE], 
                                   priceLevelProfilePosition_low  = _expiredKline[KLINDEX_LOWPRICE], 
                                   priceLevelProfilePosition_high = _expiredKline[KLINDEX_HIGHPRICE], 
                                   priceLevelProfile              = volumePriceLevelProfile, 
                                   divisionHeight                 = divisionHeight,
                                   pricePrecision                 = precisions['price'],
                                   mode                           = False)
        
    #[3]: Volume Price Level Profile Boundaries
    if analysisCount < nSamples-1:
        volumePriceLevelProfile_Filtered     = None
        volumePriceLevelProfile_Filtered_Max = None
        volumePriceLevelProfile_Boundaries   = None
    else:
        volumePriceLevelProfile_Filtered     = scipy.ndimage.gaussian_filter1d(input = volumePriceLevelProfile, sigma = round(len(volumePriceLevelProfile)/(3.3*1000)*deltaFactor, 10))
        volumePriceLevelProfile_Filtered_Max = numpy.max(volumePriceLevelProfile_Filtered)
        volumePriceLevelProfile_Boundaries   = list()
        #Extremas Search
        direction_prev = None
        volHeight_prev = None
        for plIndex, volHeight in enumerate(volumePriceLevelProfile_Filtered):
            if direction_prev is None: 
                direction_prev = True
                volHeight_prev = volHeight
            else:
                #Local Maximum
                if direction_prev and (volHeight < volHeight_prev): 
                    direction_prev = False
                    volumePriceLevelProfile_Boundaries.append(-1)
                #Local Minimum
                elif not direction_prev and (volHeight_prev < volHeight): 
                    direction_prev = True
                    volumePriceLevelProfile_Boundaries.append(plIndex-1) 
                volHeight_prev = volHeight

    #[4]: Near VPLP Boundaries
    if volumePriceLevelProfile_Boundaries is None:
        volumePriceLevelProfile_nearBoundaries = [None]*10
    else:
        vplp_nearBoundaries_down = [0]           *5
        vplp_nearBoundaries_up   = [float('inf')]*5
        #Find the nearest above boundary index
        dIndex_closePrice  = _kline[KLINDEX_CLOSEPRICE]//divisionHeight
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
            if 0 <= idx_down_target:
                dIndex = volumePriceLevelProfile_Boundaries[idx_down_target]
                vplp_nearBoundaries_down[i] = round(((dIndex+0.5)*divisionHeight/_kline[KLINDEX_CLOSEPRICE])-1, 4)
            if idx_up_target < len(volumePriceLevelProfile_Boundaries):
                dIndex = volumePriceLevelProfile_Boundaries[idx_up_target]
                vplp_nearBoundaries_up[i] = round(((dIndex+0.5)*divisionHeight/_kline[KLINDEX_CLOSEPRICE])-1, 4)
        #Finally
        volumePriceLevelProfile_nearBoundaries = tuple(vplp_nearBoundaries_down)+tuple(vplp_nearBoundaries_up)
    
    #Result Formatting & Save
    ivpResult = {'divisionHeight': divisionHeight, 'gammaFactor': gammaFactor, 'betaFactor': betaFactor,
                 'volumePriceLevelProfile':                volumePriceLevelProfile,
                 'volumePriceLevelProfile_Filtered':       volumePriceLevelProfile_Filtered, 
                 'volumePriceLevelProfile_Filtered_Max':   volumePriceLevelProfile_Filtered_Max, 
                 'volumePriceLevelProfile_Boundaries':     volumePriceLevelProfile_Boundaries,
                 'volumePriceLevelProfile_NearBoundaries': volumePriceLevelProfile_nearBoundaries,
                 '_analysisCount': analysisCount}
    try:    klineAccess[analysisCode][timestamp] = ivpResult
    except: klineAccess[analysisCode] = {timestamp: ivpResult}
    #Return True to indicate successful analysis generation
    #---nAnalysisToKeep, nKlinesToKeep
    return (2, nSamples+1)

def analysisGenerator_SWING(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode = analysisParams['analysisCode']
    swingRange   = analysisParams['swingRange']

    klineAccess_raw = klineAccess['raw']
    kline = klineAccess_raw[timestamp]
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    swing_prev    = klineAccess[analysisCode].get(timestamp_previous, None)
    analysisCount = 0 if swing_prev is None else swing_prev['_analysisCount']+1

    #Swing
    kl_hp = kline[KLINDEX_HIGHPRICE]
    kl_lp = kline[KLINDEX_LOWPRICE]
    kl_cp = kline[KLINDEX_CLOSEPRICE]
    if analysisCount == 0:
        swings      = list()
        swingSearch = {'lastExtreme': True, 
                       'max':         kl_hp, 
                       'min':         kl_lp, 
                       'max_ts':      timestamp, 
                       'min_ts':      timestamp}
    else:
        swings      = swing_prev['SWINGS'].copy()
        swingSearch = swing_prev['_SWINGSEARCH'].copy()
        if swingSearch['lastExtreme']:
            if kl_lp < swingSearch['min']: 
                swingSearch['min']    = kl_lp
                swingSearch['min_ts'] = timestamp
            if swingSearch['min']*(1+swingRange) < kl_cp:
                newSwing = (swingSearch['min_ts'], swingSearch['min'], -1)
                swings.append(newSwing)
                swingSearch['lastExtreme'] = False
                swingSearch['max']         = kl_hp
                swingSearch['max_ts']      = timestamp
        else:
            if swingSearch['max'] < kl_hp: 
                swingSearch['max']    = kl_hp
                swingSearch['max_ts'] = timestamp
            if kl_cp < swingSearch['max']*(1-swingRange):
                newSwing = (swingSearch['max_ts'], swingSearch['max'], 1)
                swings.append(newSwing)
                swingSearch['lastExtreme'] = True
                swingSearch['min']         = kl_lp
                swingSearch['min_ts']      = timestamp
        #Number of swings control
        swings = swings[-20:]

    #Result formatting & saving
    swingResult = {'SWINGS': swings, '_SWINGSEARCH': swingSearch,
                 #Process
                 '_analysisCount': analysisCount}
    klineAccess[analysisCode][timestamp] = swingResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    return (2, 2)

def analysisGenerator_VOL(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetworks, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode = analysisParams['analysisCode']
    nSamples     = analysisParams['nSamples']
    volumeType   = analysisParams['volumeType']
    MAType       = analysisParams['MAType']
    if   (volumeType == 'BASE'):    volAccessIndex = KLINDEX_VOLBASE
    elif (volumeType == 'QUOTE'):   volAccessIndex = KLINDEX_VOLQUOTE
    elif (volumeType == 'BASETB'):  volAccessIndex = KLINDEX_VOLBASETAKERBUY
    elif (volumeType == 'QUOTETB'): volAccessIndex = KLINDEX_VOLQUOTETAKERBUY
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess[analysisCode]): _analysisCount = klineAccess[analysisCode][timestamp_previous]['_analysisCount']+1
    else:                                                 _analysisCount = 0
    #Compute VOLMA
    if (MAType == 'SMA'):
        if (_analysisCount < nSamples-1):
            ma = None
        elif (nSamples-1 == _analysisCount):
            timestampsList = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False, mrktReg = mrktRegTS)
            volumeSum = 0
            for i in range (nSamples): volumeSum += klineAccess['raw'][timestampsList[i]][volAccessIndex]
            ma = volumeSum / nSamples
        elif (nSamples-1 < _analysisCount):
            timestamp_expired = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -nSamples)
            previousPriceSum = klineAccess[analysisCode][timestamp_previous]['MA']*nSamples
            newVolumeSum     = previousPriceSum - klineAccess['raw'][timestamp_expired][volAccessIndex] + klineAccess['raw'][timestamp][volAccessIndex]
            ma = newVolumeSum / nSamples
    elif (MAType == 'WMA'):
        if (_analysisCount < nSamples-1):
            ma = None
        elif (nSamples-1 <= _analysisCount):
            timestampsList = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False, mrktReg = mrktRegTS)
            baseSum     = nSamples*(nSamples+1)/2
            weightedSum = 0
            for index, ts in enumerate(timestampsList): weightedSum += klineAccess['raw'][ts][volAccessIndex]*(nSamples-index)
            ma = weightedSum/baseSum
    elif (MAType == 'EMA'):
        kValue = 2/(nSamples+1)
        if   (_analysisCount == 0): ma = None
        elif (_analysisCount == 1): ma = (klineAccess['raw'][timestamp][volAccessIndex]*kValue) + (klineAccess['raw'][timestamp_previous][volAccessIndex]*(1-kValue))
        elif (1 < _analysisCount):  ma = (klineAccess['raw'][timestamp][volAccessIndex]*kValue) + (klineAccess[analysisCode][timestamp_previous]['MA']   *(1-kValue))
    #Result formatting & saving
    volResult = {'MA': ma, '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = volResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    if (MAType == 'SMA'):
        if   (_analysisCount < nSamples-1):  return (2, nSamples) #nAnalysisToKeep, nKlinesToKeep
        elif (nSamples-1 == _analysisCount): return (2, 2)        #nAnalysisToKeep, nKlinesToKeep
        elif (nSamples-1 < _analysisCount):  return (2, 2)
    elif (MAType == 'WMA'): return (2, nSamples)
    elif (MAType == 'EMA'): return (2, 2)

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
        if (dmPlus < 0): dmPlus = 0
        dmMinus = kline_prev[KLINDEX_LOWPRICE]-kline_current[KLINDEX_LOWPRICE]
        if (dmMinus < 0): dmMinus = 0
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
        if ((dmPlusSum == 0) and (trSum == 0)):  diPlus  = 0
        else:                                    diPlus  = dmPlusSum/trSum*100
        if ((dmMinusSum == 0) and (trSum == 0)): diMinus = 0
        else:                                    diMinus = dmMinusSum/trSum*100
        if (diPlus+diMinus == 0): dx = 100
        else:                     dx = abs(diPlus-diMinus)/(diPlus+diMinus)*100
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
    if ((diPlus != None) and (diMinus != None) and (adx != None)): dmixadx = (diPlus-diMinus)*adx/100
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
        if (0 < dmixadx_absAth): dmixadx_absAthRel = round(dmixadx/dmixadx_absAth*100, 3)
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
        if (mfr == None): mfi = 100
        else:             mfi = 100-(100/(1+mfr))
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
        if (0 < mfi_absAth): mfi_absAthRel = round(mfi/mfi_absAth*100, 3)
        else:                mfi_absAthRel = 0
    #Result formatting & saving
    mfiResult = {'TP': tp, 'MF': mf, 
                 'MFI': mfi, 'MFI_ABSATH': mfi_absAth, 'MFI_ABSATHREL': mfi_absAthRel,
                 '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = mfiResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    return (nSamples+1, 1)

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
            volType  = cac[f'VOL_VolumeType']
            maType   = cac[f'VOL_MAType']
            if   type(nSamples) is not int:                             invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < nSamples:                                      invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if   type(volType) is not str:                              invalidLines[analysisCode].append("volType: Must be type 'str'")
            elif volType not in ('BASE', 'QUOTE', 'BASETB', 'QUOTETB'): invalidLines[analysisCode].append("volType: Must be 'BASE', 'QUOTE', 'BASETB', or 'QUOTETB'")
            if   type(maType) is not str:                               invalidLines[analysisCode].append("maType: Must be type 'str'")
            elif maType not in ('SMA', 'WMA', 'EMA'):                   invalidLines[analysisCode].append("maType: Must be 'SMA', 'WMA', or 'EMA'")
            if analysisCode in invalidLines: continue
            #[3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex':  lineIndex,
                                 'nSamples':   nSamples,
                                 'volumeType': volType,
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

"""
_TORCHDTYPE = atmEta_NeuralNetworks._TORCHDTYPE
_PIP_SWINGTYPE_LOW  = 'LOW'
_PIP_SWINGTYPE_HIGH = 'HIGH'
def analysisGenerator_PIP(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode = analysisParams['analysisCode']
    REFERREDANALYSISCODES = analysisParams['referredAnalysisCodes']
    SWINGRANGE            = analysisParams['swingRange']
    ALPHA_NNA             = analysisParams['alpha_NNA']
    BETA_NNA              = analysisParams['beta_NNA']
    ALPHA_CS              = analysisParams['alpha_CS']
    BETA_CS               = analysisParams['beta_CS']
    NSAMPLES_CS           = analysisParams['nSamples_CS']
    SIGMA_CS              = analysisParams['sigma_CS']

    _klineAccess_raw = klineAccess['raw']
    _kline = _klineAccess_raw[timestamp]
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess['PIP']): _pip_prev = klineAccess['PIP'][timestamp_previous]; _analysisCount = _pip_prev['_analysisCount']+1
    else:                                          _pip_prev = None;                                   _analysisCount = 0

    #[1]: Swings
    if (True):
        #Swing 0
        if (_analysisCount == 0):
            swings      = list()
            swingSearch = {'lastExtreme': True, 
                           'max':         _kline[KLINDEX_HIGHPRICE], 
                           'min':         _kline[KLINDEX_LOWPRICE], 
                           'max_ts':      timestamp, 
                           'min_ts':      timestamp}
        else:
            swings      = _pip_prev['SWINGS'].copy()
            swingSearch = _pip_prev['_SWINGSEARCH'].copy()
            if (swingSearch['lastExtreme'] == True):
                if (_kline[KLINDEX_LOWPRICE] < swingSearch['min']): 
                    swingSearch['min']    = _kline[KLINDEX_LOWPRICE]
                    swingSearch['min_ts'] = timestamp
                if (swingSearch['min']*(1+SWINGRANGE) < _kline[KLINDEX_CLOSEPRICE]):
                    swings.append((swingSearch['min_ts'], swingSearch['min'], _PIP_SWINGTYPE_LOW))
                    swingSearch['lastExtreme'] = False
                    swingSearch['max']         = _kline[KLINDEX_HIGHPRICE]
                    swingSearch['max_ts']      = timestamp
            elif (swingSearch['lastExtreme'] == False):
                if (swingSearch['max'] < _kline[KLINDEX_HIGHPRICE]): 
                    swingSearch['max']    = _kline[KLINDEX_HIGHPRICE]
                    swingSearch['max_ts'] = timestamp
                if (_kline[KLINDEX_CLOSEPRICE] < swingSearch['max']*(1-SWINGRANGE)):
                    swings.append((swingSearch['max_ts'], swingSearch['max'], _PIP_SWINGTYPE_HIGH))
                    swingSearch['lastExtreme'] = True
                    swingSearch['min']         = _kline[KLINDEX_LOWPRICE]
                    swingSearch['min_ts']      = timestamp
            #Number of swings control
            for _ in range (0, len(swings)-20): swings.pop(0)

    #[2]: Neural Network
    if (True):
        nnaSignal = None
        if (neuralNetwork is not None):
            _nn_nKlines = neuralNetwork.getNKlines()
            if ((_nn_nKlines-1) <= _analysisCount):
                #Formatting
                _nnInputTensor   = torch.zeros(size = (_nn_nKlines*6,), device = 'cpu', dtype = _TORCHDTYPE, requires_grad = False)
                _klineTSs = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = _nn_nKlines, direction = False, mrktReg = mrktRegTS)
                #Klines
                _p_max     = max([_klineAccess_raw[_klineTS][KLINDEX_HIGHPRICE] for _klineTS in _klineTSs])
                _p_min     = min([_klineAccess_raw[_klineTS][KLINDEX_LOWPRICE]  for _klineTS in _klineTSs])
                _p_range   = _p_max-_p_min
                _vol_max   = min([_klineAccess_raw[_klineTS][KLINDEX_VOLBASE]         for _klineTS in _klineTSs])
                _volTB_max = min([_klineAccess_raw[_klineTS][KLINDEX_VOLBASETAKERBUY] for _klineTS in _klineTSs])
                for _relKlineIndex in range (0, _nn_nKlines):
                    _kline = _klineAccess_raw[_klineTSs[-(1+_relKlineIndex)]]
                    if (_p_range != 0):
                        _nnInputTensor[_relKlineIndex*6+0] = (_kline[KLINDEX_OPENPRICE] -_p_min)/_p_range
                        _nnInputTensor[_relKlineIndex*6+1] = (_kline[KLINDEX_HIGHPRICE] -_p_min)/_p_range
                        _nnInputTensor[_relKlineIndex*6+2] = (_kline[KLINDEX_LOWPRICE]  -_p_min)/_p_range
                        _nnInputTensor[_relKlineIndex*6+3] = (_kline[KLINDEX_CLOSEPRICE]-_p_min)/_p_range
                    else:
                        _nnInputTensor[_relKlineIndex*6+0] = 0.5
                        _nnInputTensor[_relKlineIndex*6+1] = 0.5
                        _nnInputTensor[_relKlineIndex*6+2] = 0.5
                        _nnInputTensor[_relKlineIndex*6+3] = 0.5
                    if (_vol_max != 0): _nnInputTensor[_relKlineIndex*6+4] = (_kline[KLINDEX_VOLBASE])/_vol_max
                    else:               _nnInputTensor[_relKlineIndex*6+4] = 0.0
                    if (_volTB_max != 0): _nnInputTensor[_relKlineIndex*6+5] = (_kline[KLINDEX_VOLBASETAKERBUY])/_volTB_max
                    else:                 _nnInputTensor[_relKlineIndex*6+5] = 0.0
                #Forwarding
                _nnOutput = float(neuralNetwork.forward(inputData = _nnInputTensor)[0])*2-1
                if (0 <= _nnOutput): nnaSignal =  abs(round(math.atan(pow(_nnOutput/ALPHA_NNA, BETA_NNA))*2/math.pi, 5))
                else:                nnaSignal = -abs(round(math.atan(pow(_nnOutput/ALPHA_NNA, BETA_NNA))*2/math.pi, 5))
                print(_nnOutput, nnaSignal)

    #[3]: Classical Signal interpretation
    if (True):
        #[1]: Classical Signals Combination
        _classicalSignalSum           = 0
        _nClassicalSignalContributors = 0
        _allContributorsReady         = True
        for analysisType in REFERREDANALYSISCODES:
            #[1]: MMACDSHORT
            if (analysisType == 'MMACDSHORT'):
                _mmacdShort = klineAccess['MMACDSHORT'][timestamp]
                _mmacdShort_MSDelta_MADelta_AbsMARel = _mmacdShort['MSDELTA_ABSMAREL']
                if (_mmacdShort_MSDelta_MADelta_AbsMARel != None):
                    _classicalSignalSum += _mmacdShort_MSDelta_MADelta_AbsMARel
                    _nClassicalSignalContributors += 1
                else: _allContributorsReady = False; break
            #[2]: MMACDLONG
            if (analysisType == 'MMACDLONG'):
                _mmacdLong = klineAccess['MMACDLONG'][timestamp]
                _mmacdLong_MSDelta_MADelta_AbsMARel = _mmacdLong['MSDELTA_ABSMAREL']
                if (_mmacdLong_MSDelta_MADelta_AbsMARel != None):
                    _classicalSignalSum += _mmacdLong_MSDelta_MADelta_AbsMARel
                    _nClassicalSignalContributors += 1
                else: _allContributorsReady = False; break
            #[1]: DMIxADX
            if (analysisType == 'DMIxADX'):
                _signalSum_dmixadx = 0
                for dmixadxCode in REFERREDANALYSISCODES['DMIxADX']:
                    _dmixadx = klineAccess[dmixadxCode][timestamp]
                    _dmiadx_absATHRel = _dmixadx['DMIxADX_ABSATHREL']
                    if (_dmiadx_absATHRel != None): _signalSum_dmixadx += _dmiadx_absATHRel/100
                    else: _allContributorsReady = False; break
                if (_allContributorsReady == False): break
                else:
                    _classicalSignalSum += _signalSum_dmixadx/len(REFERREDANALYSISCODES['DMIxADX'])
                    _nClassicalSignalContributors += 1
            #[2]: MFI
            if (analysisType == 'MFI'):
                _signalSum_mfi = 0
                for mfiCode in REFERREDANALYSISCODES['MFI']: 
                    _mfi = klineAccess[mfiCode][timestamp]
                    _mfi_absATHRel = _mfi['MFI_ABSATHREL']
                    if (_mfi_absATHRel != None): _signalSum_mfi += _mfi_absATHRel/100-0.5
                    else: _allContributorsReady = False; break
                if (_allContributorsReady == False): break
                else:
                    _classicalSignalSum += _signalSum_dmixadx/len(REFERREDANALYSISCODES['DMIxADX'])
                    _nClassicalSignalContributors += 1
        if ((0 < _nClassicalSignalContributors) and (_allContributorsReady == True)):
            if (0 <= _classicalSignalSum): classicalSignal =  abs(round(math.atan(pow(_classicalSignalSum/_nClassicalSignalContributors/ALPHA_CS, BETA_CS))*2/math.pi, 5))
            else:                          classicalSignal = -abs(round(math.atan(pow(_classicalSignalSum/_nClassicalSignalContributors/ALPHA_CS, BETA_CS))*2/math.pi, 5))
        else: classicalSignal = None
        #[2]: CS Delta
        if (_pip_prev == None): _classicalSignal_prev = None
        else:                   _classicalSignal_prev = _pip_prev['CLASSICALSIGNAL']
        if (_classicalSignal_prev == None): classicalSignal_Delta = None
        else:                               classicalSignal_Delta = classicalSignal-_classicalSignal_prev
        #[3]: CS Filtered
        classicalSignal_Filtered = None
        _samplingTSs = atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = NSAMPLES_CS, direction = False, mrktReg = mrktRegTS)
        if ((_samplingTSs[-1] in klineAccess['PIP']) and (klineAccess['PIP'][_samplingTSs[-1]]['CLASSICALSIGNAL'] != None)):
            _CSSamples = [klineAccess['PIP'][_samplingTSs[-1-_sTSIndex]]['CLASSICALSIGNAL'] for _sTSIndex in range (NSAMPLES_CS-1)] + [classicalSignal,]
            _CSSamples_gaussianFiltered = scipy.ndimage.gaussian_filter1d(input = _CSSamples, sigma = SIGMA_CS)
            classicalSignal_Filtered = float(_CSSamples_gaussianFiltered[-1])
        #[4]: CS Filtered Delta
        if (_pip_prev is None): _classicalSignal_Filtered_prev = None
        else:                   _classicalSignal_Filtered_prev = _pip_prev['CLASSICALSIGNAL_FILTERED']
        if (_classicalSignal_Filtered_prev is None): classicalSignal_Filtered_Delta = None
        else:                                        classicalSignal_Filtered_Delta = classicalSignal_Filtered-_classicalSignal_Filtered_prev
        #[5]: CS Cycle Base
        if (_pip_prev is None): 
            classicalSignal_Cycle        = None
            classicalSignal_CycleUpdated = False
        else:                   
            classicalSignal_Cycle        = _pip_prev['CLASSICALSIGNAL_CYCLE']
            classicalSignal_CycleUpdated = False
        if ((classicalSignal_Cycle is None) and (classicalSignal_Filtered is not None)):
            if   (classicalSignal_Filtered < 0): classicalSignal_Cycle = 'LOW'
            elif (0 < classicalSignal_Filtered): classicalSignal_Cycle = 'HIGH'
            if (classicalSignal_Cycle is not None):
                classicalSignal_CycleUpdated = True
        elif (classicalSignal_Cycle is not None):
            if   ((classicalSignal_Cycle == 'LOW')  and (0 < classicalSignal_Filtered)): 
                classicalSignal_Cycle        = 'HIGH'
                classicalSignal_CycleUpdated = True
            elif ((classicalSignal_Cycle == 'HIGH') and (classicalSignal_Filtered < 0)): 
                classicalSignal_Cycle        = 'LOW'
                classicalSignal_CycleUpdated = True

    #[4]: IVP
    if (True):
        nearIVPBoundaries = [None]*10
        if ('IVP' in REFERREDANALYSISCODES):
            ivp = klineAccess['IVP'][timestamp]
            ivp_ivpBoundaries  = ivp['volumePriceLevelProfile_Boundaries']
            ivp_divisionHeight = ivp['divisionHeight']
            if (ivp_ivpBoundaries is not None):
                nearIVPBoundaries_down = [0]           *5
                nearIVPBoundaries_up   = [float('inf')]*5
                #Find the nearest above boundary index
                dIndex_closePrice  = _kline[KLINDEX_CLOSEPRICE]//ivp_divisionHeight
                bIndex_nearestAbove = None
                for bIndex, dIndex in enumerate(ivp_ivpBoundaries):
                    if (dIndex_closePrice <= dIndex): 
                        bIndex_nearestAbove = bIndex
                        break
                #Convert nearest down and up boundaries into price center values
                if (bIndex_nearestAbove is None):
                    idx_up_beg   = len(ivp_ivpBoundaries)
                    idx_down_beg = len(ivp_ivpBoundaries)-5
                else:
                    idx_up_beg   = bIndex_nearestAbove
                    idx_down_beg = bIndex_nearestAbove-5
                for i in range (5):
                    idx_down_target = idx_down_beg+i
                    idx_up_target   = idx_up_beg  +i
                    if (0 <= idx_down_target):
                        dIndex = ivp_ivpBoundaries[idx_down_target]
                        nearIVPBoundaries_down[i] = round(((dIndex+0.5)*ivp_divisionHeight/_kline[KLINDEX_CLOSEPRICE])-1, 4)
                    if (idx_up_target < len(ivp_ivpBoundaries)):
                        dIndex = ivp_ivpBoundaries[idx_up_target]
                        nearIVPBoundaries_up[i] = round(((dIndex+0.5)*ivp_divisionHeight/_kline[KLINDEX_CLOSEPRICE])-1, 4)
                #Finally
                nearIVPBoundaries = tuple(nearIVPBoundaries_down)+tuple(nearIVPBoundaries_up)
    
    #Result formatting & saving
    pipResult = {'SWINGS': swings, '_SWINGSEARCH': swingSearch,
                 #Neural Network
                 'NNASIGNAL': nnaSignal,
                 #Classical Signal
                 'CLASSICALSIGNAL':                classicalSignal, 
                 'CLASSICALSIGNAL_DELTA':          classicalSignal_Delta, 
                 'CLASSICALSIGNAL_FILTERED':       classicalSignal_Filtered, 
                 'CLASSICALSIGNAL_FILTERED_DELTA': classicalSignal_Filtered_Delta, 
                 'CLASSICALSIGNAL_CYCLE':          classicalSignal_Cycle,
                 'CLASSICALSIGNAL_CYCLEUPDATED':   classicalSignal_CycleUpdated,
                 #IVP
                 'NEARIVPBOUNDARIES': nearIVPBoundaries,
                 #Process
                 '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = pipResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    if (neuralNetwork == None): return (NSAMPLES_CS, 2)
    else:                       return (max(NSAMPLES_CS, _nn_nKlines), _nn_nKlines)
"""
"""
    if (currencyAnalysisConfiguration['PIP_Master'] == True):
        _analysisCode = 'PIP'
        _referredAnalysisCodes = dict()
        _bolCodes              = list()
        for _aCode in _currencyAnalysisParams:
            _aType = _aCode.split("_")[0]
            if (_aType in __PIP_REFERREDANALYSISTYPES):
                if (_aType in _referredAnalysisCodes): _referredAnalysisCodes[_aType].append(_aCode)
                else:                                  _referredAnalysisCodes[_aType] = [_aCode,]
            if (_aType == 'BOL'): _bolCodes.append(_aCode)
        _currencyAnalysisParams[_analysisCode] = {'referredAnalysisCodes':  _referredAnalysisCodes,
                                                  'bolCodes':               _bolCodes,
                                                  'swingRange':             currencyAnalysisConfiguration['PIP_SwingRange'],
                                                  'alpha_NNA':              currencyAnalysisConfiguration['PIP_NNAAlpha'],
                                                  'beta_NNA':               currencyAnalysisConfiguration['PIP_NNABeta'],
                                                  'alpha_CS':               currencyAnalysisConfiguration['PIP_ClassicalAlpha'],
                                                  'beta_CS':                currencyAnalysisConfiguration['PIP_ClassicalBeta'],
                                                  'nSamples_CS':            currencyAnalysisConfiguration['PIP_ClassicalNSamples'],
                                                  'sigma_CS':               currencyAnalysisConfiguration['PIP_ClassicalSigma'],
                                                  }
"""