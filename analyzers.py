import auxiliaries
import neural_networks
import constants

import random
import math
import numpy
import datetime
import pprint
import torch
import time
import scipy
from collections import defaultdict, deque

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

DEPTHBINS     = constants.DEPTHBINS
DEPTHBINS_MIN = min(db[0] for db in DEPTHBINS.values())
DEPTHBINS_MAX = max(db[1] for db in DEPTHBINS.values())

ANALYSIS_MITYPES = ('SMA', 'WMA', 'EMA', 'PSAR', 'BOL', 'IVP', 'SWING')
ANALYSIS_SITYPES = ('VOL', 'DEPTH', 'AGGTRADE', 'NNA', 'MMACD', 'DMIxADX', 'MFI', 'TPD', 'WOI', 'NES')

ANALYSIS_GENERATIONORDER = ('SMA', 'WMA', 'EMA', 'PSAR', 'BOL', 'IVP', 'SWING', 'VOL', 'NNA', 'MMACD', 'DMIxADX', 'MFI', 'TPD', 'WOI', 'NES')

#Aggregation --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def aggregator_kline(dataRaw, dataAgg, lastClosedAggs, rawOpenTS, aggOpenTS, aggIntervalID, precisions):
    #[1]: Instances
    kline_raw = dataRaw[rawOpenTS]
    lcAgg     = lastClosedAggs.get(aggOpenTS, None)
    is_dummy  = kline_raw[KLINDEX_SOURCE] in (FORMATTEDDATATYPE_EMPTY, FORMATTEDDATATYPE_DUMMY)

    #[2]: Initialize Or Base From The Last Closed Aggregation
    if lcAgg is None:
        if is_dummy:
            kline_agg = (aggOpenTS,
                         auxiliaries.getNextIntervalTickTimestamp(intervalID = aggIntervalID, timestamp = aggOpenTS, nTicks = 1)-1,
                         None, None, None, None, None, None, None, None, None,
                         kline_raw[KLINDEX_CLOSED],
                         FORMATTEDDATATYPE_DUMMY)
            dataAgg[aggOpenTS] = kline_agg
            if kline_raw[KLINDEX_CLOSED]:
                lastClosedAggs[aggOpenTS] = kline_agg
            return
        agg_openTime   = aggOpenTS
        agg_closeTime  = auxiliaries.getNextIntervalTickTimestamp(intervalID = aggIntervalID, timestamp = aggOpenTS, nTicks = 1)-1
        agg_openPrice  = kline_raw[KLINDEX_OPENPRICE]
        agg_highPrice  = kline_raw[KLINDEX_HIGHPRICE]
        agg_lowPrice   = kline_raw[KLINDEX_LOWPRICE]
        agg_closePrice = kline_raw[KLINDEX_CLOSEPRICE]
        agg_nTrades    = kline_raw[KLINDEX_NTRADES]
        agg_volBase    = kline_raw[KLINDEX_VOLBASE]
        agg_volQuote   = kline_raw[KLINDEX_VOLQUOTE]
        agg_volBaseTB  = kline_raw[KLINDEX_VOLBASETAKERBUY]
        agg_volQuoteTB = kline_raw[KLINDEX_VOLQUOTETAKERBUY]
        agg_source     = kline_raw[KLINDEX_SOURCE]
    else:
        if is_dummy:
            agg_closed = (lcAgg[KLINDEX_CLOSETIME] == kline_raw[KLINDEX_CLOSETIME] and kline_raw[KLINDEX_CLOSED])
            kline_agg  = lcAgg[:KLINDEX_CLOSED] + (agg_closed,) + (lcAgg[KLINDEX_SOURCE],)
            dataAgg[aggOpenTS] = kline_agg
            if kline_raw[KLINDEX_CLOSED]:
                lastClosedAggs[aggOpenTS] = kline_agg
            return
        agg_openTime   = lcAgg[KLINDEX_OPENTIME]
        agg_closeTime  = lcAgg[KLINDEX_CLOSETIME]
        agg_openPrice  = lcAgg[KLINDEX_OPENPRICE] or kline_raw[KLINDEX_OPENPRICE]
        agg_highPrice  = max(lcAgg[KLINDEX_HIGHPRICE], kline_raw[KLINDEX_HIGHPRICE]) if lcAgg[KLINDEX_HIGHPRICE] is not None else kline_raw[KLINDEX_HIGHPRICE]
        agg_lowPrice   = min(lcAgg[KLINDEX_LOWPRICE],  kline_raw[KLINDEX_LOWPRICE])  if lcAgg[KLINDEX_LOWPRICE]  is not None else kline_raw[KLINDEX_LOWPRICE]
        agg_closePrice = kline_raw[KLINDEX_CLOSEPRICE] or lcAgg[KLINDEX_CLOSEPRICE]
        agg_nTrades    = (lcAgg[KLINDEX_NTRADES]                or 0) + kline_raw[KLINDEX_NTRADES]
        agg_volBase    = round((lcAgg[KLINDEX_VOLBASE]          or 0) + kline_raw[KLINDEX_VOLBASE],          precisions['quantity'])
        agg_volQuote   = round((lcAgg[KLINDEX_VOLQUOTE]         or 0) + kline_raw[KLINDEX_VOLQUOTE],         precisions['quantity'])
        agg_volBaseTB  = round((lcAgg[KLINDEX_VOLBASETAKERBUY]  or 0) + kline_raw[KLINDEX_VOLBASETAKERBUY],  precisions['quote'])
        agg_volQuoteTB = round((lcAgg[KLINDEX_VOLQUOTETAKERBUY] or 0) + kline_raw[KLINDEX_VOLQUOTETAKERBUY], precisions['quote'])
        agg_source     = lcAgg[KLINDEX_SOURCE]

    #[3]: Determine Aggregation Closed
    agg_closed = (agg_closeTime == kline_raw[KLINDEX_CLOSETIME] and kline_raw[KLINDEX_CLOSED])

    #[4]: Build Aggregated Kline Tuple
    kline_agg = (agg_openTime, agg_closeTime, agg_openPrice, agg_highPrice, agg_lowPrice, agg_closePrice,
                 agg_nTrades, agg_volBase, agg_volQuote, agg_volBaseTB, agg_volQuoteTB, agg_closed, agg_source)

    #[5]: Save New Aggregation
    dataAgg[aggOpenTS] = kline_agg
    if kline_raw[KLINDEX_CLOSED]:
        lastClosedAggs[aggOpenTS] = kline_agg

def aggregator_depth(dataRaw, dataAgg, lastClosedAggs, rawOpenTS, aggOpenTS, aggIntervalID, precisions):
    #[1]: Instances
    depth_raw = dataRaw[rawOpenTS]
    is_dummy  = depth_raw[DEPTHINDEX_SOURCE] in (FORMATTEDDATATYPE_EMPTY, FORMATTEDDATATYPE_DUMMY)

    #[2]: Determine Aggregation Closed
    agg_closeTime = auxiliaries.getNextIntervalTickTimestamp(intervalID = aggIntervalID, timestamp = aggOpenTS, nTicks = 1)-1
    agg_closed    = (agg_closeTime == depth_raw[DEPTHINDEX_CLOSETIME] and depth_raw[DEPTHINDEX_CLOSED])

    #[3]: Build Aggregated Depth Tuple (Latest Snapshot)
    if is_dummy:
        existing = dataAgg.get(aggOpenTS, None)
        if existing is None:
            depth_agg = (aggOpenTS, agg_closeTime,
                         None, None, None, None, None, None,
                         None, None, None, None, None, None,
                         agg_closed, FORMATTEDDATATYPE_DUMMY)
        else:
            depth_agg = existing[:DEPTHINDEX_CLOSED] + (agg_closed, existing[DEPTHINDEX_SOURCE])
    else:
        depth_agg = (aggOpenTS, agg_closeTime,
                     depth_raw[DEPTHINDEX_BIDS5],
                     depth_raw[DEPTHINDEX_BIDS4],
                     depth_raw[DEPTHINDEX_BIDS3],
                     depth_raw[DEPTHINDEX_BIDS2],
                     depth_raw[DEPTHINDEX_BIDS1],
                     depth_raw[DEPTHINDEX_BIDS0],
                     depth_raw[DEPTHINDEX_ASKS0],
                     depth_raw[DEPTHINDEX_ASKS1],
                     depth_raw[DEPTHINDEX_ASKS2],
                     depth_raw[DEPTHINDEX_ASKS3],
                     depth_raw[DEPTHINDEX_ASKS4],
                     depth_raw[DEPTHINDEX_ASKS5],
                     agg_closed,
                     depth_raw[DEPTHINDEX_SOURCE])

    #[4]: Save New Aggregation
    dataAgg[aggOpenTS] = depth_agg

