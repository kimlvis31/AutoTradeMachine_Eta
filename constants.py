import binance
from datetime import datetime, timezone

TIMEZONE = datetime.now(timezone.utc).astimezone()
TIMEZONE_DELTA_SEC = TIMEZONE.utcoffset().seconds

KLINE_INTERVAL_ID_1m  = 0
KLINE_INTERVAL_ID_3m  = 1
KLINE_INTERVAL_ID_5m  = 2
KLINE_INTERVAL_ID_15m = 3
KLINE_INTERVAL_ID_30m = 4
KLINE_INTERVAL_ID_1h  = 5
KLINE_INTERVAL_ID_2h  = 6
KLINE_INTERVAL_ID_4h  = 7
KLINE_INTERVAL_ID_6h  = 8
KLINE_INTERVAL_ID_8h  = 9
KLINE_INTERVAL_ID_12h = 10
KLINE_INTERVAL_ID_1d  = 11
KLINE_INTERVAL_ID_3d  = 12
KLINE_INTERVAL_ID_1W  = 13
KLINE_INTERVAL_ID_1M  = 14
KLINE_INTERVAL_IDs = (KLINE_INTERVAL_ID_1m, 
                      KLINE_INTERVAL_ID_3m, 
                      KLINE_INTERVAL_ID_5m, 
                      KLINE_INTERVAL_ID_15m, 
                      KLINE_INTERVAL_ID_30m, 
                      KLINE_INTERVAL_ID_1h, 
                      KLINE_INTERVAL_ID_2h, 
                      KLINE_INTERVAL_ID_4h, 
                      KLINE_INTERVAL_ID_6h, 
                      KLINE_INTERVAL_ID_8h, 
                      KLINE_INTERVAL_ID_12h, 
                      KLINE_INTERVAL_ID_1d, 
                      KLINE_INTERVAL_ID_3d, 
                      KLINE_INTERVAL_ID_1W, 
                      KLINE_INTERVAL_ID_1M)

KLINE_INTERVAL_SECs = {KLINE_INTERVAL_ID_1m:      60,
                       KLINE_INTERVAL_ID_3m:     180,
                       KLINE_INTERVAL_ID_5m:     300,
                       KLINE_INTERVAL_ID_15m:    900,
                       KLINE_INTERVAL_ID_30m:   1800,
                       KLINE_INTERVAL_ID_1h:    3600,
                       KLINE_INTERVAL_ID_2h:    7200,
                       KLINE_INTERVAL_ID_4h:   14400,
                       KLINE_INTERVAL_ID_6h:   21600,
                       KLINE_INTERVAL_ID_8h:   28800,
                       KLINE_INTERVAL_ID_12h:  43200,
                       KLINE_INTERVAL_ID_1d:   86400,
                       KLINE_INTERVAL_ID_3d:  259200,
                       KLINE_INTERVAL_ID_1W:  604800,
                       KLINE_INTERVAL_ID_1M: 2678400}

