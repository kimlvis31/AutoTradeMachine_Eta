import scipy.fft
import scipy.ndimage
import scipy.stats
import atmEta_Auxillaries
import atmEta_NeuralNetworks
import atmEta_Constants

import random
import math
import numpy
import scipy
import datetime
import pprint
import torch
import time

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

ANALYSIS_MITYPES = ('SMA', 'WMA', 'EMA', 'PSAR', 'BOL', 'IVP', 'PIP')
ANALYSIS_SITYPES = ('VOL', 'MMACDSHORT', 'MMACDLONG', 'DMIxADX', 'MFI', 'WOI', 'NES')
ANALYSIS_GENERATIONORDER = ('SMA', 'WMA', 'EMA', 'PSAR', 'BOL', 'VOL', 'IVP', 'MMACDSHORT', 'MMACDLONG', 'DMIxADX', 'MFI', 'PIP')

__PIP_REFERREDANALYSISTYPES = set(['SMA', 'WMA', 'EMA', 'PSAR', 'BOL', 'IVP', 'MMACDSHORT', 'MMACDLONG', 'DMIxADX', 'MFI'])

AGGTRADESAMPLINGINTERVAL_S    = atmEta_Constants.AGGTRADESAMPLINGINTERVAL_S
BIDSANDASKSSAMPLINGINTERVAL_S = atmEta_Constants.BIDSANDASKSSAMPLINGINTERVAL_S
NMAXAGGTRADESSAMPLES          = atmEta_Constants.NMAXAGGTRADESSAMPLES
NMAXBIDSANDASKSSAMPLES        = atmEta_Constants.NMAXBIDSANDASKSSAMPLES
WOIALPHA                      = atmEta_Constants.WOIALPHA