def aggregator_aggTrade(dataRaw, dataAgg, lastClosedAggs, rawOpenTS, aggOpenTS, aggIntervalID, precisions):
    #[1]: Instances
    aggTrade_raw = dataRaw[rawOpenTS]
    lcAgg        = lastClosedAggs.get(aggOpenTS, None)
    is_dummy     = aggTrade_raw[ATINDEX_SOURCE] in (FORMATTEDDATATYPE_EMPTY, FORMATTEDDATATYPE_DUMMY)

    #[2]: Initialize Or Base From The Last Closed Aggregation
    if lcAgg is None:
        if is_dummy:
            aggTrade_agg = (aggOpenTS,
                            auxiliaries.getNextIntervalTickTimestamp(intervalID = aggIntervalID, timestamp = aggOpenTS, nTicks = 1)-1,
                            None, None, None, None, None, None,
                            aggTrade_raw[ATINDEX_CLOSED],
                            FORMATTEDDATATYPE_DUMMY)
            dataAgg[aggOpenTS] = aggTrade_agg
            if aggTrade_raw[ATINDEX_CLOSED]:
                lastClosedAggs[aggOpenTS] = aggTrade_agg
            return
        agg_quantityBuy  = aggTrade_raw[ATINDEX_QUANTITYBUY]
        agg_quantitySell = aggTrade_raw[ATINDEX_QUANTITYSELL]
        agg_nTradesBuy   = aggTrade_raw[ATINDEX_NTRADESBUY]
        agg_nTradesSell  = aggTrade_raw[ATINDEX_NTRADESSELL]
        agg_notionalBuy  = aggTrade_raw[ATINDEX_NOTIONALBUY]
        agg_notionalSell = aggTrade_raw[ATINDEX_NOTIONALSELL]
        agg_source       = aggTrade_raw[ATINDEX_SOURCE]
    else:
        if is_dummy:
            agg_closed   = (lcAgg[ATINDEX_CLOSETIME] == aggTrade_raw[ATINDEX_CLOSETIME] and aggTrade_raw[ATINDEX_CLOSED])
            aggTrade_agg = lcAgg[:ATINDEX_CLOSED] + (agg_closed,) + (lcAgg[ATINDEX_SOURCE],)
            dataAgg[aggOpenTS] = aggTrade_agg
            if aggTrade_raw[ATINDEX_CLOSED]:
                lastClosedAggs[aggOpenTS] = aggTrade_agg
            return
        agg_quantityBuy  = round((lcAgg[ATINDEX_QUANTITYBUY]  or 0) + aggTrade_raw[ATINDEX_QUANTITYBUY],  precisions['quantity'])
        agg_quantitySell = round((lcAgg[ATINDEX_QUANTITYSELL] or 0) + aggTrade_raw[ATINDEX_QUANTITYSELL], precisions['quantity'])
        agg_nTradesBuy   = (lcAgg[ATINDEX_NTRADESBUY]  or 0) + aggTrade_raw[ATINDEX_NTRADESBUY]
        agg_nTradesSell  = (lcAgg[ATINDEX_NTRADESSELL] or 0) + aggTrade_raw[ATINDEX_NTRADESSELL]
        agg_notionalBuy  = round((lcAgg[ATINDEX_NOTIONALBUY]  or 0) + aggTrade_raw[ATINDEX_NOTIONALBUY],  precisions['quote'])
        agg_notionalSell = round((lcAgg[ATINDEX_NOTIONALSELL] or 0) + aggTrade_raw[ATINDEX_NOTIONALSELL], precisions['quote'])
        agg_source       = lcAgg[ATINDEX_SOURCE]

    #[3]: Determine Aggregation Closed
    agg_closeTime = auxiliaries.getNextIntervalTickTimestamp(intervalID = aggIntervalID, timestamp = aggOpenTS, nTicks = 1)-1
    agg_closed    = (agg_closeTime == aggTrade_raw[ATINDEX_CLOSETIME] and aggTrade_raw[ATINDEX_CLOSED])

    #[4]: Build Aggregated AggTrade Tuple
    aggTrade_agg = (aggOpenTS, agg_closeTime, agg_quantityBuy, agg_quantitySell,
                    agg_nTradesBuy, agg_nTradesSell, agg_notionalBuy, agg_notionalSell,
                    agg_closed, agg_source)

    #[5]: Save New Aggregation
    dataAgg[aggOpenTS] = aggTrade_agg
    if aggTrade_raw[ATINDEX_CLOSED]:
        lastClosedAggs[aggOpenTS] = aggTrade_agg
#Aggregation END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#Analysis -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def analysisGenerator_SMA(intervalID, precisions, timestamp, klines, nSamples, analysisResults, **_):
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

def analysisGenerator_WMA(intervalID, precisions, timestamp, klines, nSamples, analysisResults, **_):
    #[1]: Instances
    wmas       = analysisResults
    pPrecision = precisions['price']
    func_gnitt = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl  = auxiliaries.getTimestampList_byNTicks

    #[2]: Previous Analysis & Analysis Count
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    wma_prev       = wmas.get(timestamp_prev, None)

    #[3]: WMA computation
    if wma_prev is None or wma_prev['WMA'] is None or wma_prev['fullCompute']:
        prices = [klines[ts][KLINDEX_CLOSEPRICE] if ts in klines else None
                  for ts in func_gtsl(intervalID = intervalID,
                                      timestamp  = timestamp,
                                      nTicks     = nSamples,
                                      direction  = False)]
        if any(p is None for p in prices):
            if wma_prev is None:
                priceSum_simple   = None
                priceSum_weighted = None
                wma               = None
                fullCompute       = True
            else:
                priceSum_simple   = wma_prev['PRICESUM_SIMPLE']
                priceSum_weighted = wma_prev['PRICESUM_WEIGHTED']
                wma               = wma_prev['WMA']
                fullCompute       = True
        else:
            priceSum_simple   = sum(prices)
            priceSum_weighted = sum(p*(nSamples-pIdx) for pIdx, p in enumerate(prices))
            wma               = round(priceSum_weighted / (nSamples*(nSamples+1)/2), pPrecision)
            fullCompute       = False
    else:
        timestamp_exp          = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -nSamples)
        priceSum_prev          = wma_prev['PRICESUM_SIMPLE']
        priceSum_weighted_prev = wma_prev['PRICESUM_WEIGHTED']
        price_exp  = klines[timestamp_exp][KLINDEX_CLOSEPRICE]
        price_this = klines[timestamp][KLINDEX_CLOSEPRICE]
        if price_exp is None or price_this is None:
            priceSum_simple   = None
            priceSum_weighted = None
            wma               = wma_prev['WMA']
            fullCompute       = True
        else:
            priceSum_simple   = priceSum_prev          - price_exp     + price_this
            priceSum_weighted = priceSum_weighted_prev - priceSum_prev + (nSamples*price_this)
            wma               = round(priceSum_weighted / (nSamples*(nSamples+1)/2), pPrecision)
            fullCompute       = False

    #[4]: Result formatting & Saving
    wmaResult = {'PRICESUM_SIMPLE':   priceSum_simple,
                 'PRICESUM_WEIGHTED': priceSum_weighted,
                 'WMA':               wma,
                 'fullCompute':       fullCompute}
    wmas[timestamp] = wmaResult

    #[5]: Memory Optimization References
    return (2,        #nAnalysisToKeep
            nSamples) #nKlinesToKeep

def analysisGenerator_EMA(intervalID, precisions, timestamp, klines, nSamples, analysisResults, **_):
    #[1]: Instances
    emas       = analysisResults
    kValue     = 2/(nSamples+1)
    pPrecision = precisions['price']
    func_gnitt = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl  = auxiliaries.getTimestampList_byNTicks

    #[2]: Previous Analysis & Analysis Count
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    ema_prev       = emas.get(timestamp_prev, None)

    #[3]: EMA computation
    if ema_prev is None or ema_prev['EMA'] is None or ema_prev['fullCompute']:
        prices = [klines[ts][KLINDEX_CLOSEPRICE] if ts in klines else None
                  for ts in func_gtsl(intervalID = intervalID,
                                      timestamp  = timestamp,
                                      nTicks     = nSamples,
                                      direction  = False)]
        if any(p is None for p in prices):
            if ema_prev is None:
                ema         = None
                fullCompute = True
            else:
                ema         = ema_prev['EMA']
                fullCompute = True
        else:
            priceSum    = sum(prices)
            ema         = round(priceSum / nSamples, pPrecision)
            fullCompute = False
    else:
        emaVal_prev = ema_prev['EMA']
        price_this  = klines[timestamp][KLINDEX_CLOSEPRICE]
        if price_this is None:
            ema         = emaVal_prev
            fullCompute = False
        else:
            ema         = round((price_this*kValue) + (emaVal_prev*(1-kValue)), pPrecision)
            fullCompute = False

    #[4]: Result formatting & Saving
    emaResult = {'EMA':         ema,
                 'fullCompute': fullCompute}
    emas[timestamp] = emaResult

    #[5]: Memory Optimization References
    return (2,        #nAnalysisToKeep
            nSamples) #nKlinesToKeep

