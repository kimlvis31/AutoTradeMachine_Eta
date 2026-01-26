from threading import Thread
from datetime import datetime, timezone, tzinfo

KLINE_INTERVAL_ID_1m  = 0;  
KLINE_INTERVAL_ID_3m  = 1;  
KLINE_INTERVAL_ID_5m  = 2;  
KLINE_INTERVAL_ID_15m = 3;  
KLINE_INTERVAL_ID_30m = 4;  
KLINE_INTERVAL_ID_1h  = 5;  
KLINE_INTERVAL_ID_2h  = 6;  
KLINE_INTERVAL_ID_4h  = 7;  
KLINE_INTERVAL_ID_6h  = 8;  
KLINE_INTERVAL_ID_8h  = 9;  
KLINE_INTERVAL_ID_12h = 10; 
KLINE_INTERVAL_ID_1d  = 11; 
KLINE_INTERVAL_ID_3d  = 12; 
KLINE_INTERVAL_ID_1W  = 13; 
KLINE_INTERVAL_ID_1M  = 14; 
KLINE_INTERVAL_IDs = (KLINE_INTERVAL_ID_1m, KLINE_INTERVAL_ID_3m, KLINE_INTERVAL_ID_5m, KLINE_INTERVAL_ID_15m, KLINE_INTERVAL_ID_30m, KLINE_INTERVAL_ID_1h, KLINE_INTERVAL_ID_2h, KLINE_INTERVAL_ID_4h, KLINE_INTERVAL_ID_6h, KLINE_INTERVAL_ID_8h, KLINE_INTERVAL_ID_12h, 
                      KLINE_INTERVAL_ID_1d, KLINE_INTERVAL_ID_3d, KLINE_INTERVAL_ID_1W, KLINE_INTERVAL_ID_1M)

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

GRID_INTERVAL_ID_1m  =  0
GRID_INTERVAL_ID_3m  =  1
GRID_INTERVAL_ID_5m  =  2
GRID_INTERVAL_ID_10m =  3
GRID_INTERVAL_ID_15m =  4
GRID_INTERVAL_ID_30m =  5
GRID_INTERVAL_ID_1h  =  6
GRID_INTERVAL_ID_2h  =  7
GRID_INTERVAL_ID_4h  =  8
GRID_INTERVAL_ID_6h  =  9
GRID_INTERVAL_ID_8h  = 10
GRID_INTERVAL_ID_12h = 11
GRID_INTERVAL_ID_1d  = 12
GRID_INTERVAL_ID_3d  = 13
GRID_INTERVAL_ID_1W  = 14
GRID_INTERVAL_ID_1M  = 15
GRID_INTERVAL_ID_3M  = 16
GRID_INTERVAL_ID_6M  = 17
GRID_INTERVAL_ID_1Y  = 18
GRID_INTERVAL_ID_2Y  = 19
GRID_INTERVAL_ID_5Y  = 20
GRID_INTERVAL_ID_10Y = 21
GRID_INTERVAL_ID_20Y = 22
GRID_INTERVAL_IDs = (GRID_INTERVAL_ID_1m, GRID_INTERVAL_ID_3m, GRID_INTERVAL_ID_5m, GRID_INTERVAL_ID_10m, GRID_INTERVAL_ID_15m, GRID_INTERVAL_ID_30m, GRID_INTERVAL_ID_1h, GRID_INTERVAL_ID_2h, GRID_INTERVAL_ID_4h, GRID_INTERVAL_ID_6h,  GRID_INTERVAL_ID_8h,  GRID_INTERVAL_ID_12h,
                     GRID_INTERVAL_ID_1d, GRID_INTERVAL_ID_3d, GRID_INTERVAL_ID_1W, GRID_INTERVAL_ID_1M,  GRID_INTERVAL_ID_3M,  GRID_INTERVAL_ID_6M,  GRID_INTERVAL_ID_1Y, GRID_INTERVAL_ID_2Y, GRID_INTERVAL_ID_5Y, GRID_INTERVAL_ID_10Y, GRID_INTERVAL_ID_20Y)
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

TIMEZONE = datetime.now(timezone.utc).astimezone()
TIMEZONE_DELTA_SEC = TIMEZONE.utcoffset().seconds

#Binance API
def getAPISymbol(dirSymbol): return dirSymbol.replace("%","/").replace("&",":")
def getDirSymbol(apiSymbol): return apiSymbol.replace("/","%").replace(":","&")



