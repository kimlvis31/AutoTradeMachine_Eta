#ATM Modules
from .chart_drawer import (chartDrawer,
                                     _NMAXLINES,
                                     _MITYPES,
                                     _SITYPES)
import auxiliaries
import analyzers
import ipc
import neural_networks
import constants

#Python Modules
import time
import termcolor
import torch
import gc

#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = ipc._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = ipc._FAR_INVALIDFUNCTIONID

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

COMMONDATAINDEXES = {'openTime':  {'kline': KLINDEX_OPENTIME,  'depth': DEPTHINDEX_OPENTIME,  'aggTrade': ATINDEX_OPENTIME},
                     'closeTime': {'kline': KLINDEX_CLOSETIME, 'depth': DEPTHINDEX_CLOSETIME, 'aggTrade': ATINDEX_CLOSETIME},
                     'closed':    {'kline': KLINDEX_CLOSED,    'depth': DEPTHINDEX_CLOSED,    'aggTrade': ATINDEX_CLOSED},
                     'source':    {'kline': KLINDEX_SOURCE,    'depth': DEPTHINDEX_SOURCE,    'aggTrade': ATINDEX_SOURCE}}

KLINTERVAL   = constants.KLINTERVAL
KLINTERVAL_S = constants.KLINTERVAL_S

_DUMMYFRAMES = {'kline':    (None, None, None, None, None, None, None, None, None,                   True, FORMATTEDDATATYPE_DUMMY),
                'depth':    (None, None, None, None, None, None, None, None, None, None, None, None, True, FORMATTEDDATATYPE_DUMMY),
                'aggTrade': (None, None, None, None, None, None,                                     True, FORMATTEDDATATYPE_DUMMY)}

_DATAFETCHCHUNKSIZE = 43_200

_ANALYSIS_GENERATIONORDER = analyzers.ANALYSIS_GENERATIONORDER
_TIMELIMIT_DATAPROCESS_NS = 100e6

_TYPEMODE_PENDING                = 0
_TYPEMODE_FETCHINGTRADELOGS      = 1
_TYPEMODE_FETCHINGNEURALNETWORKS = 2
_TYPEMODE_FETCHINGMARKETDATA     = 3
_TYPEMODE_REGENERATING           = 4
_TYPEMODE_ERROR                  = 5