def analysisGenerator_PSAR(intervalID, precisions, timestamp, klines, start, acceleration, maximum, analysisResults, **_):
    #[1]: Instances
    psars      = analysisResults
    pPrecision = precisions['price']
    func_gnitt = auxiliaries.getNextIntervalTickTimestamp

    #[2]: Previous Analysis & Analysis Count
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    psar_prev      = psars.get(timestamp_prev, None)
    mode           = 0 if psar_prev is None else psar_prev['mode']

    #[3]: PSAR computation
    if mode == 0:
        kline_prev = klines.get(timestamp_prev, None)
        kline_this = klines.get(timestamp,      None)
        if any(kl is None or kl[KLINDEX_LOWPRICE] is None or kl[KLINDEX_HIGHPRICE] is None for kl in (kline_prev, kline_this)):
            if psar_prev is None:
                pd          = None
                pd_reversed = False
                af          = None
                ep          = None
                psar        = None
                dcc         = 0
                mode        = 0
            else:
                pd          = None
                pd_reversed = False
                af          = None
                ep          = None
                psar        = psar_prev['PSAR']
                dcc         = psar_prev['DCC']+1
                mode        = 0
        else:
            p_high_delta = kline_this[KLINDEX_HIGHPRICE]-kline_prev[KLINDEX_HIGHPRICE] if kline_prev[KLINDEX_HIGHPRICE] <= kline_this[KLINDEX_HIGHPRICE] else 0
            p_low_delta  = kline_prev[KLINDEX_LOWPRICE] -kline_this[KLINDEX_LOWPRICE]  if kline_this[KLINDEX_LOWPRICE]  <= kline_prev[KLINDEX_LOWPRICE]  else 0
            pd          = (p_low_delta <= p_high_delta)
            pd_reversed = False
            af          = None
            ep          = None
            psar        = None if psar_prev is None else psar_prev['PSAR']
            dcc         = 0
            mode        = 1
    else:
        timestamp_prev2 = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -2)
        kline_prev2 = klines[timestamp_prev2]
        kline_prev1 = klines[timestamp_prev]
        kline_this  = klines[timestamp]
        if any(kl[KLINDEX_LOWPRICE] is None or kl[KLINDEX_HIGHPRICE] is None for kl in (kline_prev2, kline_prev1, kline_this)):
            pd          = None
            pd_reversed = False
            af          = None
            ep          = None
            psar        = psar_prev['PSAR']
            dcc         = psar_prev['DCC']+1
            mode        = 0
        else:
            if mode == 1:
                pd          = psar_prev['PD']
                pd_reversed = False
                af          = start
                if psar_prev['PD']: 
                    ep   = max(kline_prev1[KLINDEX_HIGHPRICE], kline_prev2[KLINDEX_HIGHPRICE])
                    psar = min(kline_prev1[KLINDEX_LOWPRICE],  kline_prev2[KLINDEX_LOWPRICE])
                else:
                    ep   = min(kline_prev1[KLINDEX_LOWPRICE],  kline_prev2[KLINDEX_LOWPRICE])
                    psar = max(kline_prev1[KLINDEX_HIGHPRICE], kline_prev2[KLINDEX_HIGHPRICE])
                dcc         = 0
                mode        = 2
            elif mode == 2:
                psar = round(psar_prev['PSAR'] + psar_prev['AF']*(psar_prev['EP']-psar_prev['PSAR']), pPrecision)
                if psar_prev['PD']:
                    #Limit Check
                    psar = min(psar, kline_prev1[KLINDEX_LOWPRICE], kline_prev2[KLINDEX_LOWPRICE])
                    #Reverse Detect
                    pd_reversed = (kline_this[KLINDEX_LOWPRICE] < psar)
                    #AF Update
                    if psar_prev['EP'] < kline_this[KLINDEX_HIGHPRICE]:
                        ep = kline_this[KLINDEX_HIGHPRICE]
                        af = psar_prev['AF'] + acceleration
                        if maximum < af: af = maximum
                    else: 
                        ep = psar_prev['EP']
                        af = psar_prev['AF']
                else:
                    #Limit Check
                    psar = max(psar, kline_prev1[KLINDEX_HIGHPRICE], kline_prev2[KLINDEX_HIGHPRICE])
                    #Reverse Detect
                    pd_reversed = (psar < kline_this[KLINDEX_HIGHPRICE])
                    #AF Update
                    if kline_this[KLINDEX_LOWPRICE] < psar_prev['EP']:
                        ep = kline_this[KLINDEX_LOWPRICE]
                        af = psar_prev['AF'] + acceleration
                        if maximum < af: af = maximum
                    else: 
                        ep = psar_prev['EP']
                        af = psar_prev['AF']
                #PD Reversal Handling
                if pd_reversed:
                    pd    = not(psar_prev['PD'])
                    af    = start
                    ep    = kline_this[KLINDEX_HIGHPRICE] if pd else kline_this[KLINDEX_LOWPRICE]
                    dcc   = 0
                    psar  = psar_prev['EP']
                else: 
                    pd  = psar_prev['PD']
                    dcc = psar_prev['DCC']+1
                    psar = psar
                mode = 2

    #[4]: Result formatting & Saving
    psarResult = {'PD':          pd,          # Progression Direction (True: Incremental, False: Decremental)
                  'PDReversed':  pd_reversed, # Progression Direction Reversal
                  'AF':          af,          # Acceleration Factor
                  'EP':          ep,          # Extreme Point
                  'PSAR':        psar,        # PSAR Value
                  'DCC':         dcc,         # Direction Continuity Counter
                  'mode':        mode         # Computation Mode (0, 1, 2)
                  }
    psars[timestamp] = psarResult

    #[5]: Memory Optimization References
    return (2, #nAnalysisToKeep
            3) #nKlinesToKeep

def analysisGenerator_BOL(intervalID, precisions, timestamp, klines, nSamples, MAType, bandWidth, analysisResults, **_):
    #[1]: Instances
    bols       = analysisResults
    pPrecision = precisions['price']
    func_gnitt = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl  = auxiliaries.getTimestampList_byNTicks

    #[2]: Previous Analysis & Analysis Count
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    bol_prev       = bols.get(timestamp_prev, None)
    mode           = 0 if bol_prev is None else bol_prev['mode']

    #[3]: BOL computation
    prices = [klines[ts][KLINDEX_CLOSEPRICE] if ts in klines else None
              for ts in func_gtsl(intervalID = intervalID,
                                  timestamp  = timestamp,
                                  nTicks     = nSamples,
                                  direction  = False)]

    #---[3-1]: MA
    #------[3-1-1]: SMA
    if MAType == 'SMA':
        if mode == 0:
            if any(p is None for p in prices):
                if bol_prev is None:
                    maComputation = None
                    ma            = None
                    mode          = 0
                else:
                    maComputation = bol_prev['MACOMPUTATION']
                    ma            = bol_prev['MA']
                    mode          = 0
            else:
                maComputation = sum(prices)
                ma            = round(maComputation / nSamples, pPrecision)
                mode          = 1
        else:
            timestamp_exp      = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -nSamples)
            maComputation_prev = bol_prev['MACOMPUTATION']
            price_exp  = klines[timestamp_exp][KLINDEX_CLOSEPRICE]
            price_this = klines[timestamp][KLINDEX_CLOSEPRICE]
            if price_exp is None or price_this is None:
                maComputation = None
                ma            = bol_prev['MA']
                mode          = 0
            else:
                maComputation = maComputation_prev - price_exp + price_this
                ma            = round(maComputation / nSamples, pPrecision)
                mode          = 1

    #------[3-1-2]: WMA
    elif MAType == 'WMA':
        if mode == 0:
            if any(p is None for p in prices):
                if bol_prev is None:
                    maComputation = (None, None)
                    ma            = None
                    mode          = 0
                else:
                    maComputation = bol_prev['MACOMPUTATION']
                    ma            = bol_prev['MA']
                    mode          = 0
            else:
                priceSum_simple   = sum(prices)
                priceSum_weighted = sum(p*(nSamples-pIdx) for pIdx, p in enumerate(prices))
                maComputation     = (priceSum_simple, priceSum_weighted)
                ma                = round(priceSum_weighted / (nSamples*(nSamples+1)/2), pPrecision)
                mode              = 1
        else:
            timestamp_exp                         = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -nSamples)
            priceSum_prev, priceSum_weighted_prev = bol_prev['MACOMPUTATION']
            price_exp  = klines[timestamp_exp][KLINDEX_CLOSEPRICE]
            price_this = klines[timestamp][KLINDEX_CLOSEPRICE]
            if price_exp is None or price_this is None:
                maComputation = (None, None)
                ma            = bol_prev['MA']
                mode          = 0
            else:
                priceSum_simple   = priceSum_prev          - price_exp     + price_this
                priceSum_weighted = priceSum_weighted_prev - priceSum_prev + (nSamples*price_this)
                maComputation     = (priceSum_simple, priceSum_weighted)
                ma                = round(priceSum_weighted / (nSamples*(nSamples+1)/2), pPrecision)
                mode              = 1

    #------[3-1-3]: EMA
    elif MAType == 'EMA':
        if mode == 0:
            if any(p is None for p in prices):
                if bol_prev is None:
                    ma   = None
                    mode = 0
                else:
                    ma   = bol_prev['MA']
                    mode = 0
            else:
                priceSum = sum(prices)
                ma       = round(priceSum / nSamples, pPrecision)
                mode     = 1
        else:
            emaVal_prev = bol_prev['MA']
            price_this  = klines[timestamp][KLINDEX_CLOSEPRICE]
            if price_this is None:
                ma   = emaVal_prev
                mode = 0
            else:
                kValue = 2/(nSamples+1)
                ma     = round((price_this*kValue) + (emaVal_prev*(1-kValue)), pPrecision)
                mode   = 1
        maComputation = None

    #---[3-2]: BOL
    if mode == 0:
        bol = None if bol_prev is None else bol_prev['BOL']
    elif mode == 1:
        dsSum = sum(math.pow(p-ma, 2) for p in prices)
        sd    = math.sqrt(dsSum/nSamples)
        bol    = (round(ma-sd*bandWidth, pPrecision), 
                  round(ma+sd*bandWidth, pPrecision))

    #[4]: Result formatting & Saving
    bolResult = {'MACOMPUTATION': maComputation,
                 'MA':            ma,
                 'BOL':           bol,
                 'mode':          mode}
    bols[timestamp] = bolResult

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

