import auxiliaries
import constants

import os
import importlib
import traceback
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





#Search & Import Analysis Function Files ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
path_PROJECT                = os.path.dirname(os.path.realpath(__file__))
ANALYSES                    = dict()
ANALYSIS_MODULES_IMPORT = ('volume.py',
                           'moving_average_simple.py',
                           'moving_average_weighted.py',
                           'moving_average_exponential.py',
                           'parabolic_stop_and_reverse.py',
                           'bollinger_band.py',
                           'interpreted_volume_profile.py',
                           'swing.py',
                           'weighted_order_imbalance.py',
                           'net_execution_strength.py')

analysis_modules_dir = os.listdir(os.path.join(path_PROJECT, 'analysis'))
for name_file in ANALYSIS_MODULES_IMPORT:
    #File Type & Template Check
    if name_file not in analysis_modules_dir:
        continue

    #File Read
    name_analysis_file = name_file[:-3]
    try:
        module        = importlib.import_module(f"analysis.{name_analysis_file}")
        analysis_code = getattr(module, 'ANALYSIS_CODE')
        ANALYSES[analysis_code] = {#DEFINING PARAMETERS
                                   'CODE':      analysis_code,
                                   'TYPE':      getattr(module, 'ANALYSIS_TYPE'),
                                   'NMAXLINES': getattr(module, 'NMAXLINES'),

                                   #ANALYSIS GENERATION
                                   'FN_GENERATE':     getattr(module, 'generate'),
                                   'FN_CONSTRUCT_AP': getattr(module, 'construct_analysis_parameters'),

                                   #LINEARIZATION
                                   'FN_LINEARIZE': getattr(module, 'linearize'),

                                   #ANALYZER (Maximum Market Data Reference Length)
                                   'FN_GET_MMDRL': getattr(module, 'get_maximum_market_data_reference_length'),

                                   #PAGE & OBJECT CALLS - CHARTDRAWER
                                   'CD_FULL_DRAW_SIGNALS':        getattr(module, 'CD_FULL_DRAW_SIGNALS'),
                                   'CD_VVR_PRECISIONCOMPENSATOR': getattr(module, 'CD_VVR_PRECISIONCOMPENSATOR'),
                                   'CD_VVR_CENTERVALUE':          getattr(module, 'CD_VVR_CENTERVALUE'),
                                   'CD_VVR_DEFAULT':              getattr(module, 'CD_VVR_DEFAULT'),
                                   'FN_CD_GIC':   getattr(module, 'cd_get_initial_configuration'),
                                   'FN_CD_ISSG':  getattr(module, 'cd_initialize_settings_subpage_generate'),
                                   'FN_CD_ISSS':  getattr(module, 'cd_initialize_settings_subpage_setup'),
                                   'FN_CD_MGTC':  getattr(module, 'cd_match_guios_to_config'),
                                   'FN_CD_LAC':   getattr(module, 'cd_load_analysis_configuration'),
                                   'FN_CD_OSCU':  getattr(module, 'cd_on_settings_content_update'),

                                   'FN_CD_PHU':   getattr(module, 'cd_on_position_highlight_update'),
                                   'FN_CD_PSU':   getattr(module, 'cd_on_position_selection_update'),
                                   'FN_CD_CVE':   getattr(module, 'cd_check_vertical_extremas'),
                                   'FN_CD_DRAW':  getattr(module, 'cd_draw'),
                                   'FN_CD_RMVED': getattr(module, 'cd_remove_expired_drawings'),
                                   'FN_CD_RMVD':  getattr(module, 'cd_remove_drawings'),
                                   'FN_CD_GVMA':  getattr(module, 'cd_get_vertical_magnitude_anchor'),

                                   'FN_CD_OGTU':  getattr(module, 'cd_on_GUI_theme_update'),

                                   'FN_USTAC':    getattr(module, 'cd_update_si_type_analysis_codes'),
                                   'FN_TYPEINIT': getattr(module, 'cd_type_init'),

                                   #PAGE & OBJECT CALLS - AUTOTRADE
                                   'FN_PG_AUTOTRADE_GDAC':  getattr(module, 'pg_autotrade_get_default_analysis_configuration'),
                                   'FN_PG_AUTOTRADE_CFSPG': getattr(module, 'pg_autotrade_configure_subpage_generate'),
                                   'FN_PG_AUTOTRADE_CFSPS': getattr(module, 'pg_autotrade_configure_subpage_setup'),
                                   'FN_PG_AUTOTRADE_LDAC':  getattr(module, 'pg_autotrade_load_analysis_configuration'),
                                   'FN_PG_AUTOTRADE_FACFG': getattr(module, 'pg_autotrade_format_analysis_configuration_from_guios'),

                                   #PAGE & OBJECT CALLS - SIMULATION RESULT
                                   'FN_PG_SIMULATION_RESULT_CFSPG': getattr(module, 'pg_simulation_result_configure_subpage_generate'),
                                   'FN_PG_SIMULATION_RESULT_CFSPS': getattr(module, 'pg_simulation_result_configure_subpage_setup'),
                                   'FN_PG_SIMULATION_RESULT_LDAC':  getattr(module, 'pg_simulation_result_load_analysis_configuration'),
                                   }

    except Exception as e:
        traceback.print_exc()