GRID_INTERVAL_ID_1m   =  0
GRID_INTERVAL_ID_3m   =  1
GRID_INTERVAL_ID_5m   =  2
GRID_INTERVAL_ID_10m  =  3
GRID_INTERVAL_ID_15m  =  4
GRID_INTERVAL_ID_30m  =  5
GRID_INTERVAL_ID_1h   =  6
GRID_INTERVAL_ID_2h   =  7
GRID_INTERVAL_ID_4h   =  8
GRID_INTERVAL_ID_6h   =  9
GRID_INTERVAL_ID_8h   = 10
GRID_INTERVAL_ID_12h  = 11
GRID_INTERVAL_ID_1d   = 12
GRID_INTERVAL_ID_3d   = 13
GRID_INTERVAL_ID_1W   = 14
GRID_INTERVAL_ID_1M   = 15
GRID_INTERVAL_ID_3M   = 16
GRID_INTERVAL_ID_6M   = 17
GRID_INTERVAL_ID_1Y   = 18
GRID_INTERVAL_ID_2Y   = 19
GRID_INTERVAL_ID_5Y   = 20
GRID_INTERVAL_ID_10Y  = 21
GRID_INTERVAL_ID_20Y  = 22
GRID_INTERVAL_ID_50Y  = 23
GRID_INTERVAL_ID_100Y = 24
GRID_INTERVAL_IDs = (GRID_INTERVAL_ID_1m, 
                     GRID_INTERVAL_ID_3m, 
                     GRID_INTERVAL_ID_5m, 
                     GRID_INTERVAL_ID_10m, 
                     GRID_INTERVAL_ID_15m, 
                     GRID_INTERVAL_ID_30m, 
                     GRID_INTERVAL_ID_1h, 
                     GRID_INTERVAL_ID_2h, 
                     GRID_INTERVAL_ID_4h, 
                     GRID_INTERVAL_ID_6h,  
                     GRID_INTERVAL_ID_8h,  
                     GRID_INTERVAL_ID_12h,
                     GRID_INTERVAL_ID_1d, 
                     GRID_INTERVAL_ID_3d, 
                     GRID_INTERVAL_ID_1W, 
                     GRID_INTERVAL_ID_1M,  
                     GRID_INTERVAL_ID_3M,  
                     GRID_INTERVAL_ID_6M,  
                     GRID_INTERVAL_ID_1Y, 
                     GRID_INTERVAL_ID_2Y, 
                     GRID_INTERVAL_ID_5Y, 
                     GRID_INTERVAL_ID_10Y, 
                     GRID_INTERVAL_ID_20Y, 
                     GRID_INTERVAL_ID_50Y, 
                     GRID_INTERVAL_ID_100Y)
GRID_INTERVAL_SECs = {GRID_INTERVAL_ID_1m:      60,
                      GRID_INTERVAL_ID_3m:     180,
                      GRID_INTERVAL_ID_5m:     300,
                      GRID_INTERVAL_ID_10m:    600,
                      GRID_INTERVAL_ID_15m:    900,
                      GRID_INTERVAL_ID_30m:   1800,
                      GRID_INTERVAL_ID_1h:    3600,
                      GRID_INTERVAL_ID_2h:    7200,
                      GRID_INTERVAL_ID_4h:   14400,
                      GRID_INTERVAL_ID_6h:   21600,
                      GRID_INTERVAL_ID_8h:   28800,
                      GRID_INTERVAL_ID_12h:  43200,
                      GRID_INTERVAL_ID_1d:   86400,
                      GRID_INTERVAL_ID_3d:  259200,
                      GRID_INTERVAL_ID_1W:  604800}

EXPECTEDTEMPORALWIDTHS = {0:       60, #  1m
                          1:      180, #  3m
                          2:      300, #  5m
                          3:      900, # 15m
                          4:     1800, # 30m
                          5:     3600, #  1h
                          6:     7200, #  2h
                          7:    14400, #  4h
                          8:    21600, #  6h
                          9:    28800, #  8h
                          10:   43200, # 12h
                          11:   86400, #  1d
                          12:  259200, #  3d
                          13:  604800, #  7d
                          14: 2592000} # 30d

KLINTERVAL                = KLINE_INTERVAL_ID_1m
KLINTERVAL_CLIENT         = binance.Client.KLINE_INTERVAL_1MINUTE
KLINTERVAL_STREAM         = "1m"
KLINTERVAL_S              = 60
KLINTERVAL_METRICS        = KLINE_INTERVAL_ID_5m
KLINTERVAL_METRICS_CLIENT = binance.Client.KLINE_INTERVAL_5MINUTE
KLINTERVAL_METRICS_STREAM = "5m"
KLINTERVAL_METRICS_S      = 300

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