def analysisGenerator_IVP(intervalID, precisions, timestamp, klines, nSamples, gammaFactor, deltaFactor, analysisResults, **_):
    #[1]: Parameters
    ivps       = analysisResults
    pPrecision = precisions['price']
    baseUnit   = pow(10, -pPrecision)
    func_gnitt = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl  = auxiliaries.getTimestampList_byNTicks

    #[2]: Analysis counter
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    ivp_prev       = ivps.get(timestamp_prev, None)
    analysisCount  = 0 if ivp_prev is None else ivp_prev['analysisCount']+1

    #[3]: Klines
    kl_this    = klines[timestamp]
    kl_this_hp = kl_this[KLINDEX_HIGHPRICE]
    kl_this_cp = kl_this[KLINDEX_CLOSEPRICE]
    if ivp_prev is None:
        lastClosePrice = kl_this_cp
        priceMax       = kl_this_hp
    else:
        lastClosePrice = ivp_prev['lastClosePrice']
        priceMax       = ivp_prev['priceMax']
        if kl_this_cp is not None:
            lastClosePrice = kl_this_cp
        if kl_this_hp is not None and (priceMax is None or priceMax < kl_this_hp):
            priceMax = kl_this_hp

    #[4]: Division Height & Volume Price Level Profiles Preparation
    #---[4-1]: Not Enough Samples
    if analysisCount < nSamples-1 or priceMax is None or lastClosePrice is None:
        betaFactor  = None
        divHeight   = None
        vplp        = None
    #---[4-2]: Enough Samples
    else:
        #[4-2-1]: Beta Factor
        betaFactor = round(lastClosePrice*gammaFactor, pPrecision)

        #[4-2-2]: Division Ceiling
        p_max     = priceMax
        p_max_OOM = math.floor(math.log(p_max, 10))
        p_max_MSD = int(p_max/pow(10, p_max_OOM))
        if p_max_MSD == 10: 
            p_max_MSD = 1
            p_max_OOM += 1
        dCeiling_MSD = (int(p_max_MSD/1)+1)*1
        dCeiling_OOM = p_max_OOM
        if dCeiling_MSD == 10: 
            dCeiling_MSD = 1
            dCeiling_OOM += 1
        dCeiling = dCeiling_MSD*pow(10, dCeiling_OOM)

        #[4-2-3]: Division Height
        divHeight_min = betaFactor/10
        divHeight_min_OOM = math.floor(math.log(divHeight_min, 10))
        divHeight_min_MSD = int(divHeight_min/pow(10, divHeight_min_OOM))
        if divHeight_min_MSD == 10: 
            divHeight_min_MSD = 1
            divHeight_min_OOM += 1
        divHeight_MSD = int(divHeight_min_MSD)
        divHeight_OOM = divHeight_min_OOM
        if divHeight_MSD == 0: 
            divHeight_MSD = 1
        _divHeight = divHeight_MSD*pow(10, divHeight_OOM)
        nBaseUnitsWithinDivHeight = int(_divHeight/baseUnit)
        if nBaseUnitsWithinDivHeight == 0: divHeight = round(baseUnit,                           pPrecision)
        else:                              divHeight = round(baseUnit*nBaseUnitsWithinDivHeight, pPrecision)

        #[4-2-4]: Number Of Divisions
        nDivisions = math.ceil(dCeiling/divHeight)

        #[4-2-5]: Price Level Profiles
        vplp_prev = ivp_prev['volumePriceLevelProfile']
        if vplp_prev is None:
            vals = []
            for ts in func_gtsl(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False):
                kl = klines[ts]
                vb = kl[KLINDEX_VOLBASE]
                lp = kl[KLINDEX_LOWPRICE]
                hp = kl[KLINDEX_HIGHPRICE]
                if vb is None or lp is None or hp is None:
                    vals = None
                    break
                vals.append((vb, lp, hp))
            if vals:
                vplp = numpy.zeros(nDivisions)
                for vb, lp, hp in vals:
                    __IVP_addPriceLevelProfile(priceLevelProfileWeight        = vb, 
                                               priceLevelProfilePosition_low  = lp, 
                                               priceLevelProfilePosition_high = hp, 
                                               priceLevelProfile              = vplp, 
                                               divisionHeight                 = divHeight, 
                                               pricePrecision                 = pPrecision)
            else:
                vplp = None
        else:
            nDivs_prev     = len(vplp_prev)
            divHeight_prev = ivp_prev['divisionHeight']
            if divHeight_prev == divHeight and nDivs_prev == nDivisions: 
                vplp = numpy.copy(vplp_prev)
            else:
                vplp = numpy.zeros(nDivisions)
                for dIdx_prev in range (nDivs_prev):
                    divPos_low_prev  = round(divHeight_prev*dIdx_prev,     pPrecision)
                    divPos_high_prev = round(divHeight_prev*(dIdx_prev+1), pPrecision)
                    __IVP_addPriceLevelProfile(priceLevelProfileWeight        = vplp_prev[dIdx_prev], 
                                               priceLevelProfilePosition_low  = divPos_low_prev, 
                                               priceLevelProfilePosition_high = divPos_high_prev, 
                                               priceLevelProfile              = vplp, 
                                               divisionHeight                 = divHeight,
                                               pricePrecision                 = pPrecision)

    #[5]: Volume Price Level Profile Update
    if vplp is not None and ivp_prev['volumePriceLevelProfile'] is not None:
        #[5-1]: This Kline
        vb = kl_this[KLINDEX_VOLBASE]
        lp = kl_this[KLINDEX_LOWPRICE]
        hp = kl_this[KLINDEX_HIGHPRICE]
        if vb is not None and lp is not None and hp is not None:
            __IVP_addPriceLevelProfile(priceLevelProfileWeight        = vb, 
                                       priceLevelProfilePosition_low  = lp, 
                                       priceLevelProfilePosition_high = hp, 
                                       priceLevelProfile              = vplp, 
                                       divisionHeight                 = divHeight,
                                       pricePrecision                 = pPrecision)
        #[5-2]: Expired Kline
        kl_expired = klines[func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -nSamples)]
        vb = kl_expired[KLINDEX_VOLBASE]
        lp = kl_expired[KLINDEX_LOWPRICE]
        hp = kl_expired[KLINDEX_HIGHPRICE]
        if vb is not None and lp is not None and hp is not None:
            __IVP_addPriceLevelProfile(priceLevelProfileWeight        = vb, 
                                       priceLevelProfilePosition_low  = lp, 
                                       priceLevelProfilePosition_high = hp, 
                                       priceLevelProfile              = vplp, 
                                       divisionHeight                 = divHeight,
                                       pricePrecision                 = pPrecision,
                                       mode                           = False)
        
    #[6]: Volume Price Level Profile Boundaries
    #---[6-1]: Not Yet Compuatable
    if vplp is None:
        vplp_Filtered     = None
        vplp_Filtered_Max = None
        vplp_Boundaries   = None
    #---[6-1]: Boundaries Search
    else:
        #[6-1-1]: Filtering & Boundaries Search
        vplp_Filtered     = scipy.ndimage.gaussian_filter1d(input = vplp, 
                                                            sigma = round(len(vplp)/(3.3*1000)*deltaFactor, 10))
        vplp_Filtered_Max = numpy.max(vplp_Filtered)
        vplp_Boundaries   = []
        #[6-1-2]: Extremas Search
        direction_prev = None
        volHeight_prev = None
        for plIndex, volHeight in enumerate(vplp_Filtered):
            #[6-1-2-1]: Initial
            if direction_prev is None:
                direction_prev = True
                volHeight_prev = volHeight
                continue
            #[6-1-2-2]: Local Maximum
            if direction_prev and (volHeight < volHeight_prev): 
                direction_prev = False
                vplp_Boundaries.append(plIndex-1)
            #[6-1-2-3]: Local Minimum
            elif not direction_prev and (volHeight_prev < volHeight): 
                direction_prev = True
                vplp_Boundaries.append(plIndex-1) 
            volHeight_prev = volHeight

    #[7]: Near VPLP Boundaries
    if vplp_Boundaries is None:
        vplp_nearBoundaries = [None]*10
    else:
        vplp_nearBoundaries_down = [None]*5
        vplp_nearBoundaries_up   = [None]*5

        #Find the nearest above boundary index
        dIndex_closePrice  = lastClosePrice//divHeight
        bIndex_nearestAbove = None
        for bIndex, dIndex in enumerate(vplp_Boundaries):
            if dIndex_closePrice <= dIndex: 
                bIndex_nearestAbove = bIndex
                break

        #Convert nearest down and up boundaries into price center values
        if bIndex_nearestAbove is None:
            idx_up_beg   = len(vplp_Boundaries)
            idx_down_beg = len(vplp_Boundaries)-5
        else:
            idx_up_beg   = bIndex_nearestAbove
            idx_down_beg = bIndex_nearestAbove-5
        for i in range (5):
            idx_down_target = idx_down_beg+i
            idx_up_target   = idx_up_beg  +i
            if 0 <= idx_down_target < len(vplp_Boundaries):
                dIndex = vplp_Boundaries[idx_down_target]
                vplp_nearBoundaries_down[i] = round((dIndex+0.5)*divHeight, pPrecision)
            if 0 <= idx_up_target < len(vplp_Boundaries):
                dIndex = vplp_Boundaries[idx_up_target]
                vplp_nearBoundaries_up[i] = round((dIndex+0.5)*divHeight, pPrecision)

        #Finally
        vplp_nearBoundaries = tuple(vplp_nearBoundaries_down+vplp_nearBoundaries_up)

    #[8]: Result Formatting & Saving
    ivpResult = {'lastClosePrice':                         lastClosePrice,
                 'priceMax':                               priceMax,
                 'gammaFactor':                            gammaFactor, 
                 'betaFactor':                             betaFactor,
                 'divisionHeight':                         divHeight, 
                 'volumePriceLevelProfile':                vplp,
                 'volumePriceLevelProfile_Filtered':       vplp_Filtered, 
                 'volumePriceLevelProfile_Filtered_Max':   vplp_Filtered_Max, 
                 'volumePriceLevelProfile_Boundaries':     vplp_Boundaries,
                 'volumePriceLevelProfile_NearBoundaries': vplp_nearBoundaries,
                 'analysisCount':                          analysisCount}
    ivps[timestamp] = ivpResult

    #[9]: Memory Optimization References
    return (2,          #nAnalysisToKeep
            nSamples+1) #nKlinesToKeep

def analysisGenerator_SWING(intervalID, timestamp, klines, swingRange, analysisResults, **_):
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
                if swingSearch['min']*(1+swingRange) < kl_hp:
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
                if kl_lp < swingSearch['max']*(1-swingRange):
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

def analysisGenerator_VOL(intervalID, precisions, timestamp, klines, nSamples, MAType, analysisResults, **_):
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

def analysisGenerator_NNA(intervalID, timestamp, klines, neuralNetworks, nnCode, alpha, beta, analysisResults, **_):
    #[1]: Instances
    nnas       = analysisResults
    func_gnitt = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl  = auxiliaries.getTimestampList_byNTicks

    #[2]: Analysis counter
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    nna_prev       = nnas.get(timestamp_prev, None)
    analysisCount  = 0 if nna_prev is None else nna_prev['analysisCount']+1
    
    #[3]: NNA
    nn  = neuralNetworks.get(nnCode, None)
    nna = None
    if nn is not None:
        nSamples = nn.getNKlines()
        if analysisCount < nSamples-1:
            nna = None
        else:
            kl0 = klines.get(func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -(nSamples-1)), None)
            #[2-1]: Invalid Input
            if (kl0 is None or 
                kl0[KLINDEX_OPENPRICE]       is None or
                kl0[KLINDEX_HIGHPRICE]       is None or
                kl0[KLINDEX_LOWPRICE]        is None or
                kl0[KLINDEX_CLOSEPRICE]      is None or
                kl0[KLINDEX_VOLBASE]         is None or
                kl0[KLINDEX_VOLBASETAKERBUY] is None
                ): 
                nna = 0
            #[2-2]: Valid Input
            else:
                #[2-2-1]: Input Tensor Construction
                values_raw = []
                cp_last    = None
                p_max      = None
                p_min      = None
                vol_max    = None
                volTB_max  = None
                for ts in reversed(func_gtsl(intervalID = intervalID, timestamp = timestamp, nTicks = nSamples, direction = False)):
                    kl = klines.get(ts, None)
                    if kl is None:
                        op   = cp_last
                        hp   = cp_last
                        lp   = cp_last
                        cp   = cp_last
                        vb   = 0
                        vbtb = 0
                    else:
                        op   = kl[KLINDEX_OPENPRICE]
                        hp   = kl[KLINDEX_HIGHPRICE]
                        lp   = kl[KLINDEX_LOWPRICE]
                        cp   = kl[KLINDEX_CLOSEPRICE]
                        vb   = kl[KLINDEX_VOLBASE]
                        vbtb = kl[KLINDEX_VOLBASETAKERBUY]
                    if cp is not None:
                        cp_last = cp
                    if op   is None: op   = cp_last
                    if hp   is None: hp   = cp_last
                    if lp   is None: lp   = cp_last
                    if cp   is None: cp   = cp_last
                    if vb   is None: vb   = 0
                    if vbtb is None: vbtb = 0
                    if p_max     is None or p_max     < hp:    p_max     = hp
                    if p_min     is None or lp        < p_min: p_min     = lp
                    if vol_max   is None or vol_max   < vb:    vol_max   = vb
                    if volTB_max is None or volTB_max < vbtb:  volTB_max = vbtb
                    values_raw.append((op, hp, lp, cp, vb, vbtb))
                p_range = p_max-p_min
                iTensor_2d = torch.tensor(data = values_raw, dtype = torch.float32, device = 'cpu', requires_grad = False)
                if p_range != 0.0:   iTensor_2d[:, 0:4] = (iTensor_2d[:, 0:4] - p_min) / p_range
                else:                iTensor_2d[:, 0:4] = 0.5
                if vol_max != 0.0:   iTensor_2d[:, 4]   /= vol_max
                else:                iTensor_2d[:, 4]   = 0.0
                if volTB_max != 0.0: iTensor_2d[:, 5]   /= volTB_max
                else:                iTensor_2d[:, 5]   = 0.0
                iTensor_flat = iTensor_2d.flatten()

                #[2-2-2]: Forwarding
                nn_out = float(nn.forward(inputData = iTensor_flat)[0])*2-1
                nna    = abs(round(math.atan(pow(nn_out/alpha, beta))*2/math.pi, 5))
                if 0 <= nn_out: nna =  nna
                else:           nna = -nna

    #[4]: Result formatting & saving
    nnaResult = {'NNA':           nna,
                 'analysisCount': analysisCount}
    nnas[timestamp] = nnaResult

    #[5]: Memory Optimization References
    #---nAnalysisToKeep, nKlinesToKeep
    if nn is None: return (2, 2)
    else:          return (nSamples, nSamples)