def analysisGenerator_SMA(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    nSamples = analysisParams['nSamples']
    analysisCode = 'SMA_{:d}'.format(nSamples)
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

def analysisGenerator_WMA(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    nSamples = analysisParams['nSamples']
    analysisCode = 'WMA_{:d}'.format(nSamples)
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

def analysisGenerator_EMA(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    nSamples = analysisParams['nSamples']
    kValue   = 2/(nSamples+1)
    analysisCode = 'EMA_{:d}'.format(nSamples)
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

def analysisGenerator_PSAR(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    psar_start        = analysisParams['start']
    psar_acceleration = analysisParams['acceleration']
    psar_maximum      = analysisParams['maximum']
    analysisCode = 'PSAR_{:.3f}_{:.3f}_{:.3f}'.format(psar_start, psar_acceleration, psar_maximum)
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

def analysisGenerator_BOL(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    nSamples  = analysisParams['nSamples']
    maType    = analysisParams['MAType']
    bandWidth = analysisParams['bandWidth']
    analysisCode = 'BOL_{:d}_{:.1f}'.format(nSamples, bandWidth)
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

def analysisGenerator_IVP(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    nSamples     = analysisParams['nSamples']
    gammaFactor  = analysisParams['gammaFactor']
    deltaFactor  = analysisParams['deltaFactor']
    analysisCode = "IVP"
    _baseUnit = pow(10, -precisions['price'])
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess[analysisCode]): _analysisCount = klineAccess[analysisCode][timestamp_previous]['_analysisCount']+1
    else:                                                 _analysisCount = 0
    targetKline = klineAccess['raw'][timestamp]
    targetKline_closePrice = targetKline[KLINDEX_CLOSEPRICE]
    targetKline_highPrice  = targetKline[KLINDEX_HIGHPRICE]
    targetKline_lowPrice   = targetKline[KLINDEX_LOWPRICE]
    targetKline_vol        = targetKline[KLINDEX_VOLBASE]
    #Previous IVP
    if (('IVP' in klineAccess) and (timestamp_previous in klineAccess['IVP'])): ivp_previous = klineAccess['IVP'][timestamp_previous]
    else:                                                                       ivp_previous = None
    #[1]: Division Height & Volume Price Level Profiles Preparation
    if (True):
        if (_analysisCount < nSamples-1):
            divisionHeight          = None
            gammaFactor             = None
            betaFactor              = None
            volumePriceLevelProfile = None
        else:
            betaFactor = round(targetKline_closePrice*gammaFactor, precisions['price'])
            #---divisionCeiling determination
            p_max = klineAccess['raw_status'][timestamp]['p_max']
            p_max_OOM = math.floor(math.log(p_max, 10))
            p_max_MSD = int(p_max/pow(10, p_max_OOM))
            if (p_max_MSD == 10): p_max_MSD = 1; p_max_OOM += 1
            dCeiling_MSD = (int(p_max_MSD/1)+1)*1
            if (dCeiling_MSD == 10): dCeiling_MSD = 1;            dCeiling_OOM = p_max_OOM+1
            else:                    dCeiling_MSD = dCeiling_MSD; dCeiling_OOM = p_max_OOM
            dCeiling = dCeiling_MSD*pow(10, dCeiling_OOM)
            #---divisionHeight determination
            divisionHeight_min = betaFactor/10
            divisionHeight_min_OOM = math.floor(math.log(divisionHeight_min, 10))
            divisionHeight_min_MSD = int(divisionHeight_min/pow(10, divisionHeight_min_OOM))
            if (divisionHeight_min_MSD == 10): divisionHeight_min_MSD = 1; divisionHeight_min_OOM += 1
            divisionHeight_MSD = int(divisionHeight_min_MSD)
            if (divisionHeight_MSD == 0): divisionHeight_MSD = 1;                  divisionHeight_OOM = divisionHeight_min_OOM
            else:                         divisionHeight_MSD = divisionHeight_MSD; divisionHeight_OOM = divisionHeight_min_OOM
            _divisionHeight = divisionHeight_MSD*pow(10, divisionHeight_OOM)
            nBaseUnitsWithinDivisionHeight = int(_divisionHeight/_baseUnit)
            if (nBaseUnitsWithinDivisionHeight == 0): divisionHeight = round(_baseUnit,                                precisions['price'])
            else:                                     divisionHeight = round(_baseUnit*nBaseUnitsWithinDivisionHeight, precisions['price'])
            #---nDivisions
            nDivisions = math.ceil(dCeiling/divisionHeight)
            #---Price Level Profiles
            if (_analysisCount == nSamples-1): volumePriceLevelProfile = numpy.zeros(nDivisions)
            else:
                volumePriceLevelProfile_prev = ivp_previous['volumePriceLevelProfile']
                nDivisions_prev     = len(volumePriceLevelProfile_prev)
                divisionHeight_prev = ivp_previous['divisionHeight']
                if ((divisionHeight_prev == divisionHeight) and (nDivisions_prev == nDivisions)): volumePriceLevelProfile = numpy.copy(volumePriceLevelProfile_prev)
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
    if (True):
        if (_analysisCount == nSamples-1):
            for ts in atmEta_Auxillaries.getTimestampList_byNTicks(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False, mrktReg = mrktRegTS):
                _kline = klineAccess['raw'][ts]
                __IVP_addPriceLevelProfile(priceLevelProfileWeight        = _kline[KLINDEX_VOLBASE], 
                                           priceLevelProfilePosition_low  = _kline[KLINDEX_LOWPRICE], 
                                           priceLevelProfilePosition_high = _kline[KLINDEX_HIGHPRICE], 
                                           priceLevelProfile              = volumePriceLevelProfile, 
                                           divisionHeight                 = divisionHeight, 
                                           pricePrecision                 = precisions['price'])
        elif (nSamples-1 < _analysisCount):
            __IVP_addPriceLevelProfile(priceLevelProfileWeight        = targetKline_vol, 
                                       priceLevelProfilePosition_low  = targetKline_lowPrice, 
                                       priceLevelProfilePosition_high = targetKline_highPrice, 
                                       priceLevelProfile              = volumePriceLevelProfile, 
                                       divisionHeight                 = divisionHeight,
                                       pricePrecision                 = precisions['price'])
        if (nSamples < _analysisCount):
            _expiredKline = klineAccess['raw'][atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -nSamples)]
            __IVP_addPriceLevelProfile(priceLevelProfileWeight        = _expiredKline[KLINDEX_VOLBASE], 
                                       priceLevelProfilePosition_low  = _expiredKline[KLINDEX_LOWPRICE], 
                                       priceLevelProfilePosition_high = _expiredKline[KLINDEX_HIGHPRICE], 
                                       priceLevelProfile              = volumePriceLevelProfile, 
                                       divisionHeight                 = divisionHeight,
                                       pricePrecision                 = precisions['price'],
                                       mode                           = False)
    #[3]: Volume Price Level Profile Boundaries
    if (True):
        if (_analysisCount < nSamples-1):
            volumePriceLevelProfile_Filtered     = None
            volumePriceLevelProfile_Filtered_Max = None
            volumePriceLevelProfile_Boundaries   = None
        else:
            volumePriceLevelProfile_Filtered     = scipy.ndimage.gaussian_filter1d(input = volumePriceLevelProfile, sigma = round(len(volumePriceLevelProfile)/(3.3*1000)*deltaFactor, 10))
            volumePriceLevelProfile_Filtered_Max = numpy.max(volumePriceLevelProfile_Filtered)
            volumePriceLevelProfile_Boundaries   = list()
            #Extremas Search
            _direction_prev = None
            _volHeight_prev = None
            for _plIndex, _volHeight in enumerate(volumePriceLevelProfile_Filtered):
                if (_direction_prev == None): _direction_prev = True; _volHeight_prev = _volHeight
                else:
                    if   ((_direction_prev == True)  and (_volHeight < _volHeight_prev)): _direction_prev = False; volumePriceLevelProfile_Boundaries.append(_plIndex-1) #Local Maximum
                    elif ((_direction_prev == False) and (_volHeight_prev < _volHeight)): _direction_prev = True                                                         #Local Minimum
                    _volHeight_prev = _volHeight
    #Result Formatting & Save
    ivpResult = {'divisionHeight': divisionHeight, 'gammaFactor': gammaFactor, 'betaFactor': betaFactor,
                 'volumePriceLevelProfile': volumePriceLevelProfile,
                 'volumePriceLevelProfile_Filtered': volumePriceLevelProfile_Filtered, 'volumePriceLevelProfile_Filtered_Max': volumePriceLevelProfile_Filtered_Max, 
                 'volumePriceLevelProfile_Boundaries': volumePriceLevelProfile_Boundaries,
                 '_analysisCount': _analysisCount}
    try:    klineAccess[analysisCode][timestamp] = ivpResult
    except: klineAccess[analysisCode] = {timestamp: ivpResult}
    #Return True to indicate successful analysis generation
    #---nAnalysisToKeep, nKlinesToKeep
    return (2, nSamples+1)

_TORCHDTYPE = atmEta_NeuralNetworks._TORCHDTYPE
_PIP_SWINGTYPE_LOW  = 'LOW'
_PIP_SWINGTYPE_HIGH = 'HIGH'
def analysisGenerator_PIP(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    analysisCode = 'PIP'
    REFERREDANALYSISCODES = analysisParams['referredAnalysisCodes']
    SWINGRANGE            = analysisParams['swingRange']
    ALPHA_NNA             = analysisParams['alpha_NNA']
    BETA_NNA              = analysisParams['beta_NNA']
    ALPHA_CS              = analysisParams['alpha_CS']
    BETA_CS               = analysisParams['beta_CS']
    NSAMPLES_CS           = analysisParams['nSamples_CS']
    SIGMA_CS              = analysisParams['sigma_CS']
    AT1_CS                = analysisParams['csActivationThreshold1']
    AT2_CS                = analysisParams['csActivationThreshold2']
    AT_WS                 = analysisParams['wsActivationThreshold']

    _klineAccess_raw = klineAccess['raw']
    _kline = _klineAccess_raw[timestamp]
    #Analysis counter
    timestamp_previous = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = intervalID, timestamp = timestamp, mrktReg = mrktRegTS, nTicks = -1)
    if (timestamp_previous in klineAccess['PIP']): _pip_prev = klineAccess['PIP'][timestamp_previous]; _analysisCount = _pip_prev['_analysisCount']+1
    else:                                          _pip_prev = None;                                   _analysisCount = 0

    #Swings
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
                elif (swingSearch['min']*(1+SWINGRANGE) < _kline[KLINDEX_CLOSEPRICE]):
                    swings.append((swingSearch['min_ts'], swingSearch['min'], _PIP_SWINGTYPE_LOW))
                    swingSearch['lastExtreme'] = False
                    swingSearch['max']         = _kline[KLINDEX_HIGHPRICE]
                    swingSearch['max_ts']      = timestamp
            elif (swingSearch['lastExtreme'] == False):
                if (swingSearch['max'] < _kline[KLINDEX_HIGHPRICE]): 
                    swingSearch['max']    = _kline[KLINDEX_HIGHPRICE]
                    swingSearch['max_ts'] = timestamp
                elif (_kline[KLINDEX_CLOSEPRICE] < swingSearch['max']*(1-SWINGRANGE)):
                    swings.append((swingSearch['max_ts'], swingSearch['max'], _PIP_SWINGTYPE_HIGH))
                    swingSearch['lastExtreme'] = True
                    swingSearch['min']         = _kline[KLINDEX_LOWPRICE]
                    swingSearch['min_ts']      = timestamp
            #Number of swings control
            for _ in range (0, len(swings)-20): swings.pop(0)

    #Neural Network
    if (True):
        nnaSignal = None
        if (neuralNetwork != None):
            _nn_nKlines = neuralNetwork.getNKlines()
            if ((_nn_nKlines-1) <= _analysisCount):
                #Formatting
                _sampleInputSize = 6+neuralNetwork.getNAnalysisInputs()
                _nnInputTensor   = torch.zeros(size = (_nn_nKlines*_sampleInputSize,), device = 'cpu', dtype = _TORCHDTYPE, requires_grad = False)
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
                        _nnInputTensor[_relKlineIndex*_sampleInputSize+0] = (_kline[KLINDEX_OPENPRICE] -_p_min)/_p_range
                        _nnInputTensor[_relKlineIndex*_sampleInputSize+1] = (_kline[KLINDEX_HIGHPRICE] -_p_min)/_p_range
                        _nnInputTensor[_relKlineIndex*_sampleInputSize+2] = (_kline[KLINDEX_LOWPRICE]  -_p_min)/_p_range
                        _nnInputTensor[_relKlineIndex*_sampleInputSize+3] = (_kline[KLINDEX_CLOSEPRICE]-_p_min)/_p_range
                    if (_vol_max   != 0): _nnInputTensor[_relKlineIndex*_sampleInputSize+4] = (_kline[KLINDEX_VOLBASE]        )/_vol_max
                    if (_volTB_max != 0): _nnInputTensor[_relKlineIndex*_sampleInputSize+5] = (_kline[KLINDEX_VOLBASETAKERBUY])/_volTB_max
                #Analysis
                _analysisReferences = neuralNetwork.getAnalysisReferences()
                _completeAnalysis   = True
                for _relKlineIndex in range (0, _nn_nKlines):
                    _tTS    = _klineTSs[-(1+_relKlineIndex)]
                    _rIndex = _relKlineIndex*_sampleInputSize+6
                    for _aCode in _analysisReferences:
                        _aType = _aCode.split("_")[0]
                        if (_aCode in klineAccess): _data  = klineAccess[_aCode][_tTS]
                        else:                       _completeAnalysis = False; break
                        if (_aType == 'SMA'):
                            if (_p_range != 0): 
                                if (_data['SMA'] == None): _completeAnalysis = False; break
                                else:                      _nnInputTensor[_rIndex+0] = (_data['SMA']-_p_min)/_p_range
                            _rIndex += 1
                        elif (_aType == 'WMA'):
                            if (_p_range != 0):
                                if (_data['WMA'] == None): _completeAnalysis = False; break
                                else:                      _nnInputTensor[_rIndex+0] = (_data['WMA']-_p_min)/_p_range
                            _rIndex += 1
                        elif (_aType == 'EMA'):
                            if (_p_range != 0): 
                                if (_data['EMA'] == None): _completeAnalysis = False; break
                                else:                      _nnInputTensor[_rIndex+0] = (_data['EMA']-_p_min)/_p_range
                            _rIndex += 1
                        elif (_aType == 'BOL'):
                            if (_p_range != 0):
                                if (_data['BOL'] == None): _completeAnalysis = False; break
                                else:
                                    _nnInputTensor[_rIndex+0] = (_data['BOL'][0]-_p_min)/_p_range
                                    _nnInputTensor[_rIndex+1] = (_data['MA']    -_p_min)/_p_range
                                    _nnInputTensor[_rIndex+2] = (_data['BOL'][1]-_p_min)/_p_range
                            _rIndex += 3
                        elif (_aType == 'PSAR'):
                            if (_p_range != 0): 
                                if (_data['PSAR'] == None): _completeAnalysis = False; break
                                else:                       _nnInputTensor[_rIndex+0] = (_data['PSAR']-_p_min)/_p_range
                            _rIndex += 1
                        elif (_aType == 'IVP'):
                            _ivp_divisionHeight = _data['divisionHeight']
                            _ivp_ivpBoundaries  = _data['volumePriceLevelProfile_boundaries']
                            if (_ivp_ivpBoundaries == None): _completeAnalysis = False; break
                            else:
                                for _bIndex in range (2, len(_ivp_ivpBoundaries)-1):
                                    _bPosition = (_ivp_ivpBoundaries[_bIndex]+0.5)*_ivp_divisionHeight
                                    if (_kline[KLINDEX_CLOSEPRICE] <= _bPosition): 
                                        _bp3 = (_ivp_ivpBoundaries[_bIndex+1]+0.5)*_ivp_divisionHeight
                                        _bp2 = _bPosition
                                        _bp1 = (_ivp_ivpBoundaries[_bIndex-1]+0.5)*_ivp_divisionHeight
                                        _bp0 = (_ivp_ivpBoundaries[_bIndex-2]+0.5)*_ivp_divisionHeight
                                        if (_p_range != 0):
                                            _nnInputTensor[_rIndex+0] = (_bp3-_p_min)/_p_range
                                            _nnInputTensor[_rIndex+1] = (_bp2-_p_min)/_p_range
                                            _nnInputTensor[_rIndex+2] = (_bp1-_p_min)/_p_range
                                            _nnInputTensor[_rIndex+3] = (_bp0-_p_min)/_p_range
                                        break
                            _rIndex += 4
                        elif (_aType == 'MMACDSHORT'):
                            _signal = _data['MSDELTA_MADELTA_ABSMAREL']
                            if (_signal == None): _completeAnalysis = False; break
                            else:
                                if (0 <= _signal): _nnInputTensor[_rIndex+0] =  abs(round(math.atan(pow(_signal/1.5, 2))*2/math.pi, 5))
                                else:              _nnInputTensor[_rIndex+0] = -abs(round(math.atan(pow(_signal/1.5, 2))*2/math.pi, 5))
                            _rIndex += 1
                        elif (_aType == 'MMACDLONG'):
                            _signal = _data['MSDELTA_MADELTA_ABSMAREL']
                            if (_signal == None): _completeAnalysis = False; break
                            else:
                                if (0 <= _signal): _nnInputTensor[_rIndex+0] =  abs(round(math.atan(pow(_signal/1.5, 2))*2/math.pi, 5))
                                else:              _nnInputTensor[_rIndex+0] = -abs(round(math.atan(pow(_signal/1.5, 2))*2/math.pi, 5))
                            _rIndex += 1
                        elif (_aType == 'DMIxADX'):
                            _signal = _data['DMIxADX_MADELTA_ABSMAREL']
                            if (_signal == None): _completeAnalysis = False; break
                            else:
                                if (0 <= _signal): _nnInputTensor[_rIndex+0] =  abs(round(math.atan(pow(_signal/1.5, 2))*2/math.pi, 5))
                                else:              _nnInputTensor[_rIndex+0] = -abs(round(math.atan(pow(_signal/1.5, 2))*2/math.pi, 5))
                            _rIndex += 1
                        elif (_aType == 'MFI'):
                            _signal = _data['MFI_MADELTA_ABSMAREL']
                            if (_signal == None): _completeAnalysis = False; break
                            else:
                                if (0 <= _signal): _nnInputTensor[_rIndex+0] =  abs(round(math.atan(pow(_signal/1.5, 2))*2/math.pi, 5))
                                else:              _nnInputTensor[_rIndex+0] = -abs(round(math.atan(pow(_signal/1.5, 2))*2/math.pi, 5))
                            _rIndex += 1
                    if (_completeAnalysis == False): break
                if (_completeAnalysis == True): 
                    _nnOutput = float(neuralNetwork.forward(inputData = _nnInputTensor)[0])
                    if (0 <= _nnOutput): nnaSignal =  abs(round(math.atan(pow(_nnOutput/ALPHA_NNA, BETA_NNA))*2/math.pi, 5))
                    else:                nnaSignal = -abs(round(math.atan(pow(_nnOutput/ALPHA_NNA, BETA_NNA))*2/math.pi, 5))
                else:                    nnaSignal = 0

    #WOI Signal
    if (True):
        #WOI Signal
        woiSignal = None
        if (bidsAndAsks != None):
            #WOI Filtered
            _woi_filtered = list()
            if (timestamp in bidsAndAsks['WOI']):
                for _dType in bidsAndAsks:
                    if not((_dType == 'depth') or (_dType == 'WOI')):
                        _gFiltered = bidsAndAsks[_dType][timestamp][1]
                        if (_gFiltered == None): _woi_filtered = None; break
                        else:                    _woi_filtered.append(_gFiltered)
            #WOI Combined
            if (_woi_filtered != None):
                _nLines = len(_woi_filtered)
                if (_nLines != 0): woiSignal = round(sum(_woi_filtered)/_nLines, 5)
        #WOI Signal AbsMA
        _absMA_kValue = 2/(288+1)
        if (woiSignal == None): woiSignal_AbsMA = None
        else:
            if (_pip_prev == None): woiSignal_prev = None
            else:                   woiSignal_prev = _pip_prev['WOISIGNAL']
            if (woiSignal_prev == None): woiSignal_AbsMA = abs(woiSignal)
            else:                        
                _woiSignal_AbsMA_prev = _pip_prev['WOISIGNAL_ABSMA']
                if (_woiSignal_AbsMA_prev == None): woiSignal_AbsMA = abs(woiSignal)*_absMA_kValue + abs(woiSignal_prev)  *(1-_absMA_kValue)
                else:                               woiSignal_AbsMA = abs(woiSignal)*_absMA_kValue + _woiSignal_AbsMA_prev*(1-_absMA_kValue)
        #WOI Signal AbsMA Relative
        if   (woiSignal_AbsMA == None): woiSignal_AbsMARel = None
        elif (woiSignal_AbsMA == 0):    woiSignal_AbsMARel = 0
        else:                           woiSignal_AbsMARel = round(woiSignal/woiSignal_AbsMA, 3)
        if (woiSignal_AbsMARel != None):
            if (0 <= woiSignal_AbsMARel): woiSignal_AbsMARel =  abs(round(math.atan(pow(woiSignal_AbsMARel/1.0, 2))*2/math.pi, 5))
            else:                         woiSignal_AbsMARel = -abs(round(math.atan(pow(woiSignal_AbsMARel/1.0, 2))*2/math.pi, 5))

    #NES Signal
    if (True):
        #NES Signal
        nesSignal = None
        if (aggTrades != None):
            #NES Filtered Gradients
            _nes_filtered = list()
            if (timestamp in aggTrades['NES']):
                for _dType in aggTrades:
                    if not((_dType == 'volumes') or (_dType == 'NES')):
                        _data = aggTrades[_dType][timestamp][1]
                        if (_data == None): _nes_filtered = None; break
                        else: _nes_filtered.append(_data)
            #NES Combined
            if (_nes_filtered != None): 
                _nLines = len(_nes_filtered)
                if (_nLines != 0): nesSignal = round(sum(_nes_filtered)/_nLines, 5)
        #NES Signal AbsMA
        _absMA_kValue = 2/(288+1)
        if (nesSignal == None): nesSignal_AbsMA = None
        else:
            if (_pip_prev == None): nesSignal_prev = None
            else:                   nesSignal_prev = _pip_prev['NESSIGNAL']
            if (nesSignal_prev == None): nesSignal_AbsMA = abs(nesSignal)
            else:                        
                _nesSignal_AbsMA_prev = _pip_prev['NESSIGNAL_ABSMA']
                if (_nesSignal_AbsMA_prev == None): nesSignal_AbsMA = abs(nesSignal)*_absMA_kValue + abs(nesSignal_prev)  *(1-_absMA_kValue)
                else:                               nesSignal_AbsMA = abs(nesSignal)*_absMA_kValue + _nesSignal_AbsMA_prev*(1-_absMA_kValue)
        #NES Signal AbsMA Relative
        if   (nesSignal_AbsMA == None): nesSignal_AbsMARel = None
        elif (nesSignal_AbsMA == 0):    nesSignal_AbsMARel = 0
        else:                           nesSignal_AbsMARel = round(nesSignal/nesSignal_AbsMA, 3)
        if (nesSignal_AbsMARel != None):
            if (0 <= nesSignal_AbsMARel): nesSignal_AbsMARel =  abs(round(math.atan(pow(nesSignal_AbsMARel/1.0, 2))*2/math.pi, 5))
            else:                         nesSignal_AbsMARel = -abs(round(math.atan(pow(nesSignal_AbsMARel/1.0, 2))*2/math.pi, 5))

    #Classical analysis interpretation
    if (True):
        #---IVP
        if (True):
            ivpTouched = False
            if ('IVP' in REFERREDANALYSISCODES):
                _ivp = klineAccess['IVP'][timestamp]
                _ivp_divisionHeight = _ivp['divisionHeight']
                _ivp_ivpBoundaries  = _ivp['volumePriceLevelProfile_Boundaries']
                if (_ivp_ivpBoundaries != None):
                    nIVPBoundaries = len(_ivp_ivpBoundaries)
                    for _bIndex in range (1, nIVPBoundaries-1):
                        _bCenter = round((_ivp_ivpBoundaries[_bIndex]+0.5)*_ivp_divisionHeight, precisions['price'])
                        _cls = 0
                        _cls += 0b1000*(0 <= _kline[KLINDEX_LOWPRICE] -_bCenter*0.999)
                        _cls += 0b0100*(0 <= _kline[KLINDEX_LOWPRICE] -_bCenter*1.001)
                        _cls += 0b0010*(0 <  _kline[KLINDEX_HIGHPRICE]-_bCenter*0.999)
                        _cls += 0b0001*(0 <  _kline[KLINDEX_HIGHPRICE]-_bCenter*1.001)
                        if ((_cls == 0b0010) or (_cls == 0b1010) or (_cls == 0b1011) or (_cls == 0b0011)): ivpTouched = True; break
        #---Classical Signal
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
                classicalSignal_Cycle           = None
                classicalSignal_CycleUpdated    = False
                classicalSignal_CycleContIndex  = None
                classicalSignal_CycleBeginPrice = None
            else:                   
                classicalSignal_Cycle           = _pip_prev['CLASSICALSIGNAL_CYCLE']
                classicalSignal_CycleUpdated    = False
                classicalSignal_CycleContIndex  = _pip_prev['CLASSICALSIGNAL_CYCLECONTINDEX']
                classicalSignal_CycleBeginPrice = _pip_prev['CLASSICALSIGNAL_CYCLEBEGINPRICE']
            if ((classicalSignal_Cycle is None) and (classicalSignal_Filtered is not None)):
                if   (classicalSignal_Filtered < 0): classicalSignal_Cycle = 'LOW'
                elif (0 < classicalSignal_Filtered): classicalSignal_Cycle = 'HIGH'
                if (classicalSignal_Cycle is not None):
                    classicalSignal_CycleUpdated    = True
                    classicalSignal_CycleContIndex  = 0
                    classicalSignal_CycleBeginPrice = _kline[KLINDEX_CLOSEPRICE]
            elif (classicalSignal_Cycle is not None):
                classicalSignal_CycleContIndex += 1
                if   ((classicalSignal_Cycle == 'LOW')  and (0 < classicalSignal_Filtered)): 
                    classicalSignal_Cycle           = 'HIGH'
                    classicalSignal_CycleUpdated    = True
                    classicalSignal_CycleContIndex  = 0
                    classicalSignal_CycleBeginPrice = _kline[KLINDEX_CLOSEPRICE]
                elif ((classicalSignal_Cycle == 'HIGH') and (classicalSignal_Filtered < 0)): 
                    classicalSignal_Cycle           = 'LOW'
                    classicalSignal_CycleUpdated    = True
                    classicalSignal_CycleContIndex  = 0
                    classicalSignal_CycleBeginPrice = _kline[KLINDEX_CLOSEPRICE]
    
    #Action Signal
    if (True):
        actionSignal = None
        if (True):
            if (classicalSignal_ImpulseCycleUpdated == True):
                _allowEntry = (classicalSignal_Cycle != classicalSignal_ImpulseCycle)
                if   (classicalSignal_ImpulseCycle == 'SHORT'): actionSignal = {'side': 'BUY'}
                elif (classicalSignal_ImpulseCycle == 'LONG'):  actionSignal = {'side': 'SELL'}
            """
            if (ivpTouched == True) and (classicalSignal_Filtered != None):
                if (classicalSignal_Filtered < 0):
                    actionSignal = ('BUY',  True, None, None, None, None)
                elif (0 < classicalSignal_Filtered):
                    actionSignal = ('SELL', False, None, None, None, None)
            """
            """
            if ((classicalSignal_Filtered < 0) and (0 < classicalSignal_Filtered_Delta)) or ((0 < classicalSignal_Filtered) and (0 < classicalSignal_Filtered_Delta)): 
                if (swings[-1][2] == _PIP_SWINGTYPE_LOW): _slPrice = swings[-1][1]
                else:                                     _slPrice = swings[-2][1]
                #_slPrice       = round(_kline[KLINDEX_CLOSEPRICE]-(_kline[KLINDEX_CLOSEPRICE]-_kline[KLINDEX_LOWPRICE])*2.0, precisions['price'])
                #_slPrice_delta = _kline[KLINDEX_CLOSEPRICE]-_slPrice
                #_tpPrice       = round((_kline[KLINDEX_CLOSEPRICE]*1.001)+_slPrice_delta*2, precisions['price'])
                actionSignal = ('BUY',  True, None, None, _slPrice, None)
            elif ((0 < classicalSignal_Filtered) and (classicalSignal_Filtered_Delta < 0)) or ((classicalSignal_Filtered < 0) and (classicalSignal_Filtered_Delta < 0)): 
                if (swings[-1][2] == _PIP_SWINGTYPE_HIGH): _slPrice = swings[-1][1]
                else:                                      _slPrice = swings[-2][1]
                #_slPrice       = round(_kline[KLINDEX_CLOSEPRICE]+(_kline[KLINDEX_HIGHPRICE]-_kline[KLINDEX_CLOSEPRICE])*2.0, precisions['price'])
                #_slPrice_delta = _slPrice-_kline[KLINDEX_CLOSEPRICE]
                #_tpPrice       = round((_kline[KLINDEX_CLOSEPRICE]*0.999)-_slPrice_delta*2, precisions['price'])
                actionSignal = ('SELL', True, None, None, _slPrice, None)
            """
            """
            if ((bidsAndAsks != None) and (aggTrades != None)):
                if ((_classicalTrend != None) and (classicalSignal_fGrad != None) and (woiSignal != None) and (nesSignal != None)):
                    #Major Trend
                    _majorTrendUpdate = False
                    #---Recent PIP
                    if   (timestamp in klineAccess['PIP']): lastTrend = klineAccess['PIP'][timestamp]['_LASTTREND']
                    elif (_pip_previous != None):           lastTrend = _pip_previous['_LASTTREND']
                    #---Trend Update
                    if (lastTrend == None):
                        if   (_classicalTrend == 'SHORT'): lastTrend = 'SHORT'
                        elif (_classicalTrend == 'LONG'):  lastTrend = 'LONG'
                    elif (lastTrend == 'SHORT'):
                        if ((_classicalTrend == 'LONG') and (AT_WS < woiSignal)): lastTrend = 'LONG'; _majorTrendUpdate = True
                    elif (lastTrend == 'LONG'):
                        if ((_classicalTrend == 'SHORT') and (woiSignal < -AT_WS)): lastTrend = 'SHORT'; _majorTrendUpdate = True
                    #Decision Making
                    if (_majorTrendUpdate == True):
                        if   (lastTrend == 'SHORT'): actionSignal = ['SELL', False, 'LONGESCAPE']
                        elif (lastTrend == 'LONG'):  actionSignal = ['BUY',  False, 'SHORTESCAPE']
                    elif (classicalSignal_fGrad_AbsMARel_CycleWeakened == True):
                        if (neuralNetwork == None):
                            if   ((classicalSignal_fGrad < 0) and (nesSignal < 0)): actionSignal = ['BUY',  (lastTrend == 'LONG'),  None]
                            elif ((0 < classicalSignal_fGrad) and (0 < nesSignal)): actionSignal = ['SELL', (lastTrend == 'SHORT'), None]
                        elif (nnaSignal != None):
                            if   ((classicalSignal_fGrad < 0) and (nesSignal < 0) and (nnaSignal < 0)): actionSignal = ['BUY',  (lastTrend == 'LONG'),  None]
                            elif ((0 < classicalSignal_fGrad) and (0 < nesSignal) and (0 < nnaSignal)): actionSignal = ['SELL', (lastTrend == 'SHORT'), None]
            else:
                if (classicalSignal_Filtered != None):
                    #Major Trend
                    _majorTrendUpdate = False
                    #---Recent PIP
                    if   (timestamp in klineAccess['PIP']): lastTrend = klineAccess['PIP'][timestamp]['_LASTTREND']
                    elif (_pip_previous != None):           lastTrend = _pip_previous['_LASTTREND']
                    #---Trend Update
                    if (lastTrend == None):
                        if   (_classicalTrend == 'SHORT'): lastTrend = 'SHORT'
                        elif (_classicalTrend == 'LONG'):  lastTrend = 'LONG'
                    elif (lastTrend == 'SHORT'):
                        if (_classicalTrend == 'LONG'): lastTrend = 'LONG'; _majorTrendUpdate = True
                    elif (lastTrend == 'LONG'):
                        if (_classicalTrend == 'SHORT'): lastTrend = 'SHORT'; _majorTrendUpdate = True
                    #---Decision Making
                    if (_majorTrendUpdate == True):
                        if   (lastTrend == 'SHORT'): actionSignal = ['SELL', False, 'LONGESCAPE']
                        elif (lastTrend == 'LONG'):  actionSignal = ['BUY',  False, 'SHORTESCAPE']
                    elif (classicalSignal_fGrad_AbsMARel_CycleWeakened == True):
                        if (neuralNetwork == None):
                            if   (classicalSignal_fGrad < 0): actionSignal = ['BUY',  (lastTrend == 'LONG'),  None]
                            elif (0 < classicalSignal_fGrad): actionSignal = ['SELL', (lastTrend == 'SHORT'), None]
                        elif (nnaSignal != None):
                            if   ((classicalSignal_fGrad < 0) and (nnaSignal < 0)): actionSignal = ['BUY',  (lastTrend == 'LONG'),  None]
                            elif ((0 < classicalSignal_fGrad) and (0 < nnaSignal)): actionSignal = ['SELL', (lastTrend == 'SHORT'), None]
            """
    
    #Result formatting & saving
    pipResult = {'SWINGS': swings, '_SWINGSEARCH': swingSearch, 
                 'NNASIGNAL': nnaSignal, 
                 'WOISIGNAL':          woiSignal, 
                 'WOISIGNAL_ABSMA':    woiSignal_AbsMA, 
                 'WOISIGNAL_ABSMAREL': woiSignal_AbsMARel,
                 'NESSIGNAL':          nesSignal, 
                 'NESSIGNAL_ABSMA':    nesSignal_AbsMA,
                 'NESSIGNAL_ABSMAREL': nesSignal_AbsMARel,

                 'CLASSICALSIGNAL':                 classicalSignal, 
                 'CLASSICALSIGNAL_DELTA':           classicalSignal_Delta, 
                 'CLASSICALSIGNAL_FILTERED':        classicalSignal_Filtered, 
                 'CLASSICALSIGNAL_FILTERED_DELTA':  classicalSignal_Filtered_Delta, 
                 'CLASSICALSIGNAL_CYCLE':           classicalSignal_Cycle,
                 'CLASSICALSIGNAL_CYCLEUPDATED':    classicalSignal_CycleUpdated,
                 'CLASSICALSIGNAL_CYCLECONTINDEX':  classicalSignal_CycleContIndex,
                 'CLASSICALSIGNAL_CYCLEBEGINPRICE': classicalSignal_CycleBeginPrice,
                 #Action Signal
                 'ACTIONSIGNAL':   actionSignal, 
                 '_analysisCount': _analysisCount}
    klineAccess[analysisCode][timestamp] = pipResult
    #Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    if (neuralNetwork == None): return (NSAMPLES_CS, 2)
    else:                       return (max(NSAMPLES_CS, _nn_nKlines), _nn_nKlines)

def analysisGenerator_VOL(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    nSamples   = analysisParams['nSamples']
    volumeType = analysisParams['volumeType']
    MAType     = analysisParams['MAType']
    analysisCode = 'VOL_{:d}'.format(nSamples)
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

def analysisGenerator_MMACDSHORT(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    signal_nSamples  = analysisParams['signal_nSamples']
    signal_kValue    = 2/(signal_nSamples+1)
    multiplier       = analysisParams['multiplier']
    activatedMAs     = analysisParams['activatedMAs']
    activatedMAPairs = analysisParams['activatedMAPairs']
    maxMANSamples     = analysisParams['maxMANSamples']
    absoluteMA_kValue = 2/(maxMANSamples+1)
    analysisCode = 'MMACDSHORT'
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

def analysisGenerator_MMACDLONG(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    signal_nSamples  = analysisParams['signal_nSamples']
    signal_kValue    = 2/(signal_nSamples+1)
    multiplier       = analysisParams['multiplier']
    activatedMAs     = analysisParams['activatedMAs']
    activatedMAPairs = analysisParams['activatedMAPairs']
    maxMANSamples     = analysisParams['maxMANSamples']
    absoluteMA_kValue = 2/(maxMANSamples+1)/10
    analysisCode = 'MMACDLONG'
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
    
def analysisGenerator_DMIxADX(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    nSamples = analysisParams['nSamples']
    analysisCode = "DMIxADX_{:d}".format(nSamples)
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
    
def analysisGenerator_MFI(klineAccess, intervalID, mrktRegTS, precisions, timestamp, neuralNetwork, bidsAndAsks, aggTrades, **analysisParams):
    nSamples = analysisParams['nSamples']
    analysisCode = "MFI_{:d}".format(nSamples)
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
                        'PIP':        analysisGenerator_PIP,
                        'VOL':        analysisGenerator_VOL,
                        'MMACDSHORT': analysisGenerator_MMACDSHORT,
                        'MMACDLONG':  analysisGenerator_MMACDLONG,
                        'DMIxADX':    analysisGenerator_DMIxADX,
                        'MFI':        analysisGenerator_MFI}
def analysisGenerator(analysisType, **params): 
    return __analysisGenerators[analysisType](**params)
def constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(currencyAnalysisConfiguration):
    _currencyAnalysisParams = dict()
    if (currencyAnalysisConfiguration['SMA_Master'] == True):
        for lineIndex in range (10):
            lineNumber = lineIndex+1
            if (currencyAnalysisConfiguration['SMA_{:d}_LineActive'.format(lineNumber)] == True):
                _nSamples   = currencyAnalysisConfiguration['SMA_{:d}_NSamples'.format(lineNumber)]
                try:
                    if (2 <= _nSamples):
                        _analysisCode = 'SMA_{:d}'.format(_nSamples)
                        _currencyAnalysisParams[_analysisCode] = {'lineNumber': lineNumber,
                                                                  'nSamples':   _nSamples}
                except: return None
    if (currencyAnalysisConfiguration['WMA_Master'] == True):
        for lineIndex in range (10):
            lineNumber = lineIndex+1
            if (currencyAnalysisConfiguration['WMA_{:d}_LineActive'.format(lineNumber)] == True):
                _nSamples   = currencyAnalysisConfiguration['WMA_{:d}_NSamples'.format(lineNumber)]
                try:
                    if (2 <= _nSamples):
                        _analysisCode = 'WMA_{:d}'.format(_nSamples)
                        _currencyAnalysisParams[_analysisCode] = {'lineNumber': lineNumber,
                                                                  'nSamples':   _nSamples}
                except: return None
    if (currencyAnalysisConfiguration['EMA_Master'] == True):
        for lineIndex in range (10):
            lineNumber = lineIndex+1
            if (currencyAnalysisConfiguration['EMA_{:d}_LineActive'.format(lineNumber)] == True):
                _nSamples   = currencyAnalysisConfiguration['EMA_{:d}_NSamples'.format(lineNumber)]
                try:
                    if (2 <= _nSamples):
                        _analysisCode = 'EMA_{:d}'.format(_nSamples)
                        _currencyAnalysisParams[_analysisCode] = {'lineNumber': lineNumber,
                                                                  'nSamples':   _nSamples}
                except: return None
    if (currencyAnalysisConfiguration['PSAR_Master'] == True):
        for lineIndex in range (5):
            lineNumber = lineIndex+1
            if (currencyAnalysisConfiguration['PSAR_{:d}_LineActive'.format(lineNumber)] == True):
                _AF_initial      = currencyAnalysisConfiguration['PSAR_{:d}_AF0'.format(lineNumber)]
                _AF_acceleration = currencyAnalysisConfiguration['PSAR_{:d}_AF+'.format(lineNumber)]
                _AF_maximum      = currencyAnalysisConfiguration['PSAR_{:d}_AFMax'.format(lineNumber)]
                try:
                    if ((0 <= _AF_initial) and (0 < _AF_acceleration) and (0 < _AF_maximum) and (_AF_initial < _AF_maximum)):
                        _analysisCode = 'PSAR_{:.3f}_{:.3f}_{:.3f}'.format(_AF_initial, _AF_acceleration, _AF_maximum)
                        _currencyAnalysisParams[_analysisCode] = {'lineNumber':   lineNumber,
                                                                  'start':        _AF_initial,
                                                                  'acceleration': _AF_acceleration,
                                                                  'maximum':      _AF_maximum}
                except: return None
    if (currencyAnalysisConfiguration['BOL_Master'] == True):
        for lineIndex in range (10):
            lineNumber = lineIndex+1
            if (currencyAnalysisConfiguration['BOL_{:d}_LineActive'.format(lineNumber)] == True):
                _nSamples  = currencyAnalysisConfiguration['BOL_{:d}_NSamples'.format(lineNumber)]
                _bandWidth = currencyAnalysisConfiguration['BOL_{:d}_BandWidth'.format(lineNumber)]
                try:
                    if ((2 <= _nSamples) and (0 < _bandWidth)):
                        _analysisCode = 'BOL_{:d}_{:.1f}'.format(_nSamples, _bandWidth)
                        _currencyAnalysisParams[_analysisCode] = {'lineNumber': lineNumber,
                                                                  'MAType':     currencyAnalysisConfiguration['BOL_MAType'],
                                                                  'nSamples':   _nSamples,
                                                                  'bandWidth':  _bandWidth}
                except: return None
    if (currencyAnalysisConfiguration['IVP_Master'] == True):
        _analysisCode = 'IVP'
        _currencyAnalysisParams[_analysisCode] = {'nSamples':    currencyAnalysisConfiguration['IVP_NSamples'],
                                                  'gammaFactor': currencyAnalysisConfiguration['IVP_GammaFactor'],
                                                  'deltaFactor': currencyAnalysisConfiguration['IVP_DeltaFactor']}
    if (currencyAnalysisConfiguration['VOL_Master'] == True):
        for lineIndex in range (5):
            lineNumber = lineIndex+1
            if (currencyAnalysisConfiguration['VOL_{:d}_LineActive'.format(lineNumber)] == True):
                _nSamples = currencyAnalysisConfiguration['VOL_{:d}_NSamples'.format(lineNumber)]
                try:
                    if (2 <= _nSamples):
                        _analysisCode = "VOL_{:d}".format(_nSamples)
                        _currencyAnalysisParams[_analysisCode] = {'lineNumber': lineNumber,
                                                                  'nSamples':   _nSamples,
                                                                  'volumeType': currencyAnalysisConfiguration['VOL_VolumeType'],
                                                                  'MAType':     currencyAnalysisConfiguration['VOL_MAType']}
                except: return None
    if (currencyAnalysisConfiguration['MMACDSHORT_Master'] == True):
        _analysisCode = "MMACDSHORT"
        _activatedMAs = list()
        for lineIndex in range (6):
            lineNumber = lineIndex+1
            if (currencyAnalysisConfiguration['MMACDSHORT_MA{:d}_LineActive'.format(lineNumber)] == True): 
                _nSamples = currencyAnalysisConfiguration['MMACDSHORT_MA{:d}_NSamples'.format(lineNumber)]
                try:
                    if (2 <= _nSamples): _activatedMAs.append(_nSamples)
                except: return None
        if (2 <= len(_activatedMAs)):
            _activatedMAs.sort()
            _activatedMAPairs = list()
            for maPairTargetIndex_short in range (0, len(_activatedMAs)-1):
                for maPairTargetIndex_long in range (maPairTargetIndex_short+1, len(_activatedMAs)): _activatedMAPairs.append((_activatedMAs[maPairTargetIndex_short], _activatedMAs[maPairTargetIndex_long]))
            _maxMANSamples = max(_activatedMAs)
            _currencyAnalysisParams[_analysisCode] = {'signal_nSamples':  currencyAnalysisConfiguration['MMACDSHORT_SignalNSamples'],
                                                      'multiplier':       currencyAnalysisConfiguration['MMACDSHORT_Multiplier'],
                                                      'activatedMAs':     _activatedMAs,
                                                      'activatedMAPairs': _activatedMAPairs,
                                                      'maxMANSamples':    _maxMANSamples}
    if (currencyAnalysisConfiguration['MMACDLONG_Master'] == True):
        _analysisCode = "MMACDLONG"
        _activatedMAs = list()
        for lineIndex in range (6):
            lineNumber = lineIndex+1
            if (currencyAnalysisConfiguration['MMACDLONG_MA{:d}_LineActive'.format(lineNumber)] == True): 
                _nSamples = currencyAnalysisConfiguration['MMACDLONG_MA{:d}_NSamples'.format(lineNumber)]
                try:
                    if (2 <= _nSamples): _activatedMAs.append(_nSamples)
                except: return None
        if (2 <= len(_activatedMAs)):
            _activatedMAs.sort()
            _activatedMAPairs = list()
            for maPairTargetIndex_short in range (0, len(_activatedMAs)-1):
                for maPairTargetIndex_long in range (maPairTargetIndex_short+1, len(_activatedMAs)): _activatedMAPairs.append((_activatedMAs[maPairTargetIndex_short], _activatedMAs[maPairTargetIndex_long]))
            _maxMANSamples = max(_activatedMAs)
            _currencyAnalysisParams[_analysisCode] = {'signal_nSamples':  currencyAnalysisConfiguration['MMACDLONG_SignalNSamples'],
                                                      'multiplier':       currencyAnalysisConfiguration['MMACDLONG_Multiplier'],
                                                      'activatedMAs':     _activatedMAs,
                                                      'activatedMAPairs': _activatedMAPairs,
                                                      'maxMANSamples':    _maxMANSamples}
    if (currencyAnalysisConfiguration['DMIxADX_Master'] == True):
        for lineIndex in range (5):
            lineNumber = lineIndex+1
            if (currencyAnalysisConfiguration['DMIxADX_{:d}_LineActive'.format(lineNumber)] == True):
                _nSamples   = currencyAnalysisConfiguration['DMIxADX_{:d}_NSamples'.format(lineNumber)]
                try:
                    if (2 <= _nSamples):
                        _analysisCode = 'DMIxADX_{:d}'.format(_nSamples)
                        _currencyAnalysisParams[_analysisCode] = {'lineNumber': lineNumber,
                                                                  'nSamples':   _nSamples}
                except: return None
    if (currencyAnalysisConfiguration['MFI_Master'] == True):
        for lineIndex in range (5):
            lineNumber = lineIndex+1
            if (currencyAnalysisConfiguration['MFI_{:d}_LineActive'.format(lineNumber)] == True):
                _nSamples   = currencyAnalysisConfiguration['MFI_{:d}_NSamples'.format(lineNumber)]
                try:
                    if (2 <= _nSamples):
                        _analysisCode = 'MFI_{:d}'.format(_nSamples)
                        _currencyAnalysisParams[_analysisCode] = {'lineNumber': lineNumber,
                                                                  'nSamples':   _nSamples}
                except: return None
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
                                                  'csActivationThreshold1': currencyAnalysisConfiguration['PIP_CSActivationThreshold1'],
                                                  'csActivationThreshold2': currencyAnalysisConfiguration['PIP_CSActivationThreshold2'],
                                                  'wsActivationThreshold':  currencyAnalysisConfiguration['PIP_WSActivationThreshold'],
                                                  'actionSignalMode':       currencyAnalysisConfiguration['PIP_ActionSignalMode'],
                                                  }
    #Return the constructed analysis params
    return _currencyAnalysisParams