#Return a list of timestamps for nTicks of interval
def getTimestampList_byRange(intervalID, timestamp_beg, timestamp_end, mrktReg = None, lastTickInclusive = False):
    if (intervalID == KLINE_INTERVAL_ID_1M):
        timestamps = list()
        timestamp_dateTime = datetime.fromtimestamp(timestamp_beg, tz = timezone.utc)
        while (True):
            nextMonth = timestamp_dateTime.month+len(timestamps)
            nextMonth_yearDeducted = nextMonth%12
            if (nextMonth_yearDeducted == 0): newMonthDate_year = timestamp_dateTime.year + int(nextMonth/12) - 1; newMonthDate_month = 12
            else:                             newMonthDate_year = timestamp_dateTime.year + int(nextMonth/12);     newMonthDate_month = nextMonth_yearDeducted
            nextTimestamp = int(datetime(year = newMonthDate_year, month = newMonthDate_month, day = 1, tzinfo = timezone.utc).timestamp())
            if (nextTimestamp <= timestamp_end): timestamps.append(nextTimestamp)
            else: break
        if (lastTickInclusive == True): return timestamps
        else:                           return timestamps[:-1]

    elif (intervalID == KLINE_INTERVAL_ID_1W):
        timestamp_ISOCalendar_BEG = datetime.fromtimestamp(timestamp_beg, tz = timezone.utc).isocalendar()
        timestamp_ISOCalendar_END = datetime.fromtimestamp(timestamp_end, tz = timezone.utc).isocalendar()
        firstTickTS = int(datetime.fromisocalendar(year = timestamp_ISOCalendar_BEG.year, week = timestamp_ISOCalendar_BEG.week, day = 1).timestamp() + TIMEZONE_DELTA_SEC)
        lastTickTS  = int(datetime.fromisocalendar(year = timestamp_ISOCalendar_END.year, week = timestamp_ISOCalendar_END.week, day = 1).timestamp() + TIMEZONE_DELTA_SEC)
        if (lastTickInclusive == True): return list(range(firstTickTS, lastTickTS+1, KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_1W]))
        else:                           return list(range(firstTickTS, lastTickTS,   KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_1W]))

    elif (intervalID == KLINE_INTERVAL_ID_3d):
        if (mrktReg == None): 
            firstTickTS = int(timestamp_beg/KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d])*KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d]
        else:
            mrktRegFirstDay = int(mrktReg      /86400)*86400
            timestamp_1d    = int(timestamp_beg/86400)*86400
            firstTickTS = (int((timestamp_1d-mrktRegFirstDay)/259200))*259200+mrktRegFirstDay
        lastTickTS  = int(timestamp_end/KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d])*KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d]
        if (lastTickInclusive == True): return list(range(firstTickTS, lastTickTS+1, KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d]))
        else:                           return list(range(firstTickTS, lastTickTS,   KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d]))

    else: 
        firstTickTS = int(timestamp_beg/KLINE_INTERVAL_SECs[intervalID])*KLINE_INTERVAL_SECs[intervalID]
        lastTickTS  = int(timestamp_end/KLINE_INTERVAL_SECs[intervalID])*KLINE_INTERVAL_SECs[intervalID]
        if (lastTickInclusive == True): return list(range(firstTickTS, lastTickTS+1, KLINE_INTERVAL_SECs[intervalID]))
        else:                           return list(range(firstTickTS, lastTickTS,   KLINE_INTERVAL_SECs[intervalID]))#Return a list of timestamps for nTicks of interval

def getTimestampList_byNTicks(intervalID, timestamp, nTicks, direction = False, mrktReg = None):
    if (intervalID == KLINE_INTERVAL_ID_1M):
        timestamps = list()
        timestamp_dateTime = datetime.fromtimestamp(timestamp, tz = timezone.utc)
        year_thisTick  = timestamp_dateTime.year
        month_thisTick = timestamp_dateTime.month
        for i in range (nTicks):
            timestamps.append(int(datetime(year = year_thisTick, month = month_thisTick, day = 1, tzinfo = timezone.utc).timestamp()))
            if (direction == False):
                month_thisTick -= 1
                if (month_thisTick == 0): month_thisTick = 12; year_thisTick -= 1
            else:
                month_thisTick += 1
                if (month_thisTick == 13): month_thisTick = 1; year_thisTick += 1
        if (direction == False): timestamps.sort(reverse = True);  return timestamps
        else:                    timestamps.sort(reverse = False); return timestamps

    elif (intervalID == KLINE_INTERVAL_ID_1W):
        timestamp_ISOCalendar_BEG = datetime.fromtimestamp(timestamp, tz = timezone.utc).isocalendar()
        firstTickTS = int(datetime.fromisocalendar(year = timestamp_ISOCalendar_BEG.year, week = timestamp_ISOCalendar_BEG.week, day = 1).timestamp() + TIMEZONE_DELTA_SEC)
        if (direction == False):
            lastTickTS = firstTickTS - KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_1W]*(nTicks-1)
            timestamps = list(range(lastTickTS, firstTickTS+1, KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_1W]))
            timestamps.sort(reverse = True)
            return timestamps
        else:
            lastTickTS = firstTickTS + KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_1W]*(nTicks-1)
            timestamps = list(range(firstTickTS, lastTickTS+1, KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_1W]))
            timestamps.sort(reverse = False)
            return timestamps

    elif (intervalID == KLINE_INTERVAL_ID_3d):
        if (mrktReg == None): firstTickTS = int(timestamp/KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d])*KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d]
        else:
            mrktRegFirstDay = int(mrktReg  /86400)*86400
            timestamp_1d    = int(timestamp/86400)*86400
            firstTickTS = (int((timestamp_1d-mrktRegFirstDay)/259200))*259200+mrktRegFirstDay
        if (direction == False):
            lastTickTS = firstTickTS - KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d]*(nTicks-1)
            timestamps = list(range(lastTickTS, firstTickTS+1, KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d]))
            timestamps.sort(reverse = True)
            return timestamps
        else:
            lastTickTS = firstTickTS + KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d]*(nTicks-1)
            timestamps = list(range(firstTickTS, lastTickTS+1, KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d]))
            timestamps.sort(reverse = False)
            return timestamps
    else: 
        firstTickTS = int(timestamp/KLINE_INTERVAL_SECs[intervalID])*KLINE_INTERVAL_SECs[intervalID]
        if (direction == False):
            lastTickTS = firstTickTS - KLINE_INTERVAL_SECs[intervalID]*(nTicks-1)
            timestamps = list(range(lastTickTS, firstTickTS+1, KLINE_INTERVAL_SECs[intervalID]))
            timestamps.sort(reverse = True)
            return timestamps
        else:
            lastTickTS = firstTickTS + KLINE_INTERVAL_SECs[intervalID]*(nTicks-1)
            timestamps = list(range(firstTickTS, lastTickTS+1, KLINE_INTERVAL_SECs[intervalID]))
            timestamps.sort(reverse = False)
            return timestamps
    