def analysisGenerator_MMACD(intervalID, precisions, timestamp, klines, signal_nSamples, activatedMAs, activatedMAPairs, maxMANSamples, analysisResults, **_):
    #[1]: Instances
    mmacds            = analysisResults
    kline             = klines[timestamp]
    signal_kValue     = 2/(signal_nSamples+1)
    absoluteMA_kValue = 2/(maxMANSamples+1)
    pPrecision        = precisions['price']
    func_gnitt        = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl         = auxiliaries.getTimestampList_byNTicks

    #[2]: Analysis counter
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    mmacd_prev     = mmacds.get(timestamp_prev, None)
    analysisCount  = 0 if mmacd_prev is None else mmacd_prev['analysisCount']+1

    #[3]: MMACD Computation
    #---[3-1]: MAs Generation
    mas_prev = None if mmacd_prev is None else mmacd_prev['MAs']
    mas      = {}
    for ma_nSamples in activatedMAs:
        #[3-1-1]: Mode & K-Value
        ma_mode   = 0 if mas_prev is None else mas_prev[ma_nSamples]['mode']
        ma_kValue = 2/(ma_nSamples+1)

        #[3-1-2]: Computation
        if ma_mode == 0:
            prices = [klines[ts][KLINDEX_CLOSEPRICE] if ts in klines else None
                      for ts in func_gtsl(intervalID = intervalID,
                                          timestamp  = timestamp,
                                          nTicks     = ma_nSamples,
                                          direction  = False)]
            if any(p is None for p in prices):
                if mas_prev is None:
                    ma_ma   = None
                    ma_mode = 0
                else:
                    ma_ma   = mas_prev[ma_nSamples]['MA']
                    ma_mode = 0
            else:
                priceSum = sum(prices)
                ma_ma    = round(priceSum / ma_nSamples, pPrecision)
                ma_mode  = 1
        elif ma_mode == 1:
            ma_ma_prev = mas_prev[ma_nSamples]['MA']
            price_this = kline[KLINDEX_CLOSEPRICE]
            if price_this is None:
                ma_ma   = ma_ma_prev
                ma_mode = 1
            else:
                ma_ma   = round((price_this*ma_kValue) + (ma_ma_prev*(1-ma_kValue)), pPrecision)
                ma_mode = 1
        mas[ma_nSamples] = {'MA':   ma_ma,
                            'mode': ma_mode}

    #---[3-2]: MA Pair Delta Sum & MMACD
    if analysisCount < (maxMANSamples-1): 
        mmacd = None
    else:
        if any(mas[ma0]['MA'] is None or mas[ma1]['MA'] is None for ma0, ma1 in activatedMAPairs):
            mmacd = None
        else:
            mmacd = sum(mas[ma0]['MA']-mas[ma1]['MA'] for ma0, ma1 in activatedMAPairs)

    #---[3-3]: Signal
    if analysisCount < (maxMANSamples+signal_nSamples-1): 
        signal = None
    else:
        signal_prev = mmacd_prev['SIGNAL']
        if signal_prev is None:
            signal = mmacd
        else:
            signal = (mmacd*signal_kValue) + (signal_prev*(1-signal_kValue))

    #---[3-4]: MSDelta
    if signal is None:
        msDelta = None
    else:
        msDelta = mmacd-signal

    #---[3-5]: MSDelta Absolute MA
    if msDelta is None: 
        msDelta_AbsMA = None
    else:
        msDelta_prev = mmacd_prev['MSDELTA']
        if msDelta_prev is None: 
            msDelta_AbsMA = None
        else:
            msDelta_AbsMA_prev = mmacd_prev['MSDELTA_ABSMA']
            if msDelta_AbsMA_prev is None: msDelta_AbsMA = abs(msDelta)*absoluteMA_kValue + abs(msDelta_prev) *(1-absoluteMA_kValue)
            else:                          msDelta_AbsMA = abs(msDelta)*absoluteMA_kValue + msDelta_AbsMA_prev*(1-absoluteMA_kValue)

    #---[3-6]: MSDelta Absolute MA Relative
    if   msDelta_AbsMA is None: msDelta_AbsMARel = None
    elif msDelta_AbsMA == 0:    msDelta_AbsMARel = 0.0
    else:                       msDelta_AbsMARel = round(msDelta/msDelta_AbsMA, 5)

    #[4]: Result Formatting & Saving
    mmacdResult = {'MAs':              mas, 
                   'MMACD':            mmacd, 
                   'SIGNAL':           signal, 
                   'MSDELTA':          msDelta, 
                   'MSDELTA_ABSMA':    msDelta_AbsMA, 
                   'MSDELTA_ABSMAREL': msDelta_AbsMARel,
                   'analysisCount': analysisCount}
    mmacds[timestamp] = mmacdResult

    #[5]: Memory Optimization References
    return (signal_nSamples+1, #nAnalysisToKeep
            maxMANSamples)     #nKlinesToKeep
    
def analysisGenerator_DMIxADX(intervalID, timestamp, klines, nSamples, analysisResults, **_):
    #[1]: Instances
    dmixadxs          = analysisResults
    absoluteMA_kValue = 2/(nSamples*10+1)
    func_gnitt        = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl         = auxiliaries.getTimestampList_byNTicks

    #[2]: Analysis counter
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    dmixadx_prev   = dmixadxs.get(timestamp_prev, None)
    analysisCount  = 0 if dmixadx_prev is None else dmixadx_prev['analysisCount']+1

    #[3]: DMIxADX computation
    #---[3-1]: DM+, DM-, TR
    if analysisCount == 0:
        dmPlus  = None
        dmMinus = None
        tr      = None
    else:
        kline_this = klines[timestamp]
        kline_prev = klines[timestamp_prev]
        hp_prev = kline_prev[KLINDEX_HIGHPRICE]
        lp_prev = kline_prev[KLINDEX_LOWPRICE]
        cp_prev = kline_prev[KLINDEX_CLOSEPRICE]
        hp_this = kline_this[KLINDEX_HIGHPRICE]
        lp_this = kline_this[KLINDEX_LOWPRICE]
        if any(v is None for v in (hp_prev, lp_prev, cp_prev, hp_this, lp_this)):
            dmPlus  = None
            dmMinus = None
            tr      = None
        else:
            move_up   = hp_this-hp_prev
            move_down = lp_prev-lp_this
            if move_down < move_up and 0 < move_up:
                dmPlus  = move_up
                dmMinus = 0.0
            elif move_up < move_down and 0 < move_down:
                dmPlus  = 0.0
                dmMinus = move_down
            else:
                dmPlus  = 0.0
                dmMinus = 0.0
            tr = max(hp_this-lp_this, abs(hp_this-cp_prev), abs(lp_this-cp_prev))
        
    #---[3-2]: DM+Sum, DM-Sum, TRSum
    if analysisCount < nSamples:
        dmPlusSum  = None
        dmMinusSum = None
        trSum      = None
    elif nSamples == analysisCount:
        tsList = func_gtsl(intervalID = intervalID, 
                           timestamp  = timestamp, 
                           nTicks     = nSamples, 
                           direction  = False)
        dmPlusSum  = 0
        dmMinusSum = 0
        trSum      = 0
        for ts in tsList:
            if ts == timestamp:
                dmPlus_ts    = dmPlus
                dmMinus_ts   = dmMinus
                tr_ts        = tr
            else:
                dmixadx_this = dmixadxs[ts]
                dmPlus_ts    = dmixadx_this['DM+']
                dmMinus_ts   = dmixadx_this['DM-']
                tr_ts        = dmixadx_this['TR']
            if tr_ts is not None:
                dmPlusSum  += dmPlus_ts
                dmMinusSum += dmMinus_ts
                trSum      += tr_ts
    elif nSamples < analysisCount:
        dmPlusSum_prev  = dmixadx_prev['DM+Sum']
        dmMinusSum_prev = dmixadx_prev['DM-Sum']
        trSum_prev      = dmixadx_prev['TRSum']
        dmPlusSum  = dmPlusSum_prev  - (dmPlusSum_prev  / nSamples)
        dmMinusSum = dmMinusSum_prev - (dmMinusSum_prev / nSamples)
        trSum      = trSum_prev      - (trSum_prev      / nSamples)
        if tr is not None:
            dmPlusSum  += dmPlus
            dmMinusSum += dmMinus
            trSum      += tr

    #---[3-3]: DI+, DI-, DX
    if nSamples <= analysisCount:
        if trSum == 0:
            diPlus  = 0.0
            diMinus = 0.0
        else:
            diPlus  = dmPlusSum /trSum
            diMinus = dmMinusSum/trSum
        if diPlus+diMinus == 0: dx = 0.0
        else:                   dx = abs(diPlus-diMinus)/(diPlus+diMinus)
    else:
        diPlus  = None
        diMinus = None
        dx      = None

    #---[3-4]: ADX
    if analysisCount < nSamples*2-1:
        adx = None
    elif analysisCount == nSamples*2-1:
        dxs = [dmixadxs[ts]['DX'] for ts in func_gtsl(intervalID = intervalID, 
                                                      timestamp  = timestamp_prev, 
                                                      nTicks     = nSamples-1, 
                                                      direction  = False)]
        dxSum = dx + sum(dxs)
        adx = dxSum/nSamples
    else:
        adx = ((dmixadx_prev['ADX']*(nSamples-1))+dx)/nSamples

    #---[3-5]: DMIxADX
    if any(v is None for v in (diPlus, diMinus, adx)):
        dmixadx = None
    else:
        dmixadx = (diPlus-diMinus)*adx

    #---[3-6]: DMIxADX Absolute Moving Average
    if dmixadx is None: 
        dmixadx_absMA = None
    else:
        dmixadx_dmixadx_prev = dmixadx_prev['DMIxADX']
        if dmixadx_dmixadx_prev is None: 
            dmixadx_absMA = None
        else:
            dmixadx_absMA_prev = dmixadx_prev['DMIxADX_ABSMA']
            if dmixadx_absMA_prev is None: dmixadx_absMA = abs(dmixadx)*absoluteMA_kValue + abs(dmixadx_dmixadx_prev)*(1-absoluteMA_kValue)
            else:                          dmixadx_absMA = abs(dmixadx)*absoluteMA_kValue + dmixadx_absMA_prev       *(1-absoluteMA_kValue)

    #---[3-7]: DMIxADX Absolute Moving Average Relative
    if   dmixadx_absMA is None: dmixadx_absMARel = None
    elif dmixadx_absMA == 0:    dmixadx_absMARel = 0.0
    else:                       dmixadx_absMARel = round(dmixadx/dmixadx_absMA, 5)

    #[4]: Result Formatting & Saving
    dmixadxResult = {'DM+':              dmPlus, 
                     'DM-':              dmMinus, 
                     'TR':               tr, 
                     'DM+Sum':           dmPlusSum, 
                     'DM-Sum':           dmMinusSum, 
                     'TRSum':            trSum,
                     'DI+':              diPlus, 
                     'DI-':              diMinus,
                     'DX':               dx,
                     'ADX':              adx, 
                     'DMIxADX':          dmixadx, 
                     'DMIxADX_ABSMA':    dmixadx_absMA, 
                     'DMIxADX_ABSMAREL': dmixadx_absMARel,
                     'analysisCount':    analysisCount}
    dmixadxs[timestamp] = dmixadxResult

    #[5]: Memory Optimization References
    return (nSamples, #nAnalysisToKeep
            2)        #nKlinesToKeep
    