METRICINDEX_OPENTIME          = 0
METRICINDEX_CLOSETIME         = 1
METRICINDEX_OPENINTEREST      = 2
METRICINDEX_OPENINTERESTVALUE = 3
METRICINDEX_LONGSHORTRATIO    = 4
METRICINDEX_CLOSED            = 5
METRICINDEX_SOURCE            = 6

DEPTHBINS = {DEPTHINDEX_BIDS5: (-5.0, -4.0),
             DEPTHINDEX_BIDS4: (-4.0, -3.0),
             DEPTHINDEX_BIDS3: (-3.0, -2.0),
             DEPTHINDEX_BIDS2: (-2.0, -1.0),
             DEPTHINDEX_BIDS1: (-1.0, -0.2),
             DEPTHINDEX_BIDS0: (-0.2,  0.0),
             DEPTHINDEX_ASKS0: ( 0.0,  0.2),
             DEPTHINDEX_ASKS1: ( 0.2,  1.0),
             DEPTHINDEX_ASKS2: ( 1.0,  2.0),
             DEPTHINDEX_ASKS3: ( 2.0,  3.0),
             DEPTHINDEX_ASKS4: ( 3.0,  4.0),
             DEPTHINDEX_ASKS5: ( 4.0,  5.0)}
DEPTHBINS_MIN = min(db[0] for db in DEPTHBINS.values())
DEPTHBINS_MAX = max(db[1] for db in DEPTHBINS.values())
DEPTHBINS_BID_THRESHOLDS = {dIdx: -DEPTHBINS[dIdx][0] / 100 for dIdx in (DEPTHINDEX_BIDS0, DEPTHINDEX_BIDS1, DEPTHINDEX_BIDS2, DEPTHINDEX_BIDS3, DEPTHINDEX_BIDS4, DEPTHINDEX_BIDS5)}
DEPTHBINS_ASK_THRESHOLDS = {dIdx:  DEPTHBINS[dIdx][1] / 100 for dIdx in (DEPTHINDEX_ASKS0, DEPTHINDEX_ASKS1, DEPTHINDEX_ASKS2, DEPTHINDEX_ASKS3, DEPTHINDEX_ASKS4, DEPTHINDEX_ASKS5)}

FORMATTEDDATATYPE_FETCHED    = 0
FORMATTEDDATATYPE_EMPTY      = 1
FORMATTEDDATATYPE_DUMMY      = 2
FORMATTEDDATATYPE_STREAMED   = 3
FORMATTEDDATATYPE_INCOMPLETE = 4

COMMONDATAINDEXES = {'openTime':  {'kline': KLINDEX_OPENTIME,  'depth': DEPTHINDEX_OPENTIME,  'aggTrade': ATINDEX_OPENTIME,  'metric': METRICINDEX_OPENTIME},
                     'closeTime': {'kline': KLINDEX_CLOSETIME, 'depth': DEPTHINDEX_CLOSETIME, 'aggTrade': ATINDEX_CLOSETIME, 'metric': METRICINDEX_CLOSETIME},
                     'closed':    {'kline': KLINDEX_CLOSED,    'depth': DEPTHINDEX_CLOSED,    'aggTrade': ATINDEX_CLOSED,    'metric': METRICINDEX_CLOSED},
                     'source':    {'kline': KLINDEX_SOURCE,    'depth': DEPTHINDEX_SOURCE,    'aggTrade': ATINDEX_SOURCE,    'metric': METRICINDEX_SOURCE}}

DUMMYFRAMES = {'kline':    (None, None, None, None, None, None, None, None, None,                   True, FORMATTEDDATATYPE_DUMMY),
               'depth':    (None, None, None, None, None, None, None, None, None, None, None, None, True, FORMATTEDDATATYPE_DUMMY),
               'aggTrade': (None, None, None, None, None, None,                                     True, FORMATTEDDATATYPE_DUMMY),
               'metric':   (None, None, None,                                                       True, FORMATTEDDATATYPE_DUMMY)}