#Calculate and return the next interval tick timestamp
def getNextIntervalTickTimestamp(intervalID, timestamp, mrktReg = None, nTicks = 1):
    if (intervalID == KLINE_INTERVAL_ID_1M):
        timestamp_dateTime = datetime.fromtimestamp(timestamp, tz = timezone.utc)
        nextMonth = timestamp_dateTime.month+nTicks
        nextMonth_yearDeducted = nextMonth%12
        if (nextMonth_yearDeducted == 0): newMonthDate_year = timestamp_dateTime.year + int(nextMonth/12) - 1; newMonthDate_month = 12
        else:                             newMonthDate_year = timestamp_dateTime.year + int(nextMonth/12);     newMonthDate_month = nextMonth_yearDeducted
        return int(datetime(year = newMonthDate_year, month = newMonthDate_month, day = 1, tzinfo = timezone.utc).timestamp())

    elif (intervalID == KLINE_INTERVAL_ID_1W):
        timestamp_ISOCalendar = datetime.fromtimestamp(timestamp, tz = timezone.utc).isocalendar()
        return int(datetime.fromisocalendar(year = timestamp_ISOCalendar.year, week = timestamp_ISOCalendar.week, day = 1).timestamp() + TIMEZONE_DELTA_SEC + KLINE_INTERVAL_SECs[intervalID]*nTicks)

    elif (intervalID == KLINE_INTERVAL_ID_3d):
        if (mrktReg == None): return (int(timestamp/KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d])+nTicks)*KLINE_INTERVAL_SECs[KLINE_INTERVAL_ID_3d]
        else:
            mrktRegFirstDay = int(mrktReg  /86400)*86400
            timestamp_1d    = int(timestamp/86400)*86400
            return (int((timestamp_1d-mrktRegFirstDay)/259200)+nTicks)*259200+mrktRegFirstDay

    else: return (int(timestamp/KLINE_INTERVAL_SECs[intervalID])+nTicks)*KLINE_INTERVAL_SECs[intervalID]
    
    