def analysisGenerator_MFI(intervalID, timestamp, klines, nSamples, analysisResults, **_):
    #[1]: Instances
    mfis              = analysisResults
    absoluteMA_kValue = 2/(nSamples*10+1)
    kline             = klines[timestamp]
    func_gnitt        = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl         = auxiliaries.getTimestampList_byNTicks

    #[2]: Analysis counter
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    mfi_prev       = mfis.get(timestamp_prev, None)
    analysisCount  = 0 if mfi_prev is None else mfi_prev['analysisCount']+1
    
    #[3]: MFI computation
    #---[3-1]: TP (Typical Price) & MF (Money Flow)
    if any(kline[daIdx] is None for daIdx in (KLINDEX_HIGHPRICE, KLINDEX_LOWPRICE, KLINDEX_CLOSEPRICE, KLINDEX_VOLBASE)):
        tp = None
        mf = None
    else:
        tp = (kline[KLINDEX_HIGHPRICE]+kline[KLINDEX_LOWPRICE]+kline[KLINDEX_CLOSEPRICE])/3
        mf = tp*kline[KLINDEX_VOLBASE]

    #---[3-2]: MFI
    #------[3-2-1]: nSamples Not Reached
    if analysisCount < nSamples: 
        mfi = None

    #------[3-2-2]: nSamples Reached
    else:
        #[3-2-2-1]: Directional Money Flow
        tsList = func_gtsl(intervalID = intervalID, 
                           timestamp  = timestamp, 
                           nTicks     = nSamples+1, 
                           direction  = False)
        mfPlusSum  = 0
        mfMinusSum = 0
        nValid     = 0
        for tsIndex in range (nSamples-1, -1, -1):
            if tsIndex == 0: 
                tp_current = tp
                mf_current = mf
            else:
                mfi_ts = mfis[tsList[tsIndex]]
                tp_current = mfi_ts['TP']
                mf_current = mfi_ts['MF']
            tp_prev = mfis[tsList[tsIndex+1]]['TP']
            if tp_current is not None and mf_current is not None and tp_prev is not None:
                tpDelta = tp_current-tp_prev
                if   tpDelta < 0: mfMinusSum += mf_current
                elif 0 < tpDelta: mfPlusSum  += mf_current
                nValid += 1

        #[3-2-2-2]: MFR (Money Flow Ratio)
        if   nValid == 0:       mfr = None
        elif mfMinusSum == 0.0: mfr = float('inf')
        else:                   mfr = mfPlusSum/mfMinusSum

        #[3-2-2-3]: MFI (Money Flow Index)
        if mfr is None: mfi = 0.5
        else:           mfi = 1.0-(1.0/(1.0+mfr))
        confidence = nValid/nSamples
        mfi        = 0.5+((mfi-0.5)*confidence)

    #---[3-3]: MFI Deviation Absolute MA
    if mfi is None: 
        mfi_devAbsMA = None
    else:
        mfi_mfi_prev = mfi_prev['MFI']
        if mfi_mfi_prev is None: 
            mfi_devAbsMA = None
        else:
            mfi_devAbsMA_prev = mfi_prev['MFI_DEVABSMA']
            if mfi_devAbsMA_prev is None: mfi_devAbsMA = abs(mfi-0.5)*absoluteMA_kValue + abs(mfi_mfi_prev-0.5)*(1-absoluteMA_kValue)
            else:                         mfi_devAbsMA = abs(mfi-0.5)*absoluteMA_kValue + mfi_devAbsMA_prev    *(1-absoluteMA_kValue)

    #---[3-4]: MFI Deviation Absolute MA Relative
    if   mfi_devAbsMA is None: mfi_devAbsMARel = None
    elif mfi_devAbsMA == 0:    mfi_devAbsMARel = 0.0
    else:                      mfi_devAbsMARel = round((mfi-0.5)/mfi_devAbsMA, 5)

    #[4]: Result Formatting & Saving
    mfiResult = {'TP':              tp, 
                 'MF':              mf, 
                 'MFI':             mfi, 
                 'MFI_DEVABSMA':    mfi_devAbsMA, 
                 'MFI_DEVABSMAREL': mfi_devAbsMARel,
                 'analysisCount':   analysisCount}
    mfis[timestamp] = mfiResult

    #[5]: Memory Optimization References
    return (nSamples+1, #nAnalysisToKeep
            1)          #nKlinesToKeep

def analysisGenerator_TPD(intervalID, timestamp, klines, viewLength, nSamples, nSamplesMA, analysisResults, **_):
    #[1]: Params & Instances
    tpds              = analysisResults
    kValueMA          = 2/(nSamplesMA+1)
    absoluteMA_kValue = 2/(nSamplesMA*10+1)
    kline             = klines[timestamp]
    func_gnitt        = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl         = auxiliaries.getTimestampList_byNTicks

    #[2]: Analysis counter
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    tpd_prev       = tpds.get(timestamp_prev, None)
    analysisCount  = 0 if tpd_prev is None else tpd_prev['analysisCount']+1

    #[3]: TPD Computation
    #---[3-1]: Last Termination
    lastTerm_TS = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -viewLength)
    cp_lastTerm = None if lastTerm_TS not in klines else klines[lastTerm_TS][KLINDEX_CLOSEPRICE]
    cp_this     = kline[KLINDEX_CLOSEPRICE]
    if cp_lastTerm is None or cp_this is None:
        lastTerm_pd = None
    else:
        lastTerm_pd = (cp_this / cp_lastTerm)-1

    #---[3-2]: Update Histogram Counts (Sliding Window O(1))
    if analysisCount == 0:
        count_dec = 0
        count_inc = 0
    else:
        count_dec = tpd_prev['COUNT_DECREMENTAL']
        count_inc = tpd_prev['COUNT_INCREMENTAL']
    #[3-2-1]: Add New Count
    if lastTerm_pd is not None:
        if   lastTerm_pd < 0: count_dec += 1
        elif 0 < lastTerm_pd: count_inc += 1
    #[3-2-2]: Remove Expired
    expired_TS = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -nSamples)
    expired_pd = None if expired_TS not in tpds else tpds[expired_TS]['LASTERM_PD']
    if expired_pd is not None:
        if   expired_pd < 0: count_dec -= 1
        elif 0 < expired_pd: count_inc -= 1

    #---[3-3]: Bias
    if analysisCount < viewLength+nSamples-1:
        bias = None
    else:
        cSum = count_inc+count_dec
        if cSum == 0:
            bias = 0
        else:
            bias = (count_inc-count_dec)/nSamples

    #---[3-4]: TPD
    if analysisCount < viewLength+nSamples+nSamplesMA-2:
        tpd = None
    elif analysisCount == viewLength+nSamples+nSamplesMA-2:
        biasSum = sum(tpds[ts]['BIAS'] for ts in func_gtsl(intervalID = intervalID, 
                                                           timestamp  = timestamp_prev, 
                                                           nTicks     = nSamplesMA-1,
                                                           direction  = False)) + bias
        tpd = round(biasSum / nSamplesMA, 5)
    else:
        tpd = round((bias*kValueMA) + (tpd_prev['TPD'] * (1-kValueMA)), 5)

    #---[3-5]: TPD Absolute Moving Average
    if tpd is None: 
        tpd_absMA = None
    else:
        tpd_tpd_prev = tpd_prev['TPD']
        if tpd_tpd_prev is None: 
            tpd_absMA = None
        else:
            tpd_absMA_prev = tpd_prev['TPD_ABSMA']
            if tpd_absMA_prev is None: tpd_absMA = abs(tpd)*absoluteMA_kValue + abs(tpd_tpd_prev)*(1-absoluteMA_kValue)
            else:                      tpd_absMA = abs(tpd)*absoluteMA_kValue + tpd_absMA_prev   *(1-absoluteMA_kValue)

    #---[3-6]: TPD Absolute Moving Average Relative
    if   tpd_absMA is None: tpd_absMARel = None
    elif tpd_absMA == 0:    tpd_absMARel = 0.0
    else:                   tpd_absMARel = round(tpd/tpd_absMA, 5)

    #[4]: Result Formatting & Saving
    tpdResult = {'LASTERM_PD':        lastTerm_pd,
                 'COUNT_INCREMENTAL': count_inc,
                 'COUNT_DECREMENTAL': count_dec,
                 'BIAS':              bias,
                 'TPD':               tpd,
                 'TPD_ABSMA':         tpd_absMA,
                 'TPD_ABSMAREL':      tpd_absMARel,
                 'analysisCount':     analysisCount}
    tpds[timestamp] = tpdResult

    #[5]: Memory Optimization References
    return (max(nSamples, nSamplesMA)+1, #nAnalysisToKeep
            viewLength+1)                #nKlinesToKeep