#Chart Drawer TL Viewer Subclass
class chartDrawer_tlViewer(chartDrawer):
    def __init__(self, **kwargs):
        self.chartDrawerType = "TLVIEWER"
        super().__init__(**kwargs)
        self.__typeInit()
        self.setTarget(target = None)

    def __typeInit(self):
        #[1]: GUIOs Deactivation
        guios_MAIN    = self.settingsSubPages['MAIN'].GUIOs
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

        #MAIN
        guios_MAIN["ANALYZER_ANALYSISRANGEBEG_RANGEINPUT"].deactivate()
        guios_MAIN["ANALYZER_ANALYSISRANGEEND_RANGEINPUT"].deactivate()
        guios_MAIN["ANALYZER_STARTANALYSIS_BUTTON"].deactivate()

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

        guios_MAIN["DEPTHOVERLAYCOLOR_TARGETSELECTION"].deactivate()
        guios_MAIN["DEPTHOVERLAYCOLOR_APPLYCOLOR"].deactivate()
        guios_MAIN["DEPTHOVERLAYCOLOR_R_SLIDER"].deactivate()
        guios_MAIN["DEPTHOVERLAYCOLOR_G_SLIDER"].deactivate()
        guios_MAIN["DEPTHOVERLAYCOLOR_B_SLIDER"].deactivate()
        guios_MAIN["DEPTHOVERLAYCOLOR_A_SLIDER"].deactivate()
        guios_MAIN["DEPTHOVERLAYDISPLAY_SWITCH"].deactivate()
        guios_MAIN["DEPTHOVERLAY_APPLYNEWSETTINGS"].deactivate()

        #[2]: Type Unique Variables
        self.__mode           = None
        self.__simulationCode = None
        self.__simulation     = None
        self.__initializeDataControl()
        self.__initializeAnalysisControl()

    def __initializeDataControl(self):
        self.__tradeLogFetchRID       = None
        self.__fetchRequests          = dict()
        self.__aggregators            = {'kline':    analyzers.aggregator_kline,
                                         'depth':    analyzers.aggregator_depth,
                                         'aggTrade': analyzers.aggregator_aggTrade}
        self.__lastClosedAggregations = {self.intervalID: {target: dict() for target in ('kline', 'depth', 'aggTrade')}}

    def __initializeAnalysisControl(self):
        self.__neuralNetworkInstances                = dict()
        self.__neuralNetworkConnectionDataRequestIDs = dict()
        self.__analysisToProcess_Sorted = dict()
        self.__analysisKwargs           = dict()
        self.__regeneration             = dict()

    def setTarget(self, target):
        #[1]: Target Read
        cClear = (self.__simulationCode is not None)
        if target is None:
            self.__simulationCode = None
            self.__simulation     = None
            self.currencySymbol   = None
            self.currencyInfo     = None
        else:
            simCode, symbol = target
            self.__simulationCode = simCode
            self.__simulation     = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATIONS', simCode))
            self.currencySymbol   = symbol
            self.currencyInfo     = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', self.currencySymbol))
        if self.__simulationCode is None: self._updateTargetText(text = "-")
        else:                             self._updateTargetText(text = f"{self.__simulationCode} [{self.currencySymbol}]")
            
        #[2]: Type Mode & Loading Cover
        self.__mode = _TYPEMODE_PENDING
        self._setLoadingCover(show = False, text = None, gaugeValue = None)

        #[3]: Data
        self._clearData()
        self._clearDrawers()
        self.__initializeDataControl()
        self.__initializeAnalysisControl()
        if cClear:
            gc.collect()
            torch.cuda.empty_cache()

        #[4]: Initialize Highlighters and Descriptors
        self._clearHighlightsAndDescriptors()

        #[5]: View Control
        #---[5-1]: Horizontal View Range Parameters Setup
        self._setHVRParams()
        #---[5-2]: RCLCGs Reset
        self._initializeRCLCGs('KLINESPRICE')
        for sivCode in self.displayBox_graphics_visibleSIViewers: self._initializeSIViewer(sivCode)
        #---[5-3] Horizontal View Range Update
        self.horizontalViewRange_magnification = 80
        if self.__simulation is None:
            hvr_new_end = round(time.time()+self.expectedKlineTemporalWidth*5)
            hvr_new_beg = round(hvr_new_end-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
        else:
            sRange = self.__simulation['simulationRange']
            hvr_new_beg = round(sRange[0]-self.expectedKlineTemporalWidth*5)
            hvr_new_end = round(hvr_new_beg+(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
        hvr_new = [hvr_new_beg, hvr_new_end]
        tz_rev  = -self.timezoneDelta
        if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]
        self.horizontalViewRange = hvr_new
        self._onHViewRangeUpdate(1)
        #---[5-4]: Vertical View Range Reset
        self._editVVR_toExtremaCenter('KLINESPRICE')
        for sivCode in self.displayBox_graphics_visibleSIViewers: self._editVVR_toExtremaCenter(sivCode)

        #[6]: Construct Analysis Parameters
        aParams       = {self.intervalID: dict()}
        func_ccapfcac = analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration
        func_filrts   = auxiliaries.formatInvalidLinesReportToString
        invalidFound  = False
        if self.__simulation is not None:
            cacCode = self.__simulation['positions'][self.currencySymbol]['currencyAnalysisConfigurationCode']
            cac     = self.__simulation['currencyAnalysisConfigurations'][cacCode]
            for iID, cac_iID in cac.items():
                aParams_iID, invalidLines = func_ccapfcac(currencyAnalysisConfiguration = cac_iID)
                if invalidLines:
                    invalidFound     = True
                    invalidLines_str = func_filrts(invalidLines = invalidLines)
                    print(termcolor.colored((f"[GUI-{self.name}] Invalid Lines Detected In Interval '{iID}' While Attempting To Construct Analysis Parameters From The Currency Analysis Configuration '{cacCode}'."+invalidLines_str), 
                                            'light_red'))
                elif aParams_iID:
                    aParams[iID] = aParams_iID
        self.analysisParams = aParams
        if invalidFound:
            self.__mode = _TYPEMODE_ERROR
            self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:ANALYSISPARAMETERSCONSTRUCTIONFAILED'), gaugeValue = None)

        #[7]: Data Formatting & Analysis Preparation
        if self.__simulation is not None:
            sRange     = self.__simulation['simulationRange']
            drs        = self.__simulation['positions'][self.currencySymbol]['dataRanges']
            dAgg       = self._data_agg
            dTSs       = self._data_timestamps
            lcas       = self.__lastClosedAggregations
            atp_sorted = self.__analysisToProcess_Sorted
            aKwargs    = self.__analysisKwargs
            regen      = self.__regeneration
            func_gnitt = auxiliaries.getNextIntervalTickTimestamp
            #[7-1]: Regeneration Range
            drs_min = None
            drs_max = None
            for t in ('kline', 'depth', 'aggTrade'):
                drs_t       = drs[t]
                drs_t_inSim = [dr for dr in drs_t if sRange[0] <= dr[1] and dr[0] <= sRange[1]] if drs_t else []
                if not drs_t_inSim:
                    continue
                drs_t_inSim_min = drs_t_inSim[0][0]
                drs_t_inSim_max = drs_t_inSim[-1][1]
                if drs_min is None or drs_t_inSim_min < drs_min: drs_min = drs_t_inSim_min
                if drs_max is None or drs_max < drs_t_inSim_max: drs_max = drs_t_inSim_max
            if drs_min is None or drs_max is None:
                regenBeg = None
                regenEnd = None
            else:
                regenBeg = func_gnitt(intervalID = KLINTERVAL, timestamp = max(drs_min, sRange[0]), nTicks = 0)
                regenEnd = func_gnitt(intervalID = KLINTERVAL, timestamp = min(drs_max, sRange[1]), nTicks = 1)-1
            regen['begin'] = regenBeg
            regen['last']  = regenEnd
            #[7-2]: Data Formatting
            for iID, aParams_iID in aParams.items():
                #[7-1]: Data
                dAgg[iID] = {target: dict() for target in ('kline', 'depth', 'aggTrade')}
                dTSs[iID] = {target: list() for target in ('kline', 'depth', 'aggTrade')}
                lcas[iID] = {target: dict() for target in ('kline', 'depth', 'aggTrade')}
                for aCode in aParams_iID:
                    dAgg[iID][aCode] = dict()
                #[7-2]: Analysis
                atp_sorted[iID] = [(aType, aCode) for aType in _ANALYSIS_GENERATIONORDER for aCode in aParams_iID if aCode[:len(aType)] == aType]
                aKwargs[iID]    = {'intervalID':     iID,
                                   'precisions':     self.currencyInfo['precisions'],
                                   'klines':         dAgg[iID]['kline'],
                                   'depths':         dAgg[iID]['depth'],
                                   'aggTrades':      dAgg[iID]['aggTrade'],
                                   'neuralNetworks': self.__neuralNetworkInstances}
                #[7-3]: Regeneration
                regen[iID] = regenBeg

        #[8]: Aggregation Interval ID Switches
        abp_GUIOs = self.auxBarPage.GUIOs
        aux       = auxiliaries
        intervalID = None
        for iID in (aux.KLINE_INTERVAL_ID_1m,
                    aux.KLINE_INTERVAL_ID_3m,
                    aux.KLINE_INTERVAL_ID_5m,
                    aux.KLINE_INTERVAL_ID_15m,
                    aux.KLINE_INTERVAL_ID_30m,
                    aux.KLINE_INTERVAL_ID_1h,
                    aux.KLINE_INTERVAL_ID_2h,
                    aux.KLINE_INTERVAL_ID_4h,
                    aux.KLINE_INTERVAL_ID_6h,
                    aux.KLINE_INTERVAL_ID_8h,
                    aux.KLINE_INTERVAL_ID_12h,
                    aux.KLINE_INTERVAL_ID_1d,
                    aux.KLINE_INTERVAL_ID_3d,
                    aux.KLINE_INTERVAL_ID_1W,
                    aux.KLINE_INTERVAL_ID_1M,):
            aiSwitch = abp_GUIOs[f'AGGINTERVAL_{iID}']
            if iID in aParams: aiSwitch.activate()
            else:              aiSwitch.deactivate()
            aiSwitch.setStatus(status = False, callStatusUpdateFunction = False)
            if intervalID is None and iID in aParams: intervalID = iID
        if intervalID is None: intervalID = aux.KLINE_INTERVAL_ID_1m
        self.intervalID = intervalID
        abp_GUIOs[f'AGGINTERVAL_{intervalID}'].setStatus(status = True, callStatusUpdateFunction = True)

        #[9]: SI Type Analysis Codes
        self._updateSITypeAnalysisCodes()

        #[10]: Trade Log Fetch Request Dispatch
        if self.__simulationCode is not None:
            self.__sendTradeLogsFetchRequest()
    
    def _process_typeUnique(self, mei_beg):
        #[1]: Mode Check
        if self.__mode != _TYPEMODE_REGENERATING:
            return False
        
        #[2]: Regenerating
        rGen        = self.__regeneration
        rGen_target = rGen[self.intervalID]
        rGen_begin  = rGen['begin']
        rGen_last   = rGen['last']
        if rGen_target is not None:
            func_gnitt = auxiliaries.getNextIntervalTickTimestamp
            func_rGen  = self.__regenerateData
            t_begin_ns   = time.perf_counter_ns()
            t_elapsed_ns = 0
            while rGen_target <= rGen_last and t_elapsed_ns < _TIMELIMIT_DATAPROCESS_NS:
                #[2-1]: Perform Analysis & Timer Update
                func_rGen(atTS = rGen_target)
                t_elapsed_ns = time.perf_counter_ns()-t_begin_ns
                #[2-2]: Next Analysis Target & Completion Update
                rGen_target = func_gnitt(intervalID = KLINTERVAL, timestamp = rGen_target, nTicks = 1)
            rGen[self.intervalID] = rGen_target

        #[3]: Loading Cover Update
        if rGen_target is None:
            completion = 1
        else:
            completion = min(round(((rGen_target-1)-rGen_begin+1)/(rGen_last-rGen_begin+1), 5), 1.0)
            self._setLoadingCover(show       = True, 
                                  text       = self.visualManager.getTextPack('GUIO_CHARTDRAWER:REGENERATINGCHARTDATA'), 
                                  gaugeValue = completion*100)
        
        #[4]: Completion Check
        if rGen_target is None or rGen_last < rGen_target:
            self.__onRegenerationComplete()
            return False
        return True
    
    def __sendTradeLogsFetchRequest(self):
        #[1]: Fetch Request Dispatch
        self.__tradeLogFetchRID = self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                                    functionID     = 'fetchSimulationTradeLogs', 
                                                    functionParams = {'simulationCode': self.__simulationCode}, 
                                                    farrHandler    = self.__onTradeLogFetchResponse_FARR)
        
        #[2]: Mode & Loading Cover Update
        self.__mode = _TYPEMODE_FETCHINGTRADELOGS
        self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:FETCHINGTRADELOGDATA'), gaugeValue = None)

    def __onTradeLogFetchResponse_FARR(self, responder, requestID, functionResult):
        #[1]: Responder Check
        if responder != 'DATAMANAGER':
            return

        #[2]: Mode Check
        if self.__mode != _TYPEMODE_FETCHINGTRADELOGS or self.__mode == _TYPEMODE_ERROR:
            return

        #[3]: Result Read
        result         = functionResult['result']
        simulationCode = functionResult['simulationCode']
        tradeLogs      = functionResult['tradeLogs']
        failureType    = functionResult['failureType']

        #[4]: Simulation Code & Request ID Check
        if simulationCode != self.__simulationCode:   return
        if requestID      != self.__tradeLogFetchRID: return
        self.__tradeLogFetchRID = None

        #[5]: Failure Handling
        if not result:
            print(termcolor.colored(f"[GUI-{self.name}] Simulation '{simulationCode}' Trade Logs Fetch Failed.\n * {failureType}", 'light_red'))
            self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:TRADELOGDATAFETCHFAILED'), gaugeValue = None)
            return

        #[6]: Trade Logs
        #---[6-1]: Logs Save
        cSymbol  = self.currencySymbol
        dRaw_tls = dict()
        for tradeLog in tradeLogs:
            if tradeLog['positionSymbol'] != cSymbol: 
                continue
            tlTS    = tradeLog['timestamp']
            dRaw_tl = dRaw_tls.get(tlTS, None)
            if dRaw_tl is None:
                dRaw_tl = {'logs':          [tradeLog,],
                           'totalQuantity': tradeLog['totalQuantity'],
                           'entryPrice':    tradeLog['entryPrice']}
                dRaw_tls[tlTS] = dRaw_tl
            else:
                dRaw_tl['logs'].append(tradeLog)
                dRaw_tl['totalQuantity'] = tradeLog['totalQuantity']
                dRaw_tl['entryPrice']    = tradeLog['entryPrice']
        #---[6-2]: Dummy Filling
        sRange       = self.__simulation['simulationRange']
        lastPosition = None
        for tlTS in auxiliaries.getTimestampList_byRange(intervalID        = KLINTERVAL,
                                                                timestamp_beg     = sRange[0],
                                                                timestamp_end     = sRange[1],
                                                                lastTickInclusive = True):
            dRaw_tl = dRaw_tls.get(tlTS, None)
            if dRaw_tl is None:
                if lastPosition is None:
                    tq = None
                    ep = None
                else:
                    tq = lastPosition['totalQuantity']
                    ep = lastPosition['entryPrice']
                dRaw_tl = {'logs':          [],
                           'totalQuantity': tq,
                           'entryPrice':    ep}
                dRaw_tls[tlTS] = dRaw_tl
            else:
                lastPosition = {'totalQuantity': dRaw_tl['totalQuantity'],
                                'entryPrice':    dRaw_tl['entryPrice']}
        #---[6-3]: Finally
        self._data_raw['tradeLog'] = dRaw_tls
            
        #[7]: Send Neural Network Connections Data Requests
        self.__sendNeuralNetworkConnectionsDataRequest()
    
    def __sendNeuralNetworkConnectionsDataRequest(self):
        #[1]: Instances
        sim     = self.__simulation
        cacCode = sim['positions'][self.currencySymbol]['currencyAnalysisConfigurationCode']
        cac     = sim['currencyAnalysisConfigurations'][cacCode]
        nns       = self.__neuralNetworkInstances
        nncd_rIDs = self.__neuralNetworkConnectionDataRequestIDs

        #[2]: NN Codes Collection
        nnCodes = set()
        for cac_iID in cac.values():
            if not cac_iID['NNA_Master']:
                continue
            for lIdx in range (_NMAXLINES['NNA']):
                lActive = cac_iID[f'NNA_{lIdx}_LineActive']
                nnCode  = cac_iID[f'NNA_{lIdx}_NeuralNetworkCode']
                if not lActive:    continue
                if nnCode is None: continue
                nnCodes.add(nnCode)
        if not nnCodes:
            self.__sendMarketDataFetchRequests()
            return

        #[3]: Requests Dispatch
        for nn_code in nnCodes:
            nncd_rID = self.ipcA.sendFAR(targetProcess = "NEURALNETWORKMANAGER",
                                        functionID     = 'getNeuralNetworkConnections',
                                        functionParams = {'neuralNetworkCode': nn_code},
                                        farrHandler    = self.__onNeuralNetworkConnectionsDataRequestResponse_FARR)
            nns[nn_code]        = None
            nncd_rIDs[nncd_rID] = nn_code

        #[4]: Mode & Loading Cover Update
        self.__mode = _TYPEMODE_FETCHINGNEURALNETWORKS
        self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:LOADINGNEURALNETWORKCONNECTIONSDATA'), gaugeValue = None)

    def __onNeuralNetworkConnectionsDataRequestResponse_FARR(self, responder, requestID, functionResult):
        #[1]: Instances
        nns       = self.__neuralNetworkInstances
        nncd_rIDs = self.__neuralNetworkConnectionDataRequestIDs

        #[2]: Source Validity Check
        if responder != 'NEURALNETWORKMANAGER': return
        if requestID not in nncd_rIDs:          return

        #[3]: Mode Check
        if self.__mode != _TYPEMODE_FETCHINGNEURALNETWORKS or self.__mode == _TYPEMODE_ERROR:
            return

        #[4]: RID Removal
        nnCode = nncd_rIDs.pop(requestID)

        #[5]: Result Handling
        if functionResult is not None:
            nKlines      = functionResult['nKlines']
            hiddenLayers = functionResult['hiddenLayers']
            outputLayer  = functionResult['outputLayer']
            connections  = functionResult['connections']
            nn = neural_networks.neuralNetwork_MLP(nKlines      = nKlines, 
                                                         hiddenLayers = hiddenLayers, 
                                                         outputLayer  = outputLayer, 
                                                         device       = 'cpu')
            nn.importConnectionsData(connections = connections)
            nn.setEvaluationMode()
            nns[nnCode] = nn

        #[6]: Request Results Check
        if not nncd_rIDs:
            if all(nns[nnCode] is not None for nnCode in nns):
                self.__sendMarketDataFetchRequests()
            else:
                self.__mode = _TYPEMODE_ERROR
                self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:NEURALNETWORKCONNECTIONSDATAREQUESTFAILED'), gaugeValue = None)
                eMsg = f"[GUI-{self.name}] The Following Neural Network Models Could Not Be Loaded"
                for nnCode in (nnCode for nnCode, nn in nns.items() if nn is None): eMsg += f"\n * '{nnCode}'"
                print(termcolor.colored(eMsg, 'light_red'))
    
    def __sendMarketDataFetchRequests(self):
        #[1]: Instances
        sim     = self.__simulation
        sRange  = sim['simulationRange']
        cSymbol = self.currencySymbol
        frs     = self.__fetchRequests
        drs     = sim['positions'][cSymbol]['dataRanges']
        func_sendFAR = self.ipcA.sendFAR
        func_omdfrr  = self.__onMarketDataFetchRequestResponse_FARR
        func_gnitt   = auxiliaries.getNextIntervalTickTimestamp

        #[2]: Requests Dispatch
        for target in ('kline', 'depth', 'aggTrade'):
            if not drs[target]:
                continue
            for dr_beg, dr_end in drs[target]:
                overlap_beg = max(dr_beg, sRange[0])
                overlap_end = min(dr_end, sRange[1])
                if overlap_beg > overlap_end:
                    continue
                chunkBeg = overlap_beg
                while chunkBeg <= overlap_end:
                    chunkEnd_max = func_gnitt(intervalID = KLINTERVAL, timestamp = chunkBeg, nTicks = _DATAFETCHCHUNKSIZE)-1
                    chunkEnd_eff = min(chunkEnd_max, overlap_end)
                    rID = func_sendFAR(targetProcess  = 'DATAMANAGER',
                                       functionID     = 'fetchMarketData',
                                       functionParams = {'symbol':     cSymbol,
                                                         'target':     target,
                                                         'fetchRange': (chunkBeg, chunkEnd_eff)},
                                       farrHandler    = func_omdfrr)
                    frs[rID] = {'target':            target,
                                'fetchRequestRange': (chunkBeg, chunkEnd_eff),
                                'fetchedRange':      None,
                                'complete':          False}
                    chunkBeg = chunkEnd_eff+1

        #[3]: Mode & Loading Cover Update
        if frs:
            self.__mode = _TYPEMODE_FETCHINGMARKETDATA
            self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:FETCHINGMARKETDATA'), gaugeValue = None)
        else:
            self.__mode = _TYPEMODE_REGENERATING
            self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:REGENERATINGCHARTDATA'), gaugeValue = 0)

    def __onMarketDataFetchRequestResponse_FARR(self, responder, requestID, functionResult):
        #[1]: Instances
        fr_result     = functionResult['result']
        fr_data       = functionResult['data']
        fr_fetchRange = functionResult.get('fetchRange', None)

        #[2]: Mode Check
        if self.__mode != _TYPEMODE_FETCHINGMARKETDATA or self.__mode == _TYPEMODE_ERROR:
            return

        #[3]: Request ID Check
        fReq = self.__fetchRequests.get(requestID, None)
        if fReq is None:
            return
        target = fReq['target']

        #[4]: Result Check
        if fr_result != 'SDF':
            self.__mode = _TYPEMODE_ERROR
            self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:MARKETDATAFETCHFAILED'), gaugeValue = None)
            print(termcolor.colored(f"[GUI-{self.name}] Market Data Fetch Error Occurred: {fr_result}", 
                                    'light_red'))
            return

        #[5]: Data Record
        dRaw_target   = self._data_raw[target]
        dIdx_openTime = COMMONDATAINDEXES['openTime'][target]
        for dl in fr_data:
            dRaw_target[dl[dIdx_openTime]] = dl

        #[6]: Completion Check & Fetch Continuation
        fReq['complete']     = True
        fReq['fetchedRange'] = [fr_fetchRange[0], fr_fetchRange[1]]

        #[7]: Status Control
        self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:FETCHINGMARKETDATA'), gaugeValue = self.__computeFetchCompletion())
        if all(_fReq['complete'] for _fReq in self.__fetchRequests.values()):
            self.__onDataFetchComplete()

    def __computeFetchCompletion(self):
        if not self.__fetchRequests:
            return 100.0
        frrWidth_sum = 0
        frWidth_sum  = 0
        for fReq in self.__fetchRequests.values():
            frr = fReq['fetchRequestRange']
            fr  = fReq['fetchedRange']
            frrWidth_sum += (frr[1]-frr[0]+1)
            if fr is not None: frWidth_sum += (fr[1]-fr[0]+1)
        return frWidth_sum/frrWidth_sum*100

    def __onDataFetchComplete(self):
        #[1]: Mode Check
        if self.__mode != _TYPEMODE_FETCHINGMARKETDATA or self.__mode == _TYPEMODE_ERROR:
            return

        #[2]: Clear Fetch Requests
        self.__fetchRequests.clear()

        #[3]: Dummy Filling
        sim        = self.__simulation
        cSymbol    = self.currencySymbol
        dRaw       = self._data_raw
        regen      = self.__regeneration
        regenBeg   = regen['begin']
        regenEnd   = regen['last']
        drs        = sim['positions'][cSymbol]['dataRanges']
        func_gnitt = auxiliaries.getNextIntervalTickTimestamp
        for target in ('kline', 'depth', 'aggTrade'):
            drs_target  = drs[target]
            dRaw_target = dRaw[target]
            #[3-1]: Gaps Determination
            if not drs_target:
                gaps = [(regenBeg, regenEnd)]
            else:
                gaps = []
                #[3-1-1]: Simulation Range Begin - First Data Range Gap
                if regenBeg <= drs_target[0][0]-1:
                    gaps.append((regenBeg, drs_target[0][0]-1))
                #[3-1-2]: Data Ranges Gap
                for i in range(len(drs_target)-1):
                    gap_beg = drs_target[i][1]+1
                    gap_end = drs_target[i+1][0]-1
                    if gap_beg <= gap_end:
                        gaps.append((gap_beg, gap_end))
                #[3-1-3]: Last Data Range - Simulation Range End Gap
                if drs_target[-1][1]+1 <= regenEnd:
                    gaps.append((drs_target[-1][1]+1, regenEnd))
            #[3-2]: Gaps Filling
            for gap_beg, gap_end in gaps:
                ts = func_gnitt(intervalID = KLINTERVAL, timestamp = gap_beg, nTicks = 0)
                while ts <= gap_end:
                    ts_close = func_gnitt(intervalID = KLINTERVAL, timestamp = ts, nTicks = 1)-1
                    dRaw_target[ts] = (ts, ts_close) + _DUMMYFRAMES[target]
                    ts = func_gnitt(intervalID = KLINTERVAL, timestamp = ts, nTicks = 1)

        #[4]: Currency Analysis Configuration Read
        cacCode = self.__simulation['positions'][self.currencySymbol]['currencyAnalysisConfigurationCode']
        cac_iID = self.__simulation['currencyAnalysisConfigurations'][cacCode][self.intervalID]
        self._readCurrencyAnalysisConfiguration(currencyAnalysisConfiguration = cac_iID)

        #[5]: Mode & Loading Cover Update
        self.__mode = _TYPEMODE_REGENERATING
        self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:REGENERATINGCHARTDATA'), gaugeValue = 0)

    def __regenerateData(self, atTS):
        #[1]: Instances
        iID                = self.intervalID
        dRaw               = self._data_raw
        dAgg_iID           = self._data_agg[iID]
        dTSs_iID           = self._data_timestamps[iID]
        lcas_iID           = self.__lastClosedAggregations[iID]
        precisions         = self.currencyInfo['precisions']
        aggregators        = self.__aggregators
        aParams_iID        = self.analysisParams[iID]
        atp_sorted_iID     = self.__analysisToProcess_Sorted[iID]
        aKwargs_symbol_iID = self.__analysisKwargs[iID]
        func_aGen  = analyzers.analysisGenerator
        func_gnitt = auxiliaries.getNextIntervalTickTimestamp
        aggTS = func_gnitt(intervalID = iID, timestamp = atTS, nTicks = 0)

        #[2]: Aggregation
        for target in ('kline', 'depth', 'aggTrade'):
            dRaw_target     = dRaw[target]
            dAgg_iID_target = dAgg_iID[target]
            dTSs_iID_target = dTSs_iID[target]
            lcas_iID_target = lcas_iID[target]
            aggregator = aggregators[target]
            if aggTS not in dAgg_iID_target:
                dTSs_iID_target.append(aggTS)
            aggregator(dataRaw        = dRaw_target,
                       dataAgg        = dAgg_iID_target,
                       lastClosedAggs = lcas_iID_target,
                       rawOpenTS      = atTS,
                       aggOpenTS      = aggTS,
                       aggIntervalID  = iID,
                       precisions     = precisions)

        #[3]: Analysis Generation
        for aType, aCode in atp_sorted_iID:
            func_aGen(analysisType    = aType,
                      timestamp       = aggTS,
                      analysisResults = dAgg_iID[aCode],
                      **aKwargs_symbol_iID,
                      **aParams_iID[aCode])

    def __onRegenerationComplete(self):
        #[1]: Horizontal ViewRange Reset
        self._onHViewRangeUpdate(1)
        self._editVVR_toExtremaCenter('KLINESPRICE')
        for sivCode in self.displayBox_graphics_visibleSIViewers: 
            self._editVVR_toExtremaCenter(sivCode)

        #[2]: Mode & Loading Cover Update
        self.__mode = _TYPEMODE_PENDING
        self._setLoadingCover(show = False, text = "-", gaugeValue = None)
    
    def _onAggregationIntervalUpdate(self, previousIntervalID):
        #[1]: Target Check
        if self.__simulation is None:
            return
        
        #[2]: SI Type Analysis Codes Update
        self._updateSITypeAnalysisCodes()

        #[3]: Currency Analysis Configuration Read
        cacCode = self.__simulation['positions'][self.currencySymbol]['currencyAnalysisConfigurationCode']
        cac_iID = self.__simulation['currencyAnalysisConfigurations'][cacCode][self.intervalID]
        self._readCurrencyAnalysisConfiguration(currencyAnalysisConfiguration = cac_iID)
        
        #[4]: Mode & Loading Cover Update
        self._setLoadingCover(show = True, text = self.visualManager.getTextPack('GUIO_CHARTDRAWER:REGENERATINGCHARTDATA'), gaugeValue = 0)
        self.__mode = _TYPEMODE_REGENERATING
        sit_aCodes  = self.siTypes_analysisCodes
        sit_aCodes['VOL']     = set()
        sit_aCodes['NNA']     = set()
        sit_aCodes['MMACD']   = set()
        sit_aCodes['DMIxADX'] = set()
        sit_aCodes['MFI']     = set()
        sit_aCodes['TPD']     = set()
        aParams_iID = self.analysisParams.get(self.intervalID)
        if aParams_iID is not None:
            if 'MMACD' in aParams_iID: sit_aCodes['MMACD'].add('MMACD')
            for aCode in aParams_iID:
                if   aCode.startswith('VOL'):     sit_aCodes['VOL'].add(aCode)
                elif aCode.startswith('NNA'):     sit_aCodes['NNA'].add(aCode)
                elif aCode.startswith('DMIxADX'): sit_aCodes['DMIxADX'].add(aCode)
                elif aCode.startswith('MFI'):     sit_aCodes['MFI'].add(aCode)
                elif aCode.startswith('TPD'):     sit_aCodes['TPD'].add(aCode)