#getTimestampList_byRange_GRID ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __getTimestampList_byRange_GRID_1Y(intervalID, timestamp_beg, timestamp_end, mrktReg, lastTickInclusive):
    timestamps = list()
    currentTickYear = datetime.fromtimestamp(timestamp_beg, tz = timezone.utc).year
    while (True):
        nextYear = currentTickYear+len(timestamps)
        nextYear_TS = int(datetime(year = nextYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
        if (nextYear_TS <= timestamp_end): timestamps.append(nextYear_TS)
        else: break
    if (lastTickInclusive == True): return timestamps
    else:                           return timestamps[:-1]
def __getTimestampList_byRange_GRID_2Y(intervalID, timestamp_beg, timestamp_end, mrktReg, lastTickInclusive):
    timestamps = list()
    if (mrktReg == None):
        currentTickYear = datetime.fromtimestamp(timestamp_beg, tz = timezone.utc).year
    else:
        mrktRegYear = datetime.fromtimestamp(mrktReg, tz = timezone.utc).year
        currentTickYear = mrktRegYear + int((datetime.fromtimestamp(timestamp_beg, tz = timezone.utc).year-mrktRegYear)/2)*2
    while (True):
        nextYear = currentTickYear+len(timestamps)*2
        nextYear_TS = int(datetime(year = nextYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
        if (nextYear_TS <= timestamp_end): timestamps.append(nextYear_TS)
        else: break
    if (lastTickInclusive == True): return timestamps
    else:                           return timestamps[:-1]
def __getTimestampList_byRange_GRID_5Y(intervalID, timestamp_beg, timestamp_end, mrktReg, lastTickInclusive):
    timestamps = list()
    if (mrktReg == None):
        currentTickYear = datetime.fromtimestamp(timestamp_beg, tz = timezone.utc).year
    else:
        mrktRegYear = datetime.fromtimestamp(mrktReg, tz = timezone.utc).year
        currentTickYear = mrktRegYear + int((datetime.fromtimestamp(timestamp_beg, tz = timezone.utc).year-mrktRegYear)/5)*5
    while (True):
        nextYear = currentTickYear+len(timestamps)*5
        nextYear_TS = int(datetime(year = nextYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
        if (nextYear_TS <= timestamp_end): timestamps.append(nextYear_TS)
        else: break
    if (lastTickInclusive == True): return timestamps
    else:                           return timestamps[:-1]
def __getTimestampList_byRange_GRID_10Y(intervalID, timestamp_beg, timestamp_end, mrktReg, lastTickInclusive):
    timestamps = list()
    if (mrktReg == None):
        currentTickYear = datetime.fromtimestamp(timestamp_beg, tz = timezone.utc).year
    else:
        mrktRegYear = datetime.fromtimestamp(mrktReg, tz = timezone.utc).year
        currentTickYear = mrktRegYear + int((datetime.fromtimestamp(timestamp_beg, tz = timezone.utc).year-mrktRegYear)/10)*10
    while (True):
        nextYear = currentTickYear+len(timestamps)*10
        nextYear_TS = int(datetime(year = nextYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
        if (nextYear_TS <= timestamp_end): timestamps.append(nextYear_TS)
        else: break
    if (lastTickInclusive == True): return timestamps
    else:                           return timestamps[:-1]
def __getTimestampList_byRange_GRID_20Y(intervalID, timestamp_beg, timestamp_end, mrktReg, lastTickInclusive):
    timestamps = list()
    if (mrktReg == None):
        currentTickYear = datetime.fromtimestamp(timestamp_beg, tz = timezone.utc).year
    else:
        mrktRegYear = datetime.fromtimestamp(mrktReg, tz = timezone.utc).year
        currentTickYear = mrktRegYear + int((datetime.fromtimestamp(timestamp_beg, tz = timezone.utc).year-mrktRegYear)/20)*20
    while (True):
        nextYear = currentTickYear+len(timestamps)*20
        nextYear_TS = int(datetime(year = nextYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
        if (nextYear_TS <= timestamp_end): timestamps.append(nextYear_TS)
        else: break
    if (lastTickInclusive == True): return timestamps
    else:                           return timestamps[:-1]
def __getTimestampList_byRange_GRID_1M(intervalID, timestamp_beg, timestamp_end, mrktReg, lastTickInclusive):
    timestamps = list()
    timestamp_dateTime = datetime.fromtimestamp(timestamp_beg, tz = timezone.utc)
    while (True):
        nextMonth = timestamp_dateTime.month+len(timestamps)
        nextMonth_yearDeducted = nextMonth%12
        if (nextMonth_yearDeducted == 0): newMonthDate_year = timestamp_dateTime.year + int(nextMonth/12) - 1; newMonthDate_month = 12
        else:                             newMonthDate_year = timestamp_dateTime.year + int(nextMonth/12);     newMonthDate_month = nextMonth_yearDeducted
        nextTimestamp = int(datetime(year = newMonthDate_year, month = newMonthDate_month, day = 1, tzinfo = timezone.utc).timestamp())
        if (nextTimestamp <= timestamp_end): timestamps.append(nextTimestamp)
        else: break
    if (lastTickInclusive == True): return timestamps
    else:                           return timestamps[:-1]
def __getTimestampList_byRange_GRID_3M(intervalID, timestamp_beg, timestamp_end, mrktReg, lastTickInclusive):
    timestamps = list()
    timestamp_dateTime = datetime.fromtimestamp(timestamp_beg, tz = timezone.utc)
    while (True):
        nextMonth = timestamp_dateTime.month+len(timestamps)*3
        nextMonth_yearDeducted = nextMonth%12
        if (nextMonth_yearDeducted == 0): effectiveYear = timestamp_dateTime.year + int(nextMonth/12) - 1; effectiveMonth = newMonthDate_month = 12
        else:                             effectiveYear = timestamp_dateTime.year + int(nextMonth/12);     effectiveMonth = nextMonth_yearDeducted
        effectiveMonth = int((effectiveMonth-1)/3)*3+1
        nextTimestamp = int(datetime(year = effectiveYear, month = effectiveMonth, day = 1, tzinfo = timezone.utc).timestamp())
        if (nextTimestamp <= timestamp_end): timestamps.append(nextTimestamp)
        else: break
    if (lastTickInclusive == True): return timestamps
    else:                           return timestamps[:-1]
def __getTimestampList_byRange_GRID_6M(intervalID, timestamp_beg, timestamp_end, mrktReg, lastTickInclusive):
    timestamps = list()
    timestamp_dateTime = datetime.fromtimestamp(timestamp_beg, tz = timezone.utc)
    while (True):
        nextMonth = timestamp_dateTime.month+len(timestamps)*6
        nextMonth_yearDeducted = nextMonth%12
        if (nextMonth_yearDeducted == 0): effectiveYear = timestamp_dateTime.year + int(nextMonth/12) - 1; effectiveMonth = newMonthDate_month = 12
        else:                             effectiveYear = timestamp_dateTime.year + int(nextMonth/12);     effectiveMonth = nextMonth_yearDeducted
        effectiveMonth = int((effectiveMonth-1)/6)*6+1
        nextTimestamp = int(datetime(year = effectiveYear, month = effectiveMonth, day = 1, tzinfo = timezone.utc).timestamp())
        if (nextTimestamp <= timestamp_end): timestamps.append(nextTimestamp)
        else: break
    if (lastTickInclusive == True): return timestamps
    else:                           return timestamps[:-1]
def __getTimestampList_byRange_GRID_1W(intervalID, timestamp_beg, timestamp_end, mrktReg, lastTickInclusive):
    timestamp_ISOCalendar_BEG = datetime.fromtimestamp(timestamp_beg, tz = timezone.utc).isocalendar()
    timestamp_ISOCalendar_END = datetime.fromtimestamp(timestamp_end, tz = timezone.utc).isocalendar()
    if ((timestamp_ISOCalendar_BEG.year == 1970) and (timestamp_ISOCalendar_BEG.week == 1)): firstTickTS = 0
    else:                                                                                    firstTickTS = int(datetime.fromisocalendar(year = timestamp_ISOCalendar_BEG.year, week = timestamp_ISOCalendar_BEG.week, day = 1).timestamp() + TIMEZONE_DELTA_SEC)
    if ((timestamp_ISOCalendar_END.year == 1970) and (timestamp_ISOCalendar_END.week == 1)): lastTickTS  = 0
    else:                                                                                    lastTickTS  = int(datetime.fromisocalendar(year = timestamp_ISOCalendar_END.year, week = timestamp_ISOCalendar_END.week, day = 1).timestamp() + TIMEZONE_DELTA_SEC)
    if (lastTickInclusive == True): return list(range(firstTickTS, lastTickTS+1, GRID_INTERVAL_SECs[GRID_INTERVAL_ID_1W]))
    else:                           return list(range(firstTickTS, lastTickTS,   GRID_INTERVAL_SECs[GRID_INTERVAL_ID_1W]))
def __getTimestampList_byRange_GRID_3D(intervalID, timestamp_beg, timestamp_end, mrktReg, lastTickInclusive):
    if (mrktReg == None): 
        firstTickTS = int(timestamp_beg/GRID_INTERVAL_SECs[GRID_INTERVAL_ID_3d])*GRID_INTERVAL_SECs[GRID_INTERVAL_ID_3d]
    else:
        mrktRegFirstDay = int(mrktReg      /86400)*86400
        timestamp_1d    = int(timestamp_beg/86400)*86400
        firstTickTS = (int((timestamp_1d-mrktRegFirstDay)/259200))*259200+mrktRegFirstDay
    lastTickTS  = int(timestamp_end/GRID_INTERVAL_SECs[GRID_INTERVAL_ID_3d])*GRID_INTERVAL_SECs[GRID_INTERVAL_ID_3d]
    if (lastTickInclusive == True): return list(range(firstTickTS, lastTickTS+1, GRID_INTERVAL_SECs[GRID_INTERVAL_ID_3d]))
    else:                           return list(range(firstTickTS, lastTickTS,   GRID_INTERVAL_SECs[GRID_INTERVAL_ID_3d]))
def __getTimestampList_byRange_GRID_ELSE(intervalID, timestamp_beg, timestamp_end, mrktReg, lastTickInclusive):
    firstTickTS = int(timestamp_beg/GRID_INTERVAL_SECs[intervalID])*GRID_INTERVAL_SECs[intervalID]
    lastTickTS  = int(timestamp_end/GRID_INTERVAL_SECs[intervalID])*GRID_INTERVAL_SECs[intervalID]
    if (lastTickInclusive == True): return list(range(firstTickTS, lastTickTS+1, GRID_INTERVAL_SECs[intervalID]))
    else:                           return list(range(firstTickTS, lastTickTS,   GRID_INTERVAL_SECs[intervalID]))

__getTimestampList_byRange_GRID_hashedFunctionRoutine = {GRID_INTERVAL_ID_1Y:  __getTimestampList_byRange_GRID_1Y,
                                                         GRID_INTERVAL_ID_2Y:  __getTimestampList_byRange_GRID_2Y,
                                                         GRID_INTERVAL_ID_5Y:  __getTimestampList_byRange_GRID_5Y,
                                                         GRID_INTERVAL_ID_10Y: __getTimestampList_byRange_GRID_10Y,
                                                         GRID_INTERVAL_ID_20Y: __getTimestampList_byRange_GRID_20Y,
                                                         GRID_INTERVAL_ID_1M:  __getTimestampList_byRange_GRID_1M,
                                                         GRID_INTERVAL_ID_3M:  __getTimestampList_byRange_GRID_3M,
                                                         GRID_INTERVAL_ID_6M:  __getTimestampList_byRange_GRID_6M,
                                                         GRID_INTERVAL_ID_1W:  __getTimestampList_byRange_GRID_1W,
                                                         GRID_INTERVAL_ID_3d:  __getTimestampList_byRange_GRID_3D,
                                                         GRID_INTERVAL_ID_1d:  __getTimestampList_byRange_GRID_ELSE,
                                                         GRID_INTERVAL_ID_12h: __getTimestampList_byRange_GRID_ELSE,
                                                         GRID_INTERVAL_ID_8h:  __getTimestampList_byRange_GRID_ELSE,
                                                         GRID_INTERVAL_ID_6h:  __getTimestampList_byRange_GRID_ELSE,
                                                         GRID_INTERVAL_ID_4h:  __getTimestampList_byRange_GRID_ELSE,
                                                         GRID_INTERVAL_ID_2h:  __getTimestampList_byRange_GRID_ELSE,
                                                         GRID_INTERVAL_ID_1h:  __getTimestampList_byRange_GRID_ELSE,
                                                         GRID_INTERVAL_ID_30m: __getTimestampList_byRange_GRID_ELSE,
                                                         GRID_INTERVAL_ID_15m: __getTimestampList_byRange_GRID_ELSE,
                                                         GRID_INTERVAL_ID_10m: __getTimestampList_byRange_GRID_ELSE,
                                                         GRID_INTERVAL_ID_5m:  __getTimestampList_byRange_GRID_ELSE,
                                                         GRID_INTERVAL_ID_3m:  __getTimestampList_byRange_GRID_ELSE,
                                                         GRID_INTERVAL_ID_1m:  __getTimestampList_byRange_GRID_ELSE}

def getTimestampList_byRange_GRID(intervalID, timestamp_beg, timestamp_end, mrktReg = None, lastTickInclusive = False): return __getTimestampList_byRange_GRID_hashedFunctionRoutine[intervalID](intervalID, timestamp_beg, timestamp_end, mrktReg, lastTickInclusive)
#getTimestampList_byRange_GRID END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



#getNextIntervalTickTimestamp_GRID ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __getNextIntervalTickTimestamp_GRID_1Y(intervalID, timestamp, mrktReg, nTicks):
    timestamp_dateTime = datetime.fromtimestamp(timestamp, tz = timezone.utc)
    nextYear = timestamp_dateTime.year+nTicks
    return int(datetime(year = nextYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
def __getNextIntervalTickTimestamp_GRID_2Y(intervalID, timestamp, mrktReg, nTicks):
    if (mrktReg == None):
        timestamp_dateTime = datetime.fromtimestamp(timestamp, tz = timezone.utc)
        nextYear = timestamp_dateTime.year+nTicks*2
        return int(datetime(year = nextYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
    else:
        mrktRegYear = datetime.fromtimestamp(mrktReg,   tz = timezone.utc).year
        currentYear = datetime.fromtimestamp(timestamp, tz = timezone.utc).year
        effectiveYear = mrktRegYear + (int((currentYear-mrktRegYear)/2)+nTicks)*2
        return int(datetime(year = effectiveYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
def __getNextIntervalTickTimestamp_GRID_5Y(intervalID, timestamp, mrktReg, nTicks):
    if (mrktReg == None):
        timestamp_dateTime = datetime.fromtimestamp(timestamp, tz = timezone.utc)
        nextYear = timestamp_dateTime.year+nTicks*5
        return int(datetime(year = nextYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
    else:
        mrktRegYear = datetime.fromtimestamp(mrktReg,   tz = timezone.utc).year
        currentYear = datetime.fromtimestamp(timestamp, tz = timezone.utc).year
        effectiveYear = mrktRegYear + (int((currentYear-mrktRegYear)/5)+nTicks)*5
        return int(datetime(year = effectiveYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
def __getNextIntervalTickTimestamp_GRID_10Y(intervalID, timestamp, mrktReg, nTicks):
    if (mrktReg == None):
        timestamp_dateTime = datetime.fromtimestamp(timestamp, tz = timezone.utc)
        nextYear = timestamp_dateTime.year+nTicks*10
        return int(datetime(year = nextYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
    else:
        mrktRegYear = datetime.fromtimestamp(mrktReg,   tz = timezone.utc).year
        currentYear = datetime.fromtimestamp(timestamp, tz = timezone.utc).year
        effectiveYear = mrktRegYear + (int((currentYear-mrktRegYear)/10)+nTicks)*10
        return int(datetime(year = effectiveYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
def __getNextIntervalTickTimestamp_GRID_20Y(intervalID, timestamp, mrktReg, nTicks):
    if (mrktReg == None):
        timestamp_dateTime = datetime.fromtimestamp(timestamp, tz = timezone.utc)
        nextYear = timestamp_dateTime.year+nTicks*20
        return int(datetime(year = nextYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
    else:
        mrktRegYear = datetime.fromtimestamp(mrktReg,   tz = timezone.utc).year
        currentYear = datetime.fromtimestamp(timestamp, tz = timezone.utc).year
        effectiveYear = mrktRegYear + (int((currentYear-mrktRegYear)/20)+nTicks)*20
        return int(datetime(year = effectiveYear, month = 1, day = 1, tzinfo = timezone.utc).timestamp())
def __getNextIntervalTickTimestamp_GRID_1M(intervalID, timestamp, mrktReg, nTicks):
    timestamp_dateTime = datetime.fromtimestamp(timestamp, tz = timezone.utc)
    nextMonth = timestamp_dateTime.month+nTicks
    nextMonth_yearDeducted = nextMonth%12
    if (nextMonth_yearDeducted == 0): newMonthDate_year = timestamp_dateTime.year + int(nextMonth/12) - 1; newMonthDate_month = 12
    else:                             newMonthDate_year = timestamp_dateTime.year + int(nextMonth/12);     newMonthDate_month = nextMonth_yearDeducted
    return int(datetime(year = newMonthDate_year, month = newMonthDate_month, day = 1, tzinfo = timezone.utc).timestamp())
def __getNextIntervalTickTimestamp_GRID_3M(intervalID, timestamp, mrktReg, nTicks):
    timestamp_dateTime = datetime.fromtimestamp(timestamp, tz = timezone.utc)
    nextMonth = timestamp_dateTime.month+nTicks*3
    nextMonth_yearDeducted = nextMonth%12
    if (nextMonth_yearDeducted == 0): effectiveYear = timestamp_dateTime.year + int(nextMonth/12) - 1; effectiveMonth = newMonthDate_month = 12
    else:                             effectiveYear = timestamp_dateTime.year + int(nextMonth/12);     effectiveMonth = nextMonth_yearDeducted
    effectiveMonth = int((effectiveMonth-1)/3)*3+1
    return int(datetime(year = effectiveYear, month = effectiveMonth, day = 1, tzinfo = timezone.utc).timestamp())
def __getNextIntervalTickTimestamp_GRID_6M(intervalID, timestamp, mrktReg, nTicks):
    timestamp_dateTime = datetime.fromtimestamp(timestamp, tz = timezone.utc)
    nextMonth = timestamp_dateTime.month+nTicks*6
    nextMonth_yearDeducted = nextMonth%12
    if (nextMonth_yearDeducted == 0): effectiveYear = timestamp_dateTime.year + int(nextMonth/12) - 1; effectiveMonth = newMonthDate_month = 12
    else:                             effectiveYear = timestamp_dateTime.year + int(nextMonth/12);     effectiveMonth = nextMonth_yearDeducted
    effectiveMonth = int((effectiveMonth-1)/6)*6+1
    return int(datetime(year = effectiveYear, month = effectiveMonth, day = 1, tzinfo = timezone.utc).timestamp())
def __getNextIntervalTickTimestamp_GRID_1W(intervalID, timestamp, mrktReg, nTicks):
    timestamp_ISOCalendar = datetime.fromtimestamp(timestamp, tz = timezone.utc).isocalendar()
    return int(datetime.fromisocalendar(year = timestamp_ISOCalendar.year, week = timestamp_ISOCalendar.week, day = 1).timestamp() + TIMEZONE_DELTA_SEC + GRID_INTERVAL_SECs[intervalID]*nTicks)
def __getNextIntervalTickTimestamp_GRID_3D(intervalID, timestamp, mrktReg, nTicks):
    if (mrktReg == None): return (int(timestamp/GRID_INTERVAL_SECs[GRID_INTERVAL_ID_3d])+nTicks)*GRID_INTERVAL_SECs[GRID_INTERVAL_ID_3d]
    else:
        mrktRegFirstDay = int(mrktReg  /86400)*86400
        timestamp_1d    = int(timestamp/86400)*86400
        return (int((timestamp_1d-mrktRegFirstDay)/259200)+nTicks)*259200+mrktRegFirstDay
def __getNextIntervalTickTimestamp_GRID_ELSE(intervalID, timestamp, mrktReg, nTicks):
    return (int(timestamp/GRID_INTERVAL_SECs[intervalID])+nTicks)*GRID_INTERVAL_SECs[intervalID]

__getNextIntervalTickTimestamp_GRID_hashedFunctionRoutine = {GRID_INTERVAL_ID_1Y:  __getNextIntervalTickTimestamp_GRID_1Y,
                                                             GRID_INTERVAL_ID_2Y:  __getNextIntervalTickTimestamp_GRID_2Y,
                                                             GRID_INTERVAL_ID_5Y:  __getNextIntervalTickTimestamp_GRID_5Y,
                                                             GRID_INTERVAL_ID_10Y: __getNextIntervalTickTimestamp_GRID_10Y,
                                                             GRID_INTERVAL_ID_20Y: __getNextIntervalTickTimestamp_GRID_20Y,
                                                             GRID_INTERVAL_ID_1M:  __getNextIntervalTickTimestamp_GRID_1M,
                                                             GRID_INTERVAL_ID_3M:  __getNextIntervalTickTimestamp_GRID_3M,
                                                             GRID_INTERVAL_ID_6M:  __getNextIntervalTickTimestamp_GRID_6M,
                                                             GRID_INTERVAL_ID_1W:  __getNextIntervalTickTimestamp_GRID_1W,
                                                             GRID_INTERVAL_ID_3d:  __getNextIntervalTickTimestamp_GRID_3D,
                                                             GRID_INTERVAL_ID_1d:  __getNextIntervalTickTimestamp_GRID_ELSE,
                                                             GRID_INTERVAL_ID_12h: __getNextIntervalTickTimestamp_GRID_ELSE,
                                                             GRID_INTERVAL_ID_8h:  __getNextIntervalTickTimestamp_GRID_ELSE,
                                                             GRID_INTERVAL_ID_6h:  __getNextIntervalTickTimestamp_GRID_ELSE,
                                                             GRID_INTERVAL_ID_4h:  __getNextIntervalTickTimestamp_GRID_ELSE,
                                                             GRID_INTERVAL_ID_2h:  __getNextIntervalTickTimestamp_GRID_ELSE,
                                                             GRID_INTERVAL_ID_1h:  __getNextIntervalTickTimestamp_GRID_ELSE,
                                                             GRID_INTERVAL_ID_30m: __getNextIntervalTickTimestamp_GRID_ELSE,
                                                             GRID_INTERVAL_ID_15m: __getNextIntervalTickTimestamp_GRID_ELSE,
                                                             GRID_INTERVAL_ID_10m: __getNextIntervalTickTimestamp_GRID_ELSE,
                                                             GRID_INTERVAL_ID_5m:  __getNextIntervalTickTimestamp_GRID_ELSE,
                                                             GRID_INTERVAL_ID_3m:  __getNextIntervalTickTimestamp_GRID_ELSE,
                                                             GRID_INTERVAL_ID_1m:  __getNextIntervalTickTimestamp_GRID_ELSE}

def getNextIntervalTickTimestamp_GRID(intervalID, timestamp, mrktReg = None, nTicks = 1): return __getNextIntervalTickTimestamp_GRID_hashedFunctionRoutine[intervalID](intervalID, timestamp, mrktReg, nTicks)
#getNextIntervalTickTimestamp_GRID END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Return if the corresponding timestamp is the beginning of a new month
def isNewMonth(timestamp):
    timestamp_dateTime = datetime.fromtimestamp(timestamp, tz = timezone.utc)
    return (timestamp_dateTime.day == 1 and timestamp_dateTime.hour == 0 and timestamp_dateTime.minute == 0 and timestamp_dateTime.second == 0 and timestamp_dateTime.microsecond == 0)

def simpleValueFormatter(value, precision = 3):
    value_abs = abs(value)
    if   (value_abs < 1e-15): return "{:s}a".format(__floatToString_hasedFunctionRoutine[precision](value*1e18, comma = False))
    elif (value_abs < 1e-12): return "{:s}f".format(__floatToString_hasedFunctionRoutine[precision](value*1e15, comma = False))
    elif (value_abs < 1e-9):  return "{:s}p".format(__floatToString_hasedFunctionRoutine[precision](value*1e12, comma = False))
    elif (value_abs < 1e-6):  return "{:s}n".format(__floatToString_hasedFunctionRoutine[precision](value*1e9,  comma = False))
    elif (value_abs < 1e-3):  return "{:s}u".format(__floatToString_hasedFunctionRoutine[precision](value*1e6,  comma = False))
    elif (value_abs < 1e0):   return "{:s}m".format(__floatToString_hasedFunctionRoutine[precision](value*1e3,  comma = False))
    elif (value_abs < 1e3):   return "{:s}".format(__floatToString_hasedFunctionRoutine[precision](value,       comma = False))
    elif (value_abs < 1e6):   return "{:s}K".format(__floatToString_hasedFunctionRoutine[precision](value/1e3,  comma = False))
    elif (value_abs < 1e9):   return "{:s}M".format(__floatToString_hasedFunctionRoutine[precision](value/1e6,  comma = False))
    elif (value_abs < 1e12):  return "{:s}B".format(__floatToString_hasedFunctionRoutine[precision](value/1e9,  comma = False))
    elif (value_abs < 1e15):  return "{:s}T".format(__floatToString_hasedFunctionRoutine[precision](value/1e12, comma = False))
    elif (value_abs < 1e18):  return "{:s}Q".format(__floatToString_hasedFunctionRoutine[precision](value/1e15, comma = False))
    else: return "SVF Not Supported"

def diskSpaceFormatter(value):
    if   (value < pow(1024, 1)): return "{:.3f} Bytes".format(value)
    elif (value < pow(1024, 2)): return "{:.3f} KB".format(value/pow(1024, 1))
    elif (value < pow(1024, 3)): return "{:.3f} MB".format(value/pow(1024, 2))
    elif (value < pow(1024, 4)): return "{:.3f} GB".format(value/pow(1024, 3))
    elif (value < pow(1024, 5)): return "{:.3f} TB".format(value/pow(1024, 4))
    elif (value < pow(1024, 6)): return "{:.3f} PB".format(value/pow(1024, 5))
    else: return "DSF Not Supported"
    
def timeStringFormatter(time_seconds):
    if   (time_seconds < 60):    return "00:{:02d}".format(time_seconds)                                                                                                                                  #Less than a minute
    elif (time_seconds < 3600):  return "{:02d}:{:02d}".format(int(time_seconds/60), time_seconds%60)                                                                                                     #Less than an hour
    elif (time_seconds < 86400): return "{:02d}:{:02d}:{:02d}".format(int(time_seconds/3600), int((time_seconds-int(time_seconds/3600)*3600)/60), time_seconds%60)                                        #Less than a day
    else: return "{:d}:{:02d}:{:02d}:{:02d}".format(int(time_seconds/86400), int((time_seconds-int(time_seconds/86400)*86400)/3600), int((time_seconds-int(time_seconds/3600)*3600)/60), time_seconds%60) #More than a day

def __floatToString_precision0(number, comma):  
    if comma: return f"{number:,.0f}"
    else:     return f"{number:.0f}"
def __floatToString_precision1(number, comma):  
    if comma: return f"{number:,.1f}"
    else:     return f"{number:.1f}"
def __floatToString_precision2(number, comma):  
    if comma: return f"{number:,.2f}"
    else:     return f"{number:.2f}"
def __floatToString_precision3(number, comma):  
    if comma: return f"{number:,.3f}"
    else:     return f"{number:.3f}"
def __floatToString_precision4(number, comma):  
    if comma: return f"{number:,.4f}"
    else:     return f"{number:.4f}"
def __floatToString_precision5(number, comma):  
    if comma: return f"{number:,.5f}"
    else:     return f"{number:.5f}"
def __floatToString_precision6(number, comma):  
    if comma: return f"{number:,.6f}"
    else:     return f"{number:.6f}"
def __floatToString_precision7(number, comma):  
    if comma: return f"{number:,.7f}"
    else:     return f"{number:.7f}"
def __floatToString_precision8(number, comma):  
    if comma: return f"{number:,.8f}"
    else:     return f"{number:.8f}"
def __floatToString_precision9(number, comma):  
    if comma: return f"{number:,.9f}"
    else:     return f"{number:.9f}"
def __floatToString_precision10(number, comma): 
    if comma: return f"{number:,.10f}"
    else:     return f"{number:.10f}"
def __floatToString_precision11(number, comma): 
    if comma: return f"{number:,.11f}"
    else:     return f"{number:.11f}"
def __floatToString_precision12(number, comma): 
    if comma: return f"{number:,.12f}"
    else:     return f"{number:.12f}"
def __floatToString_precision13(number, comma): 
    if comma: return f"{number:,.13f}"
    else:     return f"{number:.13f}"
def __floatToString_precision14(number, comma): 
    if comma: return f"{number:,.14f}"
    else:     return f"{number:.14f}"
def __floatToString_precision15(number, comma): 
    if comma: return f"{number:,.15f}"
    else:     return f"{number:.15f}"
def __floatToString_precision16(number, comma): 
    if comma: return f"{number:,.16f}"
    else:     return f"{number:.16f}"
def __floatToString_precision17(number, comma): 
    if comma: return f"{number:,.17f}"
    else:     return f"{number:.17f}"
def __floatToString_precision18(number, comma): 
    if comma: return f"{number:,.18f}"
    else:     return f"{number:.18f}"
def __floatToString_precision19(number, comma): 
    if comma: return f"{number:,.19f}"
    else:     return f"{number:.19f}"
__floatToString_hasedFunctionRoutine = {0:  __floatToString_precision0,
                                        1:  __floatToString_precision1,
                                        2:  __floatToString_precision2,
                                        3:  __floatToString_precision3,
                                        4:  __floatToString_precision4,
                                        5:  __floatToString_precision5,
                                        6:  __floatToString_precision6,
                                        7:  __floatToString_precision7,
                                        8:  __floatToString_precision8,
                                        9:  __floatToString_precision9,
                                        10: __floatToString_precision10,
                                        11: __floatToString_precision11,
                                        12: __floatToString_precision12,
                                        13: __floatToString_precision13,
                                        14: __floatToString_precision14,
                                        15: __floatToString_precision15,
                                        16: __floatToString_precision16,
                                        17: __floatToString_precision17,
                                        18: __floatToString_precision18,
                                        19: __floatToString_precision19}
def floatToString(number, precision, comma = True): return __floatToString_hasedFunctionRoutine[precision](number, comma)

def formatInvalidLinesReportToString(invalidLines):
    repString = ""
    for aCode, causes in invalidLines.items():
        repString += f"\n * {aCode}"
        for casue in causes: repString += f"\n  * {casue}"
    return repString