def analysisGenerator_WOI(intervalID, precisions, timestamp, depths, nSamples, analysisResults, **_):
    #[1]: Instances
    wois              = analysisResults
    kValue            = 2/(nSamples+1)
    absoluteMA_kValue = 2/(nSamples*10+1)
    qPrecision = precisions['quote']
    func_gnitt        = auxiliaries.getNextIntervalTickTimestamp
    func_gtsl         = auxiliaries.getTimestampList_byNTicks

    #[2]: Previous Analysis & Analysis Count
    timestamp_prev = func_gnitt(intervalID = intervalID, timestamp = timestamp, nTicks = -1)
    woi_prev       = wois.get(timestamp_prev, None)
    mode           = 0 if woi_prev is None else woi_prev['mode']

    #[3]: WOI computation
    #---[3-1]: Imbalance
    depth = depths[timestamp]
    if any(depth[vIdx] is None for vIdx in (DEPTHINDEX_BIDS5,
                                            DEPTHINDEX_BIDS4,
                                            DEPTHINDEX_BIDS3,
                                            DEPTHINDEX_BIDS2,
                                            DEPTHINDEX_BIDS1,
                                            DEPTHINDEX_BIDS0,
                                            DEPTHINDEX_ASKS0,
                                            DEPTHINDEX_ASKS1,
                                            DEPTHINDEX_ASKS2,
                                            DEPTHINDEX_ASKS3,
                                            DEPTHINDEX_ASKS4,
                                            DEPTHINDEX_ASKS5)):
        imbalance = None
    else:
        wBids_sum = sum(depth[vIdx]/abs((DEPTHBINS[vIdx][1]+DEPTHBINS[vIdx][0])/2) 
                        for vIdx in (DEPTHINDEX_BIDS5, DEPTHINDEX_BIDS4, DEPTHINDEX_BIDS3, DEPTHINDEX_BIDS2, DEPTHINDEX_BIDS1, DEPTHINDEX_BIDS0))
        wAsks_sum = sum(depth[vIdx]/abs((DEPTHBINS[vIdx][1]+DEPTHBINS[vIdx][0])/2) 
                        for vIdx in (DEPTHINDEX_ASKS5, DEPTHINDEX_ASKS4, DEPTHINDEX_ASKS3, DEPTHINDEX_ASKS2, DEPTHINDEX_ASKS1, DEPTHINDEX_ASKS0))
        imbalance = (wBids_sum-wAsks_sum)/(wAsks_sum+wBids_sum)

    #---[3-2]: WOI
    if mode == 0:
        imbalances = [imbalance,] + [wois[ts]['IMBALANCE'] if ts in wois else None
                                     for ts in func_gtsl(intervalID = intervalID,
                                                         timestamp  = timestamp_prev,
                                                         nTicks     = (nSamples-1),
                                                         direction  = False)]
        if any(val is None for val in imbalances):
            woi = None
        else:
            imbalances_sum = sum(imbalances)
            woi            = round(imbalances_sum / nSamples, qPrecision)
            mode           = 1
    elif mode == 1:
        if imbalance is None:
            woi = woi_prev['WOI']
        else:
            woi = round((imbalance*kValue) + (woi_prev['WOI']*(1-kValue)), qPrecision)

    #---[3-3]: WOI Absolute Moving Average
    if woi is None: 
        woi_absMA = None
    else:
        woi_woi_prev = woi_prev['WOI']
        if woi_woi_prev is None:
            woi_absMA = None
        else:
            woi_absMA_prev = woi_prev['WOI_ABSMA']
            if woi_absMA_prev is None: woi_absMA = abs(woi)*absoluteMA_kValue + abs(woi_woi_prev)*(1-absoluteMA_kValue)
            else:                      woi_absMA = abs(woi)*absoluteMA_kValue + woi_absMA_prev   *(1-absoluteMA_kValue)

    #---[3-4]: WOI Absolute Moving Average Relative
    if   woi_absMA is None: woi_absMARel = None
    elif woi_absMA == 0:    woi_absMARel = 0.0
    else:                   woi_absMARel = round(woi/woi_absMA, 5)

    #[4]: Result formatting & Saving
    woiResult = {'IMBALANCE':    imbalance,
                 'WOI':          woi,
                 'WOI_ABSMA':    woi_absMA,
                 'WOI_ABSMAREL': woi_absMARel,
                 'mode':         mode}
    wois[timestamp] = woiResult

    #[5]: Memory Optimization References
    return (nSamples, #nAnalysisToKeep
            nSamples) #nKlinesToKeep

def analysisGenerator_NES(intervalID, precisions, timestamp, aggTrades, nSamples, analysisResults, **_):
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

__analysisGenerators = {'SMA':     analysisGenerator_SMA,
                        'WMA':     analysisGenerator_WMA,
                        'EMA':     analysisGenerator_EMA,
                        'PSAR':    analysisGenerator_PSAR,
                        'BOL':     analysisGenerator_BOL,
                        'IVP':     analysisGenerator_IVP,
                        'SWING':   analysisGenerator_SWING,
                        'VOL':     analysisGenerator_VOL,
                        'NNA':     analysisGenerator_NNA,
                        'MMACD':   analysisGenerator_MMACD,
                        'DMIxADX': analysisGenerator_DMIxADX,
                        'MFI':     analysisGenerator_MFI,
                        'TPD':     analysisGenerator_TPD,
                        'WOI':     analysisGenerator_WOI,
                        'NES':     analysisGenerator_NES}
def analysisGenerator(analysisType, **params): 
    return __analysisGenerators[analysisType](**params)

def constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(currencyAnalysisConfiguration):
    cac = currencyAnalysisConfiguration
    cap = dict()
    invalidLines = defaultdict(list)
    if cac['SMA_Master']:
        for lineIndex in range (constants.NLINES_SMA):
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
        for lineIndex in range (constants.NLINES_WMA):
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
        for lineIndex in range (constants.NLINES_EMA):
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
        for lineIndex in range (constants.NLINES_PSAR):
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
        for lineIndex in range (constants.NLINES_BOL):
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
        for lineIndex in range (constants.NLINES_SWING):
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
        for lineIndex in range (constants.NLINES_VOL):
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
        for lineIndex in range (constants.NLINES_NNA):
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
                
    if cac['MMACD_Master']:
        analysisCode = 'MMACD'
        #[1]: Signal nSamples
        signal_nSamples = cac[f'{analysisCode}_SignalNSamples']
        if   type(signal_nSamples) is not int: invalidLines[analysisCode].append("signal_nSamples: Must be type 'int'")
        elif not 1 < signal_nSamples:          invalidLines[analysisCode].append("signal_nSamples: Must be greater than 1")
        #[2]: Activated MAs
        activatedMAs = []
        for lineIndex in range (constants.NLINES_MMACD):
            #[1]: Check Line Active
            lineActive = cac.get(f'MMACD_MA{lineIndex}_LineActive', False)
            if not lineActive: continue
            #[2]: Parameters
            nSamples = cac[f'MMACD_MA{lineIndex}_NSamples']
            if   type(nSamples) is not int: invalidLines[analysisCode].append(f"MA{lineIndex}_nSamples: Must be type 'int'")
            elif not 1 < nSamples:          invalidLines[analysisCode].append(f"MA{lineIndex}_nSamples: Must be greater than 1")
            else: activatedMAs.append(nSamples)
        #[3]: Activated MAs Sort & Params Update
        if (2 <= len(activatedMAs)) and (analysisCode not in invalidLines):
            activatedMAs.sort()
            activatedMAPairs = [(activatedMAs[maptIndex_S], activatedMAs[maptIndex_L]) for maptIndex_S in range (0, len(activatedMAs)-1) for maptIndex_L in range (maptIndex_S+1, len(activatedMAs))]
            maxMANSamples = max(activatedMAs)
            cap['MMACD'] = {'analysisCode': analysisCode,
                            'signal_nSamples':  signal_nSamples,
                            'activatedMAs':     activatedMAs,
                            'activatedMAPairs': activatedMAPairs,
                            'maxMANSamples':    maxMANSamples}
            
    if cac['DMIxADX_Master']:
        for lineIndex in range (constants.NLINES_DMIxADX):
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
        for lineIndex in range (constants.NLINES_MFI):
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
                                 'lineIndex':    lineIndex,
                                 'nSamples':     nSamples}
    
    if cac['TPD_Master']:
        for lineIndex in range (constants.NLINES_TPD):
            analysisCode = f'TPD_{lineIndex}'
            #[1]: Check Line Active
            lineActive = cac.get(f'{analysisCode}_LineActive', False)
            if not lineActive: continue
            #[2]: Parameters
            viewLength = cac[f'{analysisCode}_ViewLength']
            nSamples   = cac[f'{analysisCode}_NSamples']
            nSamplesMA = cac[f'{analysisCode}_NSamplesMA']
            if   type(viewLength) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < viewLength:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if   type(nSamples) is not int:   invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < nSamples:            invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if   type(nSamplesMA) is not int: invalidLines[analysisCode].append("nSamples: Must be type 'int'")
            elif not 1 < nSamplesMA:          invalidLines[analysisCode].append("nSamples: Must be greater than 1")
            if analysisCode in invalidLines: continue
            #[3]: Analysis Params
            cap[analysisCode] = {'analysisCode': analysisCode,
                                 'lineIndex':    lineIndex,
                                 'viewLength':   viewLength,
                                 'nSamples':     nSamples,
                                 'nSamplesMA':   nSamplesMA}
    
    if cac['WOI_Master']:
        for lineIndex in range (constants.NLINES_WOI):
            analysisCode = f'WOI_{lineIndex}'
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
            
    if cac['NES_Master']:
        for lineIndex in range (constants.NLINES_NES):
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

    #Return the constructed analysis params if no invalid line exists
    if invalidLines:
        cap = None
    return cap, invalidLines