ANALYSIS_MITYPES         = tuple(amCode for amCode in ANALYSES if ANALYSES[amCode]['TYPE'] == 'MAIN')
ANALYSIS_SITYPES         = tuple(amCode for amCode in ANALYSES if ANALYSES[amCode]['TYPE'] == 'SUB')
ANALYSIS_GENERATIONORDER = ('SMA', 'WMA', 'EMA', 'PSAR', 'BOL', 'IVP', 'SWING', 'VOL', 'NNA', 'MMACD', 'DMIxADX', 'MFI', 'TPD', 'WOI', 'NES')
#Search & Import Analysis Function Files END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





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
def analysisGenerator(analysisType, **params):
    return ANALYSES[analysisType]['FN_GENERATE'](**params) if analysisType in ANALYSES else None

def constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(currencyAnalysisConfiguration):
    #[1]: Instances & Initialization
    cap          = dict()
    invalidLines = defaultdict(list)

    #[2]: Analysis Parameters Construction
    for am in ANALYSES.values():
        am_cap, am_ils = am['FN_CONSTRUCT_AP'](currencyAnalysisConfiguration)
        cap.update(am_cap)
        invalidLines.update(am_ils)

    #[3]: Return The Constructed Analysis Parameters & Invalid Lines
    if invalidLines:
        cap = None
    return cap, invalidLines
#Analysis END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#Analysis Result Linearization --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def linearizeAnalysis(dataRaw, dataAggregated, analysisPairs, timestamp):
    #[1]: Instances
    aux        = auxiliaries
    func_gnitt = aux.getNextIntervalTickTimestamp

    #[2]: Base Data Linearization
    kline     = dataRaw['kline'][timestamp]
    depth     = dataRaw['depth'][timestamp]
    aggTrade  = dataRaw['aggTrade'][timestamp]
    closeTime = func_gnitt(intervalID = constants.KLINTERVAL, timestamp = timestamp, nTicks = 1)-1
    closed = (kline[KLINDEX_CLOSED] and depth[DEPTHINDEX_CLOSED] and aggTrade[ATINDEX_CLOSED])
    aLinearized = {'OPENTIME':  timestamp,
                   'CLOSETIME': closeTime,
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_1m}':  closed,
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_3m}':  (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_3m,  timestamp = timestamp, nTicks = 1)-1 == closeTime)),
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_5m}':  (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_5m,  timestamp = timestamp, nTicks = 1)-1 == closeTime)),
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_15m}': (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_15m, timestamp = timestamp, nTicks = 1)-1 == closeTime)),
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_30m}': (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_30m, timestamp = timestamp, nTicks = 1)-1 == closeTime)),
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_1h}':  (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_1h,  timestamp = timestamp, nTicks = 1)-1 == closeTime)),
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_2h}':  (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_2h,  timestamp = timestamp, nTicks = 1)-1 == closeTime)),
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_4h}':  (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_4h,  timestamp = timestamp, nTicks = 1)-1 == closeTime)),
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_6h}':  (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_6h,  timestamp = timestamp, nTicks = 1)-1 == closeTime)),
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_8h}':  (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_8h,  timestamp = timestamp, nTicks = 1)-1 == closeTime)),
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_12h}': (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_12h, timestamp = timestamp, nTicks = 1)-1 == closeTime)),
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_1d}':  (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_1d,  timestamp = timestamp, nTicks = 1)-1 == closeTime)),
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_3d}':  (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_3d,  timestamp = timestamp, nTicks = 1)-1 == closeTime)),
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_1W}':  (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_1W,  timestamp = timestamp, nTicks = 1)-1 == closeTime)),
                   f'CLOSED_{aux.KLINE_INTERVAL_ID_1M}':  (closed and (func_gnitt(intervalID = aux.KLINE_INTERVAL_ID_1M,  timestamp = timestamp, nTicks = 1)-1 == closeTime)),
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
        for amType, aCode in ap_iID:
            aggTS = func_gnitt(intervalID = iID, timestamp = timestamp, nTicks = 0)
            aLinearized_this = ANALYSES[amType]['FN_LINEARIZE'](intervalID     = iID,
                                                                analysisCode   = aCode,
                                                                analysisResult = dAgg_iID[aCode][aggTS])
            aLinearized.update(aLinearized_this)

    #[4]: Result Return
    return aLinearized
#Analysis Result Linearization END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