#Analysis END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#Analysis Result Linearization --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def linearizeAnalysis_SMA(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_SMA': analysisResult['SMA']}
    return lRes

def linearizeAnalysis_WMA(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_WMA': analysisResult['WMA']}
    return lRes

def linearizeAnalysis_EMA(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_EMA': analysisResult['EMA']}
    return lRes

def linearizeAnalysis_PSAR(intervalID, analysisCode, analysisResult):
    psar = analysisResult['PSAR']
    if psar is None:
        lRes = {f'{intervalID}_{analysisCode}_PSAR': None,
                f'{intervalID}_{analysisCode}_DCC':  None}
    else:
        lRes = {f'{intervalID}_{analysisCode}_PSAR': analysisResult['PSAR'],
                f'{intervalID}_{analysisCode}_DCC':  analysisResult['DCC']}
    return lRes

def linearizeAnalysis_BOL(intervalID, analysisCode, analysisResult):
    bol = analysisResult['BOL']
    if bol is None:
        lRes = {f'{intervalID}_{analysisCode}_BOLLOW':  None,
                f'{intervalID}_{analysisCode}_BOLHIGH': None,
                f'{intervalID}_{analysisCode}_MA':      None}
    else:
        lRes = {f'{intervalID}_{analysisCode}_BOLLOW':  bol[0],
                f'{intervalID}_{analysisCode}_BOLHIGH': bol[1],
                f'{intervalID}_{analysisCode}_MA':      analysisResult['MA']}
    return lRes

def linearizeAnalysis_IVP(intervalID, analysisCode, analysisResult):
    nearBoundaries = analysisResult['volumePriceLevelProfile_NearBoundaries']
    lRes = {f'{intervalID}_{analysisCode}_NB{nbIndex}': nearBoundaries[nbIndex] for nbIndex in range (len(nearBoundaries))}
    return lRes

def linearizeAnalysis_SWING(intervalID, analysisCode, analysisResult):
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

def linearizeAnalysis_VOL(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_MABASE':    analysisResult['MA_BASE'],
            f'{intervalID}_{analysisCode}_MAQUOTE':   analysisResult['MA_QUOTE'],
            f'{intervalID}_{analysisCode}_MABASETB':  analysisResult['MA_BASETB'],
            f'{intervalID}_{analysisCode}_MAQUOTETB': analysisResult['MA_QUOTETB']}
    return lRes

def linearizeAnalysis_NNA(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_NNA': analysisResult['NNA']}
    return lRes

def linearizeAnalysis_MMACD(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_MSDELTA':         analysisResult['MSDELTA'],
            f'{intervalID}_{analysisCode}_MSDELTAABSMA':    analysisResult['MSDELTA_ABSMA'],
            f'{intervalID}_{analysisCode}_MSDELTAABSMAREL': analysisResult['MSDELTA_ABSMAREL']}
    return lRes

def linearizeAnalysis_DMIxADX(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_DMIxADX':         analysisResult['DMIxADX'],
            f'{intervalID}_{analysisCode}_DMIxADXABSMA':    analysisResult['DMIxADX_ABSMA'],
            f'{intervalID}_{analysisCode}_DMIxADXABSMAREL': analysisResult['DMIxADX_ABSMAREL']}
    return lRes

def linearizeAnalysis_MFI(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_MFI':            analysisResult['MFI'],
            f'{intervalID}_{analysisCode}_MFIDEVABSMA':    analysisResult['MFI_DEVABSMA'],
            f'{intervalID}_{analysisCode}_MFIDEVABSMAREL': analysisResult['MFI_DEVABSMAREL']}
    return lRes

def linearizeAnalysis_TPD(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_TPD':         analysisResult['TPD'],
            f'{intervalID}_{analysisCode}_TPDABSMA':    analysisResult['TPD_ABSMA'],
            f'{intervalID}_{analysisCode}_TPDABSMAREL': analysisResult['TPD_ABSMAREL']}
    return lRes

def linearizeAnalysis_WOI(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_WOI':         analysisResult['WOI'],
            f'{intervalID}_{analysisCode}_WOIABSMA':    analysisResult['WOI_ABSMA'],
            f'{intervalID}_{analysisCode}_WOIABSMAREL': analysisResult['WOI_ABSMAREL']}
    return lRes

def linearizeAnalysis_NES(intervalID, analysisCode, analysisResult):
    lRes = {f'{intervalID}_{analysisCode}_NES':         analysisResult['NES'],
            f'{intervalID}_{analysisCode}_NESABSMA':    analysisResult['NES_ABSMA'],
            f'{intervalID}_{analysisCode}_NESABSMAREL': analysisResult['NES_ABSMAREL']}
    return lRes

__ANALYSISLINEARIZERS = {'SMA':     linearizeAnalysis_SMA,
                         'WMA':     linearizeAnalysis_WMA,
                         'EMA':     linearizeAnalysis_EMA,
                         'PSAR':    linearizeAnalysis_PSAR,
                         'BOL':     linearizeAnalysis_BOL,
                         'IVP':     linearizeAnalysis_IVP,
                         'SWING':   linearizeAnalysis_SWING,
                         'VOL':     linearizeAnalysis_VOL,
                         'NNA':     linearizeAnalysis_NNA,
                         'MMACD':   linearizeAnalysis_MMACD,
                         'DMIxADX': linearizeAnalysis_DMIxADX,
                         'MFI':     linearizeAnalysis_MFI,
                         'TPD':     linearizeAnalysis_TPD,
                         'WOI':     linearizeAnalysis_WOI,
                         'NES':     linearizeAnalysis_NES}
def linearizeAnalysis(dataRaw, dataAggregated, analysisPairs, timestamp):
    #[1]: Instances
    als         = __ANALYSISLINEARIZERS
    func_gnitt  = auxiliaries.getNextIntervalTickTimestamp

    #[2]: Base Data Linearization
    kline    = dataRaw['kline'][timestamp]
    depth    = dataRaw['depth'][timestamp]
    aggTrade = dataRaw['aggTrade'][timestamp]
    aLinearized = {'OPENTIME':  timestamp,
                   'CLOSETIME': func_gnitt(intervalID = constants.KLINTERVAL, timestamp = timestamp, nTicks = 1)-1,
                   'KLINE_OPENPRICE':        kline[KLINDEX_OPENPRICE],
                   'KLINE_HIGHPRICE':        kline[KLINDEX_HIGHPRICE],
                   'KLINE_LOWPRICE':         kline[KLINDEX_LOWPRICE],
                   'KLINE_CLOSEPRICE':       kline[KLINDEX_CLOSEPRICE],
                   'KLINE_NTRADES':          kline[KLINDEX_NTRADES],
                   'KLINE_VOLBASE':          kline[KLINDEX_VOLBASE],
                   'KLINE_VOLQUOTE':         kline[KLINDEX_VOLQUOTE],
                   'KLINE_VOLBASETAKERBUY':  kline[KLINDEX_VOLBASETAKERBUY],
                   'KLINE_VOLQUOTETAKERBUY': kline[KLINDEX_VOLQUOTETAKERBUY],
                   'DEPTH_BIDS5':            depth[DEPTHINDEX_BIDS5],
                   'DEPTH_BIDS4':            depth[DEPTHINDEX_BIDS4],
                   'DEPTH_BIDS3':            depth[DEPTHINDEX_BIDS3],
                   'DEPTH_BIDS2':            depth[DEPTHINDEX_BIDS2],
                   'DEPTH_BIDS1':            depth[DEPTHINDEX_BIDS1],
                   'DEPTH_BIDS0':            depth[DEPTHINDEX_BIDS0],
                   'DEPTH_ASKS0':            depth[DEPTHINDEX_ASKS0],
                   'DEPTH_ASKS1':            depth[DEPTHINDEX_ASKS1],
                   'DEPTH_ASKS2':            depth[DEPTHINDEX_ASKS2],
                   'DEPTH_ASKS3':            depth[DEPTHINDEX_ASKS3],
                   'DEPTH_ASKS4':            depth[DEPTHINDEX_ASKS4],
                   'DEPTH_ASKS5':            depth[DEPTHINDEX_ASKS5],
                   'AGGTRADE_QUANTITYBUY':   aggTrade[ATINDEX_QUANTITYBUY],
                   'AGGTRADE_QUANTITYSELL':  aggTrade[ATINDEX_QUANTITYSELL],
                   'AGGTRADE_NTRADESBUY':    aggTrade[ATINDEX_NTRADESBUY],
                   'AGGTRADE_NTRADESSELL':   aggTrade[ATINDEX_NTRADESSELL],
                   'AGGTRADE_NOTIONALBUY':   aggTrade[ATINDEX_NOTIONALBUY],
                   'AGGTRADE_NOTIONALSELL':  aggTrade[ATINDEX_NOTIONALSELL],
                   }

    #[3]: Analysis Linearization
    for iID, ap_iID in analysisPairs.items():
        dAgg_iID = dataAggregated[iID]
        for aType, aCode in ap_iID:
            aggTS = func_gnitt(intervalID = iID, timestamp = timestamp, nTicks = 0)
            aLinearized_this = als[aType](intervalID     = iID,
                                          analysisCode   = aCode,
                                          analysisResult = dAgg_iID[aCode][aggTS])
            aLinearized.update(aLinearized_this)

    #[4]: Result Return
    return aLinearized
#Analysis Result Linearization END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
